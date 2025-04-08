"""
Test module for date, time, datetime, and timestamp types in schemas.
"""

import logging
import datetime
import pytest
from ftml.logger import logger
from ftml.schema.schema_parser import SchemaParser
from ftml.schema.schema_validator import SchemaValidator, apply_defaults
from ftml.schema.schema_debug import log_schema_ast
from ftml.schema.schema_datetime_validators import convert_value, validate_date, validate_time, validate_datetime, validate_timestamp

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_date_validator():
    # Valid dates
    assert validate_date("2025-03-25") == []
    assert validate_date("2024-02-29") == []  # Leap year
    assert validate_date("03/25/2025", "%m/%d/%Y") == []

    # Invalid dates
    assert validate_date("2025-13-25") != []  # Invalid month
    assert validate_date("2025-03-32") != []  # Invalid day
    assert validate_date(12345) != []  # Not a string
    assert validate_date("03/25/2025") != []  # Wrong default format


def test_time_validator():
    # Valid times
    assert validate_time("14:30:00") == []
    assert validate_time("00:00:00") == []
    assert validate_time("23:59:59") == []
    assert validate_time("14:30:00.500") == []  # With milliseconds
    assert validate_time("02:30 PM", "%I:%M %p") == []

    # Invalid times
    assert validate_time("24:00:00") != []  # Invalid hour
    assert validate_time("14:60:00") != []  # Invalid minute
    assert validate_time("14:30:60") != []  # Invalid second
    assert validate_time(12345) != []  # Not a string



def test_datetime_validator():
    # Valid datetimes
    assert validate_datetime("2025-03-25T14:30:00Z") == []
    assert validate_datetime("2025-03-25T14:30:00+01:00") == []
    assert validate_datetime("2025-03-25T14:30:00.500Z") == []  # With milliseconds
    assert validate_datetime("2025-03-25 14:30:00", "iso8601") == []
    assert validate_datetime("Mar 25 2025 14:30:00", "%b %d %Y %H:%M:%S") == []

    # Invalid datetimes
    assert validate_datetime("2025-03-25 14:30:00") != []  # Missing T and Z
    assert validate_datetime("2025-13-25T14:30:00Z") != []  # Invalid date
    assert validate_datetime(12345) != []  # Not a string


def test_timestamp_validator():
    # Valid timestamps
    assert validate_timestamp(1711373760) == []  # Seconds
    assert validate_timestamp(1711373760123, "milliseconds") == []
    assert validate_timestamp(1711373760123456, "microseconds") == []
    assert validate_timestamp(1711373760123456789, "nanoseconds") == []

    # Invalid timestamps
    assert validate_timestamp("1711373760") != []  # Not an integer
    assert validate_timestamp(-1) != []  # Negative
    assert validate_timestamp(10**20) != []  # Too large


def test_date_schema_parsing():
    """Test parsing of date type in schemas."""
    parser = SchemaParser()

    # Test basic date type
    schema = """
    birthday: date
    """
    result = parser.parse(schema)

    assert "birthday" in result
    assert result["birthday"].type_name == "date"
    assert not result["birthday"].constraints
    assert not result["birthday"].has_default

    # Test date with format constraint
    schema = """
    us_date: date<format="%m/%d/%Y">
    """
    result = parser.parse(schema)
    assert "us_date" in result
    assert result["us_date"].type_name == "date"
    assert "format" in result["us_date"].constraints
    assert result["us_date"].constraints["format"] == "%m/%d/%Y"

    # Test date with default value
    schema = """
    start_date: date = "2025-03-25"
    """
    result = parser.parse(schema)

    assert "start_date" in result
    assert result["start_date"].type_name == "date"
    assert result["start_date"].has_default
    assert result["start_date"].default == "2025-03-25"

    # Test date with format and default
    schema = """
    custom_date: date<format="%d.%m.%Y"> = "25.03.2025"
    """
    result = parser.parse(schema)

    assert "custom_date" in result
    assert result["custom_date"].type_name == "date"
    assert "format" in result["custom_date"].constraints
    assert result["custom_date"].constraints["format"] == "%d.%m.%Y"
    assert result["custom_date"].has_default
    assert result["custom_date"].default == "25.03.2025"


