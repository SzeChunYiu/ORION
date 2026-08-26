#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRS = [
    "orion-11-recursive-epistemic-reconstruction",
    "orion-12-open-world-scientific-discovery",
    "orion-13-global-knowledge-portrait",
    "orion-14-verified-scientific-discovery",
    "orion-15-self-orion",
    "orion-16-formal-epistemic-structures-and-mechanics",
    "orion-17-epistemic-navigation-open-worlds",
    "orion-18-epistemic-authority-autonomous-science",
    "orion-19-structured-epistemic-learning",
    "orion-20-structured-problem-solving",
    "orion-21-state-as-computation",
    "orion-22-adaptive-state-reasoning",
    "orion-23-responsibility-carrying-state",
    "orion-24-orion-rse",
    "orion-25-orion-research-harness",
]
ACK = "P1_P15_REWRITE_LANE_ACKNOWLEDGES_25_OF_25_COMPUTATION_LEDGER"


def req(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("P1_P15_DYNAMIC_REWRITE_V1 FAIL: " + message)


def main() -> None:
    research = ROOT / "research" / "orion-epistemic-state-v1"
    papers_root = ROOT / "papers"
    req(research.is_dir(), "research package")

    theorem_ledger = json.loads((research / "THEOREM_LEDGER_V1.json").read_text())
    backlog = json.loads((research / "COMPUTE_EXECUTION_BACKLOG_V1.json").read_text())
    writing_ledger_path = papers_root / "P1_P15_RESULT_BOUND_CLAIM_LEDGER_V1.json"
    writing_plan_path = papers_root / "P1_P15_25_OF_25_RESULT_INTEGRATION_WRITING_PLAN_V1.md"
    req(writing_ledger_path.is_file(), "result-bound writing ledger")
    req(writing_plan_path.is_file(), "result integration writing plan")
    writing_ledger = json.loads(writing_ledger_path.read_text())

    req(
        theorem_ledger["counts"] == {"common": 16, "paper_specific": 75, "total": 91},
        "theorem counts",
    )
    req(
        len(backlog["common_jobs"]) == 10 and len(backlog["paper_jobs"]) == 15,
        "job counts",
    )
    req(len(writing_ledger["common_results"]) == 10, "common result count")
    req(len(writing_ledger["papers"]) == 15, "paper result count")
    for row in writing_ledger["common_results"] + writing_ledger["papers"]:
        req(
            re.fullmatch(r"[0-9a-f]{40}", row.get("sha", "")) is not None,
            f"{row.get('job_id', 'unknown job')} result SHA format",
        )
    req(writing_ledger["acknowledgement_token"] == ACK, "acknowledgement token")
    req(ACK in writing_plan_path.read_text(), "writing plan acknowledgement")
    req(
        writing_ledger["computation_session_paper_authority_delta"] == "NONE",
        "computation authority boundary",
    )

    result_by_paper = {row["paper"]: row for row in writing_ledger["papers"]}
    req(set(result_by_paper) == {f"P{i}" for i in range(1, 16)}, "paper result identities")

    comparison_markers = ("compare", "comparison", "against", "versus")

    for index, directory in enumerate(DIRS, 1):
        paper_id = f"P{index}"
        row = result_by_paper[paper_id]
        manuscript = papers_root / directory / "TOP_TIER_DYNAMIC_EPISTEMIC_MANUSCRIPT_V1.md"
        req(manuscript.is_file(), f"{paper_id} manuscript")
        text = manuscript.read_text()
        lower = text.lower()
        req(f"ORION-{index + 10}-DES-01" in text, f"{paper_id} job binding")
        req("paper_authority_delta = NONE" in text, f"{paper_id} authority boundary")
        req("absorbs" in lower, f"{paper_id} nearest-work absorption gate")
        req(
            any(marker in lower for marker in comparison_markers),
            f"{paper_id} comparator gate",
        )
        req("## Theory" in text, f"{paper_id} theorem section")
        req("## Decisive computation" in text, f"{paper_id} execution section")
        req(
            "## Authoritative computation disposition" in text,
            f"{paper_id} authoritative disposition section",
        )
        req(row["sha"] in text, f"{paper_id} result SHA binding")
        req(row["terminal"] in text, f"{paper_id} exact terminal binding")
        req("Allowed manuscript claims" in text, f"{paper_id} allowed-claim boundary")
        req("Not established" in text, f"{paper_id} forbidden-claim boundary")
        req("RESULT_LEDGER_BOUND" in text, f"{paper_id} result-bound status")

    req(
        (ROOT / "src" / "orion" / "epistemic_state_v1" / "model.py").is_file(),
        "model",
    )
    print(
        "P1_P15_DYNAMIC_REWRITE_V1 PASS "
        "papers=15 theorems=91 jobs=25 result_packets=25 claim_boundaries=15"
    )


if __name__ == "__main__":
    main()
