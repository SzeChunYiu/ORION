#!/usr/bin/env python3
"""Build the outcome-blind P5 C5 Double Ratchet V4 binding packet.

The builder reads only public source/code/licence bytes and Git tree metadata.
It never opens a benchmark split, task payload, native result, metric database,
protected panel, score, or manuscript.  The only metric-shaped objects exercised
are authored in-memory parser smoke fixtures labelled non-performance.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
UPSTREAM = Path(
    "/Users/billy/Documents/Codex/2026-08-23/can-x20/work/upstream/"
    "double-ratchet-0f14e910"
)
FROZEN_AT = "2026-08-23T18:35:39Z"
ARM_ID = "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY"
PROTOCOL_ID = "P5.C5.DOUBLE_RATCHET.METRIC_ONLY.EXECUTION.BINDING.V4"
COMMIT = "0f14e910d361196422d9b938f45280919952d4fd"
TREE = "3ca13a51b4fb6ff77013d8886023ee852cbf373e"
REPOSITORY = "https://github.com/amazon-science/Self-Evolving-Agents-Double-Ratchet"
ARCHIVE_SHA256 = "9426222eefc25878f7e7d1ecd1ff9824c894bc358cb8d5f31ee3c8d4a8db9640"
TERMINAL = (
    "P5_C5_V4_DOUBLE_RATCHET_SOURCE_PARSER_ISOLATION_FALLBACK_WALLCLOCK_"
    "COMPUTE_AND_DEPENDENCY_LOCK_BOUND__TWELVE_C5_FIELDS_BLOCKING__"
    "OFFICIAL_RUNNER_REGENERATES_SOLVER_OUTPUTS_AND_REPORTS_DEVELOPMENT_"
    "LOCKED_EACH_ROUND__ZERO_OF_SIX_PANEL_READY__PERFORMANCE_AND_"
    "SUPERIORITY_CANNOT_CHECK"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def write_json(name: str, value: Any) -> None:
    (HERE / name).write_text(canonical(value), encoding="utf-8")


def write_text(name: str, value: str) -> None:
    (HERE / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def git(*args: str, binary: bool = False) -> str | bytes:
    return subprocess.check_output(
        ["git", "-C", str(UPSTREAM), *args],
        text=not binary,
    )


def source_metadata() -> dict[str, Any]:
    head = str(git("rev-parse", "HEAD")).strip()
    tree = str(git("rev-parse", "HEAD^{tree}")).strip()
    if head != COMMIT or tree != TREE:
        raise RuntimeError(f"wrong upstream identity: {head} {tree}")
    if str(git("status", "--porcelain")).strip():
        raise RuntimeError("upstream scratch clone is dirty")
    archive = bytes(
        git(
            "archive",
            "--format=tar",
            "--prefix=Self-Evolving-Agents-Double-Ratchet-0f14e910/",
            COMMIT,
            binary=True,
        )
    )
    archive_sha = hashlib.sha256(archive).hexdigest()
    if archive_sha != ARCHIVE_SHA256:
        raise RuntimeError("deterministic source archive hash changed")

    raw = str(git("ls-tree", "-r", "--long", "HEAD"))
    rows: list[tuple[str, int, str]] = []
    for line in raw.splitlines():
        meta, path = line.split("\t", 1)
        mode, kind, oid, size = meta.split()
        if kind != "blob":
            raise RuntimeError("unexpected non-blob recursive tree entry")
        rows.append((path, int(size), mode))
    top_counts: dict[str, int] = {}
    for path, _, _ in rows:
        top = path.split("/", 1)[0] if "/" in path else "<root>"
        top_counts[top] = top_counts.get(top, 0) + 1
    readonly_failures = []
    for path in (UPSTREAM, *UPSTREAM.rglob("*")):
        if path.is_symlink():
            continue
        if path.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
            readonly_failures.append(str(path.relative_to(UPSTREAM)))
    return {
        "commit_sha": head,
        "tree_sha": tree,
        "commit_date_utc": str(git("show", "-s", "--format=%cI", "HEAD")).strip(),
        "commit_signature_status": str(git("show", "-s", "--format=%G?", "HEAD")).strip(),
        "detached_head": "HEAD (no branch)" in str(git("status", "--short", "--branch")),
        "clean_tree": True,
        "scratch_clone_read_only": not readonly_failures,
        "read_only_failures": readonly_failures,
        "file_count": len(rows),
        "blob_bytes": sum(size for _, size, _ in rows),
        "top_level_file_counts": dict(sorted(top_counts.items())),
        "dataset_tree_paths": sum(path.startswith("datasets/") for path, _, _ in rows),
        "stored_split_payload_paths": sum("/splits/" in path for path, _, _ in rows),
        "result_payload_paths": sum(
            path.startswith("results/") or path.endswith("result.json")
            for path, _, _ in rows
        ),
        "archive_sha256": archive_sha,
        "archive_bytes": len(archive),
        "audit_boundary": (
            "Git tree names, modes and byte counts only for repository-wide census; "
            "no benchmark/result payload was opened"
        ),
    }


def field(
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
    source = source_metadata()
    known_hashes = {
        "LICENSE": "09e8a9bcec8067104652c168685ab0931e7868f9c8284b66f5ae6edae5f1130b",
        "NOTICE": "5d86be6e681240106316a6763eb0dcb47a8adcb426c19df4693098ceb61bb531",
        "scripts/run_metric_evo.py": "fd6a2b776e1f64edb361401451e3e62d50b9caf21d129c3fa5dcbe336116dac0",
        "scripts/_common.py": "a609f1e6c10070e34dd46ca87bc2ee333ae783d45da142ff90012693b927a78f",
        "config/config.py": "6bf780a86a27a99cc102c87a2aa8f9dfd073f087466158f38f80b7aae0159760",
        "evalratchet/candidates.py": "8c8df0889547ccd33fdea6c4830159d7843501c065a401be671a1b51a3d0bc7e",
        "evalratchet/evolve.py": "86edd1c9b75e4926b3ebe754fa9cb7e85819c9cf307aed94a53323a71eda8618",
        "evalratchet/storage/metric_store.py": "e859ec13a1e7801788b7314da145f4a67d63970cf6ed9338c6658fb114a9708d",
        "evalratchet/metric_lang.py": "ffbcb7bac2d1e24a8e2576f82344da96ef44fe53a20df00da98f7cc0eae978a4",
        "evalratchet/data.py": "5ac3b673df79e17a88ec1332d039943712f01724781c73ff789d786ae18be0ea",
        "evalratchet/ops/mbpp.py": "05b05437f8ff448e02b0525e8e46bc6933a2372af658788caa999fea58bed80e",
        "vendor/skillevo/engine/solver.py": "089707d2a543c2fcf43be661a058647a0326e5402eb360156ed8baaba9de78ed",
        "vendor/skillevo/llm/prompts.py": "08611d2077e44267dbef415e26d514971ee36d268e2938e716d4b12c4eafa8f9",
        "vendor/skillevo/llm/client.py": "71193bbc04b42645f8bbf24fd3a28d180c271d990eccef978dce9380a21783f8",
    }
    observed_hashes = {name: sha256(UPSTREAM / name) for name in known_hashes}
    if observed_hashes != known_hashes:
        raise RuntimeError("source byte identity changed")

    lock_path = HERE / "DOUBLE_RATCHET_DEPENDENCY_LOCK_V4.uv.lock"
    spec_path = HERE / "DOUBLE_RATCHET_DEPENDENCY_SPEC_V4.toml"
    lock_text = lock_path.read_text(encoding="utf-8")
    package_count = lock_text.count("[[package]]")
    if package_count != 46:
        raise RuntimeError(f"unexpected dependency package count: {package_count}")

    write_json(
        "P5_C5_V4_WRITE_SURFACE_SCHEMA.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://orion.invalid/p5/v4/c5-double-ratchet-write-audit.schema.json",
            "title": "P5 C5 evaluator-only isolated write audit",
            "type": "object",
            "additionalProperties": False,
            "frozen_policy": {
                "root_filesystem": "READ_ONLY",
                "source_mount": "/input/source READ_ONLY except nested results mount",
                "candidate_visible_task_mount": "/input/task READ_ONLY",
                "sole_host_writable_root": "/input/source/results",
                "ephemeral_roots": ["/tmp", "/run/cache"],
                "capabilities": "DROP_ALL",
                "privilege_escalation": "FORBIDDEN",
                "attempt_reset": "EMPTY RESULTS DIRECTORY AND NEW CONTAINER",
                "protected_panel_mounts": "FORBIDDEN",
                "egress": "NAMED DENY-BY-DEFAULT NETWORK; IDENTITY STILL UNBOUND",
            },
            "properties": {
                "schema_version": {"const": "orion.p5.c5.isolated-write-audit.v4"},
                "arm_id": {"const": ARM_ID},
                "attempt_id": {"type": "string", "pattern": "^P5C5-[A-Z0-9_.-]+$"},
                "source_tree_sha256_pre": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "source_tree_sha256_post": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "task_tree_sha256_pre": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "task_tree_sha256_post": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "write_paths": {
                    "type": "array",
                    "items": {"type": "string", "pattern": "^results/metric_evo/"},
                },
                "forbidden_write_attempts": {"type": "integer", "minimum": 0},
                "fresh_store": {"type": "boolean"},
            },
            "required": [
                "schema_version", "arm_id", "attempt_id",
                "source_tree_sha256_pre", "source_tree_sha256_post",
                "task_tree_sha256_pre", "task_tree_sha256_post", "write_paths",
                "forbidden_write_attempts", "fresh_store",
            ],
        },
    )

    write_json(
        "P5_C5_V4_NATIVE_OUTPUT_SCHEMA.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://orion.invalid/p5/v4/c5-double-ratchet-native-terminal.schema.json",
            "title": "Outcome-blind C5 native terminal",
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "schema_version": {"const": "orion.p5.c5.double-ratchet-native-terminal.v4"},
                "arm_id": {"const": ARM_ID},
                "terminal_class": {"enum": ["EVALUATOR_REPAIR", "UNRESOLVED"]},
                "native_terminal": {
                    "enum": ["SUCCESS", "TIMEOUT", "ERROR", "EMPTY", "DOUBLE_RATCHET_GUARD_FAILURE"]
                },
                "reason": {"type": "string"},
                "evaluator_artifact_sha256": {"type": ["string", "null"]},
                "native_result_sha256": {"type": "string"},
                "metric_db_sha256": {"type": "string"},
                "solver_bytes_preserved": {"type": "boolean"},
                "performance": {"const": "CANNOT_CHECK"},
                "protected_outcome_accessed": {"const": False},
            },
            "required": [
                "schema_version", "arm_id", "terminal_class", "native_terminal",
                "reason", "evaluator_artifact_sha256", "solver_bytes_preserved",
                "performance", "protected_outcome_accessed",
            ],
        },
    )

    terminal_rules = {
        "schema_version": "orion.p5.c5.double-ratchet-native-terminal-rules.v4",
        "arm_id": ARM_ID,
        "actionable_class": "EVALUATOR_REPAIR",
        "rules": [
            {"priority": 1, "when": "protected panel or protected score enters evolution", "emit": "UNRESOLVED", "native_terminal": "DOUBLE_RATCHET_GUARD_FAILURE"},
            {"priority": 2, "when": "native exit is 124", "emit": "UNRESOLVED", "native_terminal": "TIMEOUT"},
            {"priority": 3, "when": "native exit is nonzero", "emit": "UNRESOLVED", "native_terminal": "ERROR"},
            {"priority": 4, "when": "no final expression, history, or metric.db", "emit": "UNRESOLVED", "native_terminal": "EMPTY"},
            {"priority": 5, "when": "solver/prompt/task bytes change, skill bank is nonempty, or write surface escapes results/metric_evo", "emit": "UNRESOLVED", "native_terminal": "DOUBLE_RATCHET_GUARD_FAILURE"},
            {"priority": 6, "when": "--naive, --golden-diff-selectable, joint evolution, or failed development validity is observed", "emit": "UNRESOLVED", "native_terminal": "DOUBLE_RATCHET_GUARD_FAILURE"},
            {"priority": 7, "when": "input-native certificate is not uniquely EVALUATOR_REPAIR", "emit": "UNRESOLVED", "native_terminal": "DOUBLE_RATCHET_GUARD_FAILURE"},
            {"priority": 8, "when": "all preceding guards pass on a development-only run", "emit": "EVALUATOR_REPAIR", "native_terminal": "SUCCESS"},
        ],
        "non_claims": [
            "EVALUATOR_REPAIR is a candidate terminal, not a correctness or superiority finding",
            "development agreement and synthetic fixtures are not P5 performance",
            "the parser is not the independent protected scorer",
        ],
    }
    write_json("P5_C5_V4_NATIVE_TERMINAL_RULES.json", terminal_rules)

    write_json(
        "P5_C5_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json",
        {
            "schema_version": "orion.p5.c5.candidate-visible-case-requirements.v4",
            "arm_id": ARM_ID,
            "required_content_addressed_components": [
                "P5 candidate-visible dossier bytes and schema",
                "fixed train, eval_dev and development-only locked-surrogate membership",
                "frozen solver outputs for every development item",
                "frozen solver.py and prompts.py bytes",
                "development soft-anchor bytes and provenance",
                "input-native one-of-eight certificate produced outside the evolver",
                "task and generated-output rights receipt",
            ],
            "required_separation": {
                "train": "unlabelled frozen solver outputs",
                "eval_dev": "candidate-visible sparse development anchor",
                "eval_locked": "development-only validity surrogate; never the protected final panel",
                "protected_final_panel": "absent from candidate/evolver custody and scored once externally",
            },
            "forbidden": [
                "protected revision-responsibility gold",
                "protected fresh-transfer or harm labels",
                "protected final score or per-case feedback",
                "released outcome/result payload used as a fixture",
                "regeneration of supposedly frozen solver outputs inside metric evolution",
            ],
            "state": "UNBOUND",
        },
    )

    write_json(
        "P5_C5_V4_CUSTODY_HANDOFF_SCHEMA.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://orion.invalid/p5/v4/c5-one-shot-handoff.schema.json",
            "title": "C5 final evaluator one-shot custody handoff",
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "schema_version": {"const": "orion.p5.c5.one-shot-handoff.v4"},
                "arm_id": {"const": ARM_ID},
                "source_commit": {"const": COMMIT},
                "evaluator_artifact_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "metric_db_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "native_result_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "solver_tree_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "development_task_tree_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "protected_panel_commitment": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "scorer_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "one_shot_nonce": {"type": "string", "minLength": 32},
                "candidate_feedback_channel": {"const": "NONE"},
            },
            "required": [
                "schema_version", "arm_id", "source_commit", "evaluator_artifact_sha256",
                "metric_db_sha256", "native_result_sha256", "solver_tree_sha256",
                "development_task_tree_sha256", "protected_panel_commitment", "scorer_sha256",
                "one_shot_nonce", "candidate_feedback_channel",
            ],
        },
    )

    write_json(
        "P5_C5_V4_INFORMATION_SURFACE.json",
        {
            "schema_version": "orion.p5.c5.information-surface.v4",
            "arm_id": ARM_ID,
            "native_candidate_visible": [
                "fixed task prompts and frozen no-skill solver outputs for train/eval_dev/development-locked surrogate",
                "unlabelled train gaps and detector consensus",
                "eval_dev golden-reference verbal feedback",
                "typed detector pool, lifecycle, costs, provenance and prompts",
                "metric expressions, elites, marginal statistics and audit history",
                "development-only agreement values if retained by the external study design",
            ],
            "native_writes": {
                "metric.db": ["ops", "batteries", "metric_stats", "eval_records", "audit_log"],
                "result.json": ["final_metric_expr", "final_locked_agreement", "elites", "evolution_history", "synthesized_ops_total", "store", "audit_events"],
                "stdout": "final metric expression, locked value and audit count",
            },
            "protected_hidden": [
                "fresh final panel identity and bytes",
                "protected revision-responsibility, transfer and harm labels",
                "protected scorer implementation and per-case outcomes",
                "final score before the whole matched panel is closed",
            ],
            "scientific_defect": (
                "The official runner itself generates solver outputs, evaluates eval_locked every "
                "round, persists locked values, and prints the final locked value. It is only P5-safe "
                "if eval_locked is a separately licensed development surrogate and the final protected "
                "panel never enters this process. Hosted sampling also means solver outputs are not "
                "byte-frozen merely because solver code/model labels are fixed."
            ),
            "forbidden_flags_and_paths": ["--naive", "--golden-diff-selectable", "scripts/run_co_evo.py", "scripts/run_skill_evo.py"],
            "protected_outcome_accessed": False,
        },
    )

    write_json(
        "P5_C5_V4_SOURCE_TREE_METADATA.json",
        {
            "schema_version": "orion.p5.c5.source-tree-metadata.v4",
            "repository": REPOSITORY,
            **source,
            "selected_entrypoint": "scripts/run_metric_evo.py",
            "excluded_entrypoints": ["scripts/run_co_evo.py", "scripts/run_skill_evo.py"],
            "source_hashes": known_hashes,
        },
    )

    write_json(
        "P5_C5_V4_SOURCE_RIGHTS_MANIFEST.json",
        {
            "schema_version": "orion.p5.c5.source-rights-manifest.v4",
            "arm_id": ARM_ID,
            "source": {
                "repository": REPOSITORY,
                "commit_sha": COMMIT,
                "tree_sha": TREE,
                "archive_sha256": ARCHIVE_SHA256,
                "root_spdx": "Apache-2.0",
                "license_sha256": known_hashes["LICENSE"],
                "notice_sha256": known_hashes["NOTICE"],
                "notice_retention_required": True,
            },
            "not_conveyed_by_source_licence": [
                "MBPP+/Hugging Face task content and tests",
                "P5 dossiers, development anchors and protected panel",
                "Amazon Bedrock model/service permission and data terms",
                "derived runtime image and complete dependency notices",
                "authority to retain or publish prompts, solver outputs, traces, metric.db or result.json",
            ],
            "source_rights_state": "BOUND",
            "task_benchmark_rights_state": "UNBOUND",
            "model_service_rights_state": "UNBOUND",
            "generated_artifact_rights_state": "UNBOUND",
        },
    )

    write_json(
        "P5_C5_V4_RESOURCE_REGISTRY.json",
        {
            "schema_version": "orion.p5.c5.resource-registry.v4",
            "arm_id": ARM_ID,
            "source_defaults": {
                "dataset": "mbpp",
                "train": 60,
                "eval_locked": 40,
                "eval_dev": 10,
                "rounds_upper_bound": 8,
                "min_delta": 0.01,
                "patience": 2,
                "seed": 42,
                "parallelism": 64,
                "max_tokens_per_model_call": 8192,
                "candidate_subprocess_timeout_seconds": 10,
            },
            "paper_reproduction_shape": {"rounds_upper_bound": 100, "min_delta": 0, "patience": 100, "seeds_named": [42, 7, 13]},
            "v4_bound_compute": {"vcpus": 16, "ram_gib": 32, "gpus": 0, "pids_limit": 2048, "provider_parallelism": 64},
            "v4_bound_wallclock_seconds": {"whole_c5_run": 21600, "termination_grace": 120},
            "source_retry_policy": {"attempts_per_model": 3, "base_delay_seconds": 0.5, "maximum_delay_seconds": 8.0, "jitter": "FULL", "connect_timeout_seconds": 10, "read_timeout_seconds": 120},
            "fallbacks": [],
            "unbound": [
                "aggregate API call ceiling",
                "aggregate input/output token hard stop",
                "aggregate USD hard stop and overshoot semantics",
                "exact Bedrock endpoint/DNS/TLS/service revision",
                "deny-by-default egress network attestation",
            ],
            "execution_ready": False,
        },
    )

    execution_protocol = {
        "schema_version": "orion.p5.c5.double-ratchet-execution-binding-protocol.v4",
        "protocol_id": PROTOCOL_ID,
        "arm_id": ARM_ID,
        "scope": "Evaluator-only evolution; exact run_metric_evo.py arm; no skill/co-evolution",
        "pre_evolution_gates": [
            "all 21 registry fields BOUND",
            "exact source commit/tree/licence and dependency lock reverified",
            "candidate-visible P5 development packet and frozen solver outputs byte-bound",
            "eval_locked renamed and attested as development-only surrogate",
            "--naive and --golden-diff-selectable absent",
            "fresh empty metric store and isolated results-only write surface",
            "protected panel and score paths absent",
        ],
        "development_evolution": [
            "run exactly one authorized metric-only attempt within the bound resource envelope",
            "retain every native null/error/timeout/abstention terminal",
            "verify solver, prompt and task bytes unchanged",
            "hash result.json plus metric.db into one evaluator artifact",
            "emit EVALUATOR_REPAIR only through the frozen native parser guards",
        ],
        "external_confirmation": [
            "independent custodian accepts one evaluator artifact",
            "fresh protected panel scored exactly once by immutable external scorer",
            "no per-case or aggregate feedback returns to candidate/evolver until panel close",
            "only signed authorized closing receipt may support later performance claims",
        ],
        "current_terminal": TERMINAL,
        "execution_ready": False,
    }
    write_json("P5_C5_V4_EXECUTION_BINDING_PROTOCOL.json", execution_protocol)

    parser_sha = sha256(HERE / "p5_c5_native_parser.py")
    runner_sha = sha256(HERE / "p5_c5_isolated_runner.py")
    lock_sha = sha256(lock_path)
    spec_sha = sha256(spec_path)

    fields = {
        "adapter.isolated_write_surface": field(
            "BOUND",
            binding={"runner": "p5_c5_isolated_runner.py", "runner_sha256": runner_sha, "policy": "P5_C5_V4_WRITE_SURFACE_SCHEMA.json", "host_writable_roots": ["/input/source/results"], "ephemeral_roots": ["/tmp", "/run/cache"]},
            cause=None,
            residual="The hashed wrapper freezes a results-only host write surface, a fresh-store reset and read-only source/task mounts; it still refuses command construction while any other field is unbound.",
            next_discriminator="Validate mount precedence, egress and before/after source/task digests on the eventual content-addressed Linux image.",
        ),
        "adapter.native_parser_binding": field(
            "BOUND",
            binding={"parser": "p5_c5_native_parser.py", "parser_sha256": parser_sha, "schema": "P5_C5_V4_NATIVE_OUTPUT_SCHEMA.json", "actionable_classes": ["EVALUATOR_REPAIR"], "protected_score_fields_emitted": 0},
            cause=None,
            residual="The parser freezes the C5 guard mapping and content-addresses result.json plus metric.db while withholding all agreement values; it is not a protected scorer.",
            next_discriminator="Keep parser bytes frozen and place the independent final scorer outside candidate/evolution custody.",
        ),
        "custody.external_protected_scorer": field(
            "CANNOT_CHECK", binding=None,
            cause="No independent scorer principal, immutable scorer digest, access-control identity or signed acceptance exists.",
            residual="C5 confirmatory execution is not licensed.",
            next_discriminator="Independent custodian supplies scorer identity, digest and access-control attestation without revealing protected bytes.",
        ),
        "custody.one_shot_no_feedback_barrier": field(
            "CANNOT_CHECK", binding=None,
            cause="The official runner reports its eval_locked value every round and at stdout; no independent one-shot handoff/no-return-channel receipt exists.",
            residual="The upstream eval_locked set may only be a development surrogate; final protected outcomes cannot enter this process.",
            next_discriminator="Custodian signs one accepted artifact, one protected scoring event and no feedback path; verify the protected panel was never mounted during evolution.",
        ),
        "custody.protected_panel_freshness": field(
            "CANNOT_CHECK", binding=None,
            cause="No post-protocol protected panel identity, commitment or freshness attestation was available.",
            residual="Fresh transfer, harm and performance remain CANNOT_CHECK.",
            next_discriminator="Freeze a fresh panel only after protocol and evaluator bytes are locked, under independent custody.",
        ),
        "identity.native_entrypoint_bytes": field(
            "BOUND",
            binding={"entrypoint": "scripts/run_metric_evo.py", "entrypoint_sha256": known_hashes["scripts/run_metric_evo.py"], "common_sha256": known_hashes["scripts/_common.py"], "config_sha256": known_hashes["config/config.py"], "solver_sha256": known_hashes["vendor/skillevo/engine/solver.py"], "prompts_sha256": known_hashes["vendor/skillevo/llm/prompts.py"], "metric_evolution_sha256": known_hashes["evalratchet/evolve.py"], "metric_store_sha256": known_hashes["evalratchet/storage/metric_store.py"], "excluded": ["scripts/run_co_evo.py", "scripts/run_skill_evo.py", "--naive", "--golden-diff-selectable"]},
            cause=None,
            residual="Exact evaluator-only runner, frozen solver and core metric bytes are retained; bytes alone do not freeze hosted outputs or create a P5 adapter.",
            next_discriminator="Reverify all bound bytes immediately before image build and after evolution.",
        ),
        "identity.source_license_bytes": field(
            "BOUND",
            binding={"spdx": "Apache-2.0", "license_sha256": known_hashes["LICENSE"], "notice_sha256": known_hashes["NOTICE"]},
            cause=None,
            residual="Exact source licence and notice bytes are retained; task, service, container and generated-artifact rights remain separate.",
            next_discriminator="Carry LICENSE and NOTICE into any derived runtime/source distribution.",
        ),
        "identity.source_repository_commit": field(
            "BOUND",
            binding={"repository": REPOSITORY, "commit_sha": COMMIT, "tree_sha": TREE, "commit_date_utc": source["commit_date_utc"], "archive_sha256": ARCHIVE_SHA256, "tree_file_count": source["file_count"], "tree_blob_bytes": source["blob_bytes"]},
            cause=None,
            residual="Official public source identity is byte-addressed in a clean detached read-only scratch clone.",
            next_discriminator="Fetch by commit and reverify archive/tree immediately before a build.",
        ),
        "inputs.candidate_visible_case_bytes": field(
            "UNBOUND", binding={"authoritative_tree_split_payload_paths": source["stored_split_payload_paths"], "authoritative_tree_result_payload_paths": source["result_payload_paths"]},
            cause="The source contains no stored split or result payload. No rights-cleared P5 dossier, frozen solver-output set, development anchor or development-only locked surrogate is frozen.",
            residual="The authored parser smoke is schema conformance only and licenses zero substantive P5 cases.",
            next_discriminator="Freeze one complete candidate-visible P5 development packet satisfying P5_C5_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json without any protected-final bytes.",
        ),
        "model_provider.fallbacks": field(
            "BOUND", binding={"fallbacks": [], "closed_behavior": "FAIL; DO_NOT_SWITCH_MODEL_OR_PROVIDER", "unsafe_environment_inheritance": "DENIED_BY_FRESH_CONTAINER_ENV"},
            cause=None,
            residual="The exact fallback set is empty for the selected metric-only role clients.",
            next_discriminator="Retain the empty list when primary model/service identities are selected.",
        ),
        "model_provider.primary": field(
            "UNBOUND", binding={"source_default_model": "global.anthropic.claude-opus-4-7", "source_default_region": "us-east-1", "source_roles": ["agent", "teacher", "architect", "judge", "critic", "light"], "configured_embedding_model": "global.cohere.embed-v4:0"},
            cause="Repository labels do not freeze an immutable served model revision, cross-region route, exact endpoint/TLS identity, service revision, credential principal or allowed role/capability map; frozen solver outputs are also absent.",
            residual="C5 is not licensed for execution.",
            next_discriminator="Bind exact provider/service/model revisions and credentials, then generate solver outputs once and freeze their bytes before evaluator evolution.",
        ),
        "resources.calls_tokens_usd": field(
            "UNBOUND", binding={"per_call_max_output_tokens": 8192},
            cause="Dynamic detector, synthesis, teacher and solver calls have no aggregate call, input-token, output-token or USD hard stop; provider usage reconciliation and overshoot semantics are absent.",
            residual="A per-call output limit is not an aggregate resource binding.",
            next_discriminator="Instrument a provider-reconciled pre-call hard-stop monitor over every role and retry, with exact aggregate caps and typed exhaustion terminal.",
        ),
        "resources.retry_network": field(
            "UNBOUND", binding={"source_retry_attempts": 3, "base_delay_seconds": 0.5, "max_delay_seconds": 8.0, "jitter": "FULL", "connect_timeout_seconds": 10, "read_timeout_seconds": 120, "fallbacks": []},
            cause="Retry bytes are known, but the Bedrock route/DNS/TLS endpoint, offline dataset policy and deny-by-default egress network are not independently bound or enforced.",
            residual="C5 is not licensed for networked execution.",
            next_discriminator="Bind one provider endpoint and an attested egress network that denies Hugging Face/task fetch and every other destination.",
        ),
        "resources.wallclock": field(
            "BOUND", binding={"whole_c5_run_seconds": 21600, "termination_grace_seconds": 120, "native_candidate_subprocess_seconds": 10, "enforcer": "p5_c5_isolated_runner.py", "enforcer_sha256": runner_sha, "timeout_terminal": "TIMEOUT/exit 124"},
            cause=None,
            residual="A whole-run timeout is prospectively frozen; provider calls already have connect/read timeouts and MBPP has a native 10-second candidate subprocess timeout.",
            next_discriminator="Verify TERM/KILL propagation, child cleanup and exit 124 in the eventual image.",
        ),
        "rights.container_and_generated_artifacts": field(
            "UNBOUND", binding=None,
            cause="No content-addressed runtime image/SBOM/complete notices or authority for prompts, solver outputs, task traces, metric.db and result.json retention/publication is closed.",
            residual="C5 is not licensed for runtime artifact retention or redistribution.",
            next_discriminator="Build the full image, capture SBOM/licences and obtain explicit retention/disclosure authority for all generated artifacts.",
        ),
        "rights.model_provider_and_services": field(
            "UNBOUND", binding=None,
            cause="No authorized Bedrock credential principal, study-use/data-retention terms, cross-region policy, pricing/quota receipt or publication permission is frozen.",
            residual="Apache-2.0 source rights do not authorize model service use.",
            next_discriminator="Bind provider terms, data policy, credential principal, region/route and aggregate-result publication rights.",
        ),
        "rights.task_and_benchmark_content": field(
            "UNBOUND", binding={"tree_dataset_builder_paths": source["dataset_tree_paths"], "stored_split_payload_paths": source["stored_split_payload_paths"], "result_payload_paths": source["result_payload_paths"]},
            cause="The repository explicitly excludes datasets/results. MBPP+/Hugging Face, P5 dossiers, development anchors and final protected panel have separate licences/terms not captured here.",
            residual="No benchmark or P5 content is licensed by this packet.",
            next_discriminator="Use an authored or explicitly licensed P5 development packet plus an independently licensed protected panel and scorer.",
        ),
        "runtime.compute": field(
            "BOUND", binding={"vcpus": 16, "ram_gib": 32, "gpus": 0, "pids_limit": 2048, "provider_parallelism": 64, "enforcer": "p5_c5_isolated_runner.py", "enforcer_sha256": runner_sha},
            cause=None,
            residual="The wrapper freezes container-wide CPU/RAM/PID/no-GPU limits and preserves the native 64-thread provider fan-out.",
            next_discriminator="Verify Docker/cgroup enforcement and provider fan-out on the final host before custody use.",
        ),
        "runtime.container_or_environment": field(
            "UNBOUND", binding=None,
            cause="No content-addressed Linux image containing Python 3.11, the exact lock, timeout tooling and source runtime has been built, SBOMed and smoke-verified.",
            residual="The dependency lock and source bytes alone are not an executable environment.",
            next_discriminator="Build once from the lock on the selected Linux architecture, capture image/SBOM digests and run only synthetic/native-shaped smoke.",
        ),
        "runtime.dependency_lock": field(
            "BOUND", binding={"spec": "DOUBLE_RATCHET_DEPENDENCY_SPEC_V4.toml", "spec_sha256": spec_sha, "lock": "DOUBLE_RATCHET_DEPENDENCY_LOCK_V4.uv.lock", "lock_sha256": lock_sha, "resolver": "uv 0.11.1", "python_request": ">=3.11,<3.12", "package_entries": package_count, "direct_dependencies": ["boto3", "datasets", "pydantic", "pyyaml"]},
            cause=None,
            residual="The V4 resolution closes the released default MBPP metric-only dependency base, including the source-observed but README-omitted datasets package; a future P5 task adapter may introduce additional dependencies and remains separately unbound.",
            next_discriminator="Build from this exact lock, preserve wheel/sdist receipts, and amend only under a separately named adapter revision if P5 integration needs more packages.",
        ),
        "runtime.task_environment": field(
            "UNBOUND", binding={"native_command": None},
            cause="The official entrypoint supports MBPP/report_gen, not the P5 dossier or eight-class decision. It regenerates hosted solver outputs at run time and uses eval_locked each round; no P5-native task adapter or frozen development-output environment exists.",
            residual="Silently formatting P5 as MBPP or exposing the final panel as eval_locked would change semantics and violate custody.",
            next_discriminator="Preregister and byte-freeze a P5-native evaluator-only adapter that consumes already frozen solver outputs, uses a development-only surrogate, and leaves the final protected panel external.",
        ),
    }
    required = sorted(fields)
    if len(required) != 21:
        raise RuntimeError(f"field registry must contain 21 fields, got {len(required)}")
    bound = sorted(name for name, item in fields.items() if item["state"] == "BOUND")
    blocking = sorted(name for name, item in fields.items() if item["state"] != "BOUND")
    if len(bound) != 9 or len(blocking) != 12:
        raise RuntimeError(f"unexpected field counts {len(bound)} bound {len(blocking)} blocking")

    registry = {
        "schema_version": "orion.p5.c5.double-ratchet-field-registry.v4",
        "registry_id": "P5.C5.DOUBLE_RATCHET.FIELD.REGISTRY.V4",
        "frozen_at_utc": FROZEN_AT,
        "arm_id": ARM_ID,
        "required_field_paths": required,
        "fields": fields,
        "bound_fields": bound,
        "bound_field_count": len(bound),
        "blocking_fields": blocking,
        "blocking_field_count": len(blocking),
        "execution_ready": False,
        "panel_confirmatory_ready_arms": 0,
        "bound_execution_envelope": {
            "runtime_image": None,
            "egress_network": None,
            "native_command": None,
            "fallbacks": [],
            "compute": {"vcpus": 16, "ram_gib": 32, "gpus": 0, "pids_limit": 2048, "provider_parallelism": 64},
            "wallclock_seconds": {"whole_c5_run": 21600, "termination_grace": 120},
        },
        "terminal": "C5_PARTIAL_BINDING__TWELVE_REQUIRED_FIELDS_NOT_BOUND__EXECUTION_REFUSED",
    }
    write_json("P5_C5_V4_FIELD_REGISTRY.json", registry)

    negative_entries = []
    for name in blocking:
        item = fields[name]
        negative_entries.append({"field_path": name, "state": item["state"], "cause": item["cause"], "residual": item["residual"], "next_discriminator": item["next_discriminator"]})
    scientific_defects = [
        {
            "id": "C5D1_SOLVER_OUTPUTS_REGENERATED",
            "state": "UNBOUND",
            "cause": "solve_real_outputs calls the hosted agent for train, eval_dev and eval_locked during each run; source/model labels do not byte-freeze outputs.",
            "residual": "The supposed evaluator-only arm does not yet hold realized solver outputs fixed across attempts/arms.",
            "next_discriminator": "Freeze solver outputs before evolution and require their complete pre/post tree digest to match.",
        },
        {
            "id": "C5D2_LOCKED_REPORTED_EACH_ROUND",
            "state": "CANNOT_CHECK",
            "cause": "evolve_metric_expr calls _report_locked each round, stores locked_report_agreement, writes final_locked_agreement and prints locked to stdout.",
            "residual": "The final protected panel cannot be used as native eval_locked; only a candidate-visible development surrogate is admissible.",
            "next_discriminator": "Externally attest that native eval_locked is development-only and score the final evaluator once on a separate protected panel.",
        },
        {
            "id": "C5D3_NO_P5_NATIVE_DATASET_OR_CLASS",
            "state": "UNSUPPORTED",
            "cause": "SUPPORTED_DATASETS is mbpp/report_gen and the native result exposes metric statistics, not a P5 one-of-eight responsibility decision.",
            "residual": "A P5 adapter is a separately named semantic bridge, not evidence that the released code natively solves P5.",
            "next_discriminator": "Preregister an evaluator-only P5 adapter and validate its fibres with synthetic/native-shaped cases only.",
        },
        {
            "id": "C5D4_SOURCE_HAS_NO_DATA_OR_RESULTS",
            "state": "CANNOT_CHECK",
            "cause": f"Authoritative tree has {source['stored_split_payload_paths']} stored split payload paths and {source['result_payload_paths']} result payload paths.",
            "residual": "No task, result or performance claim can be reconstructed from source metadata.",
            "next_discriminator": "Acquire separately licensed development content without opening any final protected outcome.",
        },
        {
            "id": "C5D5_README_DEPENDENCY_OMISSION",
            "state": "PRESERVED_REPAIRED_IN_V4_LOCK",
            "cause": "README lists pydantic/pyyaml/boto3, while the default MBPP loader imports the Hugging Face datasets package at runtime.",
            "residual": "V4 lock adds datasets explicitly; no claim is made that a future P5 adapter has no further dependencies.",
            "next_discriminator": "Build from the lock and preserve artifacts; amend only with explicit adapter identity.",
        },
        {
            "id": "C5D6_METRIC_FIXTURES_NOT_PERFORMANCE",
            "state": "CANNOT_CHECK",
            "cause": "Synthetic/native-shaped parser cases test mapping and refusal only.",
            "residual": "They license zero raw singletons and say nothing about H1-H4, transfer, harm, preservation, performance or superiority.",
            "next_discriminator": "Use the independently custodied one-shot panel after 6/6 matched arm readiness.",
        },
    ]
    negative = {
        "schema_version": "orion.p5.c5.double-ratchet-negative-ledger.v4",
        "arm_id": ARM_ID,
        "blocking_field_count": len(blocking),
        "blocking_entries": negative_entries,
        "scientific_defects": scientific_defects,
        "preserved_claims": {name: "CANNOT_CHECK" for name in ["H1", "H2", "H3", "H4", "fresh_transfer", "harm", "preservation", "performance", "superiority"]},
        "top_tier_publication_readiness": "NOT_ESTABLISHED",
    }
    write_json("P5_C5_V4_NEGATIVE_LEDGER.json", negative)
    ledger_lines = [
        "# P5 C5 Double Ratchet V4 negative ledger",
        "",
        f"**Outcome-blind status:** {len(bound)}/21 fields BOUND; {len(blocking)}/21 blocking; execution refused.",
        "",
        "No benchmark, native result, metric database, protected panel or protected score was opened. Synthetic/native-shaped fixtures are conformance-only.",
        "",
        "## Blocking fields",
        "",
        "| Field | State | Cause | Next discriminator |",
        "|---|---|---|---|",
    ]
    for item in negative_entries:
        ledger_lines.append(f"| `{item['field_path']}` | {item['state']} | {item['cause']} | {item['next_discriminator']} |")
    ledger_lines += ["", "## Scientific defects", ""]
    for item in scientific_defects:
        ledger_lines += [f"### {item['id']} — {item['state']}", "", f"**Cause:** {item['cause']}", "", f"**Residual:** {item['residual']}", "", f"**Next discriminator:** {item['next_discriminator']}", ""]
    write_text("P5_C5_V4_NEGATIVE_LEDGER.md", "\n".join(ledger_lines))

    # Avoid leaving bytecode outside the immutable packet manifest.
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("p5_c5_native_parser", HERE / "p5_c5_native_parser.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load parser for smoke")
    parser_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser_mod)
    smoke = parser_mod.self_smoke()
    if smoke["terminal"] != "SYNTHETIC_CONFORMANCE_ONLY":
        raise RuntimeError("synthetic parser smoke failed")
    write_json("P5_C5_V4_SMOKE_RECEIPT.json", smoke)

    result = {
        "schema_version": "orion.p5.c5.double-ratchet-execution-binding-result.v4",
        "protocol_id": PROTOCOL_ID,
        "arm_id": ARM_ID,
        "authority": "PUBLIC_SOURCE_IDENTITY_AND_OUTCOME_BLIND_PREFLIGHT_ONLY",
        "source_identity": {"repository": REPOSITORY, "commit_sha": COMMIT, "tree_sha": TREE, "archive_sha256": ARCHIVE_SHA256},
        "v4_repairs": {
            "bound_fields": len(bound),
            "blocking_fields": len(blocking),
            "newly_bound_v3_fields": ["adapter.isolated_write_surface", "adapter.native_parser_binding", "model_provider.fallbacks", "resources.wallclock", "runtime.compute", "runtime.dependency_lock"],
            "retained_bound_identity_fields": ["identity.native_entrypoint_bytes", "identity.source_license_bytes", "identity.source_repository_commit"],
            "v3_to_v4_blocker_delta": -6,
        },
        "execution": {"c5_executed": False, "execution_ready": False, "full_native_smoke": "CANNOT_CHECK", "panel_confirmatory_ready_arms": 0, "panel_required_arms": 6},
        "material_discoveries": [
            "official metric-only runner regenerates hosted solver outputs rather than consuming byte-frozen outputs",
            "official eval_locked is evaluated every round and written/printed; it cannot be the final protected panel",
            "official source natively supports mbpp/report_gen, not the P5 dossier/eight-class surface",
            "authoritative tree contains zero stored split payloads and zero result payloads",
            "README dependency list omits the default MBPP loader's datasets package; V4 lock makes it explicit",
        ],
        "preserved_boundaries": {"raw_native_singleton_licences": 0, "substantive_p5_cases": 0, "synthetic_parser_cases": smoke["synthetic_cases"], "synthetic_cases_as_performance": 0},
        "preserved_claims": negative["preserved_claims"],
        "top_tier_publication_readiness": "NOT_ESTABLISHED",
        "next_discriminator": "Freeze a rights-cleared P5 development packet and solver-output tree, bind exact Bedrock service/egress/call-token-USD envelope plus image/SBOM, and establish independent fresh-panel one-shot custody; C5 must still wait for 6/6 matched arm readiness.",
        "terminal": TERMINAL,
    }
    write_json("P5_C5_V4_RESULT.json", result)

    report = f"""# P5 C5 Double Ratchet metric-only execution binding — V4

