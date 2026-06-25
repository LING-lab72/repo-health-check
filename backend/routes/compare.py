"""Compare two repositories side-by-side."""
from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.analyzer.aggregator import aggregate
from backend.models.response import ApiResponse
from backend.services.cache import cache
from backend.services.clone import CloneError, clone_repo

router = APIRouter(prefix="/api")


class CompareRequest(BaseModel):
    """Request body for POST /api/compare."""

    repo_a: str = Field(..., description="First GitHub repository URL")
    repo_b: str = Field(..., description="Second GitHub repository URL")
    skip_ai: bool = Field(default=False, description="Skip AI diagnosis during comparison")


@router.post("/compare")
async def compare_repos(req: CompareRequest) -> ApiResponse[dict]:
    """Analyze both repos and return side-by-side comparison."""
    repo_a = cache.normalize_url(req.repo_a)
    repo_b = cache.normalize_url(req.repo_b)

    async def analyze_one(url: str) -> dict:
        cached = cache.get(url)
        if cached is not None and not cached.get("_error"):
            return cached

        repo_path: Path | None = None
        try:
            repo_path, _ = await asyncio.to_thread(clone_repo, url)
            result = await aggregate(repo_path, url, skip_ai=req.skip_ai)
            cache.set(url, result)
            return result
        finally:
            if repo_path is not None:
                shutil.rmtree(repo_path.parent, ignore_errors=True)

    try:
        result_a, result_b = await asyncio.gather(analyze_one(repo_a), analyze_one(repo_b))
    except CloneError as e:
        raise HTTPException(status_code=400, detail=f"Failed to clone repository: {e}")

    return ApiResponse(
        code=0,
        message="success",
        data={
            "repo_a": result_a,
            "repo_b": result_b,
        },
    )
