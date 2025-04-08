"""
FTML Schema AST Module

Defines the Abstract Syntax Tree nodes specific to schema definitions.
This is separate from the data AST to keep concerns separated.
"""

from typing import Dict, List, Any, Optional


class SchemaTypeNode:
    """Base class for all schema type nodes."""

    def __init__(self):
        """Initialize base schema type node."""
        self.constraints: Dict[str, Any] = {}
        self.has_default: bool = False
        self.default: Any = None
        self.optional: bool = False

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<{self.__class__.__name__}>"


class ScalarTypeNode(SchemaTypeNode):
    """
    Represents a scalar type (str, int, float, bool, null, any, etc.).

    Attributes:
        type_name: The name of the scalar type
        constraints: Dictionary of constraints for this type
    """

    def __init__(self, type_name: str):
        """
        Initialize a scalar type node.

        Args:
            type_name: The name of the scalar type (str, int, float, bool, null, any, etc.)
        """
        super().__init__()
        self.type_name = type_name

    def __repr__(self) -> str:
        """String representation for debugging."""
        constraint_str = ""
        if self.constraints:
            constraint_str = f", constraints={self.constraints}"

        default_str = ""
        if self.has_default:
            default_str = f", default={repr(self.default)}"

        optional_str = ", optional=True" if self.optional else ""

        return f"<{self.__class__.__name__} {self.type_name}{constraint_str}{default_str}{optional_str}>"


class UnionTypeNode(SchemaTypeNode):
    """
    Represents a union type (type1 | type2 | ...).

    Attributes:
        subtypes: List of SchemaTypeNode instances representing the component types
    """

    def __init__(self):
        """Initialize a union type node."""
        super().__init__()
        self.subtypes: List[SchemaTypeNode] = []

    def __repr__(self) -> str:
        """String representation for debugging."""
        subtypes_str = ", ".join(repr(t) for t in self.subtypes)
        default_str = f", default={repr(self.default)}" if self.has_default else ""
        optional_str = ", optional=True" if self.optional else ""

        return f"<{self.__class__.__name__} subtypes=[{subtypes_str}]{default_str}{optional_str}>"


class ListTypeNode(SchemaTypeNode):
    """
    Represents a list type ([item_type]).

    Attributes:
        item_type: The SchemaTypeNode representing the type of items in the list
    """

    def __init__(self):
        """Initialize a list type node."""
        super().__init__()
        self.item_type: Optional[SchemaTypeNode] = None

    def __repr__(self) -> str:
        """String representation for debugging."""
        item_str = repr(self.item_type) if self.item_type else "any"
        constraint_str = f", constraints={self.constraints}" if self.constraints else ""
        default_str = f", default={repr(self.default)}" if self.has_default else ""
        optional_str = ", optional=True" if self.optional else ""

        return f"<{self.__class__.__name__} item_type={item_str}{constraint_str}{default_str}{optional_str}>"


class ObjectTypeNode(SchemaTypeNode):
    """
    Represents an object type ({field1: type1, ...}).

    Attributes:
        fields: Dictionary mapping field names to their SchemaTypeNode
        pattern_value_type: Optional SchemaTypeNode for pattern properties (e.g., {str: type})
        ext: Whether to allow extension with additional properties not in fields
    """

    def __init__(self):
        """Initialize an object type node."""
        super().__init__()
        self.fields: Dict[str, SchemaTypeNode] = {}
        self.pattern_value_type: Optional[SchemaTypeNode] = None
        self.ext: bool = False  # Default to false - no extension

    def __repr__(self) -> str:
        """String representation for debugging."""
        if self.pattern_value_type:
            pattern_str = f", pattern_value_type={repr(self.pattern_value_type)}"
            constraint_str = f", constraints={self.constraints}" if self.constraints else ""
            default_str = f", default={repr(self.default)}" if self.has_default else ""
            optional_str = ", optional=True" if self.optional else ""
            ext_str = ", ext=True" if self.ext else ""

            return f"<{self.__class__.__name__}{pattern_str}{constraint_str}{default_str}{optional_str}{ext_str}>"
        else:
            fields_str = ", ".join(f"{k}: {repr(v)}" for k, v in self.fields.items())
            constraint_str = f", constraints={self.constraints}" if self.constraints else ""
            default_str = f", default={repr(self.default)}" if self.has_default else ""
            optional_str = ", optional=True" if self.optional else ""
            ext_str = ", ext=True" if self.ext else ""

            return (f"<{self.__class__.__name__} "
                    f"fields={{{fields_str}}}{constraint_str}{default_str}{optional_str}{ext_str}>")
