def flatten_dict(d):
    """
    Flatten a dictionary into an array of arrays e.g:

    {
        a: {
            x: 2,
            y: 3
        },
        b: {
            x: 4,
            y: 5
        }
    }

    becomes
    [
        [a, x, 2],
        [a, y, 3],
        [b, x, 4],
        [b, y, 5],
    ]

    used as a component of the pivot function
    
    """
    if type(d) != dict:
        return [[d]]

    arr = []
    for k, v in d.items():
        for el in flatten_dict(v):
            arr.append([k] + el)

    return arr

def rearrange(in_arrs, order):
    """
    rearrange elements in a given list of arrays. The last element always remains in place

    e.g.
    d =[
        [a, x, 2],
        [a, y, 3],
        [b, x, 4],
        [b, y, 5],
    ]

    rearrange(d, [1, 0])

    d =[
        [x, a, 2],
        [y, a, 3],
        [x, b, 4],
        [y, b, 5],
    ]

    used as a componenbt of the pivot function
    """
    out_arrs = []
    for arr in in_arrs:
        out_arrs += [[arr[idx] for idx in order] + [arr[-1]]]

    return out_arrs

def nest(arrays, root=None):
    """
    Unflatten a dictionary. Similar to qsdict but is simpler and works on arrays
    """
    if len(arrays) == 0:
        return {}


    d = root or defaultdict(dict)
    for arr in arrays:
        if len(arr) >= 2:
            head, *tail = arr
            if len(tail) == 1:
                d[head] = tail[0]
            elif len(tail) > 1:
                d[head] = nest([tail], d[head])
    return d
        
def pivot(d, order):
    """
    Pivots an array by a list of keys

    d = {
        "A": {
            "Category1": {
                "X": 111111,
                "Y": 222222,
            },
            "Category2": {
                "X": 333333,
                "Y": 444444,
            },
            "Category3": {
                "X": 555555,
                "Y": 666666,
            }
        },
        "B": {
            "Category1": {
                "X": 777777,
                "Y": 888888,
            },
            "Category2": {
                "X": 999999,
                "Y": 101010,
            },
            "Category3": {
                "X": 101011,
                "Y": 101012,
            }
        },
    }

    pivot(d, [2, 1, 0]) 

    becomes:
    
    d = {
    "X": {
        "Category1": {
            "A": 111111,
            "B": 777777,
        },
        "Category2": {
            "A": 333333,
            "B": 999999,
        },
        "Category3": {
            "A": 555555,
            "B": 101011,
        },
    },
    "Y": {
        "Category1": {
            "A": 222222,
            "B": 888888,
        },
        "Category2": {
            "A": 444444,
            "B": 101010,
        },
        "Category3": {
            "A": 666666,
            "B": 101012,
        },
    },
}
    """
    flattened = flatten_dict(d)
    rearranged = rearrange(flattened, order)
    nested = nest(rearranged)

    return nested
