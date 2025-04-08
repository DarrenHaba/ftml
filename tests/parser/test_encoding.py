import pytest
import os
import tempfile
from ftml import load, dump
from ftml.exceptions import FTMLEncodingError


def test_load_default_encoding():
    """Test loading a document with default encoding."""
    data = load('key = "value"')
    assert data == {"key": "value"}


def test_load_utf8_encoding():
    """Test loading a document with UTF-8 encoding."""
    data = load('ftml_encoding = "utf-8"\nkey = "value"')
    assert data == {"ftml_encoding": "utf-8", "key": "value"}


def test_load_latin1_encoding():
    """Test loading a document with Latin-1 encoding."""
    data = load('ftml_encoding = "latin-1"\nkey = "value"')
    assert data == {"ftml_encoding": "latin-1", "key": "value"}


def test_load_unsupported_encoding():
    """Test loading a document with an unsupported encoding."""
    with pytest.raises(FTMLEncodingError) as e:
        load('ftml_encoding = "unsupported"\nkey = "value"')

    assert "Unsupported encoding" in str(e.value)


def test_load_non_string_encoding():
    """Test loading a document with a non-string encoding."""
    with pytest.raises(FTMLEncodingError) as e:
        load('ftml_encoding = 123\nkey = "value"')

    assert "Invalid encoding" in str(e.value)
    assert "Encoding must be a string" in str(e.value)


def test_load_file_with_specified_encoding():
    """Test loading a file with a specified encoding."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ftml") as f:
        f.write('ftml_encoding = "utf-8"\nkey = "value with ñ"'.encode('utf-8'))

    try:
        data = load(f.name)
        assert data == {"ftml_encoding": "utf-8", "key": "value with ñ"}
    finally:
        os.unlink(f.name)


def test_dump_with_encoding():
    """Test dumping data with a specified encoding."""
    data = {
        "ftml_encoding": "utf-8",
        "key": "value with special chars: ñáéíóú"
    }

    # Dump to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ftml") as f:
        dump(data, f.name)

    try:
        # Read it back
        with open(f.name, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that encoding is preserved
        assert 'ftml_encoding = "utf-8"' in content
        assert 'key = "value with special chars: ñáéíóú"' in content

        # Also load it through the API
        loaded_data = load(f.name)
        assert loaded_data == data
    finally:
        os.unlink(f.name)


def test_reserved_encoding_key():
    """Test that the ftml_encoding key is treated as a reserved key."""
    data = load('ftml_encoding = "utf-8"\nencoding = "custom"\nkey = "value"')

    # Both keys should be present - one is the reserved encoding key, one is a regular user key
    assert data["ftml_encoding"] == "utf-8"
    assert data["encoding"] == "custom"


def test_normalize_encoding_names():
    """Test that different variations of encoding names are normalized."""
    # These all represent the same encoding
    variations = ["utf-8", "utf8", "UTF-8", "UTF8", "utf_8"]

    for encoding in variations:
        data = load(f'ftml_encoding = "{encoding}"\nkey = "value"')
        assert data["ftml_encoding"] == encoding