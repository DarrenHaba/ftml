import logging
from ftml import load, dump
from ftml.logger import logger

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_comments_only():
    """Test loading a string with only comments"""
    ftml_content = """
    // This is a comment
    // Another comment
    """
    data = load(ftml_content)
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")

    assert data == {}
    assert hasattr(data, "_ast_node")
    print(data._ast_node)
    assert data._ast_node.leading_comments


def test_document_orphaned_comments():
    """Test loading a string with comments after the last node"""
    ftml_content = """
    // Comment above node
    key = "value"
    // This is a comment after the last node
    // Another comment after the last node
    """
    data = load(ftml_content)
    assert data == {"key": "value"}
    assert hasattr(data, "_ast_node")
    # Verify document node in AST has end_leading_comments (assuming the proposal is implemented)
    assert hasattr(data._ast_node, "end_leading_comments")
    assert len(data._ast_node.end_leading_comments) == 2



def test_list_orphaned_comments():
    """Test loading a string with comments after the last list item"""
    ftml_content = """
    my_list = [
        // Comment before last item
        "only_item"
        // Comment after last item
        // Another comment after last item
    ]
    """
    data = load(ftml_content)
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")

    assert "my_list" in data
    assert data["my_list"] == ["only_item"]
    assert hasattr(data, "_ast_node")
    # Verify list node in AST has end_leading_comments (assuming the proposal is implemented)
    list_node = data._ast_node.items["my_list"].value  # This would be the ListNode
    assert hasattr(list_node, "end_leading_comments")
    assert len(list_node.end_leading_comments) == 2


def test_object_orphaned_comments():
    """Test loading a string with comments after the last object property"""
    ftml_content = """
    my_obj = {
        // Comment before property
        only_prop = "value"
        // Comment after last property
        // Another comment after last property
    }
    """
    data = load(ftml_content)
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")
    
    assert "my_obj" in data
    assert data["my_obj"] == {"only_prop": "value"}
    assert hasattr(data, "_ast_node")
    # Verify object node in AST has end_leading_comments (assuming the proposal is implemented)
    obj_node = data._ast_node.items["my_obj"].value  # This would be the ObjectNode
    assert hasattr(obj_node, "end_leading_comments")
    assert len(obj_node.end_leading_comments) == 2
    