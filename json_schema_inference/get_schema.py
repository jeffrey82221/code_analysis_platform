"""
Compile this module: 

```
python -m nuitka --module --include-package=schema schema --python-flag=nosite,-O --prefer-source-code \
    --clang --plugin-enable=anti-bloat,implicit-imports,data-files,pylint-warnings
```
"""

from common.schema import InferenceEngine

def get_schema(json_batch):
    return InferenceEngine.get_schema(json_batch)