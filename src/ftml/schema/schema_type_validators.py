"""
FTML Type Validators Module

Provides validator classes for different types of schema values.
"""

from typing import Any, List, Dict

from ftml.logger import logger

from .schema_datetime_validators import validate_date, validate_time, validate_datetime, validate_timestamp


class TypeValidator:
    """
    Base class for all type validators.

    Type validators check if a value matches a type definition
    and satisfies its constraints.
    """

    def __init__(self):
        """Initialize the type validator."""
        pass

    def validate(self, value: Any, type_info: Dict[str, Any], path: str) -> List[str]:
        """
        Validate a value against a type definition.

        Args:
            value: The value to validate
            type_info: Type information including constraints
            path: The current validation path for error messages

        Returns:
            A list of validation error messages (empty if valid)
        """
        # Basic implementation - should be overridden
        return []


class ScalarValidator(TypeValidator):
    """
    Validator for scalar types (str, int, float, bool, null).
    """

    def validate(self, value: Any, type_info: Dict[str, Any], path: str) -> List[str]:
        """
        Validate a value against a scalar type definition.

        Args:
            value: The value to validate
            type_info: Type information including constraints
            path: The current validation path for error messages

        Returns:
            A list of validation error messages (empty if valid)
        """
        errors = []
        type_name = type_info["type"]
        constraints = type_info.get("constraints", {})

        # First validate the type - passing constraints to _validate_type
        # so we can use them for format validation
        type_errors = self._validate_type(value, type_name, path, constraints)
        if type_errors:
            return type_errors  # If type is invalid, don't check constraints

        # Then validate constraints
        constraint_errors = self._validate_constraints(value, type_name, constraints, path)
        errors.extend(constraint_errors)

        return errors

    def _validate_type(self, value: Any, type_name: str, path: str, constraints: Dict[str, Any] = None) -> List[str]:
        """
        Validate that a value is of the expected type.

        Args:
            value: The value to validate
            type_name: The expected type name
            path: The current validation path for error messages
            constraints: Optional constraints to consider for type validation

        Returns:
            A list of validation error messages (empty if valid)
        """
        errors = []
        constraints = constraints or {}

        if type_name == "str":
            if not isinstance(value, str):
                errors.append(f"Expected string at '{path}', got {type(value).__name__}")

        elif type_name == "int":
            # Make sure it's an int but not a bool (which is a subclass of int in Python)
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(f"Expected integer at '{path}', got {type(value).__name__}")

        elif type_name == "float":
            # Allow int or float
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"Expected float at '{path}', got {type(value).__name__}")

        elif type_name == "bool":
            if not isinstance(value, bool):
                errors.append(f"Expected boolean at '{path}', got {type(value).__name__}")

        elif type_name == "null":
            if value is not None:
                errors.append(f"Expected null at '{path}', got {type(value).__name__}")

        elif type_name == "any":
            # Any type is valid
            pass

        # Date/Time Types - Pass format constraint to validator
        elif type_name == "date":
            # Use format constraint if available
            format_str = constraints.get("format")
            format_errors = validate_date(value, format_str)
            if format_errors:
                for error in format_errors:
                    errors.append(f"{error} at '{path}'")

        elif type_name == "time":
            # Use format constraint if available
            format_str = constraints.get("format")
            format_errors = validate_time(value, format_str)
            if format_errors:
                for error in format_errors:
                    errors.append(f"{error} at '{path}'")

        elif type_name == "datetime":
            # Use format constraint if available
            format_str = constraints.get("format")
            format_errors = validate_datetime(value, format_str)
            if format_errors:
                for error in format_errors:
                    errors.append(f"{error} at '{path}'")

        elif type_name == "timestamp":
            # Basic type validation - precision constraints handled in _validate_constraint
            precision = constraints.get("precision")
            timestamp_errors = validate_timestamp(value, precision)
            if timestamp_errors:
                for error in timestamp_errors:
                    errors.append(f"{error} at '{path}'")

        else:
            # Unknown type
            errors.append(f"Unknown type '{type_name}' at '{path}'")

        return errors

    def _validate_constraints(self, value: Any, type_name: str, constraints: Dict[str, Any], path: str) -> List[str]:
        """
        Validate that a value satisfies its constraints.

        Args:
            value: The value to validate
            type_name: The type name
            constraints: The constraints to check
            path: The current validation path for error messages

        Returns:
            A list of validation error messages (empty if valid)
        """
        errors = []

        for constraint_name, constraint_value in constraints.items():
            constraint_errors = self._validate_constraint(value, type_name, constraint_name, constraint_value, path)
            errors.extend(constraint_errors)

        return errors

    def _validate_constraint(
        self, value: Any, type_name: str, constraint_name: str, constraint_value: Any, path: str
    ) -> List[str]:
        """
        Validate a single constraint for a value.

        Args:
            value: The value to validate
            type_name: The type of the value
            constraint_name: The name of the constraint
            constraint_value: The constraint value
            path: The current validation path for error messages

        Returns:
            A list of validation error messages (empty if valid)
        """
        errors = []

        # Handle date/time specific constraints
        if type_name == "date" and constraint_name == "format":
            format_errors = validate_date(value, constraint_value)
            if format_errors:
                for error in format_errors:
                    errors.append(f"{error} at '{path}'")

        elif type_name == "time" and constraint_name == "format":
            format_errors = validate_time(value, constraint_value)
            if format_errors:
                for error in format_errors:
                    errors.append(f"{error} at '{path}'")

        elif type_name == "datetime" and constraint_name == "format":
            format_errors = validate_datetime(value, constraint_value)
            if format_errors:
                for error in format_errors:
                    errors.append(f"{error} at '{path}'")

        elif type_name == "timestamp" and constraint_name == "precision":
            timestamp_errors = validate_timestamp(value, constraint_value)
            if timestamp_errors:
                for error in timestamp_errors:
                    errors.append(f"{error} at '{path}'")

        # Special handling for enum constraint
        elif constraint_name == "enum":
            if isinstance(constraint_value, list):
                # Check if value is in the allowed list
                if value not in constraint_value:
                    # Create a nicely formatted list of allowed values for the error message
                    if all(isinstance(v, str) for v in constraint_value):
                        allowed = ", ".join(f'"{v}"' for v in constraint_value)
                    else:
                        allowed = ", ".join(str(v) for v in constraint_value)

                    errors.append(f"Value '{value}' at '{path}' is not in allowed values: {allowed}")
            else:
                errors.append(f"Invalid enum constraint at '{path}': expected list")

        # String constraints
        elif type_name == "str":
            if constraint_name == "min_length" or constraint_name == "min":
                if len(value) < constraint_value:
                    errors.append(f"String at '{path}' is too short (minimum length: {constraint_value})")

            elif constraint_name == "max_length" or constraint_name == "max":
                if len(value) > constraint_value:
                    errors.append(f"String at '{path}' is too long (maximum length: {constraint_value})")

            elif constraint_name == "pattern":
                try:
                    import re

                    pattern = re.compile(constraint_value)
                    if not pattern.match(value):
                        errors.append(f"String at '{path}' does not match pattern: {constraint_value}")
                except re.error:
                    errors.append(f"Invalid regex pattern at '{path}': {constraint_value}")

        # Numeric constraints
        elif type_name in ("int", "float"):
            if constraint_name == "min":
                if value < constraint_value:
                    errors.append(f"Number at '{path}' is too small (minimum: {constraint_value})")

            elif constraint_name == "max":
                if value > constraint_value:
                    errors.append(f"Number at '{path}' is too large (maximum: {constraint_value})")

            elif constraint_name == "precision" and type_name == "float":
                str_value = str(value)
                if "." in str_value:
                    decimal_places = len(str_value.split(".")[1])
                    if decimal_places > constraint_value:
                        errors.append(f"Float at '{path}' has too many decimal places (maximum: {constraint_value})")

        # Date/time min/max constraints
        elif type_name == "date" and constraint_name == "min":
            try:
                from datetime import datetime

                min_date = datetime.strptime(constraint_value, "%Y-%m-%d").date()
                value_date = datetime.strptime(value, "%Y-%m-%d").date()

                if value_date < min_date:
                    errors.append(f"Date '{value}' at '{path}' is before minimum date {constraint_value}")
            except ValueError:
                errors.append(f"Invalid date format for min constraint at '{path}'")

        elif type_name == "date" and constraint_name == "max":
            try:
                from datetime import datetime

                max_date = datetime.strptime(constraint_value, "%Y-%m-%d").date()
                value_date = datetime.strptime(value, "%Y-%m-%d").date()

                if value_date > max_date:
                    errors.append(f"Date '{value}' at '{path}' is after maximum date {constraint_value}")
            except ValueError:
                errors.append(f"Invalid date format for max constraint at '{path}'")

        elif type_name == "timestamp" and constraint_name == "min":
            if value < constraint_value:
                errors.append(f"Timestamp {value} at '{path}' is before minimum timestamp {constraint_value}")

        elif type_name == "timestamp" and constraint_name == "max":
            if value > constraint_value:
                errors.append(f"Timestamp {value} at '{path}' is after maximum timestamp {constraint_value}")

        return errors


