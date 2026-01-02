"""Main Stock Screener API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...database import get_db, get_data_db
from ...core.deps import get_current_user
from ...models.user import User
from ...models.stocks import SavedScreen, ScreenRun
from ...schemas.stocks import (
    ScreenRequest, ScreenResponse, StockResult,
    SavedScreenCreate, SavedScreenUpdate, SavedScreenResponse, SavedScreenSummary,
    UniverseStats, SectorInfo, ScreenFilter, UniverseFilter, SortOrder
)
from ...services.stocks import ScreenerService

router = APIRouter()


# =============================================================================
# Universe & Stats Endpoints
# =============================================================================

@router.get("/universe/stats")
def get_universe_stats(
    data_db: Session = Depends(get_data_db)
):
    """
    Get statistics about the stock universe.

    Returns total count, sector breakdown, exchange breakdown, and market cap distribution.
    """
    screener = ScreenerService(data_db)
    return screener.get_universe_stats()


@router.get("/universe/sectors")
def get_sectors(
    data_db: Session = Depends(get_data_db)
):
    """Get all available sectors with stock counts"""
    screener = ScreenerService(data_db)
    sectors = screener.get_sectors()
    return {"sectors": sectors}


@router.get("/universe/industries")
def get_industries(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    data_db: Session = Depends(get_data_db)
):
    """Get all available industries, optionally filtered by sector"""
    screener = ScreenerService(data_db)
    industries = screener.get_industries(sector)
    return {"industries": industries, "sector_filter": sector}


# =============================================================================
# Screening Endpoints
# =============================================================================

@router.post("/screen", response_model=ScreenResponse)
def run_screen(
    request: ScreenRequest,
    include_count: bool = Query(False, description="Include total count (slower)"),
    db: Session = Depends(get_db),
    data_db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run a stock screen with the specified filters.

    Returns stocks matching all filter criteria, sorted and paginated.

    Set include_count=true to get exact total_count (adds query time).
    """
    import time
    start_time = time.time()

    # Use the ScreenerService to run the screen against DATA database
    screener = ScreenerService(data_db)

    results, total_count = screener.run_screen(
        filters=request.filters,
        universe=request.universe,
        columns=request.columns,
        sort_by=request.sort_by,
        sort_order=request.sort_order or SortOrder.DESC,
        limit=request.limit,
        offset=request.offset,
        skip_count=not include_count,
    )

    execution_time_ms = int((time.time() - start_time) * 1000)

    # Convert results to StockResult objects
    stock_results = [StockResult(**r) for r in results]

    return ScreenResponse(
        total_count=total_count,
        returned_count=len(stock_results),
        offset=request.offset,
        limit=request.limit,
        results=stock_results,
        execution_time_ms=execution_time_ms
    )


# =============================================================================
# Saved Screens Endpoints
# =============================================================================

