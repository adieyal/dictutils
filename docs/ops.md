# Advanced Operations (`dictutils.ops`)

The ops module provides 20+ advanced utilities for dictionary manipulation, path operations, and data transformation.

:::{seealso}
📚 **Want to contribute new operations?** Check the [contribution guide](https://github.com/adieyal/dictutils/blob/master/README.md#contributing) on GitHub.
:::

## Path operations

```python
from dictutils.ops import deep_get, deep_set, deep_del, deep_has

d = {"a": {"b": [{"c": 1}]}}
deep_get(d, "a.b[0].c")       # 1
deep_has(d, "a.b[1].c")       # False
deep_set(d, "a.b[1].c", 2)    # auto-creates
deep_del(d, "a.b[0].c")
```

## Flatten & expand

```python
from dictutils.ops import flatten_paths, expand_paths, project, rename_keys, transpose_dict
flatten_paths({"a": {"b": 1}})       # {'a.b': 1}
expand_paths({"a.b": 1})             # {'a': {'b': 1}}
project({"a": {"b": 1}, "x": 2}, ["a.b"])  # {'a': {'b': 1}}
rename_keys({"a": {"b": 1}}, {"a.b": "alpha.beta"})  # {'alpha': {'beta': 1}}
transpose_dict({"A":{"X":1,"Y":2}, "B":{"X":3,"Y":4}})  # {'X': {'A': 1, 'B': 3}, 'Y': {'A': 2, 'B': 4}}
```

## Updates & diffs

```python
from dictutils.ops import deep_update, deep_diff
a = {"users":[{"id":1,"n": "A"}]}
b = {"users":[{"id":1,"n": "Alice"}, {"id":2,"n":"Bob"}]}
deep_update(a, b, list_strategy="by_key", by_key="id")
added, removed, changed, same = deep_diff({"x":1}, {"x":2,"y":3})
```

## Grouping & aggregation helpers

```python
from dictutils.ops import index_by, group_by, count_by, sum_by, reduce_by, rollup_tree

users = [{"id": 1, "name": "Alice", "dept": "eng"}, {"id": 2, "name": "Bob", "dept": "eng"}]
index_by(users, "id")           # {1: {"id": 1, "name": "Alice", "dept": "eng"}, 2: {...}}
group_by(users, "dept")         # {"eng": [{"id": 1, ...}, {"id": 2, ...}]}
count_by(users, "dept")         # {"eng": 2}
sum_by(users, "dept", lambda x: x["id"])  # {"eng": 3}

tree = {"total": 0, "region1": {"total": 0, "city1": {"total": 10}}}
rollup_tree(tree, {"total": lambda a, b: (a or 0) + (b or 0)})
```

## Transform & clean

```python
from dictutils.ops import map_keys, map_values, map_items, schema_check, coalesce_paths, prune

d = {"first_name": "Alice", "last_name": "Smith", "age": 30}
map_keys(d, str.upper)          # {"FIRST_NAME": "Alice", "LAST_NAME": "Smith", "AGE": 30}
map_values(d, lambda x: str(x) if isinstance(x, int) else x)  # convert numbers to strings
map_items(d, lambda k, v: (k.replace("_", "-"), v))  # {"first-name": "Alice", ...}

schema_check({"user": {"name": "Alice", "age": 30}}, {"user": {"name": str, "age": int}})  # []
coalesce_paths({"b": 2}, ["a", "b", "c"])  # 2 (first existing value)
prune({"a": 1, "b": None, "c": {}})  # {"a": 1} (removes empty values)
```

## Lists & patching

```python
from dictutils.ops import merge_lists_by, patch

a = [{"id": 1, "name": "Alice"}]
b = [{"id": 1, "name": "Alice Smith"}, {"id": 2, "name": "Bob"}]
merge_lists_by(a, b, key="id")  # merges by id, updates Alice's name, adds Bob

d = {"a": 1}
ops = [{"op": "add", "path": "b", "value": 2}, {"op": "replace", "path": "a", "value": 42}]
patch(d, ops)  # {"a": 42, "b": 2}
```

## Query-ish

```python
from dictutils.ops import where, match, distinct_by

items = [{"name": "Alice", "age": 30, "active": True}, {"name": "Bob", "age": 25, "active": False}]
where(items, lambda x: x["age"] > 25)  # [{"name": "Alice", "age": 30, "active": True}]
match(items, active=True)              # [{"name": "Alice", "age": 30, "active": True}]
distinct_by(items, "active")           # [{"name": "Alice", ...}, {"name": "Bob", ...}]
```

## Path guarantees

```python
from dictutils.ops import ensure_path as ensure

d = {}
container = ensure(d, "user.profile.settings")  # creates nested structure
# d is now {"user": {"profile": {"settings": {}}}}
# container points to the inner {} for direct manipulation
```