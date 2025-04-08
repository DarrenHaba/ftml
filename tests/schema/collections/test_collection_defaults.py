"""
Test module for FTML collection defaults.

Tests the behavior of default values in FTML collections (objects and lists),
including field-level defaults, object-level defaults, nested defaults,
and default value precedence.
"""

import logging

from ftml.logger import logger
from ftml.schema.schema_ast import ObjectTypeNode, ListTypeNode
from ftml.schema.schema_parser import SchemaParser
from ftml.schema.schema_validator import SchemaValidator, apply_defaults

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class TestSimpleCollectionDefaults:
    """Test simple default values for collections."""

    def test_empty_object_default(self):
        """Test empty object default values."""
        parser = SchemaParser()

        schema = """
        config: {} = {}
        """

        result = parser.parse(schema)

        assert "config" in result
        assert result["config"].has_default
        assert isinstance(result["config"], ObjectTypeNode)
        assert result["config"].default == {}

        # Test default application
        data = {}
        data_with_defaults = apply_defaults(data, result)
        assert "config" in data_with_defaults
        assert data_with_defaults["config"] == {}

    def test_populated_object_default(self):
        """Test populated object default values."""
        parser = SchemaParser()

        schema = """
        settings: {} = {theme = "light", debug = false}
        """

        result = parser.parse(schema)

        assert "settings" in result
        assert result["settings"].has_default
        assert isinstance(result["settings"], ObjectTypeNode)
        assert result["settings"].default == {"theme": "light", "debug": False}

        # Test default application
        data = {}
        data_with_defaults = apply_defaults(data, result)
        assert "settings" in data_with_defaults
        assert data_with_defaults["settings"] == {"theme": "light", "debug": False}

    def test_empty_list_default(self):
        """Test empty list default values."""
        parser = SchemaParser()

        schema = """
        tags: [str] = []
        """

        result = parser.parse(schema)

        assert "tags" in result
        assert result["tags"].has_default
        assert isinstance(result["tags"], ListTypeNode)
        assert result["tags"].default == []

        # Test default application
        data = {}
        data_with_defaults = apply_defaults(data, result)
        assert "tags" in data_with_defaults
        assert data_with_defaults["tags"] == []

    def test_populated_list_default(self):
        """Test populated list default values."""
        parser = SchemaParser()

        schema = """
        roles: [str] = ["user", "guest"]
        """

        result = parser.parse(schema)

        assert "roles" in result
        assert result["roles"].has_default
        assert isinstance(result["roles"], ListTypeNode)
        assert result["roles"].default == ["user", "guest"]

        # Test default application
        data = {}
        data_with_defaults = apply_defaults(data, result)
        assert "roles" in data_with_defaults
        assert data_with_defaults["roles"] == ["user", "guest"]


class TestFieldLevelDefaults:
    """Test field-level default values within collections."""

    def test_object_with_field_level_defaults(self):
        """Test object with field-level defaults."""
        parser = SchemaParser()

        schema = """
        user: {
            name: str = "Anonymous",
            active: bool = true,
            login_count: int = 0
        }
        """

        result = parser.parse(schema)

        assert "user" in result
        assert isinstance(result["user"], ObjectTypeNode)
        assert "name" in result["user"].fields
        assert result["user"].fields["name"].has_default
        assert result["user"].fields["name"].default == "Anonymous"
        assert result["user"].fields["active"].default is True
        assert result["user"].fields["login_count"].default == 0

        # Test default application for missing fields
        data = {"user": {"name": "John"}}
        data_with_defaults = apply_defaults(data, result)
        assert data_with_defaults["user"]["name"] == "John"  # Original value preserved
        assert data_with_defaults["user"]["active"] is True  # Default applied
        assert data_with_defaults["user"]["login_count"] == 0  # Default applied

    def test_nested_object_with_field_defaults(self):
        """Test nested objects with field-level defaults."""
        parser = SchemaParser()

        schema = """
        user: {
            name: str = "Anonymous",
            settings: {
                theme: str = "light",
                notifications: bool = true
            }
        }
        """

        result = parser.parse(schema)

        assert "user" in result
        assert isinstance(result["user"], ObjectTypeNode)
        assert "settings" in result["user"].fields
        assert isinstance(result["user"].fields["settings"], ObjectTypeNode)
        assert result["user"].fields["settings"].fields["theme"].default == "light"
        assert result["user"].fields["settings"].fields["notifications"].default is True

        # Test default application for nested missing fields
        data = {"user": {"name": "John", "settings": {"theme": "dark"}}}
        data_with_defaults = apply_defaults(data, result)
        assert data_with_defaults["user"]["name"] == "John"  # Original value preserved
        assert data_with_defaults["user"]["settings"]["theme"] == "dark"  # Original value preserved
        assert data_with_defaults["user"]["settings"]["notifications"] is True  # Default applied

    def test_validation_of_field_defaults(self):
        """Test that field-level defaults are properly validated."""
        parser = SchemaParser()

        # Schema with valid defaults
        valid_schema = """
        user: {
            age: int<min=0, max=120> = 18,
            score: float<min=0, max=100> = 75.5
        }
        """

        result = parser.parse(valid_schema)
        validator = SchemaValidator(result)

        # Apply defaults and validate
        data = {"user": {}}
        data_with_defaults = apply_defaults(data, result)
        errors = validator.validate(data_with_defaults)

        assert not errors, f"Expected no validation errors but got: {errors}"
        assert data_with_defaults["user"]["age"] == 18
        assert data_with_defaults["user"]["score"] == 75.5


