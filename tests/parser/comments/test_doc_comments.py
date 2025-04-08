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


def test_inner_doc_comments():
    """Test document-level inner doc comments (//!)."""
    logger.debug("RUNNING test_inner_doc_comments")
    ftml = """//! Document-level inner doc comment
//! Second document-level comment

key1 = "value1"
key2 = "value2"
"""
    logger.debug(f"Input FTML:\n{ftml}")
    data = load(ftml)
    ast = data._ast_node

    # Log the AST structure
    log_ast(ast, "Inner Doc Comments AST")

    # Verify inner doc comments are attached to the document
    assert len(ast.inner_doc_comments) == 2
    assert ast.inner_doc_comments[0].text == "Document-level inner doc comment"
    assert ast.inner_doc_comments[1].text == "Second document-level comment"

    # Test round-trip
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")
    assert "//! Document-level inner doc comment" in dumped
    assert "//! Second document-level comment" in dumped


def test_outer_doc_comments():
    """Test outer doc comments (///) on key-value pairs."""
    logger.debug("RUNNING test_outer_doc_comments")
    ftml = """/// Documentation for key1
/// More details about key1
key1 = "value1"

/// Documentation for key2
key2 = "value2"
"""
    logger.debug(f"Input FTML:\n{ftml}")
    data = load(ftml)
    ast = data._ast_node

    # Log the AST structure
    log_ast(ast, "Outer Doc Comments AST")

    # Verify outer doc comments are attached to key-value nodes
    assert len(ast.items["key1"].outer_doc_comments) == 2
    assert ast.items["key1"].outer_doc_comments[0].text == "Documentation for key1"
    assert ast.items["key1"].outer_doc_comments[1].text == "More details about key1"

    assert len(ast.items["key2"].outer_doc_comments) == 1
    assert ast.items["key2"].outer_doc_comments[0].text == "Documentation for key2"

    # Test round-trip
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")
    assert "/// Documentation for key1" in dumped
    assert "/// More details about key1" in dumped
    assert "/// Documentation for key2" in dumped


def test_container_inner_doc_comments():
    """Test inner doc comments inside containers (lists and objects)."""
    logger.debug("RUNNING test_container_inner_doc_comments")
    ftml = """list = [
    //! Inner documentation for the list
    //! Second line of list docs
    "item1",
    "item2"
]

obj = {
    //! Inner documentation for the object
    key1 = "value1",
    key2 = "value2"
}
"""
    logger.debug(f"Input FTML:\n{ftml}")
    data = load(ftml)
    ast = data._ast_node

    # Log the AST structure
    log_ast(ast, "Container Inner Doc Comments AST")

    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")

    # Verify inner doc comments are attached to the containers
    list_node = ast.items["list"].value
    assert len(list_node.inner_doc_comments) == 2
    assert list_node.inner_doc_comments[0].text == "Inner documentation for the list"
    assert list_node.inner_doc_comments[1].text == "Second line of list docs"

    obj_node = ast.items["obj"].value
    assert len(obj_node.inner_doc_comments) == 1
    assert obj_node.inner_doc_comments[0].text == "Inner documentation for the object"

    # Test round-trip
    assert "//! Inner documentation for the list" in dumped
    assert "//! Second line of list docs" in dumped
    assert "//! Inner documentation for the object" in dumped


