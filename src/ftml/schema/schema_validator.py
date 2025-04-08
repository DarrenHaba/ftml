"""
FTML Schema Validator Module

Validates data against schema definitions.
"""

from typing import Dict, Any, List, Optional

from ftml.logger import logger
from ftml import FTMLDict

from .schema_datetime_validators import convert_value
from .schema_ast import SchemaTypeNode, ScalarTypeNode, UnionTypeNode, ListTypeNode, ObjectTypeNode
from .schema_type_validators import TypeValidator, ScalarValidator, UnionValidator, ListValidator, ObjectValidator


class SchemaValidator:
    """
    Validates data against a schema.

    This class handles validating data structures against FTML schema
    definitions, reporting detailed validation errors.
    """

    def __init__(self, schema: Dict[str, SchemaTypeNode], strict: bool = True):
        """
        Initialize the validator with a schema.

        Args:
            schema: The schema to validate against
            strict: Whether to enforce strict validation (no extra properties)
        """
        self.schema = schema
        self.strict = strict
        self.current_path = []  # Path tracking for error messages
        logger.debug(f"Initialized validator with strict={strict}")
        if schema:
            logger.debug(f"Schema has {len(schema)} root fields")

    def validate(self, data: Any) -> List[str]:
        """
        Validate data against the schema.

        Args:
            data: The data to validate

        Returns:
            A list of validation error messages (empty if valid)
        """
        logger.debug("Starting validation")
        if not self.schema:
            logger.debug("No schema provided, skipping validation")
            return []  # No schema to validate against

        errors = []

        # Handle dict data
        if isinstance(data, dict):
            logger.debug(f"Validating dict data with {len(data)} keys")

            # Check for required fields in schema
            for field_name, field_type in self.schema.items():
                field_path = field_name

                # Check if field exists
                if field_name not in data:
                    # Field is missing
                    if not field_type.optional and not field_type.has_default:
                        error_msg = f"Missing required field: '{field_path}'"
                        logger.debug(f"Validation error: {error_msg}")
                        errors.append(error_msg)
                else:
                    # Field exists, validate it
                    field_value = data[field_name]
                    field_errors = self._validate_field(field_value, field_type, field_path)
                    errors.extend(field_errors)

            # Check for extra fields in strict mode
            if self.strict:
                for field_name in data:
                    if field_name not in self.schema:
                        error_msg = f"Unknown field: '{field_name}'"
                        logger.debug(f"Strict validation error: {error_msg}")
                        errors.append(error_msg)
        else:
            error_msg = f"Expected object at root, got {type(data).__name__}"
            logger.debug(f"Validation error: {error_msg}")
            errors.append(error_msg)

        if errors:
            logger.debug(f"Validation completed with {len(errors)} errors")
        else:
            logger.debug("Validation completed successfully with no errors")

        return errors

    def _validate_field(self, value: Any, type_node: SchemaTypeNode, path: str) -> List[str]:
        """
        Validate a field against its type.

        Args:
            value: The value to validate
            type_node: The type node to validate against
            path: The field path for error messages

        Returns:
            A list of validation error messages (empty if valid)
        """
        logger.debug(f"Validating field '{path}' with type {type(type_node).__name__}")

        # Convert SchemaTypeNode to validator-compatible dict
        type_info = self._convert_type_node_to_dict(type_node)

        # Create appropriate validator
        validator = self._create_validator_for_type(type_node)

        # Validate the field
        return validator.validate(value, type_info, path)

    def _convert_type_node_to_dict(self, type_node: SchemaTypeNode) -> Dict[str, Any]:
        """
        Convert a SchemaTypeNode to a dictionary format for validators.

        Args:
            type_node: The type node to convert

        Returns:
            A dictionary representation of the type node
        """
        if isinstance(type_node, ScalarTypeNode):
            return {
                "type": type_node.type_name,
                "constraints": type_node.constraints,
                "has_default": type_node.has_default,
                "default": type_node.default,
                "optional": type_node.optional,
            }

        elif isinstance(type_node, ListTypeNode):
            result = {
                "type": "list",
                "constraints": type_node.constraints,
                "has_default": type_node.has_default,
                "default": type_node.default,
                "optional": type_node.optional,
            }

            if type_node.item_type:
                result["item_type"] = self._convert_type_node_to_dict(type_node.item_type)

            return result

        elif isinstance(type_node, ObjectTypeNode):
            result = {
                "type": "dict",
                "constraints": type_node.constraints,
                "has_default": type_node.has_default,
                "default": type_node.default,
                "optional": type_node.optional,
                "strict": self.strict,
                "ext": getattr(type_node, "ext", False),
            }

            if type_node.pattern_value_type:
                result["pattern_value_type"] = self._convert_type_node_to_dict(type_node.pattern_value_type)
            elif type_node.fields:
                fields = {}
                for field_name, field_type in type_node.fields.items():
                    fields[field_name] = self._convert_type_node_to_dict(field_type)
                result["fields"] = fields

            return result

        elif isinstance(type_node, UnionTypeNode):
            subtypes = []
            for subtype in type_node.subtypes:
                subtypes.append(self._convert_type_node_to_dict(subtype))

            return {
                "type": "union",
                "subtypes": subtypes,
                "has_default": type_node.has_default,
                "default": type_node.default,
                "optional": type_node.optional,
            }

        else:
            # Fallback for unknown type nodes
            return {
                "type": "any",
                "has_default": type_node.has_default,
                "default": type_node.default,
                "optional": type_node.optional,
            }

    def _create_validator_for_type(self, type_node: SchemaTypeNode) -> TypeValidator:
        """
        Create an appropriate validator for the given type node.

        Args:
            type_node: The type node

        Returns:
            A TypeValidator instance
        """
        if isinstance(type_node, ScalarTypeNode):
            return ScalarValidator()
        elif isinstance(type_node, ListTypeNode):
            return ListValidator()
        elif isinstance(type_node, ObjectTypeNode):
            return ObjectValidator()
        elif isinstance(type_node, UnionTypeNode):
            return UnionValidator()
        else:
            # Fallback for unknown type nodes
            return TypeValidator()


