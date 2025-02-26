from ftml import load


def test_positive_int():
    ftml_input = "42"
    data = load(ftml_input)
    assert data == 42


def test_negative_int():
    ftml_input = "-42"
    data = load(ftml_input)
    assert data == -42


def test_zero_int():
    ftml_input = "0"
    data = load(ftml_input)
    assert data == 0


def test_int_in_double_quotes():
    ftml_input = '"42"'
    data = load(ftml_input)
    assert data == "42"


def test_int_in_single_quotes():
    ftml_input = "'42'"
    data = load(ftml_input)
    assert data == '42'


def test_int_with_leading_zeros():
    ftml_input = "007"
    data = load(ftml_input)
    assert data == 7  # Ensure it is parsed correctly


# todo add tests to validate type against the schema.
