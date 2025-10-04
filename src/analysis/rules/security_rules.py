def dangerous_functions(tree,code):
    issues=[]
    lines=code.splitlines()
    for i,line in enumerate(lines,start=1):
        if "eval(" in line or "exec(" in line:
            issues.append({
                "lines":i,
                "type":"dangerous function",
                "message":"Use of dangerous function 'eval' or 'exec'",
                "severity":"warning"
            })
    return issues