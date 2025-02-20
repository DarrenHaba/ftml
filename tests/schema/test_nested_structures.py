from ftml import load


def test_nested_structures():
    """Test a nested structure (a dictionary containing a list of dictionaries)."""
    schema = """
    company: dict = {
        name: str,
        employees: list[dict] = [
            { name: str, id: int }
        ]
    }
    """
    ftml_data = """
    company = {
        name = "Acme Corp",
        employees = [
            { name = "Alice", id = 1 },
            { name = "Bob", id = 2 }
        ]
    }
    """
    data = load(ftml_data, schema=schema)
    assert data == {
        "company": {
            "name": "Acme Corp",
            "employees": [{"name": "Alice", "id": 1}, {"name": "Bob", "id": 2}]
        }
    }


def test_inline_comments():
    """Test that inline comments (following a '#') are properly ignored."""
    schema = """
    user = {
        name: str,
        age: int
    }
    """
    ftml_data = """
    user = { # user data
        name = "John", # name field
        age = 30 # age field
    }
    """
    data = load(ftml_data, schema=schema)
    assert data == {"user": {"name": "John", "age": 30}}

