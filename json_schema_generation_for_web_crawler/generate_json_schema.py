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
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import tqdm
from common.schema_fitter import fit, try_unify_dict
from common.schema_objs import Union
def get_rough_schema(union_count):
    json_schemas = []
    pkgs = []
    with open('../pypi_graph_analysis/package_names.txt', 'r') as f:
        pkgs = list(map(lambda p: p.strip(), f))
    print('total package count:', len(pkgs))
    def get_json(pkg):
        url = f'https://pypi.org/pypi/{pkg}/json'
        json = requests.get(url).json()
        return json
    def get_schema(json):
        return fit(json, unify_callback=try_unify_dict)

    with ThreadPoolExecutor(max_workers=union_count if union_count <= 20 else 20) as th_exc:
        with ThreadPoolExecutor(max_workers=union_count if union_count <= 20 else 20) as pr_exc:
            jsons = th_exc.map(get_json, pkgs[:union_count], chunksize=10)
            jsons = tqdm.tqdm(jsons, total=union_count)
            jsons = filter(lambda json: 'info' in json, jsons)
            # make json batches
            # get_schema from batches
            # get_schema from result of batches
            schemas = pr_exc.map(get_schema, jsons, chunksize=10)
            union_schema = Union.set(schemas)

    return union_schema
