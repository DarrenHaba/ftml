# FTML Comments Specification

## 1. Overview

FTML (FlexTag Markup Language) supports a comprehensive comment system allowing both regular annotations and documentation comments. All comments in FTML are preserved during round-trip parsing and serialization, ensuring that the original document's structure and annotations remain intact.

## 2. Comment Types

FTML supports three primary types of comments:

| Type | Syntax | Purpose | Example |
|------|--------|---------|---------|
| Regular comment | `// text` | General annotations and explanations | `// This is a configuration file` |
| Outer doc comment | `/// text` | Documentation for the following item | `/// Configuration for port number` |
| Inner doc comment | `//! text` | Documentation for the enclosing item | `//! Application settings schema` |

### 2.1 Regular Comments

Regular comments start with `//` and continue to the end of the line. They're used for general annotations, explanations, and notes throughout FTML documents.

```ftml
// This is a regular comment
name = "My Application"  // This is also a regular comment
```

### 2.2 Documentation Comments

Documentation comments are special comments that associate documentation with specific elements in the FTML structure:

#### 2.2.1 Outer Doc Comments (`///`)

Outer documentation comments document the item that follows them, similar to Rust's `///` doc comments. They attach to the next FTML node in the document.

```ftml
/// This documents the name field
/// Can span multiple lines
name = "My Application"

/// Documentation for the settings object
settings = {
  // Regular settings content
}
```

#### 2.2.2 Inner Doc Comments (`//!`)

Inner documentation comments document the enclosing item itself, similar to Rust's `//!` doc comments. They can appear in two contexts:

1. **Document-level**: At the beginning of a file, documenting the entire document
2. **Container-level**: Inside a container (object or list), right after the opening delimiter

```ftml
//! Documentation for this entire FTML document
//! Can span multiple lines

name = "My Application"

settings = {
  //! Documentation for the settings object
  //! Describes everything in this object
  
  port = 8080
}

features = [
  //! List of supported application features
  
  "authentication",
  "logging"
]
```

## 3. Comment Attachment Rules

FTML uses a deterministic model for attaching comments to nodes in the AST:

### 3.1 Regular Comment Attachment

Regular comments (`//`) are categorized and attached as follows:

1. **Leading Comments**: Comments on lines before a node are attached as leading comments to that node
2. **Inline Comments**: A comment on the same line as a node is attached as an inline comment to that node

Example:
```ftml
// This is a leading comment for key1
// This is a second leading comment for key1
key1 = "value1"  // This is an inline comment for key1

// This is a leading comment for key2
key2 = "value2"
```

### 3.2 Documentation Comment Attachment

Documentation comments attach differently based on their type:

1. **Outer Doc Comments** (`///`):
    - Attach to the node that immediately follows them
    - Multiple consecutive outer doc comments are grouped together

2. **Inner Doc Comments** (`//!`):
    - When at the beginning of a file, attach to the document node
    - When after an opening delimiter, attach to the containing collection node

Example:
```ftml
//! Documentation for the entire document
//! Second line of document documentation

/// Documentation for the name field
name = "My Application"

settings = {
  //! Documentation for the settings object contents
  
  /// Documentation for the port field
  port = 8080
}
```

### 3.3 Nested Structure Comment Attachment

Comments in nested structures follow the same rules, with each level maintaining its own comment attachments:

```ftml
nested_list = [
  // Comment for first item
  [
    //! Inner doc for nested list
    "item1",  // Inline comment for item1
    "item2"
  ],
  
  // Comment for second item
  {
    //! Inner doc for nested object
    key = "value"  // Inline comment for key
  }
]
```

## 4. Implementation Details

### 4.1 Two-Pass Parsing

FTML uses a two-pass parsing approach to effectively handle comments:

1. **First Pass**: Build the structural AST, ignoring comments
2. **Second Pass**: Attach comments to the appropriate nodes in the existing AST

