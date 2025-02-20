
# FTML (FlexTag Markup Language) Specification

A data format that combines intuitive design with built-in schemas.

- 🛡️ Robust - Built-in schema validation and type safety
- ✨ Simple - Flat design by default, with powerful nesting when needed
- 🎯 Flexible - Smart defaults and optional fields support

> Note: While FTML works as a standalone markup language, it's designed to be the foundation for [FlexTag's](https://pypi.org/project/flextag/) advanced metadata capabilities, which will be available starting from version 0.3.x. This feature is not yet included in the current release.

## Status: Alpha

FTML is currently in alpha stage and is not yet suitable for production use. While the core functionality is working, thorough testing and refinement are still in progress.

> Note for Users: This document serves as a technical specification for FTML during its alpha phase. User-friendly guides and tutorials are planned for the beta release.

### Current Status 0.0.1
The parser successfully handles basic FTML syntax, including:
- Simple list and dictionaries key-value pairs
- Basic list structures
- Schema validation for simple structures
- Type inference and basic type safety checks

#### Phase 1 (Current - Alpha)
- Stabilizing core functionality and syntax
- Implementing foundational schema validation
- Gathering community feedback
- Bug fixes and improvements
- Technical specification documentation

#### Phase 2 (Upcoming - Beta)
- Thorough testing of deep nesting capabilities
- Comprehensive schema validation testing
- Enhanced type safety verification
- Improved error messages and debugging
- Performance optimization
- Comprehensive unit testing.
- User centered documentation
- Simple in advanced usage tutorials. 
- API stabilization/finalization.

#### Phase 3 (Future)
- Parser optimization and performance profiling
- Potential rewrite in C or Rust for improved speed
- Cross-language support foundation
- Language ports and implementations: JavaScript, Rust, Go...
- Additional languages based on community needs
- Add additional types: data

## Quick Start

First, install FTML via pip:

```bash
pip install ftml
```

Then, try out this simple Python script that demonstrates FTML’s core functionality:

```python
import ftml

# Define FTML data as a string
ftml_data = """
user = {
    name = "Alice"
    age = 28
    skills = ["Python", "Data Analysis"]
}
"""

# Load the FTML data into a Python dictionary
data = ftml.load(ftml_data)

# Modify the data: increment age and add a new skill
data["user"]["age"] += 1
data["user"]["skills"].append("Machine Learning")

# Convert the Python dictionary back to FTML format
ftml_output = ftml.dump(data)

print("Modified FTML Data:")
print(ftml_output)
```

This quick start demonstrates how to load FTML data, modify it programmatically, and dump it back into FTML format.

## Overview

FTML (FlexTag Markup Language) is designed to serve two primary purposes:

1. **Structured Data Markup:**  
   Write data in a clear, flat format with explicit nesting for lists and dictionaries.

2. **Schema Definition & Validation:**  
   Define detailed schemas that enforce type safety, optional fields, defaults, and strict ordering.

FTML supports **inline schemas**, allowing you to embed schema definitions directly within the data, or **external schemas** for reusable validation rules.

---

## Core Principles

- **Flat Structure by Default:**  
  Each item appears on its own line unless explicitly nested.


- **Explicit Nesting:**  
  Use `{}` for dictionaries and `[]` for lists.


- **Type Safety:**  
  Full type safety across all elements - fields, lists, dictionaries, and nested structures are enforced at parse time.


- **Strict Ordering:**  
  The order of items in dictionaries and lists are preserved exactly as written.


- **Optional Fields:**  
  Fields can be marked with `?` (optional) and may specify default values that are used when the field is omitted


- **Schema Support:**  
  Supports both inline schemas (embedded within data) and external schemas for reusable validation rules.

## Syntax

### Basic Structure

FTML provides a simple flat syntax for defining dictionaries and lists:

```plaintext
# Key-value pairs in a dictionary
name = "John",
age: int = 30
```

```plaintext
# List items
"item 1",
"item 2"
```

### Writing Style

#### Writing Lists and Dictionaries
For better readability, prefer multiline format for nested structures:
```plaintext
# Dictionary - Multiline (Recommended)
user = {
    name = "John Smith",
    age = 30
}

# List - Multiline (Recommended)
fruits = [
    "apple",
    "banana",
    "cherry"
]
```

Inline format is supported but should be used sparingly:

```plaintext
# Dictionary - Inline
user = { name = "John Smith", age = 30 }

# List - Inline
fruits = [ "apple", "banana", "cherry" ]
```

While the following style without indentation is supported, it's discouraged as it reduces readability:
```plaintext
# Discouraged - No indentation
users = [
"alice",
"bob",
"charlie"
]

settings = {
name = "Default Profile",
theme = "dark",
notifications = true
}
```

### Assignment Rules

#### Required: Opening Bracket Placement

The opening bracket/brace of a list or dictionary must appear on the same line as the assignment operator:

```plaintext
# Correct - Opening bracket on same line
fruits = [
    "apple",
    "banana",
    "cherry"
]

# Incorrect - Opening bracket on next line
fruits = 
[
    "apple",
    "banana",
    "cherry"
]
```
#### Optional: Closing Bracket Style

The closing bracket placement is flexible, though the following conventions are recommended:

```plaintext
# Preferred for multiline collections
fruits = [
    "apple",
    "banana",
    "cherry"
]

# Valid but not preferred
fruits = [
    "apple",
    "banana",
    "cherry"]

# Preferred for single-line collections
fruits = [ "apple", "banana", "cherry" ]
```

### Comments

FTML supports inline comments similar to YAML. Any text following a `#` on a line is considered a comment and is ignored during parsing.

```plaintext
# This is a full line comment
count = 42  # Inferred as int (positive)
```

### Nesting

For nested structures, use braces `{}` for dictionaries and brackets `[]` for lists.

```plaintext
# Dictionary with nested structure
config = {
    port: int = 8080
    hosts = ["server1", "server2"]
}
```

```plaintext
# List of dictionaries
users = [
    {name: str = "Alice", age: int = 30}
    {name: str = "Bob", age: int = 25}
]
```

### String Literals and Key Formatting

In FTML, all string values must be enclosed in double quotes ("). This rule ensures that strings are clearly delimited during parsing, type inference, and schema validation.

When it comes to dictionary keys, you have two options:
- `Unquoted Keys:` Use an unquoted identifier (e.g., username) when the key contains only alphanumeric characters or underscores.
- `Quoted Keys:` Enclose the key in double quotes if it contains spaces or special characters.
```plaintext
# Simple key (identifier format) with a string value:
username = "alice"
  
# Complex key with spaces must be enclosed in double quotes:
"full name" = "Alice Johnson"
```


### Dynamic Type Inference

FTML leverages **dynamic type inference** to simplify data entry while ensuring strong type safety. This approach allows the parser to automatically determine the type of each value when explicit type annotations are omitted.

#### Inference Rules

- **Numeric Values:**
    - Values composed solely of digits (with an optional leading `-`) are inferred as **integers**.
    - Values containing a decimal point are inferred as **floats**.

  ```plaintext
  count = 42          # Inferred as int (positive)
  balance = -15       # Inferred as int (negative)

  price = 9.99        # Inferred as float (positive)
  discount = -4.75    # Inferred as float (negative)
  ```

- **Boolean Values:**
    - The literals `true` and `false` (case-insensitive) are recognized as **booleans**.

  ```plaintext
  active = true       # Inferred as bool
  enabled = false     # Inferred as bool
  ```

- **Null Values:**
    - The literal `null` represents a **null** value.

  ```plaintext
  middle_name = null  # Inferred as null
  ```

- **String Values:**
    - **All string values must be enclosed in double quotes (`"..."`)** to avoid ambiguity.

  ```plaintext
  name = "Alice"      # Inferred as string
  ```

#### Interaction with Explicit Type Annotations

When a field includes an explicit type annotation (e.g., `age: int = 30`), FTML validates that the inferred type of the value matches the declared type. A mismatch results in a validation error:

```plaintext
# Correct: value matches the declared type.
age: int = 30

# Error: inferred type (string) does not match declared type (int).
age: int = "30"
```

#### Benefits

- **Simplicity:**  
  Users can omit explicit type declarations for many fields, reducing verbosity.

- **Robustness:**  
  Strict inference rules combined with validation against explicit annotations minimize errors during data migration and schema enforcement.

- **Unified Approach:**  
  This model caters to both beginners who favor minimal syntax and advanced users who require precise type control.

By integrating dynamic type inference, FTML provides a flexible yet rigorous framework for data representation.

## Type System

### Basic Types

- `str` - String
- `int` - Integer
- `float` - Floating point number
- `bool` - Boolean
- `null` - Null value
- `list` - List/Array
- `dict` - Dictionary/Object

### Type Annotations

Attach types to fields to define the expected type of each value. The FTML parser uses these annotations to verify that each field’s value matches the declared type, catching mismatches early during parsing.
```plaintext
name: str = "John",
age: int = 30,
active: bool = true
```

### Collection Types

Define the expected types for elements within collections. This tells the FTML parser to verify that every item in the collection matches the specified type.

- Lists:

  `list[int]` means every item in the list must be an integer.
  ```plaintext
  # List of integers
  numbers: list[int] = [1, 2, 3]
  ```

- Dictionaries:

  `dict[str]` indicates that every value in the dictionary must be a string. (Note: Dictionary keys are always treated as strings in FTML.)

  ```plaintext
  # Dictionary with string values
  settings: dict[str] = {
      host = "localhost",
      domain = "example.com"
  }
  ```

### Mixed Dictionary Values

FTML allows dictionaries to contain values of different types. You can either leave the types unspecified or annotate them explicitly for stricter validation.
- Unspecified Value Types:

  When value types are not specified, FTML accepts any type for each field.
  ```plaintext
  # Mixed dictionary with unspecified types
  settings = {
      host = "localhost",      # Inferred as string. 
      port = 8080,             # Inferred as int. 
      domain = "example.com"   # Inferred as string. 
  }
  ```

- Specified Value Types:

  By explicitly annotating each field, you enforce that the value must match the declared type.
  ```plaintext
  # Mixed dictionary with specified types
  settings: dict = {
      host: str = "localhost",
      port: int = 8080,
      domain: str = "example.com"
  }
  ```

### Mixed List Values
FTML supports lists that can either contain elements of various types or enforce homogeneity by specifying the element type.

- Unspecified Element Types:

  When value types are not specified, FTML accepts any type for each list item.
  ```plaintext
  # Mixed list with unspecified element types
  values = [
      "apple",  # Inferred as string. 
      42,       # Inferred as int. 
      true      # Inferred as bool. 
  ]
  ```

- Specified Element Types:

  By explicitly annotating each field, you enforce that the value must match the declared type.
  ```plaintext
  # List with specified element type (all elements must be integers)
  numbers: list = [
      : str "apple",
      : int 42,
      : bool true
  ]
  ```

### Union Types

Use the `|` operator to allow multiple possible types.

```plaintext
# Field can be a string or null
name: str|null = "John"

# Field can be an integer or a string
id: int|str = "A123"
```

### Optional Fields, Defaults, and Nullability

Fields in FTML can be marked as **optional** using the `?` symbol. Optional fields can also specify **default values**, which are used if the field is missing. Additionally, fields can be marked as **nullable**, allowing them to accept `null` as a valid value.

#### **1. Optional Fields (`?`)**

An optional field may or may not appear in the data. If the field is missing, it **does not appear in the result**. If the field is present, it **must match the specified type**.

##### Example:
```plaintext
# schema used for validation. 
user = {
    name = "John",
    age?: int
}
```

- **Valid Input (Field Missing):**
  ```plaintext
  # data to validate
  user = {
      name = "John"
  }
  ```
  **Result:** `{"name": "John"}` (no `age` field).

- **Valid Input (Field Present):**
  ```plaintext
  # data to validate
  user = {
      name = "John",
      age = 30
  }
  ```
  **Result:** `{"name": "John", "age": 30}`.

- **Invalid Input (Type Mismatch):**
  ```plaintext
  # data to validate
  user = {
      name = "John",
      age = "thirty"  # Error: expected int, got string
  }
  ```

#### **2. Optional Fields with Defaults (`? = default`)**

An optional field can specify a **default value**. If the field is missing, the default value is used. If the field is present, it **must match the specified type**.

##### Example:
```plaintext
# schema used for validation. 
user = {
    name = "John",
    age?: int = -1
}
```

- **Valid Input (Field Missing):**
  ```plaintext
  # data to validate
  user = {
      name = "John"
  }
  ```
  **Result:** `{"name": "John", "age": -1}` (default value is used).

- **Valid Input (Field Present):**
  ```plaintext
  # data to validate
  user = {
      name = "John",
      age = 30
  }
  ```
  **Result:** `{"name": "John", "age": 30}`.

- **Invalid Input (Type Mismatch):**
  ```plaintext
  # data to validate
  user = {
      name = "John",
      age = "thirty"  # Error: expected int, got string
  }
  ```

#### **3. Required Fields with Nullability (`: type|null = default`)**

A required field **must always be present**, but it can accept `null` as a valid value. If the field is missing, it **defaults to `null`**. If the field is present, it **must match the specified type** or be `null`.

##### Example:
```plaintext
# schema used for validation. 
user = {
    name = "John",
    age: int|null = null
}
```

- **Valid Input (Field Missing):**
  ```plaintext
  # data to validate
  user = {
      name = "John"
  }
  ```
  **Result:** `{"name": "John", "age": null}` (default `null` value is used).

- **Valid Input (Field Present with Value):**
  ```plaintext
  # data to validate
  user = {
      name = "John",
      age = 30
  }
  ```
  **Result:** `{"name": "John", "age": 30}`.

- **Valid Input (Field Present with Null):**
  ```plaintext
  # data to validate 
  user = {
      name = "John",
      age = null
  }
  ```
  **Result:** `{"name": "John", "age": null}`.

- **Invalid Input (Type Mismatch):**
  ```plaintext
  # data to validate
  user = {
      name = "John",
      age = "thirty"  # Error: expected int or null, got string
  }
  ```

#### **4. Keys with No Values**

FTML allows keys with no values, which default to `null`. This is useful for fields that are explicitly allowed to be `null`.


#####  Example 1: Valid Input with a Default Value

In this schema, the age field is allowed to be missing because it accepts null as a valid value (with a default of null):

```plaintext
# Schema definition
user = {
    name: str = "John",       # Required field with default value "John"
    age: int|null = null      # Field accepts int or null, defaults to null if no value provided
}
```

**Valid Data Input:**

```plaintext
user = {
    name = "John",
    age =                   # Valid: the "=" is required, and the missing value defaults to null.
}
```

**Result:** `{"name": "John", "age": null}` (default `null` value is used).

#### Example 2: Invalid Input Due to Missing Assignment Operator
In FTML, the assignment operator (=) is mandatory. Omitting it causes an error—even if the field might have a default or allowed value.

```plaintext
# Schema definition (Invalid Input Example)
user = {
    name: str = "John",
    score: int             # Required field without default and not nullable
}
```

**Invalid Data Input:**
```plaintext
user = {
    name = "John",
    score                  # Invalid: missing "=" after the key 'score'
}
```

**Result:**

An exception is thrown because every field must include the assignment operator (=) to indicate that the key is present.

#### **Comparison with YAML and JSON**

- **YAML:** Optional fields are not explicitly marked. Missing fields simply do not appear in the result. Keys with no values default to `null`.
- **JSON:** Optional fields are not explicitly marked. Missing fields are treated as `undefined` or omitted. Keys must have values; a key with no value is invalid JSON.

FTML improves on YAML and JSON by providing explicit syntax for optional fields, defaults, and nullability, making data structures more predictable and easier to validate.

### Inline Schemas and Self-Descriptive Data

FTML allows you to embed schema definitions directly within the data, making it **self-descriptive** and **validation-ready**. This section explains how to use inline schemas and self-descriptive data effectively.

#### Inline Schemas

Inline schemas define the expected structure and types of a data structure directly within the data. They are especially useful for ensuring data consistency and enabling validation.

##### Inline dictionary schema
```plaintext
# Inline schema for a dictionary
user: dict{name: str, age: int, email?: str|null} = {
    name = "John",
    age = 30
}
```

##### Inline Nested Schema
```plaintext
"AAPL": list[dict{open: float, high: float, low: float, close: float}] = [
    {open = 107.5, high = 110.0, low = 105.8, close = 109.3},
    {open = 109.3, high = 112.5, low = 108.0, close = 110.8}
]
```

#### Advanced Examples

##### **Mixed Types in Lists (Discouraged):**
```plaintext
fruits = [
    : str "apple",
    : str "banana",
    : int 42  # valid mixed tape. 
]
```

##### **Nested Types:**
```plaintext
config = {
    server: dict{host: str, port: int} = {
        host = "localhost",
        port = 8080
    },
    users: list[dict{name: str, age: int}] = [
        {name = "Alice", age = 30},
        {name = "Bob", age = 25}
    ]
}
```

### Advanced Structures

FTML supports advanced structures through nesting. This section explains how to use these features effectively.

#### **1. Flat Structures**

FTML uses a **flat, one-item-per-line syntax** by default. The **starting structure** must be either a **list** or a **dictionary**. Mixing lists and dictionaries at the top level is not allowed.

##### **Valid: Top-Level Dictionary**
```plaintext
name = "John",
age = 30
```
**Result:**
```json
{"name": "John", "age": 30}
```

##### **Valid: Dictionary of Dictionaries**
```plaintext
user = {name = "John", age = 30},
settings = {active = true, size = 28}
```
**Result:**
```json
{
    "user": {"name": "John", "age": 30},
    "settings": {"active": true, "size": 28}
}
```

##### **Valid: Top-Level List**
```plaintext
"item 1",
"item 2"
```
**Result:**
```plaintext
["item 1", "item 2"]
```

##### **Valid: List of List**
```plaintext
["item 1", "item 2"],
["item 3", "item 4"]
```
**Result:**
```json
[
    ["item 1", "item 2"],
    ["item 3", "item 4"]
]
```

##### **Valid: Advanced Nesting (Dictionary of Lists of Dictionaries)**
```plaintext
"AAPL" = [
    { date = "2025-02-14" open = 107.5 high = 110.0 low = 105.8 close = 109.3 }
    { date = "2025-02-15" open = 109.3 high = 112.5 low = 108.0 close = 110.8 }
]
"MSFT": [
    { date = "2025-02-14" open = 107.5 high = 110.0 low = 105.8 close = 109.3 }
    { date = "2025-02-15" open = 109.3 high = 112.5 low = 108.0 close = 110.8 }
]
```
**Result:**
```json
{
  "AAPL": [
    {"date": "2025-02-14", "open": 100.5, "high": 105.0, "low": 98.7, "close": 102.3},
    {"date": "2025-02-15", "open": 102.3, "high": 108.2, "low": 101.1, "close": 107.5}
  ],
  "MSFT": [
    {"date": "2025-02-14", "open": 107.5, "high": 110.0, "low": 105.8, "close": 109.3},
    {"date": "2025-02-15", "open": 109.3, "high": 112.5, "low": 108.0, "close": 110.8}
  ]
}
```

##### **Invalid: Mixed `dict` and `list` on Top-Level Structure**
```plaintext
name = "John",
age = 30,
"item 1",
"item 2"
```
**Reason:** Mixing dictionaries and lists at the top level is not allowed.

#### **2. Schema Validation for Optional Keys**

FTML introduces the `?` symbol for optional fields in schemas:

| Field Symbol | Meaning                   | Example    |
|--------------|---------------------------|------------|
| `?`          | Optional (0 or 1)         | `name?: str` |
| (none)       | Exactly one (required)    | `name: str`  |

##### **Examples:**

###### **Optional Field:**
```plaintext
users?: list[dict{name: str, age: int}]  # (Optional)
```

###### **Exactly One:**
```plaintext
users: list[dict{name: str, age: int}]  # (Required)
```

## Schema vs. Data Documents

FTML distinguishes between schema documents and data documents:

- **Schema Document:**  
  Contains type definitions, optional indicator `?`, and default values.  
  Used for validating incoming data.

- **Data Document:**  
  Represents the actual data.  
  Can include inline schemas for self-descriptive data.

**Validation Behavior:**
- When a schema is provided (inline or external), the data is validated against it.
    - Missing required fields cause errors.
    - Type mismatches are flagged.
    - Optional fields without defaults, if omitted, may lead to validation errors.

- Without a schema, data is parsed as-is without type enforcement.

## Python API Overview

The FTML Python API provides a simple interface for parsing, modifying, and generating FTML data. It supports schema validation and seamless conversion between FTML and Python dictionaries.

### High-Level API

```python
import ftml

# Define FTML schema and data
ftml_schema = """
user: dict = {
    name: str = "default"
    age: int = 0
    skills: list[str] = []
}
"""

ftml_data = """
user = {
    name = "John"
    age = 30
    skills = ["Python", "Data Analysis"]
}
"""

# Load FTML data into a Python dictionary-like object (FTMLData)
data = ftml.load(ftml_data, schema=ftml_schema)

# Modify the data as you would a normal dict
data["user"]["age"] += 1
data["user"]["skills"].append("Machine Learning")

# For advanced usage, you can access the full internal objects:
print("Full FTMLDocument instance:")
print(data.ftml_document)  # The complete parsed document with all metadata

print("Full FTMLSchema instance:")
print(data.ftml_schema)    # The normalized schema definition

# Convert the Python dictionary back to FTML format
ftml_output = ftml.dump(data)
print("\nFTML Output:\n", ftml_output)

# Save FTML data to a file
with open("output.ftml", "w") as file:
    ftml.dump(data, file)
```

### API Functions

- `ftml.load(data: str, schema: Optional[str] = None) -> FTMLData`  
  Parses FTML data into an FTMLData instance (a dict subclass). If a schema is provided, it validates the data against it. Users can work with the simplified data directly and also access the full internal objects via the `ftml_document` and `ftml_schema` properties.

- `ftml.dump(data: dict, file: Optional[TextIO] = None) -> str`  
  Converts a Python dictionary (or FTMLData) back to FTML format. If a file is provided, the output is written to that file.

- `ftml.validate(data: dict, schema: str) -> bool`  
  Validates a Python dictionary against an FTML schema. Raises a `ValidationError` if the data is invalid.

- `ftml.load_file(path: str, schema: Optional[str] = None) -> dict`  
  Loads FTML data from a file and parses it into an FTMLData instance.

- `ftml.dump_file(data: dict, path: str)`  
  Converts a Python dictionary to FTML format and writes it to a file.

### Internal Classes

The `ftml` module uses the following internal classes for parsing and validation:

- **`FTMLSchema`**
  - `load(schema: str) -> FTMLSchema`: Parses an FTML schema string and returns an `FTMLSchema` object.
  - `validate(data: dict) -> bool`: Validates a Python dictionary against the schema. Raises `ValidationError` if the data is invalid.

- **`FTMLDocument`**
  - `load(data: str, schema: Dict = None) -> FTMLDocument`: Parses an FTML data string and returns an `FTMLDocument` object. If a schema is provided, it validates the data against it.
  - `from_dict(data: dict) -> FTMLDocument`: Creates an `FTMLDocument` object from a Python dictionary.
  - `to_dict() -> dict`: Converts the `FTMLDocument` object to a Python dictionary.
  - `to_ftml() -> str`: Converts the `FTMLDocument` object back to an FTML string.

- **`FTMLData`**  
  A dict subclass that wraps the simplified FTML data. It provides convenient access to:
  - `ftml_document`: The full FTMLDocument instance (with complete metadata).
  - `ftml_schema`: The full FTMLSchema instance (if a schema was provided).

### Key Classes

- **`FTMLSchema`**
  - Parses and caches an FTML schema.
  - Validates data against the schema.

- **`FTMLDocument`**
  - Parses FTML documents and optionally validates them against a cached schema.
  - Provides methods to convert the document to a dict or an FTML string.

- **`FTMLData`**
  - Acts as the primary return type of `ftml.load`.
  - Behaves like a standard dictionary for everyday usage (similar to JSON or YAML data).
  - Exposes advanced metadata (via `ftml_document` and `ftml_schema`) for full round-trip serialization and advanced manipulations.

### Example Usage

```python
import ftml

# Schema definition
schema_text = """
user: dict = {
    name: str = "default"
    age: int = 0
    email?: str|null = null
}
"""

# Data definition
data_text = """
user = {
    name = "John"
    age = 30
}
"""

# Load the FTML data (returns an FTMLData instance)
data = ftml.load(data_text, schema=schema_text)

# The returned FTMLData acts like a normal dictionary:
print("Simplified FTML Data:", data)

# And advanced details are still accessible:
print("Full FTMLDocument instance:", data.ftml_document)
print("Full FTMLSchema instance:", data.ftml_schema)
```

### Contributing
We welcome community input! If you encounter bugs, have suggestions, or want to contribute:
- Open an issue on GitHub for bug reports or feature requests
- Submit pull requests for improvements
- Join discussions in the GitHub discussions section

> Please note that during the alpha phase, the API and syntax may undergo changes based on community feedback and testing results.

### Why FTML?
FTML addresses common pain points in data science workflows that existing markup languages don't solve effectively:
- No schema validation
- Limited type safety
- Poor handling of missing data and defaults
- Complex nested/indented structures

### Looking Forward
While FTML works great as a standalone markup language, its integration with FlexTag opens up powerful possibilities:

**Data Scientists**
- Memory-efficient streaming for large datasets
- Lazy loading to handle huge data files
- Advanced data pipelines through metadata routing
- Schema validation for data integrity

**LLM/AI Development**
- Schema validation for response structure
- Type checking for parsed outputs
- Flexible metadata for routing and processing
- Raw text sections for prompt/response handling

For more information about using FTML with FlexTag, visit the [FlexTag documentation](https://pypi.org/project/flextag/).
