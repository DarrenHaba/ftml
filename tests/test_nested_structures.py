from ftml import load


def test_parse_nested_dict():
    ftml_data = """
    user = {
        name = "John",
        age = 30,
        address = {
            city = "New York",
            zip = "10001"
        }
    }
    """
    data = load(ftml_data)
    assert data == {
        "user": {
            "name": "John",
            "age": 30,
            "address": {
                "city": "New York",
                "zip": "10001"
            }
        }
    }


def test_parse_nested_list():
    ftml_data = """
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    """
    data = load(ftml_data)
    assert data == {
        "matrix": [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
    }
