# dictutils/ops.py
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Callable, Union

Path = Union[str, Sequence[Union[str, int]]]
Reducer = Callable[[Any, Any], Any]

# ------------- path parsing / access primitives -------------


def _is_mapping(x: Any) -> bool:
    return isinstance(x, Mapping)


def _get_attr(obj: Any, key: str, *, default: Any = None, strict: bool = False) -> Any:
    if _is_mapping(obj):
        if key in obj:
            return obj[key]
        if strict:
            raise KeyError(key)
        return default
    # dataclass, object
    if hasattr(obj, key):
        return getattr(obj, key)
    # allow attribute-like access on objects that expose __getitem__
    if not strict:
        return default
    raise AttributeError(key)


def _set_attr(
    obj: Any, key: str, value: Any, *, create_mapping: Callable[[], Any]
) -> None:
    if _is_mapping(obj):
        obj[key] = value
        return
    # if object, try setattr
    try:
        setattr(obj, key, value)
    except Exception:
        # fallback: if it looks like a mapping-like thing, try __setitem__
        if hasattr(obj, "__setitem__"):
            obj[key] = value
        else:
            raise


def _del_attr(obj: Any, key: str) -> None:
    if _is_mapping(obj):
        del obj[key]
        return
    if hasattr(obj, key):
        delattr(obj, key)
        return
    if hasattr(obj, "__delitem__"):
        del obj[key]
        return
    raise KeyError(key)


def _is_int(s: str) -> bool:
    return s.isdigit() or (s.startswith("-") and s[1:].isdigit())


def _parse_path(path: Path) -> list[str | int]:
    """
    Parse 'a.b[0].c' or ['a','b',0,'c'] into ['a','b',0,'c'].
    """
    if isinstance(path, (list, tuple)):
        return list(path)

    s = str(path)
    out: list[str | int] = []
    buf: list[str] = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == ".":
            if buf:
                tok = "".join(buf)
                out.append(int(tok) if _is_int(tok) else tok)
                buf = []
            i += 1
        elif ch == "[":
            # flush current
            if buf:
                tok = "".join(buf)
                out.append(int(tok) if _is_int(tok) else tok)
                buf = []
            j = s.find("]", i + 1)
            if j == -1:
                raise ValueError(f"Unmatched '[' in path: {s}")
            idx = s[i + 1 : j]
            out.append(int(idx) if _is_int(idx) else idx)
            i = j + 1
        else:
            buf.append(ch)
            i += 1
    if buf:
        tok = "".join(buf)
        out.append(int(tok) if _is_int(tok) else tok)
    return out


def _ensure_container(
    parent: Any, key: str | int, *, create_mapping: Callable[[], Any]
) -> Any:
    """
    Ensure parent[key] exists and is a mapping when key is str,
    or a list when key is int. Returns the child container.
    """
    if isinstance(key, int):
        # list access
        if parent is None:
            raise TypeError("Cannot index None with int")
        if isinstance(parent, list):
            # extend list
            while len(parent) <= key if key >= 0 else False:
                parent.append(None)
            if key < 0:
                raise IndexError("negative indices not supported for creation")
            if parent[key] is None:
                parent[key] = create_mapping()
            return parent[key]
        # auto-create list if mapping slot is missing
        if _is_mapping(parent):
            lst: list[Any] = []
            parent[str(key)] = lst  # store under stringified index to avoid collisions
            while len(lst) <= key:
                lst.append(None)
            lst[key] = create_mapping()
            return lst[key]
        raise TypeError(f"Cannot ensure list on parent type {type(parent)}")

    # string key -> mapping-like
    if parent is None:
        raise TypeError("Cannot set on None")
    if _is_mapping(parent):
        if key not in parent or parent[key] is None:
            parent[key] = create_mapping()
        return parent[key]
    # object
    cur = getattr(parent, key, None)
    if cur is None:
        cur = create_mapping()
        _set_attr(parent, key, cur, create_mapping=create_mapping)
    return cur


# ------------- deep_get / set / del / has -------------


def deep_get(obj: Any, path: Path, default: Any = None, *, strict: bool = False) -> Any:
    """
    Get value from nested object using dotted path notation or path sequence.

    Args:
        obj: The object to access
        path: Path as string ("a.b.c", "a[0].b") or sequence ["a", "b", 0]
        default: Value to return if path not found (when strict=False)
        strict: If True, raise exception when path not found

    Returns:
        Value at the specified path, or default if not found

    Example:
        >>> import json
        >>> data = {"user": {"profile": {"name": "Alice", "tags": ["admin", "user"]}}}
        >>> result = deep_get(data, "user.profile.name")
        >>> print(json.dumps(result, indent=4))
        "Alice"

        >>> result = deep_get(data, ["user", "profile", "tags", 0])
        >>> print(json.dumps(result, indent=4))
        "admin"

        >>> result = deep_get(data, "user.profile.age", default="unknown")
        >>> print(json.dumps(result, indent=4))
        "unknown"
    """
    parts = _parse_path(path)
    cur = obj
    for p in parts:
        if isinstance(p, int):
            if isinstance(cur, list) and 0 <= p < len(cur):
                cur = cur[p]
            elif _is_mapping(cur) and str(p) in cur:
                cur = cur[str(p)]
            else:
                if strict:
                    raise KeyError(p)
                return default
        else:
            cur = _get_attr(cur, p, default=default, strict=strict)
            if cur is default and not strict:
                return default
    return cur


