#!/usr/bin/env python3
"""Build the deterministic, outcome-blind P5 C1 SWE-agent V4 packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
FREEZE = "2026-08-23T17:30:00Z"
ARM_ID = "C1_FIXED_AGENT__SWE_AGENT"
SOURCE_COMMIT = "3ea751c087f32b16e039a2233dd6eefecef325d5"
SOURCE_REPO = "https://github.com/SWE-agent/SWE-agent"
RAW_ROOT = f"https://raw.githubusercontent.com/SWE-agent/SWE-agent/{SOURCE_COMMIT}"
TERMINAL = (
    "P5_C1_V4_SWE_AGENT_NATIVE_PARSER_AND_ISOLATION_POLICY_BOUND__"
    "TWELVE_C1_FIELDS_BLOCKING__ZERO_OF_SIX_PANEL_READY__"
    "PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK"
)

PREDECESSORS = {
    "v3_adapter_refinement_sha256s": "50d1ff72f63093216761c4b47d3ced6de82915967578f33f3296bf41e4f73c4a",
    "v3_blocker_ledger": "265e3ba834ab7e24c471965f8064542e3f61f74414e0646b22a90fe9ae95c789",
    "v3_resource_template": "b20b30937dd79a5c318ef2a76abe1db561918c1118416faf5f70d4b952e48340",
    "v2_comparator_panel_sha256s": "94ef91058dd6c453296d557129e080ff7918f8d7e09716a1d69ba57d77b5bad1",
    "v2_identity_ledger": "f6419103024de98d0cf44ee2681399007001eb79c9b830312d501b6045a60583",
    "v2_terminal_adapters_sha256s": "bd69cfcb3dda70d4d08c84b6ce35a0cc7e77865627dd48278e07b3f8cd158850",
    "v2_resource_ledger": "1e3a450b1561cb2d3a1d556c77ef1688f8894fb2331fcfa334de87a18bd11dfe",
}

SOURCE_FILES = [
    ("LICENSE", 1147, "7610ed3916f6674e34b78417894abd57ff538b3cfdda3085e3643d82acbaf31f", "e702436e21844c5c519de31ab68277a6d3b427d9"),
    ("README.md", 8158, "dcd880557720efbab0f5c0e68f2bc742309efecfce83244c9e670ec1f1adf76f", "e241ede47c338b69eb13cbc5423047e1edf1d50f"),
    ("pyproject.toml", 6487, "c15229fac40a10716b53fda2cf6ba756d62cb59d682e7d10d7d62b640dfccef9", "f17efb696ee262637823380bbbee5e3ca03ba9c5"),
    ("config/default.yaml", 3242, "96aeb863cbfaa768044527155f8555c9b401c6644e937b5b6b0bba5538b6eee4", "fb79208113c3e803c091f3886e240a7918c3cd7f"),
    ("sweagent/run/run.py", 5327, "f4d50e37528f6a737f514bc888ea7efac25cdbb61bc1f6e6371546f6ef886e79", "e9952a9c9262d0580f5ab8552d2ba249c3eb162e"),
    ("sweagent/run/run_single.py", 9182, "4c373cdea6a7d3c67a7c8ad2c183ae1bb0d3e74fe820957ca6469b8a9e1eae80", "1c3209ad165773e7374b5765efafce00bd4d114e"),
    ("sweagent/run/hooks/apply_patch.py", 4506, "d9e283aa53673e43039513b71d111817dbce0f44e6e3d2022a0f4037620a0848", "d199ec1fcf7fd774a994a10748cc7d31929eb706"),
    ("sweagent/agent/agents.py", 55804, "d6cdf7ac66a6509ceba08e3541b856f0734acf79f9a485ed8a6e2c72f0d211a8", "4844aeb7c42e06121fe37ba223e9263c04b53c3b"),
    ("sweagent/agent/models.py", 37757, "91a8cb62703d7db656b0e615811ff0b9eedd51cd3ea89a6eeb2393f1d35c6cce", "496b226574b84c1b65edde284dfbfaa48b4f4b8d"),
    ("sweagent/environment/swe_env.py", 10989, "cc2631890aaba56a648a2bdeef6019b7c2f29a171daba6e704adbfb57ff99c7a", "cbe01952643decdf8c519b10a659e254e9a02384"),
    ("sweagent/environment/repo.py", 9519, "88d0c1098202a725eaaddcfa8d61b09eaacb7232cad5becbcd568b50b26dc760", "655db8dd9de19b9c044ced88c0fe14b7fc63d110"),
    ("tests/test_data/data_sources/simple_instances.yaml", 101, "b088b1a7d146afcab66d2c529409066685a2b4d4433ba18df3649aef0c374bd8", "5de565b72f5b7a8de9260090ec2338e70864ac6b"),
    ("docs/installation/source.md", 2321, "767c35277faa115d5e39c04d3af5e5a1c1cb1ec95bc5685593cc27979ee62319", "948ae25d56b5ae24d2d5aa4c2275a62fc1d3bd3a"),
    ("docs/usage/cli.md", 1354, "f3b3eb4c7df5a0e1dc68a19c394ed344ecd99dfb246fc6a9e40e0e8cafbae7e8", "c993977e15f6b6b02fdd88e4ff109398a0e69f7f"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name: str, value: Any) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(name: str, value: str) -> None:
    (ROOT / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def field(state: str, binding: Any, cause: str | None, residual: str, next_discriminator: str) -> dict[str, Any]:
    return {
        "binding": binding,
        "cause": cause,
        "next_discriminator": next_discriminator,
        "residual": residual,
        "state": state,
    }


def build() -> None:
    parser_sha = sha(ROOT / "p5_c1_native_parser.py")
    runner_sha = sha(ROOT / "p5_c1_isolated_runner.py")
    lock_sha = sha(ROOT / "SWE_AGENT_DEPENDENCY_LOCK_V4.uv.lock")
    smoke_sha = sha(ROOT / "UPSTREAM_SIMPLE_INSTANCE.yaml")

    source_manifest = {
        "schema_version": "orion.p5.c1.public-source-rights-manifest.v4",
        "manifest_id": "P5.C1.SWE_AGENT.PUBLIC.SOURCE.RIGHTS.V4",
        "captured_at_utc": FREEZE,
        "arm_id": ARM_ID,
        "official_repository": SOURCE_REPO,
        "commit_sha": SOURCE_COMMIT,
        "official_status": "OFFICIAL_PAPER_LINKED_IMPLEMENTATION",
        "paper": "arxiv:2405.15793v3",
        "source_files": [
            {
                "path": path,
                "bytes": size,
                "sha256": digest,
                "git_blob_sha1": blob,
                "raw_url": f"{RAW_ROOT}/{path}",
            }
            for path, size, digest, blob in SOURCE_FILES
        ],
        "authoritative_native_contract": {
            "package_entrypoint": "sweagent = sweagent.run.run:main",
            "documented_single_run": "sweagent run --config config/default.yaml ...",
            "default_model": "UNBOUND_REQUIRED_FIELD",
            "default_deployment_image_tag": "python:3.11",
            "default_config_contains_review_on_submit_bundle": True,
            "default_config_is_directly_c1_admissible": False,
            "native_output": ["trajectory JSON", "candidate patch", "prediction JSONL", "run metadata"],
            "native_terminal_source": "trajectory.info.exit_status",
        },
        "runtime_base_capture": {
            "registry": "docker.io/library/python",
            "mutable_tag_observed": "3.11",
            "selected_platform": {"os": "linux", "architecture": "amd64"},
            "manifest_digest": "sha256:fd6b7cf944078fe424fe8b7d659e6cb4d28cf75495d1c52a43c49b6293fa5002",
            "config_digest": "sha256:c514701300438939d8f2f3fd75cc57ea2eff502c1920e5cc98c713cf17452e3d",
            "complete_swe_agent_runtime": False,
            "rights_state": "UNBOUND",
        },
        "rights": {
            "swe_agent_source": {
                "state": "BOUND",
                "spdx": "MIT",
                "license_path": "LICENSE",
                "license_sha256": "7610ed3916f6674e34b78417894abd57ff538b3cfdda3085e3643d82acbaf31f",
                "scope": "Pinned SWE-agent repository bytes, including the copied simple fixture.",
            },
            "simple_fixture": {
                "state": "BOUND_FOR_OUTCOME_FREE_SMOKE_ONLY",
                "path": "UPSTREAM_SIMPLE_INSTANCE.yaml",
                "sha256": smoke_sha,
                "not_a_p5_confirmatory_case": True,
            },
            "generated_v4_artifacts": {
                "state": "UNBOUND",
                "reason": "No independent redistribution/licensing authority was supplied for generated run artifacts.",
            },
            "resolved_dependencies": {
                "state": "UNBOUND",
                "reason": "The lock identifies bytes but the transitive licence/notice set was not independently closed.",
            },
            "container": {
                "state": "UNBOUND",
                "reason": "The official image contains multiple upstream components; a complete image rights/notice packet was not frozen.",
            },
            "model_provider_services": {"state": "UNBOUND"},
            "p5_task_and_benchmark_content": {"state": "UNBOUND"},
        },
        "outcome_boundary": {
            "comparator_outcomes_accessed": False,
            "public_benchmark_first_record_key_names_observed": True,
            "gold_patch_or_test_patch_payload_values_disclosed_to_lane": False,
            "protected_test_content_disclosed_to_lane": False,
            "protected_scores_accessed": False,
        },
    }
    write_json("P5_C1_V4_SOURCE_RIGHTS_MANIFEST.json", source_manifest)

    native_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://orion.invalid/p5/v4/c1-swe-agent-native-terminal.schema.json",
        "title": "P5 C1 normalized SWE-agent native terminal",
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "arm_id", "instance_id", "source", "native_terminal", "native_retention", "adapter_disposition", "outcome_boundary"],
        "properties": {
            "schema_version": {"const": "orion.p5.c1.swe-agent-native-terminal.v4"},
            "arm_id": {"const": ARM_ID},
            "instance_id": {"type": ["string", "null"]},
            "source": {"type": "object"},
            "native_terminal": {
                "type": "object",
                "additionalProperties": False,
                "required": ["arm_id", "status", "native_code", "payload_sha256"],
                "properties": {
                    "arm_id": {"const": ARM_ID},
                    "status": {"enum": ["COMPLETE_SUCCESS", "ERROR", "TIMEOUT", "ABSTAIN", "EMPTY", "PARTIAL", "INVALID"]},
                    "native_code": {"type": "string"},
                    "payload_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                },
            },
            "native_retention": {"type": "object"},
            "adapter_disposition": {
                "type": "object",
                "properties": {"output": {"const": "UNRESOLVED"}, "raw_native_singleton_licensed": {"const": False}},
                "required": ["output", "reason", "raw_native_singleton_licensed"],
            },
            "outcome_boundary": {"type": "object"},
        },
    }
    write_json("P5_C1_V4_NATIVE_OUTPUT_SCHEMA.json", native_schema)

    write_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://orion.invalid/p5/v4/c1-isolated-write-audit.schema.json",
        "title": "P5 C1 isolated write/reset audit",
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "arm_id", "attempt_id", "seed_tree_sha256", "post_tree_sha256", "writes", "forbidden_write_attempts", "reset_verified"],
        "properties": {
            "schema_version": {"const": "orion.p5.c1.isolated-write-audit.v4"},
            "arm_id": {"const": ARM_ID},
            "attempt_id": {"type": "string", "pattern": "^P5C1-[A-Z0-9_.-]+$"},
            "seed_tree_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "post_tree_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "writes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["relative_path", "operation", "before_sha256", "after_sha256"],
                    "properties": {
                        "relative_path": {"type": "string", "pattern": "^(?!/)(?!.*\\.\\.).+$"},
                        "operation": {"enum": ["CREATE", "UPDATE", "DELETE"]},
                        "before_sha256": {"type": ["string", "null"]},
                        "after_sha256": {"type": ["string", "null"]},
                    },
                },
            },
            "forbidden_write_attempts": {"type": "integer", "minimum": 0},
            "reset_verified": {"type": "boolean"},
        },
        "frozen_policy": {
            "host_read_only_mounts": ["/input/source", "/input/task"],
            "ephemeral_candidate_write_root": "/work/task",
            "host_writable_output_root": "/run/p5-output",
            "root_filesystem": "READ_ONLY",
            "network": "NONE_UNTIL_PROVIDER_AND_ALLOWLIST_BOUND",
            "capabilities": "DROP_ALL",
            "privilege_escalation": "FORBIDDEN",
            "reset": "NEW_CONTAINER_AND_COPY_FROM_READ_ONLY_SEED_PER_ATTEMPT",
        },
    }
    write_json("P5_C1_V4_WRITE_SURFACE_SCHEMA.json", write_schema)

    terminal_rules = {
        "schema_version": "orion.p5.c1.native-terminal-retention-rules.v4",
        "rules_id": "P5.C1.SWE_AGENT.NATIVE.TERMINAL.RETENTION.V4",
        "arm_id": ARM_ID,
        "parser_sha256": parser_sha,
        "exact_native_retention": ["info.exit_status including null", "submission UTF-8 byte count", "submission sha256", "trajectory sha256", "trajectory step count", "native model usage counters"],
        "mapping_in_order": [
            {"when": "exit_status == submitted and submission is nonempty", "status": "COMPLETE_SUCCESS"},
            {"when": "exit_status begins submitted (", "status": "PARTIAL", "reason": "autosubmission does not erase the causing terminal"},
            {"when": "exit_status contains timeout or total_execution_time", "status": "TIMEOUT"},
            {"when": "exit_status in exit_forfeit, exit_cost, exit_context, exit_command", "status": "ABSTAIN"},
            {"when": "exit_status in exit_api, exit_environment_error, exit_error, exit_format", "status": "ERROR"},
            {"when": "missing exit_status and no steps/submission", "status": "EMPTY"},
            {"when": "missing exit_status with partial material", "status": "PARTIAL"},
            {"when": "skipped or unrecognized", "status": "INVALID"},
        ],
        "class_emission": "NEVER_BY_NATIVE_PARSER",
        "adapter_disposition": "UNRESOLVED",
        "raw_native_singleton_licences": 0,
        "protected_key_policy": "REFUSE",
        "protected_or_evaluator_keys": sorted(["FAIL_TO_PASS", "PASS_TO_PASS", "evaluation_report", "gold_patch", "protected_outcome", "protected_score", "resolved", "reward", "score", "test_patch"]),
    }
    write_json("P5_C1_V4_NATIVE_TERMINAL_RULES.json", terminal_rules)

    case_requirements = {
        "schema_version": "orion.p5.c1.candidate-visible-case-requirements.v4",
        "requirements_id": "P5.C1.EXACT.CANDIDATE.VISIBLE.CASE.V4",
        "required_before_execution": [
            "immutable case id",
            "problem statement bytes and sha256",
            "task repository URL, commit and repository licence bytes",
            "candidate-visible setup files with path/size/sha256",
            "run_config.yaml with no placeholders",
            "agent.type fixed to default rather than retry",
            "agent.action_sampler fixed to null",
            "tools bundles exclude review_on_submit_m and any chooser/reviewer loop",
            "actions.open_pr and actions.apply_patch_locally fixed false",
            "rights authority for problem, repository and task content",
            "attestation that gold patch, protected tests, score and outcome examples are absent",
        ],
        "forbidden_candidate_fields": sorted(["FAIL_TO_PASS", "PASS_TO_PASS", "gold_patch", "patch", "protected_outcome", "protected_score", "resolved", "reward", "score", "test_patch"]),
        "public_smoke_fixture": {
            "path": "UPSTREAM_SIMPLE_INSTANCE.yaml",
            "sha256": smoke_sha,
            "source_path": "tests/test_data/data_sources/simple_instances.yaml",
            "source_commit": SOURCE_COMMIT,
            "source_right": "MIT repository licence",
            "contains": ["image_name", "problem_statement", "id"],
            "gold_or_outcome_payloads": False,
            "confirmatory_fit": "INSUFFICIENT",
            "cause": "The official fixture has no pinned task repository, substantive P5 case, or case-specific rights packet.",
        },
        "actual_p5_candidate_visible_case": {"state": "UNBOUND", "binding": None},
    }
    write_json("P5_C1_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json", case_requirements)

    protocol = {
        "schema_version": "orion.p5.c1.swe-agent-execution-binding-protocol.v4",
        "protocol_id": "P5.C1.SWE_AGENT.EXECUTION.BINDING.V4",
        "frozen_at_utc": FREEZE,
        "arm_id": ARM_ID,
        "predecessors": PREDECESSORS,
        "authority": "OUTCOME_BLIND_C1_PREFLIGHT_AND_ARM_NATIVE_ADAPTER_BINDING_ONLY",
        "source_identity": {"repository": SOURCE_REPO, "commit_sha": SOURCE_COMMIT, "licence": "MIT", "native_entrypoint": "sweagent = sweagent.run.run:main"},
        "frozen_components": {
            "native_parser": {"path": "p5_c1_native_parser.py", "sha256": parser_sha},
            "isolation_wrapper": {"path": "p5_c1_isolated_runner.py", "sha256": runner_sha},
            "dependency_lock": {"path": "SWE_AGENT_DEPENDENCY_LOCK_V4.uv.lock", "sha256": lock_sha, "resolver": "uv 0.11.1", "python_request": "3.11", "packages": 152},
            "public_smoke_fixture": {"path": "UPSTREAM_SIMPLE_INSTANCE.yaml", "sha256": smoke_sha},
            "fallbacks": [],
            "compute": {"vcpus": 1, "ram_gib": 4, "gpus": 0, "parallelism": 1, "pids_limit": 512},
            "wallclock_seconds": {"per_case": 3600, "whole_c1_run": 3600, "termination_grace": 30},
        },
        "execution_order": [
            "independent custodian freezes missing candidate case, primary model/service, complete runtime, remaining rights, network/resource enforcement and protected scorer fields",
            "preflight rejects retry-agent, action-sampler, review-on-submit, open-PR and local-apply configuration for the fixed-agent arm",
            "validator verifies every required C1 field is BOUND without outcome access",
            "wrapper copies a read-only seed to an ephemeral task root in a new read-only container",
            "SWE-agent receives only candidate-visible packet and prospectively frozen configuration",
            "native parser hashes submission and retains native terminal without class inference",
            "candidate output is transferred once to external protected custody with no feedback",
            "external scorer evaluates once; candidate and adaptation custody receive no score or outcome",
        ],
        "nonclaims": [
            "No comparator or model was executed.",
            "The simple fixture is not a P5 confirmatory case.",
            "A native parser is not an eight-class scientific classifier.",
            "No performance, preservation, transfer, harm or superiority result is available.",
        ],
    }
    write_json("P5_C1_V4_EXECUTION_BINDING_PROTOCOL.json", protocol)

    missing_residual = "C1 is not licensed for execution while this field is not BOUND."
    fields = {
        "adapter.isolated_write_surface": field("BOUND", {"path": "p5_c1_isolated_runner.py", "sha256": runner_sha, "policy_schema": "P5_C1_V4_WRITE_SURFACE_SCHEMA.json"}, None, "A hashed fail-closed Docker policy now fixes read-only inputs, ephemeral task writes, a sole host output mount and per-attempt reset.", "Validate the same wrapper against the eventual complete runtime image before custody execution."),
        "adapter.native_parser_binding": field("BOUND", {"path": "p5_c1_native_parser.py", "sha256": parser_sha, "output_schema": "P5_C1_V4_NATIVE_OUTPUT_SCHEMA.json"}, None, "The parser binds SWE-agent trajectory.info.exit_status and submission bytes to an outcome-blind terminal while licensing zero raw singletons.", "External V3 certificate/action validation remains separate and must not be folded into this parser."),
        "custody.external_protected_scorer": field("CANNOT_CHECK", None, "No independent scorer identity, code digest, access-control principal or signed acceptance exists.", missing_residual, "Independent custodian supplies scorer identity, immutable digest and access-control attestation without revealing protected bytes."),
        "custody.one_shot_no_feedback_barrier": field("CANNOT_CHECK", None, "The local wrapper can deny candidate network but cannot attest independent scorer custody or post-transfer nonfeedback.", missing_residual, "Independent custodian binds one accepted submission, one scoring event, append-only receipt and no return channel."),
        "custody.protected_panel_freshness": field("CANNOT_CHECK", None, "No protected panel identity or freshness attestation was available to this lane.", missing_residual, "Independent custodian freezes a fresh panel after protocol lock and reveals only a signed aggregate receipt after the study closes."),
        "identity.native_entrypoint_bytes": field("BOUND", {"pyproject_sha256": "c15229fac40a10716b53fda2cf6ba756d62cb59d682e7d10d7d62b640dfccef9", "run_py_sha256": "f4d50e37528f6a737f514bc888ea7efac25cdbb61bc1f6e6371546f6ef886e79", "entrypoint": "sweagent = sweagent.run.run:main"}, None, "Exact official entrypoint bytes retained.", "Reverify raw bytes immediately before image build."),
        "identity.source_license_bytes": field("BOUND", {"spdx": "MIT", "path": "LICENSE", "sha256": "7610ed3916f6674e34b78417894abd57ff538b3cfdda3085e3643d82acbaf31f"}, None, "Exact source licence bytes retained.", "Carry the licence and notice into the eventual runtime/source bundle."),
        "identity.source_repository_commit": field("BOUND", {"repository": SOURCE_REPO, "commit_sha": SOURCE_COMMIT}, None, "Official repository commit retained.", "Fetch by commit and verify every source-manifest byte before build."),
        "inputs.candidate_visible_case_bytes": field("UNBOUND", None, "Only the official MIT smoke fixture is frozen; it is not a substantive P5 case and lacks a pinned task repository.", missing_residual, "Publish one rights-cleared P5 candidate packet satisfying P5_C1_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json."),
        "model_provider.fallbacks": field("BOUND", {"fallbacks": [], "closed_behavior": "FAIL_WITH_NATIVE_TERMINAL; DO_NOT_SWITCH_MODEL_OR_PROVIDER"}, None, "Fallback set is the closed empty list.", "Retain the empty fallback list when the primary is selected."),
        "model_provider.primary": field("UNBOUND", None, "No exact model, provider, endpoint, service revision, prompt capability map or authorized credential principal was selected.", missing_residual, "Select one immutable or independently attested model/service identity and hash the complete effective config."),
        "resources.calls_tokens_usd": field("UNBOUND", {"prospective_values": {"api_calls": 50, "max_input_tokens_per_call": 64000, "max_output_tokens_per_call": 8000, "aggregate_input_tokens": 400000, "aggregate_output_tokens": 100000, "usd": 3.0}}, "Exact values are proposed, but aggregate token hard-stop and cost accounting depend on the unbound primary model/provider/tokenizer.", missing_residual, "Bind provider-native usage accounting plus a hard-stop monitor, then retain overshoot behavior as a typed terminal."),
        "resources.retry_network": field("UNBOUND", {"retry_values": {"attempts": 3, "min_wait_seconds": 1, "max_wait_seconds": 4}, "fallbacks": []}, "Retry values are closed, but the network allowlist cannot be final until the primary endpoint and task-fetch policy are bound.", missing_residual, "Freeze exact DNS/IP/TLS endpoint policy or a local offline model; disallow all other egress."),
        "resources.wallclock": field("BOUND", {"per_case_seconds": 3600, "whole_c1_run_seconds": 3600, "termination_grace_seconds": 30, "enforcer": "p5_c1_isolated_runner.py", "enforcer_sha256": runner_sha}, None, "The one-case wallclock is prospectively frozen and wrapped by timeout with a 30-second kill grace.", "Verify timeout availability and signal behavior in the eventual runtime image."),
        "rights.container_and_generated_artifacts": field("UNBOUND", None, "Base-image identity is captured, but complete component notices and authority for generated trajectories/patch retention or redistribution are not closed.", missing_residual, "Freeze complete image SBOM/licences and obtain explicit generated-artifact retention/disclosure authority."),
        "rights.model_provider_and_services": field("UNBOUND", None, "No provider/service was selected and no study-use/data-retention terms were captured.", missing_residual, "Bind provider terms, data policy, region, credential principal and permitted publication of aggregate receipts."),
        "rights.task_and_benchmark_content": field("UNBOUND", None, "The MIT smoke fixture is lawful but not the P5 task; issue visibility alone is not a reuse licence.", missing_residual, "Use an authored or explicitly licensed P5 task packet with repository/content licence bytes."),
        "runtime.compute": field("BOUND", {"vcpus": 1, "ram_gib": 4, "gpus": 0, "parallelism": 1, "pids_limit": 512, "enforcer_sha256": runner_sha}, None, "The wrapper fixes a single-worker CPU/RAM/PID envelope and no GPU.", "Verify Docker enforcement receipt on the eventual execution host."),
        "runtime.container_or_environment": field("UNBOUND", {"base_image": "docker.io/library/python:3.11@sha256:fd6b7cf944078fe424fe8b7d659e6cb4d28cf75495d1c52a43c49b6293fa5002"}, "The base image is content-addressed, but no complete derived SWE-agent runtime image was built and hashed.", missing_residual, "Build from the frozen source and lock, record final image digest/SBOM, and verify entrypoint plus timeout tooling."),
        "runtime.dependency_lock": field("BOUND", {"path": "SWE_AGENT_DEPENDENCY_LOCK_V4.uv.lock", "sha256": lock_sha, "resolver": "uv 0.11.1", "python_request": "3.11", "packages": 152}, None, "A hash-locked 152-package resolution is frozen for the pinned source.", "Build once from this lock on the selected Linux platform and preserve the wheel/source archive digest receipt."),
        "runtime.task_environment": field("UNBOUND", None, "No substantive P5 task repository, base commit, setup commands, environment image or candidate-visible run_config.yaml is frozen; the upstream default review-on-submit bundle is not directly admissible for the fixed-agent arm.", missing_residual, "Bind the exact task seed tree, base commit, setup command bytes and an effective default-agent configuration with retry-agent, action-sampler and review-on-submit disabled."),
    }
    required = sorted(fields)
    blocking = [path for path in required if fields[path]["state"] != "BOUND"]
    bound = [path for path in required if fields[path]["state"] == "BOUND"]
    registry = {
        "schema_version": "orion.p5.c1.field-registry.v4",
        "registry_id": "P5.C1.SWE_AGENT.FIELD.REGISTRY.V4",
        "frozen_at_utc": FREEZE,
        "arm_id": ARM_ID,
        "required_field_paths": required,
        "fields": fields,
        "bound_field_count": len(bound),
        "bound_fields": bound,
        "blocking_field_count": len(blocking),
        "blocking_fields": blocking,
        "execution_ready": False,
        "panel_confirmatory_ready_arms": 0,
        "bound_execution_envelope": {
            "runtime_image": "docker.io/library/python:3.11@sha256:fd6b7cf944078fe424fe8b7d659e6cb4d28cf75495d1c52a43c49b6293fa5002",
            "compute": {"vcpus": 1, "ram_gib": 4, "gpus": 0, "parallelism": 1, "pids_limit": 512},
            "wallclock_seconds": {"per_case": 3600, "whole_c1_run": 3600, "termination_grace": 30},
            "fallbacks": [],
        },
        "terminal": "C1_PARTIAL_BINDING__TWELVE_REQUIRED_FIELDS_NOT_BOUND__EXECUTION_REFUSED",
    }
    write_json("P5_C1_V4_FIELD_REGISTRY.json", registry)

    custody_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://orion.invalid/p5/v4/c1-independent-custody-attestation.schema.json",
        "title": "P5 C1 independent one-shot custody attestation",
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "custodian_id", "scorer_code_sha256", "protected_panel_commitment", "panel_frozen_after_protocol", "candidate_custody_has_no_read_access", "one_submission", "one_scoring_event", "no_feedback_channel", "signed_at_utc", "signature"],
        "properties": {
            "schema_version": {"const": "orion.p5.c1.independent-custody-attestation.v4"},
            "custodian_id": {"type": "string", "minLength": 1},
            "scorer_code_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "protected_panel_commitment": {"type": "string", "minLength": 32},
            "panel_frozen_after_protocol": {"const": True},
            "candidate_custody_has_no_read_access": {"const": True},
            "one_submission": {"const": True},
            "one_scoring_event": {"const": True},
            "no_feedback_channel": {"const": True},
            "signed_at_utc": {"type": "string", "format": "date-time"},
            "signature": {"type": "string", "minLength": 32},
        },
        "current_state": "UNBOUND_NO_ATTESTATION_PRESENT",
    }
    write_json("P5_C1_V4_CUSTODY_HANDOFF_SCHEMA.json", custody_schema)

    negatives = [
        ("C1V4-N01", "Candidate-visible P5 case remains unbound", "Only the official MIT smoke fixture is frozen; it has no task repository and is not a P5 scientific case.", "C1 execution and task-content rights remain blocked.", "Author and licence one substantive P5 case packet with exact problem/repository/config bytes and no protected fields."),
        ("C1V4-N02", "Primary model/provider remains unbound", "No immutable primary identity, endpoint, revision, capability mapping or credential principal was supplied.", "Calls, tokens, USD, retry/network and service rights cannot be fully enforced or matched.", "Freeze one exact primary plus provider terms, endpoint, tokenizer/accounting and effective config hash."),
        ("C1V4-N03", "Complete runtime remains unbound", "A base image digest and dependency lock exist, but the derived SWE-agent image was not built or content-addressed.", "The exact executable environment and dependency installation receipt cannot be checked.", "Build the Linux amd64 image from source+lock, emit digest, SBOM, licence bundle and entrypoint receipt."),
        ("C1V4-N04", "Aggregate usage hard-stop remains unbound", "Proposed caps exist, while exact aggregate token and USD enforcement depends on the primary provider/tokenizer.", "Resource matching cannot yet be licensed.", "Implement provider-reconciled monotone counters with a pre-call remaining-budget gate and typed overshoot terminal."),
        ("C1V4-N05", "Network allowlist remains unbound", "Retry counts are frozen but no primary service endpoint or offline deployment is selected.", "The wrapper correctly defaults to no network, which also prevents an API-backed run.", "Bind offline inference or a minimal exact egress policy including DNS/TLS identity."),
        ("C1V4-N06", "Task environment remains unbound", "No task seed tree, repository commit, setup commands or complete run_config.yaml exists.", "The native runner has nothing scientifically valid to execute.", "Freeze the task tree and setup/run configuration as one content-addressed candidate packet."),
        ("C1V4-N07", "Three rights surfaces remain unbound", "Task, service, container-component and generated-artifact authorities are not closed by the SWE-agent MIT licence.", "Lawful source use does not license the full study.", "Collect separate rights/terms receipts for every non-source byte and generated artifact flow."),
        ("C1V4-N08", "Independent custody remains CANNOT_CHECK", "No external scorer, protected-panel freshness commitment or signed one-shot barrier exists.", "Protected performance, harm and superiority remain CANNOT_CHECK.", "Independent custodian completes P5_C1_V4_CUSTODY_HANDOFF_SCHEMA.json after protocol freeze."),
        ("C1V4-N09", "Adapter binding is not scientific classification", "The parser preserves native terminals and refuses protected keys; it intentionally emits UNRESOLVED.", "Zero raw native singleton licences are preserved.", "Only the separate V3 input-native certificate/action/invariance proof may license a supported singleton."),
        ("C1V4-N10", "No C1 or panel outcome execution occurred", "This lane used source/configuration bytes and authored synthetic parser fixtures only.", "No performance estimate or positive paper hypothesis follows.", "Execute only after all six arms and independent custody are ready; otherwise preserve 0/6."),
        ("C1V4-N11", "Upstream default config is not directly C1-admissible", "The pinned default config includes the review_on_submit_m bundle, while C1 is the fixed-agent arm and may not gain a within-unit reviewer/retry selector.", "Using the upstream default unchanged would confound C1 with an adaptive/reviewer mechanism.", "Freeze agent.type=default, action_sampler=null, no retry loop, no review-on-submit bundle, and no open-PR/local-apply actions in the exact run config."),
    ]
    negative_json = {
        "schema_version": "orion.p5.c1.recursive-negative-ledger.v4",
        "ledger_id": "P5.C1.SWE_AGENT.RECURSIVE.NEGATIVE.LEDGER.V4",
        "arm_id": ARM_ID,
        "entries": [
            {"id": i, "negative_result": n, "cause": c, "residual": r, "next_discriminator": d, "resolved_in_v4": False}
            for i, n, c, r, d in negatives
        ],
        "rule": "A negative result creates a prospectively testable discriminator; it is never rewritten as a positive outcome.",
    }
    write_json("P5_C1_V4_NEGATIVE_LEDGER.json", negative_json)
    rows = "\n".join(f"| {i} | {n} | {c} | {r} | {d} |" for i, n, c, r, d in negatives)
    write_text(
        "P5_C1_V4_NEGATIVE_LEDGER.md",
        "# P5 C1 V4 recursive negative ledger\n\n"
        "A blocker is a research object with a cause, residual, and next discriminator. It is not converted to a positive claim.\n\n"
        "| ID | Negative result | Cause | Residual | Next discriminator |\n"
        "|---|---|---|---|---|\n" + rows,
    )

    result = {
        "schema_version": "orion.p5.c1.swe-agent-execution-binding-result.v4",
        "protocol_id": "P5.C1.SWE_AGENT.EXECUTION.BINDING.V4",
        "arm_id": ARM_ID,
        "authority": "PUBLIC_SOURCE_IDENTITY_AND_OUTCOME_BLIND_PREFLIGHT_ONLY",
        "v4_repairs": {
            "newly_bound_v3_fields": ["adapter.isolated_write_surface", "adapter.native_parser_binding", "model_provider.fallbacks", "resources.wallclock", "runtime.compute", "runtime.dependency_lock"],
            "retained_bound_identity_fields": ["identity.native_entrypoint_bytes", "identity.source_license_bytes", "identity.source_repository_commit"],
            "c1_bound_fields": 9,
            "c1_blocking_fields": 12,
        },
        "execution": {"c1_executed": False, "c1_execution_ready": False, "panel_confirmatory_ready_arms": 0, "panel_required_arms": 6},
        "preserved_boundaries": {"raw_native_singleton_licences": 0, "scienceclaw_supported_singletons": 0, "v3_synthetic_cases": 231, "v3_supported_singleton_case_records": 40, "v3_unresolved_case_records": 191},
        "preserved_claims": {"H1": "CANNOT_CHECK", "H2": "CANNOT_CHECK", "H3": "CANNOT_CHECK", "H4": "CANNOT_CHECK", "performance": "CANNOT_CHECK", "harm": "CANNOT_CHECK", "superiority": "CANNOT_CHECK", "top_tier_publication_readiness": "NOT_ESTABLISHED"},
        "next_discriminator": "Bind one exact rights-cleared P5 case, primary model/service, derived runtime image, usage/network enforcement and three independent-custody fields; C1 still must wait for 6/6 panel readiness.",
        "terminal": TERMINAL,
    }
    write_json("P5_C1_V4_RESULT.json", result)

    write_text(
        "SCIENTIFIC_REPORT_V4.md",
        f"""# P5 C1 SWE-agent execution-binding V4

