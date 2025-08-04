"""
Integration tests for RuleBox Python bindings.
"""

import json
import tempfile
import os
import pytest
from rulebox import RuleBox


class TestIntegration:
    """Integration tests that test real-world usage scenarios."""

    def test_full_workflow(self):
        """Test a complete workflow from file creation to labeling parliamentary motions."""
        # Create a comprehensive ruleset for parliamentary motion categorization
        rules = [
            {
                "label": "economic_policy",
                "rule": {
                    "or_patterns": [
                        {"pattern": "budget|taxation|fiscal", "flags": ["i"]},
                        {"pattern": "economic|finance|treasury", "flags": ["i"]},
                        {
                            "pattern": "spending|expenditure|revenue|funding",
                            "flags": ["i"],
                        },
                        {"pattern": "£[0-9,]+|\\$[0-9,]+", "flags": []},
                    ]
                },
            },
            {
                "label": "healthcare",
                "rule": {
                    "and_patterns": [
                        {"pattern": "health|medical|nhs|hospital", "flags": ["i"]},
                        {"pattern": "service|care|treatment|funding", "flags": ["i"]},
                    ]
                },
            },
            {
                "label": "education",
                "rule": {
                    "or_patterns": [
                        {
                            "pattern": "education|school|university|college",
                            "flags": ["i"],
                        },
                        {"pattern": "student|teacher|curriculum", "flags": ["i"]},
                        {"pattern": "learning|academic", "flags": ["i"]},
                    ],
                    "not_patterns": [
                        {"pattern": "adult education.*prison", "flags": ["i"]}
                    ],
                },
            },
            {
                "label": "urgent_motion",
                "rule": {
                    "or_patterns": [
                        {"pattern": "urgent|emergency|immediate", "flags": ["i"]},
                        {"pattern": "crisis|critical", "flags": ["i"]},
                        {"pattern": "without delay", "flags": ["i"]},
                    ]
                },
            },
        ]

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(rules, f, indent=2)
            rules_file = f.name

        try:
            # Load the RuleBox
            rulebox = RuleBox.from_path(rules_file)

            # Test various parliamentary motion scenarios
            test_cases = [
                {
                    "text": "URGENT motion to address the economic crisis with immediate £500 million healthcare funding",
                    "expected_labels": {
                        "urgent_motion",
                        "economic_policy",
                        "healthcare",
                    },
                },
                {
                    "text": "Motion to increase NHS funding for medical care services and hospital treatment",
                    "expected_labels": {"healthcare", "economic_policy"},
                },
                {
                    "text": "Educational reform motion for university student funding and teacher training",
                    "expected_labels": {"education", "economic_policy"},
                },
                {
                    "text": "Motion regarding adult education programs in prison rehabilitation",
                    "expected_labels": set(),  # Should not match education due to not_pattern
                },
                {
                    "text": "Motion to establish parliamentary committees for constitutional review",
                    "expected_labels": set(),
                },
            ]

            # Test individual labeling
            for i, case in enumerate(test_cases):
                labels = set(rulebox.assign_labels(case["text"]))
                assert labels == case["expected_labels"], (
                    f"Case {i + 1} failed: expected {case['expected_labels']}, got {labels}"
                )

            # Test batch labeling
            texts = [case["text"] for case in test_cases]
            all_labels = rulebox.assign_labels_vector(texts)

            for i, (case, labels) in enumerate(zip(test_cases, all_labels)):
                labels_set = set(labels)
                assert labels_set == case["expected_labels"], (
                    f"Batch case {i + 1} failed: expected {case['expected_labels']}, got {labels_set}"
                )

        finally:
            os.unlink(rules_file)

    def test_parliamentary_motion_classification_system(self):
        """Test a realistic parliamentary motion classification system."""
        rules = [
            {
                "label": "constitutional",
                "rule": {
                    "or_patterns": [
                        {"pattern": "constitution|constitutional", "flags": ["i"]},
                        {"pattern": "amendment|bill of rights", "flags": ["i"]},
                        {"pattern": "sovereignty|devolution", "flags": ["i"]},
                        {"pattern": "electoral reform", "flags": ["i"]},
                    ]
                },
            },
            {
                "label": "foreign_affairs",
                "rule": {
                    "and_patterns": [
                        {"pattern": "foreign|international|diplomatic", "flags": ["i"]},
                        {"pattern": "policy|relations|affairs|treaty", "flags": ["i"]},
                    ]
                },
            },
            {
                "label": "social_policy",
                "rule": {
                    "or_patterns": [
                        {"pattern": "welfare|benefits|housing", "flags": ["i"]},
                        {"pattern": "social care|childcare", "flags": ["i"]},
                        {"pattern": "disability|pension", "flags": ["i"]},
                        {"pattern": "family support", "flags": ["i"]},
                    ]
                },
            },
            {
                "label": "environmental",
                "rule": {
                    "or_patterns": [
                        {"pattern": "environment|climate|carbon", "flags": ["i"]},
                        {"pattern": "renewable energy|green", "flags": ["i"]},
                        {"pattern": "pollution|emissions", "flags": ["i"]},
                        {"pattern": "sustainability|conservation", "flags": ["i"]},
                    ],
                    "not_patterns": [
                        {"pattern": "business environment", "flags": ["i"]},
                        {"pattern": "work environment", "flags": ["i"]},
                    ],
                },
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(rules, f, indent=2)
            rules_file = f.name

        try:
            rulebox = RuleBox.from_path(rules_file)

            motions = [
                "Motion to amend the constitution regarding electoral reform and voting rights",
                "Motion on international foreign policy relations with European Union treaty obligations",
                "Motion to expand social care benefits and disability pension support",
                "Motion addressing climate change through renewable energy conservation initiatives",
                "Motion regarding improving business environment regulations in the work environment",  # Should not be environmental due to not_patterns
            ]

            expected_results = [
                ["constitutional"],
                ["foreign_affairs"],
                ["social_policy"],
                ["environmental"],
                [],  # environmental pattern excluded due to "business environment" and "work environment"
            ]

            all_labels = rulebox.assign_labels_vector(motions)

            for i, (motion, labels, expected) in enumerate(
                zip(motions, all_labels, expected_results)
            ):
                # Sort labels for comparison since order doesn't matter
                labels_sorted = sorted(labels)
                expected_sorted = sorted(expected)
                assert labels_sorted == expected_sorted, (
                    f"Motion {i + 1} failed:\nText: {motion}\nExpected: {expected_sorted}\nGot: {labels_sorted}"
                )

        finally:
            os.unlink(rules_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
