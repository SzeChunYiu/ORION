#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p2_structure import (
    CandidateMethodSignature,
    StructuralNeed,
    assess_structural_candidate,
    structural_match_score,
)

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "structural_extension" / "HISTORICAL_PANEL_V1.json"
SUMMARY = ROOT / "structural_extension" / "HISTORICAL_PILOT_SUMMARY_V1.json"
RESULT = ROOT / "structural_extension" / "HISTORICAL_PILOT_RESULT_V1.json"
_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower()))


def lexical_score(target: str, candidate: str) -> float:
    left = _tokens(target)
    right = _tokens(candidate)
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _need(case: dict[str, Any]) -> StructuralNeed:
    coordinates = case["need"]
    return StructuralNeed.from_mapping(
        need_id=f"historical:{case['case_id']}",
        source_object_id=f"historical-target:{case['case_id']}",
        source_object_digest=content_digest(
            {
                "case_id": case["case_id"],
                "target_domain": case["target_domain"],
                "need": coordinates,
            }
        ),
        coordinates=coordinates,
    )


def _candidate(case_id: str, raw: dict[str, Any]) -> CandidateMethodSignature:
    return CandidateMethodSignature(
        candidate_id=raw["candidate_id"],
        domain=raw["domain"],
        assumptions=tuple(sorted(raw.get("assumptions", []))),
        invariants=tuple(sorted(raw.get("invariants", []))),
        effects=tuple(sorted(raw.get("effects", []))),
        reconstruction=raw.get("reconstruction"),
        provenance_digest=content_digest(
            {
                "case_id": case_id,
                "candidate_id": raw["candidate_id"],
                "domain": raw["domain"],
                "surface_text": raw["surface_text"],
            }
        ),
    )


def _rank(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: (-row[key], row["candidate_id"]))


def run(panel: dict[str, Any]) -> dict[str, Any]:
    cases_out: list[dict[str, Any]] = []
    lexical_hits = 0
    structural_hits = 0
    hybrid_hits = 0
    structural_false_analogy = 0

    for case in panel["cases"]:
        donor_year = int(case["donor_primary_source"]["year"])
        transfer_year = int(case["transfer_validation_source"]["year"])
        cutoff_year = int(str(case["cutoff"])[:4])
        if not donor_year <= cutoff_year < transfer_year:
            raise ValueError(f"historical cutoff invalid for {case['case_id']}")
        if not case["donor_primary_source"].get("url") or not case["transfer_validation_source"].get("url"):
            raise ValueError(f"primary-source lineage missing for {case['case_id']}")

        need = _need(case)
        rows: list[dict[str, Any]] = []
        for raw in case["candidates"]:
            candidate = _candidate(case["case_id"], raw)
            receipt = assess_structural_candidate(need, candidate)
            receipt.verify()
            lscore = lexical_score(case["target_text"], raw["surface_text"])
            sscore = structural_match_score(need, candidate)
            rows.append(
                {
                    "candidate_id": raw["candidate_id"],
                    "domain": raw["domain"],
                    "lexical_score": round(lscore, 6),
                    "structural_score": round(sscore, 6),
                    "hybrid_score": round(sscore + 0.05 * lscore, 6),
                    "structural_status": receipt.status.value,
                    "reason_codes": list(receipt.reason_codes),
                    "candidate_receipt_digest": receipt.receipt_digest,
                }
            )

        lexical = _rank(rows, "lexical_score")
        structural = _rank(rows, "structural_score")
        hybrid = _rank(rows, "hybrid_score")
        gold = case["gold_candidate_id"]
        lexical_hits += lexical[0]["candidate_id"] == gold
        structural_hits += structural[0]["candidate_id"] == gold
        hybrid_hits += hybrid[0]["candidate_id"] == gold
        if structural[0]["structural_status"] == "OBSTRUCTION":
            structural_false_analogy += 1

        cases_out.append(
            {
                "case_id": case["case_id"],
                "family": case["family"],
                "gold_candidate_id": gold,
                "lexical_top1": lexical[0]["candidate_id"],
                "structural_top1": structural[0]["candidate_id"],
                "hybrid_top1": hybrid[0]["candidate_id"],
                "lexical_gold_rank": 1 + next(i for i, row in enumerate(lexical) if row["candidate_id"] == gold),
                "structural_gold_rank": 1 + next(i for i, row in enumerate(structural) if row["candidate_id"] == gold),
                "candidate_rows": sorted(rows, key=lambda row: row["candidate_id"]),
            }
        )

    n = len(cases_out)
    result: dict[str, Any] = {
        "result_version": "P2_STRUCTURAL_DISCOVERY_HISTORICAL_PILOT_V1",
        "protocol_id": panel["protocol_id"],
        "panel_digest": content_digest(panel),
        "n_cases": n,
        "metrics": {
            "lexical_top1_recall": lexical_hits / n,
            "structural_top1_recall": structural_hits / n,
            "hybrid_top1_recall": hybrid_hits / n,
            "structural_false_analogy_rate": structural_false_analogy / n,
        },
        "cases": cases_out,
        "interpretation": {
            "terminal": "P2_STRUCTURAL_DISCOVERY_NARROWED",
            "reason": "curated historical candidate-universe pilot; no open-web/embedding/LLM superiority claim",
            "transfer_authority": "NONE",
            "novelty_authority": "NONE",
        },
    }
    result["result_digest"] = content_digest(result)
    return result


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="optionally archive the detailed trace")
    parser.add_argument("--check", action="store_true", help="check the frozen summary")
    args = parser.parse_args()
    result = run(_load(PANEL))
    if args.write:
        RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        summary = _load(SUMMARY)
        for key, value in (
            ("protocol_id", result["protocol_id"]),
            ("n_cases", result["n_cases"]),
            ("metrics", result["metrics"]),
        ):
            if summary[key] != value:
                raise SystemExit(f"historical structural pilot summary drift: {key}")
        if summary["terminal"] != result["interpretation"]["terminal"]:
            raise SystemExit("historical structural pilot terminal drift")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
