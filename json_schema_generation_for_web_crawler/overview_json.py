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
import schema_fitter
from schema_objs import Dict, List, UniformDict, Union, Simple, Optional, Unknown, JsonSchema
import typing
import json
import copy
import tqdm
from redis_decorators import RedisCaching

caching = RedisCaching('redis://localhost:6379')
    

class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class SingleView:
    def __init__(self, schema: JsonSchema=None):
        self._methods: typing.Dict[str, typing.Callable]= dict()
        self._schema = schema

    @property
    def schema(self):
        if self._schema is None:
            self._schema = schema_fitter.fit(self.json, unify_callback=schema_fitter.try_unify_dict)
        return self._schema
    
    @property
    def methods(self):
        if len(self._methods) == 0:        
            self._setup_getters()
        return self._methods

    def _setup_getters(self):
        self._setup_getters_from_schema(self.schema)
    
    def _setup_getters_from_schema(self, schema, tokens = []):
        if isinstance(schema, Dict):
            # Setup New Method
            self._methods[tuple(tokens)] = lambda: self._extract_items(tokens, self.json)
            for key, value in schema._content.items():
                self._setup_getters_from_schema(value, tokens = tokens + [key])
        elif isinstance(schema, List):
            # Setup New Method
            self._methods[tuple(tokens)] = lambda: self._extract_items(tokens, self.json)
            self._setup_getters_from_schema(schema._content, tokens = tokens + ['_list_'])
        elif isinstance(schema, UniformDict):
            # Setup New Method
            self._methods[tuple(tokens)] = lambda: self._extract_items(tokens, self.json)
            self._setup_getters_from_schema(schema._content, tokens = tokens + ['_uniform_dict_'])
        elif isinstance(schema, Optional):
            self._setup_getters_from_schema(schema._the_content, tokens = tokens)
        elif isinstance(schema, Simple):
            # Setup New Method
            self._methods[tuple(tokens)] = lambda: self._extract_items(tokens, self.json)
        elif isinstance(schema, Union):
            raise ValueError('There is Union in schema. Watch out!')
        elif isinstance(schema, Unknown):
            print('Ignore Unknown for getter creation, tokens:', tokens)
        else:
            raise ValueError('Undefined Schema Obj, schema:', schema, 'tokens:', tokens)

    def _extract_items(self, _tokens, _json, _last_tokens=[]):
        tokens = copy.copy(_tokens)
        json = copy.deepcopy(_json)
        last_tokens = copy.copy(_last_tokens)
        if tokens:
            current_token = tokens.pop(0)
            if current_token == '_list_':
                return self._extract_items(tokens, json, _last_tokens=last_tokens+[current_token])
            elif current_token == '_uniform_dict_':
                return self._extract_items(tokens, json, _last_tokens=last_tokens+[current_token])
            else:
                if last_tokens:
                    def apply_recursion(json, _tokens):
                        tokens = copy.copy(_tokens)
                        token = tokens.pop(0)
                        if token == '_uniform_dict_':
                            return hashabledict([(k, apply_recursion(e, tokens)) for k,e in json.items()])
                        elif token == '_list_':
                            return set([apply_recursion(e, tokens) for e in json])
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

    @abc.abstractproperty
    def url(self) -> str:
        raise NotImplementedError

    @property
    def json(self):
        return json.loads(self.call_json_text(self.url))

    @caching.cache_string()
    def call_json_text(self, url):
        txt = requests.get(url).text
        return txt

    def _get_items(self, keys: typing.List[str]):
        result_json = self.json
        for key in keys:
            result_json = result_json[key]
        return result_json
import concurrent
class Overview:
    def __init__(self, _class, inputs: typing.List[typing.Tuple]):
        self.views = [_class(*arg) for arg in inputs]
        with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
            self.schema = Union.set(tqdm.tqdm(executor.map(lambda v: v.schema, self.views, chunksize=100), total=len(inputs)))

class PyPiPackageView(SingleView):
    def __init__(self, pkg):
        self._pkg = pkg
        super().__init__(schema=None)
    
    @property
    def url(self):
        return f'https://pypi.org/pypi/{self._pkg}/json'

    @property
    def released_versions(self):
        return set(self.methods[('releases',)]().keys())
    
class PyPiPackageOverView(Overview):
    def __init__(self, pkgs):
        super().__init__(PyPiPackageView, [(p, ) for p in pkgs])
    
    @property
    def released_versions(self):
        result = set()
        for v in self.views:
            try:
                result |= v.released_versions
            except KeyError:
                print('ignore', v._pkg)
        return result

class PypiVersionPackageView(SingleView):
    def __init__(self, pkg, version):
        self._pkg = pkg
        self._version = version
        super().__init__(schema=None)
    @property
    def url(self):
        return f'https://pypi.org/pypi/{self._pkg}/{self._version}/json'


if __name__ == '__main__':
    v = PypiVersionPackageView('pandas', '1.5.0rc0')
    print(v.methods.keys())
    """
    s = PyPiPackageView('pytz')
    print('========================== pandas ================================')
    print(s.methods.keys())
    print(s.methods[('info', 'author')]())
    print(s.released_versions)
    v = PypiVersionPackageView('pandas', '1.5.0rc0')
    print(s.methods.keys())
    print(s.methods[('info', 'requires_dist')]())
    print('done')
    print('========================== overview =============================')
    pkgs = []
    with open('../pypi_graph_analysis/package_names.txt', 'r') as f:
        for i, pkg in enumerate(f):
            pkg = pkg.strip()
            pkgs.append(pkg)
    o = PyPiPackageOverView(pkgs[:1000])
    print(o.schema)
    print(o.released_versions)
    """