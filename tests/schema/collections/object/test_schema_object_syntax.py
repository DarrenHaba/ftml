"""
Test module for object syntax in schemas.

Focuses on testing both {T} and {str: T} syntax for object patterns.
"""

import logging

from ftml.logger import logger
from ftml.schema.schema_parser import SchemaParser
from ftml.schema.schema_validator import SchemaValidator
from ftml.schema.schema_debug import log_schema_ast


# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_simple_object_pattern_parsing():
    """Test parsing of simple {T} object pattern syntax."""
    parser = SchemaParser()

    # Test simple pattern with different scalar types
    schemas = [
        "counts: {int}",
        "names: {str}",
        "flags: {bool}",
        "values: {float}",
        "items: {any}",
        "options: {null}"
    ]

    for schema_str in schemas:
        result = parser.parse(schema_str)
        field_name = schema_str.split(":")[0].strip()
        type_name = schema_str.split("{")[1].split("}")[0].strip()

        assert field_name in result
        assert result[field_name].pattern_value_type is not None
        assert result[field_name].pattern_value_type.type_name == type_name

        # Log for debugging
        logger.debug(f"Successfully parsed {schema_str}")
        log_schema_ast(result[field_name], f"Pattern for {field_name}")


def test_object_with_type_named_keys():
    """Test that objects can have keys that happen to be named like types."""
    parser = SchemaParser()

    # Test objects where keys have type names
    schema = """
    test1: {str: int, bool: float}
    test2: {int: str, float: bool}
    """

    result = parser.parse(schema)

    # Check test1
    assert "test1" in result
    assert "str" in result["test1"].fields
    assert "bool" in result["test1"].fields
    assert result["test1"].fields["str"].type_name == "int"
    assert result["test1"].fields["bool"].type_name == "float"

    # Check test2
    assert "test2" in result
    assert "int" in result["test2"].fields
    assert "float" in result["test2"].fields
    assert result["test2"].fields["int"].type_name == "str"
    assert result["test2"].fields["float"].type_name == "bool"


def test_regular_object_with_type_named_keys_validation():
    """Test validation of regular objects with keys named like types."""
    parser = SchemaParser()

    # Define schema with regular objects that have keys named like types
    schema_str = """
    test_object: {
        str: int,
        int: str,
        float: bool,
        bool: float
    }
    """

    schema_objects = parser.parse(schema_str)

    # Valid data
    valid_data = {
        "test_object": {
            "str": 42,
            "int": "value",
            "float": True,
            "bool": 3.14
        }
    }

    # Invalid data (wrong types)
    invalid_data = {
        "test_object": {
            "str": "wrong type",
            "int": 123,
            "float": 3.14,
            "bool": False
        }
    }

    # Validate valid data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors for valid data, got: {errors}"

    # Validate invalid data
    errors = validator.validate(invalid_data)
    assert len(errors) == 4, f"Expected 4 errors for invalid data, got: {len(errors)}"

    # Make sure we have errors for each field
    error_text = " ".join(errors)
    assert "str" in error_text
    assert "int" in error_text
    assert "float" in error_text
    assert "bool" in error_text


def test_object_pattern_with_constraints():
    """Test object patterns with constraints."""
    parser = SchemaParser()

    # Test pattern with constraints
    schemas = [
        "counts: {int}<min=2, max=5>",
        "names: {str}<min=1>",
        "values: {float}<min=0>"
    ]

    for schema_str in schemas:
        result = parser.parse(schema_str)
        field_name = schema_str.split(":")[0].strip()
        type_name = schema_str.split("{")[1].split("}")[0].strip()

        assert field_name in result
        assert result[field_name].pattern_value_type is not None
        assert result[field_name].pattern_value_type.type_name == type_name
        assert result[field_name].constraints

        # Log for debugging
        logger.debug(f"Successfully parsed {schema_str} with constraints")
        log_schema_ast(result[field_name], f"Constrained pattern for {field_name}")


def test_object_pattern_with_default():
    """Test object patterns with default values."""
    parser = SchemaParser()

    # Test pattern with default values
    schema = """
    counts: {int} = {num1 = 5, num2 = 10}
    empty: {str} = {}
    """

    result = parser.parse(schema)

    assert "counts" in result
    assert result["counts"].pattern_value_type is not None
    assert result["counts"].pattern_value_type.type_name == "int"
    assert result["counts"].has_default
    assert result["counts"].default == {"num1": 5, "num2": 10}

    assert "empty" in result
    assert result["empty"].pattern_value_type is not None
    assert result["empty"].pattern_value_type.type_name == "str"
    assert result["empty"].has_default
    assert result["empty"].default == {}


def test_object_pattern_validation():
    """Test validation with object patterns using simple {T} syntax."""
    parser = SchemaParser()

    # Define schemas with simple pattern syntax
    schemas = [
        "pattern_ints: {int}",
        "pattern_strs: {str}",
        "pattern_floats: {float}",
        "pattern_bools: {bool}"
    ]

    for schema_str in schemas:
        schema_objects = parser.parse(schema_str)
        field_name = schema_str.split(":")[0].strip()

        if "int" in schema_str:
            # Valid data
            valid_data = {
                field_name: {"one": 1, "two": 2, "three": 3}
            }

            # Invalid data
            invalid_data = {
                field_name: {"one": 1, "two": "two", "three": 3}
            }
        elif "str" in schema_str:
            # Valid data
            valid_data = {
                field_name: {"one": "1", "two": "2", "three": "3"}
            }

            # Invalid data
            invalid_data = {
                field_name: {"one": "1", "two": 2, "three": "3"}
            }
        elif "float" in schema_str:
            # Valid data
            valid_data = {
                field_name: {"one": 1.1, "two": 2.2, "three": 3.0}
            }

            # Invalid data
            invalid_data = {
                field_name: {"one": 1.1, "two": "2.2", "three": 3.0}
            }
        else:  # bool
            # Valid data
            valid_data = {
                field_name: {"one": True, "two": False, "three": True}
            }

            # Invalid data
            invalid_data = {
                field_name: {"one": True, "two": "False", "three": True}
            }

        # Validate valid data
        validator = SchemaValidator(schema_objects)
        errors = validator.validate(valid_data)
        assert not errors, f"Expected no errors for {schema_str}, got: {errors}"

        # Validate invalid data
        errors = validator.validate(invalid_data)
        assert len(errors) == 1, f"Expected 1 error for {schema_str}, got: {len(errors)}"


def test_complex_object_patterns():
    """Test complex object patterns."""
    parser = SchemaParser()

    # Test pattern with complex types
    schema = """
    users: {
        name: str,
        settings: {bool}
    }
    """

    result = parser.parse(schema)

    assert "users" in result
    assert "name" in result["users"].fields
    assert "settings" in result["users"].fields
    assert result["users"].fields["settings"].pattern_value_type is not None
    assert result["users"].fields["settings"].pattern_value_type.type_name == "bool"
