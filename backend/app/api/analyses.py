"""Analysis management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import FileResponse, HTMLResponse
from ..services.file_service import file_service

from ..database import get_db
from ..schemas.analysis import AnalysisCreate, AnalysisResponse
from ..services.analysis_service import create_analysis, get_user_analyses, get_analysis_by_id
from ..core.deps import get_current_user
from ..models.user import User
from ..services.data_collection_service import data_collection_service
from ..report_generation.section_runner import run_section_generation
from ..models.section import Section

router = APIRouter(prefix="/api/analyses", tags=["analyses"])

@router.post("/", response_model=AnalysisResponse)
def create_new_analysis(
    analysis_data: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new analysis"""
    return create_analysis(db, analysis_data, current_user)

@router.get("/", response_model=List[AnalysisResponse])
def list_analyses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all analyses for the current user"""
    return get_user_analyses(db, current_user)

@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analysis details"""
    analysis = get_analysis_by_id(db, analysis_id, current_user)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    return analysis

# Add new endpoint
@router.post("/{analysis_id}/start-collection")
def start_data_collection(
    analysis_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start Phase A data collection"""
    analysis = get_analysis_by_id(db, analysis_id, current_user)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    if analysis.status != "created":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis is in '{analysis.status}' status, cannot start collection"
        )
    
    # Start background collection
    background_tasks.add_task(
        data_collection_service.collect_data_for_analysis,
        db, 
        analysis
    )
    
    return {
        "message": "Data collection started",
        "analysis_id": analysis_id,
        "status": "collection"
    }

# Add download endpoint
@router.get("/{analysis_id}/download/raw-data")
def download_raw_data(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download raw data Excel file"""
    analysis = get_analysis_by_id(db, analysis_id, current_user)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    raw_data_path = file_service.get_raw_data_path(analysis_id)
    
    if not file_service.raw_data_exists(analysis_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raw data file not found. Run data collection first."
        )
    
    # Generate filename with analysis info
    tickers = [company['ticker'] for company in analysis.companies]
    filename = "raw_data.xlsx"
    #filename = f"raw_data_{'-'.join(tickers)}_{analysis.created_at.strftime('%Y%m%d')}.xlsx"
    
    return FileResponse(
        path=str(raw_data_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Add this endpoint
@router.post("/{analysis_id}/start-analysis")
def start_analysis_generation(
    analysis_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start Phase B: Generate all 20 analysis sections"""
    analysis = get_analysis_by_id(db, analysis_id, current_user)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    if analysis.status != "collection_complete":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start analysis. Data collection must be complete first. Current status: {analysis.status}"
        )
    
    # Check if collector pickle exists
    from ..services.file_service import file_service
    if not file_service.collector_pickle_exists(analysis_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Financial collector data not found. Please run data collection again."
        )
    
    # Start section generation in background
    background_tasks.add_task(run_section_generation, analysis, db)
    
    return {
        "message": "Section generation started",
        "analysis_id": analysis_id,
        "status": "generating"
    }


@router.get("/{analysis_id}/sections")
def get_analysis_sections(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get status of all sections for an analysis"""
    analysis = get_analysis_by_id(db, analysis_id, current_user)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    sections = db.query(Section).filter(
        Section.analysis_id == analysis_id
    ).order_by(Section.section_number).all()
    
    return {
        "analysis_id": analysis_id,
        "analysis_status": analysis.status,
        "total_sections": len(sections),
        "sections": [
            {
                "section_number": s.section_number,
                "section_name": s.section_name,
                "status": s.status,
                "error_message": s.error_message,                
                "started_at": s.started_at,
                "completed_at": s.completed_at,
                "processing_time": (s.completed_at - s.started_at).total_seconds() 
            if s.started_at and s.completed_at else None
            }
            for s in sections
        ]
    }

@router.get("/{analysis_id}/sections/{section_number}")
def get_section_html(
    analysis_id: str,
    section_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get HTML content for a specific section"""
    analysis = get_analysis_by_id(db, analysis_id, current_user)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    section = db.query(Section).filter(
        Section.analysis_id == analysis_id,
        Section.section_number == section_number
    ).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    if section.status != "complete":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Section not ready. Current status: {section.status}"
        )
    
    from pathlib import Path
    html_path = Path(section.html_path)
    
    if not html_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section HTML file not found"
        )
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)