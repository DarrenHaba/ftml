#   FTML Parsing & Serialization Internals

##   1. Overview

This document describes the internal workings of FTML parsing and serialization processes. It is primarily intended for implementers and contributors to FTML libraries, as well as advanced users who need to understand the internals for debugging or extension purposes.

FTML employs a multi-stage processing pipeline for both parsing and serialization, with special attention to preserving comments and structural information for round-trip processing. This design allows FTML to maintain data integrity and developer annotations across multiple read/write cycles.

##   2. Parsing Pipeline

FTML parsing follows a carefully orchestrated, staged approach, designed for both efficiency and accuracy in representing the structure and content of FTML documents.

###   2.1 Parsing Stages

1.  **Lexical Analysis (Tokenization)**:

   * Convert raw text into a stream of tokens.
   * Preserve positional information (line, column) for accurate error reporting and debugging.
   * Identify and categorize comments, maintaining their positions within the text.

2.  **Structural Parsing**:

   * Build an Abstract Syntax Tree (AST) from the token stream.
   * Parse the core document structure (key-value pairs, objects, lists) while initially ignoring comments.

3.  **Comment Attachment**:

   * Process the token stream a second time, focusing on comment placement.
   * Attach comments to the appropriate AST nodes based on a set of predefined rules that consider proximity and positioning.

4.  **Schema Validation** (Optional):

   * Validate the parsed data against a predefined schema (if provided).
   * Apply default values from the schema to the parsed data, if necessary.

5.  **Structure Conversion**:

   * Convert the AST into a user-friendly, dictionary-like structure for ease of access and manipulation in applications.
   * Optionally, preserve references to AST nodes internally within this dictionary-like structure to enable round-trip serialization.

###   2.2 Tokenization

The tokenizer is responsible for the first stage of the parsing pipeline: breaking down the raw FTML text into a sequence of meaningful units called "tokens." Each token represents a basic element of the language, such as a keyword, an identifier, a string literal, or a punctuation mark.

```
key = "value"  //   comment
│ │ │    │     │
│ │ │    │     └─ COMMENT
│ │ │    └─────── STRING
│ │ └──────────── EQUAL
│ └────────────── WHITESPACE
└──────────────── IDENT
```

This breakdown illustrates how the tokenizer processes a simple FTML line, identifying each component and its role.

####   2.2.1 Token Types

The tokenizer categorizes each token into one of the following types:

|   Token Type          |   Description                        |   Pattern                       |   Example           |
|   :------------------ |   :--------------------------------- |   :---------------------------- |   :---------------- |
|   `IDENT`             |   Identifier                         |   `[A-Za-z_][A-Za-z0-9_]*`      |   `name`            |
|   `STRING`            |   Double-quoted string               |   `"(?:\\.|[^"\\\\])*"`          |   `"value"`         |
|   `SINGLE_STRING`     |   Single-quoted string               |   `'(?:''|[^'])*'`              |   `'value'`         |
|   `INT`               |   Integer                            |   `[+-]?\d+`                    |   `42`              |
|   `FLOAT`             |   Float                              |   `[+-]?\d+\.\d+`              |   `3.14`            |
|   `BOOL`              |   Boolean                            |   `true\|false`                |   `true`            |
|   `NULL`              |   Null                               |   `null`                        |   `null`            |
|   `LBRACE`            |   Left brace                         |   `{`                           |   `{`               |
|   `RBRACE`            |   Right brace                        |   `}`                           |   `}`               |
|   `LBRACKET`          |   Left bracket                       |   `[`                           |   `[`               |
|   `RBRACKET`          |   Right bracket                      |   `]`                           |   `]`               |
|   `EQUAL`             |   Equal sign                         |   `=`                           |   `=`               |
|   `COMMA`             |   Comma                              |   `,`                           |   `,`               |
|   `OUTER_DOC_COMMENT`   |   Outer documentation comment        |   `///[^\n]*`                  |   `///   Doc comment` |
|   `INNER_DOC_COMMENT`   |   Inner documentation comment        |   `//![^\n]*`                  |   `//!   Inner doc`   |
|   `COMMENT`           |   Regular comment                    |   `//[^\n]*`                   |   `//   Comment`     |
|   `WHITESPACE`        |   Whitespace                         |   `[ \t\r]+`                    |   `    `             |
|   `NEWLINE`           |   Newline                            |   `\n`                          |   `\n`              |
|   `EOF`               |   End of file                        |   N/A                           |   N/A               |

