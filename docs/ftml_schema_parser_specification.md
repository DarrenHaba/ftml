# FTML Schema Parser Internals

## 1. Overview

This document describes the internal workings of the FTML Schema Parser, which is responsible for parsing schema definitions and validating data against them. The Schema Parser focuses on type safety and validation rules for FTML documents.

The FTML Schema system provides a powerful yet straightforward way to define data structures and validation rules. Its key capabilities include:

- **Type Safety**: Parses type definitions (`str`, `int`, `float`, `bool`, etc.) for strong typing
- **Constraints**: Handles validation constraints like `min`, `max`, `pattern`, etc. in angle brackets
- **Unions**: Processes union types with the pipe operator (`str | int | null`)
- **Defaults**: Manages default values for fields that aren't provided
- **Comment Handling**: Comments in schema files are parsed but discarded during processing - they are not preserved for round-trip serialization
- **Purpose**: Designed for defining data structure and validation rules, not document preservation

```ftml
// This comment will be discarded by the Schema Parser
user: {
  name: str<min_length=2>,  // This constraint is preserved, but comment is discarded
  email?: str = "default@example.com"  // Optional with default value
}
```

## 2. Schema AST Structure

The Schema Abstract Syntax Tree (AST) represents the hierarchical structure of an FTML schema definition.

### 2.1 Schema Node Types

The Schema AST consists of specialized node types:

| Node Type | Description | Example Schema |
|-----------|-------------|----------------|
| `ScalarTypeNode` | Represents primitive types | `field: str` |
| `UnionTypeNode` | Represents union types | `field: str \| int` |
| `ListTypeNode` | Represents list types | `field: [int]` |
| `ObjectTypeNode` | Represents object types | `field: {prop: str}` |

All schema type nodes inherit from a base `SchemaTypeNode` class, which provides common properties:

```python
class SchemaTypeNode:
   def __init__(self):
      self.constraints = {}
      self.has_default = False
      self.default = None
      self.optional = False
```







### 2.2 Schema AST Example

```
// Schema definition
name: str<min_length=3>
age?: int<min=0> = 18
address: {
  street: str,
  city: str,
  zip: str<pattern="[0-9]{5}">
}
tags: [str]<min=1>
```

Would be represented as:

```
SchemaTypeNode (root)
├── name: ScalarTypeNode(str)
│     └── constraints: {"min_length": 3}
├── age: ScalarTypeNode(int)
│     ├── constraints: {"min": 0}
│     ├── has_default: True
│     ├── default: 18
│     └── optional: True
├── address: ObjectTypeNode
│     └── fields:
│         ├── street: ScalarTypeNode(str)
│         ├── city: ScalarTypeNode(str)
│         └── zip: ScalarTypeNode(str)
│             └── constraints: {"pattern": "[0-9]{5}"}
└── tags: ListTypeNode
      ├── item_type: ScalarTypeNode(str)
      └── constraints: {"min": 1}
```

## 3. Parsing Pipeline

The schema parsing process involves multiple specialized components working together.

### 3.1 Schema Parsing Stages

1. **Tokenization**:
    - The schema definition is first tokenized using the main FTML tokenizer
    - Comments are filtered out - schema parser ignores comments

2. **Schema Parsing**:
    - Parse field declarations with types and constraints
    - Construct schema type nodes for each field
    - Build hierarchical schema structure

3. **Constraint Parsing**:
    - Extract and parse constraints in angle brackets (`<min=0, max=100>`)
    - Convert constraint values to appropriate types

4. **Union Type Parsing**:
    - Handle pipe-separated union type expressions (`str | int | null`)
    - Resolve nested union definitions

### 3.2 Schema Parser Components

The schema parser consists of several specialized components:

| Component | Purpose |
|-----------|---------|
| `SchemaParser` | Main component that orchestrates the schema parsing process |
| `ConstraintParser` | Extracts and parses constraints in angle brackets |
| `UnionParser` | Handles union type expressions with pipe operator |
| `TypeSystem` | Registry of available types and their validation functions |

## 4. Type System

The schema parser includes a type system that defines the available types and their validation rules.

### 4.1 Built-in Types

The FTML schema system includes these built-in scalar types:

