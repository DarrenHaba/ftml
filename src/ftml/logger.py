"""
FTML Logger Module

Provides logging functionality for the FTML library.
"""

import logging
import os
import sys

# Create a logger
logger = logging.getLogger("ftml")

# Default log level - can be overridden by environment variable
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL = os.environ.get("FTML_LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()

# Configure the logger
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(levelname)s [%(name)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Set the log level
try:
    logger.setLevel(getattr(logging, LOG_LEVEL))
    logger.debug(f"Logger initialized with level {LOG_LEVEL}")
except AttributeError:
    logger.setLevel(logging.INFO)
    logger.warning(f"Invalid log level '{LOG_LEVEL}', using 'INFO'")


# Helper functions for common logging patterns
def debug_ast(node, prefix=""):
    """Log an AST node with pretty formatting for debugging."""
    if logger.level > logging.DEBUG:
        return  # Skip expensive formatting if debug is not enabled

    node_type = type(node).__name__

    if hasattr(node, "items"):  # ObjectNode or DocumentNode
        items_count = len(node.items) if hasattr(node, "items") else 0
        logger.debug(f"{prefix}AST {node_type}: {items_count} items")

        # Log comments if present
        if hasattr(node, "leading_comments") and node.leading_comments:
            logger.debug(f"{prefix}  Leading comments: {len(node.leading_comments)}")
            for i, comment in enumerate(node.leading_comments):
                logger.debug(f"{prefix}    {i}: {comment.text}")

        if hasattr(node, "inline_comment") and node.inline_comment:
            logger.debug(f"{prefix}  Inline comment: {node.inline_comment.text}")

        # if hasattr(node, 'trailing_comments') and node.trailing_comments:
        #     logger.debug(f"{prefix}  Trailing comments: {len(node.trailing_comments)}")
        #     for i, comment in enumerate(node.trailing_comments):
        #         logger.debug(f"{prefix}    {i}: {comment.text}")

        # Log items if available
        if hasattr(node, "items") and node.items:
            for key, item in node.items.items():
                logger.debug(f"{prefix}  Key: {key}")
                debug_ast(item, prefix + "    ")

    elif hasattr(node, "elements"):  # ListNode
        elements_str = f"{len(node.elements)} elements"
        logger.debug(f"{prefix}AST {node_type}: {elements_str}")

        # Log comments
        if hasattr(node, "leading_comments") and node.leading_comments:
            logger.debug(f"{prefix}  Leading comments: {len(node.leading_comments)}")
        if hasattr(node, "inline_comment") and node.inline_comment:
            logger.debug(f"{prefix}  Inline comment: {node.inline_comment.text}")
        # if hasattr(node, 'trailing_comments') and node.trailing_comments:
        #     logger.debug(f"{prefix}  Trailing comments: {len(node.trailing_comments)}")

    elif hasattr(node, "value"):  # ScalarNode
        value_type = type(node.value).__name__
        value_str = str(node.value)
        if len(value_str) > 30:
            value_str = value_str[:27] + "..."
        logger.debug(f"{prefix}AST {node_type}: {value_type}({value_str!r})")

        # Log comments
        if hasattr(node, "leading_comments") and node.leading_comments:
            logger.debug(f"{prefix}  Leading comments: {len(node.leading_comments)}")
        if hasattr(node, "inline_comment") and node.inline_comment:
            logger.debug(f"{prefix}  Inline comment: {node.inline_comment.text}")
        # if hasattr(node, 'trailing_comments') and node.trailing_comments:
        #     logger.debug(f"{prefix}  Trailing comments: {len(node.trailing_comments)}")

    elif hasattr(node, "key") and hasattr(node, "value"):  # KeyValueNode
        logger.debug(f"{prefix}AST {node_type}: {node.key}")

        # Log comments
        if hasattr(node, "leading_comments") and node.leading_comments:
            logger.debug(f"{prefix}  Leading comments: {len(node.leading_comments)}")
            for i, comment in enumerate(node.leading_comments):
                logger.debug(f"{prefix}    {i}: {comment.text}")

        if hasattr(node, "inline_comment") and node.inline_comment:
            logger.debug(f"{prefix}  Inline comment: {node.inline_comment.text}")

        # if hasattr(node, 'trailing_comments') and node.trailing_comments:
        #     logger.debug(f"{prefix}  Trailing comments: {len(node.trailing_comments)}")
        #     for i, comment in enumerate(node.trailing_comments):
        #         logger.debug(f"{prefix}    {i}: {comment.text}")

        # Log value
        if hasattr(node, "value"):
            debug_ast(node.value, prefix + "  ")
    else:
        logger.debug(f"{prefix}AST {node_type}")


def debug_dict(data, prefix=""):
    """Log a dictionary with pretty formatting for debugging."""
    if logger.level > logging.DEBUG:
        return

    if isinstance(data, dict):
        keys_str = ", ".join(list(data.keys())[:3])
        if len(data) > 3:
            keys_str += f", ... ({len(data)} total)"
        logger.debug(f"{prefix}Dict: {keys_str}")

        # Check for comment attributes if it's an FTML dict
        if hasattr(data, "_ast_node"):
            if hasattr(data._ast_node, "leading_comments") and data._ast_node.leading_comments:
                logger.debug(f"{prefix}  Leading comments: {len(data._ast_node.leading_comments)}")
            if hasattr(data._ast_node, "inline_comment") and data._ast_node.inline_comment:
                logger.debug(f"{prefix}  Inline comment: {data._ast_node.inline_comment}")
            # if hasattr(data._ast_node, 'trailing_comments') and data._ast_node.trailing_comments:
            #     logger.debug(f"{prefix}  Trailing comments: {len(data._ast_node.trailing_comments)}")
    elif isinstance(data, list):
        logger.debug(f"{prefix}List: {len(data)} elements")

    else:
        value_str = str(data)
        if len(value_str) > 30:
            value_str = value_str[:27] + "..."
        logger.debug(f"{prefix}Value: {type(data).__name__}({value_str!r})")


def log_comment(comment, prefix=""):
    """Log a single comment."""
    if comment:
        logger.debug(f"{prefix}Comment: {comment.text} (line {comment.line}, col {comment.col})")


def log_tokens(tokens, prefix=""):
    """Log all tokens for debugging."""
    if logger.level > logging.DEBUG:
        return

    logger.debug(f"{prefix}Tokens: {len(tokens)} total")
    for i, token in enumerate(tokens):
        logger.debug(f"{prefix}  {i}: {token.type.name} {token.value!r} (line {token.line}, col {token.col})")


def log_parse_result(ast, prefix=""):
    """Log the result of parsing for debugging."""
    if logger.level > logging.DEBUG:
        return

    logger.debug(f"{prefix}Parse result:")
    debug_ast(ast, prefix + "  ")
