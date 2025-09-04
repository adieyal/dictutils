from __future__ import annotations

import operator
from dataclasses import dataclass
from typing import Any, Callable, Union

_Path = Union[str, Callable[[Any], Any]]


@dataclass(frozen=True)
class Agg:
    """
    Declarative aggregate specification.

    Args:
        map: Function that extracts a value from each item to aggregate
        zero: Identity element (value or callable). If None, first mapped value seeds the total
        reduce: Function to combine values (default: operator.add)
        skip_none: If True, ignore mapped None values (default: True)
        finalize: Optional function to transform the final aggregated value

    Example:
        Sum values::

            Agg(map=lambda x: x["amount"], zero=0)

        Count items::

            Agg(map=lambda x: 1, zero=0, reduce=operator.add)

        Calculate average::

            Agg(
                map=lambda x: (x["val"], 1),
                zero=(0, 0),
                reduce=lambda a, b: (a[0] + b[0], a[1] + b[1]),
                finalize=lambda x: x[0] / x[1] if x[1] > 0 else 0
            )
    """

    map: Callable[[Any], Any]
    zero: Any = None
    reduce: Callable[[Any, Any], Any] = operator.add
    skip_none: bool = True
    finalize: Callable[[Any], Any] | None = None


_SENTINEL = object()


def _get(obj: Any, sel: _Path) -> Any:
    """
    Extract value from obj using selector.

    Args:
        obj: Object to extract from
        sel: Either a callable(obj) -> value, or dotted path string like "a.b.c"

    Returns:
        Extracted value or None if path doesn't exist

    Example:
        _get({"a": {"b": 1}}, "a.b")  # Returns 1
        _get(obj, lambda x: x.name)   # Returns obj.name
    """
    if callable(sel):
        return sel(obj)

    # Handle dotted path access: "a.b.c"
    cur = obj
    for part in str(sel).split("."):
        if cur is None:
            return None
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            cur = getattr(cur, part, None)
    return cur


def _navigate_to_leaf(root: dict, item: Any, keys: list[_Path]) -> dict:
    """Navigate through nested structure to get the leaf dict for this item."""
    node = root
    for ksel in keys:
        k = _get(item, ksel)
        node = node.setdefault(k, {})
    return node


def _initialize_leaf(
    node: dict, aggs: dict[str, Agg], include_rows: bool, rows_key: str
) -> None:
    """Initialize a leaf node with empty aggregation state."""
    if "_agg" not in node:
        node["_agg"] = {name: _SENTINEL for name in aggs}
        if include_rows:
            node[rows_key] = []


def _update_aggregation(node: dict, item: Any, spec: Agg, name: str) -> None:
    """Update a single aggregation with a new item."""
    mapped = spec.map(item)
    if mapped is None and spec.skip_none:
        return

    cur = node["_agg"][name]
    if cur is _SENTINEL:
        # Seed the accumulator
        if spec.zero is None:
            node["_agg"][name] = mapped
        else:
            zero = spec.zero() if callable(spec.zero) else spec.zero
            node["_agg"][name] = spec.reduce(zero, mapped)
    else:
        node["_agg"][name] = spec.reduce(cur, mapped)


def _finalize_aggregations(root: dict, aggs: dict[str, Agg]) -> None:
    """Move aggregated totals to top level and apply finalization."""

    def _finalize_node(n: dict):
        for v in list(n.values()):
            if isinstance(v, dict):
                _finalize_node(v)
        if "_agg" in n:
            totals = n.pop("_agg")
            for name, value in totals.items():
                spec = aggs[name]
                n[name] = spec.finalize(value) if spec.finalize else value

    _finalize_node(root)


def nest_agg(
    items: list[Any],
    keys: list[_Path],
    *,
    aggs: dict[str, Agg],
    include_rows: bool = False,
    rows_key: str = "rows",
) -> dict:
    """
    Build a nested dict keyed by `keys`, with aggregations at the leaves.

    Args:
        items: List of items (dicts/objects) to process
        keys: List of selectors for grouping. Each can be:

            - String key/attribute name
            - Dotted path like "supplier.name"
            - Callable that takes an item and returns a grouping key

        aggs: Dict of {name: Agg} specifications for leaf aggregations
        include_rows: If True, include raw items under rows_key
        rows_key: Key name for raw rows (when include_rows=True)

    Returns:
        Nested dict with aggregated values at leaves

    Example::

        items = [
            {"cat": "A", "val": 1},
            {"cat": "A", "val": 2},
            {"cat": "B", "val": 3}
        ]
        aggs = {
            "total": Agg(map=lambda it: it["val"], zero=0),
            "count": Agg(map=lambda it: 1, zero=0)
        }
        result = nest_agg(items, keys=["cat"], aggs=aggs)
        # {"A": {"total": 3, "count": 2}, "B": {"total": 3, "count": 1}}
    """
    root: dict = {}

    for item in items:
        # Navigate to the leaf node for this item
        node = _navigate_to_leaf(root, item, keys)

        # Initialize leaf state if needed
        _initialize_leaf(node, aggs, include_rows, rows_key)

        # Collect raw rows if requested
        if include_rows:
            node[rows_key].append(item)

        # Update all aggregations for this item
        for name, spec in aggs.items():
            _update_aggregation(node, item, spec, name)

    # Finalize all aggregations
    _finalize_aggregations(root, aggs)
    return root
