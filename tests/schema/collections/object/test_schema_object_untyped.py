from ftml.schema.schema_parser import SchemaParser
from ftml.schema.schema_validator import SchemaValidator


def test_untyped_object_validation():
    """Test validation of untyped object ({}) accepts any key-value pairs."""
    parser = SchemaParser()

    # Define a schema with an untyped object
    schema = """
    any_props: {}
    """

    schema_objects = parser.parse(schema)

    # Test empty object
    empty_data = {
        "any_props": {}
    }
    validator = SchemaValidator(schema_objects)
    errors = validator.validate(empty_data)
    assert not errors, f"Expected no errors for empty object, got: {errors}"

    # Test object with arbitrary properties
    mixed_data = {
        "any_props": {
            "string_prop": "value",
            "int_prop": 42,
            "bool_prop": True,
            "null_prop": None,
            "float_prop": 3.14,
            "object_prop": {"nested": "object"},
            "array_prop": [1, 2, 3]
        }
    }
    errors = validator.validate(mixed_data)
    assert not errors, f"Expected no errors for object with arbitrary properties, got: {errors}"

    # Test that object constraints still work
    constrained_schema = """
    limited_props: {}<min=2, max=4>
    """
    constrained_schema_objects = parser.parse(constrained_schema)
    validator = SchemaValidator(constrained_schema_objects)

    # Valid property count
    valid_props = {"limited_props": {"a": 1, "b": 2, "c": 3}}
    errors = validator.validate(valid_props)
    assert not errors, f"Expected no errors for valid property count, got: {errors}"

    # Invalid property count - too few
    too_few = {"limited_props": {"a": 1}}
    errors = validator.validate(too_few)
    assert len(errors) == 1, f"Expected 1 error for too few properties, got: {len(errors)}"

    # Invalid property count - too many
    too_many = {"limited_props": {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}}
    errors = validator.validate(too_many)
    assert len(errors) == 1, f"Expected 1 error for too many properties, got: {len(errors)}"


def test_object_pattern_vs_untyped():
    """Test the difference between pattern objects {str} and untyped objects {}."""
    parser = SchemaParser()

    # Parse schema with pattern object
    pattern_schema = """
    pattern_props: {str}
    """
    pattern_objects = parser.parse(pattern_schema)

    # Parse schema with untyped object
    untyped_schema = """
    untyped_props: {}
    """
    untyped_objects = parser.parse(untyped_schema)

    # Create validators
    pattern_validator = SchemaValidator(pattern_objects, strict=True)
    untyped_validator = SchemaValidator(untyped_objects, strict=True)

    # Test valid data
    valid_data = {
        "pattern_props": {"name": "John", "age": "30"},
        "untyped_props": {"name": "John", "age": 30}
    }

    # Pattern object requires string keys AND string values
    pattern_errors = pattern_validator.validate({"pattern_props": valid_data["pattern_props"]})
    assert not pattern_errors, f"Expected no errors for pattern object with string values, got: {pattern_errors}"

    # Invalid for pattern object - non-string values
    invalid_pattern = {"pattern_props": {"name": "John", "age": 30}}  # age is an int
    pattern_errors = pattern_validator.validate(invalid_pattern)
    assert pattern_errors, "Expected validation errors for pattern object with non-string values"

    # Untyped object accepts any types
    untyped_errors = untyped_validator.validate({"untyped_props": valid_data["untyped_props"]})
    assert not untyped_errors, f"Expected no errors for untyped object with mixed value types, got: {untyped_errors}"


def test_untyped_object_with_ext_flag():
    """Test that {} behaves similarly to {}<ext=true>."""
    parser = SchemaParser()

    # Define schemas
    untyped_schema = """
    untyped: {}
    """
    ext_true_schema = """
    ext_true: {}<ext=true>
    """
    ext_false_schema = """
    ext_false: {}<ext=false>
    """

    # Parse schemas
    untyped_objects = parser.parse(untyped_schema)
    ext_true_objects = parser.parse(ext_true_schema)
    ext_false_objects = parser.parse(ext_false_schema)

    # Create validators with strict=true
    untyped_validator = SchemaValidator(untyped_objects, strict=True)
    ext_true_validator = SchemaValidator(ext_true_objects, strict=True)
    ext_false_validator = SchemaValidator(ext_false_objects, strict=True)

    # Test data with arbitrary properties
    data = {
        "untyped": {"a": 1, "b": "string", "c": True},
        "ext_true": {"a": 1, "b": "string", "c": True},
        "ext_false": {"a": 1, "b": "string", "c": True}
    }

    # Untyped object should allow arbitrary properties
    untyped_errors = untyped_validator.validate({"untyped": data["untyped"]})
    assert not untyped_errors, f"Expected no errors for untyped object, got: {untyped_errors}"

    # ext=true should also allow arbitrary properties
    ext_true_errors = ext_true_validator.validate({"ext_true": data["ext_true"]})
    assert not ext_true_errors, f"Expected no errors for ext=true object, got: {ext_true_errors}"

    # ext=false with {} is a special case - it should still allow arbitrary properties
    # since there are no defined fields to check against
    ext_false_errors = ext_false_validator.validate({"ext_false": data["ext_false"]})
    assert not ext_false_errors, (f"Expected no errors for ext=false with empty object "
                                  f"definition, got: {ext_false_errors}")
