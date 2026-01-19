from pathlib import Path

from langchain_groq import ChatGroq
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

from src.refactor.tools import load_file, parse_code, lint_code, analyze_complexity
from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.helpers import clean_code_output
from src.scoring.scorer import CodeScorer
from src.refactor.report_generator import format_score_report, generate_comparison_table

logger = get_logger(__name__)


class Engine:
    def __init__(self, use_groq=None):
        # Use settings if not specified
        if use_groq is None:
            use_groq = settings.use_groq
        
        if use_groq:
            if not settings.groq_api_key:
                raise ValueError(
                    "GROQ_API_KEY not found in environment variables. "
                    "Add it to your .env file or set use_groq=False"
                )
            
            logger.info(f"Initializing Groq LLM with model: {settings.llm_model}")
            self.llm = ChatGroq(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.groq_api_key
            )
        else:
            logger.info("Initializing Ollama LLM")
            self.llm = Ollama(model="llama3", temperature=settings.llm_temperature)
        
        self.tools = [load_file, parse_code, lint_code, analyze_complexity]
        self.agent = create_react_agent(self.llm, self.tools)
        
        # Initialize scorer
        self.scorer = CodeScorer()
        logger.info("Initialized CodeScorer")
        
        self.refactor_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are a professional code-refactoring assistant.

Given the following code and its issues, produce a refactored version.

Rules:
- Return ONLY the refactored code, no explanation
- Preserve functionality and public API
- Fix all mentioned issues
- Use idiomatic, clean code
- Do not add comments explaining changes
- Do not use markdown fences (no ```)
"""
            ),
            HumanMessagePromptTemplate.from_template(
                """Original Code:
{code}

Issues Found:
{issues}

Refactored Code:"""
            )
        ])
        
        logger.info("Refactoring engine initialized successfully")
    
    def analyze_file(self, file_path: str, code: str):
        """Analyze file using linter and complexity tools."""
        logger.info(f"Analyzing file: {file_path}")
        query = f"Analyze {file_path,code} using lint_code and analyze_complexity tools"
        try:
            result = self.agent.invoke({"messages": query})
            if isinstance(result, dict) and 'messages' in result:
                messages = result['messages']
                if messages:
                    last_message = messages[-1]
                    return last_message.content
            return str(result)
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            return f"Error during analysis: {str(e)}"
    
    def analyze_and_refactor(self, file_path: str, code: str):
        """
        Run analysis, then refactor code
        
        Args:
            file_path: Path to file to analyze and refactor
            code: Source code content
            
        Returns:
            Dict with 'issues' and 'refactored_code'
        """
        logger.info(f"Starting analysis and refactoring for: {file_path}")
        lint_query = f"Load {file_path,code}, then run lint_code and analyze_complexity on it"
        
        try:
            logger.debug("Running linting and complexity analysis")
            lint_result = self.agent.invoke({"messages": lint_query})
            
            # Extract analysis from agent response
            if isinstance(lint_result, dict) and 'messages' in lint_result:
                messages = lint_result['messages']
                if messages:
                    issues = messages[-1].content
                else:
                    issues = "No issues found"
            else:
                issues = str(lint_result)
            
            logger.info("Analysis complete")
        
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            issues = f"Error during analysis: {str(e)}"
        
        try:
            original_code = Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {
                "issues": issues,
                "refactored_code": f"Error reading file: {str(e)}"
            }
        
        logger.info("Generating refactored code with LLM")
        try:
            refactor_chain = self.refactor_prompt | self.llm
            response = refactor_chain.invoke({
                "code": original_code,
                "issues": issues
            })
            if hasattr(response, 'content'):
                refactored_code = response.content
            else:
                refactored_code = str(response)
            
            # Use helper function for cleaning
            refactored_code = clean_code_output(refactored_code)
            logger.info("Refactoring complete")
            
            # Calculate scores
            try:
                logger.info("Calculating quality scores")
                # Detect language from file extension
                language = "python"  # Default
                if file_path.endswith(".js"):
                    language = "javascript"
                elif file_path.endswith((".java", ".cpp", ".c")):
                    language = "java"
                
                # Calculate scores for original and refactored code
                comparison = self.scorer.compare_code(
                    original=original_code,
                    refactored=refactored_code,
                    language=language
                )
                
                logger.info(f"Scores calculated - Improvement: {comparison.improvement:.1f}")
                
                return {
                    "issues": issues,
                    "refactored_code": refactored_code,
                    "scores": {
                        "original": comparison.original_scores,
                        "refactored": comparison.refactored_scores,
                        "improvement": comparison.improvement
                    }
                }
            except Exception as e:
                logger.warning(f"Error calculating scores: {e}")
                # Return without scores if scoring fails
                return {
                    "issues": issues,
                    "refactored_code": refactored_code
                }
            
        except Exception as e:
            logger.error(f"Error during refactoring: {e}")
            refactored_code = f"Error during refactoring: {str(e)}"
        
        return {
            "issues": issues,
            "refactored_code": refactored_code
        }
    
    def review_code(self, file_path: str, code: str):
        """
        Get a concise code review (no refactoring)
        
        Args:
            file_path: Path to file to review
            code: Source code content
            
        Returns:
            Review as string with prioritized issues
        """
        logger.info(f"Reviewing code for: {file_path}")
        query = f"""Review {file_path,code} and provide:
1. Top 3-6 most critical issues
2. Priority level for each (Critical/High/Medium/Low)
3. Brief fix suggestion for each

Use the lint_code and analyze_complexity tools."""
        
        try:
            result = self.agent.invoke({"messages": [HumanMessage(content=query)]})
            
            if isinstance(result, dict) and 'messages' in result:
                messages = result['messages']
                if messages:
                    review = messages[-1].content
                    logger.info("Code review complete")
                    return review
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Error during review: {e}")
            return f"Error during review: {str(e)}"


if __name__ == "__main__":
    from src.utils.logger import setup_logging
    
    # Setup logging for testing
    setup_logging(log_level="INFO")
    
    engine = Engine(use_groq=True)
    test_file = "src/refactor/sample.py"
    
    try:
        code = Path(test_file).read_text(encoding="utf-8")
        logger.info(f"Loaded test file: {test_file}")
    except Exception as e:
        logger.error(f"Error reading {test_file}: {e}")
        code = ""
    
    if code:
        result = engine.analyze_and_refactor(test_file, code)
        print("\n" + "="*50)
        print("Issues Found:")
        print("="*50)
        print(result["issues"])
        
        print("\n" + "="*50)
        print("Refactored Code:")
        print("="*50)
        print(result["refactored_code"])
        
        print("\n" + "="*50)
        print("Code Review:")
        print("="*50)
        review = engine.review_code(test_file, code)
        print(review)
