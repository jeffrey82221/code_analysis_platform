import requests


"""
What is a structured JSON file? 

It is a dictionary with key and elements

Elements can be `List`, `Dictionary`, or `Simple Variables`, which is a value or string (Optional[int], Optional[float], ...).

If the element is a `List`, it must have elements of same `Simple Variables` or `Dictionary` with same keys. 

If the element is a `Dictionary`, it should have fixed keys and fixed type of element. 

If the element is a `Simple Variables`, it should have fixed type.

TODO: 
- [ ] Build another create_schema with keys of dictionary shown 
- [ ] Generate consistet schema Allow multiple json's schema to be merged into a more consistent schema 
- [ ] Convert Schema to a Python DataClass
- [ ] An adaptor that takes json as input and initialize the python DataClass
"""
import sys
from typing import List, Dict, Union, Any
sys.setrecursionlimit(10000)

def create_schema(json_obj):
    try:        
        if isinstance(json_obj, list):
            # generate schema of this dict
            args_hints = []
            for e in json_obj:
                args_hints.append(create_schema(e))
            args_hints = tuple(set(args_hints))
            if len(args_hints) == 0:
                union = Any
            elif len(args_hints) == 1:
                union = args_hints[0]
            else:
                union = Union[int, str]
                union.__args__ = args_hints
            result = List[union]
        elif isinstance(json_obj, dict):
            args_hints = []
            for k, e in json_obj.items():
                assert isinstance(k, str), f'key of dictionary must be string, but {k} is {type(k)}'
                args_hints.append(create_schema(e))
            args_hints = tuple(set(args_hints))
            if len(args_hints) == 0:
                union = Any
            elif len(args_hints) == 1:
                union = args_hints[0]
            else:
                union = Union[str, int]
                union.__args__ = args_hints
            result = Dict[str, union]
        else:
            result = type(json_obj)
            # generate schema of this dict 
    except RecursionError:
        print('RecursionError happended on json_obj', json_obj)
        result = type(json_obj)
    finally:
        return result

if __name__ == '__main__':
    print(create_schema(1))
    print(create_schema('apple'))
    print(create_schema([1, 3, 'str']))
    print(create_schema({'a': 1, 'b': 2}))
    print(create_schema({'a': 1, 'b': 'str'}))
    print(create_schema({'a': 1, 'b': 'str', 'c': [1, 2, 3]}))
    print(create_schema({'a': 1, 'b': 'str', 'c': [1, 2, 3, 'str']}))
    data = requests.get(f'https://pypi.org/pypi/pandas/json').json()
    for key in data:
        print(key, ':')
        print(create_schema(data[key]))
    # print(create_schema({'a': 1, 'b': [1, 4, 'str', {'c': 3}], 'c': 'str'}))
