tests/
└── schema/
    ├── test_basic_inference.py       # Basic type inference: strings, numbers, booleans, null.
    ├── test_optional_defaults.py     # Optional fields, default values, and nullability.
    ├── test_collections.py           # List and dictionary type annotations and nested collections.
    ├── test_repeated_keys.py         # Multiplicity tests for repeated keys (* and +).
    ├── test_nested_structures.py     # Deeply nested structures and inline schemas.
    └── test_error_handling.py        # Expected failures: type mismatches, missing operators, etc.
