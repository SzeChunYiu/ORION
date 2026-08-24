#!/usr/bin/env python3
"""Packet-local scientific validator for the P2 V8 donor-envelopment study."""

from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TERMINAL = (
    "P2_V8_DONOR_ENVELOPMENT_CROSSFIT_FAILS_CRE20_WSS95_AND_HARM__"
    "NO_RESIDUAL_ADMITTED__EXACT_U4_FALLBACK"
)
V7_TERMINAL = (
    "P2_KIFMS_V7_TRANSPARENT_PUBLIC_EXECUTION_FAILS_ONE_OR_MORE_"
    "LOCKED_PERFORMANCE_GATES_REQUIRES_SUCCESSOR"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def close(actual: float, expected: float, tolerance: float = 1e-15) -> None:
    require(math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance), f"{actual} != {expected}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def main() -> None:
    json_paths = sorted(ROOT.glob("*.json"))
    for path in json_paths:
        json.loads(path.read_text())
    python_paths = sorted(ROOT.glob("*.py"))
    for path in python_paths:
        ast.parse(path.read_text(), filename=str(path))

    protocol = load("PROTOCOL_V8.json")
    implementation = load("IMPLEMENTATION_FREEZE_V8.json")
    result = load("RESULT_V8.json")
    adjudication = load("SCIENTIFIC_ADJUDICATION_V8.json")
    negative = load("NEGATIVE_RESULT_LEDGER_V8.json")
    next_discriminator = load("NEXT_DISCRIMINATOR_V9.json")
    verification = load("SCIENTIFIC_VERIFICATION_V8.json")

    require(protocol["configuration_count"] == 6, "configuration search expanded")
    require(len(protocol["residual_families"]) == 3, "more than three residual families")
    require(protocol["residual_score_definition"]["strengths"] == [0.1, 0.25], "strength drift")
    require(protocol["mandatory_base"]["identity"] == "unchanged V7 R1_L1 u4", "u4 base drift")
    support = protocol["nested_leave_one_review_out"]["support_rule"]
    require(support == {
        "mean_delta_CRE20": "> 0",
        "mean_delta_WSS95": ">= 0",
        "worst_review_delta_R10": ">= -0.05",
    }, "support rule drift")

    fixed_paths = {
        "protocol_v8": ROOT / "PROTOCOL_V8.json",
        "runner_v8": ROOT / "run_donor_envelopment_v8.py",
        "pinned_active_core_v3": ROOT / "pinned_active_core_v3.py",
    }
    for role, path in fixed_paths.items():
        require(sha256(path) == implementation["fixed_sha256"][role], f"implementation hash drift {role}")
    require(implementation["custody"]["independent"] is False, "false independent custody")

    require(result["binding_receipt"]["passed"] is True, "binding did not pass")
    require(result["u4_identity_passed_all_reviews"] is True, "u4 identity failed")
    require(len(result["u4_identity_pass_by_review"]) == 14, "wrong u4 review count")
    require(all(result["u4_identity_pass_by_review"].values()), "one or more u4 orders drifted")
    require(len(result["complete_development_grid"]) == 14, "wrong grid review count")
    require(len(result["configuration_meta"]) == 6, "wrong grid configuration count")
    require(result["preserved_terminal"] == V7_TERMINAL, "V7 adverse terminal lost")
    require(result["custody"]["independent_custody"] is False, "false result custody")
    require(result["custody"]["confirmatory_claim_permitted"] is False, "false confirmation")

    aggregate = result["cross_fitted_aggregate"]
    close(aggregate["mean_delta_vs_u4"]["cre20"], -0.0020091233819910037)
    close(aggregate["mean_delta_vs_u4"]["recall_at_010"], -0.028273809523809527)
    close(aggregate["mean_delta_vs_u4"]["wss_at_95"], -0.0009911137548134536)
    close(aggregate["worst_review_delta_r10"], -0.33333333333333337)
    require(aggregate["fallback_count"] == 12, "fallback count drift")
    close(aggregate["fallback_fraction"], 12 / 14)
    require(aggregate["strictly_positive_review_counts"] == {"cre20": 0, "r10": 0}, "positive-count drift")
    require(not any(aggregate["development_safety_checks"].values()), "adverse safety classification erased")
    selected = aggregate["selected_counts"]
    require(selected["F1_WORD_PRUNED_A100"] == 1, "word residual selection drift")
    require(selected["F2_TITLE_EMPHASIS_A250"] == 1, "title residual selection drift")
    require(selected["EXACT_U4_FALLBACK"] == 12, "fallback selection drift")
    require(sum(selected.values()) == 14, "outer selection count mismatch")

    outer = result["nested_loro_by_held_out_review"]
    require(outer["Shoulderdystocia_positioning"]["selected"] == "F1_WORD_PRUNED_A100", "harm fold drift")
    close(outer["Shoulderdystocia_positioning"]["held_out_delta_vs_u4"]["recall_at_010"], -1 / 3)
    require(outer["Total_knee_replacement"]["selected"] == "F2_TITLE_EMPHASIS_A250", "title fold drift")
    close(outer["Total_knee_replacement"]["held_out_delta_vs_u4"]["recall_at_010"], -0.0625)
    for review, receipt in outer.items():
        require(len(receipt["training_reviews"]) == 13, f"wrong nested training count {review}")
        require(review not in receipt["training_reviews"], f"held-out review leaked {review}")
        if receipt["exact_u4_fallback"]:
            require(all(value == 0 for value in receipt["held_out_delta_vs_u4"].values()), f"fallback not exact {review}")
            require(
                receipt["held_out_order_sha256"]
                == result["complete_development_grid"][review]["EXACT_U4"]["order_sha256"],
                f"fallback order drift {review}",
            )

    require(adjudication["adjudicated_terminal"] == TERMINAL, "adjudicated terminal drift")
    require(adjudication["result_sha256"] == sha256(ROOT / "RESULT_V8.json"), "result receipt drift")
    require(not any(
        item["full_fourteen_support_passed"]
        for item in adjudication["full_grid_configuration_summary"].values()
    ), "unsupported residual promoted")
    title = adjudication["full_grid_configuration_summary"]["F2_TITLE_EMPHASIS_A250"]
    close(title["mean_delta_cre20"], 0.0106931250595191)
    close(title["mean_delta_wss95"], 0.002042792819172991)
    close(title["worst_review_delta_r10"], -0.0625)

    require(negative["terminal"] == TERMINAL, "negative ledger terminal drift")
    require(len(negative["entries"]) == 6, "negative ledger entry count")
    require(next_discriminator["parent_terminal"] == TERMINAL, "next discriminator parent drift")
    require(next_discriminator["source"]["status"] == "SOURCE_IDENTITY_AND_OUTCOME_CUSTODY_NOT_YET_BOUND", "source falsely bound")
    choice = next_discriminator["frozen_development_choice"]
    require(choice["controller"] == "unchanged u4 plus F2_TITLE_EMPHASIS at alpha=0.25", "V9 controller drift")
    gates = next_discriminator["unchanged_gates"]
    require("0.010858985820770889" in gates["mean_delta_CRE20"], "CRE20 threshold relaxed")
    require("0.010858985820770889" in gates["mean_delta_R10"], "R10 threshold relaxed")
    require(gates["worst_review_delta_R10"] == ">= -0.05", "harm threshold relaxed")

    require(verification["terminal"] == TERMINAL, "verification terminal drift")
    require(verification["u4_exact_identity"] == "14/14", "verification u4 drift")
    require(verification["configuration_review_executions"] == 84, "execution count drift")

    result_text = (ROOT / "RESULT_V8.json").read_text().casefold()
    require('"title"' not in result_text and '"abstract"' not in result_text, "source text field emitted")

    manifest_path = ROOT / "SHA256SUMS"
    manifest: dict[str, str] = {}
    for line in manifest_path.read_text().splitlines():
        digest, rel = line.split("  ", 1)
        require(rel not in manifest, f"duplicate manifest path {rel}")
        manifest[rel] = digest
    expected = {
        path.name
        for path in ROOT.iterdir()
        if path.is_file() and path.name != "SHA256SUMS" and path.name != "__pycache__"
    }
    require(set(manifest) == expected, "manifest path set mismatch")
    for rel, digest in manifest.items():
        require(sha256(ROOT / rel) == digest, f"manifest mismatch {rel}")

    print(
        f"PASS P2 V8 packet: {len(json_paths)} JSON, {len(python_paths)} Python, "
        f"14 reviews, 84 residual executions; terminal={TERMINAL}"
    )


if __name__ == "__main__":
    main()
