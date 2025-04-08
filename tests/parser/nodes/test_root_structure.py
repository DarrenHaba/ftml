import pytest
from ftml import load, FTMLParseError


# --------------------------
# Valid Root-Level Tests (No Commas, Newline Separation)
# --------------------------

def test_valid_root_key_value_pairs_newline_separated():
    """Test valid root-level key-value pairs separated by newlines."""
    data = load('''
        theme = "dark"
        log_level = "info"
    ''')
    assert data == {"theme": "dark", "log_level": "info"}


def test_valid_root_complex_values():
    """Test valid root-level key-value pairs with complex values."""
    data = load('''
        list = [1, 2, 3]
        obj = { name = "test" }
    ''')
    assert data == {
        "list": [1, 2, 3],
        "obj": {"name": "test"}
    }


def test_valid_root_mixed_types():
    """Test valid root-level key-value pairs with different value types."""
    data = load('''
        string_value = "text"
        int_value = 42
        float_value = 3.14
        bool_value = true
        null_value = null
    ''')
    assert data == {
        "string_value": "text",
        "int_value": 42,
        "float_value": 3.14,
        "bool_value": True,
        "null_value": None
    }


# --------------------------
# Valid Object Tests (Commas Required Between Items)
# --------------------------

def test_valid_inline_object_with_commas():
    """Test valid inline object with comma-separated key-value pairs."""
    data = load('config = { theme = "dark", log_level = "info" }')
    assert data == {"config": {"theme": "dark", "log_level": "info"}}


def test_valid_inline_object_with_trailing_comma():
    """Test valid inline object with trailing comma."""
    data = load('config = { theme = "dark", log_level = "info", }')
    assert data == {"config": {"theme": "dark", "log_level": "info"}}


def test_valid_multi_line_object_with_commas():
    """Test valid multi-line object with comma-separated key-value pairs."""
    data = load('''
        config = {
            theme = "dark",
            log_level = "info",
        }
    ''')
    assert data == {"config": {"theme": "dark", "log_level": "info"}}


def test_valid_mixed_line_object():
    """Test valid object with mixed inline and multi-line formatting."""
    data = load('''
        config = { theme = "dark",
                   log_level = "info", }
    ''')
    assert data == {"config": {"theme": "dark", "log_level": "info"}}


# --------------------------
# Invalid Root-Level Tests
# --------------------------

def test_invalid_root_comma_separated():
    """Test that root-level key-value pairs separated by commas are invalid."""
    with pytest.raises(FTMLParseError):
        load('key1 = "val1", key2 = "val2"')  # Root commas forbidden


def test_invalid_root_no_newline_separation():
    """Test that root-level key-value pairs without newline separation are invalid."""
    with pytest.raises(FTMLParseError):
        load('key1 = "val1" key2 = "val2"')  # Missing newline between root items


def test_invalid_root_trailing_comma():
    """Test that root-level key-value pairs with trailing commas are invalid."""
    with pytest.raises(FTMLParseError):
        load('''
            key1 = "val1",
            key2 = "val2"
        ''')  # Comma after root item


# --------------------------
# Invalid Object Tests
# --------------------------

def test_invalid_inline_object_missing_comma():
    """Test that inline object with missing comma between items is invalid."""
    with pytest.raises(FTMLParseError) as e:
        load('config = { theme = "dark" log_level = "info" }')
    assert "Expected ',' or '}' after object item" in str(e.value)


def test_invalid_multi_line_object_missing_comma():
    """Test that multi-line object with missing comma between items is invalid."""
    with pytest.raises(FTMLParseError) as e:
        load('''
            config = {
                theme = "dark"
                log_level = "info"
            }
        ''')  # Missing comma after "dark"
    assert "Expected ',' or '}' after object item" in str(e.value)


# --------------------------
# Edge Cases
# --------------------------

def test_valid_empty_object():
    """Test valid empty object."""
    data = load('empty = {}')
    assert data == {"empty": {}}


def test_valid_single_item_object_no_comma():
    """Test valid object with a single item and no comma."""
    data = load('config = { theme = "dark" }')
    assert data == {"config": {"theme": "dark"}}


def test_valid_single_item_object_with_comma():
    """Test valid object with a single item and trailing comma."""
    data = load('config = { theme = "dark", }')
    assert data == {"config": {"theme": "dark"}}


def test_valid_whitespace_between_root_items():
    """Test valid root structure with extra whitespace between items."""
    data = load('''
        key1 = "value1"
        
        
        key2 = "value2"
    ''')
    assert data == {"key1": "value1", "key2": "value2"}


def test_valid_indentation_variations():
    """Test valid root structure with different indentation levels."""
    data = load('''
    key1 = "value1"
        key2 = "value2"
          key3 = "value3"
    ''')
    assert data == {"key1": "value1", "key2": "value2", "key3": "value3"}
