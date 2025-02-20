from ftml import load


def test_numeric_inference():
    """Test that numeric values are dynamically inferred as floats or ints."""
    schema = """
    account: dict = {
        balance: float,
        transactions: list[int]
    }
    """
    ftml_data = """
    account = {
        balance = 100.50,
        transactions = [10, 20, 30]
    }
    """
    data = load(ftml_data, schema=schema)
    assert data == {"account": {"balance": 100.50, "transactions": [10, 20, 30]}}


def test_boolean_inference():
    """Test that boolean values are correctly inferred and validated."""
    schema = """
    config: dict = {
        active: bool
    }
    """
    ftml_data = """
    config = {
        active = true
    }
    """
    data = load(ftml_data, schema=schema)
    assert data == {"config": {"active": True}}


def test_null_inference():
    """Test that the literal 'null' is correctly interpreted as a null value."""
    schema = """
    user = {
        middle_name: str|null = null
    }
    """
    ftml_data = """
    user = {
        middle_name = null
    }
    """
    data = load(ftml_data, schema=schema)
    assert data == {"user": {"middle_name": None}}


def test_union_type():
    """Test that a union type (str or null) accepts both valid alternatives."""
    schema = """
    user = {
        name: str|null = null
    }
    """
    # Case 1: null value
    ftml_data_null = """
    user = {
        name = null
    }
    """
    data_null = load(ftml_data_null, schema=schema)
    assert data_null == {"user": {"name": None}}

    # Case 2: string value
    ftml_data_str = """
    user = {
        name = "Alice"
    }
    """
    data_str = load(ftml_data_str, schema=schema)
    assert data_str == {"user": {"name": "Alice"}}
