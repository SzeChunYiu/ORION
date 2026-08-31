"""SCHEMA_V1 encoding of MANUSCRIPT_V2.md section 9 (Case III).

The two shipped merge domains both read licenses as *origins*. The manuscript's
own scientific cases use the other reading, in which licenses are evidence
classes and caps state nonpromotion. This encodes Case III so the package
demonstrates that reading on a real case from the paper rather than only on a
unit test.
"""

T, BC, ER = "THEOREM", "BOUNDED_COMPUTATION", "EXTERNAL_REPLAY"


def case3_bounded_computation():
    return {
        "schema": "ORION.TypedMerge.Instance.v1",
        "id": "manuscript-cases/case3-d4-bounded-computation",
        "title": "Case III: bounded computation cannot decide exact D_4(C_5^3)",
        "provenance": {
            "domain": "scientific evidence classes (non-quantum C_5^3 programme)",
            "encoded_from": "papers/orion-03-typed-merge-falsification/MANUSCRIPT_V2.md section 9",
            "ledger_row": "D2-C7 (PROVEN IN REGISTERED TYPING)",
            "encoding": (
                "Licenses are evidence classes. The analytic lemmas are seeded "
                "THEOREM. The internal support-frontier scan is seeded "
                "{BOUNDED_COMPUTATION, EXTERNAL_REPLAY} because its own metadata "
                "denies theorem authority and requires external replay. The rule "
                "from the frontier to 'support at least 23' is capped by the same "
                "set, exactly as the manuscript states."
            ),
            "expected_reading": (
                "exact-D4 and 31-in-C0 come out with EMPTY labels, not merely "
                "without THEOREM: their two premises share no license, so no "
                "single evidence class carries the derivation end to end. The "
                "license-erased reading still derives them, so both are reported "
                "as first-mixing -- the untyped record would call them supported."
            ),
        },
        "licenses": [T, BC, ER],
        "claims": [
            "davenport-corridor-lemma", "saturation-defect-lemma",
            "support-frontier-scan", "support-at-least-23",
            "exact-D4", "31-in-C0",
        ],
        "seeds": {
            "davenport-corridor-lemma": [T],
            "saturation-defect-lemma": [T],
            "support-frontier-scan": [BC, ER],
        },
        "rules": [
            {"id": "frontier-to-support23", "body": ["support-frontier-scan"],
             "head": "support-at-least-23", "cap": [BC, ER]},
            {"id": "support23-to-exact-D4",
             "body": ["support-at-least-23", "davenport-corridor-lemma"],
             "head": "exact-D4", "cap": "ALL"},
            {"id": "support23-to-31-in-C0",
             "body": ["support-at-least-23", "saturation-defect-lemma"],
             "head": "31-in-C0", "cap": "ALL"},
        ],
        "refuted": [],
        "targets": ["support-at-least-23", "exact-D4", "31-in-C0"],
        "expect": {
            "typed_licenses": {
                "support-at-least-23": [BC, ER],
                "exact-D4": [],
                "31-in-C0": [],
            },
            "typed_authorized": {
                "support-at-least-23": True, "exact-D4": False, "31-in-C0": False,
            },
            "flat_authorized": {
                "support-at-least-23": True, "exact-D4": True, "31-in-C0": True,
            },
            "first_mixing": {
                "support-at-least-23": False, "exact-D4": True, "31-in-C0": True,
            },
        },
    }


def manuscript_instances():
    return [case3_bounded_computation()]
