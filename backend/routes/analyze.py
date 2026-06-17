"""API routes for repo health analysis."""
from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from backend.analyzer.aggregator import aggregate
from backend.models.response import ApiResponse
from backend.services.cache import cache
from backend.services.clone import CloneError, CloneTimeoutError, clone_repo
from backend.services.storage import save_entry

router = APIRouter(prefix="/api")

# Track pending background tasks
_pending_tasks: set[str] = set()


class AnalyzeRequest(BaseModel):
    """Request body for POST /api/analyze."""

    repo_url: str = Field(..., description="GitHub repository URL")
    force_sync: bool = Field(default=False, description="If false, run in background")
    skip_ai: bool = Field(default=False, description="If true, skip AI diagnosis")


def _make_error(repo_url: str, msg: str) -> dict:
    return {
        "repo_url": repo_url,
        "health_score": 0,
        "badge_level": "?",
        "badge_color": "lightgrey",
        "badge_description": msg,
        "dimensions": [],
        "ai_diagnosis": [],
        "analyzed_at": "",
        "_error": msg,
    }


def _run_sync_aggregate(repo_path: Path, repo_url: str, skip_ai: bool = False) -> dict:
    """Run aggregate() synchronously in a new event loop.
    
    MUST be called from a thread (not the main async event loop).
    FastAPI automatically runs non-async endpoint handlers in a thread pool,
    and background tasks also run in threads — both are safe.
    """
    return asyncio.run(aggregate(repo_path, repo_url, skip_ai=skip_ai))


def _run_analysis(repo_url: str) -> None:
    """Background task: clone + analyze + cache. Runs in a thread (safe for asyncio.run)."""
    repo_path: Path | None = None
    url = cache.normalize_url(repo_url)
    task_hash = cache.url_hash(url)
    try:
        repo_path, _ = clone_repo(url)
        result = _run_sync_aggregate(repo_path, url)
    except Exception as e:
        err = _make_error(url, f"仓库克隆失败: {e}")
        cache.set(url, err)
        _pending_tasks.discard(task_hash)
        return
    finally:
        if repo_path is not None:
            shutil.rmtree(repo_path.parent, ignore_errors=True)

    cache.set(url, result)
    save_entry({
        "repo_url": url,
        "health_score": result["health_score"],
        "badge_level": result["badge_level"],
        "badge_color": result["badge_color"],
        "analyzed_at": result["analyzed_at"],
    })
    _pending_tasks.discard(task_hash)


@router.post("/analyze")
async def analyze_repo(req: AnalyzeRequest, background_tasks: BackgroundTasks) -> ApiResponse[dict]:
    """Start or retrieve repo health analysis."""
    repo_url = cache.normalize_url(req.repo_url)
    task_hash = cache.url_hash(repo_url)

    # 1. Cache hit — return immediately (but NOT for error results)
    cached = cache.get(repo_url)
    if cached is not None:
        if cached.get("_error"):
            # Error results are stale — network may have recovered.
            # Invalidate so we re-analyze instead of repeating the same error.
            cache.invalidate(repo_url)
        else:
            return ApiResponse(code=0, message="success (cached)", data=cached)

    # 2. Sync mode
    if req.force_sync:
        repo_path: Path | None = None
        loop = asyncio.get_running_loop()
        try:
            repo_path, _ = clone_repo(repo_url)
            try:
                result = await asyncio.wait_for(
                    loop.run_in_executor(
                        None, _run_sync_aggregate, repo_path, repo_url, req.skip_ai
                    ),
                    timeout=180.0,
                )
            except asyncio.TimeoutError:
                shutil.rmtree(repo_path.parent, ignore_errors=True)
                err = _make_error(repo_url, "分析超时（超过 180 秒），仓库可能过大")
                cache.set(repo_url, err)
                return ApiResponse(code=-1, message="timeout", data=err)
            finally:
                shutil.rmtree(repo_path.parent, ignore_errors=True)
        except (CloneError, CloneTimeoutError) as e:
            err = _make_error(repo_url, f"仓库克隆失败: {e}")
            cache.set(repo_url, err)
            return ApiResponse(code=-1, message=str(e), data=err)
        except Exception as e:
            err = _make_error(repo_url, f"分析失败: {e}")
            cache.set(repo_url, err)
            return ApiResponse(code=-1, message=str(e), data=err)

        cache.set(repo_url, result)
        save_entry({
            "repo_url": repo_url,
            "health_score": result["health_score"],
            "badge_level": result["badge_level"],
            "badge_color": result["badge_color"],
            "analyzed_at": result["analyzed_at"],
        })
        return ApiResponse(code=0, message="success", data=result)

    # 3. Async mode: background task
    _pending_tasks.add(task_hash)
    background_tasks.add_task(_run_analysis, repo_url)

    return ApiResponse(
        code=1,
        message="analyzing",
        data={"task_id": task_hash, "repo_url": repo_url, "status": "pending"},
    )



# ── Local self-analysis (sync, no clone) ──────────────────────────

@router.post("/analyze/local")
def analyze_local(skip_ai: bool = False) -> ApiResponse[dict]:
    """Analyze the Repo Health Check project itself — synchronous, no network.
    
    This is a regular (non-async) function so FastAPI runs it in a thread pool,
    allowing safe use of asyncio.run() on Windows.
    """
    import time as _time

    repo_path = Path(__file__).resolve().parent.parent.parent
    repo_url = cache.normalize_url("https://github.com/user/repo-health-check")

    cached = cache.get(repo_url)
    if cached is not None and not cached.get("_error"):
        return ApiResponse(code=0, message="success (cached)", data=cached)

    # Clear stale error cache so re-analysis works
    if cached and cached.get("_error"):
        cache.invalidate(repo_url)

    _start = _time.monotonic()
    try:
        result = _run_sync_aggregate(repo_path, repo_url, skip_ai=skip_ai)
    except Exception as e:
        import traceback
        err = _make_error(repo_url, f"本地分析失败: {e}\n{traceback.format_exc()}")
        cache.set(repo_url, err)
        return ApiResponse(code=-1, message=str(e), data=err)

    elapsed = round(_time.monotonic() - _start, 1)
    cache.set(repo_url, result)
    save_entry({
        "repo_url": repo_url,
        "health_score": result["health_score"],
        "badge_level": result["badge_level"],
        "badge_color": result["badge_color"],
        "analyzed_at": result["analyzed_at"],
    })
    return ApiResponse(code=0, message=f"success ({elapsed}s)", data=result)


# ── Status polling ────────────────────────────────────────────────

@router.get("/analyze/status")
async def analyze_status(
    task_id: str = "",
    repo_url: str | None = None,
) -> ApiResponse[dict]:
    """Check analysis status by task_id (repo URL hash).

    Prefer passing repo_url for exact cache lookup (avoids hash collision).
    When repo_url is not provided, falls back to hash iteration (legacy).
    """
    # Prefer exact lookup by URL when available
    normalized_url = cache.normalize_url(repo_url) if repo_url else None
    result = cache.get_by_hash(task_id, normalized_url)
    if result is not None:
        if result.get("_error"):
            return ApiResponse(
                code=0,
                message="failed",
                data={"status": "failed", "error": result["_error"]},
            )
        return ApiResponse(
            code=0,
            message="completed",
            data={"status": "completed", "result": result},
        )

    if task_id in _pending_tasks:
        return ApiResponse(
            code=0,
            message="pending",
            data={"status": "pending", "task_id": task_id},
        )

    return ApiResponse(
        code=0,
        message="not_found",
        data={"status": "not_found", "task_id": task_id},
    )
