#!/usr/bin/env python3
"""Build a typed retrospective representation of the historically prospective Q3 V0.

V0 itself was frozen on 2026-08-21 before either instrument outcome and before the
later R6P/R6Q resolving evidence.  The generic FrontierDecisionItem schema was
added later during publication refinement.  This script therefore does **not**
create a new prospective benchmark item.  It reconstructs the already-committed
V0 chronology into the publication schema so readers can inspect the typed
lifecycle and verify that later scoring remains separate from the old decisions.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from orion_research_harness.frontier_benchmark import (
    DeferredAlignment,
    FrontierDecisionItem,
    FrontierDeferredScore,
    FrontierInstrumentDecision,
    FrontierRelation,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

PRE_OUTCOME_FILES = (
    "development/orion-q-max-r0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md",
    "research/extensions/orion-q/MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json",
    "research/extensions/orion-q/MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_RESULTS.json",
    "research/extensions/orion-q/MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json",
    "research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json",
)

RESOLVING_FILES = (
    "research/extensions/orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json",
    "research/extensions/orion-q/MAX_R6Q_REGIME_PREDICATE_RESULTS.json",
)

LANE_A_RECEIPT = (
    "development/orion-q-max-r0/dual-harness-benchmark-v0/"
    "DUAL_HARNESS_LANE_A_RECEIPT.json"
)
LANE_B_RECEIPT = "development/orion-q-max-r0/DUAL_HARNESS_LANE_B_RECEIPT.json"
ORIGINAL_RESULT = (
    "development/orion-q-max-r0/dual-harness-benchmark-v0/"
    "DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_RESULTS.json"
)


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_manifest(paths: tuple[str, ...]) -> list[dict[str, str]]:
    rows = []
    for relative in paths:
        path = REPO_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        rows.append({"path": relative, "sha256": file_digest(path)})
    return rows


def manifest_digest(rows: list[dict[str, str]]) -> str:
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def relation(a: FrontierInstrumentDecision, b: FrontierInstrumentDecision) -> FrontierRelation:
    if a.cannot_check and b.cannot_check:
        return FrontierRelation.CANNOT_CHECK_BOTH
    if a.cannot_check:
        return FrontierRelation.CANNOT_CHECK_A
    if b.cannot_check:
        return FrontierRelation.CANNOT_CHECK_B
    diagnosis_same = a.diagnosis == b.diagnosis
    move_same = a.move == b.move
    if diagnosis_same and move_same:
        return FrontierRelation.AGREE
    if diagnosis_same or move_same:
        return FrontierRelation.PARTIAL
    return FrontierRelation.DISAGREE


def build() -> dict[str, Any]:
    pre = evidence_manifest(PRE_OUTCOME_FILES)
    resolving = evidence_manifest(RESOLVING_FILES)
    pre_digest = manifest_digest(pre)
    resolving_digest = manifest_digest(resolving)

    item = FrontierDecisionItem.create(
        item_id="ORION-Q3-V0-post-r6o-diagnosis",
        programme_id="ORION-Q",
        question=(
            "Given the committed R6 receipts through R6O, which epistemic layer is "
            "responsible for the remaining gap and what is the correct next research move?"
        ),
        evidence_digest=pre_digest,
        admissible_evidence=tuple(row["path"] for row in pre),
        diagnosis_coordinates=(
            "REPRESENTATION_REGIME_CHARACTERIZATION",
            "DONOR_FAMILY_INCOMPLETE",
            "METHOD_LANGUAGE_INADEQUATE",
            "CURRENT_SEARCH_INCOMPLETE",
        ),
        move_coordinates=(
            "REGIME_CHARACTERIZATION",
            "WEIGHT2_CLOSURE",
            "DONOR_EXTENSION",
            "METHOD_LANGUAGE_GROWTH",
            "FURTHER_SEARCH",
        ),
        deferred_scoring_rule=(
            "Score a move ALIGNED only if later committed exact scientific evidence "
            "establishes the corresponding registered frontier coordinate; preserve "
            "UNRESOLVED when later evidence does not decide it and INVALIDATED_ITEM "
            "when a frozen protocol defect makes the coordinate unscorable."
        ),
        freeze_epoch="2026-08-21",
    )

    lane_a = FrontierInstrumentDecision.create(
        item=item,
        instrument_id="ORION_GENERIC_RECEIPT_REPLAY_HOST",
        diagnosis=("REPRESENTATION_REGIME_CHARACTERIZATION",),
        move=("REGIME_CHARACTERIZATION",),
        decision_epoch="2026-08-21:lane-a-frozen-before-comparison",
    )
    lane_b = FrontierInstrumentDecision.create(
        item=item,
        instrument_id="ORION_TYPED_NON_LLM_CAMPAIGN_CONTROLLER",
        diagnosis=("REPRESENTATION_REGIME_CHARACTERIZATION",),
        move=("REGIME_CHARACTERIZATION",),
        decision_epoch="2026-08-21:lane-b-frozen-before-comparison",
    )

    score_a = FrontierDeferredScore.create(
        item=item,
        decision=lane_a,
        resolving_evidence_digest=resolving_digest,
        alignment=DeferredAlignment.ALIGNED,
        resolution_epoch="2026-08-21:R6P-R6Q-registered-resolution",
    )
    score_b = FrontierDeferredScore.create(
        item=item,
        decision=lane_b,
        resolving_evidence_digest=resolving_digest,
        alignment=DeferredAlignment.ALIGNED,
        resolution_epoch="2026-08-21:R6P-R6Q-registered-resolution",
    )

    for relative in (LANE_A_RECEIPT, LANE_B_RECEIPT, ORIGINAL_RESULT):
        if not (REPO_ROOT / relative).is_file():
            raise FileNotFoundError(relative)

    return {
        "schema": "ORION.Q3.TypedV0PublicationRecord.v1",
        "provenance_status": (
            "RETROFITTED_TYPED_VIEW_OF_HISTORICALLY_PROSPECTIVE_V0; the V0 protocol "
            "was frozen before instrument outcomes, but this generic typed schema was "
            "introduced later during publication refinement"
        ),
        "original_protocol": PRE_OUTCOME_FILES[0],
        "original_lane_a_receipt": LANE_A_RECEIPT,
        "original_lane_b_receipt": LANE_B_RECEIPT,
        "original_result": ORIGINAL_RESULT,
        "pre_outcome_evidence_manifest": pre,
        "resolving_evidence_manifest": resolving,
        "frontier_item": {**item.unsigned(), "item_digest": item.item_digest},
        "instrument_decisions": [
            {**lane_a.unsigned(), "decision_digest": lane_a.decision_digest},
            {**lane_b.unsigned(), "decision_digest": lane_b.decision_digest},
        ],
        "pre_outcome_relation": relation(lane_a, lane_b).value,
        "deferred_scores": [
            {**score_a.unsigned(), "score_digest": score_a.score_digest},
            {**score_b.unsigned(), "score_digest": score_b.score_digest},
        ],
        "authority": (
            "publication/reproducibility reconstruction only; does not create another "
            "prospective item, reliability estimate, scientific authority, or independence claim"
        ),
    }


def main() -> None:
    print(json.dumps(build(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
