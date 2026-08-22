"""Machine checks for the final ORION-Q publication specification.

The Q papers are scientific projections of committed framework/evidence surfaces.
This module checks that the canonical manuscripts still point at the declared
claim/evidence boundaries.  It does *not* grant novelty, empirical superiority,
or publication authority.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from orion.registry import (
    Q3_HARNESS_PUBLICATION_CONTRACT_ID,
    Q_SERIES_CANONICAL_MANUSCRIPTS,
    Q_SERIES_PAPER_IDS,
    Q_SERIES_PUBLICATION_SPEC_ID,
    Q_SERIES_SYNC_EPOCH,
)

SPEC_PATH = Path("papers/Q_SERIES_FINAL_SPEC_V1.json")


@dataclass(frozen=True)
class QSeriesSyncReport:
    schema: str
    sync_epoch: str
    checked_papers: tuple[str, ...]
    checks: tuple[str, ...]

    def as_json(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "sync_epoch": self.sync_epoch,
            "checked_papers": list(self.checked_papers),
            "checks": list(self.checks),
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
        }


def _load_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError(f"{path}: expected JSON object")
    return raw


def load_q_series_spec(repo_root: Path) -> dict[str, Any]:
    return _load_json(repo_root / SPEC_PATH)


def _require_file(repo_root: Path, value: str, *, label: str) -> Path:
    path = repo_root / value
    if not path.is_file():
        raise FileNotFoundError(f"{label}: required file missing: {value}")
    return path


def validate_q_series_sync(repo_root: Path) -> QSeriesSyncReport:
    spec = load_q_series_spec(repo_root)
    checks: list[str] = []

    if spec.get("schema") != Q_SERIES_PUBLICATION_SPEC_ID:
        raise ValueError("Q-series spec schema no longer matches runtime registry")
    if spec.get("sync_epoch") != Q_SERIES_SYNC_EPOCH:
        raise ValueError("Q-series spec epoch no longer matches runtime registry")
    checks.extend(["spec_schema", "spec_epoch"])

    papers = spec.get("papers")
    if not isinstance(papers, dict):
        raise TypeError("Q-series spec papers must be an object")
    if tuple(papers) != Q_SERIES_PAPER_IDS:
        raise ValueError(
            f"Q-series paper ids drifted: spec={tuple(papers)!r} registry={Q_SERIES_PAPER_IDS!r}"
        )

    canonical = tuple(str(papers[key]["canonical_manuscript"]) for key in Q_SERIES_PAPER_IDS)
    if canonical != Q_SERIES_CANONICAL_MANUSCRIPTS:
        raise ValueError("canonical Q-series manuscripts drifted from runtime registry")
    for paper_id, path in zip(Q_SERIES_PAPER_IDS, canonical, strict=True):
        _require_file(repo_root, path, label=f"{paper_id} manuscript")
    checks.append("canonical_manuscripts")

    owner = spec.get("owner_decisions", {})
    if owner.get("external_quantum_expert_review") != "SKIPPED_BY_OWNER":
        raise ValueError("external expert-review disposition changed without a new Q-series spec")
    if "PASS" in str(owner.get("effect", "")).upper():
        raise ValueError("skipping external expert review must never be encoded as a scientific PASS")
    checks.append("owner_skip_is_not_pass")

    # Q1: prove that the final sharp theorem still has both an all-n upper bound
    # and an exact support-one counterexample, plus the independent finite-core sanity check.
    q1 = papers["Q1"]
    for required in q1.get("required_internal_evidence", []):
        _require_file(repo_root, str(required), label="Q1 evidence")
    sanity = _load_json(
        repo_root
        / "papers/Q-paper-01-tare-expressivity/INDEPENDENT_HUMAN_PROOF_SANITY_RESULTS_2026-08-22.json"
    )
    if sanity.get("status") != "PASS" or sanity.get("orion_quantum_imports") is not False:
        raise ValueError("Q1 independent sanity record no longer has the declared bounded PASS")
    if sanity.get("restore_lemma", {}).get("max_delta_f3") != 2:
        raise ValueError("Q1 Restore bound drifted from max Delta F3 = 2")
    class_lemma = sanity.get("class_lemma", {})
    if class_lemma.get("w3_to_w8_failure_count") != 0:
        raise ValueError("Q1 class lemma no longer corroborates the support>=3 exchange")
    if len(class_lemma.get("w2_failures", [])) != 4:
        raise ValueError("Q1 sharp support-two boundary no longer has the four recorded w=2 failures")

    r6s = _load_json(repo_root / "research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json")
    if r6s.get("outcome") != "THEOREM_MACHINE_CHECKED":
        raise ValueError("Q1 all-n theorem receipt no longer reports THEOREM_MACHINE_CHECKED")
    covers = str(r6s.get("claim_boundary", {}).get("covers", ""))
    if "EVERY qubit count n" not in covers or "support <= 2" not in covers:
        raise ValueError("Q1 theorem scope text no longer binds the all-n support-two claim")

    r6o = _load_json(repo_root / "research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json")
    witnesses = r6o.get("discovery", {}).get("instances_with_dp_strictly_below_dplus", [])
    sharp = any(
        row.get("instance_index") == 16
        and row.get("C_unrestricted_dp") == 5
        and row.get("C_Dplus") == 6
        for row in witnesses
        if isinstance(row, dict)
    )
    if not sharp:
        raise ValueError("Q1 sharpness witness 5<6 at structured n=2 instance 16 is missing")
    checks.extend(["q1_sanity", "q1_all_n_receipt", "q1_sharpness_witness"])

    # Q2: the methodology manuscript is final only if the receipt index reaches the
    # actual programme closure rather than the pre-R6S draft state.
    q2 = papers["Q2"]
    for required in q2.get("required_internal_evidence", []):
        _require_file(repo_root, str(required), label="Q2 evidence")
    receipt_index = _require_file(
        repo_root, str(q2["receipt_index"]), label="Q2 receipt index"
    ).read_text(encoding="utf-8")
    for needle in (
        "MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json",
        "MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json",
        "MAX_R6Q_REGIME_PREDICATE_RESULTS.json",
        "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json",
        "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json",
        "N4_F3_REMINT_TRANSPORT_RESULTS.json",
        "N2_F5B_DONOR_COMPARISON_RESULTS.json",
    ):
        if needle not in receipt_index:
            raise ValueError(f"Q2 receipt index is stale: missing {needle}")
    checks.append("q2_final_closure_receipts")

    # Q3: the paper must bind to the current repaired harness contract and remain
    # scoped to one benchmark measurement.
    q3 = papers["Q3"]
    if q3.get("required_harness_contract") != Q3_HARNESS_PUBLICATION_CONTRACT_ID:
        raise ValueError("Q3 paper/harness publication contract id drifted")
    for required in q3.get("required_internal_evidence", []):
        _require_file(repo_root, str(required), label="Q3 evidence")
    q3_text = _require_file(
        repo_root, str(q3["canonical_manuscript"]), label="Q3 manuscript"
    ).read_text(encoding="utf-8")
    if "one" not in q3_text.lower() or "benchmark" not in q3_text.lower():
        raise ValueError("Q3 manuscript no longer visibly preserves the one-measurement benchmark scope")
    if "predict" in q3.get("primary_claim", "").lower():
        raise ValueError("Q3 primary claim may not promote agreement to predictive validity")
    checks.append("q3_scoped_harness_contract")

    # Q4: all six primary synthetic result families must remain present and the
    # paper may not silently turn the deferred real-domain protocol into evidence.
    q4 = papers["Q4"]
    for required in q4.get("required_internal_evidence", []):
        _require_file(repo_root, str(required), label="Q4 evidence")
    q4_text = _require_file(
        repo_root, str(q4["canonical_manuscript"]), label="Q4 manuscript"
    ).read_text(encoding="utf-8")
    if "exact-synthetic" not in q4_text.lower() and "exact synthetic" not in q4_text.lower():
        raise ValueError("Q4 manuscript lost its exact-synthetic claim boundary")
    if q4.get("current_internal_status") != "COMPLETE_FOR_SCOPED_MECHANISM_PAPER":
        raise ValueError("Q4 scoped completion status changed without a new final spec")
    checks.append("q4_synthetic_scope")

    return QSeriesSyncReport(
        schema=Q_SERIES_PUBLICATION_SPEC_ID,
        sync_epoch=Q_SERIES_SYNC_EPOCH,
        checked_papers=Q_SERIES_PAPER_IDS,
        checks=tuple(checks),
    )


def require_q_series_sync(repo_root: Path) -> None:
    validate_q_series_sync(repo_root)


__all__ = [
    "QSeriesSyncReport",
    "SPEC_PATH",
    "load_q_series_spec",
    "require_q_series_sync",
    "validate_q_series_sync",
]
