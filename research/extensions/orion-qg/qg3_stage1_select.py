#!/usr/bin/env python3
"""QG-3 stage 1: prospectively locate a positive R6Q trade regime with DP forbidden."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
ORION_Q_DIR = REPO_ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(ORION_Q_DIR))

import max_r6r_prospective_fresh_subject as r6r  # noqa: E402

CANDIDATE_CAP = 12
R6R_BENZENE_BLOB = "5c02c72b88e12b391ea1d8f77eb6b3e04fc2a915"
PROTOCOL_PATH = REPO_ROOT / "development" / "orion-qg-regime-geometry" / "QG3_POSITIVE_FORECAST_PROTOCOL_V1.md"
NOVELTY_PATH = REPO_ROOT / "development" / "orion-qg-regime-geometry" / "QG3_NOVELTY_THREAT_FREEZE_2026-08-21.md"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "orion-qg-qg3-stage1.json"
TOKEN_PREFIX = "ORIONQG_QG3_STAGE1="


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_stage1() -> dict[str, Any]:
    if not PROTOCOL_PATH.is_file() or not NOVELTY_PATH.is_file():
        raise FileNotFoundError("QG-3 freeze artifacts missing")

    dp_call_count = 0
    original_exact_dp = r6r.r6m.exact_r6m_matching

    def _dp_forbidden(*_args, **_kwargs):
        nonlocal dp_call_count
        dp_call_count += 1
        raise AssertionError("QG-3 stage 1 attempted unrestricted DP before dual-harness admission")

    r6r.r6m.exact_r6m_matching = _dp_forbidden
    try:
        f3_binding = bool(np.array_equal(r6r.r6q.F3.astype(np.int64), r6r.r6m._F3))
        listing = r6r.pinned_tree_listing()
        ducc_listing = [(p, b) for p, b in listing if p.endswith(".ducc.results.txt")]
        tree_digest = r6r.sha256_text(
            "\n".join(f"{b} {p}" for p, b in ducc_listing) + "\n"
        )
        candidates = [
            cfg
            for cfg in r6r.eligible_candidates(listing)
            if cfg["blob"] != R6R_BENZENE_BLOB
        ]

        attempts: list[dict[str, Any]] = []
        selected: dict[str, Any] | None = None
        for candidate_order, cfg in enumerate(candidates[:CANDIDATE_CAP]):
            if cfg["path"] == r6r.PROTECTED_STRETCHED_N2_PATH:
                raise AssertionError("protected stretched N2 became QG-3 candidate")
            admission = r6r.try_admit(cfg)
            attempt = {
                "candidate_order": candidate_order,
                "path": cfg["path"],
                "blob": cfg["blob"],
                "n_qubits": cfg["n_qubits"],
                "admitted": bool(admission.get("admitted")),
                "reason": admission.get("reason"),
            }
            if not admission.get("admitted"):
                attempts.append(attempt)
                continue

            matchings, predictions = r6r.stage1_predict(
                admission["terms"], admission["six"], int(cfg["n_qubits"])
            )
            positive_index = next(
                (
                    index
                    for index, row in enumerate(predictions)
                    if int(row["predicted_C_DP"]) < int(row["C_R6L"])
                ),
                None,
            )
            attempt.update(
                {
                    "six_source_indices": list(admission["six"]),
                    "champion_windows": list(admission["champion_windows"]),
                    "positive_matching_found": positive_index is not None,
                }
            )
            attempts.append(attempt)
            if positive_index is None:
                continue

            row = predictions[positive_index]
            predicted_cost = int(row["predicted_C_DP"])
            donor_cost = int(row["C_R6L"])
            if predicted_cost >= donor_cost:
                raise AssertionError("positive selector admitted a non-positive row")
            selected = {
                "candidate_order": candidate_order,
                "matching_order": positive_index,
                "subject": {
                    "commit": cfg["commit"],
                    "path": cfg["path"],
                    "blob": cfg["blob"],
                    "n_occ": cfg["n_occ"],
                    "n_virt": cfg["n_virt"],
                    "n_orb": cfg["n_orb"],
                    "n_qubits": cfg["n_qubits"],
                },
                "six_source_indices": list(admission["six"]),
                "champion_windows": list(admission["champion_windows"]),
                "matching": [list(pair) for pair in matchings[positive_index]],
                "prediction": row,
                "strict_donor_gap_predicted": donor_cost - predicted_cost,
            }
            break

        positive_found = selected is not None
        freshness_pass = bool(
            not positive_found
            or (
                selected["subject"]["blob"] not in set(r6r.COMMITTED_SUBJECT_BLOBS)
                and selected["subject"]["blob"] != R6R_BENZENE_BLOB
                and selected["subject"]["path"] != r6r.PROTECTED_STRETCHED_N2_PATH
            )
        )
        protected_unread = all(
            attempt["path"] != r6r.PROTECTED_STRETCHED_N2_PATH for attempt in attempts
        )
        no_dp_calls = dp_call_count == 0
        admission_gates_pass = bool(
            f3_binding and freshness_pass and protected_unread and no_dp_calls
        )

        base = {
            "schema": "ORION.QG.QG3.Stage1Prediction.v1",
            "issue": "SzeChunYiu/ORION#745",
            "base_revision": "13a0fc6afb1d150a114ec318d72830e3c6722b03",
            "candidate_cap": CANDIDATE_CAP,
            "library": {
                "repo": r6r.REPO,
                "commit": r6r.PINNED_COMMIT,
                "ducc_listing_sha256": tree_digest,
                "ducc_results_files_at_commit": len(ducc_listing),
            },
            "protocol_sha256": _sha256_file(PROTOCOL_PATH),
            "novelty_threat_sha256": _sha256_file(NOVELTY_PATH),
            "excluded_prior_benzene_blob": R6R_BENZENE_BLOB,
            "attempts": attempts,
            "positive_found": positive_found,
            "selected": selected,
            "predicate_binding_exact": f3_binding,
            "freshness_pass": freshness_pass,
            "protected_unread": protected_unread,
            "no_dp_calls": no_dp_calls,
            "dp_call_count": dp_call_count,
            "admission_gates_pass": admission_gates_pass,
            "ground_truth_opened": False,
            "novelty_authority": False,
        }
        base["stage1_digest"] = _sha256_bytes(_canonical(base).encode("utf-8"))
        return base
    finally:
        r6r.r6m.exact_r6m_matching = original_exact_dp


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    packet = run_stage1()
    output = Path(args.output)
    _write(output, packet)
    summary = {
        "stage1_path": str(output),
        "stage1_digest": packet["stage1_digest"],
        "positive_found": packet["positive_found"],
        "admission_gates_pass": packet["admission_gates_pass"],
        "no_dp_calls": packet["no_dp_calls"],
        "protected_unread": packet["protected_unread"],
        "selected": packet["selected"],
    }
    print(TOKEN_PREFIX + _canonical(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
