def deep_nesting(tree,code,max_length=3):
    issues=[]
    depth=0
    lines=code.splitlines()
    for i,line in enumerate(lines,start=1):
        if any(line.strip().startswith(kw)for kw in("if","for","while")):
            depth+=1
            if line.strip()=="":
                depth=0
            if depth>max_length:
                issues.append({
                    "line":i,
                    "type":"deep nesting",
                    "message":f"Nesting depth of {depth} exceeds maximum of {max_length}",
                    "severity":"warning"
                })
    return issues