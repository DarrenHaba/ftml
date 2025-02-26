import pytest

from ftml import load, FTMLValidationError


def test_union_valid_string():
    schema = '{:str|:null description}'
    valid_data = '{description = "A short description"}'
    data = load(valid_data, schema=schema)
    assert data == {"description": "A short description"}


def test_union_valid_null():
    schema = '{:str|:null description}'
    valid_data = '{description = null}'
    data = load(valid_data, schema=schema)
    assert data == {"description": None}


def test_union_invalid_type():
    schema = '{:str|:null description}'
    invalid_data = '{description = 123}'
    with pytest.raises(FTMLValidationError):
        load(invalid_data, schema=schema)
