# FTML Collections Specification

## 1. Overview

FTML (FlexTag Markup Language) supports two primary collection types:

1. **Objects**: Unordered key-value mappings enclosed in braces `{...}`
2. **Lists**: Ordered sequences of values enclosed in brackets `[...]`

Collections can be infinitely nested and mixed to create complex hierarchical data structures. This specification details how collections are defined in schemas and used in data files.

## 2. Schema vs. Data

FTML has a clear separation between **schema definitions** and **data instances**:

- **Schema**: Defines the expected structure, types, and constraints
- **Data**: Contains the actual values conforming to a schema

FTML uses a consistent file naming convention to distinguish between these two types of files:
- Data files use the `.ftml` extension (e.g., `config.ftml`)
- Schema files use the `.schema.ftml` extension (e.g., `config.schema.ftml`)

The syntax is similar but serves different purposes:

```ftml schema
// Schema definition - defines what's allowed
user: {
  name: str,
  age: int<min=0>,
  tags: [str]
}
```

```ftml
// Data instance - contains actual values
user = {
  name = "John Doe",
  age = 30,
  tags = ["admin", "developer"]
}
```

## 3. Object Collections

Objects represent unordered key-value mappings.

### 3.1 Object Syntax in Data

In FTML data files, objects are enclosed in curly braces with key-value pairs separated by commas:

```ftml
user = {
  name = "John",
  age = 30,
  settings = {
    theme = "dark",
    notifications = true
  }
}
```

Key points:
- Keys and values are separated by equals sign (`=`)
- Pairs are separated by commas
- Trailing comma is optional
- Objects can be nested
- Keys must be unique within an object

### 3.2 Object Schema Definitions

In FTML schema files, there are two ways to define object types:

#### 3.2.1 Enumerated Fields (Specific Structure)

Define an object with specific named fields:

```ftml schema
// Schema definition
user: {
  name: str,
  age: int,
  email?: str  // Optional field
}
```

In strict mode, data must include all required fields and cannot include fields not defined in the schema.

#### 3.2.2 Typed Objects with Pattern Values (`{T}`)

Define an object where all keys are strings and all values must match a specific type:

```ftml schema
// Schema definition
counts: {int}  // Any string keys, but all values must be integers
```

This permits any number of properties (including zero), but each value must conform to the specified type.

Currently, FTML only supports string keys in typed objects (`{T}`). The type `T` can be any valid FTML type, including scalars, lists, or unions.

### 3.3 Object Schema Examples

```ftml schema
// Specific structure with required and optional fields
user: {
  name: str,
  age: int,
  email?: str  // Optional field (note the question mark)
}

// Any object with string keys and integer values (str keys, int values)
scores: {int}

// Dictionary mapping usernames to roles (str keys, str values)
roles: {str}

// Completely unconstrained object (any keys, any values)
// This is discouraged as it provides no validation
data: {}

// Object that must be empty (exactly zero properties)
empty_data: {}<max=0>
```

### 3.4 Object Data Examples

```ftml
// Object matching the 'user' schema
user = {
  name = "Alice",
  age = 28,
  email = "alice@example.com"  // Optional field provided
}

// Object matching the 'scores' schema
scores = {
  math = 95,
  science = 87,
  history = 92
}

// Object matching the 'roles' schema
roles = {
  "alice" = "admin",
  "bob" = "user",
  "charlie" = "moderator"
}

// Object matching the 'data' schema (anything is allowed)
data = {
  key1 = "value",
  key2 = 123,
  key3 = {
    nested = true
  }
}

// Object matching the 'empty_data' schema (exactly zero properties)
empty_data = {}
```

## 4. List Collections

Lists represent ordered sequences of values.

### 4.1 List Syntax in Data

In FTML data files, lists are enclosed in square brackets with elements separated by commas:

```ftml
// Data
colors = [
  "red",
  "green",
  "blue"
]

nested = [
  [1, 2],
  [3, 4]
]

numbers_inline = [1, 2, 3]

numbers_multline = [
  1, 
  2, 
  3,
]
```

Key points:
- Elements are separated by commas
- Trailing comma is optional
- Lists can contain elements of different types (if the schema allows)
- Lists can be nested

### 4.2 List Schema Definitions