| Type | Description | Example |
|------|-------------|---------|
| `str` | String values | `field: str` |
| `int` | Integer values | `field: int` |
| `float` | Floating-point values | `field: float` |
| `bool` | Boolean values | `field: bool` |
| `null` | Null value | `field: null` |
| `any` | Any type (no validation) | `field: any` |
| `date` | Date values | `field: date` |
| `time` | Time values | `field: time` |
| `datetime` | Date and time values | `field: datetime` |
| `timestamp` | Unix timestamp values | `field: timestamp` |

### 4.2 Collection Types

In addition to scalar types, two collection types are supported:

| Type | Description | Example |
|------|-------------|---------|
| `list` | Ordered list of items | `field: [str]` |
| `dict` | Key-value mapping | `field: {str: int}` |

### 4.3 Type Constraints

Each type can have specific constraints:

```
// String constraints
name: str<min_length=3, max_length=50>

// Number constraints
age: int<min=0, max=120>

// Collection constraints
tags: [str]<min=1, max=10>
```

## 5. Constraint Parsing

Constraints are specified in angle brackets after a type and provide additional validation rules.

### 5.1 Constraint Syntax

```
field: type<constraint1=value1, constraint2=value2>
```

### 5.2 Constraint Value Types

Constraint values can be:

| Value Type | Example | Notes |
|------------|---------|-------|
| String | `<pattern="[a-z]+">` | Quoted strings |
| Number | `<min=0>` | Integer or float |
| Boolean | `<unique=true>` | true or false |
| Null | `<default=null>` | null literal |
| List | `<enum=["a", "b", "c"]>` | Array of values |

### 5.3 Constraint Extraction Process

The constraint parser:

1. Finds constraint boundaries (`<...>`)
2. Extracts the base type before the constraints
3. Parses the constraint string into a dictionary
4. Converts constraint values to appropriate Python types

```python
def extract_constraints(type_str):
    # Finds <...> in "str<min_length=3, max_length=10>"
    if '<' not in type_str or '>' not in type_str:
        return type_str, {}
        
    constraint_start = type_str.find('<')
    constraint_end = type_str.rfind('>')
    base_type = type_str[:constraint_start].strip()
    constraint_str = type_str[constraint_start+1:constraint_end].strip()
    
    # Parse constraints into a dictionary
    constraints = parse_constraint_string(constraint_str, base_type)
    return base_type, constraints
```

## 6. Union Type Parsing

Union types allow a field to accept multiple types of values.

### 6.1 Union Syntax

```
field: type1 | type2 | type3
```

### 6.2 Union Parsing Process

The union parser:

1. Identifies union types by finding pipe (`|`) characters outside of brackets
2. Splits the type string into individual type parts
3. Recursively parses each part as its own type
4. Constructs a `UnionTypeNode` with all subtypes

```python
def split_union_parts(type_str):
    parts = []
    current = ""
    bracket_level = 0  # Track nesting level of all bracket types
    
    for char in type_str:
        if char in '{[<':
            bracket_level += 1
            current += char
        elif char in '}]>':
            bracket_level -= 1
            current += char
        elif char == '|' and bracket_level == 0:
            # Only split on pipes outside all brackets
            parts.append(current.strip())
            current = ""
        else:
            current += char
            
    if current.strip():
        parts.append(current.strip())
        
    return parts
```

## 7. Schema Validation

After a schema is parsed, it can be used to validate data against the defined rules.

### 7.1 Validation Process

Schema validation follows these steps:

1. **Apply Defaults**:
    - Apply default values for missing fields
    - Only set defaults for fields not present in data

2. **Type Validation**:
    - Check that values match their expected types
    - Convert string values to proper types if needed (dates, times)

3. **Constraint Validation**:
    - Apply type-specific constraints
    - Collect all validation errors (not just the first)

4. **Error Reporting**:
    - Generate detailed error messages
    - Include field paths for nested validation errors

### 7.2 Type-Specific Validators

Each type has specialized validators:

| Validator | Purpose |
|-----------|---------|
| `ScalarValidator` | Validates primitive types and their constraints |
| `ListValidator` | Validates lists and their item types |
| `ObjectValidator` | Validates objects and their properties |
| `UnionValidator` | Tries each subtype until one validates successfully |

