#!/usr/bin/env python3
"""Build the exact outcome-free C3 candidate packet without executing DGM."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEV = HERE.parent
V6 = DEV / "p5-common-visible-case-rights-v6-2026-08-23"
V7 = DEV / "p5-native-task-environment-fanout-v7-2026-08-23"
V4 = DEV / "p5-dgm-execution-binding-v4-2026-08-23"
V3 = DEV / "p5-six-arm-adapter-refinement-v3-2026-08-23"
FILTER_RECEIPT = HERE / "P5_C3_FILTERED_DGM_SOURCE_RECEIPT_V8.json"
FILTER_ARCHIVE = HERE / "DGM_FILTERED_SOURCE_a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2.tar.gz"
SEED = HERE / "P5_C3_CANDIDATE_SAFE_SEED_V8.tar.gz"
RECEIPT = HERE / "P5_C3_NATIVE_TASK_ENVIRONMENT_RECEIPT_V8.json"
REPORT = HERE / "P5_C3_NATIVE_TASK_ENVIRONMENT_V8.md"
FROZEN_AT = "2026-08-23T21:00:00Z"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return digest(path.read_bytes())


def jbytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def write_json(name: str, value: object) -> tuple[str, bytes]:
    data = jbytes(value)
    (HERE / name).write_bytes(data)
    return name, data


def tar_gz(members: list[tuple[str, bytes, int]]) -> bytes:
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for path, data, mode in sorted(members):
                info = tarfile.TarInfo(path)
                info.size = len(data)
                info.mode = mode
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                info.mtime = 0
                tar.addfile(info, io.BytesIO(data))
    return out.getvalue()


def main() -> None:
    clock = time.monotonic()
    started_at = now()
    filtered = json.loads(FILTER_RECEIPT.read_text())
    if filtered["filter"]["excluded_files"] != 1595:
        raise RuntimeError("frozen excluded-file census changed")
    if filtered["filter"]["excluded_payload_contents_opened"] is not False:
        raise RuntimeError("excluded payload boundary violated")
    if file_digest(FILTER_ARCHIVE) != filtered["output"]["sha256"]:
        raise RuntimeError("filtered source archive hash mismatch")

    core_index_path = V6 / "P5_SHARED_CASE_CORE_INDEX_V6.json"
    if file_digest(core_index_path) != "aeddff407dcd73326a6b1f123131463c5ae550f74aaab7f7e522a29dce247b8e":
        raise RuntimeError("V6 core index changed")
    core_index = json.loads(core_index_path.read_text())
    if core_index["candidate_visible_core_sha256"] != "09a2eb17394d7b84c11641b468d14446af955c4c3272557810d861a275c72da7":
        raise RuntimeError("V6 core identity changed")
    core_members: list[tuple[str, bytes, int]] = []
    core_refs = []
    for component in core_index["components"]:
        src = V6 / component["path"]
        data = src.read_bytes()
        if len(data) != component["size_bytes"] or digest(data) != component["sha256"]:
            raise RuntimeError(f"V6 component changed: {component['path']}")
        rel = component["path"].removeprefix("candidate_visible/")
        seed_path = f"candidate/shared_core/{rel}"
        core_members.append((seed_path, data, 0o644))
        core_refs.append(
            {
                "path": seed_path,
                "sha256": digest(data),
                "size_bytes": len(data),
                "spdx": component["license_spdx_id"],
            }
        )

    dgm_members: list[tuple[str, bytes, int]] = []
    dgm_outer = None
    with tarfile.open(FILTER_ARCHIVE, "r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                raise RuntimeError(f"unexpected non-file in filtered source: {member.name}")
            stream = tar.extractfile(member)
            if stream is None:
                raise RuntimeError(f"cannot read filtered member: {member.name}")
            data = stream.read()
            path = f"candidate/{member.name}"
            dgm_members.append((path, data, member.mode))
            if member.name == "dgm/DGM_outer.py":
                dgm_outer = data
    if dgm_outer is None or digest(dgm_outer) != "239bc76f0e1b78210b8f7b3757b1082f6ca07db3537d6af50a45bf97709795ed":
        raise RuntimeError("DGM_outer identity mismatch")
    source_lines = dgm_outer.decode().splitlines()
    required_line_fragments = {
        19: "archive = ['initial']",
        28: "initial_folder_name = 'initial'",
        33: 'raise RuntimeError("Error: Need to properly configure evaluation results for the initial version.")',
        60: 'metadata_path = os.path.join(output_dir, commit, "metadata.json")',
        63: "metadata['overall_performance']['accuracy_score']",
        66: "metadata['overall_performance']['total_resolved_ids']",
    }
    for line, fragment in required_line_fragments.items():
        if fragment not in source_lines[line - 1]:
            raise RuntimeError(f"native initialization evidence moved at line {line}")
    blocker_excerpt = "".join(
        f"{line}: {source_lines[line - 1]}\n"
        for line in list(range(15, 36)) + list(range(50, 69))
    ).encode()
    blocker_evidence_path = HERE / "evidence" / "DGM_OUTER_INITIALIZATION_LINES_V8.txt"
    blocker_evidence_path.parent.mkdir(exist_ok=True)
    blocker_evidence_path.write_bytes(blocker_excerpt)

    domain = {
        "schema_version": "orion.p5.c3.case-action-domain.v8",
        "domain_id": "SYNTHETIC_P5_LANG1_EXECUTION_FRONT_V8",
        "case_id": "P5-PUBLIC-LANG1-COMMON-001",
        "arm_id": "C3_ARCHIVE_BASED_SELF_EDIT__DGM",
        "classification_target": "captured task patch only; DGM internal self-edit state is not a licensed responsibility-class output",
        "selected_front": "EXECUTION_REPAIR",
        "mutable_task_surface": [
            "task_worktree/src/main/java/org/apache/commons/lang3/math/NumberUtils.java"
        ],
        "immutable_fronts": [
            "evidence",
            "measurement",
            "scientific_model",
            "representation",
            "evaluator",
        ],
        "native_output_class": "UNRESOLVED",
        "outcome_authority": False,
        "eight_class_registry_sha256": file_digest(V3 / "P5_V3_EIGHT_CLASS_FRONT_REGISTRY.json"),
        "frozen_at_utc": FROZEN_AT,
    }
    domain_name, domain_bytes = write_json("P5_C3_CASE_ACTION_DOMAIN_V8.json", domain)
    proof = {
        "schema_version": "orion.p5.c3.fibre-constancy-proof.v8",
        "proof_id": "P5-C3-LANG1-EXECUTION-FRONT-CONSTANCY-V8",
        "domain_scope_sha256": digest(domain_bytes),
        "declared_class": "EXECUTION_REPAIR",
        "proof": {
            "allowed_task_write_count": 1,
            "allowed_task_write": domain["mutable_task_surface"][0],
            "all_non_execution_fronts_immutable": True,
            "candidate_receives_no_outcome_or_evaluator_bytes": True,
            "claim": "Every admitted captured task patch is confined to the execution front; correctness and performance are not certified.",
        },
        "status": "PROVED_ON_DECLARED_SYNTHETIC_DOMAIN",
        "frozen_at_utc": FROZEN_AT,
    }
    proof_name, proof_bytes = write_json("P5_C3_FIBRE_CONSTANCY_PROOF_V8.json", proof)
    certificate = {
        "schema_version": "orion.p5.candidate-visible-class-certificate.v3",
        "certificate_id": "P5V3-CERT-C3-LANG1-EXECUTION-V8",
        "arm_id": "C3_ARCHIVE_BASED_SELF_EDIT__DGM",
        "observation_id": "P5V3-OBS-P5-PUBLIC-LANG1-COMMON-001",
        "declared_class": "EXECUTION_REPAIR",
        "issuance": {
            "issuer_role": "HOST_INPUT_VALIDATOR",
            "phase": "BEFORE_CANDIDATE_ACTION",
            "candidate_visible": True,
            "input_native": True,
            "native_output_access": False,
            "protected_outcome_access": False,
            "sequence": 0,
        },
        "basis": {
            "predicate_id": "SYNTHETIC_P5_LANG1_EXECUTION_FRONT_V8",
            "source_ref_sha256": sorted(
                {
                    "3e5d001eee38d62c93c5f00acf59adba0a55cadf6df7040bdb2c432c1c16f921",
                    "a455eec2d32b031b6e49d06c73e0cf3befbe9e2cd461e5417efbade5f39f5098",
                    "f97c316795a6ba124f693bce9e8019b1735bc976affa9bce8d4c52f668575f08",
                    filtered["output"]["sha256"],
                }
            ),
            "domain_scope_sha256": digest(domain_bytes),
            "fibre_constancy_attestation": {
                "status": "PROVED_ON_DECLARED_SYNTHETIC_DOMAIN",
                "declared_class": "EXECUTION_REPAIR",
                "proof_ref_sha256": digest(proof_bytes),
            },
        },
        "complete": True,
    }
    cert_name, cert_bytes = write_json("P5_C3_INPUT_NATIVE_CERTIFICATE_V8.json", certificate)

    split = {
        "schema_version": "orion.p5.c3.mutable-immutable-split.v8",
        "case_id": "P5-PUBLIC-LANG1-COMMON-001",
        "arm_id": "C3_ARCHIVE_BASED_SELF_EDIT__DGM",
        "read_only_seed_roots": ["/p5/seed/candidate/dgm", "/p5/seed/candidate/shared_core", "/p5/seed/candidate/control"],
        "ephemeral_mutable_agent_roots": ["/p5/work/dgm_worktree", "/p5/work/output_dgm"],
        "ephemeral_mutable_task_paths": [
            "/p5/work/task_worktree/src/main/java/org/apache/commons/lang3/math/NumberUtils.java"
        ],
        "immutable_task_paths": "every other member of the exact V6 Commons Lang source archive",
        "immutable_host_roots": ["/p5/host/controller", "/p5/host/policy", "/p5/host/receipts"],
        "excluded_roots_absent": ["initial/", "initial_polyglot/", "swe_bench/ref_agent_results/"],
        "input_native_certificate_sha256": digest(cert_bytes),
        "reset": "destroy every ephemeral root after the non-executed or future single attempt",
        "frozen_at_utc": FROZEN_AT,
    }
    split_name, split_bytes = write_json("P5_C3_MUTABLE_IMMUTABLE_SPLIT_V8.json", split)
    policy = {
        "schema_version": "orion.p5.c3.endpoint-tool-write-policy.v8",
        "case_id": "P5-PUBLIC-LANG1-COMMON-001",
        "network": {
            "default": "DENY",
            "candidate_visible_allowed_endpoints": [],
            "model_service_endpoints": "UNBOUND_IN_SEPARATE_FIELD",
            "docker_daemon": "FORBIDDEN_FROM_CANDIDATE_CUSTODY",
            "protected_scorer": "FORBIDDEN",
        },
        "tools": {
            "allowed": [
                "read_candidate_seed",
                "copy_to_ephemeral_worktree",
                "edit_mutable_agent_worktree",
                "edit_exact_task_path",
                "capture_patch_digest",
            ],
            "forbidden": [
                "benchmark_execution",
                "protected_scorer_access",
                "gold_or_reference_output_access",
                "host_git_remote_access",
                "host_docker_daemon_access",
                "writes_outside_declared_ephemeral_roots",
            ],
        },
        "writes": {
            "split_manifest_sha256": digest(split_bytes),
            "before_after_digest_required": True,
            "task_write_allowlist": split["ephemeral_mutable_task_paths"],
            "all_other_task_paths": "READ_ONLY",
            "receipt_output": "/p5/receipts/c3-single-attempt",
        },
        "execution_authorized": False,
        "frozen_at_utc": FROZEN_AT,
    }
    policy_name, policy_bytes = write_json("P5_C3_ENDPOINT_TOOL_WRITE_POLICY_V8.json", policy)

    invocation = {
        "schema_version": "orion.p5.c3.invocation-environment.v8",
        "case_id": "P5-PUBLIC-LANG1-COMMON-001",
        "arm_id": "C3_ARCHIVE_BASED_SELF_EDIT__DGM",
        "source_identity": {
            "repository": "https://github.com/jennyzzt/dgm",
            "commit": "a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2",
            "tree": "dc58ea5c481124afdb97468c1bed4e0debb425c4",
            "filtered_source_sha256": filtered["output"]["sha256"],
            "entrypoint": "DGM_outer.py",
            "entrypoint_sha256": digest(dgm_outer),
        },
        "working_directory": "/p5/work/dgm_worktree",
        "argv": [
            "python3",
            "-I",
            "DGM_outer.py",
            "--max_generation",
            "1",
            "--selfimprove_size",
            "1",
            "--selfimprove_workers",
            "1",
            "--choose_selfimproves_method",
            "random",
            "--update_archive",
            "keep_all",
            "--num_swe_evals",
            "1",
            "--shallow_eval",
            "--no_full_eval",
        ],
        "environment": {
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONHASHSEED": "0",
            "TZ": "UTC",
            "P5_CASE_ID": "P5-PUBLIC-LANG1-COMMON-001",
            "P5_NETWORK_POLICY": "DENY_ALL",
            "P5_OUTCOME_ACCESS": "FORBIDDEN",
            "P5_PROTECTED_SCORER_ACCESS": "FORBIDDEN",
        },
        "native_initialization_preflight": {
            "status": "BLOCKING",
            "source_sha256": digest(dgm_outer),
            "source_lines": [19, 28, 29, 30, 31, 33, 60, 63, 64, 65, 66],
            "cause": "Unchanged DGM requires initial/ and reads prior overall_performance fields; the candidate-safe seed must exclude those prior-outcome files.",
        },
        "argparse_defect_policy": "PRESERVE_NATIVE_C3; use only the explicit valid choice random; do not patch source",
        "execution_authorized": False,
        "frozen_at_utc": FROZEN_AT,
    }
    invocation_name, invocation_bytes = write_json("P5_C3_INVOCATION_ENVIRONMENT_V8.json", invocation)

    authored = {
        domain_name: domain_bytes,
        proof_name: proof_bytes,
        cert_name: cert_bytes,
        split_name: split_bytes,
        policy_name: policy_bytes,
        invocation_name: invocation_bytes,
    }
    provenance = {
        "schema_version": "orion.p5.c3.candidate-safe-provenance.v8",
        "dgm": {
            "repository": "https://github.com/jennyzzt/dgm",
            "commit": "a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2",
            "tree": "dc58ea5c481124afdb97468c1bed4e0debb425c4",
            "filtered_source_receipt_sha256": file_digest(FILTER_RECEIPT),
            "filtered_source_sha256": filtered["output"]["sha256"],
            "included_files": 55,
            "excluded_files": 1595,
            "excluded_payload_contents_opened": False,
        },
        "shared_lang1_core": {
            "case_id": "P5-PUBLIC-LANG1-COMMON-001",
            "core_index_sha256": file_digest(core_index_path),
            "candidate_visible_core_sha256": core_index["candidate_visible_core_sha256"],
            "components": core_refs,
        },
        "predecessor_gate": {
            "v7_acceptance_sha256": file_digest(V7 / "P5_C3_NATIVE_TASK_ENVIRONMENT_ACCEPTANCE_V7.json"),
            "v7_manifest_sha256": file_digest(V7 / "P5_C3_NATIVE_TASK_ENVIRONMENT_MANIFEST_V7.json"),
            "v4_field_registry_sha256": file_digest(V4 / "P5_C3_V4_FIELD_REGISTRY.json"),
        },
        "control_sha256": {name: digest(data) for name, data in authored.items()},
        "frozen_at_utc": FROZEN_AT,
    }
    provenance_name, provenance_bytes = write_json("P5_C3_PROVENANCE_V8.json", provenance)
    authored[provenance_name] = provenance_bytes
    rights = {
        "schema_version": "orion.p5.c3.candidate-safe-rights.v8",
        "legal_advice": False,
        "components": [
            {
                "scope": "55-file filtered DGM source",
                "spdx": "Apache-2.0",
                "license_sha256": "84b7504ce8dda1f37f592cdf67ad21371864583720d79ea289b0b0c75bfcdb17",
                "source_commit": "a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2",
            },
            {
                "scope": "unchanged six-component P5 Lang-1 shared core",
                "rights_manifest_sha256": file_digest(V6 / "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json"),
                "status": "BOUND_FOR_LISTED_SHARED_CASE_COMPONENTS",
            },
            {
                "scope": "V8 control JSON authored in this lane",
                "spdx": "CC0-1.0",
                "license_path": "candidate/shared_core/PACKET-CONTENT-CC0-1.0.txt",
                "authorship_assertion_is_local_not_independent": True,
                "paths": sorted(
                    [f"candidate/control/{name}" for name in authored]
                    + ["candidate/control/P5_C3_RIGHTS_MANIFEST_V8.json"]
                ),
            },
        ],
        "not_included_or_licensed": [
            "DGM initial/ and initial_polyglot/ prior-result payloads",
            "swe_bench/ref_agent_results/",
            "dependencies, containers, model services, generated artifacts, protected scorers and outcomes",
        ],
        "frozen_at_utc": FROZEN_AT,
    }
    rights_name, rights_bytes = write_json("P5_C3_RIGHTS_MANIFEST_V8.json", rights)
    authored[rights_name] = rights_bytes

    seed_members = dgm_members + core_members + [
        (f"candidate/control/{name}", data, 0o444) for name, data in authored.items()
    ]
    seed_bytes = tar_gz(seed_members)
    SEED.write_bytes(seed_bytes)
    member_rows = [
        {"path": path, "size_bytes": len(data), "sha256": digest(data), "mode": oct(mode)}
        for path, data, mode in sorted(seed_members)
    ]
    forbidden_members = [
        row["path"]
        for row in member_rows
        if any(
            token in row["path"]
            for token in ("/initial/", "/initial_polyglot/", "/swe_bench/ref_agent_results/")
        )
    ]
    if forbidden_members:
        raise RuntimeError(f"forbidden members entered candidate seed: {forbidden_members}")

    gates = {
        "exact_mutable_agent_immutable_host_split": True,
        "input_native_certificate_committed_before_self_edit": True,
        "endpoint_policy_bytes": True,
        "tool_policy_bytes": True,
        "write_policy_bytes": True,
        "excluded_outcome_prefixes_absent": True,
        "shared_core_identity_unchanged": True,
        "exact_invocation_environment_bytes": True,
        "native_dgm_can_initialize_from_candidate_safe_seed": False,
    }
    status = "BOUND" if all(gates.values()) else "BLOCKING"
    residual = None if status == "BOUND" else "UNCHANGED_DGM_REQUIRES_EXCLUDED_INITIAL_OUTCOME_METADATA_TO_INITIALIZE"
    next_discriminator = None if status == "BOUND" else (
        "A source-native DGM release must expose an outcome-free initial-state interface, or a separately named preregistered successor adapter must do so without fabricating prior performance fields; native C3 cannot be silently patched."
    )
    finished_at = now()
    receipt = {
        "schema_version": "orion.p5.c3.native-task-environment-receipt.v8",
        "authority": "OUTCOME_BLIND_BYTE_LEVEL_C3_TASK_ENVIRONMENT_ONLY",
        "arm_id": "C3_ARCHIVE_BASED_SELF_EDIT__DGM",
        "case_id": "P5-PUBLIC-LANG1-COMMON-001",
        "field": "runtime.task_environment",
        "status": status,
        "field_instances_closed": 1 if status == "BOUND" else 0,
        "gates": gates,
        "residual": residual,
        "next_discriminator": next_discriminator,
        "candidate_seed": {
            "path": SEED.name,
            "sha256": digest(seed_bytes),
            "size_bytes": len(seed_bytes),
            "member_count": len(member_rows),
            "members": member_rows,
            "excluded_prefix_files": 1595,
            "excluded_prefix_blob_bytes": 49_707_333,
            "excluded_payload_contents_opened": False,
        },
        "source_receipt": {
            "path": FILTER_RECEIPT.name,
            "sha256": file_digest(FILTER_RECEIPT),
        },
        "native_blocker_evidence": {
            "path": str(blocker_evidence_path.relative_to(HERE)),
            "sha256": digest(blocker_excerpt),
            "source_path": "dgm/DGM_outer.py",
            "source_sha256": digest(dgm_outer),
            "line_ranges": [[15, 35], [50, 68]],
        },
        "predecessor": provenance["predecessor_gate"],
        "runtime_seconds": round(time.monotonic() - clock, 6),
        "started_at": started_at,
        "finished_at": finished_at,
        "executions": {"dgm": 0, "model": 0, "benchmark": 0, "scorer": 0, "outcomes": 0},
        "claims": {
            "runtime_image": "CANNOT_CHECK",
            "execution_readiness": "NOT_ESTABLISHED",
            "performance": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
        },
    }
    RECEIPT.write_bytes(jbytes(receipt))
    lines = [
        "# P5 C3 native task environment V8",
        "",
        f"- Field: `runtime.task_environment`",
        f"- Status: **`{status}`**",
        f"- Candidate-safe seed: `{SEED.name}`",
        f"- Seed SHA-256: `{digest(seed_bytes)}`",
        f"- Seed members: **{len(member_rows)}** = 55 filtered DGM source + 6 unchanged Lang-1 core + {len(authored)} control files",
        "- Excluded: **1,595 files / 49,707,333 blob bytes** from `initial/`, `initial_polyglot/`, and `swe_bench/ref_agent_results/`",
        "- DGM/model/benchmark/scorer/outcome executions: **0/0/0/0/0**",
        f"- Build runtime: **{receipt['runtime_seconds']:.6f} s**",
        "",
        "## Gate adjudication",
        "",
    ]
    for gate, passed in gates.items():
        lines.append(f"- `{'PASS' if passed else 'FAIL'}` — `{gate}`")
    lines.extend(
        [
            "",
            "## Exact residual",
            "",
            f"`{residual}`",
            "",
            "The unchanged native `DGM_outer.py` initializes the archive as `initial`, requires an `initial/` directory, and then reads prior `overall_performance` fields such as accuracy and resolved counts. Those bytes belong to the frozen 1,595-file exclusion. The new seed therefore closes every byte-materialization criterion but cannot truthfully establish a native runnable task environment.",
            "",
            f"Next discriminator: {next_discriminator}",
            "",
            "No manuscript/shared packet was edited and no C4 validator, pytest, CI, Git command, DGM, model, benchmark, scorer, or outcome was executed.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n")
    print(
        "P5_C3_V8_CANDIDATE_SAFE_ENVIRONMENT_BUILT__"
        f"STATUS={status}__MEMBERS={len(member_rows)}__SEED_SHA256={digest(seed_bytes)}__"
        f"RUNTIME_SECONDS={time.monotonic() - clock:.6f}"
    )


if __name__ == "__main__":
    main()
