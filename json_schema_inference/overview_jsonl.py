"""
Get schema of jsonl 
& develop analysis platform on it. 
"""
import pprint
from common.schema_inference import JsonlInferenceEngine

class Engine(JsonlInferenceEngine):
    @property
    def jsonl_path(self):
        return 'data/small_test.jsonl'

schema = Engine().get_schema()
pprint.pprint(schema)