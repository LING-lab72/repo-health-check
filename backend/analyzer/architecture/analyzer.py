"""Architecture health: God Class detection, circular dependency check, import coupling."""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from backend.analyzer.base import AnalysisResult, BaseAnalyzer
from backend.analyzer.config import weighted_average_score
from backend.analyzer.js_utils import has_js_files, run_madge

GOD_CLASS_METHOD_THRESHOLD = 20
GOD_CLASS_LINE_THRESHOLD = 500
MAX_FILES = 200


def _collect_python_files(root: Path) -> list[Path]:
    """Collect Python files for analysis."""
    files: list[Path] = []
    for p in root.rglob("*.py"):
        if any(seg in (".git", "node_modules", "__pycache__", ".venv", "venv")
               for seg in p.parts):
            continue
        if len(files) >= MAX_FILES:
            break
        files.append(p)
    return files


def _detect_god_classes(py_files: list[Path]) -> dict[str, Any]:
    """Detect God Classes: classes with >20 methods or >500 lines."""
    god_classes: list[dict[str, Any]] = []

    for fpath in py_files:
        try:
            text = fpath.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(text)
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                method_count = len(methods)
                class_lines = node.end_lineno - node.lineno if node.end_lineno else 0

                if method_count > GOD_CLASS_METHOD_THRESHOLD or class_lines > GOD_CLASS_LINE_THRESHOLD:
                    god_classes.append({
                        "name": node.name,
                        "file": str(fpath.relative_to(fpath.parents[0] if fpath.parents else fpath)),
                        "methods": method_count,
                        "lines": class_lines,
                    })

    issues: list[str] = []
    for gc in god_classes[:10]:
        issues.append(f"God Class: {gc['name']} ({gc['file']}:{gc['lines']} lines, {gc['methods']} methods)")

    # Score: no god classes = perfect
    if len(god_classes) == 0:
        score = 100
    elif len(god_classes) <= 2:
        score = 75
    elif len(god_classes) <= 5:
        score = 50
    elif len(god_classes) <= 10:
        score = 25
    else:
        score = 10

    return {
        "score": score,
        "god_classes": god_classes,
        "count": len(god_classes),
        "issues": issues,
    }


def _analyze_import_coupling(py_files: list[Path]) -> dict[str, Any]:
    """Analyze import coupling: measure inter-module dependencies."""
    imports_by_module: dict[str, set[str]] = {}
    internal_modules: set[str] = set()

    # Build internal module list (project packages)
    for fpath in py_files:
        rel = str(fpath.relative_to(fpath.parents[0] if fpath.parents else fpath)).replace("\\", "/")
        parts = rel.split("/")
        if len(parts) >= 1:
            pkg = parts[0].replace(".py", "")
            internal_modules.add(pkg)

    for fpath in py_files:
        module_name = str(fpath.relative_to(fpath.parents[0] if fpath.parents else fpath)).replace("\\", "/")
        imports = set()
        try:
            text = fpath.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(text)
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    imports.add(top)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top = node.module.split(".")[0]
                    imports.add(top)

        # Filter to internal imports
        internal_imports = imports & internal_modules
        imports_by_module[module_name] = internal_imports

    if not imports_by_module:
        return {"score": 0, "issues": ["No Python modules found"]}

    # Calculate coupling: average number of internal imports per module
    coupling_values = [len(v) for v in imports_by_module.values()]
    avg_coupling = sum(coupling_values) / len(coupling_values) if coupling_values else 0

    # Score: low coupling is good
    if avg_coupling <= 2:
        score = 95
    elif avg_coupling <= 4:
        score = 80
    elif avg_coupling <= 6:
        score = 60
    elif avg_coupling <= 10:
        score = 35
    else:
        score = 15

    issues: list[str] = []
    if avg_coupling > 6:
        issues.append(f"模块耦合度偏高: 平均每个模块导入 {avg_coupling:.1f} 个内部模块")

    return {
        "score": score,
        "avg_coupling": round(avg_coupling, 1),
        "total_modules": len(imports_by_module),
        "issues": issues,
    }


def _check_package_structure(root: Path) -> dict[str, Any]:
    """Check package structure: directory organization, __init__.py presence."""
    has_init = bool(list(root.rglob("__init__.py")))
    has_setup = any((root / f).exists() for f in ["setup.py", "setup.cfg", "pyproject.toml"])
    has_src_layout = (root / "src").is_dir()

    score = 0
    issues: list[str] = []

    if has_init:
        score += 50
    else:
        issues.append("缺少 __init__.py 文件，可能缺少包结构")
    if has_setup:
        score += 30
    else:
        issues.append("缺少 setup.py/pyproject.toml 包声明文件")
    if has_src_layout:
        score += 20
    else:
        issues.append("未使用 src 布局")

    return {
        "score": score,
        "has_init": has_init,
        "has_setup": has_setup,
        "has_src_layout": has_src_layout,
        "issues": issues,
    }


class ArchitectureAnalyzer(BaseAnalyzer):
    """Analyze architecture: God Classes, import coupling, package structure."""

    def analyze(self, repo_path: Path) -> AnalysisResult:
        py_files = _collect_python_files(repo_path)

        god_result = _detect_god_classes(py_files)
        coupling_result = _analyze_import_coupling(py_files)
        structure_result = _check_package_structure(repo_path)

        # JS/TS: madge circular dependency detection
        circular = None
        if has_js_files(repo_path):
            try:
                circular = run_madge(repo_path)
            except Exception:
                pass

        scores = {
            "module_coupling": coupling_result["score"],
            "package_structure": structure_result["score"],
            "dependency_direction": god_result["score"],
        }

        scoring = weighted_average_score(scores, "architecture")
        all_issues = (
            god_result.get("issues", [])
            + coupling_result.get("issues", [])
            + structure_result.get("issues", [])
        )

        # Add circular dep issues
        if circular and isinstance(circular, dict) and circular:
            circular_count = len(circular)
            all_issues.append(f"JS/TS 循环依赖: 发现 {circular_count} 个循环")
            # Penalize coupling score
            scores["module_coupling"] = max(0, scores["module_coupling"] - circular_count * 10)
            scoring = weighted_average_score(scores, "architecture")

        return AnalysisResult(
            dimension="architecture",
            score=scoring["score"],
            details={
                "sub_scores": scoring["sub_scores"],
                "god_classes": god_result,
                "import_coupling": coupling_result,
                "package_structure": structure_result,
                "js_circular_deps": circular,
                "total_files_analyzed": len(py_files),
            },
            issues=all_issues[:20],
        )