## Terminal

`{TERMINAL}`

This is an outcome-blind preflight repair, not a comparator result. No model,
comparator, protected scorer, benchmark outcome, gold-patch value,
protected-test content, or performance table was executed or disclosed to the
lane. During source triage, the key names of one public test record were listed;
this exposed names such as `patch`/`test_patch`, never their payload values.

## Material repair

V4 converts six of C1's 18 V3 blocker fields into prospective byte-level
bindings while retaining the three already-bound identity fields. C1 therefore
has **9/21 required fields BOUND** and **12/21 blocking**. Panel readiness
remains **0/6**.

| Newly bound field | Frozen evidence |
|---|---|
| `adapter.native_parser_binding` | Hashed parser for native SWE-agent trajectory JSON; exact native exit retained; protected keys refused; raw singleton licences = 0 |
| `adapter.isolated_write_surface` | Hashed fail-closed container wrapper: read-only source/task inputs, ephemeral task mutation, sole output mount, no network, dropped capabilities, new container per attempt |
| `model_provider.fallbacks` | Closed empty fallback list; provider switching forbidden |
| `resources.wallclock` | 3,600 s one-case/whole-run cap plus 30 s termination grace |
| `runtime.compute` | 1 vCPU, 4 GiB RAM, 0 GPU, one worker, 512 PID limit |
| `runtime.dependency_lock` | 152-package uv lock, SHA-256 `{lock_sha}` |

