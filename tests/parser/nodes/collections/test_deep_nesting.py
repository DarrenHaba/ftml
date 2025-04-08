import pytest
from ftml import load, FTMLParseError


def test_list_of_dictionaries():
    """Test a list of dictionaries."""
    ftml_input = """users = [
        { id = 1, name = "Alice", active = true },
        { id = 2, name = "Bob", active = false },
        { id = 3, name = "Charlie", active = true }
    ]"""
    data = load(ftml_input)
    assert len(data["users"]) == 3
    assert data["users"][0]["id"] == 1
    assert data["users"][1]["name"] == "Bob"
    assert data["users"][2]["active"] is True


def test_dictionary_of_dictionaries():
    """Test a dictionary of dictionaries."""
    ftml_input = """
    departments = {
        engineering = {
            head = "Alice",
            budget = 1000000,
            headcount = 50
        },
        marketing = {
            head = "Bob",
            budget = 500000,
            headcount = 25
        },
        sales = {
            head = "Charlie",
            budget = 750000,
            headcount = 40
        }
    }
    """
    data = load(ftml_input)
    assert len(data["departments"]) == 3
    assert data["departments"]["engineering"]["head"] == "Alice"
    assert data["departments"]["marketing"]["budget"] == 500000
    assert data["departments"]["sales"]["headcount"] == 40


def test_dictionary_with_list_of_dictionaries():
    """Test a dictionary containing a list of dictionaries."""
    ftml_input = """
    team = {
        name = "Development",
        members = [
            { name = "Alice", role = "Engineer", level = 3 },
            { name = "Bob", role = "Designer", level = 2 },
            { name = "Charlie", role = "PM", level = 4 }
        ],
        projects = [
            { id = "alpha", priority = "high" },
            { id = "beta", priority = "medium" }
        ]
    }
    """
    data = load(ftml_input)
    assert data["team"]["name"] == "Development"
    assert len(data["team"]["members"]) == 3
    assert data["team"]["members"][0]["level"] == 3
    assert data["team"]["projects"][1]["priority"] == "medium"


def test_list_of_lists():
    """Test a list of lists (matrix-like structure)."""
    ftml_input = """
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    """
    data = load(ftml_input)
    assert data["matrix"][0][0] == 1
    assert data["matrix"][1][1] == 5
    assert data["matrix"][2][2] == 9


