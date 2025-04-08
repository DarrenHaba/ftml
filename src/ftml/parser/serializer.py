"""
FTML Serializer Module

Converts an AST back into FTML text, preserving all comments
for perfect round-trip parsing.
"""

from ftml.logger import logger

from .ast import Node, DocumentNode, ScalarNode, ObjectNode, ListNode


class Serializer:
    """
    Serializes an AST back to FTML text with comments preserved.
    """

    def __init__(self, root: DocumentNode):
        """
        Initialize the serializer with the root node.

        Args:
            root: The root DocumentNode to serialize.
        """
        self.root = root

    def serialize(self) -> str:
        """
        Convert the AST to FTML text.

        Returns:
            The FTML text representation of the AST.
        """
        lines = []

        # Add document inner doc comments (//!)
        if hasattr(self.root, "inner_doc_comments") and self.root.inner_doc_comments:
            logger.debug(f"Adding {len(self.root.inner_doc_comments)} inner doc comments")
            for comment in self.root.inner_doc_comments:
                lines.append(f"//! {comment.text}")

            # Add a blank line after inner doc comments
            if self.root.inner_doc_comments:
                lines.append("")

        # Add document leading comments
        logger.debug(f"Serializing document with {len(self.root.leading_comments)} leading comments")
        for comment in self.root.leading_comments:
            lines.append(f"// {comment.text}")

        # Add a blank line after leading comments if there are any
        if self.root.leading_comments:
            lines.append("")

        # Serialize each key-value pair
        for key, kv_node in self.root.items.items():
            logger.debug(f"Serializing key-value pair: {key}")

            # First add leading comments for this key-value pair
            for comment in kv_node.leading_comments:
                logger.debug(f"Adding leading comment for {key}: {comment.text}")
                lines.append(f"// {comment.text}")

            # Then add outer doc comments for this key-value pair (right before the node)
            if hasattr(kv_node, "outer_doc_comments") and kv_node.outer_doc_comments:
                for comment in kv_node.outer_doc_comments:
                    logger.debug(f"Adding outer doc comment for {key}: {comment.text}")
                    lines.append(f"/// {comment.text}")

            # Serialize the value
            value_str = self._serialize_value(kv_node.value)

            # Create the key-value line
            kv_line = f"{key} = {value_str}"

            # Add inline comment if present
            if kv_node.inline_comment:
                logger.debug(f"Adding inline comment for {key}: {kv_node.inline_comment.text}")
                kv_line += f"  // {kv_node.inline_comment.text}"

            lines.append(kv_line)

            # Add a blank line after each key-value pair
            lines.append("")

        # Remove the last blank line if there is one
        if lines and lines[-1] == "":
            lines.pop()

        # Add document-level orphaned comments at the end
        if hasattr(self.root, "end_leading_comments") and self.root.end_leading_comments:
            # Add a blank line before orphaned comments if needed
            if lines and lines[-1] != "":
                lines.append("")

            for comment in self.root.end_leading_comments:
                logger.debug(f"Adding orphaned document comment: {comment.text}")
                lines.append(f"// {comment.text}")

        # Join all lines with newlines
        result = "\n".join(lines)
        logger.debug(f"Serialized {len(self.root.items)} root items into {len(lines)} lines")
        return result

    def _serialize_value(self, node: Node) -> str:
        """
        Serialize a value node to FTML text.

        Args:
            node: The node to serialize.

        Returns:
            The FTML text representation of the value.
        """
        if isinstance(node, ScalarNode):
            # Handle scalar values
            value = node.value

            # if isinstance(value, str):
            #     # Use double quotes for strings
            #     # Escape special characters if needed
            #     escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            #     return f'"{escaped}"'
            if isinstance(value, str):
                # Use double quotes for strings
                # Escape special characters if needed
                escaped = (value.replace("\\", "\\\\")  # Must come first to avoid double-escaping
                           .replace('"', '\\"')
                           .replace("\n", "\\n")
                           .replace("\r", "\\r")
                           .replace("\t", "\\t")
                           .replace("\b", "\\b")
                           .replace("\f", "\\f")
                           .replace("\a", "\\a")
                           .replace("\v", "\\v"))
                return f'"{escaped}"'

            elif isinstance(value, bool):
                return str(value).lower()

            elif value is None:
                return "null"

            else:
                # For numbers, just convert to string
                return str(value)

        elif isinstance(node, ObjectNode):
            # Handle object serialization
            return self._serialize_object(node)

        elif isinstance(node, ListNode):
            # Handle list serialization
            return self._serialize_list(node)

        # Fallback
        logger.warning(f"Unhandled node type for serialization: {type(node).__name__}")
        return str(node)

    def _serialize_object(self, node: ObjectNode, indentation_count: int = 4) -> str:
        """
        Serialize an object node to FTML text.

        Args:
            node: The object node to serialize.
            indentation_count: The number of spaces to use for indentation (default is 4).

        Returns:
            The FTML text representation of the object.
        """
        # Create the indentation string based on the count
        indentation = " " * indentation_count

        if not node.items:
            return "{}"

        lines = ["{"]

        # Add inner doc comments at the beginning of the object
        if hasattr(node, "inner_doc_comments") and node.inner_doc_comments:
            for comment in node.inner_doc_comments:
                lines.append(f"{indentation}//! {comment.text}")

        # Add leading comments for the object
        for comment in node.leading_comments:
            lines.append(f"{indentation}// {comment.text}")

        # Add inline comment for the opening brace if present
        if node.inline_comment:
            lines[0] += f"  // {node.inline_comment.text}"

        # Serialize each key-value pair
        items = list(node.items.values())
        for i, kv_node in enumerate(items):
            # Add outer doc comments for this key-value pair
            if hasattr(kv_node, "outer_doc_comments") and kv_node.outer_doc_comments:
                for comment in kv_node.outer_doc_comments:
                    lines.append(f"{indentation}/// {comment.text}")

            # Add leading comments for this key-value pair
            for comment in kv_node.leading_comments:
                lines.append(f"{indentation}// {comment.text}")

            # Serialize the key-value pair
            key = kv_node.key
            value_str = self._serialize_value(kv_node.value)

            # Handle multiline values
            if "\n" in value_str:
                # Indent each line of the value
                value_lines = value_str.split("\n")
                first_line = value_lines[0]
                rest_lines = [f"{indentation}{line}" for line in value_lines[1:]]

                # Add the key and first line of the value
                lines.append(f"{indentation}{key} = {first_line}")

                # Add the rest of the value lines
                lines.extend(rest_lines)
            else:
                # Single line value
                lines.append(f"{indentation}{key} = {value_str}")

            # Add comma if not the last item
            if i < len(items) - 1:
                lines[-1] += ","

            # Add inline comment for this key-value pair
            if kv_node.inline_comment:
                lines[-1] += f"  // {kv_node.inline_comment.text}"

        # Add orphaned comments before closing brace (but after content)
        if hasattr(node, "end_leading_comments") and node.end_leading_comments:
            for comment in node.end_leading_comments:
                lines.append(f"{indentation}// {comment.text}")

        # Close the object
        lines.append("}")

        return "\n".join(lines)

    def _serialize_list(self, node: ListNode, indentation_count: int = 4) -> str:
        """
        Serialize a list node to FTML text.

        Args:
            node: The list node to serialize.
            indentation_count: The number of spaces to use for indentation (default is 4).

        Returns:
            The FTML text representation of the list.
        """
        # Create the indentation string based on the count
        indentation = " " * indentation_count

        if not node.elements:
            return "[]"

        lines = ["["]

        # Add inner doc comments at the beginning of the list
        if hasattr(node, "inner_doc_comments") and node.inner_doc_comments:
            for comment in node.inner_doc_comments:
                lines.append(f"{indentation}//! {comment.text}")

        # Add leading comments for the list
        for comment in node.leading_comments:
            lines.append(f"{indentation}// {comment.text}")

        # Add inline comment for the opening bracket if present
        if node.inline_comment:
            lines[0] += f"  // {node.inline_comment.text}"

        # Serialize each list element
        for i, elem in enumerate(node.elements):
            # Add outer doc comments for this element
            if hasattr(elem, "outer_doc_comments") and elem.outer_doc_comments:
                for comment in elem.outer_doc_comments:
                    lines.append(f"{indentation}/// {comment.text}")

            # Add leading comments for this element
            for comment in elem.leading_comments:
                lines.append(f"{indentation}// {comment.text}")

            # Serialize the element
            elem_str = self._serialize_value(elem)

            # Handle multiline elements
            if "\n" in elem_str:
                # Indent each line of the element
                elem_lines = elem_str.split("\n")
                first_line = elem_lines[0]
                rest_lines = [f"{indentation}{line}" for line in elem_lines[1:]]

                # Add the first line of the element
                lines.append(f"{indentation}{first_line}")

                # Add the rest of the element lines
                lines.extend(rest_lines)
            else:
                # Single line element
                lines.append(f"{indentation}{elem_str}")

            # Add comma if not the last element
            if i < len(node.elements) - 1:
                lines[-1] += ","

            # Add inline comment for this element
            if elem.inline_comment:
                lines[-1] += f"  // {elem.inline_comment.text}"

        # Add orphaned comments before closing bracket (but after content)
        if hasattr(node, "end_leading_comments") and node.end_leading_comments:
            for comment in node.end_leading_comments:
                lines.append(f"{indentation}// {comment.text}")

        # Close the list
        lines.append("]")

        return "\n".join(lines)


def serialize(root: DocumentNode) -> str:
    """
    Serialize an AST to FTML text.

    Args:
        root: The root DocumentNode to serialize.

    Returns:
        The FTML text representation of the AST.
    """
    serializer = Serializer(root)
    return serializer.serialize()
