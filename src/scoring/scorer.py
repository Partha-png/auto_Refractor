"""Main scoring orchestrator that aggregates all metrics."""

from typing import Dict, List, Optional
from dataclasses import dataclass
from src.scoring.metrics import BaseMetric, MetricResult
from src.scoring.bleu_score import BLEUScoreMetric
from src.scoring.code_metrics import (
    CyclomaticComplexityMetric,
    MaintainabilityIndexMetric,
    LinesOfCodeMetric,
)
from src.scoring.perplexity import PerplexityMetric
from src.config.settings import settings
from src.config.constants import MetricType
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ScoreComparison:
    """Comparison of scores between original and refactored code."""
    
    original_scores: Dict[MetricType, MetricResult]
    refactored_scores: Dict[MetricType, MetricResult]
    overall_score: float
    overall_improvement: float
    
    def get_improvement(self, metric_type: MetricType) -> Optional[float]:
        """Get improvement percentage for a specific metric."""
        if metric_type not in self.original_scores or metric_type not in self.refactored_scores:
            return None
        
        original = self.original_scores[metric_type].score
        refactored = self.refactored_scores[metric_type].score
        
        if original == 0:
            return 100.0 if refactored > 0 else 0.0
        
        return ((refactored - original) / original) * 100


class CodeScorer:
    """
    Main scoring orchestrator that runs all metrics and aggregates results.
    """
    
    def __init__(self):
        """Initialize scorer with all available metrics."""
        self.metrics: List[BaseMetric] = []
        
        # Add enabled metrics
        if settings.enable_bleu:
            self.metrics.append(BLEUScoreMetric())
        
        if settings.enable_code_metrics:
            self.metrics.append(CyclomaticComplexityMetric())
            self.metrics.append(MaintainabilityIndexMetric())
            self.metrics.append(LinesOfCodeMetric())
        
        if settings.enable_perplexity:
            self.metrics.append(PerplexityMetric())
        
        logger.info(f"Initialized scorer with {len(self.metrics)} metrics")
    
    def score_code(self, code: str, language: str) -> Dict[MetricType, MetricResult]:
        """
        Score a single piece of code with all metrics.
        
        Args:
            code: Source code to score
            language: Programming language
        
        Returns:
            Dictionary of metric results
        """
        results = {}
        
        for metric in self.metrics:
            try:
                result = metric.calculate(code, language)
                results[metric.metric_type] = result
            except Exception as e:
                logger.error(f"Error calculating {metric.metric_type}: {e}")
                results[metric.metric_type] = MetricResult(
                    metric_type=metric.metric_type,
                    score=0.0,
                    description=metric.description,
                    details={"error": str(e)}
                )
        
        return results
    
    def compare_code(
        self,
        original_code: str,
        refactored_code: str,
        language: str
    ) -> ScoreComparison:
        """
        Compare original and refactored code across all metrics.
        
        Args:
            original_code: Original source code
            refactored_code: Refactored source code
            language: Programming language
        
        Returns:
            ScoreComparison with detailed results
        """
        logger.info(f"Comparing code for language: {language}")
        
        original_scores = {}
        refactored_scores = {}
        
        # Special handling for BLEU (requires both codes)
        bleu_metric = BLEUScoreMetric()
        if settings.enable_bleu:
            try:
                bleu_result = bleu_metric.calculate_bleu(
                    original_code, refactored_code, language
                )
                # Store in both (BLEU measures similarity)
                original_scores[MetricType.BLEU] = MetricResult(
                    metric_type=MetricType.BLEU,
                    score=100.0,  # Original is 100% similar to itself
                    description=bleu_metric.description,
                )
                refactored_scores[MetricType.BLEU] = bleu_result
            except Exception as e:
                logger.error(f"Error calculating BLEU: {e}")
        
        # Calculate other metrics for both versions
        for metric in self.metrics:
            if isinstance(metric, BLEUScoreMetric):
                continue  # Already handled
            
            try:
                orig_result, refact_result = metric.compare(
                    original_code, refactored_code, language
                )
                original_scores[metric.metric_type] = orig_result
                refactored_scores[metric.metric_type] = refact_result
            except Exception as e:
                logger.error(f"Error comparing {metric.metric_type}: {e}")
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(refactored_scores)
        overall_improvement = self._calculate_overall_improvement(
            original_scores, refactored_scores
        )
        
        return ScoreComparison(
            original_scores=original_scores,
            refactored_scores=refactored_scores,
            overall_score=overall_score,
            overall_improvement=overall_improvement,
        )
    
    def _calculate_overall_score(
        self,
        scores: Dict[MetricType, MetricResult]
    ) -> float:
        """
        Calculate weighted overall score.
        
        Normalizes all metrics to 0-100 scale where higher is better.
        """
        if not scores:
            return 0.0
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric_type, result in scores.items():
            weight = settings.get_scoring_weight(metric_type.value)
            
            # Normalize score to 0-100 where higher is better
            normalized_score = self._normalize_score(result, metric_type)
            
            weighted_sum += normalized_score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _normalize_score(
        self,
        result: MetricResult,
        metric_type: MetricType
    ) -> float:
        """Normalize score to 0-100 where higher is better."""
        score = result.score
        
        # Metrics where higher is better (already 0-100)
        if metric_type in [MetricType.BLEU, MetricType.MAINTAINABILITY_INDEX]:
            return max(0, min(100, score))
        
        # Metrics where lower is better - invert
        if metric_type == MetricType.CYCLOMATIC_COMPLEXITY:
            # Complexity: 1-10 is good, >20 is bad
            # Invert: 100 - (complexity * 5), clamped
            return max(0, min(100, 100 - (score * 5)))
        
        if metric_type == MetricType.PERPLEXITY:
            # Perplexity: 10-100 range, lower is better
            # Invert: 100 - perplexity, clamped
            return max(0, min(100, 100 - score))
        
        if metric_type == MetricType.LINES_OF_CODE:
            # LOC: Assume 100-500 range, lower is better
            # Invert: 100 - (LOC / 5), clamped
            return max(0, min(100, 100 - (score / 5)))
        
        # Default: return as-is
        return score
    
    def _calculate_overall_improvement(
        self,
        original_scores: Dict[MetricType, MetricResult],
        refactored_scores: Dict[MetricType, MetricResult]
    ) -> float:
        """Calculate overall improvement percentage."""
        original_overall = self._calculate_overall_score(original_scores)
        refactored_overall = self._calculate_overall_score(refactored_scores)
        
        if original_overall == 0:
            return 100.0 if refactored_overall > 0 else 0.0
        
        return ((refactored_overall - original_overall) / original_overall) * 100
