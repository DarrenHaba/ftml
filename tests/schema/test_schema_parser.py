"""
Test module for the new schema parser.
"""

import logging
import pytest
from ftml.logger import logger
from ftml.schema.schema_parser import SchemaParser
from ftml.schema.schema_debug import log_schema_ast
from ftml.schema.schema_ast import ScalarTypeNode, UnionTypeNode, ListTypeNode, ObjectTypeNode

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_scalar_type_parsing():
    """Test parsing scalar types."""
    parser = SchemaParser()

    # Test basic string type
    schema = """name: str"""
    result = parser.parse(schema)

    assert "name" in result
    assert isinstance(result["name"], ScalarTypeNode)
    assert result["name"].type_name == "str"
    assert not result["name"].constraints
    assert not result["name"].has_default
    assert not result["name"].optional

    # Test with constraints
    schema = """age: int<min=0, max=120>"""
    result = parser.parse(schema)

    assert "age" in result
    assert isinstance(result["age"], ScalarTypeNode)
    assert result["age"].type_name == "int"
    assert result["age"].constraints["min"] == 0
    assert result["age"].constraints["max"] == 120

    # Test with default value
    schema = """active: bool = true"""
    result = parser.parse(schema)

    assert "active" in result
    assert isinstance(result["active"], ScalarTypeNode)
    assert result["active"].type_name == "bool"
    assert result["active"].has_default
    assert result["active"].default is True

    # Test optional type
    schema = """nickname?: str"""
    result = parser.parse(schema)

    assert "nickname" in result
    assert isinstance(result["nickname"], ScalarTypeNode)
    assert result["nickname"].optional


def test_list_type_parsing():
    """Test parsing list types."""
    parser = SchemaParser()

    # Test basic list type
    schema = """tags: [str]"""
    result = parser.parse(schema)

    assert "tags" in result
    assert isinstance(result["tags"], ListTypeNode)
    assert isinstance(result["tags"].item_type, ScalarTypeNode)
    assert result["tags"].item_type.type_name == "str"

    # Test list with constraints
    schema = """scores: [int]<min=1, max=5>"""
    result = parser.parse(schema)

    assert "scores" in result
    assert isinstance(result["scores"], ListTypeNode)
    assert isinstance(result["scores"].item_type, ScalarTypeNode)
    assert result["scores"].item_type.type_name == "int"
    assert result["scores"].constraints["min"] == 1
    assert result["scores"].constraints["max"] == 5

    # Test nested lists
    schema = """matrix: [[int]]"""
    result = parser.parse(schema)

    assert "matrix" in result
    assert isinstance(result["matrix"], ListTypeNode)
    assert isinstance(result["matrix"].item_type, ListTypeNode)
    assert isinstance(result["matrix"].item_type.item_type, ScalarTypeNode)
    assert result["matrix"].item_type.item_type.type_name == "int"


def test_object_type_parsing():
    """Test parsing object types."""
    parser = SchemaParser()

    # Test basic object type
    schema = """
    user: {
        name: str,
        age: int
    }
    """
    result = parser.parse(schema)

    assert "user" in result
    assert isinstance(result["user"], ObjectTypeNode)
    assert "name" in result["user"].fields
    assert "age" in result["user"].fields
    assert isinstance(result["user"].fields["name"], ScalarTypeNode)
    assert result["user"].fields["name"].type_name == "str"
    assert isinstance(result["user"].fields["age"], ScalarTypeNode)
    assert result["user"].fields["age"].type_name == "int"

    # Test pattern object type
    schema = """scores: {int}"""
    result = parser.parse(schema)

    assert "scores" in result
    assert isinstance(result["scores"], ObjectTypeNode)
    assert result["scores"].pattern_value_type is not None
    assert isinstance(result["scores"].pattern_value_type, ScalarTypeNode)
    assert result["scores"].pattern_value_type.type_name == "int"

    # Test nested object
    schema = """
    address: {
        street: str,
        location: {
            lat: float,
            lng: float
        }
    }
    """
    result = parser.parse(schema)

    assert "address" in result
    assert isinstance(result["address"], ObjectTypeNode)
    assert "street" in result["address"].fields
    assert "location" in result["address"].fields
    assert isinstance(result["address"].fields["location"], ObjectTypeNode)
    assert "lat" in result["address"].fields["location"].fields
    assert "lng" in result["address"].fields["location"].fields


def test_union_type_parsing():
    """Test parsing union types."""
    parser = SchemaParser()

    # Test simple union
    schema = """id: str | int"""
    result = parser.parse(schema)

    assert "id" in result
    assert isinstance(result["id"], UnionTypeNode)
    assert len(result["id"].subtypes) == 2
    assert isinstance(result["id"].subtypes[0], ScalarTypeNode)
    assert result["id"].subtypes[0].type_name == "str"
    assert isinstance(result["id"].subtypes[1], ScalarTypeNode)
    assert result["id"].subtypes[1].type_name == "int"

    # Test complex union
    schema = """
    data: str | int | {
        value: float,
        unit: str
    }
    """
    result = parser.parse(schema)

    assert "data" in result
    assert isinstance(result["data"], UnionTypeNode)
    assert len(result["data"].subtypes) == 3
    assert isinstance(result["data"].subtypes[0], ScalarTypeNode)
    assert result["data"].subtypes[0].type_name == "str"
    assert isinstance(result["data"].subtypes[1], ScalarTypeNode)
    assert result["data"].subtypes[1].type_name == "int"
    assert isinstance(result["data"].subtypes[2], ObjectTypeNode)

    # Test union with default
    schema = """status: str | null = null"""
    result = parser.parse(schema)

    assert "status" in result
    assert isinstance(result["status"], UnionTypeNode)
    assert len(result["status"].subtypes) == 2
    assert result["status"].has_default
    assert result["status"].default is None


def test_multiline_schema_parsing():
    """Test parsing a multiline schema."""
    parser = SchemaParser()

    schema = """
    // Top-level schema fields
    name: str<min_length=1, max_length=100>  // User name
    
    age: int<min=0>  // User age
    
    address: {
        // Address fields
        street: str,
        city: str,
        zip: str<pattern="[0-9]{5}">  // 5-digit zip code
    }
    
    tags: [str]<max=10>  // Maximum 10 tags
    
    status: str<enum=["active", "inactive", "pending"]> | null  // User status or null
    """

    result = parser.parse(schema)

    # Log the parsed schema
    for field_name, type_node in result.items():
        log_schema_ast(type_node, f"Field: {field_name}")

    # Verify structure
    assert len(result) == 5
    assert "name" in result
    assert "age" in result
    assert "address" in result
    assert "tags" in result
    assert "status" in result

    # Check specific elements
    assert isinstance(result["name"], ScalarTypeNode)
    assert result["name"].constraints["min_length"] == 1
    assert result["name"].constraints["max_length"] == 100

    assert isinstance(result["address"], ObjectTypeNode)
    assert "street" in result["address"].fields
    assert "city" in result["address"].fields
    assert "zip" in result["address"].fields

    assert isinstance(result["tags"], ListTypeNode)
    assert result["tags"].constraints["max"] == 10

    assert isinstance(result["status"], UnionTypeNode)
    assert len(result["status"].subtypes) == 2
    assert isinstance(result["status"].subtypes[0], ScalarTypeNode)
    assert "enum" in result["status"].subtypes[0].constraints
    assert result["status"].subtypes[0].constraints["enum"] == ["active", "inactive", "pending"]
