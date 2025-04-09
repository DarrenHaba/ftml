#   FTML: FlexTag Markup Language

>   **Alpha Status**: Under active development - [Report Issues](https://github.com/DarrenHaba/ftml/issues) | [Send Feedback](https://github.com/DarrenHaba/ftml/issues). 
---

##   Data Integrity Meets Simplicity

FTML: Human-readable syntax, bulletproof validation. Built for humans, and preferred by our AI overlords 😉.

**Why developers love it:**

* **Unified data/schema syntax** - Validate data at a glance with familiar patterns.
* **Rich Constraints** - Set clear boundaries in the wild wild west of generative data.
* **Round-Trip Validation** - Continuous data integrity, catch errors at every step.
* **Python-friendly** - Seamless integration with Python dictionaries.
* **Round-Trip Comments** - Your documentation stays intact, even after edits.
* **Flexible Type Safety** - Data where everyone knows what to expect.

---

###   Quick Example: Data + Schema in Harmony

See how FTML keeps data and schemas aligned - **no surprises**:

```ftml
// Schema (What you enforce)
model_name: str
max_tokens: int
```

```ftml
// Data (What you create)
model_name = "GPT-4.5"
max_tokens = 2048
```

**Key Insight**: Data uses `=`, schemas use `:`. Same keys, same structure, built-in rules.

###   Your First Python Interaction

Now, let's see this in action with Python. First, install FTML:

```bash
pip install ftml
```

Here's how you can load and validate the data against the schema:

```python
import ftml

ftml_schema = """
// FTML Schema
model_name: str
max_tokens: int
"""

ftml_data = """
// FTML Data
model_name = "GPT-4.5"
max_tokens = 2048
"""

# Load and validate
data = ftml.load(ftml_data, schema=ftml_schema)

print("Loaded data:", data)  # Output: {'model_name': 'GPT-4.5', 'max_tokens': 2048}
```

This simple example shows how `ftml.load()` parses the FTML data, validates it against the schema, and returns a Python dictionary.

###   Modifying and Saving Data

FTML also makes it easy to modify data and save it back to FTML format, while still ensuring it adheres to the schema and preserves comments:

```python
# Modify the data
data["model_name"] = "GPT-5.0"

# Save back to FTML
modified_ftml = ftml.dump(data, schema=ftml_schema)

print("Modified FTML:")
print(modified_ftml)
```

This demonstrates how FTML maintains data integrity throughout your workflow. If you try to assign the wrong type (e.g., `data["max_tokens"] = "invalid"`), FTML will raise a validation error on dump.

###   Deeper Dive: Schema Features

FTML's schema system goes beyond just types. You can also define constraints and default values:

```ftml
// Schema
max_tokens: int<min=1, max=16000> = 2048
```

Here, we specify that `max_tokens` must be an integer between 1 and 16000, and if it's not provided in the data, it defaults to 2048.

###   Working with Collections: Lists and Objects

FTML supports complex data structures like lists and objects, all while maintaining the same intuitive syntax and validation capabilities.

**Data Collections**

```ftml
// Inline list
tags = ["ai", "config"]

// Multiline list
allowed_models = [
    "GPT-4.5",
    "Claude-3.7",
]

// Inline object
user = {name = "Alice", role = "admin"}

// Multiline object
server = {
    host = "api.example.com",
    port = 443,
}
```

As you can see, FTML's syntax for collections is clean and readable using familiar lists `[]` and objects `{}` brackets.

###   Validating Lists with Schemas

Let's see how schemas are used to validate lists:

**Data and Schema for Lists**

```ftml
// Schema
tags: [str]<min=1>                    // List of strings with at least one item
allowed_models: [str<min=1, max=10>]  // List of strings, string items length constraint

// Data
tags = ["ai", "config"]
allowed_models = [
    "GPT-4.5",
    "Claude-3.7",
]
```

**Key Points:**

* Lists are defined with `[TYPE]` syntax in the schema.
* Constraints can be applied to the list itself (e.g., `[str]<min=1>` ensures at least one item).
* Constraints can also be applied to the list items (e.g., `[str<min=1, max=10>]` limits the length of each string).
* Empty lists are valid by default unless you add constraints.

**Python Example: Validating Lists**

```python
import ftml

ftml_schema = """
tags: [str]<min=1>
allowed_models: [str<min=1, max=10>]
"""

ftml_data = """
tags = ["ai", "config"]
allowed_models = [
    "GPT-4.5",
    "Claude-3.7",
]
"""

data = ftml.load(ftml_data, schema=ftml_schema)
print("Validated List Data:", data)
```

This example demonstrates how FTML validates the list structure and its contents based on the schema.

###   Validating Objects with Schemas

FTML also provides robust schema validation for objects:

**Data and Schema for Objects**

```ftml
// Schema
user: {
    name: str<min=1>,                           // Required name string of at least 1 character
    role: str = "user"                          // Role with default value of "user"
}
server: {
    host: str<regex="^[\\w.-]+\\.[a-z]{2,}$">,  // Host with regex pattern validation
    port: int<min=1, max=65535> = 443,          // Port number with constraints and default
    timeout: int = 30                           // Optional field with default
}

// Data
user = {
    name = "Alice", 
    role = "admin"
}
server = {
    host = "api.example.com",
    port = 443,
                                                // Missing optional field, is set to default 30 
}
```

**Key Points:**

* Objects are defined with `{}` syntax in both data and schema.
* Schema definitions within objects allow for:
    * Required fields (e.g., `name: str<min=1>`).
    * Default values (e.g., `role: str = "user"`).
    * Advanced validation like regular expressions (e.g., `host: str<regex="...">`).
    * Constraints on data types (e.g., `port: int<min=1, max=65535>`).

**Python Example: Validating Objects**

```python
import ftml

ftml_schema = """
user: {
    name: str<min=1>,
    role: str = "user"
}
server: {
    host: str<regex="^[\\w.-]+\\.[a-z]{2,}$">,
    port: int<min=1, max=65535> = 443,
    timeout: int = 30
}
"""

ftml_data = """
user = {
    name = "Alice",
    role = "admin"
}
server = {
    host = "api.example.com",
    port = 443,
}
"""

data = ftml.load(ftml_data, schema=ftml_schema)
print("Validated Object Data:", data)
```

This example showcases the power of FTML's schema system in validating complex object structures with various constraints.

##   Advanced Features

FTML offers several advanced features to help you build robust data applications:

* **Round-trip Comment Preservation** - Comments in your FTML files remain intact even after parsing and serializing
* **Schema Validation** - Validate your data against schemas with rich constraint options
* **Default Values** - Define fallback values for optional fields
* **Union Types** - Create flexible schemas with multiple allowed types using `type1 | type2`
* **Strict Mode** - Choose between strict validation and more permissive options

For more documentation (dive into the rabbit hole 🕳️) see:

* [Document Structure](https://github.com/DarrenHaba/ftml/blob/main/docs/structure.md) - Root structure and document format
* [Unions and Enums](https://github.com/DarrenHaba/ftml/blob/main/docs/unions_enums.md) - Working with unions and enums in FTML
* [Versioning & Encoding](https://github.com/DarrenHaba/ftml/blob/main/docs/versioning_encoding.md) - FTML versions and character encodings
* [Date & Time Types](https://github.com/DarrenHaba/ftml/blob/main/docs/datetime.md) - Working with temporal data
* [Constraints](https://github.com/DarrenHaba/ftml/blob/main/docs/constraints.md) - Validation rules for data
* [Scalar Types](https://github.com/DarrenHaba/ftml/blob/main/docs/scalars.md) - String, number, boolean, and null types
* [Collections](https://github.com/DarrenHaba/ftml/blob/main/docs/collections.md) - Working with objects and lists in FTML
* [Comments](https://github.com/DarrenHaba/ftml/blob/main/docs/comments.md) - Comment syntax and preservation
* [Parsing & Serialization](https://github.com/DarrenHaba/ftml/blob/main/docs/parser.md) - How FTML processing works
* [Schema Parser](https://github.com/DarrenHaba/ftml/blob/main/docs/schema_parser.md) - Internal workings of the schema parser
* [API Reference](https://github.com/DarrenHaba/ftml/blob/main/docs/api.md) - Core functions and classes for loading, modifying, and saving FTML data

Note: Documentation is being actively developed as the project evolves.