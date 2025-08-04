use criterion::{black_box, criterion_group, criterion_main, Criterion};
use rulebox_rust::*;

fn create_test_rulebox() -> RuleBox {
    // Create a test rulebox with several rules
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
        LabelRule {
            uuid: "test3".to_string(),
            rule: Rule {
                or_patterns: vec![RegexRule {
                    pattern: r"\baddress\b".to_string(),
                    flags: vec!["i".to_string()],
                    compiled: None,
                }],
                and_patterns: vec![],
                not_patterns: vec![],
            },
            label: "contains_address".to_string(),
            proto_text: "".to_string(),
            active: true,
        },
        // Add an inactive rule to test filtering
        LabelRule {
            uuid: "test4".to_string(),
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
    rulebox
}

fn create_test_texts() -> Vec<String> {
    vec![
        "Please send me an email at test@example.com".to_string(),
        "Call me on my phone number 555-1234".to_string(),
        "My address is 123 Main Street".to_string(),
        "This text has email and phone keywords".to_string(),
        "This text matches no patterns".to_string(),
        "Contact info: email me or phone me at my address".to_string(),
    ]
}

fn bench_assign_labels_vector(c: &mut Criterion) {
    let rulebox = create_test_rulebox();
    let texts = create_test_texts();

    c.bench_function("assign_labels_vector (default)", |b| {
        b.iter(|| black_box(rulebox.assign_labels_vector(black_box(&texts))))
    });
}

criterion_group!(benches, bench_assign_labels_vector);
criterion_main!(benches);
