"""Base metric interface and result dataclass."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from src.config.constants import MetricType


@dataclass
class MetricResult:
    """Result from a metric calculation."""
    
    metric_type: MetricType
    score: float
    description: str
    details: Optional[Dict[str, Any]] = None
    improved: Optional[bool] = None  # True if score improved, False if degraded
    
    def __str__(self) -> str:
        """String representation of metric result."""
        status = ""
        if self.improved is True:
            status = " ✅"
        elif self.improved is False:
            status = " ⚠️"
        return f"{self.metric_type.value}: {self.score:.2f}{status}"


class BaseMetric(ABC):
    """Abstract base class for all metrics."""
    
    @property
    @abstractmethod
    def metric_type(self) -> MetricType:
        """Type of metric."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the metric."""
        pass
    
    @property
    def higher_is_better(self) -> bool:
        """Whether higher scores are better (default: True)."""
        return True
    
    @abstractmethod
    def calculate(self, code: str, language: str) -> MetricResult:
        """
        Calculate metric for given code.
        
        Args:
            code: Source code to analyze
            language: Programming language
        
        Returns:
            MetricResult with score and details
        """
        pass
    
    def compare(
        self,
        original_code: str,
        refactored_code: str,
        language: str
    ) -> tuple[MetricResult, MetricResult]:
        """
        Compare metric between original and refactored code.
        
        Args:
            original_code: Original source code
            refactored_code: Refactored source code
            language: Programming language
        
        Returns:
            Tuple of (original_result, refactored_result)
        """
        original_result = self.calculate(original_code, language)
        refactored_result = self.calculate(refactored_code, language)
        
        # Determine if improved
        if self.higher_is_better:
            refactored_result.improved = refactored_result.score > original_result.score
        else:
            refactored_result.improved = refactored_result.score < original_result.score
        
        return original_result, refactored_result
