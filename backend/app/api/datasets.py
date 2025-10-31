"""
Dataset API Endpoints
File: backend/app/api/datasets.py

Complete CRUD operations + data access endpoints for datasets
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime

from backend.app.core.deps import get_db, get_current_user
from backend.app.models.user import User
from backend.app.models.dataset import Dataset, Dashboard, SavedQuery, DatasetShareLog
from backend.app.schemas.dataset import (
    DatasetCreate, DatasetUpdate, DatasetResponse,
    ShareDatasetRequest, ShareDatasetResponse,
    DashboardCreate, DashboardResponse,
    SavedQueryCreate, SavedQueryResponse
)
from backend.app.services.collector_loader_service import collector_loader_service
from backend.app.services.file_service import file_service
from backend.app.data_collection.dataset_collector import DatasetCollection
from ..services.data_collection_service import data_collection_service
from backend.app.config import settings
from backend.app.schemas.dataset import DatasetCreate, DatasetUpdate, DatasetResponse, DataQuery, DataFilter

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


# ============================================================================
# DATASET CRUD OPERATIONS
# ============================================================================

@router.post("/", response_model=DatasetResponse, status_code=201)
async def create_dataset(
    dataset: DatasetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new dataset
    
    Body example:
    {
        "name": "Tech Giants Analysis",
        "description": "FAANG companies data exploration",
        "companies": [
            {"ticker": "AAPL", "name": "Apple Inc"},
            {"ticker": "MSFT", "name": "Microsoft Corporation"}
        ],
        "years_back": 10,
        "visibility": "private"
    }
    """
    # Create dataset record
    companies_list = [{"ticker": c.ticker, "name": c.name} for c in dataset.companies]
    
    if not dataset.name:
        tickers = [company.ticker for company in dataset.companies]
        dataset_name = f"dataset - {', '.join(tickers)} - {datetime.now().strftime('%Y-%m-%d')}"
    else:
        dataset_name = dataset.name

    new_dataset = Dataset(
        user_id=current_user.user_id,
        name=dataset_name,
        description=dataset.description,
        companies=companies_list,
        years_back=dataset.years_back,
        include_analyst=dataset.include_analyst,
        include_institutional=dataset.include_institutional,
        visibility=dataset.visibility,
        status="created"
    )
    
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)
    
    # Create directory structure
    dataset_dir = file_service.get_dataset_directory(new_dataset.dataset_id)
    file_service.ensure_directory_exists(dataset_dir)
    
    return new_dataset


