from ftml import load, dump


def test_parse_simple_dict():
    ftml_data = """
    name = "John",
    age = 30
    """
    data = load(ftml_data)
    assert data == {"name": "John", "age": 30}


def test_parse_simple_list():
    ftml_data = """
    "apple",
    "banana",
    "cherry"
    """
    data = load(ftml_data)
    assert data == ["apple", "banana", "cherry"]


def test_parse_nested_dict():
    ftml_data = """
    user = {
        name = "John",
        age = 30
    }
    """
    data = load(ftml_data)
    assert data == {"user": {"name": "John", "age": 30}}


def test_parse_nested_list():
    ftml_data = """
    fruits = [
        "apple",
        "banana",
        "cherry"
    ]
    """
    data = load(ftml_data)
    assert data == {"fruits": ["apple", "banana", "cherry"]}


def test_dump_simple_dict():
    data = {"name": "John", "age": 30}
    ftml_output = dump(data)
    assert ftml_output.strip() == 'name = "John",\nage = 30'


def test_dump_simple_list():
    data = ["apple", "banana", "cherry"]
    ftml_output = dump(data)
    assert ftml_output.strip() == '"apple",\n"banana",\n"cherry"'
