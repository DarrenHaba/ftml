# FTML Union Types & Enums Specification

## 1. Overview

FTML supports two powerful type composition mechanisms: union types and enum constraints. These features allow schema authors to express complex type relationships and restrict values to specific sets of options.

## 2. Union Types

Union types allow a field to accept values of multiple different types, providing flexibility while maintaining type safety.

### 2.1 Union Type Syntax

Union types are defined using the pipe symbol (`|`) to separate alternative types:

```ftml
// Field can be either a string or an integer
id: str | int

// Field can be a string, null, or a boolean
value: str | null | bool
```

### 2.2 Union Type Validation

When validating a field with a union type, the value must match one of the specified types. If the value matches multiple types (e.g., a string "123" potentially matching both string and integer in some implementations), FTML typically validates against types in the order they are listed.

### 2.3 Simple Union Type Examples

```ftml
// ID can be string or integer
id: str | int

// Status can be string or null (making it effectively optional)
status: str | null

// Value can be any scalar type
value: str | int | float | bool | null

// Count can be an exact integer or "unknown"
count: int | str<enum=["unknown"]>
```

## 3. Complex Union Types

Union types can include complex types such as objects and lists, not just scalars.

### 3.1 Object Unions

Different object shapes can be part of a union:

```ftml
// Contact can be an email address or a full physical address
contact: str<format="email"> | {
  street: str,
  city: str,
  state: str,
  zip: str
}
```

### 3.2 List Unions

Lists of different element types can be part of a union:

```ftml
// Data can be a list of strings or a list of integers
data: [str] | [int]
```

### 3.3 Mixed Type Unions

Unions can mix scalars, objects, and lists freely:

```ftml
// Value can be a string, a number, or a list of strings
value: str | int | float | [str]

// Config can be a string path or a complex object
config: str | {
  path: str,
  options: {
    recursive: bool,
    force: bool
  }
}
```

### 3.4 Complex Union Examples

```ftml
// User identifier can be a username, email, or numeric ID
user_id: str<pattern="[a-zA-Z0-9_]+">> | str<format="email"> | int<min=1000>

// Location can be coordinates or an address object
location: {
  lat: float,
  lng: float
} | {
  street: str,
  city: str,
  country: str
}

// Data structure can be nested in different ways
structure: {
  type: str<enum=["leaf"]>,
  value: any
} | {
  type: str<enum=["node"]>,
  children: [structure]  // Recursive reference
}
```

## 4. Constraints with Union Types

Constraints can be applied to individual types within a union.

### 4.1 Type-Specific Constraints

Each type in a union can have its own constraints:

```ftml
// String with pattern or integer with range
code: str<pattern="[A-Z]+">> | int<min=1000, max=9999>

// Email format or null
email: str<format="email"> | null
```

### 4.2 Complex Type Constraints

Constraints can be applied to complex types within unions:

```ftml
// Object with required keys or string with minimum length
config: {str: any}<required_keys=["version"]> | str<min_length=10>

// Non-empty list or single string
tags: [str]<min=1> | str
```

## 5. Union Types and Default Values

Default values can be provided for fields with union types:

### 5.1 Default Value Syntax

```ftml
// Default to null
optional_name: str | null = null

// Default to integer
id_field: str | int = 0
```

### 5.2 Default Value Selection

The default value must match one of the types in the union.

```ftml
// Valid: default is a string enum value
level: int<min=1, max=10> | str<enum=["beginner", "intermediate", "advanced"]> = "beginner"

// Valid: default is an integer
count: str<enum=["unknown"]> | int<min=0> = 0
```

## 6. Enum Constraints

Enums in FTML are implemented as constraints that limit values to a predefined set of options.

### 6.1 Enum Constraint Syntax

Enums are defined using the `enum` constraint with an array of allowed values:

```ftml
status: str<enum=["pending", "active", "completed"]>
priority: int<enum=[1, 2, 3]>
```

### 6.2 Type-Specific Enums

Enums apply to specific types and the values must match that type:

| Type | Enum Example | Valid Values |
|------|--------------|--------------|
| str | `str<enum=["red", "green", "blue"]>` | `"red"`, `"green"`, `"blue"` |
| int | `int<enum=[1, 2, 3]>` | `1`, `2`, `3` |
| float | `float<enum=[0.5, 1.0, 1.5]>` | `0.5`, `1.0`, `1.5` |
| bool | `bool<enum=[true]>` | `true` (only) |

### 6.3 Simple Enum Examples

```ftml
// String enum for status
status: str<enum=["pending", "active", "completed"]>

// Integer enum for priority
priority: int<enum=[1, 2, 3, 5, 8]>

// Boolean enum (effectively restricts to only one value)
terms_accepted: bool<enum=[true]>

// Float enum for predefined values
scale_factor: float<enum=[0.5, 1.0, 2.0]>
```

