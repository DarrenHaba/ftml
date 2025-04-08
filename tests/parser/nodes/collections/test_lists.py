import pytest

from ftml import load, FTMLParseError


def test_empty_list():
    ftml_input = 'items = []'
    data = load(ftml_input)
    assert data["items"] == []


def test_unnamed_empty_list_should_fail():
    ftml_input = '[]'
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_inline_list():
    ftml_input = 'items = [ "a", "b", "c" ]'
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


def test_multiline_list():
    ftml_input = """items = [
        "a",
        "b",
        "c"
    ]"""
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


def test_multiline_list_brackets_on_separate_lines_should_fail():
    ftml_input = """ items = 
    [
        "a",
        "b",
        "c"
    ]
    """
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_multiline_list_mixed_indentation():
    ftml_input = """ items = [
      "a",
        "b",
          "c"
    ]
    """
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


def test_multiline_list_no_whitespace():
    ftml_input = """
    items=[
        "a",
        "b",
        "c"
    ]
"""
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


def test_named_multiline_list_brackets_on_separate_lines():
    ftml_input = """
    items = [
        "a",
        "b",
        "c"
    ]
"""
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


# --- Additional Edge Cases ---
def test_multiline_list_with_trailing_comma():
    ftml_input = """
    items = [
        "a",
        "b",
        "c",
    ]
"""
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


def test_inline_list_with_trailing_comma():
    ftml_input = """
    items = ["a", "b", "c",]
"""
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


def test_inline_list_without_trailing_comma():
    ftml_input = """
    items = ["a", "b", "c"]
"""
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


def test_inline_list_with_mixed_scalars():
    ftml_input = 'items = [ "a", 2, true, null ]'
    data = load(ftml_input)
    assert data["items"] == ["a", 2, True, None]


def test_multiline_list_with_mixed_scalars():
    ftml_input = """
    items = [
        "a",
        2,
        true,
        null,
    ]
"""
    data = load(ftml_input)
    assert data["items"] == ["a", 2, True, None]


def test_multiline_list_of_lists():
    ftml_input = """
    items = [
        [1, 2],
        [[3, 4], [5, 6]],
    ]
"""
    data = load(ftml_input)
    assert data["items"] == [[1, 2], [[3, 4], [5, 6]]]


def test_multiline_list_of_mixed_lists():
    ftml_input = """
    items = [
        [1, 2.0, "three", 'four'],
        [true, false, null]
    ]
"""
    data = load(ftml_input)
    assert data["items"] == [[1, 2.0, "three", "four"], [True, False, None]]


def test_list_single_item_with_trailing_comma():
    """Test a single-item list with a trailing comma."""
    ftml_input = """items = [
        "a",
    ]"""
    data = load(ftml_input)
    assert data["items"] == ["a"]


def test_list_single_item_no_trailing_comma():
    """Test a single-item list without a trailing comma."""
    ftml_input = """items = [
        "a"
    ]"""
    data = load(ftml_input)
    assert data["items"] == ["a"]


def test_multiline_list_of_objects():
    ftml_input = """
    items = [
        {a = 1, b = 2},
        {c = true, d = false, f = null}
    ]
"""
    data = load(ftml_input)
    assert data["items"] == [{"a": 1, "b": 2}, {"c": True, "d": False, "f": None}]
