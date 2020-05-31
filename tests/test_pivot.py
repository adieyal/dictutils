from collections import OrderedDict
import pytest

from dictutils.pivot import flatten_dict, rearrange, nest, pivot

@pytest.fixture(scope="module", params=[dict, OrderedDict])
def dictionary(request):
    return request.param

def test_flatten_empty_dict(dictionary):
    d = dictionary()
    assert flatten_dict(d) == []

def test_flatten_simple_dict():
    d = {"a": "b"}
    assert flatten_dict(d) == [["a", "b"]]

    d = {"a": "b", "c": "d"}
    assert flatten_dict(d) == [["a", "b"], ["c", "d"]]

def test_flatten_simple_2_level_dict():
    d = {"a": {"b": "c"}}
    assert flatten_dict(d) == [["a", "b", "c"]] 

def test_flatten_multiple_2_level_dict():
    d = {"a": {"b": "c", "d": "e"}}
    assert flatten_dict(d) == [["a", "b", "c"], ["a", "d", "e"]] 

def test_flatten_multiple_3_level_dict():
    d = {"a": {
            "b": {
                "c": {
                    "d": "e"
                },
                "c2": {
                    "d2": "e2"
                }
            }
        }
    }
    assert flatten_dict(d) == [["a", "b", "c", "d", "e"], ["a", "b", "c2", "d2", "e2"]] 
