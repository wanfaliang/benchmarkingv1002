"""Analysis management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import FileResponse, HTMLResponse
import shutil
from pathlib import Path
import asyncio


from ..database import get_db
from ..schemas.analysis import AnalysisCreate, AnalysisResponse, AnalysisNameUpdate, AnalysisFullUpdate
from ..services.analysis_service import create_analysis, get_user_analyses, get_analysis_by_id, update_analysis_configuration, reset_analysis_state, delete_sections_and_files
from ..core.deps import get_current_user
from ..models.user import User
from ..services.data_collection_service import data_collection_service
from ..report_generation.section_runner import run_section_generation
from ..models.section import Section
from ..services.file_service import file_service

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

@router.patch("/{analysis_id}")
async def update_analysis_name(
    analysis_id: str,
    update_data: AnalysisNameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update only the analysis name (lightweight operation):
    - Updates: Analysis name
    - Keeps: All configuration and data unchanged
    - No data deletion
    """
    # Get the analysis
    analysis = get_analysis_by_id(db, analysis_id, current_user)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    try:
        # Update only the name
        analysis.name = update_data.name
        db.commit()
        db.refresh(analysis)
        
        return {
            "message": "Analysis name updated successfully",
            "analysis_id": analysis_id,
            "name": analysis.name
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update analysis name: {str(e)}"
        )


@router.put("/{analysis_id}")
async def update_analysis_full(
    analysis_id: str,
    update_data: AnalysisFullUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update full analysis configuration (companies, years_back, name):
    - Updates: Companies, years_back, name
    - Deletes: All Section records and all generated files
    - Resets: Status to 'created', progress to 0, clears timestamps
    
    Use this when you need to change the analysis scope or companies.
    """
    # Get the analysis
    analysis = get_analysis_by_id(db, analysis_id, current_user)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    try:
        # Delete sections and files using service
        sections_deleted, files_deleted = await delete_sections_and_files(db, analysis_id)
        
        # Update analysis configuration using service
        update_analysis_configuration(
            analysis,
            companies=update_data.companies,
            years_back=update_data.years_back,
            name=update_data.name
        )
        
        # Reset state since configuration changed
        reset_analysis_state(analysis, status="created")
        
        db.commit()
        db.refresh(analysis)
        
        # Recreate the directory structure
        file_service.create_analysis_dirs(analysis_id)
        
        return {
            "message": "Analysis updated successfully",
            "analysis_id": analysis_id,
            "name": analysis.name,
            "companies": analysis.companies,
            "years_back": analysis.years_back,
            "sections_deleted": sections_deleted,
            "files_deleted": files_deleted,
            "status": analysis.status,
            "note": "Configuration updated. All data cleared. Ready for fresh data collection."
        }
        
    except Exception as e:
        # Rollback database changes if anything fails
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update analysis: {str(e)}"
        )
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
        analysis_id
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

@router.post("/{analysis_id}/restart-analysis")
async def restart_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Restart analysis generation (Phase B) while keeping collected data (Phase A):
    - Keeps: Analysis record, raw_data.xlsx, financial_collector.pkl
    - Deletes: All Section records and section HTML files
    - Resets: Status to 'collection_complete', Phase to 'A', progress to 100
    
    Use this to regenerate analysis sections without re-collecting data.
    """
    # Get the analysis
    analysis = get_analysis_by_id(db, analysis_id, current_user)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Verify that raw data exists (Phase A was completed)
    if not file_service.raw_data_exists(analysis_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot restart analysis. Raw data not found. Please run data collection first."
        )
    
    if not file_service.collector_pickle_exists(analysis_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot restart analysis. Collector pickle not found. Please run data collection first."
        )
    
    try:
        # Step 1: Delete all related sections from database
        sections_deleted = db.query(Section).filter(
            Section.analysis_id == analysis_id
        ).delete()
        
        # Step 2: Reset analysis to collection_complete state
        analysis.status = "collection_complete"
        analysis.phase = "A"
        analysis.progress = 100  # Phase A complete, ready for Phase B
        # Clear Phase B timestamps but keep Phase A completion info
        analysis.started_at = None
        analysis.completed_at = None
        analysis.error_log = None
        
        db.commit()
        
        # Step 3: Delete only the sections directory (keep Excel and pickle files)
        sections_dir = file_service.get_sections_dir(analysis_id)
        files_deleted = 0
        
        if sections_dir.exists():
            # Count files before deletion
            files_deleted = sum(1 for _ in sections_dir.glob("*.html"))
            # Run the blocking file operation in a thread pool
            await asyncio.to_thread(shutil.rmtree, sections_dir)
            # Recreate empty sections directory
            sections_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            "message": "Analysis restarted successfully",
            "analysis_id": analysis_id,
            "analysis_name": analysis.name,
            "sections_deleted": sections_deleted,
            "html_files_deleted": files_deleted,
            "status": analysis.status,
            "phase": analysis.phase,
            "progress": analysis.progress,
            "raw_data_preserved": True,
            "collector_preserved": True,
            "note": "Phase A data preserved. Ready to regenerate Phase B analysis sections."
        }
        
    except Exception as e:
        # Rollback database changes if anything fails
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart analysis: {str(e)}"
        )
    
