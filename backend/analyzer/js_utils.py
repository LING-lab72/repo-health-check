"""Utilities for JavaScript/TypeScript analysis."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

JS_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
TIMEOUT = 60


def has_js_files(repo_path: Path) -> bool:
    """Check if repo contains JS/TS source files."""
    for ext in JS_EXT:
        for _ in repo_path.rglob(f"*{ext}"):
            return True
    return False


def run_npx(repo_path: Path, args: list[str]) -> dict[str, Any] | None:
    """Run npx command in repo directory, parse JSON output.

    Returns parsed JSON or None on failure.
    """
    npx_install_flag = "--yes" if os.environ.get("ALLOW_NPX_INSTALL") == "1" else "--no-install"
    try:
        result = subprocess.run(
            ["npx", npx_install_flag] + args,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            cwd=str(repo_path),
        )
        if result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError, Exception):
        pass
    return None


def run_eslint(repo_path: Path) -> dict[str, Any]:
    """Run ESLint on JS/TS files, return parsed results.

    Falls back to basic rules if no .eslintrc found.
    """
    # Try project eslint, then fallback to basic
    config_args = []
    eslintrc = repo_path / ".eslintrc.js"
    eslintrc_json = repo_path / ".eslintrc.json"
    eslintrc_ts = repo_path / ".eslintrc.cjs"
    if not any(f.exists() for f in [eslintrc, eslintrc_json, eslintrc_ts]):
        # Use basic config for unconfigured repos
        config_args = ["--rule", "{\"no-unused-vars\": \"warn\", \"no-undef\": \"warn\"}"]

    result = run_npx(repo_path, [
        "eslint", ".", "--ext", ".js,.jsx,.ts,.tsx",
        "--format", "json",
        "--no-error-on-unmatched-pattern",
    ] + config_args)

    return result or {"messages": [], "errorCount": 0, "warningCount": 0}


def run_madge(repo_path: Path) -> dict[str, Any] | None:
    """Run madge to detect circular dependencies."""
    return run_npx(repo_path, [
        "madge", ".", "--extensions", "js,jsx,ts,tsx",
        "--circular", "--json",
    ])


def parse_coverage(repo_path: Path) -> dict[str, Any] | None:
    """Parse existing coverage reports (lcov or coverage-summary)."""
    # Try Istanbul coverage-summary.json
    for pattern in ["coverage/coverage-summary.json", ".nyc_output/out.json"]:
        p = repo_path / pattern
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if "total" in data:
                    return data["total"]
            except (json.JSONDecodeError, KeyError):
                pass
    # Try lcov.info
    lcov = repo_path / "coverage" / "lcov.info"
    if lcov.exists():
        lines_pct = _parse_lcov(lcov)
        if lines_pct is not None:
            return {"lines": {"pct": lines_pct}}
    return None


def _parse_lcov(path: Path) -> float | None:
    """Parse lcov.info for line coverage percentage."""
    try:
        text = path.read_text(encoding="utf-8")
        lf = 0
        lh = 0
        for line in text.split("\n"):
            if line.startswith("LF:"):
                lf += int(line.split(":")[1])
            elif line.startswith("LH:"):
                lh += int(line.split(":")[1])
        return round((lh / lf) * 100, 1) if lf > 0 else None
    except Exception:
        return None
