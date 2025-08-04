# RuleBox Python Bindings

Python bindings for RuleBox - a regex-based text labeling system written in Rust.

See the main [project README](../README.md) for full documentation and usage examples.

# Install

```
uv add git+https://github.com/mysociety/rulebox-rust.git#subdirectory=rulebox-python
```

## Quick Development

From the project root:

```bash
# Set up everything
script/setup

# Run tests
script/test

# Interactive development
script/console
```

## Direct Usage

```python
from rulebox import RuleBox

# Load rules from a JSON file
rulebox = RuleBox.from_path("path/to/rules.json")

# Assign labels to a single text
labels = rulebox.assign_labels("some text to analyze")
print(labels)  # ['label1', 'label2', ...]

# Assign labels to multiple texts
texts = ["text1", "text2", "text3"]
all_labels = rulebox.assign_labels_vector(texts)
print(all_labels)  # [['label1'], ['label2', 'label3'], []]
```

## Pandas Integration

RuleBox works well with pandas Series containing text data:

```python
import pandas as pd
from rulebox import RuleBox

rulebox = RuleBox.from_path("rules.json")

# Works directly with pandas Series containing strings
texts = pd.Series(["Hello world", "test@example.com", "Just text"])
labels = rulebox.assign_labels_vector(texts)

# For mixed types or NA values, convert to strings first
mixed_data = pd.Series(["Hello", 123, None, "test@example.com"])
labels = rulebox.assign_labels_vector(mixed_data.astype(str).tolist())

# Or handle NA values explicitly
clean_data = mixed_data.dropna().tolist()  # Remove NA values
# OR
filled_data = mixed_data.fillna("").tolist()  # Replace NA with empty string
```

See `examples/pandas_usage.py` for more detailed examples.