class UnionValidator(TypeValidator):
    """
    Validator for union types (type1 | type2 | ...).
    """

    def validate(self, value: Any, type_info: Dict[str, Any], path: str) -> List[str]:
        """
        Validate a value against a union type definition.

        Args:
            value: The value to validate
            type_info: Type information including subtypes
            path: The current validation path for error messages

        Returns:
            A list of validation error messages (empty if valid)
        """
        # For union types, we need to check if the value is valid for any of the subtypes
        if "subtypes" not in type_info:
            return [f"Invalid union type definition at '{path}'"]

        # Try each subtype until one validates successfully
        all_subtypes_errors = []
        subtypes = type_info["subtypes"]

        logger.debug(f"Validating union type at '{path}' with {len(subtypes)} subtypes")

        for i, subtype in enumerate(subtypes):
            subtype_name = subtype.get("type", f"subtype{i}")
            logger.debug(f"Trying union subtype {i + 1}/{len(subtypes)}: {subtype_name}")

            # Create appropriate validator for this subtype
            subtype_validator = create_validator_for_type(subtype)

            # Check if this subtype validates
            subtype_errors = subtype_validator.validate(value, subtype, path)

            if not subtype_errors:
                # This subtype validates successfully
                logger.debug(f"Value matches union subtype {subtype_name}")
                return []

            all_subtypes_errors.extend(subtype_errors)

        # If we get here, no subtype validated successfully
        error_msg = f"Value at '{path}' does not match any allowed types in the union"
        logger.debug(f"Validation error: {error_msg}")
        return [error_msg]


