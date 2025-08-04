"""
Tests for the RuleBox Python bindings.
"""

import json
import tempfile
import os
import pytest
from rulebox import RuleBox


@pytest.fixture
def simple_rules_file():
    """Create a temporary rules file with simple test rules."""
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


@pytest.fixture
def complex_rules_file():
    """Create a temporary rules file with more complex rules."""
    rules = [
        {
            "label": "urgent",
            "rule": {
                "and_patterns": [
                    {"pattern": "urgent", "flags": ["i"]},
                    {"pattern": "asap|immediately|now", "flags": ["i"]},
                ]
            },
        },
        {
            "label": "polite",
            "rule": {
                "or_patterns": [
                    {"pattern": "please", "flags": ["i"]},
                    {"pattern": "thank you", "flags": ["i"]},
                    {"pattern": "thanks", "flags": ["i"]},
                ]
            },
        },
        {
            "label": "not_spam",
            "rule": {
                "or_patterns": [{"pattern": "legitimate"}],
                "not_patterns": [
                    {"pattern": "click here", "flags": ["i"]},
                    {"pattern": "free money", "flags": ["i"]},
                ],
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


class TestRuleBoxBasic:
    """Test basic RuleBox functionality."""

    def test_from_path_success(self, simple_rules_file):
        """Test successful loading from a valid rules file."""
        rulebox = RuleBox.from_path(simple_rules_file)
        assert isinstance(rulebox, RuleBox)

    def test_from_path_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        with pytest.raises(Exception) as exc_info:
            RuleBox.from_path("/nonexistent/path/rules.json")
        assert "Failed to load RuleBox" in str(exc_info.value)

    def test_from_path_invalid_json(self):
        """Test error handling for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            invalid_file = f.name

        try:
            with pytest.raises(Exception) as exc_info:
                RuleBox.from_path(invalid_file)
            assert "Failed to load RuleBox" in str(exc_info.value)
        finally:
            os.unlink(invalid_file)


class TestAssignLabels:
    """Test the assign_labels method."""

    def test_assign_labels_single_match(self, simple_rules_file):
        """Test assigning labels to text with a single match."""
        rulebox = RuleBox.from_path(simple_rules_file)

        labels = rulebox.assign_labels("Hello world")
        assert "greeting" in labels
        assert len(labels) == 1

    def test_assign_labels_multiple_matches(self, simple_rules_file):
        """Test assigning labels to text with multiple matches."""
        rulebox = RuleBox.from_path(simple_rules_file)

        labels = rulebox.assign_labels(
            "Hello! How are you? Contact me at test@example.com"
        )
        assert "greeting" in labels
        assert "question" in labels
        assert "email" in labels
        assert len(labels) == 3

    def test_assign_labels_no_match(self, simple_rules_file):
        """Test assigning labels to text with no matches."""
        rulebox = RuleBox.from_path(simple_rules_file)

        labels = rulebox.assign_labels("This is plain text with no matches.")
        assert len(labels) == 0

    def test_assign_labels_case_insensitive(self, simple_rules_file):
        """Test case insensitive matching."""
        rulebox = RuleBox.from_path(simple_rules_file)

        labels = rulebox.assign_labels("HELLO WORLD")
        assert "greeting" in labels

        labels = rulebox.assign_labels("hi there")
        assert "greeting" in labels

        labels = rulebox.assign_labels("HEY BUDDY")
        assert "greeting" in labels

    def test_assign_labels_word_boundaries(self, simple_rules_file):
        """Test that word boundaries work correctly."""
        rulebox = RuleBox.from_path(simple_rules_file)

        # Should match
        labels = rulebox.assign_labels("Hi there")
        assert "greeting" in labels

        # Should NOT match (hi is part of "This")
        labels = rulebox.assign_labels("This is a test")
        assert "greeting" not in labels

    def test_assign_labels_returns_list(self, simple_rules_file):
        """Test that assign_labels returns a list."""
        rulebox = RuleBox.from_path(simple_rules_file)

        labels = rulebox.assign_labels("Hello world")
        assert isinstance(labels, list)
        assert all(isinstance(label, str) for label in labels)


class TestAssignLabelsVector:
    """Test the assign_labels_vector method."""

    def test_assign_labels_vector_basic(self, simple_rules_file):
        """Test basic vector labeling functionality."""
        rulebox = RuleBox.from_path(simple_rules_file)

        texts = [
            "Hello world",
            "What's your email?",
            "Contact me at test@example.com",
            "Plain text",
        ]

        all_labels = rulebox.assign_labels_vector(texts)

        assert len(all_labels) == 4
        assert isinstance(all_labels, list)
        assert all(isinstance(labels, list) for labels in all_labels)

        # Check specific results
        assert "greeting" in all_labels[0]
        assert "question" in all_labels[1]
        assert "email" in all_labels[2]
        assert len(all_labels[3]) == 0

    def test_assign_labels_vector_empty_input(self, simple_rules_file):
        """Test vector labeling with empty input."""
        rulebox = RuleBox.from_path(simple_rules_file)

        all_labels = rulebox.assign_labels_vector([])
        assert all_labels == []

    def test_assign_labels_vector_single_text(self, simple_rules_file):
        """Test vector labeling with single text."""
        rulebox = RuleBox.from_path(simple_rules_file)

        all_labels = rulebox.assign_labels_vector(["Hello world"])
        assert len(all_labels) == 1
        assert "greeting" in all_labels[0]


class TestComplexRules:
    """Test more complex rule patterns."""

    def test_and_patterns(self, complex_rules_file):
        """Test AND pattern matching."""
        rulebox = RuleBox.from_path(complex_rules_file)

        # Should match (has both "urgent" and "asap")
        labels = rulebox.assign_labels("This is urgent, please do it ASAP!")
        assert "urgent" in labels

        # Should NOT match (has "urgent" but not the second pattern)
        labels = rulebox.assign_labels("This is urgent but not time-sensitive")
        assert "urgent" not in labels

    def test_not_patterns(self, complex_rules_file):
        """Test NOT pattern matching."""
        rulebox = RuleBox.from_path(complex_rules_file)

        # Should match (has "legitimate" and no excluded patterns)
        labels = rulebox.assign_labels("This is a legitimate request")
        assert "not_spam" in labels

        # Should NOT match (has excluded pattern)
        labels = rulebox.assign_labels(
            "This is legitimate but click here for free money"
        )
        assert "not_spam" not in labels

    def test_mixed_patterns(self, complex_rules_file):
        """Test text that matches multiple complex rules."""
        rulebox = RuleBox.from_path(complex_rules_file)

        text = "Please make this urgent change immediately, thanks!"
        labels = rulebox.assign_labels(text)

        assert "urgent" in labels  # has "urgent" and "immediately"
        assert "polite" in labels  # has "please" and "thanks"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_text(self, simple_rules_file):
        """Test labeling empty text."""
        rulebox = RuleBox.from_path(simple_rules_file)

        labels = rulebox.assign_labels("")
        assert len(labels) == 0

    def test_unicode_text(self, simple_rules_file):
        """Test labeling text with unicode characters."""
        rulebox = RuleBox.from_path(simple_rules_file)

        labels = rulebox.assign_labels("Hello 世界! Email: test@例え.com")
        assert "greeting" in labels
        # Note: The email pattern might not match unicode domains

    def test_very_long_text(self, simple_rules_file):
        """Test labeling very long text."""
        rulebox = RuleBox.from_path(simple_rules_file)

        long_text = "Hello " + "word " * 1000 + "test@example.com"
        labels = rulebox.assign_labels(long_text)
        assert "greeting" in labels
        assert "email" in labels

    def test_special_characters(self, simple_rules_file):
        """Test text with special regex characters."""
        rulebox = RuleBox.from_path(simple_rules_file)

        # These should not cause regex errors
        labels = rulebox.assign_labels("Hello [world] (test) {hello} ^start$ .any*")
        assert "greeting" in labels


if __name__ == "__main__":
    pytest.main([__file__])
