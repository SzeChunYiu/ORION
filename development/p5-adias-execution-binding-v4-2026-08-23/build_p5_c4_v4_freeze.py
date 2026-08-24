#!/usr/bin/env python3
"""Build the outcome-blind P5 C4 ADIAS V4 execution-binding packet."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
UPSTREAM = HERE.parents[2] / "upstream" / "adias-fbcf0c73"
FROZEN_AT = "2026-08-23T18:34:25Z"
ARM_ID = "C4_ISSUE_CENTRIC_OPTIMIZATION__ADIAS"
COMMIT = "fbcf0c73d12d30a4ee0d13c2e64b4c40d00b2993"
TREE = "98fc19e691c31b635ec432b6240db775a9527fd0"
ARCHIVE_SHA256 = "472e2ef2258c764b563b07be725a82de80df15bd617259fd839f894b8c602216"
ARCHIVE_BYTES = 86_681_600
REPOSITORY = "https://github.com/scylj1/adias"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(name: str, value: Any) -> None:
    (HERE / name).write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def source_tree_manifest() -> dict[str, Any]:
    output = subprocess.check_output(
        ["git", "-C", str(UPSTREAM), "ls-tree", "-r", "--full-tree", "--long", COMMIT],
        text=True,
    )
    entries = []
    total_bytes = 0
    for raw in output.splitlines():
        header, path_text = raw.split("\t", 1)
        mode, object_type, git_blob, size_text = header.split()
        path = UPSTREAM / path_text
        size = int(size_text)
        total_bytes += size
        entries.append(
            {
                "git_blob_sha1": git_blob,
                "mode": mode,
                "object_type": object_type,
                "path": path_text,
                "sha256": sha(path),
                "size_bytes": size,
            }
        )
    actual_head = subprocess.check_output(
        ["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True
    ).strip()
    actual_tree = subprocess.check_output(
        ["git", "-C", str(UPSTREAM), "rev-parse", "HEAD^{tree}"], text=True
    ).strip()
    if actual_head != COMMIT or actual_tree != TREE:
        raise RuntimeError(f"upstream identity mismatch: {actual_head} {actual_tree}")
    return {
        "schema_version": "orion.p5.c4.adias-source-tree-manifest.v4",
        "arm_id": ARM_ID,
        "repository": REPOSITORY,
        "commit_sha": COMMIT,
        "tree_sha": TREE,
        "commit_author_date": "2026-08-21T19:50:40+08:00",
        "commit_committer_date": "2026-08-21T19:50:40+08:00",
        "deterministic_git_archive": {
            "command_description": "git archive --format=tar --prefix=adias-fbcf0c73/ HEAD",
            "sha256": ARCHIVE_SHA256,
            "size_bytes": ARCHIVE_BYTES,
            "archive_retained": False,
        },
        "file_count": len(entries),
        "total_file_bytes": total_bytes,
        "entries": entries,
    }


def dependency_declarations() -> dict[str, Any]:
    pyproject = tomllib.loads((UPSTREAM / "pyproject.toml").read_text(encoding="utf-8"))
    requirements = [
        line.strip()
        for line in (UPSTREAM / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    requirements_dev = [
        line.strip()
        for line in (UPSTREAM / "requirements_dev.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    project = pyproject["project"]
    optional = project.get("optional-dependencies", {})
    vcs = [line for line in requirements if "git+" in line]
    unpinned_vcs = [line for line in vcs if ".git@" not in line]
    return {
        "schema_version": "orion.p5.c4.adias-dependency-declarations.v4",
        "arm_id": ARM_ID,
        "classification": "SOURCE_DECLARATIONS_NOT_A_TRANSITIVE_LOCK",
        "lock_present_in_authoritative_tree": False,
        "lock_status": "BLOCKING",
        "source_files": {
            "pyproject.toml": {"sha256": sha(UPSTREAM / "pyproject.toml")},
            "requirements.txt": {"sha256": sha(UPSTREAM / "requirements.txt")},
            "requirements_dev.txt": {"sha256": sha(UPSTREAM / "requirements_dev.txt")},
            "Dockerfile": {"sha256": sha(UPSTREAM / "Dockerfile")},
        },
        "python_requirement": project["requires-python"],
        "build_system_requires": pyproject["build-system"]["requires"],
        "project_dependencies": project["dependencies"],
        "project_optional_dependencies": optional,
        "project_dependency_declaration_count": len(project["dependencies"]),
        "optional_dependency_declaration_count": sum(len(values) for values in optional.values()),
        "requirements_declarations": requirements,
        "requirements_declaration_count": len(requirements),
        "requirements_dev_declarations": requirements_dev,
        "requirements_dev_declaration_count": len(requirements_dev),
        "vcs_declarations": vcs,
        "vcs_declaration_count": len(vcs),
        "unpinned_vcs_declarations": unpinned_vcs,
        "unpinned_vcs_declaration_count": len(unpinned_vcs),
        "material_conflicts": [
            "requirements.txt declares dotenv==0.9.9 while Dockerfile installs python-dotenv==1.1.0 and pyproject declares python-dotenv>=1.1.0,<2",
            "requirements.txt leaves numpy unversioned while pyproject constrains numpy>=1.26,<3 and Dockerfile leaves numpy unversioned",
            "tau-bench and AgentGym are unpinned Git dependencies in both requirements.txt/pyproject; Genesis and baba-is-ai are also unpinned Git dependencies in requirements.txt",
            "Dockerfile base image python:3.12-bullseye is a mutable tag rather than a digest",
        ],
        "reason_not_a_lock": (
            "Top-level ranges/pins and Docker RUN declarations do not determine one transitive graph, "
            "wheel/source identities, hashes, platform markers, VCS commits, or base-image bytes."
        ),
    }


def field(
    status: str,
    binding: Any,
    cause: str,
    residual: str,
    next_discriminator: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "binding": binding,
        "cause": cause,
        "residual": residual,
        "next_discriminator": next_discriminator,
    }


def make_fields(parser_hash: str, runner_hash: str, tree_manifest_hash: str) -> dict[str, Any]:
    return {
        "adapter.isolated_write_surface": field(
            "BLOCKING",
            None,
            "Native ADIAS selects DOCKER_HOST or /var/run/docker.sock, builds and runs host-networked containers, injects API keys, and permits root meta-agent bash/edit activity; no disposable dedicated daemon/executor receipt exists.",
            "The V4 gate describes a required isolated-daemon boundary but cannot self-attest that an executor provides it.",
            "Provision a disposable Linux executor plus dedicated rootless Docker daemon under the scratch root; demonstrate no writes, containers, images, caches, or sockets escape the declared surface.",
        ),
        "adapter.native_parser_binding": field(
            "BOUND",
            {
                "path": "p5_c4_native_parser.py",
                "sha256": parser_hash,
                "output_schema": "P5_C4_V4_NATIVE_OUTPUT_SCHEMA.json",
                "input": "one native ADIAS gen_<id>/ directory containing metadata.json and zero or more candidate-visible *_eval[/_val]/report.json files",
                "protected_and_final_test_policy": "REFUSE_BEFORE_OUTCOME_RETENTION",
                "native_scores_retained": False,
                "raw_native_singleton_licences": 0,
            },
            "ADIAS has no versioned terminal schema and process exit zero is not sufficient; V4 binds a strict structural parser to the frozen writers.",
            "Parser terminals remain UNRESOLVED for P5 responsibility/performance.",
            "Use only under external custody after exact report provenance is bound.",
        ),
        "custody.external_protected_scorer": field(
            "BLOCKING", None,
            "No independent scorer identity, code digest, signing key, or return schema is supplied.",
            "Native ADIAS report writers are candidate-side evaluation utilities, not an external protected scorer.",
            "Obtain a signed external scorer attestation with exact code/data hashes and a minimal terminal-only return contract.",
        ),
        "custody.one_shot_no_feedback_barrier": field(
            "BLOCKING", None,
            "No independent custodian attests a one-shot no-feedback barrier.",
            "ADIAS is explicitly iterative and learns from evaluation artifacts; native final_test_summary.json is written in the same run.",
            "Bind an external one-shot custodian that withholds protected inputs/outcomes until the candidate terminal is frozen.",
        ),
        "custody.protected_panel_freshness": field(
            "BLOCKING", None,
            "No protected panel identity, freshness nonce, selection receipt, or independence attestation is available.",
            "Bundled train/val/test declarations do not establish the P5 protected panel.",
            "Bind a fresh six-arm panel manifest under independent custody.",
        ),
        "identity.native_entrypoint_bytes": field(
            "BOUND",
            {
                "pyproject_sha256": sha(UPSTREAM / "pyproject.toml"),
                "console_scripts": [
                    "adias-eval = domains.run_eval:main",
                    "adias-harness = domains.harness:main",
                    "adias-report = domains.report:main",
                    "adias-run-meta-agent = run_meta_agent:main",
                ],
                "formal_outer_entrypoint": "python -u generate_loop.py",
                "root_wrapper_sha256": sha(UPSTREAM / "generate_loop.py"),
                "implementation_sha256": sha(UPSTREAM / "src/generate_loop.py"),
                "meta_wrapper_sha256": sha(UPSTREAM / "run_meta_agent.py"),
                "meta_implementation_sha256": sha(UPSTREAM / "src/run_meta_agent.py"),
                "background_scripts_admissible": False,
            },
            "Exact entrypoint bytes and released command surfaces are present.",
            "Entrypoint identity does not select a task, model, dependency graph, or environment.",
            "Carry these hashes into a complete execution manifest.",
        ),
        "identity.source_license_bytes": field(
            "BOUND",
            {
                "path": "LICENSE.md",
                "sha256": sha(UPSTREAM / "LICENSE.md"),
                "spdx": "CC-BY-NC-SA-4.0",
                "noncommercial_restriction": True,
                "sharealike_condition": True,
            },
            "Exact root licence bytes are present.",
            "The root licence cannot establish that acknowledged third-party benchmark/data/dependencies were sublicensable by the repository licensor.",
            "Maintain source attribution/noncommercial/sharealike compliance and separately close all component rights.",
        ),
        "identity.source_repository_commit": field(
            "BOUND",
            {
                "repository": REPOSITORY,
                "commit_sha": COMMIT,
                "tree_sha": TREE,
                "commit_author_date": "2026-08-21T19:50:40+08:00",
                "archive_sha256": ARCHIVE_SHA256,
                "archive_size_bytes": ARCHIVE_BYTES,
                "tree_manifest": "ADIAS_SOURCE_TREE_MANIFEST_V4.json",
                "tree_manifest_sha256": tree_manifest_hash,
                "file_count": 1578,
            },
            "The paper-linked public source identity is exact and detached.",
            "Source identity alone is not runtime, rights, or performance identity.",
            "Use only this commit/tree in a successor execution receipt.",
        ),
        "inputs.candidate_visible_case_bytes": field(
            "BLOCKING", None,
            "No exact P5 candidate-visible task/case packet, split, task identifiers, or checksum set is selected.",
            "Bundled ADIAS data and native-shaped smoke fixtures are not substantive P5 cases.",
            "Author or obtain one rights-cleared P5 case packet satisfying P5_C4_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json.",
        ),
        "model_provider.fallbacks": field(
            "BOUND",
            {
                "fallbacks": [],
                "closed_behavior": "FAIL_WITH_NATIVE_TERMINAL; DO_NOT_SWITCH_META_TASK_USER_OR_SEARCH_MODEL_OR_PROVIDER",
                "external_search": "FORCED_OFF",
                "per_role_provider_override": "FORBIDDEN",
            },
            "V4 freezes a closed empty fallback set independent of the still-unbound primary.",
            "This does not choose or authorize the primary service.",
            "Bind one model/provider/service identity and preserve this no-switch policy.",
        ),
        "model_provider.primary": field(
            "BLOCKING", None,
            "Source defaults name openai/deepseek-v4-flash, but a source default is not a provider/model/version/service binding; TauBench also has a user-simulator role.",
            "API base, model snapshot, tokenizer, context, role mapping, user simulator, and service terms remain unknown.",
            "Bind one exact model snapshot and provider endpoint for every native role, or prove a single shared binding, with no fallback.",
        ),
        "resources.calls_tokens_usd": field(
            "BLOCKING", None,
            "Source records best-effort usage after calls but provides no aggregate hard stop; cost may be absent and multiple meta/diagnostic/profile/task/user/search roles can call models.",
            "MAX_TOKENS=16384 is a per-call request, not an aggregate lock or provider-reconciled budget.",
            "Add a provider-side and local reconciled hard stop for calls, input/output tokens, and USD across all roles.",
        ),
        "resources.retry_network": field(
            "BLOCKING", None,
            "Source uses host networking for builds/runs, proxy build args, provider egress, optional web search, package/VCS downloads, and a backoff max_time of 600 seconds without a frozen endpoint allowlist.",
            "Forcing external search off and freezing empty model fallbacks does not close ordinary provider/build/network retries.",
            "Prebuild an offline image; deny network except exact provider endpoints; bind DNS/IP/TLS policy and finite retry ceilings.",
        ),
        "resources.wallclock": field(
            "BOUND",
            {
                "enforcer": "p5_c4_fail_closed_runner.py",
                "enforcer_sha256": runner_hash,
                "whole_run_seconds": 21600,
                "termination_grace_seconds": 120,
                "timeout_terminal": "TIMEOUT/exit 124",
                "native_background_scripts_forbidden": True,
                "dedicated_daemon_cleanup_required": True,
            },
            "Native code caps individual meta-agent execs at 21,600 seconds but has no whole-run cap and released scripts background the job; V4 binds a direct foreground process-group watchdog.",
            "The watchdog is never exercised on a native job in V4 because 15 fields remain blocking; isolated daemon cleanup depends on the separate write-surface field.",
            "Demonstrate timeout plus container cleanup on the rights-cleared disposable executor before execution readiness.",
        ),
        "rights.container_and_generated_artifacts": field(
            "BLOCKING", None,
            "The mutable python:3.12-bullseye base, transitive packages, VCS installs, built images, generated patches, transcripts, profiles, traces, and reports lack a complete SBOM/rights disposition.",
            "Root CC-BY-NC-SA source rights do not close third-party/container/output rights.",
            "Resolve a digest-pinned image, SBOM, licence notices, generated-artifact custody, retention, and publication permissions.",
        ),
        "rights.model_provider_and_services": field(
            "BLOCKING", None,
            "No selected model/provider/service terms, data-processing terms, or redistribution/retention disposition exists.",
            "README examples of API keys are configuration hints, not service rights.",
            "Bind service terms and authorize all meta/task/user-simulator roles before calls.",
        ),
        "rights.task_and_benchmark_content": field(
            "BLOCKING", None,
            "The tree bundles 606 ALFWorld, 863 TextCraft, 4 WebShop, and 3 ScienceWorld data files and depends on TauBench tasks, but data/ contains no component licence/NOTICE files; root CC terms cannot prove third-party grant scope.",
            "Acknowledgements and public availability are not benchmark reuse authority; the exact P5 task is also unselected.",
            "Obtain component-specific rights receipts and one rights-cleared candidate-visible P5 task/benchmark packet.",
        ),
        "runtime.compute": field(
            "BLOCKING", None,
            "Native containers set only pids_limit=256; they use host networking and set no CPU, RAM, GPU, disk, image-cache, or aggregate parallelism hard limit. Source eval_workers defaults to 10.",
            "Outer rlimits cannot account for daemon-owned containers without a demonstrated dedicated executor cgroup.",
            "Bind and demonstrate cgroup CPU/RAM/PID/disk/GPU limits covering launcher, Docker daemon, builds, and every child container.",
        ),
        "runtime.container_or_environment": field(
            "BLOCKING", None,
            "Dockerfile uses mutable python:3.12-bullseye, performs network installs, and the source has domain-specific optional build variants without image digests.",
            "No built-image digest, OS package lock, architecture, Docker/daemon version, or complete SBOM is frozen.",
            "Build offline from a resolved dependency lock and freeze image/daemon/kernel/architecture identities.",
        ),
        "runtime.dependency_lock": field(
            "BLOCKING",
            {"source_declaration_audit": "ADIAS_DEPENDENCY_DECLARATIONS_V4.json", "classification": "NOT_A_LOCK"},
            "No uv/poetry/pip-tools/conda lock or hash-complete constraints file exists; four requirements VCS dependencies are unpinned and declarations conflict.",
            "requirements.txt, pyproject ranges, requirements_dev.txt, and Docker RUN lines are source declarations, not one resolved transitive graph.",
            "Resolve Python 3.12/platform-specific artifacts with hashes and exact VCS commits, then reproduce an offline install.",
        ),
        "runtime.task_environment": field(
            "BLOCKING", None,
            "No single ADIAS domain, split, task IDs, environment implementation, seed, max turns, image variant, or case bytes are chosen for P5 C4.",
            "Six native domains have different external packages/data; source defaults and bundled fixtures are not a matched task environment.",
            "Select one rights-cleared native domain/task and freeze every environment/data/config byte and seed under a matched six-arm contract.",
        ),
    }


def main() -> None:
    if not UPSTREAM.is_dir():
        raise SystemExit(f"missing upstream clone: {UPSTREAM}")
    parser_hash = sha(HERE / "p5_c4_native_parser.py")
    runner_hash = sha(HERE / "p5_c4_fail_closed_runner.py")

    tree_manifest = source_tree_manifest()
    write_json("ADIAS_SOURCE_TREE_MANIFEST_V4.json", tree_manifest)
    tree_manifest_hash = sha(HERE / "ADIAS_SOURCE_TREE_MANIFEST_V4.json")
    write_json("ADIAS_DEPENDENCY_DECLARATIONS_V4.json", dependency_declarations())

    fields = make_fields(parser_hash, runner_hash, tree_manifest_hash)
    required_paths = list(fields)
    bound_fields = sorted(key for key, value in fields.items() if value["status"] == "BOUND")
    blocking_fields = sorted(key for key, value in fields.items() if value["status"] != "BOUND")
    if len(fields) != 21 or len(bound_fields) != 6 or len(blocking_fields) != 15:
        raise RuntimeError("unexpected 21-field census")

    registry = {
        "schema_version": "orion.p5.c4.field-registry.v4",
        "registry_id": "P5.C4.ADIAS.EXECUTION.BINDING.V4",
        "arm_id": ARM_ID,
        "frozen_at_utc": FROZEN_AT,
        "required_field_paths": required_paths,
        "fields": fields,
        "bound_fields": bound_fields,
        "blocking_fields": blocking_fields,
        "bound_field_count": len(bound_fields),
        "blocking_field_count": len(blocking_fields),
        "execution_ready": False,
        "panel_confirmatory_ready_arms": 0,
        "terminal": "P5_C4_V4_ADIAS_SOURCE_TREE_NATIVE_PARSER_EMPTY_FALLBACK_AND_WALLCLOCK_BOUND__FIFTEEN_C4_FIELDS_BLOCKING__DEPENDENCY_LOCK_TASK_RIGHTS_ISOLATION_AND_CUSTODY_UNBOUND__ZERO_OF_SIX_PANEL_READY__PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK",
        "bound_execution_envelope": {
            "authority": "PUBLIC_SOURCE_IDENTITY_AND_OUTCOME_BLIND_PREFLIGHT_ONLY",
            "source": {"commit_sha": COMMIT, "tree_sha": TREE},
            "resources": {
                "whole_run_seconds": 21600,
                "termination_grace_seconds": 120,
                "dedicated_docker_host": "REQUIRED_FROM_BOUND_SUCCESSOR_UNDER_SCRATCH_ROOT",
                "rlimits": {
                    "open_files": 4096,
                    "file_bytes": 10_737_418_240,
                    "processes": 512,
                },
            },
            "outcome_policy": "NO_PROTECTED_PANEL_OR_PERFORMANCE_ACCESS",
        },
    }
    write_json("P5_C4_V4_FIELD_REGISTRY.json", registry)

    write_json(
        "P5_C4_V4_SOURCE_RIGHTS_MANIFEST.json",
        {
            "schema_version": "orion.p5.c4.source-rights-manifest.v4",
            "arm_id": ARM_ID,
            "source_identity": {
                "repository": REPOSITORY,
                "commit_sha": COMMIT,
                "tree_sha": TREE,
                "archive_sha256": ARCHIVE_SHA256,
                "file_count": tree_manifest["file_count"],
            },
            "root_licence": {
                "path": "LICENSE.md",
                "sha256": sha(UPSTREAM / "LICENSE.md"),
                "spdx": "CC-BY-NC-SA-4.0",
                "noncommercial_only": True,
                "sharealike": True,
                "patent_and_trademark_rights_licensed": False,
            },
            "bundled_data_census": {
                "alfworld": {"files": 606, "bytes": 83_837_483},
                "scienceworld": {"files": 3, "bytes": 50_625},
                "textcraft": {"files": 863, "bytes": 540_379},
                "webshop": {"files": 4, "bytes": 30_653},
            },
            "component_licence_files_under_data": 0,
            "acknowledged_third_parties": ["HyperAgent", "tau-bench", "ALFWorld", "ScienceWorld", "TextCraft", "WebShop"],
            "closed_rights": ["exact root source licence bytes only"],
            "unclosed_rights": [
                "third-party bundled data and benchmark task content",
                "unselected P5 candidate-visible case",
                "model/provider/services",
                "transitive dependencies and built container",
                "generated patches, profiles, diagnoses, transcripts, records, reports, plots, logs, and final summaries",
                "protected scorer/panel",
            ],
            "commercial_execution_authorized": False,
            "legal_conclusion_claimed": False,
            "terminal": "SOURCE_LICENCE_BYTES_BOUND__TASK_BENCHMARK_CONTAINER_SERVICE_AND_OUTPUT_RIGHTS_CANNOT_CHECK",
        },
    )

    output_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "orion.p5.c4.adias-native-terminal.v4",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version", "arm_id", "adapter_terminal", "native_terminal",
            "generation_id", "metadata_sha256", "report_count", "nonempty_report_count",
            "reports", "native_exit_status_is_sufficient", "performance_inference",
            "raw_native_singleton_licences", "source_native_caveat",
        ],
        "properties": {
            "schema_version": {"const": "orion.p5.c4.adias-native-terminal.v4"},
            "arm_id": {"const": ARM_ID},
            "adapter_terminal": {"const": "UNRESOLVED"},
            "native_terminal": {"enum": [
                "NATIVE_COMPILE_FAILURE", "NATIVE_EMPTY_EVALUATION",
                "NATIVE_EVALUATION_ARTIFACTS_RECORDED", "NATIVE_NO_EFFECTIVE_PATCH", "NATIVE_PARTIAL",
            ]},
            "generation_id": {"type": "string", "minLength": 1},
            "metadata_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "report_count": {"type": "integer", "minimum": 0},
            "nonempty_report_count": {"type": "integer", "minimum": 0},
            "reports": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["domain", "path", "sha256", "record_count", "outcome_values_retained"],
                    "properties": {
                        "domain": {"enum": ["alfworld", "taubench_return", "taubench_retail", "textcraft", "webshop", "scienceworld"]},
                        "path": {"type": "string"},
                        "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                        "record_count": {"type": "integer", "minimum": 0},
                        "outcome_values_retained": {"const": False},
                    },
                },
            },
            "native_exit_status_is_sufficient": {"const": False},
            "performance_inference": {"const": "FORBIDDEN"},
            "raw_native_singleton_licences": {"const": 0},
            "source_native_caveat": {"type": "string", "minLength": 1},
        },
    }
    write_json("P5_C4_V4_NATIVE_OUTPUT_SCHEMA.json", output_schema)

    write_json(
        "P5_C4_V4_NATIVE_TERMINAL_RULES.json",
        {
            "schema_version": "orion.p5.c4.native-terminal-rules.v4",
            "arm_id": ARM_ID,
            "source_writers": {
                "metadata": {"path": "src/generate_loop.py", "sha256": sha(UPSTREAM / "src/generate_loop.py")},
                "report_dispatch": {"path": "src/domains/report.py", "sha256": sha(UPSTREAM / "src/domains/report.py")},
            },
            "rules": [
                {"terminal": "NATIVE_COMPILE_FAILURE", "condition": "compile_status.ok is false or native compile_failure_diagnosis.json exists"},
                {"terminal": "NATIVE_EMPTY_EVALUATION", "condition": "one or more structurally valid candidate-visible report.json files exist but every total is zero"},
                {"terminal": "NATIVE_EVALUATION_ARTIFACTS_RECORDED", "condition": "metadata.run_eval is true and at least one structurally valid candidate-visible report has total>0"},
                {"terminal": "NATIVE_NO_EFFECTIVE_PATCH", "condition": "no prior rule matches and patch_summary.has_patch is false"},
                {"terminal": "NATIVE_PARTIAL", "condition": "no prior rule matches"},
            ],
            "global_adapter_terminal": "UNRESOLVED",
            "forbidden_inferences": ["P5 performance", "P5 superiority", "P5 responsibility class", "harm", "preservation", "fresh transfer"],
            "refused_material": ["final_test paths", "protected/gold/holdout paths or keys", "final_test_summary keys"],
            "material_source_defects_preserved": [
                "generate() catches evaluation exceptions and can return normally after setting run_eval false",
                "released run scripts use nohup/background and exit after writing a PID",
                "a native report with total=0 still contains score=0 and can make get_score return non-None",
                "native report JSON has no schema/version identifier",
            ],
            "smoke_fixture_is_performance": False,
        },
    )

    write_json(
        "P5_C4_V4_WRITE_SURFACE_SCHEMA.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "orion.p5.c4.write-surface.v4",
            "type": "object",
            "additionalProperties": False,
            "required": ["source_copy", "candidate_case", "released_output_root", "scratch_root", "dedicated_docker_root", "forbidden_surfaces"],
            "properties": {
                "source_copy": {"type": "string", "description": "ephemeral mutable copy of the pinned tree under scratch_root"},
                "candidate_case": {"type": "string", "description": "read-only exact candidate-visible case packet"},
                "released_output_root": {"type": "string", "description": "sole retained output mount"},
                "scratch_root": {"type": "string", "description": "ephemeral HOME/TMP/cache/build root"},
                "dedicated_docker_root": {"type": "string", "description": "ephemeral daemon socket, image, container, layer, and volume state under scratch_root"},
                "forbidden_surfaces": {"type": "array", "minItems": 1, "items": {"type": "string"}},
            },
            "native_observed_writes": [
                "host outputs/logs/staging/temporary directories",
                "mutable source copy and Git objects/commits inside task container",
                "agent_output profiles, diagnoses, change reports, patches, token usage, transcripts, raw events",
                "records/report JSON and episode traces",
                "Docker images, containers, build cache, and optional host data mount access",
            ],
            "native_observed_network": ["host-network Docker builds", "host-network task containers", "model provider calls", "optional external web search", "package and Git dependency fetches"],
            "source_native_boundary_is_sufficient": False,
            "status": "BLOCKING_UNTIL_DISPOSABLE_EXECUTOR_RECEIPT",
        },
    )

    write_json(
        "P5_C4_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json",
        {
            "schema_version": "orion.p5.c4.candidate-visible-case-requirements.v4",
            "arm_id": ARM_ID,
            "required": [
                "case_id and schema version", "exact authored/licensed task bytes and SHA-256",
                "single native ADIAS domain and split policy", "task/environment code and data hashes",
                "all visible task identifiers and seeds", "max turns/steps and evaluation sample count",
                "candidate-visible scoring/feedback boundary", "rights holder/grant/territory/purpose/retention",
                "proof that protected panel bytes/outcomes are absent", "no fixture-to-performance promotion",
            ],
            "forbidden": ["native test/final_test content", "protected outcomes", "gold/reference answers", "unhashed external task fetches"],
            "native_shaped_smoke_fixture_is_substantive_p5_case": False,
            "status": "UNBOUND",
        },
    )

    write_json(
        "P5_C4_V4_CUSTODY_HANDOFF_SCHEMA.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "orion.p5.c4.custody-handoff.v4",
            "type": "object",
            "additionalProperties": False,
            "required": [
                "handoff_id", "arm_id", "candidate_terminal_sha256", "protected_panel_manifest_sha256",
                "freshness_nonce", "scorer_code_sha256", "custodian_identity", "custodian_signature",
                "candidate_received_protected_bytes", "feedback_before_terminal", "one_shot",
            ],
            "properties": {
                "handoff_id": {"type": "string", "minLength": 1},
                "arm_id": {"const": ARM_ID},
                "candidate_terminal_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "protected_panel_manifest_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "freshness_nonce": {"type": "string", "minLength": 16},
                "scorer_code_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "custodian_identity": {"type": "string", "minLength": 1},
                "custodian_signature": {"type": "string", "minLength": 1},
                "candidate_received_protected_bytes": {"const": False},
                "feedback_before_terminal": {"const": False},
                "one_shot": {"const": True},
            },
            "current_status": "CANNOT_CHECK_NO_ATTESTATION",
        },
    )

    write_json(
        "P5_C4_V4_RESOURCE_REGISTRY.json",
        {
            "schema_version": "orion.p5.c4.resource-registry.v4",
            "arm_id": ARM_ID,
            "wallclock": {
                "status": "BOUND_PROSPECTIVE_GATE",
                "whole_run_seconds": 21600,
                "termination_grace_seconds": 120,
                "enforcer": "p5_c4_fail_closed_runner.py",
                "enforcer_sha256": runner_hash,
                "background_launchers_forbidden": True,
            },
            "source_observations_not_adopted_as_matched_p5_values": {
                "source_meta_exec_timeout_seconds": 21600,
                "source_container_pids_limit": 256,
                "source_eval_workers_default": 10,
                "source_llm_max_tokens_per_call": 16384,
                "source_backoff_max_time_seconds": 600,
                "source_container_network_mode": "host",
            },
            "blocking": {
                "calls_tokens_usd": "no aggregate hard stop or provider reconciliation",
                "retry_network": "no exact endpoint allowlist/offline dependency build",
                "compute": "no end-to-end CPU/RAM/disk/GPU/cgroup enforcement across Docker daemon and children",
            },
            "source_defaults_are_not_a_matched_resource_lock": True,
        },
    )

    write_json(
        "P5_C4_V4_EXECUTION_BINDING_PROTOCOL.json",
        {
            "schema_version": "orion.p5.c4.adias-execution-binding-protocol.v4",
            "protocol_id": "P5.C4.ADIAS.EXECUTION.BINDING.V4",
            "arm_id": ARM_ID,
            "authority": "PUBLIC_SOURCE_IDENTITY_AND_OUTCOME_BLIND_PREFLIGHT_ONLY",
            "source": {"repository": REPOSITORY, "commit_sha": COMMIT, "tree_sha": TREE},
            "native_entrypoint": "python -u generate_loop.py",
            "forced_flags": ["--no_final_test", "--no-enable_external_search"],
            "forbidden_launchers": ["scripts/run_*.sh", "nohup", "background ampersand"],
            "native_parser": {"path": "p5_c4_native_parser.py", "sha256": parser_hash},
            "fail_closed_gate": {"path": "p5_c4_fail_closed_runner.py", "sha256": runner_hash},
            "field_registry": "P5_C4_V4_FIELD_REGISTRY.json",
            "execution_rule": "REFUSE NATIVE EXECUTION UNTIL ALL 21 C4 FIELDS ARE BOUND AND ALL SIX ARMS SHARE ONE MATCHED PANEL CONTRACT",
            "outcome_rule": "native reports are candidate-visible execution artifacts only; protected scoring is external, one-shot, and no-feedback",
            "fallback_rule": "empty fallback list; no model/provider/role switching",
            "current_bound_fields": 6,
            "current_blocking_fields": 15,
            "current_execution_ready": False,
            "panel_confirmatory_ready_arms": 0,
            "panel_required_arms": 6,
        },
    )

    negative_entries = [
        ("NATIVE_JOB_NOT_RUN", "No ADIAS model/domain/benchmark job was executed.", "Outcome blindness and 15 blockers require source preflight only.", "Performance, harm, preservation, transfer, and superiority remain CANNOT_CHECK.", "Bind every field and the six-arm panel before one custodial run."),
        ("DEPENDENCY_LOCK_ABSENT", "No transitive lock exists.", "Source has conflicting declarations and four unpinned VCS requirements.", "Runtime bytes cannot be reproduced.", "Create a hash-complete Python 3.12/platform lock with exact VCS commits."),
        ("ROOT_LICENCE_NONCOMMERCIAL", "Root source is CC-BY-NC-SA-4.0.", "The release intentionally restricts licensed use to NonCommercial purposes and applies ShareAlike conditions.", "Commercial execution/publication use is not authorized by this packet.", "Obtain rights advice/permission for the exact intended use."),
        ("BUNDLED_DATA_RIGHTS_UNCLOSED", "No component licence/NOTICE files occur under data/.", "Acknowledged third-party benchmark material is bundled without component-specific grants in the frozen tree.", "Task/benchmark rights remain CANNOT_CHECK.", "Obtain authoritative grants for every selected task/data component."),
        ("MUTABLE_BASE_IMAGE", "Dockerfile starts FROM python:3.12-bullseye.", "The tag is not digest-pinned and network installs occur during build.", "Container/environment identity is unbound.", "Resolve base manifest digest and offline SBOM build."),
        ("HOST_NETWORK_AND_KEYS", "Native build/task containers use host networking and receive provider API keys.", "build_container hard-codes network_mode=host and passes credential environment values.", "Isolation, egress, and credential exposure are unclosed.", "Demonstrate a dedicated deny-by-default executor/daemon with exact endpoints and scoped keys."),
        ("FINAL_TEST_DEFAULT_ON", "generate_loop defaults final_test=True and formal scripts commonly pass --final_test.", "Native final_test is same-run and writes outcomes locally.", "It cannot serve as the protected one-shot scorer and risks outcome leakage.", "Force --no_final_test; score only through external custody after candidate freeze."),
        ("EXTERNAL_SEARCH_DEFAULT_ON", "generate_loop defaults external search on.", "A one-shot web search can fetch unbound material and use another model surface.", "Network/model/task provenance expands unless explicitly disabled.", "Force --no-enable_external_search and deny its endpoint."),
        ("BACKGROUND_SCRIPT_TERMINAL_DEFECT", "Released run scripts use nohup and background execution.", "The shell can exit zero after writing a PID while the job is running or later fails.", "Script exit is not a native terminal.", "Launch python -u generate_loop.py in the foreground under the V4 watchdog."),
        ("ZERO_TASK_REPORT_DEFECT", "Report writers emit score=0 with total=0 and get_score can return non-None.", "Source valid_parent checks score presence, not positive task cardinality.", "A zero-task fixture/report must not be called performance.", "Parser assigns NATIVE_EMPTY_EVALUATION and retains no score."),
        ("EXIT_ZERO_INSUFFICIENT", "generate() catches exceptions, sets run_eval false, writes metadata, and can return normally.", "Process success and scientific/evaluation success are separate.", "Exit zero cannot establish a completed evaluation or P5 claim.", "Parse metadata/report structure and retain UNRESOLVED."),
        ("DOMAIN_HIDE_NOT_SECURITY_BOUNDARY", "The domain hide helper notes that the agent runs as root.", "chmod 0 is not a true lock against root; host-network container remains powerful.", "hide_domain is a cost increase, not isolation evidence.", "Use an external non-root sandbox with inaccessible protected/domain bytes."),
        ("RESOURCE_HARD_STOPS_ABSENT", "No aggregate calls/tokens/USD/compute hard stops exist.", "Source records usage after calls and uses partial per-call/per-container defaults.", "Resource comparability and spend bounds are unbound.", "Add provider-reconciled hard stops and end-to-end cgroups."),
        ("PRIMARY_MODEL_UNBOUND", "Source model names are defaults only.", "No provider endpoint/snapshot/service/role binding exists; TauBench adds a user simulator.", "Model identity and service rights remain CANNOT_CHECK.", "Bind every role to one exact approved service identity."),
        ("PROTECTED_CUSTODY_ABSENT", "No external scorer, one-shot barrier, or fresh protected panel attestation exists.", "Native ADIAS evaluation is candidate-side and iterative.", "Independent confirmatory measurement is impossible.", "Obtain a signed external custody handoff satisfying the V4 schema."),
        ("SOURCE_FIXTURE_NOT_PERFORMANCE", "Only authored native-shaped smoke fixtures are executed.", "They contain zero task records and no model/environment work.", "Smoke proves parser/gate conformance only.", "First substantive discriminator is a rights-cleared nonzero case under full custody."),
    ]
    ledger_entries = [
        {"id": ident, "failure": failure, "cause": cause, "residual": residual, "next_discriminator": nxt, "status": "PRESERVED"}
        for ident, failure, cause, residual, nxt in negative_entries
    ]
    write_json(
        "P5_C4_V4_NEGATIVE_LEDGER.json",
        {"schema_version": "orion.p5.c4.negative-ledger.v4", "arm_id": ARM_ID, "entries": ledger_entries},
    )
    negative_md = ["# P5 C4 ADIAS V4 negative ledger", "", "Every defect is retained; none is converted into performance evidence.", ""]
    for entry in ledger_entries:
        negative_md.extend([
            f"## {entry['id']}", "",
            f"- **Failure:** {entry['failure']}",
            f"- **Cause:** {entry['cause']}",
            f"- **Residual:** {entry['residual']}",
            f"- **Next discriminator:** {entry['next_discriminator']}", "",
        ])
    (HERE / "P5_C4_V4_NEGATIVE_LEDGER.md").write_text("\n".join(negative_md), encoding="utf-8")

    terminal = registry["terminal"]
    result = {
        "schema_version": "orion.p5.c4.adias-execution-binding-result.v4",
        "protocol_id": "P5.C4.ADIAS.EXECUTION.BINDING.V4",
        "arm_id": ARM_ID,
        "authority": "PUBLIC_SOURCE_IDENTITY_AND_OUTCOME_BLIND_PREFLIGHT_ONLY",
        "execution": {"c4_executed": False, "c4_execution_ready": False, "full_native_smoke": "CANNOT_CHECK", "panel_confirmatory_ready_arms": 0, "panel_required_arms": 6},
        "v4_repairs": {
            "c4_bound_fields": 6,
            "c4_blocking_fields": 15,
            "v3_to_v4_blocker_delta": -3,
            "retained_bound_identity_fields": ["identity.native_entrypoint_bytes", "identity.source_license_bytes", "identity.source_repository_commit"],
            "newly_bound_fields": ["adapter.native_parser_binding", "model_provider.fallbacks", "resources.wallclock"],
        },
        "material_discoveries": {
            "source_tree_files": 1578,
            "source_tree_bytes": tree_manifest["total_file_bytes"],
            "dependency_lock_present": False,
            "unpinned_vcs_declarations": 4,
            "component_licence_files_under_data": 0,
            "native_final_test_is_external_protected_scorer": False,
            "native_process_exit_is_scientific_terminal": False,
        },
        "preserved_boundaries": {
            "raw_native_singleton_licences": 0,
            "scienceclaw_supported_singletons": 0,
            "v3_synthetic_cases": 231,
            "v3_supported_singleton_case_records": 40,
            "v3_supported_singleton_fibres": 20,
            "v3_unresolved_case_records": 191,
            "smoke_fixture_is_substantive_p5_case": False,
        },
        "preserved_claims": {
            "H1": "CANNOT_CHECK", "H2": "CANNOT_CHECK", "H3": "CANNOT_CHECK", "H4": "CANNOT_CHECK",
            "preservation": "CANNOT_CHECK", "fresh_transfer": "CANNOT_CHECK", "harm": "CANNOT_CHECK",
            "performance": "CANNOT_CHECK", "superiority": "CANNOT_CHECK", "top_tier_publication_readiness": "NOT_ESTABLISHED",
        },
        "next_discriminator": "Resolve a hash-complete Python 3.12 dependency/image build and authoritative rights for one exact nonzero native ADIAS task; then demonstrate the dedicated rootless-Docker write/resource boundary, bind every model/service/resource field and three independent custody attestations, while C4 still waits for 6/6 panel readiness.",
        "terminal": terminal,
    }
    write_json("P5_C4_V4_RESULT.json", result)
    (HERE / "TERMINAL_V4.txt").write_text(terminal + "\n", encoding="utf-8")

    report = f"""# P5 C4 ADIAS execution-binding V4

