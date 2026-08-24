#!/usr/bin/env python3
"""Build the self-contained outcome-blind P5 C2 MOSS V4 freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
FROZEN_AT = "2026-08-23T17:38:58Z"
ARM_ID = "C2_DIRECT_SELF_EDIT__MOSS"
COMMIT = "5453f1feebad44c199f5887f852fc5bc7fb7d4da"
TREE = "ebfcd6ac3ae00749240a5e2d8a96ad570adaf63f"
ARCHIVE_SHA = "de6bb0e480749757d8e9b05a66c37c82228ea6d9d1e1cb92b6b32a3b28e5610e"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name: str, value: Any) -> None:
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def entry(state: str, *, binding: Any, cause: str | None, residual: str, next_discriminator: str) -> dict[str, Any]:
    return {
        "binding": binding,
        "cause": cause,
        "next_discriminator": next_discriminator,
        "residual": residual,
        "state": state,
    }


def main() -> None:
    parser_hash = sha(HERE / "p5_c2_native_parser.py")
    runner_hash = sha(HERE / "p5_c2_fail_closed_runner.py")
    host_lock_hash = sha(HERE / "MOSS_HOST_DEPENDENCY_LOCK_V4.uv.lock")
    node_lock_hash = sha(HERE / "MOSS_OPENCLAW_DEPENDENCY_LOCK_V4.pnpm-lock.yaml")

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
                "fail_closed_gate": "p5_c2_fail_closed_runner.py",
                "gate_sha256": runner_hash,
                "released_native_writes": [
                    "writable inner OpenClaw Git repository",
                    "MOSS_DATA_DIR session/evolution state",
                    "Docker images and containers through a host daemon",
                    "temporary Unix socket and generated local configuration",
                ],
            },
            cause="The released architecture requires host-side source mutation and Docker control. The pinned compose file does not isolate the daemon, dynamic trial workers have no CPU/RAM/PID flags, and no content-addressed disposable VM or rootless Docker endpoint is bound.",
            residual="The gate prevents accidental execution, but it is not an arm-native write-isolation proof and therefore does not close this field.",
            next_discriminator="Run the exact source in a disposable content-addressed VM with a dedicated rootless Docker daemon; prove host/source/protected mounts are absent and produce a complete before/after mutation digest.",
        ),
        "adapter.native_parser_binding": entry(
            "BOUND",
            binding={
                "path": "p5_c2_native_parser.py",
                "sha256": parser_hash,
                "input": "pinned MOSS evolution manifest schemaVersion 6",
                "output_schema": "P5_C2_V4_NATIVE_OUTPUT_SCHEMA.json",
                "protected_key_policy": "fail closed",
                "raw_native_singletons_licensed": 0,
            },
            cause=None,
            residual="The parser retains exact manifest status/latest verdict and hashes candidate identifiers while emitting only UNRESOLVED; it does not classify scientific responsibility.",
            next_discriminator="Keep the parser byte-frozen and run the separate V3 certificate/action/fibre operation outside candidate custody.",
        ),
        "custody.external_protected_scorer": entry(
            "CANNOT_CHECK",
            binding=None,
            cause="No independent scorer principal, immutable scorer digest, access control or signed acceptance exists.",
            residual="C2 is not licensed for confirmatory execution.",
            next_discriminator="An independent custodian supplies scorer identity, digest and access-control attestation without revealing protected bytes.",
        ),
        "custody.one_shot_no_feedback_barrier": entry(
            "CANNOT_CHECK",
            binding=None,
            cause="Local code cannot self-attest independent custody, one accepted successor, one score event and no return channel.",
            residual="C2 is not licensed for confirmatory execution.",
            next_discriminator="An independent custodian binds an append-only one-shot receipt and verifies no candidate/adaptation feedback path.",
        ),
        "custody.protected_panel_freshness": entry(
            "CANNOT_CHECK",
            binding=None,
            cause="No protected panel identity or post-freeze freshness attestation was available.",
            residual="C2 is not licensed for confirmatory execution.",
            next_discriminator="An independent custodian freezes a fresh panel after protocol lock and reveals only the authorized closing receipt.",
        ),
        "identity.native_entrypoint_bytes": entry(
            "BOUND",
            binding={
                "cli_path": "host-daemon/src/cli/moss",
                "cli_sha256": "bd9aa0dbcbe953bafd24d60121ddceb868dae25f005f34cb5d448e0f671f0140",
                "daemon_entrypoint": "python -m src.main",
                "daemon_sha256": "cf335c86905efd86bf47de6d7fbad00fcb5a3a786b5a208e883ab427df101107",
                "compose_sha256": "ea2dec83a2e47930ac2c391d207e1b54e9a62b8a910b82cf9a5d46cd8143e783",
                "native_commands": ["status", "batches", "batch", "start", "stop", "restart", "apply", "flag", "catch-up"],
            },
            cause=None,
            residual="Exact official CLI/daemon/compose bytes are retained.",
            next_discriminator="Reverify these raw bytes immediately before any native image build.",
        ),
        "identity.source_license_bytes": entry(
            "BOUND",
            binding={
                "root_spdx": "Apache-2.0",
                "root_license_sha256": "3903e8b0fd6b4f6fc83f194c1e7b8525f1b40a284e4682ba1cec7e77eb765b63",
                "root_notice_sha256": "da9dce4d4fbd44a4feb37a54e27220788fbcc6887e4367d479b1bd402f63dd19",
                "vendored_openclaw_spdx": "MIT",
                "vendored_openclaw_license_sha256": "62316704df7426e5a79d2827ff8aca36e9abb3a73b8e68557030749ebefec667",
            },
            cause=None,
            residual="Exact source licence/notice bytes are retained; this does not close dependency, task, service or generated-artifact rights.",
            next_discriminator="Carry all applicable notices into any eventual runtime/source bundle.",
        ),
        "identity.source_repository_commit": entry(
            "BOUND",
            binding={
                "repository": "https://github.com/hkgai-official/Moss",
                "commit_sha": COMMIT,
                "tree_sha": TREE,
                "commit_date_utc": "2026-05-23T03:57:09Z",
                "archive_sha256": ARCHIVE_SHA,
            },
            cause=None,
            residual="The official paper-linked public source identity is byte-addressed.",
            next_discriminator="Fetch by commit and reverify the archive immediately before a build.",
        ),
        "inputs.candidate_visible_case_bytes": entry(
            "UNBOUND",
            binding=None,
            cause="No exact rights-cleared P5 failure batch/session packet is frozen. The authored parser fixture is schema-only and not a substantive P5 case.",
            residual="C2 is not licensed for execution.",
            next_discriminator="Author or license a minimal P5 batch satisfying P5_C2_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json without gold, protected outcomes or scorer feedback.",
        ),
        "model_provider.fallbacks": entry(
            "BOUND",
            binding={
                "fallbacks": [],
                "per_role_provider_override": "FORBIDDEN",
                "closed_behavior": "FAIL_WITH_NATIVE_TERMINAL; DO_NOT_SWITCH_MODEL_PROVIDER_OR_CODING_AGENT",
            },
            cause=None,
            residual="The P5 C2 fallback set is the closed empty list even though native MOSS supports mixed-provider overrides.",
            next_discriminator="Retain the empty list and override prohibition when the primary identities are selected.",
        ),
        "model_provider.primary": entry(
            "UNBOUND",
            binding=None,
            cause="MOSS requires both a chat/trial model endpoint and one authenticated coding-agent CLI. No exact model, provider, endpoint, CLI version, service revision, credential principal or per-role model is selected.",
            residual="C2 is not licensed for execution.",
            next_discriminator="Freeze one chat/trial model and one coding-agent CLI/model/provider with complete effective config and independent service terms.",
        ),
        "resources.calls_tokens_usd": entry(
            "UNBOUND",
            binding={
                "source_observation": "provider runners may report tokens/cost, but Codex reports cost_usd=None and DeepSeek may not report tokens; no source-wide hard ceiling exists"
            },
            cause="No provider-reconciled hard stop exists for aggregate calls, input/output tokens or USD across all MOSS roles and trial workers.",
            residual="C2 is not licensed for execution.",
            next_discriminator="After primary binding, enforce exact aggregate counters before every call, define overshoot semantics, and reconcile to provider receipts.",
        ),
        "resources.retry_network": entry(
            "UNBOUND",
            binding={
                "frozen_policy": {"fallbacks": [], "network_default": "DENY_EXCEPT_EXACT_BOUND_ENDPOINTS"},
                "source_depth": "shallow",
            },
            cause="The primary endpoints, DNS/TLS identities and task-fetch policy are unbound; released dynamic trial containers use bridge networking and no final egress allowlist is enforced.",
            residual="C2 is not licensed for execution.",
            next_discriminator="Bind exact endpoints or local offline services and enforce a deny-by-default egress policy for gateway, daemon, coding agents and every dynamic worker.",
        ),
        "resources.wallclock": entry(
            "BOUND",
            binding={
                "enforcer": "p5_c2_fail_closed_runner.py",
                "enforcer_sha256": runner_hash,
                "whole_c2_run_seconds": 21600,
                "per_case_seconds": 21600,
                "termination_grace_seconds": 120,
                "timeout_terminal": "TIMEOUT/exit 124",
            },
            cause=None,
            residual="A prospective process-group wallclock is byte-frozen; Docker/container isolation and cleanup remain separately unbound.",
            next_discriminator="Verify TERM/KILL and container cleanup on the eventual disposable runtime before custody execution.",
        ),
        "rights.container_and_generated_artifacts": entry(
            "UNBOUND",
            binding={
                "base_image": "node:22-bookworm@sha256:cd7bcd2e7a1e6f72052feb023c7f6b722205d3fcab7bbcbd2d1bfdab10b1e935"
            },
            cause="The base image is pinned, but no complete built-image SBOM/licence bundle or authority for session, transcript, diff, image and evolution-state retention/publication is closed.",
            residual="C2 is not licensed for execution or artifact redistribution.",
            next_discriminator="Build the complete image, capture SBOM/licences, and obtain explicit generated-artifact retention/disclosure authority.",
        ),
        "rights.model_provider_and_services": entry(
            "UNBOUND",
            binding=None,
            cause="No model/coding-agent provider is selected and no study-use, data-retention, region or publication terms are captured.",
            residual="C2 is not licensed for execution.",
            next_discriminator="Bind terms and data policy for both chat/trial and coding-agent services before credentials enter the runtime.",
        ),
        "rights.task_and_benchmark_content": entry(
            "UNBOUND",
            binding={
                "authoritative_tree_benchmark_paths": 0,
                "missing_expected_path": "benchmark/claw-eval/runner/benchmark.py",
            },
            cause="The pinned source trial runner requires benchmark/claw-eval, but the complete Git tree contains zero benchmark paths; no alternative task/benchmark packet or rights file is released in this commit.",
            residual="The native replay/evaluation path and all P5 task-content reuse rights are CANNOT_CHECK.",
            next_discriminator="Obtain an upstream content-addressed release of the missing benchmark/runtime with its licence, or bind an authored P5-native evaluator as an explicitly named successor rather than silently patching the comparator.",
        ),
        "runtime.compute": entry(
            "UNBOUND",
            binding={
                "prospective": {"gpus": 0, "parallelism": 1, "ram_gib": 16, "vcpus": 8, "pids_limit": 2048}
            },
            cause="Values are proposed but not enforced across the gateway, host daemon, coding-agent subprocesses, Docker build and dynamic trial workers; native worker docker run lacks CPU/RAM/PID limit flags.",
            residual="C2 is not licensed for matched execution.",
            next_discriminator="Enforce one cgroup/VM-wide cap and verify every dynamic child stays inside it.",
        ),
        "runtime.container_or_environment": entry(
            "UNBOUND",
            binding={
                "base_image": "node:22-bookworm@sha256:cd7bcd2e7a1e6f72052feb023c7f6b722205d3fcab7bbcbd2d1bfdab10b1e935",
                "source_archive_sha256": ARCHIVE_SHA,
            },
            cause="No complete arm64/amd64 derived MOSS/OpenClaw image, host-daemon environment, Docker daemon identity or runtime SBOM was built. The local Docker client has no reachable daemon and pnpm 10.23.0 is absent.",
            residual="Only source and lock identities are frozen; native runtime execution is CANNOT_CHECK.",
            next_discriminator="On a rights-cleared disposable Linux executor, install pnpm 10.23.0, build exact source from both locks, and capture image, host environment and SBOM digests.",
        ),
        "runtime.dependency_lock": entry(
            "BOUND",
            binding={
                "host": {
                    "path": "MOSS_HOST_DEPENDENCY_LOCK_V4.uv.lock",
                    "sha256": host_lock_hash,
                    "package_entries": 11,
                    "python_request": ">=3.11",
                    "resolver": "uv 0.11.1",
                },
                "openclaw": {
                    "path": "MOSS_OPENCLAW_DEPENDENCY_LOCK_V4.pnpm-lock.yaml",
                    "sha256": node_lock_hash,
                    "package_entries": 1196,
                    "package_manager": "pnpm@10.23.0",
                    "node_engine": ">=22.12.0",
                    "identical_to_upstream_lock": True,
                },
            },
            cause=None,
            residual="Both released dependency resolutions are byte-frozen; build success, platform wheels, licences and missing benchmark dependencies remain separate blockers.",
            next_discriminator="Materialize both locks on the selected Linux platform and retain fetched package/archive digests plus licence inventory.",
        ),
        "runtime.task_environment": entry(
            "CANNOT_CHECK",
            binding={
                "released_trial_runner_sha256": "40e60a8e3393caf1a4efdf6b433873883f07049038a95364b70f7f7d2c7524d7",
                "required_but_absent": [
                    "benchmark/claw-eval/runner/benchmark.py",
                    "benchmark/claw-eval/src",
                    "benchmark/claw-eval manifests/tasks/results layout",
                ],
            },
            cause="The native runtime hard-codes a benchmark tree that is absent from the authoritative commit; no exact P5 session/batch, trial service, setup bytes or generated task manifest is bound.",
            residual="A source-native evolution/replay smoke cannot reach the trial stage without unversioned external bytes or source modification.",
            next_discriminator="Acquire an authoritative content-addressed benchmark companion release, or preregister and name a P5-native successor runtime with its own semantics and rights.",
        ),
    }

    bound = [path for path in required if fields[path]["state"] == "BOUND"]
    blocking = [path for path in required if fields[path]["state"] != "BOUND"]
    registry = {
        "schema_version": "orion.p5.c2.field-registry.v4",
        "registry_id": "P5.C2.MOSS.FIELD.REGISTRY.V4",
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
            "wallclock_seconds": {"per_case": 21600, "whole_c2_run": 21600, "termination_grace": 120},
            "runtime_launcher": None,
        },
        "terminal": "C2_PARTIAL_BINDING__FOURTEEN_REQUIRED_FIELDS_NOT_BOUND__EXECUTION_REFUSED",
    }
    write_json("P5_C2_V4_FIELD_REGISTRY.json", registry)

    source_files = [
        ("LICENSE", "3903e8b0fd6b4f6fc83f194c1e7b8525f1b40a284e4682ba1cec7e77eb765b63"),
        ("NOTICE", "da9dce4d4fbd44a4feb37a54e27220788fbcc6887e4367d479b1bd402f63dd19"),
        ("README.md", "1b081f3eab744bd67c020343698ca567cf28dfd199310772232a7c83bf89ca62"),
        (".env.example", "89c070dd14f4ca1cdda8ee6825852eb878ef2b42a724a843a024a133f93d72db"),
        ("docker-compose.yml", "ea2dec83a2e47930ac2c391d207e1b54e9a62b8a910b82cf9a5d46cd8143e783"),
        ("scripts/setup.sh", "bb591cbbca65b46941a8f2949f53bf6e5a5083d36f24c10329935bbfe14707a8"),
        ("host-daemon/pyproject.toml", "66ac3d9d64a434c3f39f3b2d06b277f3f6c4e7a42851121f9d76e2d92c2ceebf"),
        ("host-daemon/src/cli/moss", "bd9aa0dbcbe953bafd24d60121ddceb868dae25f005f34cb5d448e0f671f0140"),
        ("host-daemon/src/main.py", "cf335c86905efd86bf47de6d7fbad00fcb5a3a786b5a208e883ab427df101107"),
        ("host-daemon/src/ops/trial_runner.py", "40e60a8e3393caf1a4efdf6b433873883f07049038a95364b70f7f7d2c7524d7"),
        ("host-daemon/src/ops/docker_rpc.py", "d9f321e0bc9182e90ba81597c6893029e8e12e4dc19756826a67e71687c00d08"),
        ("openclaw/LICENSE", "62316704df7426e5a79d2827ff8aca36e9abb3a73b8e68557030749ebefec667"),
        ("openclaw/package.json", "83087d14b19f93b1e0a3f79ea09c7aeba07679c95a0d160941fcc4530d98b7ec"),
        ("openclaw/pnpm-lock.yaml", node_lock_hash),
        ("openclaw/Dockerfile", "3543bf34913a30e1a9fc51bcf6cfe95916f8beabd92f4d0a6e57e5b022d12dc9"),
        ("openclaw/src/evolution/state.ts", "431d796f36579ba4eadf56992b3660a5eee27f1b06b15ea3a373a5027eb1b428"),
        ("openclaw/src/evolution/verdict.ts", "356b0b21d0dda17cf71fdb7a8c7cc8cd2f99d69bf4c13421cd82b97e5ffaae78"),
        ("openclaw/src/evolution/loop.ts", "96e51ff3e187e085e886314aa3723c72858c04b209f9fb2e32c1e99206d8f837"),
    ]
    write_json(
        "P5_C2_V4_SOURCE_RIGHTS_MANIFEST.json",
        {
            "schema_version": "orion.p5.c2.source-rights-manifest.v4",
            "authority": "PUBLIC_SOURCE_IDENTITY_AND_RIGHTS_INVENTORY_ONLY__NOT_LEGAL_ADVICE",
            "frozen_at_utc": FROZEN_AT,
            "source": {
                "repository": "https://github.com/hkgai-official/Moss",
                "paper": "arXiv:2605.22794v2",
                "commit_sha": COMMIT,
                "tree_sha": TREE,
                "archive_sha256": ARCHIVE_SHA,
                "archive_bytes_retained_in_lane": False,
            },
            "licence_layers": [
                {"scope": "MOSS root additions", "spdx": "Apache-2.0", "license_sha256": source_files[0][1], "notice_sha256": source_files[1][1]},
                {"scope": "vendored openclaw", "spdx": "MIT", "license_sha256": "62316704df7426e5a79d2827ff8aca36e9abb3a73b8e68557030749ebefec667"},
                {"scope": "vendored a2ui and other third parties", "spdx": "MIXED", "status": "INDIVIDUAL_NOTICES_RETAINED_UPSTREAM__TRANSITIVE_CLOSURE_NOT_ESTABLISHED"},
            ],
            "hashed_authoritative_files": [{"path": path, "sha256": digest} for path, digest in source_files],
            "authoritative_tree_audit": {
                "checked_utc": FROZEN_AT,
                "github_tree_truncated": False,
                "benchmark_prefixed_paths": 0,
                "root_paths": [".env.example", ".gitignore", "LICENSE", "NOTICE", "README.md", "docker-compose.yml", "host-daemon", "openclaw", "scripts", "tec_report.pdf"],
                "native_source_requires": ["benchmark/claw-eval/runner/benchmark.py", "benchmark/claw-eval/src"],
                "terminal": "RELEASED_SOURCE_TRIAL_RUNTIME_INCOMPLETE__CANNOT_CHECK",
            },
            "rights_closed": ["public source inspection", "root Apache-2.0 source layer", "vendored OpenClaw MIT source layer"],
            "rights_not_closed": ["missing benchmark/task bytes", "transitive dependency licence/SBOM", "container distribution", "model and coding-agent services", "session/failure content", "generated transcripts/diffs/images", "protected scorer/panel"],
        },
    )

    write_json(
        "P5_C2_V4_RESOURCE_REGISTRY.json",
        {
            "schema_version": "orion.p5.c2.resource-registry.v4",
            "arm_id": ARM_ID,
            "frozen_at_utc": FROZEN_AT,
            "bound": {
                "wallclock_seconds": {"per_case": 21600, "whole_c2_run": 21600, "termination_grace": 120},
                "fallbacks": [],
                "dependency_locks": registry["fields"]["runtime.dependency_lock"]["binding"],
            },
            "source_defaults_not_adopted_as_matched_p5_values": {
                "depth_tier": "shallow has max_iter=3, max_plan_rounds=1, max_code_retries=0, n_trials_per_task=2",
                "role_timeouts_seconds": {"locator": 1800, "planner": 1800, "plan_reviewer": 1500, "implementer": 3600, "code_reviewer": 1800, "task_evaluator": 1500, "reviewer": 1200},
                "docker_build": 600,
                "build_smoke": 240,
                "swap_window": 90,
            },
            "proposed_but_unbound": {
                "compute": {"vcpus": 8, "ram_gib": 16, "gpus": 0, "parallelism": 1, "pids_limit": 2048},
                "network": "deny except exact bound endpoints",
                "calls_tokens_usd": None,
            },
            "blocking_observations": [
                "No aggregate call/token/USD hard-stop is released.",
                "Dynamic trial docker run has no CPU/RAM/PID flags.",
                "Bridge-networked gateway/workers have no final endpoint allowlist.",
                "No complete derived image or host daemon environment is materialized.",
                "The required benchmark/claw-eval tree is absent.",
            ],
        },
    )

    write_json(
        "P5_C2_V4_NATIVE_OUTPUT_SCHEMA.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "orion.p5.c2.moss-native-terminal.v4",
            "type": "object",
            "additionalProperties": False,
            "required": ["schema_version", "arm_id", "source", "native_terminal", "native_retention", "adapter_disposition", "outcome_boundary"],
            "properties": {
                "schema_version": {"const": "orion.p5.c2.moss-native-terminal.v4"},
                "arm_id": {"const": ARM_ID},
                "source": {"type": "object"},
                "native_terminal": {
                    "type": "object",
                    "required": ["arm_id", "status", "native_code", "payload_sha256"],
                    "properties": {
                        "arm_id": {"const": ARM_ID},
                        "status": {"enum": ["COMPLETE_SUCCESS", "ERROR", "TIMEOUT", "ABSTAIN", "EMPTY", "PARTIAL", "INVALID"]},
                        "native_code": {"enum": ["initialized", "in_progress", "swap_pending", "converged", "rolled_back", "failed", "aborted_max_iter", "aborted_streak"]},
                        "payload_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    },
                },
                "native_retention": {"type": "object"},
                "adapter_disposition": {
                    "type": "object",
                    "required": ["output", "raw_native_singleton_licensed"],
                    "properties": {"output": {"const": "UNRESOLVED"}, "raw_native_singleton_licensed": {"const": False}},
                },
                "outcome_boundary": {"type": "object"},
            },
        },
    )

    write_json(
        "P5_C2_V4_NATIVE_TERMINAL_RULES.json",
        {
            "schema_version": "orion.p5.c2.native-terminal-rules.v4",
            "source_schema_version": 6,
            "mapping": {
                "converged + latest verdict converged + commitHash + imageTag": "COMPLETE_SUCCESS",
                "initialized | in_progress | swap_pending": "PARTIAL",
                "aborted_max_iter | aborted_streak": "ABSTAIN",
                "failed | rolled_back": "ERROR",
                "converged missing its required candidate identity": "INVALID",
            },
            "retention": ["exact manifest status", "exact latest closed-set verdict", "current iteration/stage", "hashes rather than raw candidate identifiers"],
            "score_policy": "native development scores may occur in the manifest but are not reproduced or consulted by terminal mapping",
            "external_protected_gold_policy": "fail closed on any protected/gold/scorer key",
            "adapter_output": "always UNRESOLVED; zero raw native singleton licences",
        },
    )

    write_json(
        "P5_C2_V4_WRITE_SURFACE_SCHEMA.json",
        {
            "schema_version": "orion.p5.c2.write-surface.v4",
            "arm_id": ARM_ID,
            "required_isolation": {
                "source_seed": "read-only outside a disposable executor; copied to an ephemeral inner Git repository",
                "allowed_mutation_roots": ["ephemeral openclaw candidate tree", "ephemeral MOSS_DATA_DIR", "dedicated ephemeral Docker data root", "sole receipt output directory"],
                "forbidden_roots": ["shared checkout", "host Docker daemon", "host home/config/keychains", "protected panel", "external scorer", "other arms", "network endpoints outside final allowlist"],
                "reset": "destroy executor, Docker data root, networks, images, containers and mutable source copy after every attempt",
                "audit": "complete before/after digest of every allowed root and proof no forbidden mount or write exists",
            },
            "released_source_gap": "native MOSS currently requires host Docker and source mutation; no disposable executor binding is released",
            "field_state": "CANNOT_CHECK",
        },
    )

    write_json(
        "P5_C2_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json",
        {
            "schema_version": "orion.p5.c2.candidate-visible-case-requirements.v4",
            "required": [
                "authored or explicitly licensed session/failure bytes",
                "content hash and provenance for every chunk",
                "host-issued V3 minimal-class certificate before candidate action",
                "closed candidate-visible public-development evaluator/task definition",
                "no protected/gold labels, patches, outcomes, scorer responses or hidden-panel identifiers",
                "no outcome-selected source or case inclusion",
                "complete expected write-root declaration without prescribing the answer",
            ],
            "forbidden": ["protected score", "gold patch", "post-selection by outcome", "same-case protected feedback", "external scorer access", "unlicensed conversation/session content"],
            "smoke_fixture_is_substantive_p5_case": False,
            "current_state": "UNBOUND",
        },
    )

    write_json(
        "P5_C2_V4_CUSTODY_HANDOFF_SCHEMA.json",
        {
            "schema_version": "orion.p5.c2.custody-handoff.v4",
            "required_attestations": [
                "candidate receives only byte-frozen visible packet and public-development services",
                "one frozen successor commit/image accepted before protected scoring",
                "candidate and adaptation custody close before transfer",
                "independent scorer identity and code digest",
                "fresh protected panel frozen after protocol lock",
                "one scoring event with append-only receipt",
                "no protected score/outcome/diagnostic returns to candidate or adaptation custody",
            ],
            "local_self_attestation_allowed": False,
            "current_state": "CANNOT_CHECK",
        },
    )

    protocol = {
        "schema_version": "orion.p5.c2.moss-execution-binding-protocol.v4",
        "protocol_id": "P5.C2.MOSS.EXECUTION.BINDING.V4",
        "arm_id": ARM_ID,
        "authority": "PUBLIC_SOURCE_IDENTITY_AND_OUTCOME_BLIND_PREFLIGHT_ONLY",
        "frozen_at_utc": FROZEN_AT,
        "source_identity": {"repository": "https://github.com/hkgai-official/Moss", "commit_sha": COMMIT, "tree_sha": TREE, "archive_sha256": ARCHIVE_SHA},
        "frozen_components": {
            "native_parser": {"path": "p5_c2_native_parser.py", "sha256": parser_hash},
            "fail_closed_gate": {"path": "p5_c2_fail_closed_runner.py", "sha256": runner_hash},
            "dependency_locks": registry["fields"]["runtime.dependency_lock"]["binding"],
            "fallbacks": [],
            "wallclock_seconds": {"per_case": 21600, "whole_c2_run": 21600, "termination_grace": 120},
        },
        "execution_order": [
            "independent custodian binds every non-BOUND field without protected outcome access",
            "validator requires 21/21 BOUND and a content-addressed disposable runtime launcher",
            "candidate receives only the frozen rights-cleared case and public-development evaluator",
            "MOSS executes in a dedicated isolated Docker/VM boundary under one process-group watchdog",
            "native parser retains MOSS terminal and emits UNRESOLVED without class inference",
            "V3 certificate/action/fibre validation runs separately",
            "one frozen successor enters external protected custody once with no feedback",
        ],
        "predecessors": {
            "v2_comparator_panel_sha256s": "94ef91058dd6c453296d557129e080ff7918f8d7e09716a1d69ba57d77b5bad1",
            "v2_identity_ledger": "f6419103024de98d0cf44ee2681399007001eb79c9b830312d501b6045a60583",
            "v2_terminal_adapters_sha256s": "bd69cfcb3dda70d4d08c84b6ce35a0cc7e77865627dd48278e07b3f8cd158850",
            "v2_resource_ledger": "1e3a450b1561cb2d3a1d556c77ef1688f8894fb2331fcfa334de87a18bd11dfe",
            "v3_adapter_refinement_sha256s": "50d1ff72f63093216761c4b47d3ced6de82915967578f33f3296bf41e4f73c4a",
            "v3_blocker_ledger": "265e3ba834ab7e24c471965f8064542e3f61f74414e0646b22a90fe9ae95c789",
            "c1_swe_v4_sha256s": "2398e75169612fb777b487c795caa5402b47f27c1039f7dcfd3dcc3789020df4",
        },
        "nonclaims": [
            "No MOSS evolution, model, coding agent, benchmark, replay, protected scorer or comparator was executed.",
            "CLI help loading and parser conformance are not native evolution success.",
            "The released benchmark/runtime gap is not repaired by inventing or substituting bytes.",
            "No performance, preservation, transfer, harm or superiority inference is available.",
        ],
    }
    write_json("P5_C2_V4_EXECUTION_BINDING_PROTOCOL.json", protocol)

    smoke = {
        "schema_version": "orion.p5.c2.outcome-blind-smoke-receipt.v4",
        "frozen_at_utc": FROZEN_AT,
        "authority": "OUTCOME_BLIND_INTERFACE_SMOKE_ONLY",
        "source": {"commit_sha": COMMIT, "cli_sha256": "bd9aa0dbcbe953bafd24d60121ddceb868dae25f005f34cb5d448e0f671f0140"},
        "local_environment": {
            "platform": "Darwin arm64",
            "python_exact": "3.14.6 arm64",
            "node": "26.0.0",
            "required_pnpm": "10.23.0",
            "pnpm_present": False,
            "docker_client": "29.3.0 arm64",
            "docker_daemon_reachable": False,
            "available_disk_gib_approx": 7.1,
        },
        "native_cli_load": {
            "command_semantics": "exact pinned host-daemon/src/cli/moss --help",
            "exit_code": 0,
            "stdout_bytes": 232,
            "stdout_sha256": "17c74822d9cbd18d19020ea615d1cdbfb85459b3254bb4807e6fad51761c064e",
            "stderr_bytes": 0,
            "pass": True,
        },
        "native_status_without_gateway": {
            "command_semantics": "exact pinned CLI evo status --json against closed localhost port",
            "exit_code": 1,
            "stdout_bytes": 0,
            "stderr_bytes": 102,
            "stderr_sha256": "d6b52fb257b18311a97943da00ae29279a1e1e58d41b61398b0785ddf5fd5cc0",
            "terminal": "NATIVE_GATEWAY_UNREACHABLE_ERROR_PRESERVED",
        },
        "parser_conformance": {
            "authored_outcome_free_manifest_retained": False,
            "input_bytes": 694,
            "input_sha256": "0a244f020d7ce6b0d4afe6bfe29eae185141d686d3d733e8406ab8b6260faf3f",
            "parser_output_sha256": "cf538aec6f7baf36721cd43e6f8b1266a9ce1735f246b197b1e2f4dd1a3c9d4e",
            "exit_code": 0,
            "native_status": "PARTIAL",
            "adapter_output": "UNRESOLVED",
            "protected_key_refusal_exit_code": 2,
            "protected_key_refusal_stderr_sha256": "dcfbf6e05ec83772cc7530fe56748f3de8f5604bf28b3ae3538cefbd70d66143",
        },
        "full_native_smoke": {
            "state": "CANNOT_CHECK",
            "causes": [
                "authoritative commit omits required benchmark/claw-eval tree",
                "Docker daemon unreachable",
                "pnpm 10.23.0 unavailable",
                "primary chat/trial model and coding-agent CLI/service identities unbound",
                "no substantive rights-cleared P5 case",
            ],
            "next_discriminator": "Supply the missing authoritative benchmark companion release and execute only on a disposable rights-cleared Linux runtime after all 21 fields bind.",
        },
        "raw_or_large_payloads_retained": False,
    }
    write_json("P5_C2_V4_SMOKE_RECEIPT.json", smoke)

    negatives = [
        {
            "id": "P5.C2.V4.RELEASED.RUNTIME.GAP",
            "cause": "Pinned native trial code requires benchmark/claw-eval, while the complete official Git tree contains zero benchmark paths.",
            "residual": "Native replay/evaluation and exact task rights remain CANNOT_CHECK; source identity alone is not execution readiness.",
            "next_discriminator": "Obtain an upstream content-addressed companion release with licence, or preregister a separately named P5-native successor runtime.",
            "positive_progress": "The blocker is narrowed to exact absent paths and an authoritative tree receipt; silent substitution is prohibited.",
        },
        {
            "id": "P5.C2.V4.NATIVE.PARSER",
            "cause": "V3 had no arm-native parser and native replay improvement is a mixed fibre.",
            "residual": "The parser licenses zero raw singletons and cannot establish scientific responsibility.",
            "next_discriminator": "Combine the frozen parser with the separate V3 certificate/action/fibre validator after a real candidate exists.",
            "positive_progress": "Exact MOSS schema-v6 terminals are now preserved and external protected/gold keys fail closed.",
        },
        {
            "id": "P5.C2.V4.DOCKER.ISOLATION",
            "cause": "MOSS mutates source and controls Docker; released compose/dynamic worker commands do not impose a complete disposable resource/write boundary.",
            "residual": "The fail-closed gate and wallclock do not constitute arm-native isolation.",
            "next_discriminator": "Bind and destroy a dedicated rootless-Docker VM per attempt, with complete mount/network/mutation evidence.",
            "positive_progress": "Accidental execution is refused and the required isolation theorem is byte-specified.",
        },
        {
            "id": "P5.C2.V4.MODEL.RESOURCE.ACCOUNTING",
            "cause": "Two model surfaces and provider-specific incomplete usage fields prevent a provider-independent calls/tokens/USD hard stop.",
            "residual": "Primary, retry/network and aggregate resource fields remain UNBOUND.",
            "next_discriminator": "Choose exact services, enforce pre-call aggregate counters, reconcile provider receipts and close all egress.",
            "positive_progress": "Fallbacks are frozen empty and a 21,600-second whole-run watchdog is bound.",
        },
        {
            "id": "P5.C2.V4.LOCAL.NATIVE.SMOKE",
            "cause": "The local executor has no Docker daemon or pnpm 10.23.0; the first login-shell probe also resolved unsupported Python 3.9.6.",
            "residual": "Only exact-interpreter CLI loading and native gateway-error retention were observed, not an evolution run.",
            "next_discriminator": "Use Python >=3.11, pnpm 10.23.0 and a disposable Linux Docker runtime after the released benchmark gap is resolved.",
            "positive_progress": "Selecting the explicit Python 3.14.6 interpreter produced a clean native CLI help exit 0; environment-cause and correction are recorded.",
        },
        {
            "id": "P5.C2.V4.CUSTODY.RIGHTS",
            "cause": "Task/session, service, generated-artifact, independent scorer and protected freshness authority are not available locally.",
            "residual": "No confirmatory execution or top-tier empirical claim is licensed.",
            "next_discriminator": "Independent custody and rights owners sign content-addressed attestations before any protected scoring.",
            "positive_progress": "Root Apache-2.0, root NOTICE and vendored OpenClaw MIT bytes are separately bound rather than conflated with runtime rights.",
        },
    ]
    write_json(
        "P5_C2_V4_NEGATIVE_LEDGER.json",
        {"schema_version": "orion.p5.c2.negative-ledger.v4", "arm_id": ARM_ID, "entries": negatives},
    )
    lines = [
        "# P5 C2 V4 recursive negative-result ledger",
        "",
        "| ID | Cause | Positive progress | Residual | Next discriminator |",
        "|---|---|---|---|---|",
    ]
    for item in negatives:
        lines.append(f"| `{item['id']}` | {item['cause']} | {item['positive_progress']} | {item['residual']} | {item['next_discriminator']} |")
    (HERE / "P5_C2_V4_NEGATIVE_LEDGER.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = {
        "schema_version": "orion.p5.c2.moss-execution-binding-result.v4",
        "protocol_id": "P5.C2.MOSS.EXECUTION.BINDING.V4",
        "arm_id": ARM_ID,
        "authority": "PUBLIC_SOURCE_IDENTITY_AND_OUTCOME_BLIND_PREFLIGHT_ONLY",
        "terminal": "P5_C2_V4_MOSS_NATIVE_PARSER_DEPENDENCY_LOCKS_FALLBACK_AND_WALLCLOCK_BOUND__FOURTEEN_C2_FIELDS_BLOCKING__RELEASED_BENCHMARK_RUNTIME_ABSENT__ZERO_OF_SIX_PANEL_READY__PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK",
        "v4_repairs": {
            "retained_bound_identity_fields": ["identity.native_entrypoint_bytes", "identity.source_license_bytes", "identity.source_repository_commit"],
            "newly_bound_v3_fields": ["adapter.native_parser_binding", "model_provider.fallbacks", "resources.wallclock", "runtime.dependency_lock"],
            "c2_bound_fields": len(bound),
            "c2_blocking_fields": len(blocking),
            "v3_to_v4_blocker_delta": -4,
        },
        "execution": {"c2_executed": False, "c2_execution_ready": False, "full_native_smoke": "CANNOT_CHECK", "panel_confirmatory_ready_arms": 0, "panel_required_arms": 6},
        "material_discovery": {"authoritative_tree_benchmark_paths": 0, "native_required_path": "benchmark/claw-eval/runner/benchmark.py", "effect": "runtime.task_environment and task/benchmark rights remain CANNOT_CHECK"},
        "preserved_boundaries": {"v3_synthetic_cases": 231, "v3_supported_singleton_case_records": 40, "v3_unresolved_case_records": 191, "raw_native_singleton_licences": 0, "scienceclaw_supported_singletons": 0},
        "preserved_claims": {"H1": "CANNOT_CHECK", "H2": "CANNOT_CHECK", "H3": "CANNOT_CHECK", "H4": "CANNOT_CHECK", "performance": "CANNOT_CHECK", "preservation": "CANNOT_CHECK", "fresh_transfer": "CANNOT_CHECK", "harm": "CANNOT_CHECK", "superiority": "CANNOT_CHECK", "top_tier_publication_readiness": "NOT_ESTABLISHED"},
        "next_discriminator": "Obtain an authoritative rights-cleared benchmark companion release, then bind the remaining 14 fields on a disposable isolated Linux executor; C2 must still wait for 6/6 matched panel readiness.",
    }
    write_json("P5_C2_V4_RESULT.json", result)

    report = f"""# P5 C2 MOSS execution-binding V4

