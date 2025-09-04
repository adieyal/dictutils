from collections.abc import Iterable, Mapping
from typing import Union

# Minimum number of arguments required (excluding first parameter)
MIN_ARGS = 2


def _extract_value(q, key, strict: bool = False):
    """Extract value from row q using selector key."""
    if callable(key):
        return key(q)
    elif isinstance(key, int) and isinstance(q, Mapping) and key in q:
        return q[key]
    elif isinstance(key, str) and hasattr(q, key):
        return getattr(q, key)
    elif isinstance(q, Mapping) and key in q:
        return q[key]
    else:
        if strict:
            if isinstance(q, Mapping):
                raise KeyError(f"Missing key {key!r}")
            else:
                raise AttributeError(f"Missing attribute {key!r}")
        return None


def _set_leaf_value(current_dict, q, args, extract_fn):
    """Set the leaf value in the nested structure."""
    if isinstance(args[-1], tuple):
        # Multiple leaf values as a list
        current_dict[extract_fn(q, args[-2])] = [extract_fn(q, el) for el in args[-1]]
    else:
        # Single leaf value
        current_dict[extract_fn(q, args[-2])] = extract_fn(q, args[-1])


def qsdict(qs: Iterable[Union[Mapping, object]], *args, strict: bool = False) -> dict:
    """
    Build a nested dict from rows (dicts or objects) by a sequence of selectors.

    Args:
        qs: Iterable of mappings or objects to process
        *args: Selectors - each can be:
            - Key name (str/int) to access dict keys or object attributes
            - Callable that takes a row and returns a key
            - Tuple of selectors for the leaf values (last arg only)
        strict: If True, raise KeyError/AttributeError for missing selectors.
                If False (default), missing selectors yield None keys.

    Returns:
        Nested dict where each level corresponds to a selector

    Examples:
        >>> data = [{"cat": "A", "val": 1}, {"cat": "B", "val": 2}]
        >>> qsdict(data, "cat", "val")
        {'A': 1, 'B': 2}

        >>> qsdict(data, lambda x: x["cat"].lower(), "val")
        {'a': 1, 'b': 2}
    """
    if len(args) < MIN_ARGS:
        raise ValueError("Need at least two fields to nest dicts")

    # Create extraction function with strict mode baked in
    def extract_fn(q, key):
        return _extract_value(q, key, strict)

    # Use plain dict everywhere (Python 3.9+ has insertion-order guarantees)
    root: dict = {}
    for q in qs:
        nested_dicts = [root]

        # Build nested structure up to second-to-last level
        for key in args[:-2]:
            current_dict = nested_dicts[-1]
            value = extract_fn(q, key)
            if value not in current_dict:
                current_dict[value] = {}
            nested_dicts.append(current_dict[value])

        # Set leaf value at the deepest level
        current_dict = nested_dicts[-1]
        _set_leaf_value(current_dict, q, args, extract_fn)

    return root
