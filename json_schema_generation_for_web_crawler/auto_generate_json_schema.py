import requests
import pprint

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
sys.setrecursionlimit(100)

class Dict:
    def __init__(self, key, element):
        self._key = key
        self._element = element
    def __repr__(self):
        return f'Dict[{self._key},{self._element}]'
    def __eq__(self, obj):
        return self._element == obj._element
    def __add__(self, obj):
        if self == obj:
            return self
        else:
            if self._element == 'NoneType':
                return obj
            if obj._element == 'NoneType':
                return self
            return Union((self, obj))

class List:
    def __init__(self, item):
        self._item = item
    def __repr__(self):
        return f'List[{self._item}]'
    def __eq__(self, obj):
        return self._item == obj._item

class Union:
    def __init__(self, item_set):
        self._item_set = item_set
    def __repr__(self):
        content = ','.join(map(str, list(self._item_set)))
        return f'Union[{content}]'
    def __eq__(self, obj):
        return sorted(self._item_set) == sorted(obj._item_set)

class ExplicitDict(dict):
    def __repr__(self):
        return f'ExplicitDict[{self}]'
    def __eq__(self, obj):
        result = True
        for key in self:
            if key not in obj:
                return False
            if obj[key] is None or self[key] is None:
                pass
            else:
                if obj[key] != self[key]:
                    return False
        return result




def create_schema(json_obj):
    try:        
        if isinstance(json_obj, list):
            # generate schema of this dict
            args_hints = []
            for e in json_obj:
                args_hints.append(create_schema(e))
            args_hints = tuple(args_hints)
            if len(args_hints) == 0:
                union = 'Unknown'
            elif len(args_hints) == 1:
                union = args_hints[0]
            else:
                union = Union(args_hints)
            result = List(union)
        elif isinstance(json_obj, dict):
            args_hints = []
            for k, e in json_obj.items():
                assert isinstance(k, str), f'key of dictionary must be string, but {k} is {type(k)}'
                args_hints.append((k, create_schema(e)))
            result = ExplicitDict(args_hints)
            value_types = list(result.values())
            if all_is_complex(value_types) and has_same_element(value_types):
                result = Dict('str', value_types[0])
        else:
            result = type(json_obj).__name__
            # generate schema of this dict 
    except RecursionError:
        print('RecursionError happended on json_obj', json_obj)
        result = type(json_obj)
    finally:
        return result

def has_same_element(a_list):
    # TODO:
    # only check keys if the elements are Dict 
    # recursively check until DictKeys or Non-List elements if the elements are complex 
    return all(map(lambda a: a == a_list[0], a_list))

def all_is_complex(a_list):
    return all([isinstance(a, List) or isinstance(a, HashableDict) for a in a_list])

if __name__ == '__main__':
    data = requests.get(f'https://pypi.org/pypi/pandas/json').json()
    pprint.pprint(create_schema(data))
    print('=============================================')
    pprint.pprint(create_schema(data['releases']['0.1']))
    print('=============================================')
    pprint.pprint(create_schema(data['releases']['1.4.4']))

