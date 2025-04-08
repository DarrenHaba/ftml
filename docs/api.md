#   FTML Public API Reference

##   1. Overview

The FTML (FlexTag Markup Language) public API provides a clean, straightforward interface for loading, modifying, and saving FTML data. This document serves as a reference for the core functions and classes available to users of the FTML library.

##   2. Core Functions

###   2.1 Loading FTML Data

####   `load(ftml_data, schema=None, strict=True, preserve_comments=True, validate=True)`

Parses FTML data into a Python dictionary.

**Parameters:**

* `ftml_data` (str or PathLike): FTML content as a string or a path to an FTML file
* `schema` (str or dict, optional): Schema for validation, as a string, file path, or dict
* `strict` (bool, default=True): Whether to enforce strict validation
* `preserve_comments` (bool, default=True): Whether to preserve comments for round-trip serialization
* `validate` (bool, default=True): Whether to validate against the schema

**Returns:**

* A dictionary containing the parsed data, with comments preserved by default.

**Exceptions:**

* `FTMLParseError`: If there is a syntax error in the FTML
* `FTMLValidationError`: If validation against the schema fails

**Example:**

```python
import ftml

#   Load from a file
config = ftml.load("config.ftml")

#   Load from a string with schema validation
schema_path = "config.ftml-schema"
config_str = """
name = "My App"
version = "1.0"
"""
config = ftml.load(config_str, schema=schema_path)

#   Load without preserving comments
data = ftml.load("data.ftml", preserve_comments=False)
```

###   2.2 Saving FTML Data

####   `dump(data, fp=None, schema=None, strict=True, include_comments=True, validate=True)`

Serializes a Python dictionary to FTML text.

**Parameters:**

* `data` (dict): The data to serialize
* `fp` (str, PathLike, or file-like object, optional): Output destination; if None, returns a string
* `schema` (str or dict, optional): Schema for validation, as a string, file path, or dict
* `strict` (bool, default=True): Whether to enforce strict validation
* `include_comments` (bool, default=True): Whether to include preserved comments
* `validate` (bool, default=True): Whether to validate against the schema before serializing

**Returns:**

* If `fp` is None, returns the serialized FTML text
* Otherwise, returns None after writing to the specified file

**Exceptions:**

* `FTMLError`: If the data cannot be serialized
* `FTMLValidationError`: If validation against the schema fails

**Example:**

```python
import ftml

#   Create or modify data
config = {
    "name": "My App",
    "version": "1.0",
    "settings": {
        "port": 8080,
        "debug": True
    }
}

#   Save to a file
ftml.dump(config, "config.ftml")

#   Get as a string
ftml_text = ftml.dump(config)

#   Save with schema validation
ftml.dump(config, "config.ftml", schema="config.ftml-schema")
```

###   2.3 Schema Loading

####   `load_schema(schema_data)`

Parses an FTML schema into a schema object.

**Parameters:**

* `schema_data` (str or PathLike): Schema content as a string or path to a schema file

**Returns:**

* A dictionary containing the parsed schema

**Exceptions:**

* `FTMLParseError`: If there is a syntax error in the schema

**Example:**

```python
import ftml

#   Load a schema from a file
schema = ftml.load_schema("user.schema.ftml")

#   Use the schema for validation
user_data = ftml.load("user.ftml", schema=schema)
```

##   3. The FTMLDict Class

###   3.1 Overview

The `FTMLDict` is a dictionary subclass that can be used to maintain FTML structure and comments during modifications. It behaves like a normal dictionary but provides capabilities for preserving formatting when saving back to FTML.

###   3.2 Usage

`FTMLDict` instances are typically created automatically by the `load()` function when `preserve_comments=True`.

