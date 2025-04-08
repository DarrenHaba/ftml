import logging
import pytest
from io import StringIO
from unittest.mock import patch

import ftml
from ftml import logger
from ftml.exceptions import FTMLParseError, FTMLValidationError, FTMLEncodingError

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_load_empty_string():
    """Test loading an empty FTML string"""
    data = ftml.load("")
    assert data == {}
    print("Debug:")
    print(data)
    print(type(data))
    assert isinstance(data, ftml.FTMLDict)


def test_load_whitespace_only():
    """Test loading a string with only whitespace"""
    data = ftml.load("  \n  \t  ")
    assert data == {}


def test_load_with_syntax_error():
    """Test loading FTML with syntax errors"""
    invalid_contents = [
        "name = ",  # Missing value
        "name : 'value'",  # Using colon instead of equals
        "{ key = 'value' }",  # Missing assignment
        "array = [1, 2,]",  # Extra comma (actually valid in FTML)
        "list = [1, 2",  # Unclosed bracket
        "obj = {key = 'value'",  # Unclosed brace
        'string = "unclosed',  # Unclosed string
    ]

    for content in invalid_contents:
        if content != "array = [1, 2,]":  # This one is actually valid in FTML
            with pytest.raises(FTMLParseError):
                # Remove the match parameter entirely - we just want to verify an error is raised
                ftml.load(content)
        else:
            # This should parse without error
            data = ftml.load(content)
            assert data["array"] == [1, 2]


def test_load_scalar_types():
    """Test loading all scalar types"""
    ftml_content = """
    string_value = "test"
    single_quoted = 'test'
    int_value = 42
    float_value = 3.14
    true_value = true
    false_value = false
    null_value = null
    """

    data = ftml.load(ftml_content)

    assert data["string_value"] == "test"
    assert data["single_quoted"] == "test"
    assert data["int_value"] == 42
    assert data["float_value"] == 3.14
    assert data["true_value"] is True
    assert data["false_value"] is False
    assert data["null_value"] is None


def test_load_with_special_characters():
    """Test loading FTML with special characters and escapes"""
    ftml_content = r"""
    escape_quotes = "Quote \"inside\" string"
    escape_backslash = "Backslash \\ character"
    escape_newline = "Line 1\nLine 2"
    escape_tab = "Text\tTabbed"
    unicode_char = "Unicode: ⚡ ♥ 🚀"
    """

    data = ftml.load(ftml_content)

    assert data["escape_quotes"] == 'Quote "inside" string'
    assert data["escape_backslash"] == 'Backslash \\ character'
    assert data["escape_newline"] == 'Line 1\nLine 2'
    assert data["escape_tab"] == 'Text\tTabbed'
    assert data["unicode_char"] == 'Unicode: ⚡ ♥ 🚀'


def test_load_nested_collections():
    """Test loading deeply nested FTML structures"""
    ftml_content = """
    deeply_nested = {
        level1 = {
            level2 = {
                level3 = {
                    level4 = {
                        level5 = {
                            value = "deep"
                        }
                    }
                }
            }
        }
    }
    mixed_nesting = {
        array = [
            {
                nested_obj = {
                    list = [
                        1, 
                        [2, 3], 
                        {value = 4}
                    ]
                }
            }
        ]
    }
    """

    data = ftml.load(ftml_content)

    # Test the deeply nested object
    assert (
            data["deeply_nested"]["level1"]["level2"]["level3"]["level4"]["level5"]["value"]
            == "deep"
    )

    # Test the mixed nesting
    assert data["mixed_nesting"]["array"][0]["nested_obj"]["list"][0] == 1
    assert data["mixed_nesting"]["array"][0]["nested_obj"]["list"][1] == [2, 3]
    assert (
            data["mixed_nesting"]["array"][0]["nested_obj"]["list"][2]["value"]
            == 4
    )


def test_load_with_schema_optional_fields():
    """Test loading with a schema that has optional fields"""
    schema_content = """
    required_field: str
    optional_field?: int
    default_field: bool = false
    """

    # Valid data with all fields
    full_data = """
    required_field = "value"
    optional_field = 42
    default_field = true
    """

    # Valid data with missing optional field
    partial_data = """
    required_field = "value"
    default_field = true
    """

    # Invalid data with missing required field
    invalid_data = """
    optional_field = 42
    default_field = true
    """

    # # Test valid data with all fields
    data1 = ftml.load(full_data, schema=schema_content)
    assert data1["required_field"] == "value"
    assert data1["optional_field"] == 42
    assert data1["default_field"] is True

    # Test valid data with missing optional field
    data2 = ftml.load(partial_data, schema=schema_content)
    assert data2["required_field"] == "value"
    assert "optional_field" not in data2
    assert data2["default_field"] is True

    # Test invalid data with missing required field
    with pytest.raises(FTMLValidationError):
        ftml.load(invalid_data, schema=schema_content)


