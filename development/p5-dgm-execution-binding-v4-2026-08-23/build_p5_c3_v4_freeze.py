#!/usr/bin/env python3
"""Build the self-contained, outcome-blind P5 C3 DGM V4 freeze.

This builder does not import or execute DGM and does not read any upstream
benchmark/output payload.  It writes only inside this development directory.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
FROZEN_AT = "2026-08-23T18:15:39Z"
ARM_ID = "C3_ARCHIVE_BASED_SELF_EDIT__DGM"
COMMIT = "a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2"
TREE = "dc58ea5c481124afdb97468c1bed4e0debb425c4"
ARCHIVE_SHA = "bb92fc4c9f1a2a930059a9fa92db32f0d2ee81e030dd6925a9afbb4b2f3f1ee4"
ARCHIVE_FORMAT = "git archive --format=tar <commit>"
TERMINAL = (
    "P5_C3_V4_DGM_SOURCE_NATIVE_PARSER_EMPTY_FALLBACK_AND_OUTER_WALLCLOCK_BOUND__"
    "UNPINNED_DEPENDENCIES_NOT_MISLABELED_AS_LOCK__FIFTEEN_C3_FIELDS_BLOCKING__"
    "ZERO_OF_SIX_PANEL_READY__PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(name: str, value: Any) -> None:
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def entry(
    state: str,
    *,
    binding: Any,
    cause: str | None,
    residual: str,
    next_discriminator: str,
) -> dict[str, Any]:
    return {
        "binding": binding,
        "cause": cause,
        "next_discriminator": next_discriminator,
        "residual": residual,
        "state": state,
    }


def main() -> None:
    parser_hash = sha(HERE / "p5_c3_native_parser.py")
    runner_hash = sha(HERE / "p5_c3_fail_closed_runner.py")
    output_schema_hash = sha(HERE / "P5_C3_V4_NATIVE_OUTPUT_SCHEMA.json")
    case_requirements_hash = sha(HERE / "P5_C3_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json")

    required = [
        "adapter.isolated_write_surface",
        "adapter.native_parser_binding",
        "custody.external_protected_scorer",
        "custody.one_shot_no_feedback_barrier",
        "custody.protected_panel_freshness",
        "identity.native_entrypoint_bytes",
        "identity.source_license_bytes",
        "identity.source_repository_commit",
        "inputs.candidate_visible_case_bytes",
        "model_provider.fallbacks",
        "model_provider.primary",
        "resources.calls_tokens_usd",
        "resources.retry_network",
        "resources.wallclock",
        "rights.container_and_generated_artifacts",
        "rights.model_provider_and_services",
        "rights.task_and_benchmark_content",
        "runtime.compute",
        "runtime.container_or_environment",
        "runtime.dependency_lock",
        "runtime.task_environment",
    ]

    fields = {
        "adapter.isolated_write_surface": entry(
            "CANNOT_CHECK",
            binding={
                "fail_closed_gate": "p5_c3_fail_closed_runner.py",
                "gate_sha256": runner_hash,
                "frozen_schema": "P5_C3_V4_WRITE_SURFACE_SCHEMA.json",
                "released_native_writes": [
                    "./output_dgm/<run_id>/ logs, metadata, predictions and patches",
                    "mutable Git worktree inside the DGM container",
                    "Docker images and containers through a host daemon",
                    "task repositories and SWE-bench evaluation containers",
                ],
            },
            cause="The released DGM copies the complete repository into a mutable container, executes untrusted model-generated code, mutates Git state, writes output/archive/evaluation material, and controls Docker. No content-addressed disposable VM, rootless daemon or complete mutation proof is bound.",
            residual="The schema and fail-closed gate prevent accidental launch but do not prove isolation, daemon containment, egress closure or cleanup.",
            next_discriminator="Use a dedicated disposable Linux VM with a private rootless Docker daemon, a filtered read-only source seed, complete mount/network policy, and before/after digests of every allowed mutation root.",
        ),
        "adapter.native_parser_binding": entry(
            "BOUND",
            binding={
                "path": "p5_c3_native_parser.py",
                "sha256": parser_hash,
                "input": "adapter-authored pre-evaluation DGM patch-capture schema V4",
                "output_schema": "P5_C3_V4_NATIVE_OUTPUT_SCHEMA.json",
                "output_schema_sha256": output_schema_hash,
                "protected_key_policy": "exact and prefix-family fail closed; unknown root keys refused",
                "raw_native_singletons_licensed": 0,
            },
            cause=None,
            residual="The parser retains a source-native pre-evaluation terminal and patch identity while always emitting UNRESOLVED. It does not run the V3 certificate/action/fibre operation and never infers a responsibility class.",
            next_discriminator="Keep parser and schemas byte-frozen; after a lawful attempt, validate the input-native eight-class certificate and action/fibre proof separately outside candidate custody.",
        ),
        "custody.external_protected_scorer": entry(
            "CANNOT_CHECK",
            binding=None,
            cause="No independent scorer principal, immutable scorer digest, access-control policy or signed acceptance exists.",
            residual="C3 is not licensed for confirmatory scoring.",
            next_discriminator="An independent custodian supplies scorer identity, code digest and access-control attestation without revealing protected bytes.",
        ),
        "custody.one_shot_no_feedback_barrier": entry(
            "CANNOT_CHECK",
            binding=None,
            cause="Local code cannot self-attest one accepted successor, one score event and absence of a feedback path to DGM/candidate custody.",
            residual="C3 is not licensed for confirmatory execution.",
            next_discriminator="An independent custodian binds an append-only one-shot receipt and verifies that no protected diagnostic, score or outcome returns to adaptation custody.",
        ),
        "custody.protected_panel_freshness": entry(
            "CANNOT_CHECK",
            binding=None,
            cause="No protected panel identity or post-freeze freshness attestation was available.",
            residual="C3 is not licensed for confirmatory execution.",
            next_discriminator="Freeze a fresh protected panel only after the public-development DGM archive and protocol are locked; reveal only the authorized closing receipt.",
        ),
        "identity.native_entrypoint_bytes": entry(
            "BOUND",
            binding={
                "primary_entrypoint": "DGM_outer.py",
                "primary_entrypoint_sha256": "239bc76f0e1b78210b8f7b3757b1082f6ca07db3537d6af50a45bf97709795ed",
                "self_improve_path": "self_improve_step.py",
                "self_improve_sha256": "6f2ec364b11e7f6d35391ea66896fa2394cbca3bc59d68cf7352c2a77aa8cca7",
                "coding_agent_path": "coding_agent.py",
                "coding_agent_sha256": "0fe9f4806fee18a481c9298a6d1ab6d754bb81666031598d86a9da2b632a5829",
                "dockerfile_sha256": "55616682db154e7597b92f3406fa7bb240d91986d2f76581ba3f4a60941b6f7e",
            },
            cause=None,
            residual="Exact DGM orchestration, self-edit, coding-agent and Dockerfile bytes are retained; source defects are preserved rather than patched in place.",
            next_discriminator="Reverify these bytes at execution handoff and treat any source repair as a separately named successor arm.",
        ),
        "identity.source_license_bytes": entry(
            "BOUND",
            binding={
                "spdx": "Apache-2.0",
                "license_path": "LICENSE",
                "license_sha256": "84b7504ce8dda1f37f592cdf67ad21371864583720d79ea289b0b0c75bfcdb17",
            },
            cause=None,
            residual="The root source licence is byte-addressed; this does not close benchmark, dependency, container, service, task, generated-artifact or protected-panel rights.",
            next_discriminator="Carry the licence in any source bundle and inventory every other rights layer independently.",
        ),
        "identity.source_repository_commit": entry(
            "BOUND",
            binding={
                "repository": "https://github.com/jennyzzt/dgm",
                "commit_sha": COMMIT,
                "tree_sha": TREE,
                "commit_time": "2025-08-13T11:40:14+01:00",
                "archive_format": ARCHIVE_FORMAT,
                "archive_sha256": ARCHIVE_SHA,
            },
            cause=None,
            residual="The released DGM source identity is byte-addressed. The archive contains prior output/result paths; their payload contents were not opened in this lane.",
            next_discriminator="Fetch by commit, verify tree/archive identities, and create a filtered execution seed without opening or copying excluded outcome payloads into candidate custody.",
        ),
        "inputs.candidate_visible_case_bytes": entry(
            "UNBOUND",
            binding={
                "requirements_path": "P5_C3_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json",
                "requirements_sha256": case_requirements_hash,
                "upstream_outcome_prefixes_excluded": [
                    "initial/",
                    "initial_polyglot/",
                    "swe_bench/ref_agent_results/",
                ],
            },
            cause="No exact rights-cleared P5 failure packet, public-development archive seed or input-native eight-class certificate is frozen. The authoritative repository includes 1,595 tracked outcome/initial files that cannot silently enter the candidate-visible packet.",
            residual="The requirements are frozen, but no substantive C3 case bytes are licensed or content-addressed.",
            next_discriminator="Author or license one minimal P5 failure packet and certificate, hash it before DGM access, and prove that all excluded outcome/protected/gold paths are absent from candidate custody.",
        ),
        "model_provider.fallbacks": entry(
            "BOUND",
            binding={
                "fallbacks": [],
                "closed_behavior": "FAIL_WITH_NATIVE_TERMINAL; DO_NOT_SWITCH_MODEL_OR_PROVIDER",
                "silent_model_substitution": "FORBIDDEN",
            },
            cause=None,
            residual="The C3 fallback set is the closed empty list even though released code exposes multiple model/client surfaces.",
            next_discriminator="Retain the empty fallback set when the primary diagnosis and coding-agent identities are selected.",
        ),
        "model_provider.primary": entry(
            "UNBOUND",
            binding={
                "released_source_defaults_not_adopted": {
                    "diagnose_model": "o1-2024-12-17",
                    "coding_agent_model": "claude-3-5-sonnet-20241022",
                }
            },
            cause="No exact model/provider endpoint, service revision, credentials principal, sampling/configuration or capability mapping is selected for diagnosis and self-edit calls.",
            residual="Released model-name strings are historical defaults, not a reproducible service binding.",
            next_discriminator="Freeze one exact primary identity per role, effective request config, endpoint/TLS identity and credential principal with no fallback.",
        ),
        "resources.calls_tokens_usd": entry(
            "UNBOUND",
            binding=None,
            cause="The released DGM has generation/worker/evaluation counts but no provider-reconciled aggregate hard stop for calls, input/output tokens or USD across diagnosis, coding-agent and evaluation activity.",
            residual="C3 cost and service exposure are not bounded reproducibly.",
            next_discriminator="After primary binding, enforce pre-call aggregate counters with exact overshoot semantics and reconcile all roles to provider receipts.",
        ),
        "resources.retry_network": entry(
            "UNBOUND",
            binding={
                "frozen_policy": {
                    "fallbacks": [],
                    "network_default": "DENY_EXCEPT_EXACT_BOUND_ENDPOINTS",
                }
            },
            cause="Provider endpoints, DNS/TLS identities, retry/backoff rules, Git/task fetches and Docker egress are unbound; released execution assumes ambient network and credentials.",
            residual="C3 egress, retry multiplicity and endpoint identity are not reproducible.",
            next_discriminator="Bind exact local/offline or remote endpoints and enforce deny-by-default egress across the DGM process, Docker daemon and every task container.",
        ),
        "resources.wallclock": entry(
            "BOUND",
            binding={
                "enforcer": "p5_c3_fail_closed_runner.py",
                "enforcer_sha256": runner_hash,
                "whole_c3_run_seconds": 21600,
                "per_case_seconds": 21600,
                "termination_grace_seconds": 120,
                "timeout_terminal": "TIMEOUT/exit 124",
            },
            cause=None,
            residual="A prospective outer process-group watchdog is byte-frozen. It does not prove termination of Docker descendants or repair the ineffective released future timeout.",
            next_discriminator="On the eventual disposable runtime, verify TERM/KILL propagation and independent destruction of containers, networks, volumes and daemon state.",
        ),
        "rights.container_and_generated_artifacts": entry(
            "UNBOUND",
            binding={
                "released_base_image": "python:3.10-slim",
                "released_base_image_digest": None,
            },
            cause="The mutable base image has no digest, no built-image SBOM/licence bundle exists, and no authority is captured for retaining or publishing model-generated code, patches, logs, transcripts, predictions, images or archive state.",
            residual="C3 is not licensed for native execution or artifact redistribution.",
            next_discriminator="Pin the base and derived image by digest, generate an SBOM/licence inventory, and obtain explicit generated-artifact retention/disclosure authority.",
        ),
        "rights.model_provider_and_services": entry(
            "UNBOUND",
            binding=None,
            cause="No provider is selected and no study-use, data-retention, regional-processing or publication terms are captured.",
            residual="C3 is not licensed for service-backed execution.",
            next_discriminator="Bind applicable service terms and data policy for every diagnosis, coding and evaluation model before credentials enter the runtime.",
        ),
        "rights.task_and_benchmark_content": entry(
            "UNBOUND",
            binding={
                "documented_external_swe_bench_commit": "dc4c087c2b9e4cefebf2e3d201d27e36",
                "external_checkout_materialized_in_lane": False,
            },
            cause="The README names a separate SWE-bench checkout, while task data, project repositories, tests, reference outputs, patches and any P5-authored failure packet have separate licences and custody not closed by the DGM Apache-2.0 licence.",
            residual="C3 task/evaluation execution and retained outputs remain CANNOT_CHECK.",
            next_discriminator="Freeze exact benchmark/task/project/container identities and complete a layer-by-layer rights inventory without importing released or protected outcomes into candidate custody.",
        ),
        "runtime.compute": entry(
            "UNBOUND",
            binding={
                "prospective": {
                    "gpus": 0,
                    "parallelism": 1,
                    "pids_limit": 2048,
                    "ram_gib": 16,
                    "vcpus": 8,
                }
            },
            cause="Prospective values are not enforced across the host process, Docker build/daemon, self-edit container, evaluation workers and task containers; released defaults permit parallel self-improvement workers.",
            residual="C3 is not licensed for a matched resource comparison.",
            next_discriminator="Enforce one VM/cgroup-wide cap and verify every process and container stays within it.",
        ),
        "runtime.container_or_environment": entry(
            "UNBOUND",
            binding={
                "source_archive_sha256": ARCHIVE_SHA,
                "released_dockerfile_sha256": "55616682db154e7597b92f3406fa7bb240d91986d2f76581ba3f4a60941b6f7e",
                "released_base_image": "python:3.10-slim",
                "base_image_digest": None,
                "local_probe": "Darwin arm64; Docker 29.3.0 client; daemon unreachable",
            },
            cause="No content-addressed Linux base/derived image, host Docker daemon, task images, Python ABI, OS packages or runtime SBOM is materialized. The local Docker daemon is unreachable.",
            residual="Only source bytes are frozen; native DGM execution is CANNOT_CHECK.",
            next_discriminator="Build the filtered source on a rights-cleared disposable Linux executor from digest-pinned base/task images and record all environment and SBOM digests.",
        ),
        "runtime.dependency_lock": entry(
            "UNBOUND",
            binding={
                "requirements": {
                    "path": "requirements.txt",
                    "sha256": "4ef674aecea8fce1c1be6d663aab988dae61d5951bd296ab6250f5e2bc315aaf",
                    "declaration_entries": 19,
                    "exact_pins": 0,
                },
                "requirements_dev": {
                    "path": "requirements_dev.txt",
                    "sha256": "58cfa97e21b89fad87009c8b2e41888558a1b5e09e11951519869822ccfe324f",
                    "declaration_entries": 4,
                    "exact_pins": 0,
                },
                "lockfile_paths_in_authoritative_root": 0,
            },
            cause="The authoritative release contains 23 dependency declarations and zero exact pins or resolved lockfile. Hashing unpinned requirement text is not a dependency-resolution binding.",
            residual="V4 intentionally remains 6/21 BOUND rather than claiming a seventh binding from mutable declarations.",
            next_discriminator="Resolve on the selected Linux/Python platform, freeze every artifact hash and transitive dependency, then separately verify licences and build reproducibility.",
        ),
        "runtime.task_environment": entry(
            "CANNOT_CHECK",
            binding={
                "documented_external_swe_bench_commit": "dc4c087c2b9e4cefebf2e3d201d27e36",
                "argparse_choice_defect": "score_child_prop and best are not explicit accepted choices due adjacent string literal concatenation",
                "outcome_paths_excluded_from_candidate_seed": [
                    "initial/",
                    "initial_polyglot/",
                    "swe_bench/ref_agent_results/",
                ],
            },
            cause="No exact P5 task/harness subset, prepared SWE-bench environment, filtered source seed, project images or policy for the pinned argparse defect is bound. The external SWE-bench commit alone does not bind tasks, data or containers.",
            residual="Native task/evaluation semantics and reproducibility remain CANNOT_CHECK.",
            next_discriminator="Freeze an exact task/environment manifest and either preserve the defect as native C3 or preregister a source-repaired successor identity; do not silently patch the arm.",
        ),
    }

    bound = [path for path in required if fields[path]["state"] == "BOUND"]
    blocking = [path for path in required if fields[path]["state"] != "BOUND"]
    registry = {
        "schema_version": "orion.p5.c3.field-registry.v4",
        "registry_id": "P5.C3.DGM.FIELD.REGISTRY.V4",
        "arm_id": ARM_ID,
        "frozen_at_utc": FROZEN_AT,
        "required_field_paths": required,
        "fields": fields,
        "bound_fields": bound,
        "bound_field_count": len(bound),
        "blocking_fields": blocking,
        "blocking_field_count": len(blocking),
        "execution_ready": False,
        "panel_confirmatory_ready_arms": 0,
        "bound_execution_envelope": {
            "fallbacks": [],
            "wallclock_seconds": {
                "per_case": 21600,
                "whole_c3_run": 21600,
                "termination_grace": 120,
            },
            "runtime_launcher": None,
        },
        "terminal": "C3_PARTIAL_BINDING__FIFTEEN_REQUIRED_FIELDS_NOT_BOUND__EXECUTION_REFUSED",
    }
    write_json("P5_C3_V4_FIELD_REGISTRY.json", registry)

    source_files = [
        ("LICENSE", "84b7504ce8dda1f37f592cdf67ad21371864583720d79ea289b0b0c75bfcdb17"),
        ("README.md", "9760f30330e519946592ae88178f579dd717c3e55d3d461322e5facfa09c6bd4"),
        ("DGM_outer.py", "239bc76f0e1b78210b8f7b3757b1082f6ca07db3537d6af50a45bf97709795ed"),
        ("self_improve_step.py", "6f2ec364b11e7f6d35391ea66896fa2394cbca3bc59d68cf7352c2a77aa8cca7"),
        ("coding_agent.py", "0fe9f4806fee18a481c9298a6d1ab6d754bb81666031598d86a9da2b632a5829"),
        ("llm.py", "ca6ac22d7f128180de398cec48b9f5cc1f1f49f3bf1a8e935025588d8b09570d"),
        ("llm_withtools.py", "b6fa4ee18ad8b42767f7cad68bf8ed7f7937dcfaf32b85757182979bdb895836"),
        ("utils/docker_utils.py", "4f72795d21358299a2b3053e7798837a110a4a795fab8f064cdeaab759568552"),
        ("utils/git_utils.py", "b6d1a051ca7e663f221d5bc1c9154f33f380a80371ded6c8abfdbf23102004ea"),
        ("utils/evo_utils.py", "0eb779270390f39aa0c4ff045ec9b6c3049736c6a008ae3d2e7a2df7ef253570"),
        ("swe_bench/harness.py", "2445479db7c7b0fa607dde5153dde2a85ce1fb3dd810bb088c81ab2f265c617a"),
        ("swe_bench/report.py", "a86e6fa6f8826414c55f0742f115ab05bb35a9d733bc447fa2dcf3138a9d33d4"),
        ("Dockerfile", "55616682db154e7597b92f3406fa7bb240d91986d2f76581ba3f4a60941b6f7e"),
        ("requirements.txt", "4ef674aecea8fce1c1be6d663aab988dae61d5951bd296ab6250f5e2bc315aaf"),
        ("requirements_dev.txt", "58cfa97e21b89fad87009c8b2e41888558a1b5e09e11951519869822ccfe324f"),
    ]
    source_rights = {
        "schema_version": "orion.p5.c3.source-rights-manifest.v4",
        "authority": "PUBLIC_SOURCE_IDENTITY_RIGHTS_AND_METADATA_ONLY_OUTCOME_CENSUS__NOT_LEGAL_ADVICE",
        "frozen_at_utc": FROZEN_AT,
        "source": {
            "repository": "https://github.com/jennyzzt/dgm",
            "commit_sha": COMMIT,
            "tree_sha": TREE,
            "commit_time": "2025-08-13T11:40:14+01:00",
            "archive_format": ARCHIVE_FORMAT,
            "archive_sha256": ARCHIVE_SHA,
            "archive_bytes_retained_in_lane": False,
        },
        "hashed_authoritative_files": [
            {"path": path, "sha256": digest} for path, digest in source_files
        ],
        "authoritative_tree_metadata_census": {
            "method": "git ls-tree -r -l HEAD metadata only",
            "tracked_files": 1650,
            "tracked_blob_bytes": 53195497,
            "payload_contents_opened": False,
            "outcome_or_initial_prefixes": [
                {"prefix": "initial/", "files": 475, "blob_bytes": 27591301},
                {"prefix": "initial_polyglot/", "files": 1118, "blob_bytes": 22099022},
                {"prefix": "swe_bench/ref_agent_results/", "files": 2, "blob_bytes": 17010},
            ],
            "outcome_or_initial_union": {"files": 1595, "blob_bytes": 49707333},
            "non_outcome_union": {"files": 55, "blob_bytes": 3488164},
            "reference_outcome_entries": [
                {
                    "path": "swe_bench/ref_agent_results/claude_tools.json",
                    "git_blob": "97cc25611b6159e8127d9898f0e9b6e978704b1d",
                    "blob_bytes": 8356,
                },
                {
                    "path": "swe_bench/ref_agent_results/open_hands.json",
                    "git_blob": "72e071a4416f98e3419287cb6203c95de17db365",
                    "blob_bytes": 8654,
                },
            ],
            "candidate_seed_policy": "exclude all three prefixes before any candidate access",
        },
        "dependency_declaration_audit": {
            "requirements_txt_entries": 19,
            "requirements_txt_exact_pins": 0,
            "requirements_dev_txt_entries": 4,
            "requirements_dev_txt_exact_pins": 0,
            "authoritative_lockfiles": 0,
            "terminal": "DECLARATIONS_HASHED__DEPENDENCY_RESOLUTION_UNBOUND",
        },
        "licence_layers": [
            {
                "scope": "DGM root source",
                "spdx": "Apache-2.0",
                "license_sha256": "84b7504ce8dda1f37f592cdf67ad21371864583720d79ea289b0b0c75bfcdb17",
            },
            {
                "scope": "documented separate SWE-bench checkout and task/project artifacts",
                "status": "SEPARATE_RIGHTS_NOT_CLOSED",
                "documented_commit": "dc4c087c2b9e4cefebf2e3d201d27e36",
            },
            {
                "scope": "container, transitive dependencies, model services, generated artifacts and protected panel",
                "status": "NOT_CLOSED",
            },
        ],
        "rights_closed": ["public source inspection", "DGM Apache-2.0 source layer"],
        "rights_not_closed": [
            "SWE-bench/task/project/test/reference-output bytes",
            "P5 candidate-visible failure packet",
            "transitive dependency licences and SBOM",
            "base/derived/task container distribution",
            "model and coding-agent services",
            "generated code, patches, logs, transcripts, predictions and archive state",
            "protected scorer and panel",
        ],
    }
    write_json("P5_C3_V4_SOURCE_RIGHTS_MANIFEST.json", source_rights)

    write_json(
        "P5_C3_V4_PATCH_CAPTURE_SCHEMA.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "orion.p5.c3.dgm-patch-capture.v4",
            "title": "P5 C3 DGM outcome-blind pre-evaluation patch capture",
            "type": "object",
            "required": [
                "schema_version",
                "arm_id",
                "run_id",
                "parent_commit",
                "native_code",
                "stage",
                "exit_code",
                "patch_sha256",
                "patch_bytes",
            ],
            "properties": {
                "schema_version": {"const": "orion.p5.c3.dgm-patch-capture.v4"},
                "arm_id": {"const": ARM_ID},
                "run_id": {"type": "string", "minLength": 1},
                "parent_commit": {"type": "string", "minLength": 1},
                "native_code": {
                    "enum": [
                        "INITIALIZED",
                        "DIAGNOSIS_READY",
                        "SELF_EDIT_STARTED",
                        "PATCH_CAPTURED",
                        "NO_ENTRY",
                        "NO_PROBLEM_STATEMENT",
                        "MISSING_PATCH",
                        "EMPTY_PATCH",
                        "ARGPARSE_INTEGRITY_ERROR",
                        "PROVIDER_ERROR",
                        "RUNTIME_ERROR",
                        "TIMEOUT",
                    ]
                },
                "stage": {"enum": ["initialize", "diagnose", "self_edit", "capture_patch"]},
                "exit_code": {"type": ["integer", "null"], "minimum": 0, "maximum": 255},
                "patch_sha256": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    ]
                },
                "patch_bytes": {"type": "integer", "minimum": 0},
            },
            "additionalProperties": False,
        },
    )

    write_json(
        "P5_C3_V4_NATIVE_TERMINAL_RULES.json",
        {
            "schema_version": "orion.p5.c3.native-terminal-rules.v4",
            "source_boundary": "adapter-authored pre-evaluation patch capture; not a released DGM result schema",
            "mapping": {
                "PATCH_CAPTURED + capture_patch + exit 0 + positive patch bytes + SHA-256": "COMPLETE_SUCCESS",
                "INITIALIZED | DIAGNOSIS_READY | SELF_EDIT_STARTED | NO_PROBLEM_STATEMENT": "PARTIAL",
                "NO_ENTRY | MISSING_PATCH | EMPTY_PATCH": "EMPTY",
                "TIMEOUT": "TIMEOUT",
                "ARGPARSE_INTEGRITY_ERROR | PROVIDER_ERROR | RUNTIME_ERROR": "ERROR",
                "incoherent patch capture": "INVALID",
            },
            "retention": [
                "exact native_code and stage",
                "exact exit code",
                "hashes rather than raw run/parent identifiers",
                "patch SHA-256 and byte count but not patch payload",
            ],
            "adapter_output": "always UNRESOLVED; zero raw native singleton licences",
            "outcome_policy": "no benchmark, archive-admission, gold, protected, scorer, held-out or comparator field may be parsed or used for mapping",
            "closed_input_policy": "unknown root keys and prohibited exact/prefix key families are refused",
        },
    )

    write_json(
        "P5_C3_V4_WRITE_SURFACE_SCHEMA.json",
        {
            "schema_version": "orion.p5.c3.write-surface.v4",
            "arm_id": ARM_ID,
            "field_state": "CANNOT_CHECK",
            "released_source_gap": "DGM requires mutable Git/container/task state and a host Docker daemon; released Dockerfile copies the entire repository including outcome paths",
            "required_isolation": {
                "source_seed": "read-only filtered seed excluding initial/, initial_polyglot/ and swe_bench/ref_agent_results/; copied only inside a disposable executor",
                "allowed_mutation_roots": [
                    "ephemeral filtered DGM candidate tree",
                    "ephemeral output_dgm attempt directory",
                    "ephemeral task repositories and task containers",
                    "dedicated ephemeral Docker data root",
                    "sole receipt output directory",
                ],
                "forbidden_roots": [
                    "shared or pinned upstream checkout",
                    "initial/, initial_polyglot/ and swe_bench/ref_agent_results/ payloads",
                    "host Docker daemon and persistent images/volumes",
                    "host home, SSH, cloud config, keychains and unrelated credentials",
                    "protected panel and external scorer",
                    "other comparator arms",
                    "network endpoints outside the final allowlist",
                ],
                "audit": "complete before/after digest for every allowed root plus proof that no forbidden mount, path or endpoint was reachable",
                "reset": "destroy VM, Docker data root, networks, images, containers, mutable source and task copies after every attempt",
            },
        },
    )

    write_json(
        "P5_C3_V4_CUSTODY_HANDOFF_SCHEMA.json",
        {
            "schema_version": "orion.p5.c3.custody-handoff.v4",
            "current_state": "CANNOT_CHECK",
            "local_self_attestation_allowed": False,
            "required_attestations": [
                "public-development archive and protocol frozen before protected panel identity",
                "candidate receives only byte-frozen visible packet, filtered source and approved public-development services",
                "one frozen successor commit/image accepted before protected scoring",
                "candidate and adaptation custody close before protected transfer",
                "independent scorer identity and code digest",
                "fresh protected panel frozen after protocol lock",
                "one scoring event with append-only receipt",
                "no protected score, outcome or diagnostic returns to candidate or adaptation custody",
            ],
        },
    )

    resources = {
        "schema_version": "orion.p5.c3.resource-registry.v4",
        "arm_id": ARM_ID,
        "frozen_at_utc": FROZEN_AT,
        "bound": {
            "fallbacks": [],
            "wallclock_seconds": {
                "per_case": 21600,
                "whole_c3_run": 21600,
                "termination_grace": 120,
            },
        },
        "proposed_but_unbound": {
            "compute": {"gpus": 0, "parallelism": 1, "pids_limit": 2048, "ram_gib": 16, "vcpus": 8},
            "calls_tokens_usd": None,
            "network": "deny except exact bound endpoints",
            "dependency_resolution": None,
        },
        "source_defaults_not_adopted_as_matched_p5_values": {
            "max_generation": 80,
            "selfimprove_size": 2,
            "selfimprove_workers": 2,
            "num_swe_evals": 1,
            "coding_agent_timeout_seconds": 1800,
            "swe_harness_timeout_seconds": 32400,
            "future_result_timeout_seconds": 5400,
            "future_result_timeout_effective": False,
        },
        "dependency_declarations_not_a_lock": {
            "requirements_entries": 19,
            "requirements_exact_pins": 0,
            "requirements_dev_entries": 4,
            "requirements_dev_exact_pins": 0,
        },
        "blocking_observations": [
            "No aggregate calls/tokens/USD hard stop is released.",
            "The future.result timeout is reached only after as_completed and does not bound a running future.",
            "The Docker base tag and all Python dependency declarations are mutable.",
            "No VM/cgroup-wide compute or final endpoint allowlist is enforced.",
        ],
    }
    write_json("P5_C3_V4_RESOURCE_REGISTRY.json", resources)

    protocol = {
        "schema_version": "orion.p5.c3.dgm-execution-binding-protocol.v4",
        "protocol_id": "P5.C3.DGM.EXECUTION.BINDING.V4",
        "arm_id": ARM_ID,
        "authority": "PUBLIC_SOURCE_IDENTITY_AND_OUTCOME_BLIND_PREFLIGHT_ONLY",
        "frozen_at_utc": FROZEN_AT,
        "source_identity": {
            "repository": "https://github.com/jennyzzt/dgm",
            "commit_sha": COMMIT,
            "tree_sha": TREE,
            "archive_format": ARCHIVE_FORMAT,
            "archive_sha256": ARCHIVE_SHA,
        },
        "frozen_components": {
            "native_parser": {"path": "p5_c3_native_parser.py", "sha256": parser_hash},
            "native_output_schema": {
                "path": "P5_C3_V4_NATIVE_OUTPUT_SCHEMA.json",
                "sha256": output_schema_hash,
            },
            "fail_closed_gate": {"path": "p5_c3_fail_closed_runner.py", "sha256": runner_hash},
            "fallbacks": [],
            "wallclock_seconds": {
                "per_case": 21600,
                "whole_c3_run": 21600,
                "termination_grace": 120,
            },
        },
        "execution_order": [
            "independent owners bind all 21 fields without protected outcome access",
            "construct a filtered source seed excluding all frozen outcome/initial prefixes",
            "validator requires 21/21 BOUND and a content-addressed disposable runtime launcher",
            "candidate receives one rights-cleared failure packet plus its committed input-native certificate",
            "DGM performs at most one pre-evaluation diagnosis/self-edit/patch-capture attempt under the outer watchdog",
            "no benchmark evaluation, archive score, admission, gold/protected scorer or sibling-arm state enters candidate custody",
            "native parser retains the exact patch-capture terminal and emits UNRESOLVED",
            "V3 certificate/action/fibre validation runs separately outside candidate custody",
            "one frozen successor may enter independent protected custody once only after 6/6 panel readiness",
        ],
        "source_defect_policy": {
            "native_c3": "preserve pinned defects exactly",
            "repaired_code": "must receive a new successor identity and cannot be silently relabeled C3",
        },
        "nonclaims": [
            "No DGM, model, task, benchmark, Docker container, archive update, protected scorer or comparator was executed.",
            "Parser conformance and fail-closed preflight are not DGM success or scientific performance.",
            "A native patch is not a P5 responsibility class and always maps to UNRESOLVED.",
            "No preservation, transfer, harm, performance or superiority inference is available.",
        ],
        "predecessor": {
            "v3_blocking_fields": 18,
            "v3_bound_identity_fields": 3,
            "v3_adapter_refinement_sha256s": "50d1ff72f63093216761c4b47d3ced6de82915967578f33f3296bf41e4f73c4a",
        },
    }
    write_json("P5_C3_V4_EXECUTION_BINDING_PROTOCOL.json", protocol)

    negatives = [
        {
            "id": "P5.C3.V4.ARGPARSE.CHOICE.CONCATENATION",
            "cause": "DGM_outer.py lines 227-228 omit a comma between 'score_child_prop' and 'best', so Python forms the single choice 'score_child_propbest'.",
            "positive_progress": "The exact source defect and affected option values are frozen; the unvalidated default caveat is separated from explicit CLI acceptance.",
            "residual": "Explicit --choose_selfimproves_method score_child_prop and best are rejected, while omitting the option may still pass the default into program logic. Native task semantics are defective.",
            "next_discriminator": "Preserve this behaviour for native C3; if repaired, freeze a new commit as a separately named successor and test all intended choices without benchmark outcomes.",
        },
        {
            "id": "P5.C3.V4.INEFFECTIVE.FUTURE.TIMEOUT",
            "cause": "DGM_outer.py lines 302-305 call future.result(timeout=5400) only after as_completed yields an already-completed future.",
            "positive_progress": "A separate 21,600-second process-group watchdog plus 120-second TERM/KILL grace is byte-frozen.",
            "residual": "The released timeout cannot bound a still-running future; the outer watchdog does not itself prove Docker-descendant termination or cleanup.",
            "next_discriminator": "Verify VM-wide timeout and destructive cleanup on a disposable executor; a source-level timeout repair requires a distinct successor identity.",
        },
        {
            "id": "P5.C3.V4.MUTABLE.ENVIRONMENT",
            "cause": "Dockerfile uses python:3.10-slim without a digest; requirements.txt has 19 entries and requirements_dev.txt 4, with zero exact pins and no authoritative lockfile.",
            "positive_progress": "All declaration, Dockerfile and source hashes are retained and the dependency-lock field is explicitly adjudicated UNBOUND.",
            "residual": "Rebuilds may resolve different OS image and Python dependency bytes. V4 is honestly 6/21 BOUND, not 7/21.",
            "next_discriminator": "Resolve and hash every transitive dependency for the selected Linux/Python platform, pin base/task/derived image digests, and inventory licences/SBOM.",
        },
        {
            "id": "P5.C3.V4.UNTRUSTED.GENERATED.CODE",
            "cause": "README line 88 warns that model-generated code can behave destructively; released execution grants mutable Git and Docker-backed task surfaces.",
            "positive_progress": "A minimal allowed/forbidden write-surface and disposable reset theorem is frozen; execution remains fail closed.",
            "residual": "No native isolation proof, rootless daemon, egress allowlist, complete mutation digest or cleanup receipt exists.",
            "next_discriminator": "Execute only in a dedicated disposable VM with a private rootless daemon, filtered mounts, denied ambient credentials/egress and full before/after mutation evidence.",
        },
        {
            "id": "P5.C3.V4.OUTCOME.PAYLOAD.CUSTODY",
            "cause": "The authoritative tree tracks 1,595 files (49,707,333 bytes) under initial/, initial_polyglot/ and swe_bench/ref_agent_results/; Dockerfile COPY . would place them in the container.",
            "positive_progress": "A metadata-only census is frozen without opening payload contents, and all three prefixes are forbidden from the candidate seed.",
            "residual": "No filtered, content-addressed source seed or lawful public-development archive/case packet has been produced.",
            "next_discriminator": "Build a filtered source seed by path allowlist, prove excluded blob absence, and freeze a separate pre-protected public-development archive before candidate access.",
        },
        {
            "id": "P5.C3.V4.NATIVE.PARSER.BOUNDARY",
            "cause": "Released DGM exposes archive/evaluation metadata rather than a stable pre-evaluation result schema; V3 had only a generic synthetic adapter.",
            "positive_progress": "V4 freezes an adapter-authored patch-capture schema, rejects prohibited exact/prefix families and unknown keys, preserves native status, and maps even valid PATCH_CAPTURED to UNRESOLVED.",
            "residual": "Parser conformance is not DGM execution, and a patch remains a mixed scientific fibre until the separate certificate/action proof is valid.",
            "next_discriminator": "After all 21 fields bind, capture one lawful patch terminal and apply the byte-frozen V3 certificate/action/fibre operation outside candidate custody.",
        },
        {
            "id": "P5.C3.V4.MODEL.RESOURCE.BINDING",
            "cause": "Historical model-name strings, ambient API keys, provider endpoints, retries and aggregate calls/tokens/USD caps are not reproducibly bound.",
            "positive_progress": "Fallbacks are frozen empty and network defaults to deny except exact future endpoints.",
            "residual": "Primary service identity, effective configuration, cost accounting and egress remain UNBOUND.",
            "next_discriminator": "Bind exact diagnosis and coding-agent service identities, no-fallback configs, pre-call aggregate counters, provider receipts and a final egress allowlist.",
        },
        {
            "id": "P5.C3.V4.TASK.RIGHTS.RUNTIME",
            "cause": "The README pins a separate SWE-bench source commit, but its tasks, data, project repositories, tests, images and reference outputs have distinct identity and rights layers.",
            "positive_progress": "The documented SWE-bench commit is retained as a discriminator rather than treated as a complete task/runtime binding.",
            "residual": "Exact task environment, task content rights, container images and generated-artifact authority remain CANNOT_CHECK or UNBOUND.",
            "next_discriminator": "Freeze an exact rights-cleared task subset and all project/container identities, then build a reproducible environment without importing protected/reference outcomes.",
        },
        {
            "id": "P5.C3.V4.CUSTODY.PANEL",
            "cause": "Independent scorer identity, one-shot no-feedback enforcement and fresh protected-panel custody cannot be established locally.",
            "positive_progress": "The required attestations and no-feedback boundary are byte-specified and local self-attestation is prohibited.",
            "residual": "Six-arm confirmatory readiness remains 0/6; H1-H4, transfer, harm, performance and superiority are CANNOT_CHECK.",
            "next_discriminator": "An independent custodian signs all three content-addressed attestations only after every arm and the public-development protocol are frozen.",
        },
    ]
    write_json(
        "P5_C3_V4_NEGATIVE_LEDGER.json",
        {
            "schema_version": "orion.p5.c3.recursive-negative-ledger.v4",
            "arm_id": ARM_ID,
            "frozen_at_utc": FROZEN_AT,
            "entries": negatives,
        },
    )
    md = [
        "# P5 C3 DGM V4 recursive negative-result ledger",
        "",
        "Every row is an active research problem. `positive_progress` records only the boundary or mechanism actually repaired; no negative is rewritten as empirical success.",
        "",
        "| ID | Cause | Positive progress | Residual | Next discriminator |",
        "|---|---|---|---|---|",
    ]
    for item in negatives:
        md.append(
            "| `{id}` | {cause} | {positive_progress} | {residual} | {next_discriminator} |".format(
                **{key: str(value).replace("|", "\\|").replace("\n", " ") for key, value in item.items()}
            )
        )
    (HERE / "P5_C3_V4_NEGATIVE_LEDGER.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    result = {
        "schema_version": "orion.p5.c3.dgm-execution-binding-result.v4",
        "protocol_id": "P5.C3.DGM.EXECUTION.BINDING.V4",
        "arm_id": ARM_ID,
        "authority": "PUBLIC_SOURCE_IDENTITY_AND_OUTCOME_BLIND_PREFLIGHT_ONLY",
        "terminal": TERMINAL,
        "execution": {
            "c3_executed": False,
            "c3_execution_ready": False,
            "native_dgm_smoke": "CANNOT_CHECK",
            "panel_confirmatory_ready_arms": 0,
            "panel_required_arms": 6,
        },
        "v4_repairs": {
            "v3_bound_fields": 3,
            "v3_blocking_fields": 18,
            "v4_bound_fields": len(bound),
            "v4_blocking_fields": len(blocking),
            "v3_to_v4_blocker_delta": len(blocking) - 18,
            "newly_bound_v3_fields": [
                "adapter.native_parser_binding",
                "model_provider.fallbacks",
                "resources.wallclock",
            ],
            "retained_bound_identity_fields": [
                "identity.native_entrypoint_bytes",
                "identity.source_license_bytes",
                "identity.source_repository_commit",
            ],
            "dependency_lock_adjudication": "UNBOUND__23_DECLARATIONS__0_EXACT_PINS__NO_LOCKFILE",
        },
        "material_discoveries": {
            "argparse_choice_concatenation": True,
            "future_timeout_ineffective": True,
            "mutable_base_image": True,
            "dependency_exact_pins": 0,
            "outcome_initial_tracked_files": 1595,
            "outcome_initial_blob_bytes": 49707333,
            "payload_contents_opened": False,
        },
        "preserved_boundaries": {
            "raw_native_singleton_licences": 0,
            "v3_synthetic_cases": 231,
            "v3_supported_singleton_case_records": 40,
            "v3_unresolved_case_records": 191,
            "conditional_support_set": [
                "WITHIN_CLASS_MODEL_REPAIR",
                "MODEL_CLASS_EXPANSION",
                "REPRESENTATION_REGIME_REPAIR",
                "EXECUTION_REPAIR",
            ],
            "raw_patch_disposition": "UNRESOLVED",
        },
        "preserved_claims": {
            "H1": "CANNOT_CHECK",
            "H2": "CANNOT_CHECK",
            "H3": "CANNOT_CHECK",
            "H4": "CANNOT_CHECK",
            "preservation": "CANNOT_CHECK",
            "fresh_transfer": "CANNOT_CHECK",
            "harm": "CANNOT_CHECK",
            "performance": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
            "top_tier_publication_readiness": "NOT_ESTABLISHED",
        },
        "next_discriminator": "Resolve and hash dependencies, build a filtered content-addressed DGM seed and disposable rootless-Docker runtime, bind one rights-cleared P5 case plus model/resource/rights/custody fields, then require 6/6 matched panel readiness before any protected score.",
    }
    write_json("P5_C3_V4_RESULT.json", result)

    # Outcome-free synthetic parser and fail-closed preflight smoke. Fixtures are
    # created only in a temporary directory and are removed automatically.
    valid_capture = {
        "schema_version": "orion.p5.c3.dgm-patch-capture.v4",
        "arm_id": ARM_ID,
        "run_id": "synthetic-outcome-free-run",
        "parent_commit": "initial",
        "native_code": "PATCH_CAPTURED",
        "stage": "capture_patch",
        "exit_code": 0,
        "patch_sha256": "a" * 64,
        "patch_bytes": 321,
    }
    prohibited_capture = dict(valid_capture)
    prohibited_capture["gold_future"] = "synthetic-prohibited-key"
    with tempfile.TemporaryDirectory(prefix="p5-c3-v4-smoke-") as temp:
        temp_path = Path(temp)
        valid_path = temp_path / "valid.json"
        prohibited_path = temp_path / "prohibited.json"
        valid_raw = (json.dumps(valid_capture, sort_keys=True, separators=(",", ":")) + "\n").encode()
        prohibited_raw = (json.dumps(prohibited_capture, sort_keys=True, separators=(",", ":")) + "\n").encode()
        valid_path.write_bytes(valid_raw)
        prohibited_path.write_bytes(prohibited_raw)
        valid_proc = subprocess.run(
            [sys.executable, str(HERE / "p5_c3_native_parser.py"), str(valid_path)],
            capture_output=True,
            check=False,
        )
        prohibited_proc = subprocess.run(
            [sys.executable, str(HERE / "p5_c3_native_parser.py"), str(prohibited_path)],
            capture_output=True,
            check=False,
        )
    valid_output = json.loads(valid_proc.stdout)
    preflight_proc = subprocess.run(
        [
            sys.executable,
            str(HERE / "p5_c3_fail_closed_runner.py"),
            "--registry",
            str(HERE / "P5_C3_V4_FIELD_REGISTRY.json"),
            "--preflight",
        ],
        capture_output=True,
        check=False,
    )
    preflight_value = json.loads(preflight_proc.stdout)
    smoke = {
        "schema_version": "orion.p5.c3.outcome-blind-smoke-receipt.v4",
        "authority": "SYNTHETIC_OUTCOME_FREE_ADAPTER_AND_GATE_SMOKE_ONLY",
        "frozen_at_utc": FROZEN_AT,
        "source": {"commit_sha": COMMIT, "dgm_executed": False},
        "parser_conformance": {
            "valid_fixture_retained": False,
            "valid_input_bytes": len(valid_raw),
            "valid_input_sha256": sha_bytes(valid_raw),
            "exit_code": valid_proc.returncode,
            "stdout_bytes": len(valid_proc.stdout),
            "stdout_sha256": sha_bytes(valid_proc.stdout),
            "stderr_bytes": len(valid_proc.stderr),
            "native_status": valid_output["native_terminal"]["status"],
            "native_code": valid_output["native_terminal"]["native_code"],
            "adapter_output": valid_output["adapter_disposition"]["output"],
            "raw_native_singleton_licensed": valid_output["adapter_disposition"]["raw_native_singleton_licensed"],
            "prohibited_fixture_retained": False,
            "prohibited_input_sha256": sha_bytes(prohibited_raw),
            "prohibited_key_family": "gold_*",
            "prohibited_exit_code": prohibited_proc.returncode,
            "prohibited_stderr_sha256": sha_bytes(prohibited_proc.stderr),
        },
        "fail_closed_preflight": {
            "exit_code": preflight_proc.returncode,
            "execution_ready": preflight_value["execution_ready"],
            "blocking_field_count": preflight_value["blocking_field_count"],
            "stdout_sha256": sha_bytes(preflight_proc.stdout),
            "stderr_bytes": len(preflight_proc.stderr),
        },
        "full_native_smoke": {
            "state": "CANNOT_CHECK",
            "causes": [
                "Docker daemon unreachable",
                "base image and dependencies mutable/unbound",
                "primary models, endpoints and credentials unbound",
                "no substantive rights-cleared P5 case or task environment",
                "write isolation and custody unbound",
            ],
            "next_discriminator": "Execute only after all 21 fields bind on a disposable rights-cleared Linux runtime; no native DGM smoke is licensed in this lane.",
        },
        "raw_or_large_payloads_retained": False,
    }
    write_json("P5_C3_V4_SMOKE_RECEIPT.json", smoke)

    report = f"""# P5 C3 Darwin Gödel Machine execution-binding V4

