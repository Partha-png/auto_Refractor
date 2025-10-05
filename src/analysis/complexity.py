class Complexity:
    def __init__(self,code,tree):
        self.code=code
        self.tree=tree
        self.lines=code.splitlines()
    def run(self):
        return{
            "cyclomatic":self.cyclomatic(),
            "loc":self.line_of_code(),
            "nesting":self.is_nesting()
        }
    def cyclomatic(self):
        count=1
        keywords=["if","elif","for","while","case"]
        for line in self.lines:
            for kw in keywords:
                if kw in line:
                    count+=1
        return count
    def line_of_code(self):
        count=0
        for line in self.lines:
            if line.strip():
                count+=1
        return count
    def is_nesting(self):
        max_depth=0
        for line in self.lines:
            striped=line.lstrip()
            indent=len(line)-len(striped)
            level=indent//4
            max_depth=max(level,max_depth)
        return max_depth