####   2.2.2 Tokenizer Implementation

The tokenizer is implemented to provide detailed information with each token, which is crucial for subsequent parsing stages and error reporting.

Each token includes:

* **Type Information**: The `TokenType` enum value, indicating the token's category.
* **Value**: The actual text of the token (e.g., `"Hello world"` for a string, `42` for an integer).
* **Positional Information**: The line and column numbers where the token begins in the source text. This is essential for pinpointing the location of errors.
* **Special Handling for Comments**: Comments are treated as tokens to preserve them during parsing and ensure they can be included during serialization.

```python
#   Example token representation
Token(type=TokenType.STRING, value="Hello world", line=3, col=10)
```

##   3. AST Structure

The second stage of the parsing pipeline involves building an Abstract Syntax Tree (AST). The AST is a tree-like representation of the FTML document's structure, making it easier for the parser and other tools to understand and manipulate the data.

###   3.1 AST Node Types

The AST is composed of different types of nodes, each representing a specific construct in the FTML document:

* **DocumentNode**: This is the root node of the AST, representing the entire FTML document. It contains all the top-level key-value pairs.
* **KeyValueNode**: Represents a key-value pair, the fundamental building block of FTML.
* **ScalarNode**: Represents a single, primitive value, such as a string, number, boolean, or null.
* **ObjectNode**: Represents an object, which is a collection of nested key-value pairs enclosed in braces (`{}`).
* **ListNode**: Represents a list, which is an ordered sequence of values enclosed in brackets (`[]`).

###   3.2 Node Properties

Each AST node type stores the following information:

* **Core Value Data**: The actual data represented by the node (e.g., the string value of a `ScalarNode`, the key of a `KeyValueNode`).
* **Positional Information**: The line and column numbers where the node originates in the source text. This is used for error reporting and debugging.
* **Comment Containers**: Nodes can hold various types of comments:
   * `leading_comments`: Comments that appear on lines preceding the node.
   * `inline_comment`: A comment that appears on the same line as the node.
   * `outer_doc_comments`: Documentation comments ( `///` ) that precede and describe the node.
   * `inner_doc_comments`: Documentation comments ( `//!` ) that appear within container nodes (objects, lists) to describe their contents.

```
//   Example AST structure representation
DocumentNode
    ├── inner_doc_comments: []
    ├── leading_comments: []
    └── items:
        ├── "name" → KeyValueNode
        │       ├── key: "name"
        │       ├── value: ScalarNode("value")
        │       ├── leading_comments: [Comment("Comment for name")]
        │       └── inline_comment: null
        └── "obj" → KeyValueNode
                ├── key: "obj"
                ├── value: ObjectNode
                │       ├── items: {...}
                │       ├── leading_comments: []
                │       └── inline_comment: Comment("Inline comment")
                ├── leading_comments: []
                └── inline_comment: null
```

This example illustrates how the AST represents an FTML document, including the hierarchical structure and the attachment of comments to specific nodes.

##   4. Parsing Process

FTML parsing employs a two-pass approach to handle the complexities of both document structure and comment placement effectively.

###   4.1 First Pass: Structural Parsing

The first pass focuses solely on building the core AST structure. It processes the token stream and creates the tree of nodes representing key-value pairs, objects, and lists, while **ignoring** any comment tokens.

* Builds the AST structure while ignoring comments.
* Focuses on correctly parsing the relationships between key-value pairs, objects, and lists.
* Handles nested structures and different value types.
* Creates a "skeleton" AST that captures the document's hierarchy and data, but without comment attachments.
* Includes position information in AST nodes for error reporting.

###   4.2 Second Pass: Comment Attachment

The second pass revisits the token stream, this time concentrating on the comment tokens. It uses a set of rules to determine where each comment should be attached within the AST.

* Processes the token stream a second time, focusing exclusively on comments.
* Attaches each comment to the most appropriate AST node based on proximity and context.
* Handles special documentation comments ( `///` and `//!` ) according to their specific rules.
* Ensures that comment text and position information are preserved in the AST.

###   4.3 Comment Attachment Rules

The comment attachment process follows these rules to ensure comments are placed accurately:

