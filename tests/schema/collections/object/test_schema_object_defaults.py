"""
Test module for object syntax in schemas.

Focuses on testing both {T} and {str: T} syntax for object patterns.
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

