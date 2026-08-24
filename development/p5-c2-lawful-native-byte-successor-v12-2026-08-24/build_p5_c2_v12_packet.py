#!/usr/bin/env python3
"""Freeze and finalize the P5 C2 V12 source/rights/lineage successor."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DEVELOPMENT = HERE.parent
V6 = DEVELOPMENT / "p5-common-visible-case-rights-v6-2026-08-23"
V4 = DEVELOPMENT / "p5-moss-execution-binding-v4-2026-08-23"
V10 = DEVELOPMENT / "p5-c2-authoritative-route-discriminator-v10-2026-08-23"
V11 = DEVELOPMENT / "p5-c2-lawful-native-byte-successor-v11-2026-08-24"
IDENTITY = "C2_SOURCE_NATIVE_VISIBLE_CORE_SUCCESSOR__ORION_V12"
PROTOCOL_ID = "P5.C2.SOURCE.NATIVE.RIGHTS.LINEAGE.SUCCESSOR.V12"
FROZEN_AT = "2026-08-24T06:20:00Z"
TARGET_FIELDS = ["inputs.candidate_visible_case_bytes", "rights.task_and_benchmark_content"]
CORE_SHA = "09a2eb17394d7b84c11641b468d14446af955c4c3272557810d861a275c72da7"
CORE_INDEX_SHA = "aeddff407dcd73326a6b1f123131463c5ae550f74aaab7f7e522a29dce247b8e"
RIGHTS_SHA = "ac99e42088648c313329fed5815db8717aae3e6ca1de83d8a8d042852a6b73b3"
SOURCE_SHA = "f97c316795a6ba124f693bce9e8019b1735bc976affa9bce8d4c52f668575f08"
TREE_SHA = "4fbe1517b1bf3c549986272fe16fead6a8e4eb6f3cfa47f09c3a92bf94162abc"
MOSS_COMMIT = "5453f1feebad44c199f5887f852fc5bc7fb7d4da"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def packet_ref(path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(HERE).as_posix(), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def repo_ref(path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(REPO_ROOT).as_posix(), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def assert_hash(path: Path, expected: str) -> None:
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"identity mismatch for {path}: {actual} != {expected}")


def freeze() -> None:
    core = load(V6 / "P5_SHARED_CASE_CORE_INDEX_V6.json")
    rights = load(V6 / "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json")
    acceptance = load(V6 / "P5_SIX_ARM_SHARED_CORE_ACCEPTANCE_V6.json")
    provenance = load(V6 / "P5_PUBLIC_CASE_PROVENANCE_V6.json")
    source_tree = load(V6 / "P5_SOURCE_TREE_CONTENT_MANIFEST_V6.json")
    registry = load(V4 / "P5_C2_V4_FIELD_REGISTRY.json")
    v11 = load(V11 / "P5_C2_V11_RESULT.json")
    assert_hash(V6 / "P5_SHARED_CASE_CORE_INDEX_V6.json", CORE_INDEX_SHA)
    assert_hash(V6 / "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json", RIGHTS_SHA)
    if core["candidate_visible_core_sha256"] != CORE_SHA:
        raise RuntimeError("V6 candidate core digest changed")
    if source_tree["canonical_member_manifest_sha256"] != TREE_SHA:
        raise RuntimeError("V6 source tree digest changed")
    if registry["bound_field_count"] != 7 or registry["blocking_field_count"] != 14:
        raise RuntimeError("C2 V4 owner count basis changed")
    if v11["successor_count_basis"]["successor_bound"] != 8 or v11["successor_count_basis"]["successor_blocking"] != 13:
        raise RuntimeError("V11 separate successor basis changed")
    if not (HERE / "p5_c2_v12_source_lineage_route.py").is_file():
        raise RuntimeError("V12 route adapter missing")

    c2 = next(row for row in acceptance["receipts"] if row["arm_code"] == "C2")
    if c2["before"] != {"bound": 7, "blocking": 14} or c2["after_shared_core_only"] != {"bound": 9, "blocking": 12}:
        raise RuntimeError("V6 explicit C2 acceptance arithmetic changed")
    if [field for field in c2["field_bindings"] if c2["field_bindings"][field]["status"] == "BOUND"] != TARGET_FIELDS:
        raise RuntimeError("V6 explicit C2 acceptance field set changed")

    protocol = {
        "schema_version": "orion.p5.c2.source-native-rights-lineage-protocol.v12",
        "protocol_id": PROTOCOL_ID,
        "frozen_at_utc": FROZEN_AT,
        "successor_identity": IDENTITY,
        "authority": "SOURCE_NATIVE_CANDIDATE_VISIBLE_BYTES_RIGHTS_AND_LINEAGE_ONLY",
        "development_question": "Can the exact six-component V6 source-native public-development core be routed with complete rights and provenance under a distinct C2 successor without inheriting V11 runtime closure or released MOSS identity?",
        "atomic_questions": [
            "Do all six candidate-visible components match exact path, size and SHA-256?",
            "Does their canonical aggregate match the V6 core digest?",
            "Does the source archive reproduce the 302-file commit/tree manifest?",
            "Do Apache-2.0, NOTICE and CC0 bytes bind to the exact listed components?",
            "Are fixed source, fix patch, generated evaluator, native arm data, model/service bytes and outcomes excluded?",
            "Does the V6 C2 acceptance contract authorize exactly two fields and no V11 aggregation?",
        ],
        "saturation_assessment": {
            "knowledge": "V4 names the missing C2 case and task-rights fields; V6 supplies an explicit six-arm shared-core acceptance; V11 addresses a disjoint runtime field under a separate successor identity.",
            "search_universe": "Complete frozen V4, V6, V10 and V11 packet bytes plus the content-addressed Apache/Defects4J lineage retained by V6.",
            "formulation": "One source-native root class can lawfully close two co-specified fields, but it cannot close runtime, isolation, provider, custody, compute, container or performance obligations.",
        },
        "saturation_challenge": "V6 local authorship and post-outcome case selection are not independent authority; any native/bundled content substitution reopens rights and byte identity.",
        "frozen_hypothesis": "If all six V6 components, aggregate digest, source tree, rights mappings, exclusions and C2 acceptance arithmetic pass one read-only materialization/destruction gate, exactly the two V6-authorized fields are BOUND for V12 on the C2 V4 basis.",
        "acceptance_rules": [
            "six and only six candidate-visible components materialize read-only",
            "component and aggregate hashes match V6",
            "source commit/tree/archive and control-side mapping lineage match",
            "rights manifest and retained licence/notice hashes match",
            "known fixed bytes and forbidden outcome keys/roots are absent",
            "V12 remains non-aggregated with V11 and distinct from released MOSS",
            "attempt destruction is verified",
        ],
        "reopen_triggers": [
            "any component, aggregate, source-tree, rights or lineage hash changes",
            "any candidate-visible component is added, substituted or made writable",
            "any native/bundled task, model/service, generated artifact, fixed byte or outcome enters the core",
            "V11 runtime closure is inherited without an explicit owner aggregation contract",
            "public-development evidence is promoted to fresh, protected or confirmatory evidence",
        ],
        "forbidden": [
            "C3 or C4 work or validators",
            "MOSS, model, coding-agent, evaluator, benchmark or scorer execution",
            "protected/gold/outcome access",
            "repository CI or test-framework execution",
            "manuscript/claim-ledger edit",
        ],
    }
    write_json(HERE / "P5_C2_V12_FROZEN_PROTOCOL.json", protocol)

    basis = {
        "schema_version": "orion.p5.c2.explicit-shared-core-acceptance-basis.v12",
        "successor_identity": IDENTITY,
        "authority_source": repo_ref(V6 / "P5_SIX_ARM_SHARED_CORE_ACCEPTANCE_V6.json"),
        "authority": acceptance["authority"],
        "c2_receipt": c2,
        "permitted_field_closures": TARGET_FIELDS,
        "count_basis": {
            "source": "C2 V4 twenty-one-field registry as explicitly reproduced by the V6 C2 acceptance receipt",
            "before": {"bound": 7, "blocking": 14},
            "after_source_core_only": {"bound": 9, "blocking": 12},
        },
        "forbidden_aggregation": {
            "v11_successor_identity": v11["successor_identity"],
            "v11_state": {"bound": 8, "blocking": 13},
            "runtime_task_environment_inherited": False,
            "aggregation_with_v11_authorized": False,
            "reason": "No owner contract authorizes unioning closures across the distinct V11 and V12 successor identities.",
        },
        "released_moss_preserved": {"commit": MOSS_COMMIT, "bound": 7, "blocking": 14},
    }
    write_json(HERE / "P5_C2_V12_EXPLICIT_ACCEPTANCE_BASIS.json", basis)

    lineage = {
        "schema_version": "orion.p5.c2.source-rights-lineage-manifest.v12",
        "successor_identity": IDENTITY,
        "case_id": core["case_id"],
        "authority": "EXACT_LISTED_PUBLIC_DEVELOPMENT_BYTES_ONLY",
        "candidate_visible_component_count": core["candidate_visible_component_count"],
        "candidate_visible_bytes": core["candidate_visible_bytes"],
        "candidate_visible_core_sha256": core["candidate_visible_core_sha256"],
        "components": core["components"],
        "source_lineage": {
            "repository": provenance["source_identity"]["apache_repository"],
            "buggy_commit": provenance["source_identity"]["buggy_commit"],
            "buggy_tree": provenance["source_identity"]["buggy_tree"],
            "archive_sha256": SOURCE_SHA,
            "canonical_tree_manifest_sha256": TREE_SHA,
            "regular_file_count": source_tree["regular_file_count"],
            "regular_file_bytes": source_tree["regular_file_bytes"],
        },
        "control_side_provenance": {
            "defects4j_repository": provenance["source_identity"]["defects4j_repository"],
            "defects4j_commit": provenance["source_identity"]["defects4j_commit"],
            "mapping": repo_ref(V6 / "source_provenance/DEFECTS4J-LANG1-SOURCE-MAPPING.csv"),
            "mapping_license": repo_ref(V6 / "source_provenance/DEFECTS4J-MIT-LICENSE.txt"),
            "candidate_visible": False,
        },
        "rights_lineage": {
            "manifest": repo_ref(V6 / "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json"),
            "status": rights["rights_status"],
            "components": rights["components"],
            "legal_advice": rights["legal_advice"],
        },
        "selection_and_outcome_boundary": {
            "selection_is_post_outcome": provenance["predecessor_public_development_evidence"]["selection_is_post_outcome"],
            "known_fixed_commit": provenance["source_identity"]["fixed_commit_known_to_packet_builder"],
            "known_fix_patch_sha256": provenance["source_identity"]["known_public_fix_patch_sha256"],
            "known_public_fix_bytes_in_candidate_core": provenance["source_identity"]["known_public_fix_bytes_in_candidate_core"],
            "authority": "PUBLIC_DEVELOPMENT_ONLY__NOT_FRESH_OR_CONFIRMATORY",
        },
        "explicitly_excluded": rights["explicitly_excluded"],
    }
    write_json(HERE / "P5_C2_V12_SOURCE_RIGHTS_LINEAGE_MANIFEST.json", lineage)

    component_paths = {
        "v6_case_body": V6 / "candidate_visible/CASE_BODY_V6.json",
        "v6_task_specification": V6 / "candidate_visible/TASK_SPECIFICATION_V6.md",
        "v6_source_archive": V6 / "candidate_visible/source/commons-lang-396afc3e4693cfee182efe582455f2d97058c068.tar.gz",
        "v6_apache_license": V6 / "candidate_visible/APACHE-2.0-LICENSE.txt",
        "v6_apache_notice": V6 / "candidate_visible/APACHE-NOTICE.txt",
        "v6_cc0_license": V6 / "candidate_visible/PACKET-CONTENT-CC0-1.0.txt",
    }
    external_inputs = {
        **{name: repo_ref(path) for name, path in component_paths.items()},
        "v6_protocol": repo_ref(V6 / "P5_COMMON_VISIBLE_CASE_RIGHTS_PROTOCOL_V6.json"),
        "v6_core_index": repo_ref(V6 / "P5_SHARED_CASE_CORE_INDEX_V6.json"),
        "v6_rights_manifest": repo_ref(V6 / "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json"),
        "v6_six_arm_acceptance": repo_ref(V6 / "P5_SIX_ARM_SHARED_CORE_ACCEPTANCE_V6.json"),
        "v6_public_provenance": repo_ref(V6 / "P5_PUBLIC_CASE_PROVENANCE_V6.json"),
        "v6_source_tree_manifest": repo_ref(V6 / "P5_SOURCE_TREE_CONTENT_MANIFEST_V6.json"),
        "v6_defects4j_mapping": repo_ref(V6 / "source_provenance/DEFECTS4J-LANG1-SOURCE-MAPPING.csv"),
        "v6_defects4j_license": repo_ref(V6 / "source_provenance/DEFECTS4J-MIT-LICENSE.txt"),
        "v4_c2_registry": repo_ref(V4 / "P5_C2_V4_FIELD_REGISTRY.json"),
        "v10_result": repo_ref(V10 / "P5_C2_V10_RESULT.json"),
        "v11_result": repo_ref(V11 / "P5_C2_V11_RESULT.json"),
    }
    packet_artifacts = {
        "frozen_protocol": packet_ref(HERE / "P5_C2_V12_FROZEN_PROTOCOL.json"),
        "explicit_acceptance_basis": packet_ref(HERE / "P5_C2_V12_EXPLICIT_ACCEPTANCE_BASIS.json"),
        "source_rights_lineage": packet_ref(HERE / "P5_C2_V12_SOURCE_RIGHTS_LINEAGE_MANIFEST.json"),
        "route_adapter": packet_ref(HERE / "p5_c2_v12_source_lineage_route.py"),
    }
    freeze_doc = {
        "schema_version": "orion.p5.c2.source-rights-lineage-execution-freeze.v12",
        "protocol_id": PROTOCOL_ID,
        "frozen_at_utc": FROZEN_AT,
        "successor_identity": IDENTITY,
        "released_moss_identity_claimed": False,
        "aggregation_with_v11_authorized": False,
        "field_targets": TARGET_FIELDS,
        "packet_artifacts": packet_artifacts,
        "external_inputs": external_inputs,
        "required_component_paths": [row["path"] for row in core["components"]],
        "expected_candidate_visible_core_sha256": CORE_SHA,
        "expected_source_tree_manifest_sha256": TREE_SHA,
        "forbidden_keys_recursive": ["protected_score", "gold_patch", "gold", "hidden_panel_id", "expected_patch", "scorer_feedback"],
        "forbidden_attempt_path_components": ["protected", "gold", "hidden_panel", "scorer", "reference_solution", "outcome_cache"],
        "candidate_execution_authorized": False,
        "outcome_execution_authorized": False,
        "expected_terminal": "P5_C2_V12_SIX_OF_SIX_SOURCE_NATIVE_COMPONENTS_PASS__CORE_RIGHTS_AND_LINEAGE_BOUND__DISTINCT_NONAGGREGATED_SUCCESSOR__NO_OUTCOME_EXECUTED",
    }
    write_json(HERE / "P5_C2_V12_EXECUTION_FREEZE.json", freeze_doc)
    print("P5_C2_V12_EXECUTION_FREEZE_SEALED")


def finalize() -> None:
    freeze_doc = load(HERE / "P5_C2_V12_EXECUTION_FREEZE.json")
    for ref in freeze_doc["packet_artifacts"].values():
        path = HERE / ref["path"]
        if sha256(path) != ref["sha256"] or path.stat().st_size != ref["size_bytes"]:
            raise RuntimeError(f"frozen packet artifact drifted: {path}")
    for ref in freeze_doc["external_inputs"].values():
        path = REPO_ROOT / ref["path"]
        if sha256(path) != ref["sha256"] or path.stat().st_size != ref["size_bytes"]:
            raise RuntimeError(f"frozen external input drifted: {path}")
    receipt = load(HERE / "P5_C2_V12_SOURCE_LINEAGE_ROUTE_RECEIPT.json")
    if not (
        receipt["status"] == "PASS"
        and receipt["required_component_count"] == 6
        and receipt["mounted_component_count"] == 6
        and receipt["candidate_visible_core_sha256"] == CORE_SHA
        and receipt["source_tree_manifest_sha256"] == TREE_SHA
        and receipt["attempt_destruction_verified"] is True
    ):
        raise RuntimeError("V12 frozen route gate did not pass")
    expected_executed = {
        "benchmark": False,
        "coding_agent": False,
        "evaluator": False,
        "model": False,
        "moss": False,
        "protected_data": False,
        "repository_ci": False,
        "route_gate": True,
        "scorer": False,
        "test_framework": False,
    }
    if receipt["executed"] != expected_executed:
        raise RuntimeError("V12 route execution boundary changed")

    registry = load(V4 / "P5_C2_V4_FIELD_REGISTRY.json")
    remaining_fields = [field for field in registry["blocking_fields"] if field not in TARGET_FIELDS]
    if len(remaining_fields) != 12:
        raise RuntimeError("V12 two-field arithmetic failed")
    result = {
        "schema_version": "orion.p5.c2.source-native-rights-lineage-result.v12",
        "protocol_id": PROTOCOL_ID,
        "successor_identity": IDENTITY,
        "status": "BOUND_TWO_SOURCE_NATIVE_FIELDS_FOR_DISTINCT_SUCCESSOR",
        "field_instances_closed": 2,
        "closed_fields": TARGET_FIELDS,
        "route_receipt": packet_ref(HERE / "P5_C2_V12_SOURCE_LINEAGE_ROUTE_RECEIPT.json"),
        "count_basis": {
            "authority": "V6_EXPLICIT_C2_SHARED_CORE_ACCEPTANCE_ON_C2_V4_TWENTY_ONE_FIELD_BASIS",
            "before": {"bound": 7, "blocking": 14},
            "after_v12_source_core_only": {"bound": 9, "blocking": 12},
        },
        "identity_frontier": {
            "released_moss": {"commit": MOSS_COMMIT, "bound": 7, "blocking": 14, "unchanged": True},
            "v11_distinct_runtime_successor": {"identity": "C2_LAWFUL_NATIVE_BYTE_SUCCESSOR__ORION_V11", "bound": 8, "blocking": 13, "inherited": False},
            "v12_distinct_source_core_successor": {"identity": IDENTITY, "bound": 9, "blocking": 12},
            "aggregation_authorized": False,
            "comparison_note": "V11 and V12 close different field sets and are not a cumulative version chain; their counts must not be unioned.",
        },
        "v12_runtime_task_environment": "BLOCKING__V11_CLOSURE_NOT_INHERITED",
        "authority_boundary": "POST_OUTCOME_PUBLIC_DEVELOPMENT_SOURCE_BYTES_AND_RIGHTS_ONLY__NOT_FRESH_CONFIRMATORY_OR_PERFORMANCE",
        "panel_and_claim_boundaries": {
            "ready_arms": "0/6",
            "global_panel_field_delta": "NOT_CLAIMED__SEPARATE_IDENTITY_COUNT_BASIS",
            "H1": "CANNOT_CHECK",
            "H2": "CANNOT_CHECK",
            "H3": "CANNOT_CHECK",
            "H4": "CANNOT_CHECK",
            "performance": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
            "top_tier_peer_review_ready": "NOT_ESTABLISHED",
        },
        "manuscript_or_claim_ledger_edited": False,
        "next_discriminator": "The next exact source-native lane is rights.container_and_generated_artifacts, but it requires a rights-cleared disposable Linux image build and complete SBOM/licence/generated-artifact authority; do not infer it from V12 source-core rights.",
        "terminal": "P5_C2_V12_SOURCE_NATIVE_CORE_RIGHTS_AND_LINEAGE_BOUND__TWO_EXACT_FIELDS_CLOSED__DISTINCT_SUCCESSOR_NINE_OF_TWENTY_ONE_BOUND__TWELVE_BLOCKING__V11_NOT_AGGREGATED__RELEASED_MOSS_UNCHANGED__ZERO_OF_SIX_READY__PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK",
    }
    write_json(HERE / "P5_C2_V12_RESULT.json", result)

    rows: list[dict[str, Any]] = [
        {
            "id": "P5.C2.V12.IDENTITY.NONAGGREGATION",
            "negative_result": "V11 runtime closure and V12 source-core closure belong to distinct successor identities.",
            "positive_resolution": "V12 records a three-node identity frontier and forbids arithmetic union without an owner aggregation contract.",
            "residual": "No cumulative successor currently combines the V11 and V12 field sets.",
            "next_discriminator": "Obtain an explicit owner contract that names the exact predecessor hashes and authorizes a union transition, then revalidate every inherited field in one frozen route.",
        },
        {
            "id": "P5.C2.V12.POST.OUTCOME.BOUNDARY",
            "negative_result": "The V6 public-development case was selected after its public fix and predecessor outcomes were known.",
            "positive_resolution": "Exact source, rights and lineage are now routed without importing fixed bytes or hiding the selection boundary.",
            "residual": "V12 cannot support freshness, confirmatory, performance or superiority claims.",
            "next_discriminator": "Freeze a source-disjoint case prospectively under independent custody after protocol lock.",
        },
    ]
    for field in remaining_fields:
        entry = registry["fields"][field]
        rows.append(
            {
                "id": "P5.C2.V12.REMAINING." + field.upper().replace(".", "_"),
                "field": field,
                "negative_result": entry["cause"],
                "positive_resolution": "This obligation is separated from the now-bound source-core bytes/rights/lineage class and remains an independently testable lane.",
                "residual": entry["residual"],
                "next_discriminator": entry["next_discriminator"],
            }
        )
    ledger = {
        "schema_version": "orion.p5.c2.recursive-negative-ledger.v12",
        "successor_identity": IDENTITY,
        "resolved_in_v12": TARGET_FIELDS,
        "remaining_successor_blocker_count": 12,
        "entries": rows,
    }
    write_json(HERE / "P5_C2_V12_RECURSIVE_NEGATIVE_LEDGER.json", ledger)
    md = [
        "# P5 C2 V12 recursive negative-result ledger",
        "",
        "| ID | Negative result | Positive resolution | Residual | Next discriminator |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        clean = lambda value: str(value or "").replace("|", "\\|").replace("\n", " ")
        md.append("| " + " | ".join(clean(row[key]) for key in ("id", "negative_result", "positive_resolution", "residual", "next_discriminator")) + " |")
    write_text(HERE / "P5_C2_V12_RECURSIVE_NEGATIVE_LEDGER.md", "\n".join(md))

    report = f"""# P5 C2 source-native core, rights and lineage successor V12

