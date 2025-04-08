"""
FTML Union Type Parser Module

Handles parsing of union type expressions (type1 | type2 | ...).
"""

from typing import List

from ftml.logger import logger


class UnionParser:
    """
    Parser for union type expressions.

    This class specifically handles splitting and parsing union types,
    which are expressed with the pipe symbol (|) in FTML schemas.
    """

    def split_union_parts(self, type_str: str) -> List[str]:
        """
        Split a type string into union parts, respecting all bracket types.

        Args:
            type_str: The type string to split

        Returns:
            A list of union part strings
        """
        logger.debug(f"Splitting union type: {type_str}")

        parts = []
        current = ""
        angle_level = 0  # <> brackets for constraints
        brace_level = 0  # {} brackets for objects
        bracket_level = 0  # [] brackets for lists

        for char in type_str:
            if char == "<":
                angle_level += 1
                current += char
            elif char == ">":
                angle_level -= 1
                current += char
            elif char == "{":
                brace_level += 1
                current += char
            elif char == "}":
                brace_level -= 1
                current += char
            elif char == "[":
                bracket_level += 1
                current += char
            elif char == "]":
                bracket_level -= 1
                current += char
            elif char == "|" and angle_level == 0 and brace_level == 0 and bracket_level == 0:
                # Only split on | when not inside any bracket type
                parts.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            parts.append(current.strip())

        logger.debug(f"Split union type into {len(parts)} parts: {parts}")
        return parts

    def is_union_type(self, type_str: str) -> bool:
        """
        Determine if a type string contains a top-level union.

        Args:
            type_str: The type string to check

        Returns:
            True if the string contains a top-level union (| outside any brackets)
        """
        angle_level = 0  # <> brackets
        brace_level = 0  # {} brackets
        bracket_level = 0  # [] brackets

        for char in type_str:
            if char == "<":
                angle_level += 1
            elif char == ">":
                angle_level -= 1
            elif char == "{":
                brace_level += 1
            elif char == "}":
                brace_level -= 1
            elif char == "[":
                bracket_level += 1
            elif char == "]":
                bracket_level -= 1
            elif char == "|" and angle_level == 0 and brace_level == 0 and bracket_level == 0:
                # Found a pipe outside all brackets - this is a top-level union
                return True

        return False
