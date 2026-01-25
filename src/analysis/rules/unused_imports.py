from src.analysis.utils.ast_utils import get_node_text

def unused_imports(tree, code):
    """
    Find unused imports using Tree-sitter AST.
    """
    if not tree:
        return []
        
    issues = []
    imported = {} # name -> line_no
    all_code_identifiers = set()
    
    cursor = tree.walk()
    visit_queue = [tree.root_node]
    
    # Pass 1: Collect imports
    while visit_queue:
        node = visit_queue.pop(0)
        
        # Python: import_statement / import_from_statement
        if node.type in ("import_statement", "import_from_statement"):
            # We iterate children to find aliases or names
            for child in node.children:
                if child.type == "dotted_name": # import x.y
                    name = get_node_text(child).split('.')[0] # We care about top level mainly
                    imported[name] = child.start_point[0] + 1
                elif child.type == "aliased_import": # import x as y
                    alias = child.child_by_field_name("alias")
                    if alias:
                        name = get_node_text(alias)
                        imported[name] = child.start_point[0] + 1
        
        # Python: specific handling for 'import_from_statement' names
        # e.g. from x import y
        # The 'y' is what is imported into namespace.
            if node.type == "import_from_statement":
                 # children: from, module_name, import, names...
                 # We look for 'aliased_import' or just names in the list.
                 # Tree sitter structure varies, but generally we can look for specific children
                 pass # simplified for now, as traversing children above covers many cases if we recurse
                 
        # JS: import_statement -> import_clause -> named_imports / namespace_import
        if node.type == "import_statement" and "import" in get_node_text(node): # JS/TS/Java
            # Note: This is a simplification. 
            pass

        visit_queue.extend(node.children)

    # Pass 2: Collect all identifiers in file to check usage
    # We re-walk or optimise. 
    # To avoid complexity, let's just grab all identifiers that are NOT in import lines
    import_lines = set(imported.values())
    
    visit_queue = [tree.root_node]
    while visit_queue:
        node = visit_queue.pop(0)
        if node.type == "identifier":
             line = node.start_point[0] + 1
             # If this identifier is NOT on an import declaration line, count it as usage
             # This is a heuristic. A better way is checking parent type.
             if line not in import_lines:
                 all_code_identifiers.add(get_node_text(node))
        visit_queue.extend(node.children)

    # Check
    for name, line in imported.items():
        if name not in all_code_identifiers:
             issues.append({
                "line": line,
                "type": "Unused Import",
                "message": f"Module '{name}' imported but not used",
                "severity": "warning"
            })
            
    return issues