def test_nested_structure_doc_comments():
    """Test doc comments in nested structures."""
    logger.debug("RUNNING test_nested_structure_doc_comments")
    ftml = """nested = [
    /// Documentation for first nested list
    [
        //! Inner documentation for nested list
        "nested_item1",
        "nested_item2"
    ],
    
    /// Documentation for nested object
    {
        //! Inner documentation for nested object
        
        /// Documentation for property
        key = "value"
    }
]
"""
    logger.debug(f"Input FTML:\n{ftml}")
    data = load(ftml)
    ast = data._ast_node

    # Log the AST structure
    log_ast(ast, "Nested Doc Comments AST")

    # Get the parent list node
    nested_list = ast.items["nested"].value
    assert len(nested_list.elements) == 2

    # Check the first element (nested list)
    first_elem = nested_list.elements[0]
    assert len(first_elem.outer_doc_comments) == 1
    assert first_elem.outer_doc_comments[0].text == "Documentation for first nested list"
    assert len(first_elem.inner_doc_comments) == 1
    assert first_elem.inner_doc_comments[0].text == "Inner documentation for nested list"

    # Check the second element (nested object)
    second_elem = nested_list.elements[1]
    assert len(second_elem.outer_doc_comments) == 1
    assert second_elem.outer_doc_comments[0].text == "Documentation for nested object"
    assert len(second_elem.inner_doc_comments) == 1
    assert second_elem.inner_doc_comments[0].text == "Inner documentation for nested object"

    # Check the property of the nested object
    key_node = second_elem.items["key"]
    assert len(key_node.outer_doc_comments) == 1
    assert key_node.outer_doc_comments[0].text == "Documentation for property"

    # Test round-trip
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")
    assert "/// Documentation for first nested list" in dumped
    assert "//! Inner documentation for nested list" in dumped
    assert "/// Documentation for nested object" in dumped
    assert "//! Inner documentation for nested object" in dumped
    assert "/// Documentation for property" in dumped


def test_complex_doc_comments():
    """Test a complex scenario with various types of doc comments."""
    logger.debug("RUNNING test_complex_doc_comments")
    ftml = """//! Document-level inner doc comment
//! Another document-level comment

// Regular leading comment for key1
/// Outer doc comment for key1
key1 = "value1"  // Inline comment for key1

/// Outer doc comment for list
/// Another outer doc comment for list
my_list = [
    //! Inner doc comment for list
    //! Another inner doc comment for list
    
    /// Outer doc comment for list item
    "first",
    
    /// Outer doc comment for nested list
    [
        //! Inner doc comment for nested list
        "nested item"
    ]
]

/// Outer doc comment for object
my_obj = {
    //! Inner doc comment for object
    
    /// Outer doc comment for property
    prop1 = "value1"
}
"""
    logger.debug(f"Input FTML:\n{ftml}")
    data = load(ftml)
    ast = data._ast_node

    # Log the full AST structure
    log_ast(ast, "Complex Doc Comments AST")

    # Test round-trip
    dumped = dump(data)
    logger.debug(f"Round-trip output:\n{dumped}")

    # Verify document-level inner doc comments
    assert len(ast.inner_doc_comments) == 2
    assert ast.inner_doc_comments[0].text == "Document-level inner doc comment"
    assert ast.inner_doc_comments[1].text == "Another document-level comment"

    # Verify key1 outer doc comment and regular comments
    assert len(ast.items["key1"].outer_doc_comments) == 1
    assert ast.items["key1"].outer_doc_comments[0].text == "Outer doc comment for key1"
    assert len(ast.items["key1"].leading_comments) == 1
    assert ast.items["key1"].leading_comments[0].text == "Regular leading comment for key1"
    assert ast.items["key1"].inline_comment is not None
    assert ast.items["key1"].inline_comment.text == "Inline comment for key1"

    # Verify list outer doc comments
    assert len(ast.items["my_list"].outer_doc_comments) == 2
    assert ast.items["my_list"].outer_doc_comments[0].text == "Outer doc comment for list"
    assert ast.items["my_list"].outer_doc_comments[1].text == "Another outer doc comment for list"

    # Verify list inner doc comments
    list_node = ast.items["my_list"].value
    assert len(list_node.inner_doc_comments) == 2
    assert list_node.inner_doc_comments[0].text == "Inner doc comment for list"
    assert list_node.inner_doc_comments[1].text == "Another inner doc comment for list"

    # Verify list item doc comments
    assert len(list_node.elements[0].outer_doc_comments) == 1
    assert list_node.elements[0].outer_doc_comments[0].text == "Outer doc comment for list item"

    # Verify nested list doc comments
    nested_list = list_node.elements[1]
    assert len(nested_list.outer_doc_comments) == 1
    assert nested_list.outer_doc_comments[0].text == "Outer doc comment for nested list"
    assert len(nested_list.inner_doc_comments) == 1
    assert nested_list.inner_doc_comments[0].text == "Inner doc comment for nested list"

    # Verify object doc comments
    assert len(ast.items["my_obj"].outer_doc_comments) == 1
    assert ast.items["my_obj"].outer_doc_comments[0].text == "Outer doc comment for object"

    # Verify object inner doc comments
    obj_node = ast.items["my_obj"].value
    assert len(obj_node.inner_doc_comments) == 1
    assert obj_node.inner_doc_comments[0].text == "Inner doc comment for object"

    # Verify object property doc comments
    prop1 = obj_node.items["prop1"]
    assert len(prop1.outer_doc_comments) == 1
    assert prop1.outer_doc_comments[0].text == "Outer doc comment for property"

    # Verify all doc comments are preserved
    assert "//! Document-level inner doc comment" in dumped
    assert "/// Outer doc comment for key1" in dumped
    assert "// Regular leading comment for key1" in dumped
    assert "// Inline comment for key1" in dumped
    assert "//! Inner doc comment for list" in dumped
    assert "/// Outer doc comment for list item" in dumped
    assert "//! Inner doc comment for nested list" in dumped
    assert "//! Inner doc comment for object" in dumped
    assert "/// Outer doc comment for property" in dumped


