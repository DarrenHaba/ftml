# FTML Constraints Specification

## 1. Overview

FTML supports a comprehensive constraint system for validating field values according to schema rules. Constraints can be applied to any type using angle bracket notation, providing precise control over allowed values. This specification details the available constraints and their usage.

## 2. Constraint Syntax

### 2.1 Basic Syntax

Constraints are specified within angle brackets directly after a type definition:

```ftml
name: str<min_length=3>
```

### 2.2 Multiple Constraints

Multiple constraints can be combined with commas:

```ftml
port: int<min=1024, max=65535>
```

### 2.3 Constraint Values

Constraint values can be:
- Strings: `pattern="[a-z]+"`
- Numbers: `min=0`
- Booleans: `unique=true`
- Lists: `enum=["red", "green", "blue"]`

### 2.4 Constraints with Default Values

Constraints can be used alongside default values:

```ftml
port: int<min=1024, max=65535> = 8080
```

## 3. String Constraints

### 3.1 Length Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `min_length` | Minimum number of characters | `str<min_length=3>` |
| `max_length` | Maximum number of characters | `str<max_length=20>` |
| `min` | Alias for min_length | `str<min=3>` |
| `max` | Alias for max_length | `str<max=20>` |

```ftml
username: str<min_length=3, max_length=20>
code: str<min=6, max=6>  // Fixed length of 6
```

### 3.2 Pattern Constraint

The `pattern` constraint uses regular expressions to validate strings:

```ftml
username: str<pattern="[a-zA-Z0-9_]+">
zipcode: str<pattern="[0-9]{5}(-[0-9]{4})?">
```

### 3.3 String Constraint Examples

```ftml
// Username: 3-20 alphanumeric characters or underscores
username: str<min_length=3, max_length=20, pattern="[a-zA-Z0-9_]+">

// Password: 8+ chars with complexity requirements
password: str<min_length=8, pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).+$">

// Fixed format product code
product_code: str<pattern="[A-Z]{2}[0-9]{6}">

// Email with pattern validation
email: str<pattern="[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}">
```

## 4. Numeric Constraints

### 4.1 Integer Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `min` | Minimum value (inclusive) | `int<min=0>` |
| `max` | Maximum value (inclusive) | `int<max=100>` |

```ftml
port: int<min=1024, max=65535>
positive: int<min=1>
negative: int<max=-1>
```

### 4.2 Float Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `min` | Minimum value (inclusive) | `float<min=0.0>` |
| `max` | Maximum value (inclusive) | `float<max=1.0>` |
| `precision` | Maximum decimal places | `float<precision=2>` |

```ftml
probability: float<min=0.0, max=1.0>
percentage: float<min=0.0, max=100.0, precision=2>
```

### 4.3 Numeric Constraint Examples

```ftml
// Port number in valid range
port: int<min=1024, max=65535> = 8080

// Age must be positive
age: int<min=0>

// Probability between 0 and 1
probability: float<min=0.0, max=1.0>

// Price with 2 decimal places
price: float<min=0.0, precision=2>

// Temperature in Celsius (allows negative values)
temperature: float<min=-273.15>

// Year within reasonable range
year: int<min=1900, max=2100>
```

## 5. Collection Constraints

### 5.1 List Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `min` | Minimum number of items | `[str]<min=1>` |
| `max` | Maximum number of items | `[str]<max=10>` |
| `min_items` | Alias for min | `[str]<min_items=1>` |
| `max_items` | Alias for max | `[str]<max_items=10>` |
| `unique` | Items must be unique | `[str]<unique=true>` |

```ftml
tags: [str]<min=1, max=10>
unique_ids: [int]<unique=true>
```

### 5.2 Object Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `min` | Minimum number of properties | `{str: any}<min=1>` |
| `max` | Maximum number of properties | `{str: any}<max=20>` |
| `min_properties` | Alias for min | `{str: any}<min_properties=1>` |
| `max_properties` | Alias for max | `{str: any}<max_properties=20>` |
| `required_keys` | Keys that must be present | `{str: any}<required_keys=["id"]>` |
| `ext` | Allow additional properties beyond schema | `{...}<ext=true>` |

```ftml
headers: {str: str}<min=1, max=20>
config: {str: any}<required_keys=["version", "name"]>
```

### 5.3 Collection Constraint Examples

```ftml
// List with 1-5 strings
tags: [str]<min=1, max=5>

// List with unique integers
unique_ids: [int]<unique=true>

// Object with at least one property
non_empty: {}<min=1>

// Object with maximum 10 properties
compact: {}<max=10>

// Object requiring specific keys
valid_config: {}<required_keys=["version", "name"]>

// Object allowing additional properties
extensible: {
  id: int,
  name: str
}<ext=true>

// List of objects with constraints on each object
users: [{
  name: str<min_length=1>,
  age: int<min=18>
}]<max=100>
```

## 6. Enum Constraint

The `enum` constraint limits values to a predefined set of options.

### 6.1 Enum Syntax

```ftml
status: str<enum=["pending", "active", "completed"]>
priority: int<enum=[1, 2, 3, 5, 8]>
```

### 6.2 Enum with Multiple Types

