"""Code quality metrics using radon and custom calculations."""

from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze
from src.scoring.metrics import BaseMetric, MetricResult
from src.config.constants import MetricType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CyclomaticComplexityMetric(BaseMetric):
    """
    Cyclomatic complexity metric.
    
    Measures code complexity through control flow.
    Lower scores are better (simpler code).
    """
    
    @property
    def metric_type(self) -> MetricType:
        return MetricType.CYCLOMATIC_COMPLEXITY
    
    @property
    def description(self) -> str:
        return "Code complexity through control flow (lower is better)"
    
    @property
    def higher_is_better(self) -> bool:
        return False  # Lower complexity is better
    
    def calculate(self, code: str, language: str) -> MetricResult:
        """Calculate average cyclomatic complexity."""
        if language != "python":
            # Radon only supports Python
            return MetricResult(
                metric_type=self.metric_type,
                score=0.0,
                description=self.description,
                details={"error": f"Language {language} not supported"}
            )
        
        try:
            # Calculate complexity for all functions/methods
            complexities = cc_visit(code)
            
            if not complexities:
                return MetricResult(
                    metric_type=self.metric_type,
                    score=1.0,  # Minimal complexity
                    description=self.description,
                    details={"functions": 0}
                )
            
            # Calculate average complexity
            avg_complexity = sum(c.complexity for c in complexities) / len(complexities)
            
            # Get max complexity
            max_complexity = max(c.complexity for c in complexities)
            
            return MetricResult(
                metric_type=self.metric_type,
                score=avg_complexity,
                description=self.description,
                details={
                    "average": avg_complexity,
                    "max": max_complexity,
                    "functions": len(complexities),
                    "breakdown": [
                        {"name": c.name, "complexity": c.complexity}
                        for c in complexities
                    ]
                }
            )
        
        except Exception as e:
            logger.error(f"Error calculating cyclomatic complexity: {e}")
            return MetricResult(
                metric_type=self.metric_type,
                score=0.0,
                description=self.description,
                details={"error": str(e)}
            )


class MaintainabilityIndexMetric(BaseMetric):
    """
    Maintainability Index metric.
    
    Overall maintainability score (0-100).
    Higher scores are better (more maintainable).
    """
    
    @property
    def metric_type(self) -> MetricType:
        return MetricType.MAINTAINABILITY_INDEX
    
    @property
    def description(self) -> str:
        return "Overall maintainability score (0-100, higher is better)"
    
    def calculate(self, code: str, language: str) -> MetricResult:
        """Calculate maintainability index."""
        if language != "python":
            return MetricResult(
                metric_type=self.metric_type,
                score=0.0,
                description=self.description,
                details={"error": f"Language {language} not supported"}
            )
        
        try:
            # Calculate MI for all blocks
            mi_scores = mi_visit(code, multi=True)
            
            if not mi_scores:
                return MetricResult(
                    metric_type=self.metric_type,
                    score=100.0,  # Perfect score for empty/simple code
                    description=self.description,
                    details={"blocks": 0}
                )
            
            # Calculate average MI
            avg_mi = sum(mi_scores) / len(mi_scores)
            
            # MI is typically 0-100, higher is better
            # Clamp to 0-100 range
            avg_mi = max(0, min(100, avg_mi))
            
            return MetricResult(
                metric_type=self.metric_type,
                score=avg_mi,
                description=self.description,
                details={
                    "average": avg_mi,
                    "blocks": len(mi_scores),
                    "min": min(mi_scores),
                    "max": max(mi_scores),
                }
            )
        
        except Exception as e:
            logger.error(f"Error calculating maintainability index: {e}")
            return MetricResult(
                metric_type=self.metric_type,
                score=0.0,
                description=self.description,
                details={"error": str(e)}
            )


class LinesOfCodeMetric(BaseMetric):
    """
    Lines of Code (LOC) metric.
    
    Counts source lines of code (excluding comments and blanks).
    Lower is better for same functionality.
    """
    
    @property
    def metric_type(self) -> MetricType:
        return MetricType.LINES_OF_CODE
    
    @property
    def description(self) -> str:
        return "Source lines of code (lower is better)"
    
    @property
    def higher_is_better(self) -> bool:
        return False  # Fewer lines is better
    
    def calculate(self, code: str, language: str) -> MetricResult:
        """Calculate lines of code metrics."""
        try:
            if language == "python":
                # Use radon for Python
                analysis = analyze(code)
                sloc = analysis.sloc  # Source lines of code
                comments = analysis.comments
                blank = analysis.blank
                total = analysis.loc
            else:
                # Simple line counting for other languages
                lines = code.split('\n')
                total = len(lines)
                blank = sum(1 for line in lines if not line.strip())
                # Simple comment detection (not perfect)
                comments = sum(1 for line in lines if line.strip().startswith(('#', '//')))
                sloc = total - blank - comments
            
            return MetricResult(
                metric_type=self.metric_type,
                score=float(sloc),
                description=self.description,
                details={
                    "sloc": sloc,
                    "total": total,
                    "comments": comments,
                    "blank": blank,
                }
            )
        
        except Exception as e:
            logger.error(f"Error calculating LOC: {e}")
            # Fallback to simple line count
            sloc = len([line for line in code.split('\n') if line.strip()])
            return MetricResult(
                metric_type=self.metric_type,
                score=float(sloc),
                description=self.description,
                details={"sloc": sloc, "error": str(e)}
            )
