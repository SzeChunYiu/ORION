#!/usr/bin/env python3
"""Fail-closed verifier for the Wave-2 publication-control disposition."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, NoReturn


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DISPOSITION_PATH = HERE / "WAVE2_DISPOSITION_V1.json"


def fail(message: str) -> NoReturn:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)}: expected a JSON object")
    return value


def git_blob(path: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", f"HEAD:{path}"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except subprocess.CalledProcessError as exc:
        fail(f"cannot resolve bound path {path}: {exc.output.strip()}")


def normalized_text(path: str) -> str:
    return " ".join((ROOT / path).read_text(encoding="utf-8").split())


def main() -> int:
    disposition = load_json(DISPOSITION_PATH)

    if disposition.get("schema") != "ORION.PublicationClosure.Wave2.Disposition.v1":
        fail("unexpected disposition schema")
    if disposition.get("base_commit") != "f5e015f878bf9c7cae8119246a9c0b5f2e18d726":
        fail("unexpected content base")
    if disposition.get("scientific_authority_delta") != "NONE":
        fail("publication control must not grant scientific authority")
    if disposition.get("submission_authority") is not False:
        fail("publication control must not authorize submission")
    if disposition.get("top_tier_authority") is not False:
        fail("publication control must not authorize top-tier status")

    bindings = disposition.get("source_bindings")
    if not isinstance(bindings, dict) or not bindings:
        fail("source bindings are missing")
    for name, binding in sorted(bindings.items()):
        if not isinstance(binding, dict):
            fail(f"{name}: binding must be an object")
        path = binding.get("path")
        expected = binding.get("git_blob_sha")
        if not isinstance(path, str) or not isinstance(expected, str):
            fail(f"{name}: malformed binding")
        actual = git_blob(path)
        if actual != expected:
            fail(f"{name}: blob drift for {path}: expected {expected}, got {actual}")

    papers = disposition.get("papers")
    if not isinstance(papers, dict):
        fail("paper dispositions are missing")

    # ORION-01: the current source really contains two different theorem objects,
    # and neither file is promoted to a production-completeness result.
    p01 = papers.get("ORION-01", {})
    if p01.get("publication_lane") != "SPLIT_TWO_THEORY_PAPERS":
        fail("ORION-01 split decision drifted")
    if p01.get("production_realization") != (
        "SUCCESSOR_ONLY_UNTIL_SCHEMA_COMPLETENESS_OR_MOVE_COMPLETENESS_IS_PROVED"
    ):
        fail("ORION-01 production-realization boundary drifted")

    a_path = bindings["orion01_theory_a_manuscript"]["path"]
    b_path = bindings["orion01_theory_b_manuscript"]["path"]
    a_text = normalized_text(a_path)
    b_text = normalized_text(b_path)
    if "Alphabet-Davenport Normal Forms for Multi-Tag Quantum Compilation" not in a_text:
        fail("ORION-01 Paper A title/theorem object missing")
    if "No sharpness is claimed for multiple Tags" not in a_text:
        fail("ORION-01 Paper A multi-Tag sharpness boundary missing")
    if "Exact Certificate Complexity versus Intrinsic Support" not in b_text:
        fail("ORION-01 Paper B title/theorem object missing")
    if "beta_rank-only(R6I)=5 > 1=kappa_R6I" not in b_text:
        fail("ORION-01 Paper B strict-separation witness missing")
    if "No lower bound is proved for every local" not in b_text:
        fail("ORION-01 Paper B proof-language limitation missing")

    # ORION-20: no empirical result may be smuggled into the formal-paper choice.
    p20 = papers.get("ORION-20", {})
    if p20.get("publication_lane") != "FORMAL_OCME_THEORY_AND_MEASUREMENT_CONTRACT":
        fail("ORION-20 formal-paper decision drifted")
    p10 = load_json(ROOT / bindings["orion20_active_authority"]["path"])
    if p10.get("active_empirical_claim") is not None:
        fail("ORION-20 unexpectedly has an active empirical claim")
    if p10.get("active_terminal") != "P10_PROSPECTIVE_PROTOCOL_ONLY":
        fail("ORION-20 terminal drifted")
    if p10.get("execution_authorized") is not False:
        fail("ORION-20 execution authority unexpectedly true")
    if p10.get("scientific_result_state") != "NO_P10_PROTECTED_RESULT":
        fail("ORION-20 result-state drifted")

    # ORION-22: verify the negative robustness boundary, independent replay
    # bindings, the conditional successor, and manuscript integration.
    p22 = papers.get("ORION-22", {})
    if p22.get("science_closeout") != "COMPLETE_ON_CURRENT_MAIN":
        fail("ORION-22 science closeout drifted")
    p12 = load_json(ROOT / bindings["orion22_active_authority"]["path"])
    robust = p12.get("robustness_boundary_leaf")
    if not isinstance(robust, dict):
        fail("ORION-22 robustness boundary missing")
    expected_robust = {
        "terminal": "P12_ROBUSTNESS_STRESS_V1_EXECUTED",
        "flat_replication": "SUPPORTED",
        "price_axis": "BROKEN",
        "distribution_shift_axis": "BROKEN",
        "retuned": False,
    }
    for key, expected in expected_robust.items():
        if robust.get(key) != expected:
            fail(f"ORION-22 robustness field {key} drifted")

    successor = p12.get("price_aware_successor_leaf")
    if not isinstance(successor, dict):
        fail("ORION-22 price-aware successor missing")
    if successor.get("terminal") != "P12_PRICE_AWARE_SUCCESSOR_SUPPORTED":
        fail("ORION-22 successor terminal drifted")
    if successor.get("battery_cells_cross_checked") != 195:
        fail("ORION-22 successor coverage drifted")
    if successor.get("forward_time_deployability") != "CANNOT_CHECK":
        fail("ORION-22 forward-time boundary drifted")

    evidence = p12.get("evidence_bindings")
    if not isinstance(evidence, dict):
        fail("ORION-22 evidence bindings missing")
    for key in (
        "robustness_result_receipt",
        "price_aware_result_receipt",
        "selection_sufficiency_receipt",
        "certificate_necessity_receipt",
    ):
        if key not in evidence:
            fail(f"ORION-22 missing evidence binding: {key}")

    abstract_path = bindings["orion22_abstract"]["path"]
    abstract = normalized_text(abstract_path)
    if "price and distribution-shift axes are both **BROKEN**" not in abstract:
        fail("ORION-22 adverse regimes are absent from the canonical abstract")
    if "zero regret in all 195 frozen cells" not in abstract:
        fail("ORION-22 conditional successor is absent from the canonical abstract")
    if "forward-time-certificate" not in abstract:
        fail("ORION-22 forward-time nonclaim is absent from the canonical abstract")

    expected_terminal = (
        "WAVE2_PUBLICATION_CONTROL_FROZEN__THREE_DECISIONS_CLOSED__"
        "ORION22_SCIENCE_ALREADY_COMPLETE__NO_NEW_SCIENTIFIC_OR_SUBMISSION_AUTHORITY"
    )
    if disposition.get("portfolio_terminal") != expected_terminal:
        fail("portfolio terminal drifted")

    print(
        json.dumps(
            {
                "schema": "ORION.PublicationClosure.Wave2.CheckResult.v1",
                "base_commit": disposition["base_commit"],
                "bindings_checked": len(bindings),
                "papers_dispositioned": len(papers),
                "scientific_authority_delta": "NONE",
                "submission_authority": False,
                "terminal": "WAVE2_PUBLICATION_CONTROL_GREEN",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(
            json.dumps(
                {
                    "schema": "ORION.PublicationClosure.Wave2.CheckResult.v1",
                    "terminal": "WAVE2_PUBLICATION_CONTROL_RED",
                    "error": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        raise SystemExit(1)
