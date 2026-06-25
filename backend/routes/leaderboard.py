"""Leaderboard API endpoint."""
from fastapi import APIRouter, Query

from backend.models.response import ApiResponse
from backend.services.storage import get_all, get_total_count

router = APIRouter(prefix="/api")


@router.get("/leaderboard")
async def get_leaderboard(
    page: int | None = Query(default=None, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[list[dict] | dict]:
    """Return all persisted analysis results sorted by health_score descending."""
    if page is None:
        return ApiResponse(
            code=0,
            message="success",
            data=get_all(),
        )

    total = get_total_count()
    offset = (page - 1) * page_size
    items = get_all(limit=page_size, offset=offset)
    return ApiResponse(
        code=0,
        message="success",
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": offset + len(items) < total,
        },
    )
