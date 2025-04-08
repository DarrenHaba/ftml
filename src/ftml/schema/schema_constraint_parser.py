"""
FTML Constraint Parser Module

Handles parsing of type constraints in angle brackets (<min=0, max=10>).
"""

import json
from typing import Dict, Any, Tuple

from ftml.logger import logger
from ftml.exceptions import FTMLParseError


class ConstraintParser:
    """
    Parser for FTML type constraints.

    This class handles extracting and parsing constraints specified in
    angle brackets (<...>) in FTML schema type definitions.
    """

    def extract_constraints(self, type_str: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract constraints from a type string.

        Args:
            type_str: The type string potentially containing constraints

        Returns:
            A tuple of (base_type, constraints_dict)
        """
        logger.debug(f"Extracting constraints from: {type_str}")

        # Check if constraints are present (type<...>)
        if "<" not in type_str or ">" not in type_str:
            logger.debug(f"No constraints found in: {type_str}")
            return type_str, {}

        # Find constraint boundaries
        constraint_start = type_str.find("<")
        constraint_end = type_str.rfind(">")

        if constraint_start > constraint_end:
            raise FTMLParseError(f"Malformed constraints in type: {type_str}")

        # Extract base type and constraint string
        base_type = type_str[:constraint_start].strip()
        constraint_str = type_str[constraint_start + 1: constraint_end].strip()

        logger.debug(f"Base type: {base_type}, constraint string: {constraint_str}")

        # Parse constraints
        constraints = self.parse_constraint_string(constraint_str, base_type)

        return base_type, constraints

    def parse_constraint_string(self, constraint_str: str, base_type: str) -> Dict[str, Any]:
        """
        Parse constraints from a constraint string.

        Args:
            constraint_str: The constraint string to parse
            base_type: The base type these constraints apply to, for validation

        Returns:
            A dictionary of constraints
        """
        if not constraint_str:
            return {}

        logger.debug(f"Parsing constraints: {constraint_str} for type: {base_type}")

        constraints = {}

        # Initialize state variables for parsing
        i = 0
        length = len(constraint_str)

        while i < length:
            # Skip whitespace
            while i < length and constraint_str[i].isspace():
                i += 1

            if i >= length:
                break

            # Find the constraint name (everything up to '=')
            name_start = i
            while i < length and constraint_str[i] != "=":
                i += 1

            if i >= length:
                # Instead of just logging and skipping, raise an exception
                error_msg = f"Invalid constraint format in '{constraint_str}': missing equals sign"
                logger.error(error_msg)
                raise FTMLParseError(error_msg)

            # Extract the constraint name
            name = constraint_str[name_start:i].strip()
            i += 1  # Skip the '='

            # Skip whitespace after '='
            while i < length and constraint_str[i].isspace():
                i += 1

            if i >= length:
                logger.debug(f"Skipping invalid constraint (missing value): {name}")
                break

            # Extract the constraint value
            value_start = i

            # Handle different value types
            if constraint_str[i] == "[":  # Array/list
                # Count brackets to handle nested arrays
                bracket_level = 1
                i += 1

                while i < length and bracket_level > 0:
                    if constraint_str[i] == "[":
                        bracket_level += 1
                    elif constraint_str[i] == "]":
                        bracket_level -= 1
                    elif constraint_str[i] == '"' or constraint_str[i] == "'":
                        # Skip quoted strings
                        quote_char = constraint_str[i]
                        i += 1
                        while i < length and constraint_str[i] != quote_char:
                            if constraint_str[i] == "\\" and i + 1 < length:
                                i += 2  # Skip escaped character
                            else:
                                i += 1
                    i += 1

                # Extract the entire array as a string
                value_str = constraint_str[value_start:i]

                try:
                    # Try to parse as JSON
                    value = json.loads(value_str.replace("'", '"'))
                    logger.debug(f"Parsed array constraint: {name}={value}")
                except json.JSONDecodeError:
                    # Fallback: just use the string
                    value = value_str
                    logger.debug(f"Failed to parse array, using string: {name}={value}")

            elif constraint_str[i] == '"' or constraint_str[i] == "'":  # Quoted string
                quote_char = constraint_str[i]
                i += 1

                # Find the end of the quoted string
                while i < length and constraint_str[i] != quote_char:
                    if constraint_str[i] == "\\" and i + 1 < length:
                        i += 2  # Skip escaped character
                    else:
                        i += 1

                i += 1  # Skip the closing quote

                # Extract the quoted string
                value_str = constraint_str[value_start:i]
                value = self._parse_value(value_str)

            else:  # Simple value (number, boolean, null, etc.)
                # Find the end of the value (comma or end of string)
                while i < length and constraint_str[i] != ",":
                    i += 1

                # Extract the value
                value_str = constraint_str[value_start:i]
                value = self._parse_value(value_str)

            # Add the constraint to the dictionary
            constraints[name] = value
            logger.debug(f"Added constraint: {name}={value}")

            # Skip the comma if present
            if i < length and constraint_str[i] == ",":
                i += 1

        # Validate enum constraints if base_type is provided
        if "enum" in constraints and base_type:
            self._validate_enum_constraint(constraints["enum"], base_type)

        return constraints

    def _parse_value(self, value_str: str) -> Any:
        """
        Parse a constraint value string to its appropriate type.

        Args:
            value_str: The value string to parse

        Returns:
            The parsed value
        """
        value_str = value_str.strip()

        # Try to parse as a literal
        if value_str.lower() == "true":
            return True
        elif value_str.lower() == "false":
            return False
        elif value_str.lower() == "null":
            return None

        # Try to parse as a number
        try:
            if "." in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass

        # If it starts and ends with quotes, it's a string
        if (value_str.startswith('"') and value_str.endswith('"')) or (
            value_str.startswith("'") and value_str.endswith("'")
        ):
            return value_str[1:-1]

        # If it starts with [ and ends with ], try to parse as a list
        if value_str.startswith("[") and value_str.endswith("]"):
            try:
                return json.loads(value_str.replace("'", '"'))
            except json.JSONDecodeError:
                pass

        # Return as-is if we couldn't parse it
        return value_str

    def _validate_enum_constraint(self, enum_values: Any, base_type: str) -> None:
        """
        Validate that an enum constraint is appropriate for the base type.

        Args:
            enum_values: The enum values to validate
            base_type: The base type to validate against

        Raises:
            FTMLParseError: If the enum values are not valid for the base type
        """
        if not isinstance(enum_values, list):
            raise FTMLParseError(f"Enum constraint must be a list, got: {type(enum_values).__name__}")

        invalid_values = []

        for val in enum_values:
            if base_type == "int":
                if not isinstance(val, int):
                    invalid_values.append(val)
            elif base_type == "float":
                if not (isinstance(val, int) or isinstance(val, float)):
                    invalid_values.append(val)
            elif base_type == "str":
                if not isinstance(val, str):
                    invalid_values.append(val)
            elif base_type == "bool":
                if not isinstance(val, bool):
                    invalid_values.append(val)

        if invalid_values:
            error_msg = f"Invalid enum values for {base_type} type: {invalid_values}"
            logger.error(error_msg)
            raise FTMLParseError(error_msg)
