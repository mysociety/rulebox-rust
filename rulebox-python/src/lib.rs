use pyo3::prelude::*;
use pyo3::types::PyAny;
use rulebox_rust::RuleBox as RustRuleBox;
use std::path::PathBuf;

/// A Python wrapper for the Rust RuleBox
#[pyclass]
pub struct RuleBox {
    inner: RustRuleBox,
}

#[pymethods]
impl RuleBox {
    /// Create a RuleBox from a JSON file path (accepts either string or Path object)
    #[staticmethod]
    fn from_path(path: Bound<'_, PyAny>) -> PyResult<Self> {
        let path_str = extract_path_string(&path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyTypeError, _>(e))?;

        match RustRuleBox::from_path(&path_str) {
            Ok(rulebox) => Ok(RuleBox { inner: rulebox }),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
                "Failed to load RuleBox from path '{}': {}",
                path_str, e
            ))),
        }
    }

    /// Assign labels to a single text and return them as a list of strings
    fn assign_labels(&self, text: String) -> PyResult<Vec<String>> {
        Ok(self.inner.assign_labels(&text))
    }

    /// Assign labels to multiple texts and return them as a list of lists of strings
    fn assign_labels_vector(&self, texts: Vec<String>) -> PyResult<Vec<Vec<String>>> {
        Ok(self.inner.assign_labels_vector(&texts))
    }
}

/// Helper function to extract a path string from either a String or PathBuf
fn extract_path_string(path: &Bound<'_, PyAny>) -> Result<String, &'static str> {
    // Try PathBuf first (handles pathlib.Path objects)
    if let Ok(pathbuf) = path.extract::<PathBuf>() {
        return Ok(pathbuf.to_string_lossy().to_string());
    }

    // Try String next
    if let Ok(string_path) = path.extract::<String>() {
        return Ok(string_path);
    }

    // Neither worked
    Err("path must be a string or Path-like object")
}

/// A Python module implemented in Rust.
#[pymodule]
fn rulebox(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RuleBox>()?;
    Ok(())
}
