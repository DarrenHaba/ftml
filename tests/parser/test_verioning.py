import pytest
from ftml import load, get_ftml_version
from ftml.exceptions import FTMLVersionError


def test_load_no_version():
    """Test loading a document with no version specification."""
    data = load('key = "value"')
    assert data == {"key": "value"}


def test_load_matching_version():
    """Test loading a document with a matching version."""
    current_version = get_ftml_version()
    data = load(f'ftml_version = "{current_version}"\nkey = "value"')
    assert data == {"ftml_version": current_version, "key": "value"}


# todo mock the current version to later version.
# def test_load_older_version():
#     """Test loading a document with an older version."""
#     data = load('ftml_version = "0.5"\nkey = "value"')
#     assert data == {"ftml_version": "0.5", "key": "value"}


def test_load_newer_version():
    """Test loading a document with a newer version fails."""
    current_version = get_ftml_version()
    # Assuming current is like "1.0a1", make a "1.0a2"
    if 'a' in current_version:
        base, suffix = current_version.split('a')
        newer_version = f"{base}a{int(suffix) + 1}"
    elif 'b' in current_version:
        base, suffix = current_version.split('b')
        newer_version = f"{base}b{int(suffix) + 1}"
    elif 'rc' in current_version:
        base, suffix = current_version.split('rc')
        newer_version = f"{base}rc{int(suffix) + 1}"
    else:
        # It's a release version, make a newer minor
        major, minor = current_version.split('.')
        newer_version = f"{major}.{int(minor) + 1}"

    with pytest.raises(FTMLVersionError) as e:
        load(f'ftml_version = "{newer_version}"\nkey = "value"')

    assert "Document requires FTML version" in str(e.value)
    assert "Please update your parser" in str(e.value)


def test_load_newer_stage():
    """Test loading a document with a newer development stage fails."""
    current_version = get_ftml_version()

    # Create a more advanced stage
    if 'a' in current_version:
        # alpha to beta
        base = current_version.split('a')[0]
        newer_version = f"{base}b1"
    elif 'b' in current_version:
        # beta to release candidate
        base = current_version.split('b')[0]
        newer_version = f"{base}rc1"
    elif 'rc' in current_version:
        # rc to release
        base = current_version.split('rc')[0]
        newer_version = base
    else:
        # It's already a release version, make a newer minor
        major, minor = current_version.split('.')
        newer_version = f"{major}.{int(minor) + 1}"

    with pytest.raises(FTMLVersionError) as e:
        load(f'ftml_version = "{newer_version}"\nkey = "value"')

    assert "Document requires FTML version" in str(e.value)


def test_load_newer_major_version():
    """Test loading a document with a newer major version fails."""
    current_version = get_ftml_version()
    major = current_version.split('.')[0]
    newer_version = f"{int(major) + 1}.0"

    with pytest.raises(FTMLVersionError) as e:
        load(f'ftml_version = "{newer_version}"\nkey = "value"')

    assert "Document requires FTML version" in str(e.value)
    assert "Please update your parser" in str(e.value)


def test_load_invalid_version_format():
    """Test loading a document with an invalid version format."""
    with pytest.raises(FTMLVersionError) as e:
        load('ftml_version = "1.0.0"\nkey = "value"')

    assert "Invalid FTML version format" in str(e.value)


# todo mock the current version to later version.
# def test_load_valid_prerelease_formats():
#     """Test loading documents with valid pre-release version formats."""
#     # These should all be valid older versions and load successfully
#     versions = ["0.5", "0.9a1", "0.9b1", "0.9rc1"]
# 
#     for version in versions:
#         data = load(f'ftml_version = "{version}"\nkey = "value"')
#         assert data["ftml_version"] == version


def test_load_non_string_version():
    """Test loading a document with a non-string version."""
    with pytest.raises(FTMLVersionError) as e:
        load('ftml_version = 1.0\nkey = "value"')

    assert "Invalid FTML version" in str(e.value)
    assert "Version must be a string" in str(e.value)


def test_load_version_check_disabled():
    """Test loading a document with version checking disabled."""
    current_version = get_ftml_version()
    major = current_version.split('.')[0]
    newer_version = f"{int(major) + 1}.0"

    # This would normally fail but should pass with check_version=False
    data = load(
        f'ftml_version = "{newer_version}"\nkey = "value"',
        check_version=False
    )

    assert data == {"ftml_version": newer_version, "key": "value"}


def test_reserved_version_key():
    """Test that the ftml_version key is treated as a reserved key."""
    current_version = get_ftml_version()
    data = load(f'ftml_version = "{current_version}"\nversion = "app-1.2.3"\nkey = "value"')

    # Both keys should be present - one is the reserved version key, one is a regular user key
    assert "ftml_version" in data
    assert data["version"] == "app-1.2.3"
