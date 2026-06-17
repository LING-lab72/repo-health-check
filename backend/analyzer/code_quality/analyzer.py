"""Code quality analysis using radon (Python CC/MI) and lizard (multi-language CC)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from radon.complexity import cc_visit, cc_rank
from radon.metrics import mi_visit, mi_rank
from radon.raw import analyze as raw_analyze

from backend.analyzer.base import AnalysisResult, BaseAnalyzer
from backend.analyzer.config import weighted_average_score
from backend.analyzer.js_utils import has_js_files, run_eslint

SOURCE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go"}
PYTHON_EXT = {".py"}
JS_TS_EXTS = {".js", ".ts", ".jsx", ".tsx"}
MAX_FILES = 100

# ── lizard is optional: gracefully degrade if not installed ──────
try:
    import lizard  # type: ignore
    HAS_LIZARD = True
except ImportError:
    HAS_LIZARD = False


def _collect_sources(root: Path) -> list[Path]:
    """Collect source files respecting MAX_FILES limit."""
    files: list[Path] = []
    for ext in SOURCE_EXTS:
        for p in root.rglob(f"*{ext}"):
            if len(files) >= MAX_FILES:
                return files
            if any(seg in (".git", "node_modules", "__pycache__", ".venv", "venv", "dist")
                   for seg in p.parts):
                continue
            files.append(p)
    return files


def _partition_by_lang(sources: list[Path]) -> tuple[list[Path], list[Path], list[Path]]:
    """Split sources into (python, js_ts, other)."""
    py: list[Path] = []
    js_ts: list[Path] = []
    other: list[Path] = []
    for s in sources:
        if s.suffix in PYTHON_EXT:
            py.append(s)
        elif s.suffix in JS_TS_EXTS:
            js_ts.append(s)
        else:
            other.append(s)
    return py, js_ts, other


# ── Python-only analysis (radon) ──────────────────────────────────

def _score_cyclomatic_complexity_python(py_sources: list[Path]) -> dict[str, Any]:
    """Score cyclomatic complexity using radon (Python only).

    Radon ranking: A(1-5), B(6-10), C(11-20), D(21-30), E(31-40), F(41+).
    """
    all_blocks: list[tuple[Any, str]] = []
    sloc_total = 0

    for src in py_sources:
        try:
            text = src.read_text(encoding="utf-8", errors="ignore")
            fname = str(src.relative_to(src.parents[0] if src.parents else src.parent))
            for b in cc_visit(text):
                all_blocks.append((b, fname))
            ra = raw_analyze(text)
            sloc_total += ra.sloc
        except Exception:
            continue

    if not all_blocks:
        return {
            "score": 0, "total_functions": 0, "avg_complexity": 0,
            "issues": ["No Python functions found"], "engine": "radon",
        }

    complexities = [b[0].complexity for b in all_blocks]
    avg_cc = sum(complexities) / len(complexities)
    high_cc = [b for b in all_blocks if b[0].complexity > 10]
    extreme_cc = [b for b in all_blocks if b[0].complexity > 20]

    issues: list[str] = []
    for b, fname in extreme_cc[:10]:
        issues.append(
            f"高圈复杂度: {b.name} (CC={b.complexity}, rank={cc_rank(b.complexity)}) in {fname}"
        )

    if avg_cc <= 5:
        score = 100
    elif avg_cc <= 10:
        score = 85
    elif avg_cc <= 15:
        score = 65
    elif avg_cc <= 20:
        score = 45
    elif avg_cc <= 30:
        score = 25
    else:
        score = 10

    return {
        "score": score,
        "total_functions": len(all_blocks),
        "avg_complexity": round(avg_cc, 1),
        "high_complexity_count": len(high_cc),
        "extreme_complexity_count": len(extreme_cc),
        "sloc_total": sloc_total,
        "issues": issues,
        "engine": "radon",
    }


def _score_maintainability_python(py_sources: list[Path]) -> dict[str, Any]:
    """Score maintainability index using radon (Python only)."""
    mi_values: list[float] = []

    for src in py_sources:
        try:
            text = src.read_text(encoding="utf-8", errors="ignore")
            mi = mi_visit(text, multi=True)
            if isinstance(mi, (int, float)):
                mi_values.append(float(mi))
        except Exception:
            continue

    if not mi_values:
        return {"score": 0, "avg_mi": 0, "issues": ["No MI data available"], "engine": "radon"}

    avg_mi = sum(mi_values) / len(mi_values)
    mi_rank_val = mi_rank(avg_mi)

    rank_to_score = {"A": 95, "B": 70, "C": 40}
    score = rank_to_score.get(mi_rank_val, 30)

    issues: list[str] = []
    if mi_rank_val == "C":
        issues.append(f"可维护性指数偏低: avg MI={avg_mi:.0f}, rank={mi_rank_val}")

    return {
        "score": score,
        "avg_mi": round(avg_mi, 0),
        "mi_rank": mi_rank_val,
        "total_files_scanned": len(mi_values),
        "issues": issues,
        "engine": "radon",
    }


# ── Multi-language analysis (lizard) ──────────────────────────────

def _score_cyclomatic_complexity_lizard(non_py_sources: list[Path]) -> dict[str, Any]:
    """Score cyclomatic complexity using lizard (all languages).

    Uses the same scoring thresholds as radon for fairness:
    avg CC ≤5→100, ≤10→85, ≤15→65, ≤20→45, ≤30→25, >30→10.
    """
    if not HAS_LIZARD:
        return {
            "score": 0, "total_functions": 0, "avg_complexity": 0,
            "issues": ["lizard not installed — CC analysis unavailable for non-Python files"],
            "engine": "lizard (missing)",
        }

    funcs: list[dict[str, Any]] = []
    for src in non_py_sources:
        try:
            fname = str(src.relative_to(src.parents[0] if src.parents else src.parent))
            # lizard.analyze_file takes a file path and reads it internally
            analysis = lizard.analyze_file(str(src))
            for fn in analysis.function_list:
                funcs.append({
                    "name": fn.name if fn.name != "(anonymous)" else f"<fn@{fn.start_line}>",
                    "complexity": fn.cyclomatic_complexity,
                    "nloc": fn.nloc,
                    "token_count": fn.token_count,
                    "file": fname,
                })
        except Exception:
            continue

    if not funcs:
        return {
            "score": 0, "total_functions": 0, "avg_complexity": 0,
            "issues": ["No functions found in non-Python files"],
            "engine": "lizard",
        }

    complexities = [f["complexity"] for f in funcs]
    avg_cc = sum(complexities) / len(complexities)
    high_cc = [f for f in funcs if f["complexity"] > 10]
    extreme_cc = [f for f in funcs if f["complexity"] > 20]

    issues: list[str] = []
    for f in extreme_cc[:10]:
        issues.append(
            f"高圈复杂度: {f['name']} (CC={f['complexity']}) in {f['file']}"
        )

    # Same thresholds as radon for fairness
    if avg_cc <= 5:
        score = 100
    elif avg_cc <= 10:
        score = 85
    elif avg_cc <= 15:
        score = 65
    elif avg_cc <= 20:
        score = 45
    elif avg_cc <= 30:
        score = 25
    else:
        score = 10

    return {
        "score": score,
        "total_functions": len(funcs),
        "avg_complexity": round(avg_cc, 1),
        "high_complexity_count": len(high_cc),
        "extreme_complexity_count": len(extreme_cc),
        "issues": issues,
        "engine": "lizard",
        "raw_funcs": funcs,  # kept for duplication_rate calculation
    }


def _score_eslint_quality(repo_path: Path) -> dict[str, Any] | None:
    """Score JS/TS code quality from ESLint results.

    Returns None if ESLint is not applicable or unavailable.
    """
    if not has_js_files(repo_path):
        return None

    try:
        eslint_result = run_eslint(repo_path)
    except Exception:
        return None

    if not eslint_result:
        return None

    err_count = 0
    warn_count = 0
    if isinstance(eslint_result, list):
        for f in eslint_result:
            for m in f.get("messages", []):
                if m.get("severity") == 2:
                    err_count += 1
                else:
                    warn_count += 1
    elif isinstance(eslint_result, dict):
        err_count = eslint_result.get("errorCount", 0)
        warn_count = eslint_result.get("warningCount", 0)

    # Score mapping
    if err_count == 0 and warn_count == 0:
        score = 100
    elif err_count == 0:
        score = max(50, 95 - warn_count * 2)
    elif err_count <= 5:
        score = max(30, 85 - err_count * 10 - warn_count)
    elif err_count <= 20:
        score = max(15, 60 - err_count * 3 - warn_count)
    else:
        score = max(5, 30 - err_count)

    issues: list[str] = []
    if err_count + warn_count > 0:
        issues.append(f"ESLint: {err_count} errors, {warn_count} warnings in JS/TS files")

    return {
        "score": score,
        "error_count": err_count,
        "warning_count": warn_count,
        "issues": issues,
    }


# ── Duplication rate (real heuristic, not a copy of CC) ───────────

def _score_duplication_rate(
    lizard_funcs: list[dict[str, Any]] | None,
    py_sloc_total: int,
    py_lloc_total: int,
    eslint_score: float | None,
) -> dict[str, Any]:
    """Estimate code duplication / code health from multiple signals.

    Heuristics:
    - lizard token_count/nloc ratio: high ratio → verbose/duplicate code patterns
    - radon lloc/sloc ratio: low ratio → too many blanks/comments masking low logic density
    - ESLint errors: penalize heavily (they often flag duplication-like patterns)
    """
    issues: list[str] = []

    # ── lizard token density ──
    lizard_score: float | None = None
    if lizard_funcs:
        ratios = []
        for f in lizard_funcs:
            nloc = f.get("nloc", 1)
            tks = f.get("token_count", 0)
            if nloc > 0 and tks > 0:
                ratios.append(tks / nloc)

        if ratios:
            avg_ratio = sum(ratios) / len(ratios)
            # Healthy range: token/nloc 2-5. Higher = verbose/duplicate patterns.
            if 2 <= avg_ratio <= 5:
                lizard_score = 95.0
            elif 5 < avg_ratio <= 8:
                lizard_score = 70.0
            elif 8 < avg_ratio <= 12:
                lizard_score = 45.0
            else:
                lizard_score = 25.0
            if avg_ratio > 6:
                issues.append(
                    f"代码膨胀指数偏高: token/NLOC={avg_ratio:.1f}（可能存在重复代码模式）"
                )

    # ── radon logical density ──
    radon_score: float | None = None
    if py_sloc_total > 0 and py_lloc_total > 0:
        lloc_ratio = py_lloc_total / py_sloc_total
        # Healthy: 0.5-0.8 logical/source ratio
        if lloc_ratio >= 0.6:
            radon_score = 90.0
        elif lloc_ratio >= 0.4:
            radon_score = 70.0
        elif lloc_ratio >= 0.2:
            radon_score = 50.0
        else:
            radon_score = 30.0
            issues.append(f"逻辑代码密度偏低: LLOC/SLOC={lloc_ratio:.2f}")

    # ── Combine ──
    combined_scores: list[float] = []
    if lizard_score is not None:
        combined_scores.append(lizard_score)
    if radon_score is not None:
        combined_scores.append(radon_score)

    if not combined_scores:
        return {"score": 0, "issues": ["No duplication data available — no functions found"]}

    base_score = sum(combined_scores) / len(combined_scores)

    # ── ESLint penalty ──
    if eslint_score is not None and eslint_score < 80:
        penalty = min(25, (80 - eslint_score) * 0.5)
        base_score = max(5, base_score - penalty)
        if penalty > 10:
            issues.append(f"ESLint 扣分 -{penalty:.0f}: 代码质量规则违规较多")

    score = round(base_score, 1)

    return {
        "score": score,
        "lizard_token_ratio": round(sum(ratios) / len(ratios), 1) if lizard_funcs and 'ratios' in dir() else None,
        "issues": issues,
    }


# ── File size distribution (all languages) ────────────────────────

def _score_file_size_distribution(sources: list[Path]) -> dict[str, Any]:
    """Score file size distribution: penalize excessively large files.

    - Files > 500 lines : penalty
    - Files > 1000 lines: heavy penalty
    """
    file_sizes: list[int] = []
    oversized = 0
    extreme = 0

    for src in sources:
        try:
            lines = src.read_text(encoding="utf-8", errors="ignore").count("\n")
        except Exception:
            continue
        file_sizes.append(lines)
        if lines > 500:
            oversized += 1
        if lines > 1000:
            extreme += 1

    if not file_sizes:
        return {"score": 0, "total_files": 0, "issues": ["No source files found"]}

    avg_size = sum(file_sizes) / len(file_sizes)
    max_size = max(file_sizes)

    issues: list[str] = []
    if oversized > 0:
        issues.append(f"{oversized} 个文件超过 500 行（其中 {extreme} 个超 1000 行）")

    if extreme > 0:
        score = max(10, 60 - extreme * 15)
    elif oversized > 0:
        score = max(20, 80 - oversized * 12)
    elif avg_size <= 150:
        score = 95
    elif avg_size <= 300:
        score = 80
    elif avg_size <= 500:
        score = 55
    else:
        score = 30

    return {
        "score": score,
        "total_files": len(file_sizes),
        "average_lines": round(avg_size, 0),
        "max_lines": max_size,
        "oversized_count": oversized,
        "extreme_count": extreme,
        "issues": issues,
    }


# ── Analyzer ──────────────────────────────────────────────────────

class CodeQualityAnalyzer(BaseAnalyzer):
    """Analyze code quality: multi-language CC (radon+lizard), ESLint, duplication, file size."""

    def analyze(self, repo_path: Path) -> AnalysisResult:
        sources = _collect_sources(repo_path)
        py_sources, js_ts_sources, other_sources = _partition_by_lang(sources)
        non_py_sources = js_ts_sources + other_sources

        # ── 1. CC: dual-engine ──
        cc_py = _score_cyclomatic_complexity_python(py_sources)
        cc_np = _score_cyclomatic_complexity_lizard(non_py_sources)

        # ── 2. MI: Python only ──
        mi_py = _score_maintainability_python(py_sources)

        # ── 3. ESLint: JS/TS only ──
        eslint = _score_eslint_quality(repo_path)

        # ── 4. Compute cyclomatic_complexity sub-score ──
        py_funcs = cc_py.get("total_functions", 0)
        np_funcs = cc_np.get("total_functions", 0)
        total_funcs = py_funcs + np_funcs

        if total_funcs == 0:
            # No functions found in any language → use ESLint if available
            if eslint:
                cyclomatic_score = round(eslint["score"] * 0.7 + 30 * 0.3, 1)
                cc_label = "eslint fallback"
            else:
                cyclomatic_score = 0.0
                cc_label = "no functions — score 0"
        elif py_funcs == 0:
            # Pure non-Python project
            if eslint and js_ts_sources:
                cyclomatic_score = round(cc_np["score"] * 0.7 + eslint["score"] * 0.3, 1)
                cc_label = "lizard 0.7 + eslint 0.3"
            else:
                cyclomatic_score = float(cc_np["score"])
                cc_label = "lizard only"
        elif np_funcs == 0:
            # Pure Python project (backward compatible)
            cyclomatic_score = round(cc_py["score"] * 0.6 + mi_py["score"] * 0.4, 1)
            cc_label = "radon CC 0.6 + MI 0.4"
        else:
            # Mixed project: weighted by function count
            py_formula = cc_py["score"] * 0.6 + mi_py["score"] * 0.4
            if eslint and js_ts_sources:
                np_formula = cc_np["score"] * 0.7 + eslint["score"] * 0.3
            else:
                np_formula = cc_np["score"]
            py_weight = py_funcs / total_funcs
            np_weight = np_funcs / total_funcs
            cyclomatic_score = round(py_formula * py_weight + np_formula * np_weight, 1)
            cyclomatic_score = min(cyclomatic_score, 100.0)
            cc_label = f"mixed ({py_funcs}py + {np_funcs}np funcs)"

        # ── 5. Duplication rate: real heuristic ──
        lizard_funcs = cc_np.get("raw_funcs")
        py_sloc = cc_py.get("sloc_total", 0)
        py_lloc = sum(
            raw_analyze(s.read_text(encoding="utf-8", errors="ignore")).lloc
            for s in py_sources
            if s.suffix == ".py"
        ) if py_sources else 0
        eslint_for_dup = eslint["score"] if eslint else None
        dup_result = _score_duplication_rate(lizard_funcs, py_sloc, py_lloc, eslint_for_dup)

        # ── 6. File size distribution (unchanged) ──
        fs_result = _score_file_size_distribution(sources)

        # ── 7. Weighted average ──
        scores = {
            "cyclomatic_complexity": cyclomatic_score,
            "duplication_rate": dup_result["score"],
            "file_size_distribution": fs_result["score"],
        }

        scoring = weighted_average_score(scores, "code_quality")

        # ── 8. Collect issues ──
        all_issues = (
            cc_py.get("issues", [])
            + cc_np.get("issues", [])
            + mi_py.get("issues", [])
            + fs_result.get("issues", [])
            + dup_result.get("issues", [])
        )
        if eslint:
            all_issues += eslint.get("issues", [])
            err_count = eslint.get("error_count", 0)
            warn_count = eslint.get("warning_count", 0)
        else:
            err_count = 0
            warn_count = 0

        return AnalysisResult(
            dimension="code_quality",
            score=scoring["score"],
            details={
                "sub_scores": scoring["sub_scores"],
                "cc_label": cc_label,
                "cyclomatic_complexity_python": cc_py,
                "cyclomatic_complexity_nonpython": cc_np,
                "maintainability_python": mi_py,
                "duplication_rate": dup_result,
                "file_size_distribution": fs_result,
                "eslint": (
                    {"score": eslint["score"], "errors": err_count, "warnings": warn_count}
                    if eslint else None
                ),
                "total_files_scanned": len(sources),
                "language_breakdown": {
                    "python": len(py_sources),
                    "js_ts": len(js_ts_sources),
                    "other": len(other_sources),
                },
            },
            issues=all_issues[:20],
        )
