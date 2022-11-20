"""
A Json schema builder from multiple strutured Json files

NOTE:

What is a structured JSON file?

It is a dictionary with key and elements

Elements can be `List`, `Dictionary`, or `Simple Variables`, which is a value or string (Optional[int], Optional[float], ...).

If the element is a `List`, it must have elements of same `Simple Variables` or `Dictionary` with same keys.

If the element is a `Dictionary`, it should have fixed keys and fixed type of element.

If the element is a `Simple Variables`, it should have fixed type.

TODO:
- [X] Build another create_schema with keys of dictionary shown
- [X] Generate consistet schema to allow multiple json's schema to be merged into a more consistent schema
- [X] Convert Schema to a Python DataClass
    - [X] A class extract json properties one-by-one
    - [X] A class generate overall json content
- [X] An adaptor that takes json as input and initialize the python DataClass
"""
import requests
from common.schema_fitter import fit, try_unify_dict
from common.schema_objs import Union
def get_rough_schema(union_count):
    json_schemas = []
    with open('../pypi_graph_analysis/package_names.txt', 'r') as f:
        for i, pkg in enumerate(f):
            pkg = pkg.strip()
            if i > union_count:
                break
            url = f'https://pypi.org/pypi/{pkg}/json'
            print(url)
            json = requests.get(url).json()
            if 'info' in json:
                json_schemas.append(fit(json, unify_callback=try_unify_dict))
    union_schema = Union.set(json_schemas)
    return union_schema
