from fastapi import APIRouter

from backend.routes.analyze import router as analyze_router
from backend.routes.badge import router as badge_router
from backend.routes.leaderboard import router as leaderboard_router
from backend.routes.history import router as history_router
from backend.routes.compare import router as compare_router
from backend.routes.vote import router as vote_router
from backend.routes.auth import router as auth_router
from backend.routes.export import router as export_router

router = APIRouter()
router.include_router(analyze_router)
router.include_router(badge_router)
router.include_router(leaderboard_router)
router.include_router(history_router)
router.include_router(compare_router)
router.include_router(vote_router)
router.include_router(auth_router)
router.include_router(export_router)

__all__ = ["router"]
