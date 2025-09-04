# dictutils

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
```

#### Example
```python
from dictutils import nest_agg, Agg
items = [
    {"cat": "A", "val": 1},
    {"cat": "A", "val": 2},
    {"cat": "B", "val": 3},
]
aggs = {"total": Agg(map=lambda it: it["val"], zero=0)}
tree = nest_agg(items, keys=["cat"], aggs=aggs, include_rows=True)
# {'A': {'total': 3, 'rows': [...]}, 'B': {'total': 3, 'rows': [...]}}
```

## Development

- Install dev tools: `pip install .[test,typecheck]`
- Run tests: `pytest`
- Type check: `mypy dictutils`
- Lint: `ruff dictutils`
- Format: `black dictutils`
- Upgrade syntax: `pyupgrade --py39-plus <file.py>`
- Pre-commit: `pre-commit install` (then `git commit` auto-runs checks)

## Continuous Integration

- See `.github/workflows/ci.yml` for GitHub Actions workflow (pytest, mypy, ruff).

## Migration Note

This project uses [PEP 621](https://www.python.org/dev/peps/pep-0621/) and [pyproject.toml](https://packaging.python.org/en/latest/specifications/pyproject-toml/) for all build and packaging configuration. Legacy `setup.py`/`setup.cfg` are no longer used.

## License

MIT License. Copyright (c) 2020–2025 Adi Eyal.
