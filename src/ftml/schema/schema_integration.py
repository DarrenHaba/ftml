"""
FTML Schema Integration Module

Provides integration between the new schema system and the existing FTML system.
"""

import logging
import os
from typing import Dict, Any, Union as PyUnion

from ftml.logger import logger
from ftml.exceptions import FTMLParseError, FTMLValidationError

from .schema_parser import SchemaParser
from .schema_validator import validate_schema, apply_defaults

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def parse_schema(schema_data: PyUnion[str, os.PathLike]) -> Dict[str, Any]:
    """
    Parse an FTML schema definition.

    Args:
        schema_data: A string of schema definition or a file path to a schema file

    Returns:
        A dictionary representing the parsed schema structure

    Raises:
        FTMLParseError: If the schema cannot be parsed
    """
    logger.debug("Parsing schema")

    try:
        # If a file path is given, read its contents
        if isinstance(schema_data, (str, os.PathLike)) and os.path.exists(str(schema_data)):
            with open(schema_data, "r", encoding="utf-8") as f:
                schema_data = f.read()
                logger.debug(f"Read schema from file: {schema_data}")

        # Parse the schema
        parser = SchemaParser()
        schema = parser.parse(schema_data)

        # Log parsed schema
        logger.debug(f"Parsed schema with {len(schema)} root fields")

        return schema

    except Exception as e:
        if not isinstance(e, FTMLParseError):
            raise FTMLParseError(f"Error parsing schema: {str(e)}") from e
        raise


def validate_data(data: Dict[str, Any], schema: Dict[str, Any], strict: bool = True) -> None:
    """
    Validate data against a schema.

    Args:
        data: The data to validate
        schema: The schema to validate against
        strict: Whether to enforce strict validation

    Raises:
        FTMLValidationError: If validation fails
    """
    logger.debug("Validating data against schema")

    try:
        # Validate the data
        errors = validate_schema(data, schema, strict=strict)

        if errors:
            error_msg = "\n".join(errors)
            raise FTMLValidationError(f"Schema validation failed:\n{error_msg}", errors=errors)

        logger.debug("Validation successful")

    except Exception as e:
        if not isinstance(e, FTMLValidationError):
            raise FTMLValidationError(f"Schema validation error: {str(e)}") from e
        raise


def apply_schema_defaults(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply default values from a schema to a data dictionary.

    Args:
        data: The data dictionary to apply defaults to
        schema: The schema containing default values

    Returns:
        A new dictionary with default values applied
    """
    logger.debug("Applying schema defaults to data")
    return apply_defaults(data, schema)
