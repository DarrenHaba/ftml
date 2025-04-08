"""
Tests for advanced nested collection scenarios in FTML.

This module tests deeply nested object and list structures with defaults at various
levels to ensure proper parsing, default application, and validation.
"""

import logging

from ftml.logger import logger
from ftml.schema.schema_parser import SchemaParser
from ftml.schema.schema_validator import apply_defaults

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class TestDeepNesting:
    """Tests for deeply nested object structures."""

    def test_deeply_nested_objects(self):
        """Test deeply nested objects with defaults at multiple levels."""
        parser = SchemaParser()

        schema = """
        L1: {
            L1O1: {
                L2O1: {
                    L3O1: {
                        L4O1: {
                            L5P1: str = "level5-default"
                        } = {
                            L5P1 = "level4-default-for-level5"
                        },
                        L4P1: int = 400
                    } = {
                        L4O1 = {
                            L5P1 = "level3-default-for-level5"
                        },
                        L4P1 = 300
                    }
                } = {
                    L3O1 = {
                        L4O1 = {
                            L5P1 = "level2-default-for-level5"
                        }
                    }
                }
            }
        } = {
            L1O1 = {
                L2O1 = {
                    L3O1 = {
                        L4O1 = {
                            L5P1 = "top-level-default"
                        }
                    }
                }
            }
        }
        """

        result = parser.parse(schema)

        # Test the parsed schema structure
        assert "L1" in result
        assert result["L1"].has_default

        # Level 1 field access
        L1O1 = result["L1"].fields["L1O1"]

        # Level 2 field access
        L2O1 = L1O1.fields["L2O1"]
        assert L2O1.has_default

        # Level 3 field access
        L3O1 = L2O1.fields["L3O1"]
        assert L3O1.has_default

        # Level 4 field access
        L4O1 = L3O1.fields["L4O1"]
        assert L4O1.has_default
        assert "L4P1" in L3O1.fields
        assert L3O1.fields["L4P1"].has_default
        assert L3O1.fields["L4P1"].default == 400

        # Level 5 field access
        L5P1 = L4O1.fields["L5P1"]
        assert L5P1.has_default
        assert L5P1.default == "level5-default"

        # Test top level default
        assert result["L1"].default["L1O1"]["L2O1"]["L3O1"]["L4O1"]["L5P1"] == "top-level-default"

        # Level 2 default for level 3
        assert L2O1.default["L3O1"]["L4O1"]["L5P1"] == "level2-default-for-level5"

        # Level 3 default for level 4
        assert L3O1.default["L4O1"]["L5P1"] == "level3-default-for-level5"
        assert L3O1.default["L4P1"] == 300

        # Level 4 default for level 5
        assert L4O1.default["L5P1"] == "level4-default-for-level5"

        # Test default application
        # Case 1: Empty data - should use top level default
        data1 = {}
        data1_with_defaults = apply_defaults(data1, result)
        assert data1_with_defaults["L1"]["L1O1"]["L2O1"]["L3O1"]["L4O1"]["L5P1"] == "top-level-default"

        # Case 2: Partial data with some levels missing
        data2 = {"L1": {"L1O1": {"L2O1": {}}}}
        data2_with_defaults = apply_defaults(data2, result)
        # L2O1 is present, but empty, so use L3O1 default object
        assert data2_with_defaults["L1"]["L1O1"]["L2O1"]["L3O1"]["L4O1"]["L5P1"] == "level3-default-for-level5"
        assert data2_with_defaults["L1"]["L1O1"]["L2O1"]["L3O1"]["L4P1"] == 300

        # Case 3: Deep partial data
        data3 = {
            "L1": {
                "L1O1": {
                    "L2O1": {
                        "L3O1": {
                            "L4P1": 999  # Only provide L4P1, L4O1 should use default
                        }
                    }
                }
            }
        }
        data3_with_defaults = apply_defaults(data3, result)
        # L4P1 should use provided value
        assert data3_with_defaults["L1"]["L1O1"]["L2O1"]["L3O1"]["L4P1"] == 999
        # L4O1 should use L3O1's default
        assert data3_with_defaults["L1"]["L1O1"]["L2O1"]["L3O1"]["L4O1"]["L5P1"] == "level4-default-for-level5"

    def test_nested_objects_with_lists(self):
        """Test nested objects containing lists with defaults."""
        parser = SchemaParser()

        schema = """
        config: {
            server: {
                ports: [int] = [80, 443],
                hosts: [{
                    name: str,
                    ip: str = "127.0.0.1"
                }] = [
                    {name = "localhost", ip = "127.0.0.1"},
                    {name = "default", ip = "0.0.0.0"}
                ]
            } = {
                ports = [8080],
                hosts = [{name = "default-server", ip = "10.0.0.1"}]
            },
            features: {
                enabled: [str] = ["basic"],
                settings: {str} = {
                    logging = "info",
                    cache = "enabled"
                }
            }
        } = {
            server = {
                ports = [9090],
                hosts = []
            },
            features = {
                enabled = [],
                settings = {}
            }
        }
        """

        result = parser.parse(schema)

        # Test the parsed schema structure
        assert "config" in result
        assert result["config"].has_default

        # Access server section
        server = result["config"].fields["server"]
        assert server.has_default

        # Access ports list
        ports = server.fields["ports"]
        assert ports.has_default
        assert ports.default == [80, 443]

        # Access hosts list with object items
        hosts = server.fields["hosts"]
        assert hosts.has_default
        assert len(hosts.default) == 2
        assert hosts.default[0]["name"] == "localhost"
        assert hosts.default[1]["name"] == "default"

        # Access features section
        features = result["config"].fields["features"]
        assert "enabled" in features.fields
        assert "settings" in features.fields

        # Test default application

        # Case 1: Empty data - should use top level default
        data1 = {}
        data1_with_defaults = apply_defaults(data1, result)
        assert data1_with_defaults["config"]["server"]["ports"] == [9090]
        assert data1_with_defaults["config"]["server"]["hosts"] == []
        assert data1_with_defaults["config"]["features"]["enabled"] == []
        assert data1_with_defaults["config"]["features"]["settings"] == {}

        # Case 2: Partial data
        data2 = {
            "config": {
                "server": {},
                "features": {
                    "enabled": ["advanced"]
                }
            }
        }
        data2_with_defaults = apply_defaults(data2, result)
        # Server should use server field default
        assert data2_with_defaults["config"]["server"]["ports"] == [80, 443]
        assert data2_with_defaults["config"]["server"]["hosts"][0]["name"] == "localhost"
        # Features.enabled should use provided value
        assert data2_with_defaults["config"]["features"]["enabled"] == ["advanced"]
        # Features.settings should use field default
        assert data2_with_defaults["config"]["features"]["settings"]["logging"] == "info"

    def test_nested_lists_with_objects555(self):
        """Test nested lists containing objects with defaults."""
        parser = SchemaParser()

        schema = """
        matrix: [
            [
                {
                    x: int = 0,
                    y: int = 0,
                    data: {
                        value: float = 0.0,
                        label: str = "empty"
                    } = {
                        value = 1.0,
                        label = "default"
                    }
                }
            ]
        ] = [
            [
                {x = 1, y = 1, data = {value = 99.9, label = "origin"}}
            ],
            [
                {x = 2, y = 2, data = {value = 88.8, label = "secondary"}}
            ]
        ]
        """

        result = parser.parse(schema)

        data2 = {
            "matrix": [
                [
                    {"x": 10, "y": 20}
                    # {"x": 10, "y": 20, "data": {}}
                ]
            ]
        }

        data2_with_defaults = apply_defaults(data2, result)
        print(5555555555555555555555555)
        print(data2_with_defaults)
        print(5555555555555555555555555)
        # So the next two lines produce the error:
        assert data2_with_defaults["matrix"][0][0]["data"]["value"] == 1.0
        assert data2_with_defaults["matrix"][0][0]["data"]["label"] == "default"

    def test_nested_lists_with_objects(self):
        """Test nested lists containing objects with defaults."""
        parser = SchemaParser()
    
        schema = """
        matrix: [
            [
                {
                    x: int = 0,
                    y: int = 0,
                    data: {
                        value: float = 0.0,
                        label: str = "empty"
                    } = {
                        value = 1.0,
                        label = "default"
                    }
                }
            ]
        ] = [
            [
                {x = 1, y = 1, data = {value = 99.9, label = "origin"}}
            ],
            [
                {x = 2, y = 2, data = {value = 88.8, label = "secondary"}}
            ]
        ]
        """
    
        result = parser.parse(schema)
    
        # Test the parsed schema structure
        assert "matrix" in result
        assert result["matrix"].has_default
        assert len(result["matrix"].default) == 2

        # Check the top-level default
        matrix_default = result["matrix"].default
        assert matrix_default[0][0]["x"] == 1
        assert matrix_default[0][0]["data"]["label"] == "origin"
        assert matrix_default[1][0]["data"]["value"] == 88.8

        # Check the item type structure - corrected to match actual structure
        matrix_item_type = result["matrix"].item_type  # This is a ListTypeNode
        # The inner list's item type is an ObjectTypeNode
        inner_object = matrix_item_type.item_type
        assert inner_object.fields["x"].default == 0
        assert inner_object.fields["y"].default == 0
        assert inner_object.fields["data"].default["value"] == 1.0
        assert inner_object.fields["data"].default["label"] == "default"

        # Check field-level defaults
        data_object = inner_object.fields["data"]
        assert data_object.fields["value"].default == 0.0
        assert data_object.fields["label"].default == "empty"

        # Test default application

        # Case 1: Empty data - should use top level default
        data1 = {}
        data1_with_defaults = apply_defaults(data1, result)
        assert data1_with_defaults["matrix"][0][0]["x"] == 1
        assert data1_with_defaults["matrix"][1][0]["data"]["label"] == "secondary"

        # # Case 2: Partial data with nested empty objects
        # data2 = {
        #     "matrix": [
        #         [
        #             {"x": 10, "y": 20, "data": {}}
        #         ]
        #     ]
        # }
        # data2_with_defaults = apply_defaults(data2, result)
        # # Should keep provided values
        # assert data2_with_defaults["matrix"][0][0]["x"] == 10
        # assert data2_with_defaults["matrix"][0][0]["y"] == 20
        # # Should use field defaults for empty data object
        # assert data2_with_defaults["matrix"][0][0]["data"]["value"] == 0.0
        # assert data2_with_defaults["matrix"][0][0]["data"]["label"] == "empty"

        # Case 2: Missing list uses the default values. 
        data2 = {}
        data2_with_defaults = apply_defaults(data2, result)
        # So the next two lines produce the error:
        assert data2_with_defaults["matrix"][0][0]["data"]["value"] == 99.9
        assert data2_with_defaults["matrix"][0][0]["data"]["label"] == "origin"
        assert data2_with_defaults["matrix"][1][0]["data"]["value"] == 88.8
        assert data2_with_defaults["matrix"][1][0]["data"]["label"] == "secondary"

        # Case 3: Missing field uses default object
        data3 = {
            "matrix": [
                [
                    {"x": 10, "y": 20} # Missing "data" field!
                ]
            ]
        }
        data3_with_defaults = apply_defaults(data3, result)
        # So the next two lines produce the error:
        assert data3_with_defaults["matrix"][0][0]["data"]["value"] == 1.0
        assert data3_with_defaults["matrix"][0][0]["data"]["label"] == "default"

    def test_extreme_nesting_object_list_mix(self):
        """Test extremely nested mixed structure with objects and lists."""
        parser = SchemaParser()

        schema = """
        L1Obj: {
            L2List: [{
                L3Obj: {
                    L4List: [{
                        L5Obj: {
                            L6Val: str = "L6-default"
                        } = {
                            L6Val = "L5-default-for-L6"
                        }
                    }] = [{
                        L5Obj = {
                            L6Val = "L4-default-for-L6"
                        }
                    }]
                } = {
                    L4List = [{
                        L5Obj = {
                            L6Val = "L3-default-for-L6"
                        }
                    }]
                }
            }] = [{
                L3Obj = {
                    L4List = [{
                        L5Obj = {
                            L6Val = "L2-default-for-L6"
                        }
                    }]
                }
            }]
        } = {
            L2List = [{
                L3Obj = {
                    L4List = [{
                        L5Obj = {
                            L6Val = "L1-default-for-L6"
                        }
                    }]
                }
            }]
        }
        """

        result = parser.parse(schema)

        # Test the parsed schema structure
        assert "L1Obj" in result
        assert result["L1Obj"].has_default

        # Navigate through the schema structure
        L2List = result["L1Obj"].fields["L2List"]
        assert L2List.has_default

        L3Obj = L2List.item_type.fields["L3Obj"]
        assert L3Obj.has_default

        L4List = L3Obj.fields["L4List"]
        assert L4List.has_default

        L5Obj = L4List.item_type.fields["L5Obj"]
        assert L5Obj.has_default

        L6Val = L5Obj.fields["L6Val"]
        assert L6Val.has_default
        assert L6Val.default == "L6-default"

        # Check defaults at each level
        assert result["L1Obj"].default["L2List"][0]["L3Obj"]["L4List"][0]["L5Obj"]["L6Val"] == "L1-default-for-L6"
        assert L2List.default[0]["L3Obj"]["L4List"][0]["L5Obj"]["L6Val"] == "L2-default-for-L6"
        assert L3Obj.default["L4List"][0]["L5Obj"]["L6Val"] == "L3-default-for-L6"
        assert L4List.default[0]["L5Obj"]["L6Val"] == "L4-default-for-L6"
        assert L5Obj.default["L6Val"] == "L5-default-for-L6"

        # Test default application with various partial data

        # Case 1: Empty data - should use top level default
        data1 = {}
        data1_with_defaults = apply_defaults(data1, result)
        assert data1_with_defaults["L1Obj"]["L2List"][0]["L3Obj"]["L4List"][0]["L5Obj"]["L6Val"] == "L1-default-for-L6"

        # Case 2: Partial data - L1Obj provided but empty
        data2 = {
            "L1Obj": {}
        }

        data2_with_defaults = apply_defaults(data2, result)
        # Should use L3Obj field default for L4List
        assert data2_with_defaults["L1Obj"]["L2List"][0]["L3Obj"]["L4List"][0]["L5Obj"]["L6Val"] == "L2-default-for-L6"


