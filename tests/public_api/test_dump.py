import logging
import pytest
from io import StringIO
from unittest.mock import patch, mock_open

import ftml
from ftml import logger
from ftml.exceptions import FTMLValidationError, FTMLEncodingError

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_dump_empty_dict():
    """Test dumping an empty dictionary"""
    data = {}
    result = ftml.dump(data)
    assert result == ""


def test_dump_scalar_types():
    """Test dumping all scalar types"""
    data = {
        "string_value": "test",
        "int_value": 42,
        "float_value": 3.14,
        "true_value": True,
        "false_value": False,
        "null_value": None
    }

    result = ftml.dump(data)

    # Parse back the result to verify it matches the original data
    parsed_data = ftml.load(result)
    assert parsed_data == data


def test_dump_with_special_characters():
    """Test dumping FTML with special characters and escapes"""
    data = {
        "escape_quotes": 'Quote "inside" string',
        "escape_backslash": 'Backslash \\ character',
        "escape_newline": 'Line 1\nLine 2',
        "escape_tab": 'Text\tTabbed',
        "unicode_char": 'Unicode: ⚡ ♥ 🚀'
    }

    result = ftml.dump(data)

    # Parse back the result to verify it matches the original data
    parsed_data = ftml.load(result)
    assert parsed_data == data


def test_dump_nested_collections():
    """Test dumping deeply nested FTML structures"""
    data = {
        "deeply_nested": {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "value": "deep"
                            }
                        }
                    }
                }
            }
        },
        "mixed_nesting": {
            "array": [
                {
                    "nested_obj": {
                        "list": [
                            1,
                            [2, 3],
                            {"value": 4}
                        ]
                    }
                }
            ]
        }
    }

    result = ftml.dump(data)

    # Parse back the result to verify it matches the original data
    parsed_data = ftml.load(result)
    assert parsed_data == data


def test_dump_to_string():
    """Test dumping to a string"""
    data = {"name": "Test", "value": 42}
    result = ftml.dump(data)

    assert "name = \"Test\"" in result
    assert "value = 42" in result


def test_dump_to_file():
    """Test dumping to a file"""
    data = {"name": "Test", "value": 42}

    # Mock the open function
    m = mock_open()
    with patch('builtins.open', m):
        ftml.dump(data, "output.ftml")

    # Check that open was called and write was called with correct content
    m.assert_called_once_with('output.ftml', 'w', encoding='utf-8')
    handle = m()

    # Check that file content contains our data (using multiple asserts for more readable failure)
    write_args = [call.args[0] for call in handle.write.call_args_list]
    assert any('name = "Test"' in arg for arg in write_args), "Expected 'name = \"Test\"' in written content"
    assert any('value = 42' in arg for arg in write_args), "Expected 'value = 42' in written content"


def test_dump_to_file_object():
    """Test dumping to a file-like object"""
    data = {"name": "Test", "value": 42}
    file_obj = StringIO()

    ftml.dump(data, file_obj)

    # Check file object contains the correct content
    content = file_obj.getvalue()
    assert "name = \"Test\"" in content
    assert "value = 42" in content


def test_dump_with_schema():
    """Test dumping with schema validation"""
    schema_content = """
    id: int<min=1>
    name: str<min_length=2>
    tags?: [str]
    """

    # Valid data
    valid_data = {
        "id": 123,
        "name": "Test",
        "tags": ["tag1", "tag2"]
    }

    # Invalid data
    invalid_data1 = {
        "id": 0,  # Too small
        "name": "Test"
    }

    invalid_data2 = {
        "id": 123,
        "name": "A"  # Too short
    }

    # Test with valid data
    result = ftml.dump(valid_data, schema=schema_content)
    assert "id = 123" in result
    assert "name = \"Test\"" in result

    # Test with invalid data
    with pytest.raises(FTMLValidationError):
        ftml.dump(invalid_data1, schema=schema_content)

    with pytest.raises(FTMLValidationError):
        ftml.dump(invalid_data2, schema=schema_content)


def test_dump_with_encoding():
    """Test dumping with encoding specification"""
    data = {
        "ftml_encoding": "utf-8",
        "value": "test"
    }

    result = ftml.dump(data)
    assert "ftml_encoding = \"utf-8\"" in result
    assert "value = \"test\"" in result

    # Test with invalid encoding
    invalid_data = {
        "ftml_encoding": "invalid-encoding",
        "value": "test"
    }

    with pytest.raises(FTMLEncodingError):
        ftml.dump(invalid_data)


