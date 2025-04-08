"""
FTML Date/Time Validation Module

Provides validation logic for date, time, datetime, and timestamp types.
"""

import re
import datetime
from typing import Any, Dict, List, Optional

from ftml.logger import logger


def validate_date(value: Any, format_str: Optional[str] = None) -> List[str]:
    """
    Validate a date value against the expected format.

    Args:
        value: The value to validate
        format_str: Optional format string (strftime syntax)

    Returns:
        A list of validation error messages (empty if valid)
    """
    if not isinstance(value, str):
        return [f"Expected date string, got {type(value).__name__}"]

    # Use RFC 3339/ISO 8601 format by default (YYYY-MM-DD)
    if not format_str or format_str.lower() in ("rfc3339", "iso8601"):
        format_str = "%Y-%m-%d"

    try:
        datetime.datetime.strptime(value, format_str)
        return []
    except ValueError as e:
        return [f"Invalid date format: {str(e)}"]


def validate_time(value: Any, format_str: Optional[str] = None) -> List[str]:
    """
    Validate a time value against the expected format.

    Args:
        value: The value to validate
        format_str: Optional format string (strftime syntax)

    Returns:
        A list of validation error messages (empty if valid)
    """
    if not isinstance(value, str):
        return [f"Expected time string, got {type(value).__name__}"]

    # Use ISO 8601 format by default (HH:MM:SS[.sss])
    if not format_str or format_str.lower() == "iso8601":
        # Check for optional milliseconds
        if re.match(r"^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)(\.\d+)?$", value):
            return []
        else:
            return ["Invalid time format, expected HH:MM:SS[.sss]"]

    try:
        datetime.datetime.strptime(value, format_str)
        return []
    except ValueError as e:
        return [f"Invalid time format: {str(e)}"]


def validate_datetime(value: Any, format_str: Optional[str] = None) -> List[str]:
    """
    Validate a datetime value against the expected format.

    Args:
        value: The value to validate
        format_str: Optional format string (strftime syntax)

    Returns:
        A list of validation error messages (empty if valid)
    """
    if not isinstance(value, str):
        return [f"Expected datetime string, got {type(value).__name__}"]

    # Handle standard formats
    if not format_str:
        # Default to RFC 3339
        try:
            # Basic regex check for RFC 3339 format
            # YYYY-MM-DDThh:mm:ss[.sss]Z or with timezone offset
            if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$", value):
                return ["Invalid datetime format, expected RFC 3339 format (YYYY-MM-DDThh:mm:ss[.sss]Z)"]

            # For Z timezone, convert to +00:00 for parsing
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"

            datetime.datetime.fromisoformat(value)
            return []
        except ValueError as e:
            return [f"Invalid datetime format: {str(e)}"]
    elif format_str.lower() == "rfc3339":
        # RFC 3339 validation (same as default)
        try:
            # Check for RFC 3339 format
            if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$", value):
                return ["Invalid datetime format, expected RFC 3339 format (YYYY-MM-DDThh:mm:ss[.sss]Z)"]

            if value.endswith("Z"):
                value = value[:-1] + "+00:00"

            datetime.datetime.fromisoformat(value)
            return []
        except ValueError as e:
            return [f"Invalid RFC 3339 datetime format: {str(e)}"]
    elif format_str.lower() == "iso8601":
        # More permissive ISO 8601 format
        try:
            # Replace space with T if needed
            if " " in value and "T" not in value:
                value = value.replace(" ", "T")

            datetime.datetime.fromisoformat(value)
            return []
        except ValueError as e:
            return [f"Invalid ISO 8601 datetime format: {str(e)}"]
    else:
        # Custom format
        try:
            datetime.datetime.strptime(value, format_str)
            return []
        except ValueError as e:
            return [f"Invalid datetime format: {str(e)}"]


