"""
FTML Encoding Module

Provides functions for handling FTML document encodings.
"""

from typing import Dict, Any
import codecs
import re

from ftml.logger import logger
from ftml.exceptions import FTMLEncodingError
from ftml.version import RESERVED_ENCODING_KEY

# Default encoding for FTML files
DEFAULT_ENCODING = "utf-8"

# Supported encodings
SUPPORTED_ENCODINGS = {
    "utf-8",
    "utf8",
    "latin-1",
    "latin1",
    "iso-8859-1",
    "ascii",
    "utf-16",
    "utf16",
    "utf-16-le",
    "utf-16-be",
}


def validate_encoding(data: Dict[str, Any]) -> str:
    """
    Validate the document encoding specification.

    Args:
        data: The parsed FTML data

    Returns:
        The validated encoding name

    Raises:
        FTMLEncodingError: If the encoding is invalid
    """
    # Extract encoding if present
    encoding = data.get(RESERVED_ENCODING_KEY, DEFAULT_ENCODING)

    # Validate encoding format
    if not isinstance(encoding, str):
        raise FTMLEncodingError(f"Invalid encoding: {encoding}. Encoding must be a string.")

    # Normalize encoding name
    encoding = encoding.lower().replace("_", "-")

    # Check if encoding is supported
    if encoding not in SUPPORTED_ENCODINGS:
        raise FTMLEncodingError(
            f"Unsupported encoding: {encoding}. " f"Supported encodings are: {', '.join(sorted(SUPPORTED_ENCODINGS))}"
        )

    # Check if encoding is recognized by Python
    try:
        codecs.lookup(encoding)
    except LookupError:
        raise FTMLEncodingError(f"Encoding not supported by Python: {encoding}")

    return encoding


def read_ftml_with_encoding(file_path: str, default_encoding: str = DEFAULT_ENCODING) -> str:
    """
    Read an FTML file with the correct encoding.

    This function attempts to detect the encoding from the file content
    by looking for the ftml_encoding key, or falls back to the default.

    Args:
        file_path: Path to the FTML file
        default_encoding: Default encoding to use if not specified in the file

    Returns:
        The file content as a string

    Raises:
        FTMLEncodingError: If there's an encoding-related error
    """
    # First try to read with default encoding to see if we can find an encoding specification
    try:
        with open(file_path, "r", encoding=default_encoding) as f:
            content = f.read()

        # Look for encoding specification
        encoding_match = re.search(r'ftml_encoding\s*=\s*["\']([^"\']+)["\']', content)

        if encoding_match:
            specified_encoding = encoding_match.group(1).lower().replace("_", "-")

            # If encoding differs from what we used, re-read the file
            if specified_encoding != default_encoding:
                logger.debug(f"Re-reading file with specified encoding: {specified_encoding}")

                # Validate the encoding
                if specified_encoding not in SUPPORTED_ENCODINGS:
                    raise FTMLEncodingError(
                        f"Unsupported encoding in file: {specified_encoding}. "
                        f"Supported encodings are: {', '.join(sorted(SUPPORTED_ENCODINGS))}"
                    )

                try:
                    with open(file_path, "r", encoding=specified_encoding) as f:
                        content = f.read()
                except UnicodeDecodeError as e:
                    raise FTMLEncodingError(
                        f"Error decoding file with specified encoding '{specified_encoding}': {str(e)}"
                    )
                except LookupError:
                    raise FTMLEncodingError(f"Encoding not supported by Python: {specified_encoding}")

        return content

    except UnicodeDecodeError as e:
        raise FTMLEncodingError(f"Error decoding file with default encoding '{default_encoding}': {str(e)}")
    except Exception as e:
        if not isinstance(e, FTMLEncodingError):
            raise FTMLEncodingError(f"Error reading file: {str(e)}")
        raise