def deep_has(obj: Any, path: Path) -> bool:
    """
    Check if a path exists in nested object.

    Args:
        obj: The object to check
        path: Path as string ("a.b.c") or sequence ["a", "b", "c"]

    Returns:
        True if path exists, False otherwise

    Example:
        >>> import json
        >>> data = {"user": {"profile": {"name": "Alice"}}}
        >>> result = deep_has(data, "user.profile.name")
        >>> print(json.dumps(result, indent=4))
        true

        >>> result = deep_has(data, "user.profile.age")
        >>> print(json.dumps(result, indent=4))
        false
    """
    try:
        sentinel = object()
        return deep_get(obj, path, default=sentinel, strict=True) is not sentinel
    except Exception:
        return False


def deep_set(
    obj: Any,
    path: Path,
    value: Any,
    *,
    create_missing: bool = True,
    create_mapping: Callable[[], Any] = dict,
) -> Any:
    """
    Set value in nested object using dotted path notation.

    Args:
        obj: The object to modify
        path: Path as string ("a.b.c") or sequence ["a", "b", "c"]
        value: Value to set at the path
        create_missing: Whether to create missing intermediate paths
        create_mapping: Factory function for creating new mappings

    Returns:
        The modified object

    Example:
        >>> import json
        >>> data = {}
        >>> deep_set(data, "user.profile.name", "Alice")
        >>> print(json.dumps(data, indent=4))
        {
            "user": {
                "profile": {
                    "name": "Alice"
                }
            }
        }

        >>> deep_set(data, "user.profile.tags[0]", "admin")
        >>> print(json.dumps(data, indent=4))
        {
            "user": {
                "profile": {
                    "name": "Alice",
                    "tags": [
                        "admin"
                    ]
                }
            }
        }
    """
    parts = _parse_path(path)
    if not parts:
        return obj
    cur = obj
    for i, p in enumerate(parts[:-1]):
        nxt = parts[i + 1]
        # navigate or create
        if isinstance(p, int):
            if not isinstance(cur, list):
                if not create_missing:
                    raise TypeError(f"Expected list at segment {p}")
                # create list in a mapping slot
                raise TypeError(
                    "Cannot auto-create a list container at numeric segment without parent setter"
                )
            # ensure index exists
            while len(cur) <= p:
                cur.append(None)
            if cur[p] is None:
                cur[p] = (
                    dict()
                    if isinstance(nxt, (str,))
                    else ([] if isinstance(nxt, int) else dict())
                )
            cur = cur[p]
        elif create_missing:
            cur = _ensure_container(cur, p, create_mapping=create_mapping)
        else:
            cur = _get_attr(cur, p, strict=True)
    # set leaf
    last = parts[-1]
    if isinstance(last, int):
        if not isinstance(cur, list):
            if create_missing and _is_mapping(cur):
                # store list at stringified index
                lst: list[Any] = []
                cur[str(last)] = lst
                while len(lst) <= last:
                    lst.append(None)
                lst[last] = value
                return obj
            raise TypeError("Expected list at final segment")
        while len(cur) <= last:
            cur.append(None)
        cur[last] = value
        return obj
    # string key
    if _is_mapping(cur):
        cur[last] = value
    else:
        _set_attr(cur, last, value, create_mapping=create_mapping)
    return obj


def deep_del(obj: Any, path: Path) -> Any:
    """
    Delete value from nested object using dotted path notation.

    Args:
        obj: The object to modify
        path: Path as string ("a.b.c") or sequence ["a", "b", "c"]

    Returns:
        The modified object

    Example:
        >>> import json
        >>> data = {"user": {"profile": {"name": "Alice", "age": 30}}}
        >>> deep_del(data, "user.profile.age")
        >>> print(json.dumps(data, indent=4))
        {
            "user": {
                "profile": {
                    "name": "Alice"
                }
            }
        }
    """
    parts = _parse_path(path)
    if not parts:
        return obj
    parent = deep_get(obj, parts[:-1], strict=True)
    last = parts[-1]
    if isinstance(last, int):
        if not isinstance(parent, list) or not (0 <= last < len(parent)):
            raise KeyError(last)
        del parent[last]
    else:
        _del_attr(parent, last)
    return obj


# ------------- deep_update / deep_diff -------------


