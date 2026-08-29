#!/usr/bin/env python3
"""Fail-closed verifier for the exact ORION-06 negative-revival LUNARC run."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
from typing import Any, BinaryIO, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUNDLE_REL = Path(
    "development/orion-05-06-negative-revival-r1-2026-08-27/evidence/"
    "run-e9d4ee1df73ff22fb5742ff2cd9c200b0a5f29f9-v1"
)
PROTOCOL_COMMIT = "7483a04dae9d1bdc9a3e6faeb6383592dff91754"
EXECUTION_COMMIT = "e9d4ee1df73ff22fb5742ff2cd9c200b0a5f29f9"
SOURCE_ARCHIVE_SHA256 = "19dc73f450e71ce3b84f152d32fa535b2db05961316bfb9b2c391af39a9c85fd"
STAGE_MANIFEST_SHA256 = "2164cca8a3926a3af71554484b68cb85fbd832d2719bd127b48756b77be5a5fa"
RUN_MANIFEST_SHA256 = "723be0b268c294a08aff2b31d6f89b507431b4b5cd6d77ea34dd122b8642b991"

PROTOCOL_REL = (
    "papers/orion-06-recursive-recovery/revival/"
    "ORION06_NEGATIVE_REVIVAL_R1_PROTOCOL.json"
)
RUNNER_REL = (
    "papers/orion-06-recursive-recovery/revival/"
    "orion06_negative_revival_r1.py"
)
R6K_RUNNER_REL = (
    "research/extensions/orion-q/"
    "max_r6k_exact_rank2_shared_tag_restore_factor_dp.py"
)
R6L_RUNNER_REL = (
    "research/extensions/orion-q/"
    "max_r6l_three_tare2_shared_factor_donor.py"
)
KNOWN_R6K_REL = (
    "research/extensions/orion-q/"
    "MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_RESULTS.json"
)
KNOWN_R6L_REL = (
    "research/extensions/orion-q/"
    "MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_RESULTS.json"
)

POINT_COORDS = (
    "Lambda_joint",
    "parity_CNOT",
    "controlled_Rz",
    "controlled_H",
    "controlled_Pauli_support",
    "AND2_compute_uncompute_pairs",
    "max_extra_conjunction_scratch",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def _git_blob(root: Path, commit: str, relative: str) -> bytes:
    return _git(root, "show", f"{commit}:{relative}")


def _parse_manifest(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in path.read_text().splitlines():
        digest, relative = line.split("  ", 1)
        relative = relative.removeprefix("./")
        if relative in rows:
            raise AssertionError({"duplicate_manifest_path": relative})
        rows[relative] = digest
    return rows


def _verify_run_manifest(bundle: Path) -> int:
    manifest = bundle / "RUN_SHA256SUMS"
    if sha256_file(manifest) != RUN_MANIFEST_SHA256:
        raise AssertionError("run manifest digest drift")
    recorded = (bundle / "RUN_SHA256SUMS.sha256").read_text().split()[0]
    if recorded != RUN_MANIFEST_SHA256:
        raise AssertionError("run manifest sidecar drift")
    rows = _parse_manifest(manifest)
    for relative, expected in rows.items():
        target = bundle / relative
        if not target.is_file():
            raise AssertionError({"missing_run_file": relative})
        observed = sha256_file(target)
        if observed != expected:
            raise AssertionError(
                {"run_file_hash_mismatch": [relative, expected, observed]}
            )
    expected_files = {
        path.relative_to(bundle).as_posix()
        for path in bundle.rglob("*")
        if path.is_file()
        and path.name not in {"RUN_SHA256SUMS", "RUN_SHA256SUMS.sha256"}
    }
    if set(rows) != expected_files:
        raise AssertionError(
            {
                "run_manifest_completeness": {
                    "missing": sorted(expected_files - set(rows)),
                    "extra": sorted(set(rows) - expected_files),
                }
            }
        )
    return len(rows)


class _HashingReader:
    def __init__(self, stream: BinaryIO):
        self.stream = stream
        self.digest = hashlib.sha256()

    def read(self, size: int = -1) -> bytes:
        payload = self.stream.read(size)
        self.digest.update(payload)
        return payload


def _verify_stage_against_git_archive(root: Path, bundle: Path) -> dict[str, Any]:
    manifest_path = bundle / "manifests/STAGE_SHA256SUMS"
    if sha256_file(manifest_path) != STAGE_MANIFEST_SHA256:
        raise AssertionError("stage manifest digest drift")
    expected = _parse_manifest(manifest_path)
    process = subprocess.Popen(
        ["git", "archive", "--format=tar.gz", EXECUTION_COMMIT],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None
    reader = _HashingReader(process.stdout)
    observed: dict[str, str] = {}
    symlinks: list[tuple[str, str]] = []
    with tarfile.open(fileobj=reader, mode="r|gz") as archive:
        for member in archive:
            if member.isfile():
                source = archive.extractfile(member)
                if source is None:
                    raise AssertionError({"archive_member_unreadable": member.name})
                observed[member.name] = sha256_bytes(source.read())
            elif member.issym():
                symlinks.append((member.name, member.linkname))
    while reader.read(1024 * 1024):
        pass
    stderr = process.stderr.read() if process.stderr is not None else b""
    if process.wait() != 0:
        raise AssertionError({"git_archive_failed": stderr.decode(errors="replace")})
    if reader.digest.hexdigest() != SOURCE_ARCHIVE_SHA256:
        raise AssertionError("source archive digest drift")
    if observed != expected:
        raise AssertionError(
            {
                "stage_differs_from_execution_commit": {
                    "missing": sorted(set(expected) - set(observed)),
                    "extra": sorted(set(observed) - set(expected)),
                    "hash_mismatch": sorted(
                        path
                        for path in set(expected) & set(observed)
                        if expected[path] != observed[path]
                    ),
                }
            }
        )
    recorded_symlinks = (bundle / "manifests/STAGE_SYMLINKS.txt").read_text().splitlines()
    rendered_symlinks = [f"./{path} -> {target}" for path, target in symlinks]
    if recorded_symlinks != rendered_symlinks:
        raise AssertionError(
            {"stage_symlink_drift": [recorded_symlinks, rendered_symlinks]}
        )
    return {
        "regular_files": len(observed),
        "symlinks": len(symlinks),
        "archive_sha256": SOURCE_ARCHIVE_SHA256,
        "manifest_sha256": STAGE_MANIFEST_SHA256,
    }


def _parse_key_values(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in path.read_text().splitlines():
        if "=" in line and not line.startswith("---") and not line[0].isdigit():
            key, value = line.split("=", 1)
            rows[key] = value
    return rows


def _parse_sacct(path: Path) -> list[dict[str, str]]:
    lines = path.read_text().splitlines()
    header = lines[0].split("|")
    rows = []
    for line in lines[1:]:
        if not line:
            continue
        values = line.split("|")
        rows.append(dict(zip(header, values, strict=True)))
    return rows


def _without_runtime(value: dict[str, Any]) -> dict[str, Any]:
    return {key: row for key, row in value.items() if key != "runtime_seconds"}


def _dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_values = tuple(left[name] for name in POINT_COORDS)
    right_values = tuple(right[name] for name in POINT_COORDS)
    return all(a <= b for a, b in zip(left_values, right_values, strict=True)) and (
        left_values != right_values
    )


def _authority_is_bounded(authority: dict[str, Any]) -> bool:
    prohibited = (
        "prospective_confirmation",
        "new_subject_generalization",
        "end_to_end_qsvt_superiority",
        "hardware_independence",
        "external_independence",
        "novelty",
        "r6",
        "journal_or_submission",
        "final_freeze",
    )
    return all(authority.get(key) in (None, False) for key in prohibited)


def verify(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    bundle = root / BUNDLE_REL
    if not bundle.is_dir():
        raise FileNotFoundError(bundle)

    subprocess.run(
        ["git", "merge-base", "--is-ancestor", PROTOCOL_COMMIT, EXECUTION_COMMIT],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    protocol_at_freeze = _git_blob(root, PROTOCOL_COMMIT, PROTOCOL_REL)
    protocol_at_execution = _git_blob(root, EXECUTION_COMMIT, PROTOCOL_REL)
    if protocol_at_freeze != protocol_at_execution or protocol_at_execution != (
        root / PROTOCOL_REL
    ).read_bytes():
        raise AssertionError("frozen ORION-06 revival protocol was rewritten")
    execution_sources = {}
    for relative in (RUNNER_REL, R6K_RUNNER_REL, R6L_RUNNER_REL):
        committed = _git_blob(root, EXECUTION_COMMIT, relative)
        current = (root / relative).read_bytes()
        if committed != current:
            raise AssertionError({"execution_source_drift": relative})
        execution_sources[relative] = sha256_bytes(committed)

    run_entries = _verify_run_manifest(bundle)
    stage = _verify_stage_against_git_archive(root, bundle)
    remote = _parse_key_values(bundle / "REMOTE_FINAL_VERIFY.txt")
    required_remote = {
        "source_commit": EXECUTION_COMMIT,
        "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
        "stage_manifest_sha256": STAGE_MANIFEST_SHA256,
        "stage_manifest_entries": str(stage["regular_files"]),
        "stage_manifest_failures": "0",
        "stage_symlinks": str(stage["symlinks"]),
    }
    if any(remote.get(key) != value for key, value in required_remote.items()):
        raise AssertionError({"remote_verification_drift": [remote, required_remote]})

    jobs = _parse_sacct(bundle / "scheduler/SACCT_ROOT_JOBS.txt")
    expected_jobs = {
        "3550252": "o6-revival-new",
        "3550253": "o6-r6k-replay",
        "3550254": "o6-r6l-replay",
        "3550255": "o6-revival-adj",
    }
    if {row["JobIDRaw"]: row["JobName"] for row in jobs} != expected_jobs:
        raise AssertionError("scheduler job set drift")
    if not all(
        row["State"] == "COMPLETED"
        and row["ExitCode"] == "0:0"
        and row["Account"] == "hep2023-1-3"
        and row["Partition"] == "hep"
        for row in jobs
    ):
        raise AssertionError({"scheduler_failure": jobs})
    for job_id in expected_jobs:
        stderr_paths = list((bundle / "logs").glob(f"*-{job_id}.err"))
        if len(stderr_paths) != 1 or stderr_paths[0].read_bytes() != b"":
            raise AssertionError({"nonempty_or_missing_stderr": job_id})

    new_resources = json.loads(
        (bundle / "results/ORION06_NEW_RESOURCE_REVIVAL.json").read_text()
    )
    if new_resources["source_commit"] != EXECUTION_COMMIT:
        raise AssertionError("new-resource source commit drift")
    if new_resources["protocol_sha256"] != sha256_bytes(protocol_at_execution):
        raise AssertionError("new-resource protocol digest drift")
    if new_resources["unsolvable"] != [] or not _authority_is_bounded(
        new_resources["authority"]
    ):
        raise AssertionError("new-resource authority promotion")

    r4c = new_resources["attempts"]["R4C_H2_REGIME_LIMITED"]
    r4c_parent = r4c["strongest_parent"]
    if not (
        r4c["revival_outcome"] == "IMPROVED"
        and r4c["matching_count"] == 135135
        and r4c["pair_edge_count"] == 91
        and r4c["source_check"]["terms_exact"] is True
        and all(row["pass"] is True for row in r4c["legacy_frontier_binding"])
        and len(r4c["strict_parent_dominating_points"]) >= 1
        and all(
            _dominates(row, r4c_parent)
            for row in r4c["strict_parent_dominating_points"]
        )
        and r4c["original_negative_preserved"] is True
        and _authority_is_bounded(r4c["authority"])
    ):
        raise AssertionError("R4C revival receipt drift")

    r5b = new_resources["attempts"]["R5B_PROOF_OUTER_REPLAY"]
    if not (
        r5b["revival_outcome"] == "IMPROVED"
        and r5b["matching_count"] == 15
        and r5b["parent_pair_representation_count"] == 15
        and r5b["frozen_source_indices"] == [12, 18, 22, 25, 27, 31]
        and r5b["source"]["source_blob_verified"] is True
        and len(r5b["strict_parent_dominating_points"]) >= 1
        and all(
            not any(_dominates(parent, candidate) for parent in r5b["parent_pareto"])
            and any(_dominates(candidate, parent) for parent in r5b["parent_pareto"])
            for candidate in r5b["strict_parent_dominating_points"]
        )
        and r5b["original_negative_preserved"] is True
        and _authority_is_bounded(r5b["authority"])
    ):
        raise AssertionError("R5B revival receipt drift")

    fresh_r6k = json.loads((bundle / "results/R6K_FRESH_RESULTS.json").read_text())
    fresh_r6l = json.loads((bundle / "results/R6L_FRESH_RESULTS.json").read_text())
    known_r6k = json.loads((root / KNOWN_R6K_REL).read_text())
    known_r6l = json.loads((root / KNOWN_R6L_REL).read_text())
    if _without_runtime(fresh_r6k) != _without_runtime(known_r6k):
        raise AssertionError("fresh R6K replay differs scientifically")
    if _without_runtime(fresh_r6l) != _without_runtime(known_r6l):
        raise AssertionError("fresh R6L replay differs scientifically")

    adjudication = json.loads(
        (bundle / "results/ORION06_METHOD_LANGUAGE_REPLAYS.json").read_text()
    )
    r6i = adjudication["R6I_EXACT_RANK2"]
    r6k = adjudication["R6K_EXACT_RESTORE_FACTOR"]
    if not (
        r6i["revival_outcome"] == "RETAINED_NEGATIVE"
        and r6i["strict_by_subject"] == {"H4": False, "N2": False}
        and r6i["replay_scientifically_equal_to_known_receipt"] is True
        and r6i["original_negative_preserved"] is True
        and _authority_is_bounded(r6i["authority"])
        and r6k["revival_outcome"] == "CORRECT_SUBTRACTION"
        and r6k["strict_by_subject"] == {"H4": True, "N2": True}
        and r6k["replay_scientifically_equal_to_known_receipt"] is True
        and r6k["original_negative_preserved"] is True
        and r6k["authority"]["donor_novelty_credit"] is False
        and _authority_is_bounded(r6k["authority"])
        and adjudication["unsolvable"] == []
    ):
        raise AssertionError("method-language replay adjudication drift")

    return {
        "schema": "ORION.ORION06.NegativeRevivalBundleVerification.v1",
        "terminal": "ORION06_NEGATIVE_REVIVAL_BUNDLE_VERIFIED",
        "scientific_authority_delta": "NONE",
        "bundle": {
            "path": BUNDLE_REL.as_posix(),
            "run_manifest_entries": run_entries,
            "run_manifest_sha256": RUN_MANIFEST_SHA256,
            "stage": stage,
        },
        "source_chronology": {
            "pre_outcome_protocol_commit": PROTOCOL_COMMIT,
            "execution_commit": EXECUTION_COMMIT,
            "protocol_rewritten": False,
            "execution_sources": execution_sources,
        },
        "scheduler": {
            "jobs": expected_jobs,
            "all_completed_exit_zero": True,
            "stderr_empty": True,
        },
        "attempts": {
            "R4C_H2_REGIME_LIMITED": {
                "outcome": r4c["revival_outcome"],
                "matching_count": r4c["matching_count"],
                "strict_points": len(r4c["strict_parent_dominating_points"]),
                "residual": "open-subject mechanism evidence only",
            },
            "R5B_PROOF_OUTER_REPLAY": {
                "outcome": r5b["revival_outcome"],
                "matching_count": r5b["matching_count"],
                "strict_points": len(r5b["strict_parent_dominating_points"]),
                "residual": r5b["residual"],
            },
            "R6I_EXACT_RANK2": {
                "outcome": r6i["revival_outcome"],
                "strict_by_subject": r6i["strict_by_subject"],
            },
            "R6K_EXACT_RESTORE_FACTOR": {
                "outcome": r6k["revival_outcome"],
                "strict_by_subject": r6k["strict_by_subject"],
                "donor_novelty_credit": False,
            },
        },
        "unsolvable": [],
        "authority": {
            "prospective_confirmation": False,
            "external_independence": False,
            "novelty": False,
            "journal_or_submission": False,
            "final_freeze": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = verify(args.root)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload)
    print("ORION06_NEGATIVE_REVIVAL_BUNDLE=PASS")
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
