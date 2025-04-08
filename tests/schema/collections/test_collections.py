"""
Test module for collection types (lists and objects).
"""

import logging

from ftml.logger import logger
from ftml.schema.schema_parser import SchemaParser

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_basic_list_parsing():
    """Test basic list type parsing."""
    parser = SchemaParser()

    # Test simple list of integers
    schema = """numbers: [int]"""
    result = parser.parse(schema)

    assert "numbers" in result
    assert result["numbers"].item_type is not None
    assert result["numbers"].item_type.type_name == "int"

    # Test list with constraints
    schema = """scores: [int]<min=0, max=10>"""
    result = parser.parse(schema)

    assert "scores" in result
    assert result["scores"].item_type.type_name == "int"
    assert result["scores"].constraints["min"] == 0
    assert result["scores"].constraints["max"] == 10

    # Test list with default
    schema = """tags: [str] = ["red", "green", "blue"]"""
    result = parser.parse(schema)

    assert "tags" in result
    assert result["tags"].item_type.type_name == "str"
    assert result["tags"].has_default
    assert result["tags"].default == ["red", "green", "blue"]


def test_basic_object_parsing():
    """Test basic object type parsing."""
    parser = SchemaParser()

    # Test simple object with fields
    schema = """
    user: {
        name: str,
        age: int
    }
    """
    result = parser.parse(schema)

    assert "user" in result
    assert "name" in result["user"].fields
    assert result["user"].fields["name"].type_name == "str"
    assert "age" in result["user"].fields
    assert result["user"].fields["age"].type_name == "int"

    # Test object with pattern (string keys and int values)
    schema = """counts: {int}"""
    result = parser.parse(schema)

    assert "counts" in result
    assert result["counts"].pattern_value_type is not None
    assert result["counts"].pattern_value_type.type_name == "int"

    # Test object with constraints
    schema = """
    settings: {
        debug: bool,
        level: int
    }<min=1>
    """
    result = parser.parse(schema)

    assert "settings" in result
    assert "debug" in result["settings"].fields
    assert "level" in result["settings"].fields
    assert result["settings"].constraints["min"] == 1


def test_nested_list_parsing():
    """Test nested list type parsing."""
    parser = SchemaParser()

    # Test list of lists of integers
    schema = """matrix: [[int]]"""
    result = parser.parse(schema)

    assert "matrix" in result
    assert result["matrix"].item_type is not None
    assert result["matrix"].item_type.item_type.type_name == "int"

    # Test list of objects
    schema = """
    users: [{
        name: str,
        age: int
    }]
    """
    result = parser.parse(schema)

    assert "users" in result
    assert "name" in result["users"].item_type.fields
    assert "age" in result["users"].item_type.fields


def test_nested_object_parsing():
    """Test nested object type parsing."""
    parser = SchemaParser()

    # Test object with nested objects
    schema = """
    user: {
        name: str,
        address: {
            street: str,
            city: str,
            zip: int
        }
    }
    """
    result = parser.parse(schema)

    assert "user" in result
    assert "name" in result["user"].fields
    assert "address" in result["user"].fields
    assert "street" in result["user"].fields["address"].fields
    assert "city" in result["user"].fields["address"].fields
    assert "zip" in result["user"].fields["address"].fields

    # Test object with nested lists
    schema = """
    user: {
        name: str,
        scores: [int]
    }
    """
    result = parser.parse(schema)

    assert "user" in result
    assert "name" in result["user"].fields
    assert "scores" in result["user"].fields
    assert result["user"].fields["scores"].item_type.type_name == "int"


def test_list_with_union_items():
    """Test list with union item types."""
    parser = SchemaParser()

    # Test list with union item type
    schema = """values: [int | str | bool]"""
    result = parser.parse(schema)

    assert "values" in result
    assert len(result["values"].item_type.subtypes) == 3
    assert result["values"].item_type.subtypes[0].type_name == "int"
    assert result["values"].item_type.subtypes[1].type_name == "str"
    assert result["values"].item_type.subtypes[2].type_name == "bool"


def test_object_with_union_values():
    """Test object with union pattern value type."""
    parser = SchemaParser()

    # Test object with union pattern value type
    schema = """settings: {int | str | bool}"""
    result = parser.parse(schema)

    assert "settings" in result
    assert len(result["settings"].pattern_value_type.subtypes) == 3
    assert result["settings"].pattern_value_type.subtypes[0].type_name == "int"
    assert result["settings"].pattern_value_type.subtypes[1].type_name == "str"
    assert result["settings"].pattern_value_type.subtypes[2].type_name == "bool"


def test_complex_nested_collections():
    """Test complex nested collections."""
    parser = SchemaParser()

    # Test complex nested structure
    schema = """
    company: {
        name: str,
        departments: [{
            name: str,
            employees: [{
                name: str,
                skills: [str]
            }]
        }]
    }
    """
    result = parser.parse(schema)

    assert "company" in result
    assert "name" in result["company"].fields
    assert "departments" in result["company"].fields
    assert "name" in result["company"].fields["departments"].item_type.fields
    assert "employees" in result["company"].fields["departments"].item_type.fields
    assert "name" in result["company"].fields["departments"].item_type.fields["employees"].item_type.fields
    assert "skills" in result["company"].fields["departments"].item_type.fields["employees"].item_type.fields
    assert result["company"].fields["departments"].item_type.fields["employees"].item_type.fields["skills"].item_type.type_name == "str"
