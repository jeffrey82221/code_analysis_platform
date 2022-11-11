"""
Json Schema Objects 
that supports union operations

TODO:
- [X] Set operation of JsonSchema(s) (defined as staticmethod of Union)
    - converting a list of JsonSchemas into one schema. 
- [X] UniformDict build
- [ ] A SchemaFitter that infer Schema from Json(s)
"""
import abc
import copy
import typing
from functools import reduce

__all__ = [
    'Simple',
    'List',
    'Union',
    'Dict',
    'Optional',
    'UniformDict'
]

class JsonSchema:
    def __init__(self, content):
        self._content = content
        self.check_content()
    @abc.abstractmethod
    def check_content(self):
        raise NotImplementedError
    def __eq__(self, e):
        if type(self) == type(e):
            return self._content == e._content
        else:
            return False
    
    def __or__(self, e):
        return self._base_or(e)

    def _base_or(self, e):
        old = copy.deepcopy(self)
        new = copy.deepcopy(e)
        if old == new:
            return old
        else:
            if old._content is None:
                if new._content is None:
                    return old
                else:
                    return Optional(new)
            elif new._content is None:
                return Optional(old)
            elif isinstance(new, Union):
                new |= old
                return new
            else:
                return Union({old, new})

    def _base_hash(self):
        return hash(self._content)

    def __hash__(self):
        return self._base_hash()
    
class Simple(JsonSchema):
    """
    simple json units, such as `int`, `float`, `null`, 
        `str`, etc.
    """
    def __init__(self, content: type):
        super().__init__(content)
    def check_content(self):
        assert isinstance(self._content, type) or self._content == None
    def __repr__(self):
        if self._content is None:
            return 'None'
        else:
            return self._content.__name__
    
class List(JsonSchema):
    def __init__(self, content: JsonSchema):
        super().__init__(content)
    def check_content(self):
        assert isinstance(self._content, JsonSchema)
    def __repr__(self):
        return f'List[{self._content}]'
    def __or__(self, e):
        if isinstance(e, List):
            new = copy.deepcopy(e)
            old = copy.deepcopy(self)
            return List(old._content | new._content)
        else:
            return self._base_or(e)
            
class Union(JsonSchema):
    @staticmethod
    def set(json_schemas: typing.List[JsonSchema]):
        return reduce(lambda a, b: a | b, json_schemas)

    def __init__(self, content: typing.Set[JsonSchema]):
        super().__init__(content)
    def check_content(self):
        assert isinstance(self._content, set)
        for e in self._content:
            assert isinstance(e, JsonSchema)
    def __repr__(self):
        content_str = ','.join(map(str, list(self._content)))
        return f'Union[{content_str}]'
    def __or__(self, e):
        new = copy.deepcopy(e)
        if isinstance(new, Union):
            new_set = copy.deepcopy(self._content)
            for element in new._content:
                new_set |= element
            return Union(new_set)
        else:
            new_set = copy.deepcopy(self._content)
            new_set.add(new)
            return Union(new_set)
    def __hash__(self):
        return hash(tuple(self._content))
    

class Optional(Union):
    def __init__(self, content: JsonSchema):
        self._the_content = content
        super().__init__({Simple(None), content})
    def __repr__(self):
        return f'Optional[{self._the_content}]'
    def __or__(self, e):
        old = copy.deepcopy(self)
        new = copy.deepcopy(e)
        if new._content is None:
            return old
        elif old == new:
            return old
        else:
            if old._the_content == new:
                return old
            else:
                new_set = copy.deepcopy(old._content)
                if isinstance(new, Union):
                    new_set |= new._content
                else:
                    new_set.add(new)
                return Union(new_set)

class Dict(JsonSchema):
    def __init__(self, content: dict):
        super().__init__(content)
    def check_content(self):
        assert isinstance(self._content, dict)
        for key in self._content:
            assert isinstance(key, str)
            assert isinstance(self._content[key], JsonSchema)
    def __repr__(self):
        return f'Dict[{self._content}]'
    def __hash__(self):
        return hash(tuple(sorted(self._content.items())))    
    def __or__(self, e):
        if isinstance(e, Dict) and self._content.keys() == e._content.keys():
            old = copy.deepcopy(self)
            new = copy.deepcopy(e)
            for key in old._content:
                old._content[key] |= new._content[key]
            return old
        else:
            return self._base_or(e)
    def to_uniform_dict(self):
        schemas = [v for v in self._content.values()]
        uniform_content = Union.set(schemas)
        return UniformDict(uniform_content)

class UniformDict(JsonSchema):
    """
    Dictionary where value elements 
    are united into a JsonSchema.
    """
    def __init__(self, content: JsonSchema):
        super().__init__(content)
    
    def check_content(self):
        assert isinstance(self._content, JsonSchema)

    def __repr__(self):
        return f'UniformDict[{self._content}]'