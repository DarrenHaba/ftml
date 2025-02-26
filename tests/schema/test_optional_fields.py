import pytest

from ftml import load, F, FTMLValidationError


def test_optional_field_present():
    schema = '{:str name, :int age?}'
    ftml_data = '{name = "joe", age = 55}'
    data = load(ftml_data, schema=schema)
    assert data == {"name": "joe", "age": 55}


def test_optional_field_missing():
    schema = '{:str name, :int age?}'
    ftml_data = '{name = "joe"}'
    data = load(ftml_data, schema=schema)
    assert data == {"name": "joe"}


def test_required_field_missing():
    schema = '{:str name, :int age?}'
    ftml_data = '{}'
    with pytest.raises(FTMLValidationError):
        load(ftml_data, schema=schema)
