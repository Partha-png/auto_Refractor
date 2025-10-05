def unused_imports(tree,code):
    issues=[]
    lines=code.splitlines()
    imported=set()
    used=set()
    for i,line in enumerate(lines,start=1):
        if line.strip().startswith("import"):
            parts=line.split()
            if len(parts)>1:
                name=parts[1]
                imported.add((name,i))
        elif line.strip().startswith("from"):
            parts=line.split()
            if(len(parts)>1):
                name=parts[3]
                imported.add((name,i))
    for i,line in enumerate(lines,start=1):
        for(name,_) in imported:
            if name in line and not (line.strip().startswith("import") or line.strip().startswith("from")):
                used.add(name)
    for name,line_no in imported:
        if name not in used:
            issues.append({
                "line":line_no,
                "type":"unused import",
                "message":f"Module '{name}' imported but not used"
            })
    return issues