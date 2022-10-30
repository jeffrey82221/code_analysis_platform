"""
Example of using pdb to debug a python code

commands in pdb:
1) next line: `n`
2) move into a function: `s`
3) show current line in file: `ll`
4) print current value of a varaible: `p <var1> <var2>`
5) finish debug and let the program continue: `continue`
"""
import pdb
import os


def get_path(filename):
    """Return file's path or empty string if no path."""
    head, _ = os.path.split(filename)
    return head


pdb.set_trace()
filename = __file__
filename_path = get_path(filename)
print(f'path = {filename_path}')
