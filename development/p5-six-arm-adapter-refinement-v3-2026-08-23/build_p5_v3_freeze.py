#!/usr/bin/env python3
"""Write the frozen, outcome-free P5 V3 adapter-refinement contract.

This authoring script uses only the retained V2 interface contract and
prospectively authored synthetic contract objects.  It does not open native
comparator outputs, benchmark rows, evaluator results, or protected material.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FROZEN_AT = "2026-08-23T17:05:00Z"

CLASSES = [
    "EVIDENCE_REPAIR",
    "MEASUREMENT_REPAIR",
    "WITHIN_CLASS_MODEL_REPAIR",
    "MODEL_CLASS_EXPANSION",
    "REPRESENTATION_REGIME_REPAIR",
    "EXECUTION_REPAIR",
    "EVALUATOR_REPAIR",
]
OUTPUTS = CLASSES + ["UNRESOLVED"]

ARMS = {
    "C1_FIXED_AGENT__SWE_AGENT": {
        "name": "SWE-agent",
        "resource_ledger_arm_id": "C1_FIXED_AGENT",
        "support": CLASSES,
        "mixed_pair": ["EXECUTION_REPAIR", "EVALUATOR_REPAIR"],
    },
    "C2_DIRECT_SELF_EDIT__MOSS": {
        "name": "MOSS",
        "resource_ledger_arm_id": "C2_DIRECT_SELF_EDIT",
        "support": [
            "WITHIN_CLASS_MODEL_REPAIR",
            "MODEL_CLASS_EXPANSION",
            "REPRESENTATION_REGIME_REPAIR",
            "EXECUTION_REPAIR",
        ],
        "mixed_pair": ["WITHIN_CLASS_MODEL_REPAIR", "REPRESENTATION_REGIME_REPAIR"],
    },
    "C3_ARCHIVE_BASED_SELF_EDIT__DGM": {
        "name": "Darwin Godel Machine",
        "resource_ledger_arm_id": "C3_ARCHIVE_BASED_SELF_EDIT",
        "support": [
            "WITHIN_CLASS_MODEL_REPAIR",
            "MODEL_CLASS_EXPANSION",
            "REPRESENTATION_REGIME_REPAIR",
            "EXECUTION_REPAIR",
        ],
        "mixed_pair": ["MODEL_CLASS_EXPANSION", "EXECUTION_REPAIR"],
    },
    "C4_ISSUE_CENTRIC_OPTIMIZATION__ADIAS": {
        "name": "ADIAS",
        "resource_ledger_arm_id": "C4_ISSUE_CENTRIC_OPTIMIZATION",
        "support": [
            "WITHIN_CLASS_MODEL_REPAIR",
            "MODEL_CLASS_EXPANSION",
            "REPRESENTATION_REGIME_REPAIR",
            "EXECUTION_REPAIR",
        ],
        "mixed_pair": ["WITHIN_CLASS_MODEL_REPAIR", "EXECUTION_REPAIR"],
    },
    "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY": {
        "name": "Double Ratchet metric-only",
        "resource_ledger_arm_id": "C5_EVALUATOR_ONLY_EVOLUTION",
        "support": ["EVALUATOR_REPAIR"],
        "mixed_pair": ["EVIDENCE_REPAIR", "EVALUATOR_REPAIR"],
    },
    "C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW": {
        "name": "ScienceClaw",
        "resource_ledger_arm_id": "C6_STRONGEST_SOURCE_GROUNDED_MODERN_METHOD",
        "support": [],
        "mixed_pair": ["EVIDENCE_REPAIR", "MEASUREMENT_REPAIR"],
    },
}

PREDECESSOR = {
    "directory": "../p5-six-arm-terminal-adapters-v2",
    "protocol": {
        "path": "P5_TERMINAL_PRESERVING_ADAPTER_PROTOCOL_V2.json",
        "sha256": "0415e2f01f326a45405e95fd575dd9e11fcf2ddfd06b422fb96673a6bf93558a",
    },
    "fixtures": {
        "path": "P5_ADVERSARIAL_FIBRE_FIXTURES_V2.json",
        "sha256": "f27d844c550a55d77f6d14f3e655fbb8c15357d9e4b085d8f1f5ce9409875a05",
    },
    "resource_ledger": {
        "path": "P5_V2_RESOURCE_CONFIG_LEDGER.json",
        "sha256": "1e3a450b1561cb2d3a1d556c77ef1688f8894fb2331fcfa334de87a18bd11dfe",
    },
    "preserved_terminal": "P5_SIX_ARM_EXECUTION_CONFIG_RESOURCE_RIGHTS_AND_EIGHT_CLASS_ADAPTERS_CANNOT_CHECK",
    "confirmatory_ready_arms": 0,
}


def dump(name: str, obj: object) -> None:
    (HERE / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def field(description: str, *, required: bool = True) -> dict:
    return {
        "description": description,
        "required_for_execution": required,
        "state_vocabulary": ["BOUND", "UNBOUND", "CANNOT_CHECK", "UNSUPPORTED"],
        "binding_rule": "BOUND requires a pre-execution value and sha256 or an enumerated closed value; a template or freezable choice is UNBOUND.",
    }


certificate_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://orion.invalid/p5/v3/candidate-visible-class-certificate.schema.json",
    "title": "P5 V3 minimal candidate-visible input-native class certificate",
    "description": "The certificate is issued before candidate action and contains no native output, protected score, comparator performance, or evaluator feedback.",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version", "certificate_id", "arm_id", "observation_id",
        "declared_class", "issuance", "basis", "complete",
    ],
    "properties": {
        "schema_version": {"const": "orion.p5.candidate-visible-class-certificate.v3"},
        "certificate_id": {"type": "string", "pattern": "^P5V3-CERT-[A-Z0-9_.-]+$"},
        "arm_id": {"enum": list(ARMS)},
        "observation_id": {"type": "string", "pattern": "^P5V3-OBS-[A-Z0-9_.-]+$"},
        "declared_class": {"enum": CLASSES},
        "issuance": {
            "type": "object", "additionalProperties": False,
            "required": ["issuer_role", "phase", "candidate_visible", "input_native", "native_output_access", "protected_outcome_access", "sequence"],
            "properties": {
                "issuer_role": {"const": "HOST_INPUT_VALIDATOR"},
                "phase": {"const": "BEFORE_CANDIDATE_ACTION"},
                "candidate_visible": {"const": True},
                "input_native": {"const": True},
                "native_output_access": {"const": False},
                "protected_outcome_access": {"const": False},
                "sequence": {"type": "integer", "minimum": 0},
            },
        },
        "basis": {
            "type": "object", "additionalProperties": False,
            "required": ["predicate_id", "source_ref_sha256", "domain_scope_sha256", "fibre_constancy_attestation"],
            "properties": {
                "predicate_id": {"type": "string", "pattern": "^SYNTHETIC_[A-Z0-9_.-]+$"},
                "source_ref_sha256": {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"type": "string", "pattern": "^[0-9a-f]{64}$"}},
                "domain_scope_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "fibre_constancy_attestation": {
                    "type": "object", "additionalProperties": False,
                    "required": ["status", "declared_class", "proof_ref_sha256"],
                    "properties": {
                        "status": {"const": "PROVED_ON_DECLARED_SYNTHETIC_DOMAIN"},
                        "declared_class": {"enum": CLASSES},
                        "proof_ref_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    },
                },
            },
        },
        "complete": {"const": True},
    },
}

front_registry = {
    "schema_version": "orion.p5.eight-class-front-registry.v3",
    "registry_id": "P5.V3.FROZEN.EIGHT.CLASS.FRONT.REGISTRY",
    "frozen_at_utc": FROZEN_AT,
    "authority": "SYNTHETIC_ACTION_SURFACE_CLASSIFICATION_ONLY__NO_CORRECTNESS_OR_PERFORMANCE_AUTHORITY",
    "candidate_visible_before_action": True,
    "fronts": [
        {"class": "EVIDENCE_REPAIR", "actionable": True, "synthetic_root": "synthetic://front/evidence/", "invariance": "All non-evidence front digests remain unchanged."},
        {"class": "MEASUREMENT_REPAIR", "actionable": True, "synthetic_root": "synthetic://front/measurement/", "invariance": "All non-measurement front digests remain unchanged."},
        {"class": "WITHIN_CLASS_MODEL_REPAIR", "actionable": True, "synthetic_root": "synthetic://front/model/within-class/", "invariance": "Model family and representation front digests remain unchanged; only the within-family surface changes."},
        {"class": "MODEL_CLASS_EXPANSION", "actionable": True, "synthetic_root": "synthetic://front/model/class-expansion/", "invariance": "Evidence, measurement, representation, execution and evaluator front digests remain unchanged."},
        {"class": "REPRESENTATION_REGIME_REPAIR", "actionable": True, "synthetic_root": "synthetic://front/representation/", "invariance": "Evidence custody, model-family selection, execution and evaluator front digests remain unchanged."},
        {"class": "EXECUTION_REPAIR", "actionable": True, "synthetic_root": "synthetic://front/execution/", "invariance": "Evidence, measurement, scientific-model, representation and evaluator front digests remain unchanged."},
        {"class": "EVALUATOR_REPAIR", "actionable": True, "synthetic_root": "synthetic://front/evaluator/", "invariance": "Candidate solver bytes and every non-evaluator front digest remain unchanged."},
        {"class": "UNRESOLVED", "actionable": False, "synthetic_root": None, "invariance": "No singleton licence and no action/write-surface claim."},
    ],
    "arm_support_sets": {arm: row["support"] for arm, row in ARMS.items()},
    "raw_native_singletons_licensed": 0,
    "scienceclaw_boundary": "C6 has no supported singleton front; a selector would be a successor method rather than an adapter relabel.",
}

action_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://orion.invalid/p5/v3/complete-action-write-surface.schema.json",
    "title": "P5 V3 complete action and write-surface record",
    "description": "A synthetic action record enumerates every mutation and before/after digest for all seven actionable fronts; nonselected drift invalidates singleton emission.",
    "type": "object", "additionalProperties": False,
    "required": [
        "schema_version", "action_id", "arm_id", "observation_id", "certificate_id",
        "selected_front", "declared_complete", "mutations", "front_snapshots",
        "write_set_sha256", "protected_surface_touched", "external_scorer_surface_touched",
        "arm_specific_guards",
    ],
    "properties": {
        "schema_version": {"const": "orion.p5.complete-action-write-surface.v3"},
        "action_id": {"type": "string", "pattern": "^P5V3-ACT-[A-Z0-9_.-]+$"},
        "arm_id": {"enum": list(ARMS)},
        "observation_id": {"type": "string", "pattern": "^P5V3-OBS-[A-Z0-9_.-]+$"},
        "certificate_id": {"type": "string", "pattern": "^P5V3-CERT-[A-Z0-9_.-]+$"},
        "selected_front": {"enum": CLASSES},
        "declared_complete": {"const": True},
        "mutations": {
            "type": "array", "minItems": 1,
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["mutation_id", "operation", "target_uri", "registry_front", "before_sha256", "after_sha256"],
                "properties": {
                    "mutation_id": {"type": "string", "pattern": "^MUT-[A-Z0-9_.-]+$"},
                    "operation": {"enum": ["CREATE", "UPDATE", "DELETE", "CONFIGURE"]},
                    "target_uri": {"type": "string", "pattern": "^synthetic://front/"},
                    "registry_front": {"enum": CLASSES},
                    "before_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "after_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                },
            },
        },
        "front_snapshots": {
            "type": "array", "minItems": 7, "maxItems": 7,
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["class", "before_sha256", "after_sha256", "changed"],
                "properties": {
                    "class": {"enum": CLASSES},
                    "before_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "after_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "changed": {"type": "boolean"},
                },
            },
        },
        "write_set_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        "protected_surface_touched": {"const": False},
        "external_scorer_surface_touched": {"const": False},
        "arm_specific_guards": {
            "type": "object", "additionalProperties": False,
            "required": ["solver_bytes_unchanged", "evaluator_only_mutation", "development_validity_passed"],
            "properties": {
                "solver_bytes_unchanged": {"type": "boolean"},
                "evaluator_only_mutation": {"type": "boolean"},
                "development_validity_passed": {"type": "boolean"},
            },
        },
    },
}

terminal_rules = {
    "schema_version": "orion.p5.native-terminal-retention-rules.v3",
    "rules_id": "P5.V3.NATIVE.TERMINAL.RETENTION",
    "frozen_at_utc": FROZEN_AT,
    "native_status_vocabulary": ["COMPLETE_SUCCESS", "ERROR", "TIMEOUT", "ABSTAIN", "EMPTY", "PARTIAL", "INVALID"],
    "required_native_terminal_fields": ["arm_id", "status", "native_code", "payload_sha256"],
    "exact_retention": "The adapter output must carry a byte-for-byte equal native_terminal object for every case, including COMPLETE_SUCCESS cases mapped to a singleton.",
    "rules_in_order": [
        {"id": "T1", "when": "native status is not COMPLETE_SUCCESS", "emit": "UNRESOLVED", "reason": "NATIVE_TERMINAL_PRESERVED"},
        {"id": "T2", "when": "arm support set is empty or selected class is unsupported", "emit": "UNRESOLVED", "reason": "UNSUPPORTED_ARM_CLASS"},
        {"id": "T3", "when": "certificate is missing, nonunique, schema-invalid, late, non-input-native, outcome-exposed, or fibre-nonconstant", "emit": "UNRESOLVED", "reason": "CERTIFICATE_OR_FIBRE_FAILURE"},
        {"id": "T4", "when": "action is missing, schema-invalid, incomplete, cross-front, registry-invalid, or changes any nonselected front", "emit": "UNRESOLVED", "reason": "ACTION_OR_INVARIANCE_FAILURE"},
        {"id": "T5", "when": "certificate, action, observation, arm or selected class disagree", "emit": "UNRESOLVED", "reason": "CROSS_RECORD_MISMATCH"},
        {"id": "T6", "when": "Double Ratchet does not preserve solver bytes, restrict mutations to evaluator, or pass development validity", "emit": "UNRESOLVED", "reason": "DOUBLE_RATCHET_GUARD_FAILURE"},
        {"id": "T7", "when": "all prior checks pass and the declared synthetic fibre is constant", "emit": "the one supported declared_class", "reason": "DECLARED_SYNTHETIC_FIBRE_CONSTANT_AND_NONSELECTED_FRONTS_INVARIANT"},
    ],
    "nonclaims": [
        "A retained terminal is not a correct diagnosis.",
        "A singleton conformance output is not comparator performance, preservation, transfer, harm, or superiority.",
        "No raw native symptom licenses a singleton.",
    ],
}

protocol = {
    "schema_version": "orion.p5.six-arm-adapter-refinement-protocol.v3",
    "protocol_id": "P5.SIX_ARM.ADAPTER.REFINEMENT.V3",
    "paper_id": "P5",
    "frozen_at_utc": FROZEN_AT,
    "status": "PROSPECTIVE_OUTCOME_FREE_SYNTHETIC_CONTRACT_FREEZE",
    "authority": "SCHEMA_FIBRE_AND_INVARIANCE_CONFORMANCE_ON_DECLARED_SYNTHETIC_DOMAIN_ONLY",
    "predecessor": PREDECESSOR,
    "outcome_boundary": {
        "native_comparator_output_examples_accessed": False,
        "public_or_protected_outcome_rows_accessed": False,
        "comparators_or_models_executed": False,
        "performance_tables_accessed": False,
        "protected_data_accessed": False,
        "fixtures": "prospectively generated synthetic contract objects only",
    },
    "artifacts": {
        "certificate_schema": "P5_V3_CANDIDATE_VISIBLE_CERTIFICATE_SCHEMA.json",
        "action_schema": "P5_V3_ACTION_WRITE_SURFACE_SCHEMA.json",
        "front_registry": "P5_V3_EIGHT_CLASS_FRONT_REGISTRY.json",
        "terminal_rules": "P5_V3_NATIVE_TERMINAL_RETENTION_RULES.json",
        "resource_manifest_template": "P5_V3_MATCHED_RESOURCE_MANIFEST_TEMPLATE.json",
        "synthetic_domain": "P5_V3_DECLARED_SYNTHETIC_DOMAIN.json",
        "validator": "p5_v3_contract_validator.py",
    },
    "arm_support_sets": {arm: row["support"] for arm, row in ARMS.items()},
    "declared_domain_totality_definition": "Every frozen synthetic case must return exactly one output in the eight-class vocabulary, retain its exact native terminal, and raise no unhandled exception.",
    "fibre_constancy_definition": "Within the declared synthetic domain, group worlds by the full adapter-visible key. A singleton is permitted only when all synthetic oracle classes in the group equal the certificate/action class.",
    "invariance_definition": "Exactly the selected actionable front changes; every other front digest is equal before/after; each mutation target lies under the selected front root and every mutation is enumerated.",
    "preserved_boundaries": {
        "raw_native_singleton_licences": 0,
        "confirmatory_ready": "0/6",
        "H1": "CANNOT_CHECK", "H2": "CANNOT_CHECK", "H3": "CANNOT_CHECK", "H4": "CANNOT_CHECK",
        "protected_freshness": "CANNOT_CHECK", "performance": "CANNOT_CHECK", "harm": "CANNOT_CHECK", "superiority": "CANNOT_CHECK",
        "scienceclaw_supported_singletons": 0,
    },
}

domain = {
    "schema_version": "orion.p5.declared-synthetic-adapter-domain.v3",
    "domain_id": "P5.V3.DECLARED.SYNTHETIC.OUTCOME.FREE.DOMAIN",
    "frozen_at_utc": FROZEN_AT,
    "authority": "PROSPECTIVE_SYNTHETIC_CONTRACT_CASES_ONLY",
    "synthetic_oracle_note": "minimal_class is an authored logical property of a fictional world used only to test fibre constancy; it is not a comparator, benchmark, public, protected, or scientific outcome.",
    "native_examples_used": False,
    "outcome_rows_used": False,
    "performance_examples_used": False,
    "arms": ARMS,
    "native_statuses": terminal_rules["native_status_vocabulary"],
    "case_families": [
        {"id": "RAW_MIXED_FIBRE", "construction": "two worlds per arm share the complete raw-visible key and have distinct authored minimal classes", "expected": "UNRESOLVED"},
        {"id": "SUPPORTED_CONSTANT_FIBRE", "construction": "two worlds per supported arm-class cell share one valid certificate/action visible key and the same authored minimal class", "expected": "declared supported class"},
        {"id": "MISCERTIFIED_MIXED_FIBRE", "construction": "two worlds for each arm with support share an otherwise valid certificate/action key but have distinct authored minimal classes", "expected": "UNRESOLVED"},
        {"id": "UNSUPPORTED_CLASS", "construction": "one schema-valid certificate/action for each unsupported arm-class cell", "expected": "UNRESOLVED"},
        {"id": "CERTIFICATE_DEFECT", "variants": ["MISSING", "NONUNIQUE", "INVALID_ISSUER", "LATE", "PROTECTED_ACCESS", "NO_FIBRE_PROOF", "CLASS_MISMATCH"], "expected": "UNRESOLVED"},
        {"id": "ACTION_OR_INVARIANCE_DEFECT", "variants": ["MISSING", "INCOMPLETE", "MULTI_FRONT", "NONSELECTED_DRIFT", "PATH_OUTSIDE_REGISTRY", "FRONT_MISMATCH", "PROTECTED_SURFACE_TOUCH", "EXTERNAL_SCORER_TOUCH", "HASH_NO_CHANGE", "OBSERVATION_MISMATCH", "CERTIFICATE_MISMATCH"], "expected": "UNRESOLVED"},
        {"id": "NATIVE_NONCOMPLETE_TERMINAL", "construction": "one case per arm and each of six non-complete native statuses", "expected": "UNRESOLVED"},
        {"id": "DOUBLE_RATCHET_GUARD_DEFECT", "variants": ["SOLVER_DRIFT", "NON_EVALUATOR_MUTATION", "DEVELOPMENT_VALIDITY_FAILED"], "expected": "UNRESOLVED"},
    ],
    "generation_rule": "The checked validator deterministically instantiates every listed arm/class/status/variant cell. No stochastic generation or outcome access is permitted.",
}

manifest_fields = {
    "identity.source_repository_commit": field("Pinned source repository and commit."),
    "identity.source_license_bytes": field("Content-addressed source licence bytes."),
    "identity.native_entrypoint_bytes": field("Content-addressed native entrypoint bytes."),
    "inputs.candidate_visible_case_bytes": field("Exact candidate-visible P5 case bytes and input manifest."),
    "runtime.dependency_lock": field("Exact dependency lock digest."),
    "runtime.container_or_environment": field("Container digest or complete immutable environment identity."),
    "runtime.task_environment": field("Task, harness, OS/runtime and external environment identity."),
    "runtime.compute": field("CPU, RAM, GPU and parallelism allocation."),
    "model_provider.primary": field("Model, provider, endpoint/service revision, prompts/config and capability mapping."),
    "model_provider.fallbacks": field("Closed fallback policy and all fallback identities."),
    "resources.wallclock": field("Per-case and whole-run wallclock caps."),
    "resources.calls_tokens_usd": field("Tool/model-call, token and monetary caps."),
    "resources.retry_network": field("Retry, timeout, backoff and network allowlist."),
    "adapter.native_parser_binding": field("Hashed arm-native parser to this V3 certificate/action contract."),
    "adapter.isolated_write_surface": field("Enforced write allowlist and reset semantics matched to the registry."),
    "rights.task_and_benchmark_content": field("Lawful use of task, benchmark, issue, session and environment content."),
    "rights.model_provider_and_services": field("Lawful model/provider/API/search/tool-service use."),
    "rights.container_and_generated_artifacts": field("Container/image and generated-artifact use, retention and redistribution rights."),
    "custody.external_protected_scorer": field("Independent scorer identity, code digest and access controls."),
    "custody.protected_panel_freshness": field("Protected panel identity/freshness attestation unavailable to candidate."),
    "custody.one_shot_no_feedback_barrier": field("One-shot scoring and no outcome feedback into candidate/adaptation custody."),
}

# The V2 source/identity audit closed only these three fields for every arm.
def states(unbound_reasons: dict[str, str], unsupported: set[str] | None = None) -> dict:
    unsupported = unsupported or set()
    out = {}
    for path in manifest_fields:
        if path.startswith("identity."):
            out[path] = {"state": "BOUND", "binding": "Retained V2 content-addressed source identity", "blocker_reason": None}
        elif path in unsupported:
            out[path] = {"state": "UNSUPPORTED", "binding": None, "blocker_reason": unbound_reasons[path]}
        else:
            out[path] = {"state": "UNBOUND", "binding": None, "blocker_reason": unbound_reasons.get(path, "Required execution binding was not frozen in V2 or V3.")}
    return out


common = {
    "inputs.candidate_visible_case_bytes": "No exact P5 candidate-visible case packet is frozen.",
    "runtime.dependency_lock": "No exact dependency lock digest is frozen.",
    "runtime.container_or_environment": "No content-addressed container or complete immutable environment is frozen.",
    "runtime.task_environment": "No exact matched task/harness/runtime environment is frozen.",
    "runtime.compute": "CPU, RAM, GPU and parallelism are not selected and frozen.",
    "model_provider.primary": "Selected model/provider/service revision, configuration and capability mapping are unbound.",
    "model_provider.fallbacks": "Fallback identities and closed fallback behaviour are unbound.",
    "resources.wallclock": "Per-case and whole-run wallclock caps are unbound.",
    "resources.calls_tokens_usd": "Aggregate calls, tokens and USD caps are unbound.",
    "resources.retry_network": "Retry, timeout, backoff and network allowlist are unbound.",
    "adapter.native_parser_binding": "The generic V3 synthetic contract is hashed, but no arm-native runtime parser/binding is implemented or checked against native outputs.",
    "adapter.isolated_write_surface": "The V3 synthetic write registry is specified, but no runtime enforcement/reset wrapper is bound.",
    "rights.task_and_benchmark_content": "Task, benchmark, issue/session or environment content rights are not closed.",
    "rights.model_provider_and_services": "Model/provider and external service terms are not closed.",
    "rights.container_and_generated_artifacts": "Container/image and generated-artifact authority is not closed.",
    "custody.external_protected_scorer": "Independent protected scorer identity, code and access control remain CANNOT_CHECK.",
    "custody.protected_panel_freshness": "Protected panel identity and freshness remain CANNOT_CHECK.",
    "custody.one_shot_no_feedback_barrier": "No enforced one-shot no-feedback custody wrapper is bound.",
}

arm_overrides = {
    "C1_FIXED_AGENT__SWE_AGENT": {
        "runtime.task_environment": "Isolated task checkout/container and task environment identity are unbound.",
        "rights.task_and_benchmark_content": "Upstream repository, issue and task-content rights are not closed.",
    },
    "C2_DIRECT_SELF_EDIT__MOSS": {
        "model_provider.primary": "Authenticated coding-agent CLI, model, provider, endpoint and revision are unbound.",
        "rights.task_and_benchmark_content": "Session/failure artifacts and any external task or benchmark content rights are not closed.",
        "rights.container_and_generated_artifacts": "Docker/host mutation authority and generated-session artifact rights are not closed.",
    },
    "C3_ARCHIVE_BASED_SELF_EDIT__DGM": {
        "runtime.task_environment": "Task/harness subset, prepared benchmark environment and treatment of the pinned argparse-choice defect are unbound.",
        "resources.wallclock": "No effective whole-attempt timeout outside coding_agent is frozen.",
        "rights.task_and_benchmark_content": "SWE-bench framework, benchmark data, project, tests and patch rights are not closed.",
        "rights.container_and_generated_artifacts": "Docker authority and untrusted generated-code isolation/retention rights are not closed.",
    },
    "C4_ISSUE_CENTRIC_OPTIMIZATION__ADIAS": {
        "runtime.task_environment": "Dependency/container/domain identity, optimize_option and path policy are unbound.",
        "adapter.isolated_write_surface": "The native write allow-list conflict is unresolved; the synthetic registry does not enforce the runtime surface.",
        "rights.task_and_benchmark_content": "ADIAS source use is restricted by CC BY-NC-SA and third-party benchmark/environment rights are not closed.",
        "rights.model_provider_and_services": "Model/provider and public-search service terms are not closed.",
    },
    "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY": {
        "inputs.candidate_visible_case_bytes": "P5 dossier bytes, frozen solver identity and development-only locked surrogate are unbound.",
        "runtime.task_environment": "P5 task-output generator and selected default-versus-reproduction regime are unbound.",
        "model_provider.primary": "Bedrock revision, role mapping, detector and embedding service identities, region and frozen solver configuration are unbound.",
        "adapter.native_parser_binding": "The generic evaluator-front contract exists, but no native adapter or protected-custody wrapper is implemented and hashed.",
        "rights.task_and_benchmark_content": "MBPP+, Spider 2.0-Snow/Snowflake, report-generation data/evaluator and P5 panel rights are not closed.",
        "rights.model_provider_and_services": "Amazon Bedrock permissions, pricing, quotas and optional service terms are not closed.",
        "custody.one_shot_no_feedback_barrier": "Official eval_locked flow is not protected-custody safe without a bound development-surrogate and one-shot wrapper.",
    },
    "C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW": {
        "runtime.task_environment": "Profile, tools, optional dependencies, artifact reset, dry-run mode, topic-to-case adapter and scientific service revisions are unbound.",
        "model_provider.primary": "All model/provider/scientific service identities and capability mapping are unbound.",
        "resources.calls_tokens_usd": "All P5 tool-call, token and USD values are unbound.",
        "adapter.native_parser_binding": "ScienceClaw has no native supported singleton; implementing a selector would be a material successor method, not an adapter binding.",
        "rights.task_and_benchmark_content": "Tool datasets, topic/case and protected-panel rights are not closed.",
        "rights.model_provider_and_services": "Scientific APIs, Infinite service, model/provider and tool-service terms are not closed.",
        "rights.container_and_generated_artifacts": "Generated-artifact rights and retention/redistribution authority are not closed.",
    },
}

arm_manifests = []
for arm, meta in ARMS.items():
    reasons = dict(common)
    reasons.update(arm_overrides[arm])
    unsupported = {"adapter.native_parser_binding"} if arm == "C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW" else set()
    arm_manifests.append({
        "arm_id": arm,
        "name": meta["name"],
        "resource_ledger_arm_id": meta["resource_ledger_arm_id"],
        "fields": states(reasons, unsupported),
        "execution_ready": False,
    })

resource_manifest = {
    "schema_version": "orion.p5.matched-resource-manifest-template.v3",
    "template_id": "P5.V3.SIX.ARM.MATCHED.RESOURCE.RIGHTS.CUSTODY.TEMPLATE",
    "frozen_at_utc": FROZEN_AT,
    "authority": "OUTCOME_FREE_EXECUTION_PREFLIGHT_TEMPLATE_ONLY",
    "predecessor_resource_ledger_sha256": PREDECESSOR["resource_ledger"]["sha256"],
    "matching_rule": "Every required field must be BOUND for every arm before execution. Equality means an identical resource value where semantically fungible; otherwise a predeclared capability-equivalence rule and arm-specific value must both be frozen. Templates and freezable choices do not count as bindings.",
    "field_definitions": manifest_fields,
    "arm_manifests": arm_manifests,
    "panel_execution_rule": "If any required field is UNBOUND, CANNOT_CHECK or UNSUPPORTED for an arm, that arm is not execution-ready; do not repair readiness by deleting the arm after outcomes.",
    "confirmatory_ready_arms": 0,
    "required_arms": 6,
}

dump("P5_V3_CANDIDATE_VISIBLE_CERTIFICATE_SCHEMA.json", certificate_schema)
dump("P5_V3_ACTION_WRITE_SURFACE_SCHEMA.json", action_schema)
dump("P5_V3_EIGHT_CLASS_FRONT_REGISTRY.json", front_registry)
dump("P5_V3_NATIVE_TERMINAL_RETENTION_RULES.json", terminal_rules)
dump("P5_V3_REFINED_ADAPTER_PROTOCOL.json", protocol)
dump("P5_V3_DECLARED_SYNTHETIC_DOMAIN.json", domain)
dump("P5_V3_MATCHED_RESOURCE_MANIFEST_TEMPLATE.json", resource_manifest)

print("wrote 7 frozen P5 V3 contract artifacts")
