#!/usr/bin/env python3
"""Generate a deterministic six-round formal conformance campaign."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

from sealed_ledger import append_payload, finalize_campaign, initialize_campaign

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PROTOCOL.json"
SUBJECT = "ef02823e68f64965df27d056db8ac387246affeb"


def sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def q(numerator: int, denominator: int = 1) -> dict[str, int]:
    return {"numerator": numerator, "denominator": denominator}


def payload(
    round_number: int,
    *,
    components: dict[str, bool],
    deterministic: dict[str, bool] | None = None,
    raw_alpha: dict[str, int] | None = None,
    inflation: dict[str, int] | None = None,
    beta: dict[str, int] | None = None,
    promotion_identity: str = "promotion-authority-v1",
    note: str,
) -> dict[str, Any]:
    if deterministic is None:
        deterministic = {
            "resource": True,
            "custody": True,
            "authority": True,
            "candidate_bytes": True,
            "current_execution": True,
            "negative_history_retained": True,
        }
    return {
        "receipt_id": f"RSP-CONFORMANCE-{round_number:02d}",
        "candidate_id": f"candidate-{round_number:02d}",
        "candidate_sha256": sha(f"candidate-bytes-{round_number}"),
        "subject_revision": SUBJECT,
        "epoch_id": "protected-epoch-A" if round_number <= 4 else "protected-epoch-B",
        "protected_dataset_commitment": sha(
            "sealed-protected-A" if round_number <= 4 else "sealed-protected-B"
        ),
        "raw_alpha": raw_alpha or q(1, 1000),
        "leakage_inflation": inflation or q(2, 1),
        "leakage_beta": beta or q(1, 10000),
        "component_gates": components,
        "deterministic_gates": deterministic,
        "candidate_generator_identity": "candidate-generator-v1",
        "protected_evaluator_identity": "protected-evaluator-v1",
        "promotion_authority_identity": promotion_identity,
        "outcome_note": note,
    }


def run(output: Path) -> dict[str, Any]:
    if output.exists():
        shutil.rmtree(output)
    protocol_digest = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    initialize_campaign(
        output,
        campaign_id="SELF-ORION-RSP-CONFORMANCE-V1",
        alpha_total=Fraction(1, 20),
        protocol_sha256=protocol_digest,
        subject_revision=SUBJECT,
        candidate_generator_identity="candidate-generator-v1",
        protected_evaluator_identity="protected-evaluator-v1",
        promotion_authority_identity="promotion-authority-v1",
        archivist_identity="append-only-archivist-v1",
    )

    rounds = [
        payload(
            1,
            components={"fresh": True, "retention": True, "harm": True},
            note="all statistical and deterministic gates pass",
        ),
        payload(
            2,
            components={"fresh": False, "retention": True, "harm": True},
            note="replay repair does not transfer to fresh protected cases",
        ),
        payload(
            3,
            components={"fresh": True, "retention": True, "harm": True},
            deterministic={
                "resource": True,
                "custody": True,
                "authority": False,
                "candidate_bytes": True,
                "current_execution": True,
                "negative_history_retained": True,
            },
            promotion_identity="candidate-generator-v1",
            note="candidate attempted to self-certify promotion",
        ),
        payload(
            4,
            components={"fresh": True, "retention": True, "harm": True},
            deterministic={
                "resource": True,
                "custody": True,
                "authority": True,
                "candidate_bytes": True,
                "current_execution": False,
                "negative_history_retained": True,
            },
            raw_alpha=q(0, 1),
            inflation=q(1, 1),
            beta=q(0, 1),
            note="current execution failed; stale success is not substitutable",
        ),
        payload(
            5,
            components={"fresh": True, "retention": True, "harm": True},
            raw_alpha=q(1, 1500),
            inflation=q(3, 2),
            beta=q(1, 20000),
            note="second protected epoch with independently registered leakage debit",
        ),
        payload(
            6,
            components={"fresh": True, "retention": True, "harm": False},
            raw_alpha=q(1, 1500),
            inflation=q(3, 2),
            beta=q(1, 20000),
            note="fresh gain is vetoed by the harmful-transfer component",
        ),
    ]
    events = [append_payload(output, row) for row in rounds]
    final = finalize_campaign(output)
    summary = {
        "schema": "ORION.SelfOrion.ReusableSealedConformanceSummary.v1",
        "event_decisions": [event["decision"] for event in events],
        "event_dispositions": [event["disposition"] for event in events],
        "final_receipt_digest": final["receipt_digest"],
        "formal_terminal": final["formal_terminal"],
        "empirical_authority_delta": "NONE",
    }
    (output / "CONFORMANCE_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    summary = run(args.output)
    print("SELF_ORION_RSP_CONFORMANCE=" + json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
