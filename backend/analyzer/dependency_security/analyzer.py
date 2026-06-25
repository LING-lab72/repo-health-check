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
        for p in root.rglob(lockfile):
            if any(seg in (".git", "node_modules", "__pycache__", ".venv", "venv", "dist")
                   for seg in p.parts):
                continue
            found.append(str(p.relative_to(root)))
            if len(found) >= MAX_FILES:
                break

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
        "lockfiles": sorted(set(found)),
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
            "score": 100,
            "skipped": True,
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
        "skipped": False,
        "vulnerabilities": vuln_count,
        "issues": issues,
    }


def _run_npm_audit(root: Path) -> dict[str, Any]:
    """Run npm audit for projects with package-lock.json files."""
    lockfiles = [
        p for p in root.rglob("package-lock.json")
        if not any(seg in (".git", "node_modules", "dist") for seg in p.parts)
    ][:MAX_FILES]
    if not lockfiles:
        return {
            "score": 100,
            "skipped": True,
            "issues": ["未找到 package-lock.json，跳过 npm audit"],
            "vulnerabilities": 0,
        }

    total_vulns = 0
    issues: list[str] = []

    for lockfile in lockfiles[:5]:
        try:
            result = subprocess.run(
                ["npm", "audit", "--json", "--package-lock-only", "--omit", "dev"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(lockfile.parent),
            )
        except FileNotFoundError:
            return {"score": 50, "issues": ["npm 未安装，跳过 npm audit"], "vulnerabilities": 0}
        except subprocess.TimeoutExpired:
            issues.append(f"{lockfile.parent.name}: npm audit 扫描超时")
            continue

        if not result.stdout.strip():
            continue

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            issues.append(f"{lockfile.parent.name}: npm audit 输出解析失败")
            continue

        metadata = data.get("metadata", {}).get("vulnerabilities", {})
        vuln_count = sum(
            int(metadata.get(k, 0))
            for k in ("low", "moderate", "high", "critical")
        )
        total_vulns += vuln_count
        if vuln_count:
            issues.append(f"{lockfile.parent.relative_to(root)} 有 {vuln_count} 个 npm 依赖漏洞")

    if total_vulns == 0:
        score = 100
    elif total_vulns <= 2:
        score = 70
    elif total_vulns <= 5:
        score = 40
    else:
        score = 15

    return {"score": score, "skipped": False, "vulnerabilities": total_vulns, "issues": issues[:10]}


class DependencySecurityAnalyzer(BaseAnalyzer):
    """Analyze dependency security: bandit, pip-audit, lockfiles."""

    def analyze(self, repo_path: Path) -> AnalysisResult:
        bandit_result = _run_bandit(repo_path)
        pipaudit_result = _run_pip_audit(repo_path)
        npm_audit_result = _run_npm_audit(repo_path)
        lockfile_result = _check_lockfiles(repo_path)
        applicable_dependency_scores = [
            r["score"]
            for r in (pipaudit_result, npm_audit_result)
            if not r.get("skipped")
        ]
        dependency_audit_score = (
            min(applicable_dependency_scores) if applicable_dependency_scores else 60
        )

        scores = {
            "known_vulnerabilities": bandit_result["score"],
            "dependency_freshness": dependency_audit_score,
            "lockfile_present": lockfile_result["score"],
        }

        scoring = weighted_average_score(scores, "dependency_security")
        dependency_issues: list[str] = []
        if not pipaudit_result.get("skipped"):
            dependency_issues += pipaudit_result.get("issues", [])
        if not npm_audit_result.get("skipped"):
            dependency_issues += npm_audit_result.get("issues", [])

        all_issues = (
            bandit_result.get("issues", [])
            + dependency_issues
            + lockfile_result.get("issues", [])
        )

        return AnalysisResult(
            dimension="dependency_security",
            score=scoring["score"],
            details={
                "sub_scores": scoring["sub_scores"],
                "bandit_scan": bandit_result,
                "pip_audit": pipaudit_result,
                "npm_audit": npm_audit_result,
                "lockfiles": lockfile_result,
            },
            issues=all_issues[:20],
        )