```python
import ftml

# Sample FTML content with comments
ftml_content = """
//! Configuration for My App
// Main settings section
name = "My App"  // Application name
version = "1.0"  // Current version

// Server configuration
settings = {
    //! Important server settings
    port = 8080,  // Default port
    debug = false  // Production mode
}
"""

# Load FTML with comments preserved (default behavior)
data = ftml.load(ftml_content)  # Returns an FTMLDict

# Use like a normal dictionary
print(f"App name: {data['name']}")
print(f"Current version: {data['version']}")

# Modify values
data["version"] = "2.0"  # Update version
data["settings"]["debug"] = True  # Enable debug mode

# Serialize back to FTML with comments preserved
modified_ftml = ftml.dump(data)

# Print the result - notice comments are preserved
print("\nModified FTML with preserved comments:")
print(modified_ftml)

# Expected output will look like:
"""
Modified FTML with preserved comments:
//! Configuration for My App
// Main settings section
name = "My App"  // Application name
version = "2.0"  // Current version

// Server configuration
settings = {
    //! Important server settings
    port = 8080,  // Default port
    debug = true  // Production mode
}
```

Expected output:
```
App name: My App
Current version: 1.0

Modified FTML with preserved comments:
//! Configuration for My App

// Main settings section
name = "My App"  // Application name

version = "2.0"  // Current version

// Server configuration
settings = {
    //! Important server settings
    port = 8080,  // Default port
    debug = true  // Production mode
}
```

##   4. Common Workflows

###   4.1 Reading and Modifying Configuration

```python
import ftml

# Example configuration content
config_str = """
name = "My App"
version = "2.0"
settings = {
    port = 8080,
    debug = false
}
"""

# Load configuration from string 
# (You would typically use a file: config = ftml.load("config.ftml"))
config = ftml.load(config_str)

# Read values from the configuration
port = config["settings"]["port"]
print(f"Current port: {port}")  # Output: Current port: 8080

# Modify values
config["settings"]["debug"] = True  # Enable debug mode
config["version"] = "2.1"           # Update version
print(f"Updated version: {config['version']}")  # Output: Updated version: 2.1

# Get the modified configuration
modified_config = ftml.dump(config)
print("\nModified configuration:")
print(modified_config)

# The output will look like:
"""
name = "My App"
version = "2.1"
settings = {
    port = 8080,
    debug = true
}
"""

# To save to a file instead:
# ftml.dump(config, "config.ftml")
```

Expected output:
```
Current port: 8080
Updated version: 2.1

Modified configuration:
name = "My App"

version = "2.1"

settings = {
    port = 8080,
    debug = true
}
```

###   4.2 Schema Validation

```python
import ftml
from ftml.exceptions import FTMLValidationError

# Define schema
ftml_schema = """
// Application configuration schema
name: str<min_length=1>
version: str
settings: {
    port: int<min=1024, max=65535>,
    debug: bool
}
"""

# Example FTML content to validate
ftml_data = """
// My application config
name = "My App"
version = "1.0"
settings = {
    port = 8080,  // This would fail validation if < 1024
    debug = true
}
"""

try:
  # Load with validation
  config = ftml.load(ftml_data, schema=ftml_schema)
  print("Validation passed!")

  # Output after successful validation:
  # Validation passed!

  # Now we can safely work with the data
  print(f"Application: {config['name']} v{config['version']}")
  print(f"Port: {config['settings']['port']}")

  # Modify and validate before saving
  config["settings"]["port"] = 9000

  # Get the modified FTML content
  modified_ftml = ftml.dump(config, schema=ftml_schema)
  print("\nModified FTML:")
  print(modified_ftml)

except FTMLValidationError as e:
  print(f"Validation failed: {e}")
  if hasattr(e, "errors") and e.errors:
    for error in e.errors:
      print(f"  - {error}")

# Now let's see what happens with invalid data
invalid_ftml = """
name = ""  // Empty name - will fail min_length validation
version = "1.0"
settings = {
    port = 80,  // Port too low - will fail min validation
    debug = true
}
"""

try:
  config = ftml.load(invalid_ftml, schema=ftml_schema)
except FTMLValidationError as e:
  print("\nExpected validation failure due to invalid_ftml:")
  if hasattr(e, "errors") and e.errors:
    for error in e.errors:
      print(f"  - {error}")
```

Expected output:
```
Validation passed!
Application: My App v1.0
Port: 8080

Modified FTML:
name = "My App"

version = "1.0"

settings = {
    port = 9000,
    debug = true
}

Expected validation failure due to invalid_ftml:
  - String at 'name' is too short (minimum length: 1)
  - Number at 'settings.port' is too small (minimum: 1024)
```

