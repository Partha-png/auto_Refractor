def check_function_length(tree,code,max_length=50):
    issues=[]
    lines=code.split()
    for i,line in enumerate(lines,start=1):
        if line.strip().startswith("def"):
            start=i
            for j in range(i+1,len(lines)):
                if lines[j].strip().startswith("def") or lines[j].strip()=="":
                    break
                length=j-start
                if length>max_length:
                    if length>max_length:
                        issues.append({
                            "line": start,
                            "type": "Function Length",
                            "message": f"Function exceeds maximum length of {max_length} lines",
                            "severity": "warning"
                        })
    return issues