## Terminal

`{result['terminal']}`

This is an outcome-blind source/runtime preflight repair, not a comparator
result. No MOSS evolution, model, coding agent, benchmark, replay, protected
scorer, gold value, performance table, or protected datum was executed or
opened. The only native source execution was the exact CLI load/help surface
and its expected gateway-unreachable error path.

## Exact readiness delta

V3 retained three source-identity fields and blocked 18/21 fields for C2. V4
binds four more: the native schema-v6 terminal parser, a closed empty fallback
set, a 21,600-second whole-run watchdog, and both dependency locks. C2 is now
**7/21 BOUND** and **14/21 blocking** (delta: **-4 blockers**). Six-arm
confirmatory readiness remains **0/6**.

| Newly bound field | Evidence |
|---|---|
| `adapter.native_parser_binding` | Hashed schema-v6 parser; exact MOSS status/latest verdict retained; candidate identifiers hashed; protected/gold keys refused; raw singleton licences 0 |
| `model_provider.fallbacks` | Closed empty list; per-role provider overrides forbidden for P5 C2 |
| `resources.wallclock` | Process-group watchdog: 21,600 s plus 120 s TERM/KILL grace |
| `runtime.dependency_lock` | Host uv lock: 11 entries, `{host_lock_hash}`; exact upstream OpenClaw pnpm lock: 1,196 entries, `{node_lock_hash}` |

