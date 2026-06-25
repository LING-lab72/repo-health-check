"""Repo Health Check - FastAPI Application"""
import os

from dotenv import load_dotenv

load_dotenv()  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from backend.routes import router  # noqa: E402

_origins_str = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5174,http://127.0.0.1:5174,http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
)
if _origins_str.strip() == "*":
    ALLOWED_ORIGINS: list[str] = ["*"]
    _allow_credentials = False
else:
    ALLOWED_ORIGINS = [o.strip() for o in _origins_str.split(",") if o.strip()]
    _allow_credentials = True

app = FastAPI(
    title="Repo Health Check",
    description="仓库健康体检工具 API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
