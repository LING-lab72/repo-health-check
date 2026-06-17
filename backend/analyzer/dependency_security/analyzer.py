"""Dependency security: bandit scan, pip-audit check, lockfile detection."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from backend.analyzer.base import AnalysisResult, BaseAnalyzer
from backend.analyzer.config import weighted_average_score

LOCK_FILES = [
    "requirements.txt", "Pipfile.lock", "poetry.lock", "pyproject.toml",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Gemfile.lock",
    "composer.lock", "Cargo.lock", "go.sum", "pom.xml",
]
MAX_FILES = 200


def _check_lockfiles(root: Path) -> dict[str, Any]:
    """Check for dependency lock files."""
    found: list[str] = []
    for lockfile in LOCK_FILES:
        p = root / lockfile
        if p.exists():
            found.append(lockfile)

    # Score: more lockfiles = better dependency management
    if len(found) >= 3:
        score = 100
    elif len(found) >= 2:
        score = 85
    elif len(found) >= 1:
        score = 60
    else:
        score = 0

    issues: list[str] = []
    if not found:
        issues.append("未找到任何依赖锁定文件（lockfile），依赖版本可能不稳定")

    return {
        "score": score,
        "lockfiles": found,
        "count": len(found),
        "issues": issues,
    }


def _run_bandit(root: Path) -> dict[str, Any]:
    """Run bandit security scanner and parse output."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", str(root), "-f", "json", "-q", "-ll"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(root),
        )
    except FileNotFoundError:
        return {"score": 50, "issues": ["bandit 未安装，跳过安全扫描"], "high": 0, "medium": 0, "low": 0}
    except subprocess.TimeoutExpired:
        return {"score": 50, "issues": ["bandit 扫描超时"], "high": 0, "medium": 0, "low": 0}

    if result.returncode not in (0, 1) or not result.stdout.strip():
        return {"score": 50, "issues": ["bandit 扫描失败"], "high": 0, "medium": 0, "low": 0}

    try:
        data = json.loads(result.stdout)
        results = data.get("results", [])
    except (json.JSONDecodeError, KeyError):
        return {"score": 50, "issues": ["bandit 输出解析失败"], "high": 0, "medium": 0, "low": 0}

    # Categorize by severity
    high = sum(1 for r in results if r.get("issue_severity") == "HIGH")
    medium = sum(1 for r in results if r.get("issue_severity") == "MEDIUM")
    low = sum(1 for r in results if r.get("issue_severity") == "LOW")
    total = len(results)

    issues: list[str] = []
    for r in results[:10]:
        issues.append(
            f"[{r.get('issue_severity', '?')}] {r.get('test_name', '?')}: "
            f"{r.get('filename', '?')}:{r.get('line_number', '?')}"
        )

    # Score: no issues = perfect
    if total == 0:
        score = 100
    elif high > 0:
        score = max(10, 70 - high * 20)
    elif medium > 0:
        score = max(20, 80 - medium * 15)
    else:
        score = max(30, 90 - low * 10)

    return {
        "score": score,
        "high": high,
        "medium": medium,
        "low": low,
        "total": total,
        "issues": issues,
    }


def _run_pip_audit(root: Path) -> dict[str, Any]:
    """Run pip-audit to check for known vulnerabilities."""
    # pip-audit needs requirements or installed packages
    req_files: list[Path] = []
    for p in root.rglob("requirements*.txt"):
        if "node_modules" in str(p):
            continue
        if len(req_files) >= MAX_FILES:
            break
        req_files.append(p)
    if not req_files:
        return {
            "score": 60,
            "issues": ["未找到 requirements.txt，无法运行 pip-audit"],
            "vulnerabilities": 0,
        }

    try:
        req_file = req_files[0]
        result = subprocess.run(
            [sys.executable, "-m", "pip_audit", "-r", str(req_file), "-f", "json"],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        return {"score": 50, "issues": ["pip-audit 未安装"], "vulnerabilities": 0}
    except subprocess.TimeoutExpired:
        return {"score": 50, "issues": ["pip-audit 扫描超时"], "vulnerabilities": 0}

    if not result.stdout.strip():
        return {"score": 95, "vulnerabilities": 0, "issues": []}

    try:
        data = json.loads(result.stdout)
        vulns = data.get("dependencies", []) if isinstance(data, dict) else data
    except json.JSONDecodeError:
        return {"score": 50, "issues": ["pip-audit 输出解析失败"], "vulnerabilities": 0}

    vuln_count = sum(len(d.get("vulns", [])) for d in vulns)

    issues: list[str] = []
    for dep in vulns[:5]:
        dep_vulns = dep.get("vulns", [])
        if dep_vulns:
            issues.append(f"{dep.get('name', '?')} 有 {len(dep_vulns)} 个已知漏洞")

    # Score
    if vuln_count == 0:
        score = 100
    elif vuln_count <= 2:
        score = 70
    elif vuln_count <= 5:
        score = 40
    else:
        score = 15

    return {
        "score": score,
        "vulnerabilities": vuln_count,
        "issues": issues,
    }


class DependencySecurityAnalyzer(BaseAnalyzer):
    """Analyze dependency security: bandit, pip-audit, lockfiles."""

    def analyze(self, repo_path: Path) -> AnalysisResult:
        bandit_result = _run_bandit(repo_path)
        pipaudit_result = _run_pip_audit(repo_path)
        lockfile_result = _check_lockfiles(repo_path)

        scores = {
            "known_vulnerabilities": bandit_result["score"],
            "dependency_freshness": pipaudit_result["score"],
            "lockfile_present": lockfile_result["score"],
        }

        scoring = weighted_average_score(scores, "dependency_security")
        all_issues = (
            bandit_result.get("issues", [])
            + pipaudit_result.get("issues", [])
            + lockfile_result.get("issues", [])
        )

        return AnalysisResult(
            dimension="dependency_security",
            score=scoring["score"],
            details={
                "sub_scores": scoring["sub_scores"],
                "bandit_scan": bandit_result,
                "pip_audit": pipaudit_result,
                "lockfiles": lockfile_result,
            },
            issues=all_issues[:20],
        )