## Material authoritative-source result

The official paper-linked commit `{COMMIT}` is valid and its complete Git tree
is `{TREE}`. The release archive hash is `{ARCHIVE_SHA}`. However, native
`host-daemon/src/ops/trial_runner.py` requires
`benchmark/claw-eval/runner/benchmark.py`, `benchmark/claw-eval/src`, manifests
and results paths. The complete non-truncated authoritative Git tree contains
**zero** `benchmark/` paths. The root README/setup does not fetch that tree.

Therefore the released native replay/evaluation runtime is incomplete at this
commit. V4 does not repair this by fabricating a benchmark, borrowing
unversioned bytes, or silently substituting a different evaluator. Exact task
runtime and task/benchmark rights remain `CANNOT_CHECK`. A P5-native evaluator
would be a separately preregistered successor method, not the released MOSS arm.

## Outcome-blind smoke boundary

- Exact CLI with Python 3.14.6: help/load exit **0**.
- Exact `evo status --json` against a closed localhost port: exit **1**, native
  gateway-unreachable error preserved.
- Authored outcome-free schema fixture: parser exit **0**, native `PARTIAL`,
  adapter `UNRESOLVED`; fixture not retained.
- Injected `protected_score` key: parser refusal exit **2**.
- Full MOSS smoke: **CANNOT_CHECK** because the authoritative benchmark tree is
  absent, Docker daemon is unreachable, pnpm 10.23.0 is absent, primary model
  and coding-agent services are unbound, and no substantive rights-cleared P5
  case exists.

