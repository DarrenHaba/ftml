# FTML Root Structure & Document Format

## 1. Overview

The FTML (FlexTag Markup Language) document format is designed for human readability and ease of editing while maintaining a structured format for configuration data, settings, and other hierarchical information. This specification describes the root-level structure and overall document format of FTML files.

## 2. Document Structure

### 2.1 Basic Structure

An FTML document consists of one or more key-value pairs at the root level:

```ftml
key1 = value1
key2 = value2
key3 = value3
```

An FTML document should contain at least one key-value pair, though parsers may accept empty documents. The root of the document is a collection of named values, where each value is associated with a unique key.

### 2.2 Key-Value Assignment

Root-level key-value pairs use the equals sign (=) as an assignment operator that both separates and binds values to keys:

```ftml
name = "My Application"  // Assigns the string "My Application" to the key "name"
version = "1.0"          // Assigns the string "1.0" to the key "version"
```

The equals sign establishes the relationship between keys and their corresponding values.

### 2.3 Line Separation

Root-level key-value pairs are separated by newlines, not commas:

```ftml
// This is correct
key1 = "value1"
key2 = "value2"

// This is NOT valid FTML
key1 = "value1",  // Invalid: no commas at root level
key2 = "value2"

// This is NOT valid FTML - Only one key value pair per line. 
key1 = "value1", key2 = "value2"
```

Root-level items must appear on separate lines without commas. Commas are only used as separators within objects and lists, not at the document root level.

### 2.4 Multiple Lines Between Key-Value Pairs

Multiple blank lines between key-value pairs are allowed:

```ftml
name = "My Application"

// Notice the blank line above
version = "1.0"


// Notice two blank lines above
debug = true
```

Blank lines help visually separate logical sections of a document and improve readability.

## 3. Document Elements and Examples

### 3.1 Core Elements

An FTML document contains:

1. **Comments**: Several types of comments are supported:
    * `//` - General comments for notes and explanations
    * `///` - Outer documentation comments that document the following item
    * `//!` - Inner documentation comments that document the enclosing item
2. **Key-Value Pairs**: Root-level pairs connected by equals signs (`key = value`)
3. **Values**: Primitives (strings, numbers, booleans, null) or collections (objects, lists)
4. **Whitespace**: Spaces, tabs, and newlines for formatting

### 3.2 Reserved Document Keys

FTML reserves certain keys for special purposes:

- `ftml_version`: Declares the FTML specification version the document uses
- `ftml_encoding`: Specifies the character encoding of the document

Example:
```ftml
ftml_version = "1.0"
ftml_encoding = "utf-8"
```

### 3.3 Example Complete Document

This example demonstrates the key elements of an FTML document:

```ftml
//! Application Configuration
//! Last updated: 2025-03-25

ftml_version = "1.0"

// Application metadata
name = "Sample Application"
author = "Example Team"
release_date = "2025-03-25"

// Server configuration
server = {
    host = "localhost",
    port = 8080,
    debug = true
}

// Feature flags
features = [
    "authentication",
    "logging",
    "caching"
]
```

Note: In this specification, examples are indented with four spaces for readability, but FTML itself does not require specific indentation. Consistent indentation is encouraged for human readability, but parsers should not depend on it.

## 4. Key Naming Rules

### 4.1 Identifier Keys

Root-level keys (and keys within objects) typically follow identifier rules:

- Must start with a letter (a-z, A-Z) or underscore (_)
- Can contain letters, numbers, and underscores
- Pattern: `[A-Za-z_][A-Za-z0-9_]*`

```ftml
name = "value"
user_name = "value"
_internal = "value"
```

### 4.2 Quoted Keys

Keys can also be quoted to allow special characters or spaces:

```ftml
"my key" = "value"
'another key' = "value"
"special!@#" = "value"
```

### 4.3 Reserved Words as Keys

FTML reserves certain scalars (`null`, `true`, `false`, `int`, `float`, `string`) that cannot be used directly as bare keys. When using these reserved words as keys, they must be quoted:

```ftml
// INCORRECT - reserved words cannot be used as bare keys
null = "value"         // Error: Expected a key (identifier or quoted string)
true = "value"         // Error: Expected a key (identifier or quoted string)

// CORRECT - use quotes to indicate this is a key name
"null" = "value"
'true' = "value"
```

