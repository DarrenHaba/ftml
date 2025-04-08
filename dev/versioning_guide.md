# FTML Versioning Recommendations

## 1. Specification Versioning

For the FTML specification itself, we use a simple semantic versioning approach:
- **MAJOR.MINOR** (e.g., 1.0, 1.1, 2.0)

For our first release, **FTML 1.0a1** is appropriate as we continue to develop and refine the specification.

## 2. Package Versioning

For the Python package on PyPI, we follow the standard [PEP 440](https://www.python.org/dev/peps/pep-0440/) versioning:

Here's how we will version the package:
- Start with **1.0a1** (meaning version 1.0, alpha 1)
- Progress through alpha releases (1.0a2, 1.0a3) as we make improvements
- Move to beta releases (1.0b1, 1.0b2) when more stable
- Then release candidate (1.0rc1) when nearly production-ready
- Finally, 1.0.0 for the stable release

The package version doesn't need to match the specification version exactly, but they should align conceptually.

## 3. Implementation Approach

Here's how we might implement specification versioning in our parser:

```python
# Add to __init__.py
FTML_VERSION = "1.0a1"
PACKAGE_VERSION = "1.0a1"  # Update this with each release

def get_ftml_version():
    """Return the FTML specification version this parser implements."""
    return FTML_VERSION

def get_package_version():
    """Return the package version."""
    return PACKAGE_VERSION

def validate_version(file_version):
    """
    Validate the FTML specification version.
    
    Strict backwards compatibility:
    - Only allow parsing of files with exactly matching major version
    - Raise an error if file version is different from parser version
    """
    parser_version = get_ftml_version()

    # Split versions into major and minor components
    file_major, file_minor = map(int, file_version.split('.'))
    parser_major, parser_minor = map(int, parser_version.split('.'))

    # Raise error if major versions don't match
    if file_major != parser_major:
        raise ValueError(
            f"Unsupported FTML version. "
            f"Parser supports {parser_version}, "
            f"but file specifies version {file_version}. "
            "Please upgrade your parser."
        )

    # Optional: Add warning for newer minor versions
    if file_minor > parser_minor:
        warnings.warn(
            f"File version {file_version} is newer than parser version {parser_version}. "
            "Some features may not be supported."
        )
```

For document-level versioning, we use a reserved key:

```
// FTML example with version metadata
ftml_version = "1.0a1"
ftml_encoding = "utf-8"

// Actual document content follows
key1 = "value1"
```

Our parser could then:
1. Look for these fields when parsing
2. Validate that the specification version is supported
3. Adapt parsing behavior if needed for multiple versions

## 4. Versioning Details for Implementation

### Reserved Keys
- `ftml_version`: Specifies the FTML specification version
- `ftml_encoding`: Specifies the file encoding
- These keys are specifically reserved for FTML metadata
- Users can still use `version` or `encoding` as regular key-value pairs

### Encoding Support
- Default encoding is UTF-8
- Supports standard Python encodings:
    - `utf-8` (default)
    - `latin-1`
    - `ascii`
    - `utf-16`
- Encoding errors will be raised for mismatched specifications

## 5. Considerations and Pitfalls

Based on lessons from other markup languages:

1. **Backward Compatibility**: Maintain backward compatibility whenever possible. Breaking changes should only come with major version increases.

2. **Version Discovery**: Provide a way for users to discover what version of the specification they're using and what the parser supports.

3. **Forward Compatibility**: Consider how our parser will handle documents that claim to use future versions.

4. **Deprecation Paths**: When features need to be removed, follow a deprecation path:
    - Mark as deprecated in version X
    - Continue support with warnings in version X+1
    - Remove in version X+2

5. **Documentation**: Document version differences clearly, especially when breaking changes occur.

6. **Feature Detection**: Future consideration, add feature detection ("does this parser support X?") might be better than version checking in some cases, or use as a fallback.

## 6. Future Considerations

- Version and encoding specifications may be expanded in future releases
- Backwards compatibility will be a primary design goal
- Future integrations (like FlexTag) will use their own version keys
- Alpha status indicates ongoing development and potential significant changes