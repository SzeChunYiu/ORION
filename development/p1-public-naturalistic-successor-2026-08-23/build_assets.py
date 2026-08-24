#!/usr/bin/env python3
"""Build the outcome-blind P1 R7A public-source execution preflight.

This builder reads metadata and comparator receipts already present in the
repository.  It never fetches source content, opens protected case fields, or
executes a candidate/comparator.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected an object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


PROVIDER_CENSUS = ROOT / "development/provider-diverse-metadata-census-2026-08-23/SOURCE_CENSUS_V1.json"
PROVIDER_PROTOCOL = ROOT / "development/provider-diverse-metadata-census-2026-08-23/CENSUS_PROTOCOL_V1.json"
PROVIDER_RECEIPT = ROOT / "development/provider-diverse-metadata-census-2026-08-23/VERIFICATION_RECEIPT_V1.json"
GITHUB_SNAPSHOT = ROOT / "development/naturalistic-panel-harness-2026-08-23/SOURCE_METADATA_SNAPSHOT_V1.json"
GITHUB_STATUS = ROOT / "development/naturalistic-panel-harness-2026-08-23/PROTOCOL_BINDING_STATUS_V1.json"
COMPARATOR_LEDGER = ROOT / "development/comparator-binding-harness-2026-08-23/COMPARATOR_BINDING_LEDGER_V1.json"
COMPARATOR_REMOTE = ROOT / "development/comparator-binding-harness-2026-08-23/REMOTE_REPOSITORY_METADATA_2026-08-23.json"
R7A_AMENDMENT = ROOT / "research/claim_expansion/p1/gpt_r7/R7A_MAXT_POWER_AMENDMENT_V2.json"
R7A_POWER = ROOT / "research/claim_expansion/p1/gpt_r7a/R7A_MAXT_POWER_RECEIPT_V1.json"
R7A_QUERY = ROOT / "research/claim_expansion/p1/gpt_r7a/query_frame.py"
R7_SOURCE_VALIDATOR = ROOT / "research/claim_expansion/p1/gpt_r7/source_frame.py"
R7_CANDIDATE_VIEW = ROOT / "research/claim_expansion/p1/gpt_r7/candidate_view.py"
R2_POLICY = ROOT / "research/claim_expansion/p1/gpt_r2/policy.py"
R6_NATIVE = ROOT / "research/claim_expansion/p1/gpt_r6/native_orion_core_v1.py"
P1X_POLICY = ROOT / "research/claim_expansion/p1/p1_x_execution.py"
R7A_DEFICIENCY_AMENDMENT = HERE / "R7A_INTERFACE_DEFICIENCY_ESTIMAND_AMENDMENT_V1.json"


def build_source_rights_ledger() -> dict[str, Any]:
    census = read_json(PROVIDER_CENSUS)
    github = read_json(GITHUB_SNAPSHOT)
    sources: list[dict[str, Any]] = []

    for row in census["records"]:
        sources.append(
            {
                "artifact_modality": row["artifact_modality"],
                "candidate_domain": row["protected_domain_candidate"],
                "candidate_wave": row["wave_id"],
                "case_eligibility_status": row["case_eligibility_status"],
                "content_accessed": False,
                "content_class_rights": row["content_class_rights"],
                "exact_provider_identity": row["provider_record_identity"],
                "legal_gate": row["legal_gate"],
                "metadata_provider": row["metadata_provider_id"],
                "persistent_identifier": row["persistent_identifier"],
                "protected_fields_accessed": False,
                "public_record_url": row["public_record_url"],
                "record_sha256": row["record_sha256"],
                "r7a_case_content_admissible": False,
                "selected_pre_cutoff_revision": row["selected_pre_cutoff_revision"],
                "source_family_id": row["candidate_source_family_id"],
                "source_ledger": rel(PROVIDER_CENSUS),
            }
        )

    for row in github["records"]:
        licence = row["licence"]
        sources.append(
            {
                "artifact_modality": "GITHUB_SOFTWARE_REPOSITORY",
                "candidate_domain": row["protected_domain_candidate"],
                "candidate_wave": "UNASSIGNED_SEED_ONLY",
                "case_eligibility_status": "NOT_ASSESSED__CANDIDATE_METADATA_ROOT_ONLY",
                "content_accessed": False,
                "content_class_rights": {
                    "repository_files_at_selected_revision": {
                        "licence_path": licence["path_at_selected_revision"],
                        "licence_spdx": licence["spdx_id_at_selected_revision"],
                        "licence_text_sha256": licence["text_sha256"],
                        "status": "EXACT_LICENCE_BYTES_BOUND__SCOPE_REQUIRES_RIGHTS_OWNER_REVIEW",
                    },
                    "issue_comment_pull_request_and_attachment_text": {
                        "status": "NOT_ACCESSED__RIGHTS_NOT_VERIFIED__CANNOT_CHECK"
                    },
                },
                "exact_provider_identity": row["official_repository_identity"],
                "legal_gate": "CANNOT_CHECK_CASE_CONTENT_CLASS_RIGHTS",
                "metadata_provider": "GITHUB_REST_API",
                "persistent_identifier": f"github:{row['official_repository_identity']}",
                "protected_fields_accessed": False,
                "public_record_url": row["primary_source_url"],
                "record_sha256": row["record_sha256"],
                "r7a_case_content_admissible": False,
                "selected_pre_cutoff_revision": {
                    "commit_date": row["selected_revision_committer_date"],
                    "commit_sha": row["selected_revision_sha"],
                    "commit_url": row["selected_revision_url"],
                    "status": "EXACT_COMMIT_BOUND",
                },
                "source_family_id": row["candidate_source_family_id"],
                "source_ledger": rel(GITHUB_SNAPSHOT),
            }
        )

    return {
        "schema_version": "orion.p1.r7a.public-source-rights-ledger.v1",
        "date": "2026-08-23",
        "authority": "OUTCOME_BLIND_METADATA_AND_RIGHTS_PREFLIGHT_ONLY",
        "legal_status": "NOT_LEGAL_ADVICE__RIGHTS_OWNER_ATTESTATION_REQUIRED",
        "outcomes_accessed": False,
        "protected_case_fields_accessed": False,
        "exact_upstream_bindings": [
            {"path": rel(PROVIDER_CENSUS), "sha256": sha256(PROVIDER_CENSUS)},
            {"path": rel(PROVIDER_PROTOCOL), "sha256": sha256(PROVIDER_PROTOCOL)},
            {"path": rel(PROVIDER_RECEIPT), "sha256": sha256(PROVIDER_RECEIPT)},
            {"path": rel(GITHUB_SNAPSHOT), "sha256": sha256(GITHUB_SNAPSHOT)},
            {"path": rel(GITHUB_STATUS), "sha256": sha256(GITHUB_STATUS)},
        ],
        "summary": {
            "candidate_metadata_roots": len(sources),
            "provider_diverse_roots": len(census["records"]),
            "github_seed_roots": len(github["records"]),
            "case_content_rights_bound": 0,
            "case_eligibility_assessed": 0,
            "r7a_case_content_admissible": 0,
            "required_r7a_source_clusters_both_waves": 896,
            "scientific_terminal": "CANNOT_CHECK_SOURCE_UNIVERSE_AND_CONTENT_RIGHTS",
        },
        "rights_admission_rule": {
            "all_required": True,
            "requirements": [
                "exact immutable content revision or provider-native version identity",
                "content-class-specific licence or written permission for every byte exposed to systems/evaluators",
                "permission for storage, machine processing, derived annotation, audit quotation, and the planned artifact release tier",
                "attachments, issue comments, pull-request text, article body, dataset files, and repository code are adjudicated separately",
                "terms and access status are bound by an identified rights owner before content access",
                "sensitive, personal, confidential, embargoed, deleted, or author-intent-dependent material is excluded",
            ],
            "public_url_is_not_permission": True,
            "metadata_licence_is_not_automatically_content_licence": True,
            "ambiguous_or_partial_scope_terminal": "CANNOT_CHECK_CONTENT_CLASS_RIGHTS",
        },
        "sources": sources,
    }


def comparator_bindings() -> dict[str, dict[str, Any]]:
    ledger = read_json(COMPARATOR_LEDGER)
    return {row["binding_id"]: row for row in ledger["bindings"]}


def build_comparator_contract() -> dict[str, Any]:
    bindings = comparator_bindings()
    agent_lab = bindings["P1.AGENT_LABORATORY"]
    ai_scientist = bindings["P1.AI_SCIENTIST_V2"]

    arm_rows = [
        {
            "arm_id": "P1_X_STATIC_HIDDEN_RESPONSIBILITY",
            "binding": {"path": rel(P1X_POLICY), "sha256": sha256(P1X_POLICY)},
            "current_status": "EXACT_CONTRACT_ARM_ONLY__R7A_ADAPTER_UNBOUND",
        },
        {
            "arm_id": "GREEDY_IMMEDIATE_RESTORATION",
            "binding": {"path": rel(P1X_POLICY), "sha256": sha256(P1X_POLICY)},
            "current_status": "EXACT_CONTRACT_ARM_ONLY__R7A_ADAPTER_UNBOUND",
        },
        {
            "arm_id": "UNIFORM_PROBING",
            "binding": None,
            "current_status": "MISSING_EXACT_IMPLEMENTATION_AND_R7A_ADAPTER",
        },
        {
            "arm_id": "CHEAPEST_FIRST_PROBING",
            "binding": None,
            "current_status": "MISSING_EXACT_IMPLEMENTATION_AND_R7A_ADAPTER",
        },
        {
            "arm_id": "UNCERTAINTY_OR_VOI_PROXY",
            "binding": {"path": rel(R2_POLICY), "sha256": sha256(R2_POLICY)},
            "current_status": "LEGACY_R2_POLICY_BOUND__R7A_ADAPTER_UNBOUND",
        },
        {
            "arm_id": "DONOR_COMPLETE",
            "binding": {"path": rel(R2_POLICY), "sha256": sha256(R2_POLICY)},
            "current_status": "LEGACY_R2_POLICY_BOUND__R7A_ADAPTER_UNBOUND",
        },
        {
            "arm_id": "DONOR_COMPLETE_FORCED_BUDGET",
            "binding": None,
            "current_status": "MISSING_EXACT_WRAPPER_AND_R7A_ADAPTER",
        },
        {
            "arm_id": "DONOR_COMPLETE_MATCHED_SCHEDULE",
            "binding": None,
            "current_status": "MISSING_EXACT_WRAPPER_AND_R7A_ADAPTER",
        },
        {
            "arm_id": "STRONGEST_RUNNABLE_EXTERNAL_SELF_REVISING_SCIENTIFIC_AGENT_AT_FREEZE",
            "binding": {
                "binding_id": agent_lab["binding_id"],
                "paper": agent_lab["primary_paper"],
                "repository": agent_lab["repository"],
                "repo_head": agent_lab["repo_head"],
                "repo_license": agent_lab["repo_license"],
                "run_entrypoint": agent_lab["run_entrypoint"],
            },
            "current_status": "CANDIDATE_IDENTITY_BOUND__NATIVE_INTERFACE_MIXED_OR_UNMAPPED__NOT_AN_R7A_ARM",
        },
    ]

    return {
        "schema_version": "orion.p1.r7a.comparator-interface-contract.v1",
        "date": "2026-08-23",
        "authority": "OUTCOME_BLIND_INTERFACE_AND_IDENTITY_PREFLIGHT_ONLY",
        "outcomes_accessed": False,
        "mandatory_primary_comparator_count": 9,
        "candidate": {
            "arm_id": "ORION_R7A",
            "binding": {"path": rel(R6_NATIVE), "sha256": sha256(R6_NATIVE)},
            "current_status": "NATIVE_PREDECESSOR_BOUND__R7A_COMMON_PAYLOAD_ACTION_ADAPTER_UNBOUND",
        },
        "common_candidate_visible_payload": {
            "canonicalization": "UTF-8 JSON, sorted keys, compact separators",
            "visible_fields": [
                "opaque_episode_handle",
                "dossier",
                "source_evidence_objects",
                "opaque_probe_handles",
                "admissible_opaque_action_handles",
                "resource_envelope",
            ],
            "forbidden_fields": [
                "gold_class",
                "causal_family",
                "decision_class",
                "pair_role",
                "source_id",
                "source_rank",
                "query_id",
                "evaluator_disposition",
                "protected_outcome",
                "filesystem_path",
                "answer_correlated_ordering",
            ],
            "same_exact_payload_bytes_and_digest_for_every_arm": True,
            "no_per_arm_evidence_augmentation": True,
        },
        "common_probe_contract": {
            "maximum_revealed_probes_per_episode": 2,
            "probe_ids": [
                "P_SEARCH_COVERAGE",
                "P_REPRESENTATION_ROUNDTRIP",
                "P_ENVIRONMENT_REPLAY",
                "P_MEASUREMENT_CROSSCHECK",
                "P_OBJECTIVE_PREDICTIVE_CHECK",
                "P_BOUNDARY_COUNTERFACTUAL",
            ],
            "observations": ["SUPPORT", "REFUTE", "INCONCLUSIVE"],
            "identical_availability_and_cost_for_every_arm": True,
            "every_request_metered_and_retained": True,
        },
        "common_terminal_action_contract": {
            "exactly_one_terminal_required": True,
            "terminals": [
                "KEEP_SEARCH",
                "KEEP_COMPILE",
                "KEEP_REPAIR",
                "REVISE_MEASUREMENT",
                "REFORMULATE_OBJECTIVE",
                "REFORMULATE_BOUNDARY",
                "UNRESOLVED",
            ],
            "malformed_timeout_or_missing_output": "RETAIN_AND_SCORE_FAILURE",
            "external_adapter_may_not_invent_a_terminal": True,
        },
        "resource_matching": {
            "all_required": True,
            "coordinates": [
                "base_model_and_exact_provider_revision",
                "temperature_seed_and_sampling_settings",
                "model_call_limit",
                "input_and_output_token_limit",
                "retrieval_corpus_and_query_limit",
                "probe_limit",
                "tool_and_verifier_call_limit",
                "wall_clock_cap",
                "all_access_costs",
            ],
            "if_exact_match_impossible": "FREEZE_AND_REPORT_A_COST_ADJUSTED_FRONTIER_FOR_EVERY_ARM_OR_RETURN_CANNOT_CHECK",
        },
        "terminal_preserving_external_adapter_law": {
            "criterion": "the target R7A decision is constant on every fibre of the external system's candidate-visible native output/interface",
            "required_evidence": "prospective conformance fixtures covering all seven terminals, errors, timeout, abstention, probe use, and action availability",
            "mixed_fibre_disposition": "INTERFACE_LIMITED__CANNOT_CHECK_AS_R7A_PRIMARY_ARM",
            "prompt_wrapper_warning": "a wrapper that supplies new responsibility logic or forces a non-native decision is a new common-interface proxy, not the named external system",
        },
        "primary_comparators": arm_rows,
        "external_pressure_test_not_primary": {
            "binding_id": ai_scientist["binding_id"],
            "paper": ai_scientist["primary_paper"],
            "repository": ai_scientist["repository"],
            "repo_head": ai_scientist["repo_head"],
            "repo_license": ai_scientist["repo_license"],
            "current_status": "SOURCE_AVAILABLE_RESTRICTED__INTERFACE_UNMAPPED__NOT_AN_R7A_ARM",
        },
        "exact_upstream_bindings": [
            {"path": rel(COMPARATOR_LEDGER), "sha256": sha256(COMPARATOR_LEDGER)},
            {"path": rel(COMPARATOR_REMOTE), "sha256": sha256(COMPARATOR_REMOTE)},
            {"path": rel(R7_CANDIDATE_VIEW), "sha256": sha256(R7_CANDIDATE_VIEW)},
        ],
        "current_terminal": "CANNOT_CHECK_COMPARATOR_REGISTRY_AND_INTERFACE_BINDING",
        "execution_authorized": False,
    }


def build_external_template() -> dict[str, Any]:
    binding_ids = [
        "CONTENT_CLASS_RIGHTS_OWNER",
        "PRIMARY_SOURCE_SELECTOR_AND_ELIGIBILITY_CUSTODIAN",
        "REPLICATION_SOURCE_SELECTOR_AND_ELIGIBILITY_CUSTODIAN",
        "OWNER_SEPARATED_CASE_CONSTRUCTOR_AND_GOLD_ADJUDICATION",
        "ORION_R7A_COMMON_INTERFACE_ADAPTER",
        "ALL_NINE_PRIMARY_COMPARATOR_ADAPTERS",
        "AGENT_LABORATORY_TERMINAL_PRESERVING_ADAPTER",
        "PRIMARY_SEMANTIC_HOST_AND_MODEL_PROVIDER_REVISION",
        "CHANGED_REPLICATION_SEMANTIC_HOST_AND_MODEL_PROVIDER_REVISION",
        "PRIMARY_PROTECTED_EVALUATOR_AND_SCORER_CUSTODY",
        "REPLICATION_PROTECTED_EVALUATOR_AND_SCORER_CUSTODY",
        "EXTERNAL_RESULT_VERIFIER_CUSTODY",
        "PRIMARY_PROTECTED_EXECUTION_ENVIRONMENT",
        "REPLICATION_PROTECTED_EXECUTION_ENVIRONMENT",
    ]
    return {
        "schema_version": "orion.p1.r7a.external-binding-receipt.v1",
        "authority": "TEMPLATE_ONLY__NO_EXTERNAL_CUSTODY_IS_INFERRED",
        "binding_status_vocabulary": ["MISSING", "CANNOT_CHECK", "BOUND_VERIFIED"],
        "required_identity_fields_when_bound": [
            "owner_or_system_identity",
            "role_and_write_boundary",
            "artifact_path_or_immutable_uri",
            "artifact_sha256",
            "signed_or_independently_verifiable_attestation",
            "bound_before_case_or_outcome_access",
        ],
        "bindings": [
            {
                "binding_id": binding_id,
                "status": "MISSING",
                "owner_or_system_identity": None,
                "role_and_write_boundary": None,
                "artifact_path_or_immutable_uri": None,
                "artifact_sha256": None,
                "signed_or_independently_verifiable_attestation": None,
                "bound_before_case_or_outcome_access": None,
            }
            for binding_id in binding_ids
        ],
    }


def build_preflight(source_hash: str, comparator_hash: str, template_hash: str) -> dict[str, Any]:
    local_bindings = [
        R7A_AMENDMENT,
        R7A_POWER,
        R7A_QUERY,
        R7_SOURCE_VALIDATOR,
        R7_CANDIDATE_VIEW,
        PROVIDER_CENSUS,
        PROVIDER_PROTOCOL,
        PROVIDER_RECEIPT,
        GITHUB_SNAPSHOT,
        GITHUB_STATUS,
        COMPARATOR_LEDGER,
        COMPARATOR_REMOTE,
        R7A_DEFICIENCY_AMENDMENT,
    ]
    return {
        "schema_version": "orion.p1.r7a.public-naturalistic-execution-preflight.v1",
        "date": "2026-08-23",
        "repository_head_observed": git_head(),
        "authority": "OUTCOME_BLIND_PREFLIGHT_ONLY__NO_SCIENTIFIC_OR_CUSTODY_AUTHORITY",
        "outcomes_accessed": False,
        "historical_results_immutable": True,
        "predecessor_boundaries": [
            "P1.H1.V1 remains NOT_SUPPORTED (1/48 root-task success for both candidate and registered baseline)",
            "R2-R4 acquisition failures remain CANNOT_CHECK records, not scientific zeros",
            "R6 remains conditional and does not establish same-visible-evidence, semantic-host, cost, or external-custody fairness",
            "the 2,882-world and 400-contract positives remain exact/mechanical evidence only",
            "the information-equivalent ideal product tie remains an immutable negative expressivity boundary",
        ],
        "scientific_question": "What legal-action deficiency and decision-mixed-fibre prevalence does each native candidate-visible interface induce on noisy public naturalistic scientific evidence, and secondarily does typed transition-responsibility licensing reduce excess loss without excess broad transition, unresolved-case resolution, preservation harm, or resource advantage?",
        "primary_estimands": [
            "SOURCE_CLUSTER_WEIGHTED_LEGAL_ACTION_DEFICIENCY_FOR_EACH_NATIVE_INTERFACE",
            "PREVALENCE_OF_DECISION_MIXED_NATIVE_INTERFACE_FIBRES",
            "DOMAIN_PROVIDER_MODALITY_DISTRIBUTION_OF_MIXED_FIBRES",
            "CALIBRATED_UNRESOLVED_USE_UNDER_DECLARED_LOSSES",
            "PREVALENCE_OF_FIBRES_WITH_NO_COMMON_LEGAL_NATIVE_ACTION",
        ],
        "secondary_estimand": "CANDIDATE_MINUS_COMPARATOR_EXCESS_LOSS_UNDER_THE_MATCHED_COMMON_INTERFACE",
        "registered_design": {
            "causal_families": 8,
            "protected_domains": 4,
            "pair_clusters_per_family_domain_cell_per_wave": 12,
            "paired_source_clusters_per_wave": 384,
            "unresolved_source_clusters_per_wave": 64,
            "source_clusters_per_wave": 448,
            "source_disjoint_waves": 2,
            "total_source_clusters": 896,
            "independent_unit": "unique source study/artifact family cluster",
            "technical_repeats_pair_members_probes_and_bootstrap_draws_do_not_increase_n": True,
            "nine_comparator_max_t_projected_joint_power_at_delta_0_20_discordance_0_40": 0.920216,
            "sensitivity_warning": "At delta 0.15 and discordance 0.40, n=384 has projected power 0.06778 and the simulated minimum is 896 paired clusters per wave; the current design is a large-effect design, not a guarantee.",
        },
        "rights_first_acquisition_order": [
            "bind independent owner roles and immutable query/provider revisions",
            "enumerate metadata only and deduplicate exact source-family identities",
            "rights owner adjudicates each content class before its bytes are opened",
            "external eligibility custodian applies the frozen criteria and returns sealed counts/exclusions",
            "freeze all 32 pair-cell and four unresolved-domain denominators",
            "construct owner-separated matched adverse/control dossiers and gold",
            "bind candidate and all nine comparator adapters to one payload/action/resource contract",
            "bind primary and changed-host replication evaluators, scorers, environments, and result verifier",
            "only then authorize candidate/comparator execution",
        ],
        "source_eligibility_all_required": [
            "rights-admissible exact content revision",
            "publicly auditable scientific/workflow episode without private author intent",
            "same-source adverse and control members sharing objective, artifact family, method, and context as closely as the source permits",
            "one source-grounded factor changes the licensed transition responsibility",
            "all six probe outcomes can be independently coded as SUPPORT, REFUTE, or INCONCLUSIVE",
            "protected decision or genuine UNRESOLVED can be adjudicated without using candidate outputs",
            "no candidate decision logic is used by constructors",
            "no filename, template, provider, path, ordering, source-rank, action-availability, or opaque-handle shortcut predicts protected labels",
            "one cluster maximum per canonical study, artifact, project, dataset, or companion-paper family",
        ],
        "provider_modality_transport_guards": [
            "both waves must contain at least four metadata providers and four artifact modalities",
            "every protected domain must contain at least two providers and two modalities per wave",
            "no provider may supply more than one third of a family-domain cell",
            "provider and modality interaction estimates are frozen before scoring and cannot rescue a failed primary claim",
            "zero eligible sources in a required cell is retained as a source-universe negative and the cell is not dropped",
        ],
        "artifact_bindings": [
            *[{"path": rel(path), "sha256": sha256(path)} for path in local_bindings],
            {"path": rel(HERE / "PUBLIC_SOURCE_RIGHTS_LEDGER_V1.json"), "sha256": source_hash},
            {"path": rel(HERE / "COMPARATOR_INTERFACE_CONTRACT_V1.json"), "sha256": comparator_hash},
            {"path": rel(HERE / "EXTERNAL_BINDINGS_TEMPLATE_V1.json"), "sha256": template_hash},
        ],
        "current_facts": {
            "candidate_metadata_roots": 28,
            "case_content_rights_bound": 0,
            "case_eligibility_assessed": 0,
            "complete_source_clusters": 0,
            "r7a_candidate_adapter_bound": False,
            "primary_comparator_arms_ready": 0,
            "external_custody_roles_bound": 0,
        },
        "noncompensatory_pre_execution_gates": [
            "SOURCE_RIGHTS_COMPLETE",
            "PRIMARY_SOURCE_FRAME_COMPLETE_384_PLUS_64",
            "REPLICATION_SOURCE_FRAME_COMPLETE_384_PLUS_64",
            "SOURCE_DISJOINTNESS_COMPLETE",
            "OWNER_SEPARATED_GOLD_AND_CASE_CONSTRUCTION",
            "ORION_R7A_ADAPTER_BOUND",
            "ALL_NINE_COMPARATOR_ARMS_BOUND",
            "EXTERNAL_ADAPTER_TARGET_PURE_OR_EXPLICITLY_INTERFACE_LIMITED",
            "BYTE_IDENTICAL_VISIBLE_PAYLOADS",
            "IDENTICAL_ACTION_PROBE_AND_RESOURCE_ENVELOPES",
            "PRIMARY_AND_CHANGED_REPLICATION_HOSTS_BOUND",
            "INDEPENDENT_PRIMARY_REPLICATION_SCORERS_BOUND",
            "EXTERNAL_RESULT_VERIFIER_BOUND",
            "PROTECTED_ENVIRONMENTS_BOUND",
            "ZERO_SHORTCUT_AND_LEAKAGE_HOSTILE_FAILURES",
        ],
        "execution_authorized": False,
        "current_terminal": "P1_R7A_CANNOT_CHECK_EXTERNAL_BINDINGS",
        "valid_future_scientific_terminals_only_after_authorized_execution": [
            "P1_R7A_WIDE_PROTECTED_SUPERIORITY_SUPPORTED_IN_REGISTERED_FRAMES",
            "P1_R7A_NOT_SUPPORTED",
            "P1_R7A_CANNOT_CHECK",
        ],
    }


def main() -> int:
    source_path = HERE / "PUBLIC_SOURCE_RIGHTS_LEDGER_V1.json"
    comparator_path = HERE / "COMPARATOR_INTERFACE_CONTRACT_V1.json"
    template_path = HERE / "EXTERNAL_BINDINGS_TEMPLATE_V1.json"
    preflight_path = HERE / "R7A_EXECUTION_PREFLIGHT_V1.json"

    write_json(source_path, build_source_rights_ledger())
    write_json(comparator_path, build_comparator_contract())
    write_json(template_path, build_external_template())
    write_json(
        preflight_path,
        build_preflight(sha256(source_path), sha256(comparator_path), sha256(template_path)),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
