from collections import OrderedDict

import pytest

from dictutils.pivot import flatten_dict, nest, pivot, rearrange


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
    d = {"a": {"b": {"c": {"d": "e"}, "c2": {"d2": "e2"}}}}
    assert flatten_dict(d) == [["a", "b", "c", "d", "e"], ["a", "b", "c2", "d2", "e2"]]


def test_rearrange_basic():
    in_arrs = [["a", "x", 2], ["a", "y", 3]]
    result = rearrange(in_arrs, [1, 0])
    assert result == [["x", "a", 2], ["y", "a", 3]]


def test_rearrange_invalid_order():
    in_arrs = [["a", "x", 2]]  # Has 2 keys (indices 0,1), value at index 2

    # Index 2 is out of range (it's the value position)
    with pytest.raises(IndexError, match="order index 2 out of range"):
        rearrange(in_arrs, [2, 0])

    # Negative index
    with pytest.raises(IndexError, match="order index -1 out of range"):
        rearrange(in_arrs, [-1, 0])

    # Index too high
    with pytest.raises(IndexError, match="order index 3 out of range"):
        rearrange(in_arrs, [3, 0])


def test_nest_empty():
    assert nest([]) == {}


def test_nest_single_level():
    arrays = [["a", 1], ["b", 2]]
    result = nest(arrays)
    assert result == {"a": 1, "b": 2}


def test_nest_nested():
    arrays = [["a", "x", 1], ["a", "y", 2]]
    result = nest(arrays)
    assert result == {"a": {"x": 1, "y": 2}}


def test_pivot_basic():
    d = {"A": {"X": 1, "Y": 2}, "B": {"X": 3, "Y": 4}}
    result = pivot(d, [1, 0])
    expected = {"X": {"A": 1, "B": 3}, "Y": {"A": 2, "B": 4}}
    assert result == expected


def test_pivot_3_levels():
    d = {"A": {"Cat1": {"X": 1, "Y": 2}, "Cat2": {"X": 3, "Y": 4}}}
    result = pivot(d, [2, 1, 0])  # Move innermost level to front
    expected = {
        "X": {"Cat1": {"A": 1}, "Cat2": {"A": 3}},
        "Y": {"Cat1": {"A": 2}, "Cat2": {"A": 4}},
    }
    assert result == expected