The local CLI evidence is interface conformance only. It is not evolution
success, scientific readiness, or performance evidence.

## Rights boundary

Exact root Apache-2.0 licence (`3903e8...`), root NOTICE (`da9dce...`) and
vendored OpenClaw MIT licence (`623167...`) are bound. These source rights do
not close the missing benchmark, transitive dependencies, built container,
model/coding-agent services, session content, generated transcripts/diffs/images,
or protected scorer/panel. Those remain distinct blockers.

## Fourteen remaining blockers

1. disposable native write/isolation boundary;
2. exact P5 candidate-visible case bytes;
3. primary chat/trial model plus coding-agent CLI/model/provider;
4. aggregate calls/tokens/USD hard stops;
5. final retry and network allowlist;
6. complete runtime compute enforcement;
7. complete derived container/host environment;
8. exact task/runtime environment, including the missing benchmark tree;
9. task/benchmark/session rights;
10. model/provider/service rights;
11. container/generated-artifact rights;
12. independent external protected scorer;
13. independent one-shot no-feedback barrier; and
14. protected-panel identity/freshness.

The fail-closed runner refuses execution while any field remains non-BOUND.
It does not pretend that process-group timeout isolates a Docker daemon.

## Preserved scientific boundary

- V3 stays unchanged: 231 fictional cases, 40 supported singleton case records
  in 20 constant fibres, 191 `UNRESOLVED`, and zero raw native singleton
  licences.
