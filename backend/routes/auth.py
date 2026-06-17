"""GitHub OAuth authentication."""
import os
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request, Response

from backend.models.response import ApiResponse
from backend.services.session import encode_session, decode_session

router = APIRouter(prefix="/api/auth")

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "")
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
SESSION_COOKIE = "repo_health_session"
COOKIE_MAX_AGE = 86400 * 7  # 7 days


def _backend_url(request: Request) -> str:
    """Get the backend base URL from request."""
    return str(request.base_url).rstrip("/")


@router.get("/github")
async def github_login(request: Request):
    """Redirect to GitHub OAuth authorization page."""
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GITHUB_CLIENT_ID not configured")
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": f"{_backend_url(request)}/api/auth/callback",
        "scope": "read:user",
    }
    return Response(
        status_code=302,
        headers={"Location": f"{GITHUB_AUTH_URL}?{urlencode(params)}"},
    )


@router.get("/callback")
async def github_callback(code: str, request: Request, response: Response):
    """Handle GitHub OAuth callback: exchange code for token, get user info."""
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="OAuth not configured")

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GITHUB_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token")

        # Get user info
        user_resp = await client.get(
            GITHUB_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_resp.json()

    # Store user in session
    session = {
        "user_id": user_data.get("id"),
        "login": user_data.get("login"),
        "avatar_url": user_data.get("avatar_url"),
    }

    cookie = encode_session(session)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=cookie,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
    )

    # Redirect to frontend
    frontend = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    return Response(status_code=302, headers={"Location": frontend})


def get_current_user(request: Request) -> dict | None:
    """Extract current user from session cookie. Returns None if not logged in."""
    cookie = request.cookies.get(SESSION_COOKIE)
    if not cookie:
        return None
    session = decode_session(cookie)
    if session.get("user_id"):
        return session
    return None


@router.get("/me")
async def get_me(request: Request) -> ApiResponse[dict | None]:
    """Return current logged-in user info."""
    user = get_current_user(request)
    if user:
        return ApiResponse(code=0, message="success", data=user)
    return ApiResponse(code=0, message="not_logged_in", data=None)
