"""
Compile this module: 

```
python -m nuitka --module --include-package=common get_schema.py
```
"""

from common.schema import InferenceEngine

def get_schema(json_batch):
    return InferenceEngine.get_schema(json_batch)