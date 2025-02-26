from ftml import load


def test_default_value_assigned():
    schema = '{:str name = "N/A", :int age? = 30}'
    data = load('{name = "john"}', schema=schema)
    assert data == {"name": "N/A", "age": 30}


def test_default_value_overridden():
    schema = '{:str name = "N/A", :int age = 30}'
    data = load('{name = "John", age = 40}', schema=schema)
    assert data == {"name": "John", "age": 40}


def test_default_value_for_missing_name():
    schema = '{:str name = "N/A", :int age = 30}'
    data = load('{age = 35}', schema=schema)
    assert data == {"name": "N/A", "age": 35}


def test_default_value_for_missing_age():
    schema = '{:str name = "N/A", :int age = 30}'
    data = load('{name = "Emily"}', schema=schema)
    assert data == {"name": "Emily", "age": 30}