@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an analysis and all its associated data:
    - Database: Analysis record and all Section records
    - File system: All files in the analysis directory (Excel, pickle, HTML sections)
    """
    # Get the analysis
    analysis = get_analysis_by_id(db, analysis_id, current_user)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    try:
        # Step 1: Delete all related sections from database
        sections_deleted = db.query(Section).filter(
            Section.analysis_id == analysis_id
        ).delete()
        
        # Step 2: Delete the analysis from database
        db.delete(analysis)
        db.commit()
        
        # Step 3: Delete the entire analysis directory and all its contents (async)
        analysis_dir = file_service.get_analysis_dir(analysis_id)
        files_deleted = False
        
        if analysis_dir.exists():
            # Run the blocking file operation in a thread pool
            
            await asyncio.to_thread(shutil.rmtree, analysis_dir)
            files_deleted = True
        
        return {
            "message": "Analysis deleted successfully",
            "analysis_id": analysis_id,
            "sections_deleted": sections_deleted,
            "files_deleted": files_deleted,
            "directory_path": str(analysis_dir)
        }
        
    except Exception as e:
        # Rollback database changes if anything fails
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete analysis: {str(e)}"
        )


# RESET endpoint - keeps the analysis but clears all data/sections
@router.post("/{analysis_id}/reset")
async def reset_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reset an analysis to start fresh:
    - Keeps: Analysis record (companies, years_back, name, etc.)
    - Deletes: All Section records and all generated files
    - Resets: Status to 'created', progress to 0, clears timestamps and errors
    
    Use this to re-run data collection with updated data.
    """
    # Get the analysis
    analysis = get_analysis_by_id(db, analysis_id, current_user)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    try:
        # Step 1: Delete all related sections from database
        sections_deleted = db.query(Section).filter(
            Section.analysis_id == analysis_id
        ).delete()
        
        # Step 2: Reset analysis state (keep the analysis record itself)
        analysis.status = "created"
        analysis.phase = None
        analysis.progress = 0
        analysis.started_at = None
        analysis.completed_at = None
        analysis.error_log = None
        
        db.commit()
        
        # Step 3: Delete all files but keep the directory structure (async)
        analysis_dir = file_service.get_analysis_dir(analysis_id)
        files_deleted = False
        
        if analysis_dir.exists():
            # Run the blocking file operation in a thread pool
            import asyncio
            await asyncio.to_thread(shutil.rmtree, analysis_dir)
            files_deleted = True
            
            # Recreate the directory structure
            file_service.create_analysis_dirs(analysis_id)
        
        return {
            "message": "Analysis reset successfully",
            "analysis_id": analysis_id,
            "analysis_name": analysis.name,
            "sections_deleted": sections_deleted,
            "files_deleted": files_deleted,
            "status": analysis.status,
            "note": "Analysis is ready for fresh data collection"
        }
        
    except Exception as e:
        # Rollback database changes if anything fails
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset analysis: {str(e)}"
        )

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