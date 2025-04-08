import logging
from ftml import load, dump
from ftml.logger import logger
from tests.parser.comments.utils.helpers import log_ast

# Set up logging for tests
logger.setLevel(logging.DEBUG)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def test_basic_leading_comments():
    """Test basic leading comments on key-value pairs."""
    logger.debug("RUNNING test_basic_leading_comments")
    ftml = """// key1 leading comment
key1 = "value1"

// key2 leading comment 1
// key2 leading comment 2
key2 = "value2"
"""
    logger.debug(f"Input FTML:\n{ftml}")
    data = load(ftml)
    ast = data._ast_node

    # Log the full AST structure
    log_ast(ast, "Basic Leading Comments AST")

    # Verify comments are attached correctly
    assert len(ast.items["key1"].leading_comments) == 1
    assert ast.items["key1"].leading_comments[0].text == "key1 leading comment"

    assert len(ast.items["key2"].leading_comments) == 2
    assert ast.items["key2"].leading_comments[0].text == "key2 leading comment 1"
    assert ast.items["key2"].leading_comments[1].text == "key2 leading comment 2"

    # Test round-trip
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")
    assert "// key1 leading comment" in dumped
    assert "// key2 leading comment 1" in dumped
    assert "// key2 leading comment 2" in dumped


def test_basic_inline_comments():
    """Test basic inline comments on key-value pairs."""
    logger.debug("RUNNING test_basic_inline_comments")
    ftml = """key1 = "value1"  // key1 inline comment
key2 = "value2"  // key2 inline comment
"""
    logger.debug(f"Input FTML:\n{ftml}")
    data = load(ftml)
    ast = data._ast_node

    # Log the full AST structure
    log_ast(ast, "Basic Inline Comments AST")

    # Verify comments are attached correctly
    assert ast.items["key1"].inline_comment is not None
    assert ast.items["key1"].inline_comment.text == "key1 inline comment"

    assert ast.items["key2"].inline_comment is not None
    assert ast.items["key2"].inline_comment.text == "key2 inline comment"

    # Test round-trip
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")
    assert "// key1 inline comment" in dumped
    assert "// key2 inline comment" in dumped


































def test_simple_list_comments():
    """Test comments on simple list and its elements."""
    logger.debug("RUNNING test_simple_list_comments")
    ftml = """// my_list leading comment
my_list = [  // my_list inline comment
    // my_list[0] leading comment
    "first",  // my_list[0] inline comment
    
    // my_list[1] leading comment
    "second"  // my_list[1] inline comment
]
"""
    logger.debug(f"Input FTML:\n{ftml}")
    data = load(ftml)
    ast = data._ast_node

    # Log the full AST structure
    log_ast(ast, "Simple List Comments AST")

    # Verify list comments are attached correctly
    assert len(ast.items["my_list"].leading_comments) == 1
    assert ast.items["my_list"].leading_comments[0].text == "my_list leading comment"
    assert ast.items["my_list"].inline_comment is not None
    assert ast.items["my_list"].inline_comment.text == "my_list inline comment"

    # Verify list element comments are attached correctly
    list_node = ast.items["my_list"].value
    assert len(list_node.elements) == 2

    # First element
    first_elem = list_node.elements[0]
    assert len(first_elem.leading_comments) == 1
    assert first_elem.leading_comments[0].text == "my_list[0] leading comment"
    assert first_elem.inline_comment is not None
    assert first_elem.inline_comment.text == "my_list[0] inline comment"

    # Second element
    second_elem = list_node.elements[1]
    assert len(second_elem.leading_comments) == 1
    assert second_elem.leading_comments[0].text == "my_list[1] leading comment"
    assert second_elem.inline_comment is not None
    assert second_elem.inline_comment.text == "my_list[1] inline comment"

    # Test round-trip
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")
    assert "// my_list leading comment" in dumped
    assert "// my_list inline comment" in dumped
    assert "// my_list[0] leading comment" in dumped
    assert "// my_list[0] inline comment" in dumped
    assert "// my_list[1] leading comment" in dumped
    assert "// my_list[1] inline comment" in dumped