This clean, separation of concerns ensures robust comment handling even in complex nested structures.

### 4.2 Comment Storage in AST

Comments are stored in the AST nodes as follows:

1. **Regular Comments**:
    - `leading_comments`: Array of Comment objects that appear before the node
    - `inline_comment`: Single Comment object that appears on the same line as the node

2. **Documentation Comments**:
    - `outer_doc_comments`: Array of outer doc comments that document this node
    - `inner_doc_comments`: Array of inner doc comments that document this container

### 4.3 AST Node Comment Properties

| Node Type | Comment Properties | Description |
|-----------|-------------------|-------------|
| DocumentNode | `inner_doc_comments` | Comments attached to the entire document |
| KeyValueNode | `leading_comments`, `inline_comment`, `outer_doc_comments` | Comments for key-value pairs |
| ObjectNode | `leading_comments`, `inline_comment`, `inner_doc_comments` | Comments for object containers |
| ListNode | `leading_comments`, `inline_comment`, `inner_doc_comments`, `inline_comment_end` | Comments for list containers |
| ScalarNode | `leading_comments`, `inline_comment` | Comments for scalar values |

### 4.4 Roundtrip Preservation

During serialization, comments are output in their original positions relative to their attached nodes:

1. Document-level inner doc comments are output at the beginning of the file
2. Leading comments (including outer doc comments) are output before their node
3. Inline comments are output at the end of the line containing their node
4. Container inner doc comments are output right after the opening delimiter

## 5. Examples

### 5.1 Basic Comments

```ftml
// Regular comment
key1 = "value1"  // Inline comment

// Multiple
// leading comments
key2 = "value2"
```

### 5.2 Documentation Comments

```ftml
//! Documentation for this FTML file
//! Second line of file documentation

/// Documentation for key1
key1 = "value1"

/// Documentation for the settings object
settings = {
  //! Documentation for settings object contents
  
  /// Documentation for port
  port = 8080
}
```

### 5.3 Nested Structure Comments

```ftml
// Comment for nested structure
nested = [
  /// Doc comment for first item
  [
    //! Inner doc for nested list
    "item1",  // Comment for item1
    "item2"   // Comment for item2
  ],
  
  // Comment for second item
  {
    //! Inner doc for nested object
    key = "value"  // Comment for key
  }
]
```

### 5.4 Complex Comment Example

```ftml
//! Document-level inner doc comment
//! Another document-level comment

// Regular leading comment for key1
/// Outer doc comment for key1
key1 = "value1"  // Inline comment for key1

/// Outer doc comment for list
/// Another outer doc comment for list
my_list = [
  //! Inner doc comment for list
  //! Another inner doc comment for list
  
  /// Outer doc comment for list item
  "first",
  
  /// Outer doc comment for nested list
  [
    //! Inner doc comment for nested list
    "nested item"
  ]
]

/// Outer doc comment for object
my_obj = {
  //! Inner doc comment for object
  
  /// Outer doc comment for property
  prop1 = "value1"
}
```

## 6. Comments in Schema Definitions

While FTML supports full round-trip comment preservation for data files, comments in schema definitions are handled differently:

### 6.1 Schema Comment Handling

Schema definitions can contain all standard FTML comment types (`//`, `///`, `//!`), allowing developers to document their schemas. However:

1. **Comments are Ignored**: All comments in schema files are removed during schema parsing
2. **No Round-trip Preservation**: Unlike with data files, comments in schemas are not preserved
3. **Documentation Purpose Only**: Comments in schemas serve solely as documentation for humans reading the schema

### 6.2 Schema Parser Behavior

The schema parser:
- Removes all comments before processing the schema structure
- Does not build AST nodes for comments
- Does not attach comments to schema type nodes
- Does not reintroduce comments when using the schema for validation

### 6.3 Rationale

