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

- [-] Change redis-server cache to another one


TODO:
- [X] Use Python Cuckoo Filter to avoid repeat download of json
- [ ] enable no dump mode

REF:
https://github.com/huydhn/cuckoo-filter
https://dl.acm.org/doi/pdf/10.1145/2674005.2674994

"""
import abc
import os
import pickle
import math
from cuckoo.filter import CuckooFilter
import logging
import signal
import sys
import typing
import requests
import tqdm
from multiprocessing.pool import ThreadPool
import json
from ..objs import Union, JsonSchema
from .base import InferenceEngine

__all__ = ['JsonlInferenceEngine']


class JsonlInferenceEngine:
    def __init__(self, inference_worker_cnt=8, json_per_worker=1000):
        self._inference_worker_cnt = inference_worker_cnt
        if self._inference_worker_cnt > 1:
            from ray.util.multiprocessing import Pool
            self.Pool = Pool
        else:
            self.Pool = ThreadPool
        self._json_per_worker = json_per_worker

    @property
    def jsonl_path(self):
        raise NotImplementedError

    def get_schema(self, verbose=True):
        if verbose:
            total = sum(1 for _ in open(self.jsonl_path, 'r'))
        with open(self.jsonl_path, 'r') as f:
            with self.Pool(processes=self._inference_worker_cnt) as pr_exc:
                json_pipe = map(json.loads, f)
                if verbose:
                    json_pipe = tqdm.tqdm(
                        json_pipe, total=total, desc=self.jsonl_path)
                json_batch_pipe = InferenceEngine._batchwise_generator(
                    json_pipe, batch_size=self._json_per_worker)
                # Inferencing Json schemas from Json Batches
                json_schema_pipe = pr_exc.imap_unordered(
                    JsonlInferenceEngine._pr_run, json_batch_pipe)
                if verbose:
                    json_schema_pipe = tqdm.tqdm(json_schema_pipe, total=int(total / self._json_per_worker),
                                                 desc='batch-wise schema')
                schema = Union.set(json_schema_pipe)
        return schema

    @staticmethod
    def _pr_run(
            json_batch: typing.List[typing.Dict]):
        json_schema = InferenceEngine.get_schema(json_batch)
        return json_schema
