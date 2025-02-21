import unittest
from typing import List

from ftml.parser import TokenType, Token, FTMLParser, FTMLParseError


def create_tokens(values: List[tuple], start_line=1):
    """
    Helper function to create tokens for testing.
    Each `values` element is (TokenType, token_value).
    If TokenType is NEWLINE, we increment the line but don't emit a token.
    """
    result = []
    current_line = start_line
    for ttype, val in values:
        if ttype == TokenType.NEWLINE:
            current_line += 1
            continue
        result.append(Token(ttype, val, line=current_line, col=1))
    return result


class TestFTMLParser(unittest.TestCase):

    def test_parse_empty_dict(self):
        """
        Top-level empty dict: {}
        Expected: an empty Python dict
        """
        tokens = create_tokens([
            (TokenType.LBRACE, "{"),
            (TokenType.RBRACE, "}"),
        ])
        parser = FTMLParser(tokens)
        result = parser.parse()
        self.assertEqual(result, {}, "Empty dict should parse to {}")

    def test_parse_empty_list(self):
        """
        Top-level empty list: []
        Expected: an empty Python list
        """
        tokens = create_tokens([
            (TokenType.LBRACKET, "["),
            (TokenType.RBRACKET, "]"),
        ])
        parser = FTMLParser(tokens)
        result = parser.parse()
        self.assertEqual(result, [], "Empty list should parse to []")

    def test_dict_typed_field(self):
        """
        {
          name: str = "Alice"
        }
        => {
          "name": { "type": "str", "optional": False, "value": "Alice" }
        }
        """
        tokens = create_tokens([
            (TokenType.LBRACE, "{"),

            # name: str = "Alice"
            (TokenType.IDENTIFIER, "name"),
            (TokenType.COLON, ":"),
            (TokenType.IDENTIFIER, "str"),
            (TokenType.EQUAL, "="),
            (TokenType.STRING, "Alice"),

            (TokenType.RBRACE, "}"),
        ])
        parser = FTMLParser(tokens)
        data = parser.parse()

        self.assertIsInstance(data, dict)
        self.assertIn("name", data)
        self.assertIsInstance(data["name"], dict)
        self.assertEqual(data["name"]["type"], "str")
        self.assertFalse(data["name"]["optional"])
        self.assertEqual(data["name"]["value"], "Alice")

    def test_dict_optional_field(self):
        """
        {
          name?: str = "Alice"
        }
        => {
          "name": { "type": "str", "optional": True, "value": "Alice" }
        }
        """
        tokens = create_tokens([
            (TokenType.LBRACE, "{"),

            (TokenType.IDENTIFIER, "name?"),  # means optional
            (TokenType.COLON, ":"),
            (TokenType.IDENTIFIER, "str"),
            (TokenType.EQUAL, "="),
            (TokenType.STRING, "Alice"),

            (TokenType.RBRACE, "}"),
        ])
        parser = FTMLParser(tokens)
        data = parser.parse()

        self.assertIn("name", data)
        field = data["name"]
        self.assertEqual(field["type"], "str")
        self.assertTrue(field["optional"])
        self.assertEqual(field["value"], "Alice")

    def test_dict_untyped_field(self):
        """
        {
          age = 42
        }
        => { "age": 42 }  (untyped => direct literal)
        """
        tokens = create_tokens([
            (TokenType.LBRACE, "{"),
            (TokenType.IDENTIFIER, "age"),
            (TokenType.EQUAL, "="),
            (TokenType.INTEGER, 42),
            (TokenType.RBRACE, "}"),
        ])
        parser = FTMLParser(tokens)
        data = parser.parse()
        self.assertEqual(data, {"age": 42})

    def test_list_typed_items(self):
        """
        [
          :str "Apple",
          :float 10.5,
          "Untyped"
        ]
        => [
          {"type": "str", "value": "Apple"},
          {"type": "float", "value": 10.5},
          "Untyped"
        ]
        """
        tokens = create_tokens([
            (TokenType.LBRACKET, "["),

            # :str "Apple"
            (TokenType.COLON, ":"),
            (TokenType.IDENTIFIER, "str"),
            (TokenType.STRING, "Apple"),
            (TokenType.COMMA, ","),

            # :float 10.5
            (TokenType.COLON, ":"),
            (TokenType.IDENTIFIER, "float"),
            (TokenType.FLOAT, 10.5),
            (TokenType.COMMA, ","),

            # "Untyped"
            (TokenType.STRING, "Untyped"),

            (TokenType.RBRACKET, "]"),
        ])
        parser = FTMLParser(tokens)
        data = parser.parse()

        self.assertEqual(len(data), 3)
        self.assertEqual(data[0], {"type": "str", "value": "Apple"})
        self.assertEqual(data[1], {"type": "float", "value": 10.5})
        self.assertEqual(data[2], "Untyped")

    def test_union_type_field(self):
        """
        {
          status: str | null = "active"
        }
        => {
          "status": {
            "type": "str | null",
            "optional": False,
            "value": "active"
          }
        }
        """
        tokens = create_tokens([
            (TokenType.LBRACE, "{"),

            (TokenType.IDENTIFIER, "status"),
            (TokenType.COLON, ":"),
            (TokenType.IDENTIFIER, "str"),
            (TokenType.PIPE, "|"),
            (TokenType.IDENTIFIER, "null"),
            (TokenType.EQUAL, "="),
            (TokenType.STRING, "active"),

            (TokenType.RBRACE, "}"),
        ])
        parser = FTMLParser(tokens)
        data = parser.parse()

        self.assertIn("status", data)
        field = data["status"]
        self.assertEqual(field["type"], "str | null")
        self.assertFalse(field["optional"])
        self.assertEqual(field["value"], "active")

    def test_nested_dict_in_list(self):
        """
        [
          { name: str = "Alice" },
          :int 100
        ]
        => [
          {
            "name": { "type": "str", "optional": False, "value": "Alice" }
          },
          {"type": "int", "value": 100}
        ]
        """
        tokens = create_tokens([
            (TokenType.LBRACKET, "["),

            # { name: str = "Alice" }
            (TokenType.LBRACE, "{"),
            (TokenType.IDENTIFIER, "name"),
            (TokenType.COLON, ":"),
            (TokenType.IDENTIFIER, "str"),
            (TokenType.EQUAL, "="),
            (TokenType.STRING, "Alice"),
            (TokenType.RBRACE, "}"),
            (TokenType.COMMA, ","),

            # :int 100
            (TokenType.COLON, ":"),
            (TokenType.IDENTIFIER, "int"),
            (TokenType.INTEGER, 100),

            (TokenType.RBRACKET, "]"),
        ])
        parser = FTMLParser(tokens)
        data = parser.parse()

        self.assertEqual(len(data), 2)
        # First item is a dict with "name"
        self.assertIsInstance(data[0], dict)
        self.assertIn("name", data[0])
        self.assertEqual(data[0]["name"]["type"], "str")
        self.assertEqual(data[0]["name"]["value"], "Alice")

        # Second item is typed :int
        self.assertEqual(data[1], {"type": "int", "value": 100})

    def test_nested_list_in_dict(self):
        """
        {
          items = [ "foo", :str "bar" ]
        }
        => {
          "items": [ "foo", {"type": "str", "value": "bar"} ]
        }
        """
        tokens = create_tokens([
            (TokenType.LBRACE, "{"),

            # items = [ "foo", :str "bar" ]
            (TokenType.IDENTIFIER, "items"),
            (TokenType.EQUAL, "="),
            (TokenType.LBRACKET, "["),

            (TokenType.STRING, "foo"),
            (TokenType.COMMA, ","),
            (TokenType.COLON, ":"),
            (TokenType.IDENTIFIER, "str"),
            (TokenType.STRING, "bar"),

            (TokenType.RBRACKET, "]"),

            (TokenType.RBRACE, "}"),
        ])
        parser = FTMLParser(tokens)
        data = parser.parse()

        self.assertIn("items", data)
        items_val = data["items"]
        self.assertIsInstance(items_val, list)
        self.assertEqual(items_val[0], "foo")
        self.assertEqual(items_val[1], {"type": "str", "value": "bar"})

    def test_missing_brace_error(self):
        """
        Attempt parse: { name = 123
        Missing closing brace => should raise FTMLParseError
        """
        tokens = create_tokens([
            (TokenType.LBRACE, "{"),
            (TokenType.IDENTIFIER, "name"),
            (TokenType.EQUAL, "="),
            (TokenType.INTEGER, 123),
            # no RBRACE
        ])
        parser = FTMLParser(tokens)
        with self.assertRaises(FTMLParseError):
            parser.parse()

    def test_missing_bracket_error(self):
        """
        Attempt parse: [ :str "abc"
        Missing closing bracket => should raise FTMLParseError
        """
        tokens = create_tokens([
            (TokenType.LBRACKET, "["),
            (TokenType.COLON, ":"),
            (TokenType.IDENTIFIER, "str"),
            (TokenType.STRING, "abc"),
            # no RBRACKET
        ])
        parser = FTMLParser(tokens)
        with self.assertRaises(FTMLParseError):
            parser.parse()


if __name__ == '__main__':
    unittest.main(verbosity=2)
