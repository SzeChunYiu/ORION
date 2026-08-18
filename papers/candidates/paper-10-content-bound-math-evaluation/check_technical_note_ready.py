#!/usr/bin/env python3
"""Fail-closed structural and numerical gate for the merged P10 note."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(relative: str):
    return json.loads((ROOT / relative).read_text())


def main() -> None:
    required = [
        "README.md",
        "TECHNICAL_NOTE.md",
        "CLAIM_LEDGER.md",
        "JOURNAL_READINESS.md",
        "SATURATION_LEDGER_2026-08-18.md",
        "MERGE_DISPOSITION.md",
        "FOLLOW_UPS.md",
        "references.bib",
        "benchmark/MATHLIB_CORPUS_V2_MANIFEST.json",
        "benchmark/MATHLIB_TRANSFER_PROTOCOL_V2_1.json",
        "benchmark/NATIVE_VERIFICATION_PROTOCOL_V1.json",
        "benchmark/NATIVE_VERIFICATION_SAMPLE_V1.json",
        "results/PARSER_CONTAMINATION_AUDIT_V2.json",
        "results/MATHLIB_TRANSFER_V2_1.json",
        "results/MATHLIB_NATIVE_RECEIPTS_V1.json",
    ]
    missing = [relative for relative in required if not (ROOT / relative).is_file()]
    if missing:
        raise AssertionError(f"missing P10 closure files: {missing}")

    corpus = load("benchmark/MATHLIB_CORPUS_V2_MANIFEST.json")
    assert corpus["selected_files"] == 457
    assert corpus["selected_bytes"] == 5_655_364
    assert len(corpus["top_module_counts"]) == 31

    audit = load("results/PARSER_CONTAMINATION_AUDIT_V2.json")
    assert audit["contaminated_trajectories"] == 1289
    assert audit["trajectories"] == 4861

    result = load("results/MATHLIB_TRANSFER_V2_1.json")
    top = result["leave_top_module_out"]
    assert top["markov_minus_unigram"] >= 0.05
    assert top["bootstrap_95_percent_interval"]["interval"][0] > 0
    assert result["standalone_gate"]["numerical_conditions_pass"] is True
    assert result["standalone_gate"]["passes"] is False

    receipts = load("results/MATHLIB_NATIVE_RECEIPTS_V1.json")
    assert receipts["passes"] is True
    assert receipts["mathlib_commit"] == "e72c1e277f31441626621f7d0c7207862fc25569"
    assert receipts["lean_toolchain"] == "leanprover/lean4:v4.34.0-rc1"
    assert receipts["version_preflight"]["stdout_utf8"].startswith(
        "Lean (version 4.34.0-rc1,"
    )
    assert len(receipts["receipts"]) == 8
    assert len({item["top_module"] for item in receipts["receipts"]}) == 8
    assert all(item["verdict"] == "SUCCESS" for item in receipts["receipts"])
    assert all(item["exit_status"] == 0 for item in receipts["receipts"])
    assert receipts["negative_control"]["verdict"] == "FAIL"
    assert receipts["negative_control"]["exit_status"] != 0

    ledger = (ROOT / "SATURATION_LEDGER_2026-08-18.md").read_text()
    assert "CITED_ONLY" in ledger and "`CITED_ONLY` is forbidden" in ledger
    assert ledger.count("`ABSORBED`") >= 7
    assert ledger.count("NO_MATERIAL_CHANGE") >= 2
    assert "TECHNICAL_NOTE_MERGED_INTO_P4_P8_PROGRAMME" in ledger

    claims = (ROOT / "CLAIM_LEDGER.md").read_text()
    assert "PENDING_NATIVE_RECEIPTS" not in claims
    assert "Forbidden promotions" in claims
    note = (ROOT / "TECHNICAL_NOTE.md").read_text()
    assert "No theorem correctness" in note
    assert "TECHNICAL_NOTE_MERGED_INTO_P4_P8_PROGRAMME" in note
    print("P10 merged technical-note readiness: PASS")


if __name__ == "__main__":
    main()