# todo fix bug, key "null" when dumped loses the quotes, so when we load: `null = null`
# todo Keys aren't allowed to be existing types, str, float, null, so we get an error. 
# def test_round_trip_complex_data():
#     """Test round-trip (dump then load) of complex data"""
#     original_data = {
#         "string": "Hello, world!",
#         "integer": 42,
#         "float": 3.14159,
#         "boolean": True,
#         "null": None,
#         "array": [1, 2, 3, 4, 5],
#         "object": {
#             "nested_string": "Nested value",
#             "nested_array": ["a", "b", "c"],
#             "nested_object": {
#                 "deep": "Very deep"
#             }
#         },
#         "mixed_array": [
#             "string",
#             123,
#             False,
#             None,
#             [1, 2],
#             {"key": "value"}
#         ]
#     }
# 
#     # Dump the data to FTML string
#     ftml_string = ftml.dump(original_data)
#     print(ftml_string)
# 
#     # Load the FTML string back
#     loaded_data = ftml.load(ftml_string)
# 
#     # Compare original and loaded data
#     assert loaded_data == original_data


def test_dump_with_comments():
    """Test that comments are preserved when dumping"""
    # First load data with comments
    ftml_with_comments = """
    //! Document inner doc comment
    
    /// Outer doc comment for name
    name = "test"  // Inline comment
    
    // Leading comment for object
    object = {  // Inline comment for object
        //! Inner doc comment for object
        key = "value"  // Inline comment for key
    }
    """

    # Load with preserved comments
    data = ftml.load(ftml_with_comments)

    # Dump with include_comments=True (default)
    result_with_comments = ftml.dump(data)

    # Verify comments are preserved
    assert "//! Document inner doc comment" in result_with_comments
    assert "/// Outer doc comment for name" in result_with_comments
    assert "// Inline comment" in result_with_comments
    assert "// Leading comment for object" in result_with_comments
    assert "//! Inner doc comment for object" in result_with_comments

    # Dump with include_comments=False
    result_without_comments = ftml.dump(data, include_comments=False)

    # Verify comments are not included
    assert "//! Document inner doc comment" not in result_without_comments
    assert "/// Outer doc comment for name" not in result_without_comments
    assert "// Inline comment" not in result_without_comments


def test_dump_with_ftml_dict():
    """Test dumping with FTMLDict custom class"""
    # Create an instance of FTMLDict
    data = ftml.FTMLDict({
        "name": "Test",
        "value": 42
    })

    result = ftml.dump(data)

    assert "name = \"Test\"" in result
    assert "value = 42" in result


def test_dump_list_with_trailing_comma():
    """Test that lists are serialized correctly, possibly with trailing commas"""
    data = {
        "simple_list": [1, 2, 3],
        "empty_list": []
    }

    result = ftml.dump(data)

    # Load the result back to verify
    parsed_data = ftml.load(result)
    assert parsed_data == data


def test_dump_empty_collections():
    """Test dumping empty collections"""
    data = {
        "empty_object": {},
        "empty_array": []
    }

    result = ftml.dump(data)

    # Verify the format of empty collections
    assert "empty_object = {}" in result
    assert "empty_array = []" in result

    # Verify round-trip works
    parsed_data = ftml.load(result)
    assert parsed_data == data


def test_dump_multiline_strings():
    """Test dumping strings with line breaks"""
    data = {
        "multiline": "Line 1\nLine 2\nLine 3"
    }

    result = ftml.dump(data)

    # Verify the multiline string is properly quoted and escaped
    assert 'multiline = "Line 1\\nLine 2\\nLine 3"' in result.replace("\r\n", "\n")

    # Verify round-trip works
    parsed_data = ftml.load(result)
    assert parsed_data["multiline"] == "Line 1\nLine 2\nLine 3"


def test_dump_with_strict_schema():
    """Test dumping with strict schema validation"""
    schema_content = """
    name: str
    value: int
    """

    # Valid data with exact schema fields
    valid_data = {
        "name": "Test",
        "value": 42
    }

    # Data with extra fields
    extra_fields_data = {
        "name": "Test",
        "value": 42,
        "extra": "Not in schema"
    }

    # Test with strict=True (default)
    result_strict = ftml.dump(valid_data, schema=schema_content)
    assert "name = \"Test\"" in result_strict

    with pytest.raises(FTMLValidationError):
        ftml.dump(extra_fields_data, schema=schema_content)

    # Test with strict=False
    result_non_strict = ftml.dump(extra_fields_data, schema=schema_content, strict=False)
    assert "name = \"Test\"" in result_non_strict
    assert "extra = \"Not in schema\"" in result_non_strict