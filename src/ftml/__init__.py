"""
FTML (FlexTag Markup Language) - Public API

This module provides the main entry points for the FTML library:
- load(...) -> parse FTML data into a Python dict with comments preserved
- dump(...) -> serialize a Python dict to FTML text
- load_schema(...) -> parse a schema file
"""

import os
from typing import Optional, Union, Dict, Any, List, TextIO, BinaryIO

from .exceptions import FTMLParseError, FTMLValidationError, FTMLError, FTMLVersionError, FTMLEncodingError
from ftml.parser.parser import parse
from ftml.parser.serializer import serialize
from ftml.parser.ast import DocumentNode, KeyValueNode, ScalarNode, ObjectNode, ListNode, Node
from ftml.parser.encoding import validate_encoding, read_ftml_with_encoding
from ftml.version import validate_version, RESERVED_ENCODING_KEY, RESERVED_VERSION_KEY
from .ftml_dict import FTMLDict

from .schema.schema import Validator
from .schema import SchemaParser, apply_defaults
from .logger import logger

# FTML version constants
FTML_VERSION = "0.1a1"  # Update this to match package minor version
PACKAGE_VERSION = "0.1.0a1"  # Update this with each release


def get_ftml_version():
    """Return the FTML specification version this parser implements."""
    return FTML_VERSION


def get_package_version():
    """Return the package version."""
    return PACKAGE_VERSION


def load(
    ftml_data: Union[str, os.PathLike],
    schema: Optional[Union[str, Dict[str, Any]]] = None,
    strict: bool = True,
    preserve_comments: bool = True,
    validate: bool = True,
    check_version: bool = True,
) -> Dict[str, Any]:
    """
    Parse FTML data into a Python dictionary, with optional schema validation.

    Args:
        ftml_data: A string of FTML or a file path to FTML content.
        schema: Optional schema definition for validation.
        strict: Whether to enforce strict validation (no extra properties).
        preserve_comments: Whether to preserve comments for round-trip serialization.
        validate: Whether to validate against the schema.
        check_version: Whether to check FTML version compatibility.

    Returns:
        A dictionary containing the parsed data with comments preserved internally if requested.

    Raises:
        FTMLParseError: If there is a syntax error in the FTML.
        FTMLValidationError: If a schema is provided and validation fails.
        FTMLVersionError: If version check is enabled and the document version is incompatible.
        FTMLEncodingError: If there's an encoding-related error.
    """
    # If a file path is given, read its contents
    if isinstance(ftml_data, (str, os.PathLike)) and os.path.exists(str(ftml_data)):
        # Use our encoding-aware file reader
        ftml_data = read_ftml_with_encoding(ftml_data)

    # Always parse the document, even if empty
    try:
        # Empty document or whitespace-only
        if not ftml_data.strip():
            # Create an empty document AST and wrap in FTMLDict
            ast = DocumentNode()
            data = FTMLDict()
            data._ast_node = ast
        else:
            # Normal parsing path
            ast = parse(ftml_data)

            # Convert AST to dictionary - either preserving comments or not
            if preserve_comments:
                data = _ast_to_dict(ast)
                # Attach the AST for round-trip serialization
                if not isinstance(data, FTMLDict):
                    data = FTMLDict(data)
                data._ast_node = ast
            else:
                data = _ast_to_plain_dict(ast)

    except Exception as e:
        if not isinstance(e, FTMLParseError):
            raise FTMLParseError(f"Error parsing FTML: {str(e)}") from e
        raise

    # Check FTML version compatibility if requested
    if check_version:
        validate_version(data, FTML_VERSION)

    # Validate encoding if specified
    if RESERVED_ENCODING_KEY in data:
        validate_encoding(data)

    # If a schema is provided and validation is requested
    if schema is not None and validate:
        try:
            # Parse the schema if it's a string
            if isinstance(schema, str):
                # Check if it's a file path
                if os.path.exists(schema):
                    with open(schema, "r", encoding="utf-8") as f:
                        schema_str = f.read()
                    schema_parser = SchemaParser()
                    parsed_schema = schema_parser.parse(schema_str)
                else:
                    # Treat as a schema string
                    schema_parser = SchemaParser()
                    parsed_schema = schema_parser.parse(schema)
            else:
                parsed_schema = schema

            # Apply defaults - do this before validation to handle default values
            data = apply_defaults(data, parsed_schema)

            # Validate the data against the schema
            validator = Validator(parsed_schema, strict=strict)
            errors = validator.validate(data)

            if errors:
                error_msg = "\n".join(errors)
                raise FTMLValidationError(f"Schema validation failed:\n{error_msg}", errors=errors)

        except Exception as e:
            if not isinstance(e, FTMLValidationError):
                raise FTMLValidationError(f"Schema validation error: {str(e)}") from e
            raise

    return data


