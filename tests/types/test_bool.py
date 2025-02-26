import pytest

from ftml import load, FTMLParseError


def test_true():
    ftml_input = "true"
    data = load(ftml_input)
    assert data is True


def test_false():
    ftml_input = "false"
    data = load(ftml_input)
    assert data is False


def test_true_uppercase():
    ftml_input = "True"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_false_uppercase():
    ftml_input = "False"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_true_in_double_quotes():
    ftml_input = '"true"'
    data = load(ftml_input)
    assert data == "true"


def test_false_in_double_quotes():
    ftml_input = '"false"'
    data = load(ftml_input)
    assert data == "false"


def test_true_in_single_quotes():
    ftml_input = "'true'"
    data = load(ftml_input)
    assert data == "true"


def test_false_in_single_quotes():
    ftml_input = "'false'"
    data = load(ftml_input)
    assert data == "false"


def test_true_with_extra_whitespace():
    ftml_input = "  true  "
    data = load(ftml_input)
    assert data is True  # Ensure trimming doesn't break parsing


def test_false_with_extra_whitespace():
    ftml_input = "  false  "
    data = load(ftml_input)
    assert data is False  # Ensure trimming doesn't break parsing


# todo add tests to validate type against the schema.