## Terminal

`{terminal}`

This packet is an outcome-blind public-source preflight, not a comparator result.
No ADIAS model, domain, benchmark, replay, final test, protected scorer, panel,
gold/reference value, or performance table was executed or opened.

## Exact 21-field census

V4 binds **6/21** fields and retains **15/21 blocking**. Confirmatory panel
readiness is **0/6**.

| Bound field | Exact evidence |
|---|---|
| `identity.source_repository_commit` | Official repository `{REPOSITORY}` at `{COMMIT}`; tree `{TREE}`; 1,578-file manifest; deterministic archive SHA-256 `{ARCHIVE_SHA256}` |
| `identity.source_license_bytes` | `LICENSE.md` SHA-256 `{sha(UPSTREAM / 'LICENSE.md')}`; CC-BY-NC-SA-4.0, explicitly NonCommercial/ShareAlike |
| `identity.native_entrypoint_bytes` | Four pyproject console scripts plus direct foreground `python -u generate_loop.py`; exact wrapper/implementation hashes |
| `adapter.native_parser_binding` | Hashed generation-directory parser; final/protected/gold paths or keys refused; native outcome values not returned; P5 terminal always `UNRESOLVED` |
| `model_provider.fallbacks` | Empty fallback list; external search forced off; no meta/task/user/search model or provider switch |
| `resources.wallclock` | Direct foreground process-group watchdog, 21,600 s whole-run cap, 120 s grace, exit 124 timeout; background scripts forbidden |

