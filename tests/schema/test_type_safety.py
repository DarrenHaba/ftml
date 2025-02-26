import pytest

from ftml import load, FTMLValidationError


def test_correct_types():
    schema = '{:str name, :int age}'
    valid_data = '{name = "Alice", age = 25}'
    data = load(valid_data, schema=schema)
    assert data == {"name": "Alice", "age": 25}


def test_string_instead_of_int():
    schema = '{:str name, :int age}'
    invalid_data = '{name = "Alice", age = "not integer"}'
    with pytest.raises(FTMLValidationError):
        load(invalid_data, schema=schema)


def test_int_instead_of_string():
    schema = '{:str name, :int age}'
    invalid_data = '{name = 123, age = 25}'
    with pytest.raises(FTMLValidationError):
        load(invalid_data, schema=schema)
