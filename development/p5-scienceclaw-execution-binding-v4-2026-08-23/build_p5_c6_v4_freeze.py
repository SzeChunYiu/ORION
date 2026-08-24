#!/usr/bin/env python3
"""Build the outcome-blind P5 C6 ScienceClaw V4 execution-binding packet."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
UPSTREAM = Path(os.environ.get("P5_C6_UPSTREAM", str(HERE / ".source-audit"))).resolve()
FROZEN_AT = "2026-08-23T18:49:49Z"
ARM_ID = "C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW"
REPOSITORY = "https://github.com/lamm-mit/scienceclaw"
BRANCH = "categoryscienceclaw-mechanics"
COMMIT = "38b2f681e87272cd505c9b2671760fc3729756c2"
TREE = "8b483159e46da54675ee904841f2e8667b2348bc"
ARCHIVE_SHA256 = "2020d5dd69e5118bebccb2e82cf47807c6be6a0eeb75952e910f0bbac98f82be"
ARCHIVE_BYTES = 109_045_760
TERMINAL = (
    "P5_C6_V4_SCIENCECLAW_SOURCE_TREE_DRAFT_PARSER_AND_OUTER_WALLCLOCK_BOUND__"
    "NATIVE_SELECTOR_UNSUPPORTED_AND_FALLBACKS_OPEN__SIXTEEN_C6_FIELDS_BLOCKING__"
    "PRIOR_OUTCOME_PREFIXES_HASHED_NOT_DECODED__ZERO_OF_SIX_PANEL_READY__"
    "PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK"
)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(name: str, value: Any) -> None:
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(UPSTREAM), *args], text=True).strip()


def read_decl_lines(path: Path) -> list[str]:
    values = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        value = raw.split("#", 1)[0].strip()
        if value:
            values.append(value)
    return values


def source_tree_manifest() -> dict[str, Any]:
    if git("rev-parse", "HEAD") != COMMIT or git("rev-parse", "HEAD^{tree}") != TREE:
        raise RuntimeError("upstream identity mismatch")
    output = subprocess.check_output(
        ["git", "-C", str(UPSTREAM), "ls-tree", "-r", "--full-tree", "--long", COMMIT],
        text=True,
    )
    entries = []
    total = 0
    prior = []
    pycache = []
    for raw in output.splitlines():
        header, path_text = raw.split("\t", 1)
        mode, kind, blob, size_text = header.split()
        size = int(size_text)
        total += size
        entry = {
            "path": path_text,
            "mode": mode,
            "object_type": kind,
            "git_blob_sha1": blob,
            "size_bytes": size,
            "sha256": sha(UPSTREAM / path_text),
        }
        entries.append(entry)
        if path_text.startswith("benchmarks/") or path_text.startswith("categoryscienceclaw/HEA/"):
            prior.append({"path": path_text, "size_bytes": size, "git_blob_sha1": blob, "sha256": entry["sha256"]})
        if "__pycache__/" in path_text or path_text.endswith(".pyc"):
            pycache.append({"path": path_text, "size_bytes": size})
    return {
        "schema_version": "orion.p5.c6.scienceclaw-source-tree-manifest.v4",
        "arm_id": ARM_ID,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "commit_sha": COMMIT,
        "tree_sha": TREE,
        "commit_author_date": "2026-07-30T19:49:42-04:00",
        "commit_committer_date": "2026-07-30T19:49:42-04:00",
        "commit_subject": "Add HEA results",
        "deterministic_git_archive": {
            "command_description": "git archive --format=tar HEAD",
            "sha256": ARCHIVE_SHA256,
            "size_bytes": ARCHIVE_BYTES,
            "archive_retained": False,
        },
        "file_count": len(entries),
        "total_file_bytes": total,
        "entries": entries,
        "outcome_blind_exclusion_census": {
            "excluded_prefixes": ["benchmarks/", "categoryscienceclaw/HEA/"],
            "file_count": len(prior),
            "total_bytes": sum(x["size_bytes"] for x in prior),
            "entries": prior,
            "payload_values_decoded_or_displayed": False,
            "cryptographic_hashing_only": True,
            "future_candidate_seed_policy": "EXCLUDE_PREFIXES_BEFORE_CANDIDATE_ACCESS",
        },
        "tracked_pycache_census": {
            "file_count": len(pycache),
            "total_bytes": sum(x["size_bytes"] for x in pycache),
            "payload_values_decoded_or_executed": False,
        },
    }


def dependency_declarations() -> dict[str, Any]:
    paths = [
        "requirements.txt", "requirements-full.txt",
        "skills/corpus-search/requirements.txt", "skills/dft/requirements.txt",
        "skills/hpc/requirements.txt", "skills/minerals-data/requirements.txt",
        "skills/timesfm-forecasting/requirements.txt", "skills/uma/requirements.txt",
    ]
    files = {}
    for rel in paths:
        values = read_decl_lines(UPSTREAM / rel)
        exact = [v for v in values if "==" in v and not any(op in v for op in (">=", "<=", "!=", "~="))]
        files[rel] = {
            "sha256": sha(UPSTREAM / rel),
            "declaration_count": len(values),
            "exact_pin_count": len(exact),
            "declarations": values,
        }
    tree_paths = git("ls-tree", "-r", "--name-only", COMMIT).splitlines()
    common_locks = [
        p for p in tree_paths
        if Path(p).name in {"uv.lock", "poetry.lock", "pdm.lock", "Pipfile.lock", "package-lock.json", "pnpm-lock.yaml", "yarn.lock"}
        or Path(p).name.startswith("conda-lock")
    ]
    module = ast.parse((UPSTREAM / "deps" / "skill_deps.py").read_text(encoding="utf-8"))
    skill_deps = {}
    for node in module.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SKILL_DEPS" for t in node.targets):
            skill_deps = ast.literal_eval(node.value)
            break
    return {
        "schema_version": "orion.p5.c6.scienceclaw-dependency-declarations.v4",
        "arm_id": ARM_ID,
        "classification": "SOURCE_DECLARATIONS_AND_DYNAMIC_INSTALL_MAP_NOT_A_TRANSITIVE_LOCK",
        "lock_present_in_authoritative_tree": bool(common_locks),
        "common_lock_paths": common_locks,
        "source_files": files,
        "top_level_core_declaration_count": files["requirements.txt"]["declaration_count"],
        "top_level_core_exact_pin_count": files["requirements.txt"]["exact_pin_count"],
        "top_level_full_declaration_count": files["requirements-full.txt"]["declaration_count"],
        "top_level_full_exact_pin_count": files["requirements-full.txt"]["exact_pin_count"],
        "skill_dependency_map": {
            "source": "deps/skill_deps.py",
            "sha256": sha(UPSTREAM / "deps" / "skill_deps.py"),
            "skill_keys": len(skill_deps),
            "unique_unversioned_package_names": len({p for values in skill_deps.values() for p in values}),
            "package_references": sum(len(values) for values in skill_deps.values()),
            "installer": "deps/installer.py",
            "installer_sha256": sha(UPSTREAM / "deps" / "installer.py"),
            "failure_behavior": "per-package install failure is logged and execution continues",
        },
        "material_source_facts": [
            "No common resolved lockfile exists in the authoritative tree.",
            "requirements.txt has 9 declarations and zero exact pins.",
            "requirements-full.txt has 112 declarations and zero exact pins.",
            "The lazy installer resolves bare package names at run time and continues after individual installation failures.",
            "The selected skill set can change the dependency graph after setup.",
        ],
        "reason_not_a_lock": "Ranges, bare names, dynamic pip installation and skill-local declarations do not bind one transitive graph, artifact hashes, platform markers or service/runtime identity.",
    }


def field(status: str, binding: Any, cause: str, residual: str, next_discriminator: str) -> dict[str, Any]:
    return {"status": status, "binding": binding, "cause": cause, "residual": residual, "next_discriminator": next_discriminator}


def make_fields(parser_hash: str, runner_hash: str, manifest_hash: str) -> dict[str, Any]:
    return {
        "adapter.isolated_write_surface": field(
            "BLOCKING", None,
            "Native ScienceClaw writes profiles, credentials, drafts, journals, investigations, graphs, artifacts and attestations under ~/.scienceclaw; selected skills may execute subprocesses, install packages, submit remote jobs or contact lab/scientific services. No disposable executor proof exists.",
            "A home-directory redirect and source checkout alone do not confine subprocess, service, cache, credential, device, scheduler or network effects.",
            "Demonstrate a disposable read-only source/case executor with an isolated HOME, scratch-only outputs, no devices/schedulers, and a complete reset/egress receipt.",
        ),
        "adapter.native_parser_binding": field(
            "BOUND",
            {
                "path": "p5_c6_native_parser.py", "sha256": parser_hash,
                "input": "one native scienceclaw-post --dry-run draft JSON",
                "output_schema": "P5_C6_V4_NATIVE_OUTPUT_SCHEMA.json",
                "protected_key_policy": "RAW_KEY_REFUSAL_BEFORE_JSON_DECODING",
                "scientific_payload_values_retained": False,
                "raw_native_singleton_licences": 0,
                "all_adapter_terminals": ["UNRESOLVED"],
            },
            "V4 binds a strict structural parser to the released dry-run draft shape without inventing a ScienceClaw selector.",
            "A valid draft, artifact, open need, status or content hash remains provenance/representation evidence and never identifies one P5 responsibility class.",
            "A resolved ScienceClaw decision requires a separately named, prospectively frozen revision-proposal successor; do not relabel this native parser.",
        ),
        "custody.external_protected_scorer": field(
            "BLOCKING", None,
            "No independent scorer identity, code digest, signing key or terminal-only return schema is supplied.",
            "ScienceClaw self-critique, peer review, benchmark files and artifact audits are candidate-side facilities, not an external protected scorer.",
            "Obtain a signed external scorer attestation with exact code/data hashes and no candidate-readable outcomes.",
        ),
        "custody.one_shot_no_feedback_barrier": field(
            "BLOCKING", None,
            "No independent one-shot no-feedback custodian exists; ScienceClaw is explicitly iterative, stores artifacts/needs and can refine content from prior outputs.",
            "Local code cannot self-attest that protected information was withheld from a recursive discovery system.",
            "Bind an external custodian that releases only a terminal after candidate freeze and proves no protected feedback entered artifacts, memory, tools or services.",
        ),
        "custody.protected_panel_freshness": field(
            "BLOCKING", None,
            "No fresh protected panel identity, nonce, selection receipt or independence attestation exists.",
            "The public benchmarks/ and HEA result paths are prior source content and cannot establish fresh protected evaluation.",
            "Bind a new six-arm protected panel manifest under independent custody after excluding all source-bundled prior-outcome prefixes.",
        ),
        "identity.native_entrypoint_bytes": field(
            "BOUND",
            {
                "setup.py": sha(UPSTREAM / "setup.py"),
                "bin/scienceclaw-post": sha(UPSTREAM / "bin" / "scienceclaw-post"),
                "autonomous/post_generator.py": sha(UPSTREAM / "autonomous" / "post_generator.py"),
                "autonomous/deep_investigation.py": sha(UPSTREAM / "autonomous" / "deep_investigation.py"),
                "core/llm_client.py": sha(UPSTREAM / "core" / "llm_client.py"),
                "artifacts/artifact.py": sha(UPSTREAM / "artifacts" / "artifact.py"),
                "released_command": "scienceclaw-post --agent <id> --topic <topic> --community <community> --skills <csv> --dry-run",
                "dry_run_caveat": "dry-run suppresses Infinite posting only; it still runs the investigation and writes a draft",
            },
            "Exact released command and implementation bytes are present.",
            "Entrypoint identity does not bind topic/case, profile, skills, dependencies, models, tools, services, isolation or scientific terminal semantics.",
            "Carry all hashes into a future source-native conformance receipt without treating --dry-run as outcome-free execution.",
        ),
        "identity.source_license_bytes": field(
            "BOUND",
            {"path": "LICENSE", "sha256": sha(UPSTREAM / "LICENSE"), "spdx": "Apache-2.0", "package_json_declared_license": "MIT", "metadata_consistent": False},
            "Exact root Apache-2.0 licence bytes are present, while package.json separately declares MIT.",
            "The root grant binds source identity but the metadata inconsistency and third-party skills, APIs, datasets, models, services and generated artifacts require separate adjudication.",
            "Use the exact root licence bytes and obtain component/service/content-specific rights receipts; do not infer rights from package.json.",
        ),
        "identity.source_repository_commit": field(
            "BOUND",
            {
                "repository": REPOSITORY, "branch": BRANCH, "commit_sha": COMMIT, "tree_sha": TREE,
                "archive_sha256": ARCHIVE_SHA256, "archive_size_bytes": ARCHIVE_BYTES,
                "tree_manifest": "SCIENCECLAW_SOURCE_TREE_MANIFEST_V4.json", "tree_manifest_sha256": manifest_hash,
                "file_count": 2122, "total_file_bytes": 106818041,
            },
            "The paper-linked public branch commit, full tree and deterministic archive are exact.",
            "This commit includes public prior-result prefixes and tracked bytecode; it is not itself a clean candidate seed or runtime identity.",
            "Build a separately hashed filtered seed excluding benchmarks/, categoryscienceclaw/HEA/ and tracked bytecode before any candidate access.",
        ),
        "inputs.candidate_visible_case_bytes": field(
            "BLOCKING", None,
            "No exact P5 candidate-visible topic/case packet, source corpus, allowed evidence or checksums are selected.",
            "A free-form topic string and public source-bundled examples are not a matched P5 case.",
            "Author or obtain one rights-cleared P5 case satisfying P5_C6_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json.",
        ),
        "model_provider.fallbacks": field(
            "BLOCKING", None,
            "Released source has multiple automatic fallbacks: deep-to-simple investigation, coherence-shield-to-direct calls, Hugging Face text-to-chat calls, rule/keyword reasoning and skill-selection fallbacks, parameter retries, and per-package install continuation.",
            "No native flag closes all fallback behavior; silently declaring an empty list would misdescribe the released method.",
            "Create a separately named source patch or upstream release that aborts on every fallback, then freeze and hash its exact no-switch semantics before outcomes.",
        ),
        "model_provider.primary": field(
            "BLOCKING", None,
            "Defaults permit OpenAI, Anthropic or Hugging Face and mutable environment/config values; selected skills can add other model or scientific-service roles.",
            "Backend, model snapshot, endpoint, tokenizer, context, temperature and role/capability mapping remain unknown.",
            "Bind one exact primary identity for every LLM/tool role and forbid all switches under a separately identified method if source changes are required.",
        ),
        "resources.calls_tokens_usd": field(
            "BLOCKING", None,
            "Source exposes per-call max_tokens values but no aggregate hard stop across reasoning, retry, reflection, peer review, tools, services or recursive needs.",
            "Per-call output limits are not calls/input tokens/USD budgets and may omit tool/service costs.",
            "Add provider-reconciled aggregate hard stops across every LLM, API, scheduler and laboratory/tool service.",
        ),
        "resources.retry_network": field(
            "BLOCKING", None,
            "Native code performs network searches, provider/service/API calls, package installs, optional posting, retries and possible remote job submission without a frozen endpoint allowlist or global retry ceiling.",
            "--dry-run prevents posting only; it does not disable investigation network access, provider calls, skill retries or dynamic installation.",
            "Preinstall offline dependencies, forbid asynchronous remote jobs and posting, and bind a deny-by-default endpoint/DNS/TLS/retry policy.",
        ),
        "resources.wallclock": field(
            "BOUND",
            {"enforcer": "p5_c6_fail_closed_runner.py", "enforcer_sha256": runner_hash, "whole_run_seconds": 21600, "termination_grace_seconds": 120, "timeout_terminal": "TIMEOUT/exit 124", "remote_async_jobs_forbidden": True},
            "V4 supplies an outer process-group watchdog for one future foreground scienceclaw-post invocation.",
            "The current registry still refuses with 16 blockers; process termination cannot cancel undeclared remote jobs, which are therefore forbidden rather than treated as bounded.",
            "Demonstrate timeout and cleanup only after isolated execution, task/tool selection and deny-by-default network bindings close.",
        ),
        "rights.container_and_generated_artifacts": field(
            "BLOCKING", None,
            "No content-addressed image/SBOM or publication/retention disposition exists for drafts, artifacts, journals, graphs, attestations, model outputs, figures, code or service-derived content.",
            "Root source rights do not close dependency, container, generated-output or third-party-content rights.",
            "Freeze the complete image/SBOM/notices and a generated-artifact custody, retention and redistribution policy.",
        ),
        "rights.model_provider_and_services": field(
            "BLOCKING", None,
            "No selected LLM/provider, Infinite, scientific API, database, search, scheduler or laboratory-service terms and data-processing dispositions are bound.",
            "Public endpoints and API examples are not authorization for matched evaluation use or redistribution.",
            "Bind exact service terms and data/output rights for every selected role and forbid unlisted services.",
        ),
        "rights.task_and_benchmark_content": field(
            "BLOCKING", None,
            "The repository contains 334 skill directories but only four nested component licence files; external datasets, papers, database results and one P5 case are unselected. Public prior-result prefixes are not fresh benchmark authority.",
            "Root Apache source licensing does not by itself establish reuse rights for all fetched content, databases, services or protected evaluation material.",
            "Select a minimal rights-cleared skill/content set and exact candidate-visible/protected-case receipts.",
        ),
        "runtime.compute": field(
            "BLOCKING", None,
            "Selected skills can use subprocesses, local code, GPUs, HPC/schedulers or external services; no aggregate CPU, RAM, GPU, PID, disk, parallelism or remote-work cap is frozen.",
            "psutil detection and per-tool defaults are observations, not hard enforcement.",
            "Bind cgroup/disk/PID/GPU limits and prohibit remote/asynchronous execution unless separately metered and cancelable.",
        ),
        "runtime.container_or_environment": field(
            "BLOCKING", None,
            "No digest-pinned base image, OS package set, Python build, architecture, tool binary set, credential surface or complete SBOM is frozen.",
            "The installer clones/pulls mutable source and resolves network packages at run time.",
            "Build a filtered, offline, content-addressed environment from a resolved lock and freeze every tool binary and credential mount.",
        ),
        "runtime.dependency_lock": field(
            "BLOCKING", {"audit": "SCIENCECLAW_DEPENDENCY_DECLARATIONS_V4.json", "classification": "NOT_A_LOCK"},
            "No common lockfile exists; core/full requirements have 9/112 declarations and zero exact pins; the 60-key lazy map names 96 unversioned packages and continues after installation failures.",
            "A hashed declaration list does not identify resolved transitive artifacts or prove that all selected skills installed successfully.",
            "Resolve one platform-specific hash-complete lock for the exact selected skill set and reproduce an offline fail-fast install.",
        ),
        "runtime.task_environment": field(
            "BLOCKING", None,
            "Agent profile, topic-to-case adapter, exact skills, tool parameters, data revisions, seeds, memory/artifact reset, dry-run draft path and service revisions are unbound.",
            "ScienceClaw selection and fallback behavior can change the executed scientific workflow for the same topic.",
            "Freeze one complete profile/topic/skill/tool/data/reset manifest and exclude source-bundled prior outcomes before candidate access.",
        ),
    }


def main() -> None:
    if not (UPSTREAM / ".git").exists():
        raise SystemExit(f"missing upstream clone: {UPSTREAM}")
    manifest = source_tree_manifest()
    write_json("SCIENCECLAW_SOURCE_TREE_MANIFEST_V4.json", manifest)
    manifest_hash = sha(HERE / "SCIENCECLAW_SOURCE_TREE_MANIFEST_V4.json")
    deps = dependency_declarations()
    write_json("SCIENCECLAW_DEPENDENCY_DECLARATIONS_V4.json", deps)

    parser_hash = sha(HERE / "p5_c6_native_parser.py")
    runner_hash = sha(HERE / "p5_c6_fail_closed_runner.py")
    fields = make_fields(parser_hash, runner_hash, manifest_hash)
    bound = sorted(k for k, v in fields.items() if v["status"] == "BOUND")
    blocking = sorted(k for k, v in fields.items() if v["status"] != "BOUND")
    if len(fields) != 21 or len(bound) != 5 or len(blocking) != 16:
        raise RuntimeError((len(fields), len(bound), len(blocking)))
    registry = {
        "schema_version": "orion.p5.c6.scienceclaw-field-registry.v4", "arm_id": ARM_ID,
        "fields": fields, "required_field_count": 21, "bound_field_count": 5,
        "blocking_field_count": 16, "bound_fields": bound, "blocking_fields": blocking,
        "execution_ready": False, "native_selector_supported": False,
        "panel_confirmatory_ready_arms": 0, "panel_required_arms": 6, "terminal": TERMINAL,
    }
    write_json("P5_C6_V4_FIELD_REGISTRY.json", registry)

    write_json("P5_C6_V4_EXECUTION_BINDING_PROTOCOL.json", {
        "schema_version": "orion.p5.c6.execution-binding-protocol.v4", "protocol_id": "P5.C6.SCIENCECLAW.EXECUTION.BINDING.V4", "arm_id": ARM_ID,
        "scope": "OUTCOME_BLIND_PUBLIC_SOURCE_AND_PREFLIGHT_ONLY", "source": {"repository": REPOSITORY, "branch": BRANCH, "commit_sha": COMMIT, "tree_sha": TREE},
        "forbidden": ["model execution", "scientific-tool execution", "benchmark execution", "protected scorer access", "protected payload decoding", "prior-outcome payload decoding", "performance inference", "P5 singleton emission"],
        "admissible_v4_actions": ["source-name/size/hash census", "source-code inspection", "structural parser fixture", "protected-key refusal fixture", "fail-closed registry preflight", "checksums"],
        "release_gate": {"required_bound_fields": 21, "current_bound_fields": 5, "current_blockers": 16, "native_selector_supported": False, "released": False},
    })
    write_json("P5_C6_V4_NATIVE_OUTPUT_SCHEMA.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "orion.p5.c6.scienceclaw-native-terminal.v4", "type": "object", "additionalProperties": False,
        "required": ["schema_version", "arm_id", "adapter_terminal", "native_terminal", "draft_sha256", "draft_size_bytes", "top_level_keys", "investigation_result_key_count", "structural_list_counts", "scientific_payload_values_retained", "native_exit_status_is_sufficient", "raw_native_singleton_licences", "performance_inference", "source_native_caveat"],
        "properties": {
            "schema_version": {"const": "orion.p5.c6.scienceclaw-native-terminal.v4"}, "arm_id": {"const": ARM_ID},
            "adapter_terminal": {"const": "UNRESOLVED"}, "native_terminal": {"const": "NATIVE_DRY_RUN_DRAFT_RECORDED"},
            "draft_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}, "draft_size_bytes": {"type": "integer", "minimum": 1},
            "top_level_keys": {"type": "array", "items": {"type": "string"}}, "investigation_result_key_count": {"type": "integer", "minimum": 0},
            "structural_list_counts": {"type": "object", "additionalProperties": {"type": ["integer", "null"]}},
            "scientific_payload_values_retained": {"const": False}, "native_exit_status_is_sufficient": {"const": False},
            "raw_native_singleton_licences": {"const": 0}, "performance_inference": {"const": "FORBIDDEN"}, "source_native_caveat": {"type": "string"},
        },
    })
    write_json("P5_C6_V4_NATIVE_TERMINAL_RULES.json", {
        "schema_version": "orion.p5.c6.native-terminal-rules.v4", "arm_id": ARM_ID,
        "rules": [
            {"condition": "valid strict native dry-run draft shape with no prohibited key", "native_terminal": "NATIVE_DRY_RUN_DRAFT_RECORDED", "adapter_terminal": "UNRESOLVED"},
            {"condition": "protected/gold/hidden/holdout/final-test key family present", "native_terminal": "INPUT_REFUSED", "adapter_terminal": "NO_OUTPUT"},
            {"condition": "invalid JSON, wrong shape or missing nonempty candidate-visible fields", "native_terminal": "INPUT_REFUSED", "adapter_terminal": "NO_OUTPUT"},
        ],
        "draft_or_process_success_is_p5_selector": False, "raw_native_singleton_licences": 0,
        "successor_rule": "Any ScienceClaw revision-proposal selector is a separately named material successor, not this native adapter.",
    })
    write_json("P5_C6_V4_WRITE_SURFACE_SCHEMA.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "orion.p5.c6.write-surface.v4", "type": "object", "additionalProperties": False,
        "required": ["source_read_only", "case_read_only", "isolated_home", "scratch_root", "output_root", "network_policy", "remote_async_jobs_allowed", "devices_allowed", "reset_receipt_sha256"],
        "properties": {"source_read_only": {"const": True}, "case_read_only": {"const": True}, "isolated_home": {"const": True}, "scratch_root": {"type": "string"}, "output_root": {"type": "string"}, "network_policy": {"const": "DENY_BY_DEFAULT_EXACT_ALLOWLIST"}, "remote_async_jobs_allowed": {"const": False}, "devices_allowed": {"const": False}, "reset_receipt_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}},
        "current_status": "BLOCKING_UNDEMONSTRATED",
    })
    write_json("P5_C6_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json", {
        "schema_version": "orion.p5.c6.candidate-visible-case-requirements.v4", "arm_id": ARM_ID,
        "required": ["case_id", "topic_bytes_sha256", "allowed_source_corpus_manifest_sha256", "allowed_skills_and_tool_parameters", "candidate_visible_rights_receipt_sha256", "source_filtered_seed_sha256", "outcome_prefix_exclusion_receipt_sha256", "protected_keys_absent", "no_prior_outcome_payloads", "no_reference_answers", "no_protected_scores"],
        "excluded_source_prefixes": ["benchmarks/", "categoryscienceclaw/HEA/"], "current_case": None, "current_status": "BLOCKING",
    })
    write_json("P5_C6_V4_CUSTODY_HANDOFF_SCHEMA.json", {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "orion.p5.c6.custody-handoff.v4", "type": "object", "additionalProperties": False,
        "required": ["candidate_freeze_sha256", "external_scorer_code_sha256", "protected_panel_manifest_sha256", "freshness_nonce", "one_shot", "feedback_to_candidate", "signed_attestation", "terminal_only_return"],
        "properties": {"candidate_freeze_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}, "external_scorer_code_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}, "protected_panel_manifest_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}, "freshness_nonce": {"type": "string", "minLength": 16}, "one_shot": {"const": True}, "feedback_to_candidate": {"const": False}, "signed_attestation": {"type": "string", "minLength": 1}, "terminal_only_return": {"const": True}},
        "current_status": "CANNOT_CHECK",
    })
    write_json("P5_C6_V4_RESOURCE_REGISTRY.json", {
        "schema_version": "orion.p5.c6.resource-registry.v4", "arm_id": ARM_ID,
        "wallclock": {"whole_run_seconds": 21600, "termination_grace_seconds": 120, "remote_async_jobs_allowed": False, "status": "BOUND"},
        "model_provider": {"primary": None, "fallbacks": None, "status": "BLOCKING", "native_fallbacks_detected": ["deep-to-simple investigation", "coherence-shield-to-direct", "Hugging Face text-to-chat", "rule/keyword reasoning", "skill-selection", "parameter retry"]},
        "calls_tokens_usd": {"status": "BLOCKING"}, "retry_network": {"status": "BLOCKING"}, "compute": {"status": "BLOCKING"}, "dependency_lock": {"status": "BLOCKING", "audit": "SCIENCECLAW_DEPENDENCY_DECLARATIONS_V4.json"},
    })
    write_json("P5_C6_V4_SOURCE_RIGHTS_MANIFEST.json", {
        "schema_version": "orion.p5.c6.source-rights-manifest.v4", "arm_id": ARM_ID,
        "root_licence": {"path": "LICENSE", "sha256": sha(UPSTREAM / "LICENSE"), "spdx": "Apache-2.0"},
        "paper_licence": "CC-BY-NC-ND-4.0", "package_json_declared_license": "MIT", "source_metadata_consistent": False,
        "direct_skill_directories": 334, "files_under_skills": 1930, "nested_component_licence_files": 4,
        "nested_component_licence_paths": ["skills/document-skills/docx/LICENSE.txt", "skills/document-skills/pdf/LICENSE.txt", "skills/document-skills/pptx/LICENSE.txt", "skills/document-skills/xlsx/LICENSE.txt"],
        "source_execution_authorized_by_packet": False, "task_content_rights_closed": False, "service_rights_closed": False, "generated_artifact_rights_closed": False,
        "rights_caveat": "Root source licensing does not by itself close fetched datasets/papers, databases, APIs, model/provider terms, scientific tools, schedulers/labs, containers or generated outputs.",
    })

    failures = [
        ("SCIENCECLAW_SELECTOR_UNSUPPORTED", "Native drafts/artifacts/open needs/statuses do not select a P5 responsibility class.", "The released method is a discovery/provenance substrate, not a revision-proposal selector.", "All native fibres remain UNRESOLVED; raw singleton licences stay zero.", "Preregister a separately named selector successor with input-native certificate and exclusive-front action proof."),
        ("SOURCE_PRIOR_OUTCOME_PREFIXES", "The paper-linked commit includes benchmarks/ and categoryscienceclaw/HEA/ prior-result paths.", "The branch commit itself adds HEA results.", "13 files / 106755 bytes must be excluded before candidate access; payload values were not decoded or displayed.", "Build and hash a filtered candidate seed with an exclusion receipt."),
        ("TRACKED_BYTECODE", "The authoritative tree tracks 374 __pycache__/.pyc files totaling 3400553 bytes.", "Generated bytecode was committed alongside source.", "Interpreter/build provenance is not reconstructible from source declarations alone; bytecode must not enter the candidate seed.", "Exclude bytecode and rebuild only from the frozen source and hash-complete environment."),
        ("DRY_RUN_NOT_OUTCOME_FREE", "scienceclaw-post --dry-run still runs the investigation and writes a full draft.", "The flag suppresses Infinite posting after model/tool execution rather than simulating execution.", "No native dry-run command was executed in V4.", "Use only after all model/tool/data/rights/resource bindings close; never call it an outcome-free smoke."),
        ("FALLBACKS_OPEN", "Native fallback behavior cannot be closed by a released CLI flag.", "Multiple automatic reasoning/provider/workflow/installation fallbacks are source-native.", "model_provider.fallbacks remains BLOCKING; silently emptying it would change/misdescribe the method.", "Require an upstream release or separately named fail-fast successor identity."),
        ("DEPENDENCIES_UNRESOLVED", "No resolved dependency lock exists.", "Core/full requirements have zero exact pins and the lazy installer resolves bare names at run time while continuing after failures.", "Runtime and scientific-tool identity remain CANNOT_CHECK.", "Create a hash-complete platform-specific selected-skill lock and offline fail-fast build."),
        ("WRITE_AND_NETWORK_SURFACE_OPEN", "Native execution can mutate ~/.scienceclaw, run subprocesses, install packages and contact model/scientific/Infinite/remote services.", "The released runtime is designed for open-world recursive discovery.", "No isolated write/network/device/scheduler receipt exists.", "Demonstrate a disposable deny-by-default executor on the exact selected tool set."),
        ("RIGHTS_ROOTS_OPEN", "Task/content/service/container/generated-output rights are not closed.", "Root source rights and public availability do not cover every external root.", "Execution and publication reuse remain unauthorized by this packet.", "Obtain root-specific rights receipts before any substantive case."),
        ("PROTECTED_CUSTODY_ABSENT", "No external scorer, one-shot barrier or fresh panel attestation exists.", "Candidate-side artifacts, audits and public benchmarks are not independent custody.", "Performance and superiority remain CANNOT_CHECK.", "Obtain signed independent custody after candidate freeze."),
        ("STRUCTURAL_SMOKE_NOT_SCIENCE", "Only an authored native-shaped draft and prohibited-key fixture are parsed.", "No model, tool, corpus, benchmark or protected outcome is executed.", "Smoke establishes parser/refusal/preflight conformance only.", "The first scientific discriminator is a rights-cleared case under complete execution and custody bindings."),
    ]
    entries = [{"id": i, "failure": f, "cause": c, "residual": r, "next_discriminator": n, "status": "PRESERVED"} for i, f, c, r, n in failures]
    write_json("P5_C6_V4_NEGATIVE_LEDGER.json", {"schema_version": "orion.p5.c6.negative-ledger.v4", "arm_id": ARM_ID, "entries": entries})
    lines = ["# P5 C6 ScienceClaw V4 negative ledger", "", "Every adverse result is retained; none is converted into a performance or singleton claim.", ""]
    for x in entries:
        lines += [
            f"## {x['id']}",
            "",
            f"- **Failure:** {x['failure']}",
            f"- **Cause:** {x['cause']}",
            f"- **Residual:** {x['residual']}",
            f"- **Next discriminator:** {x['next_discriminator']}",
            "",
        ]
    (HERE / "P5_C6_V4_NEGATIVE_LEDGER.md").write_text("\n".join(lines), encoding="utf-8")

    result = {
        "schema_version": "orion.p5.c6.scienceclaw-execution-binding-result.v4", "protocol_id": "P5.C6.SCIENCECLAW.EXECUTION.BINDING.V4", "arm_id": ARM_ID,
        "authority": "PUBLIC_SOURCE_IDENTITY_AND_OUTCOME_BLIND_PREFLIGHT_ONLY",
        "execution": {"c6_executed": False, "c6_execution_ready": False, "native_scienceclaw_smoke": "CANNOT_CHECK", "panel_confirmatory_ready_arms": 0, "panel_required_arms": 6},
        "v4_repairs": {"c6_bound_fields": 5, "c6_blocking_fields": 16, "v3_bound_fields": 3, "v3_blocking_fields": 18, "v3_to_v4_blocker_delta": -2, "retained_bound_identity_fields": ["identity.native_entrypoint_bytes", "identity.source_license_bytes", "identity.source_repository_commit"], "newly_bound_fields": ["adapter.native_parser_binding", "resources.wallclock"], "model_provider_fallbacks_adjudication": "BLOCKING_NATIVE_FALLBACKS_CANNOT_BE_CLOSED_WITH_RELEASED_CLI"},
        "material_discoveries": {"source_tree_files": 2122, "source_tree_bytes": 106818041, "excluded_prior_outcome_prefix_files": 13, "excluded_prior_outcome_prefix_bytes": 106755, "prior_outcome_payload_values_decoded_or_displayed": False, "tracked_pycache_files": 374, "tracked_pycache_bytes": 3400553, "dependency_lock_present": False, "core_declarations": 9, "core_exact_pins": 0, "full_declarations": 112, "full_exact_pins": 0, "dynamic_skill_dependency_keys": 60, "dynamic_unique_unversioned_packages": 96, "native_dry_run_is_outcome_free": False, "native_selector_supported": False},
        "preserved_boundaries": {"raw_native_singleton_licences": 0, "scienceclaw_supported_singletons": 0, "all_native_scienceclaw_fibres": "UNRESOLVED", "v3_synthetic_cases": 231, "v3_supported_singleton_case_records": 40, "v3_supported_singleton_fibres": 20, "v3_unresolved_case_records": 191, "smoke_fixture_is_substantive_p5_case": False},
        "preserved_claims": {"H1": "CANNOT_CHECK", "H2": "CANNOT_CHECK", "H3": "CANNOT_CHECK", "H4": "CANNOT_CHECK", "preservation": "CANNOT_CHECK", "fresh_transfer": "CANNOT_CHECK", "harm": "CANNOT_CHECK", "performance": "CANNOT_CHECK", "superiority": "CANNOT_CHECK", "top_tier_publication_readiness": "NOT_ESTABLISHED"},
        "next_discriminator": "First preregister a separately named fail-fast ScienceClaw revision-proposal successor, then build a prior-outcome-free filtered seed and hash-complete offline environment for one rights-cleared case; bind all model/tool/service/resource/rights/custody fields and require 6/6 panel readiness before protected scoring.",
        "terminal": TERMINAL,
    }
    write_json("P5_C6_V4_RESULT.json", result)
    (HERE / "TERMINAL_V4.txt").write_text(TERMINAL + "\n", encoding="utf-8")

    report = f"""# P5 C6 ScienceClaw execution-binding V4

