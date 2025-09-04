# Core Functions

This section covers the main functions provided by dictutils in detail.

## qsdict - Query Selector Dictionary

**When to use:** Converting flat data (CSV rows, API responses) into nested dictionaries for reporting or quick crosstabs.

`qsdict` builds nested dictionaries from flat data by following a sequence of selectors.

### Signature

```python
def qsdict(
    qs: Iterable[Union[Mapping, object]], 
    *args, 
    strict: bool = False
) -> dict
```

### Parameters

- `qs`: Iterable of dictionaries or objects to process
- `*args`: Sequence of selectors (strings, integers, or callable functions)
- `strict`: If True, raises errors for missing keys/attributes

### Selectors

Selectors can be:

1. **String keys**: Access dictionary keys or object attributes
2. **Integer keys**: Access dictionary keys (useful for numeric keys)
3. **Callable functions**: Custom extraction logic

### Examples

#### Basic usage

```python
from dictutils import qsdict
import json

data = [
    {"category": "food", "item": "apple", "price": 1.20},
    {"category": "food", "item": "bread", "price": 2.50},
    {"category": "drink", "item": "water", "price": 0.80},
]

# Basic nesting
nested = qsdict(data, "category", "item", "price")
print(json.dumps(nested, indent=4))
# Output:
# {
#     "drink": {
#         "water": 0.8
#     },
#     "food": {
#         "apple": 1.2,
#         "bread": 2.5
#     }
# }
```

#### Using callable selectors

```python
import json

# Custom extraction function
def price_tier(item):
    return "expensive" if item["price"] > 2.0 else "cheap"

tiered = qsdict(data, price_tier, "item", "price")
print(json.dumps(tiered, indent=4))
# Output:
# {
#     "cheap": {
#         "apple": 1.2,
#         "water": 0.8
#     },
#     "expensive": {
#         "bread": 2.5
#     }
# }
```

#### Strict mode

```python
import json

incomplete_data = [{"a": 1}, {"b": 2}]  # Missing keys

# Non-strict (default): missing keys become None
result = qsdict(incomplete_data, "a", "b")
print(json.dumps(result, indent=4))
# Output:
# {
#     "1": {
#         "null": null
#     },
#     "null": {
#         "2": 2
#     }
# }

# Strict mode: raises KeyError
try:
    qsdict(incomplete_data, "a", "b", strict=True)
except KeyError as e:
    print(f"Error: {e}")
```

## mergedict - Deep Dictionary Merging

**When to use:** Combining configuration files, merging API responses, or overlaying defaults with user settings.

`mergedict` recursively merges multiple nested dictionaries.

### Signature

```python
def mergedict(*args, path=None, update: bool = True) -> dict
```

### Parameters

- `*args`: Dictionaries to merge (first one is modified in-place)
- `path`: Internal parameter for error tracking
- `update`: If True, later values override earlier ones

### Behavior

- First argument is modified in-place and returned
- Nested dictionaries are recursively merged
- Non-dict values are overwritten (when `update=True`)

### Examples

#### Basic merging

```python
from dictutils import mergedict
import json

base = {"a": {"x": 1, "y": 2}, "b": 3}
override = {"a": {"y": 20, "z": 30}, "c": 4}

result = mergedict(base, override)
print(json.dumps(base, indent=4))  # Modified in-place
# Output:
# {
#     "a": {
#         "x": 1,
#         "y": 20,
#         "z": 30
#     },
#     "b": 3,
#     "c": 4
# }
```

#### Multiple dictionaries

```python
import json

d1 = {"level1": {"level2": {"a": 1}}}
d2 = {"level1": {"level2": {"b": 2}}}
d3 = {"level1": {"level2": {"c": 3}}}

merged = mergedict(d1, d2, d3)
print(json.dumps(d1, indent=4))  # d1 is modified in-place
# Output:
# {
#     "level1": {
#         "level2": {
#             "a": 1,
#             "b": 2,
#             "c": 3
#         }
#     }
# }
```

## pivot - Dictionary Pivoting

**When to use:** Reshaping data dimensions for analysis, switching from time-series to metric-focused views, or preparing data for different reporting formats.

`pivot` reorders the levels of a nested dictionary structure.

### Signature

```python
def pivot(d: dict, order: list[int]) -> dict
```

### Parameters

- `d`: Dictionary to pivot
- `order`: List of indices specifying the new order of key levels

### Process

1. Flattens the dictionary to arrays of [key1, key2, ..., value]
2. Rearranges keys according to `order`
3. Rebuilds the nested structure

### Examples

#### Basic pivoting

```python
from dictutils import pivot
import json

# Original: country -> city -> population
data = {
    "USA": {"NYC": 8000000, "LA": 4000000},
    "UK": {"London": 9000000, "Manchester": 500000}
}

# Pivot to: city -> country -> population
pivoted = pivot(data, [1, 0])
print(json.dumps(pivoted, indent=4))
# Output:
# {
#     "LA": {
#         "USA": 4000000
#     },
#     "London": {
#         "UK": 9000000
#     },
#     "Manchester": {
#         "UK": 500000
#     },
#     "NYC": {
#         "USA": 8000000
#     }
# }
```

