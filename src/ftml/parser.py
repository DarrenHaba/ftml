from typing import Union, Dict, List, Any

from ftml.exceptions import FTMLParseError
from ftml.tokenizer import Token, TokenType


class FTMLParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = None
        self.advance()

    def advance(self):
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
            self.pos += 1
        else:
            self.current_token = None

    def parse(self) -> Union[Dict, List]:
        if self.current_token is None:
            return {}

        # Handle top-level list
        if self.current_token.type == TokenType.LBRACKET:
            return self.parse_list()

        # Handle list of primitive values
        if self.current_token.type in (TokenType.STRING, TokenType.INTEGER,
                                       TokenType.FLOAT, TokenType.BOOLEAN, TokenType.NULL):
            return self.parse_top_level_list()

        return self.parse_dict()

    def parse_top_level_list(self) -> List:
        items = []
        while self.current_token:
            items.append(self.parse_value())
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
        return items

    def parse_dict(self) -> Dict:
        result = {}
        while self.current_token and self.current_token.type not in (TokenType.RBRACE, TokenType.RBRACKET):
            key = self.parse_key()

            # Check for duplicate keys
            if key in result:
                raise FTMLParseError(
                    f"Duplicate key '{key}' at line {self.current_token.line}"
                )

            # Handle schema type annotations
            if self.current_token and self.current_token.type == TokenType.COLON:
                self.advance()  # Consume colon
                type_def = self.parse_type_definition()

                # Create schema definition
                schema_def = {'type': type_def}

                # Handle optional fields
                if key.endswith('?'):
                    schema_def['optional'] = True
                    key = key.rstrip('?')

                # Handle default values
                if self.current_token and self.current_token.type == TokenType.EQUAL:
                    self.advance()
                    schema_def['default'] = self.parse_value()

                result[key] = schema_def
            else:
                self.consume(TokenType.EQUAL)
                value = self.parse_value()
                result[key] = value

            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()

        return result

    def parse_list(self) -> List:
        self.consume(TokenType.LBRACKET)
        items = []
        while self.current_token and self.current_token.type != TokenType.RBRACKET:
            items.append(self.parse_value())
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
        self.consume(TokenType.RBRACKET)
        return items

    def parse_value(self) -> Any:
        token = self.current_token
        if token.type == TokenType.LBRACE:
            self.advance()
            value = self.parse_dict()
            self.consume(TokenType.RBRACE)
            return value
        elif token.type == TokenType.LBRACKET:
            return self.parse_list()
        else:
            self.advance()
            return token.value

    def parse_key(self) -> str:
        if self.current_token.type in (TokenType.STRING, TokenType.IDENTIFIER):
            key = self.current_token.value
            self.advance()

            # Check for multiplicity symbols
            if self.current_token and self.current_token.type in (TokenType.QUESTION,
                                                                  TokenType.STAR,
                                                                  TokenType.PLUS):
                key += self.current_token.type.value
                self.advance()

            return key
        raise FTMLParseError(f"Invalid key type: {self.current_token.type}")

    def consume(self, expected_type: TokenType):
        if self.current_token and self.current_token.type == expected_type:
            self.advance()
        else:
            raise FTMLParseError(f"Expected {expected_type}, got {self.current_token.type if self.current_token else 'EOF'}")

    def parse_typed_key(self):
        key_token = self.current_token
        self.advance()  # Move past identifier/string
        self.consume(TokenType.COLON)
        type_tokens = []
        while self.current_token and self.current_token.type not in (TokenType.COMMA, TokenType.EQUAL, TokenType.RBRACE):
            type_tokens.append(str(self.current_token.value))
            self.advance()
        return key_token.value, ' '.join(type_tokens)

    def parse_type(self):
        type_tokens = []
        while self.current_token and self.current_token.type not in (TokenType.EQUAL, TokenType.COMMA, TokenType.PIPE):
            type_tokens.append(self.current_token.value)
            self.advance()
        return ' '.join(type_tokens)

    def parse_type_definition(self):
        type_parts = []
        while self.current_token and self.current_token.type not in (TokenType.COMMA,
                                                                     TokenType.EQUAL,
                                                                     TokenType.RBRACE):
            if self.current_token.value is not None:
                type_parts.append(str(self.current_token.value))
            self.advance()
        return ' '.join(type_parts) if type_parts else None

    def handle_type_annotation(self, key: str, value_type: str):
        # Store type information for schema validation
        pass

    def peek_next(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
