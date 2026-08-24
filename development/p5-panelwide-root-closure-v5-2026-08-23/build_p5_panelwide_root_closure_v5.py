#!/usr/bin/env python3
"""Build the P5 V5 panel-wide root-cause closure packet.

This builder is outcome blind.  It reads only the six V4 execution-binding
packets and the already-frozen six-arm identity ledger.  It never opens a
protected outcome, model, task/benchmark payload, or comparator output.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DATE = "2026-08-23"

ARM_INPUTS = [
    ("C1", "development/p5-swe-agent-execution-binding-v4-2026-08-23"),
    ("C2", "development/p5-moss-execution-binding-v4-2026-08-23"),
    ("C3", "development/p5-dgm-execution-binding-v4-2026-08-23"),
    ("C4", "development/p5-adias-execution-binding-v4-2026-08-23"),
    ("C5", "development/p5-double-ratchet-execution-binding-v4-2026-08-23"),
    ("C6", "development/p5-scienceclaw-execution-binding-v4-2026-08-23"),
]

IDENTITY_LEDGER = (
    "development/p5-six-arm-comparator-panel-2026-08-23/"
    "P5_SIX_ARM_COMPARATOR_IDENTITY_LEDGER_V2.json"
)
PUBLIC_PANEL_PROTOCOL = (
    "development/p5-six-arm-comparator-panel-2026-08-23/"
    "P5_OUTCOME_BLIND_COMPARATOR_AND_PUBLIC_PANEL_PROTOCOL_V1.json"
)

TERMINAL = (
    "P5_V5_PANELWIDE_ROOT_CAUSE_CONTRACT_AND_SIX_PARSER_DISPATCH_BOUND__"
    "EIGHTY_FOUR_BLOCKER_INSTANCES_COLLAPSED_TO_FIVE_ROOT_WORK_PACKAGES__"
    "ZERO_ARM_FIELD_BINDINGS_CREATED_WITHOUT_MISSING_EXTERNAL_OR_ARM_SPECIFIC_EVIDENCE__"
    "FORTY_TWO_OF_ONE_HUNDRED_TWENTY_SIX_FIELDS_BOUND__EIGHTY_FOUR_BLOCKING__"
    "ZERO_OF_SIX_READY__PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def status(entry: dict[str, Any]) -> str:
    raw = entry.get("state", entry.get("status"))
    return "BOUND" if raw == "BOUND" else "BLOCKING"


def parser_sha(binding: dict[str, Any]) -> str:
    return binding.get("sha256") or binding["parser_sha256"]


def parser_path(binding: dict[str, Any]) -> str:
    return binding.get("path") or binding["parser"]


def arm_files(arm_code: str, directory: Path) -> tuple[Path, Path]:
    fields = directory / f"P5_{arm_code}_V4_FIELD_REGISTRY.json"
    result = directory / f"P5_{arm_code}_V4_RESULT.json"
    if not fields.exists() or not result.exists():
        raise FileNotFoundError(f"missing V4 packet inputs for {arm_code}: {directory}")
    return fields, result


def build() -> None:
    identity = json.loads((ROOT / IDENTITY_LEDGER).read_text())
    public_protocol = json.loads((ROOT / PUBLIC_PANEL_PROTOCOL).read_text())
    if len(identity["arms"]) != 6 or public_protocol["governing_endpoint"]["comparator_count"] != 6:
        raise AssertionError("the governing panel is not six-arm")

    arms: list[dict[str, Any]] = []
    all_required: list[str] | None = None
    blocker_fanout: Counter[str] = Counter()
    input_snapshot: list[dict[str, Any]] = []

    packet_manifest_verification: dict[str, dict[str, Any]] = {}
    for arm_code, rel_dir in ARM_INPUTS:
        directory = ROOT / rel_dir
        fields_path, result_path = arm_files(arm_code, directory)
        registry = json.loads(fields_path.read_text())
        result = json.loads(result_path.read_text())
        required = sorted(registry["fields"])
        if len(required) != 21:
            raise AssertionError(f"{arm_code} does not have exactly 21 fields")
        if all_required is None:
            all_required = required
        elif required != all_required:
            raise AssertionError(f"{arm_code} field universe differs from C1")

        recomputed_bound = sorted(k for k, v in registry["fields"].items() if status(v) == "BOUND")
        recomputed_blocking = sorted(k for k, v in registry["fields"].items() if status(v) == "BLOCKING")
        if registry["bound_field_count"] != len(recomputed_bound):
            raise AssertionError(f"{arm_code} bound count is internally inconsistent")
        if registry["blocking_field_count"] != len(recomputed_blocking):
            raise AssertionError(f"{arm_code} blocker count is internally inconsistent")
        blocker_fanout.update(recomputed_blocking)

        pbind = registry["fields"]["adapter.native_parser_binding"]["binding"]
        ppath = directory / parser_path(pbind)
        psha = parser_sha(pbind)
        if sha256(ppath) != psha:
            raise AssertionError(f"{arm_code} parser bytes do not match its V4 field binding")

        packet_files = sorted(p for p in directory.iterdir() if p.is_file())
        packet_manifest = [
            {
                "path": str(p.relative_to(ROOT)),
                "sha256": sha256(p),
                "size_bytes": p.stat().st_size,
            }
            for p in packet_files
        ]
        listed_checksums = []
        checksum_failures = []
        for line in (directory / "SHA256SUMS").read_text().splitlines():
            expected, name = line.split("  ", 1)
            actual = sha256(directory / name)
            listed_checksums.append(name)
            if actual != expected:
                checksum_failures.append({"path": name, "expected_sha256": expected, "actual_sha256": actual})
        packet_manifest_verification[arm_code] = {
            "status": "PASS" if not checksum_failures else "CANNOT_CHECK_MANIFEST_MISMATCH",
            "listed_entries": len(listed_checksums),
            "failures": checksum_failures,
        }
        arms.append(
            {
                "arm_code": arm_code,
                "arm_id": registry["arm_id"],
                "v4_registry_path": str(fields_path.relative_to(ROOT)),
                "v4_registry_sha256": sha256(fields_path),
                "v4_result_path": str(result_path.relative_to(ROOT)),
                "v4_result_sha256": sha256(result_path),
                "v4_terminal": result["terminal"],
                "bound_fields": recomputed_bound,
                "blocking_fields": recomputed_blocking,
                "bound_field_count": len(recomputed_bound),
                "blocking_field_count": len(recomputed_blocking),
                "execution_ready": False,
                "parser": {
                    "path": str(ppath.relative_to(ROOT)),
                    "sha256": psha,
                    "panel_dispatch_status": "BOUND_FROM_V4_BYTES",
                },
                "wallclock_binding": registry["fields"]["resources.wallclock"]["binding"],
                "packet_file_count": len(packet_files),
            }
        )
        input_snapshot.extend(packet_manifest)

    assert all_required is not None
    if sum(a["blocking_field_count"] for a in arms) != 84:
        raise AssertionError("expected the six V4 packets to contain exactly 84 blocking instances")
    if sum(a["bound_field_count"] for a in arms) != 42:
        raise AssertionError("expected the six V4 packets to contain exactly 42 bound instances")

    field_equivalence = [
        {
            "equivalence_id": "E1_EXTERNAL_CUSTODY_TRIPLET",
            "fields": [
                "custody.external_protected_scorer",
                "custody.one_shot_no_feedback_barrier",
                "custody.protected_panel_freshness",
            ],
            "arm_count": 6,
            "blocking_instances": 18,
            "closure_scope": "ONE_SIGNED_PANEL_BUNDLE_NAMING_ALL_SIX_ARMS",
            "current_status": "BLOCKING_EXTERNAL_EVIDENCE_ABSENT",
            "anti_inflation_rule": "Schema and local signature-checking code cannot establish custodian independence, freshness, or no feedback.",
        },
        {
            "equivalence_id": "E2_CANDIDATE_VISIBLE_CASE",
            "fields": ["inputs.candidate_visible_case_bytes"],
            "arm_count": 6,
            "blocking_instances": 6,
            "closure_scope": "ONE_SHARED_BYTE_MANIFEST_PLUS_SIX_NATIVE_ACCEPTANCE_RECEIPTS",
            "current_status": "BLOCKING_NO_SUBSTANTIVE_RIGHTS_CLEARED_P5_PACKET",
        },
        {
            "equivalence_id": "E3_PRIMARY_MODEL_ROLE_MAP",
            "fields": ["model_provider.primary"],
            "arm_count": 6,
            "blocking_instances": 6,
            "closure_scope": "SHARED_PROVIDER_CORE_ONLY_IF_EVERY_NATIVE_ROLE_IS_EXACTLY_COVERED",
            "current_status": "BLOCKING_MODEL_PROVIDER_AND_ROLE_IDENTITIES_ABSENT",
        },
        {
            "equivalence_id": "E4_AGGREGATE_CALL_TOKEN_USD_METER",
            "fields": ["resources.calls_tokens_usd"],
            "arm_count": 6,
            "blocking_instances": 6,
            "closure_scope": "ONE_PANEL_METER_SPEC_PLUS_SIX_PROVIDER_RECONCILIATIONS",
            "current_status": "BLOCKING_PRIMARY_PROVIDER_AND_ENFORCEMENT_ABSENT",
        },
        {
            "equivalence_id": "E5_DENY_DEFAULT_EGRESS_AND_RETRY",
            "fields": ["resources.retry_network"],
            "arm_count": 6,
            "blocking_instances": 6,
            "closure_scope": "ONE_POLICY_PLUS_SIX_COMPLETE_PROCESS_TREE_RECEIPTS",
            "current_status": "BLOCKING_ENDPOINTS_AND_EXECUTOR_ENFORCEMENT_ABSENT",
        },
        {
            "equivalence_id": "E6_CONTAINER_AND_GENERATED_ARTIFACT_RIGHTS",
            "fields": ["rights.container_and_generated_artifacts"],
            "arm_count": 6,
            "blocking_instances": 6,
            "closure_scope": "COMMON_DISPOSITION_TEMPLATE_PLUS_SIX_IMAGE_SBOMS_AND_ARTIFACT_GRANTS",
            "current_status": "BLOCKING_EXTERNAL_RIGHTS_AND_ARM_IMAGES_ABSENT",
        },
        {
            "equivalence_id": "E7_MODEL_AND_SERVICE_RIGHTS",
            "fields": ["rights.model_provider_and_services"],
            "arm_count": 6,
            "blocking_instances": 6,
            "closure_scope": "ONE_SERVICE_BUNDLE_ONLY_IF_IDENTICAL_PROVIDER_TERMS_COVER_EVERY_ROLE",
            "current_status": "BLOCKING_PROVIDER_SELECTION_AND_TERMS_ABSENT",
        },
        {
            "equivalence_id": "E8_TASK_AND_BENCHMARK_CONTENT_RIGHTS",
            "fields": ["rights.task_and_benchmark_content"],
            "arm_count": 6,
            "blocking_instances": 6,
            "closure_scope": "ONE_AUTHORED_OR_LICENSED_P5_PACKET_PLUS_ARM_COMPONENT_INVENTORIES",
            "current_status": "BLOCKING_RIGHTS_GRANTS_ABSENT",
        },
        {
            "equivalence_id": "E9_CONTENT_ADDRESSED_RUNTIME",
            "fields": ["runtime.container_or_environment"],
            "arm_count": 6,
            "blocking_instances": 6,
            "closure_scope": "SIX_ARM_SPECIFIC_IMAGES_OR_ENVIRONMENTS_UNDER_ONE_RECEIPT_SCHEMA",
            "current_status": "BLOCKING_ARM_RUNTIME_BYTES_ABSENT",
        },
        {
            "equivalence_id": "E10_NATIVE_TASK_ENVIRONMENT",
            "fields": ["runtime.task_environment"],
            "arm_count": 6,
            "blocking_instances": 6,
            "closure_scope": "ONE_SHARED_CASE_CORE_PLUS_SIX_ARM_NATIVE_ENVIRONMENT_MANIFESTS",
            "current_status": "BLOCKING_CASE_AND_ARM_ENVIRONMENT_BYTES_ABSENT",
        },
        {
            "equivalence_id": "E11_ISOLATED_WRITE_SURFACE",
            "fields": ["adapter.isolated_write_surface"],
            "arm_count": 4,
            "blocking_instances": 4,
            "closure_scope": "ONE_OUTER_CAPSULE_POLICY_PLUS_C2_C3_C4_C6_COMPLETE_DESCENDANT_RECEIPTS",
            "current_status": "BLOCKING_DISPOSABLE_EXECUTOR_PROOF_ABSENT",
        },
        {
            "equivalence_id": "E12_AGGREGATE_COMPUTE",
            "fields": ["runtime.compute"],
            "arm_count": 4,
            "blocking_instances": 4,
            "closure_scope": "ONE_CAP_VECTOR_PLUS_C2_C3_C4_C6_PROCESS_DAEMON_REMOTE_WORK_RECEIPTS",
            "current_status": "BLOCKING_EXECUTOR_ENFORCEMENT_ABSENT",
        },
        {
            "equivalence_id": "E13_DEPENDENCY_LOCK",
            "fields": ["runtime.dependency_lock"],
            "arm_count": 3,
            "blocking_instances": 3,
            "closure_scope": "C3_C4_C6_ARM_SPECIFIC_HASH_COMPLETE_LOCKS",
            "current_status": "BLOCKING_RESOLVED_LOCKS_ABSENT",
        },
        {
            "equivalence_id": "E14_SCIENCECLAW_FALLBACKS",
            "fields": ["model_provider.fallbacks"],
            "arm_count": 1,
            "blocking_instances": 1,
            "closure_scope": "SEPARATELY_NAMED_C6_FAIL_FAST_SUCCESSOR_BYTES",
            "current_status": "BLOCKING_NATIVE_FALLBACKS_RETAINED",
        },
    ]

    work_packages = [
        {
            "root_id": "R1_INDEPENDENT_PANEL_CUSTODY",
            "equivalence_ids": ["E1_EXTERNAL_CUSTODY_TRIPLET"],
            "blocking_instances": 18,
            "shared_artifact_fanout": 18,
            "status": "CONTRACT_IMPLEMENTED__INDEPENDENT_SIGNED_EVIDENCE_ABSENT",
            "next_discriminator": "An independent principal signs one post-protocol six-arm panel/scorer/freshness/no-feedback bundle accepted by the V5 gate.",
        },
        {
            "root_id": "R2_COMMON_CASE_RIGHTS_AND_NATIVE_TASK_ADAPTATION",
            "equivalence_ids": ["E2_CANDIDATE_VISIBLE_CASE", "E8_TASK_AND_BENCHMARK_CONTENT_RIGHTS", "E10_NATIVE_TASK_ENVIRONMENT"],
            "blocking_instances": 18,
            "shared_artifact_fanout": 12,
            "status": "CONTRACT_IMPLEMENTED__SUBSTANTIVE_PACKET_RIGHTS_AND_SIX_ENVIRONMENTS_ABSENT",
            "next_discriminator": "Author or license one substantive P5 candidate-visible packet and bind its byte/rights manifest before producing six native environment receipts.",
        },
        {
            "root_id": "R3_MODEL_SERVICE_METERING_EGRESS_AND_FALLBACKS",
            "equivalence_ids": ["E3_PRIMARY_MODEL_ROLE_MAP", "E4_AGGREGATE_CALL_TOKEN_USD_METER", "E5_DENY_DEFAULT_EGRESS_AND_RETRY", "E7_MODEL_AND_SERVICE_RIGHTS", "E14_SCIENCECLAW_FALLBACKS"],
            "blocking_instances": 25,
            "shared_artifact_fanout": 12,
            "status": "CONTRACT_IMPLEMENTED__PROVIDER_ROLE_RIGHTS_ENDPOINTS_METER_AND_C6_SUCCESSOR_ABSENT",
            "next_discriminator": "Select exact role-complete provider identities and terms, then deploy one deny-default metering broker; C6 additionally needs separately named fail-fast bytes.",
        },
        {
            "root_id": "R4_CONTENT_ADDRESSED_RUNTIME_DEPENDENCIES_AND_ARTIFACT_RIGHTS",
            "equivalence_ids": ["E6_CONTAINER_AND_GENERATED_ARTIFACT_RIGHTS", "E9_CONTENT_ADDRESSED_RUNTIME", "E13_DEPENDENCY_LOCK"],
            "blocking_instances": 15,
            "shared_artifact_fanout": 0,
            "status": "COMMON_SCHEMA_IMPLEMENTED__ARM_SPECIFIC_IMAGES_LOCKS_SBOMS_AND_GRANTS_ABSENT",
            "next_discriminator": "Resolve C3/C4/C6 locks, then build and SBOM six content-addressed runtimes with complete generated-artifact dispositions.",
        },
        {
            "root_id": "R5_OUTER_CAPSULE_ISOLATION_AND_COMPUTE",
            "equivalence_ids": ["E11_ISOLATED_WRITE_SURFACE", "E12_AGGREGATE_COMPUTE"],
            "blocking_instances": 8,
            "shared_artifact_fanout": 8,
            "status": "CONTRACT_IMPLEMENTED__DISPOSABLE_EXECUTOR_AND_COMPLETE_DESCENDANT_RECEIPTS_ABSENT",
            "next_discriminator": "Provision one reproducible outer-capsule design and produce per-arm receipts covering child processes, Docker daemons, caches, devices, schedulers and remote work.",
        },
    ]
    if sum(x["blocking_instances"] for x in field_equivalence) != 84:
        raise AssertionError("equivalence classes are not an exact partition of 84 blockers")
    if sum(x["blocking_instances"] for x in work_packages) != 84:
        raise AssertionError("root work packages are not an exact partition of 84 blockers")

    parser_registry = [
        {"arm_code": a["arm_code"], "arm_id": a["arm_id"], **a["parser"]}
        for a in arms
    ]

    protocol = {
        "schema_version": "orion.p5.panelwide-root-closure-protocol.v5",
        "protocol_id": "P5.SIX_ARM.PANELWIDE.ROOT.CLOSURE.V5",
        "paper_id": "P5",
        "frozen_at_utc": f"{DATE}T19:19:11Z",
        "freeze_semantics": "PROSPECTIVE_BEFORE_ANY_P5_CONFIRMATORY_ARM_EXECUTION_OR_PROTECTED_OUTCOME_ACCESS",
        "authority": "OUTCOME_BLIND_CONTROL_PLANE_CONTRACT_AND_V4_STATUS_RECOMPUTATION_ONLY",
        "outcomes_accessed": False,
        "protected_outcomes_accessed": False,
        "models_accessed_or_executed": False,
        "benchmarks_accessed_or_executed": False,
        "arm_executions_performed": 0,
        "grants_performance_authority": False,
        "governing_identity_ledger": {"path": IDENTITY_LEDGER, "sha256": sha256(ROOT / IDENTITY_LEDGER)},
        "governing_public_panel_protocol": {"path": PUBLIC_PANEL_PROTOCOL, "sha256": sha256(ROOT / PUBLIC_PANEL_PROTOCOL)},
        "required_field_paths": all_required,
        "evidence_promotion_rule": (
            "A panel artifact fans out to an arm field only when the same bytes logically satisfy that field for that arm, "
            "the arm-specific acceptance receipt validates, and every required external or arm-native fact is present. "
            "A protocol, schema, placeholder, local assertion, or another arm's receipt is never promoted."
        ),
        "common_execution_contract": {
            "preflight": [
                "Verify all six frozen arm identities, source/result/field-registry hashes and parser hashes.",
                "Require one common candidate-visible packet digest and prohibit protected, gold, scorer and prior-outcome payloads.",
                "Require six arm-native environment/image manifests and six acceptance receipts.",
                "Refuse all arm execution until every one of the 126 arm-field instances is BOUND.",
            ],
            "outer_capsule": [
                "One disposable capsule per arm; no shared mutable state between arms.",
                "Read-only source and case mounts; scratch-only candidate writes; output is terminal-only and append-only.",
                "Deny protected, scorer, sibling, host-promotion, device, scheduler and undeclared credential surfaces.",
                "Account for every descendant process, nested container/daemon, cache, subprocess, service call and remote job.",
                "Require before/after digests, egress log, cgroup/resource receipt, cleanup receipt and typed timeout/budget terminals.",
            ],
            "anti_shortcut": "Wrapper source without a matching executor receipt does not bind isolation, compute, runtime, network, or task-environment fields.",
        },
        "common_resource_contract": {
            "matched_values": "MUST_BE_FILLED_ONCE_AFTER_CASE_AND_PROVIDER_SELECTION_AND_THEN_BYTE_FROZEN",
            "required_caps": [
                "whole-arm and per-case wallclock plus termination grace",
                "aggregate provider calls, input tokens, output tokens and USD with pre-call refusal and overshoot semantics",
                "CPU, RAM, PID, disk, GPU and aggregate parallelism across every local descendant and daemon",
                "finite retries and timeouts by role",
                "deny-default egress with exact DNS/IP/TLS/service identities and no background/remote work",
            ],
            "comparability_rule": "Nominal equality is insufficient; effective capability and accounting coverage must be adjudicated for each native role.",
            "anti_shortcut": "Unselected providers, tokenizers, prices, endpoints or executors make the corresponding fields BLOCKING.",
        },
        "common_parser_contract": {
            "parser_count": 6,
            "dispatch_registry": parser_registry,
            "terminal_policy": "Retain native invalid, error, timeout, abstention and UNRESOLVED; emit no protected score or invented singleton.",
            "status": "BOUND_FROM_SIX_EXISTING_V4_PARSER_BINDINGS__NO_NEW_ARM_FIELD_DELTA",
        },
        "common_custody_contract": {
            "one_bundle_can_target_field_instances": 18,
            "required_external_facts": [
                "independent custodian principal and signing key",
                "protected panel commitment, selection nonce and post-protocol freshness attestation",
                "immutable external scorer code/data digest and access-control identity",
                "one accepted frozen candidate terminal per arm and exactly one score event",
                "proof that protected inputs, diagnostics, scores and outcomes never returned to candidate/adaptation custody",
                "terminal-only signed closing receipt naming all six arm/source/parser/config digests",
            ],
            "anti_self_attestation": "This local repository cannot establish independent custody, panel freshness or absence of a feedback channel. The V5 gate can verify receipt structure and hashes but not institutional independence by itself.",
            "status": "SCHEMA_AND_GATE_BOUND__EXTERNAL_EVIDENCE_ABSENT__EIGHTEEN_ARM_FIELDS_REMAIN_BLOCKING",
        },
        "rights_and_runtime_boundary": (
            "No panel-wide contract projects one source licence, provider term, task grant, image, lockfile, SBOM, "
            "runtime receipt or generated-artifact permission across incompatible arms."
        ),
        "forbidden_promotions": [
            "Do not convert a shared schema into six evidence receipts.",
            "Do not convert a source default into a model/provider/version binding.",
            "Do not convert a base-image digest into a derived runtime/SBOM binding.",
            "Do not convert public accessibility into task, benchmark, service or generated-artifact rights.",
            "Do not convert a local signature or hash check into independent custody or freshness.",
            "Do not execute any arm, model, benchmark or protected scorer under this packet.",
            "Do not promote synthetic/parser conformance into performance, superiority, harm or fresh-transfer evidence.",
        ],
        "terminal": TERMINAL,
    }
    dump(OUT / "P5_PANELWIDE_ROOT_CLOSURE_PROTOCOL_V5.json", protocol)

    cross_arm = {
        "schema_version": "orion.p5.panelwide-blocker-equivalence-registry.v5",
        "registry_id": "P5.V5.PANELWIDE.BLOCKER.EQUIVALENCE.REGISTRY",
        "authority": protocol["authority"],
        "arm_count": 6,
        "fields_per_arm": 21,
        "field_instances_total": 126,
        "v4_bound_instances": 42,
        "v4_blocking_instances": 84,
        "v5_new_arm_field_bindings": 0,
        "v5_bound_instances": 42,
        "v5_blocking_instances": 84,
        "blocker_delta": 0,
        "field_blocker_fanout": dict(sorted(blocker_fanout.items())),
        "equivalence_classes": field_equivalence,
        "root_work_packages": work_packages,
        "matched_exposure_audit": {
            "status": "BLOCKING_COMMON_EFFECTIVE_VECTOR_NOT_YET_FROZEN",
            "wallclock_observation": {
                "C1": "whole=3600s; per-case=3600s; grace=30s",
                "C2": "whole=21600s; per-case=21600s; grace=120s",
                "C3": "whole=21600s; per-case=21600s; grace=120s",
                "C4": "whole=21600s; grace=120s",
                "C5": "whole=21600s; native-candidate-subprocess=10s; grace=120s",
                "C6": "whole=21600s; grace=120s",
            },
            "finding": "All six wallclock fields are individually byte-bound, but C1 differs from C2-C6 and C5 has an additional 10-second native subprocess cap. Individual BOUND status does not establish the panel's matched-exposure condition.",
            "next_discriminator": "After case and provider selection, freeze one common effective resource vector and obtain six arm-native acceptance/coverage receipts; rerun power and estimand checks before execution.",
            "arm_field_delta": 0,
        },
        "arms": arms,
        "input_packet_snapshot_file_count": len(input_snapshot),
        "input_packet_snapshot": input_snapshot,
        "fresh_verification_boundary": {
            "v4_field_registry_result_and_parser_hashes": "PASS_FOR_ALL_SIX",
            "packet_sha256sum_manifests": packet_manifest_verification,
            "native_validator_observations": {
                "C1": {"status": "PASS", "receipt": "P5_C1_V4_VALIDATED__9_BOUND__12_BLOCKING"},
                "C2": {"status": "PASS", "checks_passed": 71},
                "C3": {"status": "PASS", "checks_passed": 134},
                "C4": {
                    "status": "PASS_BUT_REWRITES_AUDIT_RECEIPT_WITH_TEMP_PATH_DERIVED_HASH",
                    "checks_passed": 35,
                    "residual": "Fresh validation changes AUDIT_RECEIPT_V4.json because the smoke metadata hashes a random temporary generation path; the frozen SHA256SUMS entry therefore does not reproduce.",
                },
                "C5": {"status": "PASS", "checks_passed": 351},
                "C6": {
                    "status": "CANNOT_CHECK",
                    "residual": "p5_c6_v4_validator.py requires development/p5-scienceclaw-execution-binding-v4-2026-08-23/.source-audit, which is absent after cleanup.",
                },
            },
            "assurance_claim": "The 84-field recomputation is fresh from JSON and six parser/result/registry digests; full native packet assurance is not uniformly fresh.",
        },
        "terminal": TERMINAL,
    }
    dump(OUT / "P5_PANELWIDE_BLOCKER_EQUIVALENCE_REGISTRY_V5.json", cross_arm)

    negative_records = []
    for wp in work_packages:
        negative_records.append(
            {
                "root_id": wp["root_id"],
                "blocking_instances_before": wp["blocking_instances"],
                "blocking_instances_after": wp["blocking_instances"],
                "arm_field_delta": 0,
                "repair_completed": "A single panel-wide contract, receipt shape, fan-out rule and fail-closed gate now replace duplicated prose.",
                "why_not_promoted": wp["status"],
                "next_discriminator": wp["next_discriminator"],
                "preserved_terminal": "CANNOT_CHECK",
            }
        )
    negative = {
        "schema_version": "orion.p5.panelwide-root-closure-negative-ledger.v5",
        "authority": protocol["authority"],
        "records": negative_records,
        "root_count": 5,
        "blocking_instances_before": 84,
        "blocking_instances_after": 84,
        "arm_field_blocker_delta": 0,
        "efficiency_gain": (
            "The work queue is reduced from 84 repeated arm-field statements to five evidence-producing work packages. "
            "This is coordination compression, not scientific blocker removal."
        ),
        "highest_fanout_next_discriminator": work_packages[0]["next_discriminator"],
        "highest_fanout_directly_authorable_next_discriminator": work_packages[1]["next_discriminator"],
        "assurance_negatives_outside_the_84_field_partition": [
            {
                "id": "P5.V5.ASSURANCE.C4.NONDETERMINISTIC.AUDIT.RECEIPT",
                "state": "CANNOT_CHECK",
                "cause": "C4 native validation rewrites AUDIT_RECEIPT_V4.json with a digest of metadata containing a random temporary path, so its frozen SHA256SUMS entry drifts.",
                "next_discriminator": "Make the smoke metadata path-invariant, regenerate the audit once, freeze SHA256SUMS, then prove two consecutive validator runs are byte-identical.",
            },
            {
                "id": "P5.V5.ASSURANCE.C6.SOURCE.AUDIT.ABSENT",
                "state": "CANNOT_CHECK",
                "cause": "The cleaned C6 packet no longer contains the .source-audit repository required by its native validator.",
                "next_discriminator": "Teach the validator to reconstruct/verify the exact source from its content-addressed manifest without retaining an untracked audit tree, or restore a separately verified immutable source checkout.",
            },
        ],
        "terminal": TERMINAL,
    }
    dump(OUT / "P5_PANELWIDE_ROOT_CLOSURE_NEGATIVE_LEDGER_V5.json", negative)

    result = {
        "schema_version": "orion.p5.panelwide-root-closure-result.v5",
        "protocol_id": protocol["protocol_id"],
        "authority": protocol["authority"],
        "execution": {
            "arm_executions": 0,
            "models_executed": 0,
            "benchmarks_executed": 0,
            "protected_outcomes_accessed": False,
            "confirmatory_ready_arms": 0,
            "required_arms": 6,
        },
        "exact_recomputation": {
            "fields_per_arm": 21,
            "field_instances_total": 126,
            "v4_bound_instances": 42,
            "v4_blocking_instances": 84,
            "v5_new_arm_field_bindings": 0,
            "v5_bound_instances": 42,
            "v5_blocking_instances": 84,
            "blocker_delta": 0,
            "per_arm": {
                a["arm_code"]: {
                    "arm_id": a["arm_id"],
                    "bound": a["bound_field_count"],
                    "blocking": a["blocking_field_count"],
                    "execution_ready": False,
                }
                for a in arms
            },
        },
        "panelwide_repairs": {
            "exact_equivalence_classes": 14,
            "root_work_packages": 5,
            "parser_dispatch_bindings_verified": 6,
            "custody_field_instances_targeted_by_one_external_bundle": 18,
            "arm_field_bindings_created": 0,
            "scientific_blockers_removed": 0,
            "coordination_claim": "84 blocker instances are now an exact, non-overlapping five-package evidence queue.",
            "coordination_work_items_before": 84,
            "coordination_work_items_after": 5,
            "coordination_work_item_delta": -79,
            "coordination_compression_fraction": 0.9404761904761905,
            "matched_exposure_status": "BLOCKING_COMMON_EFFECTIVE_VECTOR_NOT_YET_FROZEN",
        },
        "fresh_verification_boundary": cross_arm["fresh_verification_boundary"],
        "preserved_claims": {
            "H1": "CANNOT_CHECK",
            "H2": "CANNOT_CHECK",
            "H3": "CANNOT_CHECK",
            "H4": "CANNOT_CHECK",
            "fresh_transfer": "CANNOT_CHECK",
            "harm": "CANNOT_CHECK",
            "performance": "CANNOT_CHECK",
            "preservation": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
            "top_tier_publication_readiness": "NOT_ESTABLISHED",
        },
        "highest_fanout_next_discriminator": negative["highest_fanout_next_discriminator"],
        "highest_fanout_directly_authorable_next_discriminator": negative["highest_fanout_directly_authorable_next_discriminator"],
        "terminal": TERMINAL,
    }
    dump(OUT / "P5_PANELWIDE_ROOT_CLOSURE_RESULT_V5.json", result)

    protocol_md = f"""# P5 V5 Panel-wide Root-closure Protocol

