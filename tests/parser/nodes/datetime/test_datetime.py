import datetime
from ftml.schema.schema_datetime_validators import (
    validate_date, validate_time, validate_datetime, validate_timestamp,
    convert_value
)


def test_date_validation():
    assert validate_date("2025-03-25") == []
    assert validate_date("2024-02-29") == []  # Leap year

    assert validate_date("2025-13-25") != []
    assert validate_date("2025-03-32") != []
    assert validate_date("25-03-2025") != []
    assert validate_date("not a date") != []
    assert validate_date(20250325) != []

    assert validate_date("03/25/2025", "%m/%d/%Y") == []
    assert validate_date("25.03.2025", "%d.%m.%Y") == []

    assert validate_date("2025-03-25", "%m/%d/%Y") != []


def test_time_validation():
    assert validate_time("14:30:00") == []
    assert validate_time("00:00:00") == []
    assert validate_time("23:59:59") == []
    assert validate_time("14:30:00.500") == []

    assert validate_time("24:00:00") != []
    assert validate_time("14:60:00") != []
    assert validate_time("14:30:60") != []
    assert validate_time("not a time") != []
    assert validate_time(143000) != []

    assert validate_time("02:30 PM", "%I:%M %p") == []
    assert validate_time("14:30", "%H:%M") == []
    assert validate_time("14:30:00", "%I:%M %p") != []


def test_datetime_validation():
    assert validate_datetime("2025-03-25T14:30:00Z") == []
    assert validate_datetime("2025-03-25T14:30:00+01:00") == []
    assert validate_datetime("2025-03-25T14:30:00.500Z") == []

    assert validate_datetime("2025-03-25 14:30:00") != []
    assert validate_datetime("2025-13-25T14:30:00Z") != []
    assert validate_datetime("2025-03-25T24:30:00Z") != []
    assert validate_datetime("not a datetime") != []
    assert validate_datetime(20250325143000) != []

    assert validate_datetime("2025-03-25 14:30:00", "iso8601") == []
    assert validate_datetime("Mar 25 2025 14:30:00", "%b %d %Y %H:%M:%S") == []

    assert validate_datetime("2025-03-25T14:30:00Z", "%Y-%m-%d %H:%M:%S") != []


def test_timestamp_validation():
    assert validate_timestamp(1711373760) == []
    assert validate_timestamp(0) == []
    assert validate_timestamp(9999999999) == []

    assert validate_timestamp("1711373760") != []
    assert validate_timestamp(-1) != []
    assert validate_timestamp(10000000000) != []

    assert validate_timestamp(1711373760123, "milliseconds") == []
    assert validate_timestamp(1711373760123456, "microseconds") == []
    assert validate_timestamp(1711373760123456789, "nanoseconds") == []

    assert validate_timestamp(1711373760, "unknown") != []
    assert validate_timestamp(10**14, "milliseconds") != []
    assert validate_timestamp(10**17, "microseconds") != []
    assert validate_timestamp(10**20, "nanoseconds") != []


def test_date_conversion():
    date_val = convert_value("2025-03-25", "date")
    assert isinstance(date_val, datetime.date)
    assert date_val.year == 2025
    assert date_val.month == 3
    assert date_val.day == 25

    date_val = convert_value("03/25/2025", "date", {"format": "%m/%d/%Y"})
    assert isinstance(date_val, datetime.date)
    assert date_val.year == 2025
    assert date_val.month == 3
    assert date_val.day == 25

    invalid_val = convert_value("not a date", "date")
    assert invalid_val == "not a date"


def test_time_conversion():
    time_val = convert_value("14:30:00", "time")
    assert isinstance(time_val, datetime.time)
    assert time_val.hour == 14
    assert time_val.minute == 30
    assert time_val.second == 0

    time_val = convert_value("14:30:00.500", "time")
    assert isinstance(time_val, datetime.time)
    assert time_val.microsecond == 500000

    time_val = convert_value("02:30 PM", "time", {"format": "%I:%M %p"})
    assert isinstance(time_val, datetime.time)
    assert time_val.hour == 14
    assert time_val.minute == 30

    invalid_val = convert_value("not a time", "time")
    assert invalid_val == "not a time"


def test_datetime_conversion():
    dt_val = convert_value("2025-03-25T14:30:00Z", "datetime")
    assert isinstance(dt_val, datetime.datetime)
    assert dt_val.year == 2025
    assert dt_val.month == 3
    assert dt_val.day == 25
    assert dt_val.hour == 14
    assert dt_val.minute == 30
    assert dt_val.second == 0
    assert dt_val.tzinfo is not None

    dt_val = convert_value("Mar 25 2025 14:30:00", "datetime", {"format": "%b %d %Y %H:%M:%S"})
    assert isinstance(dt_val, datetime.datetime)
    assert dt_val.year == 2025
    assert dt_val.month == 3
    assert dt_val.day == 25

    invalid_val = convert_value("not a datetime", "datetime")
    assert invalid_val == "not a datetime"


def test_timestamp_conversion():
    ts_val = convert_value(1711373760, "timestamp")
    assert isinstance(ts_val, datetime.datetime)
    assert ts_val.year == 2024  # Value may depend on actual timestamp

    ts_ms = convert_value(1711373760123, "timestamp", {"precision": "milliseconds"})
    assert isinstance(ts_ms, datetime.datetime)

    ts_us = convert_value(1711373760123456, "timestamp", {"precision": "microseconds"})
    assert isinstance(ts_us, datetime.datetime)

    ts_ns = convert_value(1711373760123456789, "timestamp", {"precision": "nanoseconds"})
    assert isinstance(ts_ns, datetime.datetime)

    invalid_val = convert_value("not a timestamp", "timestamp")
    assert invalid_val == "not a timestamp"
