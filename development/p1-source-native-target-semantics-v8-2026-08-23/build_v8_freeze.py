#!/usr/bin/env python3
"""Freeze the P1 V8 target-semantics discriminator and owner-algebra schema."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FROZEN = "2026-08-23T16:35:00Z"
PUBLIC_COMMIT = "390267dfa9c6669e506ba67b5dde5dddd8f96232"

SOURCES = [
    "KEEP_OR_REPAIR_REPORTING",
    "REVISE_MEASUREMENT_OR_DATA",
    "REVISE_METHOD_OR_ANALYSIS",
    "WITHDRAW_CLAIM_OR_CONCLUSION",
    "WITHDRAW_ARTIFACT_FULL_RETRACTION",
    "UNRESOLVED",
]
TARGETS = [
    "KEEP_SEARCH",
    "KEEP_COMPILE",
    "KEEP_REPAIR",
    "REVISE_MEASUREMENT",
    "REFORMULATE_OBJECTIVE",
    "REFORMULATE_BOUNDARY",
    "UNRESOLVED",
]
OPERATIONS = [
    "KEEP",
    "REPAIR_METADATA_TYPOGRAPHY_ATTRIBUTION_FORMATTING_OR_REPORTING",
    "REVISE_MEASUREMENT_OR_DATA",
    "REVISE_METHOD_OR_ANALYSIS",
    "WITHDRAW_OR_MATERIALLY_NARROW_CLAIM_OR_CONCLUSION",
    "WITHDRAW_ARTIFACT",
    "ABSTAIN",
]


def dump(name: str, obj: object) -> None:
    (HERE / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


protocol = {
    "schema_version": "orion.p1.source-native-target-semantics-protocol.v8",
    "protocol_id": "P1.SOURCE_NATIVE.R7.TARGET.SEMANTICS.V8",
    "successor_identity": "P1_R7_PUBLIC_TARGET_SEMANTICS_AND_RIGHTS_ADJUDICATION_V8",
    "paper_id": "P1",
    "gap_id": "G16",
    "frozen_at_utc": FROZEN,
    "status": "PROSPECTIVE_PUBLIC_SEMANTIC_SOURCE_AND_RIGHTS_DISCRIMINATOR_FROZEN",
    "authority": "PUBLIC_PRIMARY_REPOSITORY_SEMANTIC_AND_RIGHTS_EVIDENCE_ONLY__NO_CASE_OR_OUTCOME_AUTHORITY",
    "predecessor": {
        "directory": "../p1-source-native-action-adapter-v2",
        "manifest_sha256": "9f4503f693e155b12fb8c333f4777619cec1d66e387dcfc0e141fffa6933847d",
        "terminal": "P1_SOURCE_NATIVE_R7_ADAPTER_CANNOT_CHECK_TARGET_SEMANTICS",
        "fully_certified": 0,
        "known_rejected": 116929,
        "not_disproved_but_uncertified": 720,
        "partial_adapter": {"UNRESOLVED": "UNRESOLVED"},
    },
    "frozen_public_target_corpus": {
        "repository": "https://github.com/SzeChunYiu/ORION",
        "commit": PUBLIC_COMMIT,
        "tree": "1a77f45cf959d8e472315438e2e1f823be5d03c9",
        "files": [
            "research/claim_expansion/p1/gpt_r1/ARD_PROTOCOL_V1.md",
            "research/claim_expansion/p1/gpt_r1/FRAMEWORK_CONSISTENCY_V1.md",
            "research/claim_expansion/p1/gpt_r1/run_ard_exact_pilot.py",
            "research/claim_expansion/p1/gpt_r7/R7_DESIGN_PROTOCOL_V1.json",
            "papers/FRAMEWORK_SNAPSHOT.json",
            "src/orion/registry.py",
            "src/orion/self_orion/revision_gate.py",
        ],
        "capture_rule": "Fetch immutable raw URLs and GitHub repository/commit/license metadata; retain hashes, byte counts, headers needed for provenance and derived semantic assertions, but no remote source body in the handoff.",
    },
    "questions": [
        "Does a public primary owner repository bind the seven target identifiers as scientific decisions separately from diagnostic probes?",
        "Does it bind exhaustive licensed and forbidden postpublication operations for every actionable target?",
        "Does it bind a decision-to-postpublication-action bridge, target error/timeout behavior and a closed-world denotation statement?",
        "Are access, reuse and redistribution rights explicit enough to retain the supporting source payloads?",
        "Under unchanged R7 gates, how many of the 720 not-disproved maps become certified or rejected?",
    ],
    "unchanged_gates": [
        "G1_TOTALITY", "G2_SORT_AND_COORDINATE_PRESERVATION", "G3_NO_AUTHORITY_EXPANSION",
        "G4_NO_LICENSED_ACTION_ERASURE", "G5_COLLISION_FREEDOM",
        "G6_UNRESOLVED_PRESERVATION", "G7_AUTHORITY_NEUTRALITY",
    ],
    "decision_rule": {
        "cell_pass": "Only an owner-authoritative exhaustive target denotation proves equality of sort, coordinate, licensed operations, forbidden operations, recommendation/execution authority and terminal behavior.",
        "cell_reject": "Only an authoritative contradiction, forbidden operation or extensional inequality proof rejects a cell; absence of evidence is not inequality.",
        "cell_cannot_check": "Any missing essential target field remains CANNOT_CHECK_TARGET_DENOTATION.",
        "map_positive": "All six images pass all seven unchanged gates.",
        "map_negative": "At least one image or whole-map collision has an authoritative failure witness.",
        "map_cannot_check": "No failure witness exists but at least one essential image field remains missing.",
    },
    "forbidden_inferences": [
        "public visibility implies a reuse licence",
        "repository authorship implies owner ratification of an algebra not present in the repository",
        "lexical or causal-anchor overlap proves postpublication operation equivalence",
        "diagnostic probes are one-to-one denotations of terminal decisions",
        "zero certified maps means zero possible maps",
        "missing evidence proves impossibility",
        "a conditional completion is the inherited R7 semantics",
        "semantic-interface evidence authorizes case action, execution, performance or publication superiority",
    ],
    "outcome_boundary": {
        "case_text_accessed": False,
        "row_level_outcomes_accessed": False,
        "system_outputs_accessed": False,
        "protected_data_accessed": False,
        "model_or_comparator_executed": False,
    },
    "terminals": {
        "positive": "P1_SOURCE_NATIVE_R7_TOTAL_SEMANTICS_PRESERVING_ADAPTER_BOUND_V8",
        "negative": "P1_SOURCE_NATIVE_R7_TOTAL_ADAPTER_IMPOSSIBLE_V8__AUTHORITATIVE_TARGET_CONTRADICTION",
        "cannot_check": "P1_V8_PUBLIC_TARGET_SEMANTICS_PARTIALLY_BOUND__R7_POSTPUBLICATION_DENOTATIONS_RIGHTS_AND_OWNER_RATIFICATION_CANNOT_CHECK",
    },
}

owner_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://orion.invalid/p1/v8/r7-owner-approved-target-decision-algebra.schema.json",
    "title": "P1 V8 owner-approved R7 target decision algebra",
    "description": "Prospective semantic authority needed to adjudicate the source-native adapter without case text or outcomes.",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version", "algebra_id", "supersedes_or_extends", "closed_world",
        "decision_probe_typing", "targets", "terminal_behavior", "authority_boundary",
        "rights", "ratification",
    ],
    "properties": {
        "schema_version": {"const": "orion.p1.r7.owner-approved-target-decision-algebra.v8"},
        "algebra_id": {"type": "string", "minLength": 1},
        "supersedes_or_extends": {
            "type": "object", "additionalProperties": False,
            "required": ["public_commit", "ard_protocol_sha256", "r7_protocol_sha256"],
            "properties": {
                "public_commit": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "ard_protocol_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "r7_protocol_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            },
        },
        "closed_world": {"const": True},
        "decision_probe_typing": {
            "type": "object", "additionalProperties": False,
            "required": ["decisions_are_terminals", "diagnostic_actions_are_probes", "one_to_one_bridge"],
            "properties": {
                "decisions_are_terminals": {"const": True},
                "diagnostic_actions_are_probes": {"const": True},
                "one_to_one_bridge": {"enum": ["NONE", "EXPLICIT_TABLE"]},
            },
        },
        "targets": {
            "type": "array", "minItems": 7, "maxItems": 7,
            "items": {
                "type": "object", "additionalProperties": False,
                "required": [
                    "decision_id", "sort", "scientific_process_coordinate",
                    "postpublication_coordinate", "licensed_postpublication_operations",
                    "forbidden_postpublication_operations", "recommendation_authority",
                    "execution_authority", "diagnostic_probe_relations", "exhaustive",
                ],
                "properties": {
                    "decision_id": {"enum": TARGETS},
                    "sort": {"enum": ["SCIENTIFIC_PROCESS_DECISION", "UNRESOLVED"]},
                    "scientific_process_coordinate": {"type": "string", "minLength": 1},
                    "postpublication_coordinate": {"type": ["string", "null"]},
                    "licensed_postpublication_operations": {"type": "array", "uniqueItems": True, "items": {"enum": OPERATIONS}},
                    "forbidden_postpublication_operations": {"type": "array", "uniqueItems": True, "items": {"enum": OPERATIONS}},
                    "recommendation_authority": {"enum": ["NONE", "ADVISORY", "OWNER_RATIFIED"]},
                    "execution_authority": {"enum": ["NONE", "EXTERNAL_OWNER_ONLY", "SYSTEM"]},
                    "diagnostic_probe_relations": {"type": "array", "uniqueItems": True, "items": {"type": "string"}},
                    "exhaustive": {"const": True},
                },
            },
        },
        "terminal_behavior": {
            "type": "object", "additionalProperties": False,
            "required": ["abstention", "error", "timeout", "malformed", "unsupported"],
            "properties": {key: {"enum": TARGETS} for key in ["abstention", "error", "timeout", "malformed", "unsupported"]},
        },
        "authority_boundary": {
            "type": "object", "additionalProperties": False,
            "required": ["may_infer_responsibility", "may_execute_postpublication_action", "may_adopt_promote_or_merge"],
            "properties": {
                "may_infer_responsibility": {"type": "boolean"},
                "may_execute_postpublication_action": {"type": "boolean"},
                "may_adopt_promote_or_merge": {"type": "boolean"},
            },
        },
        "rights": {
            "type": "object", "additionalProperties": False,
            "required": ["public_archive_url", "reuse_licence_spdx", "licence_text_sha256"],
            "properties": {
                "public_archive_url": {"type": "string", "pattern": "^https://"},
                "reuse_licence_spdx": {"type": "string", "minLength": 1},
                "licence_text_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            },
        },
        "ratification": {
            "type": "object", "additionalProperties": False,
            "required": ["vocabulary_owner_identity", "delegation_basis", "artifact_sha256", "signature_scheme", "key_id", "signature", "ratified_at_utc", "independent_semantic_reviewer"],
            "properties": {
                "vocabulary_owner_identity": {"type": "string", "minLength": 1},
                "delegation_basis": {"type": "string", "minLength": 1},
                "artifact_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "signature_scheme": {"enum": ["SIGSTORE", "SSH", "GPG"]},
                "key_id": {"type": "string", "minLength": 1},
                "signature": {"type": "string", "minLength": 1},
                "ratified_at_utc": {"type": "string", "format": "date-time"},
                "independent_semantic_reviewer": {
                    "type": "object", "additionalProperties": False,
                    "required": ["identity", "review_sha256", "disposition"],
                    "properties": {
                        "identity": {"type": "string", "minLength": 1},
                        "review_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                        "disposition": {"enum": ["CONFORMANT", "NONCONFORMANT", "CANNOT_CHECK"]},
                    },
                },
            },
        },
    },
}

required_fields = {
    "schema_version": "orion.p1.r7.owner-algebra-field-custodian-registry.v8",
    "registry_id": "P1.V8.REQUIRED.OWNER.ALGEBRA.FIELDS.AND.CUSTODIANS",
    "authority": "PROSPECTIVE_COMPLETION_REQUIREMENTS_ONLY__NOT_RATIFICATION",
    "target_count": 7,
    "actionable_target_count": 6,
    "requirements": [
        {
            "field_path": "closed_world",
            "current_state": "UNBOUND",
            "required_source": "owner-approved target algebra",
            "required_custodian": "R7_VOCABULARY_OWNER_OR_FORMALLY_DELEGATED_TAXONOMY_CUSTODIAN",
            "discriminator": "Explicit true statement that listed target profiles are exhaustive for adapter adjudication.",
        },
        {
            "field_path": "targets[*].scientific_process_coordinate",
            "current_state": "BOUND_PUBLIC_INTENSIONAL_ANCHOR__NOT_EXHAUSTIVE",
            "required_source": "owner-approved target algebra retaining or superseding the public anchor",
            "required_custodian": "R7_VOCABULARY_OWNER_OR_FORMALLY_DELEGATED_TAXONOMY_CUSTODIAN",
            "discriminator": "One closed coordinate definition per target, including overlap/disjointness rules.",
        },
        {
            "field_path": "targets[*].postpublication_coordinate",
            "current_state": "UNBOUND",
            "required_source": "owner-approved target algebra",
            "required_custodian": "R7_VOCABULARY_OWNER_OR_FORMALLY_DELEGATED_TAXONOMY_CUSTODIAN",
            "discriminator": "Exact postpublication coordinate or explicit NONE for every target.",
        },
        {
            "field_path": "targets[*].licensed_postpublication_operations",
            "current_state": "UNBOUND",
            "required_source": "owner-approved target algebra",
            "required_custodian": "R7_VOCABULARY_OWNER_OR_FORMALLY_DELEGATED_TAXONOMY_CUSTODIAN",
            "discriminator": "Exhaustive operation set for G3 and G4.",
        },
        {
            "field_path": "targets[*].forbidden_postpublication_operations",
            "current_state": "UNBOUND",
            "required_source": "owner-approved target algebra",
            "required_custodian": "R7_VOCABULARY_OWNER_OR_FORMALLY_DELEGATED_TAXONOMY_CUSTODIAN",
            "discriminator": "Exhaustive forbidden operation set for inequality and authority-expansion witnesses.",
        },
        {
            "field_path": "decision_probe_typing",
            "current_state": "PARTIALLY_BOUND__SEPARATE_TYPES_AND_NO_INHERITED_ONE_TO_ONE_BRIDGE",
            "required_source": "owner-approved explicit bridge table or explicit NONE",
            "required_custodian": "R7_VOCABULARY_OWNER_OR_FORMALLY_DELEGATED_TAXONOMY_CUSTODIAN",
            "discriminator": "Retain probe/decision separation and state any postpublication recommendation bridge without relabeling probes as decisions.",
        },
        {
            "field_path": "targets[*].recommendation_authority",
            "current_state": "UNBOUND_FOR_POSTPUBLICATION_ACTIONS",
            "required_source": "owner-approved authority boundary",
            "required_custodian": "R7_VOCABULARY_OWNER_AND_HOST_AUTHORITY_OWNER",
            "discriminator": "Distinguish semantic recommendation from execution/adoption authority.",
        },
        {
            "field_path": "targets[*].execution_authority",
            "current_state": "PUBLIC_FRAMEWORK_DENIES_SELF_ADOPTION_PROMOTION_AND_MERGE__POSTPUBLICATION_HOST_UNBOUND",
            "required_source": "owner-approved authority boundary",
            "required_custodian": "HOST_AUTHORITY_OWNER",
            "discriminator": "Explicit NONE, EXTERNAL_OWNER_ONLY or SYSTEM per target.",
        },
        {
            "field_path": "terminal_behavior.{abstention,error,timeout,malformed,unsupported}",
            "current_state": "UNBOUND_FOR_TARGET_SEMANTICS",
            "required_source": "owner-approved target algebra",
            "required_custodian": "R7_VOCABULARY_OWNER_OR_FORMALLY_DELEGATED_TAXONOMY_CUSTODIAN",
            "discriminator": "One fail-closed terminal for each non-success condition; system-level scoring prose is insufficient.",
        },
        {
            "field_path": "rights.{public_archive_url,reuse_licence_spdx,licence_text_sha256}",
            "current_state": "UNBOUND__NO_DETECTED_LICENCE_APPLICABLE_TO_TARGET_CORPUS",
            "required_source": "licence text controlled by the applicable rights holder",
            "required_custodian": "TARGET_CORPUS_RIGHTS_HOLDER_OR_AUTHORISED_LICENSOR",
            "discriminator": "Explicit reuse/redistribution licence and immutable public archive.",
        },
        {
            "field_path": "ratification",
            "current_state": "UNBOUND__PUBLIC_COMMIT_UNSIGNED_AND_NOT_AN_ALGEBRA_RATIFICATION",
            "required_source": "content-addressed signature bundle over the completed algebra",
            "required_custodian": "R7_VOCABULARY_OWNER_OR_FORMALLY_DELEGATED_TAXONOMY_CUSTODIAN",
            "discriminator": "Verify signature, delegation basis, artifact digest and timestamp before enumeration.",
        },
        {
            "field_path": "ratification.independent_semantic_reviewer",
            "current_state": "UNBOUND",
            "required_source": "independent semantic conformance review",
            "required_custodian": "REVIEWER_WITH_NO_ALGEBRA_AUTHORSHIP_OR_CASE_OUTCOME_CUSTODY",
            "discriminator": "Review all seven target profiles against public predecessors and unchanged G1-G7 before case/outcome access.",
        },
    ],
    "source_taxonomy_custody": {
        "current_state": "FROZEN_IN_R7_PREDECESSOR_WITH_MIXED_RIGHTS_BOUNDARIES",
        "required_custodian": "SOURCE_TAXONOMY_EVIDENCE_VERIFIER",
        "rule": "Do not rewrite source terminals to fit a target algebra; preserve partial-retraction/removal scope uncertainties and all predecessor rights terminals.",
    },
    "execution_rule": "Only a completed schema-valid, licensed, signed algebra with an independent CONFORMANT review may trigger the unchanged 117,649-map rerun. No case text or outcomes may be used to choose the algebra.",
}

dump("P1_V8_PROTOCOL.json", protocol)
dump("P1_V8_REQUIRED_OWNER_ALGEBRA_SCHEMA.json", owner_schema)
dump("P1_V8_REQUIRED_FIELD_CUSTODIAN_REGISTRY.json", required_fields)
print("wrote P1 V8 protocol, owner-algebra schema and custodian registry")
