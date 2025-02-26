from ftml import load


def test_null():
    ftml_input = "null"
    data = load(ftml_input)
    assert data is None


def test_null_in_double_quotes():
    ftml_input = '"null"'
    data = load(ftml_input)
    assert data == "null"


def test_null_in_single_quotes():
    ftml_input = "'null'"
    data = load(ftml_input)
    assert data == "null"


def test_null_with_extra_whitespace():
    ftml_input = "  null  "
    data = load(ftml_input)
    assert data is None  # Ensure trimming doesn't break parsing


# todo add tests to validate type against the schema.
