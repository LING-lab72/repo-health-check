"""Leaderboard API endpoint."""
from fastapi import APIRouter

from backend.models.response import ApiResponse
from backend.services.storage import get_all

router = APIRouter(prefix="/api")


@router.get("/leaderboard")
async def get_leaderboard() -> ApiResponse[list[dict]]:
    """Return all persisted analysis results sorted by health_score descending."""
    return ApiResponse(
        code=0,
        message="success",
        data=get_all(),
    )