**Authority:** `{protocol['authority']}`  
**Freeze:** `{protocol['freeze_semantics']}`  
**Protected outcomes accessed:** no  
**Arm/model/benchmark executions:** 0 / 0 / 0

## Purpose

The six V4 packets expose 84 blocking arm-field instances.  V5 removes duplicated coordination, not adverse evidence: it partitions those 84 instances into 14 exact equivalence classes and five evidence-producing work packages.  A panel artifact may fan out only when the same bytes are logically sufficient for each named arm and each arm-specific acceptance receipt passes.  A schema or local assertion is never evidence of external custody, rights, a runtime, or an arm-native fact.

## Common control plane

1. **Execution:** no arm command may be constructed until all 126 field instances are `BOUND`.  Each arm receives a disposable capsule, read-only source/case inputs, scratch-only writes, complete descendant/daemon accounting, before/after digests, cleanup and typed terminals.
2. **Resources:** one prospectively frozen matched vector must cover wallclock, calls, input/output tokens, USD, CPU, RAM, PIDs, disk, GPU, parallelism, retries and deny-default egress.  The vector remains unfilled until case/provider selection; inventing values now would not bind a real tokenizer, price, endpoint or executor.
3. **Isolation:** wrapper bytes alone do not prove containment.  C2/C3/C4/C6 still require complete executor receipts covering nested Docker, caches, devices, schedulers and remote work.
4. **Parsers:** all six V4 parser byte bindings are reverified and dispatched by arm identity.  Every native invalid/error/timeout/abstention/`UNRESOLVED` terminal is retained; no protected score or singleton is emitted.
5. **Custody:** one externally signed six-arm bundle can close 18 repeated custody instances, but this repository cannot self-attest independence, freshness or no feedback.

