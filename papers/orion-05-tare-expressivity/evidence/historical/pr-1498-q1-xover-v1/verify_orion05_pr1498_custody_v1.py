#!/usr/bin/env python3
"""Verify exact historical custody for the adverse PR #1498 Q1-XOVER study.

This verifier never executes the archived experiment.  It checks byte custody,
the donor commit/tag, the recorded RUN_INCOMPLETE outcome and the narrow
authority boundary that prevents the old direct-D++ timeouts from being promoted
into either a positive general crossover or a refutation of the later sparse
O(n^9) solver theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tarfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
MANIFEST_NAME = "ORION05_PR1498_CUSTODY_V1.json"
DONOR_HEAD = "272f2a1aa7b63d409fc460b35bb89e4aa8b5dcbb"
DONOR_BASE = "25004a302b938344c3f47c00f7ad680de6aca9a0"
ARCHIVE_TAG = "archive/orion-01-05/pr-1498-head-272f2a1aa7b6"
ALLOWED_EFFECT = "HISTORICAL_OLD_DXX_BUDGET_FRONTIER_ONLY"
LOCAL_ARCHIVE_TERMINAL = (
    "ORION05_PR1498_LOCAL_ARCHIVE_PASS__DONOR_OBJECTS_NOT_CHECKED"
)
DONOR_OBJECT_VERIFICATION_PASS = "VERIFIED_TAG_COMMIT_LINEAGE_DIFF_AND_BLOBS"
REQUIRED_FORBIDDEN_PROMOTIONS = {
    "GENERAL_POSITIVE_CROSSOVER",
    "SPARSE_O_N9_REFUTATION",
    "PRODUCTION_ACCELERATION_OR_RESOURCE_VALUE",
    "REWRITE_RAW_RECEIPT_OR_P6_FALSE",
}
EXPECTED_OUTCOMES = {
    "P1_all_size_theorem": True,
    "P2_sandwich": True,
    "P3_family_size_identity": True,
    "P4_witness_support": True,
    "P5_r6q_identity_fresh_subject": True,
    "P6_feasibility_rule": False,
}
EXPECTED_BY_N = {
    1: {"sampled": 72, "exact": 72, "timeouts": 0},
    2: {"sampled": 96, "exact": 96, "timeouts": 0},
    3: {"sampled": 96, "exact": 96, "timeouts": 0},
    4: {"sampled": 72, "exact": 72, "timeouts": 0},
    5: {"sampled": 36, "exact": 36, "timeouts": 0},
    6: {"sampled": 12, "exact": 0, "timeouts": 12},
}


def _fail(label: str, detail: Any) -> None:
    raise AssertionError({label: detail})


def _require(condition: bool, label: str, detail: Any) -> None:
    if not condition:
        _fail(label, detail)


def _git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
    ).strip()


def _git_bytes(*args: str) -> bytes:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, stderr=subprocess.STDOUT
    )


def _required_git(label: str, *args: str) -> str:
    """Run one strict donor-object check and convert absence into custody failure."""

    try:
        return _git(*args)
    except subprocess.CalledProcessError as error:
        raise AssertionError(
            {
                label: {
                    "git_args": list(args),
                    "returncode": error.returncode,
                    "output": str(error.output or "").strip(),
                },
            }
        ) from None


def _required_git_bytes(label: str, *args: str) -> bytes:
    """Byte-returning strict donor check with the same fail-closed boundary."""

    try:
        return _git_bytes(*args)
    except subprocess.CalledProcessError as error:
        output = error.output or b""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        raise AssertionError(
            {
                label: {
                    "git_args": list(args),
                    "returncode": error.returncode,
                    "output": output.strip(),
                },
            }
        ) from None


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob(data: bytes) -> str:
    framed = f"blob {len(data)}\0".encode("ascii") + data
    try:
        return hashlib.sha1(framed, usedforsecurity=False).hexdigest()
    except TypeError:  # pragma: no cover - compatibility with older Python
        return hashlib.sha1(framed).hexdigest()


def _load_manifest(archive_root: Path) -> dict[str, Any]:
    return json.loads((archive_root / MANIFEST_NAME).read_text(encoding="utf-8"))


def require_scientific_disposition(
    proposed: str, *, archive_root: Path | None = None
) -> str:
    """Allow only historical adverse custody; reject scientific promotion."""

    archive_root = Path(archive_root or HERE)
    manifest = _load_manifest(archive_root)
    disposition = manifest["scientific_disposition"]
    allowed = disposition["allowed_effect"]
    forbidden = set(disposition["forbidden_promotions"])
    if proposed != allowed:
        _fail(
            "promotion_not_permitted",
            {
                "proposed": proposed,
                "allowed": allowed,
                "explicitly_forbidden": proposed in forbidden,
            },
        )
    return allowed


def _verify_donor_and_file_bindings(
    archive_root: Path,
    manifest: dict[str, Any],
    *,
    require_donor_objects: bool,
) -> tuple[int, str]:
    donor = manifest["donor"]
    expected_donor = {
        "pull_request": 1498,
        "head_ref": "r1/q1-xover-20260827",
        "head_commit": DONOR_HEAD,
        "merge_base_commit": DONOR_BASE,
        "archive_tag": ARCHIVE_TAG,
        "archive_tag_kind": "LIGHTWEIGHT_COMMIT_TAG",
        "archive_tag_target": DONOR_HEAD,
        "changed_path_count": 14,
    }
    _require(donor == expected_donor, "donor_binding_drift", donor)

    diff_rows: list[tuple[str, str]] | None = None
    if require_donor_objects:
        tag_ref = f"refs/tags/{ARCHIVE_TAG}"
        tag_kind = _required_git("required_archive_tag_missing", "cat-file", "-t", tag_ref)
        _require(tag_kind == "commit", "archive_tag_kind_drift", tag_ref)
        tag_target = _required_git("required_archive_tag_unresolvable", "rev-parse", tag_ref)
        _require(tag_target == DONOR_HEAD, "archive_tag_target_drift", tag_ref)
        _require(
            _required_git("required_donor_head_missing", "cat-file", "-t", DONOR_HEAD)
            == "commit",
            "donor_head_kind_drift",
            DONOR_HEAD,
        )
        _require(
            _required_git("required_donor_base_missing", "cat-file", "-t", DONOR_BASE)
            == "commit",
            "donor_base_kind_drift",
            DONOR_BASE,
        )
        _require(
            _required_git(
                "required_donor_lineage_objects_missing",
                "merge-base",
                DONOR_BASE,
                DONOR_HEAD,
            )
            == DONOR_BASE,
            "donor_lineage_drift",
            {"base": DONOR_BASE, "head": DONOR_HEAD},
        )

        diff_rows = []
        donor_diff = _required_git(
            "required_donor_diff_objects_missing",
            "diff",
            "--name-status",
            f"{DONOR_BASE}..{DONOR_HEAD}",
        )
        for line in donor_diff.splitlines():
            fields = line.split("\t")
            _require(len(fields) == 2, "donor_rename_or_copy_not_supported", line)
            diff_rows.append((fields[0], fields[1]))
        _require(
            all(status == "A" for status, _ in diff_rows),
            "donor_paths_not_additive",
            diff_rows,
        )

    records = manifest["files"]
    _require(len(records) == 14, "file_record_count_drift", len(records))
    original_paths = [row["original_path"] for row in records]
    archived_paths = [row["archive_path"] for row in records]
    _require(len(set(original_paths)) == 14, "duplicate_original_path", original_paths)
    _require(len(set(archived_paths)) == 14, "duplicate_archive_path", archived_paths)
    if diff_rows is not None:
        _require(
            set(diff_rows) == {("A", path) for path in original_paths},
            "donor_changed_path_set_drift",
            {"donor": diff_rows, "manifest": original_paths},
        )

    raw_root = (archive_root / "raw").resolve()
    actual_archived_paths = {
        str(path.relative_to(archive_root))
        for path in raw_root.rglob("*")
        if path.is_file()
    }
    _require(
        actual_archived_paths == set(archived_paths),
        "raw_archive_membership_drift",
        {
            "missing": sorted(set(archived_paths) - actual_archived_paths),
            "extra": sorted(actual_archived_paths - set(archived_paths)),
        },
    )

    for row in records:
        original = row["original_path"]
        expected_archive_path = f"raw/{original}"
        _require(
            row["source_commit"] == DONOR_HEAD
            and row["archive_path"] == expected_archive_path,
            "per_file_source_binding_drift",
            row,
        )
        relative = Path(row["archive_path"])
        _require(
            not relative.is_absolute() and ".." not in relative.parts,
            "unsafe_archive_path",
            row["archive_path"],
        )
        path = (archive_root / relative).resolve()
        _require(
            path.is_relative_to(archive_root.resolve()),
            "archive_path_escape",
            str(path),
        )
        data = path.read_bytes()
        observed = {
            "git_mode": "100755" if path.stat().st_mode & 0o111 else "100644",
            "git_blob": _git_blob(data),
            "sha256": _sha256(data),
            "byte_count": len(data),
        }
        declared = {key: row[key] for key in observed}
        _require(observed == declared, "archived_file_binding_drift", {original: observed})
        if require_donor_objects:
            tree_line = _required_git(
                "required_donor_path_missing",
                "ls-tree",
                DONOR_HEAD,
                "--",
                original,
            )
            tree_fields = tree_line.split()
            _require(
                len(tree_fields) >= 3 and tree_fields[0] == row["git_mode"],
                "donor_file_mode_drift",
                {"path": original, "ls_tree": tree_line},
            )
            _require(
                _required_git(
                    "required_donor_path_missing",
                    "rev-parse",
                    f"{DONOR_HEAD}:{original}",
                )
                == row["git_blob"],
                "donor_blob_binding_drift",
                original,
            )
            _require(
                _required_git_bytes(
                    "required_donor_blob_missing",
                    "cat-file",
                    "blob",
                    row["git_blob"],
                )
                == data,
                "archived_bytes_differ_from_donor",
                original,
            )
    donor_verification = (
        DONOR_OBJECT_VERIFICATION_PASS if require_donor_objects else "NOT_REQUESTED"
    )
    return len(records), donor_verification


def _verify_scientific_boundary(
    archive_root: Path, manifest: dict[str, Any]
) -> dict[str, Any]:
    raw = archive_root / "raw"
    qroot = raw / "research" / "extensions" / "orion-q"
    result = json.loads((qroot / "Q1_XOVER_RESULTS_V1.json").read_text())
    _require(result["verdict"] == "RUN_INCOMPLETE", "raw_verdict_drift", result["verdict"])
    _require(
        result["prediction_outcomes"] == EXPECTED_OUTCOMES,
        "raw_prediction_outcomes_drift",
        result["prediction_outcomes"],
    )
    _require(
        result["frozen_config"]["dxx_budget_s"] == 600.0,
        "per_cell_budget_drift",
        result["frozen_config"],
    )

    instances_by_n = [
        (cell["n"], instance)
        for cells in result["panel"].values()
        for cell in cells
        for instance in cell["instances"]
    ]
    observed_by_n = {
        n: {
            "sampled": sum(row_n == n for row_n, _ in instances_by_n),
            "exact": sum(
                row_n == n and row["dxx"]["status"] == "EXACT"
                for row_n, row in instances_by_n
            ),
            "timeouts": sum(
                row_n == n and row["dxx"]["status"] == "TIMEOUT"
                for row_n, row in instances_by_n
            ),
        }
        for n in range(1, 7)
    }
    _require(observed_by_n == EXPECTED_BY_N, "raw_coverage_drift", observed_by_n)
    _require(
        all(
            row["dxx"]["status"] in {"EXACT", "TIMEOUT"}
            for _, row in instances_by_n
        ),
        "unexpected_panel_status",
        [row["dxx"]["status"] for _, row in instances_by_n],
    )

    disposition = manifest["scientific_disposition"]
    _require(
        disposition["raw_terminal_preserved_verbatim"] == "RUN_INCOMPLETE",
        "manifest_raw_terminal_drift",
        disposition,
    )
    raw_summary = disposition["raw_observations"]
    _require(
        raw_summary
        == {
            "sampled_cells_total": 384,
            "n_le_5_exact": 372,
            "n_le_5_nonexact": 0,
            "n_6_sampled": 12,
            "n_6_timeout": 12,
            "per_cell_budget_seconds": 600,
            "algorithm_executed": "4^(2n)-table direct D++ implementation",
            "sparse_o_n9_solver_executed": False,
        },
        "manifest_raw_summary_drift",
        raw_summary,
    )

    defects = disposition["authority_defects_preserved"]
    required_defects = {
        "registered_p6_did_not_predict_zero_timeouts": True,
        "evaluator_added_unregistered_timeouts_equal_zero_clause": True,
        "evaluator_structural_clause_did_not_test_named_n_gt_6_collections": True,
    }
    _require(
        all(defects.get(key) is value for key, value in required_defects.items()),
        "authority_defect_custody_drift",
        defects,
    )
    _require(
        defects.get("p6_false_is_not_authority_for_general_prediction_refutation") is True,
        "p6_authority_boundary_missing",
        defects,
    )

    registered_p6 = result["predictions"]["P6_feasibility_rule"].lower()
    runner = (qroot / "q1_crossover_evaluation.py").read_text(encoding="utf-8")
    _require("timeout" not in registered_p6, "registered_p6_timeout_clause_drift", registered_p6)
    _require(
        "p6_ok = timeouts == 0" in runner,
        "unregistered_timeout_evaluator_clause_missing",
        "p6_ok = timeouts == 0",
    )
    _require(
        max(n for n, _ in instances_by_n) == 6,
        "panel_structural_coverage_drift",
        sorted({n for n, _ in instances_by_n}),
    )
    named_n_gt_6 = {
        row["n_qubits"] for row in result["chemistry"].values()
    } | {result["fresh_subject"]["n_qubits"]}
    _require(
        named_n_gt_6 == {8, 12},
        "named_n_gt_6_collection_drift",
        named_n_gt_6,
    )
    _require(
        "r6p.dxx_search" in runner
        and "orion05_r11_sparse_direct_solver" not in runner,
        "executed_algorithm_identity_drift",
        "expected old r6p.dxx_search only",
    )

    authority = manifest["authority"]
    _require(
        authority["positive_crossover_established"] is False
        and authority["sparse_o_n9_refuted"] is False
        and authority["production_runtime_value"] is False,
        "improper_scientific_promotion",
        authority,
    )
    _require(
        set(disposition["forbidden_promotions"]) == REQUIRED_FORBIDDEN_PROMOTIONS,
        "forbidden_promotion_set_drift",
        disposition["forbidden_promotions"],
    )
    require_scientific_disposition(ALLOWED_EFFECT, archive_root=archive_root)

    sampled = sum(row["sampled"] for row in observed_by_n.values())
    exact = sum(row["exact"] for n, row in observed_by_n.items() if n <= 5)
    timeouts = observed_by_n[6]["timeouts"]
    return {
        "raw_verdict": result["verdict"],
        "coverage": {
            "sampled": sampled,
            "exact_n_le_5": exact,
            "timeouts_n_6": timeouts,
            "by_n": observed_by_n,
        },
        "authority_defects_preserved": required_defects,
    }


def _verify_source_archive_and_logs(
    archive_root: Path, manifest: dict[str, Any]
) -> dict[str, bool]:
    development = (
        archive_root
        / "raw"
        / "development"
        / "q1-xover-lunarc-2026-08-27"
    )
    source_archive = development / "source.tar.gz"
    actual_sha = _sha256(source_archive.read_bytes())
    run1 = json.loads((development / "SUBMISSION.run1.json").read_text())
    run2 = json.loads((development / "SUBMISSION.json").read_text())
    source_binding = manifest["scientific_disposition"]["source_archive_binding"]
    observed = {
        "archived_blob_matches_run1_submission": actual_sha
        == run1["source_archive_sha256"],
        "archived_blob_matches_run2_submission": actual_sha
        == run2["source_archive_sha256"],
        "run2_source_archive_materialized": any(
            row["sha256"] == run2["source_archive_sha256"]
            for row in manifest["files"]
        ),
    }
    _require(
        source_binding["archived_source_archive_sha256"] == actual_sha
        and source_binding["run1_submission_declared_sha256"]
        == run1["source_archive_sha256"]
        and source_binding["run2_submission_declared_sha256"]
        == run2["source_archive_sha256"],
        "source_archive_declared_binding_drift",
        source_binding,
    )
    _require(
        observed
        == {
            "archived_blob_matches_run1_submission": True,
            "archived_blob_matches_run2_submission": False,
            "run2_source_archive_materialized": False,
        },
        "source_archive_run_binding_drift",
        observed,
    )
    _require(
        all(source_binding[key] is value for key, value in observed.items()),
        "source_archive_manifest_disposition_drift",
        source_binding,
    )
    with tarfile.open(source_archive, "r:gz") as bundle:
        members = set(bundle.getnames())
    _require(
        "research/extensions/orion-q/q1_crossover_evaluation.py" in members
        and "research/extensions/orion-q/Q1_XOVER_PROTOCOL_V1.md" in members,
        "source_archive_membership_drift",
        len(members),
    )

    for log_name in ("q1xover-3544037-run1.out", "q1xover-3544067.out"):
        log = (development / log_name).read_text(encoding="utf-8")
        _require(
            "ORIONQ_Q1XOVER_VERDICT=RUN_INCOMPLETE" in log
            and "ORION_Q1XOVER_RUN_COMPLETE" in log,
            "run_log_terminal_drift",
            log_name,
        )
    return observed


def verify_archive(
    *,
    archive_root: Path | None = None,
    require_donor_objects: bool = False,
) -> dict[str, Any]:
    archive_root = Path(archive_root or HERE)
    manifest = _load_manifest(archive_root)
    _require(
        manifest["schema"] == "ORION.ORION05.HistoricalEvidenceCustody.v1"
        and manifest["paper_id"] == "ORION-05"
        and manifest["terminal"] == "ORION05_PR1498_HISTORICAL_CUSTODY_PASS",
        "manifest_identity_drift",
        {key: manifest.get(key) for key in ("schema", "paper_id", "terminal")},
    )
    files_verified, donor_object_verification = _verify_donor_and_file_bindings(
        archive_root,
        manifest,
        require_donor_objects=require_donor_objects,
    )
    science = _verify_scientific_boundary(archive_root, manifest)
    source_archive_binding = _verify_source_archive_and_logs(archive_root, manifest)
    return {
        "terminal": manifest["terminal"] if require_donor_objects else LOCAL_ARCHIVE_TERMINAL,
        "manifest_terminal": manifest["terminal"],
        "donor_object_verification": donor_object_verification,
        "paper_id": manifest["paper_id"],
        "donor_head": DONOR_HEAD,
        "archive_tag": ARCHIVE_TAG,
        "files_verified": files_verified,
        "raw_verdict": science["raw_verdict"],
        "coverage": science["coverage"],
        "authority_defects_preserved": science["authority_defects_preserved"],
        "source_archive_binding": source_archive_binding,
        "scientific_effect": ALLOWED_EFFECT,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    donor_mode = parser.add_mutually_exclusive_group()
    donor_mode.add_argument(
        "--require-donor-objects",
        dest="require_donor_objects",
        action="store_true",
        help="fail closed unless the archive tag and donor commit objects verify",
    )
    donor_mode.add_argument(
        "--local-archive-only",
        dest="require_donor_objects",
        action="store_false",
        help="verify archived bytes and authority only; report donor objects unchecked",
    )
    parser.set_defaults(require_donor_objects=True)
    args = parser.parse_args()
    print(
        json.dumps(
            verify_archive(require_donor_objects=args.require_donor_objects),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
