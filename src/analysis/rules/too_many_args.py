def check_too_many_args(tree, code, max_args=3):
    """
    Check for functions with too many arguments using AST.
    """
    if not tree:
        return []
        
    issues = []
    
    # Define node types that contain parameters for different languages
    # Python: parameters
    # JS: formal_parameters
    # Java: formal_parameters
    # C++: parameter_list
    param_list_types = {"parameters", "formal_parameters", "parameter_list"}
    
    cursor = tree.walk()
    visit_queue = [tree.root_node]
    
    while visit_queue:
        node = visit_queue.pop(0)
        
        # Check if node is a function definition
        if node.type in ("function_definition", "function_declaration", "method_declaration", "method_definition"):
             # Find parameter list child
             for child in node.children:
                 if child.type in param_list_types:
                     # Count identifier children or parameter declarations
                     # Simplest: count named children (excluding punctuation)
                     arg_count = child.named_child_count
                     
                     # Python 'parameters' includes defaults, etc. Named children is accurate.
                     # (e.g. "a, b=1" -> 2 named children)
                     
                     if arg_count > max_args:
                         issues.append({
                            "line": node.start_point[0] + 1,
                            "type": "Too Many Args",
                            "message": f"Function has {arg_count} arguments, which exceeds the maximum of {max_args}",
                            "severity": "warning"
                        })
                     break
        
        visit_queue.extend(node.children)
        
    return issues