from __future__ import annotations

import json
import re
from pathlib import Path

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p2_structure import (
    CandidateMethodSignature,
    StructuralNeed,
    assess_structural_candidate,
    structural_match_score,
)

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "orion-12-open-world-scientific-discovery"
PANEL = PAPER / "structural_extension" / "HISTORICAL_PANEL_V1.json"
SUMMARY = PAPER / "structural_extension" / "HISTORICAL_PILOT_SUMMARY_V1.json"
_TOKEN = re.compile(r"[a-z0-9]+")


def lexical_score(left: str, right: str) -> float:
    a = set(_TOKEN.findall(left.lower()))
    b = set(_TOKEN.findall(right.lower()))
    return len(a & b) / len(a | b) if a and b else 0.0


def test_historical_panel_is_pretransfer_and_source_bound():
    panel = json.loads(PANEL.read_text(encoding="utf-8"))
    assert panel["authority"] == "BOUNDED_CURATED_HISTORICAL_PILOT"
    for case in panel["cases"]:
        cutoff_year = int(case["cutoff"][:4])
        assert int(case["donor_primary_source"]["year"]) <= cutoff_year
        assert cutoff_year < int(case["transfer_validation_source"]["year"])
        assert case["donor_primary_source"]["url"].startswith("https://")
        assert case["transfer_validation_source"]["url"].startswith("https://")


def test_frozen_historical_pilot_reproduces_narrowed_summary():
    panel = json.loads(PANEL.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    lexical_hits = 0
    structural_hits = 0
    hybrid_hits = 0
    false_analogies = 0

    for case in panel["cases"]:
        need = StructuralNeed.from_mapping(
            need_id=f"historical:{case['case_id']}",
            source_object_id=f"historical-target:{case['case_id']}",
            source_object_digest=content_digest(
                {
                    "case_id": case["case_id"],
                    "target_domain": case["target_domain"],
                    "need": case["need"],
                }
            ),
            coordinates=case["need"],
        )
        rows = []
        for raw in case["candidates"]:
            candidate = CandidateMethodSignature(
                candidate_id=raw["candidate_id"],
                domain=raw["domain"],
                assumptions=tuple(sorted(raw.get("assumptions", []))),
                invariants=tuple(sorted(raw.get("invariants", []))),
                effects=tuple(sorted(raw.get("effects", []))),
                reconstruction=raw.get("reconstruction"),
                provenance_digest=content_digest(
                    {
                        "case_id": case["case_id"],
                        "candidate_id": raw["candidate_id"],
                        "surface_text": raw["surface_text"],
                    }
                ),
            )
            receipt = assess_structural_candidate(need, candidate)
            lscore = lexical_score(case["target_text"], raw["surface_text"])
            sscore = structural_match_score(need, candidate)
            rows.append(
                (
                    raw["candidate_id"],
                    lscore,
                    sscore,
                    sscore + 0.05 * lscore,
                    receipt.status.value,
                )
            )
        lexical_top = max(rows, key=lambda row: (row[1], row[0]))
        structural_top = max(rows, key=lambda row: (row[2], row[0]))
        hybrid_top = max(rows, key=lambda row: (row[3], row[0]))
        gold = case["gold_candidate_id"]
        lexical_hits += lexical_top[0] == gold
        structural_hits += structural_top[0] == gold
        hybrid_hits += hybrid_top[0] == gold
        false_analogies += structural_top[4] == "OBSTRUCTION"

    n = len(panel["cases"])
    observed = {
        "lexical_top1_recall": lexical_hits / n,
        "structural_top1_recall": structural_hits / n,
        "hybrid_top1_recall": hybrid_hits / n,
        "structural_false_analogy_rate": false_analogies / n,
    }
    assert observed == summary["metrics"]
    assert summary["terminal"] == "P2_STRUCTURAL_DISCOVERY_NARROWED"
    assert summary["unexecuted_strong_baselines"]
