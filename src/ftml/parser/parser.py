"""
FTML Parser Module

Implements a two-pass parser for FTML:
1. First pass parses the structure, ignoring comments
2. Second pass attaches comments to the appropriate nodes
"""

from typing import List

from ftml.exceptions import FTMLParseError
from ftml.logger import logger

from .comment_attacher import CommentAttacher
from .tokenizer import Token, TokenType, Tokenizer
from .ast import Node, DocumentNode, KeyValueNode, ScalarNode, ObjectNode, ListNode


class StructuralParser:
    """
    First-pass parser that builds the AST structure, ignoring comments.
    """

    def __init__(self, tokens: List[Token]):
        """
        Initialize the parser with a list of tokens.

        Args:
            tokens: The tokens to parse.
        """
        # Filter out all comment tokens for the structural parsing
        self.tokens = [
            t
            for t in tokens
            if t.type
            not in (
                TokenType.COMMENT,
                # TokenType.DOC_COMMENT,
                TokenType.OUTER_DOC_COMMENT,
                TokenType.INNER_DOC_COMMENT,
            )
        ]
        self.pos = 0

    def peek(self) -> Token:
        """
        Look at the current token without advancing.

        Returns:
            The current token, or an EOF token if at the end.
        """
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, None, -1, -1)

    def advance(self) -> Token:
        """
        Get the current token and advance to the next.

        Returns:
            The current token.
        """
        token = self.peek()
        self.pos += 1
        return token

    def match(self, *types: TokenType) -> bool:
        """
        Check if the current token is one of the specified types,
        and advance if it is.

        Args:
            *types: The token types to match.

        Returns:
            True if the current token matched, False otherwise.
        """
        if self.check(*types):
            self.advance()
            return True
        return False

    def check(self, *types: TokenType) -> bool:
        """
        Check if the current token is one of the specified types.

        Args:
            *types: The token types to check.

        Returns:
            True if the current token is one of the specified types.
        """
        current = self.peek()
        return current.type in types

    def consume(self, type: TokenType, message: str) -> Token:
        """
        Consume a token of the expected type or raise an error.

        Args:
            type: The expected token type.
            message: The error message if the token is not of the expected type.

        Returns:
            The consumed token.

        Raises:
            FTMLParseError: If the current token is not of the expected type.
        """
        if self.check(type):
            return self.advance()

        token = self.peek()
        raise FTMLParseError(
            f"{message} at line {token.line}, col {token.col}. " f"Got {token.type.name} {token.value!r}"
        )

    def parse(self) -> DocumentNode:
        """
        Parse the tokens into a document AST, ignoring comments.

        Returns:
            The root DocumentNode of the AST.
        """
        document = DocumentNode()
        logger.debug("Starting first-pass structural parsing")

        # Skip initial whitespace and newlines
        self._skip_whitespace_and_newlines()

        # Parse root-level key-value pairs
        while not self.check(TokenType.EOF):
            # Skip any whitespace and newlines
            self._skip_whitespace_and_newlines()

            # If at EOF, break
            if self.check(TokenType.EOF):
                break

            # Parse a key-value pair - supports both identifiers and quoted strings as keys
            if self.check(TokenType.IDENT, TokenType.STRING, TokenType.SINGLE_STRING):
                kv_node = self._parse_key_value_pair()

                # Check for duplicate keys
                if kv_node.key in document.items:
                    raise FTMLParseError(
                        f"Duplicate root key '{kv_node.key}' at line {kv_node.line}, col {kv_node.col}"
                    )

                document.items[kv_node.key] = kv_node

                # After parsing a key-value pair, first skip any whitespace (but not newlines)
                while self.check(TokenType.WHITESPACE):
                    self.advance()

                # Then check if the next token is a newline or EOF
                if not self.check(TokenType.NEWLINE, TokenType.EOF):
                    token = self.peek()
                    raise FTMLParseError(
                        f"Expected newline after key-value pair at line {token.line}, col {token.col}. "
                        f"Got {token.type.name} {token.value!r}"
                    )

            else:
                token = self.peek()
                logger.debug(f"Expected a key but got: {token.type.name} {token.value!r}")
                raise FTMLParseError(
                    f"Expected a key (identifier or quoted string) at line {token.line}, col {token.col}. "
                    f"Got {token.type.name} {token.value!r}"
                )

        logger.debug(f"Finished first-pass parsing with {len(document.items)} root items")
        return document

    def _parse_key_value_pair(self) -> KeyValueNode:
        """
        Parse a key-value pair.

        Returns:
            The KeyValueNode representing the key-value pair.
        """
        # Get the key token - now supports quoted keys
        if self.check(TokenType.IDENT):
            key_token = self.advance()
            key = key_token.value
        elif self.check(TokenType.STRING, TokenType.SINGLE_STRING):
            key_token = self.advance()
            key = key_token.value
        else:
            raise FTMLParseError(
                f"Expected a key (identifier or quoted string) at line {self.peek().line}, col {self.peek().col}. "
                f"Got {self.peek().type.name} {self.peek().value!r}"
            )

        # Skip whitespace after key
        self._skip_whitespace()

        # Expect equals sign
        self.consume(TokenType.EQUAL, f"Expected '=' after key '{key}'")

        # Skip whitespace after equals
        self._skip_whitespace()

        # Parse the value
        value_node = self._parse_value()

        # Create and return the key-value node
        return KeyValueNode(key, value_node, key_token.line, key_token.col)

    def _parse_value(self) -> Node:
        """
        Parse a value (scalar, object, or list).

        Returns:
            The parsed value node.
        """
        if self.check(TokenType.STRING, TokenType.SINGLE_STRING):
            token = self.advance()
            return ScalarNode(token.value, token.line, token.col)

        elif self.check(TokenType.INT, TokenType.FLOAT):
            token = self.advance()
            return ScalarNode(token.value, token.line, token.col)

        elif self.check(TokenType.BOOL):
            token = self.advance()
            return ScalarNode(token.value, token.line, token.col)

        elif self.check(TokenType.NULL):
            token = self.advance()
            return ScalarNode(None, token.line, token.col)

        elif self.check(TokenType.LBRACE):
            # Parse object
            return self._parse_object()

        elif self.check(TokenType.LBRACKET):
            # Parse list
            return self._parse_list()

        # If we get here, it's an error
        token = self.peek()
        logger.debug(f"Expected value but got: {token.type.name} {token.value!r}")
        raise FTMLParseError(
            f"Expected a value at line {token.line}, col {token.col}. " f"Got {token.type.name} {token.value!r}"
        )

    def _parse_object(self) -> ObjectNode:
        """
        Parse an object (collection of key-value pairs enclosed in braces).

        Returns:
            The ObjectNode representing the object.
        """
        # Consume the opening brace
        opening_token = self.advance()
        node = ObjectNode(opening_token.line, opening_token.col)

        # Skip any whitespace and newlines
        self._skip_whitespace_and_newlines()

        # Check for empty object
        if self.check(TokenType.RBRACE):
            self.advance()  # Consume closing brace
            return node

        # Parse key-value pairs
        while True:
            # Skip any whitespace and newlines
            self._skip_whitespace_and_newlines()

            # Check for closing brace
            if self.check(TokenType.RBRACE):
                self.advance()  # Consume closing brace
                return node

            # Parse a key - now can be identifier or quoted string
            if not self.check(TokenType.IDENT, TokenType.STRING, TokenType.SINGLE_STRING):
                raise FTMLParseError(
                    f"Expected a key (identifier or quoted string) at line {self.peek().line}, col {self.peek().col}. "
                    f"Got {self.peek().type.name} {self.peek().value!r}"
                )

            # Parse key-value pair
            kv_node = self._parse_key_value_pair()

            # Check for duplicate keys
            if kv_node.key in node.items:
                raise FTMLParseError(f"Duplicate key '{kv_node.key}' at line {kv_node.line}, col {kv_node.col}")

            # Add to the object
            node.items[kv_node.key] = kv_node

            # Skip any whitespace AND newlines - crucial for handling multiline objects without trailing commas
            self._skip_whitespace_and_newlines()

            # Check for comma or closing brace
            if self.check(TokenType.COMMA):
                self.advance()  # Consume comma
                # Skip any whitespace and newlines after comma
                self._skip_whitespace_and_newlines()
                # If we see a closing brace after a comma, that's fine (trailing comma)
                if self.check(TokenType.RBRACE):
                    self.advance()  # Consume closing brace
                    return node
            elif self.check(TokenType.RBRACE):
                self.advance()  # Consume closing brace
                return node
            else:
                # If not a comma or closing brace, it's an error
                raise FTMLParseError(
                    f"Expected ',' or '}}' after object item at line {self.peek().line}, col {self.peek().col}. "
                    f"Got {self.peek().type.name} {self.peek().value!r}"
                )

    def _parse_list(self) -> ListNode:
        """
        Parse a list (ordered sequence of values enclosed in brackets).

        Returns:
            The ListNode representing the list.
        """
        # Consume the opening bracket
        opening_token = self.advance()
        node = ListNode(opening_token.line, opening_token.col)

        # Skip any whitespace and newlines
        self._skip_whitespace_and_newlines()

        # Check for empty list
        if self.check(TokenType.RBRACKET):
            self.advance()  # Consume closing bracket
            return node

        # Parse list elements
        while True:
            # Skip any whitespace and newlines
            self._skip_whitespace_and_newlines()

            # Check for closing bracket
            if self.check(TokenType.RBRACKET):
                self.advance()  # Consume closing bracket
                return node

            # Parse value
            value_node = self._parse_value()

            # Add to the list
            node.elements.append(value_node)

            # Skip any whitespace AND newlines - this is crucial for handling multiline lists without trailing commas
            self._skip_whitespace_and_newlines()

            # Check for comma or closing bracket
            if self.check(TokenType.COMMA):
                self.advance()  # Consume comma
                # Skip any whitespace and newlines after comma
                self._skip_whitespace_and_newlines()
                # If we see a closing bracket after a comma, that's fine (trailing comma)
                if self.check(TokenType.RBRACKET):
                    self.advance()  # Consume closing bracket
                    return node
            elif self.check(TokenType.RBRACKET):
                self.advance()  # Consume closing bracket
                return node
            else:
                # If not a comma or closing bracket, it's an error
                raise FTMLParseError(
                    f"Expected ',' or ']' after list element at line {self.peek().line}, col {self.peek().col}. "
                    f"Got {self.peek().type.name} {self.peek().value!r}"
                )

    def _skip_whitespace(self):
        """Skip any whitespace tokens (but not newlines)."""
        while self.check(TokenType.WHITESPACE):
            self.advance()

    def _skip_whitespace_and_newlines(self):
        """Skip any whitespace and newline tokens."""
        while self.check(TokenType.WHITESPACE, TokenType.NEWLINE):
            self.advance()


def parse(ftml_text: str) -> DocumentNode:
    """
    Parse FTML text into an AST.

    Args:
        ftml_text: The FTML text to parse.

    Returns:
        The root DocumentNode of the AST.
    """
    logger.debug("Starting FTML parsing")
    tokenizer = Tokenizer(ftml_text)
    tokens = tokenizer.tokenize()
    logger.debug(f"Tokenized {len(tokens)} tokens")

    # First pass: Build the AST structure, ignoring comments
    structure_parser = StructuralParser(tokens)
    ast = structure_parser.parse()

    # Second pass: Attach comments to the appropriate nodes
    # using our simplified approach that only handles leading and inline comments
    comment_attacher = CommentAttacher(tokens, ast)
    ast = comment_attacher.attach_comments()

    return ast
