"""Code quality metrics using radon and custom calculations."""

from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze
from src.scoring.metrics import BaseMetric, MetricResult
from src.config.constants import MetricType
from src.utils.logger import get_logger
from src.ingestion.parser import parse_content
from src.analysis.ast_complexity import calculate_complexity

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
        # Use Tree-sitter AST for all supported languages
        try:
            tree = parse_content(code, language)
            
            if not tree:
                return MetricResult(
                    metric_type=self.metric_type,
                    score=0.0,
                    description=self.description,
                    details={"error": "Could not parse code"}
                )
            
            # Calculate complexity
            complexity = calculate_complexity(tree, language)
            
            return MetricResult(
                metric_type=self.metric_type,
                score=float(complexity),
                description=self.description,
                details={
                    "average": complexity, # AST gives total complexity usually, or we can assume it's one block if small
                    "functions": 1, # Simplified for now
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
    def metric_type() -> MetricType:
        return MetricType.MAINTAINABILITY_INDEX
    
    @property
    def description(self) -> str:
        return "Overall maintainability score (0-100, higher is better)"
    
    def calculate(self, code: str, language: str) -> MetricResult:
        """Calculate maintainability index (language-agnostic approach)."""
        
        # For Python, use radon if available
        if language == "python":
            try:
                mi_result = mi_visit(code, multi=True)
                
                # Handle different return types from radon
                if isinstance(mi_result, (int, float)):
                    mi_score = float(mi_result)
                elif isinstance(mi_result, list) and len(mi_result) > 0:
                    if hasattr(mi_result[0], 'mi'):
                        mi_score = sum(item.mi for item in mi_result) / len(mi_result)
                    else:
                        mi_score = sum(mi_result) / len(mi_result)
                else:
                    mi_score = None
                
                if mi_score is not None:
                    mi_score = max(0.0, min(100.0, mi_score))
                    return MetricResult(
                        metric_type=self.metric_type,
                        score=mi_score,
                        description=self.description,
                        details={"method": "radon", "value": mi_score}
                    )
            except Exception as e:
                logger.debug(f"Radon MI failed, using fallback: {e}")
        
        # FALLBACK: Language-agnostic heuristic
        # Based on: complexity, LOC, comment ratio
        try:
            from src.analysis.ast_complexity import calculate_complexity
            from src.ingestion.parser import parse_content
            
            # Get complexity
            tree = parse_content(code, language)
            if tree:
                complexity = calculate_complexity(tree, code)
            else:
                complexity = 10
            
            # Get LOC
            lines = [line for line in code.split('\n') if line.strip()]
            loc = len(lines)
            
            # Get comment ratio (rough estimate)
            comment_chars = {
                'python': '#',
                'javascript': '//',
                'java': '//',
                'cpp': '//',
                'c': '//',
                'ruby': '#',
                'go': '//',
                'rust': '//'
            }
            comment_char = comment_chars.get(language, '#')
            comments = sum(1 for line in lines if line.strip().startswith(comment_char))
            comment_ratio = comments / loc if loc > 0 else 0
            
            # Heuristic formula (similar to MI concept)
            #  High MI = Low complexity + Reasonable size + Good comments
            base_score = 100
            base_score -= min(complexity * 2, 40)  # Penalize complexity (max -40)
            base_score -= min(loc / 10, 30)         # Penalize large files (max -30)
            base_score += min(comment_ratio * 50, 20)  # Reward comments (max +20)
            
            mi_score = max(0.0, min(100.0, base_score))
            
            return MetricResult(
                metric_type=self.metric_type,
                score=mi_score,
                description=self.description,
                details={
                    "method": "heuristic",
                    "complexity": complexity,
                    "loc": loc,
                    "comment_ratio": round(comment_ratio, 2)
                }
            )
        
        except Exception as e:
            logger.error(f"Error calculating maintainability index: {e}")
            return MetricResult(
                metric_type=self.metric_type,
                score=50.0,
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
