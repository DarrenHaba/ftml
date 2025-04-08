# FTML Scalars Specification

## 1. Overview

FTML (FlexTag Markup Language) supports five scalar data types that represent basic values:

| Type | Description | Example | Schema Notation |
|------|-------------|---------|----------------|
| String | Text enclosed in quotes | `"Hello world"` | `str` |
| Integer | Whole numbers | `42` | `int` |
| Float | Decimal numbers | `3.14` | `float` |
| Boolean | True/false values | `true` | `bool` |
| Null | Absence of a value | `null` | `null` |

These scalars serve as the building blocks for more complex data structures in FTML.

## 2. String Type

Strings in FTML represent textual data.

### 2.1 Double-Quoted Strings

The primary string format uses double quotes with escape sequences:

```ftml
name = "Hello, world!"
```

#### 2.1.1 Escape Sequences

Double-quoted strings support the following escape sequences:

| Sequence | Represents |
|----------|------------|
| `\"` | Double quote |
| `\\` | Backslash |
| `\n` | Newline |
| `\r` | Carriage return |
| `\t` | Tab |
| `\b` | Backspace |
| `\f` | Form feed |

Example:
```ftml
message = "Line 1\nLine 2"
path = "C:\\Users\\Username"
quote = "He said, \"Hello!\""
```

### 2.2 Single-Quoted Strings

FTML also supports single-quoted strings with simpler escaping rules:

```ftml
name = 'Hello, world!'
```

In single-quoted strings, a single quote character is escaped by doubling it:

```ftml
message = 'It''s working!'  // Represents: It's working!
```

Single-quoted strings do not process other escape sequences like `\n` or `\t`; these are treated as literal characters.

### 2.3 Multiline Strings

For multiline text, use escape sequences in double-quoted strings:

```ftml
message = "This is a multiline\nstring with an explicit\nnewline character."
```

### 2.4 String Constraints

In schema definitions, strings can have constraints:

```ftml
// Schema definition
username: str<min_length=3, max_length=20, pattern="[a-zA-Z0-9_]+">
email: str<format="email">
```

## 3. Integer Type

Integers represent whole numbers without a decimal component.

### 3.1 Syntax

Integers can be positive, negative, or zero:

```ftml
positive = 42
negative = -17
zero = 0
```

### 3.2 Range

The valid range depends on the implementation, but typically corresponds to the host language's integer limits (e.g., 64-bit signed integers).

### 3.3 Integer Constraints

In schema definitions, integers can have constraints:

```ftml
// Schema definition
port: int<min=1024, max=65535>
age: int<min=0>
```

## 4. Float Type

Floats represent decimal numbers with fractional components.

### 4.1 Syntax

Floats must include a decimal point:

```ftml
pi = 3.14159
negative = -2.718
zero = 0.0
```

### 4.2 Range and Precision

The valid range and precision depend on the implementation, but typically correspond to IEEE 754 double-precision floating-point format.

### 4.3 Float Constraints

In schema definitions, floats can have constraints:

```ftml
// Schema definition
probability: float<min=0.0, max=1.0>
temperature: float<precision=2>  // Limits decimal places to 2
```

## 5. Boolean Type

Booleans represent logical true or false values.

### 5.1 Syntax

Only lowercase `true` and `false` are valid:

```ftml
debug = true
enabled = false
```

### 5.2 Boolean Constraints

In schema definitions, booleans can have default values:

```ftml
// Schema definition
debug: bool = false
feature_enabled: bool = true
```

## 6. Null Type

Null represents the absence of a value.

### 6.1 Syntax

The keyword `null` (lowercase) represents a null value:

```ftml
value = null
optional_setting = null
```

### 6.2 Null in Schemas

In schemas, null can be used as part of union types to indicate optional values:

```ftml
// Schema definition
middle_name: str | null  // Can be a string or null
```

## 7. Type Coercion and Conversion

### 7.1 No Implicit Coercion

FTML does not perform implicit type coercion. Values must match their expected types.

```ftml
// These are different types
int_value = 42
string_value = "42"
float_value = 42.0
bool_value = true
```

### 7.2 Schema-Based Conversion

When using schema validation, some implementations may perform type conversion if the value is compatible with the target type:

```ftml
// Schema definition
port: int

// May be interpreted as valid in some implementations
config = {
  port = "8080"  // String might be converted to int during validation
}
```

## 8. Scalar Values in Collections

Scalars can be used in both objects and lists:

```ftml
// In objects
person = {
  name = "Alice",
  age = 30,
  height = 5.8,
  active = true,
  middle_name = null
}

// In lists
values = [
  "string",
  42,
  3.14,
  true,
  null
]
```

## 9. Special Cases and Edge Cases

### 9.1 Empty Strings

Empty strings are valid:

```ftml
empty = ""
also_empty = ''
```

### 9.2 Number Notation

Standard decimal notation is required:

```ftml
// Valid
standard = 1000

// Invalid in FTML (not supported)
// scientific = 1e3
// hex = 0x3E8
// octal = 0o1750
// binary = 0b1111101000
```

### 9.3 Boolean Case Sensitivity

Boolean values must be lowercase:

```ftml
// Valid
valid = true

// Invalid
// invalid = TRUE
// invalid = True
```

## 10. Best Practices

### 10.1 String Usage

- Use double quotes for strings containing escape sequences
- Use single quotes for simple strings, especially those containing double quotes
- Consider readability when choosing between quotation styles

### 10.2 Number Precision

- Use integers when representing whole numbers
- Use floats only when fractional precision is required
- Be aware of floating-point precision limitations

### 10.3 Boolean Clarity

- Use booleans for true/false flags
- Choose key names that make boolean values intuitive (e.g., `is_enabled` instead of `status`)

### 10.4 Null Values

- Use null when a value is intentionally absent
- In schemas, consider using union types with null to indicate optional values

### 10.5 Type Consistency

- Maintain consistent types for the same logical value throughout a document
- Use schemas to enforce type constraints when data integrity is important