* **Leading Comments**: Comments that appear on lines preceding a node are attached to that node's `leading_comments` list.
* **Inline Comments**: A comment on the same line as a node is attached to the node's `inline_comment` property.
* **Document-Level Inner Doc Comments**: `//!` comments at the very beginning of the file are attached to the `DocumentNode`'s `inner_doc_comments` list.
* **Container Inner Doc Comments**: `//!` comments immediately after an opening delimiter (`{` or `[`) within an object or list are attached to the `ObjectNode` or `ListNode`'s `inner_doc_comments` list.
* **Outer Doc Comments**: `///` comments on lines immediately preceding a node are attached to the node's `outer_doc_comments` list.

##   5. Serialization Pipeline

FTML serialization is the process of converting a parsed FTML structure (represented by an AST or a dictionary) back into its textual representation. This process aims to be the inverse of parsing, preserving the original structure and all associated comments to ensure accurate round-trip processing.

###   5.1 Serialization Stages

1.  **AST Reconstruction**:

   * Recreate the AST from the dictionary-like structure, or use the AST preserved during parsing.
   * Ensure that all comments are correctly attached to their corresponding nodes.

2.  **Structure Traversal**:

   * Traverse the AST in a depth-first order to systematically visit each node.
   * Generate the textual representation of each node, preserving the hierarchical structure of the document.

3.  **Comment Inclusion**:

   * Incorporate comments into the output text at the appropriate positions, respecting their original placement relative to other elements.
   * Strive to maintain the original formatting and spacing of comments as much as possible.

4.  **Output Formatting**:

   * Apply consistent indentation and spacing rules to enhance readability.
   * Format multiline structures (objects and lists) in a clear and organized manner.

###   5.2 AST-to-Text Conversion

The core of the serialization process lies in converting the various AST node types back into their corresponding FTML text representations.

####   5.2.1 Document Serialization

The serialization of a `DocumentNode` involves iterating through its key-value pairs and generating the text for each, along with any comments associated with the document itself.

```python
def serialize_document(document):
    lines = []

    #   Add document inner doc comments (//!)
    for comment in document.inner_doc_comments:
        lines.append(f"//! {comment.text}")

    #   Add a blank line after doc comments if present
    if document.inner_doc_comments:
        lines.append("")

    #   Add document leading comments
    for comment in document.leading_comments:
        lines.append(f"//   {comment.text}")

    #   Add a blank line after leading comments if present
    if document.leading_comments:
        lines.append("")

    #   Serialize each key-value pair
    for key, kv_node in document.items.items():
        lines.extend(serialize_key_value(kv_node))
        lines.append("")  #   Blank line after each key-value pair

    #   Remove the last blank line if there is one
    if lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)
```

####   5.2.2 Primitive Value Serialization

Scalar values are converted to their respective text representations (e.g., strings are enclosed in quotes, booleans are converted to "true" or "false").

```python
def serialize_scalar(node):
    value = node.value

    if isinstance(value, str):
        #   Escape special characters
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'

    elif isinstance(value, bool):
        return str(value).lower()

    elif value is None:
        return "null"

    else:
        #   For numbers, just convert to string
        return str(value)
```

####   5.2.3 Collection Serialization

Objects and lists are serialized recursively, with indentation to represent their nested structure.

```python
def serialize_object(node, indent=0):
    if not node.items:
        return "{}"

    indent_str = "  " * indent
    lines = ["{"]

    #   Add inner doc comments
    for comment in node.inner_doc_comments:
        lines.append(f"{indent_str}//! {comment.text}")

    #   Serialize each key-value pair
    for key, kv_node in node.items.items():
        #   Add comments and the key-value itself
        #   ...

    lines.append(f"{indent_str}}}")
    return "\n".join(lines)
```

###   5.3 Maintaining Structural Fidelity

The serializer ensures that the output FTML text adheres to the language's syntax rules:

* Root-level key-value pairs are separated by newlines.
* Object properties and list elements are separated by commas.
* Nesting is represented using braces and brackets.

###   5.4 Comment Preservation

The serializer meticulously places comments back into the output text, respecting their original attachment to AST nodes:

```
//   Leading comments appear before their node
key = "value"  //   Inline comments appear at end of line

object = {
    //!   Inner doc comments appear after opening delimiter
    prop = "value"
}
```

###   5.5 Indentation and Formatting

Consistent formatting is applied to the output to enhance readability:

* Indentation is used to represent nesting levels (typically 2 or 4 spaces).
* Spacing is added around delimiters (`=`, `,`, `{`, `}`, `[`, `]`).
* Line breaks are inserted to separate elements in multiline structures.
* Alignment is used to improve the visual organization of related items.

