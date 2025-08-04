use pyo3::prelude::*;
use rulebox_rust::RuleBox as RustRuleBox;

/// A Python wrapper for the Rust RuleBox
#[pyclass]
pub struct RuleBox {
    inner: RustRuleBox,
}

#[pymethods]
impl RuleBox {
    /// Create a RuleBox from a JSON file path
    #[staticmethod]
    fn from_path(path: String) -> PyResult<Self> {
        match RustRuleBox::from_path(&path) {
            Ok(rulebox) => Ok(RuleBox { inner: rulebox }),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
                "Failed to load RuleBox from path '{}': {}",
                path, e
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

/// A Python module implemented in Rust.
#[pymodule]
fn rulebox(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RuleBox>()?;
    Ok(())
}
