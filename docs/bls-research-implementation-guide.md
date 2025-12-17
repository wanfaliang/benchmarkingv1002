# BLS Research Module Implementation Guide

This document provides a comprehensive guide for implementing BLS (Bureau of Labor Statistics) survey explorers in the Finexus Research module.

---

## 1. The DATA Project

### What is the DATA Project?

The DATA project (`finexus-data-collector`) is a separate data collection and processing system that:
- Collects economic data from various sources (BLS, BEA, Treasury, NASDAQ, etc.)
- Processes and stores data in a PostgreSQL database
- Provides an admin interface for data management

### Location

```
D:\finexus-data-collector
```
and official data and introduction files are in its
\data\bls\{survey}\*.*
Look into specifically the files {survey}.txt
### Useful Resources from DATA

While the DATA project has only implemented explorers for CU, LN, LA, and CE surveys, it contains:

- **Documentation**: `D:\finexus-data-collector\docs/*.md` - Survey-specific documentation
- **Database Models**: Source models that we copied to this project
- **API Patterns**: Reference implementations for the 4 implemented surveys

**Note**: For surveys beyond CU, LN, LA, and CE, we must implement from scratch using only the database models and BLS documentation, and we can retrieve all the real and latest data from DATA to undertand such as series characteristic, various codes, such as sectors, industries, occupation, to name a few.

---

## 2. Dual Database Architecture

### Overview

Finexus uses two separate databases:

| Database | Environment Variable | Purpose | Access |
|----------|---------------------|---------|--------|
| **Finexus App DB** | `DATABASE_URL` | Users, analyses, datasets, app data | Read/Write |
| **DATA DB** | `DATA_DATABASE_URL` | Economic data (BLS, BEA, Treasury, etc.) | **Read-Only** |

### Configuration (`.env`)

```env
# Primary database (Finexus app)
DATABASE_URL=postgresql://user:password@localhost:5432/finexus_app

# DATA project database (read-only)
DATA_DATABASE_URL=postgresql://user:password@localhost:5432/data
```

### Database Connection (`backend/app/database.py`)

```python
# Primary database session
def get_db():
    """Get database session for Finexus app database"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DATA database session (read-only)
def get_data_db():
    """Get database session for DATA database (read-only)"""
    if DataSessionLocal is None:
        raise RuntimeError("DATA_DATABASE_URL not configured")
    db = DataSessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Usage in Endpoints

```python
from ....database import get_data_db

@router.get("/some-endpoint")
def get_data(db: Session = Depends(get_data_db)):
    # Query DATA database (read-only)
    results = db.query(SomeModel).all()
    return results
```

---

## 3. The Research Module

### Purpose

The Research module provides data exploration interfaces for economic and financial data sourced from the DATA project:

- **BLS Surveys**: Employment, prices, wages, productivity data
- **Treasury**: Yield curves, interest rates
- **BEA**: GDP, trade, industry data
- **Financial/Market**: Stock screeners, market data

### Architecture

```
User Request
    │
    ▼
Frontend (React/JSX)
    │
    ▼
API Layer (FastAPI)
    │
    ▼
DATA Database (PostgreSQL, Read-Only)
```

---

## 4. Project File Structure

### Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, router registration
│   ├── config.py                  # Settings from .env
│   ├── database.py                # DB connections (get_db, get_data_db)
│   │
│   ├── api/                       # API endpoints
│   │   ├── auth.py                # Authentication endpoints
│   │   ├── research/              # Research module
│   │   │   ├── __init__.py
│   │   │   ├── treasury.py        # Treasury research endpoints
│   │   │   └── bls/               # BLS survey explorers
│   │   │       ├── __init__.py
│   │   │       ├── cu_schemas.py  # CU Pydantic schemas
│   │   │       ├── cu_explorer.py # CU API endpoints
│   │   │       ├── ln_schemas.py
│   │   │       ├── ln_explorer.py
│   │   │       ├── la_schemas.py
│   │   │       ├── la_explorer.py
│   │   │       ├── ce_schemas.py
│   │   │       └── ce_explorer.py
│   │   └── ...
│   │
│   ├── core/                      # Core utilities
│   │   ├── deps.py                # get_current_user dependency
│   │   └── security.py            # JWT token handling
│   │
│   ├── models/                    # Finexus app models (users, etc.)
│   │
│   └── data_models/               # DATA database models (read-only)
│       ├── __init__.py
│       ├── bls_models.py          # All BLS survey models
│       ├── treasury_models.py     # Treasury data models
│       └── bea_models.py          # BEA data models
```

