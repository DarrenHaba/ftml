from ftml import load


def test_top_level_scalar_string():
    ftml_input = '"hello"'
    data = load(ftml_input)
    assert data == "hello"


def test_top_level_scalar_int():
    ftml_input = "42"
    data = load(ftml_input)
    assert data == 42


def test_top_level_scalar_float():
    ftml_input = "42.5"
    data = load(ftml_input)
    assert data == 42.5


def test_top_level_scalar_null():
    ftml_input = "null"
    data = load(ftml_input)
    assert data is None


def test_top_level_scalar_true():
    ftml_input = "true"
    data = load(ftml_input)
    assert data is True


def test_top_level_scalar_false():
    ftml_input = "false"
    data = load(ftml_input)
    assert data is False