def test_trailing_comments_after_list():
    """Test comments that appear after a list's last item."""
    ftml = """my_list = [
    // Comment before last item
    "only_item"
    // Comment after last item
    // Another comment after last item
]
// Comment after closing bracket
// Another comment after closing bracket
"""
    logger.debug(f"Input FTML:\n{ftml}")
    data = load(ftml)
    ast = data._ast_node

    # Log the full AST structure
    log_ast(ast, "Trailing Comments After List AST")

    # Test round-trip
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")

    # Verify comments after last item (should be attached to the list node)
    list_node = ast.items["my_list"].value
    # Check if the comments are attached to the list node itself
    for comment in list_node.elements[0].leading_comments:
        logger.debug(f"Comment on list element: {comment.text}")

    # Check if the list has inline_comment_end for comments on the closing bracket
    if hasattr(list_node, "inline_comment_end") and list_node.inline_comment_end:
        logger.debug(f"List inline_comment_end: {list_node.inline_comment_end.text}")















def test_simple_object_comments():
    """Test comments on simple object and its properties."""
    logger.debug("RUNNING test_simple_object_comments")
    ftml = """// my_obj leading comment
my_obj = {  // my_obj inline comment
    // my_obj.prop1 leading comment
    prop1 = "value1",  // my_obj.prop1 inline comment
    
    // my_obj.prop2 leading comment
    prop2 = "value2"  // my_obj.prop2 inline comment
}
"""
    logger.debug(f"Input FTML:\n{ftml}")
    data = load(ftml)
    ast = data._ast_node

    # Log the full AST structure
    log_ast(ast, "Simple Object Comments AST")

    # Verify object comments are attached correctly
    assert len(ast.items["my_obj"].leading_comments) == 1
    assert ast.items["my_obj"].leading_comments[0].text == "my_obj leading comment"
    assert ast.items["my_obj"].inline_comment is not None
    assert ast.items["my_obj"].inline_comment.text == "my_obj inline comment"

    # Verify object property comments are attached correctly
    obj_node = ast.items["my_obj"].value
    assert len(obj_node.items) == 2

    # First property
    prop1 = obj_node.items["prop1"]
    assert len(prop1.leading_comments) == 1
    assert prop1.leading_comments[0].text == "my_obj.prop1 leading comment"
    assert prop1.inline_comment is not None
    assert prop1.inline_comment.text == "my_obj.prop1 inline comment"

    # Second property
    prop2 = obj_node.items["prop2"]
    assert len(prop2.leading_comments) == 1
    assert prop2.leading_comments[0].text == "my_obj.prop2 leading comment"
    assert prop2.inline_comment is not None
    assert prop2.inline_comment.text == "my_obj.prop2 inline comment"

    # Test round-trip
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")
    assert "// my_obj leading comment" in dumped
    assert "// my_obj inline comment" in dumped
    assert "// my_obj.prop1 leading comment" in dumped
    assert "// my_obj.prop1 inline comment" in dumped
    assert "// my_obj.prop2 leading comment" in dumped
    assert "// my_obj.prop2 inline comment" in dumped






def test_trailing_comments_after_object():
    """Test comments that appear after an object's last property."""
    ftml = """my_obj = {
    // Comment before property
    only_prop = "value"
    // Comment after last property
    // Another comment after last property
}
// Comment after closing brace
// Another comment after closing brace
"""
    logger.debug(f"Input FTML:\n{ftml}")
    data = load(ftml)
    ast = data._ast_node

    # Log the full AST structure
    log_ast(ast, "Trailing Comments After Object AST")

    # Test round-trip
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")

    # Verify comments after last property (if they're attached to anything)
    obj_node = ast.items["my_obj"].value
    # Check if comments are attached to any properties
    for prop_key, prop_node in obj_node.items.items():
        for comment in prop_node.leading_comments:
            logger.debug(f"Comment on property {prop_key}: {comment.text}")

    # Check if object has any comment properties for trailing comments
    if hasattr(obj_node, "inline_comment_end") and obj_node.inline_comment_end:
        logger.debug(f"Object inline_comment_end: {obj_node.inline_comment_end.text}")









