#!/usr/bin/env python3
"""Regenerate the SCHEMA_V1 example instances shipped with this package.

Every record set below is transcribed verbatim from the committed evidence and
the `expect` blocks are copied from the committed receipts, so running this
script and re-running the test suite is a closed loop: the examples cannot drift
away from the artifacts they claim to encode.

Sources:
  cedar-multipolicy  papers/orion-03-typed-merge-falsification/evidence/
                     round1-cedar-multipolicy/rust-adjudicator/src/main.rs
                     (record sets) and RUST_ADJUDICATION_V1.json (expectations)
  x509-truststore    papers/orion-03-typed-merge-falsification/evidence/
                     round2-x509-truststore/ROUND2_RESULTS_V2.json and
                     TASK_MANIFEST_V2.json
"""

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
TARGET = "__target__"
R1 = ("papers/orion-03-typed-merge-falsification/evidence/round1-cedar-multipolicy")
R2 = ("papers/orion-03-typed-merge-falsification/evidence/round2-x509-truststore")

# (name, required atoms, [(origin, atoms, retracted)], flat, typed)
CONTROLS = [
    ("spliced_foreign_origin_requirements", ["subject=alice", "scope=admin"],
     [("A", ["subject=alice"], False), ("B", ["scope=admin"], False)], True, False),
    ("retracted_evidence_erasure", ["subject=alice", "scope=admin"],
     [("A", ["subject=alice", "scope=admin"], True)], True, False),
    ("two_partial_sources_make_stronger_target",
     ["principal", "action", "resource", "context"],
     [("A", ["principal", "action"], False), ("B", ["resource", "context"], False)],
     True, False),
    ("alternative_complete_origin", ["subject=alice", "scope=admin"],
     [("A", ["subject=alice"], False), ("B", ["scope=admin"], False),
      ("C", ["subject=alice", "scope=admin"], False)], True, True),
    ("explicit_bridge_licence", ["subject=alice", "scope=admin"],
     [("A", ["subject=alice"], False), ("B", ["scope=admin"], False),
      ("BRIDGE-LICENCE", ["subject=alice", "scope=admin"], False)], True, True),
    ("single_origin_complete_record", ["subject=alice", "scope=admin"],
     [("A", ["subject=alice", "scope=admin"], False)], True, True),
    ("multiple_complete_origins_not_false_alarm", ["subject=alice", "scope=admin"],
     [("A", ["subject=alice", "scope=admin"], False),
      ("B", ["subject=alice", "scope=admin"], False)], True, True),
]


def control_instance(name, required, records, flat, typed):
    live = [r for r in records if not r[2]]
    doc = {
        "schema": "ORION.TypedMerge.Instance.v1",
        "id": f"cedar-multipolicy/{name}",
        "title": f"Round 1 origin-witness control: {name}",
        "provenance": {
            "domain": "authorization records with origin attribution",
            "transcribed_from": f"{R1}/rust-adjudicator/src/main.rs",
            "expectations_from": f"{R1}/RUST_ADJUDICATION_V1.json",
            "encoding": (
                "One license per non-retracted origin record. Each required atom is "
                "seeded with the origins whose record carries it, so the capped rule "
                "transfer (intersection of body labels) yields exactly the origins "
                "carrying every required atom -- the typed predicate. The "
                "license-erased pass yields the flat predicate."
            ),
        },
        "licenses": [r[0] for r in records],
        "claims": list(required) + [TARGET],
        "seeds": {a: [r[0] for r in live if a in r[1]] for a in required},
        "rules": [{"id": "compose", "body": list(required), "head": TARGET, "cap": "ALL"}],
        "refuted": [],
        "targets": [TARGET],
        "expect": {
            "typed_authorized": {TARGET: typed},
            "flat_authorized": {TARGET: flat},
            "first_mixing": {TARGET: flat and not typed},
        },
    }
    if any(r[2] for r in records):
        doc["seeds"] = {a: [r[0] for r in live if a in r[1]] for a in required}
        doc["flat_seeded_claims"] = [
            a for a in required if any(a in r[1] for r in records)
        ]
        doc["provenance"]["retraction_note"] = (
            "The single record is retracted, so it contributes no typed license. "
            "main.rs calls flat_constructs with erase_retraction=true for this "
            "control only: the flat merge has lost the retraction marker and still "
            "sees the atoms. flat_seeded_claims encodes exactly that divergence."
        )
    return doc


def cycle_instance():
    return {
        "schema": "ORION.TypedMerge.Instance.v1",
        "id": "cedar-multipolicy/unsupported_positive_cycle",
        "title": "Round 1 origin-witness control: unsupported_positive_cycle",
        "provenance": {
            "domain": "authorization records with origin attribution",
            "transcribed_from": f"{R1}/rust-adjudicator/src/main.rs (positive_closure, empty seeds)",
            "expectations_from": f"{R1}/RUST_ADJUDICATION_V1.json",
            "also_proved_in": f"{R1}/lean/Orion03Round1.lean (unsupported_positive_cycle_is_empty)",
            "encoding": "Two claims deriving each other, with no seed label anywhere.",
        },
        "licenses": ["origin"],
        "claims": ["cycle_a", "cycle_b"],
        "seeds": {},
        "rules": [
            {"id": "a_from_b", "body": ["cycle_b"], "head": "cycle_a", "cap": "ALL"},
            {"id": "b_from_a", "body": ["cycle_a"], "head": "cycle_b", "cap": "ALL"},
        ],
        "refuted": [],
        "targets": ["cycle_a", "cycle_b"],
        "expect": {
            "typed_authorized": {"cycle_a": False, "cycle_b": False},
            "flat_authorized": {"cycle_a": False, "cycle_b": False},
            "first_mixing": {"cycle_a": False, "cycle_b": False},
        },
    }


def write(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main():
    written = []
    for name, required, records, flat, typed in CONTROLS:
        written.append(write(
            HERE / "cedar-multipolicy" / f"{name}.json",
            control_instance(name, required, records, flat, typed),
        ))
    written.append(write(
        HERE / "cedar-multipolicy" / "unsupported_positive_cycle.json", cycle_instance()))
    from x509_builder import x509_instances  # noqa: E402
    from manuscript_cases_builder import manuscript_instances  # noqa: E402
    for doc in x509_instances():
        written.append(write(HERE / "x509-truststore" / f"{doc['id'].split('/')[-1]}.json", doc))
    for doc in manuscript_instances():
        written.append(write(HERE / "manuscript-cases" / f"{doc['id'].split('/')[-1]}.json", doc))
    for path in written:
        print(path.relative_to(HERE.parent))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(HERE))
    main()
