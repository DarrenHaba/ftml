import pytest

from ftml import load, FTMLParseError


def test_str_double_quote():
    ftml_input = '"hello"'
    data = load(ftml_input)
    assert data == "hello"


def test_str_single_quote():
    ftml_input = "'hello'"
    data = load(ftml_input)
    assert data == "hello"


def test_str_escape_single_quote():
    ftml_input = '"who\'s"'
    data = load(ftml_input)
    assert data == "who's"


def test_str_escape_double_quote():
    ftml_input = "'He said \"hello\"'"
    data = load(ftml_input)
    assert data == 'He said "hello"'


def test_str_escape_both_quotes():
    ftml_input = '"He said \\"who\'s there?\\""'
    data = load(ftml_input)
    assert data == 'He said "who\'s there?"'


def test_str_escape_backslash():
    ftml_input = '"This is a backslash: \\\\"'
    data = load(ftml_input)
    assert data == "This is a backslash: \\"


def test_str_no_quotes():
    ftml_input = 'hello'
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_str_escape_sequence_in_double_quotes():
    ftml_input = '"Line1\nLine2"'
    data = load(ftml_input)
    assert data == "Line1\nLine2"  # \n should be interpreted as a newline


def test_str_escape_sequence_in_single_quotes():
    ftml_input = "'Line1\\nLine2'"
    data = load(ftml_input)
    assert data == "Line1\\nLine2"  # No escape processing; should be literal


def test_str_escape_tab_in_double_quotes():
    ftml_input = '"Column1\\tColumn2"'
    data = load(ftml_input)
    assert data == "Column1\tColumn2"  # \t should be interpreted as a tab


def test_str_escape_tab_in_single_quotes():
    ftml_input = "'Column1\\tColumn2'"
    data = load(ftml_input)
    assert data == "Column1\\tColumn2"  # No escape processing; should be literal


def test_str_escape_backslash_in_double_quotes():
    ftml_input = '"C:\\\\Users\\\\Test"'
    data = load(ftml_input)
    assert data == "C:\\Users\\Test"  # Double backslashes should resolve to single backslashes


def test_str_escape_backslash_in_single_quotes():
    ftml_input = "'C:\\\\Users\\\\Test'"
    data = load(ftml_input)
    assert data == "C:\\\\Users\\\\Test"  # No escape processing; should remain double backslashes


# todo add tests to validate type against the schema.
