"""
Type stubs for the rulebox module.

This module provides Python bindings for the Rust-based RuleBox text labeling engine.
"""

from typing import List, Union
from pathlib import Path

class RuleBox:
    """
    A text labeling engine that applies regex-based rules to classify text.

    The RuleBox loads rule definitions from JSON files and can apply them to
    single texts or batches of texts for efficient processing.
    """

    @staticmethod
    def from_path(path: Union[str, Path]) -> "RuleBox":
        """
        Load a RuleBox from a JSON rules file.

        Args:
            path: Path to the JSON file containing rule definitions.
                  Can be a string path or pathlib.Path object.

        Returns:
            A new RuleBox instance with the loaded rules.

        Raises:
            Exception: If the file cannot be read or contains invalid JSON/rules.

        Example:
            >>> rulebox = RuleBox.from_path("rules.json")
            >>> labels = rulebox.assign_labels("Hello world!")
        """
        ...

    def assign_labels(self, text: str) -> List[str]:
        """
        Assign labels to a single text string.

        Args:
            text: The text to analyze and label.

        Returns:
            A list of labels that match the input text.
            Returns an empty list if no rules match.

        Example:
            >>> rulebox = RuleBox.from_path("rules.json")
            >>> labels = rulebox.assign_labels("Hello world!")
            >>> print(labels)  # ['greeting']
        """
        ...

    def assign_labels_vector(self, texts: List[str]) -> List[List[str]]:
        """
        Assign labels to multiple text strings efficiently.

        Args:
            texts: A list of text strings to analyze and label.

        Returns:
            A list of label lists, where each inner list contains
            the labels for the corresponding input text.

        Example:
            >>> rulebox = RuleBox.from_path("rules.json")
            >>> texts = ["Hello there", "Goodbye", "Hi everyone"]
            >>> labels = rulebox.assign_labels_vector(texts)
            >>> print(labels)  # [['greeting'], [], ['greeting']]
        """
        ...
