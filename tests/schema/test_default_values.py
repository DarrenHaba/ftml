"""
Test module for default value handling in schemas.
"""

import logging
import pytest
from ftml.logger import logger
from ftml.schema.schema_parser import SchemaParser
from ftml.schema.schema_validator import SchemaValidator, apply_defaults
from ftml.schema.schema_debug import log_schema_ast

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_scalar_defaults():
    """Test default values for scalar types."""
    parser = SchemaParser()

    # Test various scalar defaults
    schema = """
    name: str = "Anonymous"
    age: int = 0
    active: bool = true
    score: float = 0.0
    data: null = null
    """

    result = parser.parse(schema)

    # Check name default
    assert "name" in result
    assert result["name"].has_default
    assert result["name"].default == "Anonymous"

    # Check age default
    assert "age" in result
    assert result["age"].has_default
    assert result["age"].default == 0

    # Check active default
    assert "active" in result
    assert result["active"].has_default
    assert result["active"].default is True

    # Check score default
    assert "score" in result
    assert result["score"].has_default
    assert result["score"].default == 0.0

    # Check data default
    assert "data" in result
    assert result["data"].has_default
    assert result["data"].default is None


def test_default_application():
    """Test applying default values to data."""
    parser = SchemaParser()

    schema = """
    name: str = "Anonymous"
    age: int = 0
    active: bool = true
    tags: [str] = ["default"]
    """

    schema_objects = parser.parse(schema)

    # Empty data
    data = {}

    # Apply defaults
    result = apply_defaults(data, schema_objects)

    # Check that defaults were applied
    assert "name" in result
    assert result["name"] == "Anonymous"
    assert "age" in result
    assert result["age"] == 0
    assert "active" in result
    assert result["active"] is True
    assert "tags" in result
    assert result["tags"] == ["default"]

    # Data with some fields present
    data = {
        "name": "John",
        "tags": ["custom"]
    }

    # Apply defaults
    result = apply_defaults(data, schema_objects)

    # Check that existing values were preserved and only missing fields got defaults
    assert "name" in result
    assert result["name"] == "John"  # Preserved
    assert "age" in result
    assert result["age"] == 0  # Default applied
    assert "active" in result
    assert result["active"] is True  # Default applied
    assert "tags" in result
    assert result["tags"] == ["custom"]  # Preserved


def test_nested_defaults():
    """Test default values in nested structures."""
    parser = SchemaParser()

    schema = """
    user: {
        name: str = "Anonymous",
        settings: {
            theme: str = "light",
            notifications: bool = true
        }
    } = {
        name = "Guest",
        settings = {
            theme = "system",
            notifications = false
        }
    }
    """

    schema_objects = parser.parse(schema)

    # Empty data
    data = {}

    # Apply defaults
    result = apply_defaults(data, schema_objects)

    # Check that defaults were applied at the top level
    assert "user" in result
    assert result["user"]["name"] == "Guest"
    assert result["user"]["settings"]["theme"] == "system"
    assert result["user"]["settings"]["notifications"] is False

    # Partial data
    data = {
        "user": {
            "name": "John"
        }
    }

    # Apply defaults
    result = apply_defaults(data, schema_objects)

    # Check that existing values were preserved and nested defaults were applied
    assert "user" in result
    assert result["user"]["name"] == "John"  # Preserved
    assert "settings" in result["user"]
    assert result["user"]["settings"]["theme"] == "light"  # Field default, not object default
    assert result["user"]["settings"]["notifications"] is True  # Field default, not object default


def test_list_defaults():
    """Test default values for list types and items."""
    parser = SchemaParser()

    schema = """
    colors: [str] = ["red", "green", "blue"]
    settings: [{
        name: str,
        value: str = "default"
    }] = [
        {
            name = "theme",
            value = "dark"
        }
    ]
    """

    schema_objects = parser.parse(schema)

    # Empty data
    data = {}

    # Apply defaults
    result = apply_defaults(data, schema_objects)

    # Check that defaults were applied
    assert "colors" in result
    assert result["colors"] == ["red", "green", "blue"]
    assert "settings" in result
    assert len(result["settings"]) == 1
    assert result["settings"][0]["name"] == "theme"
    assert result["settings"][0]["value"] == "dark"

    # Partial data with list items
    data = {
        "settings": [
            {
                "name": "language"
                # value will get default
            },
            {
                "name": "timezone",
                "value": "UTC"
            }
        ]
    }

    # Apply defaults
    result = apply_defaults(data, schema_objects)

    # Check that list item defaults were applied
    assert "settings" in result
    assert len(result["settings"]) == 2
    assert result["settings"][0]["name"] == "language"
    assert result["settings"][0]["value"] == "default"  # Default applied
    assert result["settings"][1]["name"] == "timezone"
    assert result["settings"][1]["value"] == "UTC"  # Preserved


def test_union_defaults():
    """Test default values for union types."""
    parser = SchemaParser()

    schema = """
    status: str | null = null
    data: int | str | {
        value: any
    } = "none"
    complex: {
        count: int
    } | [int] = {
        count = 0
    }
    """

    schema_objects = parser.parse(schema)

    # Empty data
    data = {}

    # Apply defaults
    result = apply_defaults(data, schema_objects)

    # Check that defaults were applied
    assert "status" in result
    assert result["status"] is None
    assert "data" in result
    assert result["data"] == "none"
    assert "complex" in result
    assert "count" in result["complex"]
    assert result["complex"]["count"] == 0


def test_default_validation():
    """Test that default values respect constraints."""
    parser = SchemaParser()

    # Valid defaults
    schema = """
    count: int<min=0, max=100> = 50
    status: str<enum=["active", "inactive"]> = "active"
    items: [str]<min=1, max=5> = ["default"]
    """

    schema_objects = parser.parse(schema)

    # Empty data
    data = {}

    # Apply defaults
    result = apply_defaults(data, schema_objects)

    # Validate with defaults applied
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(result)

    # Should be valid
    assert not errors, f"Expected no errors, got: {errors}"


def test_optional_with_defaults():
    """Test interaction between optional fields and defaults."""
    parser = SchemaParser()

    schema = """
    required: str
    optional?: str
    with_default: str = "default"
    optional_with_default?: str = "optional default"
    """

    schema_objects = parser.parse(schema)

    # Test if fields with defaults are effectively optional
    partial_data = {
        "required": "value"
        # Missing optional, with_default, and optional_with_default
    }

    # Validate partial data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(partial_data)

    # Only required fields without defaults should cause errors
    assert not errors, f"Expected no errors with defaults, got: {errors}"

    # Apply defaults
    result = apply_defaults(partial_data, schema_objects)

    # Check what was added
    assert "required" in result
    assert "optional" not in result  # Optional without default stays missing
    assert "with_default" in result  # Field with default gets added
    assert "optional_with_default" in result  # Optional with default gets added


if __name__ == "__main__":
    # Run tests individually for debugging
    test_scalar_defaults()
    test_default_application()
    test_nested_defaults()
    test_list_defaults()
    test_union_defaults()
    test_default_validation()
    test_optional_with_defaults()

    print("All default value tests passed!")