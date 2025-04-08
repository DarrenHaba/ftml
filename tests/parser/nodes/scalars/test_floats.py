from ftml import load, FTMLParseError
import pytest


# Root-level floats are no longer allowed

def test_positive_float_should_fail():
    ftml_input = "42.5"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_positive_float_with_key():
    ftml_input = "my_key = 42.5"
    data = load(ftml_input)
    assert data["my_key"] == 42.5


def test_negative_float_should_fail():
    ftml_input = "-42.5"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_negative_float_with_key():
    ftml_input = "my_key = -42.5"
    data = load(ftml_input)
    assert data["my_key"] == -42.5


def test_zero_float_should_fail():
    ftml_input = "0.0"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_zero_float_with_key():
    ftml_input = "my_key = 0.0"
    data = load(ftml_input)
    assert data["my_key"] == 0.0


def test_float_in_double_quotes_should_fail():
    ftml_input = '"42.5"'
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_float_in_double_quotes_with_key():
    ftml_input = "my_key = \"42.5\""
    data = load(ftml_input)
    assert data["my_key"] == "42.5"


def test_float_in_single_quotes_should_fail():
    ftml_input = "'42.5'"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_float_in_single_quotes_with_key():
    ftml_input = "my_key = '42.5'"
    data = load(ftml_input)
    assert data["my_key"] == "42.5"


def test_float_with_leading_zeros_should_fail():
    ftml_input = "007.5"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_float_with_leading_zeros_and_key():
    ftml_input = "my_key = 007.5"
    data = load(ftml_input)
    assert data["my_key"] == 7.5