In FTML schema files, there are two ways to define list types:

#### 4.2.1 Typed Lists (`[T]`)

Define a list where all elements must match a specific type:

```ftml schema
// Schema definition
tags: [str]  // List of strings
```

All elements in the list must conform to the specified type.

#### 4.2.2 Unconstrained Lists (`[]`)

Define a list that can contain elements of any type:

```ftml schema
// Schema definition
values: []  // List of any value types
```

This permits any value types in the list, including mixed types.

### 4.3 List Schema Examples

```ftml schema
// List of strings
names: [str]

// List of integers with min/max element count constraints
scores: [int]<min=1, max=5>

// List of specific objects
users: [{
  name: str,
  age: int
}]

// List of int list (nested)
matrix: [[int]]

// Unconstrained list (any value types)
// This is discouraged as it provides little validation
data: []

// List that must be empty (exactly zero elements)
empty_list: []<max=0>
```

### 4.4 List Data Examples

```ftml
// List matching the 'names' schema
names = ["Alice", "Bob", "Charlie"]

// List matching the 'scores' schema
scores = [95, 87, 92]

// List matching the 'users' schema
users = [
  {
    name = "Alice",
    age = 28
  },
  {
    name = "Bob",
    age = 32
  }
]

// List matching the 'matrix' schema
matrix = [
  [1, 2, 3],
  [4, 5, 6],
  [7, 8, 9]
]

// List matching the 'data' schema (anything is allowed)
data = [
  "string",
  123,
  true,
  {
    key = "value"
  }
]

// List matching the 'empty_list' schema (exactly zero properties)
empty_list = []
```

## 5. Collection Constraints

FTML provides two primary types of constraints for collections:
1. **Type constraints** - restricting what types of values can be included
2. **Size constraints** - restricting how many elements or properties can be included

These constraints can be combined to create precisely defined collection types.

### 5.1 Object Constraints

#### 5.1.1 Type Constraints

Objects can be constrained by the types of values they contain:

```ftml schema
// Object where all values must be integers
counts: {int}

// Object where all values must be strings
labels: {str}

// Object where all values must be booleans
flags: {bool}

// Object where all values must be objects (nested objects)
nested: {{}}

// Object where all values must be lists
collections: {[]}

// Object where all values must be lists of integers
itemCounts: {[int]}
```

In all these cases, keys must be strings as FTML only supports string keys for objects.

#### 5.1.2 Size Constraints

Objects can have constraints applied that limit the number of properties they contain:

```ftml schema
// Object with minimum 2 properties
required_fields: {}<min=2>

// Object with maximum 5 properties
limited_fields: {}<max=5>

// Object with between 2 and 10 properties
bounded_fields: {}<min=2, max=10>

// Object that must be empty (exactly zero properties)
empty_object: {}<max=0>
```

These constraints apply to the number of key-value pairs in the object, regardless of what the keys or values are.

An important distinction to understand:
```ftml schema
// Schema definition
any_data: {}           // This means "any object with any number of properties" (unconstrained)
empty_data: {}<max=0>  // means "must be an empty object with zero properties"
```

Both accept empty objects in data:
```ftml
// Data
any_data = {}
empty_data = {}
```

But only the unconstrained version allows properties to be added:
```ftml
// Data
any_data = {name = "value"}    // Valid (unconstrained)
empty_data = {name = "value"}  // Error (schema says a max of zero properties)
```

#### 5.1.3 Combined Constraints

Type and size constraints can be combined:

```ftml schema
// Object with integer values and between 1 and 5 properties
scores: {int}<min=1, max=5>

// Object with list values and at least 3 properties
categories: {[]}<min=3>

// Object of constrained integer values (0-100) with size limits (1-5 properties)
scores: {int<min=0, max=100>}<min=1, max=5>
```

### 5.2 List Constraints

#### 5.2.1 Type Constraints

Lists can be constrained by the types of elements they contain:

```ftml schema
// List where all elements must be integers
numbers: [int]

// List where all elements must be strings
names: [str]

// List where all elements must be booleans
flags: [bool]

// List where all elements must be objects
records: [{}]

// List where all elements must be lists (nested lists)
matrix: [[]]

// List where all elements must be lists of integers
rows: [[int]]
```

