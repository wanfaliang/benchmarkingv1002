"""Analysis business logic"""
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime
import shutil
import asyncio
from pathlib import Path
from .file_service import file_service

from ..models.analysis import Analysis
from ..models.user import User
from ..models.section import Section
from ..schemas.analysis import AnalysisCreate, CompanyInfo

def create_analysis(db: Session, analysis_data: AnalysisCreate, user: User) -> Analysis:
    """Create a new analysis"""
    
    # Generate name if not provided
    if not analysis_data.name:
        tickers = [company.ticker for company in analysis_data.companies]
        analysis_name = f"Analysis - {', '.join(tickers)} - {datetime.now().strftime('%Y-%m-%d')}"
    else:
        analysis_name = analysis_data.name
    
    # Create analysis record - store companies as list directly
    analysis = Analysis(
        user_id=user.user_id,
        name=analysis_name,
        companies=[company.dict() for company in analysis_data.companies],  # Store as list
        years_back=analysis_data.years_back,
        status="created",
        phase=None,
        progress=0
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return analysis

def get_user_analyses(db: Session, user: User) -> List[Analysis]:
    """Get all analyses for a user"""
    return db.query(Analysis).filter(Analysis.user_id == user.user_id).order_by(Analysis.created_at.desc()).all()

def get_analysis_by_id(db: Session, analysis_id: str, user: User) -> Analysis:
    """Get analysis by ID for the current user"""
    return db.query(Analysis).filter(
        Analysis.analysis_id == analysis_id,
        Analysis.user_id == user.user_id
    ).first()

def create_analysis(db: Session, analysis_data: AnalysisCreate, user: User) -> Analysis:
    """Create a new analysis"""
    
    # Generate name if not provided
    if not analysis_data.name:
        tickers = [company.ticker for company in analysis_data.companies]
        analysis_name = f"Analysis - {', '.join(tickers)} - {datetime.now().strftime('%Y-%m-%d')}"
    else:
        analysis_name = analysis_data.name
    
    # Create analysis record - store companies as list directly
    analysis = Analysis(
        user_id=user.user_id,
        name=analysis_name,
        companies=[company.dict() for company in analysis_data.companies],  # Store as list
        years_back=analysis_data.years_back,
        status="created",
        phase=None,
        progress=0
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return analysis

def get_user_analyses(db: Session, user: User) -> List[Analysis]:
    """Get all analyses for a user"""
    return db.query(Analysis).filter(Analysis.user_id == user.user_id).order_by(Analysis.created_at.desc()).all()

def get_analysis_by_id(db: Session, analysis_id: str, user: User) -> Analysis:
    """Get analysis by ID for the current user"""
    return db.query(Analysis).filter(
        Analysis.analysis_id == analysis_id,
        Analysis.user_id == user.user_id
    ).first()

# ============================================================================
# Helper Functions for Analysis Management
# ============================================================================

def generate_analysis_name(companies: List[CompanyInfo]) -> str:
    """Generate analysis name from company tickers"""
    tickers = [company.ticker for company in companies]
    return f"Analysis - {', '.join(tickers)} - {datetime.now().strftime('%Y-%m-%d')}"

async def delete_sections_and_files(db: Session, analysis_id: str) -> tuple[int, bool]:
    """
    Delete all sections from database and all files from filesystem
    Returns: (sections_deleted_count, files_deleted_bool)
    """
    # Delete sections from database
    sections_deleted = db.query(Section).filter(
        Section.analysis_id == analysis_id
    ).delete()
    print("Debug")
    # Delete all files
    analysis_dir = file_service.get_analysis_dir(analysis_id)
    files_deleted = False
    
    if analysis_dir.exists():
        await asyncio.to_thread(shutil.rmtree, analysis_dir)
        files_deleted = True
    
    return sections_deleted, files_deleted

async def delete_sections_only(db: Session, analysis_id: str) -> tuple[int, int]:
    """
    Delete sections from database and section HTML files only (keep Excel and pickle)
    Returns: (sections_deleted_count, html_files_deleted_count)
    """
    # Delete sections from database
    sections_deleted = db.query(Section).filter(
        Section.analysis_id == analysis_id
    ).delete()
    
    # Delete only section HTML files
    sections_dir = file_service.get_sections_dir(analysis_id)
    html_files_deleted = 0
    
    if sections_dir.exists():
        # Count HTML files before deletion
        html_files_deleted = sum(1 for _ in sections_dir.glob("*.html"))
        await asyncio.to_thread(shutil.rmtree, sections_dir)
        # Recreate empty sections directory
        sections_dir.mkdir(parents=True, exist_ok=True)
    
    return sections_deleted, html_files_deleted

def reset_analysis_state(analysis: Analysis, status: str, phase: Optional[str] = None, progress: int = 0) -> None:
    """Reset analysis state fields"""
    analysis.status = status
    analysis.phase = phase
    analysis.progress = progress
    analysis.started_at = None
    analysis.completed_at = None
    analysis.error_log = None

def update_analysis_configuration(
    analysis: Analysis, 
    companies: List[CompanyInfo], 
    years_back: int, 
    name: Optional[str] = None
) -> None:
    """Update analysis configuration (companies, years_back, name)"""
    if not name:
        name = generate_analysis_name(companies)
    
    analysis.name = name
    analysis.companies = [company.dict() for company in companies]
    analysis.years_back = years_back