The 15 blockers are: native Docker/write isolation; exact candidate-visible
case; primary model/provider role mapping; aggregate calls/tokens/USD; retry and
network allowlist; end-to-end compute; digest-pinned environment; transitive
dependency lock; exact task environment; task/benchmark rights; service rights;
container/generated-artifact rights; external scorer; one-shot no-feedback
barrier; and fresh protected-panel custody.

## Material source audit

The frozen Git tree contains **1,578 files / {tree_manifest['total_file_bytes']:,} bytes**.
It includes 606 ALFWorld data files, 863 TextCraft files, 4 WebShop files, and
3 ScienceWorld split files. There are **zero component licence/NOTICE files
under `data/`**. Root CC-BY-NC-SA source bytes therefore do not close
third-party task/benchmark rights.

There is **no dependency lock**. `pyproject.toml`, `requirements.txt`,
`requirements_dev.txt`, and Docker RUN lines are declarations, not a resolved
transitive graph. Four requirements VCS dependencies are unpinned; declarations
also conflict (`dotenv` versus `python-dotenv`, and unconstrained versus ranged
`numpy`). The base `python:3.12-bullseye` is a mutable tag. V4 preserves these
facts rather than relabelling declarations as a lock.

Native Docker builds and task containers use host networking. Provider keys are
passed into a root container; only a PID limit is set. The meta agent has bash
and edit tools. The source's own domain-hide docstring concedes that `chmod 0`
is not a true lock because the agent runs as root. Consequently isolation and
end-to-end compute remain blocking despite the prospective fail-closed gate.

