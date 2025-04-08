"""
FTML Schema Module

Provides schema parsing, validation, and default value application for FTML.
This is a complete rewrite of the schema functionality with a cleaner, more
modular design than the original implementation.
"""

import os
from typing import Dict, Any, List, Optional, Union as PyUnion

from ftml.logger import logger
from ftml.exceptions import FTMLParseError, FTMLValidationError

# Import internal schema components
from .schema_ast import SchemaTypeNode, ScalarTypeNode, UnionTypeNode, ListTypeNode, ObjectTypeNode
from .schema_parser import SchemaParser
from .schema_validator import SchemaValidator, apply_defaults


# Public API function for schema parsing
def parse_schema(schema_data: PyUnion[str, os.PathLike]) -> Dict[str, SchemaTypeNode]:
    """
    Parse an FTML schema string into a schema structure.

    Args:
        schema_data: A string of schema definition or a file path to a schema file

    Returns:
        A dictionary containing the parsed schema structure

    Raises:
        FTMLParseError: If there is a syntax error in the schema
    """
    try:
        # If a file path is given, read its contents
        if isinstance(schema_data, (str, os.PathLike)) and os.path.exists(str(schema_data)):
            logger.debug(f"Reading schema from file: {schema_data}")
            with open(schema_data, "r", encoding="utf-8") as f:
                schema_content = f.read()
        else:
            # Assume it's a schema string
            schema_content = schema_data

        # Parse the schema
        parser = SchemaParser()
        schema = parser.parse(schema_content)
        logger.debug(f"Parsed schema with {len(schema)} root fields")

        return schema

    except Exception as e:
        if not isinstance(e, FTMLParseError):
            raise FTMLParseError(f"Error parsing schema: {str(e)}") from e
        raise


# Public API function for schema validation
def validate_data(data: Dict[str, Any], schema: Dict[str, SchemaTypeNode], strict: bool = True) -> List[str]:
    """
    Validate data against a schema.

    Args:
        data: The data to validate
        schema: The schema to validate against
        strict: Whether to enforce strict validation (no extra properties)

    Returns:
        A list of validation error messages (empty if valid)

    Raises:
        FTMLValidationError: If validation fails
    """
    try:
        # Apply defaults to data
        data_with_defaults = apply_defaults(data, schema)

        # Validate data against schema
        validator = SchemaValidator(schema, strict=strict)
        errors = validator.validate(data_with_defaults)

        return errors

    except Exception as e:
        if not isinstance(e, FTMLValidationError):
            raise FTMLValidationError(f"Schema validation error: {str(e)}") from e
        raise


# Public API function to apply schema defaults
def apply_schema_defaults(data: Dict[str, Any], schema: Dict[str, SchemaTypeNode]) -> Dict[str, Any]:
    """
    Apply default values from a schema to a data dictionary.

    Args:
        data: The data dictionary to apply defaults to
        schema: The schema containing default values

    Returns:
        A new dictionary with default values applied
    """
    return apply_defaults(data, schema)


class Validator:
    """
    Validator for FTML data against schemas.
    Compatibility validator for maintaining a consistent validation interface.
    """

    def __init__(self, schema: Optional[Dict[str, Any]] = None, strict: bool = True):
        """
        Initialize the validator.

        Args:
            schema: The schema to validate against
            strict: Whether to enforce strict validation (no extra properties)
        """
        self.schema = schema
        self.strict = strict
        self.current_path = []  # Path tracking for error messages

    def validate(self, data: Any, schema: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Validate data against a schema.

        Args:
            data: The data to validate
            schema: The schema to validate against (overrides the instance schema)

        Returns:
            A list of validation error messages (empty if valid)
        """
        # Use provided schema or instance schema
        use_schema = schema if schema is not None else self.schema

        if use_schema is None:
            logger.debug("No schema provided, skipping validation")
            return []  # No schema to validate against

        # Convert schema to SchemaTypeNode if needed
        schema_ast = self._convert_schema_to_ast(use_schema)

        # Create validator and validate
        validator = SchemaValidator(schema_ast, strict=self.strict)
        return validator.validate(data)

    def _convert_schema_to_ast(self, schema: Dict[str, Any]) -> Dict[str, SchemaTypeNode]:
        """
        Convert schema dictionary to AST nodes.

        Args:
            schema: Schema in dictionary format

        Returns:
            Schema as AST nodes
        """
        result = {}

        for field_name, type_info in schema.items():
            # Check if type_info is already a SchemaTypeNode
            if isinstance(type_info, SchemaTypeNode):
                result[field_name] = type_info
            else:
                # Convert dictionary to type node
                result[field_name] = self._convert_dict_to_type_node(type_info)

        return result

    def _convert_dict_to_type_node(self, type_info: Dict[str, Any]) -> SchemaTypeNode:
        """
        Convert type information dictionary to a SchemaTypeNode.

        Args:
            type_info: Type information in dictionary format

        Returns:
            Equivalent SchemaTypeNode representing the type
        """
        type_name = type_info.get("type", "any")

        if type_name == "union":
            node = UnionTypeNode()

            # Convert subtypes
            for subtype in type_info.get("subtypes", []):
                node.subtypes.append(self._convert_dict_to_type_node(subtype))

        elif type_name == "list":
            node = ListTypeNode()

            # Set item type if present
            if "item_type" in type_info:
                node.item_type = self._convert_dict_to_type_node(type_info["item_type"])

        elif type_name == "dict":
            node = ObjectTypeNode()

            # Set pattern value type or fields
            if "value_type" in type_info:
                node.pattern_value_type = self._convert_dict_to_type_node(type_info["value_type"])
            elif "dict_schema" in type_info:
                for field_name, field_type in type_info["dict_schema"].items():
                    node.fields[field_name] = self._convert_dict_to_type_node(field_type)

        else:
            # Scalar type
            node = ScalarTypeNode(type_name)

        # Set common properties
        node.constraints = type_info.get("constraints", {})
        node.optional = type_info.get("optional", False)

        if type_info.get("has_default", False):
            node.has_default = True
            node.default = type_info.get("default")

        return node


# Re-export components that are part of the public API
__all__ = [
    "SchemaParser",
    "Validator",
    "parse_schema",
    "validate_data",
    "apply_schema_defaults",
    "apply_defaults",  # Also expose the direct function
]


# Ensure backward compatibility by importing these from schema_parser
try:
    from ftml.schema_parser import SchemaParser as InternalSchemaParser

    schema_parser = InternalSchemaParser
except ImportError:
    # Fallback if not available
    schema_parser = None
