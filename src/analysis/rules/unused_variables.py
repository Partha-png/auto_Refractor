

def unused_variables(tree, code):
    """
    Find unused variables using Tree-sitter AST.
    """
    if not tree:
        return []
        
    issues = []
    assignments = {} # name -> line_no
    usages = set()
    
    cursor = tree.walk()
    visit_queue = [tree.root_node]
    
    while visit_queue:
        node = visit_queue.pop(0)
        
        # Check for assignments
        # Python: assignment
        if node.type == "assignment":
            # LHS is the first child usually (or loop through children)
            # This is simplified. Real python grammar is complex (targets=...)
            left_node = node.child_by_field_name("left")
            if left_node and left_node.type == "identifier":
                name = left_node.text.decode('utf-8')
                assignments[name] = left_node.start_point[0] + 1
        
        # JS: variable_declarator (name = init)
        elif node.type == "variable_declarator":
            name_node = node.child_by_field_name("name")
            if name_node and name_node.type == "identifier":
                name = name_node.text.decode('utf-8')
                assignments[name] = name_node.start_point[0] + 1

        # Check for usages (Identifier generally)
        # But we must exclude the definition sites we just found.
        # Simplest way: Collection ALL identifiers, then filter out the ones
        # that are strictly in 'declared' position.
        
        if node.type == "identifier":
             # We need context. Is this a definition or usage?
             # Parent type tells us.
             parent = node.parent
             is_definition = False
             
             if parent:
                 if parent.type == "assignment" and parent.child_by_field_name("left") == node:
                     is_definition = True
                 elif parent.type == "variable_declarator" and parent.child_by_field_name("name") == node:
                     is_definition = True
                 elif parent.type == "function_definition" and parent.child_by_field_name("name") == node:
                     is_definition = True
                 elif parent.type == "class_definition" and parent.child_by_field_name("name") == node:
                     is_definition = True
                 # Add function params as 'assignments' (definitions)
                 elif parent.type == "parameters": # Python parameters
                     is_definition = True
                     name = node.text.decode('utf-8')
                     assignments[name] = node.start_point[0] + 1
                     
             if not is_definition:
                 usages.add(node.text.decode('utf-8'))
        
        visit_queue.extend(node.children)

    # Calculate unused
    for var, line_no in assignments.items():
        if var not in usages and var != "_" and not var.startswith("__"):
            issues.append({
                "line": line_no,
                "type": "Unused Variable",
                "message": f"Variable '{var}' assigned but not used",
                "severity": "warning"
            })
            
    return issues