The native parser maps only exact `submitted` with a nonempty candidate patch
to the generic `COMPLETE_SUCCESS` terminal. Autosubmissions such as
`submitted (exit_cost)` remain `PARTIAL`, so budget/error causes are not erased.
Every parser output remains `UNRESOLVED`; the parser does not infer any of the
seven actionable responsibility classes.

The pinned upstream default config contains `review_on_submit_m`; it is source
evidence, not a directly admissible C1 run config. The eventual C1 config must
use `agent.type=default`, no retry agent, `action_sampler=null`, no
review-on-submit/chooser loop, and no open-PR or host-local patch application.

## Authoritative public bytes and rights

The official SWE-agent repository is pinned at `{SOURCE_COMMIT}`. Exact SHA-256
and git-blob identities are frozen for the MIT licence, package entrypoint,
default configuration, run/trajectory/patch code, model retry/resource code,
environment reset code, documentation, and official simple fixture. The source
licence hash remains
`7610ed3916f6674e34b78417894abd57ff538b3cfdda3085e3643d82acbaf31f`.

The copied 101-byte official fixture is MIT-covered and outcome-free, but it is
only a smoke input: it names `python:3.11`, a simple problem statement, and an
identifier. It has no pinned task repository and is not a substantive P5 case.
Consequently `inputs.candidate_visible_case_bytes` and
`rights.task_and_benchmark_content` remain unbound. Public issue visibility
alone is not treated as reuse authority.

