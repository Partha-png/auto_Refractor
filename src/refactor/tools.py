from langchain.tools import tool
from src.refactor.llm_Agent import LinterAgent, ComplexityAgent
from src.ingestion.parser import parser_code
from src.utils.logger import get_logger

logger = get_logger(__name__)

# @tool("load_file", return_direct=False)
# def load_file(file_path: str):
#     """Load file content - Reserved for future agent-driven workflows."""
#     try:
#         return LoaderAgent(file_path).run()
#     except Exception as e:
#         logger.error(f"Error in load_file tool: {e}")
#         return {"agent_invoked": "loader_agent", "error": str(e)}

# @tool("parse_Code", return_direct=False)
# def parse_code(file_path: str):
#     """Parse code into AST - Reserved for future agent-driven workflows."""
#     try:
#         return ParserAgent(file_path).run()
#     except Exception as e:
#         logger.error(f"Error in parse_code tool: {e}")
#         return {"agent_invoked": "parser_agent", "error": str(e)}

@tool("lint_code", return_direct=True)
def lint_code(file_path: str):
    """Find code quality issues using linter."""
    try:
        results = parser_code([file_path])
        if not results or not results[0].get("tree"):
            logger.error(f"Failed to parse {file_path} for linting")
            return {"agent_invoked": "linter_agent", "issues": [], "error": "Parse failed"}
        
        file_data = results[0]
        language = file_data.get("language", "python")  # Get language from parser
        return LinterAgent(file_data["tree"], file_data["content"], language).run()
    except Exception as e:
        logger.error(f"Error in lint_code tool: {e}")
        return {"agent_invoked": "linter_agent", "issues": [], "error": str(e)}

@tool("analyze_complexity", return_direct=True)
def analyze_complexity(file_path: str):
    """Analyze code complexity metrics."""
    try:
        results = parser_code([file_path])
        if not results or not results[0].get("tree"):
            logger.error(f"Failed to parse {file_path} for complexity analysis")
            return {"agent_invoked": "complexity_agent", "metrics": {}, "error": "Parse failed"}
        
        file_data = results[0]
        # Pass language if available, default to python
        language = file_data.get("language", "python")
        return ComplexityAgent(file_data["content"], file_data["tree"], language).run()
    except Exception as e:
        logger.error(f"Error in analyze_complexity tool: {e}")
        return {"agent_invoked": "complexity_agent", "metrics": {}, "error": str(e)}