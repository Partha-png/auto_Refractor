def check_too_many_args(tree,code,max_args=3):
    issues=[]
    lines=code.splitlines()
    for i,line in enumerate(lines,start=1):
        if line.strip().startswith("def"):
            arg_count=line.count(",")+1 if"(" in line else 0
            if arg_count>max_args:
                issues.append({
                    "line":i,
                    "type":"too many args",
                    "message":f"Function has {arg_count} arguments, which exceeds the maximum of {max_args}",
                    "severity":"warning"
                })
    return issues