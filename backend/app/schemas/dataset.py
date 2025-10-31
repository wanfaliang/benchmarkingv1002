"""
File: backend/app/schemas/dataset.py
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class CompanyInput(BaseModel):
    """Company information for dataset creation"""
    ticker: str
    name: str


class DatasetCreate(BaseModel):
    """Request to create new dataset"""
    name: str = Field(..., min_length=0, max_length=200)
    description: Optional[str] = None
    companies: List[CompanyInput]
    years_back: int = Field(10, ge=1, le=20)
    include_analyst: bool = True
    include_institutional: bool = True
    visibility: str = Field("private", pattern="^(private|shared|public)$")


class DatasetUpdate(BaseModel):
    """Request to update dataset configuration"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    companies: Optional[List[CompanyInput]] = None
    years_back: Optional[int] = Field(None, ge=1, le=20)
    visibility: Optional[str] = Field(None, pattern="^(private|shared|public)$")


class DatasetResponse(BaseModel):
    """Dataset information response"""
    dataset_id: str
    user_id: str
    name: str
    description: Optional[str]
    companies: List[Dict[str, str]]
    years_back: int
    status: str
    progress: int
    visibility: str
    data_size_mb: Optional[int]
    row_count: Optional[int]
    created_at: datetime
    updated_at: datetime
    collected_at: Optional[datetime]
    last_accessed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ShareDatasetRequest(BaseModel):
    """Request to share dataset with another user"""
    email: str  # Email of user to share with
    permission: str = Field("view", pattern="^(view|edit|admin)$")
    message: Optional[str] = None  # Optional message to recipient


class ShareDatasetResponse(BaseModel):
    """Response after sharing dataset"""
    success: bool
    shared_with_user_id: str
    permission: str
    share_link: Optional[str] = None  # If generating public link


class DashboardCreate(BaseModel):
    """Request to create dashboard"""
    name: str
    description: Optional[str] = None
    layout: Dict[str, Any]
    is_default: bool = False


class DashboardResponse(BaseModel):
    """Dashboard information response"""
    dashboard_id: str
    dataset_id: str
    user_id: str
    name: str
    description: Optional[str]
    layout: Dict[str, Any]
    is_default: bool
    is_template: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

from typing import List, Optional, Any
from pydantic import BaseModel

class DataFilter(BaseModel):
    """Single filter condition"""
    field: str
    operator: str  # eq, ne, gt, gte, lt, lte, in, between, contains
    value: Any


class DataQuery(BaseModel):
    """Flexible data query request"""
    filters: Optional[List[DataFilter]] = None
    columns: Optional[List[str]] = None
    companies: Optional[List[str]] = None
    years: Optional[List[int]] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
    limit: Optional[int] = None
    offset: int = 0

class SavedQueryCreate(BaseModel):
    """Request to save query"""
    name: str
    description: Optional[str] = None
    data_source: str
    query_config: Dict[str, Any]
    is_public: bool = False


class SavedQueryResponse(BaseModel):
    """Saved query information response"""
    query_id: str
    dataset_id: Optional[str]
    name: str
    description: Optional[str]
    data_source: str
    query_config: Dict[str, Any]
    is_public: bool
    usage_count: int
    created_at: datetime
    last_used_at: Optional[datetime]
    
    class Config:
        from_attributes = True