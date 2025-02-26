from ftml import load


def test_empty_list():
    ftml_input = '{ items = [] }'
    data = load(ftml_input)
    assert data["items"] == []


# --- Unnamed Lists (Root-level Lists) ---
def test_unnamed_inline_list():
    ftml_input = '[ "a", "b", "c" ]'
    data = load(ftml_input)
    assert data == ["a", "b", "c"]


def test_unnamed_multiline_list():
    ftml_input = """[
        "a",
        "b",
        "c"
    ]"""
    data = load(ftml_input)
    assert data == ["a", "b", "c"]


def test_unnamed_multiline_list_brackets_on_separate_lines():
    ftml_input = """
    [
        "a",
        "b",
        "c"
    ]
    """
    data = load(ftml_input)
    assert data == ["a", "b", "c"]


def test_unnamed_multiline_list_mixed_indentation():
    ftml_input = """
    [
      "a",
        "b",
          "c"
    ]
    """
    data = load(ftml_input)
    assert data == ["a", "b", "c"]


# --- Named Lists (Wrapped in a Dictionary) ---
def test_named_inline_list():
    ftml_input = '{ items = [ "a", "b", "c" ] }'
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


def test_named_multiline_list():
    ftml_input = """{
    items =
    [
        "a",
        "b",
        "c"
    ]
}"""
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


def test_named_multiline_list_brackets_on_separate_lines():
    ftml_input = """{
    items =
    [
        "a",
        "b",
        "c"
    ]
}"""
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


def test_named_multiline_list_mixed_indentation():
    ftml_input = """{
    items =
      [
        "a",
          "b",
            "c"
      ]
}"""
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


# --- Additional Edge Cases ---
def test_named_list_with_trailing_comma():
    ftml_input = """{
    items =
    [
        "a",
        "b",
        "c",
    ]
}"""
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


def test_named_list_brace_on_new_line_with_trailing_comma():
    ftml_input = """
{
    items =
    [
        "a",
        "b",
        "c",
    ]
}"""
    data = load(ftml_input)
    assert data["items"] == ["a", "b", "c"]


def test_unnamed_list_with_trailing_comma():
    ftml_input = """[
        "a",
        "b",
        "c",
    ]"""
    data = load(ftml_input)
    assert data == ["a", "b", "c"]


def test_inline_list_with_mixed_primitives():
    ftml_input = '{ items = [ "a", 2, true, null ] }'
    data = load(ftml_input)
    assert data["items"] == ["a", 2, True, None]


def test_multiline_list_with_mixed_primitives():
    ftml_input = """{
    items =
    [
        "a",
        2,
        true,
        null
    ]
}"""
    data = load(ftml_input)
    assert data["items"] == ["a", 2, True, None]


# def test_list_schema_validation():
#     schema = """
# :dict{
#     :list[:int] numbers
# }
# """
#     # Valid list
#     ftml_input = '{ numbers = [ 1, 2, 3 ] }'
#     data = load(ftml_input, schema=schema)
#     assert data["numbers"] == [1, 2, 3]
# 
#     # Invalid list: one item is not an int
#     ftml_input_invalid = '{ numbers = [ 1, "2", 3 ] }'
#     with pytest.raises(Exception):
#         load(ftml_input_invalid, schema=schema)
# 
# 
# def test_dump_list():
#     ftml_input = '{ items = [1, 2, 3] }'
#     data = load(ftml_input)
#     assert data["items"] == [1, 2, 3]
#     data_dump = dump(data)
#     assert data_dump.__contains__("items")
#     assert data_dump.__contains__("1, 2, 3")