class TestObjectLevelDefaults:
    """Test object-level default values for collections."""

    def test_object_level_defaults(self):
        """Test object-level defaults for entire structures."""
        parser = SchemaParser()

        schema = """
        config: {
            theme: str,
            debug: bool
        } = {
            theme = "light",
            debug = false
        }
        """

        result = parser.parse(schema)

        assert "config" in result
        assert result["config"].has_default
        assert isinstance(result["config"], ObjectTypeNode)
        assert result["config"].default == {"theme": "light", "debug": False}

        # Test default application when object is missing
        data = {}
        data_with_defaults = apply_defaults(data, result)
        assert "config" in data_with_defaults
        assert data_with_defaults["config"] == {"theme": "light", "debug": False}

    def test_nested_object_level_defaults(self):
        """Test nested object-level defaults."""
        parser = SchemaParser()

        schema = """
        user: {
            profile: {
                name: str,
                bio: str
            } = {
                name = "Guest",
                bio = "New user"
            }
        }
        """

        result = parser.parse(schema)

        assert "user" in result
        assert isinstance(result["user"], ObjectTypeNode)
        assert "profile" in result["user"].fields
        assert result["user"].fields["profile"].has_default
        assert result["user"].fields["profile"].default == {"name": "Guest", "bio": "New user"}

        # Test default application when nested object is missing
        data = {"user": {}}
        data_with_defaults = apply_defaults(data, result)
        assert "profile" in data_with_defaults["user"]
        assert data_with_defaults["user"]["profile"] == {"name": "Guest", "bio": "New user"}


class TestCombinedDefaults:
    """Test combinations of field-level and object-level defaults."""

    def test_combined_field_and_object_defaults(self):
        """Test objects with both field-level and object-level defaults."""
        parser = SchemaParser()

        schema = """
        profile: {
            name: str = "Guest",
            settings: {
                theme: str = "light",
                notifications: bool = true
            }
        } = {
            name = "Default User",
            settings = {
                theme = "system",
                notifications = false
            }
        }
        """

        result = parser.parse(schema)

        assert "profile" in result
        assert result["profile"].has_default  # Object-level default
        assert isinstance(result["profile"], ObjectTypeNode)
        assert result["profile"].fields["name"].has_default  # Field-level default

        # Object-level default
        assert result["profile"].default == {
            "name": "Default User",
            "settings": {
                "theme": "system",
                "notifications": False
            }
        }

        # Field-level defaults
        assert result["profile"].fields["name"].default == "Guest"
        assert result["profile"].fields["settings"].fields["theme"].default == "light"

    def test_default_precedence(self):
        """Test precedence between field-level and object-level defaults."""
        parser = SchemaParser()

        schema = """
        profile: {
            name: str = "Guest",
            settings: {
                theme: str = "light",
                notifications: bool = true
            }
        } = {
            name = "Default User",
            settings = {
                theme = "system",
                notifications = false
            }
        }
        """

        result = parser.parse(schema)

        # Test case 1: Empty data - should use object-level default
        data1 = {}
        data1_with_defaults = apply_defaults(data1, result)
        assert data1_with_defaults["profile"]["name"] == "Default User"  # From object default
        assert data1_with_defaults["profile"]["settings"]["theme"] == "system"  # From object default

        # Test case 2: Partial object - should use field-level defaults
        data2 = {"profile": {"name": "John"}}
        data2_with_defaults = apply_defaults(data2, result)
        assert data2_with_defaults["profile"]["name"] == "John"  # Provided value
        assert data2_with_defaults["profile"]["settings"]["theme"] == "light"  # Field default
        assert data2_with_defaults["profile"]["settings"]["notifications"] is True  # Field default

        # Test case 3: Nested partial object - should use nested field defaults
        data3 = {"profile": {"settings": {}}}
        data3_with_defaults = apply_defaults(data3, result)
        assert data3_with_defaults["profile"]["name"] == "Guest"  # Field default
        assert data3_with_defaults["profile"]["settings"]["theme"] == "light"  # Nested field default
        assert data3_with_defaults["profile"]["settings"]["notifications"] is True  # Nested field default