## No-inflation boundary

No public availability implies rights.  No source default implies a model identity.  No base image implies a built runtime.  No local hash or signature check implies independent custody.  No parser/conformance receipt implies performance, harm, preservation, fresh transfer or superiority.

## Exact terminal

`{TERMINAL}`
"""
    (OUT / "P5_PANELWIDE_ROOT_CLOSURE_PROTOCOL_V5.md").write_text(protocol_md)

    reg_lines = [
        "# P5 V5 Cross-arm Blocker Equivalence Registry",
        "",
        "## Exact recomputation",
        "",
        "| Arm | Bound / 21 | Blocking / 21 | Ready |",
        "|---|---:|---:|---|",
    ]
    for a in arms:
        reg_lines.append(f"| {a['arm_code']} | {a['bound_field_count']} | {a['blocking_field_count']} | no |")
    reg_lines += [
        "",
        "**Total:** 42/126 bound, 84/126 blocking; 0/6 ready; V5 blocker delta = 0.",
        "",
        "## Exact equivalence classes",
        "",
        "| ID | Blocking instances | Closure scope | Current status |",
        "|---|---:|---|---|",
    ]
    for e in field_equivalence:
        reg_lines.append(f"| {e['equivalence_id']} | {e['blocking_instances']} | {e['closure_scope']} | {e['current_status']} |")
    reg_lines += [
        "",
        "## Five root work packages",
        "",
        "| Root | Instances | One-artifact fan-out | Status |",
        "|---|---:|---:|---|",
    ]
    for w in work_packages:
        reg_lines.append(f"| {w['root_id']} | {w['blocking_instances']} | {w['shared_artifact_fanout']} | {w['status']} |")
    reg_lines += ["", f"Exact terminal: `{TERMINAL}`", ""]
    (OUT / "P5_PANELWIDE_BLOCKER_EQUIVALENCE_REGISTRY_V5.md").write_text("\n".join(reg_lines))

    neg_lines = [
        "# P5 V5 Recursive Negative Ledger",
        "",
        "The five contracts are implemented, but none supplies the missing external or arm-native facts.  Therefore the scientific arm-field blocker delta is exactly zero.",
        "",
        "| Root | Before | After | Why retained | Next discriminator |",
        "|---|---:|---:|---|---|",
    ]
    for r in negative_records:
        neg_lines.append(f"| {r['root_id']} | {r['blocking_instances_before']} | {r['blocking_instances_after']} | {r['why_not_promoted']} | {r['next_discriminator']} |")
    neg_lines += [
        "",
        f"**Highest-fan-out next discriminator (18 fields):** {negative['highest_fanout_next_discriminator']}",
        "",
        f"**Highest-fan-out directly authorable discriminator (12 fields):** {negative['highest_fanout_directly_authorable_next_discriminator']}",
        "",
        "## Assurance negatives outside the 84-field partition",
        "",
        "- **C4:** the native validator is scientifically pass/fail closed, but it rewrites `AUDIT_RECEIPT_V4.json` with a temporary-path-derived metadata hash; the frozen packet manifest therefore does not reproduce.",
        "- **C6:** the native validator cannot run after cleanup because its required `.source-audit` checkout is absent.  The C6 field/result/parser bytes and packet checksum manifest remain readable, but fresh source-level assurance is `CANNOT_CHECK`.",
        "",
        f"Exact terminal: `{TERMINAL}`",
        "",
    ]
    (OUT / "P5_PANELWIDE_ROOT_CLOSURE_NEGATIVE_LEDGER_V5.md").write_text("\n".join(neg_lines))

    report = f"""# P5 V5 Panel-wide Root-closure Scientific Report

