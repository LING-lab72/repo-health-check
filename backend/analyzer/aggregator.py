"""Analysis aggregator: run 6 analyzers and compute weighted health score."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.ai.diagnose import ai_diagnose
from backend.analyzer.code_quality.analyzer import CodeQualityAnalyzer
from backend.analyzer.test_coverage.analyzer import TestCoverageAnalyzer
from backend.analyzer.architecture.analyzer import ArchitectureAnalyzer
from backend.analyzer.documentation.analyzer import DocumentationAnalyzer
from backend.analyzer.dependency_security.analyzer import DependencySecurityAnalyzer
from backend.analyzer.engineering.analyzer import EngineeringAnalyzer
from backend.analyzer.config import load_health_spec

ANALYZERS = [
    CodeQualityAnalyzer(),
    TestCoverageAnalyzer(),
    ArchitectureAnalyzer(),
    DocumentationAnalyzer(),
    DependencySecurityAnalyzer(),
    EngineeringAnalyzer(),
]


def _get_badge_level(score: float) -> dict[str, str]:
    """Map health score to badge level and color."""
    spec = load_health_spec()
    badge_levels = spec.get("badge_levels", {})

    for level in sorted(badge_levels.values(), key=lambda x: x["min"], reverse=True):
        if score >= level["min"]:
            return {
                "level": level["label"],
                "color": level["color"],
                "description": level["description"],
            }

    return {"level": "D", "color": "red", "description": "差"}


def _compute_health_score(dimensions: list[dict[str, Any]]) -> float:
    """Compute weighted health score from dimension results and spec weights."""
    spec = load_health_spec()
    dims_config = spec.get("dimensions", {})

    total = 0.0
    total_weight = 0.0

    for dim in dimensions:
        dim_name = dim["dimension"]
        config = dims_config.get(dim_name, {})
        weight = config.get("weight", 1 / 6)
        total += dim["score"] * weight
        total_weight += weight

    score = round(total / total_weight, 2) if total_weight > 0 else 0.0
    return max(0.0, min(100.0, score))


async def aggregate(
    repo_path: Path,
    repo_url: str,
    skip_ai: bool = False,
    ai_api_key: str | None = None,
) -> dict[str, Any]:
    """Run all 6 analyzers against a repo and produce aggregated health report."""
    loop = asyncio.get_running_loop()

    # Run 6 analyzers in parallel
    tasks = [loop.run_in_executor(None, a.analyze, repo_path) for a in ANALYZERS]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    dimensions: list[dict[str, Any]] = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            dimensions.append({
                "dimension": getattr(ANALYZERS[i].__class__, "__name__", "unknown"),
                "score": 0.0,
                "details": {"error": str(r)},
                "issues": [f"Analysis failed: {r}"],
            })
        else:
            dimensions.append({
                "dimension": r.dimension,
                "score": r.score,
                "details": r.details,
                "issues": r.issues,
            })

    health_score = _compute_health_score(dimensions)
    badge = _get_badge_level(health_score)

    # AI diagnosis (skip if requested)
    try:
        ai_diagnosis_result = (
            await ai_diagnose(dimensions, repo_url, api_key_override=ai_api_key)
            if not skip_ai
            else []
        )
    except Exception:
        ai_diagnosis_result = []

    return {
        "repo_url": repo_url,
        "health_score": health_score,
        "badge_level": badge["level"],
        "badge_color": badge["color"],
        "badge_description": badge["description"],
        "dimensions": dimensions,
        "ai_diagnosis": ai_diagnosis_result,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }
