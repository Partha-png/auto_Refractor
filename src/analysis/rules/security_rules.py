def dangerous_functions(tree, code):
    issues = []
    visit_queue = [tree.root_node]
    
    while visit_queue:
        node = visit_queue.pop(0)
        
        # Check for call nodes named eval/exec
        if node.type == "call":
            func_node = node.child_by_field_name("function")
            if func_node and func_node.type == "identifier":
                func_name = func_node.text.decode('utf-8')
                if func_name in ("eval", "exec"):
                    issues.append({
                        "line": node.start_point[0] + 1,
                        "type": "dangerous function",
                        "message": f"Use of dangerous function '{func_name}'",
                        "severity": "error"
                    })
        
        visit_queue.extend(node.children)
    
    return issues