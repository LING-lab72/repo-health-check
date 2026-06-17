"""Base analyzer interface for all health check dimensions."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AnalysisResult:
    """Unified result from any dimension analyzer."""

    dimension: str
    score: float
    details: dict[str, Any] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)


class BaseAnalyzer(ABC):
    """Abstract base class for all dimension analyzers.

    Every analyzer MUST implement analyze() returning an AnalysisResult.
    """

    @abstractmethod
    def analyze(self, repo_path: Path) -> AnalysisResult:
        """Run analysis on the given repository path.

        Args:
            repo_path: Path to the cloned repository root.

        Returns:
            AnalysisResult with dimension name, score, details and issues.
        """
        ...
