"""Machine checks for the recursively refined ORION-Q publication specification.

The Q papers are scientific projections of committed framework/evidence surfaces.
This module checks that canonical manuscripts, claim ledgers, review terminals and
load-bearing evidence still agree. It does *not* grant novelty, empirical
superiority, journal acceptance, or physical-quantum authority.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from orion.programme.q_series_content_binding import require_q_series_content_binding
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
            "predicts_journal_acceptance": False,
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


def _require_text(path: Path, needles: tuple[str, ...], *, label: str) -> str:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise ValueError(f"{label}: missing required publication boundary text {missing!r}")
    return text


def validate_q_series_sync(repo_root: Path) -> QSeriesSyncReport:
    # Byte binding runs first so an edited canonical paper/spec cannot pass merely
    # because its replacement text still contains the expected keywords.
    require_q_series_content_binding(repo_root)
    spec = load_q_series_spec(repo_root)
    checks: list[str] = ["canonical_content_binding"]

    if spec.get("schema") != Q_SERIES_PUBLICATION_SPEC_ID:
        raise ValueError("Q-series spec schema no longer matches runtime registry")
    if spec.get("sync_epoch") != Q_SERIES_SYNC_EPOCH:
        raise ValueError("Q-series spec epoch no longer matches runtime registry")
    checks.extend(["spec_schema", "spec_epoch"])

    for key in ("refinement_protocol", "academic_method_donor_pin", "venue_profiles"):
        _require_file(repo_root, str(spec.get(key, "")), label=f"Q-series {key}")
    checks.append("recursive_refinement_contract")

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
    checks.append("canonical_v3_manuscripts")

    owner = spec.get("owner_decisions", {})
    if owner.get("external_quantum_expert_review") != "SKIPPED_BY_OWNER":
        raise ValueError("external expert-review disposition changed without a new Q-series spec")
    if "PASS" in str(owner.get("effect", "")).upper():
        raise ValueError("skipping external expert review must never be encoded as a scientific PASS")
    if owner.get("future_prospective_upgrade_studies") != (
        "REQUIRED_ONLY_FOR_CLAIMS_THAT_EXCEED_CURRENT_SCOPED_TERMINALS"
    ):
        raise ValueError("successor-research disposition changed without a new Q-series spec")
    checks.append("owner_decisions_non_authorizing")

    # Q1 — theorem + sharpness + bounded PRX/npj targeting.
    q1 = papers["Q1"]
    for required in q1.get("required_internal_evidence", []):
        _require_file(repo_root, str(required), label="Q1 evidence")
    _require_file(repo_root, str(q1["claim_ledger"]), label="Q1 claim ledger")
    if q1.get("current_internal_status") != (
        "READY_FOR_SCOPED_TARGET__PRX_INTERNAL_PREFLIGHT_AND_NPJQI"
    ):
        raise ValueError("Q1 V3 scoped-readiness state drifted")
    if q1.get("novelty_search_status") != "NOT_LOCATED_IN_BOUNDED_SEARCH__NOT_NOVELTY_CERTIFICATE":
        raise ValueError("Q1 novelty-search boundary changed without a new final spec")
    _require_text(
        repo_root / str(q1["round2_review"]),
        ("PRX Quantum", "READY_FOR_SCOPED_TARGET", "npj Quantum Information"),
        label="Q1 round-two review",
    )
    sanity = _load_json(
        repo_root
        / "papers/orion-05-tare-expressivity/INDEPENDENT_HUMAN_PROOF_SANITY_RESULTS_2026-08-22.json"
    )
    if sanity.get("status") != "PASS" or sanity.get("orion_quantum_imports") is not False:
        raise ValueError("Q1 independent sanity record no longer has the declared bounded PASS")
    if sanity.get("restore_lemma", {}).get("max_delta_f3") != 2:
        raise ValueError("Q1 Restore bound drifted from max Delta F3 = 2")
    class_lemma = sanity.get("class_lemma", {})
    if class_lemma.get("w3_to_w8_failure_count") != 0 or len(class_lemma.get("w2_failures", [])) != 4:
        raise ValueError("Q1 finite-core sanity no longer matches the sharp support-two boundary")

    r6s = _load_json(repo_root / "research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json")
    if r6s.get("outcome") != "THEOREM_MACHINE_CHECKED":
        raise ValueError("Q1 all-n theorem receipt no longer reports THEOREM_MACHINE_CHECKED")
    covers = str(r6s.get("claim_boundary", {}).get("covers", ""))
    if "EVERY qubit count n" not in covers or "support <= 2" not in covers:
        raise ValueError("Q1 theorem scope text no longer binds the all-n support-two claim")

    r6o = _load_json(repo_root / "research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json")
    witnesses = r6o.get("discovery", {}).get("instances_with_dp_strictly_below_dplus", [])
    if not any(
        row.get("instance_index") == 16
        and row.get("C_unrestricted_dp") == 5
        and row.get("C_Dplus") == 6
        for row in witnesses
        if isinstance(row, dict)
    ):
        raise ValueError("Q1 sharpness witness 5<6 at structured n=2 instance 16 is missing")
    checks.extend(["q1_v3_scope", "q1_sanity", "q1_all_n_receipt", "q1_sharpness_witness"])

    # Q2 — scoped single-programme method paper ready; broad causal/general claim blocked.
    q2 = papers["Q2"]
    for required in q2.get("required_internal_evidence", []):
        _require_file(repo_root, str(required), label="Q2 evidence")
    _require_file(repo_root, str(q2["claim_ledger"]), label="Q2 claim ledger")
    if q2.get("current_internal_status") != (
        "READY_FOR_SCOPED_TARGET__NPJ_AI_POSITIONING_RISK__NCS_EVIDENCE_BLOCKED"
    ):
        raise ValueError("Q2 scoped/stretch readiness boundary drifted")
    if q2.get("stretch_terminal") != "EVIDENCE_BLOCKED":
        raise ValueError("Q2 Nature Computational Science blocker was silently removed")
    if not str(q2.get("current_target_terminal", "")).startswith("READY_FOR_SCOPED_TARGET"):
        raise ValueError("Q2 scoped current-target terminal no longer records readiness")
    _require_text(
        repo_root / str(q2["round2_review"]),
        ("EVIDENCE_BLOCKED", "READY_FOR_SCOPED_TARGET", "single-programme"),
        label="Q2 round-two review",
    )
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
    checks.extend(["q2_v3_scope", "q2_final_closure_receipts", "q2_stretch_blocker_preserved"])

    # Q3 — systems contract improved, predictive impact remains blocked by N=1.
    q3 = papers["Q3"]
    if q3.get("required_harness_contract") != Q3_HARNESS_PUBLICATION_CONTRACT_ID:
        raise ValueError("Q3 paper/harness publication contract id drifted")
    for required in q3.get("required_internal_evidence", []):
        _require_file(repo_root, str(required), label="Q3 evidence")
    _require_file(repo_root, str(q3["claim_ledger"]), label="Q3 claim ledger")
    if q3.get("current_internal_status") != "SYSTEMS_REFINED__NPJ_PREDICTIVE_EVIDENCE_BLOCKED":
        raise ValueError("Q3 N=1 evidence-limited status drifted")
    if q3.get("predictive_npj_terminal") != "EVIDENCE_BLOCKED":
        raise ValueError("Q3 predictive npj evidence blocker was silently removed")
    q3_text = _require_text(
        repo_root / str(q3["canonical_manuscript"]),
        ("one demonstration", "not a reliability estimate", "deferred outcome scoring"),
        label="Q3 manuscript",
    )
    if "predictive validity" not in q3_text.lower() and "predictive" not in q3_text.lower():
        raise ValueError("Q3 manuscript lost explicit predictive-validity boundary")
    _require_text(
        repo_root / str(q3["round2_review"]),
        ("N=1", "EVIDENCE_BLOCKED", "benchmark-definition"),
        label="Q3 round-two review",
    )
    checks.extend(["q3_typed_benchmark_contract", "q3_one_item_boundary", "q3_predictive_blocker_preserved"])

    # Q4 — scoped exact-synthetic benchmark ready; real-agent transfer remains blocked.
    q4 = papers["Q4"]
    for required in q4.get("required_internal_evidence", []):
        _require_file(repo_root, str(required), label="Q4 evidence")
    _require_file(repo_root, str(q4["claim_ledger"]), label="Q4 claim ledger")
    if q4.get("current_internal_status") != (
        "READY_FOR_SCOPED_TARGET__NPJ_AI_POSITIONING_RISK__NMI_EVIDENCE_BLOCKED"
    ):
        raise ValueError("Q4 scoped/stretch readiness boundary drifted")
    if q4.get("stretch_terminal") != "EVIDENCE_BLOCKED":
        raise ValueError("Q4 real-transfer/NMI evidence blocker was silently removed")
    q4_text = _require_text(
        repo_root / str(q4["canonical_manuscript"]),
        ("post-study", "exact-synthetic", "real scientific-agent"),
        label="Q4 manuscript",
    )
    if "does not claim real scientific-agent effectiveness" not in q4_text:
        raise ValueError("Q4 manuscript lost the real-agent transfer boundary")
    paired = _load_json(repo_root / "papers/orion-08-typed-state/PUBLICATION_PAIRED_ANALYSIS_V1.json")
    stale = paired["studies"]["N4_B"]["STALE_MATTERS"]["scoped_vs_never_mean_round_utility"]
    waste = paired["studies"]["N4_B"]["REOPEN_WASTEFUL"]["scoped_vs_never_mean_round_utility"]
    for label, row in (("STALE_MATTERS", stale), ("REOPEN_WASTEFUL", waste)):
        lo, hi = row["bootstrap_95pct_ci"]
        if not (lo <= 0.0 <= hi):
            raise ValueError(f"Q4 N4-B {label} scoped-vs-never boundary no longer crosses zero")
    _require_text(
        repo_root / str(q4["round2_review"]),
        ("EVIDENCE_BLOCKED", "READY_FOR_SCOPED_TARGET", "bootstrap"),
        label="Q4 round-two review",
    )
    checks.extend(["q4_v3_scope", "q4_paired_analysis", "q4_n4b_boundary", "q4_transfer_blocker_preserved"])

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