class TestNestedCollectionDefaults:
    """Test default values in nested collections."""

    def test_object_containing_list_defaults(self):
        """Test objects containing lists with defaults."""
        parser = SchemaParser()

        schema = """
        user: {
            name: str = "Anonymous",
            roles: [str] = ["user"]
        }
        """

        result = parser.parse(schema)

        assert "user" in result
        assert isinstance(result["user"], ObjectTypeNode)
        assert "roles" in result["user"].fields
        assert isinstance(result["user"].fields["roles"], ListTypeNode)
        assert result["user"].fields["roles"].has_default
        assert result["user"].fields["roles"].default == ["user"]

        # Test default application
        data = {"user": {"name": "John"}}
        data_with_defaults = apply_defaults(data, result)
        assert data_with_defaults["user"]["name"] == "John"
        assert data_with_defaults["user"]["roles"] == ["user"]

    def test_list_containing_object_defaults(self):
        """Test lists containing objects with defaults."""
        parser = SchemaParser()

        schema = """
        users: [{
            name: str,
            active: bool = true
        }] = [{name = "Admin", active = true}]
        """

        result = parser.parse(schema)

        assert "users" in result
        assert isinstance(result["users"], ListTypeNode)
        assert result["users"].has_default
        assert result["users"].default == [{"name": "Admin", "active": True}]
        assert isinstance(result["users"].item_type, ObjectTypeNode)
        assert "active" in result["users"].item_type.fields
        assert result["users"].item_type.fields["active"].has_default
        assert result["users"].item_type.fields["active"].default is True

        # Test default application for missing list
        data = {}
        data_with_defaults = apply_defaults(data, result)
        assert "users" in data_with_defaults
        assert data_with_defaults["users"] == [{"name": "Admin", "active": True}]

        # Test default application for list with partial objects
        data = {"users": [{"name": "John"}, {"name": "Alice", "active": False}]}
        data_with_defaults = apply_defaults(data, result)
        assert data_with_defaults["users"][0]["active"] is True  # Default applied
        assert data_with_defaults["users"][1]["active"] is False  # Original value preserved

    def test_deeply_nested_defaults(self):
        """Test deeply nested structures with defaults."""
        parser = SchemaParser()

        schema = """
        organization: {
            name: str = "Unnamed Org",
            departments: [{
                name: str,
                manager: {
                    name: str = "Unnamed Manager",
                    id: int = 0
                } = {
                    name = "Default Manager",
                    id = 1
                },
                employees: [{
                    name: str,
                    role: str = "Staff"
                }] = []
            }] = [{
                name = "Default Department",
                manager = {
                    name = "Department Head",
                    id = 999
                },
                employees = []
            }]
        }
        """

        result = parser.parse(schema)

        # Verify schema structure
        assert "organization" in result
        assert isinstance(result["organization"], ObjectTypeNode)
        assert "departments" in result["organization"].fields
        assert isinstance(result["organization"].fields["departments"], ListTypeNode)

        # Test default application - completely empty data
        data = {}
        data_with_defaults = apply_defaults(data, result)

        # Check first level defaults
        assert data_with_defaults["organization"]["name"] == "Unnamed Org"

        # Check second level defaults (list default)
        assert len(data_with_defaults["organization"]["departments"]) == 1
        assert data_with_defaults["organization"]["departments"][0]["name"] == "Default Department"

        # Check third level defaults (nested object default)
        assert data_with_defaults["organization"]["departments"][0]["manager"]["name"] == "Department Head"
        assert data_with_defaults["organization"]["departments"][0]["manager"]["id"] == 999


