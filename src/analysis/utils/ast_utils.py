"""
AST utilities for linter rules.
"""
from typing import Set, Dict, List, Tuple

def get_node_text(node) -> str:
    """Get text content of a node."""
    if not node:
        return ""
    return node.text.decode('utf-8')