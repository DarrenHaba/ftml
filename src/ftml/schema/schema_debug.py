"""
FTML Schema Debugging Utilities

Provides utilities for logging and visualizing the Schema AST structure.
"""

from typing import List, Dict, Any, Optional
from ftml.logger import logger

from .schema_ast import SchemaTypeNode, ScalarTypeNode, UnionTypeNode, ListTypeNode, ObjectTypeNode


def visualize_schema_ast(node: SchemaTypeNode, indent: int = 0, field_name: Optional[str] = None) -> List[str]:
    """
    Recursively visualize a Schema AST node structure.

    Args:
        node: The schema AST node to visualize
        indent: Current indentation level
        field_name: Optional field name for this node (if it's a field in an object)

    Returns:
        A list of string lines representing the AST
    """
    indent_str = "  " * indent
    output = []

    # Handle different node types
    if isinstance(node, ScalarTypeNode):
        node_desc = f"{field_name + ': ' if field_name else ''}ScalarTypeNode({node.type_name})"
        output.append(f"{indent_str}{node_desc}")

        # Add constraints if any
        if node.constraints:
            output.append(f"{indent_str}  Constraints: {node.constraints}")

        # Add default value if any
        if node.has_default:
            output.append(f"{indent_str}  Default: {repr(node.default)}")

        # Add optional flag if set
        if node.optional:
            output.append(f"{indent_str}  Optional: True")

    elif isinstance(node, UnionTypeNode):
        node_desc = f"{field_name + ': ' if field_name else ''}UnionTypeNode"
        output.append(f"{indent_str}{node_desc}")

        # Add subtypes
        output.append(f"{indent_str}  Subtypes:")
        for i, subtype in enumerate(node.subtypes):
            output.append(f"{indent_str}    [{i}]:")
            output.extend([f"{indent_str}      {line}" for line in visualize_schema_ast(subtype)])

        # Add default value if any
        if node.has_default:
            output.append(f"{indent_str}  Default: {repr(node.default)}")

        # Add optional flag if set
        if node.optional:
            output.append(f"{indent_str}  Optional: True")

    elif isinstance(node, ListTypeNode):
        node_desc = f"{field_name + ': ' if field_name else ''}ListTypeNode"
        output.append(f"{indent_str}{node_desc}")

        # Add item type if specified
        if node.item_type:
            output.append(f"{indent_str}  ItemType:")
            output.extend([f"{indent_str}    {line}" for line in visualize_schema_ast(node.item_type)])
        else:
            output.append(f"{indent_str}  ItemType: any")

        # Add constraints if any
        if node.constraints:
            output.append(f"{indent_str}  Constraints: {node.constraints}")

        # Add default value if any
        if node.has_default:
            output.append(f"{indent_str}  Default: {repr(node.default)}")

        # Add optional flag if set
        if node.optional:
            output.append(f"{indent_str}  Optional: True")

    elif isinstance(node, ObjectTypeNode):
        node_desc = f"{field_name + ': ' if field_name else ''}ObjectTypeNode"
        output.append(f"{indent_str}{node_desc}")

        # Add pattern value type if specified
        if node.pattern_value_type:
            output.append(f"{indent_str}  PatternValueType:")
            output.extend([f"{indent_str}    {line}" for line in visualize_schema_ast(node.pattern_value_type)])

        # Add fields if any
        if node.fields:
            output.append(f"{indent_str}  Fields:")
            for field_name, field_type in node.fields.items():
                output.extend(visualize_schema_ast(field_type, indent + 2, field_name))

        # Add constraints if any
        if node.constraints:
            output.append(f"{indent_str}  Constraints: {node.constraints}")

        # Add default value if any
        if node.has_default:
            output.append(f"{indent_str}  Default: {repr(node.default)}")

        # Add optional flag if set
        if node.optional:
            output.append(f"{indent_str}  Optional: True")

    else:
        # Handle unknown node types
        output.append(f"{indent_str}Unknown node type: {type(node).__name__}")

    return output


def log_schema_ast(node: SchemaTypeNode, title: str = "Schema AST") -> None:
    """
    Log the schema AST structure with the specified title.

    Args:
        node: The schema AST node to log
        title: Title for the logged AST
    """
    logger.debug(f"\n--- {title} ---")
    for line in visualize_schema_ast(node):
        logger.debug(line)
    logger.debug("--- End Schema AST ---")


def log_schema_parse_process(input_schema: str, parsed_schema: Dict[str, Any], title: str = "Schema Parsing") -> None:
    """
    Log the schema parsing process with input and output.

    Args:
        input_schema: The input schema text
        parsed_schema: The parsed schema structure
        title: Title for the logged process
    """
    logger.debug(f"\n--- {title} ---")
    logger.debug(f"Input Schema:\n{input_schema}")
    logger.debug("\nParsed Schema:")
    for key, value in parsed_schema.items():
        logger.debug(f"{key}: {value}")
    logger.debug("--- End Schema Parsing ---")
