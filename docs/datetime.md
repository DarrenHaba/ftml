# FTML Date, Time, and Timestamp Types Specification

## 1. Overview

FTML supports four dedicated types for handling temporal data:

| Type | Description | Default Format | Internal Representation |
|------|-------------|----------------|------------------------|
| `date` | Calendar date without time | RFC 3339 (`YYYY-MM-DD`) | `datetime.date` |
| `time` | Time of day without date | ISO 8601 (`HH:MM:SS[.sss]`) | `datetime.time` |
| `datetime` | Combined date and time, typically with timezone | RFC 3339 (`YYYY-MM-DDThh:mm:ss[.sss]Z`) | `datetime.datetime` |
| `timestamp` | Integer epoch time | Seconds since epoch | `int` → `datetime.datetime` |

## 2. Type Details

### 2.1 Date Type

The `date` type represents a calendar date without time components.

```ftml
// Schema definition
birthday: date

// Usage
birthday = "2025-03-25"
```

By default, dates use RFC 3339/ISO 8601 format: `YYYY-MM-DD`.

#### Format Constraints

```ftml
// Default RFC 3339 format
meeting_date: date = "2025-03-25"

// Explicit RFC 3339/ISO 8601 format
explicit_date: date<format="rfc3339"> = "2025-03-25"
explicit_date: date<format="iso8601"> = "2025-03-25"

// Custom format using strftime syntax
us_date: date<format="%m/%d/%Y"> = "03/25/2025"
euro_date: date<format="%d.%m.%Y"> = "25.03.2025"
```

### 2.2 Time Type

The `time` type represents a time of day without date components.

```ftml
// Schema definition
start_time: time

// Usage
start_time = "14:30:00"
```

By default, times use ISO 8601 format: `HH:MM:SS[.sss]`.

#### Format Constraints

```ftml
// Default ISO 8601 format
meeting_time: time = "14:30:00"
precise_time: time = "14:30:00.500"  // With milliseconds

// Explicit ISO 8601 format
explicit_time: time<format="iso8601"> = "14:30:00"

// Custom format using strftime syntax
am_pm_time: time<format="%I:%M %p"> = "02:30 PM"
hours_mins: time<format="%H:%M"> = "14:30"
```

### 2.3 DateTime Type

The `datetime` type represents a combined date and time, typically with timezone information.

```ftml
// Schema definition
created_at: datetime

// Usage
created_at = "2025-03-25T14:30:00Z"  // UTC
created_at = "2025-03-25T14:30:00+01:00"  // With offset
```

By default, datetimes use RFC 3339 format: `YYYY-MM-DDThh:mm:ss[.sss]Z` or with timezone offset.

#### Format Constraints

```ftml
// Default RFC 3339 format
event_time: datetime = "2025-03-25T14:30:00Z"
precise_time: datetime = "2025-03-25T14:30:00.500Z"  // With milliseconds

// Explicit RFC 3339 format
explicit_dt: datetime<format="rfc3339"> = "2025-03-25T14:30:00Z"

// ISO 8601 format (more permissive, allows space separator)
iso_dt: datetime<format="iso8601"> = "2025-03-25 14:30:00"

// Custom format using strftime syntax
custom_dt: datetime<format="%Y-%m-%d %H:%M"> = "2025-03-25 14:30"
log_dt: datetime<format="%b %d %Y %H:%M:%S"> = "Mar 25 2025 14:30:00"
```

### 2.4 Timestamp Type

The `timestamp` type represents a point in time as an integer epoch timestamp.

```ftml
// Schema definition
created_ts: timestamp

// Usage
created_ts = 1711373760  // March 25, 2025 14:30:00 UTC
```

By default, timestamps use seconds precision.

#### Precision Constraints

```ftml
// Default seconds precision (10 digits)
seconds_ts: timestamp = 1711373760

// Milliseconds precision (13 digits)
millis_ts: timestamp<precision="milliseconds"> = 1711373760123

// Microseconds precision (16 digits)
micros_ts: timestamp<precision="microseconds"> = 1711373760123456

// Nanoseconds precision (19 digits)
nanos_ts: timestamp<precision="nanoseconds"> = 1711373760123456789
```

## 3. Schema Validation Examples

### 3.1 Basic Schema with Multiple Date/Time Types

```ftml
schema_version = "1.0"

// Person schema with temporal fields
name: str<min=2>
birthday: date
preferred_meeting_time: time
account_created: datetime
last_login: timestamp
```

### 3.2 Schema with Format Constraints