@router.get("/saved", response_model=List[SavedScreenSummary])
def list_saved_screens(
    include_templates: bool = Query(False, description="Include system templates"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all saved screens for the current user.

    Optionally include system templates.
    """
    query = db.query(SavedScreen).filter(SavedScreen.user_id == current_user.user_id)

    if not include_templates:
        query = query.filter(SavedScreen.is_template == False)

    screens = query.order_by(SavedScreen.updated_at.desc()).all()

    return [
        SavedScreenSummary(
            screen_id=s.screen_id,
            name=s.name,
            description=s.description,
            filter_count=len(s.filters) if s.filters else 0,
            is_template=s.is_template,
            template_key=s.template_key,
            last_run_at=s.last_run_at,
            run_count=s.run_count,
            last_result_count=s.last_result_count
        )
        for s in screens
    ]


@router.post("/saved", response_model=SavedScreenResponse)
def create_saved_screen(
    screen_data: SavedScreenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new saved screen"""
    saved_screen = SavedScreen(
        user_id=current_user.user_id,
        name=screen_data.name,
        description=screen_data.description,
        filters=[f.model_dump() for f in screen_data.filters] if screen_data.filters else [],
        universe=screen_data.universe.model_dump() if screen_data.universe else None,
        columns=screen_data.columns,
        sort_by=screen_data.sort_by,
        sort_order=screen_data.sort_order.value if screen_data.sort_order else "desc",
        is_template=False
    )

    db.add(saved_screen)
    db.commit()
    db.refresh(saved_screen)

    return saved_screen


@router.get("/saved/{screen_id}", response_model=SavedScreenResponse)
def get_saved_screen(
    screen_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific saved screen"""
    screen = db.query(SavedScreen).filter(
        SavedScreen.screen_id == screen_id,
        SavedScreen.user_id == current_user.user_id
    ).first()

    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved screen not found"
        )

    return screen


@router.put("/saved/{screen_id}", response_model=SavedScreenResponse)
def update_saved_screen(
    screen_id: str,
    screen_data: SavedScreenUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing saved screen"""
    screen = db.query(SavedScreen).filter(
        SavedScreen.screen_id == screen_id,
        SavedScreen.user_id == current_user.user_id
    ).first()

    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved screen not found"
        )

    # Update only provided fields
    if screen_data.name is not None:
        screen.name = screen_data.name
    if screen_data.description is not None:
        screen.description = screen_data.description
    if screen_data.filters is not None:
        screen.filters = [f.model_dump() for f in screen_data.filters]
    if screen_data.universe is not None:
        screen.universe = screen_data.universe.model_dump()
    if screen_data.columns is not None:
        screen.columns = screen_data.columns
    if screen_data.sort_by is not None:
        screen.sort_by = screen_data.sort_by
    if screen_data.sort_order is not None:
        screen.sort_order = screen_data.sort_order.value

    screen.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(screen)

    return screen


@router.delete("/saved/{screen_id}")
def delete_saved_screen(
    screen_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a saved screen"""
    screen = db.query(SavedScreen).filter(
        SavedScreen.screen_id == screen_id,
        SavedScreen.user_id == current_user.user_id
    ).first()

    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved screen not found"
        )

    if screen.is_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system templates"
        )

    # Delete associated screen runs first (cascade)
    db.query(ScreenRun).filter(ScreenRun.screen_id == screen_id).delete()

    db.delete(screen)
    db.commit()

    return {"message": "Screen deleted successfully", "screen_id": screen_id}


@router.post("/saved/{screen_id}/run", response_model=ScreenResponse)
def run_saved_screen(
    screen_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    data_db: Session = Depends(get_data_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run a saved screen and return results.

    Also updates the screen's last_run_at and run_count.
    """
    screen = db.query(SavedScreen).filter(
        SavedScreen.screen_id == screen_id,
        SavedScreen.user_id == current_user.user_id
    ).first()

    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved screen not found"
        )

    import time
    start_time = time.time()

    # Reconstruct filters and universe from saved screen
    filters = None
    if screen.filters:
        filters = [
            ScreenFilter(
                feature=f.get("feature"),
                operator=f.get("operator"),
                value=f.get("value")
            )
            for f in screen.filters
        ]

    universe = None
    if screen.universe:
        universe = UniverseFilter(**screen.universe)

    sort_order = SortOrder(screen.sort_order) if screen.sort_order else SortOrder.DESC

    # Use the ScreenerService to run the screen against DATA database
    screener = ScreenerService(data_db)

    results, total_count = screener.run_screen(
        filters=filters,
        universe=universe,
        columns=screen.columns,
        sort_by=screen.sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )

    execution_time_ms = int((time.time() - start_time) * 1000)

    # Convert results to StockResult objects
    stock_results = [StockResult(**r) for r in results]

    # Update screen run stats
    screen.last_run_at = datetime.utcnow()
    screen.run_count += 1
    screen.last_result_count = total_count

    # Log the run
    run_log = ScreenRun(
        screen_id=screen_id,
        user_id=current_user.user_id,
        filters_snapshot=screen.filters,
        universe_snapshot=screen.universe,
        result_count=total_count,
        execution_time_ms=execution_time_ms
    )
    db.add(run_log)
    db.commit()

    return ScreenResponse(
        total_count=total_count,
        returned_count=len(stock_results),
        offset=offset,
        limit=limit,
        results=stock_results,
        execution_time_ms=execution_time_ms
    )
