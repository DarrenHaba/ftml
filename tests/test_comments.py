from ftml import load, dump


def test_comment():
    ftml_input = '''{
    value = "hello"  # comment here
    }'''
    data = load(ftml_input)
    assert data["value"] == "hello"


def test_comment_in_schema():
    schema = """
:dict{
    :str name # comment here
}
"""
    ftml_input = """
{
    name = "Carol",
}
"""
    data = load(ftml_input, schema=schema)
    assert data["name"] == "Carol"


def test_inline_comment():
    ftml_input = '''{
    value = "hello"  # inline comment
    }'''
    data = load(ftml_input)
    assert data["value"] == "hello"


def test_schema_and_data_comments_preservation():
    ftml_input = r"""
# Comment above dictionary (schema)
:dict{
    # Comment at start of dictionary (schema)
    :str name,    # Inline comment for name (schema)
    # Comment at middle of dictionary (schema)
    :int age         # Inline comment for age (schema)
    # Comment at end of dictionary (schema)
}

{
    # Data section comment (top-level)
    name = "Heidi",   # Inline comment after name
    age = 27          # Inline comment after age
    # Trailing data comment
}
"""
    # Load the FTML content with embedded schema.
    data_obj = load(ftml_input)
    # Dump the data back to FTML.
    print("\nLoaded FTML:")
    print(data_obj)
    output = dump(data_obj, schema=data_obj.embedded_schema)

    print("\nDumped FTML:")
    print(output)

    # Verify that the schema section appears with comments in the proper locations.
    # (These assertions may be adjusted based on your expected formatting.)
    assert ":dict{" in output
    assert "# Comment above dictionary (schema)" in output
    assert ":str name" in output
    assert "# Inline comment for name (in schema)" in output
    assert ":int age" in output
    assert "# Inline comment for age (in schema)" in output

    # Verify that data section comments are preserved.
    assert "name = \"Heidi\"" in output
    assert "# Data section comment (top-level)" in output
    assert "# Inline comment after name" in output
    assert "# Inline comment after age" in output
    assert "# Trailing data comment" in output

