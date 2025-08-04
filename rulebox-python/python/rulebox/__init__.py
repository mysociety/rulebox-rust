"""
RuleBox - A regex-based text labeling system.

This module provides Python bindings for the RuleBox Rust library,
which allows for fast regex-based text classification using JSON rule definitions.
"""

from .rulebox import RuleBox

__all__ = ["RuleBox"]
__version__ = "0.1.0"
