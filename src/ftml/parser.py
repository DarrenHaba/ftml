from enum import Enum, auto
from typing import List, Dict, Any, Union, Optional


class TokenType(Enum):
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    COLON = auto()  # :
    EQUAL = auto()  # =
    COMMA = auto()  # ,
    PIPE = auto()  # |
    QUESTION = auto()  # ?
    IDENTIFIER = auto()  # could be unquoted keys or type names
    STRING = auto()
    FLOAT = auto()
    INTEGER = auto()
    BOOLEAN = auto()
    NULL = auto()
    WHITESPACE = auto()
    NEWLINE = auto()
    EOF = auto()


class FTMLParseError(Exception):
    pass


class Token:
    def __init__(self, type_: TokenType, value: Any, line: int = 1, col: int = 1):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value}, line={self.line}, col={self.col})"


class FTMLParser:
    """
    A simplified parser for FTML data using explicit { } for dicts and [ ] for lists.
    - Supports typed dict fields: key?: type|otherType = value
    - Supports typed list items: :type|otherType value
    - Union types with pipe (|), optional with '?'
    - Commas between fields/items
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token: Optional[Token] = None
        self.advance()

    def advance(self):
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
            self.pos += 1
        else:
            self.current_token = Token(TokenType.EOF, None, line=-1, col=-1)

    def parse(self) -> Any:
        """
        Entry point. Expect a single top-level dict or list.
        """
        self.skip_whitespace()
        if self.current_token.type == TokenType.LBRACE:
            return self.parse_dict()
        elif self.current_token.type == TokenType.LBRACKET:
            return self.parse_list()
        else:
            raise FTMLParseError(
                f"Expected '{{' or '[' at start, got {self.current_token.type} at line {self.current_token.line}"
            )

    def parse_dict(self) -> Dict[str, Any]:
        """
        Parse { key [?: type]? = value, ... }
        or { key: type = value, anotherKey = value, ... }
        """
        self.consume(TokenType.LBRACE)
        result: Dict[str, Any] = {}
        self.skip_whitespace()

        while True:
            self.skip_whitespace()
            if self.current_token.type == TokenType.RBRACE:
                # End of dictionary
                break
            if self.current_token.type == TokenType.EOF:
                raise FTMLParseError("Unclosed '{' in dictionary")

            # Parse one "key" and optionally type or optional suffix
            key, optional_flag = self.parse_dict_key()

            self.skip_whitespace()
            # Check if we have a typed field (key: type) or just '='
            field_def = self.maybe_parse_typed_field()

            self.skip_whitespace()
            if field_def is not None:
                # typed => must see '=' if we want a value
                type_str = field_def
                is_optional = optional_flag

                val = None
                if self.current_token.type == TokenType.EQUAL:
                    self.advance()  # consume '='
                    self.skip_whitespace()
                    val = self.parse_value()
                # If there's no '=', we can do val=None or raise an error
                if val is None:
                    val = None

                result[key] = {
                    "type": type_str,
                    "optional": is_optional,
                    "value": val
                }
            else:
                # untyped => must have '='
                self.consume(TokenType.EQUAL)
                self.skip_whitespace()
                val = self.parse_value()
                result[key] = val

            self.skip_whitespace()
            # Now expect either ',' or '}'
            if self.current_token.type == TokenType.COMMA:
                self.advance()  # consume comma
                continue
            elif self.current_token.type == TokenType.RBRACE:
                break
            else:
                raise FTMLParseError(
                    f"Expected ',' or '}}' after dict field, got {self.current_token.type} at line {self.current_token.line}"
                )

        self.consume(TokenType.RBRACE)
        return result

    def parse_dict_key(self):
        """
        Return (key, optional_flag).
        key might be an IDENTIFIER or STRING
        optional_flag is True if key ended with '?'
        """
        tk = self.current_token
        if tk.type not in (TokenType.IDENTIFIER, TokenType.STRING):
            raise FTMLParseError(
                f"Expected dict key (IDENTIFIER/STRING), got {tk.type} at line {tk.line}"
            )
        raw_key = tk.value
        self.advance()

        optional_flag = False
        # If the next token is '?', that means optional. But you said you want "key?" as a single token sometimes.
        # If your tokenizer merges 'key?' into one token, you'd parse it differently. Let's assume we do that below:
        # If you want a separate token for '?', do something else:
        # For simplicity, let's see if raw_key ends with '?':
        if isinstance(raw_key, str) and raw_key.endswith('?'):
            optional_flag = True
            raw_key = raw_key[:-1]

        return raw_key, optional_flag

    def maybe_parse_typed_field(self) -> Optional[str]:
        """
        If the current token is ':', parse a type definition
        which can include union pipes (|).
        Return the full type string (e.g. 'str | null'),
        or None if there's no typed field.
        """
        self.skip_whitespace()
        if self.current_token.type == TokenType.COLON:
            self.advance()  # consume ':'
            self.skip_whitespace()
            # parse the type, including union pipes or brackets/braces if you want nested.
            type_str = self.parse_type_definition()
            return type_str
        return None

    def parse_list(self) -> List[Any]:
        """
        Parse [ item, item, ... ].
        Each item can be:
          - typed list item: :SomeType literalOrStructure
          - untyped literalOrStructure (string, number, {dict}, [list], etc.)
        """
        self.consume(TokenType.LBRACKET)  # consume '['
        items: List[Any] = []
        self.skip_whitespace()

        # We'll loop until we see a ']' or run out of tokens
        while True:
            self.skip_whitespace()
            if self.current_token.type == TokenType.RBRACKET:
                # End of the list
                break
            if self.current_token.type == TokenType.EOF:
                raise FTMLParseError("Unclosed '[' in list")

            # -- Parse exactly one item here --
            if self.current_token.type == TokenType.COLON:
                # typed item
                self.advance()  # consume ':'
                self.skip_whitespace()
                tdef = self.parse_type_definition()  # e.g. "str" or "float | null"
                self.skip_whitespace()
                val = self.parse_value()  # parse the actual value
                items.append({"type": tdef, "value": val})
            else:
                # untyped item
                val = self.parse_value()
                items.append(val)

            # After parsing one item, expect either ',' or ']'
            self.skip_whitespace()
            if self.current_token.type == TokenType.COMMA:
                # consume comma, then loop for next item
                self.advance()
                continue
            elif self.current_token.type == TokenType.RBRACKET:
                # end of list
                break
            else:
                # unexpected token
                raise FTMLParseError(
                    f"Expected comma or ']' after list item, got {self.current_token.type} at line {self.current_token.line}"
                )

        # Now consume the closing bracket
        self.consume(TokenType.RBRACKET)
        return items

    def parse_value(self) -> Any:
        """
        Parse a single value: literal, dict, or list.
        Typed items in a list are handled by parse_list.
        """
        self.skip_whitespace()
        tk = self.current_token

        if tk.type == TokenType.LBRACE:
            return self.parse_dict()
        elif tk.type == TokenType.LBRACKET:
            return self.parse_list()
        elif tk.type in (TokenType.STRING, TokenType.IDENTIFIER,
                         TokenType.FLOAT, TokenType.INTEGER,
                         TokenType.BOOLEAN, TokenType.NULL):
            val = tk.value
            self.advance()
            return val
        else:
            raise FTMLParseError(
                f"Unexpected token {tk.type} at line {tk.line}, can't parse as value"
            )

    def parse_type_definition(self) -> str:
        """
        Parse a type expression like:
           "str", "float", "dict{...}", "str | null" etc.
        For simplicity, we'll just parse tokens until we hit
        ',', '=', ']', '}', or the next high-level boundary.
        If we see '|', we'll add spaces around it => " | ".
        """
        parts = []
        while True:
            self.skip_whitespace()
            tk = self.current_token
            if tk.type in (TokenType.COMMA, TokenType.EQUAL,
                           TokenType.RBRACKET, TokenType.RBRACE,
                           TokenType.EOF):
                break
            elif tk.type == TokenType.PIPE:
                parts.append(" | ")
                self.advance()
            elif tk.type == TokenType.IDENTIFIER:
                parts.append(str(tk.value))
                self.advance()
            else:
                # If we encounter a token that isn’t allowed in a type expression,
                # break and let the next parser function handle it.
                break
        return "".join(parts)

    def skip_whitespace(self):
        while self.current_token.type in (TokenType.WHITESPACE, TokenType.NEWLINE):
            self.advance()

    def consume(self, expected: TokenType):
        """Consume one token of expected type, or raise an error."""
        self.skip_whitespace()
        if self.current_token.type != expected:
            raise FTMLParseError(
                f"Expected {expected}, got {self.current_token.type} at line {self.current_token.line}"
            )
        self.advance()