```ftml
schema_version = "1.0"

// Event schema with format constraints
event_name: str
start_date: date<format="%m/%d/%Y"> = "01/01/2025"
start_time: time<format="%I:%M %p"> = "09:00 AM"
created_at: datetime<format="rfc3339">
modified_ts: timestamp<precision="milliseconds">
```

### 3.3 Schema with Multiple Constraints

```ftml
schema_version = "1.0"

// Log entry schema with multiple constraints
severity: str<enum=["info", "warning", "error"]>
message: str<min=1>
timestamp: timestamp
source_file: str
line_number: int<min=1>
created_at: datetime<format="iso8601">
```

## 4. Format Reference Table

### 4.1 Standard Date/Time Formats

| Format Name | Pattern | Example | Notes |
|-------------|---------|---------|-------|
| RFC 3339 Date | `YYYY-MM-DD` | `2025-03-25` | Default for `date` type |
| ISO 8601 Time | `HH:MM:SS[.sss]` | `14:30:00.500` | Default for `time` type |
| RFC 3339 DateTime | `YYYY-MM-DDThh:mm:ss[.sss]Z` | `2025-03-25T14:30:00Z` | Default for `datetime` type, requires T separator and Z or timezone offset |
| ISO 8601 DateTime | `YYYY-MM-DD HH:MM:SS` | `2025-03-25 14:30:00` | More permissive, allows space separator |

### 4.2 Common strftime Format Specifiers

| Specifier | Meaning | Example |
|-----------|---------|---------|
| `%Y` | 4-digit year | `2025` |
| `%m` | Month (01-12) | `03` |
| `%d` | Day of month (01-31) | `25` |
| `%H` | Hour (00-23) | `14` |
| `%M` | Minute (00-59) | `30` |
| `%S` | Second (00-59) | `00` |
| `%I` | Hour (01-12) | `02` |
| `%p` | AM/PM | `PM` |
| `%b` | Abbreviated month name | `Mar` |
| `%B` | Full month name | `March` |
| `%a` | Abbreviated weekday | `Tue` |
| `%A` | Full weekday | `Tuesday` |

### 4.3 Timestamp Precision Options

| **Precision**     | **Digits** | **Range**                         | **Example**             | **Scale (Factor)** |
|------------------|------------|-----------------------------------|--------------------------|--------------------|
| seconds          | 10         | 0 to 9,999,999,999                | 1711373760               | ×1                 |
| milliseconds     | 13         | 0 to 9,999,999,999,999            | 1711373760123            | ×1,000             |
| microseconds     | 16         | 0 to 9,999,999,999,999,999        | 1711373760123456         | ×1,000,000         |
| nanoseconds      | 19         | 0 to 9,999,999,999,999,999,999    | 1711373760123456789      | ×1,000,000,000     |

## 5. Implementation Details

### 5.1 Internal Representation

When FTML parses date, time, and datetime values:

- `date` strings → `datetime.date` objects
- `time` strings → `datetime.time` objects
- `datetime` strings → `datetime.datetime` objects
- `timestamp` integers → `datetime.datetime` objects (when needed)

### 5.2 Validation Process

1. **Type Validation**: Verifies the input is the correct type (string for date/time, integer for timestamp)
2. **Format Validation**: Checks if the value conforms to the specified format
3. **Constraint Validation**: Applies any additional constraints (min/max values, etc.)

### 5.3 Practical Usage

```ftml
// Real-world example: Event scheduling
event = {
    name = "Team Meeting"
    description = "Weekly status update"
    date = "2025-03-25"  // RFC 3339 date
    start_time = "14:00:00"  // ISO 8601 time
    end_time = "15:30:00"
    created_at = "2025-03-20T09:15:30Z"  // RFC 3339 datetime
    reminder_ts = 1711373400  // Timestamp (5 minutes before)
    timezone = "UTC"
}
```

## 6. Best Practices

1. **Use Default Formats When Possible**:
    - For date: `YYYY-MM-DD`
    - For time: `HH:MM:SS[.sss]`
    - For datetime: `YYYY-MM-DDThh:mm:ss[.sss]Z`

2. **Include Timezone Information** for datetime values when relevant (use `Z` for UTC or explicit offsets like `+01:00`)

3. **Choose Appropriate Precision** for timestamps based on your needs:
    - Most applications only need seconds precision
    - High-performance systems might require milliseconds or microseconds
    - Nanoseconds precision is rarely needed outside scientific applications

4. **Use Custom Formats Sparingly**:
    - Custom formats reduce interoperability
    - When needed, document them clearly

5. **Validate Time-Sensitive Data**:
    - Add min/max constraints for dates and timestamps in time-sensitive applications
    - Example: `expiry_date: date<min="2025-01-01">`

This specification provides a comprehensive guide to using date, time, datetime, and timestamp types in FTML.