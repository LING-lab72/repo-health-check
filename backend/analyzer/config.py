"""Load and cache health-spec.yaml for scoring."""
from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path
from typing import Any

import yaml


def _find_spec_path() -> Path:
    """Find sdd/health-spec.yaml relative to this file or project root."""
    env_root = os.environ.get("REPO_HEALTH_TEST_ROOT") or os.environ.get("REPO_HEALTH_ROOT")
    candidates = [
        Path(env_root) / "sdd" / "health-spec.yaml" if env_root else None,
        Path(__file__).resolve().parent.parent.parent.parent / "sdd" / "health-spec.yaml",
        Path.cwd() / "sdd" / "health-spec.yaml",
    ]
    for p in candidates:
        if p and p.exists():
            return p
    raise FileNotFoundError("health-spec.yaml not found. Expected at <project>/sdd/health-spec.yaml")


@lru_cache(maxsize=1)
def load_health_spec() -> dict[str, Any]:
    """Load and cache the health specification from sdd/health-spec.yaml."""
    path = _find_spec_path()
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_dimension_spec(dimension: str) -> dict[str, Any]:
    """Get the spec for a single dimension (e.g. 'code_quality')."""
    spec = load_health_spec()
    return spec["dimensions"][dimension]


def get_thresholds(dimension: str) -> dict[str, int]:
    """Get ordered thresholds for a dimension (highest first)."""
    spec = get_dimension_spec(dimension)
    th = spec["thresholds"]
    return {
        "excellent": th["excellent"],
        "good": th["good"],
        "warning": th["warning"],
        "critical": th["critical"],
    }


def get_sub_metrics(dimension: str) -> list[dict[str, Any]]:
    """Get sub-metrics list with their weights."""
    spec = get_dimension_spec(dimension)
    return spec["sub_metrics"]


def weighted_average_score(scores: dict[str, float], dimension: str) -> dict[str, Any]:
    """Compute weighted average from sub-metric scores.

    Args:
        scores: {sub_metric_key: score_0_100}
        dimension: dimension name (e.g. 'code_quality')

    Returns:
        dict with 'score', 'sub_scores', 'missing_keys'
    """
    sub_metrics = get_sub_metrics(dimension)
    total = 0.0
    total_weight = 0.0
    detail_scores: dict[str, dict[str, Any]] = {}
    missing: list[str] = []

    for sm in sub_metrics:
        key = sm["key"]
        weight = sm["weight"]
        if key in scores:
            val = scores[key]
            total += val * weight
            total_weight += weight
            detail_scores[key] = {"score": round(val, 1), "weight": weight, "name": sm["name"]}
        else:
            missing.append(key)
            detail_scores[key] = {"score": 0, "weight": weight, "name": sm["name"], "missing": True}

    score = round(total / total_weight, 2) if total_weight > 0 else 0.0
    return {
        "score": score,
        "sub_scores": detail_scores,
        "missing_keys": missing,
        "total_weight": round(total_weight, 4),
    }
