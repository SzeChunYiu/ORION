#!/usr/bin/env python3
"""Build endpoint mappings and outcome-blind sampling manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


PROTOCOLS = {
    "P1": ROOT / "research/claim_expansion/p1/gpt_r7/R7A_MAXT_POWER_AMENDMENT_V2.json",
    "P2": ROOT / "papers/paper-02-open-world-scientific-discovery/protocol/P2_TASK_WORLD_SUCCESSOR_V2.json",
    "P3": ROOT / "papers/paper-03-global-knowledge-portrait/protocol/P3_PARTIAL_IDENTIFICATION_SUCCESSOR_V1.json",
    "P5": ROOT / "papers/paper-05-self-orion/protocol/P5_WIDE_REVISION_LEVEL_SUCCESSOR_V1.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def index(records: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    return {record[field]: record for record in records}


def source_ref(record: dict[str, Any], revision_key: str) -> dict[str, Any]:
    return {
        "source_id": record["source_id"],
        "canonical_url": record["canonical_url"],
        "immutable_revision": record.get(revision_key),
    }


def main() -> None:
    online = json.loads((HERE / "ONLINE_EVIDENCE_RECEIPTS.json").read_text())
    gh = index(online["github"], "source_id")
    hf = index(online["hugging_face"], "dataset_id")
    zenodo = index(online["zenodo"], "record_id")
    dataverse = online["dataverse"]

    endpoint_sources = {}
    for paper, path in PROTOCOLS.items():
        payload = json.loads(path.read_text())
        endpoint_sources[paper] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
            "claim_id": payload["claim_id"],
            "current_terminal": payload["current_terminal"],
            "design": payload["design"],
            "external_bindings_required": payload["external_bindings_required"],
        }

    bindings = {
        "schema_version": "orion.public-empirical-data-binding.v1",
        "captured_at_utc": online["captured_at_utc"],
        "authority": "PUBLIC_DATA_BINDING_PREFLIGHT_ONLY__NOT_EMPIRICAL_EVIDENCE__NOT_LEGAL_ADVICE",
        "papers": ["P1", "P2", "P3", "P5"],
        "excluded_papers": ["P4"],
        "dataset_rows_accessed": 0,
        "protected_outcome_bytes_accessed": False,
        "endpoint_sources": endpoint_sources,
        "paper_bindings": [
            {
                "paper_id": "P1",
                "successor_identity": "P1.NATURALISTIC.TRANSITION.TRANSPORT.V1",
                "exact_endpoint": "minimal licensed scientific transition from noisy natural evidence, with protected recovery/utility, no excess high-level rewrite, preservation and dependency-impact gates, against nine exact comparator arms in two source-disjoint waves",
                "candidate_bindings": [
                    {
                        **source_ref(hf["SWE-bench/SWE-bench_Multilingual"], "revision_sha"),
                        "downloadable_bytes": "YES__ONE_PINNED_PARQUET_LFS_OBJECT",
                        "rights": "MIT_IN_DATASET_CARD_AT_PINNED_REVISION",
                        "labels": "PUBLIC_ISSUE_PATCH_TEST_TRANSITION__NO_RESPONSIBILITY_OR_MINIMAL_SCIENTIFIC_LAYER_GOLD",
                        "eligibility": "SOFTWARE_ONLY__NO_FOUR_DOMAIN_OR_MIXED_FIBRE_ELIGIBILITY_AUDIT",
                        "freshness_custody": "PUBLIC_GOLD_AND_TEST_PATCH_FIELDS__NOT_PROTECTED_OR_FRESH",
                        "runnable_comparator": "SWE_AGENT_CAN_RUN_ON_THE_NATIVE_INTERFACE__NOT_AN_R7_ADAPTER",
                        "terminal": "PARTIAL_SOURCE_BYTES_ONLY__P1_ENDPOINT_OPEN",
                    },
                    {
                        **source_ref(gh["DEFECTS4J"], "commit_sha"),
                        "downloadable_bytes": "YES__COMMIT_ARCHIVE_AND_REPRODUCIBLE_BUG_FRAMEWORK",
                        "rights": "MIT_TEXT_AT_PINNED_license.txt",
                        "labels": "BUGGY_FIXED_REVISION_AND_TRIGGERING_TEST__NO_EPISTEMIC_TRANSITION_AUTHORITY_LABEL",
                        "eligibility": "REPRODUCIBLE_SOFTWARE_BUGS_ONLY",
                        "freshness_custody": "PUBLIC_BUG_IDENTITIES_AND_FIXES__NO_PROTECTED_WAVE",
                        "runnable_comparator": "FRAMEWORK_RUNNABLE__NO_NINE_ARM_R7_INTERFACE",
                        "terminal": "PARTIAL_REPRODUCIBLE_TRANSITION_ONLY__P1_ENDPOINT_OPEN",
                    },
                    {
                        **source_ref(hf["allenai/peer_read"], "revision_sha"),
                        "downloadable_bytes": "BUILDER_AND_DATASET_CARD_PUBLIC__EXTERNAL_DATA_PAYLOAD_ROUTE",
                        "rights": "CANNOT_CHECK__CARD_LICENSE_UNKNOWN_AND_REPOSITORY_LICENSE_FILE_ABSENT",
                        "labels": "REVIEWS_HISTORIES_AND_ACCEPTANCE__NO_MINIMAL_REVISION_OR_RESPONSIBILITY_GOLD",
                        "eligibility": "SCIENTIFIC_REVIEW_MODALITY_ONLY__CONTENT_CLASS_PERMISSION_UNBOUND",
                        "freshness_custody": "PUBLIC_HISTORICAL_RECORDS__NO_PROTECTED_SCORER",
                        "runnable_comparator": "NONE_BOUND_TO_R7",
                        "terminal": "CANNOT_CHECK_RIGHTS_AND_ENDPOINT_LABELS",
                    },
                ],
                "comparator_candidate": {
                    **source_ref(gh["SWE_AGENT_COMPARATOR"], "commit_sha"),
                    "license": "MIT",
                    "native_function": "AUTONOMOUS_GITHUB_ISSUE_RESOLUTION_AND_SWE_BENCH_BATCH_RUNNER",
                    "missing_for_p1": "BYTE_EQUIVALENT_R7_DOSSIER_ACTION_RESPONSIBILITY_AND_MATCHED_RESOURCE_ADAPTER",
                    "status": "RUNNABLE_ISSUE_SOLVER__NOT_A_FROZEN_R7_ARM",
                },
                "closed_cells": [
                    "PINNED_PUBLIC_SOFTWARE_TRANSITION_BYTES_EXIST",
                    "ONE_DATASET_CARD_LICENSE_AND_ONE_BUG_FRAMEWORK_LICENSE_ARE_EXPLICIT",
                ],
                "still_open": endpoint_sources["P1"]["external_bindings_required"]
                + [
                    "PROTECTED_RESPONSIBILITY_AND_MINIMAL_TRANSITION_GOLD",
                    "FOUR_DOMAIN_PROVIDER_MODALITY_ELIGIBILITY",
                    "ISSUE_REVIEW_ATTACHMENT_CONTENT_RIGHTS",
                    "NINE_LAWFUL_R7_COMPARATOR_ADAPTERS",
                ],
                "paper_level_blocker_closed": False,
            },
            {
                "paper_id": "P2",
                "successor_identity": "P2.GUARDED.ENVELOPE.EXTERNAL.V1",
                "exact_endpoint": "paired task-world gold-recall success without false inclusion across four source-disjoint arenas under identical query, provider, budget and scoring exposure, with independent obligation custody and three frozen comparators",
                "candidate_bindings": [
                    {
                        **source_ref(dataverse, "version"),
                        "downloadable_bytes": "YES__144_VERSIONED_FILES_WITH_PROVIDER_SHA1_CHECKSUMS",
                        "rights": "CC0_1_0_AT_DATAVERSE_DATASET_VERSION_1_0",
                        "labels": "26_SYSTEMATIC_REVIEW_INCLUSION_LABEL_FILES_AND_ELIGIBILITY_CRITERIA",
                        "eligibility": "NATURALISTIC_BOUNDED_SCREENING_WORLDS__NOT_OPEN_WEB_ROUTE_WORLDS",
                        "freshness_custody": "LABELS_PUBLIC__NO_PROTECTED_OBLIGATION_GOLD",
                        "runnable_comparator": "ASREVIEW_PINNED_SEPARATELY__NATIVE_SCREENING_NOT_CLOSURE_AUTHORITY",
                        "terminal": "LICENSED_BOUNDED_SCREENING_GOLD_BOUND__P2_OPEN_WORLD_ENDPOINT_OPEN",
                    },
                    {
                        **source_ref(zenodo["10423427"], "record_id"),
                        "downloadable_bytes": "YES__ONE_PINNED_53_881_052_BYTE_CSV_WITH_MD5",
                        "rights": "CC_BY_4_0_IN_ZENODO_RECORD",
                        "labels": "25_540_DEDUPLICATED_CITATIONS_LABELLED_INCLUDE_EXCLUDE_BY_TWO_REVIEWERS",
                        "eligibility": "ONE_PHYSIOTHERAPY_SYSTEMATIC_REVIEW_UPDATE__ONE_ARENA_ONLY",
                        "freshness_custody": "PUBLIC_LABELS__NO_PROTECTED_GOLD",
                        "runnable_comparator": "ASREVIEW_FORMAT_ADAPTER_FEASIBLE_BUT_NOT_FROZEN",
                        "terminal": "ONE_LICENSED_NATURALISTIC_POOL_BOUND__MULTI_ARENA_ENDPOINT_OPEN",
                    },
                    {
                        **source_ref(hf["allenai/scifact"], "revision_sha"),
                        "downloadable_bytes": "BUILDER_AND_CARD_PINNED__CANONICAL_S3_LATEST_DATA_URL_IS_MUTABLE",
                        "rights": "CONTENT_CLASS_SPECIFIC__CLAIMS_CC_BY_4_0__ABSTRACTS_ODC_BY_1_0__CODE_APACHE_2_0__HF_CARD_SAYS_CC_BY_NC_2_0",
                        "labels": "SCIENTIFIC_CLAIM_EVIDENCE_LABELS__ORIGINAL_TEST_GOLD_WITHHELD",
                        "eligibility": "BOUNDED_CLAIM_VERIFICATION_NOT_OPEN_WORLD_TASK_CLOSURE",
                        "freshness_custody": "ORIGINAL_TEST_LABELS_PROVIDER_HELD_BUT_CAMPAIGN_IDENTITY_AND_EPOCH_UNBOUND",
                        "runnable_comparator": "OFFICIAL_PIPELINE_EXISTS__NO_P2_CLOSURE_TERMINAL_ADAPTER",
                        "terminal": "LICENCE_SCHEMA_CONFLICT_AND_ENDPOINT_MISMATCH__P2_OPEN",
                    },
                ],
                "comparator_candidate": {
                    **source_ref(gh["ASREVIEW_COMPARATOR"], "commit_sha"),
                    "license": "APACHE_2_0",
                    "native_function": "ACTIVE_LEARNING_SCREENING_AND_SIMULATION",
                    "missing_for_p2": "ROUTE_TRACE_EXPOSURE_COST_AND_THREE_VALUED_TASK_CLOSURE_ADAPTER",
                    "status": "RUNNABLE_DONOR_CANDIDATE__NOT_A_FROZEN_P2_ARM",
                },
                "closed_cells": [
                    "PUBLIC_LICENSED_NATURALISTIC_SYSTEMATIC_REVIEW_POOLS_EXIST",
                    "INCLUSION_LABEL_AND_ELIGIBILITY_CRITERIA_FILES_HAVE_VERSIONED_IDENTITIES",
                    "ONE_RUNNABLE_SCREENING_DONOR_IS_PINNED",
                ],
                "still_open": endpoint_sources["P2"]["external_bindings_required"]
                + [
                    "OPEN_WEB_PROVIDER_AND_ROUTE_WORLD_BINDING",
                    "FUTURE_OPTION_AND_TASK_CLOSURE_GOLD",
                    "ASREVIEW_OR_SIEVE_TERMINAL_PRESERVING_ADAPTER",
                ],
                "paper_level_blocker_closed": False,
            },
            {
                "paper_id": "P3",
                "successor_identity": "P3.ENVELOPE.COVERAGE.TRANSPORT.V1",
                "exact_endpoint": "floor-adjusted avoidable false merge or downstream decision harm on 768 source-artifact-family clusters, with nonzero referent/construct/measurement/temporal variation, independent gold, raw-text attack and four comparators",
                "candidate_bindings": [
                    {
                        **source_ref(zenodo["3460908"], "record_id"),
                        "downloadable_bytes": "YES__THREE_PINNED_ARCHIVES_WITH_MD5",
                        "rights": "CC_BY_NC_SA_3_0_IN_ZENODO_RECORD",
                        "labels": "BIOMEDICAL_FULL_TEXT_CONCEPT_ANNOTATION_COREFERENCE_AND_SEPARATE_EVALUATION_GOLD",
                        "eligibility": "RAW_TEXT_AND_GOLD_AVAILABLE__SINGLE_BIOMEDICAL_DOMAIN",
                        "freshness_custody": "EVALUATION_GOLD_PUBLICLY_DOWNLOADABLE__NOT_INTRINSICALLY_PROTECTED",
                        "runnable_comparator": "SHARED_TASK_FORMAT__NO_P3_SET_VALUED_TERMINAL_ADAPTER",
                        "terminal": "RAW_TEXT_GOLD_SOURCE_BOUND__MULTI_DOMAIN_ENVELOPE_ENDPOINT_OPEN",
                    },
                    {
                        **source_ref(gh["SCIREX"], "commit_sha"),
                        "downloadable_bytes": "YES__PINNED_7_318_844_BYTE_RELEASE_ARCHIVE_HEAD_WITH_STRONG_ETAG",
                        "rights": "APACHE_2_0_REPOSITORY__UNDERLYING_ARTICLE_TEXT_CONTENT_CLASS_NOT_INDEPENDENTLY_CLEARED",
                        "labels": "METHOD_METRIC_TASK_MATERIAL_SCORE_RELATIONS_AND_COREFERENCE",
                        "eligibility": "README_REPORTS_APPROXIMATELY_HALF_OF_RELATIONS_HAVE_AN_ENTITY_WITH_NO_RETAINED_MENTION",
                        "freshness_custody": "PUBLIC_RELEASE__NO_PROTECTED_GOLD",
                        "runnable_comparator": "OFFICIAL_MODEL_CODE_EXISTS__NO_P3_PORTRAIT_TERMINAL",
                        "terminal": "ADVERSE_OBSERVATION_COVERAGE_AND_RIGHTS_AUDIT_REQUIRED",
                    },
                    {
                        **source_ref(zenodo["15827226"], "record_id"),
                        "downloadable_bytes": "YES__PINNED_486_043_BYTE_ZIP_WITH_MD5",
                        "rights": "CC_BY_4_0_IN_ZENODO_RECORD",
                        "labels": "REFERENCE_ONTOLOGY_ALIGNMENTS",
                        "eligibility": "SYSTEMATIC_ALTERATIONS_OF_ONE_BIBLIOGRAPHIC_SEED__NOT_NATURALISTIC_MULTI_DOMAIN_RAW_TEXT",
                        "freshness_custody": "PUBLIC_REFERENCE_ALIGNMENTS__NO_PROTECTED_GOLD",
                        "runnable_comparator": "OAEI_MATCHERS_POSSIBLE__NO_FOUR_EXACT_ARMS_BOUND",
                        "terminal": "LICENSED_ALIGNMENT_CONTROL_BOUND__P3_ENDPOINT_OPEN",
                    },
                ],
                "comparator_candidate": {
                    **source_ref(gh["OPENEA"], "commit_sha"),
                    "license": "GPL_3_0",
                    "native_function": "ENTITY_ALIGNMENT_BENCHMARK_AND_TWELVE_REPRESENTATIVE_METHODS",
                    "missing_for_p3": "SCIENCE_SPECIFIC_COORDINATES_SET_VALUED_INVALID_TERMINAL_AND_UNDERLYING_KG_RIGHTS_MATRIX",
                    "status": "RUNNABLE_DONOR_TOOLKIT__NOT_FOUR_FROZEN_P3_ARMS",
                },
                "closed_cells": [
                    "PINNED_LICENSED_RAW_TEXT_CONCEPT_GOLD_EXISTS_IN_ONE_DOMAIN",
                    "PINNED_LICENSED_REFERENCE_ALIGNMENT_CONTROL_EXISTS",
                    "ONE_GENERAL_ENTITY_ALIGNMENT_TOOLKIT_IS_PINNED",
                ],
                "still_open": endpoint_sources["P3"]["external_bindings_required"]
                + [
                    "NONZERO_VARIATION_ON_ALL_FOUR_SCIENTIFIC_COORDINATES",
                    "PUBLICATION_TEXT_CONTENT_CLASS_RIGHTS_PER_ARTICLE",
                    "FOUR_EXACT_COMPARATOR_ADAPTERS",
                    "PROTECTED_DOWNSTREAM_LOSS_AND_DECISION_AUTHORITY",
                ],
                "paper_level_blocker_closed": False,
            },
            {
                "paper_id": "P5",
                "successor_identity": "P5.FRESH.AUTHORITY.CAMPAIGN.V1",
                "exact_endpoint": "correct minimal revision with preservation and protected fresh-transfer success across eight revision classes and eight domains, with six frozen comparators and every harm gate noncompensatory",
                "candidate_bindings": [
                    {
                        **source_ref(hf["SWE-bench/SWE-bench_Multilingual"], "revision_sha"),
                        "downloadable_bytes": "YES__ONE_PINNED_PARQUET_LFS_OBJECT__300_TASKS",
                        "rights": "MIT_IN_DATASET_CARD",
                        "labels": "PUBLIC_ISSUE_GOLD_PATCH_TEST_PATCH_AND_TEST_LISTS",
                        "eligibility": "IMPLEMENTATION_OR_EXECUTION_REPAIR_ONLY__NO_EIGHT_REVISION_CLASS_GOLD",
                        "freshness_custody": "ALL_GOLD_FIELDS_PUBLIC__NOT_PROTECTED_FRESH_TRANSFER",
                        "runnable_comparator": "SWE_AGENT_PINNED_SEPARATELY_AS_FIXED_ISSUE_SOLVER",
                        "terminal": "ONE_PUBLIC_SOFTWARE_TASK_SOURCE_BOUND__P5_PRIMARY_ENDPOINT_OPEN",
                    },
                    {
                        **source_ref(hf["SWE-bench/SWE-bench_Verified"], "revision_sha"),
                        "downloadable_bytes": "YES__ONE_PINNED_PARQUET_LFS_OBJECT__500_TASKS",
                        "rights": "CANNOT_CHECK__CURRENT_DATASET_CARD_HAS_NO_LICENSE_FIELD_OR_LICENSE_TAG",
                        "labels": "PUBLIC_HUMAN_VALIDATED_ISSUE_PATCH_AND_TEST_FIELDS",
                        "eligibility": "IMPLEMENTATION_BUG_ONLY__NO_HIDDEN_REVISION_RESPONSIBILITY",
                        "freshness_custody": "PUBLIC_GOLD__NO_PROTECTED_EVALUATOR",
                        "runnable_comparator": "SWE_BENCH_HARNESS_RUNNABLE__NOT_SELF_EVOLUTION",
                        "terminal": "CANNOT_CHECK_DATASET_RIGHTS__P5_ENDPOINT_OPEN",
                    },
                    {
                        **source_ref(gh["DEFECTS4J"], "commit_sha"),
                        "downloadable_bytes": "YES__854_ACTIVE_REPRODUCIBLE_BUGS_REPORTED_AT_PIN",
                        "rights": "MIT_TEXT_AT_PINNED_license.txt",
                        "labels": "BUGGY_FIXED_REVISION_AND_TRIGGERING_TEST",
                        "eligibility": "IMPLEMENTATION_CLASS_ONLY",
                        "freshness_custody": "PUBLIC_FIXES__NO_PROTECTED_SPLIT",
                        "runnable_comparator": "REPRODUCTION_FRAMEWORK_ONLY",
                        "terminal": "REPRODUCIBLE_IMPLEMENTATION_STRATUM_CANDIDATE__P5_OPEN",
                    },
                    {
                        **source_ref(gh["BUGSWARM"], "commit_sha"),
                        "downloadable_bytes": "PUBLIC_REST_API_AND_DOCKER_ARTIFACT_ROUTE__NO_ARTIFACT_BODY_FETCHED",
                        "rights": "BSD_3_CLAUSE_FOR_INFRASTRUCTURE__UNDERLYING_PROJECT_AND_CONTAINER_CONTENT_RIGHTS_UNBOUND",
                        "labels": "REAL_CI_FAIL_PASS_PAIRS__NO_PROTECTED_CAUSAL_REVISION_LABEL",
                        "eligibility": "ENVIRONMENT_EXECUTION_FAILURE_CANDIDATE_ONLY",
                        "freshness_custody": "PUBLIC_MINED_ARTIFACTS__NO_FRESH_HOST_CUSTODY",
                        "runnable_comparator": "BUGSWARM_TOOLING_AVAILABLE__NO_SELF_REVISION_ARMS",
                        "terminal": "CANNOT_CHECK_ARTIFACT_RIGHTS_AND_CAUSAL_LABELS",
                    },
                    {
                        **source_ref(gh["BUGSINPY"], "commit_sha"),
                        "downloadable_bytes": "YES__PINNED_REPOSITORY_ARCHIVE",
                        "rights": "CANNOT_CHECK__NO_ROOT_LICENSE_FILE_AT_PIN",
                        "labels": "BUGGY_FIXED_PROJECT_VERSIONS",
                        "eligibility": "IMPLEMENTATION_BUG_ONLY",
                        "freshness_custody": "PUBLIC_FIXES__NO_PROTECTED_SPLIT",
                        "runnable_comparator": "FRAMEWORK_RUNNABLE",
                        "terminal": "CANNOT_CHECK_RIGHTS__P5_ENDPOINT_OPEN",
                    },
                ],
                "comparator_candidate": {
                    **source_ref(gh["SWE_AGENT_COMPARATOR"], "commit_sha"),
                    "license": "MIT",
                    "native_function": "AUTONOMOUS_GITHUB_ISSUE_RESOLUTION_AND_SWE_BENCH_BATCH_RUNNER",
                    "missing_for_p5": "PERSISTENT_ISSUE_STATE_SELF_EDIT_SELF_EVOLUTION_REVISION_CLASS_AND_HOST_PROMOTION_INTERFACES",
                    "status": "ONE_FIXED_AGENT_BASELINE_PINNED__SIX_ARM_FREEZE_OPEN",
                },
                "closed_cells": [
                    "PINNED_LICENSED_MULTILINGUAL_ISSUE_PATCH_TASK_BYTES_EXIST",
                    "PINNED_REPRODUCIBLE_BUG_FRAMEWORK_EXISTS",
                    "ONE_RUNNABLE_FIXED_ISSUE_SOLVER_BASELINE_IS_PINNED",
                ],
                "still_open": endpoint_sources["P5"]["external_bindings_required"]
                + [
                    "PROTECTED_EIGHT_CLASS_REVISION_RESPONSIBILITY_GOLD",
                    "SAME_VISIBLE_SYMPTOM_BLOCKING",
                    "FRESH_TRANSFER_AND_HARM_OUTCOMES",
                    "SIX_EXACT_SELF_EDIT_OR_SELF_EVOLUTION_ARMS",
                ],
                "paper_level_blocker_closed": False,
            },
        ],
        "closure_summary": {
            "papers_audited": 4,
            "paper_level_empirical_blockers_closed": 0,
            "paper_level_empirical_blockers_still_open": 4,
            "closed_preflight_fact_classes": [
                "IMMUTABLE_PUBLIC_SOURCE_IDENTITIES",
                "SOME_CONTENT_CLASS_LICENSES",
                "SOME_PUBLIC_LABEL_SCHEMAS",
                "SOME_RUNNABLE_DONOR_TOOLKITS",
            ],
            "not_closed": [
                "CASE_ELIGIBILITY_FOR_ANY_REGISTERED_WIDE_PANEL",
                "PROTECTED_FRESHNESS_OR_EXTERNAL_CUSTODY",
                "ANY_COMPLETE_COMPARATOR_FAMILY",
                "ANY_PROSPECTIVE_PAPER_ENDPOINT",
            ],
            "scientific_terminal": "PUBLIC_SOURCE_SUBSTRATE_PARTIALLY_BOUND__NO_PAPER_LEVEL_EMPIRICAL_BLOCKER_CLOSED",
        },
    }

    # Outcome-blind sampling manifests select only public file identities or
    # whole split metadata. No row, label, issue, patch, test, or archive body is opened.
    synergy_labels = [
        file for file in dataverse["files"] if file["label"] == "labels.csv"
    ]
    selected_synergy = sorted(
        synergy_labels,
        key=lambda item: hashlib.sha256(item["directory_label"].encode()).hexdigest(),
    )[:4]
    swe_multi_file = next(
        sibling
        for sibling in hf["SWE-bench/SWE-bench_Multilingual"]["siblings"]
        if sibling["path"].endswith(".parquet")
    )
    swe_verified_file = next(
        sibling
        for sibling in hf["SWE-bench/SWE-bench_Verified"]["siblings"]
        if sibling["path"].endswith(".parquet")
    )
    sampling = {
        "schema_version": "orion.public-empirical-data-binding.sampling-manifests.v1",
        "captured_at_utc": online["captured_at_utc"],
        "authority": "OUTCOME_BLIND_FILE_IDENTITY_SELECTION_ONLY",
        "dataset_rows_accessed": 0,
        "label_values_accessed": 0,
        "protected_outcome_bytes_accessed": False,
        "manifests": [
            {
                "paper_id": "P1",
                "manifest_id": "P1_PUBLIC_TRANSITION_SOURCE_PREFLIGHT_V1",
                "selected_objects": [
                    {
                        "source_id": "SWE-BENCH__SWE-BENCH_MULTILINGUAL",
                        "revision_sha": hf["SWE-bench/SWE-bench_Multilingual"]["revision_sha"],
                        "path": swe_multi_file["path"],
                        "lfs_sha256": swe_multi_file["lfs"]["sha256"],
                        "declared_split_examples": 300,
                    },
                    {
                        "source_id": "ALLENAI__PEER_READ",
                        "revision_sha": hf["allenai/peer_read"]["revision_sha"],
                        "selected_at": "DATASET_CARD_AND_BUILDER_REVISION_ONLY",
                        "reason_no_payload": "LICENCE_UNKNOWN_AND_ENDPOINT_LABELS_INADEQUATE",
                    },
                ],
                "row_ids_materialized": False,
                "eligibility_status": "CANNOT_CHECK_P1_WIDE_PANEL_ELIGIBILITY",
            },
            {
                "paper_id": "P2",
                "manifest_id": "P2_SYSTEMATIC_REVIEW_WORLD_PREFLIGHT_V1",
                "selection_rule": "FOUR_LOWEST_SHA256_DIRECTORY_LABELS_AMONG_26_VERSION_1_0_labels.csv_FILES",
                "selected_objects": selected_synergy,
                "row_ids_materialized": False,
                "eligibility_status": "FOUR_BOUNDED_SCREENING_WORLD_FILES_SELECTED__FOUR_OPEN_WORLD_ARENAS_NOT_BOUND",
            },
            {
                "paper_id": "P3",
                "manifest_id": "P3_RAW_TEXT_ALIGNMENT_PREFLIGHT_V1",
                "selected_objects": [
                    *[
                        {
                            "source_id": "ZENODO_3460908",
                            "key": file["key"],
                            "size": file["size"],
                            "checksum": file["checksum"],
                        }
                        for file in zenodo["3460908"]["files"]
                    ],
                    {
                        "source_id": "ZENODO_15827226",
                        "key": zenodo["15827226"]["files"][0]["key"],
                        "size": zenodo["15827226"]["files"][0]["size"],
                        "checksum": zenodo["15827226"]["files"][0]["checksum"],
                    },
                    {
                        "source_id": "SCIREX",
                        "commit_sha": gh["SCIREX"]["commit_sha"],
                        "path": gh["SCIREX"]["metadata_only_file_heads"][0]["path"],
                        "content_length_header": gh["SCIREX"]["metadata_only_file_heads"][0]["content_length_header"],
                        "http_etag": gh["SCIREX"]["metadata_only_file_heads"][0]["etag"],
                    },
                ],
                "archive_bodies_opened": 0,
                "row_ids_materialized": False,
                "eligibility_status": "ONE_RAW_TEXT_BIOMEDICAL_GOLD_SOURCE_AND_TWO_ALIGNMENT_CONTROLS_BOUND__P3_MULTI_DOMAIN_PANEL_OPEN",
            },
            {
                "paper_id": "P5",
                "manifest_id": "P5_PUBLIC_DEVELOPMENT_FAILURE_PREFLIGHT_V1",
                "selected_objects": [
                    {
                        "source_id": "SWE-BENCH__SWE-BENCH_MULTILINGUAL",
                        "revision_sha": hf["SWE-bench/SWE-bench_Multilingual"]["revision_sha"],
                        "path": swe_multi_file["path"],
                        "lfs_sha256": swe_multi_file["lfs"]["sha256"],
                        "declared_split_examples": 300,
                    },
                    {
                        "source_id": "SWE-BENCH__SWE-BENCH_VERIFIED",
                        "revision_sha": hf["SWE-bench/SWE-bench_Verified"]["revision_sha"],
                        "path": swe_verified_file["path"],
                        "lfs_sha256": swe_verified_file["lfs"]["sha256"],
                        "declared_split_examples": 500,
                    },
                    {
                        "source_id": "DEFECTS4J",
                        "commit_sha": gh["DEFECTS4J"]["commit_sha"],
                        "tree_sha": gh["DEFECTS4J"]["tree_sha"],
                    },
                    {
                        "source_id": "BUGSWARM",
                        "commit_sha": gh["BUGSWARM"]["commit_sha"],
                        "artifact_bodies_opened": 0,
                    },
                ],
                "row_ids_materialized": False,
                "eligibility_status": "IMPLEMENTATION_AND_EXECUTION_SOURCE_FAMILIES_ONLY__EIGHT_CLASS_PROTECTED_PANEL_OPEN",
            },
        ],
    }

    (HERE / "PUBLIC_SOURCE_BINDINGS.json").write_text(
        json.dumps(bindings, indent=2, sort_keys=True) + "\n"
    )
    (HERE / "MINIMAL_SAMPLING_MANIFESTS.json").write_text(
        json.dumps(sampling, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
