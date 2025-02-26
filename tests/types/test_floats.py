from ftml import load


def test_positive_float():
    ftml_input = "42.5"
    data = load(ftml_input)
    assert data == 42.5


def test_negative_float():
    ftml_input = "-42.5"
    data = load(ftml_input)
    assert data == -42.5


def test_zero_float():
    ftml_input = "0.0"
    data = load(ftml_input)
    assert data == 0.0


def test_float_in_double_quotes():
    ftml_input = '"42.5"'
    data = load(ftml_input)
    assert data == "42.5"


def test_float_in_single_quotes():
    ftml_input = "'42.5'"
    data = load(ftml_input)
    assert data == '42.5'


def test_float_with_leading_zeros():
    ftml_input = "007.5"
    data = load(ftml_input)
    assert data == 7.5  # Ensure it is parsed correctly


# todo add tests to validate type against the schema.
