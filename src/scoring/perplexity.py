"""Perplexity metric for code naturalness (optional, resource-intensive)."""

from typing import Optional
from src.scoring.metrics import BaseMetric, MetricResult
from src.config.constants import MetricType
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PerplexityMetric(BaseMetric):
    """
    Perplexity metric for code naturalness.
    
    Measures how "natural" or "readable" the code is using a language model.
    Lower perplexity = more natural/readable code.
    
    Note: This is resource-intensive and requires a code-specific LM.
    Disabled by default in settings.
    """
    
    @property
    def metric_type(self) -> MetricType:
        return MetricType.PERPLEXITY
    
    @property
    def description(self) -> str:
        return "Code naturalness/readability (lower is better)"
    
    @property
    def higher_is_better(self) -> bool:
        return False  # Lower perplexity is better
    
    def calculate(self, code: str, language: str) -> MetricResult:
        """
        Calculate perplexity for code.
        
        Note: This is a placeholder implementation.
        Full implementation would require:
        1. A code-specific language model (e.g., CodeGPT, CodeBERT)
        2. Tokenization specific to programming languages
        3. Significant computational resources
        
        For now, returns a simplified metric based on code characteristics.
        """
        if not settings.enable_perplexity:
            return MetricResult(
                metric_type=self.metric_type,
                score=0.0,
                description=self.description,
                details={"error": "Perplexity calculation disabled in settings"}
            )
        
        try:
            # Simplified perplexity estimation based on code characteristics
            score = self._estimate_perplexity(code)
            
            return MetricResult(
                metric_type=self.metric_type,
                score=score,
                description=self.description,
                details={
                    "note": "Simplified estimation, not true perplexity",
                    "method": "heuristic"
                }
            )
        
        except Exception as e:
            logger.error(f"Error calculating perplexity: {e}")
            return MetricResult(
                metric_type=self.metric_type,
                score=0.0,
                description=self.description,
                details={"error": str(e)}
            )
    
    def _estimate_perplexity(self, code: str) -> float:
        """
        Estimate perplexity using heuristics.
        
        This is a simplified approach that considers:
        - Average line length
        - Token diversity
        - Nesting depth indicators
        
        Returns a score roughly in the range 10-100.
        """
        lines = [line for line in code.split('\n') if line.strip()]
        
        if not lines:
            return 10.0  # Minimal perplexity for empty code
        
        # Calculate average line length
        avg_line_length = sum(len(line) for line in lines) / len(lines)
        
        # Calculate token diversity (unique tokens / total tokens)
        tokens = code.split()
        if tokens:
            diversity = len(set(tokens)) / len(tokens)
        else:
            diversity = 1.0
        
        # Estimate based on line length and diversity
        # Longer lines and lower diversity = higher perplexity (less readable)
        estimated_perplexity = (avg_line_length / 2) * (1 / diversity)
        
        # Clamp to reasonable range
        return max(10.0, min(100.0, estimated_perplexity))
