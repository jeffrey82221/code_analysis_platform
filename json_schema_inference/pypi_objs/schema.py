import typing
from common.api_schema_inference import InferenceEngine


class PypiPackageSchemaInferencer(InferenceEngine):
    def __init__(self, api_thread_cnt=30, inference_worker_cnt=4, json_per_worker=10,
                 cuckoo_dump='pypi_cuckoo.pickle', schema_dump='pypi_schema.pickle'):
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
