def check_function_length(tree, code, max_length=50):
    """
    Check for functions exceeding max length using AST.
    """
    if not tree:
        return []
        
    issues = []
    
    cursor = tree.walk()
    visit_queue = [tree.root_node]
    
    while visit_queue:
        node = visit_queue.pop(0)
        
        # Check if node is a function definition
        if node.type in ("function_definition", "function_declaration", "method_declaration", "method_definition"):
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            length = end_line - start_line
            
            if length > max_length:
                 issues.append({
                    "line": start_line + 1,
                    "type": "Function Length",
                    "message": f"Function exceeds maximum length of {max_length} lines ({length} lines)",
                    "severity": "warning"
                })
        
        visit_queue.extend(node.children)
        
    return issues