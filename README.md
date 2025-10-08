## Auto-Refractor
Auto-Refractor is an intelligent code analysis and refactoring system that automatically reviews GitHub pull requests. It leverages AI-powered agents to detect code issues, suggest improvements, and generate refactored versions while maintaining code functionality and best practices.
The project was inspired by a personal goal: to automate code quality reviews and reduce manual effort in maintaining clean, efficient codebases, while exploring the capabilities of LLM-based code analysis and tree-sitter parsing.

🔍 Automated PR Analysis: scans open pull requests for code quality issues
🧠 AI-Powered Refactoring: generates improved code using LLMs (Groq/Ollama)
🎯 Multi-Rule Linting: detects unused variables, security issues, and complexity
📊 Complexity Metrics: measures cyclomatic complexity, nesting depth, and LOC
🔗 GitHub Integration: seamless PR commenting and branch management

## 🛠️ Installation

1. Clone the repository:
```
git clone https://github.com/partha-png/auto_Refractor.git
cd auto_Refractor
```

2. Create a virtual environment and activate it:
```
python -m venv venv
venv\Scripts\activate
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```
4. Set up environment variables: Create a .env file in the root directory and add your API keys:
```
GITHUB_TOKEN=your_github_personal_access_token
GROQ_API_KEY=your_groq_api_key
```
## 🏗️ Project Structure
```
auto_Refractor/
├── src/                        # Source code
│   ├── analysis/              # Code analysis components
│   │   ├── rules/            # Linting rule implementations
│   │   ├── complexity.py     # Complexity analyzer
│   │   └── linter.py         # Main linting engine
│   ├── github/               # GitHub API integration
│   │   ├── client.py        # GitHub client wrapper
│   │   └── pr_monitor.py    # PR monitoring system
│   ├── ingestion/           # Code parsing and loading
│   │   ├── loader.py        # File loader utilities
│   │   └── parser.py        # Tree-sitter parser
│   └── refactor/            # Refactoring engine
│       ├── engine.py        # Main refactoring orchestrator
│       ├── llm_Agent.py     # LLM agent implementations
│       └── tools.py         # LangChain tool definitions
├── sample.py                  # Sample Python file for testing
├── sample.js                  # Sample JavaScript file
├── sample.cpp                 # Sample C++ file
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```
## 🤖 How It Works

1. PR Monitoring:

Fetches all open pull requests from a repository
Identifies changed files in each PR
Filters for supported programming languages


2. Code Analysis:

Parses code using tree-sitter for AST generation
Runs multiple linting rules in parallel
Calculates complexity metrics
Generates detailed issue reports


3. AI Refactoring:

Sends code and issues to LLM (Groq/Ollama)
Receives refactored version, maintaining functionality
Validates and cleans LLM output
Post suggestions as PR comments



## 📖 Research Inspiration
Auto-Refractor's architecture leverages modern approaches in code analysis:
[1] "Tree-sitter: A New Parsing System for Programming Tools" - GitHub Engineering, 2018
[2] "Large Language Models for Code: Survey and Open Problems" - Fan et al., 2023
Auto-Refractor applies these ideas by:

Using tree-sitter for language-agnostic AST parsing
Implementing LLM-based code understanding and generation
Combining static analysis with AI-powered suggestions

## 🛡️ License
This project is licensed under the Apache License 2.0 - please take a look at the LICENSE file for details.

## 🙏 Acknowledgments

Built with LangChain and LangGraph
Powered by Groq API and Ollama
AST parsing via Tree-sitter
GitHub integration using PyGithub
LLM models: DeepSeek-R1 and Llama3