class ListValidator(TypeValidator):
    """
    Validator for list types ([item_type]).
    """

    def validate(self, value: Any, type_info: Dict[str, Any], path: str) -> List[str]:
        """
        Validate a value against a list type definition.

        Args:
            value: The value to validate
            type_info: Type information including item_type and constraints
            path: The current validation path for error messages

        Returns:
            A list of validation error messages (empty if valid)
        """
        errors = []

        # First check that the value is a list
        if not isinstance(value, list):
            return [f"Expected list at '{path}', got {type(value).__name__}"]

        # Check list constraints
        constraints = type_info.get("constraints", {})
        for constraint_name, constraint_value in constraints.items():
            if constraint_name == "min" or constraint_name == "min_items":
                if len(value) < constraint_value:
                    errors.append(f"List at '{path}' is too short (minimum items: {constraint_value})")

            elif constraint_name == "max" or constraint_name == "max_items":
                if len(value) > constraint_value:
                    errors.append(f"List at '{path}' is too long (maximum items: {constraint_value})")

            elif constraint_name == "unique" and constraint_value is True:
                # Check for duplicate items
                seen = set()
                duplicates = []
                for i, item in enumerate(value):
                    # Only works for hashable items
                    try:
                        if item in seen:
                            duplicates.append(i)
                        seen.add(item)
                    except TypeError:
                        # Skip uniqueness check for unhashable items
                        errors.append(f"Cannot check uniqueness for unhashable item at '{path}[{i}]'")

                if duplicates:
                    errors.append(f"List at '{path}' contains duplicate items at positions: {duplicates}")

        # Check item type if specified
        if "item_type" in type_info:
            item_type = type_info["item_type"]
            item_validator = create_validator_for_type(item_type)

            # Validate each item in the list
            for i, item in enumerate(value):
                item_path = f"{path}[{i}]"
                item_errors = item_validator.validate(item, item_type, item_path)
                errors.extend(item_errors)

        return errors


