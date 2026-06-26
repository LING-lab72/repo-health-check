"""Tests for BaseAnalyzer interface contract and real analyzer output."""
from pathlib import Path

import pytest

from backend.analyzer.base import AnalysisResult, BaseAnalyzer
from backend.analyzer.code_quality.analyzer import CodeQualityAnalyzer
from backend.analyzer.test_coverage.analyzer import TestCoverageAnalyzer
from backend.analyzer.architecture.analyzer import ArchitectureAnalyzer
from backend.analyzer.documentation.analyzer import DocumentationAnalyzer
from backend.analyzer.dependency_security.analyzer import DependencySecurityAnalyzer
from backend.analyzer.engineering.analyzer import EngineeringAnalyzer

ALL_ANALYZERS = [
    CodeQualityAnalyzer,
    TestCoverageAnalyzer,
    ArchitectureAnalyzer,
    DocumentationAnalyzer,
    DependencySecurityAnalyzer,
    EngineeringAnalyzer,
]


def _find_repo_root() -> Path:
    """Find the project root even when pytest changes rootdir in CI."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "backend").is_dir() and (parent / "frontend").is_dir():
            return parent
    return Path(__file__).resolve().parent.parent.parent


REPO_ROOT = _find_repo_root()


def test_base_analyzer_is_abstract():
    """BaseAnalyzer cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseAnalyzer()  # type: ignore[abstract]


@pytest.mark.parametrize("analyzer_cls", ALL_ANALYZERS)
def test_analyzer_implements_analyze(analyzer_cls: type[BaseAnalyzer], tmp_path: Path):
    """Every analyzer must implement analyze() and return AnalysisResult."""
    analyzer = analyzer_cls()
    result = analyzer.analyze(tmp_path)

    assert isinstance(result, AnalysisResult)
    assert isinstance(result.dimension, str)
    assert len(result.dimension) > 0
    assert isinstance(result.score, float)
    assert isinstance(result.details, dict)
    assert isinstance(result.issues, list)


@pytest.mark.parametrize("analyzer_cls", ALL_ANALYZERS)
def test_analyzer_dimension_matches_class(analyzer_cls: type[BaseAnalyzer], tmp_path: Path):
    """Each analyzer should return its expected dimension name."""
    analyzer = analyzer_cls()
    result = analyzer.analyze(tmp_path)

    expected_dimensions = {
        CodeQualityAnalyzer: "code_quality",
        TestCoverageAnalyzer: "test_coverage",
        ArchitectureAnalyzer: "architecture",
        DocumentationAnalyzer: "documentation",
        DependencySecurityAnalyzer: "dependency_security",
        EngineeringAnalyzer: "engineering",
    }

    assert result.dimension == expected_dimensions[analyzer_cls]


def test_analysis_result_defaults():
    """AnalysisResult should have sensible defaults for optional fields."""
    result = AnalysisResult(dimension="test", score=85.0)
    assert result.details == {}
    assert result.issues == []


def test_code_quality_on_own_project():
    """Run code_quality analyzer against this project's own code."""
    analyzer = CodeQualityAnalyzer()
    result = analyzer.analyze(REPO_ROOT)

    assert 0 <= result.score <= 100
    assert "sub_scores" in result.details
    assert isinstance(result.details["total_files_scanned"], int)
    # Should find our Python files
    assert result.details["total_files_scanned"] > 0


def test_test_coverage_detects_own_tests():
    """Test that test_coverage finds our own test files."""
    analyzer = TestCoverageAnalyzer()
    result = analyzer.analyze(REPO_ROOT)

    assert 0 <= result.score <= 100
    assert result.details["test_file_ratio"]["test_files"] > 0
    frameworks = result.details["frameworks"]["frameworks"]
    assert "pytest" in frameworks


def test_architecture_on_own_project():
    """Run architecture analyzer on this project."""
    analyzer = ArchitectureAnalyzer()
    result = analyzer.analyze(REPO_ROOT)

    assert 0 <= result.score <= 100
    assert "god_classes" in result.details
    # Our project should have package structure
    assert result.details["package_structure"]["has_init"] is True


def test_documentation_on_own_project():
    """Run documentation analyzer on this project."""
    analyzer = DocumentationAnalyzer()
    result = analyzer.analyze(REPO_ROOT)

    assert 0 <= result.score <= 100
    # We have a project.md (not README yet, but let it work)
    assert "readme" in result.details
    # Even if README not found, comment density should be checked
    assert "comment_density" in result.details


def test_engineering_on_own_project():
    """Run engineering analyzer on this project."""
    analyzer = EngineeringAnalyzer()
    result = analyzer.analyze(REPO_ROOT)

    assert 0 <= result.score <= 100
    # We have .gitignore, CI configs, pre-commit
    assert result.details["git_hygiene"]["has_gitignore"] is True
    assert result.details["linter"]["count"] >= 1
