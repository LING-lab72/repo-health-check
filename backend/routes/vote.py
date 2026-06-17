"""Voting API endpoint with rate limiting and GitHub OAuth support."""
from datetime import date

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from backend.models.response import ApiResponse
from backend.routes.auth import get_current_user
from backend.services.cache import cache
from backend.services.storage import cast_vote, get_all

router = APIRouter(prefix="/api")


class VoteRequest(BaseModel):
    """Request body for POST /api/vote."""

    repo_url: str = Field(..., description="GitHub repository URL to vote for")


def _client_ip(request: Request) -> str:
    """Extract client IP."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


@router.post("/vote")
async def vote_repo(request: Request, req: VoteRequest) -> ApiResponse[dict]:
    """Cast a vote for a repository."""
    repo_url = cache.normalize_url(req.repo_url)

    user = get_current_user(request)
    voter_id = str(user["user_id"]) if user else _client_ip(request)

    count = cast_vote(repo_url, voter_id)
    if count is None:
        raise HTTPException(status_code=429, detail="Vote too frequently, please wait")

    entries = get_all()
    week_start = date.today().isoformat()
    top = entries[0] if entries else None

    return ApiResponse(
        code=0,
        message="success",
        data={
            "repo_url": repo_url,
            "votes": count,
            "week_start": week_start,
            "current_leader": top["repo_url"] if top else None,
            "leader_score": top["health_score"] if top else 0,
        },
    )