```ftml
// Can only be null or one of the specified strings
visibility: str<enum=["public", "private", "unlisted"]> | null
```

### 6.3 Enum Constraint Examples

```ftml
// String enum for status
status: str<enum=["pending", "active", "completed"]>

// Integer enum for priority levels
priority: int<enum=[1, 2, 3]>

// Boolean with only one allowed value (must be true)
required: bool<enum=[true]>

// Float enum for preset values
zoom_level: float<enum=[0.5, 1.0, 1.5, 2.0]>

// String enum with default
theme: str<enum=["light", "dark", "system"]> = "system"
```

## 7. Date and Time Constraints

Special constraints are available for date, time, datetime, and timestamp types.

### 7.1 Date Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `min` | Minimum date (inclusive) | `date<min="2020-01-01">` |
| `max` | Maximum date (inclusive) | `date<max="2029-12-31">` |
| `format` | Date format pattern | `date<format="rfc3339">` |

```ftml
birthdate: date<min="1900-01-01", max="2099-12-31">
custom_date: date<format="%m/%d/%Y">
```

### 7.2 Time Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `format` | Time format pattern | `time<format="iso8601">` |

```ftml
meeting_time: time<format="%H:%M:%S">
```

### 7.3 DateTime Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `min` | Minimum datetime (inclusive) | `datetime<min="2020-01-01T00:00:00Z">` |
| `max` | Maximum datetime (inclusive) | `datetime<max="2029-12-31T23:59:59Z">` |
| `format` | Datetime format pattern | `datetime<format="rfc3339">` |

```ftml
created_at: datetime<min="2020-01-01T00:00:00Z">
expiry: datetime<format="iso8601">
```

### 7.4 Timestamp Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `min` | Minimum timestamp (inclusive) | `timestamp<min=1577836800>` |
| `max` | Maximum timestamp (inclusive) | `timestamp<max=1893456000>` |
| `precision` | Timestamp precision | `timestamp<precision="milliseconds">` |

```ftml
created_ts: timestamp<min=1577836800>
log_ts: timestamp<precision="milliseconds">
```

### 7.5 Date/Time Format Values

The following format values are supported:

| Format Value | Description |
|--------------|-------------|
| `rfc3339` | RFC 3339 format (default for datetime) |
| `iso8601` | ISO 8601 format (more permissive) |
| `%Y-%m-%d` | Custom format using strftime syntax (default for date) |
| `%H:%M:%S` | Custom format using strftime syntax (default for time) |

### 7.6 Timestamp Precision Values

The following precision values are supported:

| Precision Value | Description |
|-----------------|-------------|
| `seconds` | Seconds precision (default) |
| `milliseconds` | Milliseconds precision (13 digits) |
| `microseconds` | Microseconds precision (16 digits) |
| `nanoseconds` | Nanoseconds precision (19 digits) |

## 8. Constraint Combination and Inheritance

### 8.1 Combining Multiple Constraints

Constraints can be combined to create powerful validation rules:

```ftml
username: str<min_length=3, max_length=20, pattern="[a-zA-Z0-9_]+">
price: float<min=0.0, max=1000000.0, precision=2>
```

### 8.2 Constraints with Union Types

When using union types, constraints apply to each applicable type:

```ftml
// Constraints apply to the string type only
id: str<min_length=5, pattern="[A-Z]+">> | int<min=10000>

// Enum applies to string type only
status: str<enum=["active", "inactive"]> | null
```

## 9. Implementation Details

### 9.1 Constraint Parsing

The constraint parser:

1. Extracts constraints from type strings using angle brackets
2. Parses constraint values based on their format (string, number, boolean, list)
3. Normalizes and validates constraint names and values

### 9.2 Constraint Validation

During validation, the implementation:

1. Checks if the value's type matches the expected type
2. Validates the value against each specified constraint
3. Collects all validation errors for comprehensive reporting
4. Generates meaningful error messages with field paths

### 9.3 Validation Order

Constraints are validated in the following order:

1. Type validation (is the value the correct type?)
2. Enum constraints (is the value in the allowed set?)
3. Range constraints (min, max, min_length, max_length)
4. Pattern constraints
5. Collection constraints (unique, required_keys)
6. Custom format and precision constraints

## 10. Best Practices

### 10.1 Clear Constraints

- Use constraints to enforce business rules and data integrity
- Choose descriptive constraint values for clarity
- Document non-obvious constraints with comments

```ftml
// Must be a valid US phone number (10 digits)
phone: str<pattern="^[0-9]{10}$">
```

### 10.2 Balanced Validation

- Use constraints to prevent invalid data, not to implement complex business logic
- Balance strictness with flexibility based on requirements
- Consider the performance impact of complex regex patterns

### 10.3 Effective Defaults

- Ensure default values meet their own constraints
- Use defaults to guide users toward valid values
- Test default values against constraints

```ftml
// Port defaults to a common value within the allowed range
port: int<min=1024, max=65535> = 8080
```

### 10.4 Error Messages

The validation system produces clear error messages that include:

- The field path (e.g., `user.address.zipcode`)
- The constraint that was violated
- The actual value that failed validation
- A human-readable description of the issue