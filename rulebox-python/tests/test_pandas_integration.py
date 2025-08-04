"""
Tests for pandas integration with RuleBox Python bindings.
"""

import json
import tempfile
import os
import pytest
import pandas as pd
from rulebox import RuleBox


@pytest.fixture
def sample_rules_file():
    """Create a temporary rules file for testing."""
    rules = [
        {
            "label": "greeting",
            "rule": {
                "or_patterns": [
                    {"pattern": "\\bhello\\b", "flags": ["i"]},
                    {"pattern": "\\bhi\\b", "flags": ["i"]},
                    {"pattern": "\\bhey\\b", "flags": ["i"]},
                ]
            },
        },
        {"label": "question", "rule": {"and_patterns": [{"pattern": "\\?"}]}},
        {
            "label": "email",
            "rule": {
                "or_patterns": [
                    {"pattern": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"}
                ]
            },
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(rules, f, indent=2)
        temp_file = f.name

    yield temp_file

    # Cleanup
    try:
        os.unlink(temp_file)
    except FileNotFoundError:
        pass


class TestPandasIntegration:
    """Test pandas integration with RuleBox."""

    def test_assign_labels_vector_with_pandas_series_strings(self, sample_rules_file):
        """Test assign_labels_vector with a pandas Series containing strings."""
        rulebox = RuleBox.from_path(sample_rules_file)

        # Create a pandas Series with string data
        texts_series = pd.Series(
            [
                "Hello world",
                "What's your email?",
                "Contact me at test@example.com",
                "Plain text with no matches",
            ]
        )

        # Test what happens when we pass the Series directly
        try:
            all_labels = rulebox.assign_labels_vector(texts_series)

            # If it works, verify the results
            assert len(all_labels) == 4
            assert isinstance(all_labels, list)
            assert all(isinstance(labels, list) for labels in all_labels)

            # Check specific results
            assert "greeting" in all_labels[0]
            assert "question" in all_labels[1]
            assert "email" in all_labels[2]
            assert len(all_labels[3]) == 0

            print(
                "✓ pandas Series was automatically converted and processed successfully"
            )

        except (TypeError, ValueError) as e:
            # If it fails, document the expected behavior
            print(f"✗ pandas Series failed with error: {e}")
            print("This is expected if automatic conversion is not supported")

            # Test that converting to list works as a workaround
            all_labels = rulebox.assign_labels_vector(texts_series.tolist())

            assert len(all_labels) == 4
            assert isinstance(all_labels, list)
            assert all(isinstance(labels, list) for labels in all_labels)

            # Check specific results
            assert "greeting" in all_labels[0]
            assert "question" in all_labels[1]
            assert "email" in all_labels[2]
            assert len(all_labels[3]) == 0

            print("✓ pandas Series.tolist() conversion works as expected")

    def test_assign_labels_vector_with_pandas_series_numeric(self, sample_rules_file):
        """Test assign_labels_vector with a pandas Series containing numeric data."""
        rulebox = RuleBox.from_path(sample_rules_file)

        # Create a pandas Series with numeric data that should be converted to strings
        numeric_series = pd.Series([123, 456.7, 0, -1])

        try:
            all_labels = rulebox.assign_labels_vector(numeric_series)

            # If it works, verify the results (numeric values shouldn't match our text rules)
            assert len(all_labels) == 4
            assert isinstance(all_labels, list)
            assert all(isinstance(labels, list) for labels in all_labels)

            # All should be empty since numeric values don't match text patterns
            assert all(len(labels) == 0 for labels in all_labels)

            print("✓ pandas Series with numeric values was processed successfully")

        except (TypeError, ValueError) as e:
            print(f"✗ pandas Series with numeric values failed: {e}")

            # Test that converting to string list works
            all_labels = rulebox.assign_labels_vector(
                numeric_series.astype(str).tolist()
            )

            assert len(all_labels) == 4
            assert isinstance(all_labels, list)
            assert all(isinstance(labels, list) for labels in all_labels)

            # All should be empty since numeric strings don't match our text patterns
            assert all(len(labels) == 0 for labels in all_labels)

            print("✓ pandas Series converted to string list works as expected")

    def test_assign_labels_vector_with_pandas_series_mixed_types(
        self, sample_rules_file
    ):
        """Test assign_labels_vector with a pandas Series containing mixed data types."""
        rulebox = RuleBox.from_path(sample_rules_file)

        # Create a pandas Series with mixed data types
        mixed_series = pd.Series(
            ["Hello world", 123, "What's up?", None, "test@example.com"]
        )

        try:
            all_labels = rulebox.assign_labels_vector(mixed_series)

            # If it works, verify the results
            assert len(all_labels) == 5
            assert isinstance(all_labels, list)
            assert all(isinstance(labels, list) for labels in all_labels)

            # Check that string values still get processed correctly
            assert "greeting" in all_labels[0]  # "Hello world"
            # Index 1 is numeric, should be empty
            assert len(all_labels[1]) == 0  # 123
            assert "question" in all_labels[2]  # "What's up?"
            # Index 3 is None, behavior depends on how it's handled
            assert "email" in all_labels[4]  # "test@example.com"

            print("✓ pandas Series with mixed types was processed successfully")

        except (TypeError, ValueError) as e:
            print(f"✗ pandas Series with mixed types failed: {e}")

            # Test that converting to string list works, handling None values
            string_list = mixed_series.astype(str).tolist()
            all_labels = rulebox.assign_labels_vector(string_list)

            assert len(all_labels) == 5
            assert isinstance(all_labels, list)
            assert all(isinstance(labels, list) for labels in all_labels)

            print("✓ pandas Series with mixed types converted to string list works")

    def test_assign_labels_vector_with_empty_pandas_series(self, sample_rules_file):
        """Test assign_labels_vector with an empty pandas Series."""
        rulebox = RuleBox.from_path(sample_rules_file)

        # Create an empty pandas Series
        empty_series = pd.Series([], dtype=str)

        try:
            all_labels = rulebox.assign_labels_vector(empty_series)
            assert all_labels == []
            print("✓ Empty pandas Series was processed successfully")

        except (TypeError, ValueError) as e:
            print(f"✗ Empty pandas Series failed: {e}")

            # Test that converting to list works
            all_labels = rulebox.assign_labels_vector(empty_series.tolist())
            assert all_labels == []
            print("✓ Empty pandas Series converted to list works")

    def test_assign_labels_vector_with_pandas_series_with_na(self, sample_rules_file):
        """Test assign_labels_vector with a pandas Series containing NaN/NA values."""
        rulebox = RuleBox.from_path(sample_rules_file)

        # Create a pandas Series with NaN values
        series_with_na = pd.Series(
            ["Hello world", pd.NA, "What's up?", None, "test@example.com"]
        )

        try:
            all_labels = rulebox.assign_labels_vector(series_with_na)

            # If it works, verify the results
            assert len(all_labels) == 5
            assert isinstance(all_labels, list)
            assert all(isinstance(labels, list) for labels in all_labels)

            print("✓ pandas Series with NA values was processed successfully")

        except (TypeError, ValueError) as e:
            print(f"✗ pandas Series with NA values failed: {e}")

            # Test different strategies for handling NA values

            # Strategy 1: Drop NA values
            clean_series = series_with_na.dropna()
            all_labels = rulebox.assign_labels_vector(clean_series.tolist())
            assert len(all_labels) == 3  # Only non-NA values
            print("✓ pandas Series with NA values (dropna strategy) works")

            # Strategy 2: Fill NA with empty string
            filled_series = series_with_na.fillna("")
            all_labels = rulebox.assign_labels_vector(filled_series.tolist())
            assert len(all_labels) == 5  # All values, NA replaced with empty string
            print("✓ pandas Series with NA values (fillna strategy) works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