def dump(
    data: Dict[str, Any],
    fp: Optional[Union[str, os.PathLike, TextIO, BinaryIO]] = None,
    schema: Optional[Union[str, Dict[str, Any]]] = None,
    strict: bool = True,
    include_comments: bool = True,
    validate: bool = True,
) -> Optional[str]:
    """
    Serialize a Python dictionary to FTML text, with optional validation.

    Args:
        data: A Python dictionary to serialize.
        fp: A file path or file-like object to write to. If None, returns a string.
        schema: Optional schema definition for validation before serializing.
        strict: Whether to enforce strict validation (no extra properties).
        include_comments: Whether to include preserved comments in the output.
        validate: Whether to validate against the schema before serializing.

    Returns:
        The FTML text if fp is None, otherwise None.

    Raises:
        FTMLError: If the data cannot be serialized.
        FTMLValidationError: If schema validation fails.
    """
    # Check FTML version in the data if provided
    if RESERVED_VERSION_KEY in data and isinstance(data[RESERVED_VERSION_KEY], str):
        try:
            validate_version(data, FTML_VERSION)
        except FTMLVersionError as e:
            logger.warning(f"Version warning: {str(e)}")

    # Check encoding in the data if provided
    if RESERVED_ENCODING_KEY in data:
        validate_encoding(data)

    # First validate against schema if provided and validation is requested
    if schema is not None and validate:
        try:
            # Parse the schema if it's a string
            if isinstance(schema, str):
                # Check if it's a file path
                if os.path.exists(schema):
                    with open(schema, "r", encoding="utf-8") as f:
                        schema_str = f.read()
                    schema_parser = SchemaParser()
                    parsed_schema = schema_parser.parse(schema_str)
                else:
                    # Treat as a schema string
                    schema_parser = SchemaParser()
                    parsed_schema = schema_parser.parse(schema)
            else:
                parsed_schema = schema

            # Validate the data against the schema
            validator = Validator(parsed_schema, strict=strict)
            errors = validator.validate(data)

            if errors:
                error_msg = "\n".join(errors)
                raise FTMLValidationError(f"Schema validation failed:\n{error_msg}", errors=errors)

        except Exception as e:
            if not isinstance(e, FTMLValidationError):
                raise FTMLValidationError(f"Schema validation error: {str(e)}") from e
            raise

    try:
        # Convert dictionary to AST, preserving comments if include_comments is True
        if not include_comments and hasattr(data, "_ast_node"):
            # Create a new data dictionary without the _ast_node
            new_data = dict(data)
            ast = _dict_to_ast(new_data)
            _remove_comments_from_ast(ast)
        else:
            # Use our improved _dict_to_ast function that preserves comments
            ast = _dict_to_ast(data)

        # Serialize AST to FTML text
        serialized = serialize(ast)

        # Determine output encoding
        try:
            encoding = validate_encoding(data)
        except FTMLEncodingError as e:
            logger.warning(f"Encoding validation error: {e}. Falling back to UTF-8.")
            encoding = "utf-8"
        finally:
            # Ensure encoding is always set, even if an unexpected error occurs
            encoding = "utf-8"

        # Handle output destination
        if fp is None:
            # Return as string
            return serialized
        elif isinstance(fp, (str, os.PathLike)):
            # File path provided - write to file
            with open(fp, "w", encoding=encoding) as f:
                f.write(serialized)
            return None
        else:
            # File-like object provided - write to it
            try:
                # Try text mode first
                fp.write(serialized)
            except TypeError:
                # If that fails, try binary mode
                fp.write(serialized.encode(encoding))
            return None
    except Exception as e:
        raise FTMLError(f"Error serializing data to FTML: {str(e)}") from e


def load_schema(schema_data: Union[str, os.PathLike]) -> Dict[str, Any]:
    """
    Parse an FTML schema into a schema object.

    Args:
        schema_data: A string of schema definition or a file path to a schema file.

    Returns:
        The parsed schema as a dictionary.

    Raises:
        FTMLParseError: If there is a syntax error in the schema.
    """
    # If a file path is given, read its contents
    if isinstance(schema_data, (str, os.PathLike)) and os.path.exists(str(schema_data)):
        with open(schema_data, "r", encoding="utf-8") as f:
            schema_data = f.read()

    try:
        schema_parser = SchemaParser()
        return schema_parser.parse(schema_data)
    except Exception as e:
        # Re-raise errors for consistency
        raise FTMLParseError(f"Error parsing schema: {str(e)}") from e


