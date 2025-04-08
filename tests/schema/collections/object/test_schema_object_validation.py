"""
Test module for object validation.
"""

import logging
from ftml.logger import logger
from ftml.schema.schema_parser import SchemaParser
from ftml.schema.schema_validator import SchemaValidator, apply_defaults

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_simple_object_validation():
    """Test validation of simple object types."""
    parser = SchemaParser()

    # Define a simple object schema
    schema = """
    user: {
        name: str,
        age: int,
        active: bool
    }
    """

    schema_objects = parser.parse(schema)

    # Valid data
    valid_data = {
        "user": {
            "name": "John",
            "age": 30,
            "active": True
        }
    }

    # Validate valid data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data - wrong types
    invalid_data = {
        "user": {
            "name": 123,      # Number instead of string
            "age": "thirty",  # String instead of number
            "active": "yes"   # String instead of boolean
        }
    }

    # Validate invalid data
    errors = validator.validate(invalid_data)
    assert len(errors) == 3, f"Expected 3 errors, got: {len(errors)}"

    # Missing required fields
    missing_data = {
        "user": {
            "name": "John"
            # Missing age and active
        }
    }

    errors = validator.validate(missing_data)
    assert len(errors) == 2, f"Expected 2 errors, got: {len(errors)}"


def test_object_pattern_validation():
    """Test validation of object pattern types."""
    parser = SchemaParser()

    # Define an object pattern schema
    schema = """
    counts: {int}
    settings: {bool}
    """

    schema_objects = parser.parse(schema)

    # Valid data
    valid_data = {
        "counts": {
            "apples": 5,
            "oranges": 10,
            "bananas": 3
        },
        "settings": {
            "debug": True,
            "verbose": False,
            "cache": True
        }
    }

    # Validate valid data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data - wrong value types
    invalid_data = {
        "counts": {
            "apples": 5,
            "oranges": "ten",  # String instead of int
            "bananas": True    # Boolean instead of int
        },
        "settings": {
            "debug": True,
            "verbose": "no",   # String instead of boolean
            "cache": 1         # Number instead of boolean
        }
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 4, f"Expected 4 errors, got: {len(errors)}"


def test_object_constraints_validation():
    """Test validation of object constraints."""
    parser = SchemaParser()

    # Define a schema with object constraints
    schema = """
    required_fields: {any}<min=2>
    limited_fields: {
        name: str,
        age: int,
        email: str,
        phone?: str
    }<max=3>
    exact_fields: {str}<min=1, max=1>
    """

    schema_objects = parser.parse(schema)

    # Valid data
    valid_data = {
        "required_fields": {
            "key1": "value1",
            "key2": 123
        },
        "limited_fields": {
            "name": "John",
            "age": 30,
            "email": "john@example.com"
            # Omitting phone to stay within max=3
        },
        "exact_fields": {
            "only_key": "only_value"
        }
    }

    # Validate valid data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"


def test_nested_object_validation():
    """Test validation of nested objects."""
    parser = SchemaParser()

    # Define a schema with nested objects
    schema = """
    user: {
        name: str,
        address: {
            street: str,
            city: str,
            zip: int
        },
        contact: {
            email: str,
            phone?: str
        }
    }
    """

    schema_objects = parser.parse(schema)

    # Valid data
    valid_data = {
        "user": {
            "name": "John",
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "zip": 12345
            },
            "contact": {
                "email": "john@example.com"
                # phone is optional
            }
        }
    }

    # Validate valid data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data - errors in nested objects
    invalid_data = {
        "user": {
            "name": "John",
            "address": {
                "street": "123 Main St",
                "city": 12345,  # Number instead of string
                "zip": "12345"  # String instead of number
            },
            "contact": {
                # Missing required email
                "phone": "555-1234"
            }
        }
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 3, f"Expected 3 errors, got: {len(errors)}"


def test_object_with_union_fields_validation():
    """Test validation of objects with union field types."""
    parser = SchemaParser()

    # Define a schema with union field types
    schema = """
    data: {
        id: str | int,
        value: float | null,
        content: str | {
            text: str,
            format: str
        }
    }
    """

    schema_objects = parser.parse(schema)

    # Valid data with first union variant
    valid_data_1 = {
        "data": {
            "id": "abc123",      # String variant
            "value": 3.14,       # Float variant
            "content": "raw text"  # String variant
        }
    }

    # Validate valid data first variant
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data_1)
    assert not errors, f"Expected no errors, got: {errors}"

    # Valid data with second union variant
    valid_data_2 = {
        "data": {
            "id": 12345,         # Integer variant
            "value": None,       # Null variant
            "content": {         # Object variant
                "text": "Formatted text",
                "format": "markdown"
            }
        }
    }

    # Validate valid data second variant
    errors = validator.validate(valid_data_2)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data - type not in union
    invalid_data = {
        "data": {
            "id": True,          # Boolean not in union
            "value": "3.14",     # String not in union
            "content": 123       # Number not in union
        }
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 3, f"Expected 3 errors, got: {len(errors)}"


def test_complex_object_with_lists_validation():
    """Test validation of complex objects with lists."""
    parser = SchemaParser()

    # Define a schema with objects containing lists
    schema = """
    product: {
        name: str,
        price: float,
        tags: [str],
        variations: [{
            name: str,
            price_adjustment: float,
            available: bool
        }]
    }
    """

    schema_objects = parser.parse(schema)

    # Valid data
    valid_data = {
        "product": {
            "name": "T-Shirt",
            "price": 19.99,
            "tags": ["clothing", "casual", "summer"],
            "variations": [
                {
                    "name": "Small",
                    "price_adjustment": -2.00,
                    "available": True
                },
                {
                    "name": "Large",
                    "price_adjustment": 2.50,
                    "available": False
                }
            ]
        }
    }

    # Validate valid data
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data - errors in nested lists and objects
    invalid_data = {
        "product": {
            "name": "T-Shirt",
            "price": "19.99",   # String instead of float
            "tags": ["clothing", 123, "summer"],  # Number in string list
            "variations": [
                {
                    "name": "Small",
                    "price_adjustment": -2.00,
                    "available": True
                },
                {
                    "name": "Large",
                    "price_adjustment": "premium",  # String instead of float
                    "available": "no"               # String instead of boolean
                }
            ]
        }
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 4, f"Expected 4 errors, got: {len(errors)}"


def test_object_defaults():
    """Test default values for objects."""
    parser = SchemaParser()

    # Define a schema with default values
    schema = """
    user: {
        name: str = "Anonymous",
        age: int = 0,
        settings: {
            theme: str = "light",
            notifications: bool = true
        }
    }
    """

    schema_objects = parser.parse(schema)

    # Empty data
    empty_data = {"user": {}}

    # Apply defaults
    data_with_defaults = apply_defaults(empty_data, schema_objects)

    # Check defaults were applied
    assert "user" in data_with_defaults
    assert "name" in data_with_defaults["user"]
    assert data_with_defaults["user"]["name"] == "Anonymous"
    assert "age" in data_with_defaults["user"]
    assert data_with_defaults["user"]["age"] == 0
    assert "settings" in data_with_defaults["user"]
    assert data_with_defaults["user"]["settings"]["theme"] == "light"
    assert data_with_defaults["user"]["settings"]["notifications"] is True

    # Partial data
    partial_data = {
        "user": {
            "name": "John",
            "settings": {
                "notifications": False
            }
        }
    }

    # Apply defaults
    result = apply_defaults(partial_data, schema_objects)

    # Check existing values preserved and missing ones defaulted
    assert result["user"]["name"] == "John"  # Preserved
    assert result["user"]["age"] == 0  # Default applied
    assert result["user"]["settings"]["theme"] == "light"  # Default applied
    assert result["user"]["settings"]["notifications"] is False  # Preserved


if __name__ == "__main__":
    # Run tests individually for debugging
    test_simple_object_validation()
    test_object_pattern_validation()
    test_object_constraints_validation()
    test_nested_object_validation()
    test_object_with_union_fields_validation()
    test_object_pattern_with_complex_values()
    test_complex_object_with_lists_validation()
    test_object_defaults()

    print("All object validation tests passed!")