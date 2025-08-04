#[cfg(test)]
mod tests {
    use rulebox_rust::*;

    #[test]
    fn test_assign_labels_vector_optimized_default() {
        let rules = vec![
            LabelRule {
                uuid: "test1".to_string(),
                rule: Rule {
                    or_patterns: vec![RegexRule {
                        pattern: r"\bemail\b".to_string(),
                        flags: vec!["i".to_string()],
                        compiled: None,
                    }],
                    and_patterns: vec![],
                    not_patterns: vec![],
                },
                label: "contains_email".to_string(),
                proto_text: "".to_string(),
                active: true,
            },
            LabelRule {
                uuid: "test2".to_string(),
                rule: Rule {
                    or_patterns: vec![RegexRule {
                        pattern: r"\bphone\b".to_string(),
                        flags: vec!["i".to_string()],
                        compiled: None,
                    }],
                    and_patterns: vec![],
                    not_patterns: vec![],
                },
                label: "contains_phone".to_string(),
                proto_text: "".to_string(),
                active: true,
            },
            // Add an inactive rule to test filtering
            LabelRule {
                uuid: "test3".to_string(),
                rule: Rule {
                    or_patterns: vec![RegexRule {
                        pattern: r"\binactive\b".to_string(),
                        flags: vec!["i".to_string()],
                        compiled: None,
                    }],
                    and_patterns: vec![],
                    not_patterns: vec![],
                },
                label: "inactive_rule".to_string(),
                proto_text: "".to_string(),
                active: false,
            },
        ];

        let mut rulebox = RuleBox(rules);
        rulebox.compile().expect("Failed to compile rules");

        let texts = vec![
            "Please send me an email".to_string(),
            "Call me on my phone".to_string(),
            "This has both email and phone".to_string(),
            "This text matches no patterns".to_string(),
            "This contains inactive keyword".to_string(),
        ];

        let results = rulebox.assign_labels_vector(&texts);

        // Check results
        assert_eq!(results.len(), 5);

        // First text should match email
        assert!(results[0].contains(&"contains_email".to_string()));
        assert!(!results[0].contains(&"contains_phone".to_string()));
        assert!(!results[0].contains(&"inactive_rule".to_string()));

        // Second text should match phone
        assert!(results[1].contains(&"contains_phone".to_string()));
        assert!(!results[1].contains(&"contains_email".to_string()));

        // Third text should match both email and phone
        assert!(results[2].contains(&"contains_email".to_string()));
        assert!(results[2].contains(&"contains_phone".to_string()));
        assert!(!results[2].contains(&"inactive_rule".to_string()));

        // Fourth text should match nothing
        assert!(results[3].is_empty());

        // Fifth text should not match inactive rule
        assert!(results[4].is_empty());

        println!("✅ All tests passed! The optimized default implementation works correctly.");
        println!("Results: {:?}", results);
    }
}
