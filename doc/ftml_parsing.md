# FTML Parsing Documentation

## Overview

FTML (FlexTag Markup Language) includes a parser that transforms FTML text into native Python data structures. It automatically detects and separates embedded schema definitions from data, applies validation (including default value assignment), and supports full round‑trip serialization. This document explains the parser’s architecture, workflow, and advanced features.

## Parser Architecture

The parser is organized into four primary components:

- **Main Parser:** Orchestrates the overall process by first checking for an embedded schema, splitting the content into schema and data sections, and then handing off each section to the appropriate parser.
- **Schema Parser:** Uses a recursive descent approach to interpret type‑first expressions. It handles:
    - Basic types (e.g. `str`, `int`)
    - Optional markers (`?`)
    - Default values (using `=`)
    - Union types (using the `|` operator)
    - Complex types like lists (`list[...]`) and dictionaries (`dict{...}`)
- **Data Parser:** Converts FTML data (e.g. dictionaries defined with `{...}` and lists defined with `[...]`) into corresponding Python objects.
- **Validator:** Recursively checks that the parsed data conforms to the schema. This step also applies default values for missing fields and enforces type safety.

## Parsing Process

1. **Schema Detection**  
   The parser inspects the content’s first character. If it starts with a colon (`:`), it treats the first section as the schema:
   ```python
   if content.strip().startswith(":"):
       parts = content.split("\n\n", 1)
       schema_content = parts[0]
       data_content = parts[1] if len(parts) > 1 else ""
   ```

2. **Schema Parsing**  
   The schema section is processed using a recursive descent strategy:
   ```python
   schema = parse_schema(schema_content)
   ```
   This step builds a nested dictionary representation of the schema by:
    - Recognizing simple and complex types.
    - Handling nested type expressions (including balancing braces and brackets).
    - Supporting union types and optional markers.

3. **Data Parsing**  
   The data section is converted into Python structures:
   ```python
   data = parse_data(data_content)
   ```
   This parser manages dictionaries, lists, and literal values (strings, numbers, booleans, and null).

4. **Validation and Default Application**  
   Once both schema and data are parsed, the validator checks for type conformance and applies any default values:
   ```python
   if schema and data:
       validate_data(data, schema)
   ```
   This ensures that the final data structure is complete and type‑safe.

## Advanced Features

- **Nested Structures:**  
  Deeply nested dictionaries and lists are handled gracefully, using helper routines to correctly parse and balance nested expressions.

- **Custom Field Extraction:**  
  A dedicated helper function extracts complete type expressions (even when they include spaces or nested constructs), avoiding premature splits.

- **Robust Error Handling:**  
  Detailed error messages (e.g., for unclosed brackets or missing assignment operators) assist users in quickly pinpointing issues.

## Summary

The FTML parser efficiently transforms FTML content into Python data by separating schema and data, recursively parsing both sections, and enforcing validation rules. Its design prioritizes clarity, type safety, and flexibility—making FTML a robust tool for structured data markup.
````markdown