def apply_defaults(data: Dict[str, Any], schema: Dict[str, SchemaTypeNode]) -> Dict[str, Any]:
    """
    Apply default values from a schema to a data dictionary.

    Args:
        data: The data dictionary to apply defaults to
        schema: The schema containing default values

    Returns:
        A new dictionary with default values applied
    """
    logger.debug("Applying default values to data")
    if not isinstance(data, dict) or not isinstance(schema, dict):
        logger.debug("Cannot apply defaults: data or schema is not a dictionary")
        return data

    # Preserve FTMLDict and _ast_node if present
    if hasattr(data, "_ast_node") and data._ast_node is not None:
        result = FTMLDict(data)
        result._ast_node = data._ast_node
    else:
        result = data.copy()

    logger.debug(f"Applying defaults for {len(schema)} schema fields")

    for key, type_node in schema.items():
        if key in result:
            logger.debug(f"Field '{key}' exists in data, checking for nested defaults")

            # If the field is an object with fields, apply defaults recursively
            if isinstance(result[key], dict) and isinstance(type_node, ObjectTypeNode) and type_node.fields:
                logger.debug(f"Recursively applying defaults to dict field '{key}'")
                result[key] = apply_defaults(result[key], type_node.fields)

            # If the field is a list, handle recursive application of defaults
            elif isinstance(result[key], list) and isinstance(type_node, ListTypeNode):
                logger.debug(f"Recursively applying defaults to list field '{key}'")
                # Handle nested lists (lists of lists)
                if isinstance(type_node.item_type, ListTypeNode):
                    for i, sublist in enumerate(result[key]):
                        if isinstance(sublist, list):
                            # Process each nested list recursively
                            for j, item in enumerate(sublist):
                                if isinstance(item, dict) and isinstance(type_node.item_type.item_type, ObjectTypeNode):
                                    # Apply defaults for missing fields in each object
                                    result[key][i][j] = apply_defaults_to_object(
                                        item, type_node.item_type.item_type.fields
                                    )

                # Handle standard lists of objects
                elif isinstance(type_node.item_type, ObjectTypeNode):
                    for i, item in enumerate(result[key]):
                        if isinstance(item, dict):
                            # Apply defaults for missing fields in each object
                            result[key][i] = apply_defaults_to_object(item, type_node.item_type.fields)

            # Handle date/time type conversions
            elif hasattr(type_node, "type_name") and type_node.type_name in ("date", "time", "datetime", "timestamp"):
                constraints = type_node.constraints if hasattr(type_node, "constraints") else {}
                result[key] = convert_value_by_schema(result[key], type_node.type_name, constraints)

            continue

        # Field is missing - check if it has a default value
        if type_node.has_default:
            # Apply the default value
            logger.debug(f"Applying default value for missing field '{key}'")
            result[key] = type_node.default

            # Convert date/time defaults if needed
            if hasattr(type_node, "type_name") and type_node.type_name in ("date", "time", "datetime", "timestamp"):
                constraints = type_node.constraints if hasattr(type_node, "constraints") else {}
                result[key] = convert_value_by_schema(result[key], type_node.type_name, constraints)

            # If the default is a dict and this is an object type with fields, apply nested defaults
            if isinstance(result[key], dict) and isinstance(type_node, ObjectTypeNode) and type_node.fields:
                logger.debug(f"Recursively applying defaults to default dict '{key}'")
                result[key] = apply_defaults(result[key], type_node.fields)

        # For required objects without defaults, create an empty dict and apply defaults
        elif not type_node.optional and isinstance(type_node, ObjectTypeNode) and type_node.fields:
            logger.debug(f"Creating empty dict with defaults for required field '{key}'")
            result[key] = apply_defaults({}, type_node.fields)

        # Don't add empty objects for optional fields without defaults
        elif type_node.optional:
            # For optional fields without defaults, don't add them
            logger.debug(f"Skipping optional field '{key}' without default")

        else:
            logger.debug(f"No default available for required field '{key}'")

    logger.debug(f"Finished applying defaults, result has {len(result)} fields")
    return result


