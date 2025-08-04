use regex::{Regex as RustRegex, RegexBuilder};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::fs;
use uuid::Uuid;

// Represents a regex pattern and flags
#[derive(Debug, Serialize, Deserialize)]
pub struct RegexRule {
    pub pattern: String,
    #[serde(default)]
    pub flags: Vec<String>,

    #[serde(skip)]
    pub compiled: Option<RustRegex>,
}

impl RegexRule {
    pub fn compile(&mut self) -> Result<(), String> {
        let mut builder = RegexBuilder::new(&self.pattern);
        for flag in &self.flags {
            match flag.as_str() {
                "i" => builder.case_insensitive(true),
                "m" => builder.multi_line(true),
                _ => return Err(format!("Unknown regex flag: {}", flag)),
            };
        }
        match builder.build() {
            Ok(re) => {
                self.compiled = Some(re);
                Ok(())
            }
            Err(e) => Err(format!("Invalid regex '{}': {}", self.pattern, e)),
        }
    }

    pub fn check(&self, text: &str) -> bool {
        match &self.compiled {
            Some(re) => re.is_match(text),
            None => false,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Rule {
    #[serde(default)]
    pub and_patterns: Vec<RegexRule>,
    #[serde(default)]
    pub or_patterns: Vec<RegexRule>,
    #[serde(default)]
    pub not_patterns: Vec<RegexRule>,
}

impl Rule {
    pub fn compile(&mut self) -> Result<(), String> {
        for p in &mut self.and_patterns {
            p.compile()?;
        }
        for p in &mut self.or_patterns {
            p.compile()?;
        }
        for p in &mut self.not_patterns {
            p.compile()?;
        }

        if !self.and_patterns.is_empty() && !self.or_patterns.is_empty() {
            return Err("Rule can't have both and_patterns and or_patterns".into());
        }

        if self.and_patterns.is_empty()
            && self.or_patterns.is_empty()
            && !self.not_patterns.is_empty()
        {
            return Err("Rule cannot consist solely of not_patterns".into());
        }

        Ok(())
    }

    pub fn check(&self, text: &str) -> bool {
        if !self.and_patterns.is_empty() && !self.and_patterns.iter().all(|r| r.check(text)) {
            return false;
        }

        if !self.or_patterns.is_empty() && !self.or_patterns.iter().any(|r| r.check(text)) {
            return false;
        }

        if self.not_patterns.iter().any(|r| r.check(text)) {
            return false;
        }

        true
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LabelRule {
    #[serde(default = "generate_uuid")]
    pub uuid: String,
    pub rule: Rule,
    pub label: String,
    #[serde(default)]
    pub proto_text: String,
    #[serde(default = "default_true")]
    pub active: bool,
}

fn generate_uuid() -> String {
    Uuid::now_v7().to_string()
}
fn default_true() -> bool {
    true
}

impl LabelRule {
    pub fn compile(&mut self) -> Result<(), String> {
        self.rule.compile()
    }

    pub fn check(&self, text: &mut LabeledText) {
        if self.active && self.rule.check(&text.content) {
            text.labels.insert(self.label.clone());
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LabeledText {
    content: String,
    #[serde(default)]
    labels: HashSet<String>,
}

impl LabeledText {
    pub fn new(content: String) -> Self {
        Self {
            content,
            labels: HashSet::new(),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RuleBox(pub Vec<LabelRule>);

impl RuleBox {
    pub fn from_path(path: &str) -> Result<Self, Box<dyn std::error::Error>> {
        let json = fs::read_to_string(path)?;
        let mut rulebox: RuleBox = serde_json::from_str(&json)?;
        rulebox.compile()?;
        Ok(rulebox)
    }

    pub fn compile(&mut self) -> Result<(), String> {
        for rule in &mut self.0 {
            rule.compile()?;
        }
        Ok(())
    }

    pub fn check(&self, text: &str) -> LabeledText {
        let mut labeled = LabeledText::new(text.to_string());
        for rule in &self.0 {
            rule.check(&mut labeled);
        }
        labeled
    }

    pub fn check_many(&self, texts: &[String]) -> Vec<HashSet<String>> {
        texts.iter().map(|t| self.check(t).labels).collect()
    }

    pub fn assign_labels(&self, text: &str) -> Vec<String> {
        let labels = self.check(text).labels;
        labels.into_iter().collect()
    }

    pub fn assign_labels_vector(&self, texts: &[String]) -> Vec<Vec<String>> {
        // Optimized implementation: pre-filter active rules and use explicit loops
        let active_rules: Vec<&LabelRule> = self.0.iter().filter(|rule| rule.active).collect();
        let mut results = Vec::with_capacity(texts.len());

        for text in texts {
            let mut labels = Vec::new();
            for rule in &active_rules {
                // Skip if we already have this label assigned
                if !labels.contains(&rule.label) && rule.rule.check(text) {
                    labels.push(rule.label.clone());
                }
            }
            results.push(labels);
        }
        results
    }
}
