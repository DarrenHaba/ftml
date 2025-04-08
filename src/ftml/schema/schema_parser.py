"""
FTML Schema Parser Module

Parses FTML schema definitions into a structured representation.
"""

import re
from typing import Dict, Any, List, Optional

from ftml.logger import logger
from ftml.exceptions import FTMLParseError

from .schema_ast import SchemaTypeNode, ScalarTypeNode, UnionTypeNode, ListTypeNode, ObjectTypeNode
from .schema_union_parser import UnionParser
from .schema_constraint_parser import ConstraintParser
from .schema_type_system import TypeSystem
from .schema_debug import log_schema_ast


class SchemaParser:
    """
    Parser for FTML schema definitions.

    This class parses FTML schema strings into structured schema objects
    that can be used for validation. The parser has been redesigned to be
    more modular and maintainable.
    """

    def __init__(self):
        """Initialize the schema parser with necessary components."""
        self.type_system = TypeSystem()
        self.union_parser = UnionParser()
        self.constraint_parser = ConstraintParser()

        # Regex for extracting type with optional constraints and default value
        self.TYPE_PATTERN = re.compile(r"([^<>=]*?)(?:<(.+?)>)?(?:\s*=\s*(.+))?$")

    def parse(self, schema_str: str) -> Dict[str, SchemaTypeNode]:
        """
        Parse a schema string into a structured schema object.

        Args:
            schema_str: The schema string to parse

        Returns:
            A dictionary mapping field names to their schema type nodes
        """
        logger.debug("Starting schema parsing")

        # First, remove all comments from the schema
        schema_str = self._remove_comments(schema_str)

        schema = {}
        lines = schema_str.strip().split("\n")
        logger.debug(f"Schema contains {len(lines)} lines after removing comments")

        # Parse line by line, handling multiline structures
        field_name = None
        current_type = ""
        open_braces = 0
        open_brackets = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Update brace/bracket counts for this line
            open_braces += line.count("{") - line.count("}")
            open_brackets += line.count("[") - line.count("]")

            # If we're in the middle of parsing a multiline field
            if field_name is not None:
                current_type += " " + line

                # If we've closed all braces and brackets, we've finished this field
                if open_braces == 0 and open_brackets == 0:
                    logger.debug(f"Completed multiline field '{field_name}': {current_type}")

                    # Parse the field type
                    type_node = self._parse_type_definition(current_type)

                    # Check for optional marker in field name
                    optional = False
                    if field_name.endswith("?"):
                        field_name = field_name[:-1].strip()
                        optional = True
                        logger.debug(f"Field '{field_name}' marked as optional")

                    # Set optional flag
                    type_node.optional = optional

                    # Add to schema
                    schema[field_name] = type_node

                    # Reset for next field
                    field_name = None
                    current_type = ""

                continue

            # This is a new field - look for the colon that separates field from type
            if ":" in line:
                parts = line.split(":", 1)
                field_name_part = parts[0].strip()
                type_def = parts[1].strip()

                # Update open braces/brackets for this type definition
                type_open_braces = type_def.count("{") - type_def.count("}")
                type_open_brackets = type_def.count("[") - type_def.count("]")

                # If this field's type definition spans multiple lines
                if type_open_braces > 0 or type_open_brackets > 0:
                    logger.debug(f"Starting multiline field '{field_name_part}': {type_def}")
                    field_name = field_name_part
                    current_type = type_def
                    open_braces = type_open_braces
                    open_brackets = type_open_brackets
                else:
                    # Single line field - process it immediately
                    logger.debug(f"Processing single-line field '{field_name_part}': {type_def}")

                    # Parse the field type
                    type_node = self._parse_type_definition(type_def)

                    # Check for optional marker in field name
                    optional = False
                    if field_name_part.endswith("?"):
                        field_name_part = field_name_part[:-1].strip()
                        optional = True
                        logger.debug(f"Field '{field_name_part}' marked as optional")

                    # Set optional flag
                    type_node.optional = optional

                    # Add to schema
                    schema[field_name_part] = type_node

        # Handle any field that was still being processed at the end
        if field_name is not None:
            logger.debug(f"Finalizing multiline field '{field_name}': {current_type}")

            # Parse the field type
            type_node = self._parse_type_definition(current_type)

            # Check for optional marker
            optional = False
            if field_name.endswith("?"):
                field_name = field_name[:-1].strip()
                optional = True
                logger.debug(f"Field '{field_name}' marked as optional")

            # Set optional flag
            type_node.optional = optional

            # Add to schema
            schema[field_name] = type_node

        logger.debug(f"Finished schema parsing with {len(schema)} fields")
        return schema

    def _remove_comments(self, schema_str: str) -> str:
        """
        Remove all comments from schema string.

        Args:
            schema_str: The schema string with comments

        Returns:
            The schema string with all comments removed
        """
        # Split into lines
        lines = schema_str.split("\n")
        result_lines = []

        for line in lines:
            # Check for comment start
            comment_pos = line.find("//")

            # If comment found and not inside a string
            if comment_pos >= 0:
                # Check if the comment is inside a string
                inside_string = False
                string_char = None
                escaped = False

                for i, char in enumerate(line[:comment_pos]):
                    if char in ('"', "'") and not escaped:
                        if inside_string and char == string_char:
                            inside_string = False
                            string_char = None
                        elif not inside_string:
                            inside_string = True
                            string_char = char

                    escaped = char == "\\" and not escaped

                # If comment is not inside a string, remove it
                if not inside_string:
                    line = line[:comment_pos].rstrip()

            # Add non-empty lines
            if line.strip():
                result_lines.append(line)

        return "\n".join(result_lines)

    def _parse_type_definition(self, type_def: str) -> SchemaTypeNode:
        """
        Parse a type definition string into a schema type node.

        Args:
            type_def: The type definition string

        Returns:
            A SchemaTypeNode representing the type
        """
        logger.debug(f"Parsing type definition: {type_def}")

        # First check for default value at the top level (outside all braces/brackets)
        # default_value = None
        default_str = None
        type_str = type_def

        # Track brace/bracket levels to find equals sign outside all brackets
        brace_level = 0
        bracket_level = 0
        angle_level = 0

        # Scan through the string looking for = outside all brackets
        for i in range(len(type_def)):
            char = type_def[i]

            if char == "{":
                brace_level += 1
            elif char == "}":
                brace_level -= 1
            elif char == "[":
                bracket_level += 1
            elif char == "]":
                bracket_level -= 1
            elif char == "<":
                angle_level += 1
            elif char == ">":
                angle_level -= 1
            # Check for equals sign at the top level
            elif (
                char == "="
                and brace_level == 0
                and bracket_level == 0
                and angle_level == 0
                and i > 0
                and type_def[i - 1] == " "
                and i + 1 < len(type_def)
                and type_def[i + 1] == " "
            ):
                # Found top-level equals sign with spaces around it
                type_str = type_def[: i - 1].strip()
                default_str = type_def[i + 2:].strip()
                logger.debug(f"Found top-level default value: {default_str}, type definition is now: {type_str}")
                break

        # Check if this is a union type
        if self.union_parser.is_union_type(type_str):
            logger.debug(f"Detected union type: {type_str}")
            return self._parse_union_type(type_str, default_str)

        # Check for list type (starts with '[')
        elif type_str.startswith("["):
            logger.debug(f"Detected list type: {type_str}")
            return self._parse_list_type(type_str, default_str)

        # Check for object type (starts with '{')
        elif type_str.startswith("{"):
            logger.debug(f"Detected object type: {type_str}")
            return self._parse_object_type(type_str, default_str)

        # Otherwise, it's a scalar type
        else:
            logger.debug(f"Detected scalar type: {type_str}")
            return self._parse_scalar_type(type_str, default_str)

    def _parse_union_type(self, type_str: str, default_str: Optional[str] = None) -> UnionTypeNode:
        """
        Parse a union type string into a UnionTypeNode.

        Args:
            type_str: The union type string
            default_str: Optional default value string

        Returns:
            A UnionTypeNode representing the union type
        """
        # Create a union type node
        node = UnionTypeNode()

        # Split the union type into its component types
        union_parts = self.union_parser.split_union_parts(type_str)

        # Parse each component type
        for part in union_parts:
            subtype_node = self._parse_type_definition(part)
            node.subtypes.append(subtype_node)

        # Parse default value if present
        if default_str:
            node.has_default = True
            node.default = self._parse_default_value(default_str)

        # Log the parsed union type
        logger.debug(f"Parsed union type with {len(node.subtypes)} subtypes")
        log_schema_ast(node, "Union Type")

        return node

    def _parse_list_type(self, type_str: str, default_str: Optional[str] = None) -> ListTypeNode:
        """
        Parse a list type string into a ListTypeNode.

        Args:
            type_str: The list type string
            default_str: Optional default value string

        Returns:
            A ListTypeNode representing the list type
        """
        # Create a list type node
        node = ListTypeNode()

        # Extract constraints if present
        list_str = type_str
        constraints = {}

        # Check for constraints after closing bracket
        closing_bracket_pos = type_str.rindex("]")
        if closing_bracket_pos < len(type_str) - 1 and "<" in type_str[closing_bracket_pos:]:
            list_str = type_str[: closing_bracket_pos + 1]
            constraint_str = type_str[closing_bracket_pos + 1:]
            _, constraints = self.constraint_parser.extract_constraints(constraint_str)

        # Store constraints
        node.constraints = constraints

        # Parse item type if specified
        if list_str != "[]":
            # Extract item type from between brackets
            item_type_str = list_str[1:-1].strip()
            node.item_type = self._parse_type_definition(item_type_str)

        # Parse default value if present
        if default_str:
            node.has_default = True
            node.default = self._parse_default_value(default_str)

        # Log the parsed list type
        logger.debug(f"Parsed list type with constraints: {constraints}")
        log_schema_ast(node, "List Type")

        return node

    def _parse_object_type(self, type_str: str, default_str: Optional[str] = None) -> ObjectTypeNode:
        """
        Parse an object type string into an ObjectTypeNode.

        Args:
            type_str: The object type string
            default_str: Optional default value string

        Returns:
            An ObjectTypeNode representing the object type

        Raises:
            FTMLParseError: If the syntax is invalid or can't be parsed
        """
        logger.debug(f"Parsing object type: {type_str}")

        # Create an object type node
        node = ObjectTypeNode()

        # Extract constraints if present
        obj_str = type_str
        constraints = {}

        # Check if the type_str contains a complete object (has both { and })
        if "{" in type_str and "}" in type_str:
            # Check for constraints after closing brace
            closing_brace_pos = type_str.rindex("}")
            if closing_brace_pos < len(type_str) - 1 and "<" in type_str[closing_brace_pos:]:
                obj_str = type_str[: closing_brace_pos + 1]
                constraint_str = type_str[closing_brace_pos + 1:]
                _, constraints = self.constraint_parser.extract_constraints(constraint_str)
        else:
            # Handle incomplete object syntax (missing closing brace)
            raise FTMLParseError(f"Invalid object type syntax: {type_str} - missing closing brace")

        # Store constraints
        node.constraints = constraints

        # Check and set ext flag if present
        if "ext" in constraints:
            node.ext = bool(constraints["ext"])

        # Extract content between braces
        if obj_str.startswith("{") and obj_str.endswith("}"):
            content = obj_str[1:-1].strip()
            logger.debug(f"Content between braces: {content}")
        else:
            raise FTMLParseError(f"Invalid object type syntax: {obj_str} - expected {{...}}")

        # STEP 1: Check if empty
        if not content:
            logger.debug("Empty object type {}")

            # Apply default if present
            if default_str:
                node.has_default = True
                node.default = self._parse_default_value(default_str)
                logger.debug(f"Set default value: {node.default}")

            return node

        # # STEP 2: Check for pattern type by looking for a single key-value pattern
        # # For example: str: int or str: int | str | bool
        # if ':' in content and ',' not in content:
        #     parts = content.split(':', 1)
        #     if len(parts) == 2:
        #         pattern_key = parts[0].strip()
        #         pattern_value = parts[1].strip()
        #
        #         # Check if the pattern key is a scalar type
        #         if pattern_key in self.type_system.scalar_types:
        #             logger.debug(f"DETECTED PATTERN TYPE: {pattern_key} with value type: {pattern_value}")
        #
        #             # Parse the pattern value type
        #             value_type_node = self._parse_type_definition(pattern_value)
        #
        #             # Set as pattern value type
        #             node.pattern_value_type = value_type_node
        #
        #             # Apply default if present
        #             if default_str:
        #                 node.has_default = True
        #                 node.default = self._parse_default_value(default_str)
        #                 logger.debug(f"Set default value: {node.default}")
        #
        #             return node

        # STEP 3: Determine if this is a field declaration object or a pattern object
        # We do this by checking for colons that are not inside any brackets
        has_field_declarations = False
        brace_level = 0
        bracket_level = 0
        angle_level = 0

        for i, char in enumerate(content):
            if char == "{":
                brace_level += 1
            elif char == "}":
                brace_level -= 1
            elif char == "[":
                bracket_level += 1
            elif char == "]":
                bracket_level -= 1
            elif char == "<":
                angle_level += 1
            elif char == ">":
                angle_level -= 1
            elif char == ":" and brace_level == 0 and bracket_level == 0 and angle_level == 0:
                has_field_declarations = True
                break

        # STEP 4: Process as object with fields if field declarations are found
        if has_field_declarations:
            logger.debug(f"DETECTED REGULAR OBJECT with fields: {content}")

            try:
                # Split by commas that are outside any nested braces/brackets
                fields = self._split_object_fields(content)
                logger.debug(f"Split into {len(fields)} fields: {fields}")

                for field in fields:
                    if ":" in field:
                        key_str, value_str = field.split(":", 1)
                        key = key_str.strip()
                        value_type = value_str.strip()

                        logger.debug(f"Field: {key} = {value_type}")

                        # Check for optional marker
                        optional = False
                        if key.endswith("?"):
                            key = key[:-1].strip()
                            optional = True
                            logger.debug(f"Field {key} is optional")

                        # Parse the value type
                        try:
                            type_node = self._parse_type_definition(value_type)
                            type_node.optional = optional

                            # Add to object fields
                            node.fields[key] = type_node
                        except Exception as e:
                            # If field type parsing fails, provide a clear error
                            raise FTMLParseError(f"Failed to parse type for field '{key}': {str(e)}")
                    else:
                        # No colon in field definition
                        raise FTMLParseError(f"Invalid field format in object: {field}")
            except FTMLParseError:
                # Re-raise ParseErrors
                raise
            except Exception as e:
                # Convert other exceptions
                raise FTMLParseError(f"Error parsing object fields in {type_str}: {str(e)}")

            # Apply default if present
            if default_str:
                node.has_default = True
                node.default = self._parse_default_value(default_str)
                logger.debug(f"Set default value: {node.default}")

            return node

        # STEP 5: Check for union pattern by looking for pipes outside angle brackets
        is_union_pattern = False
        angle_level = 0
        union_positions = []

        for i, char in enumerate(content):
            if char == "<":
                angle_level += 1
            elif char == ">":
                angle_level -= 1
                if angle_level < 0:
                    # Unclosed angle bracket
                    raise FTMLParseError(f"Unbalanced angle brackets in object type: {type_str}")
            elif char == "|" and angle_level == 0:
                is_union_pattern = True
                union_positions.append(i)
                logger.debug(f"Found union pipe at position {i}")

        # Check for unbalanced angle brackets
        if angle_level != 0:
            raise FTMLParseError(f"Unbalanced angle brackets in object type: {type_str}")

        if is_union_pattern:
            # Create a union type node for the pattern value type
            union_node = UnionTypeNode()

            # Split the content by union positions
            parts = []
            start_pos = 0

            for pos in union_positions:
                part = content[start_pos:pos].strip()
                parts.append(part)
                start_pos = pos + 1

            # Add the last part
            parts.append(content[start_pos:].strip())

            # Parse each union part
            for part in parts:
                # Check if the part has constraints
                base_type, part_constraints = part, {}
                if "<" in part and ">" in part:
                    try:
                        base_type, part_constraints = self.constraint_parser.extract_constraints(part)
                    except Exception as e:
                        raise FTMLParseError(f"Error parsing constraints in union part '{part}': {str(e)}")

                # Create a type node for this part
                if base_type in self.type_system.scalar_types:
                    type_node = ScalarTypeNode(base_type)
                    type_node.constraints = part_constraints
                    union_node.subtypes.append(type_node)
                else:
                    raise FTMLParseError(f"Unknown type '{base_type}' in union pattern")

            # Set the union node as the pattern value type
            node.pattern_value_type = union_node

            # Apply default if present
            if default_str:
                node.has_default = True
                node.default = self._parse_default_value(default_str)
                logger.debug(f"Set default value: {node.default}")

            return node

        # STEP 6: Check if it's a pattern type {T} or {T<constraints>}
        # First check for colons - if present, it's not a pattern type
        if ":" not in content:
            # No colons, now check for commas outside angle brackets
            has_comma_outside_angle = False
            angle_level = 0

            for char in content:
                if char == "<":
                    angle_level += 1
                elif char == ">":
                    angle_level -= 1
                elif char == "," and angle_level == 0:
                    has_comma_outside_angle = True
                    break

            # If no commas outside angle brackets, attempt to process as pattern type
            if not has_comma_outside_angle:
                logger.debug(f"Checking for pattern type: {content}")

                # Try to extract base type and constraints (if any)
                base_type, type_constraints = content, {}
                if "<" in content and ">" in content:
                    try:
                        base_type, type_constraints = self.constraint_parser.extract_constraints(content)
                        logger.debug(f"Extracted base_type: {base_type}, constraints: {type_constraints}")
                    except Exception as e:
                        logger.debug(f"Error extracting constraints: {str(e)}")
                        # If constraint extraction fails, continue to next step
                        pass

                # Check if base_type is a valid scalar type
                if base_type in self.type_system.scalar_types:
                    logger.debug(f"DETECTED PATTERN TYPE: {base_type} with constraints: {type_constraints}")
                    # Create scalar type node for pattern
                    pattern_type = ScalarTypeNode(base_type)
                    pattern_type.constraints = type_constraints
                    # Set as pattern value type
                    node.pattern_value_type = pattern_type

                    # Apply default if present
                    if default_str:
                        node.has_default = True
                        node.default = self._parse_default_value(default_str)
                        logger.debug(f"Set default value: {node.default}")

                    return node

        # STEP 7: Last check - it must be a regular object with fields
        logger.debug(f"DETECTED REGULAR OBJECT with fields: {content}")

        try:
            # Split by commas that are outside any nested braces/brackets
            fields = self._split_object_fields(content)
            logger.debug(f"Split into {len(fields)} fields: {fields}")

            for field in fields:
                if ":" in field:
                    key_str, value_str = field.split(":", 1)
                    key = key_str.strip()
                    value_type = value_str.strip()

                    logger.debug(f"Field: {key} = {value_type}")

                    # Check for optional marker
                    optional = False
                    if key.endswith("?"):
                        key = key[:-1].strip()
                        optional = True
                        logger.debug(f"Field {key} is optional")

                    # Parse the value type
                    try:
                        type_node = self._parse_type_definition(value_type)
                        type_node.optional = optional

                        # Add to object fields
                        node.fields[key] = type_node
                    except Exception as e:
                        # If field type parsing fails, provide a clear error
                        raise FTMLParseError(f"Failed to parse type for field '{key}': {str(e)}")
                else:
                    # No colon in field definition
                    raise FTMLParseError(f"Invalid field format in object: {field}")
        except FTMLParseError:
            # Re-raise ParseErrors
            raise
        except Exception as e:
            # Convert other exceptions
            raise FTMLParseError(f"Error parsing object fields in {type_str}: {str(e)}")

        # Apply default if present
        if default_str:
            node.has_default = True
            node.default = self._parse_default_value(default_str)
            logger.debug(f"Set default value: {node.default}")

        return node

    def _split_object_fields(self, content: str) -> List[str]:
        """
        Split object fields by commas, respecting nested structures.
        This version handles multiple levels of nesting.

        Args:
            content: The object content to split

        Returns:
            A list of field strings
        """
        fields = []
        current = ""
        brace_level = 0  # {} level
        bracket_level = 0  # [] level
        angle_level = 0  # <> level

        for char in content:
            if char == "{":
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
            elif char == "<":
                angle_level += 1
                current += char
            elif char == ">":
                angle_level -= 1
                current += char
            elif char == "," and brace_level == 0 and bracket_level == 0 and angle_level == 0:
                # Only split on commas outside all bracket types
                fields.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            fields.append(current.strip())

        logger.debug(f"Split content into {len(fields)} fields")
        return fields

    def _parse_object_fields(self, content: str, node: ObjectTypeNode) -> None:
        """
        Parse the fields in an object type.

        Args:
            content: The object content string to parse
            node: The ObjectTypeNode to populate with fields
        """
        if not content.strip():
            return

        # Split fields on commas that are not inside brackets/braces
        fields = self._split_fields(content)

        for field in fields:
            if ":" in field:
                field_name, field_type = field.split(":", 1)
                field_name = field_name.strip()
                field_type = field_type.strip()

                # Check for optional marker
                optional = False
                if field_name.endswith("?"):
                    field_name = field_name[:-1].strip()
                    optional = True

                # Parse field type
                type_node = self._parse_type_definition(field_type)
                type_node.optional = optional

                # Add to object fields
                node.fields[field_name] = type_node

    def _parse_scalar_type(self, type_str: str, default_str: Optional[str] = None) -> ScalarTypeNode:
        """
        Parse a scalar type string into a ScalarTypeNode.

        Args:
            type_str: The scalar type string
            default_str: Optional default value string

        Returns:
            A ScalarTypeNode representing the scalar type
        """
        # Extract base type and constraints
        base_type, constraints = self.constraint_parser.extract_constraints(type_str)

        # Verify it's a valid scalar type
        if not self.type_system.is_scalar_type(base_type):
            raise FTMLParseError(f"Unknown scalar type: '{base_type}'")

        # Create a scalar type node
        node = ScalarTypeNode(base_type)
        node.constraints = constraints

        # Parse default value if present
        if default_str:
            node.has_default = True
            node.default = self._parse_default_value(default_str)

        # Log the parsed scalar type
        logger.debug(f"Parsed scalar type: {base_type} with constraints: {constraints}")
        log_schema_ast(node, "Scalar Type")

        return node

    def _parse_default_value(self, default_str: str) -> Any:
        """
        Parse a default value string.

        Args:
            default_str: The default value string

        Returns:
            The parsed default value
        """
        logger.debug(f"Parsing default value: {default_str}")

        # Handle scalar values first
        default_str = default_str.strip()

        # Handle booleans
        if default_str.lower() == "true":
            return True
        elif default_str.lower() == "false":
            return False

        # Handle null
        elif default_str.lower() == "null":
            return None

        # Handle quoted strings
        elif (default_str.startswith('"') and default_str.endswith('"')) or (
            default_str.startswith("'") and default_str.endswith("'")
        ):
            # Remove quotes and handle escapes
            inner = default_str[1:-1]
            # Process common escape sequences
            return inner.replace(r"\"", '"').replace(r"\\", "\\")

        # Handle numbers
        elif "." in default_str and default_str.replace(".", "", 1).isdigit():
            try:
                return float(default_str)
            except ValueError:
                pass  # Continue to next checks if not a valid float
        elif default_str.isdigit() or (default_str.startswith("-") and default_str[1:].isdigit()):
            try:
                return int(default_str)
            except ValueError:
                pass  # Continue to next checks if not a valid int

        # Handle objects
        if default_str.startswith("{") and default_str.endswith("}"):
            return self._parse_object_default(default_str)

        # Handle lists
        elif default_str.startswith("[") and default_str.endswith("]"):
            return self._parse_list_default(default_str)

        # If all else fails, return as string
        logger.debug(f"Treating default as string: {default_str}")
        return default_str

    def _parse_object_default(self, default_str: str) -> Dict[str, Any]:
        """
        Parse an object default value string.

        Args:
            default_str: The object default string (like "{key1 = value1, key2 = value2}")

        Returns:
            A dictionary representation of the object
        """
        logger.debug(f"Parsing object default: {default_str}")

        # Remove braces
        content = default_str[1:-1].strip()

        # Handle empty object
        if not content:
            logger.debug("Empty object default")
            return {}

        # Split by commas that are outside any nested braces/brackets
        field_strs = self._split_object_fields(content)
        logger.debug(f"Split default object into {len(field_strs)} fields")

        # Parse each field
        result = {}
        for field_str in field_strs:
            logger.debug(f"Processing default field: {field_str}")
            if "=" in field_str:
                key, value = field_str.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Recursively parse the value
                parsed_value = self._parse_default_value(value)
                result[key] = parsed_value
                logger.debug(f"  Added default field {key} = {parsed_value}")
            else:
                # If we encounter a field without =, it might be an error
                logger.warning(f"Skipping invalid default field format: {field_str}")

        return result

    def _parse_list_default(self, default_str: str) -> List[Any]:
        """
        Parse a list default value string.

        Args:
            default_str: The list default string (like "[value1, value2]")

        Returns:
            A list of parsed values
        """
        logger.debug(f"Parsing list default: {default_str}")

        # Remove brackets
        content = default_str[1:-1].strip()

        # Handle empty list
        if not content:
            logger.debug("Empty list default")
            return []

        # Split by commas that are outside any nested braces/brackets
        item_strs = self._split_object_fields(content)
        logger.debug(f"Split default list into {len(item_strs)} items")

        # Parse each item
        result = []
        for item_str in item_strs:
            # Recursively parse the value
            parsed_value = self._parse_default_value(item_str.strip())
            result.append(parsed_value)
            logger.debug(f"  Added default list item: {parsed_value}")

        return result

    def _split_fields(self, text: str) -> List[str]:
        """
        Split a string on commas, respecting brackets and braces.

        Args:
            text: The string to split

        Returns:
            A list of field strings
        """
        parts = []
        current = ""
        angle_level = 0  # <> brackets
        bracket_level = 0  # [] brackets
        brace_level = 0  # {} brackets

        for char in text:
            if char == "<":
                angle_level += 1
                current += char
            elif char == ">":
                angle_level -= 1
                current += char
            elif char == "[":
                bracket_level += 1
                current += char
            elif char == "]":
                bracket_level -= 1
                current += char
            elif char == "{":
                brace_level += 1
                current += char
            elif char == "}":
                brace_level -= 1
                current += char
            elif char == "," and angle_level == 0 and bracket_level == 0 and brace_level == 0:
                parts.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            parts.append(current.strip())

        logger.debug(f"Split text into {len(parts)} fields")
        return parts
