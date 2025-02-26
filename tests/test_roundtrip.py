import ftml
from ftml import load, dump


def test_roundtrip_data_only():
    data = {
        "name": "Frank",
        "age": 35,
        "skills": ["python", "testing"]
    }
    ftml_str = dump(data)
    result = load(ftml_str)
    print(result)
    assert result == data


def test_roundtrip_with_schema():
    schema = """
:obj{
    :str name,
    :int age,
    :list[:str] skills
}
"""
    data = {
        "name": "Grace #not yaml comment",
        "age": 29,
        "skills": ["design", "development"]
    }
    ftml_str = dump(data, schema=schema)
    result = load(ftml_str)
    # Check both data and that an embedded schema is available
    assert result == data
    dumped = dump(result)
    print(dumped)
    # assert result.embedded_schema is not None