### Frontend Structure

```
frontend/
├── src/
│   ├── App.js                     # Routes configuration
│   ├── services/
│   │   └── api.js                 # API client functions
│   ├── layouts/
│   │   └── BLSLayout.jsx          # BLS navigation tabs
│   └── pages/
│       └── bls/
│           ├── CUExplorer.jsx     # Consumer Price Index
│           ├── LNExplorer.jsx     # Labor Force Statistics
│           ├── LAExplorer.jsx     # Local Area Unemployment
│           └── CEExplorer.jsx     # Current Employment Statistics
```

### Key Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (DB URLs, API keys, secrets) |
| `backend/app/config.py` | Pydantic settings class |
| `backend/app/database.py` | Database connections |
| `backend/app/main.py` | FastAPI app and router registration |
| `frontend/src/App.js` | React routes |
| `frontend/src/layouts/BLSLayout.jsx` | BLS tab navigation |

---

## 5. User Authentication

### How It Works

All Research module endpoints require authentication via JWT tokens.

### Injecting Authentication

```python
from ....api.auth import get_current_user

@router.get("/dimensions")
def get_dimensions(
    db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)  # Requires login
):
    # current_user is available if needed
    return db.query(SomeModel).all()
```

### Frontend Token Handling

The frontend automatically includes the JWT token in requests via axios interceptor in `api.js`:

```javascript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## 6. Implemented BLS Surveys

### Overview

| Survey | Code | Full Name | Status |
|--------|------|-----------|--------|
| CU | Consumer Price Index - All Urban | Implemented |
| LN | Labor Force Statistics | Implemented |
| LA | Local Area Unemployment Statistics | Implemented |
| CE | Current Employment Statistics | Implemented |

### Common Patterns

All implemented surveys follow these patterns:

#### Backend Structure

1. **Schemas** (`{survey}_schemas.py`):
   - Dimension models (areas, items, industries, etc.)
   - Series models
   - Data point models
   - Overview/analytics response models
   - Timeline response models

2. **Endpoints** (`{survey}_explorer.py`):
   - `GET /dimensions` - Available filter dimensions
   - `GET /series` - List series with filters
   - `GET /series/{id}/data` - Time series data
   - `GET /overview` - Headline statistics
   - `GET /overview/timeline` - Overview timeline data
   - Survey-specific analysis endpoints

#### Frontend Structure

1. **API Functions** (`api.js`):
   ```javascript
   export const xxResearchAPI = {
     getDimensions: () => api.get('/api/research/bls/xx/dimensions'),
     getSeries: (params) => api.get('/api/research/bls/xx/series', { params }),
     getSeriesData: (id, params) => api.get(`/api/research/bls/xx/series/${id}/data`, { params }),
     getOverview: () => api.get('/api/research/bls/xx/overview'),
     getOverviewTimeline: (monthsBack) => api.get('/api/research/bls/xx/overview/timeline', { params: { months_back: monthsBack } }),
     // Survey-specific endpoints...
   };
   ```

2. **Explorer Page** (`XXExplorer.jsx`):
   - Overview section with headline metrics
   - Analysis sections with tables and charts
   - Time range dropdowns for filtering
   - Timeline selectors for point-in-time data
   - Series explorer for raw data access

#### UI Components

Standard components used across all explorers:

- `Card` - Section container
- `SectionHeader` - Colored section titles
- `Select` - Dropdown selectors
- `TimelineSelector` - Point-in-time selection
- `ChangeIndicator` - MoM/YoY change display
- `LoadingSpinner` - Loading state
- Recharts for visualization (LineChart, BarChart)

### Survey-Specific Details

#### CU - Consumer Price Index

- **Dimensions**: Areas, Items, Periodicity
- **Key Metrics**: Index values, inflation rates
- **Special Features**: Item hierarchy, regional breakdown

#### LN - Labor Force Statistics

- **Dimensions**: Many demographic dimensions (age, sex, race, education, etc.)
- **Key Metrics**: Unemployment rate, labor force participation
- **Special Features**: Complex filtering, headline unemployment series

#### LA - Local Area Unemployment

- **Dimensions**: Areas (states, metros), Measures
- **Key Metrics**: Unemployment rate, labor force, employed/unemployed counts
- **Special Features**: Geographic map visualization, state/metro comparison

#### CE - Current Employment Statistics

- **Dimensions**: Industries, Supersectors, Data Types
- **Key Metrics**: Employment (thousands), earnings, hours
- **Special Features**: Industry hierarchy, earnings analysis

---

## 7. Implementation Guide for New Surveys

### Step 1: Identify Available Models

Check `backend/app/data_models/bls_models.py` for the survey's models:

```python
# Example: Look for models starting with survey prefix
class XXArea(Base):
class XXItem(Base):
class XXSeries(Base):
class XXData(Base):
```

### Step 2: Create Backend Schemas

Create `backend/app/api/research/bls/xx_schemas.py`:

```python
from typing import List, Optional
from pydantic import BaseModel

