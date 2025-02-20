from ftml import load


def test_parse_string():
    ftml_data = 'name = "John"'
    data = load(ftml_data)
    print(data)
    assert data == {"name": "John"}


def test_parse_integer():
    ftml_data = 'age = 30'
    data = load(ftml_data)
    assert data == {"age": 30}


def test_parse_float():
    ftml_data = 'price = 9.99'
    data = load(ftml_data)
    assert data == {"price": 9.99}


def test_parse_boolean():
    ftml_data = 'active = true'
    data = load(ftml_data)
    assert data == {"active": True}


def test_parse_null():
    ftml_data = 'middle_name = null'
    data = load(ftml_data)
    assert data == {"middle_name": None}