## Terminal

`{TERMINAL}`

This packet is an outcome-blind public-source preflight, not a comparator result.
No ScienceClaw investigation, model, skill, scientific service, benchmark,
protected scorer, prior-result payload, gold/reference value or performance
table was executed or decoded. Source files were cryptographically hashed;
prior-result paths were censused by name/size/hash only.

## Exact 21-field census

V4 binds **5/21** fields and retains **16/21 blocking**. The two new bindings
are a terminal-preserving native draft parser and an outer process-group
wallclock. Confirmatory panel readiness remains **0/6**.

| Bound field | Exact evidence |
|---|---|
| `identity.source_repository_commit` | `{REPOSITORY}` branch `{BRANCH}` at `{COMMIT}`; tree `{TREE}`; 2,122 files / 106,818,041 bytes; uncompressed archive SHA-256 `{ARCHIVE_SHA256}` |
| `identity.source_license_bytes` | root `LICENSE` SHA-256 `{sha(UPSTREAM / "LICENSE")}`, Apache-2.0; package.json separately says MIT, so metadata consistency is false |
| `identity.native_entrypoint_bytes` | exact `setup.py`, `bin/scienceclaw-post`, post generator, deep investigator, LLM client and artifact-store hashes |
| `adapter.native_parser_binding` | strict dry-run draft-shape parser; protected key families refused before JSON decoding; scientific values not retained; every admissible draft maps to `UNRESOLVED` |
| `resources.wallclock` | 21,600-second foreground process-group cap plus 120-second termination grace; remote asynchronous jobs forbidden |

