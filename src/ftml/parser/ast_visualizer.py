"""
Helper module for visualizing AST structures.

Use this to debug FTML parsing by seeing the entire AST structure.
"""


def visualize_ast(node, indent=0):
    """
    Recursively visualize the AST structure with all comments.

    Args:
        node: The AST node to visualize
        indent: Current indentation level

    Returns:
        A string representation of the AST
    """
    indent_str = "  " * indent
    output = []

    if hasattr(node, "__class__"):
        node_type = node.__class__.__name__
    else:
        node_type = type(node).__name__

    # DocumentNode
    if node_type == "DocumentNode":
        output.append(f"{indent_str}DocumentNode:")

        # Inner doc comments (//!)
        if hasattr(node, "inner_doc_comments") and node.inner_doc_comments:
            output.append(f"{indent_str}  InnerDocComments:")
            for i, comment in enumerate(node.inner_doc_comments):
                output.append(f'{indent_str}    {i}: "{comment.text}" (line {comment.line})')

        # Legacy doc comments (////)
        # if hasattr(node, "doc_comments") and node.doc_comments:
        #     output.append(f"{indent_str}  LegacyDocComments:")
        #     for i, comment in enumerate(node.doc_comments):
        #         output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

        # Leading comments
        if hasattr(node, "leading_comments") and node.leading_comments:
            output.append(f"{indent_str}  LeadingComments:")
            for i, comment in enumerate(node.leading_comments):
                output.append(f'{indent_str}    {i}: "{comment.text}" (line {comment.line})')

        # Items
        if hasattr(node, "items"):
            output.append(f"{indent_str}  Items:")
            for key, value in node.items.items():
                output.append(f"{indent_str}    {key}:")
                output.extend(visualize_ast(value, indent + 3))

        # Trailing comments
        # if hasattr(node, "trailing_comments") and node.trailing_comments:
        #     output.append(f"{indent_str}  TrailingComments:")
        #     for i, comment in enumerate(node.trailing_comments):
        #         output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

    # KeyValueNode
    elif node_type == "KeyValueNode":
        output.append(f"{indent_str}KeyValueNode: {node.key} (line {node.line})")

        # Outer doc comments (///)
        if hasattr(node, "outer_doc_comments") and node.outer_doc_comments:
            output.append(f"{indent_str}  OuterDocComments:")
            for i, comment in enumerate(node.outer_doc_comments):
                output.append(f'{indent_str}    {i}: "{comment.text}" (line {comment.line})')

        # Leading comments
        if hasattr(node, "leading_comments") and node.leading_comments:
            output.append(f"{indent_str}  LeadingComments:")
            for i, comment in enumerate(node.leading_comments):
                output.append(f'{indent_str}    {i}: "{comment.text}" (line {comment.line})')

        # Value
        if hasattr(node, "value"):
            output.append(f"{indent_str}  Value:")
            output.extend(visualize_ast(node.value, indent + 2))

        # Inline comment
        if hasattr(node, "inline_comment") and node.inline_comment:
            output.append(
                f'{indent_str}  InlineComment: "{node.inline_comment.text}" (line {node.inline_comment.line})'
            )

        # Trailing comments
        # if hasattr(node, "trailing_comments") and node.trailing_comments:
        #     output.append(f"{indent_str}  TrailingComments:")
        #     for i, comment in enumerate(node.trailing_comments):
        #         output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

    # ListNode
    elif node_type == "ListNode":
        output.append(f"{indent_str}ListNode: with {len(node.elements) if hasattr(node, 'elements') else 0} elements")

        # Inner doc comments (//!)
        if hasattr(node, "inner_doc_comments") and node.inner_doc_comments:
            output.append(f"{indent_str}  InnerDocComments:")
            for i, comment in enumerate(node.inner_doc_comments):
                output.append(f'{indent_str}    {i}: "{comment.text}" (line {comment.line})')

        # Outer doc comments (///)
        if hasattr(node, "outer_doc_comments") and node.outer_doc_comments:
            output.append(f"{indent_str}  OuterDocComments:")
            for i, comment in enumerate(node.outer_doc_comments):
                output.append(f'{indent_str}    {i}: "{comment.text}" (line {comment.line})')

        # Legacy doc comments (////)
        # if hasattr(node, "doc_comments") and node.doc_comments:
        #     output.append(f"{indent_str}  LegacyDocComments:")
        #     for i, comment in enumerate(node.doc_comments):
        #         output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

        # Leading comments
        if hasattr(node, "leading_comments") and node.leading_comments:
            output.append(f"{indent_str}  LeadingComments:")
            for i, comment in enumerate(node.leading_comments):
                output.append(f'{indent_str}    {i}: "{comment.text}" (line {comment.line})')

        # Elements
        if hasattr(node, "elements") and node.elements:
            output.append(f"{indent_str}  Elements:")
            for i, elem in enumerate(node.elements):
                output.append(f"{indent_str}    Element {i}:")
                output.extend(visualize_ast(elem, indent + 3))

        # Inline comment
        if hasattr(node, "inline_comment") and node.inline_comment:
            output.append(
                f'{indent_str}  InlineComment: "{node.inline_comment.text}" (line {node.inline_comment.line})'
            )

        # Inline comment on end bracket
        if hasattr(node, "inline_comment_end") and node.inline_comment_end:
            output.append(
                f'{indent_str}  InlineCommentEnd: "{node.inline_comment_end.text}" '
                f"(line {node.inline_comment_end.line})"
            )

        # Trailing comments
        # if hasattr(node, "trailing_comments") and node.trailing_comments:
        #     output.append(f"{indent_str}  TrailingComments:")
        #     for i, comment in enumerate(node.trailing_comments):
        #         output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

    # ObjectNode
    elif node_type == "ObjectNode":
        output.append(f"{indent_str}ObjectNode: with {len(node.items) if hasattr(node, 'items') else 0} items")

        # Inner doc comments (//!)
        if hasattr(node, "inner_doc_comments") and node.inner_doc_comments:
            output.append(f"{indent_str}  InnerDocComments:")
            for i, comment in enumerate(node.inner_doc_comments):
                output.append(f'{indent_str}    {i}: "{comment.text}" (line {comment.line})')

        # Outer doc comments (///)
        if hasattr(node, "outer_doc_comments") and node.outer_doc_comments:
            output.append(f"{indent_str}  OuterDocComments:")
            for i, comment in enumerate(node.outer_doc_comments):
                output.append(f'{indent_str}    {i}: "{comment.text}" (line {comment.line})')

        # Legacy doc comments (////)
        # if hasattr(node, "doc_comments") and node.doc_comments:
        #     output.append(f"{indent_str}  LegacyDocComments:")
        #     for i, comment in enumerate(node.doc_comments):
        #         output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

        # Leading comments
        if hasattr(node, "leading_comments") and node.leading_comments:
            output.append(f"{indent_str}  LeadingComments:")
            for i, comment in enumerate(node.leading_comments):
                output.append(f'{indent_str}    {i}: "{comment.text}" (line {comment.line})')

        # Items
        if hasattr(node, "items") and node.items:
            output.append(f"{indent_str}  Key Items:")
            for key, item in node.items.items():
                output.append(f"{indent_str}    Key: {key}:")
                output.extend(visualize_ast(item, indent + 3))

        # Inline comment
        if hasattr(node, "inline_comment") and node.inline_comment:
            output.append(
                f'{indent_str}  InlineComment: "{node.inline_comment.text}" (line {node.inline_comment.line})'
            )

        # Trailing comments
        # if hasattr(node, "trailing_comments") and node.trailing_comments:
        #     output.append(f"{indent_str}  TrailingComments:")
        #     for i, comment in enumerate(node.trailing_comments):
        #         output.append(f"{indent_str}    {i}: \"{comment.text}\" (line {comment.line})")

    # ScalarNode
    elif node_type == "ScalarNode":
        value_type = type(node.value).__name__ if node.value is not None else "None"
        output.append(f"{indent_str}ScalarNode: {repr(node.value)} ({value_type}, line {node.line})")

        # Outer doc comments (///)
        if hasattr(node, "outer_doc_comments") and node.outer_doc_comments:
            output.append(f"{indent_str}  OuterDocComments:")
            for i, comment in enumerate(node.outer_doc_comments):
                output.append(f'{indent_str}    {i}: "{comment.text}" (line {comment.line})')

        # Leading comments
        if hasattr(node, "leading_comments") and node.leading_comments:
            output.append(f"{indent_str}  LeadingComments:")
            for i, comment in enumerate(node.leading_comments):
                output.append(f'{indent_str}    {i}: "{comment.text}" (line {comment.line})')

        # Inline comment
        if hasattr(node, "inline_comment") and node.inline_comment:
            output.append(
                f'{indent_str}  InlineComment: "{node.inline_comment.text}" (line {node.inline_comment.line})'
            )

    # Other node types
    else:
        output.append(f"{indent_str}{node_type}: {node}")

    return output


def print_ast(node):
    """Print the AST in a readable format"""
    print("\n".join(visualize_ast(node)))