###   4.3 Creating New FTML Documents

```python
import ftml

# Create a new configuration
config = {
  "name": "New App",
  "version": "1.0",
  "settings": {
    "port": 8080,
    "debug": False,
    "database": {
      "host": "localhost",
      "port": 5432
    }
  },
  "features": ["authentication", "logging", "caching"]
}

# Get the FTML as a string
ftml_string = ftml.dump(config)

# Display the result
print(ftml_string)

# Use this you want to save the FTML to a file:
# ftml.dump(config, "new_config.ftml")
```

Expected output:
```
name = "New App"

version = "1.0"

settings = {
    port = 8080,
    debug = false,
    database = {
        host = "localhost",
        port = 5432
    }
}

features = [
    "authentication",
    "logging",
    "caching"
]
```

###   4.4 Comment Preservation and Limitations

Comments in FTML are preserved when using load() and dump(), but have important limitations:

```python
import ftml

# Original FTML with various comment types
ftml_with_comments = """
//! Document-level comment

// Leading comment for name
name = "My App"  // Inline comment for name

// Comment for settings section
settings = {
    //! Inner doc comment for settings
    port = 8080  // Port comment
}
"""

# Load preserves all comments
data = ftml.load(ftml_with_comments)

# Modifying existing data preserves its comments
data["name"] = "Updated App Name"  # Comments for 'name' are preserved, but cannot be edited
data["settings"]["port"] = 9000    # Comment for 'port' is preserved, but cannot be edited

# New data added programmatically cannot have comments
data["version"] = "1.0"            # No way to add comments to this
data["settings"]["debug"] = True   # No way to add comments to this

# Result preserves all original comments
result = ftml.dump(data)
print(result)
```

Expected output:
```
//! Document-level comment

// Leading comment for name
name = "Updated App Name"  // Inline comment for name

// Comment for settings section
settings = {
    //! Inner doc comment for settings
    port = 9000,  // Port comment
    debug = true
}

version = "1.0"
```

##   5. Error Handling

The FTML library provides specific exception classes for different error types:

###   5.1 Exception Hierarchy

* `FTMLError`: Base class for all FTML exceptions
    * `FTMLParseError`: Raised when there is a syntax error in FTML
    * `FTMLValidationError`: Raised when validation against a schema fails

### 5.2 Error Handling Example

```python
import ftml
from ftml.exceptions import FTMLParseError, FTMLValidationError

# Example schema content
schema_str = """
// Simple user schema
name: str<min_length=1>
age: int<min=0>
"""

# Example invalid FTML content
invalid_ftml = """
name = 
age = "twenty"  // Should be a number
"""

try:
  # Option 1: Parse schema from string
  data = ftml.load(invalid_ftml, schema=schema_str)

  # Option 2: Load schema from file (if you have one)
  # data = ftml.load("user.ftml", schema="user.schema.ftml")
except FTMLParseError as e:
  print(f"Syntax error in FTML: {e}")
except FTMLValidationError as e:
  print(f"Validation failed: {e}")
  if hasattr(e, "errors") and e.errors:
    for error in e.errors:
      print(f"  - {error}")
except Exception as e:
  print(f"Unexpected error: {e}")
```

Expected output:
```
Syntax error in FTML: Expected a value at line 2, col 8. Got NEWLINE '\n'
```

### 5.3 Manual Validation

For cases where you want to validate data without loading or dumping:

```python
import ftml
from ftml.exceptions import FTMLValidationError

# Schema definition
schema_str = """
// User schema
name: str<min_length=1>
age: int<min=0>
"""

# Data to validate (already in Python dictionary form)
user_data = {
  "name": "",  # Invalid - empty string fails min_length
  "age": 25
}

try:
  # Load the schema first
  schema = ftml.load_schema(schema_str)

  # Validate the data
  errors = ftml.validate(user_data, schema)

  if errors:
    print("Validation errors:")
    for error in errors:
      print(f"  - {error}")
  else:
    print("Data is valid!")
except Exception as e:
  print(f"Error during validation: {e}")
```

Expected output:
```
Validation errors:
- String at 'name' is too short (minimum length: 1)
```





