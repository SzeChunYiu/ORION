#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRS = [
    "paper-01-recursive-epistemic-reconstruction",
    "paper-02-open-world-scientific-discovery",
    "paper-03-global-knowledge-portrait",
    "paper-04-verified-scientific-discovery",
    "paper-05-self-orion",
    "paper-06-formal-epistemic-structures-and-mechanics",
    "paper-07-epistemic-navigation-open-worlds",
    "paper-08-epistemic-authority-autonomous-science",
    "paper-09-structured-epistemic-learning",
    "paper-10-structured-problem-solving",
    "paper-11-state-as-computation",
    "paper-12-adaptive-state-reasoning",
    "paper-13-responsibility-carrying-state",
    "paper-14-orion-rse",
    "paper-15-orion-research-harness",
]


def req(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("P1_P15_DYNAMIC_REWRITE_V1 FAIL: " + message)


def main() -> None:
    research = ROOT / "research" / "orion-epistemic-state-v1"
    req(research.is_dir(), "research package")
    ledger = json.loads((research / "THEOREM_LEDGER_V1.json").read_text())
    backlog = json.loads((research / "COMPUTE_EXECUTION_BACKLOG_V1.json").read_text())
    req(
        ledger["counts"] == {"common": 16, "paper_specific": 75, "total": 91},
        "theorem counts",
    )
    req(
        len(backlog["common_jobs"]) == 10 and len(backlog["paper_jobs"]) == 15,
        "job counts",
    )
    for index, directory in enumerate(DIRS, 1):
        manuscript = (
            ROOT
            / "papers"
            / directory
            / "TOP_TIER_DYNAMIC_EPISTEMIC_MANUSCRIPT_V1.md"
        )
        req(manuscript.is_file(), f"P{index} manuscript")
        text = manuscript.read_text()
        req(f"P{index}-DES-01" in text, f"P{index} job binding")
        req(
            "paper_authority_delta = NONE" in text,
            f"P{index} authority boundary",
        )
        req("donor" in text.lower(), f"P{index} donor absorption/comparison gate")
        req("## Theory" in text, f"P{index} theorem section")
        req("## Decisive computation" in text, f"P{index} execution section")
    req(
        (ROOT / "src" / "orion" / "epistemic_state_v1" / "model.py").is_file(),
        "model",
    )
    print("P1_P15_DYNAMIC_REWRITE_V1 PASS papers=15 theorems=91 jobs=25")


if __name__ == "__main__":
    main()
