#!/usr/bin/env python3
"""Fail-closed completion gate for Paper Q3.

This checker grants no scientific or submission authority. It verifies the chronology and
artifact completeness of the prospective Q3 case series after the scientific result files
and replay/score receipts have been committed.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
Q3 = ROOT / "papers/Q-paper-03-dual-instrument"

PREOUTCOME_ANCHOR = "85bb1bc013b8148e2e2d9664cabd17e8bbd7b1a1"
ANALYZER_COMMITS = {
    "Q3-R1": "4737de39e7bb9b794a6730d869b541f6d128ed47",
    "Q3-R2": "a261ea2a56566e35cfca86f34740ca04d4be2404",
}
INSTANCES = {
    "Q3-R1": {
        "dir": Q3 / "instances/Q3-R1-QG19",
        "result": ROOT / "research/extensions/orion-qg/QG19_OUTSIDE_CONE_SHARPNESS_RESULTS.json",
        "frontier": "QG-19",
    },
    "Q3-R2": {
        "dir": Q3 / "instances/Q3-R2-QG20",
        "result": ROOT / "research/extensions/orion-qg/QG20_SIXLCU_OBJECTIVE_SCOPE_RESULTS.json",
        "frontier": "QG-20",
    },
}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()


def load(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    required_global = [
        Q3 / "Q3_REPLACEMENT_PROSPECTIVE_PROTOCOL_V2.md",
        Q3 / "Q3_CONTAMINATION_DISPOSITION_2026-08-22.md",
        Q3 / "Q3_D2_D3_DISPOSITION_V2.md",
    ]
    for path in required_global:
        if not path.is_file():
            errors.append(f"MISSING_GLOBAL:{path.relative_to(ROOT)}")

    # Both clean replacement instruments must predate scientific analyzer introduction.
    for instance, commit in ANALYZER_COMMITS.items():
        try:
            subprocess.run(["git", "merge-base", "--is-ancestor", PREOUTCOME_ANCHOR, commit],
                           cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if PREOUTCOME_ANCHOR == commit:
                errors.append(f"CHRONOLOGY_DEGENERATE:{instance}")
        except subprocess.CalledProcessError:
            errors.append(f"PREOUTCOME_NOT_ANCESTOR_OF_ANALYZER:{instance}")

    for instance, cfg in INSTANCES.items():
        d = cfg["dir"]
        for name in (
            "QUESTION_FREEZE.json", "SHARED_PACKET.json", "LANE_A_RECEIPT.json",
            "LANE_B_MANIFEST.json", "LANE_B_RECEIPT.json", "PREOUTCOME_AGREEMENT.json",
            "EXPERIMENT_LOG.md", "DEFERRED_OUTCOME_BINDING.json", "FINAL_SCORE.json",
            "INDEPENDENT_REPLAY_RECEIPT.json",
        ):
            if not (d / name).is_file():
                errors.append(f"MISSING_INSTANCE_FILE:{instance}:{name}")
        if not cfg["result"].is_file():
            errors.append(f"MISSING_SCIENTIFIC_RESULT:{instance}:{cfg['result'].relative_to(ROOT)}")
            continue

        if all((d / n).is_file() for n in ("LANE_A_RECEIPT.json", "LANE_B_RECEIPT.json", "PREOUTCOME_AGREEMENT.json")):
            a = load(d / "LANE_A_RECEIPT.json")
            b = load(d / "LANE_B_RECEIPT.json")
            pre = load(d / "PREOUTCOME_AGREEMENT.json")
            if a.get("scientific_outcome_accessed") is not False:
                errors.append(f"LANE_A_NOT_PROSPECTIVE:{instance}")
            if b.get("scientific_outcome_accessed") is not False:
                errors.append(f"LANE_B_NOT_PROSPECTIVE:{instance}")
            if pre.get("scientific_outcome_accessed") is not False:
                errors.append(f"PREOUTCOME_AGREEMENT_NOT_PROSPECTIVE:{instance}")
            if a.get("frontier_question_id") != cfg["frontier"] or b.get("frontier_question_id") != cfg["frontier"]:
                errors.append(f"FRONTIER_ID_DRIFT:{instance}")

        if (d / "FINAL_SCORE.json").is_file():
            score = load(d / "FINAL_SCORE.json")
            if score.get("score_status") != "SCORED":
                errors.append(f"INSTANCE_NOT_SCORED:{instance}:{score.get('score_status')}")
            if score.get("aggregate_reliability_claim_authorized") is not False:
                errors.append(f"ILLEGAL_RELIABILITY_PROMOTION:{instance}")

        if (d / "INDEPENDENT_REPLAY_RECEIPT.json").is_file():
            replay = load(d / "INDEPENDENT_REPLAY_RECEIPT.json")
            if replay.get("byte_identical_double_run") is not True:
                errors.append(f"REPLAY_NOT_IDENTICAL:{instance}")
            if replay.get("scientific_result_sha256") != replay.get("replayed_result_sha256"):
                errors.append(f"REPLAY_DIGEST_MISMATCH:{instance}")

    contam = Q3 / "Q3_CONTAMINATION_DISPOSITION_2026-08-22.md"
    if contam.is_file():
        body = contam.read_text(encoding="utf-8")
        for token in ("Q3-V1 / QG-7d", "Q3-V2 / QG-15c", "CONTAMINATED"):
            if token not in body:
                errors.append(f"CONTAMINATED_SLOT_VISIBILITY_LOST:{token}")

    d23 = Q3 / "Q3_D2_D3_DISPOSITION_V2.md"
    if d23.is_file() and "Q3_D2_D3_ACCEPTED_LIMITATIONS__NO_IN_PLACE_REPAIR__INSTANCE_FAILS_CLOSED_IF_TRIGGERED" not in d23.read_text(encoding="utf-8"):
        errors.append("D2_D3_DISPOSITION_NOT_BOUND")

    if errors:
        print("Q3_COMPLETION_CHECK=FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Q3_COMPLETION_CHECK=PASS")
    print("VALID_PROSPECTIVE_SERIES=V0,Q3-R1,Q3-R2")
    print("CONTAMINATED_RETIRED_SLOTS=Q3-V1/QG-7d,Q3-V2/QG-15c")
    print("REPLACEMENT_INSTANCES_SCORED=2")
    print("REPLACEMENT_RESULTS_REPLAYED=2")
    print("D2_D3=ACCEPTED_FAIL_CLOSED_LIMITATIONS")
    print("AGGREGATE_RELIABILITY_AUTHORITY=FALSE")
    print("SCIENTIFIC_AUTHORITY=NOT_GRANTED_BY_CHECKER")
    return 0


if __name__ == "__main__":
    sys.exit(main())