##   6. Round-Trip Preservation

FTML is designed to support round-trip parsing and serialization, meaning that an FTML document can be parsed into an internal representation and then serialized back to text without losing any significant information, including comments and structural details.

###   6.1 The FTMLDict Class

The `FTMLDict` class, a subclass of the standard Python `dict`, plays a crucial role in enabling round-trip preservation. It augments the dictionary with the ability to store a reference to the corresponding AST node.

```python
class FTMLDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ast_node = None  #   Holds the AST node
```

###   6.2 Preserving AST During Dictionary Operations

When an `FTMLDict` is modified (e.g., adding, updating, or deleting a key), the following actions are taken:

1.  The public dictionary interface is updated to reflect the change.
2.  The internal AST representation is synchronized to mirror the dictionary's state.
3.  Comments attached to unchanged AST nodes are preserved.
4.  New or modified AST nodes are created without any associated comments.

###   6.3 Dictionary to AST Conversion

The `_dict_to_ast` function is responsible for converting an `FTMLDict` (or a regular `dict`) back into an AST. It intelligently reuses existing AST nodes and their associated comments when possible, ensuring that comments are preserved during serialization.

```python
def _dict_to_ast(data):
    """Convert dictionary to AST, preserving comments if available."""
    doc = DocumentNode()

    #   If data has an attached AST node, preserve its comments
    original_ast = getattr(data, '_ast_node', None)
    if original_ast and isinstance(original_ast, DocumentNode):
        doc.leading_comments = original_ast.leading_comments
        doc.inline_comment = original_ast.inline_comment
        doc.inner_doc_comments = getattr(original_ast, 'inner_doc_comments', [])

    #   Process each key in the data dictionary
    for key, value in data.items():
        value_node = _value_to_node(value, ...)
        kv_node = KeyValueNode(key, value_node, -1, -1)

        #   Copy comments if original key exists
        if original_ast and key in original_ast.items:
            original_kv = original_ast.items[key]
            kv_node.leading_comments = original_kv.leading_comments
            kv_node.inline_comment = original_kv.inline_comment
            #   ...

        doc.items[key] = kv_node

    return doc
```

##   7. Error Handling

FTML parsers are designed to provide robust error handling, offering informative error messages to aid in debugging and issue resolution.

###   7.1 Error Types

FTML parsers can encounter several types of errors during the parsing process:

* **Lexical Errors**: These occur during tokenization when the parser encounters invalid characters or malformed tokens (e.g., an unterminated string).
* **Syntax Errors**: These arise when the token stream violates the expected grammar of the FTML language (e.g., a missing equals sign or comma).
* **Semantic Errors**: These occur when the syntax is valid, but the structure or meaning of the FTML document is invalid according to the language's rules (e.g., duplicate keys within an object).

###   7.2 Error Information

To facilitate effective error diagnosis, FTML parsers provide rich information with each error:

* **Error Code or Type**: A categorization of the error to help in programmatic handling.
* **Line and Column Position**: The precise location in the source text where the error occurred.
* **Detailed Message**: A human-readable explanation of the error.
* **Context (Nearby Text)**: A snippet of the surrounding text to provide context.

###   7.3 Error Recovery

FTML parsers employ error recovery strategies to minimize the impact of errors and allow parsing to continue as much as possible:

* **Tokenizer**: The tokenizer may skip invalid input until it can identify a valid token, allowing parsing to proceed after a lexical error.
* **Parser**: The parser may attempt to skip to the next key-value pair or the next closing delimiter (`}` or `]`) after encountering a syntax error, enabling it to parse subsequent parts of the document.
* **Comment Attacher**: The comment attacher may skip invalid or unattachable comments, ensuring that the rest of the document's structure is processed.

##   8. Implementation Considerations

Efficient and robust FTML parsing and serialization require careful consideration of several implementation details.

###   8.1 Performance Optimizations

* **Minimize String Copying**: String operations can be expensive. Implementations should strive to minimize unnecessary string copying.
* **Appropriate Data Structures**: Choosing the right data structures for token streams and AST representation can significantly impact performance.
* **Balance Memory and Fidelity**: There's often a trade-off between memory usage and the fidelity of comment preservation. Implementations should consider this balance based on the application's requirements.
* **Optional Comment Preservation**: For performance-critical applications where comment preservation is not essential, consider providing an option to disable comment processing.

###   8.2 Error Recovery Strategies

