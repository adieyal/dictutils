# Quickstart

Welcome to **dictutils**! This library provides small, dependency-free utilities for working with nested dictionaries and objects. The emphasis is on **examples you can copy and paste**.

:::{note}
👨‍💻 **Contributing?** Check out the [GitHub repository](https://github.com/adieyal/dictutils) for development setup and contribution guidelines.
:::

## Installation

```bash
pip install dictutils
```

Requires Python 3.9+.

## First steps

```python
from dictutils import qsdict, mergedict, pivot, nest_agg, Agg
```

### 1. Build nested dicts with qsdict

```python
from dictutils import qsdict
import json

lst = [
    {"shape": "circle", "colour": "blue", "count": 5},
    {"shape": "circle", "colour": "pink", "count": 15},
    {"shape": "square", "colour": "yellow", "count": 29},
    {"shape": "square", "colour": "blue", "count": 10},
]

result = qsdict(lst, "shape", "colour", "count")
print(json.dumps(result, indent=4))
# Output:
# {
#     "circle": {
#         "blue": 5,
#         "pink": 15
#     },
#     "square": {
#         "blue": 10,
#         "yellow": 29
#     }
# }
```

### 2. Merge safely with mergedict

```python
from dictutils import mergedict
import json

a = {"a": {"x": 1}, "list": [1, 2]}
b = {"a": {"y": 2}, "list": [3, 4]}

result = mergedict(a, b)
print(json.dumps(result, indent=4))
# Output:
# {
#     "a": {
#         "x": 1,
#         "y": 2
#     },
#     "list": [
#         1,
#         2,
#         3,
#         4
#     ]
# }
```

### 3. Pivot nested dicts with pivot

```python
from dictutils import pivot
import json

d = {"A": {"X": 1, "Y": 2}, "B": {"X": 3, "Y": 4}}
result = pivot(d, [1, 0])
print(json.dumps(result, indent=4))
# Output:
# {
#     "X": {
#         "A": 1,
#         "B": 3
#     },
#     "Y": {
#         "A": 2,
#         "B": 4
#     }
# }
```

### 4. Aggregate with nest_agg

```python
from dictutils import nest_agg, Agg
import json

items = [
    {"cat": "A", "val": 1},
    {"cat": "A", "val": 2},
    {"cat": "B", "val": 3},
]
aggs = {
    "total": Agg(map=lambda it: it["val"], zero=0),
    "count": Agg(map=lambda it: 1, zero=0),
}
result = nest_agg(items, keys=["cat"], aggs=aggs, include_rows=True)
print(json.dumps(result, indent=4, default=str))
# Output:
# {
#     "A": {
#         "count": 2,
#         "rows": [
#             {"cat": "A", "val": 1},
#             {"cat": "A", "val": 2}
#         ],
#         "total": 3
#     },
#     "B": {
#         "count": 1,
#         "rows": [
#             {"cat": "B", "val": 3}
#         ],
#         "total": 3
#     }
# }
```

### 5. Path-based operations (dictutils.ops)

```python
from dictutils.ops import deep_get, deep_set, flatten_paths, expand_paths
import json

data = {"user": {"name": "Alice", "emails": ["a@example.com"]}}

# Get nested value
name = deep_get(data, "user.name")
print(f"Name: {name}")
# Output: Name: Alice

# Set nested value (auto-creates missing path)
deep_set(data, "user.age", 30)

# Flatten to dot notation
flat = flatten_paths(data)
print("Flattened:")
print(json.dumps(flat, indent=4))
# Output:
# {
#     "user.age": 30,
#     "user.emails[0]": "a@example.com",
#     "user.name": "Alice"
# }

# Expand back to nested dict
expanded = expand_paths(flat)
print("Expanded:")
print(json.dumps(expanded, indent=4))
# Output:
# {
#     "user": {
#         "age": 30,
#         "emails": [
#             "a@example.com"
#         ],
#         "name": "Alice"
#     }
# }
```

**Next:** :doc:`core` • :doc:`ops` • :doc:`cookbook`