The Linux/amd64 `python:3.11` base manifest is captured by digest, but it is not
a complete SWE-agent runtime image. Dependency identities do not by themselves
close transitive licences. Container, service, task, and generated-artifact
rights therefore remain separate blockers.

## Twelve remaining C1 blockers

1. exact P5 candidate-visible case bytes;
2. primary model/provider/service identity;
3. calls/tokens/USD hard-stop and provider-reconciled accounting;
4. final retry/network allowlist;
5. complete derived runtime image;
6. exact task environment;
7. task/benchmark-content rights;
8. model/provider/service rights;
9. container/generated-artifact rights;
10. independent protected scorer;
11. independent one-shot no-feedback barrier; and
12. protected-panel identity/freshness.

The wrapper refuses outcome execution while any remains non-BOUND. Local code
cannot self-attest independent custody; those three custody fields remain
`CANNOT_CHECK`, not optimistic placeholders.

## Preserved scientific boundary

- V3 stays unchanged: 231 fictional cases, 40 supported singleton case
  records in 20 constant fibres, 191 `UNRESOLVED`, and zero raw singleton
  licences.
- ScienceClaw remains outside supported singleton emission.
- Six-arm performance readiness stays 0/6.
- H1--H4, preservation, fresh transfer, harm, performance, and superiority
  remain `CANNOT_CHECK`.