def test_load_with_complex_schema():
    """Test loading with a complex schema featuring various types and constraints"""
    schema_content = """
    id: int<min=1>
    name: str<min_length=2, max_length=100>
    email?: str<pattern="^[\\w.-]+@[\\w.-]+\\.[a-zA-Z]{2,}$">
    tags: [str]<min=1, max=5>
    metadata: {
        created: str,
        modified?: str,
        version: int = 1
    }
    settings: {str} = {}
    """

    valid_data = """
    id = 123
    name = "Test User"
    email = "user@example.com"
    tags = ["test", "user"]
    metadata = {
        created = "2023-01-01",
        modified = "2023-01-02",
        version = 2
    }
    settings = {
        theme = "dark",
        notifications = "enabled"
    }
    """

    # Test valid data
    data = ftml.load(valid_data, schema=schema_content)
    assert data["id"] == 123
    assert data["name"] == "Test User"
    assert data["email"] == "user@example.com"
    assert data["tags"] == ["test", "user"]
    assert data["metadata"]["created"] == "2023-01-01"
    assert data["metadata"]["modified"] == "2023-01-02"
    assert data["metadata"]["version"] == 2
    assert data["settings"]["theme"] == "dark"
    assert data["settings"]["notifications"] == "enabled"

    # Invalid data examples (tested individually)
    invalid_data_examples = [
        """id = 0  // ID too small
           name = "Test User"
           tags = ["test"]
           metadata = { created = "2023-01-01" }""",

        """id = 123
           name = "A"  // Name too short
           tags = ["test"]
           metadata = { created = "2023-01-01" }""",

        """id = 123
           name = "Test User"
           email = "invalid-email"  // Invalid email format
           tags = ["test"]
           metadata = { created = "2023-01-01" }""",

        """id = 123
           name = "Test User"
           tags = []  // Empty tags (min=1)
           metadata = { created = "2023-01-01" }""",

        """id = 123
           name = "Test User"
           tags = ["test"]
           metadata = {}  // Missing required 'created' field
           """
    ]

    for example in invalid_data_examples:
        with pytest.raises(FTMLValidationError):
            ftml.load(example, schema=schema_content)


def test_load_with_file_object():
    """Test loading FTML from a file-like object"""
    ftml_content = """
    name = "Test"
    value = 42
    """

    # Create a StringIO object
    file_obj = StringIO(ftml_content)

    # Mock both open and os.path.exists
    with patch('builtins.open', return_value=file_obj), \
            patch('os.path.exists', return_value=True):
        # This should work with a file path that doesn't actually exist
        # since we're mocking both the open call and os.path.exists
        data = ftml.load("fake_path.ftml")

        assert data["name"] == "Test"
        assert data["value"] == 42


def test_load_with_union_types_schema():
    """Test loading with a schema containing union types"""
    schema_content = """
    value: int | str
    collection: [int] | {str}
    complex_union: {
        type: str,
        data: int | {count: int} | [str]
    }
    """

    # Test int value for union
    int_data = """
    value = 42
    collection = [1, 2, 3]
    complex_union = {
        type = "number",
        data = 100
    }
    """

    # Test string value for union
    str_data = """
    value = "text"
    collection = {
        key1 = "value1",
        key2 = "value2"
    }
    complex_union = {
        type = "object",
        data = {
            count = 5
        }
    }
    """

    # Test array value for complex union
    array_data = """
    value = "text"
    collection = [1, 2, 3]
    complex_union = {
        type = "array",
        data = ["one", "two", "three"]
    }
    """

    # Test all valid variations
    int_result = ftml.load(int_data, schema=schema_content)
    assert int_result["value"] == 42
    assert int_result["collection"] == [1, 2, 3]
    assert int_result["complex_union"]["data"] == 100

    str_result = ftml.load(str_data, schema=schema_content)
    assert str_result["value"] == "text"
    assert str_result["collection"]["key1"] == "value1"
    assert str_result["complex_union"]["data"]["count"] == 5

    array_result = ftml.load(array_data, schema=schema_content)
    assert array_result["value"] == "text"
    assert array_result["complex_union"]["data"] == ["one", "two", "three"]


def test_load_with_encoding_specification():
    """Test loading FTML with encoding specification"""
    ftml_content = """
    ftml_encoding = "utf-8"
    value = "test"
    """

    data = ftml.load(ftml_content)
    assert data["ftml_encoding"] == "utf-8"
    assert data["value"] == "test"

    # Test with invalid encoding
    invalid_encoding = """
    ftml_encoding = "invalid-encoding"
    value = "test"
    """

    with pytest.raises(FTMLEncodingError):
        ftml.load(invalid_encoding)


def test_load_with_doc_comments():
    """Test loading FTML with documentation comments"""
    ftml_content = """
    //! Inner doc comment for the document
    
    /// Outer doc comment for name
    name = "test"  // Inline comment for name
    
    /// First outer doc comment for object
    /// Second outer doc comment for object
    object = {
        //! Inner doc comment for object
        
        /// Outer doc comment for key
        key = "value"  // Inline comment for key
    }
    """

    data = ftml.load(ftml_content)

    # Verify the parsed values
    assert data["name"] == "test"
    assert data["object"]["key"] == "value"

    # Check that comments are preserved in the AST
    assert hasattr(data, "_ast_node")
    assert hasattr(data._ast_node, "inner_doc_comments")
    assert data._ast_node.inner_doc_comments
