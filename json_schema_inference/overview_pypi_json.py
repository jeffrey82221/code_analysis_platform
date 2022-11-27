"""
TODO:

    - [ ] Refactor:
        - [ ] seperate version / constraint related class & package & release related classes
    - [X] Release Version
        - [X] Version class with version id as input
        - [X] develop sorting algorithm for version ids
        - [X] parsing of required_dist str
        - [X] Version constraint class that takes dependent string as input
        - [X] Version constraint class that can determine whether a Version obj fit or not
        - [X] Ignoring RC versions
    - [ ] Platform
        - [ ] Develop platform tags data cleaning strategy at PypiVersionPackageVeiw
            - [X] seperate by ; and ,
            - [X] lower cases
            - [X] strip space
            - [ ] allow decomposition into different os
        - [ ] Building Platform node object
    - [X] Develop python-version property (returning Python-version objs)
        - [X] Search for all python versions
        - [X] Version constraint class that takes dependent string as input
        - [X] Version constraint class that can determine whether a Version obj fit or not
        - [X] Embedding into the Big class
    - [ ] Build Dependency-Hyperedge Obj
        - [ ] Scan for all extra conditions
        - [ ] Add python package nodes
        - [ ] Add dependency condition
"""
import typing
from pypi_objs.release import Releases
from common.api_schema_inference import InferenceEngine
import pprint

class PypiPackageSchemaInferencer(InferenceEngine):
    def __init__(self, api_thread_cnt=30, inference_worker_cnt=4, json_per_worker=10, cuckoo_dump='pypi_cuckoo.pickle', schema_dump='pypi_schema.pickle'):
        super().__init__(
            api_thread_cnt=api_thread_cnt,
            inference_worker_cnt=inference_worker_cnt,
            json_per_worker=json_per_worker,
            cuckoo_dump=cuckoo_dump,
            schema_dump=schema_dump
        )
    def index_generator(self) -> typing.Iterable[str]:
        with open('../pypi_graph_analysis/package_names.txt', 'r') as f:
            for pkg in map(lambda p: p.strip(), f):
                yield pkg
    
    def get_url(self, pkg: str) -> str:
        url = f'https://pypi.org/pypi/{pkg}/json'
        return url

    def is_valid_json(self, json_dict: typing.Dict) -> bool:
        return 'info' in json_dict

if __name__ == '__main__':
    inference_engine = PypiPackageSchemaInferencer()
    schema = inference_engine.get_schema()
    pprint.pprint(schema)
    releases = Releases('pandas', schema=schema).releases
    pprint.pprint(releases[-1].requires_dist)
