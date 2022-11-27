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
from pypi_objs.release import Releases
from generate_json_schema import InferenceEngine
import pprint


if __name__ == '__main__':
    inference_engine = InferenceEngine()
    schema = inference_engine.get_schema()
    pprint.pprint(schema)
    releases = Releases('pandas', schema=schema).releases
    pprint.pprint(releases[-1].requires_dist)