#### 5.2.2 Size Constraints

Lists can have constraints applied that limit the number of elements they contain:

```ftml schema
// List with minimum 2 elements
required_items: []<min=2>

// List with maximum 5 elements
limited_items: []<max=5>

// List with between 2 and 10 elements
bounded_items: []<min=2, max=10>

// List that must be empty (exactly zero elements)
empty_list: []<max=0>
```

These constraints apply to the number of elements in the list, regardless of what the elements are.

An important distinction to understand:
```ftml schema
// Schema definition
any_items: []           // This means "any list with any number of elements" (unconstrained)
empty_items: []<max=0>  // means "must be an empty list with zero elements"
```

Both accept empty lists in data:
```ftml
// Data
any_items = []
empty_items = []
```

But only the unconstrained version allows elements to be added:
```ftml
// Data
any_items = ["one", "two"]    // Valid (unconstrained)
empty_items = ["one", "two"]  // Error (schema says a max of zero elements)
```

#### 5.2.3 Combined Constraints

Type and size constraints can be combined:

```ftml schema
// List of integers with between 2 and 10 elements
scores: [int]<min=2, max=10>

// List of objects with at least 1 element
users: [{}]<min=1>

// List of constrained integers (0-100) with size limits (2-10 elements)
scores: [int<min=0, max=100>]<min=2, max=10>
```

### 5.3 Constraint Summary Table

| Collection Type | Syntax | Description |
|-----------------|--------|-------------|
| **Objects**     |        |             |
| Any object      | `{}` | Object with any properties and values |
| Typed object    | `{T}` | Object with string keys and values of type T |
| Sized object    | `{}<min=X, max=Y>` | Object with size constraints |
| Combined        | `{T}<min=X, max=Y>` | Object with type and size constraints |
| Nested object   | `{{}}` | Object with object values |
| Object of lists | `{[]}` | Object with list values |
| **Lists**       |        |             |
| Any list        | `[]` | List with any element types |
| Typed list      | `[T]` | List with elements of type T |
| Sized list      | `[]<min=X, max=Y>` | List with size constraints |
| Combined        | `[T]<min=X, max=Y>` | List with type and size constraints |
| List of objects | `[{}]` | List with object elements |
| Nested list     | `[[]]` | List with list elements |

## 6. Union Types in Collections

FTML supports powerful union type combinations for collections, allowing for flexible schema definitions.

### 6.1 Element-Level Union Types

Union types can be used within collections to allow multiple types for individual elements or values:

```ftml schema
// List where each element can be either a string OR an integer
mixed_list: [str | int]

// Object where each value can be either a string OR a boolean
mixed_values: {str | bool}

// List of elements that can be strings, numbers, or null
flexible_data: [str | int | float | null]
```

In these cases, each individual element/value can be any of the specified types.

### 6.2 Collection-Level Union Types

Union types can also be applied to entire collections, allowing for different collection type patterns:

```ftml schema
// Can be EITHER a list of integers OR a list of strings
number_or_text_list: [int] | [str]

// Can be EITHER an object with integer values OR an object with string values
counts_or_labels: {int} | {str}

// Can be EITHER a list of objects OR a list of strings
records_or_names: [{name: str, id: int}] | [str]

// Can be a list of integers OR an object with integer values OR a single integer OR null
flexible_number: [int] | {int} | int | null
```

In these cases, the entire collection must conform to one of the specified collection types.

### 6.3 Combined Union Types

Union types can be combined in sophisticated ways:

```ftml schema
// Can be EITHER a list of mixed types (str or int) OR a list of booleans
mixed_or_flags: [str | int] | [bool]

// Can be EITHER an object with string values OR an object with boolean values
// OR an object with integer values within a specific range
config_options: {str} | {bool} | {int<min=0, max=100>}

// Can be EITHER a list of strings OR a specific object structure
identifier_or_details: [str] | {
  name: str,
  description: str,
  tags: [str]
}
```

### 6.4 Union Types with Size Constraints

Union types can be combined with size constraints:

```ftml schema
// Can be EITHER a list of strings (2-5 elements) OR a list of integers (any number)
limited_strings_or_numbers: [str]<min=2, max=5> | [int]

// Can be EITHER an object with string values (max 3 properties) 
// OR an object with integer values (min 1 property)
limited_text_or_counts: {str}<max=3> | {int}<min=1>
```