The 16 blockers are native write/isolation; exact case; all native fallbacks;
primary model/tool/service identities; calls/tokens/USD; retry/network;
compute; content-addressed environment; dependency lock; task/profile/skill/data
manifest; three rights roots; and three independent-custody fields.

## Material authoritative-source results

The exact paper-linked branch commit is valid. It also contains two prior-result
prefixes: `benchmarks/` (4 files / 85,993 bytes) and
`categoryscienceclaw/HEA/` (9 files / 20,762 bytes). Their 13 payloads were not
decoded or displayed. A future candidate seed must exclude both prefixes
before candidate access. The tree also tracks 374 `__pycache__`/`.pyc` files
(3,400,553 bytes); these are excluded from any clean rebuild.

The root Apache-2.0 licence bytes are exact, but `package.json` declares MIT.
There are 334 direct skill directories, 1,930 files under `skills/`, and four
nested component licence files. Root source licensing does not close fetched
papers/datasets, scientific databases/APIs, model/provider terms, schedulers or
labs, containers, or generated artifacts.

## Native semantic result: no selector

`scienceclaw-post --dry-run` is not an outcome-free smoke: it first runs the
investigation and only suppresses Infinite posting, then writes a full draft.
V4 therefore did **not** run it. The structural parser was tested only on an
authored native-shaped fixture and returns no scientific values.