This approach is intentional because:
- Schemas are used only for validation during data loading/dumping
- There is no need to load/dump the schema itself with preserved comments
- Simplifies the schema parsing and validation process

### 6.4 Example

```ftml
// User schema definition
//! Defines the structure of a user record

// Basic user information
name: str<min_length=1>  // Name must not be empty
age?: int<min=0>         // Optional age field
roles: [str]             // List of role strings

// Contact information section
contact: {
  //! User contact details
  email: str             // Primary email address
  phone?: str            // Optional phone number
}
```

## 7. Best Practices

1. **Use Appropriate Comment Types**:
   - Use regular comments (`//`) for general notes and annotations
   - Use outer doc comments (`///`) to document specific fields and values
   - Use inner doc comments (`//!`) to document containers and the file itself

2. **Comment Placement**:
   - Place outer doc comments immediately before the item they document
   - Place inner doc comments at the start of the file or immediately after opening brackets/braces
   - Avoid placing comments between a comma and the next item in collections

3. **Documentation Style**:
   - Keep documentation comments clear and concise
   - Use consistent formatting within doc comments
   - For multiline documentation, use consecutive doc comments rather than line breaks

4. **Grouping Comments**:
   - Group related comments together
   - Separate groups of comments with blank lines when appropriate

5. **Round-trip Preservation**:
   - Remember that all comments will be preserved when using libraries that support round-trip parsing
   - Consider comment placement with respect to how the document will be serialized



# FTML Comments: Edge Cases and Special Handling

## 1. Orphaned Comments

The FTML comment attachment rules work well for most cases, but there are several edge cases where comments become "orphaned" - they don't have a clear node to attach to under the current rules:

### 1.1 Document-Level Orphaned Comments

Comments that appear at the end of a document (after all nodes) have no subsequent node to attach to as leading comments:

```ftml
key = "value"
// This comment has nothing after it
// Another trailing comment
```

### 1.2 Collection-Level Orphaned Comments

Comments that appear inside collections but after the last element/property:

**Lists:**
```ftml
my_list = [
    "item1",
    // This comment appears after the last item
    // Another trailing comment
]
```

**Objects:**
```ftml
my_obj = {
    prop = "value",
    // This comment appears after the last property
    // Another trailing comment
}
```

### 1.3 Empty Document Comments

Comments in a document with no nodes have nowhere to attach:

```ftml
// These comments exist in an otherwise empty document
// Another comment
```

## 2. Special Handling for Orphaned Comments

To preserve all comments during round-trip parsing, FTML handles these edge cases as follows:

### 2.1 Document-Level Orphaned Comments

Comments that appear after the last node in a document are attached to the document node itself as `leading_comments`. This ensures they're preserved even though they aren't leading any specific node.

### 2.2 Collection-Level Orphaned Comments

#### Lists
Comments that appear inside a list but after the last element are attached to the closing bracket as "leading comments of the end delimiter." The `ListNode` class provides an `inline_comment_end` property to support this.

#### Objects
Similarly, comments that appear inside an object but after the last property are attached to the closing brace as "leading comments of the end delimiter."

### 2.3 Empty Document Comments

For documents containing only comments, all comments are attached to the document node itself as `leading_comments`.

## 3. Implementation Implications

The attachment of orphaned comments represents a departure from the strict "leading" or "inline" categorization:

1. These comments aren't truly "leading" anything in the traditional sense
2. They're preserved primarily to ensure round-trip fidelity
3. The parser must specifically check for these cases

## 4. Usage Considerations

When writing FTML documents:

1. **Prefer standard placement**: When possible, place comments before the node they describe
2. **Understand preservation boundaries**: Comments placed after the last node in any context might not be attached semantically to what they appear to follow
3. **Documentation comments edge cases**: Note that outer doc comments (`///`) that have no subsequent node may not be properly categorized as documentation

This handling ensures that all comments in the source document are preserved even when they don't fit neatly into the standard attachment rules.