### 6.5 Union Types Summary Table

| Union Pattern | Example | Description |
|---------------|---------|-------------|
| **Element-Level Unions** | | |
| `[T1 \| T2]` | `[str \| int]` | List where each element can be any of the specified types |
| `{T1 \| T2}` | `{str \| bool}` | Object where each value can be any of the specified types |
| **Collection-Level Unions** | | |
| `[T1] \| [T2]` | `[str] \| [int]` | Either a list of T1 OR a list of T2 |
| `{T1} \| {T2}` | `{str} \| {int}` | Either an object with T1 values OR an object with T2 values |
| **Collection Size Constraints** | | |
| `[T]<constraints>` | `[str]<min=2, max=5>` | List with size constraints |
| `{T}<constraints>` | `{str}<min=1, max=3>` | Object with property count constraints |
| **Element/Value Constraints** | | |
| `[T<constraints>]` | `[int<min=0, max=100>]` | List of constrained elements |
| `{T<constraints>}` | `{int<min=0, max=100>}` | Object with constrained values |
| **Combined Constraints** | | |
| `[T<constraints>]<constraints>` | `[int<min=0, max=100>]<min=2, max=5>` | Size-constrained list of constrained elements |
| `{T<constraints>}<constraints>` | `{int<min=0, max=100>}<min=1, max=3>` | Size-constrained object with constrained values |



## 7. Default Values for Collections

FTML supports default values for both scalar types and collections, allowing for powerful data population when values are not provided.

### 7.1 Default Value Basics

Default values are specified using the `=` symbol after the type definition:

```ftml schema
// Schema with default values
name: str = "Anonymous"
enabled: bool = true
count: int = 0
```

Important points about default values:

- Fields with default values become implicitly optional (no need for the `?` marker)
- Default values are used when the field is missing in the data
- The type of the default value must match the declared type

### 7.2 Collection Default Values

Collections can have default values at two different levels:

#### 7.2.1 Simple Collection Defaults

```ftml schema
// Default empty collections
tags: [str] = []
settings: {} = {}

// Default populated collections
roles: [str] = ["user", "guest"]
scores: {int} = {math = 0, science = 0}
```

#### 7.2.2 Field-Level vs Object-Level Defaults

FTML supports both field-level defaults (within collections) and object-level defaults (for entire collections):

```ftml schema
// Field-level defaults within an object
user: {
  name: str = "Anonymous",  // Optional, has default
  active: bool = true,      // Optional, has default
  email: str                // Required 
}

// Object-level default for the entire structure
config: {
  theme: str,
  debug: bool
} = {                       // Optional, has default Object
  theme = "light",
  debug = false
}

// Both field-level and object-level defaults
profile: {
  name: str = "Guest",      // Optional, has default
  settings: {
    theme: str = "light",   // Nested, optional, has default
    notifications: bool = true
  }
} = {                       // Optional, has default Object
  name = "Default User",
  settings = {
    theme = "system",
    notifications = false
  }
}
```

### 7.3 Default Value Precedence

The precedence for applying default values follows these rules:

1. **Existing data**: Values in the data always take precedence over any defaults
2. **Field-level defaults**: If a parent object exists but a field is missing, field-level defaults apply
3. **Object-level defaults**: If an entire object is missing, the object-level default is used

### 7.4 Default Value Examples

#### 7.4.1 Basic Example

```ftml schema
// Schema
username: str = "Anonymous"
age: int = 0
```

```ftml
// Empty data
// After applying defaults: {username = "Anonymous", age = 0}

// Partial data
username = "John"
// After applying defaults: {username = "John", age = 0}
```

#### 7.4.2 Nested Object Example

```ftml schema
// Schema
user: {
  name: str = "Anonymous",
  settings: {
    theme: str = "light",
    notifications: bool = true
  }
} = {
  name = "Guest",
  settings = {
    theme = "system",
    notifications = false
  }
}
```

