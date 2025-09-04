from collections import OrderedDict, UserDict, defaultdict

import pytest

from dictutils.mergedict import mergedict


def test_no_arguments():
    with pytest.raises(TypeError):
        mergedict()


def test_none_arguments():
    # None is now allowed and handled properly
    assert mergedict(None, None) is None
    assert mergedict({1: 2}, None) == {1: 2}
    assert mergedict(None, {1: 2}) == {1: 2}


def test_merge_non_dict():
    a = [1, 2]
    b = {}
    with pytest.raises(TypeError, match="All arguments must be mappings or None"):
        mergedict(a, b)


def test_two_empty_dicts():
    assert mergedict({}, {}) == {}


def test_accepts_other_mappings():
    assert mergedict(defaultdict(), defaultdict()) == {}
    assert mergedict(OrderedDict(), OrderedDict()) == {}


def test_one_empty_dict():
    assert mergedict({1: 2}, {}) == {1: 2}
    assert mergedict({}, {1: 2}) == {1: 2}


def test_one_argument():
    d = {1: 2, 3: 4}
    result = mergedict(d)
    assert result == d
    assert result is d  # Should return the same dict object


def test_simple_merge():
    a = {1: 2}
    b = {3: 4}
    assert mergedict(a, b) == {1: 2, 3: 4}


def test_overwrite():
    a = {1: 2, 3: 5}
    b = {3: 4}
    assert mergedict(a, b) == {1: 2, 3: 4}


def test_no_overwrite():
    a = {1: 2, 3: 5}
    b = {3: 4}
    assert mergedict(a, b, update=False) == {1: 2, 3: 5}


def test_nested():
    a = {1: {2: 3}}
    b = {2: {4: 5}}
    assert mergedict(a, b) == {1: {2: 3}, 2: {4: 5}}


def test_nested2():
    a = {1: {2: {3: 4}}}
    b = {2: {4: 5}}
    assert mergedict(a, b) == {1: {2: {3: 4}}, 2: {4: 5}}


def test_nested_merge():
    a = {1: {2: {3: 4}}}
    b = {1: {4: 5}}
    assert mergedict(a, b) == {
        1: {2: {3: 4}, 4: 5},
    }


def test_nested_merge_with_update_false():
    # Test the fix: update flag should be passed to recursive calls
    a = {1: {2: 3, 4: 5}}
    b = {1: {2: 999}}  # This should NOT override when update=False
    result = mergedict(a, b, update=False)
    assert result == {1: {2: 3, 4: 5}}


def test_concatenate_arrays():
    a = {1: [1, 2]}
    b = {1: [3, 4]}
    assert mergedict(a, b) == {1: [1, 2, 3, 4]}


def test_merge_multiple():
    a = {1: [1, 2]}
    b = {1: [3, 4]}
    c = {2: [3, 4]}
    assert mergedict(a, b, c) == {1: [1, 2, 3, 4], 2: [3, 4]}


def test_converts_nested_mappings_to_dicts():
    # Test that nested mappings are converted to plain dicts
    a = {}
    b = {"nested": UserDict({"key": "value"})}
    result = mergedict(a, b)
    assert result == {"nested": {"key": "value"}}
    assert result is not None
    assert isinstance(result["nested"], dict)  # Should be plain dict, not UserDict
