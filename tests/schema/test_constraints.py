"""
Test module for schema constraint parsing and validation.
"""

import logging
from ftml.logger import logger
from ftml.schema.schema_parser import SchemaParser
from ftml.schema.schema_validator import SchemaValidator


# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_string_constraints():
    """Test string constraint parsing and validation."""
    parser = SchemaParser()

    # Test min/max length constraints
    schema = """
    username: str<min_length=3, max_length=20>
    """
    result = parser.parse(schema)

    assert "username" in result
    assert result["username"].type_name == "str"
    assert result["username"].constraints["min_length"] == 3
    assert result["username"].constraints["max_length"] == 20

    # Test pattern constraint
    schema = """
    email: str<pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$">
    """
    result = parser.parse(schema)

    assert "email" in result
    assert result["email"].type_name == "str"
    assert "pattern" in result["email"].constraints
    pattern = result["email"].constraints["pattern"]
    assert "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$" == pattern

    # Test enum constraint
    schema = """
    color: str<enum=["red", "green", "blue"]>
    """
    result = parser.parse(schema)

    assert "color" in result
    assert result["color"].type_name == "str"
    assert "enum" in result["color"].constraints
    assert result["color"].constraints["enum"] == ["red", "green", "blue"]


def test_numeric_constraints():
    """Test numeric constraint parsing and validation."""
    parser = SchemaParser()

    # Test integer min/max constraints
    schema = """
    port: int<min=1024, max=65535>
    """
    result = parser.parse(schema)

    assert "port" in result
    assert result["port"].type_name == "int"
    assert result["port"].constraints["min"] == 1024
    assert result["port"].constraints["max"] == 65535

    # Test float constraints with precision
    schema = """
    price: float<min=0.0, max=1000.0, precision=2>
    """
    result = parser.parse(schema)

    assert "price" in result
    assert result["price"].type_name == "float"
    assert result["price"].constraints["min"] == 0.0
    assert result["price"].constraints["max"] == 1000.0
    assert result["price"].constraints["precision"] == 2


def test_collection_constraints():
    """Test collection constraint parsing and validation."""
    parser = SchemaParser()

    # Test list constraints
    schema = """
    tags: [str]<min=1, max=10>
    """
    result = parser.parse(schema)

    assert "tags" in result
    assert result["tags"].constraints["min"] == 1
    assert result["tags"].constraints["max"] == 10

    # Test object constraints
    schema = """
    counts: {str: int}<min=1, max=5>
    """
    result = parser.parse(schema)

    assert "counts" in result
    assert result["counts"].constraints["min"] == 1
    assert result["counts"].constraints["max"] == 5


def test_complex_constraints():
    """Test combinations of constraints."""
    parser = SchemaParser()

    # Test combination of constraints
    schema = """
    data: {
        id: str<min_length=5, pattern="[A-Z0-9]+">,
        value: float<min=0.0, precision=2>,
        tags: [str]<max=5, min=1>
    }
    """
    result = parser.parse(schema)

    assert "data" in result
    assert "id" in result["data"].fields
    assert result["data"].fields["id"].constraints["min_length"] == 5
    assert "pattern" in result["data"].fields["id"].constraints

    assert "value" in result["data"].fields
    assert result["data"].fields["value"].constraints["min"] == 0.0
    assert result["data"].fields["value"].constraints["precision"] == 2

    assert "tags" in result["data"].fields
    assert result["data"].fields["tags"].constraints["max"] == 5
    assert result["data"].fields["tags"].constraints["min"] == 1


def test_constraint_validation():
    """Test actual validation of constraints."""
    parser = SchemaParser()

    # Define a schema with various constraints
    schema = """
    user: {
        username: str<min_length=3, max_length=20>,
        email: str<pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$">,
        age: int<min=18, max=120>,
        score: float<min=0.0, max=100.0, precision=1>,
        roles: [str]<min=1, max=5>,
        settings: {}<max=1>
    }
    """

    # Parse the schema
    schema_objects = parser.parse(schema)

    # Create test data - valid
    valid_data = {
        "user": {
            "username": "johndoe",
            "email": "john@example.com",
            "age": 30,
            "score": 85.5,
            "roles": ["user", "admin"],
            "settings": {
                "status": "good",
            }
        }
    }

    # Validate the data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)

    # Should be valid
    assert not errors, f"Expected no errors, got: {errors}"

    # Create test data - invalid
    invalid_data = {
        "user": {
            "username": "jo",  # Too short
            "email": "not-an-email",  # Invalid email
            "age": 150,  # Too high
            "score": 101.12345,  # Too high and too many decimal places
            "roles": [],  # Too few
            "settings": {
                "key_1": "value 1",
                "key_2": "value 2",  # Too many
            }
        }
    }

    # Validate the data
    errors = validator.validate(invalid_data)

    # Should be invalid with multiple errors
    assert len(errors) >= 6, f"Expected at least 6 errors, got: {len(errors)}"

    # Check for specific error messages
    error_str = "\n".join(errors)
    assert "username" in error_str and "too short" in error_str.lower()
    assert "email" in error_str and "pattern" in error_str.lower()
    assert "age" in error_str and "too large" in error_str.lower()
    assert "score" in error_str and "too large" in error_str.lower()
    assert "roles" in error_str and "too short" in error_str.lower()
    assert "settings" in error_str and "too many" in error_str.lower()


def test_enum_validation():
    """Test enum constraint validation."""
    parser = SchemaParser()

    # Define a schema with enum constraints
    schema = """
    data: {
        status: str<enum=["pending", "active", "completed"]>,
        priority: int<enum=[1, 2, 3]>,
        flag: bool<enum=[true]>
    }
    """

    # Parse the schema
    schema_objects = parser.parse(schema)

    # Create test data - valid
    valid_data = {
        "data": {
            "status": "active",
            "priority": 2,
            "flag": True
        }
    }

    # Validate the data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)

    # Should be valid
    assert not errors, f"Expected no errors, got: {errors}"

    # Create test data - invalid
    invalid_data = {
        "data": {
            "status": "unknown",  # Not in enum
            "priority": 4,  # Not in enum
            "flag": False  # Not in enum (only true allowed)
        }
    }

    # Validate the data
    errors = validator.validate(invalid_data)

    # Should be invalid with multiple errors
    assert len(errors) == 3, f"Expected 3 errors, got: {len(errors)}"

    # Check for specific error messages
    error_str = "\n".join(errors)
    assert "status" in error_str and "not in allowed values" in error_str.lower()
    assert "priority" in error_str and "not in allowed values" in error_str.lower()
    assert "flag" in error_str and "not in allowed values" in error_str.lower()
