from ftml import load


def test_infer_integer():
    ftml_data = 'count = 42'
    data = load(ftml_data)
    assert data == {"count": 42}


def test_infer_float():
    ftml_data = 'price = 9.99'
    data = load(ftml_data)
    assert data == {"price": 9.99}


def test_infer_boolean():
    ftml_data = 'active = true'
    data = load(ftml_data)
    assert data == {"active": True}


def test_infer_null():
    ftml_data = 'middle_name = null'
    data = load(ftml_data)
    assert data == {"middle_name": None}


def test_infer_string():
    ftml_data = 'name = "John"'
    data = load(ftml_data)
    assert data == {"name": "John"}