## Scientific result first

**Terminal:** `{TERMINAL}`

The exact official metric-only arm is source-bound at `{COMMIT}` / tree `{TREE}`, but **C5 was not executed**. Exactly **{len(bound)}/21 fields are BOUND and {len(blocking)}/21 remain blocking**. Panel readiness is **0/6**. Performance, superiority, preservation, transfer, harm and H1-H4 remain **CANNOT_CHECK**.

The key scientific defect is not an installation detail: `run_metric_evo.py` calls the hosted solver afresh for train, eval_dev and eval_locked, so realized solver outputs are not fixed merely because the solver code/model label is fixed. It also computes `eval_locked` agreement every round, persists it in `metric.db`/history/result.json and prints the final value. A P5 use is therefore admissible only if native `eval_locked` is a separate development-only surrogate and the true protected panel never enters the evolution process. The frozen evaluator must be scored exactly once by an independent custodian.

## Exact source and native arm

- Repository: `{REPOSITORY}`
- Commit: `{COMMIT}` (unsigned Git commit status `N`, 2026-07-29T05:20:31Z)
- Tree: `{TREE}`
- Deterministic archive SHA-256: `{ARCHIVE_SHA256}`
- Tree metadata: {source['file_count']} blobs / {source['blob_bytes']} bytes; {source['stored_split_payload_paths']} stored split payloads; {source['result_payload_paths']} result payloads.
- Entrypoint: `scripts/run_metric_evo.py`, SHA-256 `{known_hashes['scripts/run_metric_evo.py']}`.
- Licence: Apache-2.0 `{known_hashes['LICENSE']}`; NOTICE `{known_hashes['NOTICE']}`.
- Excluded: co-evolution, skill evolution, `--naive`, and `--golden-diff-selectable`.

