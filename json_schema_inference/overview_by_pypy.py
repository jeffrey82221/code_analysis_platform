"""
PyPy speed up experiment on schema inferencing
Result: 2.3 X speed up. 

How to execute in pypy: 
`pypy3 overview_by_pypy.py`
"""
from common.schema import InferenceEngine
import json
import tqdm
jsonl_path = 'data/kaggle_data/test.jsonl'
total = sum(1 for _ in open(jsonl_path))
with open(jsonl_path) as f:
    json_pipe = map(json.loads, f)
    json_pipe = tqdm.tqdm(json_pipe, total=total)
    schema = InferenceEngine.get_schema(json_pipe)

print(schema)
