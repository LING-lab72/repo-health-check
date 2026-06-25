"""Badge SVG generation endpoint."""
from __future__ import annotations

import html

from fastapi import APIRouter, Response

from backend.constants import BADGE_COLORS, DEFAULT_BADGE_COLOR
from backend.services.cache import cache
from backend.services.storage import get_by_url_hash

router = APIRouter(prefix="/api")

SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{value_width}" height="20" fill="{color}"/>
    <rect width="{width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif"
     font-size="11" text-rendering="geometricPrecision">
    <text x="{label_x}" y="14">{label}</text>
    <text x="{value_x}" y="14">{value}</text>
  </g>
</svg>"""


def _char_width(text: str) -> int:
    """Estimate pixel width of text (rough: ~7px per char)."""
    return max(len(text) * 7, 20)


def _build_svg(label: str, value: str, color_hex: str) -> str:
    """Build a shields.io-style SVG badge."""
    # Escape dynamic text to prevent SVG injection (XSS)
    label_safe = html.escape(label, quote=True)
    value_safe = html.escape(value, quote=True)

    label_w = _char_width(label_safe) + 10
    value_w = _char_width(value_safe) + 10
    total_w = label_w + value_w

    return SVG_TEMPLATE.format(
        width=total_w,
        label_width=label_w,
        value_width=value_w,
        label_x=label_w // 2,
        value_x=label_w + value_w // 2,
        label=label_safe,
        value=value_safe,
        color=color_hex,
    )


@router.get("/badge/{repo_hash}")
async def get_badge(repo_hash: str):
    """Return a shields.io-style SVG badge for the given repo hash.

    Color mapping:
    - A → brightgreen (#4c1)
    - B → yellow (#dfb317)
    - C → orange (#fe7d37)
    - D → red (#e05d44)
    - unknown → lightgrey (#9f9f9f)
    """
    # 1. Try cache first
    result = cache.get_by_hash(repo_hash)

    # 2. Fallback to persistent storage
    if result is None:
        result = get_by_url_hash(repo_hash)

    if result is not None:
        level = result.get("badge_level", "?")
        color_key = result.get("badge_color", "lightgrey")
        color_hex = BADGE_COLORS.get(color_key, DEFAULT_BADGE_COLOR)
        value = level
    else:
        color_hex = BADGE_COLORS["lightgrey"]
        value = "unknown"

    svg = _build_svg(label="health", value=value, color_hex=color_hex)
    return Response(content=svg, media_type="image/svg+xml")
