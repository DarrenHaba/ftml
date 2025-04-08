"""
FTML Comment Attacher Module

Handles attaching comments to AST nodes with support for:
1. Doc comments (/// and //!)
2. Leading comments (comments above a node)
3. Inline comments (comments on the same line)
"""

from typing import List, Union

from ftml.logger import logger

from .tokenizer import Token, TokenType
from .ast import Comment, Node, DocumentNode, KeyValueNode, ObjectNode, ListNode


class CommentAttacher:
    """
    Attaches comments to AST nodes including doc comments:
    - Outer doc comments (///): Documentation for the following item
    - Inner doc comments (//!): Documentation for the enclosing item
    - Leading comments (//): Comments that appear before a node
    - Inline comments (//): Comments that appear on the same line as a node
    """

    def __init__(self, tokens: List[Token], ast: DocumentNode):
        """
        Initialize the comment attacher.

        Args:
            tokens: All tokens including comments.
            ast: The AST structure built by the first pass.
        """
        self.tokens = tokens
        self.ast = ast
        self.processed_comments = set()  # Track processed comments by (line, col)

        # Build a mapping of line numbers to tokens for easier processing
        self.line_to_tokens = {}
        for token in tokens:
            if token.line not in self.line_to_tokens:
                self.line_to_tokens[token.line] = []
            self.line_to_tokens[token.line].append(token)

        # Find the last line in the file
        self.last_line = max(self.line_to_tokens.keys()) if self.line_to_tokens else 1

    def attach_comments(self) -> DocumentNode:
        """
        Attach comments to nodes in the AST.

        Returns:
            The AST with comments attached.
        """
        logger.debug("Starting comment attachment with doc comment support")

        # Process document-level inner doc comments first
        self._attach_document_inner_doc_comments()

        # Special case: Empty document (no nodes)
        if not self.ast.items:
            self._handle_empty_document()
            return self.ast

        # Process root level key-value pairs normally
        for key, kv_node in self.ast.items.items():
            # Standard comment attachment
            self._attach_outer_doc_comments(kv_node)
            self._attach_leading_comments(kv_node)
            self._attach_inline_comment(kv_node)

            # Process collections
            if isinstance(kv_node.value, ListNode):
                self._attach_collection_inner_doc_comments(kv_node.value)
                self._process_list(kv_node.value)
                # Special case: Check for orphaned comments in the list
                self._check_list_orphaned_comments(kv_node.value)
            elif isinstance(kv_node.value, ObjectNode):
                self._attach_collection_inner_doc_comments(kv_node.value)
                self._process_object(kv_node.value)
                # Special case: Check for orphaned comments in the object
                self._check_object_orphaned_comments(kv_node.value)

        # Special case: Check for document-level orphaned comments
        self._check_document_orphaned_comments()

        logger.debug(f"Completed comment attachment, processed {len(self.processed_comments)} comments")
        return self.ast

    def _handle_empty_document(self) -> None:
        """Special case: Handle a document with no nodes."""
        # For empty documents, all comments are considered document leading comments
        for line in range(1, self.last_line + 1):
            if line not in self.line_to_tokens:
                continue

            for token in self.line_to_tokens[line]:
                if token.type == TokenType.COMMENT and (token.line, token.col) not in self.processed_comments:
                    text = token.value[2:].strip()  # Remove // prefix
                    comment = Comment(text, token.line, token.col)
                    self.ast.leading_comments.append(comment)
                    self.processed_comments.add((token.line, token.col))

    def _check_document_orphaned_comments(self) -> None:
        """Special case: Check for comments after the last node in the document."""
        # Find the last line that contains a node
        last_node_line = 0
        for key, kv_node in self.ast.items.items():
            if kv_node.line > last_node_line:
                last_node_line = kv_node.line

        # Look for comments after the last node
        orphaned_comments = []
        for line in range(last_node_line + 1, self.last_line + 1):
            if line not in self.line_to_tokens:
                continue

            for token in self.line_to_tokens[line]:
                if token.type == TokenType.COMMENT and (token.line, token.col) not in self.processed_comments:
                    text = token.value[2:].strip()  # Remove // prefix
                    comment = Comment(text, token.line, token.col)
                    orphaned_comments.append(comment)
                    self.processed_comments.add((token.line, token.col))

        # Attach orphaned comments to the document
        self.ast.end_leading_comments = orphaned_comments

    def _check_list_orphaned_comments(self, list_node: ListNode) -> None:
        """Special case: Check for comments after the last element in a list."""
        # Skip empty lists
        if not list_node.elements:
            return

        # Find the last line containing an element
        last_elem_line = 0
        for elem in list_node.elements:
            if hasattr(elem, "line") and elem.line > last_elem_line:
                last_elem_line = elem.line

        # Find the closing bracket line (search from the last element line forward)
        closing_line = None
        for line in range(last_elem_line + 1, self.last_line + 1):
            if line not in self.line_to_tokens:
                continue

            for token in self.line_to_tokens[line]:
                if token.type == TokenType.RBRACKET:
                    closing_line = line
                    break

            if closing_line:
                break

        if not closing_line:
            return  # Cannot find closing bracket

        # Look for comments between last element and closing bracket
        orphaned_comments = []
        for line in range(last_elem_line + 1, closing_line):
            if line not in self.line_to_tokens:
                continue

            for token in self.line_to_tokens[line]:
                if token.type == TokenType.COMMENT and (token.line, token.col) not in self.processed_comments:
                    text = token.value[2:].strip()  # Remove // prefix
                    comment = Comment(text, token.line, token.col)
                    orphaned_comments.append(comment)
                    self.processed_comments.add((token.line, token.col))

        # Attach orphaned comments to the list
        list_node.end_leading_comments = orphaned_comments

    def _check_object_orphaned_comments(self, obj_node: ObjectNode) -> None:
        """Special case: Check for comments after the last property in an object."""
        # Skip empty objects
        if not obj_node.items:
            return

        # Find the last line containing a property
        last_prop_line = 0
        for key, kv_node in obj_node.items.items():
            if kv_node.line > last_prop_line:
                last_prop_line = kv_node.line

        # Find the closing brace line (search from the last property line forward)
        closing_line = None
        for line in range(last_prop_line + 1, self.last_line + 1):
            if line not in self.line_to_tokens:
                continue

            for token in self.line_to_tokens[line]:
                if token.type == TokenType.RBRACE:
                    closing_line = line
                    break

            if closing_line:
                break

        if not closing_line:
            return  # Cannot find closing brace

        # Look for comments between last property and closing brace
        orphaned_comments = []
        for line in range(last_prop_line + 1, closing_line):
            if line not in self.line_to_tokens:
                continue

            for token in self.line_to_tokens[line]:
                if token.type == TokenType.COMMENT and (token.line, token.col) not in self.processed_comments:
                    text = token.value[2:].strip()  # Remove // prefix
                    comment = Comment(text, token.line, token.col)
                    orphaned_comments.append(comment)
                    self.processed_comments.add((token.line, token.col))

        # Attach orphaned comments to the object
        obj_node.end_leading_comments = orphaned_comments

    def _attach_document_inner_doc_comments(self) -> None:
        """
        Find and attach inner doc comments at the document level.
        """
        # Look for inner doc comments at the beginning of the file
        doc_inner_comments = []

        # Find all INNER_DOC_COMMENT tokens
        for line_num, tokens in sorted(self.line_to_tokens.items()):
            for token in tokens:
                if token.type == TokenType.INNER_DOC_COMMENT:
                    text = token.value[3:].strip()  # Remove //! prefix
                    comment = Comment(text, token.line, token.col)
                    doc_inner_comments.append(comment)
                    self.processed_comments.add((token.line, token.col))
                elif token.type not in (
                    TokenType.WHITESPACE,
                    TokenType.NEWLINE,
                    TokenType.COMMENT,
                    TokenType.OUTER_DOC_COMMENT,
                ):
                    # If we found a non-comment token, we're done with document-level comments
                    self.ast.inner_doc_comments = doc_inner_comments
                    return

        # If we got here, we've processed all tokens
        self.ast.inner_doc_comments = doc_inner_comments

    def _attach_collection_inner_doc_comments(self, node: Union[ListNode, ObjectNode]) -> None:
        """
        Find and attach inner doc comments to a collection node.

        Args:
            node: The collection node to process.
        """
        # Check lines after the opening bracket/brace
        collection_inner_comments = []

        # Get the line of the opening bracket/brace
        start_line = node.line

        # Find the first non-whitespace line
        for line in range(start_line + 1, self.last_line + 1):
            if not self.line_to_tokens.get(line):
                continue

            # Check if this line has an inner doc comment
            has_inner_doc = False
            has_other_content = False

            for token in self.line_to_tokens[line]:
                if token.type == TokenType.INNER_DOC_COMMENT:
                    if (token.line, token.col) not in self.processed_comments:
                        text = token.value[3:].strip()  # Remove //! prefix
                        comment = Comment(text, token.line, token.col)
                        collection_inner_comments.append(comment)
                        self.processed_comments.add((token.line, token.col))
                        has_inner_doc = True
                elif token.type not in (TokenType.WHITESPACE, TokenType.NEWLINE):
                    # If we found a non-inner-doc token, stop collecting inner doc comments
                    has_other_content = True
                    break

            # If we found non-inner-doc content or no inner doc comment, stop
            if has_other_content or not has_inner_doc:
                break

        # Attach inner doc comments to the collection
        node.inner_doc_comments = collection_inner_comments

    def _attach_outer_doc_comments(self, node: Node) -> None:
        """
        Find and attach outer doc comments to a node.

        Args:
            node: The node to process.
        """
        if not hasattr(node, "line"):
            return

        # Find the previous node line
        prev_line = self._find_previous_node_line(node)
        node_line = node.line

        # Check lines between prev_line and node_line for outer doc comments
        outer_doc_comments = []

        for line in range(prev_line + 1, node_line):
            if not self.line_to_tokens.get(line):
                continue

            for token in self.line_to_tokens[line]:
                if token.type == TokenType.OUTER_DOC_COMMENT and (token.line, token.col) not in self.processed_comments:
                    text = token.value[3:].strip()  # Remove /// prefix
                    comment = Comment(text, token.line, token.col)
                    outer_doc_comments.append(comment)
                    self.processed_comments.add((token.line, token.col))

        # Attach outer doc comments to the node
        if hasattr(node, "outer_doc_comments"):
            node.outer_doc_comments = outer_doc_comments

    def _attach_leading_comments(self, node: Node) -> None:
        """
        Find and attach leading comments to a node.

        Args:
            node: The node to process.
        """
        if not hasattr(node, "line"):
            return

        # Find the previous node line
        prev_line = self._find_previous_node_line(node)
        node_line = node.line

        # Check lines between prev_line and node_line for regular comments
        leading_comments = []

        for line in range(prev_line + 1, node_line):
            if not self.line_to_tokens.get(line):
                continue

            for token in self.line_to_tokens[line]:
                if token.type == TokenType.COMMENT and (token.line, token.col) not in self.processed_comments:
                    text = token.value[2:].strip()  # Remove // prefix
                    comment = Comment(text, token.line, token.col)
                    leading_comments.append(comment)
                    self.processed_comments.add((token.line, token.col))

        # Attach leading comments to the node
        if hasattr(node, "leading_comments"):
            node.leading_comments = leading_comments

    def _attach_inline_comment(self, node: Node) -> None:
        """
        Find and attach an inline comment to a node.

        Args:
            node: The node to process.
        """
        if not hasattr(node, "line"):
            return

        node_line = node.line

        # Check the same line as the node for a regular comment
        if not self.line_to_tokens.get(node_line):
            return

        for token in self.line_to_tokens[node_line]:
            if token.type == TokenType.COMMENT and (token.line, token.col) not in self.processed_comments:
                text = token.value[2:].strip()  # Remove // prefix
                comment = Comment(text, token.line, token.col)
                if hasattr(node, "inline_comment"):
                    node.inline_comment = comment
                    self.processed_comments.add((token.line, token.col))
                break

    def _process_list(self, list_node: ListNode) -> None:
        """
        Process a list node and its elements.

        Args:
            list_node: The list node to process.
        """
        # Process each element in the list
        for element in list_node.elements:
            # First attach outer doc comments
            self._attach_outer_doc_comments(element)

            # Then attach regular comments
            self._attach_leading_comments(element)
            self._attach_inline_comment(element)

            # Recursively process nested collections
            if isinstance(element, ListNode):
                self._attach_collection_inner_doc_comments(element)
                self._process_list(element)
            elif isinstance(element, ObjectNode):
                self._attach_collection_inner_doc_comments(element)
                self._process_object(element)

    def _process_object(self, obj_node: ObjectNode) -> None:
        """
        Process an object node and its properties.

        Args:
            obj_node: The object node to process.
        """
        # Process each property in the object
        for key, kv_node in obj_node.items.items():
            # First attach outer doc comments
            self._attach_outer_doc_comments(kv_node)

            # Then attach regular comments
            self._attach_leading_comments(kv_node)
            self._attach_inline_comment(kv_node)

            # Recursively process nested collections
            if isinstance(kv_node.value, ListNode):
                self._attach_collection_inner_doc_comments(kv_node.value)
                self._process_list(kv_node.value)
            elif isinstance(kv_node.value, ObjectNode):
                self._attach_collection_inner_doc_comments(kv_node.value)
                self._process_object(kv_node.value)

    def _find_previous_node_line(self, node: Node) -> int:
        """
        Find the line of the previous node or other important syntax element.

        Args:
            node: The current node.

        Returns:
            The line number of the previous node or 0 if no previous node.
        """
        if not hasattr(node, "line"):
            return 0

        node_line = node.line

        # For root-level key-value nodes
        if isinstance(node, KeyValueNode) and node.key in self.ast.items:
            # Check previous key-value nodes
            prev_line = 0
            for key, kv_node in self.ast.items.items():
                if kv_node.line < node_line and kv_node.line > prev_line:
                    prev_line = kv_node.line
            return prev_line

        # For nodes inside collections, use heuristics
        # This is a simplified approach; a more thorough approach would track parent nodes
        return max(0, node_line - 5)  # Just a simple heuristic