def deep_update(
    a: Any,
    b: Any,
    *,
    dict_strategy: str = "merge",  # "merge" | "replace"
    list_strategy: str = "extend",  # "extend" | "replace" | "unique" | "by_key"
    unique_by: Callable[[Any], Any] | None = None,
    by_key: str | Callable[[Any], Any] | None = None,
    scalar_strategy: str = "replace",  # "replace" | "keep_first" | "keep_last"
) -> Any:
    """
    Strategy-aware deep update of object a with values from object b.

    Args:
        a: Target object to update
        b: Source object to merge from
        dict_strategy: How to handle dict merging ("merge" or "replace")
        list_strategy: How to handle list merging ("extend", "replace", "unique", "by_key")
        unique_by: Function to extract unique key for "unique" strategy
        by_key: Key or function for "by_key" strategy
        scalar_strategy: How to handle scalar conflicts ("replace", "keep_first", "keep_last")

    Returns:
        The updated object a

    Example:
        >>> import json
        >>> data1 = {"users": [{"id": 1, "name": "Alice"}], "config": {"debug": True}}
        >>> data2 = {"users": [{"id": 2, "name": "Bob"}], "config": {"port": 8080}}
        >>> deep_update(data1, data2)
        >>> print(json.dumps(data1, indent=4))
        {
            "users": [
                {
                    "id": 1,
                    "name": "Alice"
                },
                {
                    "id": 2,
                    "name": "Bob"
                }
            ],
            "config": {
                "debug": true,
                "port": 8080
            }
        }
    """
    if a is None:
        return b
    if b is None:
        return a

    # dict vs dict
    if _is_mapping(a) and _is_mapping(b):
        if dict_strategy == "replace":
            a.clear()
            a.update(b)
            return a
        # merge
        for k, vb in b.items():
            if k in a:
                a[k] = deep_update(
                    a[k],
                    vb,
                    dict_strategy=dict_strategy,
                    list_strategy=list_strategy,
                    unique_by=unique_by,
                    by_key=by_key,
                    scalar_strategy=scalar_strategy,
                )
            else:
                a[k] = vb
        return a

    # list vs list
    if isinstance(a, list) and isinstance(b, list):
        if list_strategy == "replace":
            a[:] = b
            return a
        if list_strategy == "extend":
            a.extend(b)
            return a
        if list_strategy == "unique":
            key = unique_by or (lambda x: x)
            seen = {key(x) for x in a}
            for x in b:
                kx = key(x)
                if kx not in seen:
                    a.append(x)
                    seen.add(kx)
            return a
        if list_strategy == "by_key":
            if by_key is None:
                raise ValueError("by_key is required for list_strategy='by_key'")
            getk = (lambda x: x.get(by_key)) if isinstance(by_key, str) else by_key
            idx = {getk(x): i for i, x in enumerate(a)}
            for el in b:
                k = getk(el)
                if (
                    k in idx
                    and isinstance(a[idx[k]], Mapping)
                    and isinstance(el, Mapping)
                ):
                    a[idx[k]] = deep_update(
                        a[idx[k]],
                        el,
                        dict_strategy=dict_strategy,
                        list_strategy=list_strategy,
                        unique_by=unique_by,
                        by_key=by_key,
                        scalar_strategy=scalar_strategy,
                    )
                else:
                    a.append(el)
            return a

    # scalars / mismatched types
    if scalar_strategy in ("replace", "keep_last"):
        return b
    if scalar_strategy == "keep_first":
        return a
    return b


def deep_diff(a: Any, b: Any) -> tuple[Any, Any, Any, Any]:
    """
    Compare two nested structures and return differences.

    Args:
        a: First object to compare
        b: Second object to compare

    Returns:
        Tuple of (added, removed, changed, same) where each mirrors the input structure

    Example:
        >>> import json
        >>> data1 = {"user": {"name": "Alice", "age": 30}, "active": True}
        >>> data2 = {"user": {"name": "Alice", "age": 31}, "role": "admin"}
        >>> added, removed, changed, same = deep_diff(data1, data2)
        >>> print(json.dumps({"added": added, "removed": removed, "changed": changed}, indent=4))
        {
            "added": {
                "role": "admin"
            },
            "removed": {
                "active": true
            },
            "changed": {
                "user": {
                    "changed": {
                        "age": {
                            "from": 30,
                            "to": 31
                        }
                    },
                    "same": {
                        "name": "Alice"
                    }
                }
            }
        }
    """
    if _is_mapping(a) and _is_mapping(b):
        akeys = set(a.keys())
        bkeys = set(b.keys())
        added = {k: b[k] for k in bkeys - akeys}
        removed = {k: a[k] for k in akeys - bkeys}
        changed: dict[str, Any] = {}
        same: dict[str, Any] = {}
        for k in akeys & bkeys:
            sub = deep_diff(a[k], b[k])
            if any(x not in ({}, []) and x is not None for x in sub[:3]):
                # something changed beneath
                added_k, removed_k, changed_k, same_k = sub
                node: dict[str, Any] = {}
                if added_k not in ({}, []) and added_k is not None:
                    node["added"] = added_k
                if removed_k not in ({}, []) and removed_k is not None:
                    node["removed"] = removed_k
                if changed_k not in ({}, []) and changed_k is not None:
                    node["changed"] = changed_k
                if same_k not in ({}, []) and same_k is not None:
                    node["same"] = same_k
                changed[k] = node
            elif a[k] == b[k]:
                same[k] = a[k]
            else:
                changed[k] = {"from": a[k], "to": b[k]}
        return (added, removed, changed, same)

    if isinstance(a, list) and isinstance(b, list):
        # simple list diff (by position)
        maxlen = max(len(a), len(b))
        added_list: list[Any] = []
        removed_list: list[Any] = []
        changed_list: list[dict[str, Any]] = []
        same_list: list[Any] = []
        for i in range(maxlen):
            if i >= len(a):
                added_list.append(b[i])
                continue
            if i >= len(b):
                removed_list.append(a[i])
                continue
            if a[i] == b[i]:
                same_list.append(a[i])
            else:
                changed_list.append({"from": a[i], "to": b[i]})
        return (added_list, removed_list, changed_list, same_list)

    # scalars
    if a == b:
        return ({}, {}, {}, a)
    return (b, a, {"from": a, "to": b}, {})


