import pytest

from dictutils.mergedict import mergedict

def test_none_input():
    with pytest.raises(TypeError):
        mergedict(None, None) == None

def test_one_argument_none():
    with pytest.raises(TypeError):
        mergedict(None, {1: 2})
        
    with pytest.raises(TypeError):
        mergedict({1: 2}, None)

def test_merge_non_dict():
    a = [1, 2]
    b = {}
    with pytest.raises(TypeError):
        mergedict(a, b)

def test_two_empty_dicts():
    assert mergedict({}, {}) == {}

def test_one_empty_dict():
    assert mergedict({1: 2}, {}) == {1: 2}
    assert mergedict({}, {1: 2}) == {1: 2}

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

    assert mergedict(a, b) == {
       1: {2: 3},
       2: {4: 5}
    }

def test_nested2():
    a = {1: {2: {3: 4}}}
    b = {2: {4: 5}}

    assert mergedict(a, b) == {
       1: {2: {3: 4}},
       2: {4: 5}
    }

def test_nested_merge():
    a = {1: {2: {3: 4}}}
    b = {1: {4: 5}}

    assert mergedict(a, b) == {
        1: {
            2: {3: 4},
            4: 5
        },
    }

def test_concatenate_arrays():
    a = {1: [1, 2]}
    b = {1: [3, 4]}

    assert mergedict(a, b) == {
        1: [1, 2, 3, 4]
    }