## Terminal

`{TERMINAL}`

This is an outcome-blind source/runtime preflight repair, not a comparator
result. No DGM, model, task, benchmark, Docker container, archive update,
protected scorer, gold value, performance table, or protected datum was run or
opened. The only executions were a synthetic adapter fixture, a synthetic
prohibited-key refusal, and the fail-closed registry preflight.

## Exact readiness delta

V3 retained three exact source-identity fields and blocked 18/21 C3 fields.
V4 binds three more: the closed native patch-capture parser, an empty fallback
set, and a 21,600-second outer process-group watchdog. C3 is therefore
**6/21 BOUND** and **15/21 blocking** (delta: **-3 blockers**). Six-arm
confirmatory readiness remains **0/6**.

The anticipated 7/21 count is intentionally not forced. The authoritative
`requirements.txt` and `requirements_dev.txt` contain 19 + 4 declarations,
**zero exact pins**, and no resolved lockfile. Hashing declaration text does not
bind dependency resolution, so `runtime.dependency_lock` remains `UNBOUND`.

| Newly bound field | Evidence |
|---|---|
| `adapter.native_parser_binding` | Hashed closed patch-capture parser; exact/prefix protected families and unknown keys refused; native terminal retained; output always `UNRESOLVED` |
| `model_provider.fallbacks` | Closed empty list; silent model/provider substitution forbidden |
| `resources.wallclock` | Process-group watchdog: 21,600 s plus 120 s TERM/KILL grace |

