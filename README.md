# dictutils

**A collection of utilities for manipulating nested dictionaries and data structures in Python.**

[![Documentation Status](https://readthedocs.org/projects/dictutils/badge/?version=latest)](https://dictutils.readthedocs.io/en/latest/?badge=latest)
[![CI](https://github.com/adieyal/dictutils/workflows/CI/badge.svg)](https://github.com/adieyal/dictutils/actions)

## Requirements
- Python 3.9+

## Installation

Install from PyPI (recommended):

```bash
pip install dictutils
```

Or from source (using PEP 517/518):

```bash
pip install .
# For contributors (editable install):
pip install -e .[test,typecheck,lint]
```

## Quick Examples

```python
from dictutils import qsdict, mergedict, pivot, nest_agg, Agg

# Build nested dicts from lists
sales = [{"region": "North", "product": "Widget", "revenue": 1000}]
result = qsdict(sales, "region", "product", "revenue")
# {"North": {"Widget": 1000}}

# Safely merge nested dicts
a = {"user": {"name": "Alice"}}
b = {"user": {"email": "alice@example.com"}}
mergedict(a, b)  # {"user": {"name": "Alice", "email": "alice@example.com"}}

# Pivot nested structures  
data = {"A": {"X": 1, "Y": 2}, "B": {"X": 3, "Y": 4}}
pivot(data, [1, 0])  # {"X": {"A": 1, "B": 3}, "Y": {"A": 2, "B": 4}}

# Advanced aggregation
aggs = {"total": Agg(map=lambda x: x["amount"], zero=0)}
nest_agg(transactions, keys=["category"], aggs=aggs)
```

## API

### `dictutils.qsdict`

```python
def qsdict(qs: Iterable[Union[Mapping, object]], *args, strict: bool = False) -> dict:
    """Build a nested dict from rows (dicts or objects) by a sequence of selectors."""
```

#### Example
```python
from dictutils import qsdict
lst = [
    {"shape": "circle", "colour": "blue", "count": 5},
    {"shape": "circle", "colour": "pink", "count": 15},
    {"shape": "square", "colour": "yellow", "count": 29},
    {"shape": "square", "colour": "blue", "count": 10},
]
result = qsdict(lst, "shape", "colour", "count")
# {'circle': {'blue': 5, 'pink': 15}, 'square': {'yellow': 29, 'blue': 10}}

# Strict mode raises on missing keys/attributes
qsdict([{"a": 1}], "a", "missing", strict=True)  # KeyError
```

### `dictutils.mergedict`

```python
def mergedict(*args, path=None, update=True) -> dict:
    """Merge multiple nested dicts. The first dict is updated in-place."""
```

#### Example
```python
from dictutils import mergedict
d1 = {"a": {"b": 1}}
d2 = {"a": {"c": 2}}
merged = mergedict(d1, d2)
# d1 is now {"a": {"b": 1, "c": 2}}
```

### `dictutils.pivot`

```python
def pivot(d: dict, order: list[int]) -> dict:
    """Pivot a nested dict by a list of key indices."""
```

#### Example
```python
from dictutils import pivot
d = {"A": {"X": 1, "Y": 2}, "B": {"X": 3, "Y": 4}}
result = pivot(d, [1, 0])
# {'X': {'A': 1, 'B': 3}, 'Y': {'A': 2, 'B': 4}}
```

### `dictutils.nestagg`

```python
from typing import Any, Callable
from dataclasses import dataclass

def nest_agg(
    items: list[Any],
    keys: list[str | Callable[[Any], Any]],
    *,
    aggs: dict[str, 'Agg'],
    include_rows: bool = False,
    rows_key: str = "rows",
) -> dict:
    """Group and aggregate items by keys, with flexible aggregation at leaves."""

@dataclass(frozen=True)
class Agg:
    map: Callable[[Any], Any]
    zero: Any | Callable[[], Any] | None = None
    reduce: Callable[[Any, Any], Any] = operator.add
    skip_none: bool = True
    finalize: Callable[[Any], Any] | None = None  # Transform final result
```

#### Examples
```python
from dictutils import nest_agg, Agg

# Simple aggregation
items = [{"cat": "A", "val": 1}, {"cat": "A", "val": 2}, {"cat": "B", "val": 3}]
aggs = {"total": Agg(map=lambda it: it["val"], zero=0)}
result = nest_agg(items, keys=["cat"], aggs=aggs)
# {'A': {'total': 3}, 'B': {'total': 3}}

# Calculate averages with finalize
aggs = {
    "avg": Agg(
        map=lambda x: (x["val"], 1),
        zero=(0, 0),
        reduce=lambda a, b: (a[0] + b[0], a[1] + b[1]),
        finalize=lambda x: x[0] / x[1] if x[1] > 0 else 0
    )
}
result = nest_agg(items, keys=["cat"], aggs=aggs)
# {'A': {'avg': 1.5}, 'B': {'avg': 3.0}}
```

### `dictutils.ops` - Advanced Operations

The `ops` module provides 20+ utilities for advanced dictionary manipulation:

#### Path Operations
```python
from dictutils.ops import deep_get, deep_set, deep_has, ensure_path

d = {"user": {"profile": {"name": "Alice"}}}
deep_get(d, "user.profile.name")    # "Alice"
deep_set(d, "user.profile.age", 30) # Creates nested path if needed
deep_has(d, "user.settings")        # False
ensure_path(d, "user.settings")     # Creates empty dict at path
```

#### Data Transformation
```python
from dictutils.ops import flatten_paths, expand_paths, pivot, transpose_dict

# Flatten nested structure to dot notation
flatten_paths({"a": {"b": 1, "c": 2}})  # {"a.b": 1, "a.c": 2}

# Expand dot notation back to nested
expand_paths({"a.b": 1, "a.c": 2})     # {"a": {"b": 1, "c": 2}}

# Transpose nested dict structure
transpose_dict({"A": {"X": 1, "Y": 2}, "B": {"X": 3, "Y": 4}})
# {"X": {"A": 1, "B": 3}, "Y": {"A": 2, "B": 4}}
```

#### Aggregation Helpers
```python
from dictutils.ops import group_by, count_by, sum_by, index_by

users = [
    {"id": 1, "name": "Alice", "dept": "eng", "salary": 90000},
    {"id": 2, "name": "Bob", "dept": "eng", "salary": 85000},
    {"id": 3, "name": "Carol", "dept": "sales", "salary": 70000}
]

group_by(users, "dept")                    # {"eng": [...], "sales": [...]}
count_by(users, "dept")                    # {"eng": 2, "sales": 1}  
sum_by(users, "dept", lambda x: x["salary"]) # {"eng": 175000, "sales": 70000}
index_by(users, "id")                      # {1: {...}, 2: {...}, 3: {...}}
```

## Real-World Examples

### Sales Data Analysis
```python
from dictutils import qsdict, nest_agg, Agg

# Convert query results to nested structure
sales = [
    {"region": "North", "product": "Widget", "revenue": 1000, "units": 50},
    {"region": "North", "product": "Gadget", "revenue": 1500, "units": 30},
    {"region": "South", "product": "Widget", "revenue": 800, "units": 40},
]

# Group by region -> product, show revenue
by_region = qsdict(sales, "region", "product", "revenue")
# {"North": {"Widget": 1000, "Gadget": 1500}, "South": {"Widget": 800}}

# Calculate metrics with aggregation
aggs = {
    "total_revenue": Agg(map=lambda x: x["revenue"], zero=0),
    "avg_price": Agg(
        map=lambda x: (x["revenue"], x["units"]),
        zero=(0, 0), 
        reduce=lambda a, b: (a[0] + b[0], a[1] + b[1]),
        finalize=lambda x: x[0] / x[1] if x[1] > 0 else 0
    )
}
metrics = nest_agg(sales, keys=["region"], aggs=aggs)
# {"North": {"total_revenue": 2500, "avg_price": 31.25}, ...}
```

### Configuration Management
```python
from dictutils import mergedict
from dictutils.ops import deep_get, deep_set

# Merge multiple config sources
default_config = {"db": {"host": "localhost", "port": 5432}}
user_config = {"db": {"password": "secret"}, "cache": {"ttl": 300}}
env_config = {"db": {"host": "prod-db.example.com"}}

config = mergedict({}, default_config, user_config, env_config)
# Result: {"db": {"host": "prod-db.example.com", "port": 5432, "password": "secret"}, "cache": {"ttl": 300}}

# Access nested values safely
db_host = deep_get(config, "db.host", default="localhost")
deep_set(config, "logging.level", "INFO")  # Creates nested structure
```

## Documentation

📖 **[Complete Documentation](https://dictutils.readthedocs.io/en/latest/)** - API reference, cookbook, and examples

- **[Quickstart Guide](https://dictutils.readthedocs.io/en/latest/quickstart.html)** - Get up and running quickly
- **[API Reference](https://dictutils.readthedocs.io/en/latest/api_reference.html)** - Complete function documentation  
- **[Cookbook](https://dictutils.readthedocs.io/en/latest/cookbook.html)** - Real-world examples and patterns
- **[Advanced Operations](https://dictutils.readthedocs.io/en/latest/ops.html)** - dictutils.ops module guide

## Development

- Install dev tools: `pip install .[test,typecheck,lint]`
- Run tests: `pytest`
- Type check: `mypy dictutils`
- Lint: `ruff dictutils`
- Format: `black dictutils`
- Upgrade syntax: `pyupgrade --py39-plus <file.py>`
- Pre-commit: `pre-commit install` (then `git commit` auto-runs checks)

## Contributing

Contributions are welcome! See our [documentation](https://dictutils.readthedocs.io/) for development setup and coding standards.

## Migration from 0.1.x

This is a major release with breaking changes. See [CHANGELOG.md](CHANGELOG.md) for detailed migration guidance.

## License

MIT License. Copyright (c) 2020–2025 Adi Eyal.