class TestDefaultValuePrecedence:
    """Test precedence rules for default values."""

    def test_data_over_field_defaults(self):
        """Test that existing data takes precedence over field defaults."""
        parser = SchemaParser()

        schema = """
        user: {
            name: str = "Anonymous",
            active: bool = true
        }
        """

        result = parser.parse(schema)

        # Data with values that should override defaults
        data = {"user": {"name": "John", "active": False}}
        data_with_defaults = apply_defaults(data, result)

        # Check that original values are preserved
        assert data_with_defaults["user"]["name"] == "John"
        assert data_with_defaults["user"]["active"] is False

    def test_field_over_object_defaults(self):
        """Test that field defaults take precedence over object defaults when parent exists."""
        parser = SchemaParser()

        schema = """
        profile: {
            name: str = "Guest",
            active: bool = true
        } = {
            name = "Default",
            active = false
        }
        """

        result = parser.parse(schema)

        # Empty object should use field defaults, not object defaults
        data = {"profile": {}}
        data_with_defaults = apply_defaults(data, result)

        # Check that field defaults are used
        assert data_with_defaults["profile"]["name"] == "Guest"
        assert data_with_defaults["profile"]["active"] is True

        # But missing object should use object defaults
        empty_data = {}
        empty_with_defaults = apply_defaults(empty_data, result)

        # Check that object defaults are used
        assert empty_with_defaults["profile"]["name"] == "Default"
        assert empty_with_defaults["profile"]["active"] is False


class TestCollectionConstraintsWithDefaults:
    """Test that default values adhere to collection constraints."""

    def test_object_pattern_with_default(self):
        """Test object patterns with default values."""
        parser = SchemaParser()

        # Test pattern with default values (replicates your example test)
        schema = """
        counts: {int} = {num1 = 5, num2 = 10}
        empty: {str} = {}
        """

        result = parser.parse(schema)
        print("result:")
        print(result)

        assert "counts" in result
        assert result["counts"].pattern_value_type is not None
        assert result["counts"].pattern_value_type.type_name == "int"
        assert result["counts"].has_default
        assert result["counts"].default == {"num1": 5, "num2": 10}

        assert "empty" in result
        assert result["empty"].pattern_value_type is not None
        assert result["empty"].pattern_value_type.type_name == "str"
        assert result["empty"].has_default
        assert result["empty"].default == {}

        # Test default application
        data = {}
        data_with_defaults = apply_defaults(data, result)
        assert data_with_defaults["counts"] == {"num1": 5, "num2": 10}
        assert data_with_defaults["empty"] == {}

        # Test validation
        validator = SchemaValidator(result)
        errors = validator.validate(data_with_defaults)
        assert not errors, f"Expected no validation errors but got: {errors}"

    def test_type_constraints_with_defaults(self):
        """Test that default values conform to collection type constraints."""
        parser = SchemaParser()

        # Object pattern with default values of the correct type
        schema = """
        scores: {int<min=0, max=100>} = {math = 75, science = 80}
        """

        result = parser.parse(schema)
        validator = SchemaValidator(result)

        # Apply defaults and validate
        data = {}
        data_with_defaults = apply_defaults(data, result)
        errors = validator.validate(data_with_defaults)

        assert not errors, f"Expected no validation errors but got: {errors}"
        assert data_with_defaults["scores"] == {"math": 75, "science": 80}

    def test_size_constraints_with_defaults(self):
        """Test that default values conform to collection size constraints."""
        parser = SchemaParser()

        # List with size constraints and matching default
        schema = """
        top_scores: [int]<min=3, max=5> = [95, 90, 85]
        """

        result = parser.parse(schema)
        validator = SchemaValidator(result)

        # Apply defaults and validate
        data = {}
        data_with_defaults = apply_defaults(data, result)
        errors = validator.validate(data_with_defaults)

        assert not errors, f"Expected no validation errors but got: {errors}"
        assert data_with_defaults["top_scores"] == [95, 90, 85]

    def test_union_types_with_defaults(self):
        """Test default values with union types."""
        parser = SchemaParser()

        # Union type with default matching one of the options
        schema = """
        identifier: int | str = "default-id"
        data: {int} | [str] = ["item1", "item2"]
        """

        result = parser.parse(schema)
        validator = SchemaValidator(result)

        # Apply defaults and validate
        data = {}
        data_with_defaults = apply_defaults(data, result)
        errors = validator.validate(data_with_defaults)

        assert not errors, f"Expected no validation errors but got: {errors}"
        assert data_with_defaults["identifier"] == "default-id"
        assert data_with_defaults["data"] == ["item1", "item2"]