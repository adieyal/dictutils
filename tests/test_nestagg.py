import operator

from dictutils.nestagg import Agg, nest_agg


def test_nest_agg_single_key_sum():
    items = [
        {"cat": "A", "val": 1},
        {"cat": "A", "val": 2},
        {"cat": "B", "val": 3},
    ]
    aggs = {"total": Agg(map=lambda it: it["val"], zero=0)}
    result = nest_agg(items, keys=["cat"], aggs=aggs)
    assert result == {"A": {"total": 3}, "B": {"total": 3}}


def test_nest_agg_two_keys_count():
    items = [
        {"cat": "A", "sub": 1},
        {"cat": "A", "sub": 2},
        {"cat": "B", "sub": 1},
    ]
    aggs = {"count": Agg(map=lambda it: 1, zero=0, reduce=operator.add)}
    result = nest_agg(items, keys=["cat", "sub"], aggs=aggs)
    assert result == {"A": {1: {"count": 1}, 2: {"count": 1}}, "B": {1: {"count": 1}}}


def test_nest_agg_multiple_aggs_and_rows():
    items = [
        {"cat": "A", "val": 1},
        {"cat": "A", "val": 2},
        {"cat": "B", "val": 3},
    ]
    aggs = {
        "total": Agg(map=lambda it: it["val"], zero=0),
        "max": Agg(map=lambda it: it["val"], zero=None, reduce=max),
    }
    result = nest_agg(items, keys=["cat"], aggs=aggs, include_rows=True)
    assert result["A"]["total"] == 3  # noqa: PLR2004
    assert result["A"]["max"] == 2  # noqa: PLR2004
    assert result["B"]["total"] == 3  # noqa: PLR2004
    assert result["B"]["max"] == 3  # noqa: PLR2004
    assert len(result["A"]["rows"]) == 2  # noqa: PLR2004
    assert len(result["B"]["rows"]) == 1


def test_nest_agg_empty_input():
    aggs = {"sum": Agg(map=lambda it: it.get("x", 0), zero=0)}
    result = nest_agg([], keys=["cat"], aggs=aggs)
    assert result == {}


def test_nest_agg_skip_none():
    items = [
        {"cat": "A", "val": 1},
        {"cat": "A", "val": None},
        {"cat": "A", "val": 2},
    ]
    aggs = {"total": Agg(map=lambda it: it["val"], zero=0, skip_none=True)}
    result = nest_agg(items, keys=["cat"], aggs=aggs)
    assert result == {"A": {"total": 3}}


def test_nest_agg_no_skip_none():
    items = [
        {"cat": "A", "val": 1},
        {"cat": "A", "val": None},
    ]
    aggs = {
        "total": Agg(
            map=lambda it: it["val"],
            zero=0,
            skip_none=False,
            reduce=lambda a, b: (a or 0) + (b or 0),
        )
    }
    result = nest_agg(items, keys=["cat"], aggs=aggs)
    assert result == {"A": {"total": 1}}


def test_nest_agg_callable_key():
    items = [
        {"cat": "A", "val": 1},
        {"cat": "B", "val": 2},
    ]
    aggs = {"total": Agg(map=lambda it: it["val"], zero=0)}
    result = nest_agg(items, keys=[lambda it: it["cat"]], aggs=aggs)
    assert result == {"A": {"total": 1}, "B": {"total": 2}}


def test_nest_agg_dotted_path():
    items = [
        {"user": {"name": "Alice"}, "val": 1},
        {"user": {"name": "Alice"}, "val": 2},
        {"user": {"name": "Bob"}, "val": 3},
    ]
    aggs = {"total": Agg(map=lambda it: it["val"], zero=0)}
    result = nest_agg(items, keys=["user.name"], aggs=aggs)
    assert result == {"Alice": {"total": 3}, "Bob": {"total": 3}}


def test_nest_agg_finalize_hook():
    # Test the new finalize feature for calculating averages
    items = [
        {"cat": "A", "val": 1},
        {"cat": "A", "val": 3},
        {"cat": "B", "val": 2},
    ]
    aggs = {
        "average": Agg(
            map=lambda it: (it["val"], 1),  # (sum, count)
            zero=(0, 0),
            reduce=lambda a, b: (a[0] + b[0], a[1] + b[1]),
            finalize=lambda x: x[0] / x[1] if x[1] > 0 else 0,
        )
    }
    result = nest_agg(items, keys=["cat"], aggs=aggs)
    assert result == {"A": {"average": 2.0}, "B": {"average": 2.0}}


def test_nest_agg_zero_seeding_with_none():
    # Test that when zero=None, first mapped value seeds the total
    items = [
        {"cat": "A", "val": 5},
        {"cat": "A", "val": 3},
    ]
    aggs = {"min": Agg(map=lambda it: it["val"], zero=None, reduce=min)}
    result = nest_agg(items, keys=["cat"], aggs=aggs)
    assert result == {"A": {"min": 3}}


def test_nest_agg_custom_rows_key():
    items = [{"cat": "A", "val": 1}]
    aggs = {"total": Agg(map=lambda it: it["val"], zero=0)}
    result = nest_agg(
        items, keys=["cat"], aggs=aggs, include_rows=True, rows_key="items"
    )
    assert "items" in result["A"]
    assert len(result["A"]["items"]) == 1
