from langchain.tools import tool
from src.refactor.llm_Agent import LinterAgent, ComplexityAgent, LoaderAgent, ParserAgent
from src.ingestion.parser import parser_code
@tool("load_file",return_direct=False)
def load_file(file_path):
    """ creating the loader file tool """
    return LoaderAgent(file_path).run()
@tool("parse_Code",return_direct=False)
def parse_code(file_path):
    """ creating the parser file tool """
    return ParserAgent(file_path).run()
@tool("lint_code",return_direct=True)
def lint_code(file_path):
    """ creating the linter tool """
    tree=parser_code(file_path)
    with open(file_path ,"r", encoding="utf-8") as f:
        code=f.read()
    return LinterAgent(tree,code).run()
@tool("analyze_complexity",return_direct=True)
def analyze_complexity(file_path):
    """ creating the complexity analyzer tool """
    with open(file_path,"r",encoding="utf-8") as f:
        code=f.read()
    tree=parser_code(file_path)
    return ComplexityAgent(code,tree).run()