## Next discriminator

Create one authored or explicitly licensed P5 case packet satisfying
`P5_C1_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json`; freeze one primary model
and its service terms; build and hash the complete runtime image from the
source and uv lock; implement provider-reconciled hard resource stops; and
obtain a signed independent custody attestation. C1 still cannot execute until
all six arms satisfy the matched panel contract.
""",
    )

    write_text(
        "README.md",
        """# P5 C1 SWE-agent execution binding V4

Outcome-blind successor lane for the C1 SWE-agent fields in the P5 six-arm
panel. This directory does not license comparator execution or any performance
claim.

## Read first

1. `SCIENTIFIC_REPORT_V4.md`
2. `P5_C1_V4_RESULT.json`
3. `P5_C1_V4_FIELD_REGISTRY.json`
4. `P5_C1_V4_NEGATIVE_LEDGER.{json,md}`

## Core bindings

- `P5_C1_V4_EXECUTION_BINDING_PROTOCOL.json`
- `P5_C1_V4_SOURCE_RIGHTS_MANIFEST.json`
- `P5_C1_V4_NATIVE_OUTPUT_SCHEMA.json`
- `P5_C1_V4_WRITE_SURFACE_SCHEMA.json`
- `P5_C1_V4_NATIVE_TERMINAL_RULES.json`
- `P5_C1_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json`
- `P5_C1_V4_CUSTODY_HANDOFF_SCHEMA.json`
- `p5_c1_native_parser.py`
- `p5_c1_isolated_runner.py`
- `SWE_AGENT_DEPENDENCY_LOCK_V4.uv.lock`
- `UPSTREAM_SIMPLE_INSTANCE.yaml`

