"""Independently re-derive frozen P4 V2 H1/H2/H3 facts. Never relabel H3."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orion.transfer.v2.canonical import content_digest

FOLLOWUP_PROTOCOL_ID = "P4.partial-evidence-acquisition.v2"
FROZEN_P4_CAMPAIGN_ID = "P4.protected-authority.v2"

_REPO = Path(__file__).resolve().parents[4]
_P4 = _REPO / "papers" / "orion-14-verified-scientific-discovery"
_METRICS = _P4 / "evidence" / "protected_v2" / "PUBLICATION_METRICS_V2.json"
_FAMILY = _P4 / "evidence" / "protected_v2" / "FAMILY_CONTRAST_V2.json"
_READINESS = _P4 / "JOURNAL_READINESS.md"


class IntegrityError(ValueError):
    """Frozen P4 V2 facts failed independent re-derivation."""


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def reproduce_p4_v2_hypotheses() -> dict[str, Any]:
    metrics = _load(_METRICS)
    family = _load(_FAMILY)
    readiness = _READINESS.read_text(encoding="utf-8")

    if metrics["campaign_run_id"] != "31976589735":
        raise IntegrityError("frozen campaign_run_id mismatch")
    if metrics["subject_commit"] != "f6e51b5c8f905382b8e2f5568d9035fc14241aa1":
        raise IntegrityError("frozen subject_commit mismatch")
    if "ORION-14 = PEER_REVIEW_READY" not in readiness:
        raise IntegrityError("JOURNAL_READINESS no longer attests PEER_REVIEW_READY")
    if "NOT_SUPPORTED" not in readiness:
        raise IntegrityError("JOURNAL_READINESS no longer preserves the H3 null")

    repro = metrics["reproduction"]
    opportunities = int(repro["promotion_opportunities"])
    orion_fp = int(repro["orion_false_promotions"])
    comparator_fp = int(repro["comparator_false_promotions"])
    orion_clean = int(repro["orion_clean_promotions"])
    comparator_clean = int(repro["comparator_clean_promotions"])
    clean_total = int(repro["clean_total"])
    h1_effect = (orion_fp - comparator_fp) / opportunities
    h2_effect = (orion_clean - comparator_clean) / clean_total
    if orion_fp != 0 or comparator_fp != 180 or opportunities != 360:
        raise IntegrityError("H1 headline counts do not reproduce")
    if abs(h1_effect - (-0.5)) > 1e-12:
        raise IntegrityError("H1 effect does not reproduce from headline counts")
    if metrics["hypotheses"]["H1"]["status"] != "PASS":
        raise IntegrityError("frozen H1 status is not PASS")
    if orion_clean != 60 or comparator_clean != 60 or clean_total != 60:
        raise IntegrityError("H2 headline counts do not reproduce")
    if h2_effect != 0.0:
        raise IntegrityError("H2 effect does not reproduce")
    if metrics["hypotheses"]["H2"]["status"] != "PASS":
        raise IntegrityError("frozen H2 status is not PASS")

    insufficient = family["families"]["INSUFFICIENT_EVIDENCE"]
    n = int(insufficient["ORION"]["n"])
    orion_cc = int(round(float(insufficient["ORION"]["correct_terminal_rate"]) * n))
    comparator_cc = int(
        round(
            float(insufficient["provenai-citation-fidelity-influence"]["correct_terminal_rate"])
            * int(insufficient["provenai-citation-fidelity-influence"]["n"])
        )
    )
    h3_effect = (orion_cc - comparator_cc) / n
    if n != 30 or orion_cc != 30 or comparator_cc != 30 or h3_effect != 0.0:
        raise IntegrityError("H3 30/30 null does not reproduce")
    if metrics["hypotheses"]["H3"]["status"] != "NOT_SUPPORTED":
        raise IntegrityError("frozen H3 was relabeled; stop for integrity repair")

    ablations = metrics["ablations"]
    if len(ablations) != 8:
        raise IntegrityError("expected eight registered ablations")
    worsen = all(int(row["false_promotions"]) > orion_fp for row in ablations.values())
    preserve = all(float(row["clean_coverage"]) == 1.0 for row in ablations.values())
    if not worsen or not preserve:
        raise IntegrityError("ablation diagnostic facts do not reproduce")

    telemetry = metrics["telemetry"]
    telemetry_pass = all(
        int(telemetry[key]) == 0
        for key in (
            "candidate_protected_identifier_hits",
            "comparator_protected_identifier_hits",
            "candidate_external_ip_connects",
            "comparator_external_ip_connects",
        )
    )
    if not telemetry_pass:
        raise IntegrityError("custody telemetry facts do not reproduce")

    h1 = metrics["hypotheses"]["H1"]
    h2 = metrics["hypotheses"]["H2"]
    h3 = metrics["hypotheses"]["H3"]
    unsigned: dict[str, Any] = {
        "schema": "orion.p4.partial-evidence.h3-reproduction.v2",
        "frozen_campaign_id": FROZEN_P4_CAMPAIGN_ID,
        "followup_protocol_id": FOLLOWUP_PROTOCOL_ID,
        "p4_v2_readiness": "PEER_REVIEW_READY",
        "subject_commit": metrics["subject_commit"],
        "campaign_run_id": metrics["campaign_run_id"],
        "H1": {
            "status": "PASS",
            "orion_false_promotions": f"{orion_fp}/{opportunities}",
            "comparator_false_promotions": f"{comparator_fp}/{opportunities}",
            "effect": h1_effect,
            "ci95": [h1["ci95_low"], h1["ci95_high"]],
        },
        "H2": {
            "status": "PASS",
            "orion_clean_promotions": f"{orion_clean}/{clean_total}",
            "comparator_clean_promotions": f"{comparator_clean}/{clean_total}",
            "effect": h2_effect,
            "ci95": [h2["ci95_low"], h2["ci95_high"]],
        },
        "H3": {
            "status": "NOT_SUPPORTED",
            "orion_correct_cannot_check": f"{orion_cc}/{n}",
            "comparator_correct_cannot_check": f"{comparator_cc}/{n}",
            "effect": h3_effect,
            "ci95": [h3["ci95_low"], h3["ci95_high"]],
            "relabeled": False,
            "note": "Easy-abstention saturation; H3 remains a null and is not converted into a follow-up win.",
        },
        "ablations_worsen_false_promotion": True,
        "ablations_preserve_clean_coverage": True,
        "telemetry_pass": True,
    }
    return {**unsigned, "receipt_digest": content_digest(unsigned)}