## Terminal

`{result['terminal']}`

## Positive closure

V12 materializes the exact V6 six-component candidate-visible core as a
read-only route: authored case body, authored task specification, the complete
buggy Apache Commons Lang source archive, Apache-2.0 licence, Apache NOTICE and
CC0-1.0 authored-content licence. All six components match path, size and
SHA-256; their canonical aggregate matches `{CORE_SHA}` across 703,610 bytes.
The source archive independently reproduces the 302-file commit/tree manifest
`{TREE_SHA}`.

The V6 C2 acceptance receipt explicitly maps this core to exactly
`inputs.candidate_visible_case_bytes` and
`rights.task_and_benchmark_content`. V12's frozen gate passes 6/6 components,
retains all exclusions, keeps the complete mount read-only and verifies attempt
destruction. On that explicit C2 V4 basis, the distinct V12 successor is **9/21
bound and 12/21 blocking**.

## Non-aggregation and released identity

V12 does not inherit V11's `runtime.task_environment` closure. V11 remains a
distinct 8/21 runtime successor; V12 is a distinct 9/21 source-core successor;
released MOSS at `{MOSS_COMMIT}` remains 7/21 bound and 14/21 blocking. These
three identities are not arithmetically unioned, ranked or presented as a
cumulative version chain.

## Scientific boundary