def validate(data: Dict[str, Any], schema: Union[str, os.PathLike, Dict[str, Any]], strict: bool = True) -> List[str]:
    """
    Validate a Python dictionary against an FTML schema.

    Args:
        data: A Python dictionary to validate.
        schema: An FTML schema string, file path, or parsed schema dictionary.
        strict: Whether to enforce strict validation (no extra properties).

    Returns:
        A list of validation error messages (empty if valid).

    Raises:
        FTMLError: If there's an error during validation.
    """
    try:
        # Parse the schema if it's a string or file path
        if isinstance(schema, (str, os.PathLike)):
            # Check if it's a file path
            if os.path.exists(str(schema)):
                with open(schema, "r", encoding="utf-8") as f:
                    schema_str = f.read()
                schema_parser = SchemaParser()
                parsed_schema = schema_parser.parse(schema_str)
            else:
                # Treat as a schema string
                schema_parser = SchemaParser()
                parsed_schema = schema_parser.parse(schema)
        else:
            parsed_schema = schema

        # Validate the data against the schema
        validator = Validator(parsed_schema, strict=strict)
        errors = validator.validate(data)

        return errors

    except Exception as e:
        if isinstance(e, FTMLValidationError):
            return e.errors if hasattr(e, "errors") else [str(e)]
        else:
            raise FTMLError(f"Validation error: {str(e)}") from e


# Helper functions for AST conversion
def _ast_to_dict(ast: DocumentNode) -> Dict[str, Any]:
    """
    Convert an AST to a Python dictionary.

    Args:
        ast: The root DocumentNode to convert.

    Returns:
        A dictionary containing the data from the AST.
    """
    result = FTMLDict()
    result._ast_node = ast

    for key, kv_node in ast.items.items():
        value = _node_to_value(kv_node.value)
        result[key] = value

    return result


def _ast_to_plain_dict(ast: DocumentNode) -> Dict[str, Any]:
    """
    Convert an AST to a plain Python dictionary without comments.

    Args:
        ast: The root DocumentNode to convert.

    Returns:
        A plain dictionary without comment information.
    """
    result = {}

    for key, kv_node in ast.items.items():
        value = _node_to_plain_value(kv_node.value)
        result[key] = value

    return result


def _node_to_value(node: Node) -> Any:
    """
    Convert a node to a Python value.

    Args:
        node: The node to convert.

    Returns:
        The Python value represented by the node.
    """
    if isinstance(node, ScalarNode):
        return node.value

    elif isinstance(node, ObjectNode):
        obj = FTMLDict()
        obj._ast_node = node
        for key, kv_node in node.items.items():
            obj[key] = _node_to_value(kv_node.value)
        return obj

    elif isinstance(node, ListNode):
        lst = [_node_to_value(elem) for elem in node.elements]
        # We can't attach AST to lists directly in Python
        # If we need to preserve comments in lists, we'd need a custom list class
        return lst

    # Fallback
    return None


def _node_to_plain_value(node: Node) -> Any:
    """
    Convert a node to a plain Python value without comments.

    Args:
        node: The node to convert.

    Returns:
        The plain Python value without comment information.
    """
    if isinstance(node, ScalarNode):
        return node.value

    elif isinstance(node, ObjectNode):
        obj = {}
        for key, kv_node in node.items.items():
            obj[key] = _node_to_plain_value(kv_node.value)
        return obj

    elif isinstance(node, ListNode):
        return [_node_to_plain_value(elem) for elem in node.elements]

    # Fallback
    return None


def _dict_to_ast(data: Dict[str, Any]) -> DocumentNode:
    """
    Convert a Python dictionary to an AST.
    Preserves comments if data has _ast_node attached.

    Args:
        data: The dictionary to convert.

    Returns:
        The root DocumentNode of the AST.
    """
    # Start with an empty document node
    doc = DocumentNode()

    # If data has an attached AST node, preserve its comments and structure
    original_ast = None
    if hasattr(data, "_ast_node") and isinstance(data._ast_node, DocumentNode):
        original_ast = data._ast_node
        # Copy document-level comments
        doc.leading_comments = original_ast.leading_comments
        doc.inline_comment = original_ast.inline_comment
        if hasattr(original_ast, "inner_doc_comments"):
            doc.inner_doc_comments = original_ast.inner_doc_comments

    # Process each key in the current data dictionary
    for key, value in data.items():
        # Skip internal comment keys
        if key.startswith("__comments__"):
            continue

        # Create a value node with the current value
        value_node = _value_to_node(
            value, original_ast.items.get(key).value if original_ast and key in original_ast.items else None
        )

        # Create a key-value node (using dummy line/col values)
        kv_node = KeyValueNode(key, value_node, -1, -1)

        # If we have the original AST, copy comments for this key
        if original_ast and key in original_ast.items:
            original_kv = original_ast.items[key]
            kv_node.leading_comments = original_kv.leading_comments
            kv_node.inline_comment = original_kv.inline_comment
            if hasattr(original_kv, "outer_doc_comments"):
                kv_node.outer_doc_comments = original_kv.outer_doc_comments

        # Add the key-value node to the document
        doc.items[key] = kv_node

    return doc


