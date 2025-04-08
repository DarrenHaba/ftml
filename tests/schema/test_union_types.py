"""
Test module for union type parsing and validation.
"""

import logging

from ftml import SchemaParser
from ftml.logger import logger
from ftml.schema import SchemaValidator
from ftml.schema.schema_union_parser import UnionParser

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_union_parser():
    """Test the union parser directly."""
    union_parser = UnionParser()

    # Test simple union splitting
    union_str = "str | int | bool"
    parts = union_parser.split_union_parts(union_str)
    assert len(parts) == 3
    assert parts[0] == "str"
    assert parts[1] == "int"
    assert parts[2] == "bool"

    # Test union with constraints
    union_str = "str<min_length=3> | int<min=0>"
    parts = union_parser.split_union_parts(union_str)
    assert len(parts) == 2
    assert parts[0] == "str<min_length=3>"
    assert parts[1] == "int<min=0>"

    # Test union with complex types
    union_str = "str | [int] | {name: str}"
    parts = union_parser.split_union_parts(union_str)
    assert len(parts) == 3
    assert parts[0] == "str"
    assert parts[1] == "[int]"
    assert parts[2] == "{name: str}"

    # Test nested unions inside complex types
    union_str = "str | [int | str] | {type: str | int}"
    parts = union_parser.split_union_parts(union_str)
    assert len(parts) == 3
    assert parts[0] == "str"
    assert parts[1] == "[int | str]"
    assert parts[2] == "{type: str | int}"


def test_basic_union_parsing():
    """Test basic union type parsing in schemas."""
    parser = SchemaParser()

    # Test basic union of scalar types
    schema = """
    id: str | int
    """
    result = parser.parse(schema)

    assert "id" in result
    assert len(result["id"].subtypes) == 2
    assert result["id"].subtypes[0].type_name == "str"
    assert result["id"].subtypes[1].type_name == "int"

    # Test union with more than two types
    schema = """
    value: str | int | float | bool | null
    """
    result = parser.parse(schema)

    assert "value" in result
    assert len(result["value"].subtypes) == 5
    assert result["value"].subtypes[0].type_name == "str"
    assert result["value"].subtypes[1].type_name == "int"
    assert result["value"].subtypes[2].type_name == "float"
    assert result["value"].subtypes[3].type_name == "bool"
    assert result["value"].subtypes[4].type_name == "null"

    # Test union with default value
    schema = """
    status: str | null = null
    """
    result = parser.parse(schema)

    assert "status" in result
    assert len(result["status"].subtypes) == 2
    assert result["status"].has_default
    assert result["status"].default is None


def test_complex_union_parsing():
    """Test parsing of unions with complex types."""
    parser = SchemaParser()

    # Test union with list and scalar
    schema = """
    data: str | [int]
    """
    result = parser.parse(schema)

    assert "data" in result
    assert len(result["data"].subtypes) == 2
    assert result["data"].subtypes[0].type_name == "str"
    assert result["data"].subtypes[1].item_type.type_name == "int"

    # Test union with object and scalar
    schema = """
    address: str | {
        street: str,
        city: str
    }
    """
    result = parser.parse(schema)

    assert "address" in result
    assert len(result["address"].subtypes) == 2
    assert result["address"].subtypes[0].type_name == "str"
    assert "street" in result["address"].subtypes[1].fields
    assert "city" in result["address"].subtypes[1].fields

    # Test union with all complex types
    schema = """
    content: [str] | {any} | {
        type: str,
        value: any
    }
    """
    result = parser.parse(schema)

    assert "content" in result
    assert len(result["content"].subtypes) == 3
    assert result["content"].subtypes[0].item_type.type_name == "str"
    assert result["content"].subtypes[1].pattern_value_type.type_name == "any"
    assert "type" in result["content"].subtypes[2].fields
    assert "value" in result["content"].subtypes[2].fields


