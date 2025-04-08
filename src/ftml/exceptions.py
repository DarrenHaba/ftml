"""
FTML Exception Classes

This module defines all exception classes used in the FTML library.
"""


class FTMLError(Exception):
    """Base exception for all FTML-related errors."""

    pass


class FTMLParseError(FTMLError):
    """
    Raised when there is a syntax error in FTML.

    This includes malformed syntax, unclosed braces or brackets,
    invalid tokens, and other parsing-related errors.
    """

    pass


class FTMLValidationError(FTMLError):
    """
    Raised when FTML data fails to validate against a schema.

    This includes type mismatches, constraint violations, missing required
    fields, and other schema validation errors.
    """

    def __init__(self, message, errors=None, path=None):
        super().__init__(message)
        self.errors = errors or []
        self.path = path


class FTMLVersionError(FTMLError):
    """
    Raised when there is a version compatibility issue.

    This includes unsupported versions and invalid version formats.
    """

    pass


class FTMLEncodingError(FTMLError):
    """
    Raised when there is an encoding-related error.

    This includes unsupported encodings and encoding/decoding errors.
    """

    pass
