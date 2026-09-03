#!/usr/bin/env python3
"""Fail-closed verifier for A4_MODEL_IDENTITY_FREEZE_V1.json.

Live-verifies, against the committed lane files, exactly the facts the freeze
asserts:

  1. every execution flag is false (freeze-before-outcomes);
  2. >=3 model/agent family identities are frozen, spanning >=3 distinct
     classes (GPT-class, Claude/Gemini-class, open-weight);
  3. every identity carries the full identity contract (family id, runtime
     version, model id, host, invocation contract, decoding) and references
     a committed echo receipt file;
  4. each committed receipt file exists and contains its frozen expected
     token verbatim — a receipt that cannot be produced from the repo is a
     fabricated liveness claim and goes RED;
  5. every lane that is not LANE_VERIFIED_ON_LUNARC_SBATCH is explicitly
     listed in open_preconditions (no silent deployment gap);
  6. the banned shipped proxy lane is recorded as replaced.

This checker never executes a model call and never upgrades an honest
blocked-lane record to verified.

Usage:
  check_a4_model_identity_freeze_v1.py --self-test \
      --freeze A4_MODEL_IDENTITY_FREEZE_V1.json
  check_a4_model_identity_freeze_v1.py \
      --freeze A4_MODEL_IDENTITY_FREEZE_V1.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_FLAGS_FALSE = [
    "protected_agent_runs_executed",
    "protected_outcomes_accessed",
    "development_partition_runs_executed",
    "intervention_study_executed",
    "results_exist",
    "lanes_fully_deployed",
]

REQUIRED_CLASSES = {
    "GPT_CLASS",
    "CLAUDE_OR_GEMINI_CLASS",
    "OPEN_WEIGHT_CLASS",
}

REQUIRED_IDENTITY_FIELDS = [
    "model_family_id",
    "runtime_version",
    "model_id",
    "identity_echo_host",
    "invocation_contract",
    "decoding",
    "receipt_file",
    "receipt_expected_token",
]


def verify(freeze: dict, freeze_dir: Path) -> dict:
    errors: list[str] = []

    # 1. flags
    for flag in REQUIRED_FLAGS_FALSE:
        if freeze["flags"].get(flag) is not False:
            errors.append(f"execution flag not false: {flag}")

    # 2. >=3 identities over >=3 distinct classes
    ids = freeze.get("model_identities", [])
    if len(ids) < 3:
        errors.append(f"fewer than 3 model identities frozen: {len(ids)}")
    classes = {i.get("class") for i in ids}
    missing_classes = REQUIRED_CLASSES - classes
    if missing_classes:
        errors.append(f"required family class missing: {sorted(missing_classes)}")

    # 3+4. identity contract + committed receipt bytes
    for ident in ids:
        fid = ident.get("model_family_id", "<unnamed>")
        for field in REQUIRED_IDENTITY_FIELDS:
            if not ident.get(field):
                errors.append(f"identity {fid}: missing field {field}")
        rf = freeze_dir / ident["receipt_file"] if ident.get("receipt_file") else None
        if rf is not None:
            if not rf.exists():
                errors.append(f"identity {fid}: receipt file missing: {ident['receipt_file']}")
            elif ident.get("receipt_expected_token", "") not in rf.read_text():
                errors.append(
                    f"identity {fid}: expected token not found in committed receipt {ident['receipt_file']}"
                )
        if not str(ident.get("receipt_verified_utc", "")).startswith("2026-09-03"):
            errors.append(f"identity {fid}: receipt not same-day verified (2026-09-03)")

    # 5. every non-verified lane is an explicit open precondition
    open_pre = json.dumps(freeze.get("open_preconditions_before_any_study_model_call", []))
    for lane in freeze.get("lunarc_sbatch_lanes", []):
        fam = lane.get("family", "<unknown>")
        status = lane.get("status", "")
        if "LANE_VERIFIED_ON_LUNARC_SBATCH" not in status and fam not in open_pre:
            errors.append(f"lane for {fam} not verified and not declared an open precondition")

    # 6. banned proxy lane recorded as replaced
    if "35.220.164.252:3888/v1" not in json.dumps(freeze.get("provider_config_replacement", {})):
        errors.append("banned shipped proxy lane not recorded in provider_config_replacement")

    return {
        "schema": "ORION.A4.ModelIdentityFreezeCheckResult.v1",
        "decision": "RED" if errors else "GREEN",
        "errors": errors,
    }


def self_test(freeze: dict, tmp: Path) -> None:
    # structural green on the committed freeze
    r = verify(freeze, tmp)
    assert r["decision"] == "GREEN", f"expected GREEN, got {r}"

    # hostile: flag flipped
    forged = json.loads(json.dumps(freeze))
    forged["flags"]["intervention_study_executed"] = True
    r2 = verify(forged, tmp)
    assert r2["decision"] == "RED" and any("intervention_study_executed" in e for e in r2["errors"])

    # hostile: receipt file removed
    victim = tmp / freeze["model_identities"][0]["receipt_file"]
    keep = victim.read_bytes()
    victim.unlink()
    r3 = verify(json.loads(json.dumps(freeze)), tmp)
    assert r3["decision"] == "RED" and any("receipt file missing" in e for e in r3["errors"])
    victim.write_bytes(keep)

    # hostile: token removed from the receipt bytes (a receipt that no
    # longer carries the frozen token verbatim is a broken liveness claim)
    tok = freeze["model_identities"][0]["receipt_expected_token"].encode()
    assert tok in keep, "self-test fixture must carry the token verbatim"
    victim.write_bytes(keep.replace(tok, b"A4_TOKEN_SCRUBBED"))
    r4 = verify(json.loads(json.dumps(freeze)), tmp)
    assert r4["decision"] == "RED" and any("expected token not found" in e for e in r4["errors"])
    victim.write_bytes(keep)

    # hostile: two families only
    forged5 = json.loads(json.dumps(freeze))
    forged5["model_identities"] = forged5["model_identities"][:2]
    r5 = verify(forged5, tmp)
    assert r5["decision"] == "RED" and any("fewer than 3" in e for e in r5["errors"])

    # hostile: silent lane gap (verified status stripped without open precondition)
    forged6 = json.loads(json.dumps(freeze))
    forged6["lunarc_sbatch_lanes"][0]["status"] = "LANE_BLOCKED_HONEST_RECORD"
    r6 = verify(forged6, tmp)
    assert r6["decision"] == "RED" and any("open precondition" in e for e in r6["errors"])

    print("A4_MODEL_IDENTITY_FREEZE_SELF_TEST_GREEN")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", type=Path, required=True)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    freeze = json.loads(a.freeze.read_text())
    if a.self_test:
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            src = a.freeze.parent / "receipts"
            if src.is_dir():
                shutil.copytree(src, tdp / "receipts")
            self_test(freeze, tdp)
        return 0
    result = verify(freeze, a.freeze.parent)
    print(json.dumps(result, indent=1))
    return 0 if result["decision"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
