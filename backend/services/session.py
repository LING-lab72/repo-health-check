"""Simple cookie-based session using itsdangerous."""
from __future__ import annotations

import json
import os
from typing import Any

from itsdangerous import URLSafeSerializer

SECRET = os.environ.get("SESSION_SECRET")
if not SECRET:
    raise RuntimeError("SESSION_SECRET must be set; refusing to start with an insecure default")

_serializer = URLSafeSerializer(SECRET)


def encode_session(data: dict[str, Any]) -> str:
    """Encode session data to a signed cookie string."""
    return _serializer.dumps(json.dumps(data))


def decode_session(cookie: str) -> dict[str, Any]:
    """Decode a signed cookie string back to session data."""
    try:
        raw = _serializer.loads(cookie)
        return json.loads(raw)
    except Exception:
        return {}
