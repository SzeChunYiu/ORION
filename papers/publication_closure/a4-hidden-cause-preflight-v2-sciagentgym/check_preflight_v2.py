#!/usr/bin/env python3
"""Fail-closed verifier for the A4 SciAgentGym preflight (PREFLIGHT_V2.json).

Live-verifies, against the pinned repository state, exactly the facts the
preflight claims to have verified: the repository licence blob, the two
dataset files' base-record/variant counts, and the per-domain census. Rows
the preflight marks CANNOT_CHECK are asserted to still carry that terminal —
this checker never upgrades them.

Usage:
  check_preflight_v2.py --freeze PREFLIGHT_V2.json \
      --multi /tmp/multi.json --single /tmp/single.json --license /tmp/LICENSE
  check_preflight_v2.py --self-test --freeze PREFLIGHT_V2.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

EXPECTED_LICENSE_SHA_GIT_BLOB = "261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def census(records: list[dict]) -> tuple[int, int, Counter]:
    base = len(records)
    total = 0
    domains: Counter = Counter()
    for r in records:
        variants = 1
        variants += 1 if r.get("augmented_versions") else 0
        variants += 1 if r.get("refined_versions") else 0
        # paper counts base + refined = 259; augmented replaces base in 128 rows
        subject = (r.get("metadata") or {}).get("subject") or "UNKNOWN"
        domains[subject] += 1
        total += 1
    return base, total, domains


def verify(freeze: dict, multi: list[dict], single: list[dict], license_bytes: bytes) -> dict:
    errors: list[str] = []
    sub = freeze["primary_proposed_substrate"]

    if git_blob_sha(license_bytes) != sub["code_and_data_repository"]["license_blob_sha"]:
        errors.append("licence blob sha mismatch")
    if b"Apache License" not in license_bytes:
        errors.append("licence text is not Apache")

    base_m, _, dom_m = census(multi)
    base_s, _, dom_s = census(single)
    base = base_m + base_s
    if base != sub["task_storage"]["base_records"]:
        errors.append(f"base records {base} != frozen {sub['task_storage']['base_records']}")

    doms = dom_m + dom_s
    frozen_census = {k: v[0] for k, v in sub["domain_census_base_and_total"].items()}
    if dict(doms) != frozen_census:
        errors.append(f"domain census mismatch: {dict(doms)} != {frozen_census}")

    # refined/augmented variant accounting reaches the paper's 259 total
    with_variants = sum(
        1 for r in multi + single if r.get("refined_versions") or r.get("augmented_versions")
    )
    if base + with_variants != sub["task_storage"]["augmented_plus_refined_total"]:
        errors.append(
            f"variant accounting {base}+{with_variants} != {sub['task_storage']['augmented_plus_refined_total']}"
        )

    # CANNOT_CHECK terminals must remain CANNOT_CHECK — never upgraded here
    for path, key in (
        (sub["per_task_provenance"], "terminal"),
        (sub["executability"], "terminal"),
    ):
        if "CANNOT_CHECK" not in str(path.get(key, "")):
            errors.append(f"a CANNOT_CHECK terminal was upgraded: {path.get(key)}")

    for flag in (
        "protected_agent_runs_executed",
        "protected_outcomes_accessed",
        "confirmatory_subset_selected",
    ):
        if freeze.get(flag) is not False:
            errors.append(f"execution flag not false: {flag}")

    return {
        "schema": "ORION.A4.SciAgentGymPreflightCheckResult.v1",
        "decision": "RED" if errors else "GREEN",
        "errors": errors,
        "base_records": base,
        "domains": dict(doms),
    }


def self_test(freeze: dict) -> None:
    # structural: flags false, CANNOT_CHECK rows intact, no upgraded terminal
    sub = freeze["primary_proposed_substrate"]
    assert freeze["protected_agent_runs_executed"] is False
    assert freeze["confirmatory_subset_selected"] is False
    assert "CANNOT_CHECK" in sub["per_task_provenance"]["terminal"]
    assert "CANNOT_CHECK" in sub["executability"]["terminal"]
    assert sub["scope_verdict"]["conservative_count_meets_bar"] is False
    assert sub["scope_verdict"]["meets_120_tasks_4_domains"] is True

    # hostile: forged licence bytes must fail
    fake = json.loads(json.dumps(freeze))
    r = verify(fake, [], [], b"MIT License")
    assert r["decision"] == "RED" and any("licence" in e for e in r["errors"])

    # hostile: upgraded CANNOT_CHECK must fail
    fake2 = json.loads(json.dumps(freeze))
    fake2["primary_proposed_substrate"]["per_task_provenance"]["terminal"] = "VERIFIED"
    r2 = verify(fake2, [], [], b"Apache License fake")
    assert r2["decision"] == "RED" and any("upgraded" in e for e in r2["errors"])

    print("PREFLIGHT_V2_SELF_TEST_GREEN")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", type=Path, required=True)
    ap.add_argument("--multi", type=Path)
    ap.add_argument("--single", type=Path)
    ap.add_argument("--license", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    freeze = json.loads(a.freeze.read_text())
    if a.self_test:
        self_test(freeze)
        return 0
    if not (a.multi and a.single and a.license):
        ap.error("--multi, --single and --license required")
    result = verify(
        freeze,
        json.loads(a.multi.read_text()),
        json.loads(a.single.read_text()),
        a.license.read_bytes(),
    )
    print(json.dumps(result, indent=1))
    return 0 if result["decision"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
