from ftml.schema.schema_ast import ObjectTypeNode
from ftml.schema.schema_parser import SchemaParser
from ftml.schema.schema_validator import SchemaValidator


def test_object_ext_constraint_parsing():
    """Test parsing of ext constraint for objects."""
    parser = SchemaParser()

    # Test explicit ext=true
    schema_str = "user: {name: str, age: int}<ext=true>"
    result = parser.parse(schema_str)

    assert "user" in result
    assert isinstance(result["user"], ObjectTypeNode)
    assert result["user"].ext is True

    # Test explicit ext=false
    schema_str = "user: {name: str, age: int}<ext=false>"
    result = parser.parse(schema_str)

    assert "user" in result
    assert isinstance(result["user"], ObjectTypeNode)
    assert result["user"].ext is False

    # Test default (should be ext=false)
    schema_str = "user: {name: str, age: int}"
    result = parser.parse(schema_str)

    assert "user" in result
    assert isinstance(result["user"], ObjectTypeNode)
    assert result["user"].ext is False


def test_object_ext_constraint_validation():
    """Test validation with ext constraint."""
    parser = SchemaParser()

    # Parse schema with ext=true
    schema_str = "user: {name: str, age: int}<ext=true>"
    schema = parser.parse(schema_str)

    # Create validator with strict=true
    validator = SchemaValidator(schema, strict=True)

    # Test with extra fields (should be valid with ext=true)
    data = {"user": {"name": "John", "age": 30, "email": "john@example.com"}}
    errors = validator.validate(data)
    assert not errors, f"Expected no errors but got: {errors}"

    # Parse schema with ext=false
    schema_str = "user: {name: str, age: int}<ext=false>"
    schema = parser.parse(schema_str)

    # Create validator with strict=true
    validator = SchemaValidator(schema, strict=True)

    # Test with extra fields (should be invalid with ext=false)
    data = {"user": {"name": "John", "age": 30, "email": "john@example.com"}}
    errors = validator.validate(data)
    assert errors, "Expected validation errors for extra fields"
    assert any("contains unknown fields" in error for error in errors)


def test_strict_mode_and_ext_interaction():
    """Test interaction between global strict mode and per-object ext flag."""
    parser = SchemaParser()

    # Parse schema with ext=false
    schema_str = "user: {name: str, age: int}<ext=false>"
    schema = parser.parse(schema_str)

    # Create validator with strict=false (should override ext=false)
    validator = SchemaValidator(schema, strict=False)

    # Test with extra fields (should be valid due to strict=false)
    data = {"user": {"name": "John", "age": 30, "email": "john@example.com"}}
    errors = validator.validate(data)
    assert not errors, f"Expected no errors but got: {errors}"

    # Parse schema with ext=true
    schema_str = "user: {name: str, age: int}<ext=true>"
    schema = parser.parse(schema_str)

    # Create validator with strict=true
    validator = SchemaValidator(schema, strict=True)

    # Test with extra fields (should be valid due to ext=true)
    data = {"user": {"name": "John", "age": 30, "email": "john@example.com"}}
    errors = validator.validate(data)
    assert not errors, f"Expected no errors but got: {errors}"