"""
AST-based complexity calculation using Tree-sitter.
Supports multiple languages by mapping AST node types to complexity increments.
"""
from typing import Dict, Set
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Map of node types that increase complexity for each language
# We use a broad set of control flow nodes
COMPLEXITY_NODES: Dict[str, Set[str]] = {
    "python": {
        "if_statement", "for_statement", "while_statement", "elif_clause",
        "except_clause", "with_statement", "assert_statement", "match_statement",
        "case_clause", "boolean_operator"  # boolean_operator handles 'and'/'or'
    },
    "javascript": {
        "if_statement", "for_statement", "while_statement", "do_statement",
        "switch_statement", "catch_clause", "ternary_expression", 
        "binary_expression", # Need to check for && and || specifically
        "for_in_statement"
    },
    "java": {
        "if_statement", "for_statement", "while_statement", "do_statement",
        "switch_expression", "catch_clause", "ternary_expression",
        "binary_expression"
    },
    "cpp": {
        "if_statement", "for_statement", "while_statement", "do_statement",
        "switch_statement", "catch_clause", "conditional_expression",
        "binary_expression"
    },
    # Fallback/Generic
    "common": {
        "if_statement", "for_statement", "while_statement", "switch_statement",
        "catch_clause"
    }
}

def calculate_complexity(tree, language: str) -> int:
    """
    Calculate cyclomatic complexity by traversing the AST.
    Start with 1 and add 1 for each control flow node.
    """
    if not tree:
        return 1
        
    complexity = 1
    cursor = tree.walk()
    
    # Get node types for this language
    # Map 'c++' to 'cpp' etc if needed
    lang_key = language.lower().replace("c++", "cpp").replace("js", "javascript")
    target_nodes = COMPLEXITY_NODES.get(lang_key, COMPLEXITY_NODES["common"])
    
    visit_queue = [tree.root_node]
    
    while visit_queue:
        node = visit_queue.pop(0)
        
        # Check if this node increases complexity
        if node.type in target_nodes:
            # For binary expressions, we only care about boolean logic (&&, ||)
            # Tree-sitter usually groups them as 'binary_expression' with an operator child
            if node.type == "binary_expression":
                operator = node.child_by_field_name("operator")
                if operator:
                    op_text = operator.text.decode('utf-8')
                    if op_text in ["&&", "||", "and", "or"]:
                        complexity += 1
            else:
                complexity += 1
                
        # For Python elif, it might be nested or a specialized clause depending on grammar version
        # The set includes 'elif_clause' which handles it for modern python grammar
        
        # Add children to queue
        visit_queue.extend(node.children)
        
    return complexity