def apply_defaults_to_object(obj_data: Dict[str, Any], obj_schema: Dict[str, SchemaTypeNode]) -> Dict[str, Any]:
    """Apply defaults to an object, including handling missing fields."""
    result = obj_data.copy()

    # Check for missing fields and apply defaults
    for field_name, field_type in obj_schema.items():
        if field_name not in result:
            # Field is missing - check if it has a default value
            if field_type.has_default:
                # Apply the default value
                logger.debug(f"Applying default value for missing field '{field_name}' in object")
                result[field_name] = field_type.default

    return result


def validate_schema(data: Dict[str, Any], schema: Dict[str, SchemaTypeNode], strict: bool = True) -> List[str]:
    """
    Validate data against a schema.

    Args:
        data: The data to validate
        schema: The schema to validate against
        strict: Whether to enforce strict validation

    Returns:
        A list of validation error messages (empty if valid)

    Raises:
        FTMLValidationError: If validation fails
    """
    # Apply defaults to data
    data_with_defaults = apply_defaults(data, schema)

    # Validate data against schema
    validator = SchemaValidator(schema, strict=strict)
    errors = validator.validate(data_with_defaults)

    return errors


def convert_value_by_schema(value: Any, type_name: str, constraints: Optional[Dict[str, Any]] = None) -> Any:
    """
    Convert a value based on its schema type, primarily for date/time types.

    Args:
        value: The value to convert
        type_name: The type name from schema
        constraints: Optional constraints dictionary

    Returns:
        Converted value if applicable, original value otherwise
    """
    # Handle date/time types
    if type_name in ("date", "time", "datetime", "timestamp"):
        return convert_value(value, type_name, constraints)

    # Return original value for other types
    return value
