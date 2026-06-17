"""Tests for badge SVG generation."""
from backend.routes.badge import _build_svg, BADGE_COLORS


def test_build_svg_structure():
    svg = _build_svg(label="health", value="A", color_hex="#4c1")
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert "health" in svg
    assert "A" in svg
    assert "#4c1" in svg


def test_build_svg_unknown():
    svg = _build_svg(label="health", value="unknown", color_hex="#9f9f9f")
    assert "unknown" in svg


def test_badge_colors_all_defined():
    assert BADGE_COLORS["brightgreen"] == "#4c1"
    assert BADGE_COLORS["red"] == "#e05d44"
    assert BADGE_COLORS["orange"] == "#fe7d37"
    assert BADGE_COLORS["yellow"] == "#dfb317"
    assert BADGE_COLORS["lightgrey"] == "#9f9f9f"


def test_build_svg_all_levels():
    """Verify SVG renders for all badge levels."""
    colors = {
        "A": "#4c1",
        "B": "#dfb317",
        "C": "#fe7d37",
        "D": "#e05d44",
    }
    for level, color in colors.items():
        svg = _build_svg(label="health", value=level, color_hex=color)
        assert level in svg
        assert color in svg
