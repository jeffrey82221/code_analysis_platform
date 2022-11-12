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
    - [ ] A class extract json properties one-by-one
    - [ ] A class generate overall json content 
- [ ] An adaptor that takes json as input and initialize the python DataClass
"""
from schema_fitter import fit, try_unify_dict
from schema_objs import Union
if __name__ == '__main__':
    json_schemas = []
    with open('../pypi_graph_analysis/package_names.txt', 'r') as f:
        for i, pkg in enumerate(f):
            pkg = pkg.strip()
            if i > 1000:
                break
            url = f'https://pypi.org/pypi/{pkg}/json'
            print(url)
            json = requests.get(url).json()
            if 'info' in json:
                # pprint.pprint(json)
                json_schemas.append(fit(json, unify_callback=try_unify_dict))
    union_schema = Union.set(json_schemas)
    pprint.pprint(union_schema)
    