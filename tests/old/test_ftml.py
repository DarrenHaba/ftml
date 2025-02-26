import unittest
from ftml import load, dump, validate, FTMLParseError, FTMLValidationError
from ftml.logger import setup_logging
import logging


class TestFTMLBasics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up logging for tests
        setup_logging(level=logging.DEBUG)

    def test_load_data_only(self):
        """Test loading data without schema"""
        ftml_input = """
{
    name = "John",
    age = 30
}
"""
        result = load(ftml_input)
        self.assertEqual(result["name"], "John")
        self.assertEqual(result["age"], 30)

    def test_load_with_schema(self):
        """Test loading data with embedded schema"""
        ftml_input = """
:dict{
    :str name,
    :int age
}

{
    name = "John",
    age = 30
}
"""
        result = load(ftml_input)
        self.assertEqual(result["name"], "John")
        self.assertEqual(result["age"], 30)
        self.assertIsNotNone(result.embedded_schema)

    def test_validation_success(self):
        """Test validation with valid data"""
        schema_str = """
:dict{
    :str name,
    :int age
}
"""
        data = {
            "name": "John",
            "age": 30
        }

        # This should not raise any exceptions
        result = load(dump(data), schema=schema_str)
        self.assertEqual(result["name"], "John")
        self.assertEqual(result["age"], 30)

    def test_validation_failure(self):
        """Test validation with invalid data"""
        schema_str = """
:dict{
    :str name,
    :int age
}
"""
        data = {
            "name": 123,  # Should be a string
            "age": "30"  # Should be an integer
        }

        # This should raise a ValidationError
        with self.assertRaises(FTMLValidationError):
            load(dump(data), schema=schema_str)

    def test_optional_fields(self):
        """Test optional fields in schema"""
        schema_str = """
:dict{
    :str name,
    :int? age
}
"""
        # Data without optional field
        data1 = {
            "name": "John"
        }

        # Data with optional field
        data2 = {
            "name": "John",
            "age": 30
        }

        # Both should validate
        result1 = load(dump(data1), schema=schema_str)
        result2 = load(dump(data2), schema=schema_str)

        self.assertEqual(result1["name"], "John")
        self.assertNotIn("age", result1)

        self.assertEqual(result2["name"], "John")
        self.assertEqual(result2["age"], 30)

    def test_default_values(self):
        """Test default values in schema"""
        schema_str = """
:dict{
    :str name,
    :int age = 25
}
"""
        # Data without field that has default
        data = {
            "name": "John"
        }

        # Load with validation
        result = load(dump(data), schema=schema_str)

        # The 'age' field should have the default value
        self.assertEqual(result["name"], "John")
        self.assertEqual(result["age"], 25)

    def test_union_types(self):
        """Test union types in schema"""
        schema_str = """
:dict{
    :str|:null name,
    :int|:float age
}
"""
        # Test various valid combinations
        valid_data = [
            {"name": "John", "age": 30},
            {"name": None, "age": 30},
            {"name": "John", "age": 30.5},
            {"name": None, "age": 30.5}
        ]

        for data in valid_data:
            # This should not raise any exceptions
            result = load(dump(data), schema=schema_str)
            for key, value in data.items():
                self.assertEqual(result[key], value)

        # Test invalid data
        invalid_data = {
            "name": 123,  # Neither string nor null
            "age": "30"  # Neither int nor float
        }

        # This should raise a ValidationError
        with self.assertRaises(FTMLValidationError):
            load(dump(invalid_data), schema=schema_str)

    def test_nested_structures(self):
        """Test nested structures in schema"""
        schema_str = """
:dict{
    :str name,
    :dict{
        :str street,
        :str city,
        :str? state
    } address,
    :list[:str] tags
}
"""
        data = {
            "name": "John",
            "address": {
                "street": "123 Main St",
                "city": "Anytown"
            },
            "tags": ["developer", "python"]
        }

        # This should not raise any exceptions
        result = load(dump(data), schema=schema_str)

        self.assertEqual(result["name"], "John")
        self.assertEqual(result["address"]["street"], "123 Main St")
        self.assertEqual(result["address"]["city"], "Anytown")
        self.assertNotIn("state", result["address"])
        self.assertEqual(result["tags"], ["developer", "python"])

    def test_round_trip(self):
        """Test round-trip serialization and parsing"""
        schema_str = """
:dict{
    :str name,
    :int age,
    :list[:str] tags
}
"""
        data = {
            "name": "John",
            "age": 30,
            "tags": ["developer", "python"]
        }

        # Serialize with schema
        ftml_str = dump(data, schema=schema_str)

        # Parse back
        result = load(ftml_str)

        # Check data
        self.assertEqual(result["name"], "John")
        self.assertEqual(result["age"], 30)
        self.assertEqual(result["tags"], ["developer", "python"])

        # Check schema
        self.assertIsNotNone(result.embedded_schema)
        self.assertEqual(result.embedded_schema["type"], "dict")


if __name__ == '__main__':
    unittest.main()
