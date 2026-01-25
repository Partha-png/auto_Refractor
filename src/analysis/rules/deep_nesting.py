def deep_nesting(tree, code, max_depth=3):
    """
    Check for deep nesting using AST.
    """
    if not tree:
        return []
        
    issues = []
    
    # Types that increase nesting level
    nesting_types = {
        "if_statement", "for_statement", "while_statement", "switch_statement", 
        "do_statement", "try_statement", "catch_clause", "function_definition",
        "class_definition"
    }
    
    # Recursive walker to track depth
    def walk(node, current_depth):
        if node.type in nesting_types:
            current_depth += 1
            if current_depth > max_depth:
                 issues.append({
                    "line": node.start_point[0] + 1,
                    "type": "deep nesting",
                    "message": f"Nesting depth of {current_depth} exceeds maximum of {max_depth}",
                    "severity": "warning"
                })
        
        for child in node.children:
            walk(child, current_depth)
            
    walk(tree.root_node, 0)
    return issues