"""Engineering standards: CI/CD, linter config, git hygiene, license detection."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.analyzer.base import AnalysisResult, BaseAnalyzer
from backend.analyzer.config import weighted_average_score

CI_CONFIGS = [
    ".github/workflows/*.yml", ".github/workflows/*.yaml",
    ".gitlab-ci.yml", ".travis.yml", "Jenkinsfile",
    ".circleci/config.yml", "azure-pipelines.yml",
    "bitbucket-pipelines.yml", ".drone.yml",
]

LINTER_CONFIGS = [
    ".flake8", ".pylintrc", "pyproject.toml", "setup.cfg",
    ".eslintrc*", ".prettierrc*", ".stylelintrc*",
    ".editorconfig", ".pre-commit-config.yaml",
    ".golangci.yml", "checkstyle.xml",
]

LICENSE_FILES = [
    "LICENSE", "LICENSE.txt", "LICENSE.md",
    "COPYING", "COPYING.txt",
    "UNLICENSE", "LICENCE",
]


def _check_cicd(root: Path) -> dict[str, Any]:
    """Detect CI/CD configuration files."""
    found: list[str] = []

    for pattern in CI_CONFIGS:
        if pattern.endswith("/*.yml") or pattern.endswith("/*.yaml"):
            patterns = list(Path(root / pattern.split("/*")[0]).glob(pattern.split("/")[-1]))
            for p in patterns:
                found.append(str(p.relative_to(root)))
        else:
            p = root / pattern
            if p.exists():
                found.append(pattern)

    found = sorted(set(found))

    if len(found) >= 2:
        score = 95
    elif len(found) == 1:
        score = 75
    else:
        score = 0

    issues: list[str] = []
    if not found:
        issues.append("未找到 CI/CD 配置文件（GitHub Actions/Travis/Jenkins 等）")

    return {
        "score": score,
        "configs": found,
        "count": len(found),
        "issues": issues,
    }


def _check_linter(root: Path) -> dict[str, Any]:
    """Detect linter/formatter configuration."""
    found: list[str] = []

    for pattern in LINTER_CONFIGS:
        if "*" in pattern:
            try:
                for p in root.rglob(pattern):
                    if "node_modules" not in str(p):
                        found.append(pattern.replace("*", p.suffix.rsplit(".", 1)[-1] if p.suffix else ""))
            except Exception:
                pass
        else:
            p = root / pattern
            if p.exists():
                found.append(pattern)

    found = sorted(set(found))

    if len(found) >= 3:
        score = 95
    elif len(found) >= 2:
        score = 75
    elif len(found) == 1:
        score = 50
    else:
        score = 5

    issues: list[str] = []
    if len(found) < 2:
        issues.append("Linter 配置不足，建议添加 flake8/eslint/prettier")

    return {
        "score": score,
        "configs": found,
        "count": len(found),
        "issues": issues,
    }


def _check_git_hygiene(root: Path) -> dict[str, Any]:
    """Check git hygiene: .gitignore, .gitattributes, git directory."""
    has_git = (root / ".git").is_dir()
    has_gitignore = (root / ".gitignore").exists()
    has_gitattributes = (root / ".gitattributes").exists()

    # Check .gitignore quality
    gitignore_score = 0
    if has_gitignore:
        try:
            content = (root / ".gitignore").read_text(encoding="utf-8", errors="ignore")
            quality_markers = ["node_modules", "__pycache__", ".env", "dist", "build", "*.pyc"]
            matches = sum(1 for m in quality_markers if m.lower() in content.lower())
            gitignore_score = min(100, matches * 25)
        except Exception:
            gitignore_score = 30

    score = 0
    if has_git:
        score += 10
    if has_gitignore:
        score += gitignore_score * 0.6
    if has_gitattributes:
        score += 20

    issues: list[str] = []
    if not has_git:
        issues.append("不是 Git 仓库")
    if not has_gitignore:
        issues.append("缺少 .gitignore 文件")

    return {
        "score": score,
        "has_git": has_git,
        "has_gitignore": has_gitignore,
        "has_gitattributes": has_gitattributes,
        "gitignore_quality": gitignore_score,
        "issues": issues,
    }


def _check_license(root: Path) -> dict[str, Any]:
    """Detect license file."""
    found: str | None = None
    for fname in LICENSE_FILES:
        p = root / fname
        if p.exists():
            found = fname
            break

    score = 100 if found else 0

    issues: list[str] = []
    if not found:
        issues.append("未找到 LICENSE 文件")

    return {
        "score": score,
        "license_file": found,
        "has_license": found is not None,
        "issues": issues,
    }


class EngineeringAnalyzer(BaseAnalyzer):
    """Analyze engineering standards: CI/CD, linter, git hygiene, license."""

    def analyze(self, repo_path: Path) -> AnalysisResult:
        cicd = _check_cicd(repo_path)
        linter = _check_linter(repo_path)
        git = _check_git_hygiene(repo_path)
        license_result = _check_license(repo_path)

        scores = {
            "cicd_config": cicd["score"],
            "linter_config": linter["score"],
            "git_hygiene": git["score"],
            "license_present": license_result["score"],
        }

        scoring = weighted_average_score(scores, "engineering")
        all_issues = (
            cicd.get("issues", [])
            + linter.get("issues", [])
            + git.get("issues", [])
            + license_result.get("issues", [])
        )

        return AnalysisResult(
            dimension="engineering",
            score=scoring["score"],
            details={
                "sub_scores": scoring["sub_scores"],
                "cicd": cicd,
                "linter": linter,
                "git_hygiene": git,
                "license": license_result,
            },
            issues=all_issues[:20],
        )
