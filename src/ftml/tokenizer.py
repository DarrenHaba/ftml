import re
from enum import Enum
from dataclasses import dataclass

from ftml.exceptions import FTMLParseError


class TokenType(Enum):
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    EQUAL = "="
    COMMA = ","
    COLON = ":"
    PIPE = "|"
    QUESTION = "?"
    PLUS = "+"
    STAR = "*"
    COMMENT = "COMMENT"


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


class FTMLTokenizer:
    _token_specs = [
        (TokenType.STRING, r'"(?:[^"\\]|\\.)*"'),
        (TokenType.COMMENT, r'#.*'),
        (TokenType.FLOAT, r'-?\d+\.\d+'),
        (TokenType.INTEGER, r'-?\d+'),
        (TokenType.BOOLEAN, r'true|false'),
        (TokenType.NULL, r'null'),
        (TokenType.LBRACE, r'{'),
        (TokenType.RBRACE, r'}'),
        (TokenType.LBRACKET, r'\['),
        (TokenType.RBRACKET, r'\]'),
        (TokenType.EQUAL, r'='),
        (TokenType.COMMA, r','),
        (TokenType.COLON, r':'),
        (TokenType.PIPE, r'\|'),
        (TokenType.QUESTION, r'\?'),
        (TokenType.PLUS, r'\+'),
        (TokenType.STAR, r'\*'),
        (TokenType.IDENTIFIER, r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ]

    def __init__(self, input_str: str):
        self.input = input_str
        self.pos = 0
        self.line = 1
        self.col = 1

    def _next_token(self):
        while self.pos < len(self.input):
            if self.input[self.pos].isspace():
                if self.input[self.pos] == '\n':
                    self.line += 1
                    self.col = 1
                else:
                    self.col += 1
                self.pos += 1
                continue

            for token_type, pattern in self._token_specs:
                regex = re.compile(pattern)
                match = regex.match(self.input, self.pos)
                if match:
                    value = match.group()
                    start_col = self.col
                    self.col += match.end() - match.start()
                    self.pos = match.end()

                    if token_type == TokenType.STRING:
                        value = value[1:-1].replace('\\"', '"')
                    elif token_type == TokenType.BOOLEAN:
                        value = value.lower() == 'true'
                    elif token_type == TokenType.INTEGER:
                        value = int(value)
                    elif token_type == TokenType.FLOAT:
                        value = float(value)
                    elif token_type == TokenType.NULL:
                        value = None

                    return Token(token_type, value, self.line, start_col)

            raise FTMLParseError(f"Unexpected character '{self.input[self.pos]}' at {self.line}:{self.col}")

        return None

    def tokenize(self):
        tokens = []
        while True:
            token = self._next_token()
            if token is None:
                break
            if token.type != TokenType.COMMENT:
                tokens.append(token)
        return tokens