def test_nested_union_parsing():
    """Test parsing of nested union types."""
    parser = SchemaParser()

    # Test union within a list
    schema = """
    items: [str | int]
    """
    result = parser.parse(schema)

    assert "items" in result
    assert len(result["items"].item_type.subtypes) == 2
    assert result["items"].item_type.subtypes[0].type_name == "str"
    assert result["items"].item_type.subtypes[1].type_name == "int"

    # Test union within an object
    schema = """
    data: {
        id: str | int,
        value: float | null
    }
    """
    result = parser.parse(schema)

    assert "data" in result
    assert len(result["data"].fields["id"].subtypes) == 2
    assert result["data"].fields["id"].subtypes[0].type_name == "str"
    assert result["data"].fields["id"].subtypes[1].type_name == "int"
    assert len(result["data"].fields["value"].subtypes) == 2
    assert result["data"].fields["value"].subtypes[0].type_name == "float"
    assert result["data"].fields["value"].subtypes[1].type_name == "null"


def test_union_validation():
    """Test validation of union types."""
    parser = SchemaParser()

    # Define a schema with union types
    schema = """
    data: {
        id: str | int,
        value: float | null,
        content: str | {
            text: str,
            format: str
        },
        items: [str | int]
    }
    """

    # Parse the schema
    schema_objects = parser.parse(schema)

    # Create test data with all possible union variants
    valid_data = {
        "data": {
            "id": "abc123",  # Using string variant
            "value": 3.14,   # Using float variant
            "content": {     # Using object variant
                "text": "Hello",
                "format": "plaintext"
            },
            "items": ["a", 1, "b", 2]  # Mixed string and int
        }
    }

    # Validate the data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)

    # Should be valid
    assert not errors, f"Expected no errors, got: {errors}"

    # Create alternative valid data with different variants
    alt_valid_data = {
        "data": {
            "id": 12345,     # Using int variant
            "value": None,   # Using null variant
            "content": "Raw text content",  # Using string variant
            "items": ["a", "b", "c"]  # All strings
        }
    }

    # Validate the alternative data
    errors = validator.validate(alt_valid_data)

    # Should also be valid
    assert not errors, f"Expected no errors for alternative data, got: {errors}"

    # Create invalid data
    invalid_data = {
        "data": {
            "id": True,      # Neither string nor int
            "value": "zero", # Neither float nor null
            "content": 123,  # Neither string nor object
            "items": [True, False]  # Neither string nor int
        }
    }

    # Validate the invalid data
    errors = validator.validate(invalid_data)

    # Should be invalid with multiple errors
    assert len(errors) == 5, f"Expected 4 errors, got: {len(errors)} - {errors}"

    # Check for specific error messages
    error_str = "\n".join(errors)
    assert "id" in error_str and "does not match any allowed types" in error_str
    assert "value" in error_str and "does not match any allowed types" in error_str
    assert "content" in error_str and "does not match any allowed types" in error_str
    assert "items" in error_str and "does not match any allowed types" in error_str


def test_union_with_constraints():
    """Test union types with constraints on subtypes."""
    parser = SchemaParser()

    # Define a schema with constrained union types
    schema = """
    data: {
        id: str<min_length=3> | int<min=1000>,
        status: str<enum=["active", "inactive"]> | null
    }
    """

    # Parse the schema
    schema_objects = parser.parse(schema)

    # Valid data with constraints satisfied
    valid_data = {
        "data": {
            "id": "ABC123",  # String with sufficient length
            "status": "active"  # String in enum
        }
    }

    # Validate the data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)

    # Should be valid
    assert not errors, f"Expected no errors, got: {errors}"

    # Alternative valid data
    alt_valid_data = {
        "data": {
            "id": 2000,  # Int above minimum
            "status": None  # Using null variant
        }
    }

    # Validate the alternative data
    errors = validator.validate(alt_valid_data)

    # Should also be valid
    assert not errors, f"Expected no errors for alternative data, got: {errors}"

    # Invalid data that violates constraints
    invalid_data = {
        "data": {
            "id": "AB",  # String too short
            "status": "pending"  # String not in enum
        }
    }

    # Validate the invalid data
    errors = validator.validate(invalid_data)

    # Should have errors for both fields
    assert len(errors) == 2, f"Expected 2 errors, got: {len(errors)} - {errors}"

    # More invalid data
    more_invalid_data = {
        "data": {
            "id": 500,  # Int too small
            "status": False  # Neither string in enum nor null
        }
    }

    # Validate the invalid data
    errors = validator.validate(more_invalid_data)

    # Should have errors for both fields
    assert len(errors) == 2, f"Expected 2 errors, got: {len(errors)} - {errors}"