V6 case selection is known post-outcome. Known fixed source/patch bytes,
Defects4J generated environments/evaluators, native arm data, generated solver
outputs, models/services and protected/scorer material remain excluded. Only
the route gate ran: no MOSS, model, coding agent, evaluator, benchmark, scorer,
protected datum, CI or test framework was executed. Thus 0/6 arms are ready;
H1-H4, performance and superiority remain `CANNOT_CHECK`; top-tier readiness
is not established. No manuscript or claim ledger was edited.

## Next discriminator

The remaining source-adjacent right is
`rights.container_and_generated_artifacts`. Closing it requires a
rights-cleared disposable Linux build, complete image SBOM/licence bundle and
explicit session/transcript/diff/image/evolution-state retention and
publication authority. V12 source-core rights cannot be promoted into that
separate field.
"""
    write_text(HERE / "SCIENTIFIC_REPORT_V12.md", report)
    readme = """# P5 C2 source-native core, rights and lineage successor V12

Start with `SCIENTIFIC_REPORT_V12.md`, `P5_C2_V12_RESULT.json`, and
`P5_C2_V12_SOURCE_LINEAGE_ROUTE_RECEIPT.json`.

V12 is a distinct non-aggregated source-core successor. It binds exactly two
V6-authorized fields on the C2 V4 basis; it does not inherit V11 runtime state
or modify released MOSS.

