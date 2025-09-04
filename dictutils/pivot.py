from __future__ import annotations

from collections.abc import Mapping

# Minimum array length for nesting (key + value)
MIN_ARRAY_LENGTH = 2


def flatten_dict(d: Mapping) -> list[list]:
    """
    Flatten a dictionary into an array of arrays.

    Example:
        {a: {x: 2, y: 3}, b: {x: 4, y: 5}}
        becomes
        [[a, x, 2], [a, y, 3], [b, x, 4], [b, y, 5]]

    Used as a component of the pivot function.
    """
    if not isinstance(d, Mapping):
        return [[d]]

    arr = []
    for k, v in d.items():
        for el in flatten_dict(v):
            arr.append([k] + el)

    return arr


def rearrange(in_arrs: list[list], order: list[int]) -> list[list]:
    """
    Rearrange elements in a given list of arrays by order indices.
    The last element (value) always remains in place.

    Args:
        in_arrs: List of arrays to rearrange
        order: List of indices specifying new order of keys

    Returns:
        Rearranged arrays

    Raises:
        IndexError: If any index in order is out of range for the row

    Example:
        rearrange([[a, x, 2], [a, y, 3]], [1, 0])
        becomes [[x, a, 2], [y, a, 3]]
    """
    out = []
    for arr in in_arrs:
        # Validate indices against row width (excluding the last element which is the value)
        max_key_index = len(arr) - 2  # -1 for last element, -1 for 0-based indexing
        for i in order:
            if i < 0 or i > max_key_index:
                raise IndexError(
                    f"order index {i} out of range for row with {max_key_index + 1} keys"
                )

        out.append([arr[i] for i in order] + [arr[-1]])

    return out


def nest(arrays: list, root: dict | None = None) -> dict:
    """
    Unflatten a dictionary from arrays. Similar to qsdict but simpler.

    Args:
        arrays: List of arrays where each array represents a path + value
        root: Optional existing dict to merge into

    Returns:
        Nested dictionary
    """
    if not arrays:
        return {}

    d = root or {}
    for arr in arrays:
        if len(arr) >= MIN_ARRAY_LENGTH:
            head, *tail = arr
            if len(tail) == 1:
                d[head] = tail[0]
            else:
                d[head] = nest([tail], d.get(head, {}))
    return d


def pivot(d: dict, order: list[int]) -> dict:
    """
    Pivot a nested dictionary by rearranging the key levels according to order.

    Args:
        d: Input nested dictionary
        order: List of indices specifying the new order of key levels

    Returns:
        Pivoted dictionary with keys rearranged

    Example:
        d = {"A": {"X": 1, "Y": 2}, "B": {"X": 3, "Y": 4}}
        pivot(d, [1, 0]) -> {"X": {"A": 1, "B": 3}, "Y": {"A": 2, "B": 4}}
    """
    flattened = flatten_dict(d)
    rearranged = rearrange(flattened, order)
    nested = nest(rearranged)
    return nested