# ------------- flatten/expand/select/rename/transpose -------------


def flatten_paths(d: Any, prefix: str = "", sep: str = ".") -> dict[str, Any]:
    """
    Flatten nested mappings into dot-notation paths.

    Args:
        d: Object to flatten
        prefix: Prefix for all paths
        sep: Separator for path components

    Returns:
        Dictionary with flattened paths as keys

    Example:
        >>> import json
        >>> data = {"user": {"profile": {"name": "Alice", "tags": ["admin", "user"]}}}
        >>> result = flatten_paths(data)
        >>> print(json.dumps(result, indent=4))
        {
            "user.profile.name": "Alice",
            "user.profile.tags[0]": "admin",
            "user.profile.tags[1]": "user"
        }
    """
    out: dict[str, Any] = {}

    def _walk(x: Any, cur: str) -> None:
        if _is_mapping(x):
            for k, v in x.items():
                key = f"{cur}{sep}{k}" if cur else str(k)
                _walk(v, key)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                key = f"{cur}[{i}]"
                _walk(v, key)
        else:
            out[cur] = x

    _walk(d, prefix or "")
    return out


def expand_paths(path: str | Sequence[str | int]) -> list[str | int]:
    """
    Parse dotted path string into list of keys.

    Args:
        path: Dotted path string or sequence

    Returns:
        List of path components

    Examples:
        >>> expand_paths("a.b.c")
        ['a', 'b', 'c']
        >>> expand_paths("users.0.name")
        ['users', 0, 'name']
    """
    if isinstance(path, (list, tuple)):
        return list(path)

    s = str(path)
    out: list[str | int] = []
    buf: list[str] = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == ".":
            if buf:
                tok = "".join(buf)
                out.append(int(tok) if _is_int(tok) else tok)
                buf = []
            i += 1
        elif ch == "[":
            # flush current
            if buf:
                tok = "".join(buf)
                out.append(int(tok) if _is_int(tok) else tok)
                buf = []
            j = s.find("]", i + 1)
            if j == -1:
                raise ValueError(f"Unmatched '[' in path: {s}")
            idx = s[i + 1 : j]
            out.append(int(idx) if _is_int(idx) else idx)
            i = j + 1
        else:
            buf.append(ch)
            i += 1
    if buf:
        tok = "".join(buf)
        out.append(int(tok) if _is_int(tok) else tok)
    return out


def project(d: Any, paths: Iterable[Path]) -> dict[str, Any]:
    """
    Extract only specified paths from nested object.

    Args:
        d: Source object to project from
        paths: Paths to extract

    Returns:
        New object containing only the specified paths

    Example:
        >>> import json
        >>> data = {"user": {"name": "Alice", "age": 30, "email": "alice@example.com"}}
        >>> result = project(data, ["user.name", "user.email"])
        >>> print(json.dumps(result, indent=4))
        {
            "user": {
                "name": "Alice",
                "email": "alice@example.com"
            }
        }
    """
    out: dict[str, Any] = {}
    for p in paths:
        val = deep_get(d, p, default=None, strict=False)
        deep_set(out, p, val)
    return out


def rename_keys(d: Any, mapping: Mapping[str, str]) -> Any:
    """
    Rename keys using path mapping.

    Args:
        d: Object to modify
        mapping: Dictionary mapping old paths to new paths

    Returns:
        The modified object

    Example:
        >>> import json
        >>> data = {"user": {"firstName": "Alice", "lastName": "Smith"}}
        >>> rename_keys(data, {
        ...     "user.firstName": "user.name.first",
        ...     "user.lastName": "user.name.last"
        ... })
        >>> print(json.dumps(data, indent=4))
        {
            "user": {
                "name": {
                    "first": "Alice",
                    "last": "Smith"
                }
            }
        }
    """
    for old, new in mapping.items():
        if deep_has(d, old):
            val = deep_get(d, old)
            deep_del(d, old)
            deep_set(d, new, val)
    return d


