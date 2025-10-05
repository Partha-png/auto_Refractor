"""
Refactoring Engine - AI-powered code analysis and refactoring
"""

import os
from dotenv import load_dotenv

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

# Load environment variables
load_dotenv()


class Engine:
    def __init__(self, use_groq=True):
        if use_groq:
            groq_api_key = os.getenv("GROQ_API_KEY")  # FIX: Uppercase
            if not groq_api_key:
                raise ValueError(
                    "GROQ_API_KEY not found in environment variables. "
                    "Add it to your .env file or set use_groq=False"
                )
            
            self.llm = ChatGroq(
                model="deepseek-r1-distill-llama-70b",
                temperature=0,
                api_key=groq_api_key
            )
        else:
            self.llm = Ollama(model="llama3",temperature=0)
        self.tools = [load_file, parse_code, lint_code, analyze_complexity]
        self.agent = create_react_agent(self.llm, self.tools)
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
    
    def analyze_file(self, file_path: str,code):
        query = f"Analyze {file_path,code} using lint_code and analyze_complexity tools"
        try:
            result = self.agent.invoke({"messages": [HumanMessage(content=query)]})
            if isinstance(result, dict) and 'messages' in result:
                messages = result['messages']
                if messages:
                    last_message = messages[-1]
                    return last_message.content
            return str(result)
        except Exception as e:
            return f"Error during analysis: {str(e)}"
    
    def analyze_and_refactor(self, file_path: str,code):
        """
        Run analysis, then refactor code
        
        Args:
            file_path: Path to file to analyze and refactor
            
        Returns:
            Dict with 'issues' and 'refactored_code'
        """
        print(f"📊 Analyzing {file_path}...")
        lint_query = f"Load {file_path,code}, then run lint_code and analyze_complexity on it"
        
        try:
            lint_result = self.agent.invoke({"messages": [HumanMessage(content=lint_query)]})
            
            # Extract analysis from agent response
            if isinstance(lint_result, dict) and 'messages' in lint_result:
                messages = lint_result['messages']
                if messages:
                    issues = messages[-1].content
                else:
                    issues = "No issues found"
            else:
                issues = str(lint_result)
        
        except Exception as e:
            issues = f"Error during analysis: {str(e)}"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_code = f.read()
        except Exception as e:
            return {
                "issues": issues,
                "refactored_code": f"Error reading file: {str(e)}"
            }
        print(f"🔧 Generating refactored code...")
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
            refactored_code = self._clean_code_output(refactored_code)
            
        except Exception as e:
            refactored_code = f"Error during refactoring: {str(e)}"
        
        return {
            "issues": issues,
            "refactored_code": refactored_code
        }
    
    def _clean_code_output(self, code: str) -> str:
        """
        Remove markdown fences and extra formatting from LLM output
        
        Args:
            code: Raw LLM output
            
        Returns:
            Clean code string
        """
        # Remove markdown code fences
        code = code.strip()
        
        if code.startswith("```"):
            lines = code.split("\n")
            # Remove first line (```python or ```)
            lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)
        
        return code.strip()
    
    def review_code(self, file_path: str):
        """
        Get a concise code review (no refactoring)
        
        Args:
            file_path: Path to file to review
            
        Returns:
            Review as string with prioritized issues
        """
        query = f"""Review {file_path} and provide:
1. Top 3-6 most critical issues
2. Priority level for each (Critical/High/Medium/Low)
3. Brief fix suggestion for each

Use the lint_code and analyze_complexity tools."""
        
        try:
            result = self.agent.invoke({"messages": [HumanMessage(content=query)]})
            
            if isinstance(result, dict) and 'messages' in result:
                messages = result['messages']
                if messages:
                    return messages[-1].content
            
            return str(result)
            
        except Exception as e:
            return f"Error during review: {str(e)}"