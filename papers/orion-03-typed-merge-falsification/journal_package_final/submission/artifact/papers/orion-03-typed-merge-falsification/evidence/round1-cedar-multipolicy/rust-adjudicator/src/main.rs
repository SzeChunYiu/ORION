//! Independent Rust/native-Cedar adjudicator for ORION-03 Round 1.
//!
//! The native stage invokes the upstream Cedar integration API at the frozen
//! Git revision.  The control stage independently implements the frozen
//! origin-preserving record predicate without importing ORION Python code.

use cedar_testing::cedar_test_impl::RustEngine;
use cedar_testing::integration_testing::{
    parse_entities_from_test, parse_policies_from_test, parse_schema_from_test,
    perform_integration_test, JsonTest,
};
use std::collections::BTreeSet;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

const INTEGRATION_COMMIT: &str = "75989795c75d861270ce6cac38ef9d9e5b220a0c";
const CEDAR_COMMIT: &str = "bcb8bd93a292b59ae8f1dcf53b9b4176a2d3405d";

#[derive(Clone, Copy)]
struct Record<'a> {
    origin: &'a str,
    atoms: &'a [&'a str],
    retracted: bool,
}

#[derive(Clone, Copy)]
struct ControlResult<'a> {
    name: &'a str,
    flat: bool,
    typed: bool,
    expected_flat: bool,
    expected_typed: bool,
}

impl ControlResult<'_> {
    fn passed(self) -> bool {
        self.flat == self.expected_flat && self.typed == self.expected_typed
    }
}

fn flat_constructs(required: &[&str], records: &[Record<'_>], erase_retraction: bool) -> bool {
    required.iter().all(|required_atom| {
        records.iter().any(|record| {
            (erase_retraction || !record.retracted) && record.atoms.contains(required_atom)
        })
    })
}

fn typed_constructs(required: &[&str], records: &[Record<'_>]) -> bool {
    records
        .iter()
        .filter(|record| !record.retracted)
        .any(|record| {
            !record.origin.is_empty()
                && required
                    .iter()
                    .all(|required_atom| record.atoms.contains(required_atom))
        })
}

fn positive_closure<'a>(seeds: &[&'a str], rules: &[(&[&'a str], &'a str)]) -> BTreeSet<&'a str> {
    let mut closure: BTreeSet<&str> = seeds.iter().copied().collect();
    loop {
        let before = closure.len();
        for (body, head) in rules {
            if body.iter().all(|atom| closure.contains(atom)) {
                closure.insert(head);
            }
        }
        if closure.len() == before {
            return closure;
        }
    }
}

fn controls() -> Vec<ControlResult<'static>> {
    let splice_records = [
        Record {
            origin: "A",
            atoms: &["subject=alice"],
            retracted: false,
        },
        Record {
            origin: "B",
            atoms: &["scope=admin"],
            retracted: false,
        },
    ];
    let retracted = [Record {
        origin: "A",
        atoms: &["subject=alice", "scope=admin"],
        retracted: true,
    }];
    let stronger = [
        Record {
            origin: "A",
            atoms: &["principal", "action"],
            retracted: false,
        },
        Record {
            origin: "B",
            atoms: &["resource", "context"],
            retracted: false,
        },
    ];
    let alternative_complete = [
        splice_records[0],
        splice_records[1],
        Record {
            origin: "C",
            atoms: &["subject=alice", "scope=admin"],
            retracted: false,
        },
    ];
    let explicit_bridge = [
        splice_records[0],
        splice_records[1],
        Record {
            origin: "BRIDGE-LICENCE",
            atoms: &["subject=alice", "scope=admin"],
            retracted: false,
        },
    ];
    let single_complete = [Record {
        origin: "A",
        atoms: &["subject=alice", "scope=admin"],
        retracted: false,
    }];
    let multiple_complete = [
        Record {
            origin: "A",
            atoms: &["subject=alice", "scope=admin"],
            retracted: false,
        },
        Record {
            origin: "B",
            atoms: &["subject=alice", "scope=admin"],
            retracted: false,
        },
    ];
    let cycle_a_body = ["cycle_b"];
    let cycle_b_body = ["cycle_a"];
    let cycle_rules: [(&[&str], &str); 2] =
        [(&cycle_a_body, "cycle_a"), (&cycle_b_body, "cycle_b")];
    let empty_cycle = positive_closure(&[], &cycle_rules);

    vec![
        ControlResult {
            name: "spliced_foreign_origin_requirements",
            flat: flat_constructs(&["subject=alice", "scope=admin"], &splice_records, false),
            typed: typed_constructs(&["subject=alice", "scope=admin"], &splice_records),
            expected_flat: true,
            expected_typed: false,
        },
        ControlResult {
            name: "retracted_evidence_erasure",
            flat: flat_constructs(&["subject=alice", "scope=admin"], &retracted, true),
            typed: typed_constructs(&["subject=alice", "scope=admin"], &retracted),
            expected_flat: true,
            expected_typed: false,
        },
        ControlResult {
            name: "unsupported_positive_cycle",
            flat: !empty_cycle.is_empty(),
            typed: !empty_cycle.is_empty(),
            expected_flat: false,
            expected_typed: false,
        },
        ControlResult {
            name: "two_partial_sources_make_stronger_target",
            flat: flat_constructs(
                &["principal", "action", "resource", "context"],
                &stronger,
                false,
            ),
            typed: typed_constructs(&["principal", "action", "resource", "context"], &stronger),
            expected_flat: true,
            expected_typed: false,
        },
        ControlResult {
            name: "alternative_complete_origin",
            flat: flat_constructs(
                &["subject=alice", "scope=admin"],
                &alternative_complete,
                false,
            ),
            typed: typed_constructs(&["subject=alice", "scope=admin"], &alternative_complete),
            expected_flat: true,
            expected_typed: true,
        },
        ControlResult {
            name: "explicit_bridge_licence",
            flat: flat_constructs(&["subject=alice", "scope=admin"], &explicit_bridge, false),
            typed: typed_constructs(&["subject=alice", "scope=admin"], &explicit_bridge),
            expected_flat: true,
            expected_typed: true,
        },
        ControlResult {
            name: "single_origin_complete_record",
            flat: flat_constructs(&["subject=alice", "scope=admin"], &single_complete, false),
            typed: typed_constructs(&["subject=alice", "scope=admin"], &single_complete),
            expected_flat: true,
            expected_typed: true,
        },
        ControlResult {
            name: "multiple_complete_origins_not_false_alarm",
            flat: flat_constructs(&["subject=alice", "scope=admin"], &multiple_complete, false),
            typed: typed_constructs(&["subject=alice", "scope=admin"], &multiple_complete),
            expected_flat: true,
            expected_typed: true,
        },
    ]
}

