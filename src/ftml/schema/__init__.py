"""
FTML Schema module

Contains components for schema definition, parsing, and validation.
"""

# Everything else below this doesn't work:
from .schema_parser import SchemaParser
from .schema_validator import SchemaValidator, validate_schema, apply_defaults
from .schema_ast import SchemaTypeNode, ScalarTypeNode, UnionTypeNode, ListTypeNode, ObjectTypeNode
from .schema_type_system import TypeSystem
from .schema_type_validators import (
    TypeValidator,
    ScalarValidator,
    UnionValidator,
    ListValidator,
    ObjectValidator,
    create_validator_for_type,
)

# Optional: Define what's exported when someone does "from ftml.schema import *"
__all__ = [
    # Core schema components
    "SchemaParser",
    "SchemaValidator",
    "validate_schema",
    "apply_defaults",
    # Schema AST nodes
    "SchemaTypeNode",
    "ScalarTypeNode",
    "UnionTypeNode",
    "ListTypeNode",
    "ObjectTypeNode",
    # Type system
    "TypeSystem",
    # Validators
    "TypeValidator",
    "ScalarValidator",
    "UnionValidator",
    "ListValidator",
    "ObjectValidator",
    "create_validator_for_type",
]