##   6. Advanced Usage

###   6.1 Working with In-Memory AST

For advanced use cases where you need to inspect or manipulate the FTML document structure, you can use the `FTMLDict` to interact with comments.

```python
import ftml

# Load FTML with comments
document = """
//! Configuration file
name = "My App"  // Application name
version = "1.0"  // Version number
"""

# Parse into an FTMLDict with AST
data = ftml.load(document)

# Access the internal AST
if hasattr(data, "_ast_node"):
  ast = data._ast_node

  # Inspect AST structure
  print(f"Document has {len(ast.items)} items")

  # Print comments
  for key, kv_node in ast.items.items():
    print(f"Key: {key}")

    # Print leading comments
    if kv_node.leading_comments:
      print("  Leading comments:")
      for comment in kv_node.leading_comments:
        print(f"    - {comment.text}")

    # Print inline comment
    if kv_node.inline_comment:
      print(f"  Inline comment: {kv_node.inline_comment.text}")

  # Add a new comment to an existing node
  if "name" in ast.items:
    # Import Comment class through internal path (advanced usage)
    from ftml.parser.ast import Comment

    # Create and add a new leading comment
    new_comment = Comment("This is a manually added comment", 0, 0)
    ast.items["name"].leading_comments.append(new_comment)

  # Dump with the modified AST
  result = ftml.dump(data)
  print("\nModified FTML with added comment:")
  print(result)
```

Example output:
```
Document has 2 items
Key: name
  Inline comment: Application name
Key: version
  Inline comment: Version number

Modified FTML with added comment:
//! Configuration file

// This is a manually added comment
name = "My App"  // Application name

version = "1.0"  // Version number
```

###   6.2 Schema Validation and Default Values

FTML provides public functions for advanced schema processing, including standalone validation and applying default values.

```python
import ftml

# Schema with validation constraints and default values
schema_str = """
// User profile schema
name: str<min_length=1>  // Name is required
version: str = "1.0"     // Version defaults to "1.0"
active: bool = true      // Active defaults to true
settings: {
    theme: str = "light",  // Theme defaults to "light"
    notifications: bool = false
}
"""

# Load the schema
schema = ftml.load_schema(schema_str)

# Empty data - will cause validation errors
data = {}

print("=== Before applying defaults ===")
print(f"Data: {data}")

# Validate without defaults
errors = ftml.validate(data, schema)
if errors:
  print("\nValidation errors:")
  for error in errors:
    print(f"  - {error}")
else:
  print("\nData is valid!")

# Apply schema defaults to data
print("\n=== Applying defaults ===")
data_with_defaults = ftml.apply_defaults(data, schema)
print(f"Data with defaults: {data_with_defaults}")

# Validate again after applying defaults
errors = ftml.validate(data_with_defaults, schema)
if errors:
  print("\nValidation errors still exist:")
  for error in errors:
    print(f"  - {error}")
else:
  print("\nData is now valid after applying defaults!")

# Fix remaining validation issues
data_with_defaults["name"] = "User Profile"

# Final validation
errors = ftml.validate(data_with_defaults, schema)
if not errors:
  print("\nFully valid data:")
  print(data_with_defaults)
```

Example output:
```
=== Before applying defaults ===
Data: {}

Validation errors:
  - Missing required field: 'name'
  - Missing required field: 'settings'

=== Applying defaults ===
Data with defaults: {'version': '1.0', 'active': True, 'settings': {'theme': 'light', 'notifications': False}}

Validation errors still exist:
  - Missing required field: 'name'

Fully valid data:
{'version': '1.0', 'active': True, 'settings': {'theme': 'light', 'notifications': False}, 'name': 'User Profile'}
```


##   7. Configuration Options

###   7.1 Logging Configuration

FTML uses Python's standard logging module. You can configure logging either programmatically or via an environment variable:

```python
import logging
from ftml import logger

#   Set log level programmatically
logger.setLevel(logging.DEBUG)

#   Add a custom handler
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
```

Alternatively, set the environment variable:

```
FTML_LOG_LEVEL=DEBUG
```

###   7.2 Strict Mode vs Non-Strict Mode

