"""
FTML Version Handling Module

Provides functions for checking and validating FTML version compatibility.
"""

import re
from typing import Dict, Any, Optional, Tuple
from .exceptions import FTMLVersionError
from .logger import logger

# Reserved keys for FTML metadata
RESERVED_VERSION_KEY = "ftml_version"
RESERVED_ENCODING_KEY = "ftml_encoding"

# Regular expression for version parsing
VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)(?:(a|b|rc)(\d+))?$")


def validate_version(data: Dict[str, Any], parser_version: str) -> None:
    """
    Validate that the document version is compatible with the parser version.

    Args:
        data: The parsed FTML data
        parser_version: The version of the parser

    Raises:
        FTMLVersionError: If the document version is not compatible
    """
    # Extract document version if present
    doc_version = data.get(RESERVED_VERSION_KEY)

    if doc_version is None:
        # No version specified, assume compatible
        logger.debug("No FTML version specified in document, assuming compatible")
        return

    # Validate version format
    if not isinstance(doc_version, str):
        raise FTMLVersionError(f"Invalid FTML version: {doc_version}. Version must be a string.")

    # Check compatibility
    try:
        doc_version_info = _parse_version(doc_version)
        parser_version_info = _parse_version(parser_version)

        # Compare versions
        if _is_compatible(doc_version_info, parser_version_info):
            logger.debug(f"Document version {doc_version} is compatible with parser version {parser_version}")
            return

        # If we get here, it's an incompatible version
        raise FTMLVersionError(
            f"Document requires FTML version {doc_version}, but parser only supports up to {parser_version}. "
            "Please update your parser."
        )

    except ValueError:
        raise FTMLVersionError(
            f"Invalid FTML version format: {doc_version}. "
            "Expected format is 'MAJOR.MINOR' or 'MAJOR.MINOR(a|b|rc)NUMBER' (e.g., '1.0', '1.0a1', '1.0b2', '1.0rc1')."
        )


def _parse_version(version: str) -> Tuple[int, int, Optional[str], Optional[int]]:
    """
    Parse a version string into components.

    Args:
        version: Version string in the format 'MAJOR.MINOR' or 'MAJOR.MINOR(a|b|rc)NUMBER'

    Returns:
        Tuple of (major, minor, stage, stage_version)
        where stage is None for release versions or 'a', 'b', 'rc' for pre-release versions

    Raises:
        ValueError: If the version string is not in the expected format
    """
    match = VERSION_PATTERN.match(version)
    if not match:
        raise ValueError(
            f"Invalid version format: {version}. " "Expected format is 'MAJOR.MINOR' or 'MAJOR.MINOR(a|b|rc)NUMBER'"
        )

    major = int(match.group(1))
    minor = int(match.group(2))

    # Stage and stage version may be None for release versions
    stage = match.group(3)
    stage_version = int(match.group(4)) if match.group(4) else None

    return (major, minor, stage, stage_version)


def _is_compatible(doc_version_info: Tuple, parser_version_info: Tuple) -> bool:
    """
    Check if document version is compatible with parser version.

    Args:
        doc_version_info: Document version tuple from _parse_version
        parser_version_info: Parser version tuple from _parse_version

    Returns:
        True if compatible, False otherwise
    """
    doc_major, doc_minor, doc_stage, doc_stage_ver = doc_version_info
    parser_major, parser_minor, parser_stage, parser_stage_ver = parser_version_info

    # If document major is lower, it's compatible
    if doc_major < parser_major:
        return True

    # If document major is higher, it's incompatible
    if doc_major > parser_major:
        return False

    # Same major version, check minor
    if doc_minor < parser_minor:
        return True

    if doc_minor > parser_minor:
        return False

    # Same major and minor, check pre-release status

    # If parser is release (no stage), it's compatible with all same version
    if parser_stage is None:
        return True

    # If document is release but parser is pre-release, document needs newer version
    if doc_stage is None:
        return False

    # Compare pre-release stages: a < b < rc < release
    stage_order = {"a": 0, "b": 1, "rc": 2}

    if stage_order[doc_stage] < stage_order[parser_stage]:
        return True

    if stage_order[doc_stage] > stage_order[parser_stage]:
        return False

    # Same stage, compare stage version
    return doc_stage_ver <= parser_stage_ver


def get_document_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract FTML metadata from the document.

    Args:
        data: The parsed FTML data

    Returns:
        Dictionary containing metadata (version, encoding)
    """
    metadata = {}

    if RESERVED_VERSION_KEY in data:
        metadata["version"] = data[RESERVED_VERSION_KEY]

    if RESERVED_ENCODING_KEY in data:
        metadata["encoding"] = data[RESERVED_ENCODING_KEY]

    return metadata