```ftml
// Empty data
// Result: Uses object default for the entire structure
// {
//   user = {
//     name = "Guest",
//     settings = {
//       theme = "system",
//       notifications = false
//     }
//   }
// }

// Partial data with user but missing settings
user = {
  name = "John"
}
// Result: Uses field-level defaults for the missing settings
// {
//   user = {
//     name = "John",
//     settings = {
//       theme = "light",
//       notifications = true
//     }
//   }
// }

// Partial data with user and partial settings
user = {
  name = "John",
  settings = {
    theme = "dark"
  }
}
// Result: Uses field-level default for the missing notifications
// {
//   user = {
//     name = "John",
//     settings = {
//       theme = "dark",
//       notifications = true
//     }
//   }
// }
```

#### 7.4.3 List Example

```ftml schema
// Schema
roles: [str] = ["user"]
user?: {
  name: str,
  permissions: [str] = ["read"]
}
```

```ftml
// Empty data
// Result: Uses default for roles, user is omitted (optional)
// {
//   roles = ["user"]
// }

// With user data
roles = ["admin"]
user = {
  name = "John"
}
// Result: Uses provided roles and field-level default for permissions
// {
//   roles = ["admin"],
//   user = {
//     name = "John",
//     permissions = ["read"]
//   }
// }
```

### 7.5 Default Value Rules

1. **Type matching**: Default values must match the declared type
2. **Optionality**: Fields with default values are implicitly optional
3. **Hierarchy**: Nested defaults follow a scope hierarchy (field-level vs object-level)
4. **Validation**: Default values must pass all type constraints
5. **Propagation**: Defaults are applied recursively to nested structures

## 8. Collections & Strict Mode

FTML schemas can be validated in strict or non-strict mode:

### 8.1 Strict Mode Behavior

In strict mode:
- For enumerated objects (`{name: str, age: int}`), extra properties are rejected
- For pattern objects (`{int}`), extra properties are allowed if they match the pattern
- For typed lists (`[str]`), elements of the wrong type are rejected
- For unconstrained lists (`[]`), any element types are allowed

### 8.2 Non-Strict Mode Behavior

In non-strict mode:
- For enumerated objects, extra properties are allowed
- All other behaviors remain the same as strict mode

## 9. Nested Collections

Collections can be arbitrarily nested to create complex structures:

```ftml schema
// Schema definition
organization: {
  name: str,
  departments: [{
    name: str,
    manager?: {
      name: str,
      email: str
    },
    employees: [{
      name: str,
      role: str,
      skills: [str]
    }]
  }]
}
```

```ftml
// Data instance
organization = {
  name = "Acme Corp",
  departments = [
    {
      name = "Engineering",
      manager = {
        name = "Alice Johnson",
        email = "alice@example.com"
      },
      employees = [
        {
          name = "Bob Smith",
          role = "Developer",
          skills = ["Python", "JavaScript", "AWS"]
        },
        {
          name = "Carol Davis",
          role = "QA Engineer",
          skills = ["Testing", "Automation"]
        }
      ]
    },
    {
      name = "Marketing",
      employees = []
    }
  ]
}
```

## 10. Best Practices

### 10.1 Schema Design

1. **Prefer enumerated objects** (`{name: str, age: int}`) when you know the exact field names
2. **Use typed pattern objects** (`{int}`) when fields are dynamic but values should be of the same type
3. **Use typed lists** (`[str]`) instead of unconstrained lists (`[]`) whenever possible
4. **Apply container constraints** to enforce size and property requirements
5. **Provide sensible defaults** for optional collections

### 10.2 Data Organization

1. **Use consistent indentation** for readability
2. **Group related properties** together in objects
3. **Add trailing commas** in multiline collections for easier editing
4. **Use line breaks** to make complex structures more readable
5. **Consider splitting** very large collections into multiple smaller ones

## 11. Error Patterns to Avoid

1. **Mixed Schema and Data Syntax**:
   ```
   // Incorrect - mixing schema syntax in data
   user = {
     name: "John"  // Using : instead of =
   }
   ```

2. **Unconstrained Collections**:
   ```
   // Discouraged - provides no validation
   data: {}
   values: []
   ```

3. **Inconsistent Nesting**:
   ```
   // Overly complex nesting
   data = {
     users = {
       user1 = {
         profile = {
           details = {
             // Too deep, consider flattening
           }
         }
       }
     }
   }
   ```
