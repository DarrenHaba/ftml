import logging
import os
import tempfile
import unittest
import ftml
from ftml import logger
from ftml.exceptions import FTMLValidationError
from tests.parser.comments.utils.helpers import log_ast

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class TestFTMLApi(unittest.TestCase):
    """Test cases for the FTML public API functions."""

    def test_load_from_string(self):
        """Test loading FTML from a string."""
        ftml_content = """
        // Sample config
        name = "My App"
        version = "1.0"
        """

        data = ftml.load(ftml_content)

        self.assertEqual(data["name"], "My App")
        self.assertEqual(data["version"], "1.0")
        self.assertTrue(hasattr(data, "_ast_node"), "Comments should be preserved by default")

    def test_load_without_comments(self):
        """Test loading FTML without preserving comments."""
        ftml_content = """
        // Sample config
        name = "My App"
        version = "1.0"
        """

        data = ftml.load(ftml_content, preserve_comments=False)

        self.assertEqual(data["name"], "My App")
        self.assertEqual(data["version"], "1.0")
        self.assertFalse(hasattr(data, "_ast_node"), "Comments should not be preserved")

    def test_load_from_file(self):
        """Test loading FTML from a file."""
        ftml_content = """
        // Sample config
        name = "My App"
        version = "1.0"
        """

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ftml', delete=False) as f:
            f.write(ftml_content)
            file_path = f.name

        try:
            data = ftml.load(file_path)

            self.assertEqual(data["name"], "My App")
            self.assertEqual(data["version"], "1.0")
            self.assertTrue(hasattr(data, "_ast_node"), "Comments should be preserved by default")
        finally:
            # Clean up
            os.unlink(file_path)

    def test_load_with_schema_validation(self):
        """Test loading FTML with schema validation."""
        schema_content = """
        name: str<min_length=1>
        version: str
        required_field: str  // This field is required but missing
        """

        ftml_content = """
        name = "My App"
        version = "1.0"
        """

        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ftml', delete=False) as f:
            f.write(ftml_content)
            data_path = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.schema.ftml', delete=False) as f:
            f.write(schema_content)
            schema_path = f.name

        try:
            # Test validation failure
            with self.assertRaises(FTMLValidationError):
                ftml.load(data_path, schema=schema_path)

            # Test validation disabled
            data = ftml.load(data_path, schema=schema_path, validate=False)
            self.assertEqual(data["name"], "My App")
            self.assertEqual(data["version"], "1.0")
        finally:
            # Clean up
            os.unlink(data_path)
            os.unlink(schema_path)

    def test_dump_to_string(self):
        """Test dumping FTML to a string."""
        data = {
            "name": "My App",
            "version": "1.0",
            "settings": {
                "port": 8080,
                "debug": True
            }
        }

        ftml_string = ftml.dump(data)

        self.assertIn('name = "My App"', ftml_string)
        self.assertIn('version = "1.0"', ftml_string)
        self.assertIn('port = 8080', ftml_string)
        self.assertIn('debug = true', ftml_string)

    def test_dump_to_file(self):
        """Test dumping FTML to a file."""
        data = {
            "name": "My App",
            "version": "1.0"
        }

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.ftml', delete=False) as f:
            file_path = f.name

        try:
            ftml.dump(data, file_path)

            # Read the file and check contents
            with open(file_path, 'r') as f:
                content = f.read()
                self.assertIn('name = "My App"', content)
                self.assertIn('version = "1.0"', content)
        finally:
            # Clean up
            os.unlink(file_path)

    def test_dump_with_schema_validation(self):
        """Test dumping FTML with schema validation."""
        schema_content = """
        name: str
        version: str
        """

        data = {
            "name": "My App",
            "version": 1.0
        }

        # Create a temporary schema file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.schema.ftml', delete=False) as f:
            f.write(schema_content)
            schema_path = f.name

        try:
            # Test validation failure
            with self.assertRaises(FTMLValidationError):
                ftml.dump(data, schema=schema_path)

            # Test validation disabled
            ftml_string = ftml.dump(data, schema=schema_path, validate=False)
            self.assertIn('name = "My App"', ftml_string)
            self.assertIn('version = 1.0', ftml_string)
        finally:
            # Clean up
            os.unlink(schema_path)

    def test_round_trip_parsing(self):
        """Test round-trip parsing with comments preserved."""
        ftml_content = """
// Sample config
name = "My App"  // App name
version = "1.0"  // Current version

// Settings section
settings = {
    // Network settings
    port = 8080  // Default port
}
        """

        # Load the data
        data = ftml.load(ftml_content)

        # Modify some values
        data["name"] = "Updated App"
        data["settings"]["port"] = 9000

        # Dump back to string
        result = ftml.dump(data)

        # Verify both data and comments are preserved
        self.assertIn('// Sample config', result)
        self.assertIn('name = "Updated App"', result)
        self.assertIn('// App name', result)
        self.assertIn('version = "1.0"', result)
        self.assertIn('// Current version', result)
        self.assertIn('// Settings section', result)
        self.assertIn('// Network settings', result)
        self.assertIn('port = 9000', result)
        self.assertIn('// Default port', result)

    def test_round_trip_with_file(self):
        """Test round-trip parsing with a file."""
        ftml_content = """
// Sample date/time data
meeting_date = "2025-03-25"  // Today's date
meeting_time = "14:30:00"    // Meeting time
created_at = "2025-03-25T14:30:00Z"  // ISO timestamp
unix_time = 1711373760  // Unix timestamp
"""

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ftml', delete=False) as f:
            f.write(ftml_content)
            file_path = f.name

        try:
            # Load the data
            data = ftml.load(file_path)

            # Verify values were loaded correctly
            self.assertEqual(data["meeting_date"], "2025-03-25")
            self.assertEqual(data["meeting_time"], "14:30:00")
            self.assertEqual(data["created_at"], "2025-03-25T14:30:00Z")
            self.assertEqual(data["unix_time"], 1711373760)

            # Update a value
            data["meeting_time"] = "15:00:00"

            # Save the data back
            ftml.dump(data, file_path)

            # Load again and verify
            data2 = ftml.load(file_path)
            print(data2)
            self.assertEqual(data2["meeting_date"], "2025-03-25")
            self.assertEqual(data2["meeting_time"], "15:00:00")  # Updated time
            self.assertEqual(data2["created_at"], "2025-03-25T14:30:00Z")
            self.assertEqual(data2["unix_time"], 1711373760)

            # Check that comments were preserved
            with open(file_path, 'r') as f:
                content = f.read()
                self.assertIn("// Today's date", content)
                self.assertIn("// Meeting time", content)
                self.assertIn("// ISO timestamp", content)
                self.assertIn("// Unix timestamp", content)

        finally:
            # Clean up
            os.unlink(file_path)

    def test_complex_nested_structures(self):
        """Test handling of complex nested structures."""
        ftml_content = """
        config = {
            server = {
                port = 8080,
                hosts = [
                    { name = "primary", ip = "192.168.1.1" },
                    { name = "backup", ip = "192.168.1.2" }
                ]
            },
            databases = [
                {
                    name = "main",
                    settings = {
                        host = "db1.example.com",
                        replicas = ["192.168.2.1", "192.168.2.2"]
                    }
                },
                {
                    name = "logs",
                    settings = {
                        host = "logs.example.com",
                        replicas = []
                    }
                }
            ]
        }
        """

        # Load the data
        data = ftml.load(ftml_content)

        # Log the full AST structure
        ast = data._ast_node
        log_ast(ast, "Document With Only Inner Doc Comments AST")

        # Verify the nested structure was parsed correctly
        self.assertEqual(data["config"]["server"]["port"], 8080)
        self.assertEqual(data["config"]["server"]["hosts"][0]["name"], "primary")
        self.assertEqual(data["config"]["server"]["hosts"][1]["ip"], "192.168.1.2")
        self.assertEqual(data["config"]["databases"][0]["name"], "main")
        self.assertEqual(data["config"]["databases"][0]["settings"]["replicas"][1], "192.168.2.2")
        self.assertEqual(data["config"]["databases"][1]["settings"]["host"], "logs.example.com")
        self.assertEqual(len(data["config"]["databases"][1]["settings"]["replicas"]), 0)

        # Modify nested data
        data["config"]["server"]["port"] = 9000
        data["config"]["databases"][0]["settings"]["replicas"].append("192.168.2.3")

        # Dump and reload
        ftml_string = ftml.dump(data)
        new_data = ftml.load(ftml_string)

        # Verify changes were preserved
        self.assertEqual(new_data["config"]["server"]["port"], 9000)
        self.assertEqual(len(new_data["config"]["databases"][0]["settings"]["replicas"]), 3)
        self.assertEqual(new_data["config"]["databases"][0]["settings"]["replicas"][2], "192.168.2.3")