Repository-wide inspection used Git tree names/modes/counts only. No benchmark or result payload was opened. The scratch clone is clean, detached and read-only.

## V4 bindings

The six V3 blockers repaired by V4 are: isolated results-only write surface, native terminal parser, empty fallback set, whole-run wallclock, compute envelope, and a 46-entry uv dependency resolution. Together with the three retained source identity fields, this yields 9 bound fields.

The parser can emit only `EVALUATOR_REPAIR` or `UNRESOLVED`. `EVALUATOR_REPAIR` requires exact source, unchanged solver/prompt/task bytes, empty skill bank, evaluator-only writes, anchored validity, a unique input-native evaluator-repair certificate, and no protected panel/score. It never returns agreement values and is not a protected scorer.

The generated lock explicitly includes `datasets`, which the default MBPP loader imports even though README's short install list names only pydantic, pyyaml and boto3. This is a dependency repair, not a scientific result and not a claim that a future P5 adapter needs no extra dependencies.

## Twelve blockers

{chr(10).join(f'- `{name}` — {fields[name]["cause"]}' for name in blocking)}

## Synthetic/native-shaped smoke boundary

The parser's {smoke['synthetic_cases']} in-memory cases exercised one guarded success shape and five fail-closed paths. They load no real metric, task, benchmark, result or protected outcome; license zero substantive singletons; and are not performance evidence.

