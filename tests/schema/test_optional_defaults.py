from ftml import load


def test_validate_required_field():
    schema = """
    user = {
        name: str,
        age: int
    }
    """
    ftml_data = """
    user = {
        name = "John",
        age = 30
    }
    """
    data = load(ftml_data, schema=schema)
    assert data == {"user": {"name": "John", "age": 30}}


def test_validate_optional_field():
    schema = """
    user = {
        name: str,
        age?: int
    }
    """
    ftml_data = """
    user = {
        name = "John"
    }
    """
    data = load(ftml_data, schema=schema)
    assert data == {"user": {"name": "John"}}


def test_validate_default_value():
    schema = """
    user = {
        name: str = "default",
        age?: int = 0
    }
    """
    ftml_data = """
    user = {
        name = "John"
    }
    """
    data = load(ftml_data, schema=schema)
    assert data == {"user": {"name": "John", "age": 0}}


def test_optional_field_with_default():
    """Test that optional fields with defaults are correctly handled."""
    schema = """
    user = {
        name?: str = "John Doe"
    }
    """
    ftml_data = """
    user = {}
    """
    data = load(ftml_data, schema=schema)
    assert data == {"user": {"name": "John Doe"}}
