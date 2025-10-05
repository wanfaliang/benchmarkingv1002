"""Analysis business logic"""
from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime

from ..models.analysis import Analysis
from ..models.user import User
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