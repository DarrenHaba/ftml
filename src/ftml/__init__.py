"""
FTML (FlexTag Markup Language) - Public API

The main entry points are:
- load(...) -> parse FTML data into a Python structure, optionally validating it
- dump(...) -> serialize a Python structure (optionally with schema) into FTML

Exceptions:
- FTMLParseError
- ValidationError

Usage example in tests or user code:
    from ftml import load, dump, FTMLParseError, ValidationError
"""

import os
from typing import Optional, Union

# Import the low-level “core” functionality
from .ftml_core import (
    load as _core_load,
    dump as _core_dump,
)


# Todo move to a separate file
class FTMLParseError(Exception):
    """
    Raised when there is a parsing error in FTML syntax.
    E.g., unclosed braces, unquoted strings, or invalid characters.
    """
    pass


class FTMLValidationError(Exception):
    """
    Raised when data fails to validate against an FTML schema.
    """
    pass


def load(
        ftml_data: Union[str, os.PathLike],
        schema: Optional[Union[str, os.PathLike]] = None,
        validate: bool = True
):
    """
    High-level load function for FTML data.

    :param ftml_data: A string of FTML or a file path to FTML content.
    :param schema:    (Optional) A string or file path to an external schema.
                      If provided, it takes precedence over any embedded schema.
    :param validate:  Whether to validate the data. If True (default),
                      the function will parse and validate against:
                        1) The external schema (if given),
                        2) The internal/embedded schema (if present),
                      raising ValidationError on mismatch.
                      If False, no validation is performed.

    :return: A Python object (dict, list, scalar) or an FTMLData-like structure
             once you wrap it with advanced features.

    :raises FTMLParseError: If there is a syntax or parsing error in the data.
    :raises ValidationError: If there is a schema and the data fails validation.
    """
    # 1. If `ftml_data` is a file path, read its contents:
    if isinstance(ftml_data, (str, os.PathLike)) and os.path.exists(str(ftml_data)):
        with open(ftml_data, 'r', encoding='utf-8') as f:
            ftml_data = f.read()

    # 2. If `schema` is provided and is a file path, read its contents:
    external_schema_str = None
    if schema is not None:
        if isinstance(schema, (str, os.PathLike)) and os.path.exists(str(schema)):
            with open(schema, 'r', encoding='utf-8') as f:
                external_schema_str = f.read()
        else:
            external_schema_str = schema  # Already a string

    # 3. Wrap the core parsing in a try/except to raise FTMLParseError on any parse error
    try:
        result = _core_load(ftml_data)  # parse data into python structure
    except Exception as e:
        # If it looks like a parse error from your core parser, re-raise as FTMLParseError
        raise FTMLParseError(str(e)) from e

    # 4. If validate is True, do your “validate against external schema => internal schema” logic
    if validate:
        # ... parse external_schema_str if present
        # ... check for embedded schema in `result` if relevant
        # ... call your real validator
        # If invalid, raise ValidationError(...).
        pass

    # 5. Return final object (for now, just the dict)
    return result


def dump(
        data,
        schema: Optional[Union[str, os.PathLike]] = None,
        validate: bool = True
):
    """
    High-level dump function to serialize Python data to FTML.

    :param data:      A Python object (dict, list, etc.) to be serialized.
    :param schema:    (Optional) A string or file path to an external schema.
                      If present, we can validate 'data' against it before dumping.
                      Also if the data has an embedded schema, we might unify or overwrite it.
    :param validate:  Whether to validate the data before dumping. Default True.

    :return: A string of FTML.

    :raises ValidationError: If validation is enabled and data fails the schema check.
    :raises FTMLParseError: Rarely used here, but could arise if your code tries to parse
                            or re-parse during dump. In general, only for completeness.
    """
    # Optional: If you want to unify external schema with embedded schema, do it here.
    # If validate == True, do a final validation pass before generating the FTML string.
    if validate and schema is not None:
        # ... parse the external schema
        # ... validate
        pass

    # 1) Hand off to your core dumper:
    try:
        ftml_str = _core_dump(data)
    except Exception as e:
        # If your dumper can throw parse-like errors or others, re-raise accordingly.
        raise FTMLParseError(str(e)) from e

    # 2) Possibly embed the schema into the FTML output if we want an “inline schema”.
    #    For now, we skip that. You’ll add it once the internal schema is standardized.

    return ftml_str


# We can optionally keep them in __all__ for clarity
__all__ = [
    "load",
    "dump",
    "FTMLParseError",
    "FTMLValidationError",
]