class ObjectValidator(TypeValidator):
    """
    Validator for object types ({field1: type1, ...}).
    """

    def validate(self, value: Any, type_info: Dict[str, Any], path: str) -> List[str]:
        """
        Validate a value against an object type definition.

        Args:
            value: The value to validate
            type_info: Type information including fields and constraints
            path: The current validation path for error messages

        Returns:
            A list of validation error messages (empty if valid)
        """
        errors = []

        # First check that the value is an object (dict)
        if not isinstance(value, dict):
            return [f"Expected object at '{path}', got {type(value).__name__}"]

        # Check object constraints
        constraints = type_info.get("constraints", {})
        for constraint_name, constraint_value in constraints.items():
            if constraint_name == "min" or constraint_name == "min_properties":
                if len(value) < constraint_value:
                    errors.append(f"Object at '{path}' has too few properties (minimum: {constraint_value})")

            elif constraint_name == "max" or constraint_name == "max_properties":
                if len(value) > constraint_value:
                    errors.append(f"Object at '{path}' has too many properties (maximum: {constraint_value})")

            elif constraint_name == "required_keys":
                missing_keys = []
                for required_key in constraint_value:
                    if required_key not in value:
                        missing_keys.append(required_key)

                if missing_keys:
                    errors.append(f"Object at '{path}' is missing required keys: {missing_keys}")

        # Check field types if specified
        if "fields" in type_info:
            fields = type_info["fields"]

            # Check each field in the schema
            for field_name, field_type in fields.items():
                field_path = f"{path}.{field_name}"

                # Check if required field is missing
                if field_name not in value:
                    if not field_type.get("optional", False) and not field_type.get("has_default", False):
                        errors.append(f"Missing required field: '{field_path}'")
                else:
                    # Field exists, validate it
                    field_validator = create_validator_for_type(field_type)
                    field_errors = field_validator.validate(value[field_name], field_type, field_path)
                    errors.extend(field_errors)

            # # Check for extra fields in strict mode
            # if type_info.get("strict", True):
            #     extra_fields = []
            #     for field_name in value:
            #         if field_name not in fields:
            #             extra_fields.append(field_name)
            #
            #     if extra_fields:
            #         errors.append(f"Object at '{path}' contains unknown fields: {extra_fields}")
            # Check for extra fields based on global strict mode AND per-object ext flag
            should_check_extra = type_info.get("strict", True) and not type_info.get("ext", False)
            if should_check_extra:
                extra_fields = []
                for field_name in value:
                    if field_name not in fields:
                        extra_fields.append(field_name)

                if extra_fields:
                    errors.append(f"Object at '{path}' contains unknown fields: {extra_fields}")

        # Check pattern value type if specified
        elif "pattern_value_type" in type_info:
            pattern_type = type_info["pattern_value_type"]
            pattern_validator = create_validator_for_type(pattern_type)

            # Validate each value in the object
            for key, val in value.items():
                val_path = f"{path}.{key}"
                val_errors = pattern_validator.validate(val, pattern_type, val_path)
                errors.extend(val_errors)

        return errors


def create_validator_for_type(type_info: Dict[str, Any]) -> TypeValidator:
    """
    Create an appropriate validator for the given type.

    Args:
        type_info: Type information

    Returns:
        A TypeValidator instance
    """
    type_name = type_info.get("type")

    if type_name == "union":
        return UnionValidator()
    elif type_name == "list":
        return ListValidator()
    elif type_name == "dict":
        return ObjectValidator()
    else:
        return ScalarValidator()