## Result

The six authoritative V4 field registries were independently recomputed at 21 fields per arm.  They contain **42 bound and 84 blocking instances**: C1 9/12, C2 7/14, C3 6/15, C4 6/15, C5 9/12, and C6 5/16 (bound/blocking).  V5 verifies all six parser byte bindings and replaces the 84-item duplicated work queue with five non-overlapping root work packages.

The exact arm-field blocker delta is **0**.  This is intentional rather than a failed repair: the repeated high-fan-out fields depend on evidence that is not present and cannot be manufactured locally—independent custody, substantive candidate-visible case rights, provider/service identities and terms, executor receipts, or arm-specific images/locks/environments.  Treating the new schemas as those missing facts would create false readiness.

The 42 individually bound instances also do not establish a matched panel envelope: C1 freezes 3,600 seconds with 30-second grace, C2--C6 freeze 21,600 seconds with 120-second grace, and C5 adds a 10-second native-candidate subprocess cap.  V5 therefore keeps the panel-wide matched-exposure gate blocking until one common effective vector and six native coverage receipts are frozen.

## Efficiency gain

The work is no longer 84 independent repairs:

| Work package | Instances governed | Strongest single-artifact fan-out |
|---|---:|---:|
| Independent panel custody | 18 | 18 |
| Common case, content rights, native task adaptation | 18 | 12 |
| Model/service, metering, egress, fallbacks | 25 | 12 |
| Runtime, dependencies, artifact rights | 15 | 0 (arm-specific evidence) |
| Outer capsule isolation and compute | 8 | 8 |

