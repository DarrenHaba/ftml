from ftml import load, FTMLParseError
import pytest


# Root-level null values are no longer allowed

def test_null_should_fail():
    ftml_input = "null"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_null_with_key():
    ftml_input = "my_key = null"
    data = load(ftml_input)
    assert data["my_key"] is None


def test_null_in_double_quotes_should_fail():
    ftml_input = '"null"'
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_null_in_double_quotes_with_key():
    ftml_input = "my_key = \"null\""
    data = load(ftml_input)
    assert data["my_key"] == "null"


def test_null_in_single_quotes_should_fail():
    ftml_input = "'null'"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_null_in_single_quotes_with_key():
    ftml_input = "my_key = 'null'"
    data = load(ftml_input)
    assert data["my_key"] == "null"


def test_null_with_extra_whitespace_should_fail():
    ftml_input = "  null  "
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_null_with_extra_whitespace_and_key():
    ftml_input = "my_key =   null  "
    data = load(ftml_input)
    assert data["my_key"] is None
