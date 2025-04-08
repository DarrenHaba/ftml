# FTML Schema System Developer Guide

## Introduction

The FTML Schema System provides a robust framework for defining, parsing, and validating structured data in FTML format. This document serves as a comprehensive guide for developers working with or extending the schema system.

### Design Philosophy

The schema system was rebuilt with these core principles:

1. **Separation of Concerns** - Each component has a single, well-defined responsibility
2. **Testability** - Every component can be tested in isolation
3. **Maintainability** - Clean interfaces and clear documentation
4. **Extensibility** - Well-defined extension points for new types and constraints
5. **Debuggability** - Comprehensive logging and visualization tools

## System Architecture

The schema system is organized into several focused modules, each with a specific responsibility:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Schema Parser  │───►│  Union Parser   │    │ Constraint      │
│                 │    │                 │◄───│ Parser          │
└────────┬────────┘    └─────────────────┘    └─────────────────┘
         │                                            ▲
         │                                            │
         ▼                                            │
┌─────────────────┐    ┌─────────────────┐    ┌──────┴──────────┐
│  Schema AST     │◄───┤  Type System    │───►│ Type Validators │
│                 │    │                 │    │                 │
└────────┬────────┘    └─────────────────┘    └─────────────────┘
         │                      ▲
         │                      │
         ▼                      │
┌─────────────────┐    ┌────────┴────────┐
│  Schema         │───►│ Schema Debug    │
│  Validator      │    │                 │
└─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Schema Text** → **Schema Parser** → **Schema AST**
2. **Schema AST** + **Data** → **Schema Validator** → **Validation Results**

## Module Details

### 1. `schema_ast.py`

Defines the Abstract Syntax Tree (AST) nodes that represent schema types.

**Key Classes:**
- `SchemaTypeNode`: Base class for all schema type nodes
- `ScalarTypeNode`: Represents scalar types (str, int, float, bool, null)
- `UnionTypeNode`: Represents union types (type1 | type2 | ...)
- `ListTypeNode`: Represents list types ([item_type])
- `ObjectTypeNode`: Represents object types ({field1: type1, ...})

**Responsibilities:**
- Provide a structured representation of schema types
- Store type-specific information (constraints, defaults, etc.)

### 2. `union_parser.py`

Handles parsing of union type expressions.

**Key Classes:**
- `UnionParser`: Parses union type expressions into component types

**Responsibilities:**
- Split union types respecting brackets and nesting
- Detect top-level unions vs. nested unions

### 3. `constraint_parser.py`

Extracts and parses constraints from type definitions.

**Key Classes:**
- `ConstraintParser`: Parses constraints specified in angle brackets

**Responsibilities:**
- Extract constraints from type strings
- Parse constraint values to appropriate types
- Validate constraint consistency

### 4. `type_system.py`

Provides a registry for type definitions and validation rules.

**Key Classes:**
- `TypeSystem`: Registry of types and their validators

**Responsibilities:**
- Register and manage types
- Register and manage constraint validators
- Track scalar and collection types

### 5. `schema_parser.py`

Main parser that converts schema text to an AST.

**Key Classes:**
- `SchemaParser`: Parses schema text into a structured AST

**Responsibilities:**
- Remove comments from schema text
- Parse field definitions
- Identify and parse types
- Handle multiline structures
- Coordinate with specialized parsers

### 6. `type_validators.py`

Provides validators for different types of values.

**Key Classes:**
- `TypeValidator`: Base class for all type validators
- `ScalarValidator`: Validates scalar values
- `UnionValidator`: Validates union types
- `ListValidator`: Validates list values
- `ObjectValidator`: Validates object values

**Responsibilities:**
- Validate values against type definitions
- Validate constraints
- Generate meaningful error messages

### 7. `schema_validator.py`

Coordinates validation of data against schemas.

**Key Classes:**
- `SchemaValidator`: Validates data against schema definitions

**Responsibilities:**
- Apply defaults to data
- Coordinate type-specific validation
- Track validation paths for error reporting

### 8. `schema_debug.py`

Provides utilities for debugging schema components.

**Key Functions:**
- `visualize_schema_ast()`: Creates a textual representation of a schema AST
- `log_schema_ast()`: Logs schema AST structure
- `log_schema_parse_process()`: Logs the schema parsing process

**Responsibilities:**
- Visualize schema structures
- Format and log schema components for debugging

## Extension Points

### Adding New Types

To add a new scalar type:

1. Add the type name to the `scalar_types` set in `TypeSystem`
2. Register a validator function for the type
3. Implement constraint validation for the type

Example:

```python
# In type_system.py
def __init__(self):
    # Add to scalar_types
    self.scalar_types.add("email")
    
    # Register validator
    self.register_type("email", validate_email, is_scalar=True)
    
    # Register constraint validators
    self.register_constraint_validator("email", "domain", validate_email_domain)

# Define validators
def validate_email(value, type_info, path):
    if not isinstance(value, str) or "@" not in value:
        return [f"Expected email at '{path}', got {value}"]
    return []

def validate_email_domain(value, constraint_value, path):
    if not value.endswith(constraint_value):
        return [f"Email at '{path}' must have domain {constraint_value}"]
    return []
```

### Adding New Constraints

To add a new constraint:

1. Update the constraint parser to recognize the constraint
2. Add a constraint validator function
3. Register the constraint validator with the type system

Example:

```python
# In type_validators.py - ScalarValidator class
def _validate_constraint(self, value, type_name, constraint_name, constraint_value, path):
    # Add new constraint handling
    if constraint_name == "uppercase" and type_name == "str":
        if constraint_value is True and not value.isupper():
            return [f"String at '{path}' must be uppercase"]
    
    # Handle existing constraints...
    return []
```