The highest-fan-out closure is now one signed independent-custody bundle naming all six arms, their parser/source/config hashes, a post-protocol fresh panel, immutable external scorer and a one-shot no-feedback receipt.  If genuine and independently adjudicated, that one bundle targets 18 field instances.  The highest-fan-out directly authorable closure is one substantive rights-cleared P5 visible-case packet, targeting 12 shared input/content-rights instances before six native environment bindings.

## Scientific boundary

No arm, model, benchmark or protected scorer was run.  No comparator output or protected outcome was accessed.  H1--H4, harm, preservation, fresh transfer, performance and superiority remain `CANNOT_CHECK`; P5 remains `NOT_ESTABLISHED` for top-tier submission readiness.

Fresh input assurance has two retained negatives: C4's native validator rewrites its audit receipt using a random temporary-path-derived hash, so the frozen packet checksum does not reproduce; C6's cleaned packet lacks the `.source-audit` checkout required by its native validator.  The six field registries, results and bound parser digests used for the 42/84 recomputation were nevertheless verified directly.

## Exact terminal

`{TERMINAL}`
"""
    (OUT / "SCIENTIFIC_REPORT_V5.md").write_text(report)
    (OUT / "TERMINAL_V5.txt").write_text(TERMINAL + "\n")

    manifest_lines = []
    for path in sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "SHA256SUMS"):
        manifest_lines.append(f"{sha256(path)}  {path.name}")
    (OUT / "SHA256SUMS").write_text("\n".join(manifest_lines) + "\n")


if __name__ == "__main__":
    build()