- MOSS native convergence/replay improvement is not a scientific responsibility
  class and maps to `UNRESOLVED` absent the separate V3 certificate/action proof.
- Six-arm performance readiness remains 0/6.
- H1--H4, preservation, fresh transfer, harm, performance and superiority all
  remain `CANNOT_CHECK`; top-tier publication readiness is not established.

## Next discriminator

Obtain an upstream content-addressed and rights-cleared companion release for
`benchmark/claw-eval` (or explicitly preregister a different P5-native successor
runtime). Then bind one P5 case, both primary model surfaces, aggregate resource
hard stops, deny-by-default egress, a disposable rootless-Docker executor,
complete runtime/SBOM rights, and three independent custody attestations. C2
still cannot execute confirmatorily until all six arms satisfy the matched panel.
"""
    (HERE / "SCIENTIFIC_REPORT_V4.md").write_text(report, encoding="utf-8")

    (HERE / "README.md").write_text(
        "# P5 MOSS C2 execution-binding V4\n\n"
        "Self-contained outcome-blind preflight for the official MOSS direct-self-edit arm. "
        "Start with `SCIENTIFIC_REPORT_V4.md`, `P5_C2_V4_RESULT.json`, and "
        "`P5_C2_V4_FIELD_REGISTRY.json`. No comparator/model/protected outcome was run. "
        "The package binds 7/21 C2 fields, leaves 14 blocking, and records the released "
        "source's absent `benchmark/claw-eval` runtime exactly as CANNOT_CHECK.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
