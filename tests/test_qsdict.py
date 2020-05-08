import pytest

from dictutils.qsdict import qsdict

def test_qdict_no_arguments():
    with pytest.raises(ValueError):
        d = qsdict([])

def test_qdict_one_arguments():
    with pytest.raises(ValueError):
        d = qsdict([], 1)

def test_qdict_more_than_one_argument():
    d = qsdict([], 1, 2, 3)
    assert d == {}

def test_with_missing_parameters():
    d = qsdict([{"1":"2", "3":4}], "1", "9")
    assert d == {"2": None}

"""
def test_qdict_at_least_two_parameters():
    with pytest.raises(ValueError):
        d = qsdict([{"a": "b"}], "a")

"""

def test_qdict_basic_input():
    d = qsdict([{"a": "b", "c": "d"}], "a", "c")
    assert d == {
        "b": "d"
    }

def test_with_int_arguments():
    d = qsdict([{1: 2, 3: 4}], 1, 3)
    assert d == {
        2: 4
    }

def test_qdict_two_rows():
    d = qsdict([
        {"a": "b", "c": "d"},
        {"a": "c", "c": "e"},
    ], "a", "c")

    assert d == {
        "b": "d",
        "c": "e"
    }

def test_qdict_overwrites_value_with_two_parameters():
    d = qsdict([
        {"a": "b", "c": "d"},
        {"a": "b", "c": "f"},
    ], "a", "c")

    assert d == {
        "b": "f"
    }

def test_qdict_3_level_nesting():
    d = [
        {"a": 1, "b": 2, "c": 3},
        {"a": 1, "b": 4, "c": 6},
    ]

    d1 = qsdict(d, "a", "b", "c")

    assert d1 == {
        1 : {
            2: 3,
            4: 6
        }
    }

    d2 = qsdict(d, "b", "a", "c")

    assert d2 == {
        2 : {
            1: 3
        },
        4 : {
            1: 6
        }
    }

def test_callable():
    d = [
        {"a": 1, "b": 2, "c": 3},
        {"a": 1, "b": 4, "c": 6},
    ]

    d1 = qsdict(d, "a", lambda x: "Hello World", "b", "c")

    assert d1 == {
        1 : {
            "Hello World": {
                2: 3,
                4: 6
            }
        }
    }

    d2 = qsdict(d, "b", lambda x: x["a"] + 1,  "c")

    assert d2 == {
        2 : {
            2: 3
        },
        4 : {
            2: 6
        }
    }

def test_object_properties():
    class TestClass:
        def __init__(self, a, b, c):
            self.a, self.b, self.c = a, b, c

    c1 = TestClass(1, 2, 3)
    c2 = TestClass(1, 4, 6)

    d = [c1, c2]

    d1 = qsdict(d, "a", "b", "c")

    assert d1 == {
        1 : {
            2: 3,
            4: 6
        }
    }

def test_long_input():
    d = [
        {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
        {"a": 1, "b": 2, "c": 3, "d": 7, "e": 8},
    ]

    d1 = qsdict(d, "a", "b", "c", "d",  "e")

    assert d1 == {
        1: {
            2: {
                3: {
                    4: 5,
                    7: 8
                }
            }
        }
    }
