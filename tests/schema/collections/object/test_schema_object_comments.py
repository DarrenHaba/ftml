"""
Test module for comment handling in schema parsing.

Verifies that all types of comments are properly ignored during schema parsing.
"""

import logging
import pytest

from ftml import FTMLParseError
from ftml.logger import logger
from ftml.schema.schema_ast import UnionTypeNode, ObjectTypeNode, ScalarTypeNode
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


def test_basic_comments_in_schema_parsing():
    """Test that basic comments are properly stripped during schema parsing."""
    parser = SchemaParser()

    # Schema with regular comments
    schema = """
    // Comment at the beginning
    field1: str  // Inline comment
    
    // Comment between fields
    field2: int
    """

    result = parser.parse(schema)

    # Check that we parsed the schema correctly despite comments
    assert "field1" in result
    assert result["field1"].type_name == "str"
    assert "field2" in result
    assert result["field2"].type_name == "int"


def test_doc_comments_ignored():
    """Test that documentation comments (/// and //!) are ignored."""
    parser = SchemaParser()

    # Schema with documentation comments
    schema = """
    //! Document-level inner doc comment
    //! Should be completely ignored

    /// Documentation for field1
    /// Multiple lines
    field1: str
    
    field2: {
        //! Documentation for object
        nested: int
    }
    """

    result = parser.parse(schema)

    # Check that doc comments didn't affect parsing
    assert "field1" in result
    assert result["field1"].type_name == "str"
    assert "field2" in result
    assert "nested" in result["field2"].fields
    assert result["field2"].fields["nested"].type_name == "int"


def test_comments_in_object_pattern():
    """Test comments within object pattern syntax."""
    parser = SchemaParser()

    # Schema with comments in object pattern
    schema = """
    pattern: { // Comment at object start
        // Comment before pattern type
        str // Comment after pattern type
    } // Comment after object close
    
    pattern_with_fields: {
        // Comment before field
        field1: int, // Comment after field
        
        /// Doc comment for field2
        field2: str // Another inline comment
    }
    """

    result = parser.parse(schema)

    # Check pattern parsing
    assert "pattern" in result
    assert result["pattern"].pattern_value_type is not None
    assert result["pattern"].pattern_value_type.type_name == "str"

    # Check object with fields
    assert "pattern_with_fields" in result
    assert "field1" in result["pattern_with_fields"].fields
    assert result["pattern_with_fields"].fields["field1"].type_name == "int"
    assert "field2" in result["pattern_with_fields"].fields
    assert result["pattern_with_fields"].fields["field2"].type_name == "str"


def test_complex_multiline_comments():
    """Test complex multiline comment scenarios."""
    parser = SchemaParser()

    # Schema with complex multiline comments
    schema = """
    // -----------------------------------------------
    // This is a complex schema with many comment types
    // -----------------------------------------------

    //! This is a schema for testing comment handling
    //! All of these comments should be completely ignored

    /// Documentation for user_info
    /// This has multiple lines
    /// And should be ignored
    user_info: {
        // Basic user information section
        // ---------------------------

        name: str<min_length=1>, // Name cannot be empty

        /// Age must be positive
        age?: int<min=0>,  // Optional age field

        // List of roles
        roles: [
            //! Inner doc for roles list
            str  // Each role is a string
        ],

        // Comment before object
        contact: {
            //! Contact information

            email: str,  // Primary email

            // Comment before optional field
            phone?: str  // Optional phone
        } // Comment after object
    } // Comment after top-level object
    """

    result = parser.parse(schema)

    # Check that the schema was parsed correctly despite all the comments
    assert "user_info" in result
    assert isinstance(result["user_info"], ObjectTypeNode)

    user_info = result["user_info"]
    assert "name" in user_info.fields
    assert user_info.fields["name"].type_name == "str"
    assert user_info.fields["name"].constraints.get("min_length") == 1

    assert "age" in user_info.fields
    assert user_info.fields["age"].type_name == "int"
    assert user_info.fields["age"].constraints.get("min") == 0
    assert user_info.fields["age"].optional

    assert "roles" in user_info.fields
    assert user_info.fields["roles"].item_type.type_name == "str"

    assert "contact" in user_info.fields
    contact = user_info.fields["contact"]
    assert "email" in contact.fields
    assert "phone" in contact.fields
    assert contact.fields["phone"].optional
