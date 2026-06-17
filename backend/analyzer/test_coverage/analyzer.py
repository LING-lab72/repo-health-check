"""Test coverage analysis: test file ratio, framework detection."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.analyzer.base import AnalysisResult, BaseAnalyzer
from backend.analyzer.config import weighted_average_score
from backend.analyzer.js_utils import parse_coverage

TEST_FILE_PATTERNS = [
    "test_*.py", "*_test.py", "test_*.ts", "*.test.ts", "test_*.tsx", "*.test.tsx",
    "*.spec.ts", "*.spec.tsx", "test_*.js", "*.test.js", "*.spec.js",
    "Test*.java", "*Test.java", "*_test.go",
]

_TEST_DIRS = {"tests", "test", "spec", "__tests__", "specs"}

TEST_FRAMEWORKS = {
    "pytest": ["pytest", "conftest.py", "tox.ini"],
    "unittest": ["import unittest", "from unittest import"],
    "jest": ["jest.config.", ".jestrc", "\"jest\""],
    "vitest": ["vitest.config.", "vitest"],
    "mocha": ["mocha", ".mocharc"],
    "junit": ["@Test", "import org.junit"],
    "go_testing": ["func Test", "_test.go"],
}


def _find_source_files(root: Path) -> list[Path]:
    """Find all source files (non-test)."""
    source_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go"}
    files: list[Path] = []
    for ext in source_exts:
        for p in root.rglob(f"*{ext}"):
            if len(files) >= 200:
                return files
            if any(seg in (".git", "node_modules", "__pycache__", ".venv", "venv", "dist")
                   for seg in p.parts):
                continue
            files.append(p)
    return files


def _is_test_file(path: Path) -> bool:
    """Check if a file is a test file by name or directory."""
    name = path.name.lower()
    parent_name = path.parent.name.lower()

    if parent_name in _TEST_DIRS:
        return True

    for pattern_parts in TEST_FILE_PATTERNS:
        parts = pattern_parts.split("/")
        file_part = parts[-1]
        if file_part.startswith("*"):
            if name.endswith(file_part[1:]):
                return True
        elif file_part.endswith("*"):
            if name.startswith(file_part[:-1]):
                return True
        elif path.match(pattern_parts[-1]):
            return True

    return False


def _score_test_file_ratio(root: Path) -> dict[str, Any]:
    """Score the ratio of test files to source files."""
    all_files = _find_source_files(root)
    test_files = [f for f in all_files if _is_test_file(f)]
    source_files = [f for f in all_files if not _is_test_file(f)]

    total = len(source_files) + len(test_files)
    if total == 0:
        return {"score": 0, "issues": ["No source files found"]}

    ratio = len(test_files) / max(len(source_files), 1)

    # Score: ratio >= 0.5 → excellent, 0.2-0.5 → good, <0.1 → poor
    if ratio >= 0.5:
        score = 95
    elif ratio >= 0.3:
        score = 80
    elif ratio >= 0.2:
        score = 65
    elif ratio >= 0.1:
        score = 45
    elif ratio > 0:
        score = 25
    else:
        score = 0

    issues: list[str] = []
    if ratio < 0.1:
        issues.append(f"测试文件比例过低: {ratio:.1%} (测试文件 {len(test_files)}, 源文件 {len(source_files)})")

    return {
        "score": score,
        "ratio": round(ratio, 3),
        "source_files": len(source_files),
        "test_files": len(test_files),
        "issues": issues,
    }


def _detect_test_frameworks(root: Path) -> dict[str, Any]:
    """Detect which test frameworks are in use."""
    found_frameworks: list[str] = []

    # Check config files
    for fw, markers in TEST_FRAMEWORKS.items():
        for marker in markers:
            # Config file markers
            if not marker.startswith("import") and not marker.startswith("func"):
                try:
                    config_files = list(root.rglob(marker))
                    if config_files:
                        # Skip node_modules
                        config_files = [cf for cf in config_files
                                        if "node_modules" not in str(cf)]
                    if config_files:
                        found_frameworks.append(fw)
                        break
                except Exception:
                    pass
            # Import/file pattern markers
            else:
                try:
                    for src in _find_source_files(root)[:50]:
                        content = src.read_text(encoding="utf-8", errors="ignore")
                        if marker in content:
                            found_frameworks.append(fw)
                            break
                    else:
                        continue
                    break
                except Exception:
                    pass

    found_frameworks = sorted(set(found_frameworks))

    # Score: multiple frameworks → good coverage strategy
    if len(found_frameworks) >= 2:
        score = 90
    elif len(found_frameworks) == 1:
        score = 75
    else:
        score = 10

    issues: list[str] = []
    if not found_frameworks:
        issues.append("未检测到测试框架")

    return {
        "score": score,
        "frameworks": found_frameworks,
        "issues": issues,
    }


def _score_coverage_percentage(root: Path) -> dict[str, Any]:
    """Estimate coverage from test file presence (actual coverage requires running tests).

    We use test_file_ratio as a proxy and check for coverage config files.
    """
    # Check for coverage config
    has_coverage_config = any(
        (root / f).exists()
        for f in [".coveragerc", "setup.cfg", "tox.ini", "pyproject.toml"]
    ) or any(root.rglob("coverage*.json"))

    test_result = _score_test_file_ratio(root)
    ratio = test_result.get("ratio", 0)

    # Estimate coverage from file ratio
    if ratio >= 0.5 and has_coverage_config:
        score = 85
    elif ratio >= 0.5:
        score = 70
    elif ratio >= 0.2:
        score = 50
    elif ratio > 0:
        score = 20
    else:
        score = 0

    return {
        "score": score,
        "has_coverage_config": has_coverage_config,
        "test_file_ratio": ratio,
        "issues": [] if ratio > 0 else ["无测试文件"],
    }


class TestCoverageAnalyzer(BaseAnalyzer):
    """Analyze test coverage: test file ratio, framework detection, coverage config."""

    def analyze(self, repo_path: Path) -> AnalysisResult:
        coverage = _score_coverage_percentage(repo_path)
        ratio_result = _score_test_file_ratio(repo_path)
        framework_result = _detect_test_frameworks(repo_path)

        # JS/TS: Parse existing coverage reports
        js_coverage = parse_coverage(repo_path)
        if js_coverage:
            lines_pct = js_coverage.get("lines", {}).get("pct", 0)
            if isinstance(lines_pct, (int, float)):
                coverage["js_coverage_percent"] = round(lines_pct, 1)
                if lines_pct >= 80:
                    coverage["score"] = max(coverage["score"], 90)
                elif lines_pct >= 50:
                    coverage["score"] = max(coverage["score"], 65)
                else:
                    coverage["score"] = max(coverage["score"], 30)

        scores = {
            "coverage_percentage": coverage["score"],
            "test_file_ratio": ratio_result["score"],
            "test_framework_detected": framework_result["score"],
        }

        scoring = weighted_average_score(scores, "test_coverage")
        all_issues = (
            coverage.get("issues", [])
            + ratio_result.get("issues", [])
            + framework_result.get("issues", [])
        )

        return AnalysisResult(
            dimension="test_coverage",
            score=scoring["score"],
            details={
                "sub_scores": scoring["sub_scores"],
                "coverage_estimate": coverage,
                "test_file_ratio": ratio_result,
                "frameworks": framework_result,
            },
            issues=all_issues[:20],
        )