When validating against schemas, you can choose strict or non-strict mode:

```python
#   Strict mode (default): rejects extra properties not in the schema
data = ftml.load("config.ftml", schema="schema.ftml", strict=True)

#   Non-strict mode: allows extra properties not defined in the schema
data = ftml.load("config.ftml", schema="schema.ftml", strict=False)
```

##   8. Performance Considerations

###   8.1 Comment Preservation

Preserving comments can impact performance, especially for large files. If performance is critical and comment preservation is not required, you can disable it:

```python
#   Maximum performance, no comments preserved
data = ftml.load("large_file.ftml", preserve_comments=False)

#   Save without comments for maximum performance
ftml.dump(data, "output.ftml", include_comments=False)
```

###   8.2 Schema Validation

Schema validation also adds overhead. If you are working with trusted data and performance is a concern, you can skip validation:

```python
#   Skip validation for performance when reading trusted data
data = ftml.load("large_file.ftml", validate=False)

#   Skip validation when writing
ftml.dump(data, "output.ftml", validate=False)
```

##   9. Integration with Other Libraries

###   9.1 Working with JSON

The FTML library makes it easy to convert between FTML and JSON:

```python
import json
import ftml

#   FTML to JSON
ftml_data = ftml.load("config.ftml", preserve_comments=False)
json_str = json.dumps(ftml_data, indent=2)
with open("config.json", "w") as f:
    f.write(json_str)

#   JSON to FTML
with open("data.json", "r") as f:
    json_data = json.load(f)
ftml.dump(json_data, "data.ftml")
```

###   9.2 Working with YAML

Similarly, you can convert between FTML and YAML:

```python
import yaml
import ftml

#   FTML to YAML
ftml_data = ftml.load("config.ftml", preserve_comments=False)
with open("config.yaml", "w") as f:
    yaml.dump(ftml_data, f)

#   YAML to FTML
with open("data.yaml", "r") as f:
    yaml_data = yaml.safe_load(f)
ftml.dump(yaml_data, "data.ftml")
```

##   10. Best Practices

###   10.1 File Management

Use Python's `with` statements to ensure proper file handling, and use the `os` module for robust path manipulation:

```python
import ftml
import os

#   Use with statements for file operations
with open("temp.ftml", "w") as f:
    ftml.dump(data, f)

#   Use appropriate file paths
config_dir = os.path.join(os.path.expanduser("~"), ".config", "myapp")
os.makedirs(config_dir, exist_ok=True)
config_path = os.path.join(config_dir, "settings.ftml")
```

###   10.2 Error Handling

Wrap FTML operations in `try...except` blocks to handle potential exceptions:

```python
import ftml
from ftml.exceptions import FTMLError

try:
    #   Group related operations
    data = ftml.load("input.ftml")
    #   Process data...
    ftml.dump(data, "output.ftml")
except FTMLError as e:
    #   Handle FTML-specific errors
    print(f"FTML operation failed: {e}")
except Exception as e:
    #   Handle other errors
    print(f"Unexpected error: {e}")
```

###   10.3 Schema Management

Load schemas once and reuse them to avoid redundant parsing:

```python
import ftml
import os

#   Keep schemas with related files
app_dir = "myapp"
config_schema = os.path.join(app_dir, "schemas", "config.ftml-schema")
user_schema = os.path.join(app_dir, "schemas", "user.ftml-schema")

#   Load schemas once and reuse
config_schema_obj = ftml.load_schema(config_schema)
user_schema_obj = ftml.load_schema(user_schema)

#   Use for multiple operations
config = ftml.load("config.ftml", schema=config_schema_obj)
user = ftml.load("user.ftml", schema=user_schema_obj)
```

###   10.4 Preserving Source Format

When updating configuration files, load them with `preserve_comments=True` and modify the returned `FTMLDict` to maintain the original formatting and comments:

```python
import ftml

#   Preserve formatting and comments during updates
config = ftml.load("config.ftml")  #   Comments preserved by default

#   Only modify what's needed
config["version"] = "2.0"  #   Original formatting of other fields is preserved

#   Preserve during save
ftml.dump(config, "config.ftml")  #   Comments included by default
