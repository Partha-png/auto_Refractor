import os
from dotenv import load_dotenv

from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.agents import initialize_agent, AgentType
from langchain.chains import LLMChain

from src.refactor.tools import load_file, parse_code, lint_code, analyze_complexity


class Engine:
    def __init__(self):
            # Hugging Face LLM
        self.llm =  Ollama(model="llama3")
        # Register tools
        self.tools = [load_file, parse_code, lint_code, analyze_complexity]

        # Agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

        # Refactor prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    """You are a professional code-refactoring assistant. 
You have access to the following tools:
{tools}

Behavior rules:
- Use the available tools (load_file, parse_code, lint_code, analyze_complexity) to fetch facts and analysis.
- If the user asks to refactor code, return ONLY the refactored source code, no commentary, no markdown fences, no extra text.
- If the user asks for a review, produce a concise prioritized list of issues and suggested fixes (3–6 bullets).
- Preserve functionality and public API. Prefer minimal, idiomatic changes.
- Do not reveal internal reasoning or tool call formatting.
- For multiple files, clearly label which file each output refers to.
"""
                ),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Refactor chain
        self.refactor_chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def analyze_file(self, file_path: str):
        """Run analysis only (lint + complexity)."""
        query = f"Analyze {file_path} using the available tools"
        return self.agent.run(query)

    def analyze_and_refactor(self, file_path: str):
        """Run analysis, then refactor code."""
        lint_query = f"Load {file_path}, parse it, and run lint_code"
        lint_result = self.agent.run(lint_query)

        with open(file_path, "r") as f:
            original_code = f.read()

        refactored_code = self.refactor_chain.run(
            code=original_code,
            issues=lint_result
        )

        return {
            "issues": lint_result,
            "refactored_code": refactored_code
        }
if __name__ == "__main__":
    engine = Engine()
    file = "src/sample.py"

    print("\n=== Analysis ===")
    analysis = engine.analyze_file(file)
    print(analysis)

    print("\n=== Refactor ===")
    results = engine.analyze_and_refactor(file)
    print("Issues:", results["issues"])
    print("Refactored Code:\n", results["refactored_code"])