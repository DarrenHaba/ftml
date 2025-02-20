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
    with pytest.raises(ValidationError):
        load(ftml_data, schema=schema)


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

# Update the tests to expect errors
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