Best practice is to avoid using reserved words as keys, even with quotes, to maintain code clarity and prevent potential confusion.

### 4.4 Key Uniqueness

Root-level keys must be unique within a document. Duplicate keys will cause a parse error:

```ftml
// INVALID FTML - duplicate keys
name = "First"
name = "Second"  // Error: duplicate key
```

## 5. Document Encoding

### 5.1 Character Encoding

FTML documents should be encoded in UTF-8 by default. This enables support for international character sets while maintaining compatibility with ASCII.

A document may specify its encoding using a special key:

```ftml
ftml_encoding = "utf-8"
```

Supported encodings include:
- `utf-8` (default)
- `latin-1`, `latin1`, `iso-8859-1`
- `ascii`
- `utf-16`, `utf-16-le`, `utf-16-be`

### 5.2 Line Endings

FTML parsers should accept both LF (`\n`) and CRLF (`\r\n`) line endings:

- Unix-style line endings (LF): `\n`
- Windows-style line endings (CRLF): `\r\n`

## 6. Document Size

### 6.1 Recommendations

While there's no strict limit on document size, FTML is optimized for human readability:

- **Recommended maximum**: A few thousand lines
- **Recommended organization**: Split large configurations into multiple files
- **Key organization**: Group related keys together

### 6.2 Nesting Depth

FTML supports arbitrary nesting of collections, but for readability:

- **Recommended maximum nesting**: 5-6 levels deep

## 7. Document Partitioning

### 7.1 File Organization

For complex configurations, consider splitting FTML documents by functional area:

```
config/
  |- main.ftml         # Main application settings
  |- logging.ftml      # Logging configuration
  |- database.ftml     # Database settings
  |- security.ftml     # Security settings
```

### 7.2 Referencing Between Documents

While FTML doesn't have a built-in include mechanism, applications can implement references:

```ftml
// Reference to another configuration file
database_config = "database.ftml"
logging_config = "logging.ftml"
```

## 8. Version Information

### 8.1 Application Version

Documents can (optionally) include an application-specific version identifier:

```ftml
version = "1.0"
```

This key is reserved and is used by parsers to check compatibility.

## 9. Root-Level vs Nested Elements

### 9.1 Syntax Differences

Important differences between root-level and nested key-value pairs:

| Feature | Root Level | Nested (in Objects) |
|---------|------------|---------------------|
| Separator between pairs | Newlines | Commas |
| Required delimiter | None | Braces `{ }` |
| Key uniqueness | Must be unique | Must be unique within object |
| Key formatting | On its own line | Can share lines |

### 9.2 Example Comparison

```ftml
// Root level structure
key1 = "value1"
key2 = "value2"

// Nested structure
object = {
  key1 = "value1",
  key2 = "value2"
}
```

## 10. Best Practices

### 10.1 Document Organization

- Place related keys together in sections
- Use comments to create section headers
- Consider hierarchical structure for complex settings

Example:
```ftml
//! Application Configuration

// ======== General Settings ========
name = "My Application"
version = "1.0"

// ======== Network Settings ========
host = "localhost"
port = 8080

// ======== Logging Settings ========
logging = {
  level = "info",
  file = "app.log",
  rotation = true
}
```

### 10.2 Key Naming Conventions

- Use consistent naming conventions (snake_case, camelCase, etc.)
- Be descriptive in key names
- Group related settings in objects rather than using prefixes
- Avoid using reserved words as keys, even with quotes

```ftml
// Instead of this:
database_host = "localhost"
database_port = 5432
database_user = "admin"

// Consider this:
database = {
  host = "localhost",
  port = 5432,
  user = "admin"
}
```

### 10.3 Whitespace Usage

- Use consistent indentation (typically 2 or 4 spaces)
- Use blank lines to separate logical sections

## 11. Implementation Notes

### 11.1 Parser Behavior

FTML parsers should:

- Treat a document as a stream of key-value pairs
- Maintain the order of root-level keys as they appear in the source
- Preserve comments for round-trip serialization
- Validate key uniqueness at the root level
- Require quotes around reserved words when used as keys

### 11.2 Serializer Behavior

FTML serializers should:

- Output one root key-value pair per line
- Maintain the original order of keys
- Preserve comments in their appropriate positions
- Use consistent indentation for nested structures
- Properly quote any key that uses a reserved word