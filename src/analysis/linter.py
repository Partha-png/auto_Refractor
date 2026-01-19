from src.analysis.rules.unused_variables import unused_variables
from src.analysis.rules.unused_imports import unused_imports
from src.analysis.rules.too_many_args import check_too_many_args
from src.analysis.rules.security_rules import dangerous_functions
from src.analysis.rules.function_length import check_function_length
from src.analysis.rules.deep_nesting import deep_nesting
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Linter:
    def __init__(self, tree, code):
        self.tree = tree
        self.code = code
        self.rules = [
            unused_variables,
            unused_imports,
            check_too_many_args,
            dangerous_functions,
            check_function_length,
            deep_nesting
        ]
        logger.debug(f"Initialized linter with {len(self.rules)} rules")
    
    def run(self, tree, code):
        logger.info(f"Running {len(self.rules)} linting rules")
        issues = []
        for rule in self.rules:
            rule_issues = rule(tree, code)
            issues.extend(rule_issues)
            logger.debug(f"Rule {rule.__name__} found {len(rule_issues)} issues")
        
        logger.info(f"Linting complete: {len(issues)} total issues found")
        return issues