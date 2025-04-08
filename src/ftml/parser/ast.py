"""
FTML Abstract Syntax Tree Node Definitions

This module defines the node classes that make up the AST (Abstract Syntax Tree)
for the FTML language. Each node includes fields for storing comments to enable
round-trip parsing.
"""

from typing import List, Dict, Any, Optional


class Comment:
    """
    Represents a comment in the FTML document.

    Attributes:
        text: The text of the comment (not including the // or ////),
        line: The line number where the comment appears.
        col: The column where the comment starts.
    """

    def __init__(self, text: str, line: int, col: int):
        """
        Initialize a Comment.

        Args:
            text: The text of the comment (not including the // or ////),
            line: The line number where the comment appears.
            col: The column where the comment starts.
        """
        self.text = text.strip()
        self.line = line
        self.col = col

    def __repr__(self) -> str:
        """String representation of the comment for debugging."""
        return f"Comment({self.text!r}, line={self.line}, col={self.col})"


class Node:
    """
    Base class for all AST nodes.

    All nodes can have associated comments:
    - leading_comments: Comments that appear before this node
    - inline_comment: Comment that appears on the same line as this node
    - outer_doc_comments: Documentation comments (///) that document the following item.
    """

    def __init__(self):
        """Initialize a Node with empty comments lists."""
        self.leading_comments: List[Comment] = []
        self.inline_comment: Optional[Comment] = None
        # self.trailing_comments: List[Comment] = []  # deprecated
        self.outer_doc_comments: List[Comment] = []  # /// comments

    def has_comments(self) -> bool:
        """Check if this node has any active comments attached."""
        return bool(self.leading_comments) or self.inline_comment is not None or bool(self.outer_doc_comments)


class DocumentNode(Node):
    """
    Top-level node for an FTML document.

    Attributes:
        items: Dictionary of key-value pairs at the root level.
        inner_doc_comments: List of inner documentation comments (//!) at the document level.
    """

    def __init__(self):
        """Initialize a DocumentNode with empty items."""
        super().__init__()
        self.items: Dict[str, KeyValueNode] = {}
        self.inner_doc_comments: List[Comment] = []  # //! comments
        self.end_leading_comments: List[Comment] = []  # Comments after the last node

    def __repr__(self) -> str:
        """String representation of the document for debugging."""
        return f"<DocumentNode with {len(self.items)} items>"


class KeyValueNode(Node):
    """
    Represents a key-value pair (key = value).

    Attributes:
        key: The key string.
        value: The value node.
        line: The line number where this node appears.
        col: The column where this node starts.
    """

    def __init__(self, key: str, value: "Node", line: int, col: int):
        """
        Initialize a KeyValueNode.

        Args:
            key: The key string.
            value: The value node.
            line: The line number where this node appears.
            col: The column where this node starts.
        """
        super().__init__()
        self.key = key
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self) -> str:
        """String representation of the key-value pair for debugging."""
        return f"<KeyValueNode {self.key}={self.value!r}>"


class ScalarNode(Node):
    """
    Represents a scalar value (string, int, float, bool, null).

    Attributes:
        value: The scalar value.
        line: The line number where this node appears.
        col: The column where this node starts.
    """

    def __init__(self, value: Any, line: int, col: int):
        """
        Initialize a ScalarNode.

        Args:
            value: The scalar value.
            line: The line number where this node appears.
            col: The column where this node starts.
        """
        super().__init__()
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self) -> str:
        """String representation of the scalar for debugging."""
        return f"<ScalarNode value={self.value!r}>"


class ObjectNode(Node):
    """
    Represents an object (collection of key-value pairs in braces).

    Attributes:
        items: Dictionary of key to KeyValueNode.
        line: The line number where this node appears.
        col: The column where this node starts.
        inner_doc_comments: List of inner documentation comments (//!) for this object.
    """

    def __init__(self, line: int, col: int):
        """
        Initialize an ObjectNode with empty items.

        Args:
            line: The line number where this node appears.
            col: The column where this node starts.
        """
        super().__init__()
        self.items: Dict[str, KeyValueNode] = {}
        self.line = line
        self.col = col
        self.inner_doc_comments: List[Comment] = []  # //! comments
        self.end_leading_comments: List[Comment] = []  # Comments before closing brace

    def __repr__(self) -> str:
        """String representation of the object for debugging."""
        return f"<ObjectNode with {len(self.items)} items>"


class ListNode(Node):
    """
    Represents a list (ordered collection of values in brackets).

    Attributes:
        elements: List of child nodes.
        line: The line number where this node appears.
        col: The column where this node starts.
        self.inline_comment_end: Optional[Comment] = None
        inline_comment_end: Comment on the closing bracket, if any.
    """

    def __init__(self, line: int, col: int):
        """
        Initialize a ListNode with empty elements.

        Args:
            line: The line number where this node appears.
            col: The column where this node starts.
        """
        super().__init__()
        self.elements: List[Node] = []
        self.line = line
        self.col = col
        self.inline_comment_end: Optional[Comment] = None  # For comments on closing bracket
        self.inner_doc_comments: List[Comment] = []  # //! comments
        self.end_leading_comments: List[Comment] = []  # Comments before closing bracket
