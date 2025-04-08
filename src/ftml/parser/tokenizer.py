"""
FTML Tokenizer Module

Defines the tokens and tokenizer for the FTML language.
The tokenizer converts raw FTML text into a stream of tokens,
preserving comments and positional information for round-trip parsing.
"""

import re
import enum
from typing import List, Any, NamedTuple

from ftml.exceptions import FTMLParseError
from ftml.logger import logger


class TokenType(enum.Enum):
    """Types of tokens in the FTML language."""

    OUTER_DOC_COMMENT = "OUTER_DOC_COMMENT"  # /// Generate docs for following item
    INNER_DOC_COMMENT = "INNER_DOC_COMMENT"  # //! Generate docs for enclosing item
    COMMENT = "COMMENT"  # // Comment text
    STRING = "STRING"  # "String value"
    SINGLE_STRING = "SINGLE_STRING"  # 'String value'
    INT = "INT"  # 42
    FLOAT = "FLOAT"  # 3.14
    BOOL = "BOOL"  # true, false
    NULL = "NULL"  # null
    IDENT = "IDENT"  # identifier (key name)
    LBRACE = "LBRACE"  # {
    RBRACE = "RBRACE"  # }
    LBRACKET = "LBRACKET"  # [
    RBRACKET = "RBRACKET"  # ]
    EQUAL = "EQUAL"  # =
    COMMA = "COMMA"  # ,
    NEWLINE = "NEWLINE"  # \n
    WHITESPACE = "WHITESPACE"  # Space, tab, etc.
    EOF = "EOF"  # End of file


class Token(NamedTuple):
    """
    Represents a token in the FTML language.

    Attributes:
        type: The type of the token.
        value: The string value of the token.
        line: The line number in the source.
        col: The column number in the source.
    """

    type: TokenType
    value: Any
    line: int
    col: int


class Tokenizer:
    """
    Tokenizes FTML text into a stream of Token objects.

    This tokenizer preserves all whitespace, newlines, and comments
    to enable perfect round-trip parsing.
    """

    # Token regex patterns
    TOKEN_PATTERNS = [
        (TokenType.OUTER_DOC_COMMENT, r"///[^\n]*"),  # Must come before regular comments
        (TokenType.INNER_DOC_COMMENT, r"//![^\n]*"),  # Must come before regular comments
        (TokenType.COMMENT, r"//[^\n]*"),
        (TokenType.STRING, r'"(?:\\.|[^"\\])*"'),
        (TokenType.SINGLE_STRING, r"'(?:''|[^'])*'"),
        (TokenType.FLOAT, r"[+-]?\d+\.\d+"),
        (TokenType.INT, r"[+-]?\d+"),
        (TokenType.BOOL, r"\b(?:true|false)\b"),
        (TokenType.NULL, r"\bnull\b"),
        (TokenType.IDENT, r"[A-Za-z_][A-Za-z0-9_]*"),
        (TokenType.LBRACE, r"\{"),
        (TokenType.RBRACE, r"\}"),
        (TokenType.LBRACKET, r"\["),
        (TokenType.RBRACKET, r"\]"),
        (TokenType.EQUAL, r"="),
        (TokenType.COMMA, r","),
        (TokenType.WHITESPACE, r"[ \t\r]+"),
        (TokenType.NEWLINE, r"\n"),
    ]

    def __init__(self, text: str):
        """
        Initialize the tokenizer with the text to tokenize.

        Args:
            text: The FTML text to tokenize.
        """
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.patterns = []
        for ttype, pattern in self.TOKEN_PATTERNS:
            self.patterns.append((ttype, re.compile(pattern)))

    def _match(self):
        """
        Find the longest matching token at the current position.

        Returns:
            A tuple of (token_type, match_object) or None if no match.
        """
        if self.pos >= len(self.text):
            return None

        best_match = None
        best_ttype = None

        for ttype, regex in self.patterns:
            m = regex.match(self.text, self.pos)
            if m and (best_match is None or m.end() > best_match.end()):
                best_match = m
                best_ttype = ttype

        return (best_ttype, best_match) if best_match else None

    def _advance_line(self):
        """Update line count and reset column count when encountering a newline."""
        self.line += 1
        self.col = 1

    def next_token(self) -> Token:
        """
        Get the next token from the input.

        Returns:
            The next token.

        Raises:
            FTMLParseError: If the input contains unrecognized text.
        """
        if self.pos >= len(self.text):
            return Token(TokenType.EOF, None, self.line, self.col)

        result = self._match()
        if not result:
            error_context = self.text[self.pos: min(self.pos + 10, len(self.text))]
            raise FTMLParseError(
                f"Tokenization error at line {self.line}, col {self.col}: " f"unrecognized text {error_context!r}"
            )

        ttype, match = result
        token_str = match.group()
        start_line, start_col = self.line, self.col

        # Update position and tracking info
        self.pos = match.end()
        for ch in token_str:
            if ch == "\n":
                self._advance_line()
            else:
                self.col += 1

        # Process the token value based on its type
        if ttype == TokenType.SINGLE_STRING:
            # Handle single-quoted strings ('text')
            value = self._interpret_single_quoted(token_str)
        elif ttype == TokenType.STRING:
            # Handle double-quoted strings ("text")
            value = self._interpret_double_quoted(token_str)
        elif ttype == TokenType.INT:
            value = int(token_str)
        elif ttype == TokenType.FLOAT:
            value = float(token_str)
        elif ttype == TokenType.BOOL:
            value = token_str.lower() == "true"
        elif ttype == TokenType.NULL:
            value = None
        else:
            value = token_str

        return Token(ttype, value, start_line, start_col)

    def _interpret_single_quoted(self, raw: str) -> str:
        """
        Parse the contents of a single-quoted string.

        Args:
            raw: The raw string including quotes.

        Returns:
            The interpreted string value.
        """
        # Remove outer quotes
        inner = raw[1:-1]
        # Handle doubled single quotes as escapes ('it''s' -> "it's")
        return inner.replace("''", "'")

    def _interpret_double_quoted(self, raw: str) -> str:
        """
        Parse the contents of a double-quoted string, interpreting escape sequences.

        Args:
            raw: The raw string including quotes.

        Returns:
            The interpreted string value with escape sequences processed.
        """
        # Remove outer quotes
        inner = raw[1:-1]
        # Process all escape sequences
        return (
            inner.replace(r"\\", "\\")  # Must come first to avoid double-escaping
            .replace(r"\"", '"')
            .replace(r"\n", "\n")
            .replace(r"\t", "\t")
            .replace(r"\r", "\r")
            .replace(r"\a", "\a")
            .replace(r"\b", "\b")
            .replace(r"\f", "\f")
            .replace(r"\v", "\v")
        )

    def tokenize(self) -> List[Token]:
        """
        Tokenize the entire input text.

        Returns:
            A list of all tokens in the input, including whitespace and comments.
        """
        tokens = []
        while True:
            token = self.next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break

        logger.debug(f"Tokenized {len(tokens)} tokens")
        return tokens
