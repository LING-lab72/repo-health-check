"""Tests for exported HTML report escaping."""

from backend.routes.export import _diagnosis_row, _dimension_row, _radar_svg


def test_dimension_row_escapes_name_and_clamps_score():
    row = _dimension_row({"dimension": "<script>alert(1)</script>", "score": "999"})

    assert "<script>" not in row
    assert "&lt;script&gt;" in row
    assert "100%" in row


def test_diagnosis_row_escapes_advice():
    row = _diagnosis_row({
        "severity": "high",
        "advice": "<img src=x onerror=alert(1)>",
        "confidence": "88",
        "estimated_hours": "2",
    })

    assert "<img" not in row
    assert "&lt;img" in row
    assert "88%" in row


def test_radar_svg_escapes_labels():
    svg = _radar_svg([
        {"dimension": "<script>", "score": 80},
        {"dimension": "tests", "score": 70},
        {"dimension": "docs", "score": 60},
    ])

    assert "<script>" not in svg
    assert "&lt;script&gt;" in svg
    assert "Dimension radar chart" in svg
