# FTML Versioning & Encoding Specification

## 1. Overview

FTML (FlexTag Markup Language) includes robust versioning and encoding support to ensure compatibility between documents and parsers, and to handle different character encodings properly. This specification details the versioning system that enables backward compatibility and proper encoding handling within the FTML ecosystem.

## 2. Versioning

FTML employs a straightforward versioning system to ensure that documents can be properly processed by compatible parsers.

### 2.1 Version Format

FTML uses a MAJOR.MINOR format for version numbers:

| Format | Example | Description |
|--------|---------|-------------|
| MAJOR.MINOR | 1.0 | Standard release version |
| MAJOR.MINOR(a\|b\|rc)NUMBER | 1.0a1, 1.1b2, 1.2rc1 | Pre-release versions |

- **MAJOR**: Incremented for backward-incompatible changes
- **MINOR**: Incremented for backward-compatible feature additions
- **Pre-release identifiers**: Optional alpha (a), beta (b), or release candidate (rc) markers, followed by a number

### 2.2 Compatibility Rules

FTML follows these compatibility rules:

- **Backward Compatibility**: Documents created with older versions of FTML will always work with newer parsers
- **No Forward Compatibility**: Documents created with newer versions will not work with older parsers
- **Version Checking**: By default, parsers validate that document versions are compatible
- **Version Precedence**: a < b < rc < release (e.g., 1.0a1 < 1.0b1 < 1.0rc1 < 1.0)

### 2.3 Version Specification

FTML documents can specify their version using a reserved key:

```ftml
// It is best practice to place a schema version at the top. 
ftml_version = "1.0"


name = "Alice"
age = 39
```

When a document does not specify a version, it is assumed to be compatible with the parser.

### 2.4 Error Handling

The versioning system provides clear error messages when incompatible versions are detected:

| Error Condition | Error Message |
|-----------------|---------------|
| Invalid version format | "Invalid FTML version format: X. Expected format is 'MAJOR.MINOR' or 'MAJOR.MINOR(a\|b\|rc)NUMBER'." |
| Incompatible version | "Document requires FTML version X, but parser only supports up to Y. Please update your parser." |
| Non-string version | "Invalid FTML version: X. Version must be a string." |

### 2.5 API Functions

The FTML library exposes these versioning-related functions:

| Function | Description |
|----------|-------------|
| `validate_version(data, parser_version)` | Checks if a document's version is compatible with the parser |
| `get_document_metadata(data)` | Extracts version and encoding metadata from a document |
| `get_ftml_version()` | Returns the current FTML specification version |
| `get_package_version()` | Returns the library package version |

## 3. Encoding

FTML supports multiple character encodings to accommodate various use cases and international text.

### 3.1 Supported Encodings

| Encoding Name | Aliases | Description |
|---------------|---------|-------------|
| utf-8 | utf8 | Unicode Transformation Format, 8-bit (default) |
| latin-1 | latin1, iso-8859-1 | Western European encoding |
| ascii | | ASCII-only encoding |
| utf-16 | utf16, utf-16-le, utf-16-be | Unicode Transformation Format, 16-bit |

### 3.2 Encoding Specification

FTML documents can specify their encoding using a reserved key:

```ftml
// This encoding declaration must be at the top of the file to be effective
ftml_encoding = "latin-1"

// Latin-1 encoding handles European characters efficiently
document_type = "Résumé"
candidate  = "Björn Müller"
```

When a document does not specify an encoding, UTF-8 is used as the default.

### 3.3 Encoding Detection

FTML implementations detect the encoding in the following manner:

1. Initially read the file with UTF-8 encoding (default)
2. Look for the `ftml_encoding` key in the content
3. If a different encoding is specified, re-read the file with the specified encoding
4. If no encoding is specified, continue with UTF-8

### 3.4 Error Handling

The encoding system provides clear error messages:

| Error Condition | Error Message |
|-----------------|---------------|
| Invalid encoding value | "Invalid encoding: X. Encoding must be a string." |
| Unsupported encoding | "Unsupported encoding: X. Supported encodings are: [list of supported encodings]" |
| Decoding error | "Error decoding file with specified encoding 'X': [detailed error]" |

## 4. Implementation Details

### 4.1 Version Validation Process

The version validation follows this procedure:

1. Extract the document version from the `ftml_version` key
2. If no version is present, assume compatibility
3. Parse both document and parser versions into components (MAJOR, MINOR, stage, stage_version)
4. Apply compatibility rules:
   - If document major < parser major: compatible
   - If document major > parser major: incompatible
   - If same major, document minor < parser minor: compatible
   - If same major, document minor > parser minor: incompatible
   - If same major and minor, compare pre-release status

### 4.2 Encoding Validation Process

The encoding validation follows this procedure:

