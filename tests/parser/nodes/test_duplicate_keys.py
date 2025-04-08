import pytest
from ftml import load, FTMLParseError


def test_duplicate_root_keys_raises_error():
    """Test that duplicate keys at the root level raise an error."""
    with pytest.raises(FTMLParseError) as excinfo:
        load('''
            user = "Alice"
            user = "Bob"  // Duplicate key
        ''')

    assert "Duplicate root key 'user'" in str(excinfo.value)


def test_duplicate_nested_keys_raises_error():
    """Test that duplicate keys in an object raise an error."""
    with pytest.raises(FTMLParseError) as excinfo:
        load('''
            config = {
                theme = "dark",
                theme = "light"  // Duplicate key
            }
        ''')

    assert "Duplicate key 'theme'" in str(excinfo.value)


def test_duplicate_keys_in_inline_object():
    """Test that duplicate keys in an inline object raise an error."""
    with pytest.raises(FTMLParseError) as excinfo:
        load('settings = { color = "blue", color = "red" }')

    assert "Duplicate key 'color'" in str(excinfo.value)


def test_duplicate_keys_in_nested_objects():
    """Test that duplicate keys in deeply nested objects raise an error."""
    with pytest.raises(FTMLParseError) as excinfo:
        load('''
            user = {
                name = "Alice",
                profile = {
                    email = "alice@example.com",
                    email = "alice.new@example.com"  // Duplicate key
                }
            }
        ''')

    assert "Duplicate key 'email'" in str(excinfo.value)


def test_valid_multiple_root_keys():
    """Test valid document with multiple unique root keys."""
    data = load('''
        name = "Project X"
        version = 1.0
        tags = ["alpha", "test"]
    ''')

    assert data == {
        "name": "Project X",
        "version": 1.0,
        "tags": ["alpha", "test"]
    }


def test_valid_multiple_nested_keys():
    """Test valid document with multiple unique nested keys."""
    data = load('''
        user = {
            name = "Alice",
            age = 30,
            contact = {
                email = "alice@example.com",
                phone = "555-1234"
            }
        }
    ''')

    assert data == {
        "user": {
            "name": "Alice",
            "age": 30,
            "contact": {
                "email": "alice@example.com",
                "phone": "555-1234"
            }
        }
    }


def test_case_sensitive_keys():
    """Test that keys are case-sensitive and different cases are treated as different keys."""
    data = load('''
        name = "lowercase"
        Name = "Capitalized"
        NAME = "UPPERCASE"
    ''')

    assert data == {
        "name": "lowercase",
        "Name": "Capitalized",
        "NAME": "UPPERCASE"
    }


def test_similar_but_different_keys():
    """Test that similar but different keys are treated as unique."""
    data = load('''
        user_id = 123
        user_ID = 456
        userId = 789
    ''')

    assert data == {
        "user_id": 123,
        "user_ID": 456,
        "userId": 789
    }


def test_complex_structure_with_unique_keys():
    """Test that complex structures with all unique keys are valid."""
    data = load('''
        config = {
            server = {
                host = "localhost",
                port = 8080
            },
            database = {
                host = "db.example.com",
                port = 5432,
                credentials = {
                    username = "admin",
                    password = "secret"
                }
            }
        }
    ''')

    assert data == {
        "config": {
            "server": {
                "host": "localhost",
                "port": 8080
            },
            "database": {
                "host": "db.example.com",
                "port": 5432,
                "credentials": {
                    "username": "admin",
                    "password": "secret"
                }
            }
        }
    }