def test_empty_and_comment_only_documents():
    """Test handling of empty documents and documents with only comments"""
    import ftml
    from ftml.parser.ast import DocumentNode

    # Case 1: Empty string
    data1 = ftml.load("")
    assert data1 == {}
    assert isinstance(data1, ftml.FTMLDict)
    assert hasattr(data1, "_ast_node")
    assert isinstance(data1._ast_node, DocumentNode)

    # Case 2: Document with only whitespace
    data2 = ftml.load("   \n   ")
    assert data2 == {}
    assert isinstance(data2, ftml.FTMLDict)
    assert hasattr(data2, "_ast_node")

    # Case 3: Document with only regular comments
    data3 = ftml.load("// Comment 1\n// Comment 2")
    assert data3 == {}
    assert isinstance(data3, ftml.FTMLDict)
    assert hasattr(data3, "_ast_node")

    # Case 4: Document with only inner doc comments
    data4 = ftml.load("//! Doc comment 1\n//! Doc comment 2")
    assert data4 == {}
    assert isinstance(data4, ftml.FTMLDict)
    assert hasattr(data4, "_ast_node")
    assert len(data4._ast_node.inner_doc_comments) == 2

    def test_document_only_inner_doc_comments():
        """Test loading a string with ONLY inner doc comments and no nodes"""

    # Important: Use a raw string with no indentation before the //! comments
    ftml_content = r"""//! This is a document comment
//! Another document comment"""
    data = load(ftml_content)

    # Log the full AST structure
    ast = data._ast_node
    log_ast(ast, "Document With Only Inner Doc Comments AST")

    # Verify document loads without error
    assert data == {}

    # Inner doc comments SHOULD be attached to the document node
    assert len(data._ast_node.inner_doc_comments) == 2
    assert data._ast_node.inner_doc_comments[0].text == "This is a document comment"
    assert data._ast_node.inner_doc_comments[1].text == "Another document comment"


def test_document_comment_whitespace():
    """Test loading a string with ONLY inner doc comments and no nodes"""
    # Important: Use a raw string with no indentation before the //! comments
    ftml_content = r"""    
        //! This is a document comment
//! Another document comment


"""
    data = load(ftml_content)

    # Log the full AST structure
    ast = data._ast_node
    log_ast(ast, "Document With Only Inner Doc Comments AST")

    # Verify document loads without error
    assert data == {}

    # Inner doc comments SHOULD be attached to the document node
    assert len(data._ast_node.inner_doc_comments) == 2
    assert data._ast_node.inner_doc_comments[0].text == "This is a document comment"
    assert data._ast_node.inner_doc_comments[1].text == "Another document comment"