A valid draft, immutable artifact, content hash, open need, status, mutation or
audit is provenance/representation evidence. None is a native P5 revision
choice. The parser therefore licenses zero raw singletons and maps every
admissible native fibre to `UNRESOLVED`. A ScienceClaw revision-proposal module
would be a separately named material successor, not an adapter relabel.

## Open fallback and dependency results

`model_provider.fallbacks` remains blocking rather than being optimistically
set to an empty list. Released code includes deep-to-simple investigation,
coherence-shield-to-direct, Hugging Face text-to-chat, rule/keyword reasoning,
skill-selection and parameter fallbacks; the lazy dependency installer also
continues after package failures. No released CLI flag closes all behavior.

No resolved dependency lock exists. `requirements.txt` has 9 declarations and
zero exact pins; `requirements-full.txt` has 112 and zero exact pins. The
60-key lazy map references 96 unique unversioned package names and resolves
selected dependencies at run time. Hashing these declarations is not a lock.

## Outcome-blind smoke boundary

- authored native-shaped draft: parser exit 0, native draft-recorded,
  adapter `UNRESOLVED`, raw singleton licences 0;
- injected synthetic `protected_score` key: refused before JSON decoding,
  exit 2;
- registry preflight: exit 3, 16 blockers, native execution false;
- full ScienceClaw smoke: `CANNOT_CHECK` because `--dry-run` would execute
  models/tools/services and the method/rights/resources/custody are unbound.