def test_nested_structure_comments():
    """Test comments on nested structures (lists in lists, objects in lists, etc.)"""
    logger.debug("RUNNING test_nested_structure_comments")
    ftml = """// nested_list leading comment
nested_list = [  // nested_list inline comment
    // nested_list[0] leading comment
    [  // nested_list[0] inline comment
        // nested_list[0][0] leading comment
        "inner_item1",  // nested_list[0][0] inline comment
        
        // nested_list[0][1] leading comment
        "inner_item2"  // nested_list[0][1] inline comment
    ],
    
    // nested_list[1] leading comment
    {  // nested_list[1] inline comment
        // nested_list[1].prop1 leading comment
        prop1 = "value1",  // nested_list[1].prop1 inline comment
        
        // nested_list[1].prop2 leading comment
        prop2 = "value2"  // nested_list[1].prop2 inline comment
    }
]
"""
    logger.debug(f"Input FTML:\n{ftml}")
    data = load(ftml)
    ast = data._ast_node

    # Log the full AST structure
    log_ast(ast, "Nested Structure Comments AST")

    # Verify top-level list comments
    assert len(ast.items["nested_list"].leading_comments) == 1
    assert ast.items["nested_list"].leading_comments[0].text == "nested_list leading comment"
    assert ast.items["nested_list"].inline_comment is not None
    assert ast.items["nested_list"].inline_comment.text == "nested_list inline comment"

    # Get the top list node
    list_node = ast.items["nested_list"].value
    assert len(list_node.elements) == 2

    # First element (inner list)
    inner_list = list_node.elements[0]
    assert len(inner_list.leading_comments) == 1
    assert inner_list.leading_comments[0].text == "nested_list[0] leading comment"
    assert inner_list.inline_comment is not None
    assert inner_list.inline_comment.text == "nested_list[0] inline comment"

    # Inner list items
    assert len(inner_list.elements) == 2
    inner_item1 = inner_list.elements[0]
    assert len(inner_item1.leading_comments) == 1
    assert inner_item1.leading_comments[0].text == "nested_list[0][0] leading comment"
    assert inner_item1.inline_comment is not None
    assert inner_item1.inline_comment.text == "nested_list[0][0] inline comment"

    inner_item2 = inner_list.elements[1]
    assert len(inner_item2.leading_comments) == 1
    assert inner_item2.leading_comments[0].text == "nested_list[0][1] leading comment"
    assert inner_item2.inline_comment is not None
    assert inner_item2.inline_comment.text == "nested_list[0][1] inline comment"

    # Second element (inner object)
    inner_obj = list_node.elements[1]
    assert len(inner_obj.leading_comments) == 1
    assert inner_obj.leading_comments[0].text == "nested_list[1] leading comment"
    assert inner_obj.inline_comment is not None
    assert inner_obj.inline_comment.text == "nested_list[1] inline comment"

    # Inner object properties
    obj_prop1 = inner_obj.items["prop1"]
    assert len(obj_prop1.leading_comments) == 1
    assert obj_prop1.leading_comments[0].text == "nested_list[1].prop1 leading comment"
    assert obj_prop1.inline_comment is not None
    assert obj_prop1.inline_comment.text == "nested_list[1].prop1 inline comment"

    obj_prop2 = inner_obj.items["prop2"]
    assert len(obj_prop2.leading_comments) == 1
    assert obj_prop2.leading_comments[0].text == "nested_list[1].prop2 leading comment"
    assert obj_prop2.inline_comment is not None
    assert obj_prop2.inline_comment.text == "nested_list[1].prop2 inline comment"

    # Test round-trip
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")
    # Check a few key parts of the output
    assert "// nested_list leading comment" in dumped
    assert "// nested_list[0] inline comment" in dumped
    assert "// nested_list[0][0] leading comment" in dumped
    assert "// nested_list[1].prop2 inline comment" in dumped
