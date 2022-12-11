"""
PyPy speed up experiment on schema inferencing
Result: 2.3 X speed up. 

1) How to execute in pypy: 
`pypy3 overview_speedup.py`

2) How to compile into binary using Nuitka and execute the binary?

Build:
```
python -m nuitka overview_speedup.py --lto=no \
    --nofollow-import-to=pytest --python-flag=nosite,-O --prefer-source-code \
    --clang --plugin-enable=anti-bloat,implicit-imports,data-files,pylint-warnings
```
Remove Build:
```
rm -r overview_speedup.build
```
Run:

`./overview_speedup.dist/overview_speedup -j data/small_test.jsonl -v 0`

NOTE: 
- Speed up against python: 0.735 -> 0.546
- Speed up against pypy: 0.751 -> 0.546

3) How to compile `common.schema` into .so file

```
python -m nuitka common/schema --lto=no \
    --nofollow-import-to=pytest --python-flag=nosite,-O --prefer-source-code \
    --clang --plugin-enable=anti-bloat,implicit-imports,data-files,pylint-warnings
```
TODO: 
- [ ] Build a nuitka-base multiprocessing package. 
    - [ ] Bridging C and python
    - [ ] Easy deploy parallelizing function to nuitka C binary. 
    - [ ] A map and unordered map interface for python development
"""
from get_schema import get_schema
import json
import getopt
import sys

def progress(input_pipe, total=None):
    tick = total / 100
    for i, item in enumerate(input_pipe):
        if i % tick == 0:
            print(f'{int(i/total*100)}%')
        yield item

def parse_input(argv):
    arg_help = "{0} -j <jsonl_path> -v <verbose>".format(argv[0])
    
    try:
        opts, args = getopt.getopt(argv[1:], "hj:v:", ["help", "jsonl_path=", 
        "verbose="])
    except:
        print(arg_help)
        sys.exit(2)

    result = {}
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-j", "--jsonl_path"):
            result['jsonl_path'] = arg
        elif opt in ("-v", "--verbose"):
            result['verbose'] = bool(int(arg))
    return result

def main(inputs):
    jsonl_path = inputs['jsonl_path']
    verbose = inputs['verbose']
    total = sum(1 for _ in open(jsonl_path))
    with open(jsonl_path) as f:
        json_pipe = map(json.loads, f)
        if verbose:
            json_pipe = progress(json_pipe, total=total)
        schema = get_schema(json_pipe)
    print(schema)

if __name__ == '__main__':
    inputs = parse_input(sys.argv)
    main(inputs)