def test_time_schema_parsing():
    """Test parsing of time type in schemas."""
    parser = SchemaParser()

    # Test basic time type
    schema = """
    meeting_time: time
    """
    result = parser.parse(schema)

    assert "meeting_time" in result
    assert result["meeting_time"].type_name == "time"
    assert not result["meeting_time"].constraints

    # Test time with format constraint
    schema = """
    am_pm_time: time<format="%I:%M %p">
    """
    result = parser.parse(schema)

    assert "am_pm_time" in result
    assert result["am_pm_time"].type_name == "time"
    assert "format" in result["am_pm_time"].constraints
    assert result["am_pm_time"].constraints["format"] == "%I:%M %p"

    # Test time with default value
    schema = """
    default_time: time = "14:30:00"
    """
    result = parser.parse(schema)

    assert "default_time" in result
    assert result["default_time"].type_name == "time"
    assert result["default_time"].has_default
    assert result["default_time"].default == "14:30:00"


def test_datetime_schema_parsing():
    """Test parsing of datetime type in schemas."""
    parser = SchemaParser()

    # Test basic datetime type
    schema = """
    created_at: datetime
    """
    result = parser.parse(schema)

    assert "created_at" in result
    assert result["created_at"].type_name == "datetime"
    assert not result["created_at"].constraints

    # Test datetime with format constraint
    schema = """
    custom_dt: datetime<format="%Y-%m-%d %H:%M:%S">
    """
    result = parser.parse(schema)

    assert "custom_dt" in result
    assert result["custom_dt"].type_name == "datetime"
    assert "format" in result["custom_dt"].constraints
    assert result["custom_dt"].constraints["format"] == "%Y-%m-%d %H:%M:%S"

    # Test datetime with default value
    schema = """
    default_dt: datetime = "2025-03-25T14:30:00Z"
    """
    result = parser.parse(schema)

    assert "default_dt" in result
    assert result["default_dt"].type_name == "datetime"
    assert result["default_dt"].has_default
    assert result["default_dt"].default == "2025-03-25T14:30:00Z"


def test_timestamp_schema_parsing():
    """Test parsing of timestamp type in schemas."""
    parser = SchemaParser()

    # Test basic timestamp type
    schema = """
    created_ts: timestamp
    """
    result = parser.parse(schema)

    assert "created_ts" in result
    assert result["created_ts"].type_name == "timestamp"
    assert not result["created_ts"].constraints

    # Test timestamp with precision constraint
    schema = """
    ms_timestamp: timestamp<precision="milliseconds">
    """
    result = parser.parse(schema)

    assert "ms_timestamp" in result
    assert result["ms_timestamp"].type_name == "timestamp"
    assert "precision" in result["ms_timestamp"].constraints
    assert result["ms_timestamp"].constraints["precision"] == "milliseconds"

    # Test timestamp with default value
    schema = """
    default_ts: timestamp = 1711373760
    """
    result = parser.parse(schema)

    assert "default_ts" in result
    assert result["default_ts"].type_name == "timestamp"
    assert result["default_ts"].has_default
    assert result["default_ts"].default == 1711373760