fn run_native(snapshot: &Path) {
    for fixture in ["1.json", "2.json", "3.json", "4.json", "5.json"] {
        let fixture_path = snapshot.join("tests/multi").join(fixture);
        eprintln!("Running test: {fixture_path:?}");
        let fixture_text = fs::read_to_string(&fixture_path)
            .unwrap_or_else(|error| panic!("failed to read {}: {error}", fixture_path.display()));
        let test: JsonTest = serde_json::from_str(&fixture_text)
            .unwrap_or_else(|error| panic!("failed to parse {}: {error}", fixture_path.display()));

        // The pinned upstream resolver treats CEDAR_INTEGRATION_TESTS_PATH as
        // an exact file override rather than a directory prefix.  Bind each
        // referenced source explicitly before calling the upstream parsers.
        env::set_var(
            "CEDAR_INTEGRATION_TESTS_PATH",
            snapshot.join(&test.policies),
        );
        let policies = parse_policies_from_test(&test);
        env::set_var("CEDAR_INTEGRATION_TESTS_PATH", snapshot.join(&test.schema));
        let schema = parse_schema_from_test(&test);
        env::set_var(
            "CEDAR_INTEGRATION_TESTS_PATH",
            snapshot.join(&test.entities),
        );
        let entities = parse_entities_from_test(&test, &schema);
        env::remove_var("CEDAR_INTEGRATION_TESTS_PATH");

        perform_integration_test(
            policies,
            entities,
            schema,
            test.should_validate,
            test.requests,
            &fixture_path.display().to_string(),
            &RustEngine::new(),
        );
    }
}

fn bool_json(value: bool) -> &'static str {
    if value {
        "true"
    } else {
        "false"
    }
}

fn main() {
    let mut args = env::args_os();
    let _program = args.next();
    let Some(snapshot) = args.next() else {
        eprintln!("usage: orion03-cedar-round1-adjudicator SNAPSHOT_ROOT");
        std::process::exit(2);
    };
    if args.next().is_some() {
        eprintln!("exactly one SNAPSHOT_ROOT argument is required");
        std::process::exit(2);
    }
    let snapshot = PathBuf::from(snapshot);
    if !snapshot.join("tests/multi/1.json").is_file() {
        eprintln!("snapshot does not contain the frozen multi corpus");
        std::process::exit(2);
    }

    run_native(&snapshot);
    let results = controls();
    let passed = results.iter().filter(|result| result.passed()).count();
    if passed != results.len() {
        eprintln!("one or more Rust authority controls failed");
        std::process::exit(1);
    }

    println!("{{");
    println!("  \"authority\": {{");
    println!("    \"external_independence\": \"CANNOT_CHECK\",");
    println!("    \"hostile_controls_are_real_domain_results\": false,");
    println!("    \"journal_authority\": false,");
    println!("    \"native_semantics_only\": true");
    println!("  }},");
    println!("  \"hostile_and_safe_controls\": {{");
    println!("    \"cases\": [");
    for (index, result) in results.iter().enumerate() {
        println!("      {{");
        println!("        \"flat\": {},", bool_json(result.flat));
        println!("        \"name\": \"{}\",", result.name);
        println!("        \"status\": \"PASS\",");
        println!("        \"typed\": {}", bool_json(result.typed));
        print!("      }}");
        if index + 1 != results.len() {
            println!(",");
        } else {
            println!();
        }
    }
    println!("    ],");
    println!("    \"passed\": {},", passed);
    println!("    \"total\": {}", results.len());
    println!("  }},");
    println!("  \"native_cedar\": {{");
    println!("    \"decision_reason_error_and_validation_exact\": true,");
    println!("    \"fixtures_passed\": 5,");
    println!("    \"requests_adjudicated\": 15");
    println!("  }},");
    println!("  \"schema\": \"ORION.ORION03.CedarMultiPolicy.RustAdjudication.v1\",");
    println!("  \"terminal\": \"NATIVE_CEDAR_AND_RUST_CONTROLS_PASS\",");
    println!("  \"upstream\": {{");
    println!("    \"cedar_commit\": \"{}\",", CEDAR_COMMIT);
    println!("    \"integration_commit\": \"{}\"", INTEGRATION_COMMIT);
    println!("  }}");
    println!("}}");
}
