"""
Saved Screens API endpoints

CRUD operations for user-saved stock screens.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import time

from ...database import get_db, get_data_db
from ...models.stocks import SavedScreen, ScreenRun
from ...schemas.stocks import (
    SavedScreenCreate,
    SavedScreenUpdate,
    SavedScreenResponse,
    SavedScreenSummary,
    ScreenFilter,
    UniverseFilter,
    SortOrder,
    ScreenResponse,
    StockResult,
)
from ...core.deps import get_current_user
from ...models.user import User
from ...services.stocks import ScreenerService

router = APIRouter(prefix="/screens", tags=["screens"])


# =============================================================================
# Helper Functions
# =============================================================================

def screen_to_response(screen: SavedScreen) -> SavedScreenResponse:
    """Convert SavedScreen model to response schema."""
    return SavedScreenResponse(
        screen_id=screen.screen_id,
        user_id=screen.user_id,
        name=screen.name,
        description=screen.description,
        filters=screen.filters or [],
        universe=screen.universe,
        columns=screen.columns,
        sort_by=screen.sort_by,
        sort_order=screen.sort_order or "desc",
        is_template=screen.is_template,
        template_key=screen.template_key,
        last_run_at=screen.last_run_at,
        run_count=screen.run_count or 0,
        last_result_count=screen.last_result_count,
        created_at=screen.created_at,
        updated_at=screen.updated_at,
    )


def screen_to_summary(screen: SavedScreen) -> SavedScreenSummary:
    """Convert SavedScreen model to summary schema."""
    return SavedScreenSummary(
        screen_id=screen.screen_id,
        name=screen.name,
        description=screen.description,
        filter_count=len(screen.filters) if screen.filters else 0,
        is_template=screen.is_template,
        template_key=screen.template_key,
        last_run_at=screen.last_run_at,
        run_count=screen.run_count or 0,
        last_result_count=screen.last_result_count,
    )


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/", response_model=List[SavedScreenSummary])
def list_saved_screens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all saved screens for the current user.

    Returns a summary list (not full configuration).
    """
    screens = db.query(SavedScreen).filter(
        SavedScreen.user_id == current_user.user_id,
        SavedScreen.is_template == False
    ).order_by(SavedScreen.updated_at.desc()).all()

    return [screen_to_summary(s) for s in screens]


@router.post("/", response_model=SavedScreenResponse, status_code=status.HTTP_201_CREATED)
def create_saved_screen(
    screen_data: SavedScreenCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new saved screen for the current user.
    """
    # Convert Pydantic models to dict for JSON storage
    filters_json = [f.model_dump() for f in screen_data.filters]
    universe_json = screen_data.universe.model_dump() if screen_data.universe else None

    screen = SavedScreen(
        user_id=current_user.user_id,
        name=screen_data.name,
        description=screen_data.description,
        filters=filters_json,
        universe=universe_json,
        columns=screen_data.columns,
        sort_by=screen_data.sort_by,
        sort_order=screen_data.sort_order.value if screen_data.sort_order else "desc",
        is_template=False,
    )

    db.add(screen)
    db.commit()
    db.refresh(screen)

    return screen_to_response(screen)


@router.get("/{screen_id}", response_model=SavedScreenResponse)
def get_saved_screen(
    screen_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific saved screen by ID.

    Only returns screens owned by the current user.
    """
    screen = db.query(SavedScreen).filter(
        SavedScreen.screen_id == screen_id,
        SavedScreen.user_id == current_user.user_id
    ).first()

    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screen '{screen_id}' not found"
        )

    return screen_to_response(screen)


