"""
Pytest configuration and shared fixtures for RuleBox tests.
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import rulebox
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their names."""
    for item in items:
        # Mark tests that might be slow
        if "vector" in item.name and "long" in item.name:
            item.add_marker(pytest.mark.slow)

        # Mark integration tests
        if "integration" in item.name or item.name.startswith("test_integration"):
            item.add_marker(pytest.mark.integration)
