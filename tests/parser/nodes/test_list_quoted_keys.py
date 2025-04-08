import pytest

from ftml import load, FTMLParseError


def test_object_with_double_quoted_keys():
    """Test objects with double-quoted keys."""
    ftml_input = 'obj = { "quoted key" = "value", "another-key" = 42 }'
    data = load(ftml_input)
    assert data["obj"] == {"quoted key": "value", "another-key": 42}


def test_object_with_single_quoted_keys():
    """Test objects with single-quoted keys."""
    ftml_input = "obj = { 'quoted key' = 'value', 'another-key' = 42 }"
    data = load(ftml_input)
    assert data["obj"] == {"quoted key": "value", "another-key": 42}


def test_object_with_mixed_quoted_keys():
    """Test objects with a mix of quoted and unquoted keys."""
    ftml_input = 'obj = { normal = "value", "quoted key" = 42, \'single-quoted\' = true }'
    data = load(ftml_input)
    assert data["obj"] == {"normal": "value", "quoted key": 42, "single-quoted": True}


def test_root_level_quoted_key():
    """Test quoted keys at the root level."""
    ftml_input = '"quoted key" = "value"\n\'single-quoted\' = 42'
    data = load(ftml_input)
    assert data == {"quoted key": "value", "single-quoted": 42}


def test_double_quoted_key_with_escapes():
    """Test double-quoted keys with escape sequences."""
    ftml_input = '"key\\nwith\\tescapes" = "value"'
    data = load(ftml_input)
    # Double quotes support escape sequences
    assert list(data.keys())[0] == "key\nwith\tescapes"


def test_single_quoted_key_with_escapes():
    """Test single-quoted keys with escape sequences."""
    ftml_input = "'key\\nwith\\tescapes' = 'value'"
    data = load(ftml_input)
    # Single quotes treat content literally
    assert list(data.keys())[0] == "key\\nwith\\tescapes"


def test_double_quoted_key_with_quotes():
    """Test double-quoted keys containing quotes."""
    ftml_input = '"key with \\"quotes\\"" = "value"'
    data = load(ftml_input)
    assert list(data.keys())[0] == 'key with "quotes"'


def test_single_quoted_key_with_quotes():
    """Test single-quoted keys containing quotes."""
    ftml_input = "'key with ''quotes''' = 'value'"
    data = load(ftml_input)
    assert list(data.keys())[0] == "key with 'quotes'"


def test_single_quoted_key_with_unicode():
    """Test single-quoted keys with Unicode characters."""
    ftml_input = "'ключ' = 'значение'"
    data = load(ftml_input)
    assert data["ключ"] == "значение"


def test_double_quoted_key_with_unicode():
    """Test double-quoted keys with Unicode characters."""
    ftml_input = '"schlüssel" = "wert"'
    data = load(ftml_input)
    assert data["schlüssel"] == "wert"


def test_quoted_key_in_nested_object():
    """Test quoted keys in nested objects."""
    ftml_input = """
    outer = {
        inner = {
            "quoted key" = "value",
            'another key' = 42
        }
    }
    """
    data = load(ftml_input)
    assert data["outer"]["inner"]["quoted key"] == "value"
    assert data["outer"]["inner"]["another key"] == 42


def test_invalid_key_without_quotes():
    """Test that keys with spaces require quotes."""
    ftml_input = 'invalid key = "value"'
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_invalid_key_with_unclosed_quotes():
    """Test that unclosed quoted keys are rejected."""
    ftml_input = '"unclosed key = "value"'
    with pytest.raises(FTMLParseError):
        load(ftml_input)
