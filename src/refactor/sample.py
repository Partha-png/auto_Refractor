"""
Small but extremely complex code for testing refactoring engine.
This file intentionally has many code quality issues.
"""

def process_data(a, b, c, d, e, f, g):  # Too many arguments
    """Process data with terrible complexity."""
    import os  # Unused import
    import sys  # Unused import
    x = 1  # Unused variable
    y = 2  # Unused variable
    result = 0
    
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:  # Deep nesting level 4
                    if e > 0:  # Deep nesting level 5
                        for i in range(10):
                            for j in range(10):
                                for k in range(10):  # Deep nesting level 8
                                    if i == j == k:
                                        result += 1
                                    elif i > j:
                                        if j > k:  # Even deeper
                                            result += 2
                                        else:
                                            result -= 1
                                    else:
                                        result += 3
                    else:
                        result = -1
                else:
                    result = -2
            else:
                result = -3
        else:
            result = -4
    else:
        result = -5
    
    # Eval is dangerous
    data = eval("1 + 1")  # Security issue
    
    return result + f + g