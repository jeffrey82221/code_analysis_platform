"""
PyPy speed up experiment on schema inferencing
Result: 2.3 X speed up. 

1) How to execute in pypy: 
`pypy3 overview_by_pypy.py`

2) How to compile into binary using Nuitka and execute the binary?

`python -m nuitka overview_by_pypy.py --standalone --lto=no --nofollow-import-to=pytest --python-flag=nosite,-O --prefer-source-code --clang --plugin-enable=anti-bloat,implicit-imports,data-files,pylint-warnings`
`./overview_by_pypy.dist/overview_by_pypy`

NOTE: 
- Speed up against python: 0.735 -> 0.546
- Speed up against pypy: 0.751 -> 0.546
"""
from common.schema import InferenceEngine
import json

def progress(input_pipe, total=None):
    tick = total / 100
    for i, item in enumerate(input_pipe):
        if i % tick == 0:
            print(f'{int(i/total*100)}%')
        yield item

if __name__ == '__main__':
    jsonl_path = 'data/small_test.jsonl'
    total = sum(1 for _ in open(jsonl_path))
    with open(jsonl_path) as f:
        json_pipe = map(json.loads, f)
        json_pipe = progress(json_pipe, total=total)
        schema = InferenceEngine.get_schema(json_pipe)

    print(schema)
