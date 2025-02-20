from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ftml.document import FTMLDocument
    from ftml.schema import FTMLSchema


def simplify_data(data):
    """
    Recursively simplify the parsed FTML AST into a plain dictionary,
    stripping out extra metadata.
    """
    if isinstance(data, dict):
        simple = {}
        for key, value in data.items():
            if isinstance(value, dict) and "type" in value:
                simple[key] = value.get("default", None)
            else:
                simple[key] = simplify_data(value)
        return simple
    elif isinstance(data, list):
        return [simplify_data(item) for item in data]
    else:
        return data


class FTMLData(dict):
    """
    A dict subclass that holds the simplified FTML data (as a dict) along with
    references to the full FTMLDocument and FTMLSchema objects.

    You can use the FTMLData instance as a normal dictionary and also access:
      - ftml_document: the original FTMLDocument instance (with methods like to_dict, to_ftml)
      - ftml_schema: the original FTMLSchema instance
    """
    def __init__(self, simple_data, ftml_document: FTMLDocument, ftml_schema: FTMLSchema = None):
        super().__init__(simple_data)
        self._ftml_document = ftml_document
        self._ftml_schema = ftml_schema

    @property
    def ftml_document(self) -> FTMLDocument:
        """Return the full FsTMLDocument instance."""
        return self._ftml_document

    @property
    def ftml_schema(self) -> FTMLSchema:
        """Return the full FTMLSchema instance (or None if not provided)."""
        return self._ftml_schema