## Exact source and outcome-blind custody boundary

The audited source is `https://github.com/jennyzzt/dgm` commit `{COMMIT}`, tree
`{TREE}`, uncompressed `git archive --format=tar {COMMIT}` SHA-256
`{ARCHIVE_SHA}`, and Apache-2.0 licence SHA-256
`84b7504ce8dda1f37f592cdf67ad21371864583720d79ea289b0b0c75bfcdb17`.

A metadata-only `git ls-tree -r -l HEAD` census found **1,650 tracked files**
and **53,195,497 blob bytes**. Three outcome/initial prefixes contain **1,595
files** and **49,707,333 bytes**: `initial/` (475; 27,591,301),
`initial_polyglot/` (1,118; 22,099,022), and
`swe_bench/ref_agent_results/` (2; 17,010). Their payload contents were not
opened. A future candidate seed must exclude these prefixes before candidate
access; upstream `Dockerfile` currently performs `COPY . .` and is insufficient.

## Four retained source defects

1. **Argparse concatenation:** `DGM_outer.py:227-228` lacks a comma between
   `score_child_prop` and `best`, creating `score_child_propbest`. Explicit
   intended values are not accepted, although omission can still inject the
   unvalidated default.
2. **Ineffective future timeout:** `DGM_outer.py:302-305` calls
   `future.result(timeout=5400)` only after `as_completed` yields the future, so
   it cannot bound a still-running attempt.