@router.put("/{screen_id}", response_model=SavedScreenResponse)
def update_saved_screen(
    screen_id: str,
    screen_data: SavedScreenUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing saved screen.

    Only updates fields that are provided.
    """
    screen = db.query(SavedScreen).filter(
        SavedScreen.screen_id == screen_id,
        SavedScreen.user_id == current_user.user_id
    ).first()

    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screen '{screen_id}' not found"
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

    db.commit()
    db.refresh(screen)

    return screen_to_response(screen)


@router.delete("/{screen_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_screen(
    screen_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a saved screen.

    Also deletes associated run history.
    """
    screen = db.query(SavedScreen).filter(
        SavedScreen.screen_id == screen_id,
        SavedScreen.user_id == current_user.user_id
    ).first()

    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screen '{screen_id}' not found"
        )

    # Delete associated runs
    db.query(ScreenRun).filter(ScreenRun.screen_id == screen_id).delete()

    # Delete the screen
    db.delete(screen)
    db.commit()


@router.post("/{screen_id}/duplicate", response_model=SavedScreenResponse)
def duplicate_saved_screen(
    screen_id: str,
    new_name: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Duplicate an existing saved screen.

    Creates a copy with a new name (defaults to "Copy of {original_name}").
    """
    original = db.query(SavedScreen).filter(
        SavedScreen.screen_id == screen_id,
        SavedScreen.user_id == current_user.user_id
    ).first()

    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screen '{screen_id}' not found"
        )

    duplicate = SavedScreen(
        user_id=current_user.user_id,
        name=new_name or f"Copy of {original.name}",
        description=original.description,
        filters=original.filters,
        universe=original.universe,
        columns=original.columns,
        sort_by=original.sort_by,
        sort_order=original.sort_order,
        is_template=False,
    )

    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)

    return screen_to_response(duplicate)


@router.post("/{screen_id}/log-run")
def log_screen_run(
    screen_id: str,
    result_count: int,
    execution_time_ms: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log a screen run and update the screen's usage stats.

    Called after running a saved screen to track usage.
    """
    screen = db.query(SavedScreen).filter(
        SavedScreen.screen_id == screen_id,
        SavedScreen.user_id == current_user.user_id
    ).first()

    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screen '{screen_id}' not found"
        )

    # Update screen stats
    screen.last_run_at = datetime.utcnow()
    screen.run_count = (screen.run_count or 0) + 1
    screen.last_result_count = result_count

    # Create run record
    run = ScreenRun(
        screen_id=screen_id,
        user_id=current_user.user_id,
        filters_snapshot=screen.filters,
        universe_snapshot=screen.universe,
        result_count=result_count,
        execution_time_ms=execution_time_ms,
    )

    db.add(run)
    db.commit()

    return {"success": True, "run_count": screen.run_count}


@router.post("/{screen_id}/run", response_model=ScreenResponse)
def run_saved_screen(
    screen_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    include_count: bool = Query(False, description="Include total count (slower)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    data_db: Session = Depends(get_data_db)
):
    """
    Run a saved screen and return results.

    This executes the screen's filters against the stock database and returns matching stocks.
    """
    screen = db.query(SavedScreen).filter(
        SavedScreen.screen_id == screen_id,
        SavedScreen.user_id == current_user.user_id
    ).first()

    if not screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screen '{screen_id}' not found"
        )

    start_time = time.time()

    # Convert stored JSON filters to Pydantic models
    filters = []
    if screen.filters:
        for f in screen.filters:
            filters.append(ScreenFilter(**f))

    universe = None
    if screen.universe:
        universe = UniverseFilter(**screen.universe)

    sort_order = SortOrder(screen.sort_order) if screen.sort_order else SortOrder.DESC

    # Run the screen
    screener = ScreenerService(data_db)
    results, total_count = screener.run_screen(
        filters=filters,
        universe=universe,
        columns=screen.columns,
        sort_by=screen.sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
        skip_count=not include_count,
    )

    execution_time_ms = int((time.time() - start_time) * 1000)

    # Update screen stats
    screen.last_run_at = datetime.utcnow()
    screen.run_count = (screen.run_count or 0) + 1
    screen.last_result_count = total_count if total_count > 0 else len(results)
    db.commit()

    # Convert results to StockResult objects
    stock_results = [StockResult(**r) for r in results]

    return ScreenResponse(
        total_count=total_count,
        returned_count=len(stock_results),
        offset=offset,
        limit=limit,
        results=stock_results,
        execution_time_ms=execution_time_ms
    )
