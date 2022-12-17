"""
Optional[str] / str: get set
Dict[]: create folder and iterate into
int: get max / min / mean
DynamicDict: get key set
List[str]: expand List and get set of str
UniformDict: expand to leaf

"""
import abc
import requests

import typing
import json
import copy
import tqdm
import concurrent
from functools import reduce
from redis_dec import Cache
from redis import StrictRedis
from jsonschema_inference.schema.fitter import fit
from jsonschema_inference.schema.objs import Dict, List, UniformDict, Union, Simple, Optional, Unknown, JsonSchema

__all__ = ['SingleView', 'OverView']

redis = StrictRedis(port=9001, decode_responses=True)
cache = Cache(redis)


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class SingleView:
    """
    This is a view data class of API Json.

    (need to provide a url by overide the `url` abstractproperty)
    """

    def __init__(self, schema: JsonSchema = None):
        self._methods: typing.Dict[str, typing.Callable] = dict()
        self._schema = schema

    @abc.abstractproperty
    def url(self) -> str:
        raise NotImplementedError

    @property
    def schema(self):
        if self._schema is None:
            self._schema = fit(
                self.json, unify_callback=schema_fitter.try_unify_dict)
        return self._schema

    @property
    def methods(self):
        if len(self._methods) == 0:
            self._setup_getters()
        return self._methods

    def _setup_getters(self):
        self._setup_getters_from_schema(self.schema)

    def _setup_getters_from_schema(self, schema, tokens=[]):
        if isinstance(schema, Dict):
            # Setup New Method
            self._methods[tuple(tokens)] = lambda: self._extract_items(
                tokens, self.json)
            for key, value in schema._content.items():
                self._setup_getters_from_schema(value, tokens=tokens + [key])
        elif isinstance(schema, List):
            # Setup New Method
            self._methods[tuple(tokens)] = lambda: self._extract_items(
                tokens, self.json)
            self._setup_getters_from_schema(
                schema._content, tokens=tokens + ['_list_'])
        elif isinstance(schema, UniformDict):
            # Setup New Method
            self._methods[tuple(tokens)] = lambda: self._extract_items(
                tokens, self.json)
            self._setup_getters_from_schema(
                schema._content, tokens=tokens + ['_uniform_dict_'])
        elif isinstance(schema, Optional):
            self._setup_getters_from_schema(schema._the_content, tokens=tokens)
        elif isinstance(schema, Simple):
            # Setup New Method
            self._methods[tuple(tokens)] = lambda: self._extract_items(
                tokens, self.json)
        elif isinstance(schema, Union):
            raise ValueError('There is Union in schema. Watch out!')
        elif isinstance(schema, Unknown):
            pass
        else:
            raise ValueError(
                'Undefined Schema Obj, schema:',
                schema,
                'tokens:',
                tokens)

    def _extract_items(self, _tokens, _json, _last_tokens=[]):
        tokens = copy.copy(_tokens)
        json = copy.deepcopy(_json)
        last_tokens = copy.copy(_last_tokens)
        if tokens:
            current_token = tokens.pop(0)
            if current_token == '_list_':
                return self._extract_items(
                    tokens, json, _last_tokens=last_tokens + [current_token])
            elif current_token == '_uniform_dict_':
                return self._extract_items(
                    tokens, json, _last_tokens=last_tokens + [current_token])
            else:
                if last_tokens:
                    def apply_recursion(json, _tokens):
                        tokens = copy.copy(_tokens)
                        token = tokens.pop(0)
                        if token == '_uniform_dict_':
                            return hashabledict(
                                [(k, apply_recursion(e, tokens)) for k, e in json.items()])
                        elif token == '_list_':
                            return set([apply_recursion(e, tokens)
                                        for e in json])
                        else:
                            result = json[token]
                            if isinstance(result, dict):
                                result = hashabledict(result)
                            return result
                    return apply_recursion(json, last_tokens + [current_token])
                else:
                    return self._extract_items(tokens, json[current_token])
        else:
            return json

    @property
    def json(self):
        return self.call_json(self.url)

    @cache.dict(86400)
    def call_json(self, url):
        result = requests.get(url).json()
        return result

    def _get_items(self, keys: typing.List[str]):
        result_json = self.json
        for key in keys:
            result_json = result_json[key]
        return result_json

    def get(self, *args):
        return self.methods[tuple(args)]()


class OverView:
    """
    This the a viewing data class of multiple homogeneous Json

    It adapts a child of SingleView to show the overview of
    properties over multiple Json(s)
    """

    def __init__(self, _class: SingleView,
                 inputs: typing.List[typing.Tuple], schema: JsonSchema = None):
        self.views = [_class(*arg, schema=schema) for arg in inputs]
        if schema is not None:
            self.schema = schema
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=48) as executor:
                self.schema = Union.set(
                    tqdm.tqdm(
                        executor.map(
                            lambda v: v.schema,
                            self.views,
                            chunksize=100),
                        total=len(inputs)))
        self.method_keys = reduce(
            lambda a, b: a | b, map(
                lambda v: set(
                    v.methods.keys()), self.views))

    def get(self, *args):
        result = set()
        for v in self.views:
            try:
                js = v.get(*args)
                if isinstance(js, list):
                    js = set(js)
                    result |= js
                else:
                    result.add(js)
            except KeyError:
                pass
        return result