#### Three-level pivoting

```python
import json

# Original: year -> quarter -> metric -> value
data = {
    "2023": {
        "Q1": {"revenue": 100, "profit": 20},
        "Q2": {"revenue": 110, "profit": 25}
    }
}

# Pivot to: metric -> year -> quarter -> value
pivoted = pivot(data, [2, 0, 1])
print(json.dumps(pivoted, indent=4))
# Output:
# {
#     "profit": {
#         "2023": {
#             "Q1": 20,
#             "Q2": 25
#         }
#     },
#     "revenue": {
#         "2023": {
#             "Q1": 100,
#             "Q2": 110
#         }
#     }
# }
```

## nestagg - Nested Aggregation

**When to use:** Building summary reports from transaction data, calculating grouped statistics, or creating multi-dimensional analytics from flat records.

`nest_agg` groups data by keys and applies aggregation functions at the leaf level.

### Signatures

```python
def nest_agg(
    items: list[Any],
    keys: list[str | Callable[[Any], Any]],
    *,
    aggs: dict[str, Agg],
    include_rows: bool = False,
    rows_key: str = "rows",
) -> dict

@dataclass(frozen=True)
class Agg:
    map: Callable[[Any], Any]
    zero: Any = None
    reduce: Callable[[Any, Any], Any] = operator.add
    skip_none: bool = True
    finalize: Optional[Callable[[Any], Any]] = None
```

### Parameters

- `items`: List of items to group and aggregate
- `keys`: List of grouping keys (strings or functions)
- `aggs`: Dictionary of aggregation specifications
- `include_rows`: If True, include original rows in results
- `rows_key`: Key name for storing original rows

### Agg Parameters

- `map`: Function to extract value from each item
- `zero`: Initial value (or callable returning initial value)
- `reduce`: Function to combine values (default: addition)
- `skip_none`: Skip None values from mapping
- `finalize`: Optional post-processing function

### Examples

#### Basic aggregation

```python
from dictutils import nest_agg, Agg
import operator
import json

sales = [
    {"region": "North", "product": "A", "amount": 100, "quantity": 5},
    {"region": "North", "product": "A", "amount": 50, "quantity": 2},
    {"region": "North", "product": "B", "amount": 200, "quantity": 10},
    {"region": "South", "product": "A", "amount": 150, "quantity": 8},
]

aggs = {
    "total_amount": Agg(map=lambda x: x["amount"], zero=0),
    "total_quantity": Agg(map=lambda x: x["quantity"], zero=0),
    "count": Agg(map=lambda x: 1, zero=0),
}

result = nest_agg(sales, ["region", "product"], aggs=aggs)
print(json.dumps(result, indent=4))
# Output:
# {
#     "North": {
#         "A": {
#             "count": 2,
#             "total_amount": 150,
#             "total_quantity": 7
#         },
#         "B": {
#             "count": 1,
#             "total_amount": 200,
#             "total_quantity": 10
#         }
#     },
#     "South": {
#         "A": {
#             "count": 1,
#             "total_amount": 150,
#             "total_quantity": 8
#         }
#     }
# }
```

#### Advanced aggregations

```python
import json

# Calculate averages using finalize
aggs = {
    "avg_price": Agg(
        map=lambda x: (x["amount"], x["quantity"]),
        zero=(0, 0),
        reduce=lambda a, b: (a[0] + b[0], a[1] + b[1]),
        finalize=lambda x: round(x[0] / x[1], 2) if x[1] > 0 else 0
    ),
    "max_amount": Agg(
        map=lambda x: x["amount"],
        reduce=max
    ),
}

result = nest_agg(sales, ["region"], aggs=aggs)
print(json.dumps(result, indent=4))
# Output:
# {
#     "North": {
#         "avg_price": 0.43,
#         "max_amount": 200
#     },
#     "South": {
#         "avg_price": 0.05,
#         "max_amount": 150
#     }
# }
```

#### Including original rows

```python
import json

result = nest_agg(
    sales, 
    ["region"], 
    aggs={"total": Agg(map=lambda x: x["amount"], zero=0)},
    include_rows=True
)
print(json.dumps(result, indent=4, default=str))
# Output:
# {
#     "North": {
#         "rows": [
#             {"region": "North", "product": "A", "amount": 100, "quantity": 5},
#             {"region": "North", "product": "A", "amount": 50, "quantity": 2},
#             {"region": "North", "product": "B", "amount": 200, "quantity": 10}
#         ],
#         "total": 350
#     },
#     "South": {
#         "rows": [
#             {"region": "South", "product": "A", "amount": 150, "quantity": 8}
#         ],
#         "total": 150
#     }
# }
```