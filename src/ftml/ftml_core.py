# ftml_core.py
# Next iteration: rename dict -> object, allow top-level scalar.

import re
import enum
from typing import List, Optional, Union, Any, Dict


###############################################################################
# 1) Token Types and Tokenizer (Lexer)
###############################################################################

class TokenType(enum.Enum):
    COMMENT = "COMMENT"
    STRING = "STRING"
    SINGLE_STRING = "SINGLE_STRING"
    INT = "INT"
    FLOAT = "FLOAT"
    BOOL = "BOOL"
    NULL = "NULL"
    IDENT = "IDENT"  # e.g. name, user, etc.
    LBRACE = "{"  # {
    RBRACE = "}"  # }
    LBRACKET = "["  # [
    RBRACKET = "]"  # ]
    EQUAL = "="  # =
    COMMA = ","  # ,
    COLON = ":"  # :
    NEWLINE = "NEWLINE"  # \n
    WHITESPACE = "WHITESPACE"
    EOF = "EOF"


class Token:
    __slots__ = ("type", "value", "line", "col")

    def __init__(self, ttype: TokenType, value: Any, line: int, col: int):
        self.type = ttype
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line}, col={self.col})"


class FTMLTokenizer:
    """
    Produces tokens from raw FTML text. Preserves line comments as separate tokens.
    """

    TOKEN_REGEX = [
        (TokenType.COMMENT, r'#[^\n]*'),
        (TokenType.STRING, r'"(?:\\.|[^"\\])*"'),
        (TokenType.SINGLE_STRING, r"'(?:''|[^'])*'"),
        (TokenType.FLOAT, r'[+-]?\d+\.\d+'),
        (TokenType.INT, r'[+-]?\d+'),
        (TokenType.BOOL, r'\b(true|false)\b'),
        (TokenType.NULL, r'\bnull\b'),
        (TokenType.LBRACE, r'\{'),
        (TokenType.RBRACE, r'\}'),
        (TokenType.LBRACKET, r'\['),
        (TokenType.RBRACKET, r'\]'),
        (TokenType.EQUAL, r'='),
        (TokenType.COMMA, r','),
        (TokenType.COLON, r':'),
        (TokenType.IDENT, r'[A-Za-z_][A-Za-z0-9_]*'),
        (TokenType.WHITESPACE, r'[ \t\r]+'),
        (TokenType.NEWLINE, r'\n'),
    ]

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.patterns = []
        for ttype, pattern in self.TOKEN_REGEX:
            self.patterns.append((ttype, re.compile(pattern)))

    def _match(self):
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
        self.line += 1
        self.col = 1

    def next_token(self) -> Token:
        if self.pos >= len(self.text):
            return Token(TokenType.EOF, None, self.line, self.col)

        result = self._match()
        if not result:
            raise ValueError(
                f"Lex error at line {self.line}, col {self.col}: "
                f"unrecognized text {self.text[self.pos:self.pos + 10]!r}"
            )
        ttype, match = result
        token_str = match.group()
        start_line, start_col = self.line, self.col

        self.pos = match.end()
        for ch in token_str:
            if ch == '\n':
                self._advance_line()
            else:
                self.col += 1

        if ttype == TokenType.SINGLE_STRING:
            # single-quoted text
            value = self._interpret_single_quoted(token_str)
        elif ttype == TokenType.STRING:
            value = self._interpret_double_quoted(token_str)
        elif ttype == TokenType.INT:
            value = int(token_str)
        elif ttype == TokenType.FLOAT:
            value = float(token_str)
        elif ttype == TokenType.BOOL:
            value = (token_str.lower() == "true")
        elif ttype == TokenType.NULL:
            value = None
        else:
            value = token_str

        return Token(ttype, value, start_line, start_col)

    def _interpret_single_quoted(self, raw: str) -> str:
        # raw includes the leading and trailing single quotes.
        # E.g. "'It''s a test'"
        inner = raw[1:-1]  # remove outer single quotes
        # per YAML/TOML, we double single quotes to escape => '' => '
        return inner.replace("''", "'")

    def _interpret_double_quoted(self, raw: str) -> str:
        inner = raw[1:-1]  # remove outer quotes
        # interpret \n, \t, etc. as actual escapes
        return (inner
                .replace(r'\"', '"')
                .replace(r'\\', '\\')
                .replace(r'\n', '\n')
                .replace(r'\t', '\t')
                )

    def tokenize(self) -> List[Token]:
        tokens = []
        while True:
            tk = self.next_token()
            if tk.type == TokenType.EOF:
                tokens.append(tk)
                break
            if tk.type != TokenType.WHITESPACE:
                tokens.append(tk)
        return tokens