### Extending Validation Logic

To extend validation logic:

1. Subclass the appropriate validator
2. Override the `validate()` method
3. Register the validator with the type system

Example:

```python
class EnhancedStringValidator(ScalarValidator):
    def validate(self, value, type_info, path):
        # First apply basic validation
        errors = super().validate(value, type_info, path)
        if errors:
            return errors
            
        # Add custom validation
        if type_info.get("type") == "str" and len(value) > 1000:
            errors.append(f"String at '{path}' exceeds reasonable length")
        
        return errors

# Register in the type system
type_system.register_validator("str", EnhancedStringValidator())
```

## Testing Guidelines

### Unit Testing Approach

1. **Test Each Component Separately**
    - Test parsing without validation
    - Test validation with pre-parsed schemas
    - Test constraint extraction independently

2. **Focus on Edge Cases**
    - Empty inputs
    - Malformed inputs
    - Boundary conditions
    - Complex nested structures

3. **Test Error Handling**
    - Verify appropriate exceptions are raised
    - Check error messages are informative

### Test Structure

Organize tests by module and functionality:

- `test_schema_parser.py` - Tests for basic schema parsing
- `test_constraints.py` - Tests for constraint parsing and validation
- `test_union_types.py` - Tests for union type handling
- `test_default_values.py` - Tests for default value handling

### Test Coverage Goals

Aim for 100% coverage of:
- Public API
- Error handling paths
- Edge cases
- Default value resolution

## Best Practices

### Code Organization

1. **Keep Modules Focused**
    - Each module should have a clear, single responsibility
    - Avoid adding unrelated functionality to existing modules

2. **Use Clear Interfaces**
    - Define public API methods clearly
    - Document parameter and return types

3. **Isolate Side Effects**
    - Keep parsing pure (no external side effects)
    - Centralize logging and error handling

### Naming Conventions

1. **Consistent Method Names**
    - `parse_*` for parsing functions
    - `validate_*` for validation functions
    - `apply_*` for functions that modify data

2. **Clear Class Names**
    - Use `*Node` suffix for AST node classes
    - Use `*Parser` suffix for parser classes
    - Use `*Validator` suffix for validator classes

3. **Private Methods**
    - Prefix private methods with underscore
    - Document purpose even for private methods

### Error Handling

1. **Use Specific Exceptions**
    - `FTMLParseError` for syntax errors
    - `FTMLValidationError` for validation errors

2. **Provide Context**
    - Include field path in error messages
    - Explain why validation failed

3. **Centralize Error Creation**
    - Use helper methods to ensure consistent errors
    - Include line/column information when available

### Logging

1. **Log Key Events**
    - Schema parsing start/end
    - Type resolution
    - Validation decisions

2. **Use Appropriate Log Levels**
    - `DEBUG` for detailed parsing info
    - `INFO` for normal operations
    - `WARNING` for non-fatal issues
    - `ERROR` for fatal errors

3. **Include Context**
    - Log field names
    - Log value excerpts (truncated if long)
    - Log decision points in complex logic

## Common Pitfalls

### Anti-Patterns to Avoid

1. **Mixing Parsing and Validation**
    - Keep these as separate steps
    - Don't validate during parsing

2. **Global State**
    - Avoid shared mutable state
    - Pass state explicitly as parameters

3. **Deep Nesting**
    - Extract complex logic to helper methods
    - Use early returns for validation

4. **Implicit Type Conversion**
    - Be explicit about type conversions
    - Document conversion behavior

### Lessons Learned

1. **Explicit is Better Than Implicit**
    - Clear error messages help debugging
    - Document behavior with examples

2. **Composability Over Complexity**
    - Complex features should be built from simple ones
    - Favor composition over inheritance

3. **Test-Driven Development**
    - Write tests before implementing features
    - Use tests to clarify requirements

## Examples

### Basic Schema Parsing

```python
from ftml.schema_parser import SchemaParser
from ftml.schema_debug import log_schema_ast

# Parse a schema
parser = SchemaParser()
schema_text = """
user: {
    name: str<min_length=3>,
    age: int<min=0>,
    email?: str
}
"""
schema = parser.parse(schema_text)

# Debug the parsed schema
log_schema_ast(schema["user"], "User Schema")
```

### Schema Validation

```python
from ftml.schema_parser import SchemaParser
from ftml.schema_validator import SchemaValidator

# Parse schema
parser = SchemaParser()
schema = parser.parse("config: {debug: bool, port: int<min=1024, max=65535>}")

# Create validator
validator = SchemaValidator(schema)

# Validate data
data = {"config": {"debug": True, "port": 8080}}
errors = validator.validate(data)

if not errors:
   print("Validation successful")
else:
   for error in errors:
      print(f"Error: {error}")
```

### Adding Custom Type

```python
from ftml.type_system import TypeSystem
from ftml.type_validators import ScalarValidator

# Create custom validator
class EmailValidator(ScalarValidator):
    def _validate_type(self, value, type_name, path):
        if type_name == "email":
            if not isinstance(value, str) or "@" not in value:
                return [f"Expected email at '{path}', got {value}"]
            return []
        return super()._validate_type(value, type_name, path)

# Register with type system
type_system = TypeSystem()
type_system.register_type("email", EmailValidator(), is_scalar=True)
```

## Conclusion

By following this guide and adhering to the design principles, you can maintain and extend the FTML schema system while preserving its clarity and reliability. Remember that the key to preventing "spaghetti code" is disciplined adherence to separation of concerns, thorough testing, and clear documentation.