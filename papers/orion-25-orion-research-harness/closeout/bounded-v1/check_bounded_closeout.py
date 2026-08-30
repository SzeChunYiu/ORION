#!/usr/bin/env python3
"""Fail-closed checker for the ORION-25 bounded source closeout."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1]
EXEC = PAPER / "experiments" / "execution-integrity-v1"
LAW = PAPER / "experiments" / "trust-domain-law-v1"


def load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalized_text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def close(actual: float, expected: float, *, tol: float = 1e-12) -> None:
    if not math.isclose(actual, expected, rel_tol=tol, abs_tol=tol):
        raise AssertionError(f"{actual!r} != {expected!r}")


def main() -> int:
    result = load(HERE / "RESULT.json")
    expected = load(HERE / "EXPECTED_TERMINALS.json")
    binding = load(HERE / "SOURCE_BINDING.json")

    fault = load(EXEC / "FAULT_INJECTION_RESULT_V1.json")
    benign = load(EXEC / "FALSE_REJECTION_RESULT_V1.json")
    h1 = load(EXEC / "H1_CHAIN_LENGTH_RESULT_V1.json")
    h2 = load(EXEC / "H2_TRUST_DOMAIN_RESULT_V1.json")
    host = load(EXEC / "HOST_PROCESS_FAULT_RESULT_V1.json")
    overhead = load(EXEC / "OVERHEAD_RESULT_V1.json")
    law = load(LAW / "RESULT_V1.json")

    terminals = expected["required_source_terminals"]
    assert fault["terminal"] == terminals["fault_injection"]
    assert benign["terminal"] == terminals["false_rejection"]
    assert h1["terminal"] == terminals["chain_length"]
    assert h2["terminal"] == terminals["trust_domains"]
    assert host["terminal"] == terminals["host_process"]
    assert overhead["terminal"] == terminals["overhead"]
    assert law["terminal"] == terminals["trust_domain_law"]

    assert fault["faults_attempted"] == fault["faults_applied"] == 6
    assert sum(item["detected"] for item in fault["results"]) == 6
    assert fault["false_promotions"] == 0
    assert result["artifact_corruption"]["faults_detected"] == 6
    assert result["artifact_corruption"]["false_promotions"] == 0

    assert benign["variants_applied"] == 6
    assert sum(not item["falsely_rejected"] for item in benign["results"]) == 6
    assert sum(item["bytes_differ_from_original"] for item in benign["results"]) == 4
    assert benign["false_rejections"] == 0
    assert result["benign_reencoding"]["byte_distinct_variants"] == 4

    assert h1["k_values_tested"] == [1, 2, 3]
    assert h1["detection_rates"] == {"1": 1.0, "2": 1.0, "3": 1.0}
    assert all(h1["per_k"][str(k)]["clean_chains_verified"] == 4 for k in (1, 2, 3))

    assert h2["k_fixed"] == 3
    assert h2["false_promotion_rate_by_d"] == {"1": 1.0, "2": 0.0, "3": 0.0}
    assert {d: h2["per_d"][d]["false_promotions"] for d in ("1", "2", "3")} == {
        "1": 4,
        "2": 0,
        "3": 0,
    }

    assert host["checker_accepted_stale_artifact_count"] == 2
    assert sum(bool(item.get("failed_loudly")) for item in host["results"]) == 2
    assert result["process_liveness"]["stale_valid_artifacts_accepted"] == 2

    close(overhead["no_attestation_seconds"]["median"] * 1000, result["composition_overhead"]["median_no_attestation_ms"])
    close(overhead["attested_seconds"]["median"] * 1000, result["composition_overhead"]["median_attested_ms"])
    close(overhead["overhead_seconds_median"] * 1000, result["composition_overhead"]["median_added_ms"])
    close(overhead["overhead_multiple"], result["composition_overhead"]["relative_multiple"])
    close(overhead["per_link_overhead_microseconds"], result["composition_overhead"]["per_link_overhead_microseconds"])
    assert overhead["bytes"]["no_attestation"] == 6926
    assert overhead["bytes"]["attested"] == 9650

    assert law["cells_total"] == law["cells_matching_theorem_T"] == 1000
    assert law["necessity_failures"] == law["sufficiency_failures"] == 0
    assert "CRYPTOGRAPHIC only" in law["custody_limit"]

    adverse = [
        json.loads(line)
        for line in (HERE / "ADVERSE_AND_CANNOT_CHECK.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    adverse_ids = {item["id"] for item in adverse}
    assert {
        "ORION25-ADV-FULL-KEY-COMPROMISE",
        "ORION25-ADV-STALE-ARTIFACT",
        "ORION25-CC-ORGANIZATIONAL-INDEPENDENCE",
        "ORION25-CC-MULTI-DOMAIN-COMPROMISE",
        "ORION25-CC-PRODUCTION-COMPARATORS",
        "ORION25-CC-FINAL-PDF",
    } <= adverse_ids

    chapter8 = normalized_text(PAPER / "manuscript/chapters/08-results-status.tex")
    chapter9 = normalized_text(PAPER / "manuscript/chapters/09-limitations-and-authority.tex")
    for fragment in (
        "0/6 false promotions",
        "0/6 false rejections",
        "4/4 cases",
        "0/4",
        "1.340 ms",
        "13.8",
        "stale-artifact cases were accepted",
    ):
        assert fragment in chapter8, fragment
    assert "cryptographic-independence result, not a theorem about organizational independence" in chapter8
    assert "Multiple-domain compromise" in chapter9
    assert "successor work rather than a prerequisite for the bounded framework paper" in chapter9

    assert result["paper_disposition"] == "CANNOT_CHECK"
    assert result["source_closeout_terminal"] == "BOUNDED_PAPER_SOURCE_COMPLETE__FINAL_RENDER_AND_FILING_PENDING"
    assert not any(result["filing_gate"].values())
    assert binding["scientific_authority_delta"] == result["scientific_authority_delta"] == "NONE"

    print(expected["checker_terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