## Native terminal audit

ADIAS report writers emit unversioned `report.json` files. The source can write
`score=0` with `total=0`, while `get_score` still returns a non-`None` value;
such a fixture is not performance. `generate()` also catches evaluation errors,
sets `run_eval=false`, writes metadata, and may return normally. Released run
scripts use `nohup`/backgrounding, so shell exit zero is not the job terminal.

The V4 parser therefore distinguishes compile failure, empty evaluation,
evaluation artifacts recorded, no effective patch, and partial execution. It
never returns native score/success/reward/progress/cost values and always maps
to P5 `UNRESOLVED`. This is structural conformance, not responsibility or
performance evidence.

Native `final_test` defaults on and writes `final_test_summary.json` inside the
same iterative process. That is not an independent protected scorer. V4 forces
`--no_final_test`; protected scoring must be external, fresh, one-shot, and
withheld until candidate freeze. External search also defaults on; V4 forces it
off.

## Outcome-blind smoke boundary

Only authored zero-task, native-shaped `metadata.json`/`report.json` fixtures
are parsed. Smoke proves parser classification and refusal of protected keys.
The fail-closed runner is checked only for its current 15-field refusal. No
dependency installation, container build, Docker access, provider call, domain
harness, task episode, or benchmark run occurs.

## Scientific boundary and next discriminator

