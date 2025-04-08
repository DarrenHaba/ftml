import logging

import pytest
from ftml import load, FTMLValidationError, logger, FTMLParseError

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Basic object tests
def test_empty_object():
    ftml_input = 'obj = {}'
    data = load(ftml_input)
    assert data["obj"] == {}


def test_unnamed_empty_object_should_fail():
    ftml_input = '{}'
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_inline_object():
    ftml_input = 'obj = { key1 = "value1", key2 = "value2" }'
    data = load(ftml_input)
    assert data["obj"] == {"key1": "value1", "key2": "value2"}


def test_multiline_single_object():
    ftml_input = """obj = {
        key1 = "value1"
    }"""
    data = load(ftml_input)
    assert data["obj"] == {"key1": "value1"}


def test_multiline_single_object_with_ending_comma():
    ftml_input = """obj = {
        key1 = "value1",
    }"""
    data = load(ftml_input)
    assert data["obj"] == {"key1": "value1"}


def test_multiline_object():
    ftml_input = """obj = {
        key1 = "value1",
        key2 = "value2",
        key3 = "value3"
    }"""
    data = load(ftml_input)
    assert data["obj"] == {"key1": "value1", "key2": "value2", "key3": "value3"}


def test_multiline_inline_values_object():
    ftml_input = """obj = {
        key1 = "value1", key2 = "value2"
    }"""
    data = load(ftml_input)
    assert data["obj"] == {"key1": "value1", "key2": "value2"}


def test_object_braces_on_separate_lines():
    ftml_input = """obj = 
    {
        key1 = "value1",
        key2 = "value2",
        key3 = "value3"
    }
    """
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_multiline_mixed_formatting():
    ftml_input = """obj = { key1 = "value1",
        key2 = "value2", key3 = "value3",
        key4 = "value4"
    }"""
    data = load(ftml_input)
    assert data["obj"] == {"key1": "value1", "key2": "value2", "key3": "value3", "key4": "value4"}

def test_object_mixed_indentation():
    ftml_input = """obj = {
      key1 = "value1",
        key2 = "value2",
          key3 = "value3"
    }
    """
    data = load(ftml_input)
    assert data["obj"] == {"key1": "value1", "key2": "value2", "key3": "value3"}


def test_inline_object_with_trailing_comma():
    ftml_input = """obj = {
        key1 = "value1",
        key2 = "value2",
        key3 = "value3",
    }"""
    data = load(ftml_input)
    assert data["obj"] == {"key1": "value1", "key2": "value2", "key3": "value3"}


def test_multiline_object_with_trailing_comma():
    ftml_input = """obj = {key1 = "value1", key2 = "value2",}"""
    data = load(ftml_input)
    assert data["obj"] == {"key1": "value1", "key2": "value2"}


def test_object_with_mixed_scalars():
    ftml_input = 'obj = { a = "one", b = 2, c = 3.0, d = true, e = false, f = null }'
    data = load(ftml_input)
    assert data["obj"] == {"a": "one", "b": 2, "c": 3.0, "d": True, "e": False, "f": None}


def test_object_with_quoted_keys():
    ftml_input = 'obj = { "quoted key" = "value", "another-key" = 42 }'
    data = load(ftml_input)
    assert data["obj"] == {"quoted key": "value", "another-key": 42}


def test_object_with_duplicate_keys_should_fail():
    ftml_input = 'obj = { key = "value1", key = "value2" }'
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_multiple_root_objects():
    ftml_input = """
    config = {
        port = 8080,
        host = "localhost"
    }
    metadata = {
        version = "1.0",
        author = "test"
    }
    """
    data = load(ftml_input)
    assert data["config"]["port"] == 8080
    assert data["metadata"]["author"] == "test"


def test_multiple_root_objects_no_comma():
    ftml_input = """
    first = { key = "value" }
    second = { key = "another" }
    """
    data = load(ftml_input)
    assert data["first"]["key"] == "value"
    assert data["second"]["key"] == "another"


def test_object_with_list_values():
    ftml_input = """obj = {
        key1 = [1, 2, 3],
        key2 = ["a", "b", "c"],
        key3 = [true, false, null]
    }"""
    data = load(ftml_input)
    assert data["obj"] == {
        "key1": [1, 2, 3],
        "key2": ["a", "b", "c"],
        "key3": [True, False, None]
    }

    # # Invalid: one value is a string
    # invalid_data = """
    # scores = {
    #     alice = 10
    #     bob = "twenty"
    #     carol = 30
    # }
    # """
    # with pytest.raises(FTMLValidationError):
    #     load(invalid_data, schema=schema)
    # 
    # # Invalid: one value is null
    # invalid_data_null = """
    # scores = {
    #     alice = 10
    #     bob = null
    #     carol = 30
    # }
    # """
    # with pytest.raises(FTMLValidationError):
    #     load(invalid_data_null, schema=schema)