### 7.3 Validation Example

```python
# Define schema
schema = parse_schema("""
name: str<min_length=2>
age: int<min=0>
addresses: [{
  street: str,
  city: str,
  zip: str<pattern="[0-9]{5}">
}]
""")

# Validate data
data = {
  "name": "John",
  "age": 30,
  "addresses": [
    {"street": "123 Main St", "city": "Anytown", "zip": "12345"},
    {"street": "456 Park Ave", "city": "Somewhere", "zip": "abcde"}  # Invalid zip
  ]
}

errors = validate_data(data, schema)
# errors would include: "String at 'addresses[1].zip' does not match pattern: [0-9]{5}"
```

## 8. Date and Time Handling

FTML Schema includes specialized handling for date and time types.

### 8.1 Date/Time Types

| Type | Description | Format |
|------|-------------|--------|
| `date` | Calendar date | "2023-01-15" |
| `time` | Time of day | "14:30:00" |
| `datetime` | Date and time | "2023-01-15T14:30:00Z" |
| `timestamp` | Unix timestamp | 1673791800 |

### 8.2 Date/Time Constraints

Each date/time type supports specific constraints:

| Constraint | Type | Example |
|------------|------|---------|
| `format` | date, time, datetime | `date<format="rfc3339">` |
| `min` | date, time, datetime, timestamp | `date<min="2020-01-01">` |
| `max` | date, time, datetime, timestamp | `date<max="2029-12-31">` |
| `precision` | timestamp | `timestamp<precision="milliseconds">` |

### 8.3 Date/Time Validation

The validation process for date/time types:

1. Validates format according to specified format string
2. Performs range checking for min/max constraints
3. For timestamps, validates according to precision

## 9. Schema Integration

The schema system integrates with the main FTML system through public API functions.

### 9.1 Public API Functions

| Function | Purpose |
|----------|---------|
| `parse_schema(schema_data)` | Parse an FTML schema definition |
| `validate_data(data, schema, strict=True)` | Validate data against a schema |
| `apply_schema_defaults(data, schema)` | Apply defaults from schema to data |

### 9.2 Integration Example

```python
import ftml

# Parse a schema from string or file
schema = ftml.parse_schema("""
user: {
  name: str<min_length=2>,
  email: str,
  age?: int<min=0> = 18
}
""")

# Load data with schema validation
data = ftml.load("user.ftml", schema=schema)

# Apply defaults from schema
data_with_defaults = ftml.apply_schema_defaults(data, schema)

# Validate data against schema
errors = ftml.validate_data(data, schema)
if errors:
    print("Validation errors:", errors)
```

## 10. Error Handling

The schema system provides detailed error handling for both parsing and validation.

### 10.1 Schema Parsing Errors

Parsing errors include:

- Invalid type syntax
- Unknown types
- Malformed constraints
- Invalid default values
- Syntax errors in field definitions

### 10.2 Validation Errors

Validation errors include:

- Type mismatch errors
- Constraint violations
- Missing required fields
- Invalid structure errors

### 10.3 Error Context

Errors include detailed context:

- Field path (e.g., `user.addresses[0].zip`)
- Expected type or constraint
- Actual value that failed validation
- Detailed message explaining the issue

## 11. Implementation Notes

### 11.1 Schema Parser Limitations

Current limitations include:

- Comments in schema files are ignored

### 11.2 Performance Considerations

For efficient schema validation:

- Schema parsing is done once and the result cached
- Validation is optimized for common cases
- Type system uses lazy constraint validation
- Default values are only applied when needed

### 11.3 Extension Points

The schema system can be extended through:

- Registering custom types
- Adding custom constraint validators
- Implementing advanced validation rules
- Extending the type system

## 12. Best Practices

### 12.1 Schema Design

- Use descriptive field names
- Add constraints to ensure data quality
- Use appropriate types for values
- Set sensible default values
- Make fields optional when appropriate

### 12.2 Schema Organization

- Group related fields together
- Use nested objects for complex structures
- Keep schemas flat when possible
- Document the schema with comments

### 12.3 Validation Strategy

- Validate early in data processing
- Handle validation errors gracefully
- Provide user-friendly error messages
- Consider partial validation for large datasets