###############################################################################
# 2) AST Node Definitions
###############################################################################

class Node:
    def __init__(self):
        self.leading_comments: List[str] = []
        self.inline_comment: Optional[str] = None
        self.trailing_comments: List[str] = []


class ScalarNode(Node):
    """
    Represents a primitive (string, int, float, bool, null).
    """

    def __init__(self, value: Any):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"<ScalarNode value={self.value!r}>"


class KeyValueNode(Node):
    """
    Represents one "key = value" pair inside an object.
    """

    def __init__(self, key: str, value_node: Node):
        super().__init__()
        self.key = key
        self.value_node = value_node

    def __repr__(self):
        return f"<KeyValueNode {self.key}={self.value_node}>"


class ObjectNode(Node):
    """
    Previously DictNode. Now it's an "object" in FTML with { ... } syntax.
    """

    def __init__(self):
        super().__init__()
        self.items: List[KeyValueNode] = []

    def __repr__(self):
        return f"<ObjectNode items={self.items}>"


class ListNode(Node):
    """
    Represents a list: [value1, value2, ...].
    """

    def __init__(self):
        super().__init__()
        self.elements: List[Node] = []

    def __repr__(self):
        return f"<ListNode elements={self.elements}>"


class DocumentNode(Node):
    """
    Top-level node for an FTML document. Data can be an ObjectNode, ListNode, or ScalarNode.
    """

    def __init__(self):
        super().__init__()
        self.data: Optional[Node] = None


###############################################################################
# 3) Parser
###############################################################################

class ParserError(Exception):
    pass


class FTMLParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, None, -1, -1)

    def advance(self) -> Token:
        t = self.peek()
        self.pos += 1
        return t

    def parse_document(self) -> DocumentNode:
        doc = DocumentNode()
        # parse data (could be object, list, or scalar)
        doc.data = self.parse_value()
        return doc

    def parse_value(self) -> Node:
        tk = self.peek()
        if tk.type == TokenType.LBRACE:
            return self.parse_object()
        elif tk.type == TokenType.LBRACKET:
            return self.parse_list()
        elif tk.type in (
                TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.SINGLE_STRING,
                TokenType.BOOL, TokenType.NULL, TokenType.IDENT, TokenType.COMMENT
        ):
            return self.parse_scalar()
        else:
            # Could be empty or unknown
            raise ParserError(f"Unexpected token {tk} in parse_value()")

    def parse_object(self) -> ObjectNode:
        self.advance()  # consume '{'
        node = ObjectNode()

        while True:
            self._skip_nonsemantic()
            tk = self.peek()
            if tk.type == TokenType.RBRACE:
                self.advance()  # consume '}'
                return node
            if tk.type == TokenType.EOF:
                raise ParserError("Unclosed '{' - reached EOF")

            kv = self.parse_key_value()
            node.items.append(kv)

            self._skip_nonsemantic()
            if self.peek().type == TokenType.COMMA:
                self.advance()
            else:
                # next should be '}' or error
                continue

    def parse_key_value(self) -> KeyValueNode:
        # expect key (IDENT or STRING)
        tk = self.peek()
        if tk.type not in (TokenType.IDENT, TokenType.STRING):
            raise ParserError(f"Expected identifier or quoted key, got {tk}")
        key_token = self.advance()
        key_str = str(key_token.value)

        self._skip_nonsemantic()

        # expect '='
        eq = self.peek()
        if eq.type != TokenType.EQUAL:
            raise ParserError(f"Expected '=' after key '{key_str}', got {eq}")
        self.advance()

        self._skip_nonsemantic()

        value_node = self.parse_value()
        kv_node = KeyValueNode(key_str, value_node)
        self._maybe_gather_inline_comment(kv_node)

        return kv_node

    def parse_list(self) -> ListNode:
        self.advance()  # consume '['
        node = ListNode()

        while True:
            self._skip_nonsemantic()
            tk = self.peek()
            if tk.type == TokenType.RBRACKET:
                self.advance()  # consume ']'
                return node
            if tk.type == TokenType.EOF:
                raise ParserError("Unclosed '[' - reached EOF")

            elem = self.parse_value()
            node.elements.append(elem)

            self._skip_nonsemantic()
            if self.peek().type == TokenType.COMMA:
                self.advance()
            else:
                continue

    def parse_scalar(self) -> ScalarNode:
        tk = self.peek()
        # handle comment tokens if we decide they appear here
        if tk.type == TokenType.COMMENT:
            # For now, skip them and parse again
            comment_val = tk.value.lstrip('#').strip()
            self.advance()
            # parse the next real scalar
            scalar = self.parse_scalar()
            scalar.leading_comments.insert(0, comment_val)
            return scalar

        self.advance()  # consume
        if tk.type in (TokenType.STRING, TokenType.SINGLE_STRING):
            return ScalarNode(tk.value)
        elif tk.type == TokenType.INT:
            return ScalarNode(tk.value)
        elif tk.type == TokenType.FLOAT:
            return ScalarNode(tk.value)
        elif tk.type == TokenType.BOOL:
            return ScalarNode(tk.value)
        elif tk.type == TokenType.NULL:
            return ScalarNode(None)
        elif tk.type == TokenType.IDENT:
            # Unquoted string => error or handle specially
            raise ParserError(f"Unquoted string or unknown token '{tk.value}' at line {tk.line}")
        else:
            raise ParserError(f"Unexpected token {tk} in parse_scalar()")

    def _skip_nonsemantic(self):
        while True:
            tk = self.peek()
            if tk.type in (TokenType.NEWLINE, TokenType.WHITESPACE):
                self.advance()
            elif tk.type == TokenType.COMMENT:
                # we skip it or attach to next node
                self.advance()
            else:
                break

    def _maybe_gather_inline_comment(self, node: Node):
        tk = self.peek()
        if tk.type == TokenType.COMMENT:
            comment_val = tk.value.lstrip('#').strip()
            node.inline_comment = comment_val
            self.advance()


