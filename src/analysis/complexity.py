from src.utils.logger import get_logger

logger = get_logger(__name__)


class Complexity:
    def __init__(self, code, tree):
        self.code = code
        self.tree = tree
        self.lines = code.splitlines()
        logger.debug(f"Initialized complexity analyzer for {len(self.lines)} lines of code")
    
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
        count = 1
        keywords = ["if", "elif", "for", "while", "case"]
        for line in self.lines:
            for kw in keywords:
                if kw in line:
                    count += 1
        logger.debug(f"Cyclomatic complexity: {count}")
        return count
    
    def line_of_code(self):
        count = 0
        for line in self.lines:
            if line.strip():
                count += 1
        logger.debug(f"Lines of code: {count}")
        return count
    
    def is_nesting(self):
        max_depth = 0
        for line in self.lines:
            striped = line.lstrip()
            indent = len(line) - len(striped)
            level = indent // 4
            max_depth = max(level, max_depth)
        logger.debug(f"Max nesting depth: {max_depth}")
        return max_depth