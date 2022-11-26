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

- [ ] Change redis-server cache to another one


TODO:
Use Python Cuckoo Filter to avoid repeat download of json

REF:
https://github.com/huydhn/cuckoo-filter
https://dl.acm.org/doi/pdf/10.1145/2674005.2674994

"""
import typing
import requests
from concurrent.futures import ThreadPoolExecutor
import tqdm

from common.schema_fitter import fit, try_unify_dict
from common.schema_objs import Union, JsonSchema
from common.ray_pool_executor import RayActorPoolExecutor
import time
import os
import pickle
import math
from cuckoo.filter import CuckooFilter
import logging
import signal
import sys


def build_pkg_name_generator():
    with open('../pypi_graph_analysis/package_names.txt', 'r') as f:
        for pkg in map(lambda p: p.strip(), f):
            yield pkg


def get_url(pkg):
    url = f'https://pypi.org/pypi/{pkg}/json'
    return url


def get_json(url):
    result = requests.get(url).json()
    return result


def batchwise_generator(gen, batch_size=100):
    batch = []
    for i, element in enumerate(gen):
        batch.append(element)
        if i % batch_size == (batch_size - 1):
            yield batch
            del batch
            batch = []
    if batch:
        yield batch


def get_schema(json_batch):
    return Union.set(
        map(lambda js: fit(js, unify_callback=try_unify_dict), json_batch))


class PackageCuckooFilter:
    """
    filter out packages whose json schema
    has already been inference and captured into the
    final union json schema
    """

    def __init__(self, pkg_gen_builder=typing.Callable[[
    ], typing.Iterable], dump_file_path='pkg_cuckoo.pickle', error_rate: float = 0.01):
        self._dump_file_path = dump_file_path
        if os.path.exists(self._dump_file_path):
            self._cuckoo = self.load()
        else:
            # build the cuckoo filter from scratch
            pkgs = list(pkg_gen_builder())
            assert error_rate <= 1. and error_rate > 0.
            bucket_size = round(- math.log10(error_rate)) + 1
            # fingerprint_size = int(math.ceil(math.log(1.0 / error_rate, 2) + math.log(2 * bucket_size, 2)))
            if bucket_size == 1:
                alpha = 0.5
            elif bucket_size >= 2 and bucket_size < 4:
                alpha = 0.84
            elif bucket_size >= 4 and bucket_size < 8:
                alpha = 0.95
            elif bucket_size >= 8:
                alpha = 0.98
            capacity = round(len(pkgs) / alpha)
            logging.info('capacity of cuckoo filter:', capacity)
            logging.info(
                'false positive error rate of cuckoo filter:',
                error_rate)
            logging.info('bucket size of cuckoo filter:', bucket_size)
            self._cuckoo = CuckooFilter(
                capacity=capacity,
                error_rate=error_rate,
                bucket_size=bucket_size)
            for pkg in pkgs:
                self._cuckoo.insert(pkg)

    def remove_pkg(self, pkg: str):
        self._cuckoo.delete(pkg)

    def filter(self, pkg_gen: typing.Iterable):
        for pkg in pkg_gen:
            if self._cuckoo.contains(pkg):
                yield pkg

    def load(self):
        with open(self._dump_file_path, 'rb') as handle:
            result = pickle.load(handle)
        logging.info(self._dump_file_path, 'Loaded')
        return result

    def exit_gracefully(self, *args):
        self.save()
        print('[PackageCuckooFilter] exit gracefully')

    def save(self):
        with open(self._dump_file_path, 'wb') as handle:
            pickle.dump(self._cuckoo, handle, protocol=pickle.HIGHEST_PROTOCOL)
        logging.info(self._dump_file_path, 'Saved')


class SchemaReducer:
    def __init__(self, pkg_cuckoo_filter: PackageCuckooFilter,
                 dump_file_path='schema.pickle'):
        self._pkg_cuckoo_filter = pkg_cuckoo_filter
        self._dump_file_path = dump_file_path
        if os.path.exists(self._dump_file_path):
            self._current_schema = self.load()
        else:
            self._current_schema = None

    def reduce(
            self, schema_pkgs_gen: typing.Iterable[typing.Tuple[JsonSchema, typing.List[str]]]):
        for schema, pkgs in schema_pkgs_gen:
            for pkg in pkgs:
                self._pkg_cuckoo_filter.remove_pkg(pkg)
            if self._current_schema is not None:
                self._current_schema |= schema
            else:
                self._current_schema = schema

    def load(self):
        with open(self._dump_file_path, 'rb') as handle:
            result = pickle.load(handle)
        logging.info(self._dump_file_path, 'Loaded')
        return result

    def save(self):
        with open(self._dump_file_path, 'wb') as handle:
            pickle.dump(
                self._current_schema,
                handle,
                protocol=pickle.HIGHEST_PROTOCOL)
        logging.info(self._dump_file_path, 'Saved')

    def exit_gracefully(self, *args):
        self.save()
        print('[SchemaReducer] exit gracefully')

    @property
    def union_schema(self):
        return self._current_schema


def register_graceful_exist(objs):
    def do_exit(*args):
        for p in objs:
            p.exit_gracefully(*args)
        sys.exit(1)
    signal.signal(signal.SIGINT, do_exit)
    signal.signal(signal.SIGTERM, do_exit)


def get_rough_schema(union_count):
    """
    A pipeline for inferencing json schema from a
    list of urls

    Pipeline components:
    - [X] pkg name generator
    - [X] package name cuckoo filter (* load from pickle or create from all pkg names)
    - [X] url generator + pkg name passing
    - [X] json generator + pkg name passing (* IO bound)
    - [X] error json filtering
    - [X] json batch aggregator + pkg batch passing
    - [X] json schema generator + pkg batch passing (* CPU bound)
    - [X] json schema reducer + cuckoo contain deletion (* saved and load via pickle)
    """
    api_thread_cnt = 20
    union_worker_cnt = 1
    batch_size = 10
    pkg_filter = PackageCuckooFilter(build_pkg_name_generator)
    schema_holder = SchemaReducer(pkg_filter)
    pkgs = list(build_pkg_name_generator())
    pkg_name_pipe = pkgs[:3000]
    with ThreadPoolExecutor(max_workers=api_thread_cnt) as th_exc:
        with RayActorPoolExecutor(max_workers=union_worker_cnt) as pr_exc:
            register_graceful_exist([pkg_filter, schema_holder, pr_exc])
            pkg_name_pipe = pkg_filter.filter(pkg_name_pipe)
            url_pkg_name_pipe = map(
                lambda pkg: (
                    get_url(pkg),
                    pkg),
                pkg_name_pipe)

            def th_run(instance):
                url, pkg = instance
                json_result = get_json(url)
                return json_result, pkg
            json_pkg_name_pipe = th_exc.map(th_run, url_pkg_name_pipe)
            json_pkg_name_pipe = filter(
                lambda x: 'info' in x[0], json_pkg_name_pipe)

            json_pkg_name_batch_pipe = batchwise_generator(
                json_pkg_name_pipe, batch_size=batch_size)

            def pr_run(json_pkg_name_batch):
                pkg_name_batch = list(map(lambda x: x[1], json_pkg_name_batch))
                json_schema = get_schema(
                    map(lambda x: x[0], json_pkg_name_batch))
                return json_schema, pkg_name_batch

            json_schema_pkgs_pipe = pr_exc.map(
                pr_run, json_pkg_name_batch_pipe)
            json_schema_pkgs_pipe = tqdm.tqdm(
                json_schema_pkgs_pipe, total=round(
                    len(pkgs) / batch_size))
            schema_holder.reduce(json_schema_pkgs_pipe)

    schema_holder.save()
    pkg_filter.save()
    return schema_holder.union_schema
