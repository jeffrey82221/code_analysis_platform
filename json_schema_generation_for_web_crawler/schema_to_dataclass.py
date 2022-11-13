
"""
Manually Build a Class for a Schema

- [ ] 
"""

import inspect
import ast

def convert(json_schema) -> str:
    """
    Args: 
        json_schema 
    Return: 
        python code string 
    """
    pass
expr = """
class TMP:
    pass
"""



if __name__ == '__main__':
    p = ast.parse(expr)
    ast.walk(p)