These are interface checks only, not discovery quality or performance evidence.
H1--H4, preservation, fresh transfer, harm, performance and superiority remain
`CANNOT_CHECK`; top-tier readiness is not established.

## Next discriminator

First preregister a separately named fail-fast revision-proposal successor that
aborts rather than falling back and proves an input-native class certificate
plus exclusive-front action. Then build a filtered prior-outcome-free source
seed and hash-complete offline environment for one rights-cleared case; bind
all model/tool/service/resource/rights/custody fields. Protected scoring remains
forbidden until all six arms satisfy the same matched panel.
"""
    (HERE / "SCIENTIFIC_REPORT_V4.md").write_text(report, encoding="utf-8")
    readme = f"""# P5 C6 ScienceClaw execution-binding V4

Outcome-blind public-source preflight for `{ARM_ID}` at `{COMMIT}`.

- No native ScienceClaw/model/tool/benchmark/protected job was run.
- Exact readiness: **5/21 BOUND**, **16/21 blocking**, **0/6 panel ready**.
- ScienceClaw has **zero native P5 singleton licences**; all fibres remain `UNRESOLVED`.
- Public prior-result prefixes were hashed/censused but their payload values were not decoded.
- `--dry-run` still executes the investigation and was not used as a smoke.

Read `SCIENTIFIC_REPORT_V4.md`, `P5_C6_V4_FIELD_REGISTRY.json`, and
`P5_C6_V4_NEGATIVE_LEDGER.md`.

Outcome-free verification after cloning the exact branch into `.source-audit`:

```text
rtk python build_p5_c6_v4_freeze.py
rtk python p5_c6_v4_validator.py
rtk sha256sum -c SHA256SUMS
```

No pytest or repository CI belongs to this lane.
"""
    (HERE / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