3. **Mutable environment:** `python:3.10-slim` is not digest-pinned and all 23
   Python dependency declarations are unpinned.
4. **Untrusted code:** README line 88 warns generated code may behave
   destructively; no native write/isolation proof is available.

These defects are not silently patched. Any repaired source must receive a new
successor identity. The native C3 identity preserves the audited bytes.

## Outcome-blind smoke

- Authored `PATCH_CAPTURED` fixture: parser exit **{valid_proc.returncode}**,
  native `COMPLETE_SUCCESS`, adapter `UNRESOLVED`, raw singleton licensed
  `false`; fixture removed.
- Injected synthetic `gold_*` key: parser refusal exit
  **{prohibited_proc.returncode}**; fixture removed.
- Registry preflight: exit **{preflight_proc.returncode}**, execution-ready
  `false`, **{preflight_value['blocking_field_count']}** blockers.
- Full native DGM smoke: **CANNOT_CHECK** because Docker, dependencies, models,
  task/case rights, isolation and custody are unbound.

Parser success is interface conformance only. A raw patch, including a valid
native patch capture, always maps to `UNRESOLVED` and cannot identify a P5
responsibility class.

## Fifteen remaining blockers

1. disposable native write/isolation boundary;
2. exact P5 candidate-visible case and public-development archive bytes;
3. primary diagnosis and coding-agent model/provider identities;
4. aggregate calls/tokens/USD hard stops;
5. retry/backoff and final network allowlist;
6. complete compute enforcement;
7. content-addressed base/derived/task containers and host environment;
8. exact resolved dependency lock;
9. exact task/runtime environment and argparse-defect policy;
10. task/benchmark/project/test/reference-output rights;
11. model/provider/service rights;
12. container/generated-artifact rights;
13. independent external protected scorer;
14. independent one-shot no-feedback barrier; and
15. protected-panel identity/freshness.