## Next discriminator

{result['next_discriminator']}
"""
    write_text("SCIENTIFIC_REPORT_V4.md", report)
    write_text(
        "README.md",
        f"""# P5 C5 Double Ratchet metric-only V4 freeze

Outcome-blind execution-binding packet for `{COMMIT}`. No comparator, benchmark, native result or protected outcome was run/read.

- Scientific report: `SCIENTIFIC_REPORT_V4.md`
- Field registry: `P5_C5_V4_FIELD_REGISTRY.json` ({len(bound)} BOUND / {len(blocking)} blocking)
- Negative ledger: `P5_C5_V4_NEGATIVE_LEDGER.md`
- Exact terminal/result: `P5_C5_V4_RESULT.json`
- Parser and synthetic-only smoke: `p5_c5_native_parser.py`, `P5_C5_V4_SMOKE_RECEIPT.json`
- Fail-closed runner: `p5_c5_isolated_runner.py`

Run `python p5_c5_v4_validator.py` for outcome-free structural validation. The runner preflight must refuse execution while any field is unbound.
""",
    )

    # Audit is declarative; the independent validator rechecks it without
    # reading any substantive payload.
    audit = {
        "schema_version": "orion.p5.c5.audit-receipt.v4",
        "arm_id": ARM_ID,
        "frozen_at_utc": FROZEN_AT,
        "source_commit": COMMIT,
        "source_tree": TREE,
        "source_file_count": source["file_count"],
        "source_blob_bytes": source["blob_bytes"],
        "stored_split_payloads_opened": 0,
        "result_payloads_opened": 0,
        "protected_outcomes_opened": 0,
        "synthetic_parser_cases": smoke["synthetic_cases"],
        "synthetic_parser_cases_passed": smoke["synthetic_cases_passed"],
        "raw_native_singleton_licences": 0,
        "bound_field_count": len(bound),
        "blocking_field_count": len(blocking),
        "execution_ready": False,
        "c5_executed": False,
        "panel_ready": "0/6",
        "validator_contract": {"minimum_checks": 80, "checksum_manifest_required": True},
        "terminal": TERMINAL,
    }
    write_json("AUDIT_RECEIPT_V4.json", audit)

    temp_archive = HERE / ".source-archive.tmp.tar"
    if temp_archive.exists():
        temp_archive.unlink()

    checksum_excludes = {"SHA256SUMS"}
    files = sorted(
        p for p in HERE.iterdir()
        if p.is_file() and p.name not in checksum_excludes and not p.name.startswith(".")
    )
    lines = [f"{sha256(path)}  {path.name}" for path in files]
    write_text("SHA256SUMS", "\n".join(lines))
    print(
        canonical(
            {
                "arm_id": ARM_ID,
                "bound_field_count": len(bound),
                "blocking_field_count": len(blocking),
                "checksum_entries": len(lines),
                "execution_ready": False,
                "terminal": TERMINAL,
            }
        ),
        end="",
    )


if __name__ == "__main__":
    main()