def test_date_constraints():
    """Test constraints for date type."""
    parser = SchemaParser()

    # Define a schema with date constraints
    schema = """
    past_date: date<max="2025-01-01">
    future_date: date<min="2025-01-01">
    specific_format: date<format="%m/%d/%Y">
    """

    schema_objects = parser.parse(schema)
    validator = SchemaValidator(schema_objects)

    # Valid data
    valid_data = {
        "past_date": "2024-12-31",
        "future_date": "2025-01-02",
        "specific_format": "03/25/2025"
    }

    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data
    invalid_data = {
        "past_date": "2025-01-02",  # After max
        "future_date": "2024-12-31",  # Before min
        "specific_format": "2025-03-25"  # Wrong format
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 3, f"Expected 3 errors, got: {len(errors)}"

    # Check specific error messages
    error_str = "\n".join(errors)
    assert "past_date" in error_str and "after maximum date" in error_str
    assert "future_date" in error_str and "before minimum date" in error_str
    assert "specific_format" in error_str and "format" in error_str


def test_time_constraints():
    """Test constraints for time type."""
    parser = SchemaParser()

    # Define a schema with time constraints
    schema = """
    standard_time: time
    custom_format: time<format="%I:%M %p">
    """

    schema_objects = parser.parse(schema)
    validator = SchemaValidator(schema_objects)

    # Valid data
    valid_data = {
        "standard_time": "14:30:00",
        "custom_format": "02:30 PM"
    }

    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data
    invalid_data = {
        "standard_time": "25:30:00",  # Invalid hour
        "custom_format": "14:30:00"  # Wrong format
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 2, f"Expected 2 errors, got: {len(errors)}"


def test_datetime_constraints():
    """Test constraints for datetime type."""
    parser = SchemaParser()

    # Define a schema with datetime constraints
    schema = """
    standard_dt: datetime
    iso8601_dt: datetime<format="iso8601">
    custom_format: datetime<format="%b %d %Y %H:%M:%S">
    """

    schema_objects = parser.parse(schema)
    validator = SchemaValidator(schema_objects)

    # Valid data
    valid_data = {
        "standard_dt": "2025-03-25T14:30:00Z",
        "iso8601_dt": "2025-03-25 14:30:00",
        "custom_format": "Mar 25 2025 14:30:00"
    }

    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data
    invalid_data = {
        "standard_dt": "2025-03-25 14:30:00",  # Missing T and Z
        "iso8601_dt": "03/25/2025 2:30 PM",  # Not ISO 8601
        "custom_format": "2025-03-25T14:30:00Z"  # Wrong format
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 3, f"Expected 3 errors, got: {len(errors)}"


def test_timestamp_constraints():
    """Test constraints for timestamp type."""
    parser = SchemaParser()

    # Define a schema with timestamp constraints
    schema = """
    standard_ts: timestamp
    ms_ts: timestamp<precision="milliseconds">
    us_ts: timestamp<precision="microseconds">
    ns_ts: timestamp<precision="nanoseconds">
    range_ts: timestamp<min=1704067200, max=1767225599>  # 2025 only
    """

    schema_objects = parser.parse(schema)
    validator = SchemaValidator(schema_objects)

    # Valid data
    valid_data = {
        "standard_ts": 1711373760,
        "ms_ts": 1711373760123,
        "us_ts": 1711373760123456,
        "ns_ts": 1711373760123456789,
        "range_ts": 1711373760
    }

    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data
    invalid_data = {
        "standard_ts": "1711373760",  # String, not int
        "ms_ts": 1711373760,  # Missing milliseconds precision
        "us_ts": 9999999999999999999,  # Too large
        "ns_ts": -1,  # Negative
        "range_ts": 1672531200  # 2023-01-01, outside range
    }

    errors = validator.validate(invalid_data)
    assert len(errors) >= 4, f"Expected at least 4 errors, got: {len(errors)}"


def test_datetime_defaults():
    """Test default values for date/time types."""
    parser = SchemaParser()

    # Define a schema with defaults
    schema = """
    event: {
        name: str = "Event",
        date: date = "2025-03-25",
        time: time = "14:30:00",
        created_at: datetime = "2025-03-25T14:30:00Z",
        timestamp: timestamp = 1711373760
    }
    """

    schema_objects = parser.parse(schema)

    # Empty data
    data = {"event": {}}

    # Apply defaults
    result = apply_defaults(data, schema_objects)

    # Check defaults
    assert result["event"]["name"] == "Event"
    assert result["event"]["date"] == datetime.date(2025, 3, 25)
    assert result["event"]["time"] == datetime.time(14, 30, 0)
    assert result["event"]["created_at"] == datetime.datetime(2025, 3, 25, 14, 30, 0, tzinfo=datetime.timezone.utc)
    assert result["event"]["timestamp"] == datetime.datetime(2024, 3, 25, 13, 36, tzinfo=datetime.timezone.utc)


def test_datetime_conversions():
    """Test date/time value conversions."""
    # Test date conversion
    date_val = convert_value("2025-03-25", "date")
    assert isinstance(date_val, datetime.date)
    assert date_val.year == 2025
    assert date_val.month == 3
    assert date_val.day == 25

    # Test time conversion
    time_val = convert_value("14:30:00", "time")
    assert isinstance(time_val, datetime.time)
    assert time_val.hour == 14
    assert time_val.minute == 30
    assert time_val.second == 0

    # Test datetime conversion
    dt_val = convert_value("2025-03-25T14:30:00Z", "datetime")
    assert isinstance(dt_val, datetime.datetime)
    assert dt_val.year == 2025
    assert dt_val.month == 3
    assert dt_val.day == 25
    assert dt_val.hour == 14
    assert dt_val.minute == 30
    assert dt_val.second == 0
    assert dt_val.tzinfo is not None  # Has timezone

    # Test timestamp conversion
    ts_val = convert_value(1711373760, "timestamp")
    assert isinstance(ts_val, datetime.datetime)

    # Test with constraints
    custom_date = convert_value("03/25/2025", "date", {"format": "%m/%d/%Y"})
    assert isinstance(custom_date, datetime.date)
    assert custom_date.month == 3
    assert custom_date.day == 25
    assert custom_date.year == 2025

    custom_time = convert_value("02:30 PM", "time", {"format": "%I:%M %p"})
    assert isinstance(custom_time, datetime.time)
    assert custom_time.hour == 14
    assert custom_time.minute == 30


def test_datetime_in_objects():
    """Test date/time types in nested objects."""
    parser = SchemaParser()

    # Define a schema with nested date/time types
    schema = """
    event: {
        name: str,
        schedule: {
            date: date,
            start_time: time,
            end_time: time
        },
        metadata: {
            created_at: datetime,
            updated_at: datetime
        }
    }
    """

    schema_objects = parser.parse(schema)
    validator = SchemaValidator(schema_objects)

    # Valid data
    valid_data = {
        "event": {
            "name": "Team Meeting",
            "schedule": {
                "date": "2025-03-25",
                "start_time": "14:30:00",
                "end_time": "15:30:00"
            },
            "metadata": {
                "created_at": "2025-03-20T09:15:30Z",
                "updated_at": "2025-03-20T09:15:30Z"
            }
        }
    }

    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data
    invalid_data = {
        "event": {
            "name": "Team Meeting",
            "schedule": {
                "date": "invalid-date",
                "start_time": "invalid-time",
                "end_time": "invalid-time"
            },
            "metadata": {
                "created_at": "invalid-datetime",
                "updated_at": "invalid-datetime"
            }
        }
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 5, f"Expected 5 errors, got: {len(errors)}"


def test_datetime_in_lists():
    """Test date/time types in lists."""
    parser = SchemaParser()

    # Define a schema with date/time types in lists
    schema = """
    dates: [date]
    times: [time]
    datetimes: [datetime]
    timestamps: [timestamp]
    """

    schema_objects = parser.parse(schema)
    validator = SchemaValidator(schema_objects)

    # Valid data
    valid_data = {
        "dates": ["2025-03-25", "2025-03-26", "2025-03-27"],
        "times": ["14:30:00", "15:30:00", "16:30:00"],
        "datetimes": ["2025-03-25T14:30:00Z", "2025-03-26T14:30:00Z"],
        "timestamps": [1711373760, 1711460160]
    }

    errors = validator.validate(valid_data)
    assert not errors, f"Expected no errors, got: {errors}"

    # Invalid data
    invalid_data = {
        "dates": ["2025-03-25", "invalid-date"],
        "times": ["14:30:00", "invalid-time"],
        "datetimes": ["2025-03-25T14:30:00Z", "invalid-datetime"],
        "timestamps": [1711373760, "invalid-timestamp"]
    }

    errors = validator.validate(invalid_data)
    assert len(errors) == 4, f"Expected 4 errors, got: {len(errors)}"


def test_datetime_in_unions():
    """Test date/time types in unions."""
    parser = SchemaParser()

    # Define a schema with date/time types in unions
    schema = """
    date_or_string: date | str
    time_or_null: time | null
    dt_or_ts: datetime | timestamp
    """

    schema_objects = parser.parse(schema)
    validator = SchemaValidator(schema_objects)

    # Valid data with first variants
    valid_data_1 = {
        "date_or_string": "2025-03-25",
        "time_or_null": "14:30:00",
        "dt_or_ts": "2025-03-25T14:30:00Z"
    }

    errors = validator.validate(valid_data_1)
    assert not errors, f"Expected no errors, got: {errors}"

    # Valid data with second variants
    valid_data_2 = {
        "date_or_string": "Not a date but a string",
        "time_or_null": None,
        "dt_or_ts": 1711373760
    }

    errors = validator.validate(valid_data_2)
    assert not errors, f"Expected no errors, got: {errors}"


def test_real_world_example():
    """Test a real-world example with date/time types."""
    parser = SchemaParser()

    # Define a schema for event scheduling
    schema = """
    event: {
        name: str<min_length=1>,
        description: str,
        date: date,
        start_time: time,
        end_time: time,
        created_at: datetime,
        reminder_ts: timestamp,
        timezone: str = "UTC",
        all_day: bool = false,
        attendees: [str],
        metadata: {
            created_by: str,
            last_modified: datetime
        },
        recurring?: {
            frequency: str<enum=["daily", "weekly", "monthly", "yearly"]>,
            until: date
        }
    }
    """

    schema_objects = parser.parse(schema)
    validator = SchemaValidator(schema_objects)

    # Valid event data
    valid_event = {
        "event": {
            "name": "Team Meeting",
            "description": "Weekly status update",
            "date": "2025-03-25",
            "start_time": "14:00:00",
            "end_time": "15:30:00",
            "created_at": "2025-03-20T09:15:30Z",
            "reminder_ts": 1711373400,
            "attendees": ["alice@example.com", "bob@example.com"],
            "metadata": {
                "created_by": "alice@example.com",
                "last_modified": "2025-03-20T09:15:30Z"
            },
            "recurring": {
                "frequency": "weekly",
                "until": "2025-06-25"
            }
        }
    }

    errors = validator.validate(valid_event)
    assert not errors, f"Expected no errors, got: {errors}"

    # Apply defaults to minimal data
    minimal_event = {
        "event": {
            "name": "Quick Meeting",
            "description": "Brief sync",
            "date": "2025-03-25",
            "start_time": "14:00:00",
            "end_time": "14:30:00",
            "created_at": "2025-03-20T09:15:30Z",
            "reminder_ts": 1711373400,
            "attendees": ["alice@example.com"],
            "metadata": {
                "created_by": "alice@example.com",
                "last_modified": "2025-03-20T09:15:30Z"
            }
        }
    }

    result = apply_defaults(minimal_event, schema_objects)

    # Check defaults were applied
    assert result["event"]["timezone"] == "UTC"
    assert result["event"]["all_day"] is False
    assert "recurring" not in result["event"]  # Optional field without default


if __name__ == "__main__":
    # Run tests individually for debugging
    test_date_schema_parsing()
    test_time_schema_parsing()
    test_datetime_schema_parsing()
    test_timestamp_schema_parsing()
    test_date_constraints()
    test_time_constraints()
    test_datetime_constraints()
    test_timestamp_constraints()
    test_datetime_defaults()
    test_datetime_conversions()
    test_datetime_in_objects()
    test_datetime_in_lists()
    test_datetime_in_unions()
    test_real_world_example()

    print("All date/time type tests passed!")