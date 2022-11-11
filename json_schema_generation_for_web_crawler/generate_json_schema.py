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
- [X] Build another create_schema with keys of dictionary shown 
- [X] Generate consistet schema to allow multiple json's schema to be merged into a more consistent schema 
- [ ] Convert Schema to a Python DataClass
- [ ] An adaptor that takes json as input and initialize the python DataClass
"""
from schema_fitter import fit, try_unify_dict
from schema_objs import Union
if __name__ == '__main__':

    data1 = requests.get(f'https://pypi.org/pypi/pandas/json').json()
    data2 = requests.get(f'https://pypi.org/pypi/networkx/json').json()
    data3 = requests.get(f'https://pypi.org/pypi/tensorflow/json').json()
    schemas = [fit(d, unify_callback=try_unify_dict) for d in [data1, data2, data3]]
    union_schema = Union.set(schemas)
    pprint.pprint(union_schema)
    