from ftml import load


def test_list_of_ints():
    """Test that a list schema enforces that all elements are integers."""
    schema = """
    numbers: list[int] = [ ]
    """
    ftml_data = """
    numbers = [1, 2, 3]
    """
    data = load(ftml_data, schema=schema)
    assert data == {"numbers": [1, 2, 3]}


def test_mixed_dictionary():
    """Test a dictionary schema with explicit types for mixed data."""
    schema = """
    config: dict = {
        host: str,
        port: int
    }
    """
    ftml_data = """
    config = {
        host = "localhost",
        port = 8080
    }
    """
    data = load(ftml_data, schema=schema)
    assert data == {"config": {"host": "localhost", "port": 8080}}
