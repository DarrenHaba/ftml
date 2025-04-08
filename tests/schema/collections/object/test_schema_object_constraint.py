"""
Test module for object syntax in schemas.

Focuses on testing both {T} and {str: T} syntax for object patterns.
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
