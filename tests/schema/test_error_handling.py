import pytest

from ftml import load
from ftml.exceptions import ValidationError, FTMLParseError


def test_invalid_type():
    """Test that a type mismatch (string instead of int) raises a ValidationError."""
    schema = """
    user = {
        name: str,
        age: int
    }
    """
    ftml_data = """
    user = {
        name = "John",
        age = "30"  # invalid type: should be int
    }
    """
    with pytest.raises(ValidationError) as exc_info:
        load(ftml_data, schema=schema)
    error_message = str(exc_info.value)
    # Check that the error message includes field name, expected type, actual type, and the offending value.
    assert "age" in error_message
    assert "Expected int" in error_message
    assert "str" in error_message
    assert "30" in error_message


def test_missing_assignment_operator():
    """Test that missing the assignment operator '=' triggers an error."""
    schema = """
    user = {
        name: str,
        age: int
    }
    """
    ftml_data = """
    user = {
        name = "John",
        age 30  # Missing '=' operator for age
    }
    """
    with pytest.raises(Exception):
        load(ftml_data, schema=schema)


def test_repeated_keys_error():
    """Test that repeated keys raise a parse error."""
    schema = """
    users = {
        name: str,
        age: int
    }
    """
    ftml_data = """
    users = {name = "John", age = 30},
    users = {name = "Jane", age = 25}
    """
    with pytest.raises(FTMLParseError):
        load(ftml_data, schema=schema)


def test_repeated_keys_inline_error():
    """Test that repeated keys in the same dict raise an error."""
    ftml_data = """
    user = {
        name = "John",
        name = "Jane"
    }
    """
    with pytest.raises(FTMLParseError):
        load(ftml_data)


def test_missing_field_error_message_detail():
    """Test that the error message for a missing field includes the field name."""
    schema = """
    user = {
        name: str,
        age: int
    }
    """
    ftml_data = """
    user = {
        name = "John"
    }
    """
    with pytest.raises(ValidationError) as exc_info:
        load(ftml_data, schema=schema)
    error_message = str(exc_info.value)
    assert "Missing required field" in error_message
    assert "age" in error_message


def test_expected_dict_error_message_detail():
    """Test that the error message for a field expecting a dict is descriptive."""
    schema = """
    user = {
        profile: dict
    }
    """
    ftml_data = """
    user = {
        profile = "not a dict"
    }
    """
    with pytest.raises(ValidationError) as exc_info:
        load(ftml_data, schema=schema)
    error_message = str(exc_info.value)
    print(5555)
    print(error_message)
    print(555)
    assert "Expected dict for field 'profile'" in error_message