def transpose_dict(d: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Transpose a 2D dictionary (swap row/column keys).

    Args:
        d: Dictionary of dictionaries to transpose

    Returns:
        Transposed dictionary

    Example:
        >>> import json
        >>> data = {"row1": {"col1": "A", "col2": "B"}, "row2": {"col1": "C", "col2": "D"}}
        >>> result = transpose_dict(data)
        >>> print(json.dumps(result, indent=4))
        {
            "col1": {
                "row1": "A",
                "row2": "C"
            },
            "col2": {
                "row1": "B",
                "row2": "D"
            }
        }
    """
    out: dict[str, dict[str, Any]] = {}
    for rkey, inner in d.items():
        for ckey, val in inner.items():
            out.setdefault(ckey, {})[rkey] = val
    return out


# ------------- indexing / grouping / reductions -------------


def index_by(items: Iterable[Any], key: str | Callable[[Any], Any]) -> dict[Any, Any]:
    """
    Create dictionary indexed by key function or path.

    Args:
        items: Collection to index
        key: Path string or function to extract index key

    Returns:
        Dictionary mapping keys to items

    Example:
        >>> import json
        >>> users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        >>> result = index_by(users, "id")
        >>> print(json.dumps(result, indent=4))
        {
            "1": {
                "id": 1,
                "name": "Alice"
            },
            "2": {
                "id": 2,
                "name": "Bob"
            }
        }
    """

    def getk(x):
        return deep_get(x, key) if isinstance(key, str) else key(x)

    out: dict[Any, Any] = {}
    for it in items:
        out[getk(it)] = it
    return out


def group_by(
    items: Iterable[Any], key: str | Callable[[Any], Any]
) -> dict[Any, list[Any]]:
    """
    Group items by key function or path.

    Args:
        items: Collection to group
        key: Path string or function to extract grouping key

    Returns:
        Dictionary mapping keys to lists of items

    Example:
        >>> import json
        >>> users = [
        ...     {"role": "admin", "name": "Alice"},
        ...     {"role": "user", "name": "Bob"},
        ...     {"role": "admin", "name": "Carol"}
        ... ]
        >>> result = group_by(users, "role")
        >>> print(json.dumps(result, indent=4))
        {
            "admin": [
                {
                    "role": "admin",
                    "name": "Alice"
                },
                {
                    "role": "admin",
                    "name": "Carol"
                }
            ],
            "user": [
                {
                    "role": "user",
                    "name": "Bob"
                }
            ]
        }
    """

    def getk(x):
        return deep_get(x, key) if isinstance(key, str) else key(x)

    out: dict[Any, list[Any]] = {}
    for it in items:
        out.setdefault(getk(it), []).append(it)
    return out


def count_by(items: Iterable[Any], key: str | Callable[[Any], Any]) -> dict[Any, int]:
    """
    Count items by key function or path.

    Args:
        items: Collection to count
        key: Path string or function to extract counting key

    Returns:
        Dictionary mapping keys to counts

    Example:
        >>> import json
        >>> users = [{"role": "admin"}, {"role": "user"}, {"role": "admin"}, {"role": "guest"}]
        >>> result = count_by(users, "role")
        >>> print(json.dumps(result, indent=4))
        {
            "admin": 2,
            "user": 1,
            "guest": 1
        }
    """

    def getk(x):
        return deep_get(x, key) if isinstance(key, str) else key(x)

    out: dict[Any, int] = {}
    for it in items:
        k = getk(it)
        out[k] = out.get(k, 0) + 1
    return out


def sum_by(
    items: Iterable[Any],
    key: str | Callable[[Any], Any],
    map: Callable[[Any], Any],
) -> dict[Any, Any]:
    """
    Sum mapped values by key function or path.

    Args:
        items: Collection to process
        key: Path string or function to extract grouping key
        map: Function to extract value to sum

    Returns:
        Dictionary mapping keys to summed values

    Example:
        >>> import json
        >>> sales = [
        ...     {"region": "North", "amount": 100},
        ...     {"region": "South", "amount": 200},
        ...     {"region": "North", "amount": 150}
        ... ]
        >>> result = sum_by(sales, "region", lambda x: x["amount"])
        >>> print(json.dumps(result, indent=4))
        {
            "North": 250,
            "South": 200
        }
    """

    def getk(x):
        return deep_get(x, key) if isinstance(key, str) else key(x)

    out: dict[Any, Any] = {}
    for it in items:
        k = getk(it)
        v = map(it)
        out[k] = (out.get(k, 0) + v) if v is not None else out.get(k, 0)
    return out


def reduce_by(
    items: Iterable[Any],
    key: str | Callable[[Any], Any],
    *,
    zero: Any,
    reduce: Reducer,
    map: Callable[[Any], Any] = lambda x: x,
) -> dict[Any, Any]:
    """
    Reduce items by key using custom reducer function.

    Args:
        items: Collection to reduce
        key: Path string or function to extract grouping key
        zero: Initial value for reduction
        reduce: Binary function to combine values
        map: Function to transform items before reduction

    Returns:
        Dictionary mapping keys to reduced values

    Example:
        >>> import json
        >>> sales = [
        ...     {"region": "North", "amount": 100},
        ...     {"region": "South", "amount": 200},
        ...     {"region": "North", "amount": 150}
        ... ]
        >>> result = reduce_by(sales, "region", zero=0, reduce=lambda a, b: max(a, b),
        ...                   map=lambda x: x["amount"])
        >>> print(json.dumps(result, indent=4))
        {
            "North": 150,
            "South": 200
        }
    """

    def getk(x):
        return deep_get(x, key) if isinstance(key, str) else key(x)

    out: dict[Any, Any] = {}
    for it in items:
        k = getk(it)
        v = map(it)
        out[k] = reduce(out.get(k, zero), v)
    return out


def rollup_tree(
    tree: Mapping[str, Any], reducers: Mapping[str, Callable[[Any, Any], Any]]
) -> dict[str, Any]:
    """
    Roll up aggregate values from leaves to parents in a tree structure.

    Args:
        tree: Tree structure as nested dictionaries
        reducers: Map of field names to reduction functions

    Returns:
        Tree with rolled-up values

    Example:
        >>> import json
        >>> tree = {
        ...     "departments": {
        ...         "engineering": {
        ...             "budget": 100,
        ...             "teams": {
        ...                 "frontend": {"budget": 40},
        ...                 "backend": {"budget": 60}
        ...             }
        ...         }
        ...     }
        ... }
        >>> result = rollup_tree(tree, {"budget": lambda a, b: (a or 0) + (b or 0)})
        >>> print(json.dumps(result, indent=4))
        {
            "departments": {
                "engineering": {
                    "budget": 200,
                    "teams": {
                        "frontend": {
                            "budget": 40
                        },
                        "backend": {
                            "budget": 60
                        }
                    }
                }
            }
        }
    """

    def _walk(node: dict[str, Any]) -> dict[str, Any]:
        totals = {name: None for name in reducers}
        for _k, v in node.items():
            if isinstance(v, dict):
                child_totals = _walk(v)
                for name, red in reducers.items():
                    if child_totals.get(name) is not None:
                        totals[name] = (
                            red(totals[name], child_totals[name])
                            if totals[name] is not None
                            else child_totals[name]
                        )
        # add current node's own values
        for name, red in reducers.items():
            if name in node and node[name] is not None:
                totals[name] = (
                    red(totals[name], node[name])
                    if totals[name] is not None
                    else node[name]
                )
        # write back
        for name, val in totals.items():
            if val is not None:
                node[name] = val
        return totals

    root = dict(tree)
    _walk(root)
    return root


# ------------- transform & validation -------------


def map_values(
    d: Any,
    fn: Callable[[Any], Any],
    *,
    deep: bool = False,
    predicate: Callable[[Any, Any], bool] | None = None,
) -> Any:
    """
    Transform values in a mapping using a function.

    Args:
        d: Object to transform
        fn: Function to apply to values
        deep: Whether to recursively transform nested mappings
        predicate: Optional function to filter which values to transform

    Returns:
        New object with transformed values

    Example:
        >>> import json
        >>> data = {"user": {"age": 30, "score": 95.5, "name": "Alice"}}
        >>> result = map_values(data, lambda x: x * 2 if isinstance(x, (int, float)) else x,
        ...                    deep=True)
        >>> print(json.dumps(result, indent=4))
        {
            "user": {
                "age": 60,
                "score": 191.0,
                "name": "Alice"
            }
        }
    """
    if not _is_mapping(d):
        return fn(d) if (predicate is None or predicate(None, d)) else d
    out: dict[Any, Any] = {}
    for k, v in d.items():
        if deep and _is_mapping(v):
            out[k] = map_values(v, fn, deep=True, predicate=predicate)
        else:
            out[k] = fn(v) if (predicate is None or predicate(k, v)) else v
    return out


def map_keys(
    d: Mapping[str, Any],
    fn: Callable[[str], str],
    *,
    deep: bool = False,
) -> dict[str, Any]:
    """
    Transform keys in a mapping using a function.

    Args:
        d: Mapping to transform
        fn: Function to apply to keys
        deep: Whether to recursively transform nested mappings

    Returns:
        New mapping with transformed keys

    Example:
        >>> import json
        >>> data = {
        ...     "first_name": "Alice",
        ...     "last_name": "Smith",
        ...     "user_details": {"email_address": "alice@example.com"}
        ... }
        >>> result = map_keys(data, lambda k: k.replace("_", "-"), deep=True)
        >>> print(json.dumps(result, indent=4))
        {
            "first-name": "Alice",
            "last-name": "Smith",
            "user-details": {
                "email-address": "alice@example.com"
            }
        }
    """
    out: dict[str, Any] = {}
    for k, v in d.items():
        nk = fn(k)
        out[nk] = map_keys(v, fn, deep=True) if deep and _is_mapping(v) else v
    return out


def map_items(
    d: Mapping[str, Any],
    fn: Callable[[str, Any], tuple[str, Any]],
    *,
    deep: bool = False,
) -> dict[str, Any]:
    """
    Transform both keys and values in a mapping using a function.

    Args:
        d: Mapping to transform
        fn: Function that takes (key, value) and returns (new_key, new_value)
        deep: Whether to recursively transform nested mappings

    Returns:
        New mapping with transformed items

    Example:
        >>> import json
        >>> data = {"count": 5, "total": 100}
        >>> result = map_items(data, lambda k, v: (f"{k}_value", v * 10))
        >>> print(json.dumps(result, indent=4))
        {
            "count_value": 50,
            "total_value": 1000
        }
    """
    out: dict[str, Any] = {}
    for k, v in d.items():
        if deep and _is_mapping(v):
            mapped_v = map_items(v, fn, deep=True)
        else:
            mapped_v = v
        nk, nv = fn(k, mapped_v)
        out[nk] = nv
    return out


def schema_check(
    d: Any, schema: Mapping[str, Any], *, mode: str = "collect"
) -> list[str]:
    """
    Validate object against a simple schema.

    Args:
        d: Object to validate
        schema: Schema definition with nested structure and types
        mode: "collect" to return errors, "raise" to throw exception

    Returns:
        List of validation error messages

    Example:
        >>> import json
        >>> data = {"user": {"name": "Alice", "age": "30"}}  # age should be int
        >>> schema = {"user": {"name": str, "age": int}}
        >>> result = schema_check(data, schema)
        >>> print(json.dumps(result, indent=4))
        [
            "user.age: expected <class 'int'>, got <class 'str'>"
        ]
    """
    errors: list[str] = []

    def _walk(node: Any, sch: Any, path: str) -> None:
        if _is_mapping(sch):
            if not _is_mapping(node):
                errors.append(f"{path or '<root>'}: expected mapping")
                return
            for k, sub in sch.items():
                if k not in node:
                    errors.append(f"{path + '.' if path else ''}{k}: missing")
                else:
                    _walk(node[k], sub, f"{path + '.' if path else ''}{k}")
        elif sch is not None and not isinstance(node, sch):
            errors.append(f"{path}: expected {sch}, got {type(node)}")

    _walk(d, schema, "")
    if errors and mode == "raise":
        raise ValueError("schema_check failed:\n" + "\n".join(errors))
    return errors


def coalesce_paths(
    d: Any,
    candidates: Sequence[Path],
    *,
    set_to: Path | None = None,
    default: Any = None,
) -> Any:
    """
    Return first existing value from candidate paths, optionally setting result to a path.

    Args:
        d: Object to search
        candidates: List of paths to try in order
        set_to: Optional path to set the found value to
        default: Value to return if no candidates exist

    Returns:
        First found value or default

    Example:
        >>> import json
        >>> data = {"user": {"email": "alice@example.com"}}
        >>> result = coalesce_paths(data, ["user.username", "user.email", "user.id"],
        ...                        default="anonymous")
        >>> print(json.dumps(result, indent=4))
        "alice@example.com"

        >>> coalesce_paths(data, ["user.username", "user.id"],
        ...                set_to="user.display_name", default="anonymous")
        >>> print(json.dumps(data, indent=4))
        {
            "user": {
                "email": "alice@example.com",
                "display_name": "anonymous"
            }
        }
    """
    for p in candidates:
        if deep_has(d, p):
            val = deep_get(d, p)
            if set_to is not None:
                deep_set(d, set_to, val)
            return val
    if set_to is not None:
        deep_set(d, set_to, default)
    return default


def prune(
    d: Any,
    *,
    remove_empty: bool = True,
    predicate: Callable[[Any, Any], bool] | None = None,
) -> Any:
    """
    Remove empty values or values matching predicate, recursively.

    Args:
        d: Object to prune
        remove_empty: Whether to remove None, {}, [] values
        predicate: Optional function to determine what to remove

    Returns:
        Pruned object

    Example:
        >>> import json
        >>> data = {
        ...     "user": {
        ...         "name": "Alice",
        ...         "email": None,
        ...         "tags": [],
        ...         "profile": {"bio": "", "settings": {}}
        ...     }
        ... }
        >>> result = prune(data)
        >>> print(json.dumps(result, indent=4))
        {
            "user": {
                "name": "Alice"
            }
        }
    """
    if _is_mapping(d):
        keys = list(d.keys())
        for k in keys:
            v = prune(d[k], remove_empty=remove_empty, predicate=predicate)
            drop = False
            if predicate and predicate(k, v):
                drop = True
            if remove_empty and (v is None or v in ({}, [])):
                drop = True
            if drop:
                del d[k]
            else:
                d[k] = v
        return d
    if isinstance(d, list):
        out = [prune(x, remove_empty=remove_empty, predicate=predicate) for x in d]
        return [x for x in out if not (remove_empty and (x is None or x in ({}, [])))]
    return d


# ------------- merging lists / patching -------------


def merge_lists_by(
    a: list[Any],
    b: list[Any],
    *,
    key: str | Callable[[Any], Any],
    on_conflict: str = "prefer_right",  # "prefer_right" | "prefer_left" | "merge_dict"
) -> list[Any]:
    """
    Merge two lists by matching items on a key.

    Args:
        a: First list (modified in place)
        b: Second list to merge from
        key: Path or function to extract matching key
        on_conflict: How to handle conflicts ("prefer_right", "prefer_left", "merge_dict")

    Returns:
        The merged list a

    Example:
        >>> import json
        >>> users1 = [{"id": 1, "name": "Alice", "role": "user"}]
        >>> users2 = [
        ...     {"id": 1, "name": "Alice", "role": "admin"},
        ...     {"id": 2, "name": "Bob", "role": "user"}
        ... ]
        >>> result = merge_lists_by(users1, users2, key="id")
        >>> print(json.dumps(result, indent=4))
        [
            {
                "id": 1,
                "name": "Alice",
                "role": "admin"
            },
            {
                "id": 2,
                "name": "Bob",
                "role": "user"
            }
        ]
    """

    def getk(x):
        return deep_get(x, key) if isinstance(key, str) else key(x)

    idx = {getk(x): i for i, x in enumerate(a)}
    for el in b:
        k = getk(el)
        if k in idx:
            i = idx[k]
            if on_conflict == "prefer_left":
                continue
            if on_conflict == "prefer_right":
                a[i] = el
                continue
            if on_conflict == "merge_dict" and _is_mapping(a[i]) and _is_mapping(el):
                a[i] = deep_update(a[i], el)  # default strategies
            else:
                a[i] = el
        else:
            a.append(el)
            idx[k] = len(a) - 1
    return a


def patch(d: Any, ops: Sequence[Mapping[str, Any]]) -> Any:
    """
    Apply JSON-Patch-like operations to an object.

    Args:
        d: Object to patch
        ops: List of operation dictionaries with "op", "path", and optionally "value"

    Returns:
        The patched object

    Example:
        >>> import json
        >>> data = {"user": {"name": "Alice", "age": 30}}
        >>> operations = [
        ...     {"op": "replace", "path": "user.age", "value": 31},
        ...     {"op": "add", "path": "user.email", "value": "alice@example.com"},
        ...     {"op": "remove", "path": "user.age"}
        ... ]
        >>> result = patch(data, operations)
        >>> print(json.dumps(result, indent=4))
        {
            "user": {
                "name": "Alice",
                "email": "alice@example.com"
            }
        }
    """
    for op in ops:
        operation = op.get("op")
        path = op.get("path")
        if operation in ("add", "replace"):
            if path is not None:
                deep_set(d, path, op.get("value"))
        elif operation == "remove":
            if path is not None:
                deep_del(d, path)
        else:
            raise ValueError(f"Unsupported op: {operation}")
    return d


# ------------- query-ish -------------


def where(items: Iterable[Any], pred: Callable[[Any], bool]) -> list[Any]:
    """
    Filter items by predicate function.

    Args:
        items: Collection to filter
        pred: Function that returns True for items to keep

    Returns:
        List of items matching the predicate

    Example:
        >>> import json
        >>> users = [
        ...     {"name": "Alice", "age": 30},
        ...     {"name": "Bob", "age": 25},
        ...     {"name": "Carol", "age": 35}
        ... ]
        >>> result = where(users, lambda x: x["age"] >= 30)
        >>> print(json.dumps(result, indent=4))
        [
            {
                "name": "Alice",
                "age": 30
            },
            {
                "name": "Carol",
                "age": 35
            }
        ]
    """
    return [x for x in items if pred(x)]


def match(items: Iterable[Any], **eq: Any) -> list[Any]:
    """
    Match items by exact field values using dot-path notation.

    Args:
        items: Collection to search
        **eq: Field paths and expected values

    Returns:
        List of items matching all criteria

    Example:
        >>> import json
        >>> users = [
        ...     {"name": "Alice", "profile": {"role": "admin", "active": True}},
        ...     {"name": "Bob", "profile": {"role": "user", "active": True}},
        ...     {"name": "Carol", "profile": {"role": "admin", "active": False}}
        ... ]
        >>> result = match(users, **{"profile.role": "admin", "profile.active": True})
        >>> print(json.dumps(result, indent=4))
        [
            {
                "name": "Alice",
                "profile": {
                    "role": "admin",
                    "active": true
                }
            }
        ]
    """
    outs: list[Any] = []
    for it in items:
        ok = True
        for p, v in eq.items():
            if deep_get(it, p, default=None) != v:
                ok = False
                break
        if ok:
            outs.append(it)
    return outs


def distinct_by(items: Iterable[Any], key: str | Callable[[Any], Any]) -> list[Any]:
    """
    Remove duplicates by key function or path.

    Args:
        items: Collection to deduplicate
        key: Path string or function to extract uniqueness key

    Returns:
        List with duplicates removed (first occurrence kept)

    Example:
        >>> import json
        >>> users = [
        ...     {"id": 1, "name": "Alice"},
        ...     {"id": 2, "name": "Bob"},
        ...     {"id": 1, "name": "Alice Updated"}
        ... ]
        >>> result = distinct_by(users, "id")
        >>> print(json.dumps(result, indent=4))
        [
            {
                "id": 1,
                "name": "Alice"
            },
            {
                "id": 2,
                "name": "Bob"
            }
        ]
    """

    def getk(x):
        return deep_get(x, key) if isinstance(key, str) else key(x)

    seen = set()
    out: list[Any] = []
    for it in items:
        k = getk(it)
        if k not in seen:
            seen.add(k)
            out.append(it)
    return out


# ------------- ensure / ensure_path -------------


def ensure_path(
    d: Any,
    path: Path,
    *,
    factory: Callable[[], Any] = dict,
) -> Any:
    """
    Ensure nested path exists and return the container at that path.

    Args:
        d: Object to modify
        path: Path to ensure exists
        factory: Function to create new containers

    Returns:
        The container at the specified path

    Example:
        >>> import json
        >>> data = {}
        >>> container = ensure_path(data, "user.profile.settings")
        >>> container["theme"] = "dark"
        >>> print(json.dumps(data, indent=4))
        {
            "user": {
                "profile": {
                    "settings": {
                        "theme": "dark"
                    }
                }
            }
        }
    """
    parts = _parse_path(path)
    cur = d
    for i, p in enumerate(parts):
        if i == len(parts) - 1:
            # ensure final container exists and return it
            if isinstance(p, int):
                if not isinstance(cur, list):
                    raise TypeError("Final ensure segment expects list")
                while len(cur) <= p:
                    cur.append(None)
                if cur[p] is None:
                    cur[p] = factory()
                return cur[p]
            else:
                if _is_mapping(cur):
                    if p not in cur or cur[p] is None:
                        cur[p] = factory()
                    return cur[p]
                # object
                existing = getattr(cur, p, None)
                if existing is None:
                    existing = factory()
                    _set_attr(cur, p, existing, create_mapping=factory)
                return existing
        # intermediate
        cur = _ensure_container(cur, p, create_mapping=factory)
    return cur


# alias for symmetry
ensure = ensure_path
