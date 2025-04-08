import pytest

from ftml import load, dump, FTMLError, FTMLParseError


# Root-level strings are no longer allowed, all should fail

def test_str_double_quote_with_key():
    ftml_input = 'my_var = "hello"'
    data = load(ftml_input)
    assert data["my_var"] == "hello"


def test_str_double_quote_should_fail():
    ftml_input = '"hello"'
    with pytest.raises(FTMLError):
        load(ftml_input)


def test_str_single_quote_should_fail():
    ftml_input = "'hello'"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_str_single_quote_with_key():
    ftml_input = "my_var = 'hello'"
    data = load(ftml_input)
    assert data["my_var"] == "hello"


def test_str_escape_single_quote_with_key():
    ftml_input = 'my_var = "who\'s"'
    data = load(ftml_input)
    assert data["my_var"] == "who's"


def test_str_escape_double_quote_with_key():
    ftml_input = "my_var = 'He said \"hello\"'"
    data = load(ftml_input)
    assert data["my_var"] == 'He said "hello"'


def test_str_escape_both_quotes_should_fail():
    ftml_input = 'key = "He said \"who\'s there?\""'
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_str_escape_backslash_with_key():
    ftml_input = 'my_key = "This is a backslash: \\\\"'
    data = load(ftml_input)
    assert data["my_key"] == "This is a backslash: \\"


def test_str_no_quotes_should_fail():
    ftml_input = "key = value"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_str_escape_sequence_in_double_quotes_with_key():
    ftml_input = 'my_key = "Line1\nLine2"'
    data = load(ftml_input)
    assert data["my_key"] == "Line1\nLine2"


def test_str_escape_sequence_in_single_quotes_with_key():
    ftml_input = "my_key = 'Line1\\nLine2'"
    data = load(ftml_input)
    assert data["my_key"] == "Line1\\nLine2"


def test_str_escape_tab_in_double_quotes_with_key():
    ftml_input = 'my_key = "Column1\\tColumn2"'
    data = load(ftml_input)
    assert data["my_key"] == "Column1\tColumn2"


def test_str_escape_tab_in_single_quotes_with_key():
    ftml_input = "my_key = 'Column1\\tColumn2'"
    data = load(ftml_input)
    assert data["my_key"] == "Column1\\tColumn2"


def test_str_escape_backslash_in_double_quotes_with_key():
    ftml_input = 'my_key = "C:\\\\Users\\\\Test"'
    data = load(ftml_input)
    assert data["my_key"] == "C:\\Users\\Test"


def test_str_escape_backslash_in_single_quotes_with_key():
    ftml_input = "my_key = 'C:\\\\Users\\\\Test'"
    data = load(ftml_input)
    assert data["my_key"] == "C:\\\\Users\\\\Test"






def test_string_escaping():
    """Test that all escape sequences are properly handled in double-quoted strings."""
    # Define strings with different escape sequences
    test_cases = {
        "newlines": "Line 1\nLine 2\nLine 3",
        "tabs": "Tab\tSeparated\tValues",
        "carriage_returns": "Windows\r\nStyle\r\nNewlines",
        "quotes": "String with \"double quotes\"",
        "backslashes": "Path with backslashes: C:\\Windows\\System32",
        "mixed": "Mixed \"quotes\", \ttabs and\nnewlines\r\nand Windows newlines",
        "control_chars": "Bell: \a, Backspace: \b, Form feed: \f, Vertical tab: \v"
    }

    # Create test data
    data = dict(test_cases)

    # Serialize to FTML
    result = dump(data)

    # Verify escape sequences are correctly serialized
    assert 'newlines = "Line 1\\nLine 2\\nLine 3"' in result.replace("\r\n", "\n")
    assert 'tabs = "Tab\\tSeparated\\tValues"' in result.replace("\r\n", "\n")
    assert 'carriage_returns = "Windows\\r\\nStyle\\r\\nNewlines"' in result.replace("\r\n", "\n")
    assert 'quotes = "String with \\"double quotes\\""' in result.replace("\r\n", "\n")
    assert 'backslashes = "Path with backslashes: C:\\\\Windows\\\\System32"' in result.replace("\r\n", "\n")
    assert 'mixed = "Mixed \\"quotes\\", \\ttabs and\\nnewlines\\r\\nand Windows newlines"' in result.replace("\r\n", "\n")
    assert 'control_chars = "Bell: \\a, Backspace: \\b, Form feed: \\f, Vertical tab: \\v"' in result.replace("\r\n", "\n")

    # Verify round-trip works
    parsed_data = load(result)
    for key, expected in test_cases.items():
        assert parsed_data[key] == expected, f"Failed on key: {key}"

def test_single_quoted_strings():
    """Test that single-quoted strings are handled properly."""
    # FTML should preserve the distinction between single and double quotes if specified
    ftml_content = "single_quoted = 'This is a ''single quoted'' string'\ndouble_quoted = \"This is a \\\"double quoted\\\" string\""

    data = load(ftml_content)
    assert data["single_quoted"] == "This is a 'single quoted' string"
    assert data["double_quoted"] == "This is a \"double quoted\" string"

def test_multiline_string_representation():
    """Test that multiline strings are properly formatted in the serialized output."""
    data = {
        "short_multiline": "Just\ntwo\nlines",
        "long_multiline": "This is a much longer string\nwith multiple lines\nthat should be properly escaped\nwhen serialized to FTML"
    }

    result = dump(data)

    # The serialized output should contain the properly escaped strings
    assert 'short_multiline = "Just\\ntwo\\nlines"' in result.replace("\r\n", "\n")
    assert 'long_multiline = "This is a much longer string\\nwith multiple lines\\nthat should be properly escaped\\nwhen serialized to FTML"' in result.replace("\r\n", "\n")

    # Round-trip check
    parsed_data = load(result)
    assert parsed_data["short_multiline"] == data["short_multiline"]
    assert parsed_data["long_multiline"] == data["long_multiline"]