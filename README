# dictutils

A collection of useful tools for manipulating dictionaries.

## dictutils.qsdict

Takes a list of dicts or objects and convert it into nested dicts.

```python
lst = [
    {"shape": "circle", "colour": "blue", "count": 5},
    {"shape": "circle", "colour": "pink", "count":15},
    {"shape": "square", "colour": "yellow", "count": 29},
    {"shape": "square", "colour": "blue", "count": 10}
]

qsdict(lst, "shape", "colour", "count")

# returns

{
    "circle": {
        "blue": 5,
        "pink": 15
    },
    "square": {
        "yellow": 29,
        "blue": 10
    }
}

qsdict(lst, "colour", "shape", "count")

# returns

{
    "blue": {
        "circle": 5,
        "square": 10
    },
    "pink": {
        "circle": 15
    },
    "yellow": {
        "square": 29
    }
}
```

Can also accept callables

```python

qsdict(lst, lambda x: x["colour"][0:2], "shape", "count")

{
    "bl": {
        "circle": 5,
        "square": 10
    },
    "pi": {
        "circle": 15
    },
    "ye": {
        "square": 29
    }
}
```

Access an arbitary number of arguments

```python
lst = [
    {"shape": "circle", "colour": "blue", "country": "France", "count": 5},
    {"shape": "circle", "colour": "pink", "country": "Germany", "count":15},
    {"shape": "square", "colour": "yellow", "country": "France", "count": 29},
    {"shape": "square", "colour": "blue", "country": "China", "count": 10}
]

qsdict(lst, lambda x: x["colour"][0:2], "shape", "country","count")

# Returns
{
    "bl": {
        "circle": {
            "France": 5
        },
        "square": {
            "China": 10
        }
    },
    "pi": {
        "circle": {
            "Germany": 15
        }
    },
    "ye": {
        "square": {
            "France": 29
        }
    }
}
```

Pass a tuple as the last argument if you prefer the leaf node to be a list

```python
qsdict(lst, lambda x: x["colour"][0:2], "shape", ("country","count"))

{
    "bl": {
        "circle": [
            "France",
            5
        ],
        "square": [
            "China",
            10
        ]
    },
    "pi": {
        "circle": [
            "Germany",
            15
        ]
    },
    "ye": {
        "square": [
            "France",
            29
        ]
    }
}
```

## dictutils.mergedict

Merges two nested dictionaries. Note that the first dictionary is updated.

```python
d1 = {
    "blue": {
        "circle": {
            "France": 5
        },
        "square": {
            "China": 10
        }
    },
    "pink": {
        "circle": {
            "Germany": 15
        }
    },
    "yellow": {
        "square": {
            "France": 29
        }
    }
}

d2 = {
    "blue": {
        "brightness": 4,
    },
    "pink": {
        "brightness": 4,
    },
    "yellow": {
        "brightness": 4,
    }
}

mergedict(d1, d2)

print(d1)

{
    "blue": {
        "circle": {
            "France": 5
        },
        "square": {
            "China": 10
        },
        "brightness": 4
    },
    "pink": {
        "circle": {
            "Germany": 15
        },
        "brightness": 4
    },
    "yellow": {
        "square": {
            "France": 29
        },
        "brightness": 4
    }
}
```

If you don't want to clobber the first dictionary, provide an empty dictionary
```
d0 = {}
mergedict(d0, d1)
mergedict(d0, d2)
```

This can be repeated an arbitary number of times to create a complicated data structure while avoiding nested loops and unwieldy code. This code is courtsey of this Stack Overflow [thread](https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries).

## dictutils.pivot

Pivots a dictionary by a give list of keys

```python
d1 = {
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

print(pivot(d, [2, 1, 0])

{
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
