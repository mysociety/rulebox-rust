"""
Type-annotated test to demonstrate type hints for RuleBox.
"""

import json
import tempfile
import os
from typing import List
from rulebox import RuleBox


def create_test_rules() -> str:
    """Create a temporary rules file and return its path."""
    rules = [
        {
            "label": "greeting",
            "rule": {
                "or_patterns": [
                    {"pattern": "\\bhello\\b", "flags": ["i"]},
                    {"pattern": "\\bhi\\b", "flags": ["i"]},
                ]
            },
        }
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(rules, f)
        return f.name


def demonstrate_typing() -> None:
    """Demonstrate the typed interface of RuleBox."""
    rules_file = create_test_rules()

    try:
        # Type hint shows this returns RuleBox
        rulebox: RuleBox = RuleBox.from_path(rules_file)

        # Type hint shows this returns List[str]
        single_labels: List[str] = rulebox.assign_labels("Hello world!")

        # Type hint shows this returns List[List[str]]
        texts: List[str] = ["Hello there", "Goodbye", "Hi everyone"]
        multiple_labels: List[List[str]] = rulebox.assign_labels_vector(texts)

        # Use the results
        print(f"Single text labels: {single_labels}")
        print(f"Multiple text labels: {multiple_labels}")

        # This would cause a type error if uncommented:
        # rulebox.assign_labels(123)  # mypy error: Argument 1 has incompatible type "int"; expected "str"

    finally:
        os.unlink(rules_file)


if __name__ == "__main__":
    demonstrate_typing()
