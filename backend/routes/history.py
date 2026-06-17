"""History API endpoint."""
from fastapi import APIRouter

from backend.models.response import ApiResponse
from backend.services.storage import get_history

router = APIRouter(prefix="/api")


@router.get("/history/{repo_url:path}")
async def get_analysis_history(repo_url: str) -> ApiResponse[list[dict]]:
    """Return all historical analysis entries for a repository."""
    history = get_history(repo_url)
    return ApiResponse(
        code=0,
        message="success",
        data=history,
    )