## Preserved scientific boundary

- V3 remains unchanged: 231 fictional cases, 40 supported singleton case
  records in 20 constant fibres, 191 `UNRESOLVED`, and zero raw native
  singleton licences.
- The only conditional support labels remain `WITHIN_CLASS_MODEL_REPAIR`,
  `MODEL_CLASS_EXPANSION`, `REPRESENTATION_REGIME_REPAIR`, and
  `EXECUTION_REPAIR`; each still requires an input-native certificate and
  complete single-front write-set proof.
- Six-arm performance readiness is 0/6.
- H1--H4, preservation, fresh transfer, harm, performance and superiority all
  remain `CANNOT_CHECK`; top-tier publication readiness is not established.

## Next discriminator

Resolve and hash every dependency; build a filtered content-addressed source
seed and disposable rootless-Docker Linux runtime; bind one rights-cleared P5
failure packet plus input-native certificate, exact models, aggregate resource
stops and all rights/custody attestations. C3 still cannot enter confirmatory
scoring until all six matched arms are ready.
"""
    (HERE / "SCIENTIFIC_REPORT_V4.md").write_text(report, encoding="utf-8")

    (HERE / "README.md").write_text(
        "# P5 DGM C3 execution-binding V4\n\n"
        "Self-contained outcome-blind preflight for the pinned Darwin Gödel Machine archive-based self-edit arm. "
        "Start with `SCIENTIFIC_REPORT_V4.md`, `P5_C3_V4_RESULT.json`, and `P5_C3_V4_FIELD_REGISTRY.json`. "
        "No DGM/model/benchmark/protected outcome was run or opened. The package binds 6/21 C3 fields, leaves 15 blocking, "
        "records why unpinned dependency declarations are not a lock, and keeps panel readiness at 0/6.\n",
        encoding="utf-8",
    )

    # Placeholder audit is validated structurally, then replaced by the finalizer
    # with the deterministic validator receipt.
    write_json(
        "AUDIT_RECEIPT_V4.json",
        {
            "schema_version": "orion.p5.c3.audit-receipt.v4",
            "arm_id": ARM_ID,
            "authority": "OUTCOME_BLIND_SOURCE_RUNTIME_PREFLIGHT_ONLY",
            "frozen_at_utc": FROZEN_AT,
            "terminal": TERMINAL,
            "execution": {
                "git_or_shared_checkout_edited": False,
                "pytest_run": False,
                "repository_ci_run": False,
                "native_dgm_or_model_run": False,
                "benchmark_or_protected_or_gold_opened": False,
                "raw_or_large_final_payload_retained": False,
            },
            "readiness": {
                "v3_bound_fields": 3,
                "v3_blocking_fields": 18,
                "v4_bound_fields": len(bound),
                "v4_blocking_fields": len(blocking),
                "blocker_delta": len(blocking) - 18,
                "panel_ready_arms": 0,
                "panel_required_arms": 6,
            },
            "source_receipt": {
                "repository": "https://github.com/jennyzzt/dgm",
                "commit_sha": COMMIT,
                "tree_sha": TREE,
                "archive_format": ARCHIVE_FORMAT,
                "archive_sha256": ARCHIVE_SHA,
                "outcome_payload_contents_opened": False,
                "outcome_initial_files_metadata_only": 1595,
                "outcome_initial_blob_bytes_metadata_only": 49707333,
            },
            "smoke_summary": {
                "parser_patch_captured_exit": valid_proc.returncode,
                "parser_patch_captured_native_status": valid_output["native_terminal"]["status"],
                "parser_adapter_output": valid_output["adapter_disposition"]["output"],
                "parser_prohibited_key_refusal_exit": prohibited_proc.returncode,
                "preflight_refusal_exit": preflight_proc.returncode,
                "native_dgm_smoke": "CANNOT_CHECK",
            },
            "validation": {"state": "PENDING_FINALIZER"},
        },
    )

    # The cleanup receipt is recomputed by the finalizer after validation.
    write_json(
        "CLEANUP_AUDIT_V4.json",
        {
            "schema_version": "orion.p5.c3.cleanup-audit.v4",
            "audited_at_utc": FROZEN_AT,
            "temporary_smoke_fixtures_removed": True,
            "parser_smoke_output_removed": True,
            "scratch_source_runtime_removed": True,
            "temporary_source_archive_removed": True,
            "outcome_payloads_retained": False,
            "python_cache_paths": [],
            "no_raw_or_large_payload_retained": True,
            "lane_file_count_before_sha256s": None,
            "lane_total_bytes_before_sha256s": None,
            "largest_file": None,
        },
    )


if __name__ == "__main__":
    main()
