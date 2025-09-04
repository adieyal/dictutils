from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def mergedict(*args, path=None, update: bool = True) -> dict[Any, Any] | None:
    """
    Merge multiple nested mappings into a single dict.

    If the first argument is a plain dict, it is updated in-place and returned.
    If the first argument is None or a non-dict Mapping, a new dict is created.

    Args:
        *args: Mappings to merge (first one is modified in-place if possible)
        path: Internal use for error reporting
        update: If True, values in later dicts override earlier ones

    Returns:
        The merged dict (same object as first argument when possible)

    Raises:
        TypeError: If no arguments provided or arguments are not mappings
    """
    if not args:
        raise TypeError("mergedict requires at least one mapping")

    head, *tail = args

    if not tail:
        # Single argument - return it directly if it's a valid mapping
        if head is None:
            return None
        if not isinstance(head, Mapping):
            raise TypeError("All arguments must be mappings or None")
        return head if isinstance(head, dict) else dict(head)

    result = _coerce_to_dict(head)

    for d in tail:
        result = _mergedict(result, d, path, update)

    return result


def _coerce_to_dict(m: Mapping | None) -> dict[Any, Any] | None:
    """Convert a mapping to a dict, with type checking."""
    if m is None:
        return None
    if not isinstance(m, Mapping):
        raise TypeError("All arguments must be mappings or None")
    return dict(m)


def _handle_none_inputs(
    a: dict[Any, Any] | None, b: Mapping | None
) -> dict[Any, Any] | None:
    """Handle cases where a or b is None."""
    if a is None and b is None:
        return None
    if a is None:
        return dict(b) if b is not None else None
    if b is None:
        return a
    return None  # Indicates normal processing should continue


def _merge_existing_key(
    a: dict, b: Mapping, key: Any, path: list, update: bool
) -> None:
    """Handle merging when key already exists in target dict."""
    if isinstance(a[key], dict) and isinstance(b[key], Mapping):
        # Recursive merge for nested dicts
        _mergedict(a[key], b[key], path + [str(key)], update=update)
    elif a[key] == b[key]:
        # Same leaf value - no action needed
        pass
    elif isinstance(a[key], list) and isinstance(b[key], list):
        # Concatenate arrays
        a[key].extend(b[key])
    elif update:
        # Update value when update=True
        a[key] = b[key]
    # When update=False, keep original a[key]


def _copy_new_key(a: dict, b: Mapping, key: Any) -> None:
    """Copy a new key from source to target, converting Mappings to dicts."""
    a[key] = b[key] if not isinstance(b[key], Mapping) else dict(b[key])


def _mergedict(
    a: dict[Any, Any] | None, b: Mapping | None, path=None, update: bool = True
) -> dict[Any, Any] | None:
    """
    Internal merge function that handles the recursive merging logic.

    Args:
        a: Target dict (modified in-place)
        b: Source mapping to merge into a
        path: Current path for error reporting
        update: If True, values in b override values in a

    Returns:
        The merged dict a (or a new dict if a was None)
    """
    # Handle None inputs
    result = _handle_none_inputs(a, b)
    if result is not None or (a is None and b is None):
        return result

    if not isinstance(b, Mapping):
        raise TypeError("Both a and b must be dicts or mappings")

    if path is None:
        path = []

    # At this point, a is guaranteed to be non-None dict
    assert a is not None
    for key in b:
        if key in a:
            _merge_existing_key(a, b, key, path, update)
        else:
            _copy_new_key(a, b, key)

    return a