1. Extract the document encoding from the `ftml_encoding` key
2. Normalize the encoding name (lowercase, replace underscores with hyphens)
3. Check if the encoding is in the supported list
4. Verify that Python's codec system recognizes the encoding

### 4.3 Reading Files with Correct Encoding

FTML implements a two-step process for reading files with the correct encoding:

1. Initial read:
   ```python
   with open(file_path, 'r', encoding=default_encoding) as f:
       content = f.read()
   ```

2. Check for encoding specification:
   ```python
   encoding_match = re.search(r'ftml_encoding\s*=\s*["\']([^"\']+)["\']', content)
   ```

3. Re-read if necessary:
   ```python
   if specified_encoding != default_encoding:
       with open(file_path, 'r', encoding=specified_encoding) as f:
           content = f.read()
   ```

## 5. Usage Examples

### 5.1 Versioning Examples

#### 5.1.1 Basic Version Specification

```ftml
ftml_version = "1.0"

document_type = "Resume"
candidate = "Brian Miller"
```

#### 5.1.2 Loading With Version Checking

```python
import ftml

# Get FTML version
version = ftml.get_ftml_version()  # Returns "1.0"

# Get package version
package_version = ftml.get_package_version()  # Returns "1.0a1"

# Load with version checking (default behavior)
data = ftml.load('ftml_version = "1.0"\nname = "Alice"')

# Load without version checking
data = ftml.load('ftml_version = "2.0"\nname = "Alice"', check_version=False)
```

### 5.2 Encoding Examples

#### 5.2.1 Default Encoding (UTF-8)

```ftml
title = "Regular UTF-8 document"
description = "Contains Unicode characters: äöüß€¥"
```

#### 5.2.2 Specified Encoding

```ftml
ftml_encoding = "latin-1"
title = "Latin-1 document"
description = "Contains Latin-1 characters: äöüß"
```

#### 5.2.3 Working with Encodings in Code

```python
import ftml

# Load with default encoding (UTF-8)
data = ftml.load('name = "Alice"')

# Load with specified encoding
data = ftml.load('ftml_encoding = "latin-1"\nname = "Alice"')

# Load from a file with encoding detection
data = ftml.load('my_file.ftml')  # Will detect ftml_encoding if present

# Dump with encoding
data = {
    "ftml_encoding": "utf-8",
    "key": "value with special chars: ñáéíóú"
}
ftml.dump(data, 'output.ftml')
```

## 6. Best Practices

### 6.1 Versioning Best Practices

- Always specify the FTML version in documents intended for distribution
- Place the `ftml_version` key at the top of the document for visibility
- Use the minimum version that satisfies your requirements
- Set the version when dumping FTML:
  ```python
  ftml.dump(data, file_path, version="1.0")
  ```

### 6.2 Encoding Best Practices

- Use UTF-8 encoding by default for new documents
- Only specify an alternative encoding when necessary
- Place the `ftml_encoding` key at the top of the document, before any content
- For files with non-ASCII characters, always specify the encoding explicitly
- When creating international applications, always use the encoding detection mechanism
- Set the encoding when dumping FTML:
  ```python
  ftml.dump(data, file_path, encoding="utf-8")
  ```

## 7. Edge Cases and Special Handling

### 7.1 Version Edge Cases

- **Pre-release Versions**:
   - Pre-release versions (alpha, beta, release candidate) are ordered as: a < b < rc < release
   - A document specifying version "1.0rc1" is compatible with a parser version "1.0" but not with "1.0b2"

- **Missing Version**:
   - Documents without version specification are assumed compatible with any parser
   - This ensures backward compatibility with legacy documents

- **Version Override**:
   - Version checking can be disabled in the API:
  ```python
  data = ftml.load(content, check_version=False)
  ```
   - This allows working with newer documents using older parsers at your own risk

### 7.2 Encoding Edge Cases

- **BOM Handling**:
   - UTF-8 BOM is handled automatically by Python's text processing
   - UTF-16 files with BOM are correctly detected when using utf-16 encoding

- **Fallback Strategy**:
   - If encoding detection fails, the implementation falls back to UTF-8
   - A clear error message is provided if the content cannot be decoded with the specified encoding

- **Normalized Encoding Names**:
   - Encoding names are normalized by converting to lowercase and replacing underscores with hyphens
   - This allows for flexibility in encoding specification: `"UTF-8"`, `"utf_8"`, and `"utf8"` are all recognized

### 7.3 Combined Version and Encoding

When both version and encoding are specified, they work independently:

```ftml
ftml_encoding = "utf-8"
ftml_version = "1.0"
title = "Document with both specifications"
```

The encoding is detected and applied first, then the version compatibility is checked. This ensures that the document can be properly read before attempting version validation.