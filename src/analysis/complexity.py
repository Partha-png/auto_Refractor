from src.analysis.ast_complexity import calculate_complexity
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Complexity:
    def __init__(self, code, tree, language="python"):
        self.code = code
        self.tree = tree
        self.language = language
        self.lines = code.splitlines()
        logger.debug(f"Initialized complexity analyzer for {len(self.lines)} lines of code ({language})")
    
    def run(self):
        logger.info("Calculating complexity metrics")
        metrics = {
            "cyclomatic": self.cyclomatic(),
            "loc": self.line_of_code(),
            "nesting": self.is_nesting()
        }
        logger.info(f"Complexity metrics: {metrics}")
        return metrics
    
    def cyclomatic(self):
        """Calculate cyclomatic complexity using Tree-sitter AST."""
        if not self.tree:
            logger.warning("No AST found, complexity defaults to 1")
            return 1
            
        return calculate_complexity(self.tree, self.language)
    
    def line_of_code(self):
        count = 0
        for line in self.lines:
            if line.strip():
                count += 1
        logger.debug(f"Lines of code: {count}")
        return count
    
    def is_nesting(self):
        """
        Estimate nesting depth.
        TODO: Use AST for this too in future iterations.
        """
        max_depth = 0
        for line in self.lines:
            striped = line.lstrip()
            if not striped: continue
            indent = len(line) - len(striped)
            level = indent // 4
            max_depth = max(level, max_depth)
        logger.debug(f"Max nesting depth: {max_depth}")
        return max_depth