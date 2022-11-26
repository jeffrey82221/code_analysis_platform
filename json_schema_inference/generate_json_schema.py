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

- [ ] Change redis-server cache to another one


TODO:
Use Python Cuckoo Filter to avoid repeat download of json

REF:
https://github.com/huydhn/cuckoo-filter
https://dl.acm.org/doi/pdf/10.1145/2674005.2674994

"""
import requests
from concurrent.futures import ThreadPoolExecutor
import tqdm

from common.schema_fitter import fit, try_unify_dict
from common.schema_objs import Union
from common.ray_pool_executor import RayActorPoolExecutor
import time


def get_rough_schema(union_count):
    """
    A pipeline for inferencing json schema from a
    list of urls

    Pipeline components:
    - [ ] pkg name generator
    - [ ] package name cuckoo filter (* saved)
    - [ ] url generator + pkg name passing
    - [ ] json generator + pkg name passing (* IO bound)
    - [ ] json batch aggregator + pkg batch passing
    - [ ] json schema generator + pkg batch passing (* CPU bound)
    - [ ] json schema reducer + cuckoo contain deletion
    """
    pkgs = []
    with open('../pypi_graph_analysis/package_names.txt', 'r') as f:
        pkgs = list(map(lambda p: p.strip(), f))
    print('total package count:', len(pkgs))

    with ThreadPoolExecutor(max_workers=union_count if union_count <= 20 else 20) as th_exc:
        jsons = th_exc.map(_get_json, pkgs[:union_count], chunksize=10)
        jsons = tqdm.tqdm(jsons, total=union_count)
        jsons = list(filter(lambda js: 'info' in js, jsons))
    time.sleep(1)
    with RayActorPoolExecutor(max_workers=union_count if union_count <= 4 else 4) as pr_exc:
        jsons_gen = tqdm.tqdm(jsons, total=len(jsons))
        json_batches = batchwise_generator(jsons_gen, batch_size=1000)
        schemas = pr_exc.map(_get_schema, json_batches)
        union_schema = Union.set(schemas)

    return union_schema


def _get_json(pkg):
    url = f'https://pypi.org/pypi/{pkg}/json'
    result = requests.get(url).json()
    return result


def batchwise_generator(gen, batch_size=100):
    batch = []
    for i, element in enumerate(gen):
        batch.append(element)
        if i % batch_size == (batch_size - 1):
            yield batch
            del batch
            batch = []
    yield batch


def _get_schema(json_batch):
    return Union.set(map(lambda js: fit(js, unify_callback=try_unify_dict), json_batch))
