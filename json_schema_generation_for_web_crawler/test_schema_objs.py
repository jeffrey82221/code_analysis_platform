import pytest
import copy
from schema_objs import Simple, List, Dict, Union, Optional, UniformDict

@pytest.fixture()
def simple_int():
    return Simple(int)

@pytest.fixture()
def simple_float():
    return Simple(float)

@pytest.fixture()
def simple_none():
    return Simple(None)

@pytest.fixture()
def int_list():
    return List(Simple(int))

@pytest.fixture()
def float_list():
    return List(Simple(float))

@pytest.fixture()
def int_float_dict():
    return Dict({'a': Simple(int), 'b': Simple(float)})

@pytest.fixture()
def complex_dict():
    return Dict({'a': Simple(int), 'b': List(Simple(float)), 'c': Dict({'a': Simple(str), 'b': Optional(Simple(int))})})

@pytest.fixture()
def int_float_union():
    return Union({Simple(int), Simple(float)})

@pytest.fixture()
def optional_int():
    return Optional(Simple(int))

@pytest.fixture()
def optional_int_list():
    return Optional(List(Simple(int)))

def test_repr(
        simple_int, simple_float, simple_none,
        int_list, float_list, int_float_dict, complex_dict, int_float_union,
        optional_int, optional_int_list
    ):
    assert str(simple_int) == 'int'
    assert str(simple_float) == 'float'
    assert str(simple_none) == 'None'
    assert str(int_list) == 'List[int]'
    assert str(float_list) == 'List[float]'
    assert str(int_float_dict) == "Dict[{'a': int, 'b': float}]"
    assert str(complex_dict) == "Dict[{'a': int, 'b': List[float], 'c': Dict[{'a': str, 'b': Optional[int]}]}]"
    assert str(int_float_union) == 'Union[int,float]'
    assert str(simple_float|simple_int) == 'Union[int,float]'
    assert str(simple_float|int_list) == 'Union[List[int],float]'
    assert str(optional_int) == 'Optional[int]'
    assert str(optional_int_list) == 'Optional[List[int]]'
    assert str(Optional(int_float_dict)) == "Optional[Dict[{'a': int, 'b': float}]]"

def test_equal(
    simple_int, simple_float, simple_none,
    int_list, float_list, int_float_dict, complex_dict
    ):
    assert simple_int == copy.deepcopy(simple_int)
    assert simple_float == copy.deepcopy(simple_float)
    assert simple_none == copy.deepcopy(simple_none)
    assert int_list == copy.deepcopy(int_list)
    assert float_list == copy.deepcopy(float_list)
    assert int_float_dict == copy.deepcopy(int_float_dict)
    assert complex_dict == copy.deepcopy(complex_dict)
    assert simple_int != simple_float
    assert int_list != float_list
    assert simple_none != simple_int
    assert simple_int != int_list
    assert complex_dict != int_float_dict


def test_union(
     simple_int, simple_float, simple_none,
    int_list, float_list, int_float_dict, complex_dict, int_float_union
):
    assert (simple_int | simple_int) == simple_int
    assert (simple_float | simple_float) == simple_float
    assert (float_list | float_list) == float_list
    assert (simple_int | simple_float) == int_float_union
    assert (simple_float | simple_int) == int_float_union
    assert (simple_float | simple_int | simple_int) == int_float_union
    assert (simple_float|int_list) == Union({simple_float,int_list})
    assert (simple_float|int_float_dict) == Union({simple_float,int_float_dict})
    assert (simple_none|simple_int) == Optional(simple_int)
    assert (simple_none|complex_dict) == Optional(complex_dict)
    assert (simple_none|simple_int|simple_int) == Optional(simple_int)
    assert (simple_int|simple_none|simple_int) == Optional(simple_int)
    assert (Optional(simple_int)|Simple(None)) == Optional(simple_int)
    assert (Optional(simple_float)|Optional(simple_float)) == Optional(simple_float)
    assert (Optional(simple_float)|simple_int) == Union({simple_int, simple_float, simple_none})
    assert (Optional(simple_float)|Optional(simple_int)) == Union({simple_int, simple_float, simple_none})
    assert (simple_int|Optional(simple_float)) == Union({simple_int, simple_float, simple_none})
    assert (simple_int|Union({simple_float, simple_int})) == Union({simple_int, simple_float})
    assert float_list | int_list == List(Union({simple_float, simple_int}))
    assert float_list | List(Optional(Simple(float))) == List(Optional(simple_float))
    assert Dict({'a': Simple(int), 'b': Simple(float)}) | Dict({'a': Simple(int), 'b': Simple(float)}) == Dict({'a': Simple(int), 'b': Simple(float)})
    assert Dict({'a': Simple(int), 'b': Simple(float)}) | Dict({'a': Simple(None), 'b': Simple(float)}) == Dict({'a': Optional(Simple(int)), 'b': Simple(float)})
    assert Dict({'a': Simple(int), 'b': Simple(float)}) | Dict({'a': Simple(int)}) == Union(
        {Dict({'a': Simple(int), 'b': Simple(float)}), Dict({'a': Simple(int)})}
        )
    
def test_set(simple_int, simple_float, simple_none,
    int_list, float_list, int_float_dict, complex_dict, int_float_union
):
    assert Union.set([simple_int, simple_float]) == int_float_union
    assert Union.set([simple_int, simple_none]) == Optional(simple_int)
    assert Union.set([int_list, float_list, int_float_dict]) == Union({List(Union({simple_int, simple_float})), int_float_dict})
    assert Union.set([complex_dict, complex_dict, complex_dict]) == complex_dict
    assert {complex_dict, complex_dict} == {complex_dict}
    assert len({Optional(simple_int), List(simple_int)}) == 2
    assert len({List(simple_int), List(simple_int)}) == 1
    assert len({Optional(simple_float), List(simple_float), UniformDict(simple_float)}) == 3

def test_to_uniform_dict(int_float_dict, simple_int, simple_float):
    assert int_float_dict.to_uniform_dict() == UniformDict(Union({simple_int, simple_float}))
