"""Documentation analysis: README quality, comment density, API doc detection."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from backend.analyzer.base import AnalysisResult, BaseAnalyzer
from backend.analyzer.config import weighted_average_score

README_PATTERNS = re.compile(r"readme", re.IGNORECASE)
README_QUALITY_SECTIONS = [
    "install", "usage", "getting started", "quick start", "example",
    "contributing", "license", "documentation", "api", "overview",
    "description", "features", "configuration", "setup", "requirements",
]

DOC_FILE_EXTS = {".md", ".rst", ".txt", ".adoc"}
API_DOC_MARKERS = [
    "sphinx", "mkdocs", "swagger", "openapi", "api-docs",
    "jsdoc", "typedoc", "godoc", "javadoc",
]
API_DOC_FILES = ["mkdocs.yml", "conf.py", "docusaurus.config.js", "typedoc.json"]
MAX_FILES = 200


def _find_readme(root: Path) -> Path | None:
    """Find README file."""
    for p in root.iterdir():
        if p.is_file() and README_PATTERNS.search(p.stem):
            return p
    return None


def _score_readme_quality(root: Path) -> dict[str, Any]:
    """Score README quality by checking for standard sections."""
    readme = _find_readme(root)
    if not readme:
        return {"score": 0, "issues": ["未找到 README 文件"]}

    try:
        text = readme.read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        return {"score": 10, "issues": ["README 文件不可读"]}

    size = len(text)
    found_sections: list[str] = []
    missing_sections: list[str] = []

    for section in README_QUALITY_SECTIONS:
        if section in text:
            found_sections.append(section)
        else:
            missing_sections.append(section)

    # Check heading structure
    has_headings = bool(re.search(r"^#{1,3}\s", text, re.MULTILINE))
    has_code_blocks = "```" in text
    has_links = "http" in text or re.search(r"\[.+\]\(.+\)", text)

    # Score components
    section_score = min(100, len(found_sections) * 7)  # max ~100 with 14 sections
    size_score = min(50, size // 20)  # size bonus up to 1000 chars
    structure_score = 0
    if has_headings:
        structure_score += 15
    if has_code_blocks:
        structure_score += 15
    if has_links:
        structure_score += 10
    if size > 500:
        structure_score += 10

    score = min(100, section_score * 0.5 + size_score + structure_score)

    issues: list[str] = []
    if len(missing_sections) > 8:
        issues.append(f"README 缺少关键章节，已找到 {len(found_sections)}/{len(README_QUALITY_SECTIONS)} 个")
    if not has_code_blocks:
        issues.append("README 缺少代码示例")
    if not has_headings:
        issues.append("README 缺少标题结构")

    return {
        "score": score,
        "readme_path": str(readme.name),
        "size_chars": size,
        "found_sections": found_sections,
        "missing_count": len(missing_sections),
        "has_headings": has_headings,
        "has_code_blocks": has_code_blocks,
        "issues": issues,
    }


def _score_comment_density(root: Path) -> dict[str, Any]:
    """Score comment density in source files."""
    source_exts = {".py": ("#", '"""', "'''"),
                   ".js": ("//", "/*"),
                   ".ts": ("//", "/*"),
                   ".tsx": ("//", "/*"),
                   ".jsx": ("//", "/*"),
                   ".java": ("//", "/*"),
                   ".go": ("//", "/*")}

    files: list[Path] = []
    for ext in source_exts:
        for p in root.rglob(f"*{ext}"):
            if any(seg in (".git", "node_modules", "__pycache__", ".venv", "venv", "dist")
                   for seg in p.parts):
                continue
            if len(files) >= MAX_FILES:
                break
            files.append(p)

    if not files:
        return {"score": 0, "issues": ["No source files found"]}

    total_lines = 0
    comment_lines = 0

    for fpath in files:
        try:
            lines = fpath.read_text(encoding="utf-8", errors="ignore").split("\n")
        except Exception:
            continue

        ext = fpath.suffix.lower()
        markers = source_exts.get(ext, ("#",))

        in_multiline = False
        for line in lines:
            stripped = line.strip()
            total_lines += 1

            if not stripped:
                continue

            is_comment = False
            for marker in markers:
                if marker.startswith("/*") or marker.startswith('"""') or marker.startswith("'''"):
                    if in_multiline:
                        is_comment = True
                        if marker in stripped and stripped.index(marker) == 0:
                            in_multiline = False
                    elif stripped.startswith(marker):
                        is_comment = True
                        in_multiline = True
                elif stripped.startswith(marker):
                    is_comment = True
                    break

            if is_comment:
                comment_lines += 1

    if total_lines == 0:
        return {"score": 0, "issues": ["No code lines found"]}

    ratio = comment_lines / total_lines

    # Score: good comment ratio ~0.15-0.30
    if 0.10 <= ratio <= 0.40:
        score = 90
    elif 0.05 <= ratio < 0.10 or 0.40 < ratio <= 0.50:
        score = 70
    elif ratio < 0.02 or ratio > 0.60:
        score = 20
    else:
        score = 45

    issues: list[str] = []
    if ratio < 0.05:
        issues.append(f"注释密度过低: {ratio:.1%}")
    elif ratio > 0.50:
        issues.append(f"注释密度过高: {ratio:.1%}（可能存在过多注释代码）")

    return {
        "score": score,
        "comment_ratio": round(ratio, 3),
        "total_lines": total_lines,
        "comment_lines": comment_lines,
        "files_scanned": len(files),
        "issues": issues,
    }