def test_extremely_deep_nesting():
    """Test extremely deep nesting (7+ levels)."""
    ftml_input = """
    level1 = {
        a = {
            b = {
                c = {
                    d = {
                        e = {
                            f = {
                                g = {
                                    value = "found me!"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    data = load(ftml_input)
    assert data["level1"]["a"]["b"]["c"]["d"]["e"]["f"]["g"]["value"] == "found me!"


def test_mixed_deep_nesting():
    """Test mixed deep nesting with alternating lists and dictionaries."""
    ftml_input = """
    config = {
        system = {
            paths = [
                {
                    type = "data",
                    locations = [
                        {
                            primary = "/data",
                            backups = [
                                { path = "/backup1", priority = 1 },
                                { path = "/backup2", priority = 2 }
                            ]
                        }
                    ]
                },
                {
                    type = "logs",
                    locations = [
                        {
                            primary = "/logs",
                            backups = [
                                { path = "/logbackup", priority = 1 }
                            ]
                        }
                    ]
                }
            ]
        }
    }
    """
    data = load(ftml_input)
    # Navigate through the deep structure
    assert data["config"]["system"]["paths"][0]["type"] == "data"
    assert data["config"]["system"]["paths"][0]["locations"][0]["backups"][1]["path"] == "/backup2"
    assert data["config"]["system"]["paths"][1]["locations"][0]["backups"][0]["priority"] == 1


def test_complex_configuration():
    """Test a realistic complex configuration structure."""
    ftml_input = """
    application = {
        name = "MyApp",
        version = "1.0.0",
        settings = {
            server = {
                host = "localhost",
                port = 8080,
                ssl = {
                    enabled = true,
                    cert_path = "/etc/certs/server.crt",
                    key_path = "/etc/certs/server.key"
                },
                routes = [
                    { path = "/api", auth = true, methods = ["GET", "POST"] },
                    { path = "/public", auth = false, methods = ["GET"] }
                ]
            },
            database = {
                primary = {
                    type = "postgres",
                    host = "db1.example.com",
                    port = 5432,
                    credentials = {
                        username = "app_user",
                        password = "secret"
                    },
                    pools = [
                        { name = "read", size = 10, timeout = 30 },
                        { name = "write", size = 5, timeout = 60 }
                    ]
                },
                replicas = [
                    { 
                        host = "db2.example.com", 
                        port = 5432,
                        read_only = true
                    },
                    { 
                        host = "db3.example.com", 
                        port = 5432,
                        read_only = true
                    }
                ]
            },
            cache = {
                enabled = true,
                ttl = 300,
                strategies = [
                    { type = "memory", max_size = 1024 },
                    { type = "redis", host = "cache.example.com" }
                ]
            },
            logging = {
                level = "info",
                outputs = [
                    { type = "console", format = "json" },
                    { 
                        type = "file", 
                        path = "/var/log/app.log",
                        rotation = {
                            size = "100MB",
                            count = 5
                        }
                    }
                ]
            }
        }
    }
    """
    data = load(ftml_input)

    # Test various paths through the complex structure
    assert data["application"]["name"] == "MyApp"
    assert data["application"]["settings"]["server"]["ssl"]["enabled"] is True
    assert data["application"]["settings"]["server"]["routes"][0]["methods"][1] == "POST"
    assert data["application"]["settings"]["database"]["primary"]["credentials"]["username"] == "app_user"
    assert data["application"]["settings"]["database"]["primary"]["pools"][0]["size"] == 10
    assert data["application"]["settings"]["database"]["replicas"][1]["host"] == "db3.example.com"
    assert data["application"]["settings"]["cache"]["strategies"][1]["host"] == "cache.example.com"
    assert data["application"]["settings"]["logging"]["outputs"][1]["rotation"]["count"] == 5


def test_mix_of_all_scalars():
    """Test a deeply nested structure with all scalar types at various levels."""
    ftml_input = """
    data = {
        strings = {
            simple = "hello",
            list = ["a", "b", "c"],
            nested = { key = "value" }
        },
        numbers = {
            integers = [1, 2, 3],
            floats = [1.1, 2.2, 3.3],
            mixed = {
                int_val = 42,
                float_val = 3.14,
                list = [1, 2.5, 3]
            }
        },
        booleans = {
            true_val = true,
            false_val = false,
            list = [true, false, true],
            nested = {
                deep = {
                    deeper = {
                        value = false
                    }
                }
            }
        },
        nulls = {
            explicit = null,
            list = [null, null],
            mixed = [1, null, "text", null]
        },
        mixed_array = [
            "string",
            42,
            3.14,
            true,
            null,
            { key = "object in array" },
            [1, 2, 3]
        ]
    }
    """
    data = load(ftml_input)

    # Test string values
    assert data["data"]["strings"]["simple"] == "hello"
    assert data["data"]["strings"]["list"] == ["a", "b", "c"]
    assert data["data"]["strings"]["nested"]["key"] == "value"

    # Test number values
    assert data["data"]["numbers"]["integers"] == [1, 2, 3]
    assert data["data"]["numbers"]["floats"] == [1.1, 2.2, 3.3]
    assert data["data"]["numbers"]["mixed"]["int_val"] == 42
    assert data["data"]["numbers"]["mixed"]["float_val"] == 3.14

    # Test boolean values
    assert data["data"]["booleans"]["true_val"] is True
    assert data["data"]["booleans"]["false_val"] is False
    assert data["data"]["booleans"]["nested"]["deep"]["deeper"]["value"] is False

    # Test null values
    assert data["data"]["nulls"]["explicit"] is None
    assert data["data"]["nulls"]["list"] == [None, None]
    assert data["data"]["nulls"]["mixed"] == [1, None, "text", None]

    # Test mixed array
    assert data["data"]["mixed_array"][0] == "string"
    assert data["data"]["mixed_array"][1] == 42
    assert data["data"]["mixed_array"][2] == 3.14
    assert data["data"]["mixed_array"][3] is True
    assert data["data"]["mixed_array"][4] is None
    assert data["data"]["mixed_array"][5]["key"] == "object in array"
    assert data["data"]["mixed_array"][6] == [1, 2, 3]