# Dimension models
class XXDimensionItem(BaseModel):
    code: str
    name: str
    # ... dimension-specific fields

    class Config:
        from_attributes = True

class XXDimensions(BaseModel):
    dimension1: List[XXDimension1Item]
    dimension2: List[XXDimension2Item]
    # ...

# Series models
class XXSeriesInfo(BaseModel):
    series_id: str
    series_title: str
    # ... series metadata

# Data models
class XXDataPoint(BaseModel):
    year: int
    period: str
    period_name: str
    value: Optional[float] = None

# Response models
class XXOverviewResponse(BaseModel):
    survey_code: str = "XX"
    # ... overview fields
```

### Step 3: Create Backend Endpoints

Create `backend/app/api/research/bls/xx_explorer.py`:

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ....database import get_data_db
from ....api.auth import get_current_user
from .xx_schemas import XXDimensions, XXSeriesListResponse, ...
from ....data_models.bls_models import XXArea, XXSeries, XXData, BLSPeriod

router = APIRouter(
    prefix="/api/research/bls/xx",
    tags=["BLS XX Survey"]
)

@router.get("/dimensions", response_model=XXDimensions)
def get_dimensions(
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    areas = db.query(XXArea).order_by(XXArea.sort_sequence).all()
    # ... query other dimensions
    return XXDimensions(areas=areas, ...)

@router.get("/overview")
def get_overview(
    db: Session = Depends(get_data_db),
    current_user = Depends(get_current_user)
):
    # Build overview with latest data
    pass

# ... more endpoints
```

### Step 4: Register Router

Update `backend/app/main.py`:

```python
from .api.research.bls import xx_explorer as xx_research

# In router registration section:
app.include_router(xx_research.router)
```

### Step 5: Create Frontend API Functions

Update `frontend/src/services/api.js`:

```javascript
export const xxResearchAPI = {
  getDimensions: () => api.get('/api/research/bls/xx/dimensions'),
  getSeries: (params = {}) => api.get('/api/research/bls/xx/series', { params }),
  // ... more functions
};
```

### Step 6: Create Frontend Explorer Page

Create `frontend/src/pages/bls/XXExplorer.jsx`:

- Follow the pattern from existing explorers
- Use consistent components (Card, SectionHeader, etc.)
- Include time range dropdowns and timeline selectors
- Use Recharts for visualizations

### Step 7: Add Navigation Tab

Update `frontend/src/layouts/BLSLayout.jsx`:

```javascript
const BLS_TABS = [
  // ... existing tabs
  { id: 'xx', label: 'XX', title: 'Survey Full Name', available: true },
];
```

### Step 8: Add Route

Update `frontend/src/App.js`:

