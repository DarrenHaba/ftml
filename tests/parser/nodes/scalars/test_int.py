from ftml import load, FTMLParseError
import pytest


# Root-level integers are no longer allowed

def test_positive_int_should_fail():
    ftml_input = "42"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_positive_int_with_key():
    ftml_input = "my_key = 42"
    data = load(ftml_input)
    assert data["my_key"] == 42  # Now passes


def test_negative_int_should_fail():
    ftml_input = "-42"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_negative_int_with_key():
    ftml_input = "my_key = -42"
    data = load(ftml_input)
    assert data["my_key"] == -42


def test_zero_int_should_fail():
    ftml_input = "0"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_zero_int_with_key():
    ftml_input = "my_key = 0"
    data = load(ftml_input)
    assert data["my_key"] == 0


def test_int_in_double_quotes_should_fail():
    ftml_input = '"42"'
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_int_in_double_quotes_with_key():
    ftml_input = "my_key = \"42\""
    data = load(ftml_input)
    assert data["my_key"] == "42"


def test_int_in_single_quotes_should_fail():
    ftml_input = "'42'"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_int_in_single_quotes_with_key():
    ftml_input = "my_key = '42'"
    data = load(ftml_input)
    assert data["my_key"] == "42"


def test_int_with_leading_zeros_should_fail():
    ftml_input = "007"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_int_with_leading_zeros_and_key():
    ftml_input = "my_key = 007"
    data = load(ftml_input)
    assert data["my_key"] == 7
