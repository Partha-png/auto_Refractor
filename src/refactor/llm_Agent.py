from src.analysis.linter import Linter
from src.analysis.complexity import Complexity
from src.ingestion.loader import load_files_from_directory
from src.ingestion.parser import parser_code
class LinterAgent:
    def __init__(self,tree,code,rules=None):
        self.linter=Linter(tree,code,rules)
    def run(self):
        issues=self.linter.run()
        return{"agent invoked":"linter agent","issues":issues}
class ComplexityAgent:
    def __init__(self,code,tree):
        self.complexity=Complexity(code,tree)
    def run(self):
        metrics=self.complexity.run()
        return {"agent invoked":"complexity agent","metrics":metrics}
class LoaderAgent:
    def __init__ (self,file_path):
        self.file_path=file_path
    def run(self):
        files = load_files_from_directory([self.file_path])
        return {"agent invoked": "loader agent", "file": files[0]}
class ParserAgent:
    def __init__(self,file_path):
        self.file_path=file_path
    def run(self):
        results=parser_code([self.file_path])
        file=results[0]
        return  {"agent invoked":"parser agent",
    "ast_tree":file["tree"],
    "code":file["content"],
    "path":file["path"]}