```javascript
import XXExplorer from './pages/bls/XXExplorer';

// In BLS routes:
<Route path="xx" element={<XXExplorer />} />
```

---

## 8. Available BLS Survey Models

The following surveys have models in `backend/app/data_models/bls_models.py`:

| Prefix | Survey Name | Models Available |
|--------|------------|------------------|
| AP | Average Price | APItem, APSeries, APData |
| CU | Consumer Price Index - Urban | CUArea, CUItem, CUSeries, CUData |
| CW | Consumer Price Index - Urban Wage Earners | CWArea, CWItem, CWSeries, CWData |
| SU | Consumer Price Index - Size Class | SUArea, SUItem, SUSeries, SUData |
| LA | Local Area Unemployment | LAArea, LAMeasure, LASeries, LAData |
| CE | Current Employment Statistics | CEIndustry, CESupersector, CEDataType, CESeries, CEData |
| PC | Producer Price Index - Commodity | PCIndustry, PCProduct, PCSeries, PCData |
| WP | Producer Price Index - Final Demand | WPGroup, WPItem, WPSeries, WPData |
| SM | State & Metro Employment | SMState, SMArea, SMSupersector, SMIndustry, SMSeries, SMData |
| JT | Job Openings & Labor Turnover (JOLTS) | JTDataElement, JTIndustry, JTState, JTArea, JTSeries, JTData |
| EC | Employment Cost Index | ECCompensation, ECGroup, ECOwnership, ECSeries, ECData |
| OE | Occupational Employment | OEAreaType, OEDataType, OEIndustry, OEOccupation, OESeries, OEData |
| PR | Productivity | PRClass, PRMeasure, PRDuration, PRSector, PRSeries, PRData |
| IP | Industrial Production | IPSector, IPIndustry, IPMeasure, IPDuration, IPSeries, IPData |
| TU | American Time Use Survey | TUStatType, TUActivityCode, TUSex, TUAge, TUSeries, TUData |
| LN | Labor Force Statistics | LNLaborForceStatus, LNPeriodicity, LNAge, LNSeries, LNData, ... (many dimension tables) |
| EI | Employment Index | EIIndex, EISeries, EIData |
| BD | Business Employment Dynamics | BDState, BDIndustry, BDDataClass, BDSeries, BDData |

---

## 9. Best Practices

### Efficiency

1. **Use pagination** for large result sets (`limit`, `offset` parameters)
2. **Index frequently queried fields** in database models
3. **Cache static dimension data** on the frontend
4. **Load data lazily** - don't fetch all data on page load

### Quality

1. **Validate inputs** using Pydantic schemas
2. **Handle null values** gracefully in responses
3. **Include proper error messages** for failed queries
4. **Test with various data ranges** (monthly, yearly, all-time)

### Consistency

1. **Follow existing patterns** - study CU, LN, LA, CE implementations
2. **Use standard components** - don't reinvent UI elements
3. **Maintain naming conventions**:
   - Backend: `{survey}_schemas.py`, `{survey}_explorer.py`
   - Frontend: `{Survey}Explorer.jsx`
   - API prefix: `/api/research/bls/{survey}`

4. **Include standard features**:
   - Time range dropdown
   - Timeline selector for point-in-time data
   - Table with all metric columns (Value, MoM Change, MoM %, YoY Change, YoY %)
   - Charts for visualization
   - Series explorer for raw data

### Documentation

1. **Comment complex queries** in endpoint code
2. **Document schema fields** with descriptions
3. **Update this guide** when adding new surveys

---

## 10. Resources

### BLS Documentation

- BLS Website: https://www.bls.gov/
- Series ID Formats: https://www.bls.gov/help/hlpforma.htm
- API Documentation: https://www.bls.gov/developers/

### DATA Project Documentation

- Location: `D:\finexus-data-collector\docs\`
- May contain survey-specific notes and data dictionaries

### Code References

- Implemented surveys: `backend/app/api/research/bls/`
- Data models: `backend/app/data_models/bls_models.py`
- Frontend pages: `frontend/src/pages/bls/`

---

*Last Updated: December 2024*