def _detect_api_documentation(root: Path) -> dict[str, Any]:
    """Detect API documentation presence."""
    found_configs: list[str] = []
    found_dirs: list[str] = []

    # Check for doc config files
    for cfg in API_DOC_FILES:
        if (root / cfg).exists() or any(root.rglob(cfg)):
            found_configs.append(cfg)

    # Check for doc directories
    for d in ["docs", "doc", "documentation", "api-docs", "apidoc"]:
        p = root / d
        if p.is_dir() and any(p.iterdir()):
            found_dirs.append(d)

    # Check for doc markers in files
    if found_dirs:
        for doc_dir_name in found_dirs:
            doc_dir = root / doc_dir_name
            for ext in DOC_FILE_EXTS:
                files = list(doc_dir.rglob(f"*{ext}"))
                if files:
                    found_configs.append(f"{doc_dir_name}/*.{ext}")

    score = 0
    if len(found_configs) >= 2 or len(found_dirs) >= 2:
        score = 90
    elif found_configs or found_dirs:
        score = 60
    else:
        score = 10

    issues: list[str] = []
    if score <= 10:
        issues.append("未检测到 API 文档配置（Sphinx/MkDocs/Swagger 等）")

    return {
        "score": score,
        "doc_configs": found_configs,
        "doc_directories": found_dirs,
        "issues": issues,
    }


class DocumentationAnalyzer(BaseAnalyzer):
    """Analyze documentation: README quality, comment density, API doc presence."""

    def analyze(self, repo_path: Path) -> AnalysisResult:
        readme = _score_readme_quality(repo_path)
        api_doc = _detect_api_documentation(repo_path)
        comments = _score_comment_density(repo_path)

        scores = {
            "readme_quality": readme["score"],
            "api_documentation": api_doc["score"],
            "comment_ratio": comments["score"],
        }

        scoring = weighted_average_score(scores, "documentation")
        all_issues = readme.get("issues", []) + api_doc.get("issues", []) + comments.get("issues", [])

        return AnalysisResult(
            dimension="documentation",
            score=scoring["score"],
            details={
                "sub_scores": scoring["sub_scores"],
                "readme": readme,
                "api_documentation": api_doc,
                "comment_density": comments,
            },
            issues=all_issues[:20],
        )