Execution-free reproduction order:

1. `python build_p5_c2_v12_packet.py --phase freeze`
2. `python p5_c2_v12_source_lineage_route.py`
3. `python build_p5_c2_v12_packet.py --phase finalize`
4. `python validate_p5_c2_v12_packet.py`
"""
    write_text(HERE / "README.md", readme)

    excluded = {"ARTIFACT_MANIFEST_V12.json", "SHA256SUMS"}
    artifacts = [packet_ref(path) for path in sorted(HERE.rglob("*")) if path.is_file() and path.name not in excluded and "__pycache__" not in path.parts]
    write_json(
        HERE / "ARTIFACT_MANIFEST_V12.json",
        {
            "schema_version": "orion.p5.c2.artifact-manifest.v12",
            "successor_identity": IDENTITY,
            "artifact_count": len(artifacts),
            "artifacts": artifacts,
            "exclusions": ["ARTIFACT_MANIFEST_V12.json (self-reference)", "SHA256SUMS (generated after manifest)"],
        },
    )
    paths = [path for path in sorted(HERE.rglob("*")) if path.is_file() and path.name != "SHA256SUMS" and "__pycache__" not in path.parts]
    write_text(HERE / "SHA256SUMS", "\n".join(f"{sha256(path)}  {path.relative_to(HERE).as_posix()}" for path in paths))
    print(result["terminal"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("freeze", "finalize"), required=True)
    args = parser.parse_args()
    if args.phase == "freeze":
        freeze()
    else:
        finalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
