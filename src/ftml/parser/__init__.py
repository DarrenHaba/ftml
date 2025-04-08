"""
FTML Parser module

Contains components for parsing and serializing FTML data.
"""

from .parser import parse
from .serializer import serialize
from .ast import DocumentNode, KeyValueNode, ScalarNode, ObjectNode, ListNode, Comment, Node
from .tokenizer import Tokenizer, Token, TokenType

# Optional: Define what's exported when someone does "from ftml.parser import *"
__all__ = [
    "parse",
    "serialize",
    "DocumentNode",
    "KeyValueNode",
    "ScalarNode",
    "ObjectNode",
    "ListNode",
    "Comment",
    "Node",
    "Tokenizer",
    "Token",
    "TokenType",
]
