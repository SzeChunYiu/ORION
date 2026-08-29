#!/usr/bin/env python3
"""Exact atomic-custody reconstruction for ORION-21 NR07 anchor v2.

This is a forensic successor. It does not re-adjudicate the width-law study.
It reconstructs the frozen NR07 anchor using integer correlation arithmetic,
enumerates every feature tied at the top-r boundary, and maps the two recorded
aggregate numerators to the resulting exact prediction transcripts.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, NoReturn

import numpy as np


HERE = Path(__file__).resolve().parent


def discover_root() -> Path:
    for candidate in (HERE, *HERE.parents):
        if (candidate / ".git").exists():
            return candidate
    return HERE


ROOT = discover_root()
PROTOCOL_PATH = HERE / "PROTOCOL.json"
MANIFEST_PATH = HERE / "SOURCE_MANIFEST.json"
DEFAULT_OUTPUT_DIR = HERE


def fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        fail(f"{path}: expected a JSON object")
    return value


def git_blob(revision: str, path: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", f"{revision}:{path}"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except subprocess.CalledProcessError as exc:
        fail(f"cannot resolve {revision}:{path}: {exc.output.strip()}")


def git_path_exists(revision: str, path: str) -> bool:
    return (
        subprocess.run(
            ["git", "cat-file", "-e", f"{revision}:{path}"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def verify_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    bindings = manifest.get("bindings")
    if not isinstance(bindings, dict) or not bindings:
        fail("manifest bindings missing")

    checked: list[dict[str, str]] = []
    for name, binding in sorted(bindings.items()):
        if not isinstance(binding, dict):
            fail(f"{name}: binding must be an object")
        path = binding.get("path")
        revision = binding.get("revision", "HEAD")
        expected = binding.get("git_blob_sha")
        if not all(isinstance(x, str) for x in (path, revision, expected)):
            fail(f"{name}: malformed binding")
        actual = git_blob(revision, path)
        if actual != expected:
            fail(f"{name}: expected blob {expected}, got {actual}")
        checked.append(
            {"name": name, "path": path, "revision": revision, "git_blob_sha": actual}
        )

    absent = manifest.get("required_absences")
    if not isinstance(absent, list):
        fail("required_absences must be a list")
    absence_rows: list[dict[str, Any]] = []
    for row in absent:
        if not isinstance(row, dict):
            fail("malformed required_absences row")
        path = row.get("path")
        revision = row.get("revision")
        if not isinstance(path, str) or not isinstance(revision, str):
            fail("malformed absence binding")
        exists = git_path_exists(revision, path)
        if exists:
            fail(f"custody expectation violated: {revision}:{path} exists")
        absence_rows.append({"path": path, "revision": revision, "exists": False})

    return {"bindings": checked, "required_absences": absence_rows}


def bank(x: np.ndarray, subsets: list[tuple[int, ...]]) -> np.ndarray:
    """Committed P11H bank semantics, copied as a tiny auditable kernel."""
    idx = np.asarray(subsets, dtype=np.int16)
    return np.prod(x[:, idx], axis=2, dtype=np.int8)


def rung_stream(seed: int, cell: tuple[int, int, int]) -> np.random.Generator:
    """Committed P11H keyed stream semantics."""
    return np.random.default_rng([seed, 0, *cell])


def pack_bits(
    bits: np.ndarray,
    relative_path: str,
    payloads: dict[str, str],
) -> dict[str, Any]:
    arr = np.asarray(bits, dtype=np.uint8)
    raw = np.packbits(arr, bitorder="little").tobytes()
    encoded = base64.b64encode(raw).decode("ascii") + "\n"
    if relative_path in payloads and payloads[relative_path] != encoded:
        fail(f"conflicting transcript payload for {relative_path}")
    payloads[relative_path] = encoded
    return {
        "encoding": "numpy.packbits/little+base64-file",
        "bit_count": int(arr.size),
        "path": relative_path,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def hash_row_ids(row_ids: list[int]) -> str:
    payload = ",".join(str(row_id) for row_id in row_ids).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def exact_accuracy(numerator: int, denominator: int) -> dict[str, Any]:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "fraction": f"{numerator}/{denominator}",
        "decimal": numerator / denominator,
    }


def generate_anchor(
    protocol: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str]]:
    anchor = protocol["anchor"]
    cell = tuple(int(x) for x in anchor["cell"])
    if len(cell) != 3:
        fail("anchor cell must have three coordinates")
    d, s, r = cell
    seed = int(anchor["seed"])
    train_size = int(anchor["train_size"])
    n_queries = int(anchor["n_queries"])
    n_test = int(anchor["n_test"])
    expected_num = int(anchor["historical_expected_numerator"])
    observed_num = int(anchor["lunarc_observed_numerator"])
    denominator = n_queries * n_test

    if denominator != int(anchor["denominator"]):
        fail("anchor denominator is inconsistent")
    if expected_num / denominator != float(anchor["historical_expected_accuracy"]):
        fail("historical expected decimal is inconsistent")
    if observed_num / denominator != float(anchor["lunarc_observed_accuracy"]):
        fail("LUNARC observed decimal is inconsistent")

    subsets = list(itertools.combinations(range(d), s))
    rng = rung_stream(seed, cell)
    queries = [
        rng.choice(len(subsets), size=r, replace=False).tolist()
        for _ in range(n_queries)
    ]
    test_x = rng.choice((-1, 1), size=(n_test, d)).astype(np.int8)
    test_bank = bank(test_x, subsets)
    train_x = rng.choice((-1, 1), size=(train_size, d)).astype(np.int8)
    train_bank = bank(train_x, subsets)

    query_rows: list[dict[str, Any]] = []
    candidate_correct_lists: list[list[int]] = []
    candidate_feature_lists: list[list[list[int]]] = []
    candidate_predictions: list[list[np.ndarray]] = []
    labels_by_query: list[np.ndarray] = []
    transcript_payloads: dict[str, str] = {}

    for query_id, active in enumerate(queries):
        active_array = np.asarray(active, dtype=np.int64)
        train_y = (train_bank[:, active_array].sum(axis=1) > 0).astype(np.uint8)
        test_y = (test_bank[:, active_array].sum(axis=1) > 0).astype(np.uint8)
        labels_by_query.append(test_y)
        label_bits = pack_bits(
            test_y,
            f"transcript/q{query_id}-labels.bits.b64",
            transcript_payloads,
        )

        y_pm = (2 * train_y.astype(np.int16)) - 1
        correlation_numerators = np.sum(
            train_bank.astype(np.int16) * y_pm[:, None], axis=0, dtype=np.int64
        )
        abs_numerators = np.abs(correlation_numerators)

        ranked_abs = sorted(
            range(len(subsets)), key=lambda index: (-int(abs_numerators[index]), index)
        )
        boundary_abs = int(abs_numerators[ranked_abs[r - 1]])
        fixed = sorted(
            int(index)
            for index in range(len(subsets))
            if int(abs_numerators[index]) > boundary_abs
        )
        tied = sorted(
            int(index)
            for index in range(len(subsets))
            if int(abs_numerators[index]) == boundary_abs
        )
        need = r - len(fixed)
        if need < 0:
            fail(f"query {query_id}: negative boundary need")

        candidates: list[dict[str, Any]] = []
        correct_counts: list[int] = []
        support_options: list[list[int]] = []
        prediction_options: list[np.ndarray] = []

        for candidate_id, chosen in enumerate(itertools.combinations(tied, need)):
            support = fixed + list(chosen)
            signs = np.sign(correlation_numerators[support]).astype(np.int16)
            if np.any(signs == 0):
                fail(f"query {query_id}: zero-sign selected at nonzero boundary")
            scores = np.sum(
                test_bank[:, support].astype(np.int16) * signs[None, :],
                axis=1,
                dtype=np.int16,
            )
            predictions = (scores > 0).astype(np.uint8)
            correct_count = int(np.count_nonzero(predictions == test_y))
            mismatch_rows = np.flatnonzero(predictions != test_y).astype(int).tolist()
            candidates.append(
                {
                    "candidate_id": candidate_id,
                    "support_feature_indices": support,
                    "correct_count": correct_count,
                    "incorrect_count": n_test - correct_count,
                    "prediction_bits": (
                        {
                            "encoding": "reference/query-label",
                            "bit_count": n_test,
                            "reference_query_id": query_id,
                            "sha256": label_bits["sha256"],
                        }
                        if correct_count == n_test
                        else pack_bits(
                            predictions,
                            f"transcript/q{query_id}-candidate{candidate_id}-predictions.bits.b64",
                            transcript_payloads,
                        )
                    ),
                    "mismatch_test_row_ids_sha256": hash_row_ids(mismatch_rows),
                }
            )
            correct_counts.append(correct_count)
            support_options.append(support)
            prediction_options.append(predictions)

        candidate_correct_lists.append(correct_counts)
        candidate_feature_lists.append(support_options)
        candidate_predictions.append(prediction_options)
        query_row: dict[str, Any] = {
            "query_id": query_id,
            "label_bits": label_bits,
            "candidate_count": len(candidates),
            "candidates": candidates,
        }
        if query_id == 0:
            query_row.update(
                {
                    "correlation_denominator": train_size,
                    "boundary_abs_correlation_numerator": boundary_abs,
                    "fixed_above_boundary_feature_indices": fixed,
                    "boundary_tied_feature_indices": tied,
                }
            )
        query_rows.append(query_row)

    worlds: list[dict[str, Any]] = []
    ranges = [range(len(values)) for values in candidate_correct_lists]
    for world_id, selection in enumerate(itertools.product(*ranges)):
        numerator = sum(
            candidate_correct_lists[query_id][candidate_id]
            for query_id, candidate_id in enumerate(selection)
        )
        worlds.append(
            {
                "world_id": world_id,
                "query_candidate_ids": list(selection),
                "accuracy": exact_accuracy(numerator, denominator),
            }
        )

    expected_worlds = [
        world for world in worlds if world["accuracy"]["numerator"] == expected_num
    ]
    observed_worlds = [
        world for world in worlds if world["accuracy"]["numerator"] == observed_num
    ]

    if len(expected_worlds) != 1 or len(observed_worlds) != 1:
        terminal = "NR07_EXACT_ANCHOR_NONUNIQUE_ORIGIN_CANNOT_CHECK"
        transcript_delta: dict[str, Any] | None = None
    else:
        expected_selection = expected_worlds[0]["query_candidate_ids"]
        observed_selection = observed_worlds[0]["query_candidate_ids"]
        differing_rows: list[dict[str, Any]] = []
        expected_correct = 0
        observed_correct = 0
        for query_id, (expected_candidate, observed_candidate) in enumerate(
            zip(expected_selection, observed_selection, strict=True)
        ):
            expected_pred = candidate_predictions[query_id][expected_candidate]
            observed_pred = candidate_predictions[query_id][observed_candidate]
            labels = labels_by_query[query_id]
            diff = np.flatnonzero(expected_pred != observed_pred)
            if diff.size:
                expected_correct_on_diff = int(
                    np.count_nonzero(expected_pred[diff] == labels[diff])
                )
                observed_correct_on_diff = int(
                    np.count_nonzero(observed_pred[diff] == labels[diff])
                )
                expected_correct += expected_correct_on_diff
                observed_correct += observed_correct_on_diff
                differing_rows.append(
                    {
                        "query_id": query_id,
                        "prediction_disagreement_count": int(diff.size),
                        "test_row_ids_sha256": hash_row_ids(diff.astype(int).tolist()),
                        "historical_expected_correct_on_disagreements": expected_correct_on_diff,
                        "lunarc_observed_correct_on_disagreements": observed_correct_on_diff,
                    }
                )
        net = observed_num - expected_num
        if observed_correct - expected_correct != net:
            fail("raw transcript net does not equal aggregate numerator delta")
        transcript_delta = {
            "aggregate_numerator_delta": net,
            "aggregate_accuracy_delta": exact_accuracy(net, denominator),
            "prediction_disagreement_count": sum(
                row["prediction_disagreement_count"] for row in differing_rows
            ),
            "differing_queries": differing_rows,
            "historical_expected_correct_on_disagreements": expected_correct,
            "lunarc_observed_correct_on_disagreements": observed_correct,
        }

        q0 = query_rows[0]
        localized = (
            q0["boundary_tied_feature_indices"] == [35, 93, 263]
            and q0["candidates"][expected_selection[0]]["support_feature_indices"]
            == [16, 311, 35]
            and q0["candidates"][observed_selection[0]]["support_feature_indices"]
            == [16, 311, 93]
            and transcript_delta["prediction_disagreement_count"] == 1011
            and net == 1
        )
        terminal = (
            "NR07_EXACT_ANCHOR_ARGSORT_BOUNDARY_TIE_LOCALIZED"
            if localized
            else "NR07_EXACT_ANCHOR_DISCREPANCY_NOT_LOCALIZED"
        )

    result = {
        "schema": "ORION.ORION21.NR07.ExactAnchorResult.v2",
        "protocol_identity": protocol["protocol_identity"],
        "anchor": {
            "cell": list(cell),
            "seed": seed,
            "train_size": train_size,
            "n_queries": n_queries,
            "n_test": n_test,
            "denominator": denominator,
            "feature_bank_width": len(subsets),
            "row_order": "query_id then test_row_id in generator order",
        },
        "recorded_pair": {
            "historical_expected": exact_accuracy(expected_num, denominator),
            "lunarc_observed": exact_accuracy(observed_num, denominator),
        },
        "queries": query_rows,
        "aggregate_worlds": worlds,
        "historical_expected_matching_world_ids": [
            world["world_id"] for world in expected_worlds
        ],
        "lunarc_observed_matching_world_ids": [
            world["world_id"] for world in observed_worlds
        ],
        "transcript_delta": transcript_delta,
        "forensic_terminal": terminal,
    }
    return result, transcript_payloads


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    protocol = load_json(PROTOCOL_PATH)
    manifest = load_json(MANIFEST_PATH)
    if protocol.get("schema") != "ORION.ORION21.NR07.ExactAnchorProtocol.v2":
        fail("unexpected protocol schema")
    if manifest.get("schema") != "ORION.ORION21.NR07.ExactAnchorSourceManifest.v2":
        fail("unexpected source manifest schema")

    source_check = verify_manifest(manifest)
    anchor_result, transcript_payloads = generate_anchor(protocol)

    scientific_terminal = protocol["authority"]["controlling_scientific_terminal"]
    custody_terminal = protocol["authority"]["source_custody_terminal"]
    expected_forensic = protocol["authority"]["expected_forensic_terminal"]
    if anchor_result["forensic_terminal"] != expected_forensic:
        fail(
            f"forensic terminal {anchor_result['forensic_terminal']} "
            f"does not match frozen expected terminal {expected_forensic}"
        )

    result = {
        **anchor_result,
        "source_check": {
            "bindings_checked": len(source_check["bindings"]),
            "required_absences_checked": len(source_check["required_absences"]),
        },
        "source_custody_terminal": custody_terminal,
        "controlling_scientific_terminal": scientific_terminal,
        "scientific_authority_delta": "NONE",
        "submission_authority": False,
        "terminal": (
            f"{anchor_result['forensic_terminal']}__"
            f"{custody_terminal}__SCIENCE_REMAINS_{scientific_terminal}"
        ),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for relative_path, transcript_payload in sorted(transcript_payloads.items()):
        output_path = args.output_dir / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(transcript_payload, encoding="ascii")

    payload = json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"
    (args.output_dir / "RESULT.json").write_text(payload, encoding="utf-8")
    print(result["terminal"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"NR07_EXACT_ANCHOR_V2_RED: {exc}", file=sys.stderr)
        raise
