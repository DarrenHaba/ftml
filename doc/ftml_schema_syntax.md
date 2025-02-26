# FTML Schema Syntax Documentation

## Overview

FTML schemas define the structure, types, and constraints of FTML data using a concise type‑first syntax. This approach allows you to enforce data integrity by specifying required fields, optional fields, default values, union types, and nested structures.

## Schema Declaration

Schemas begin with a colon (`:`) followed by a type expression. For example:
```ftml
:dict{
    :str name,
    :int age
}
```

## Basic Types

FTML supports these basic types:
- **`str`** – A sequence of characters.
- **`int`** – An integer number.
- **`float`** – A floating‑point number.
- **`bool`** – A boolean value (`true` or `false`).
- **`null`** – Represents a null value.

## Complex Types

### Lists

Lists use the `list` keyword with the item type enclosed in square brackets `[]`. Lists can contain elements of a specific type or be unrestricted.

#### List Variants:

- **Unrestricted List**  
  Allows any type of elements:
  ```ftml
  :list[]  # No constraints on element types.
  ```

- **Typed List**  
  Enforces that all elements must be of a specific type:
  ```ftml
  :list[:int]  # All elements must be integers.
  ```

- **Nested List**  
  Lists can contain other lists or structured data:
  ```ftml
  :list[dict{
      :str key,
      :int value
  }]
  ```
  Ensures each list item follows a defined dictionary structure.

Lists provide a structured way to handle collections of data while enforcing type consistency.

### Dictionaries

Dictionaries use the `dict` keyword with field definitions enclosed in curly braces `{}`. In FTML, all dictionary keys are implicitly strings.

#### Dictionary Variants:

- **Unrestricted Dictionary**  
  Allows any key-value pairs:
  ```ftml
  :dict{}  # No constraints on keys or values.
  ```

- **Uniform Value Dictionary**  
  Enforces that all values must be of the same type:
  ```ftml
  :dict{ :int }  # All values must be integers.
  ```

- **Structured Dictionary**  
  Specifies expected keys and their types:
  ```ftml
  :dict{
      :str name,
      :int age
  }
  ```
  Ensures `name` is a string and `age` is an integer.

Dictionaries provide both flexibility and structure, making them useful for various FTML data representations.

## Field Definitions

### Required Fields

By default, all fields are required:
```ftml
:str name  # A required string field
```

### Optional Fields

Append a `?` to the type to mark a field as optional:
```ftml
:str? middle_name  # An optional field
```

### Default Values

Specify default values using the `=` operator:
```ftml
:int age = 30             # A field with a default value of 30
:str? middle_name = "N/A"  # An optional field with a default value
```

### Union Types

Use the `|` operator to allow multiple types for a field:
```ftml
:str|:null description   # Field can be a string or null
:int|:float measurement  # Field can be either an integer or a float
```

## Nested Structures

Schemas can be nested to model complex data:
```ftml
:dict{
    :str name,
    :dict{
        :str street,
        :str city,
        :str? zip
    } address,
    :list[dict{
        :str key,
        :str value
    }] attributes
}
```

## Formal Grammar (Simplified)

```
schema           ::= ":" type_expression

type_expression  ::= simple_type | complex_type | union_type

simple_type      ::= "str" | "int" | "float" | "bool" | "null"

complex_type     ::= list_type | dict_type

list_type        ::= "list" "[" type_expression "]"

dict_type        ::= "dict" "{" field_list "}"

field_list       ::= field ("," field)*

field            ::= ":" type_expression optionality? field_name default_value?

optionality      ::= "?"

field_name       ::= identifier

default_value    ::= "=" value

union_type       ::= type_expression "|" type_expression
```

## Schema Validation Rules

When validating data against a schema:
1. **Type Checking:**  
   Each value (and every item in lists or fields in dictionaries) must match its declared type.
2. **Required Fields:**  
   All required fields must be present. Optional fields can be omitted.
3. **Default Values:**  
   Missing fields with defaults are automatically populated during validation.

## Examples

### Simple Schema Example
```ftml
:dict{
    :str name,
    :int age = 30
}
```

### Advanced Schema with Unions and Optional Fields
```ftml
:dict{
    :str name,
    :int? age = 25,
    :bool active = true,
    :str|:null description
}
```

### Nested Schema Example
```ftml
:dict{
    :str name,
    :dict{
        :str street,
        :str city,
        :str? zip
    } address,
    :list[str] tags = []
}
```

## Summary

FTML schemas offer a robust, self-descriptive means to define the structure and constraints of your data. The type‑first syntax clarifies data expectations by specifying required versus optional fields, default values, and supporting nested and union types. This ensures that data is consistent, type‑safe, and ready for validation.