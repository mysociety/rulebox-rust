# RuleBox

A fast, flexible regex-based text labeling system with Python bindings.

RuleBox allows you to define complex rule-based text classification using JSON configuration files with regex patterns, boolean logic (AND, OR, NOT), and flags. The core engine is written in Rust for performance, with Python bindings for easy integration.

## Quick Start

```bash
# Set up development environment
script/setup

# Run tests
script/test

# Interactive development
script/console
```

## Installation

### From Source


## Usage

```python
from rulebox import RuleBox

# Load rules from a JSON file
rulebox = RuleBox.from_path("rules.json")

# Classify a single text
labels = rulebox.assign_labels("Hello! How are you?")
print(labels)  # ['greeting', 'question']

# Classify multiple texts
texts = ["Hello world", "Send help!", "user@example.com"]
all_labels = rulebox.assign_labels_vector(texts)
print(all_labels)  # [['greeting'], ['urgent'], ['email']]
```

## Rule Format

Rules are defined in JSON with the following structure:

```json
[
  {
    "label": "greeting",
    "rule": {
      "or_patterns": [
        {"pattern": "\\bhello\\b", "flags": ["i"]},
        {"pattern": "\\bhi\\b", "flags": ["i"]},
        {"pattern": "\\bhey\\b", "flags": ["i"]}
      ]
    }
  },
  {
    "label": "urgent",
    "rule": {
      "and_patterns": [
        {"pattern": "urgent", "flags": ["i"]},
        {"pattern": "asap|immediately|now", "flags": ["i"]}
      ]
    }
  },
  {
    "label": "not_spam",
    "rule": {
      "or_patterns": [
        {"pattern": "legitimate"}
      ],
      "not_patterns": [
        {"pattern": "click here", "flags": ["i"]},
        {"pattern": "free money", "flags": ["i"]}
      ]
    }
  }
]
```

### Pattern Types

- **`or_patterns`**: Text matches if ANY pattern matches
- **`and_patterns`**: Text matches if ALL patterns match  
- **`not_patterns`**: Text matches if NONE of these patterns match

### Flags

- **`i`**: Case insensitive matching
- **`m`**: Multi-line mode

## Development

- **`script/setup`** - Set up development environment
- **`script/test`** - Run the test suite
- **`script/build`** - Build the Python extension
- **`script/console`** - Start interactive development console
- **`script/example`** - Run example code
- **`script/clean`** - Clean build artifacts
- **`script/help`** - Show all available commands

### Architecture

- **`rulebox-rust/`** - Core Rust library with regex engine and rule logic
- **`rulebox-python/`** - Python bindings using PyO3 and Maturin
- **`script/`** - Development automation scripts