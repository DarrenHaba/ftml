"""
Test module for object syntax in schemas.

Focuses on testing both {T} and {str: T} syntax for object patterns.
"""

import logging

import pytest

from ftml import FTMLParseError
from ftml.logger import logger
from ftml.schema.schema_ast import UnionTypeNode, ScalarTypeNode, ObjectTypeNode, ListTypeNode
from ftml.schema.schema_parser import SchemaParser
from ftml.schema.schema_validator import SchemaValidator

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_union_in_object_pattern():
    """Test union types in object patterns."""
    parser = SchemaParser()

    # Test pattern with union types
    schema_str = "values: {int | str | bool}"

    result = parser.parse(schema_str)
    field_name = schema_str.split(":")[0].strip()

    assert field_name in result
    assert result[field_name].pattern_value_type is not None
    assert isinstance(result[field_name].pattern_value_type, UnionTypeNode)
    assert len(result[field_name].pattern_value_type.subtypes) == 3

    # Validate the subtypes
    subtypes = result[field_name].pattern_value_type.subtypes
    assert subtypes[0].type_name == "int"
    assert subtypes[1].type_name == "str"
    assert subtypes[2].type_name == "bool"

    # Validation test - valid data
    valid_data = {
        "values": {
            "int_value": 42,
            "str_value": "test",
            "bool_value": True
        }
    }

    validator = SchemaValidator(result)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors for valid data, got: {errors}"

    # Validation test - invalid data
    invalid_data = {
        "values": {
            "int_value": 42,
            "invalid_value": [],  # Not int, str, or bool
            "bool_value": True
        }
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 1, f"Expected 1 error for invalid data, got: {len(errors)}"


def test_complex_object_pattern_unions():
    """Test complex union patterns with constraints."""
    parser = SchemaParser()

    # Test various complex pattern scenarios
    # 1. Object pattern with union of value types, each with constraints
    schema_str = """
    constrained_union: {int<min=5, max=10> | str<min_length=5, max_length=10>}
    """

    result = parser.parse(schema_str)

    # Check that the pattern_value_type is a union
    assert "constrained_union" in result
    assert result["constrained_union"].pattern_value_type is not None
    assert isinstance(result["constrained_union"].pattern_value_type, UnionTypeNode)

    # Check the constraints on the subtypes
    union_subtypes = result["constrained_union"].pattern_value_type.subtypes
    assert len(union_subtypes) == 2

    # Int subtype with constraints
    int_subtype = union_subtypes[0]
    assert int_subtype.type_name == "int"
    assert int_subtype.constraints["min"] == 5
    assert int_subtype.constraints["max"] == 10

    # String subtype with constraints
    str_subtype = union_subtypes[1]
    assert str_subtype.type_name == "str"
    assert str_subtype.constraints["min_length"] == 5
    assert str_subtype.constraints["max_length"] == 10

    # Validation tests - valid data (meets constraints)
    valid_data = {
        "constrained_union": {
            "int_value": 7,  # Valid int between 5-10
            "str_value": "abcdef"  # Valid string length 6 (between 5-10)
        }
    }

    validator = SchemaValidator(result)
    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors for valid data, got: {errors}"

    # Validation tests - invalid data (fails constraints)
    invalid_data = {
        "constrained_union": {
            "int_value": 3,  # Invalid: less than min=5
            "str_value": "abcdef"  # Valid
        }
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 1, f"Expected 1 error for invalid data, got: {len(errors)}"

    # Another invalid case - string too short
    invalid_data2 = {
        "constrained_union": {
            "int_value": 7,  # Valid
            "str_value": "abc"  # Invalid: less than min_length=5
        }
    }

    errors = validator.validate(invalid_data2)
    assert len(errors) == 1, f"Expected 1 error for invalid data, got: {len(errors)}"



def test_union_of_object_patterns():
    """Test union of object patterns {T1} | {T2}."""
    parser = SchemaParser()

    # Test union of object patterns
    schema_str = """
    pattern_union: {int} | {str} | null
    """

    result = parser.parse(schema_str)

    # Check that we have a union at the top level
    assert "pattern_union" in result
    assert isinstance(result["pattern_union"], UnionTypeNode)
    assert len(result["pattern_union"].subtypes) == 3

    # First subtype should be an object pattern with int values
    int_pattern = result["pattern_union"].subtypes[0]
    assert isinstance(int_pattern, ObjectTypeNode)
    assert int_pattern.pattern_value_type.type_name == "int"

    # Second subtype should be an object pattern with string values
    str_pattern = result["pattern_union"].subtypes[1]
    assert isinstance(str_pattern, ObjectTypeNode)
    assert str_pattern.pattern_value_type.type_name == "str"

    # Third subtype should be null
    null_pattern = result["pattern_union"].subtypes[2]
    assert isinstance(null_pattern, ScalarTypeNode)
    assert null_pattern.type_name == "null"

    # Validation tests

    # Valid data - all integers
    valid_int_data = {
        "pattern_union": {
            "a": 1,
            "b": 2,
            "c": 3
        }
    }

    validator = SchemaValidator(result)
    errors = validator.validate(valid_int_data)
    assert not errors, f"Expected no errors for valid int data, got: {errors}"

    # Valid data - all strings
    valid_str_data = {
        "pattern_union": {
            "a": "one",
            "b": "two",
            "c": "three"
        }
    }

    errors = validator.validate(valid_str_data)
    assert not errors, f"Expected no errors for valid string data, got: {errors}"

    # Valid data - null
    valid_null_data = {
        "pattern_union": None
    }

    errors = validator.validate(valid_null_data)
    assert not errors, f"Expected no errors for valid null data, got: {errors}"

    # Invalid data - mixed types
    invalid_data = {
        "pattern_union": {
            "a": 1,
            "b": "two",  # Mixed int and string
            "c": 3
        }
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 1, f"Expected 1 error for invalid data, got: {len(errors)}"


def test_very_complex_union_patterns():
    """Test for very complex union patterns with object constraints."""
    parser = SchemaParser()

    # Test a complex union with multiple object patterns, scalars, and constraints
    schema_str = """
    super_complex: {str}<max=10> | {int}<min=5> | int | null | float | str
    """

    result = parser.parse(schema_str)

    # Check that we have a union at the top level
    assert "super_complex" in result
    assert isinstance(result["super_complex"], UnionTypeNode)
    assert len(result["super_complex"].subtypes) == 6

    # First subtype should be an object pattern with string values and max=10 constraint
    str_pattern = result["super_complex"].subtypes[0]
    assert isinstance(str_pattern, ObjectTypeNode)
    assert str_pattern.pattern_value_type.type_name == "str"
    assert str_pattern.constraints["max"] == 10

    # Second subtype should be an object pattern with int values and min=5 constraint
    int_pattern = result["super_complex"].subtypes[1]
    assert isinstance(int_pattern, ObjectTypeNode)
    assert int_pattern.pattern_value_type.type_name == "int"
    assert int_pattern.constraints["min"] == 5

    # Third subtype should be plain int
    int_type = result["super_complex"].subtypes[2]
    assert isinstance(int_type, ScalarTypeNode)
    assert int_type.type_name == "int"

    # Fourth subtype should be null
    null_type = result["super_complex"].subtypes[3]
    assert isinstance(null_type, ScalarTypeNode)
    assert null_type.type_name == "null"

    # Fifth subtype should be float
    float_type = result["super_complex"].subtypes[4]
    assert isinstance(float_type, ScalarTypeNode)
    assert float_type.type_name == "float"

    # Sixth subtype should be str
    str_type = result["super_complex"].subtypes[5]
    assert isinstance(str_type, ScalarTypeNode)
    assert str_type.type_name == "str"

    # Validation tests

    # 1. Valid string object with < 10 properties
    valid_str_obj = {
        "super_complex": {
            "a": "one",
            "b": "two",
            "c": "three"
        }
    }

    validator = SchemaValidator(result)
    errors = validator.validate(valid_str_obj)
    assert not errors, f"Expected no errors for valid string object, got: {errors}"

    # 2. Invalid string object with > 10 properties
    invalid_str_obj = {
        "super_complex": {
            "a": "1", "b": "2", "c": "3", "d": "4", "e": "5",
            "f": "6", "g": "7", "h": "8", "i": "9", "j": "10",
            "k": "11"  # One too many
        }
    }

    errors = validator.validate(invalid_str_obj)
    assert len(errors) == 1, f"Expected 1 error for string object with too many properties, got: {len(errors)}"

    # 3. Valid int object with >= 5 properties
    valid_int_obj = {
        "super_complex": {
            "a": 1, "b": 2, "c": 3, "d": 4, "e": 5
        }
    }

    errors = validator.validate(valid_int_obj)
    assert not errors, f"Expected no errors for valid int object, got: {errors}"

    # 4. Invalid int object with < 5 properties
    invalid_int_obj = {
        "super_complex": {
            "a": 1, "b": 2, "c": 3, "d": 4
        }
    }

    errors = validator.validate(invalid_int_obj)
    assert len(errors) == 1, f"Expected 1 error for int object with too few properties, got: {len(errors)}"

    # 5. Valid scalar types
    valid_scalar_cases = [
        {"super_complex": 42},  # int
        {"super_complex": None},  # null
        {"super_complex": 3.14},  # float
        {"super_complex": "string"}  # str
    ]

    for case in valid_scalar_cases:
        errors = validator.validate(case)
        assert not errors, f"Expected no errors for valid scalar {case}, got: {errors}"


def test_union_validation_fallback():
    """Test that validation falls back to other union options when one fails."""
    parser = SchemaParser()

    # Use proper syntax for union types - now with proper constraints
    schema_str = """
    numbers: {int}<min=1, max=1> | {int}<min=2>
    """

    result = parser.parse(schema_str)

    # Verify schema structure
    assert "numbers" in result
    assert isinstance(result["numbers"], UnionTypeNode)
    assert len(result["numbers"].subtypes) == 2

    # First union option: {int}<min=1, max=1> - object with exactly 1 int property
    first_option = result["numbers"].subtypes[0]
    assert first_option.constraints["min"] == 1
    assert first_option.constraints["max"] == 1
    assert first_option.pattern_value_type.type_name == "int"

    # Second union option: {int}<min=2> - object with 2+ int properties
    second_option = result["numbers"].subtypes[1]
    assert second_option.constraints["min"] == 2
    assert second_option.pattern_value_type.type_name == "int"

    # Create validator
    validator = SchemaValidator(result)

    # Test case 1: Object with 1 int property - should match first option
    case1_data = {
        "numbers": {"a": 42}
    }
    errors = validator.validate(case1_data)
    assert not errors, f"Expected case 1 to be valid, got errors: {errors}"

    # Test case 2: Object with 3 int properties - should match second option
    # This would fail the first option (max=1) but pass the second (min=2)
    case2_data = {
        "numbers": {"a": 10, "b": 20, "c": 30}
    }
    errors = validator.validate(case2_data)
    assert not errors, f"Expected case 2 to be valid, got errors: {errors}"

    # Test case 3: Invalid data - doesn't match either option
    # Contains a string value instead of int
    case3_data = {
        "numbers": {"a": "string", "b": 20}
    }
    errors = validator.validate(case3_data)
    assert errors, "Expected invalid data to produce errors"

    # Test case 4: Empty object - should now fail both options
    # - Fails first option (requires min=1)
    # - Fails second option (requires min=2)
    case4_data = {
        "numbers": {}
    }
    errors = validator.validate(case4_data)
    assert errors, "Expected empty object to produce errors"


def test_null_defaults_in_nesting():
    """Test null values as defaults in nested structures."""
    parser = SchemaParser()

    schema = """
    nullable: {
        maybe_obj: str | str = null
    }
    """

    result = parser.parse(schema)

































def test_null_defaults_in_nesting():
    """Test null values as defaults in nested structures."""
    parser = SchemaParser()

    # This should now work with the fixed parser
    schema = """
    nullable: {
        maybe_obj: {} | null = null,
        mixed_type: str | int | bool = "default",
        container_mix: [] | {} | null = []
    }
    """

    result = parser.parse(schema)

    # Verify the structure
    assert "nullable" in result
    assert isinstance(result["nullable"], ObjectTypeNode)

    # Check maybe_obj field
    maybe_obj = result["nullable"].fields["maybe_obj"]
    assert isinstance(maybe_obj, UnionTypeNode)
    assert len(maybe_obj.subtypes) == 2
    assert isinstance(maybe_obj.subtypes[0], ObjectTypeNode)
    assert maybe_obj.subtypes[1].type_name == "null"
    assert maybe_obj.has_default
    assert maybe_obj.default is None

    # Check mixed_type field
    mixed_type = result["nullable"].fields["mixed_type"]
    assert isinstance(mixed_type, UnionTypeNode)
    assert len(mixed_type.subtypes) == 3
    assert mixed_type.subtypes[0].type_name == "str"
    assert mixed_type.subtypes[1].type_name == "int"
    assert mixed_type.subtypes[2].type_name == "bool"
    assert mixed_type.has_default
    assert mixed_type.default == "default"

    # Check container_mix field
    container_mix = result["nullable"].fields["container_mix"]
    assert isinstance(container_mix, UnionTypeNode)
    assert len(container_mix.subtypes) == 3
    assert isinstance(container_mix.subtypes[0], ListTypeNode)
    assert isinstance(container_mix.subtypes[1], ObjectTypeNode)
    assert container_mix.subtypes[2].type_name == "null"
    assert container_mix.has_default
    assert isinstance(container_mix.default, list)
    assert len(container_mix.default) == 0


def test_two_level_nested_unions():
    """Test union types nested two levels deep."""
    parser = SchemaParser()

    schema = """
    config: {
        level1: {
            simple_union: int | bool | null,
            complex_union: {str} | [int] | null,
            default_union: str | int = 42
        }
    }
    """

    result = parser.parse(schema)

    # Check level 1
    assert "config" in result
    assert isinstance(result["config"], ObjectTypeNode)

    # Check level 2
    level1 = result["config"].fields["level1"]
    assert isinstance(level1, ObjectTypeNode)

    # Check simple_union
    simple_union = level1.fields["simple_union"]
    assert isinstance(simple_union, UnionTypeNode)
    assert len(simple_union.subtypes) == 3
    assert simple_union.subtypes[0].type_name == "int"
    assert simple_union.subtypes[1].type_name == "bool"
    assert simple_union.subtypes[2].type_name == "null"

    # Check complex_union
    complex_union = level1.fields["complex_union"]
    assert isinstance(complex_union, UnionTypeNode)
    assert len(complex_union.subtypes) == 3

    # First option: {str}
    assert isinstance(complex_union.subtypes[0], ObjectTypeNode)
    assert complex_union.subtypes[0].pattern_value_type is not None
    assert complex_union.subtypes[0].pattern_value_type.type_name == "str"

    # Second option: [int]
    assert isinstance(complex_union.subtypes[1], ListTypeNode)
    assert complex_union.subtypes[1].item_type is not None
    assert complex_union.subtypes[1].item_type.type_name == "int"

    # Third option: null
    assert complex_union.subtypes[2].type_name == "null"

    # Check default_union
    default_union = level1.fields["default_union"]
    assert isinstance(default_union, UnionTypeNode)
    assert default_union.has_default
    assert default_union.default == 42


def test_multi_level_nested_unions():
    """Test union types nested multiple levels deep."""
    parser = SchemaParser()

    schema = """
    root: {
        level1: {
            level2: {
                level3: {
                    deep_union: int | {
                        nested: bool | null = null
                    } | [str] = 123
                }
            }
        }
    }
    """

    result = parser.parse(schema)

    # Navigate to the deepest level
    root = result["root"]
    level1 = root.fields["level1"]
    level2 = level1.fields["level2"]
    level3 = level2.fields["level3"]
    deep_union = level3.fields["deep_union"]

    # Check deep_union structure
    assert isinstance(deep_union, UnionTypeNode)
    assert len(deep_union.subtypes) == 3
    assert deep_union.subtypes[0].type_name == "int"
    assert isinstance(deep_union.subtypes[1], ObjectTypeNode)
    assert isinstance(deep_union.subtypes[2], ListTypeNode)
    assert deep_union.has_default
    assert deep_union.default == 123

    # Check the nested object inside the union
    nested_obj = deep_union.subtypes[1]
    assert "nested" in nested_obj.fields

    nested_field = nested_obj.fields["nested"]
    assert isinstance(nested_field, UnionTypeNode)
    assert len(nested_field.subtypes) == 2
    assert nested_field.subtypes[0].type_name == "bool"
    assert nested_field.subtypes[1].type_name == "null"
    assert nested_field.has_default
    assert nested_field.default is None


def test_validation_with_nested_unions():
    """Test data validation against schemas with nested union types."""
    parser = SchemaParser()

    schema = """
    config: {
        format: "json" | "yaml" | "xml",
    }
    """

    # Assert that this raises a FTMLParseError
    with pytest.raises(FTMLParseError):
        parser.parse(schema)