def _value_to_node(value: Any, original_node: Optional[Node] = None) -> Node:
    """
    Convert a Python value to a node, preserving comments from original if available.

    Args:
        value: The value to convert.
        original_node: The original node to copy comments from, if available.

    Returns:
        The node representing the value.
    """
    if isinstance(value, (str, int, float, bool)) or value is None:
        # Create a scalar node
        node = ScalarNode(value, -1, -1)  # Dummy line/col values

        # Copy comments from original node if available
        if original_node and isinstance(original_node, ScalarNode):
            node.leading_comments = original_node.leading_comments
            node.inline_comment = original_node.inline_comment
            if hasattr(original_node, "outer_doc_comments"):
                node.outer_doc_comments = original_node.outer_doc_comments

        return node

    elif isinstance(value, dict):
        # Create a new object node
        node = ObjectNode(-1, -1)  # Dummy line/col values

        # Copy comments from original node if available
        if original_node and isinstance(original_node, ObjectNode):
            node.leading_comments = original_node.leading_comments
            node.inline_comment = original_node.inline_comment
            if hasattr(original_node, "outer_doc_comments"):
                node.outer_doc_comments = original_node.outer_doc_comments
            if hasattr(original_node, "inner_doc_comments"):
                node.inner_doc_comments = original_node.inner_doc_comments

        # Process each key in the dictionary
        for key, val in value.items():
            # Find the original value node for this key if available
            original_val_node = None
            if original_node and isinstance(original_node, ObjectNode) and key in original_node.items:
                original_val_node = original_node.items[key].value

            # Create the value node, preserving comments
            value_node = _value_to_node(val, original_val_node)

            # Create a key-value node
            kv_node = KeyValueNode(key, value_node, -1, -1)  # Dummy line/col values

            # Copy comments from the original key-value node if available
            if original_node and isinstance(original_node, ObjectNode) and key in original_node.items:
                original_kv = original_node.items[key]
                kv_node.leading_comments = original_kv.leading_comments
                kv_node.inline_comment = original_kv.inline_comment
                if hasattr(original_kv, "outer_doc_comments"):
                    kv_node.outer_doc_comments = original_kv.outer_doc_comments

            node.items[key] = kv_node

        return node

    elif isinstance(value, list):
        # Create a new list node
        node = ListNode(-1, -1)  # Dummy line/col values

        # Copy comments from original node if available
        if original_node and isinstance(original_node, ListNode):
            node.leading_comments = original_node.leading_comments
            node.inline_comment = original_node.inline_comment
            node.inline_comment_end = (
                original_node.inline_comment_end if hasattr(original_node, "inline_comment_end") else None
            )
            if hasattr(original_node, "outer_doc_comments"):
                node.outer_doc_comments = original_node.outer_doc_comments
            if hasattr(original_node, "inner_doc_comments"):
                node.inner_doc_comments = original_node.inner_doc_comments

        # Process each item in the list
        for i, item in enumerate(value):
            # Find the original element for this index if available
            original_elem = None
            if original_node and isinstance(original_node, ListNode) and i < len(original_node.elements):
                original_elem = original_node.elements[i]

            # Create the element node, preserving comments
            element_node = _value_to_node(item, original_elem)

            node.elements.append(element_node)

        return node

    # Fallback
    return ScalarNode(None, -1, -1)  # Dummy line/col values


def _remove_comments_from_ast(node: Node) -> None:
    """
    Recursively remove all comments from an AST node and its children.

    Args:
        node: The node to remove comments from.
    """
    if node is None:
        return

    # Clear comments on this node
    if hasattr(node, "leading_comments"):
        node.leading_comments = []
    if hasattr(node, "inline_comment"):
        node.inline_comment = None
    if hasattr(node, "trailing_comments"):
        node.trailing_comments = []

    # Recursively clear comments on children
    if isinstance(node, DocumentNode):
        for key, kv_node in node.items.items():
            _remove_comments_from_ast(kv_node)
            _remove_comments_from_ast(kv_node.value)

    elif isinstance(node, ObjectNode):
        for key, kv_node in node.items.items():
            _remove_comments_from_ast(kv_node)
            _remove_comments_from_ast(kv_node.value)

    elif isinstance(node, ListNode):
        for elem in node.elements:
            _remove_comments_from_ast(elem)


# Make these available in the public API
__all__ = [
    "load",
    "dump",
    "validate",
    "apply_defaults",
    "load_schema",
    "FTMLDict",
    "FTMLError",
    "FTMLParseError",
    "FTMLValidationError",
    "FTMLVersionError",
    "FTMLEncodingError",
    "logger",
    "get_ftml_version",
    "get_package_version",
]
