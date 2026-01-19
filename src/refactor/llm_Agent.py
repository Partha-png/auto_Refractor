from src.analysis.linter import Linter
from src.analysis.complexity import Complexity
from src.ingestion.loader import load_files_from_directory
from src.ingestion.parser import parser_code
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LinterAgent:
    """Agent wrapper for Linter - finds code quality issues."""
    
    def __init__(self, tree, code):
        self.tree = tree
        self.code = code
        self.linter = Linter(tree, code)
    
    def run(self):
        try:
            issues = self.linter.run(self.tree, self.code)
            logger.debug(f"LinterAgent found {len(issues)} issues")
            return {"agent_invoked": "linter_agent", "issues": issues}
        except Exception as e:
            logger.error(f"Error in LinterAgent: {e}")
            return {"agent_invoked": "linter_agent", "issues": [], "error": str(e)}


class ComplexityAgent:
    """Agent wrapper for Complexity - calculates code metrics."""
    
    def __init__(self, code, tree):
        self.code = code
        self.tree = tree
        self.complexity = Complexity(code, tree)
    
    def run(self):
        try:
            metrics = self.complexity.run()
            logger.debug(f"ComplexityAgent calculated metrics: {metrics}")
            return {"agent_invoked": "complexity_agent", "metrics": metrics}
        except Exception as e:
            logger.error(f"Error in ComplexityAgent: {e}")
            return {"agent_invoked": "complexity_agent", "metrics": {}, "error": str(e)}
class LoaderAgent:
    """Agent wrapper for file loading."""
    
    def __init__(self, file_path):
        self.file_path = file_path
    
    def run(self):
        """Load file and return content."""
        try:
            files = load_files_from_directory([self.file_path])
            if not files:
                logger.error(f"No files loaded from {self.file_path}")
                return {"agent_invoked": "loader_agent", "file": None, "error": "No files found"}
            
            logger.debug(f"LoaderAgent loaded {self.file_path}")
            return {"agent_invoked": "loader_agent", "file": files[0]}
        except Exception as e:
            logger.error(f"Error in LoaderAgent: {e}")
            return {"agent_invoked": "loader_agent", "file": None, "error": str(e)}


class ParserAgent:
    """Agent wrapper for code parsing."""
    
    def __init__(self, file_path):
        self.file_path = file_path
    
    def run(self):
        """Parse file and return AST."""
        try:
            results = parser_code([self.file_path])
            if not results:
                logger.error(f"No results from parsing {self.file_path}")
                return {"agent_invoked": "parser_agent", "error": "No parse results"}
            
            file = results[0]
            logger.debug(f"ParserAgent parsed {self.file_path}")
            return {
                "agent_invoked": "parser_agent",
                "ast_tree": file["tree"],
                "code": file["content"],
                "path": file["path"]
            }
        except Exception as e:
            logger.error(f"Error in ParserAgent: {e}")
            return {"agent_invoked": "parser_agent", "error": str(e)}