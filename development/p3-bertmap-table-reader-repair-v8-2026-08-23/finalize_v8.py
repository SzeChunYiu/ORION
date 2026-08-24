#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TERMINAL = (
    "P3_V8_BERTMAP_TABLE_READER_MINIMAL_REPAIR_SOURCE_HASH_AND_SYNTHETIC_EMPTY_NONEMPTY_EXECUTION_BOUND__"
    "MALFORMED_STALE_AND_PROHIBITED_CASES_FAIL_CLOSED__V7_PARSER_SYNTHETIC_COMPATIBILITY_BOUND__"
    "NATIVE_SMOKE_AND_SCIENTIFIC_READINESS_UNCHANGED"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name: str, value) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    protocol = json.loads((ROOT / "PROTOCOL_V8.json").read_text())
    receipt = json.loads((ROOT / "LANGUAGE_LEVEL_EXECUTION_RECEIPT_V8.json").read_text())
    assert receipt["terminal"] == TERMINAL
    result = {
        "schema_version": "orion.p3.bertmap-table-reader-repair.result.v8",
        "protocol_id": protocol["protocol_id"],
        "terminal": TERMINAL,
        "authority": receipt["authority"],
        "exact_repair": {
            "source_commit": receipt["source_identity"]["commit"],
            "source_tree": receipt["source_identity"]["tree"],
            "source_path": receipt["source_identity"]["path"],
            "original_sha256": receipt["source_identity"]["original_sha256"],
            "patch_sha256": receipt["source_identity"]["patch_sha256"],
            "repaired_sha256": receipt["source_identity"]["repaired_sha256"],
            "expression_before": 'dp["Score"]',
            "expression_after": "dp.Score",
            "root_source_rights": "APACHE_2_0_ROOT_SOURCE_AND_NOTICE_BOUND__NOT_LEGAL_ADVICE",
            "full_runtime_rights": "NOT_CLOSED",
        },
        "scientific_result": {
            "prospective_protocol_freeze": "PASS",
            "synthetic_cases": "8/8 PASS",
            "empty_nonreference": "PASS_UNCHANGED",
            "nonempty_falsey_threshold": "PASS_UNCHANGED",
            "nonempty_truthy_threshold_before": "TYPEERROR_REPRODUCED",
            "nonempty_truthy_threshold_after": "EXISTING_THRESHOLD_SEMANTICS_EXECUTED",
            "malformed_stale_prohibited": "5/5 FAIL_CLOSED",
            "semantic_ast_boundary": "ONE_FROZEN_ACCESS_CHANGE_ONLY",
            "v7_parser_synthetic_compatibility": "PASS_INTERFACE_AUTHORITY_ONLY",
            "actual_native_bertmap_execution": "CANNOT_CHECK__NOT_RUN",
            "actual_native_artifacts": "0/5",
        },
        "scope_correction": receipt["semantic_equivalence_boundary"]["v7_scope_correction"],
        "semantic_equivalence_boundary": receipt["semantic_equivalence_boundary"],
        "forbidden_operations": receipt["forbidden_operations"],
        "v7_compatibility_island": receipt["v7_compatibility_island"],
        "readiness_delta": receipt["readiness_delta"],
        "claim_boundary": {
            "source_patch_and_synthetic_language_execution": "BOUND",
            "native_smoke": "CANNOT_CHECK",
            "correctness": "CANNOT_CHECK",
            "coverage": "CANNOT_CHECK",
            "harm": "CANNOT_CHECK",
            "transport": "CANNOT_CHECK",
            "performance": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
            "top_tier_submission_ready": False,
        },
        "remaining_blockers": receipt["remaining_blockers"],
        "next_discriminator": receipt["next_discriminator"],
        "evidence": {
            "protocol_sha256": sha(ROOT / "PROTOCOL_V8.json"),
            "protocol_freeze_receipt_sha256": sha(ROOT / "PROTOCOL_FREEZE_RECEIPT_V8.json"),
            "language_level_execution_receipt_sha256": sha(ROOT / "LANGUAGE_LEVEL_EXECUTION_RECEIPT_V8.json"),
            "patch_sha256": sha(ROOT / "mapping_dp_score_v8.patch"),
            "pinned_mapping_sha256": sha(ROOT / "PINNED_MAPPING_V7.py"),
            "upstream_license_sha256": sha(ROOT / "UPSTREAM_LICENSE.txt"),
        },
    }
    write_json("RESULT_V8.json", result)

    negatives = {
        "schema_version": "orion.p3.bertmap-table-reader-repair.negative-ledger.v8",
        "protocol_id": protocol["protocol_id"],
        "terminal": TERMINAL,
        "entries": [
            {
                "id": "P3V8-N01",
                "negative_result": "V7 described the table-reader defect as affecting every nonempty non-reference table.",
                "cause": "For falsey threshold, Python short-circuits `not threshold or ...`; the defective subscript is never evaluated.",
                "positive_progress": "V8 prospectively separates empty, falsey-threshold and truthy-threshold cases and reproduces the TypeError only at the exact truthy-threshold boundary.",
                "residual": "Prior wording must not be reused as an all-nonempty claim.",
                "next_discriminator": "Use the V8 truthy-threshold scope in every integration artifact.",
            },
            {
                "id": "P3V8-N02",
                "negative_result": "Pinned mapping.py cannot apply a truthy threshold because `itertuples()` rows do not support string-key access.",
                "cause": "The comparison uses dp[\"Score\"] while the same row is otherwise accessed by attributes.",
                "positive_progress": "The exact one-expression Apache-2.0 source patch dp.Score passes synthetic truthy-threshold execution and preserves normalized method AST outside that access.",
                "residual": "This is source-patch and language-level evidence, not DeepOnto or native BERTMap execution.",
                "next_discriminator": "Apply only the content-addressed V8 patch inside a complete rights-closed runtime.",
            },
            {
                "id": "P3V8-N03",
                "negative_result": "Malformed synthetic tables lack Score or carry nonnumeric Score values.",
                "cause": "The source method expects an attribute named Score and a value comparable to the threshold.",
                "positive_progress": "Both cases fail closed without returning mappings.",
                "residual": "No new coercion or schema-repair semantics were introduced by this minimal patch.",
                "next_discriminator": "Keep upstream schema validation explicit in any native adapter; do not silently coerce malformed scores.",
            },
            {
                "id": "P3V8-N04",
                "negative_result": "A synthetic five-file fixture passes the frozen V7 parser, but no actual native BERTMap artifact exists.",
                "cause": "V8 stops at the first meaningful repair boundary and forbids models, ontologies, prediction and native execution.",
                "positive_progress": "The repaired EntityMapping row shape remains compatible with the exact V7 structural parser contract.",
                "residual": "Native smoke stays 2/3 and BERTMap actual-artifact presence stays 0/5.",
                "next_discriminator": "Require all five actual artifacts from one fresh isolated no-gold run; synthetic fixture hashes cannot satisfy this gate.",
            },
            {
                "id": "P3V8-N05",
                "negative_result": "The V7 26-distribution island is constructor-only and full Python/JVM rights/SBOM remain open.",
                "cause": "DeepOnto, pandas integration, JVM/JARs and generated artifact layers are outside the island's closure.",
                "positive_progress": "V8 reuses the exact V7 source, lock, manifest and parser identities without inflating them into a complete runtime claim.",
                "residual": "No native or scientific comparator promotion is lawful from this packet alone.",
                "next_discriminator": "Bind a complete content-addressed Python runtime and component-level Java SBOM/rights decisions before native execution custody.",
            },
        ],
    }
    write_json("NEGATIVE_RESULT_LEDGER_V8.json", negatives)

    (ROOT / "NEGATIVE_RESULT_LEDGER_V8.md").write_text(f"""# P3 V8 negative-result ledger

Terminal: `{TERMINAL}`

| ID | Negative result | Positive progress | Residual / next discriminator |
|---|---|---|---|
| P3V8-N01 | V7 over-scoped the failure to every nonempty table. | V8 proves falsey-threshold short-circuit and truthy-threshold failure separately. | Integrate only the corrected truthy-threshold scope. |
| P3V8-N02 | Pinned `dp[\"Score\"]` fails for `itertuples()` rows when threshold is truthy. | One-expression `dp.Score` patch passes exact synthetic execution. | Bind the patch in a complete rights-closed runtime. |
| P3V8-N03 | Missing/nonnumeric scores are malformed. | Both fail closed; no silent coercion was added. | Preserve explicit schema validation in the adapter. |
| P3V8-N04 | Synthetic parser conformance is not native execution. | Exact V7 parser accepts the repaired synthetic row shape. | Require five actual artifacts from one fresh isolated run; current presence is 0/5. |
| P3V8-N05 | Full Python/JVM rights and SBOM are open. | Exact V7 identities remain bounded and unchanged. | Close component rights/SBOM before native custody or promotion. |
""")

    (ROOT / "SCIENTIFIC_REPORT_V8.md").write_text(f"""# P3 BERTMap table-reader repair V8

## Exact terminal

`{TERMINAL}`

## Efficient root-cause repair

V8 repairs exactly one source expression in DeepOnto commit
`74ca8d47f01bad0b8739f19ee2c392bdf6d9c090`, tree
`b499cb5780bbe749f7db44d0bc872d275a2737ea`,
`src/deeponto/align/mapping.py` SHA-256
`9cf0dce1c5bd142e4175f628f8f3267f54ed6deac9f31e165a25b4a073eedff0`:

```diff
- if not threshold or dp[\"Score\"] >= threshold:
+ if not threshold or dp.Score >= threshold:
```

The patch SHA-256 is `{receipt['source_identity']['patch_sha256']}` and the
resulting source SHA-256 is `{receipt['source_identity']['repaired_sha256']}`.
The upstream root source is Apache-2.0 and the exact licence text is retained;
this is not legal advice and it does not close the full runtime's component
rights.

## Prospective outcome-blind execution

The protocol was frozen before patch execution. Eight of eight authored
synthetic cases passed:

- empty non-reference table: unchanged empty result;
- nonempty table with `threshold=None`: original and repaired methods both
  return both exact rows;
- nonempty table with truthy threshold `0.5`: the pinned source reproduces
  `TypeError`, while V8 returns only the `0.9` row under the pre-existing rule;
- missing and nonnumeric Score tables fail closed;
- stale source identity, reference-mode request and external fixture request
  fail closed before prohibited access.

This corrects a V7 scope overstatement: **not every nonempty table fails**.
The defective expression is reached only when `threshold` is truthy; falsey
thresholds short-circuit it. The normalized method AST is identical after
replacing only that frozen access.

No DeepOnto import, JVM, model, ontology, benchmark, paper `data.zip`,
gold/reference alignment, protected outcome, training, prediction, mapping
repair, scoring or comparison occurred.

## Parser and readiness boundary

The exact V7 parser SHA-256
`d1184dc129082bdcf18b415b551f244a695b4e34417286afc37a3f3a5d788bc5`
accepted a temporary authored five-file fixture with row counts 2 raw, 2
extended, 1 filtered and 1 repaired. Those synthetic files were deleted.
They are not native BERTMap artifacts. Actual native artifact presence is
**0/5**, so native smoke is not claimed.

| Axis | Before | After | Net |
|---|---:|---:|---:|
| Truthy-threshold source defect | blocking | exact patch + synthetic execution bound | root cause repaired at language level |
| Three-family native smoke | 2/3 | 2/3 | 0 |
| Scientific comparator readiness | 0/3 | 0/3 | 0 |
| Actual BERTMap artifacts | 0/5 | 0/5 | 0 |

## Remaining shortest path

1. Bind a complete content-addressed repaired DeepOnto Python runtime.
2. Close component-level JVM/JAR provenance, rights and SBOM decisions.
3. Run one fresh isolated no-gold native BERTMap smoke and require all five
   actual artifacts to pass the unchanged V7 parser.
4. Only then freeze independently custodied rights-valid evaluation.

Correctness, coverage, harm, transport, performance, superiority and top-tier
submission readiness remain `CANNOT_CHECK` / not established.
""")

    (ROOT / "README.md").write_text("""# P3 BERTMap table-reader repair V8 packet

Outcome-blind, prospectively frozen one-expression source repair for the
DeepOnto `itertuples()` Score-access defect. Start with `SCIENTIFIC_REPORT_V8.md`
and `RESULT_V8.json`. Run `PYTHONDONTWRITEBYTECODE=1 python validate_v8.py` for
the packet-native scientific validator. This is not a native BERTMap run and
contains no ontology, benchmark, gold/reference, protected outcome, model,
checkpoint, prediction, score, or actual native output.
""")
    print(json.dumps({"terminal": TERMINAL, "result": "RESULT_V8.json", "negative_entries": len(negatives["entries"])}, sort_keys=True))


if __name__ == "__main__":
    main()