The V3 synthetic contract stays unchanged: **231** authored synthetic cases,
**40** supported singleton case records in **20** constant fibres, **191**
`UNRESOLVED`, zero raw native singleton licences, and zero ScienceClaw
singletons. A source/native parser does not upgrade any unsupported fibre.
H1-H4, preservation, fresh transfer, harm, performance, and superiority remain
`CANNOT_CHECK`; top-tier readiness is not established.

The exact next discriminator is: resolve a hash-complete Python 3.12 lock and
digest-pinned offline image, then obtain authoritative rights for one exact
nonzero native ADIAS task. Only after a disposable rootless-Docker
write/resource demonstration, exact model/service/resource bindings, and three
independent custody attestations may C4 be reconsidered—and it must still wait
for all six arms to share the matched panel.
"""
    (HERE / "SCIENTIFIC_REPORT_V4.md").write_text(report, encoding="utf-8")

    readme = """# P5 C4 ADIAS execution-binding V4 packet

Outcome-blind public-source preflight for `C4_ISSUE_CENTRIC_OPTIMIZATION__ADIAS`
at commit `fbcf0c73d12d30a4ee0d13c2e64b4c40d00b2993`.

- No native ADIAS/model/domain/benchmark/protected job was run.
- Exact readiness: **6/21 BOUND**, **15/21 blocking**, **0/6 panel ready**.
- Smoke uses only authored zero-task native-shaped fixtures; it is not performance.
- `requirements.txt`/`pyproject.toml` are preserved as declarations, **not a lock**.
- Source/root rights do not close task, data, service, image, output, or custody rights.

Read `SCIENTIFIC_REPORT_V4.md`, `P5_C4_V4_FIELD_REGISTRY.json`, and
`P5_C4_V4_NEGATIVE_LEDGER.md`. Run only the outcome-blind validator:

```text
python p5_c4_v4_validator.py
```
"""
    (HERE / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
