"""
Test module for list validation.
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


def test_simple_list_validation():
    """Test validation of simple list types."""
    parser = SchemaParser()

    # Define a simple list schema
    schema = """
    numbers: [int]
    strings: [str]
    """

    schema_objects = parser.parse(schema)

    # Valid data
    valid_data = {
        "numbers": [1, 2, 3, 4, 5],
        "strings": ["a", "b", "c"]
    }

    # Validate valid data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data - wrong type in lists
    invalid_data = {
        "numbers": [1, "two", 3],
        "strings": ["a", 2, "c"]
    }

    # Validate invalid data
    errors = validator.validate(invalid_data)
    assert len(errors) == 2, f"Expected 2 errors, got: {len(errors)}"

    # Empty lists should be valid
    empty_data = {
        "numbers": [],
        "strings": []
    }

    errors = validator.validate(empty_data)
    assert not errors, f"Expected no errors for empty lists, got: {errors}"


def test_list_constraints_validation():
    """Test validation of list constraints."""
    parser = SchemaParser()

    # Define a schema with list constraints
    schema = """
    required_items: [str]<min=2>
    limited_items: [int]<max=3>
    exact_items: [bool]<min=2, max=2>
    """

    schema_objects = parser.parse(schema)

    # Valid data
    valid_data = {
        "required_items": ["a", "b", "c"],
        "limited_items": [1, 2],
        "exact_items": [True, False]
    }

    # Validate valid data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data - too few items
    too_few_data = {
        "required_items": ["a"],
        "limited_items": [1, 2],
        "exact_items": [True, False]
    }

    errors = validator.validate(too_few_data)
    assert len(errors) == 1, f"Expected 1 error, got: {len(errors)}"
    assert "required_items" in " ".join(errors)

    # Invalid data - too many items
    too_many_data = {
        "required_items": ["a", "b"],
        "limited_items": [1, 2, 3, 4],
        "exact_items": [True, False]
    }

    errors = validator.validate(too_many_data)
    assert len(errors) == 1, f"Expected 1 error, got: {len(errors)}"
    assert "limited_items" in " ".join(errors)

    # Invalid data - wrong item count
    wrong_count_data = {
        "required_items": ["a", "b"],
        "limited_items": [1, 2],
        "exact_items": [True, False, True]
    }

    errors = validator.validate(wrong_count_data)
    assert len(errors) == 1, f"Expected 1 error, got: {len(errors)}"
    assert "exact_items" in " ".join(errors)


def test_nested_list_validation():
    """Test validation of nested lists."""
    parser = SchemaParser()

    # Define a schema with nested lists
    schema = """
    matrix: [[int]]
    jagged: [[str]]
    """

    schema_objects = parser.parse(schema)

    # Valid data
    valid_data = {
        "matrix": [[1, 2], [3, 4], [5, 6]],
        "jagged": [["a", "b"], ["c"], ["d", "e", "f"]]
    }

    # Validate valid data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data - wrong type in nested list
    invalid_data = {
        "matrix": [[1, 2], [3, "four"], [5, 6]],
        "jagged": [["a", "b"], ["c"], ["d", 5, "f"]]
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 2, f"Expected 2 errors, got: {len(errors)}"


def test_list_with_union_validation():
    """Test validation of lists with union item types."""
    parser = SchemaParser()

    # Define a schema with union item types
    schema = """
    values: [int | str]
    complex: [int | {name: str} | [bool]]
    """

    schema_objects = parser.parse(schema)

    # Valid data
    valid_data = {
        "values": [1, "two", 3, "four"],
        "complex": [
            42,
            {"name": "object"},
            [True, False, True]
        ]
    }

    # Validate valid data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data - types not in union
    invalid_data = {
        "values": [1, True, 3],  # Boolean not in union
        "complex": [
            42,
            {"id": 123},  # Missing required field 'name'
            [1, 2, 3]     # Numbers instead of booleans
        ]
    }

    errors = validator.validate(invalid_data)
    assert len(errors) >= 3, f"Expected at least 3 errors, got: {len(errors)}"


def test_complex_nested_list_validation():
    """Test validation of complex nested list structures."""
    parser = SchemaParser()

    # Define a schema with complex nested lists
    schema = """
    data: [{
        id: str,
        values: [int]<min=1>,
        items: [{
            name: str,
            active: bool
        }]
    }]
    """

    schema_objects = parser.parse(schema)

    # Valid data
    valid_data = {
        "data": [
            {
                "id": "group1",
                "values": [1, 2, 3],
                "items": [
                    {"name": "item1", "active": True},
                    {"name": "item2", "active": False}
                ]
            },
            {
                "id": "group2",
                "values": [4],
                "items": []
            }
        ]
    }

    # Validate valid data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data - various nested validation errors
    invalid_data = {
        "data": [
            {
                "id": "group1",
                "values": [],  # Empty array violates min=1
                "items": [
                    {"name": "item1", "active": "yes"}  # String instead of boolean
                ]
            },
            {
                "id": 123,  # Number instead of string
                "values": [4],
                "items": [
                    {"name": 456, "active": True}  # Number instead of string
                ]
            }
        ]
    }

    errors = validator.validate(invalid_data)
    assert len(errors) >= 3, f"Expected at least 3 errors, got: {len(errors)}"


def test_list_defaults():
    """Test default values for lists."""
    parser = SchemaParser()

    # Define a schema with default values
    schema = """
    required: [int]
    with_default: [str] = ["default"]
    empty_default: [bool] = []
    """

    schema_objects = parser.parse(schema)

    # Empty data
    empty_data = {}

    # Apply defaults
    data_with_defaults = apply_defaults(empty_data, schema_objects)

    # Check defaults were applied
    assert "required" not in data_with_defaults  # No default provided
    assert "with_default" in data_with_defaults
    assert data_with_defaults["with_default"] == ["default"]
    assert "empty_default" in data_with_defaults
    assert data_with_defaults["empty_default"] == []

    # Partial data
    partial_data = {
        "with_default": ["custom"]
    }

    # Apply defaults
    result = apply_defaults(partial_data, schema_objects)

    # Check existing values preserved and missing ones defaulted
    assert "with_default" in result
    assert result["with_default"] == ["custom"]  # Preserved
    assert "empty_default" in result
    assert result["empty_default"] == []  # Default applied


def test_untyped_list_validation():
    """Test validation of untyped list ([]) accepts any type of items."""
    parser = SchemaParser()

    # Define a schema with an untyped list
    schema = """
    any_items: []
    """

    schema_objects = parser.parse(schema)

    # Test empty list
    empty_data = {
        "any_items": []
    }
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(empty_data)
    assert not errors, f"Expected no errors for empty list, got: {errors}"

    # Test mixed types in list
    mixed_data = {
        "any_items": [1, "string", True, None, 3.14, {"nested": "object"}, [1, 2, 3]]
    }
    errors = validator.validate(mixed_data)
    assert not errors, f"Expected no errors for mixed types in list, got: {errors}"

    # Test that list constraints still work
    constrained_schema = """
    limited_items: []<min=2, max=4>
    """
    constrained_schema_objects = parser.parse(constrained_schema)
    validator = SchemaValidator(constrained_schema_objects)

    # Valid length
    valid_length = {"limited_items": [1, 2, 3]}
    errors = validator.validate(valid_length)
    assert not errors, f"Expected no errors for valid length, got: {errors}"

    # Invalid length - too short
    too_short = {"limited_items": [1]}
    errors = validator.validate(too_short)
    assert len(errors) == 1, f"Expected 1 error for too short list, got: {len(errors)}"

    # Invalid length - too long
    too_long = {"limited_items": [1, 2, 3, 4, 5]}
    errors = validator.validate(too_long)
    assert len(errors) == 1, f"Expected 1 error for too long list, got: {len(errors)}"