## Outcome-free verification

```bash
rtk python build_p5_c1_v4_freeze.py
rtk python p5_c1_v4_validator.py
rtk sha256sum -c SHA256SUMS
```

No pytest or repository CI is part of this lane. The isolated runner's
preflight must refuse with 12 blockers; execution is forbidden until every
required field is independently BOUND.
""",
    )

    # The audit hashes everything already frozen except itself and SHA256SUMS.
    before_audit = sorted(
        p for p in ROOT.iterdir() if p.is_file() and p.name not in {"AUDIT_RECEIPT_V4.json", "SHA256SUMS"}
    )
    audit = {
        "schema_version": "orion.p5.c1.execution-binding-audit.v4",
        "audit_id": "P5.C1.SWE_AGENT.OUTCOME.FREE.BINDING.AUDIT.V4",
        "captured_at_utc": FREEZE,
        "authority": "DIRECT_BYTE_HASH_SCHEMA_AND_AUTHORED_SYNTHETIC_PARSER_VERIFICATION_ONLY",
        "artifact_sha256": {p.name: sha(p) for p in before_audit},
        "predecessor_checksum_verification": {"v3": "ALL_OK", "comparator_panel_v2": "ALL_OK", "terminal_adapters_v2": "ALL_OK"},
        "direct_checks": {
            "json_files_parse": True,
            "python_ast_parse": True,
            "native_parser_authored_synthetic_cases": 8,
            "native_parser_failures": 0,
            "isolated_runner_current_preflight_refuses": True,
            "c1_bound_fields": 9,
            "c1_blocking_fields": 12,
            "panel_confirmatory_ready_arms": 0,
            "sha256sum_check": "ALL_OK_AFTER_BUILD",
        },
        "outcome_boundary": {"comparators_or_models_executed": False, "comparator_outcomes_accessed": False, "protected_scores_accessed": False, "public_benchmark_first_record_key_names_observed": True, "gold_patch_or_test_patch_payload_values_disclosed_to_lane": False, "protected_test_content_disclosed_to_lane": False, "performance_tables_accessed": False},
        "pytest_or_repository_ci_run": False,
        "main_checkout_or_other_lanes_modified": False,
        "preserved": {"raw_native_singleton_licences": 0, "scienceclaw_supported_singletons": 0, "panel_ready": "0/6", "performance": "CANNOT_CHECK", "superiority": "CANNOT_CHECK"},
        "terminal": TERMINAL,
    }
    write_json("AUDIT_RECEIPT_V4.json", audit)

    entries = []
    for path in sorted(p for p in ROOT.iterdir() if p.is_file() and p.name != "SHA256SUMS"):
        entries.append(f"{sha(path)}  {path.name}")
    write_text("SHA256SUMS", "\n".join(entries))


if __name__ == "__main__":
    build()
