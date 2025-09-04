from collections import namedtuple

import pytest

from dictutils.qsdict import qsdict


def test_qsdict_no_arguments():
    with pytest.raises(ValueError):
        qsdict([])


def test_qsdict_one_argument():
    with pytest.raises(ValueError):
        qsdict([], 1)


def test_qsdict_more_than_one_argument():
    d = qsdict([], 1, 2, 3)
    assert d == {}


def test_qsdict_with_missing_parameters():
    d = qsdict([{"1": "2", "3": 4}], "1", "9")
    assert d == {"2": None}


def test_qsdict_with_missing_parameters_strict():
    with pytest.raises(KeyError, match="Missing key '9'"):
        qsdict([{"1": "2", "3": 4}], "1", "9", strict=True)


def test_qsdict_basic_input():
    d = qsdict([{"a": "b", "c": "d"}], "a", "c")
    assert d == {"b": "d"}


def test_qsdict_with_int_arguments():
    d = qsdict([{1: 2, 3: 4}], 1, 3)
    assert d == {2: 4}


def test_qsdict_two_rows():
    d = qsdict(
        [
            {"a": "b", "c": "d"},
            {"a": "c", "c": "e"},
        ],
        "a",
        "c",
    )
    assert d == {"b": "d", "c": "e"}


def test_qsdict_overwrites_value_with_two_parameters():
    d = qsdict(
        [
            {"a": "b", "c": "d"},
            {"a": "b", "c": "f"},
        ],
        "a",
        "c",
    )
    assert d == {"b": "f"}


def test_qsdict_3_level_nesting():
    d = [
        {"a": 1, "b": 2, "c": 3},
        {"a": 1, "b": 4, "c": 6},
    ]
    d1 = qsdict(d, "a", "b", "c")
    assert d1 == {1: {2: 3, 4: 6}}

    d2 = qsdict(d, "b", "a", "c")
    assert d2 == {2: {1: 3}, 4: {1: 6}}


def test_qsdict_callable():
    d = [
        {"a": 1, "b": 2, "c": 3},
        {"a": 1, "b": 4, "c": 6},
    ]
    d1 = qsdict(d, "a", lambda x: "Hello World", "b", "c")
    assert d1 == {1: {"Hello World": {2: 3, 4: 6}}}


def test_qsdict_4_level_nested():
    d = [
        {"a": 1, "b": 2, "c": 3, "d": 4},
        {"a": 1, "b": 4, "c": 6, "d": 7},
    ]
    d1 = qsdict(d, "a", "b", "c", "d")
    assert d1 == {1: {2: {3: 4}, 4: {6: 7}}}


def test_qsdict_tuple_returns_array():
    d = [
        {"a": 1, "b": 2, "c": 3, "d": 4},
        {"a": 1, "b": 4, "c": 6, "d": 7},
    ]
    d1 = qsdict(d, "a", "b", ("c", "d"))
    assert d1 == {1: {2: [3, 4], 4: [6, 7]}}


def test_qsdict_with_objects():
    TestClass = namedtuple("TestClass", ["a", "b", "c"])
    d = [
        TestClass(1, 2, 3),
        TestClass(1, 4, 6),
    ]
    d1 = qsdict(d, "a", "b", "c")
    assert d1 == {1: {2: 3, 4: 6}}


def test_qsdict_with_objects_and_callable():
    class TestClass:
        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c

    d = [
        TestClass(1, 2, 3),
        TestClass(1, 4, 6),
    ]
    d1 = qsdict(d, lambda x: x.a, "b", "c")
    assert d1 == {1: {2: 3, 4: 6}}


def test_qsdict_with_objects_strict_missing_attr():
    class TestClass:
        def __init__(self, a, b):
            self.a = a
            self.b = b

    d = [TestClass(1, 2)]
    with pytest.raises(AttributeError, match="Missing attribute 'missing'"):
        qsdict(d, "a", "missing", strict=True)


def test_qsdict_nested_access_with_callable():
    # Test accessing nested values with callable selectors
    d = [{"nested": {"key": "value1"}}, {"nested": {"key": "value2"}}]
    result = qsdict(d, lambda x: x["nested"]["key"], lambda x: "leaf")
    assert result == {"value1": "leaf", "value2": "leaf"}


def test_qsdict_callable_and_nested_combined():
    # Test combining callable selectors for complex access patterns
    d = [
        {"cat": "A", "nested": {"val": 1}},
        {"cat": "A", "nested": {"val": 2}},
        {"cat": "B", "nested": {"val": 3}},
    ]
    result = qsdict(d, lambda x: x["cat"].lower(), lambda x: x["nested"]["val"])
    assert result == {"a": 2, "b": 3}  # Last value overwrites due to same key "a"


def test_qsdict_with_none_keys():
    # Test behavior when selectors return None (creates None keys)
    d = [{"a": 1}, {"b": 2}]  # Second item has no "a" key
    result = qsdict(d, "a", "b", strict=False)
    assert result == {1: None, None: 2}  # None key created for missing "a"