## 7. Combining Enums and Unions

Enum constraints and union types can be combined for powerful type definitions.

### 7.1 Enums in Union Types

Each type in a union can have its own enum constraint:

```ftml
// Can be a specific set of strings or specific integers
level: str<enum=["beginner", "intermediate", "advanced"]> | int<enum=[1, 2, 3]>

// Can be "unknown" or a positive integer
count: str<enum=["unknown"]> | int<min=1>
```

### 7.2 Optional Enums with Null

Union with null makes an enum value optional:

```ftml
// Optional status (can be one of the enum values or null)
status: str<enum=["pending", "active", "completed"]> | null

// Required in objects, optional at root
settings: {
  theme: str<enum=["light", "dark"]>  // Required in settings object
} | null  // But settings object itself is optional
```

### 7.3 Combined Examples

```ftml
// Status can be enum string, number code, or null
status: str<enum=["pending", "active", "completed"]> | int<enum=[0, 1, 2]> | null

// Document type with version restrictions
document: {
  type: str<enum=["article", "report"]>,
  version: int<enum=[1, 2]> | str<enum=["legacy"]>
}

// Complex validation combining unions and enums
response: {
  success: bool<enum=[true]>,
  data: any
} | {
  success: bool<enum=[false]>,
  error: str,
  code: int<enum=[400, 401, 403, 404, 500]>
}
```

## 8. Advanced Union Type Patterns

Union types enable several advanced patterns in schema definitions.

### 8.1 Type Discrimination

Union types can define discriminated unions using a "type" field:

```ftml
// Discriminated union based on "type" field
shape: {
  type: str<enum=["circle"]>,
  radius: float<min=0.0>
} | {
  type: str<enum=["rectangle"]>,
  width: float<min=0.0>,
  height: float<min=0.0>
} | {
  type: str<enum=["triangle"]>,
  points: [{x: float, y: float}]<length=3>
}
```

### 8.2 Recursive Types

Union types can refer to themselves to create recursive data structures:

```ftml
// Recursive JSON-like data structure
json_value: str | int | float | bool | null | [json_value] | {str: json_value}

// Tree node structure
node: {
  value: any,
  children: [node] | null
}
```

### 8.3 Content Polymorphism

Union types can handle content polymorphism based on format or structure:

```ftml
// Content can be raw text or formatted content
content: str | {
  format: str<enum=["markdown", "html", "plain"]>,
  text: str,
  metadata?: {str: any}
}

// Message can be text or multimedia
message: str | {
  type: str<enum=["image", "video", "audio"]>,
  url: str<format="uri">,
  caption?: str
}
```

## 9. Enum Best Practices

### 9.1 Enum Design

- Use string enums for semantic values
- Use integer enums for coded values
- Document the meaning of each enum value
- Consider extensibility needs

### 9.2 Exhaustive vs. Non-Exhaustive Enums

Some FTML implementations may support a concept of exhaustive vs. non-exhaustive enums:

```ftml
// Exhaustive: only listed values allowed
status: str<enum=["pending", "active", "completed"]>

// Non-exhaustive: suggested values, but others may be allowed
// Implementation-specific, might use enum_strict=false
category: str<enum=["news", "sports", "entertainment"], enum_strict=false>
```

### 9.3 Default Values

Choose sensible defaults for enum fields:

```ftml
// Default to most common or safest option
visibility: str<enum=["public", "private", "unlisted"]> = "private"
```

## 10. Union Type Best Practices

### 10.1 Union Design

- List more specific types before more general types
- Use unions sparingly for clarity
- Document the purpose of each alternative

### 10.2 Optional Fields

Use union with null to make fields optional:

```ftml
// Optional string field
middle_name: str | null

// Optional complex structure
address: {
  street: str,
  city: str,
  country: str
} | null
```

### 10.3 Type Safety

- Avoid overly permissive unions like `str | int | bool | null`
- Consider using discriminated unions for better type safety
- Document expected types and formats

## 11. Implementation Notes

### 11.1 Parsing Considerations

When parsing union types:

1. Try each type in the order specified
2. Match against the first compatible type
3. Handle overlap between types (e.g., a string that looks like an integer)

### 11.2 Validation Behavior

When validating union types:

1. Try each type until a match is found
2. For each type, apply all its constraints
3. Fail validation only if the value matches no types
4. Provide clear error messages about why no types matched

### 11.3 Serialization

When serializing fields with union types:

1. Use the original type when deserializing/serializing
2. Maintain type information during transformations
3. Preserve enum values exactly as defined