###############################################################################
# 4) Converting the AST to a Python Data Structure
###############################################################################

def ast_to_data(node: Node) -> Any:
    if isinstance(node, ScalarNode):
        return node.value
    elif isinstance(node, ObjectNode):
        out = {}
        for kv in node.items:
            out[kv.key] = ast_to_data(kv.value_node)
        return out
    elif isinstance(node, ListNode):
        return [ast_to_data(e) for e in node.elements]
    elif isinstance(node, DocumentNode):
        return ast_to_data(node.data) if node.data else None
    else:
        return None


###############################################################################
# 5) Serializer (Dump) - Minimal changes (still says { }, rename to object in schema later)
###############################################################################

def data_to_ast(data: Any) -> Node:
    if isinstance(data, dict):
        node = ObjectNode()
        for k, v in data.items():
            val_node = data_to_ast(v)
            kvn = KeyValueNode(str(k), val_node)
            node.items.append(kvn)
        return node
    elif isinstance(data, list):
        node = ListNode()
        for item in data:
            node.elements.append(data_to_ast(item))
        return node
    else:
        return ScalarNode(data)


def serialize_ast(node: Node, indent: int = 0) -> str:
    if isinstance(node, ScalarNode):
        return _scalar_to_str(node.value)
    elif isinstance(node, ObjectNode):
        lines = []
        lines.append("{")
        for kv in node.items:
            line = f"  {kv.key} = {serialize_ast(kv.value_node, indent + 2)},"
            lines.append(line)
        lines.append("}")
        return "\n".join(lines)
    elif isinstance(node, ListNode):
        if not node.elements:
            return "[]"
        lines = ["["]
        for e in node.elements:
            lines.append(f"  {serialize_ast(e, indent + 2)},")
        lines.append("]")
        return "\n".join(lines)
    elif isinstance(node, DocumentNode):
        if node.data:
            return serialize_ast(node.data, indent)
        else:
            return ""
    else:
        return ""


def _scalar_to_str(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        escaped = value.replace('"', '\\"')
        return f"\"{escaped}\""
    return str(value)


###############################################################################
# 6) Public load/dump entry points (MINIMAL)
###############################################################################

def load(ftml_text: str) -> Any:
    lexer = FTMLTokenizer(ftml_text)
    tokens = lexer.tokenize()
    parser = FTMLParser(tokens)
    try:
        doc_node = parser.parse_document()
    except ParserError as e:
        # Just re-raise for now. In your higher-level code, you'd catch and raise FTMLParseError
        raise e
    data = ast_to_data(doc_node)
    # If top-level is a scalar, we just return that scalar as is.
    return data


def dump(data: Any) -> str:
    node = data_to_ast(data)
    return serialize_ast(node)