class TestEdgeCases:
    """Test edge cases with nested collections and defaults."""

    def test_empty_collections_with_defaults(self):
        """Test empty collections with defaults."""
        parser = SchemaParser()

        schema = """
        emptiness: {
            empty_obj: {} = {},
            empty_list: [] = [],
            obj_with_empty_defaults: {
                a: int = 1,
                b: str = "text"
            } = {},
            list_with_empty_item_defaults: [{
                x: int = 0,
                y: int = 0
            }] = []
        }
        """

        result = parser.parse(schema)

        # Test schema structure
        assert "emptiness" in result

        empty_obj = result["emptiness"].fields["empty_obj"]
        assert empty_obj.has_default
        assert empty_obj.default == {}

        empty_list = result["emptiness"].fields["empty_list"]
        assert empty_list.has_default
        assert empty_list.default == []

        obj_with_empty_defaults = result["emptiness"].fields["obj_with_empty_defaults"]
        assert obj_with_empty_defaults.has_default
        assert obj_with_empty_defaults.default == {}

        list_with_empty_item_defaults = result["emptiness"].fields["list_with_empty_item_defaults"]
        assert list_with_empty_item_defaults.has_default
        assert list_with_empty_item_defaults.default == []

        # Test default application
        data = {}
        data_with_defaults = apply_defaults(data, result)

        assert "emptiness" in data_with_defaults
        assert data_with_defaults["emptiness"]["empty_obj"] == {}
        assert data_with_defaults["emptiness"]["empty_list"] == []
        assert data_with_defaults["emptiness"]["obj_with_empty_defaults"]["a"] == 1
        assert data_with_defaults["emptiness"]["obj_with_empty_defaults"]["b"] == "text"
        assert data_with_defaults["emptiness"]["list_with_empty_item_defaults"] == []
