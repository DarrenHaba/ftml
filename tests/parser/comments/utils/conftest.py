"""
Pytest configuration for FTML tests.

This adds helpful features for debugging FTML tests.
"""

# import pytest
# import logging
# import os
# from ftml.logger import logger
# from ftml.tests.helpers import log_ast
# 
# 
# def pytest_addoption(parser):
#     """Add command-line options for FTML testing."""
#     parser.addoption(
#         "--log-asts",
#         action="store_true",
#         default=False,
#         help="Log the full AST structure for all tests"
#     )
#     parser.addoption(
#         "--save-logs",
#         action="store_true",
#         default=False,
#         help="Save logs to a file for review"
#     )
# 
# 
# def pytest_configure(config):
#     """Configure pytest for FTML testing."""
#     # Set log level based on verbosity
#     if config.option.verbose > 1:
#         logger.setLevel(logging.DEBUG)
#     else:
#         logger.setLevel(logging.INFO)
# 
#     # Set up file logging if requested
#     if config.option.save_logs:
#         file_handler = logging.FileHandler('ftml_tests.log', mode='w')
#         formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] %(message)s')
#         file_handler.setFormatter(formatter)
#         logger.addHandler(file_handler)
# 
#     # Set environment variable to control AST logging
#     if config.option.log_asts:
#         os.environ["FTML_LOG_ASTS"] = "1"
#     else:
#         os.environ.pop("FTML_LOG_ASTS", None)
# 
# 
# @pytest.fixture
# def log_full_ast():
#     """
#     Fixture to log the full AST structure of a parsed document.
#     
#     Use this fixture in tests where you need to see the complete AST.
#     
#     Example:
#         def test_example(log_full_ast):
#             ast = load_with_comments("key = value")
#             log_full_ast(ast, "My test AST")
#     """
#     def _log_ast(ast, title="Test AST"):
#         """Log the AST structure."""
#         log_ast(ast, title)
# 
#     return _log_ast