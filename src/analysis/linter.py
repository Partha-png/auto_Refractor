from src.analysis.rules.unused_variables import unused_variables
from src.analysis.rules.unused_imports import unused_imports
from src.analysis.rules.too_many_args import check_too_many_args
from src.analysis.rules.security_rules import dangerous_functions
from src.analysis.rules.function_length import check_function_length
from src.analysis.rules.deep_nesting import deep_nesting
class Linter:
    def __init__(self, tree, code,rules=None):
        self.tree=tree
        self.code=code
        default_rules=[
            unused_variables,
            unused_imports,
            check_too_many_args,
            dangerous_functions,
            check_function_length,
            deep_nesting
        ]
        self.rules= rules or default_rules
    def run(self,tree,code):
        issues=[]
        for rule in self.rules:
            issues.extend(rule(tree,code))
        return issues