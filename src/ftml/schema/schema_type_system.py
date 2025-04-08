"""
FTML Type System Module

Provides a registry for type definitions and validation rules.
"""

from typing import Dict, Any, Callable, Set

from ftml.logger import logger
from ftml.exceptions import FTMLParseError


class TypeSystem:
    """
    Registry for FTML type definitions and validation rules.

    This class maintains a registry of all available types and their
    validation functions, allowing for extensible type support.
    """

    def __init__(self):
        """Initialize the type system with built-in scalar types."""
        # Dictionary mapping type names to validator functions
        self.validators: Dict[str, Callable] = {}

        # Dictionary mapping type names to constraint validators
        self.constraint_validators: Dict[str, Dict[str, Callable]] = {}

        # Set of all scalar types
        self.scalar_types: Set[str] = {
            "str",
            "int",
            "float",
            "bool",
            "null",
            "any",
            "date",
            "time",
            "datetime",
            "timestamp",
        }

        # Set of special collection types
        self.collection_types: Set[str] = {"list", "dict"}

        # Register built-in types
        self._register_builtin_types()

    def _register_builtin_types(self):
        """Register built-in scalar types and their validators."""
        logger.debug("Registering built-in types")

        # Register basic types
        for type_name in self.scalar_types:
            self.validators[type_name] = lambda x, t=type_name: logger.debug(f"Validating {t}: {x}")
            self.constraint_validators[type_name] = {}

        # Register specific validators for date/time types
        if "date" in self.scalar_types:
            self.register_constraint_validator("date", "format", self._validate_date_format)
            self.register_constraint_validator("date", "min", self._validate_date_min)
            self.register_constraint_validator("date", "max", self._validate_date_max)

        if "time" in self.scalar_types:
            self.register_constraint_validator("time", "format", self._validate_time_format)

        if "datetime" in self.scalar_types:
            self.register_constraint_validator("datetime", "format", self._validate_datetime_format)
            self.register_constraint_validator("datetime", "min", self._validate_datetime_min)
            self.register_constraint_validator("datetime", "max", self._validate_datetime_max)

        if "timestamp" in self.scalar_types:
            self.register_constraint_validator("timestamp", "precision", self._validate_timestamp_precision)
            self.register_constraint_validator("timestamp", "min", self._validate_timestamp_min)
            self.register_constraint_validator("timestamp", "max", self._validate_timestamp_max)

    def register_type(self, type_name: str, validator: Callable, is_scalar: bool = False):
        """
        Register a new type with its validator.

        Args:
            type_name: The name of the type to register
            validator: The function that validates values of this type
            is_scalar: Whether this is a scalar type
        """
        logger.debug(f"Registering type: {type_name}")
        self.validators[type_name] = validator

        if is_scalar:
            self.scalar_types.add(type_name)

        # Initialize empty constraint validators dictionary
        if type_name not in self.constraint_validators:
            self.constraint_validators[type_name] = {}

    def register_constraint_validator(self, type_name: str, constraint_name: str, validator: Callable):
        """
        Register a constraint validator for a specific type.

        Args:
            type_name: The name of the type
            constraint_name: The name of the constraint
            validator: Function that validates the constraint
        """
        logger.debug(f"Registering constraint validator for {type_name}.{constraint_name}")

        if type_name not in self.constraint_validators:
            self.constraint_validators[type_name] = {}

        self.constraint_validators[type_name][constraint_name] = validator

    def is_scalar_type(self, type_name: str) -> bool:
        """
        Check if a type is a scalar type.

        Args:
            type_name: The name of the type to check

        Returns:
            True if the type is scalar, False otherwise
        """
        return type_name in self.scalar_types

    def is_collection_type(self, type_name: str) -> bool:
        """
        Check if a type is a collection type.

        Args:
            type_name: The name of the type to check

        Returns:
            True if the type is a collection, False otherwise
        """
        return type_name in self.collection_types

    def validate_type(self, value: Any, type_name: str) -> bool:
        """
        Validate a value against a type.

        Args:
            value: The value to validate
            type_name: The name of the type to validate against

        Returns:
            True if the value is valid for the type, False otherwise
        """
        if type_name not in self.validators:
            raise FTMLParseError(f"Unknown type: {type_name}")

        return self.validators[type_name](value)

    def validate_constraint(self, value: Any, type_name: str, constraint_name: str, constraint_value: Any) -> bool:
        """
        Validate a constraint for a value of a specific type.

        Args:
            value: The value to validate
            type_name: The name of the type
            constraint_name: The name of the constraint
            constraint_value: The value of the constraint

        Returns:
            True if the constraint is satisfied, False otherwise
        """
        if type_name not in self.constraint_validators or constraint_name not in self.constraint_validators[type_name]:
            raise FTMLParseError(f"Unknown constraint {constraint_name} for type {type_name}")

        return self.constraint_validators[type_name][constraint_name](value, constraint_value)

    def _validate_date_format(self, value, constraint_value, path):
        """Validate date format constraint."""
        # Format validation is handled in type_validators.py
        return []

    def _validate_date_min(self, value, constraint_value, path):
        """Validate minimum date constraint."""
        try:
            from datetime import datetime

            min_date = datetime.strptime(constraint_value, "%Y-%m-%d").date()
            value_date = datetime.strptime(value, "%Y-%m-%d").date()

            if value_date < min_date:
                return [f"Date '{value}' at '{path}' is before minimum date {constraint_value}"]
        except ValueError:
            return [f"Invalid date format for min constraint at '{path}'"]
        return []

    def _validate_date_max(self, value, constraint_value, path):
        """Validate maximum date constraint."""
        try:
            from datetime import datetime

            max_date = datetime.strptime(constraint_value, "%Y-%m-%d").date()
            value_date = datetime.strptime(value, "%Y-%m-%d").date()

            if value_date > max_date:
                return [f"Date '{value}' at '{path}' is after maximum date {constraint_value}"]
        except ValueError:
            return [f"Invalid date format for max constraint at '{path}'"]
        return []

    def _validate_time_format(self, value, constraint_value, path):
        """Validate time format constraint."""
        # Format validation is handled in type_validators.py
        return []

    def _validate_datetime_format(self, value, constraint_value, path):
        """Validate datetime format constraint."""
        # Format validation is handled in type_validators.py
        return []

    def _validate_datetime_min(self, value, constraint_value, path):
        """Validate minimum datetime constraint."""
        try:
            from datetime import datetime

            # Handle RFC 3339 format
            if "T" in value and ("Z" in value or "+" in value or "-" in value):
                if value.endswith("Z"):
                    value = value[:-1] + "+00:00"
                value_dt = datetime.fromisoformat(value)

                if constraint_value.endswith("Z"):
                    constraint_value = constraint_value[:-1] + "+00:00"
                min_dt = datetime.fromisoformat(constraint_value)

                if value_dt < min_dt:
                    return [f"Datetime '{value}' at '{path}' is before minimum datetime {constraint_value}"]
            else:
                # For custom formats, use string comparison (less accurate but simpler)
                if value < constraint_value:
                    return [f"Datetime '{value}' at '{path}' is before minimum datetime {constraint_value}"]
        except ValueError:
            return [f"Invalid datetime format for min constraint at '{path}'"]
        return []

    def _validate_datetime_max(self, value, constraint_value, path):
        """Validate maximum datetime constraint."""
        try:
            from datetime import datetime

            # Handle RFC 3339 format
            if "T" in value and ("Z" in value or "+" in value or "-" in value):
                if value.endswith("Z"):
                    value = value[:-1] + "+00:00"
                value_dt = datetime.fromisoformat(value)

                if constraint_value.endswith("Z"):
                    constraint_value = constraint_value[:-1] + "+00:00"
                max_dt = datetime.fromisoformat(constraint_value)

                if value_dt > max_dt:
                    return [f"Datetime '{value}' at '{path}' is after maximum datetime {constraint_value}"]
            else:
                # For custom formats, use string comparison (less accurate but simpler)
                if value > constraint_value:
                    return [f"Datetime '{value}' at '{path}' is after maximum datetime {constraint_value}"]
        except ValueError:
            return [f"Invalid datetime format for max constraint at '{path}'"]
        return []

    def _validate_timestamp_precision(self, value, constraint_value, path):
        """Validate timestamp precision constraint."""
        # Precision validation is handled in type_validators.py
        return []

    def _validate_timestamp_min(self, value, constraint_value, path):
        """Validate minimum timestamp constraint."""
        if value < constraint_value:
            return [f"Timestamp {value} at '{path}' is before minimum timestamp {constraint_value}"]
        return []

    def _validate_timestamp_max(self, value, constraint_value, path):
        """Validate maximum timestamp constraint."""
        if value > constraint_value:
            return [f"Timestamp {value} at '{path}' is after maximum timestamp {constraint_value}"]
        return []

    def get_supported_constraints(self, type_name: str) -> Set[str]:
        """
        Get the set of supported constraints for a type.

        Args:
            type_name: The name of the type

        Returns:
            Set of constraint names supported by the type
        """
        if type_name not in self.constraint_validators:
            return set()

        return set(self.constraint_validators[type_name].keys())