Robust parsers implement effective error recovery to handle imperfect or incomplete FTML documents gracefully:

* **Root-Level Errors**: When an error occurs at the root level, the parser might skip to the next key-value pair, allowing it to parse the remainder of the document.
* **Collection Errors**: Within objects or lists, the parser might skip to the next element or the closing delimiter, attempting to salvage as much data as possible.
* **Informative Error Context**: Providing detailed error messages with context helps developers quickly identify and fix issues in their FTML documents.

###   8.3 Memory Management

* **String Interning**: Sharing string data where possible can reduce memory consumption.
* **Lazy Initialization**: Delaying the creation of comment collections until they are needed can save memory, especially in documents with few comments.
* **Memory-Position Tradeoffs**: For very large documents, consider strategies to balance memory usage with the need to retain accurate positional information for error reporting.

###   8.4 Thread Safety

* **Immutable Objects**: The safest approach is to make parser and serializer objects immutable after construction.
* **Thread Confinement**: If mutability is necessary, ensure that parser and serializer instances are not shared between threads.
* **Synchronization**: In threaded environments, use appropriate synchronization mechanisms (locks, etc.) to protect shared data.

##   9. Extension Points

FTML's parsing and serialization processes can be extended to support custom requirements.

###   9.1 Custom Node Types

Implementations can extend the AST with custom node types to represent domain-specific data or optimizations:

* Special handling for date and time values.
* Application-specific value types (e.g., color codes, file paths).
* Optimized representations for large collections.

###   9.2 Stream Processing

For extremely large FTML documents, stream processing techniques can be employed:

* Incremental tokenization: Tokenizing the input in chunks rather than all at once.
* Partial AST construction: Building portions of the AST as the input is processed.
* Streaming serialization: Generating output text in chunks without needing to hold the entire result in memory.

###   9.3 Visitor Pattern

The visitor pattern can be a useful tool for traversing and manipulating the AST in a structured way:

```python
class FTMLVisitor:
    def visit_document(self, node): pass
    def visit_key_value(self, node): pass
    def visit_scalar(self, node): pass
    def visit_object(self, node): pass
    def visit_list(self, node): pass

class ASTPrinter(FTMLVisitor):
    def visit_scalar(self, node):
        print(f"Primitive: {node.value}")
    #   ...
```

##   10. Testing Strategies

Thorough testing is crucial to ensure the correctness and robustness of FTML parsers and serializers.

###   10.1 Testing Categories

A comprehensive test suite should cover the following categories:

* **Lexer/Tokenizer Tests**: Verify that the tokenizer correctly identifies and categorizes all tokens.
* **Parser Correctness Tests**: Ensure that the parser builds the AST according to the FTML grammar.
* **Comment Attachment Tests**: Validate that comments are attached to the correct AST nodes.
* **Round-Trip Preservation Tests**: Confirm that parsing and then serializing an FTML document produces the original document (including comments and formatting).
* **Error Handling Tests**: Check that the parser correctly identifies and reports various types of errors.
* **Performance Benchmarks**: Measure the parser's and serializer's performance on different types and sizes of FTML documents.

###   10.2 Test Case Design

Effective test cases should include:

* **Simple Cases**: Basic tests for each language feature.
* **Edge Cases**: Tests with empty documents, very large values, or unusual input.
* **Corner Cases**: Tests with complex nesting, various comment placements, and tricky syntax.
* **Real-World Examples**: Tests based on actual FTML documents.
* **Stress Tests**: Tests with extremely large documents to evaluate performance and memory usage.

###   10.3 Property-Based Testing

Property-based testing can be a powerful technique for verifying parser/serializer pairs:

* **Roundtrip Property**: `parse(serialize(parse(doc))) == parse(doc)` (Parsing a serialized and then parsed document should be equivalent to parsing the original).
* **Structure Preservation**: Ensure that the types and structure of data are preserved during round-trip.
* **Comment Preservation**: Verify that comments are attached to the correct nodes and that their content is unchanged during round-trip.

##   11. Conclusion

This document has provided a detailed look into the inner workings of FTML parsing and serialization. By understanding these internals, developers can create efficient, robust, and extensible FTML processing tools. The emphasis on clear structure, comment preservation, and error handling ensures that FTML can be used reliably in a wide range of applications.
```

I've done my best to incorporate your preferences and the suggested improvements. Please review it and let me know if there are any further adjustments you'd like to make.