@router.get("/", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    visibility: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's datasets (owned + shared with them)
    
    Query params:
    - skip: Pagination offset
    - limit: Max results
    - status: Filter by status (created, collecting, ready, failed)
    - visibility: Filter by visibility (private, shared, public)
    """
    query = db.query(Dataset).filter(
        (Dataset.user_id == current_user.user_id) |
        (Dataset.shared_with.any(user_id=current_user.user_id))
    )
    
    if status:
        query = query.filter(Dataset.status == status)
    if visibility:
        query = query.filter(Dataset.visibility == visibility)
    
    query = query.order_by(Dataset.updated_at.desc())
    datasets = query.offset(skip).limit(limit).all()
    
    return datasets


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dataset details"""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Check access permission
    if not _has_dataset_access(dataset, current_user.user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update last accessed time
    dataset.last_accessed_at = datetime.utcnow()
    db.commit()
    
    return dataset


@router.patch("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset_name(
    dataset_id: str,
    name: str,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update dataset name and description only (lightweight update)"""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only owner can update dataset")
    
    dataset.name = name
    if description is not None:
        dataset.description = description
    dataset.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(dataset)
    
    return dataset


@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset_config(
    dataset_id: str,
    update: DatasetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update full dataset configuration (requires re-collection)
    
    Warning: This will delete existing data and reset status to 'created'
    """
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only owner can update configuration")
    
    # Update configuration
    if update.name:
        dataset.name = update.name
    if update.description is not None:
        dataset.description = update.description
    if update.companies:
        dataset.companies = [{"ticker": c.ticker, "name": c.name} for c in update.companies]
    if update.years_back:
        dataset.years_back = update.years_back
    if update.visibility:
        dataset.visibility = update.visibility
    
    # Reset status and clear data
    dataset.status = "created"
    dataset.progress = 0
    dataset.data_size_mb = None
    dataset.row_count = None
    dataset.collected_at = None
    dataset.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(dataset)
    
    # TODO: Delete existing pickle file
    
    return dataset


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete dataset and all associated data"""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only owner can delete dataset")
    
    # Delete from database (cascades to dashboards, queries, etc.)
    db.delete(dataset)
    db.commit()
    
    # TODO: Delete files from disk
    
    return {"message": "Dataset deleted successfully", "dataset_id": dataset_id}


@router.post("/{dataset_id}/reset")
async def reset_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset dataset to 'created' state, keeping configuration"""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only owner can reset dataset")
    
    dataset.status = "created"
    dataset.progress = 0
    dataset.error_log = None
    dataset.data_size_mb = None
    dataset.row_count = None
    dataset.collected_at = None
    
    db.commit()
    
    return {"message": "Dataset reset successfully", "dataset_id": dataset_id}


# ============================================================================
# DATA COLLECTION
# ============================================================================

@router.post("/{dataset_id}/start-collection")
async def start_collection(
    dataset_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start data collection for dataset"""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only owner can start collection")
    
    if dataset.status not in ["created", "failed"]:
        raise HTTPException(status_code=400, detail=f"Cannot collect data when status is {dataset.status}")
    
    
    # Start background collection
    background_tasks.add_task(
        data_collection_service.collect_data_for_dataset,
        dataset_id
    )
    
    return {
        "message": "Data collection started",
        "analysis_id": dataset_id,
        "status": "collection"
    }
    

@router.get("/{dataset_id}/download/raw-data")
async def download_raw_data(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download raw Excel file"""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not _has_dataset_access(dataset, current_user.user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if dataset.status != "ready":
        raise HTTPException(status_code=400, detail=f"Dataset not ready. Status: {dataset.status}")
        

    raw_data_path = file_service.get_raw_dataset_path(dataset_id)
    
    if not file_service.raw_dataset_exists(dataset_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raw dataset file not found. Run data collection first."
        )
    
    # Generate filename with analysis info
    tickers = [company['ticker'] for company in dataset.companies]
    filename = "raw_data.xlsx"
    # filename = f"raw_data_{'-'.join(tickers)}_{dataset.created_at.strftime('%Y%m%d')}.xlsx" let the frontend handle filename formatting
    
    return FileResponse(
        path=str(raw_data_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ============================================================================
# DATA ACCESS ENDPOINTS 
# ============================================================================

@router.get("/{dataset_id}/data/profile")
async def get_profile(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_profiles()
  
    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/financial")
async def get_financial_data(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_all_financial_data()


    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/is")
async def get_income_statement_data(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_income_statements()
    
    print(f"Retrieved income statement data from dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")

    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/bs")
async def get_balance_sheet_data(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_balance_sheets()
    
    print(f"Retrieved balance sheet data from dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")

    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/cf")
async def get_cash_flow_statement_data(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_cash_flows()
    
    print(f"Retrieved cash flow data from dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")

    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/ratio")
async def get_ratio_data(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_ratios()
    
    print(f"Retrieved ratios from dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")

    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/km")
async def get_key_metrics_data(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_key_metrics()
    
    print(f"Retrieved key metrics from dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")

    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/ev")
async def get_enterprise_value_data(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_enterprise_values()
    
    print(f"Retrieved enterprise value data from dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")

    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/eh")
async def get_employee_historical_data(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_employee_history()
    
    print(f"Retrieved employee historical data from dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")

    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/insiderstat")
async def get_insider_stat_data(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_insider_statistics()
    
    print(f"Retrieved insider statistics data from dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")

    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/analyst")
async def get_analyst_estimate_data(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_analyst_estimates_only() # not using get_analyst_estimates which returns both estimates and targets
    
    print(f"Retrieved analyst estimate data from dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")

    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/target")
async def get_analyst_target_data(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_price_targets()
    
    print(f"Retrieved analyst price target from dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")

    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/analystcoverage")
async def get_analyst_coverage_data(
    dataset_id: str,
    columns: Optional[List[str]] = Query(None),
    companies: Optional[List[str]] = Query(None),
    years: Optional[List[int]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get consolidated financial data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_analyst_coverage_summary()
    
    print(f"Retrieved analyst coverage data from dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {df.columns.tolist()}")

    # Apply filters (same logic as before)
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if years:
        df = df[df['Year'].isin(years)]
    if columns:
        cols = ['Company', 'Symbol', 'Year'] + [c for c in columns if c in df.columns]
        df = df[cols]
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }


@router.get("/{dataset_id}/data/prices/daily")
async def get_daily_prices(
    dataset_id: str,
    symbols: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily price data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_prices_daily()
    
    if symbols:
        df = df[df['symbol'].isin(symbols)]
    if start_date:
        df = df[df['date'] >= start_date]
    if end_date:
        df = df[df['date'] <= end_date]
    
    df = df.sort_values('date', ascending=False)
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }


@router.get("/{dataset_id}/data/prices/monthly")
async def get_monthly_prices(
    dataset_id: str,
    symbols: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly price data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_prices_monthly()
    
    if symbols:
        df = df[df['symbol'].isin(symbols)]
    if start_date:
        df = df[df['date'] >= start_date]
    if end_date:
        df = df[df['date'] <= end_date]
    
    df = df.sort_values('date', ascending=False)
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/prices/sp500daily")
async def get_sp500daily_prices(
    dataset_id: str,
    symbols: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily price data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_sp500_daily()
    
    if symbols:
        df = df[df['symbol'].isin(symbols)]
    if start_date:
        df = df[df['date'] >= start_date]
    if end_date:
        df = df[df['date'] <= end_date]
    
    df = df.sort_values('date', ascending=False)
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/prices/sp500monthly")
async def get_sp500monthly_prices(
    dataset_id: str,
    symbols: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly price data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_sp500_monthly()
    
    if symbols:
        df = df[df['symbol'].isin(symbols)]
    if start_date:
        df = df[df['date'] >= start_date]
    if end_date:
        df = df[df['date'] <= end_date]
    
    df = df.sort_values('date', ascending=False)
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]

    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/{dataset_id}/data/institutional")
async def get_institutional_ownership(
    dataset_id: str,
    companies: Optional[List[str]] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get institutional ownership data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_institutional_ownership()
    
    if companies:
        df = df[df['Symbol'].isin(companies)]
    
    df = df.sort_values(['Symbol', 'date'], ascending=False)

    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }


@router.get("/{dataset_id}/data/insider")
async def get_insider_trading(
    dataset_id: str,
    companies: Optional[List[str]] = Query(None),
    transaction_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get insider trading transactions"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_insider_trading_latest()
    
    if companies:
        df = df[df['Symbol'].isin(companies)]
    if transaction_type:
        df = df[df['transactionType'] == transaction_type]
    if start_date:
        df = df[df['transactionDate'] >= start_date]
    
    df = df.sort_values('transactionDate', ascending=False)
    
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }


@router.get("/{dataset_id}/data/economic")
async def get_economic_data(
    dataset_id: str,
    indicators: Optional[List[str]] = Query(None),
    start_year: Optional[int] = Query(None),
    end_year: Optional[int] = Query(None),
    limit: Optional[int] = Query(None),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get macroeconomic indicators"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    df = collector.get_economic()
    
    if start_year:
        df = df[df['Year'] >= start_year]
    if end_year:
        df = df[df['Year'] <= end_year]
    if indicators:
        cols = ['Year'] + [i for i in indicators if i in df.columns]
        df = df[cols]
    
    df = df.sort_values('Year', ascending=False)
    total = len(df)
    end_index = (offset + limit) if limit is not None else None
    df = df.iloc[offset:end_index]
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "available_indicators": [c for c in df.columns if c != 'Year'],
        "total": total,
        "offset": offset,
        "limit": limit,
        "columns": df.columns.tolist()
    }

@router.get("/metadata")
async def get_metadata(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Not dependent on dataset - get metadata about available data, needs fixing later to remove dataset_id"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    financial_df = collector.get_all_financial_data()
    
    return {
        "companies": financial_df['Symbol'].unique().tolist(),
        "company_names": dict(zip(financial_df['Symbol'], financial_df['Company'])),
        "years": sorted(financial_df['Year'].unique().tolist()),
        "available_metrics": [c for c in financial_df.columns if c not in ['Company', 'Symbol', 'Year', 'date', 'symbol']],
        "data_sources": [
            "financial",
            "income statement",
            "balance sheet",
            "cash flow",
            "ratios",
            "key metrics",
            "enterprise value",
            "prices_daily",
            "prices_monthly",
            "sp500_daily",
            "sp500_monthly",
            "institutional",
            "insider trading",
            "insider statistics",
            "company profiles",
            "employee history",
            "analyst estimates",
            "price targets",
            "analyst coverage",
            "economic",
        ]
    }

@router.get("/{dataset_id}/metadata")
async def get_dataset_metadata(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get metadata about available data"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    financial_df = collector.get_all_financial_data()
    
    return {
        "companies": financial_df['Symbol'].unique().tolist(),
        "company_names": dict(zip(financial_df['Symbol'], financial_df['Company'])),
        "years": sorted(financial_df['Year'].unique().tolist()),
        "available_metrics": [c for c in financial_df.columns if c not in ['Company', 'Symbol', 'Year', 'date', 'symbol']],
        "data_sources": [
            "financial",
            "income statement",
            "balance sheet",
            "cash flow",
            "ratios",
            "key metrics",
            "enterprise value",
            "prices_daily",
            "prices_monthly",
            "sp500_daily",
            "sp500_monthly",
            "institutional",
            "insider trading",
            "insider statistics",
            "company profiles",
            "employee history",
            "analyst estimates",
            "price targets",
            "analyst coverage",
            "economic",
        ]
    }


# ============================================================================
# SAVED QUERIES (Updated - dataset_id optional)
# ============================================================================

@router.post("/queries", response_model=SavedQueryResponse)
async def create_saved_query(
    query: SavedQueryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a query for reuse
    Query is user-wide (works on any dataset with same data_source)
    """
  
    new_query = SavedQuery(
        dataset_id=None,  # Queries are not tied to a specific dataset
        user_id=current_user.user_id,
        name=query.name,
        description=query.description,
        data_source=query.data_source,
        query_config=query.query_config,
        is_public=query.is_public
    )
    
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    
    return new_query


@router.get("/queries/all", response_model=List[SavedQueryResponse])
async def list_saved_queries(
    data_source: Optional[str] = Query(None),
    include_public: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List saved queries
 
    Filters:
    - data_source: queries for specific data source
    - include_public: include public queries from other users
    """
    # Start with user's own queries
    query_builder = db.query(SavedQuery).filter(
        SavedQuery.user_id == current_user.user_id
    )
    
    
    # Filter by data_source
    if data_source:
        query_builder = query_builder.filter(SavedQuery.data_source == data_source)
    
    user_queries = query_builder.all()
    
    # Add public queries from other users
    if include_public:
        public_query_builder = db.query(SavedQuery).filter(
            SavedQuery.is_public == True,
            SavedQuery.user_id != current_user.user_id
        )
        
        if data_source:
            public_query_builder = public_query_builder.filter(SavedQuery.data_source == data_source)
        
        public_queries = public_query_builder.all()
        return user_queries + public_queries
    
    return user_queries


@router.get("/queries/{query_id}", response_model=SavedQueryResponse)
async def get_saved_query(
    query_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific saved query"""
    query = db.query(SavedQuery).filter(SavedQuery.query_id == query_id).first()
    
    if not query:
        raise HTTPException(404, "Query not found")
    
    # Check access: owner or public query
    if query.user_id != current_user.user_id and not query.is_public:
        raise HTTPException(403, "Access denied")
    
    return query


@router.post("/queries/{query_id}/execute")
async def execute_saved_query(
    query_id: str,
    dataset_id: str = Query(..., description="Dataset to run query against"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute a saved query against a dataset
    
    This is the magic: run saved query on ANY dataset!
    """
    # Get the saved query
    saved_query = db.query(SavedQuery).filter(SavedQuery.query_id == query_id).first()
    
    if not saved_query:
        raise HTTPException(404, "Query not found")
    
    # Check access to query
    if saved_query.user_id != current_user.user_id and not saved_query.is_public:
        raise HTTPException(403, "Access denied to this query")
    
    # Check access to dataset
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    # Execute the query
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    
    # Get data source
    data_source = saved_query.data_source
    data_source = data_source.lower()
    df = pd.DataFrame()
    try:
        df = _get_df_for_data_source(collector, data_source)
    except ValueError as e:
        raise HTTPException(400, str(e))
        
    # Apply saved query config
    config = saved_query.query_config
    
    if config.get('filters'):
        df = _apply_filters(df, [DataFilter(**f) for f in config['filters']])
    
    if config.get('companies'):
        symbol_col = 'Symbol' if 'Symbol' in df.columns else 'symbol'
        if symbol_col in df.columns:
            df = df[df[symbol_col].isin(config['companies'])]
    
    if config.get('years') and 'Year' in df.columns:
        df = df[df['Year'].isin(config['years'])]
    
    if config.get('columns'):
        available_cols = [c for c in config['columns'] if c in df.columns]
        df = df[available_cols]
    
    if config.get('sort_by') and config['sort_by'] in df.columns:
        df = df.sort_values(config['sort_by'], ascending=(config.get('sort_order', 'asc') == 'asc'))
    
    total = len(df)
    limit = config.get('limit')
    offset = config.get('offset', 0)
    
    if limit:
        df = df.iloc[offset:offset+limit]
    
    df = _clean_dataframe_for_json(df)
    
    # Update usage stats
    saved_query.usage_count += 1
    saved_query.last_used_at = datetime.utcnow()
    db.commit()
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "query_name": saved_query.name,
        "data_source": data_source
    }


@router.put("/queries/{query_id}", response_model=SavedQueryResponse)
async def update_saved_query(
    query_id: str,
    query_update: SavedQueryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update saved query"""
    query = db.query(SavedQuery).filter(SavedQuery.query_id == query_id).first()
    
    if not query:
        raise HTTPException(404, "Query not found")
    
    if query.user_id != current_user.user_id:
        raise HTTPException(403, "Only owner can update query")
    
    query.name = query_update.name
    query.description = query_update.description
    query.data_source = query_update.data_source
    query.query_config = query_update.query_config
    query.is_public = query_update.is_public
    query.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(query)
    
    return query


@router.delete("/queries/{query_id}")
async def delete_saved_query(
    query_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete saved query"""
    query = db.query(SavedQuery).filter(SavedQuery.query_id == query_id).first()
    
    if not query:
        raise HTTPException(404, "Query not found")
    
    if query.user_id != current_user.user_id:
        raise HTTPException(403, "Only owner can delete query")
    
    db.delete(query)
    db.commit()
    
    return {"message": "Query deleted", "query_id": query_id}

@router.post("/{dataset_id}/query")
async def query_data(
    dataset_id: str,
    query: DataQuery,  # Use Pydantic model, not Dict
    data_source: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Flexible data query with filtering, sorting, pagination"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    collector = collector_loader_service.load_dataset_collector(dataset_id)
    data_source = data_source.lower()
    df = pd.DataFrame()
    try:
        df = _get_df_for_data_source(collector, data_source)
    except ValueError as e:
        raise HTTPException(400, str(e))
            
    # Apply filters
    if query.filters:
        df = _apply_filters(df, query.filters)
    
    if query.companies:
        symbol_col = 'Symbol' if 'Symbol' in df.columns else 'symbol'
        if symbol_col in df.columns:
            df = df[df[symbol_col].isin(query.companies)]
    
    if query.years and 'Year' in df.columns:
        df = df[df['Year'].isin(query.years)]
    
    if query.columns:
        available_cols = [c for c in query.columns if c in df.columns]
        df = df[available_cols]
    
    if query.sort_by and query.sort_by in df.columns:
        df = df.sort_values(query.sort_by, ascending=(query.sort_order == "asc"))
    
    total = len(df)
    if query.limit:
        df = df.iloc[query.offset:query.offset+query.limit]
    
    df = _clean_dataframe_for_json(df)
    
    return {
        "data": df.to_dict(orient='records'),
        "total": total,
        "offset": query.offset,
        "limit": query.limit
    }


@router.post("/{dataset_id}/aggregate")
async def aggregate_data(
    dataset_id: str,
    request: Dict[str, Any],
    data_source: str = Query("financial"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aggregate data by grouping"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    # Same implementation as data.py aggregate endpoint
    # ... (copy from data.py)
    pass


@router.post("/{dataset_id}/pivot")
async def pivot_data(
    dataset_id: str,
    request: Dict[str, Any],
    data_source: str = Query("financial"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create pivot table"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    # Same implementation as data.py pivot endpoint
    # ... (copy from data.py)
    pass


@router.post("/{dataset_id}/compare")
async def compare_companies(
    dataset_id: str,
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare specific metrics across companies"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    # Same implementation as data.py compare endpoint
    # ... (copy from data.py)
    pass


# ============================================================================
# SHARING ENDPOINTS
# ============================================================================

@router.post("/{dataset_id}/share", response_model=ShareDatasetResponse)
async def share_dataset(
    dataset_id: str,
    share_request: ShareDatasetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Share dataset with another user by email
    
    Body:
    {
        "email": "colleague@example.com",
        "permission": "view",  // view, edit, admin
        "message": "Check out this dataset!"
    }
    """
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only owner can share dataset")
    
    # Find user to share with
    from backend.app.models.user import User as UserModel
    target_user = db.query(UserModel).filter(UserModel.email == share_request.email).first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User with email {share_request.email} not found")
    
    if target_user.user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot share dataset with yourself")
    
    # Check if already shared
    from backend.app.models.dataset import dataset_shares
    existing_share = db.execute(
        dataset_shares.select().where(
            dataset_shares.c.dataset_id == dataset_id,
            dataset_shares.c.shared_with_user_id == target_user.user_id
        )
    ).first()
    
    if existing_share:
        # Update permission
        db.execute(
            dataset_shares.update().where(
                dataset_shares.c.dataset_id == dataset_id,
                dataset_shares.c.shared_with_user_id == target_user.user_id
            ).values(permission=share_request.permission)
        )
    else:
        # Create new share
        db.execute(
            dataset_shares.insert().values(
                dataset_id=dataset_id,
                shared_with_user_id=target_user.user_id,
                permission=share_request.permission,
                shared_by_user_id=current_user.user_id
            )
        )
    
    # Log share action
    share_log = DatasetShareLog(
        dataset_id=dataset_id,
        shared_by_user_id=current_user.user_id,
        shared_with_user_id=target_user.user_id,
        action="shared",
        permission=share_request.permission,
        share_method="email"
    )
    db.add(share_log)
    
    # Update dataset visibility if needed
    if dataset.visibility == "private":
        dataset.visibility = "shared"
    
    db.commit()
    
    # TODO: Send email notification to target user
    
    return ShareDatasetResponse(
        success=True,
        shared_with_user_id=target_user.user_id,
        permission=share_request.permission
    )


@router.delete("/{dataset_id}/share/{user_id}")
async def unshare_dataset(
    dataset_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove user's access to dataset"""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only owner can unshare dataset")
    
    # Remove share
    from backend.app.models.dataset import dataset_shares
    db.execute(
        dataset_shares.delete().where(
            dataset_shares.c.dataset_id == dataset_id,
            dataset_shares.c.shared_with_user_id == user_id
        )
    )
    
    # Log action
    share_log = DatasetShareLog(
        dataset_id=dataset_id,
        shared_by_user_id=current_user.user_id,
        shared_with_user_id=user_id,
        action="unshared"
    )
    db.add(share_log)
    
    db.commit()
    
    return {"message": "Dataset access removed", "user_id": user_id}


@router.get("/{dataset_id}/shares")
async def list_dataset_shares(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all users who have access to this dataset"""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only owner can view shares")
    
    # Get all shares
    from backend.app.models.dataset import dataset_shares
    from backend.app.models.user import User as UserModel
    
    shares = db.execute(
        dataset_shares.select().where(dataset_shares.c.dataset_id == dataset_id)
    ).all()
    
    result = []
    for share in shares:
        user = db.query(UserModel).filter(UserModel.user_id == share.shared_with_user_id).first()
        if user:
            result.append({
                "user_id": user.user_id,
                "email": user.email,
                "full_name": user.full_name,
                "permission": share.permission,
                "shared_at": share.shared_at
            })
    
    return {"shares": result, "total": len(result)}


@router.post("/{dataset_id}/share/public")
async def create_public_share_link(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a public share link for the dataset
    Anyone with the link can view (but not edit)
    """
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only owner can create public link")
    
    # Generate unique share token
    import secrets
    share_token = secrets.token_urlsafe(32)
    
    dataset.share_token = share_token
    dataset.visibility = "public"
    
    # Log action
    share_log = DatasetShareLog(
        dataset_id=dataset_id,
        shared_by_user_id=current_user.user_id,
        action="shared",
        share_method="link",
        permission="view"
    )
    db.add(share_log)
    
    db.commit()
    
    share_link = f"{settings.FRONTEND_URL}/datasets/public/{share_token}"
    
    return {
        "share_link": share_link,
        "share_token": share_token,
        "expires": None  # TODO: Add expiration if needed
    }


@router.delete("/{dataset_id}/share/public")
async def revoke_public_share_link(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke public share link"""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if dataset.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only owner can revoke public link")
    
    dataset.share_token = None
    dataset.visibility = "private"
    
    db.commit()
    
    return {"message": "Public share link revoked"}


@router.get("/public/{share_token}", response_model=DatasetResponse)
async def access_public_dataset(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Access dataset via public share link (no auth required)"""
    dataset = db.query(Dataset).filter(Dataset.share_token == share_token).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Invalid share link")
    
    # Log access
    share_log = DatasetShareLog(
        dataset_id=dataset.dataset_id,
        action="accessed",
        share_method="link"
    )
    db.add(share_log)
    
    dataset.last_accessed_at = datetime.utcnow()
    db.commit()
    
    return dataset


# ============================================================================
# DASHBOARD MANAGEMENT
# ============================================================================

@router.post("/{dataset_id}/dashboards", response_model=DashboardResponse)
async def create_dashboard(
    dataset_id: str,
    dashboard: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a custom dashboard for this dataset"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    new_dashboard = Dashboard(
        dataset_id=dataset_id,
        user_id=current_user.user_id,
        name=dashboard.name,
        description=dashboard.description,
        layout=dashboard.layout,
        is_default=dashboard.is_default
    )
    
    db.add(new_dashboard)
    db.commit()
    db.refresh(new_dashboard)
    
    return new_dashboard


@router.get("/{dataset_id}/dashboards", response_model=List[DashboardResponse])
async def list_dashboards(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all dashboards for this dataset"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    dashboards = db.query(Dashboard).filter(
        Dashboard.dataset_id == dataset_id,
        Dashboard.user_id == current_user.user_id
    ).all()
    
    return dashboards


@router.get("/{dataset_id}/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dataset_id: str,
    dashboard_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific dashboard"""
    dashboard = db.query(Dashboard).filter(Dashboard.dashboard_id == dashboard_id).first()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    if dashboard.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    dashboard.view_count += 1
    db.commit()
    
    return dashboard


@router.put("/{dataset_id}/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dataset_id: str,
    dashboard_id: str,
    dashboard_update: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update dashboard configuration"""
    dashboard = db.query(Dashboard).filter(Dashboard.dashboard_id == dashboard_id).first()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    if dashboard.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only owner can update dashboard")
    
    dashboard.name = dashboard_update.name
    dashboard.description = dashboard_update.description
    dashboard.layout = dashboard_update.layout
    dashboard.is_default = dashboard_update.is_default
    dashboard.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(dashboard)
    
    return dashboard


@router.delete("/{dataset_id}/dashboards/{dashboard_id}")
async def delete_dashboard(
    dataset_id: str,
    dashboard_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete dashboard"""
    dashboard = db.query(Dashboard).filter(Dashboard.dashboard_id == dashboard_id).first()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    if dashboard.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Only owner can delete dashboard")
    
    db.delete(dashboard)
    db.commit()
    
    return {"message": "Dashboard deleted", "dashboard_id": dashboard_id}


# ============================================================================
# SAVED QUERIES
# ============================================================================

@router.post("/{dataset_id}/queries", response_model=SavedQueryResponse)
async def create_saved_query(
    dataset_id: str,
    query: SavedQueryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a query for reuse"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    new_query = SavedQuery(
        dataset_id=dataset_id,
        user_id=current_user.user_id,
        name=query.name,
        description=query.description,
        data_source=query.data_source,
        query_config=query.query_config,
        is_public=query.is_public
    )
    
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    
    return new_query


@router.get("/{dataset_id}/queries", response_model=List[SavedQueryResponse])
async def list_saved_queries(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List saved queries"""
    _validate_dataset_access(dataset_id, current_user.user_id, db)
    
    queries = db.query(SavedQuery).filter(
        SavedQuery.dataset_id == dataset_id,
        SavedQuery.user_id == current_user.user_id
    ).all()
    
    return queries


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _has_dataset_access(dataset: Dataset, user_id: str) -> bool:
    """Check if user has access to dataset"""
    # Owner has access
    if dataset.user_id == user_id:
        return True
    
    # Check if shared with user
    for shared_user in dataset.shared_with:
        if shared_user.user_id == user_id:
            return True
    
    return False


def _validate_dataset_access(dataset_id: str, user_id: str, db: Session):
    """Validate user has access to dataset"""
    dataset = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not _has_dataset_access(dataset, user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if dataset.status != "ready":
        raise HTTPException(status_code=400, detail=f"Dataset not ready. Status: {dataset.status}")
    
    return dataset


def _clean_dataframe_for_json(df: pd.DataFrame) -> pd.DataFrame:
    """Clean DataFrame for JSON serialization"""
    import numpy as np
    
    df = df.copy()
    df = df.replace([np.inf, -np.inf, np.nan], None)
    df = df.where(pd.notnull(df), None)
    
    for col in df.select_dtypes(include=['datetime64']).columns:
        df[col] = df[col].astype(str)
    
    return df



def _apply_filters(df: pd.DataFrame, filters: List[DataFilter]) -> pd.DataFrame:
    """Apply filters to DataFrame"""
    if not filters:
        return df
    
    for f in filters:
        if f.field not in df.columns:
            continue

        column_dtype = df[f.field].dtype
        
        # Convert value to match column dtype
        if pd.api.types.is_numeric_dtype(column_dtype):
            f.value = float(f.value) if '.' in str(f.value) else int(f.value)

        if f.operator == "eq":
            df = df[df[f.field] == f.value]
        elif f.operator == "ne":
            df = df[df[f.field] != f.value]
        elif f.operator == "gt":
            df = df[df[f.field] > f.value]
        elif f.operator == "gte":
            df = df[df[f.field] >= f.value]
        elif f.operator == "lt":
            df = df[df[f.field] < f.value]
        elif f.operator == "lte":
            df = df[df[f.field] <= f.value]
        elif f.operator == "in":
            df = df[df[f.field].isin(f.value)]
        elif f.operator == "between":
            df = df[df[f.field].between(f.value[0], f.value[1])]
        elif f.operator == "contains":
            df = df[df[f.field].astype(str).str.contains(str(f.value), case=False, na=False)]
    
    return df

def _get_df_for_data_source(collector: DatasetCollection, data_source: str) -> pd.DataFrame:
    """Helper to get DataFrame for specific data source"""
    if data_source == "financial":
        return collector.get_all_financial_data()
    elif data_source == "is":
        return collector.get_income_statements()
    elif data_source == "bs":
        return collector.get_balance_sheets()
    elif data_source == "cf":
        return collector.get_cash_flows()
    elif data_source == "ratios":
        return collector.get_ratios()
    elif data_source == "metrics":
        return collector.get_key_metrics()
    elif data_source == "ev":
        return collector.get_enterprise_values()
    elif data_source == "daily" or data_source == "prices daily" or data_source == "daily prices":
        return collector.get_prices_daily()
    elif data_source == "monthly" or data_source == "prices monthly" or data_source == "monthly prices":
        return collector.get_prices_monthly()
    elif data_source == "sp500d" or data_source == "s&p 500 daily" or data_source == "sp 500 daily":
        return collector.get_sp500_daily()
    elif data_source == "sp500m" or data_source == "s&p 500 monthly" or data_source == "sp 500 monthly":
        return collector.get_sp500_monthly()
    elif data_source == "institutional":
        return collector.get_institutional_ownership()
    elif data_source == "insider" or data_source == "insider trading":
        return collector.get_insider_trading_latest()
    elif data_source == "insider statistics" or data_source == "insiderstats":
        return collector.get_insider_statistics()
    elif data_source == "profiles":
        return collector.get_profiles()
    elif data_source == "employees":
        return collector.get_employee_history()
    elif data_source == "analyst":
        return collector.get_analyst_estimates_only()
    elif data_source == "targets":
        return collector.get_price_targets()
    elif data_source == "coverage":
        return collector.get_analyst_coverage_summary()
    elif data_source == "economic" or data_source == "economic indicators":
        return collector.get_economic()
    else:
        raise ValueError(f"Invalid data_source: {data_source}")