def unused_variables(tree,code):
    issues=[]
    assigned=set()
    used=set()
    lines=code.splitlines()
    for i,line in enumerate(lines,start=1):
        if "=" in line and not line.strip().startswith("#"):
            var=line.split("=")[0].strip()
            assigned.add((var,i))
    for var,_ in assigned:
            for line in lines:
                if var in line:
                    used.add(var)
    for var,line_no in assigned:
        if var not in used:
            issues.append({
                "line": line_no,
                "type": "Unused Variable",
                "message": f"Variable '{var}' assigned but not used",
                "severity": "warning"
            })
    return issues