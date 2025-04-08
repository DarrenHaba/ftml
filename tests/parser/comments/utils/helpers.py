"""
Helper utilities for FTML testing.
"""

import logging
from ftml.logger import logger

def visualize_ast(node, indent=0):
    """
    Recursively visualize the AST structure with all comments.
    """
    indent_str = "  " * indent
    output = []
    node_type = node.__class__.__name__ if hasattr(node, "__class__") else type(node).__name__

    if node_type == "DocumentNode":
        output.append(f"{indent_str}DocumentNode:")

        if hasattr(node, "doc_comments") and node.doc_comments:
            output.append(f"{indent_str}  DocComments:")
            for i, comment in enumerate(node.doc_comments):
                output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

        if hasattr(node, "leading_comments") and node.leading_comments:
            output.append(f"{indent_str}  LeadingComments:")
            for i, comment in enumerate(node.leading_comments):
                output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

        if hasattr(node, "items"):
            output.append(f"{indent_str}  Items:")
            for key, value in node.items.items():
                output.append(f"{indent_str}    {key}:")
                output.extend(visualize_ast(value, indent + 3))

        if hasattr(node, "trailing_comments") and node.trailing_comments:
            output.append(f"{indent_str}  TrailingComments:")
            for i, comment in enumerate(node.trailing_comments):
                output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

    elif node_type == "KeyValueNode":
        output.append(f"{indent_str}KeyValueNode: {node.key} (line {node.line})")

        if hasattr(node, "leading_comments") and node.leading_comments:
            output.append(f"{indent_str}  LeadingComments:")
            for i, comment in enumerate(node.leading_comments):
                output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

        if hasattr(node, "value"):
            output.append(f"{indent_str}  Value:")
            output.extend(visualize_ast(node.value, indent + 2))

        if hasattr(node, "inline_comment") and node.inline_comment:
            output.append(f"{indent_str}  InlineComment: \"{node.inline_comment.text}\" (line {node.inline_comment.line})")

        if hasattr(node, "trailing_comments") and node.trailing_comments:
            output.append(f"{indent_str}  TrailingComments:")
            for i, comment in enumerate(node.trailing_comments):
                output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

    elif node_type == "ScalarNode":
        value_type = type(node.value).__name__ if node.value is not None else "None"
        output.append(f"{indent_str}ScalarNode: {repr(node.value)} ({value_type}, line {node.line})")

        # Add display of comments for scalar nodes
        if hasattr(node, "leading_comments") and node.leading_comments:
            output.append(f"{indent_str}  LeadingComments:")
            for i, comment in enumerate(node.leading_comments):
                output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

        if hasattr(node, "inline_comment") and node.inline_comment:
            output.append(f"{indent_str}  InlineComment: \"{node.inline_comment.text}\" (line {node.inline_comment.line})")

        if hasattr(node, "trailing_comments") and node.trailing_comments:
            output.append(f"{indent_str}  TrailingComments:")
            for i, comment in enumerate(node.trailing_comments):
                output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

    elif node_type == "ListNode":
        output.append(f"{indent_str}ListNode: with {len(node.elements)} elements")

        if hasattr(node, "leading_comments") and node.leading_comments:
            output.append(f"{indent_str}  LeadingComments:")
            for i, comment in enumerate(node.leading_comments):
                output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

        for index, element in enumerate(node.elements):
            output.append(f"{indent_str}  Element {index}:")
            output.extend(visualize_ast(element, indent + 2))

        if hasattr(node, "inline_comment") and node.inline_comment:
            output.append(f"{indent_str}  InlineComment: \"{node.inline_comment.text}\" (line {node.inline_comment.line})")

        if hasattr(node, "trailing_comments") and node.trailing_comments:
            output.append(f"{indent_str}  TrailingComments:")
            for i, comment in enumerate(node.trailing_comments):
                output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

    elif node_type == "ObjectNode":
        output.append(f"{indent_str}ObjectNode: with {len(node.items)} items")

        if hasattr(node, "leading_comments") and node.leading_comments:
            output.append(f"{indent_str}  LeadingComments:")
            for i, comment in enumerate(node.leading_comments):
                output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

        if hasattr(node, "items"):
            for key, value in node.items.items():
                output.append(f"{indent_str}  Key: {key}:")
                output.extend(visualize_ast(value, indent + 2))

        if hasattr(node, "inline_comment") and node.inline_comment:
            output.append(f"{indent_str}  InlineComment: \"{node.inline_comment.text}\" (line {node.inline_comment.line})")

        if hasattr(node, "trailing_comments") and node.trailing_comments:
            output.append(f"{indent_str}  TrailingComments:")
            for i, comment in enumerate(node.trailing_comments):
                output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

    else:
        output.append(f"{indent_str}{node_type}: {node}")

    return output


def log_ast(ast, title="AST Structure"):
    """Log the full AST structure for debugging"""
    logger.debug(f"\n--- {title} ---")
    for line in visualize_ast(ast):
        logger.debug(line)
    logger.debug("--- End AST ---")
