from pathlib import Path

from langchain_groq import ChatGroq
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from src.ingestion.parser import parser_code
from src.ingestion.loader import detect_lang
from src.refactor.llm_Agent import LinterAgent, ComplexityAgent
from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.helpers import clean_code_output
from src.scoring.scorer import CodeScorer

logger = get_logger(__name__)


class Engine:
    def __init__(self, use_groq=None):
        """Initialize refactoring engine with LLM and analysis tools."""
        # Use settings if not specified
        if use_groq is None:
            use_groq = settings.use_groq
        
        # Initialize LLM
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
        
        # Initialize scorer
        self.scorer = CodeScorer()
        logger.info("Initialized CodeScorer")
        
        # Refactoring prompt template
        self.refactor_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are an expert code refactoring assistant. Your goal is to IMPROVE code quality while preserving functionality.

CRITICAL CONSTRAINTS:
1. Preserve the public API - do NOT change function signatures, parameter names, or return types
2. Return ONLY valid, parseable code - test your syntax mentally before responding
3. Do NOT add new imports unless absolutely necessary for the fix
4. Do NOT introduce new issues while fixing old ones
5. Fix ALL security issues (eval, exec, unsafe operations)
6. Ensure the refactored code is BETTER than the original

REFACTORING PRIORITIES (in order):
1. FIX SECURITY ISSUES - Replace eval(), exec() with safe alternatives
2. REMOVE UNUSED CODE - Delete unused imports, variables, and dead code
3. REDUCE COMPLEXITY - Simplify nested conditions, extract helper functions if needed
4. IMPROVE READABILITY - Use clear names, add type hints if helpful
5. REDUCE ARGUMENTS - Group related parameters into dataclasses/dicts if >5 args

OUTPUT RULES:
- Return ONLY the refactored code, no explanation
- Do not use markdown code fences (no ```)
- Do not add comments explaining what you changed
- Ensure proper indentation and valid Python syntax
- Do not add __main__ blocks unless they were in the original

VALIDATION CHECKLIST (before responding):
✓ Is the syntax valid?
✓ Are all imports actually used?
✓ Did I preserve the original function signatures?
✓ Did I fix the security issues?
✓ Is the code simpler and more readable?
"""
            ),
            HumanMessagePromptTemplate.from_template(
                """Original Code:
{code}

Issues Found by Analysis:
{issues}

Refactored Code:"""
            )
        ])
        
        logger.info("Refactoring engine initialized successfully")
    
    def _format_linter_issues(self, issues):
        """Format linter issues for display."""
        if not issues:
            return "No issues found."
        
        formatted = []
        for issue in issues[:10]:  # Limit to top 10 for LLM context
            line = issue.get('line', '?')
            type_name = issue.get('type', 'Unknown')
            message = issue.get('message', '')
            formatted.append(f"  Line {line}: [{type_name}] {message}")
        
        if len(issues) > 10:
            formatted.append(f"  ... and {len(issues) - 10} more issues")
        
        return "\n".join(formatted)
    
    def analyze_and_refactor(self, file_path: str, code: str):
        """
        Run analysis, then refactor code.
        
        DETERMINISTIC ANALYSIS: Always runs linter and complexity analyzer.
        
        Args:
            file_path: Path to file to analyze and refactor
            code: Source code content
            
        Returns:
            Dict with 'issues', 'refactored_code', and optionally 'scores'
        """
        logger.info(f"Starting analysis and refactoring for: {file_path}")
        
        # STEP 1: COMPULSORY ANALYSIS
        try:
            logger.debug("Parsing file for analysis")
            results = parser_code([file_path])
            
            if not results or not results[0].get("tree"):
                logger.error(f"Failed to parse {file_path}")
                issues = "Error: Could not parse file for analysis"
            else:
                file_data = results[0]
                tree = file_data["tree"]
                content = file_data["content"]
                language = file_data.get("language", detect_lang(file_path))
                
                # Run linter (COMPULSORY)
                logger.info(f"Running linter for {language} code")
                linter_result = LinterAgent(tree, content, language).run()
                
                # Run complexity analysis (COMPULSORY)
                logger.info(f"Running complexity analysis for {language} code")
                complexity_result = ComplexityAgent(content, tree, language).run()
                
                # Format results
                linter_issues = linter_result.get("issues", [])
                complexity_metrics = complexity_result.get("metrics", {})
                
                issues = f"""Code Analysis Results:

Linter found {len(linter_issues)} issues:
{self._format_linter_issues(linter_issues)}

Complexity Metrics:
- Cyclomatic Complexity: {complexity_metrics.get('cyclomatic', 'N/A')}
- Lines of Code: {complexity_metrics.get('loc', 'N/A')}
- Max Nesting Depth: {complexity_metrics.get('nesting', 'N/A')}
"""
                logger.info("Analysis complete")
        
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            issues = f"Error during analysis: {str(e)}"
        
        # STEP 2: REFACTOR
        logger.info("Generating refactored code with LLM")
        try:
            refactor_chain = self.refactor_prompt | self.llm
            response = refactor_chain.invoke({
                "code": code,
                "issues": issues
            })
            
            refactored_code = response.content if hasattr(response, 'content') else str(response)
            refactored_code = clean_code_output(refactored_code)
            logger.info("Refactoring complete")
            
            # STEP 3: CALCULATE SCORES (optional, doesn't block on failure)
            try:
                logger.info("Calculating quality scores")
                language = detect_lang(file_path)
                
                comparison = self.scorer.compare_code(
                    original_code=code,
                    refactored_code=refactored_code,
                    language=language
                )
                
                logger.info(f"Scores calculated - Improvement: {comparison.overall_improvement:.1f}")
                
                return {
                    "issues": issues,
                    "refactored_code": refactored_code,
                    "scores": {
                        "original": comparison.original_scores,
                        "refactored": comparison.refactored_scores,
                        "improvement": comparison.overall_improvement
                    }
                }
            except Exception as e:
                logger.warning(f"Error calculating scores: {e}")
                return {
                    "issues": issues,
                    "refactored_code": refactored_code
                }
            
        except Exception as e:
            logger.error(f"Error during refactoring: {e}")
            return {
                "issues": issues,
                "refactored_code": f"Error during refactoring: {str(e)}"
            }


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