def validate_timestamp(value: Any, precision: Optional[str] = None) -> List[str]:
    """
    Validate a timestamp value.

    Args:
        value: The value to validate
        precision: Optional precision specification (seconds, milliseconds, microseconds, nanoseconds)

    Returns:
        A list of validation error messages (empty if valid)
    """
    # Check type
    if not isinstance(value, int):
        return [f"Expected integer timestamp, got {type(value).__name__}"]

    # Determine allowed range based on precision
    if not precision or precision == "seconds":
        # Seconds precision (10 digits)
        if value < 0 or value > 9999999999:
            return ["Timestamp out of range for seconds precision (expected 0 to 9,999,999,999)"]
    elif precision == "milliseconds":
        # Milliseconds precision (13 digits)
        if value < 0 or value > 9999999999999:
            return ["Timestamp out of range for milliseconds precision (expected 0 to 9,999,999,999,999)"]
    elif precision == "microseconds":
        # Microseconds precision (16 digits)
        if value < 0 or value > 9999999999999999:
            return ["Timestamp out of range for microseconds precision (expected 0 to 9,999,999,999,999,999)"]
    elif precision == "nanoseconds":
        # Nanoseconds precision (19 digits)
        if value < 0 or value > 9999999999999999999:
            return ["Timestamp out of range for nanoseconds precision (expected 0 to 9,999,999,999,999,999,999)"]
    else:
        return [f"Unknown timestamp precision: {precision}"]

    return []


def convert_value(value: Any, type_name: str, constraints: Optional[Dict[str, Any]] = None) -> Any:
    """
    Convert a string or integer value to the appropriate Python datetime object.

    Args:
        value: The value to convert
        type_name: The type name (date, time, datetime, timestamp)
        constraints: Optional constraints dictionary containing format or precision

    Returns:
        A Python datetime.date, datetime.time, or datetime.datetime object
    """
    constraints = constraints or {}

    try:
        if type_name == "date":
            format_str = constraints.get("format")
            if not format_str or format_str.lower() in ("rfc3339", "iso8601"):
                format_str = "%Y-%m-%d"
            return datetime.datetime.strptime(value, format_str).date()

        elif type_name == "time":
            format_str = constraints.get("format")
            if not format_str or format_str.lower() == "iso8601":
                # Standard ISO 8601 time format
                if "." in value:
                    # With milliseconds
                    hour, minute, rest = value.split(":", 2)
                    second, millis = rest.split(".")
                    return datetime.time(int(hour), int(minute), int(second), int(millis) * 1000)
                else:
                    # Without milliseconds
                    hour, minute, second = value.split(":")
                    return datetime.time(int(hour), int(minute), int(second))
            else:
                # Custom format
                return datetime.datetime.strptime(value, format_str).time()

        elif type_name == "datetime":
            format_str = constraints.get("format")

            if not format_str:
                # Default RFC 3339
                if value.endswith("Z"):
                    value = value[:-1] + "+00:00"
                return datetime.datetime.fromisoformat(value)
            elif format_str.lower() == "rfc3339":
                if value.endswith("Z"):
                    value = value[:-1] + "+00:00"
                return datetime.datetime.fromisoformat(value)
            elif format_str.lower() == "iso8601":
                # More permissive ISO 8601
                if " " in value and "T" not in value:
                    value = value.replace(" ", "T")
                return datetime.datetime.fromisoformat(value)
            else:
                # Custom format
                return datetime.datetime.strptime(value, format_str)

        elif type_name == "timestamp":
            precision = constraints.get("precision")

            # Convert to seconds
            seconds = value
            if precision == "milliseconds":
                seconds = value / 1000
            elif precision == "microseconds":
                seconds = value / 1000000
            elif precision == "nanoseconds":
                seconds = value / 1000000000

            # Convert to datetime
            return datetime.datetime.fromtimestamp(seconds, tz=datetime.timezone.utc)

    except (ValueError, TypeError) as e:
        logger.error(f"Error converting value {value} to {type_name}: {str(e)}")
        return value  # Return original value on error

    return value  # Return original value for unknown types
