"""Compare two repositories side-by-side."""
from __future__ import annotations

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


@router.post("/compare")
async def compare_repos(req: CompareRequest) -> ApiResponse[dict]:
    """Analyze both repos and return side-by-side comparison."""
    repo_a = cache.normalize_url(req.repo_a)
    repo_b = cache.normalize_url(req.repo_b)

    results: dict[str, dict] = {}
    temp_dirs: list[Path] = []

    for label, url in [("repo_a", repo_a), ("repo_b", repo_b)]:
        try:
            repo_path, _ = clone_repo(url)
            temp_dirs.append(repo_path.parent)
            results[label] = await aggregate(repo_path, url)
        except CloneError as e:
            raise HTTPException(status_code=400, detail=f"Failed to clone {url}: {e}")

    # Cleanup
    for d in temp_dirs:
        shutil.rmtree(d, ignore_errors=True)

    return ApiResponse(
        code=0,
        message="success",
        data={
            "repo_a": results.get("repo_a"),
            "repo_b": results.get("repo_b"),
        },
    )
