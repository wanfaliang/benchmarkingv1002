"""Analysis schemas for API requests/responses"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CompanyInfo(BaseModel):
    ticker: str
    name: str

class AnalysisCreate(BaseModel):
    """Schema for creating new analysis"""
    companies: List[CompanyInfo]  # List of names and tickers
    years_back: int = 10
    name: Optional[str] = None

class AnalysisResponse(BaseModel):
    """Schema for analysis response"""
    analysis_id: str
    user_id: str
    name: Optional[str]
    companies: List[CompanyInfo]
    years_back: int
    status: str
    phase: Optional[str]
    progress: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True