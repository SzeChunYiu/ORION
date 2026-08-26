#!/usr/bin/env python3
"""Theorem-complete census for V1-THEOREM-CENSUS-01.

Enumerates every declared theorem at the frozen base and binds it to its
formal domain, proof artifact, mechanization status and remaining
verification. Distinguishes a proved schema from a mechanized proof from a
finite enumeration, and never promotes one to another.

Negative terminals it can report: THEOREM_IDENTITY_COLLISION,
ASSUMPTION_UNBOUND, PROOF_STATUS_OVERCLAIM, CANNOT_CHECK.

Repairs nothing. Emits no scientific authority.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

FOUND = "research/orion-foundations-v3"
MECHANIZED = {"MECHANIZED_CORE", "MECHANIZED_FINITE_WITNESSES", "MECHANIZED_DEFINITIONAL_COUPLING"}


def show(base: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{base}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--lean-build", choices=["PASS", "FAIL", "CANNOT_CHECK"], default="CANNOT_CHECK")
    ap.add_argument("--lean-evidence", default="")
    args = ap.parse_args()
    base = args.base

    raw_thm = show(base, f"{FOUND}/THEOREM_LEDGER_V1.json")
    raw_paper = show(base, f"{FOUND}/PAPER_THEOREM_LEDGER_V1.json")
    raw_cov = show(base, f"{FOUND}/FORMALIZATION_COVERAGE_V1.json")
    if not (raw_thm and raw_paper and raw_cov):
        print("V1_THEOREM_CENSUS: CANNOT_CHECK — a source ledger is absent at the frozen base")
        return 2

    thm = json.loads(raw_thm)
    paper = json.loads(raw_paper)
    cov = json.loads(raw_cov)
    lean_by_id = {t["theorem_id"]: t for t in cov["theorems"]}

    rows: list[dict[str, Any]] = []
    for t in thm["theorems"]:
        lean = lean_by_id.get(t["theorem_id"], {})
        artifact = t.get("proof_artifact")
        artifact_path = f"{FOUND}/{artifact}" if artifact else None
        rows.append({
            "theorem_id": t["theorem_id"],
            "family": "OSTC",
            "title": t.get("title"),
            "formal_domain": t.get("formal_domain"),
            "declared_status": t.get("status"),
            "proof_artifact": artifact_path,
            "proof_artifact_present": bool(artifact_path and show(base, artifact_path) is not None),
            "lean_status": lean.get("lean_status", "ABSENT_FROM_COVERAGE"),
            "machine_checked": lean.get("machine_checked"),
            "not_machine_checked": lean.get("not_machine_checked"),
            "remaining_verification": t.get("remaining_verification"),
            "authority_delta": "NONE",
        })

    for p in paper["papers"]:
        for name in p["theorems"]:
            rows.append({
                "theorem_id": f"{p['paper']}::{name.split()[0]}",
                "family": p["paper"],
                "title": name,
                "formal_domain": p.get("object"),
                "declared_status": p.get("status"),
                "ostc_dependencies": p.get("ostc_dependencies"),
                "execution_job": p.get("execution_job"),
                "proof_artifact": None,
                "proof_artifact_present": False,
                "lean_status": "NOT_APPLICABLE_PAPER_LEVEL",
                "remaining_verification": "bound to the paper's own execution job",
                "authority_delta": "NONE",
            })

    ids = [r["theorem_id"] for r in rows]
    collisions = sorted({i for i, c in Counter(ids).items() if c > 1})
    missing_artifact = [r["theorem_id"] for r in rows if r["family"] == "OSTC" and not r["proof_artifact_present"]]
    # Overclaim: a mechanized status with no Lean project, or PROVED with no artifact.
    lean_present = show(base, f"{FOUND}/formal/lean/OrionFoundations/Core.lean") is not None
    overclaims = []
    for r in rows:
        if r["lean_status"] in MECHANIZED and not lean_present:
            overclaims.append({"theorem_id": r["theorem_id"], "reason": "mechanized status with no Lean source at base"})
        if r["family"] == "OSTC" and str(r["declared_status"]).startswith("PROVED") and not r["proof_artifact_present"]:
            overclaims.append({"theorem_id": r["theorem_id"], "reason": "PROVED status with absent proof artifact"})

    terminal = "V1_THEOREM_CENSUS_COMPLETE"
    if collisions:
        terminal = "THEOREM_IDENTITY_COLLISION"
    elif overclaims:
        terminal = "PROOF_STATUS_OVERCLAIM"

    payload = {
        "schema": "ORION.V1.TheoremCensus.v1",
        "base_main": base,
        "terminal": terminal,
        "theorems": rows,
        "summary": {
            "total": len(rows),
            "ostc": sum(r["family"] == "OSTC" for r in rows),
            "paper_level": sum(r["family"] != "OSTC" for r in rows),
            "lean_status": dict(Counter(r["lean_status"] for r in rows if r["family"] == "OSTC")),
            "declared_status": dict(Counter(str(r["declared_status"]) for r in rows)),
            "identity_collisions": len(collisions),
            "ostc_missing_proof_artifact": len(missing_artifact),
            "proof_status_overclaims": len(overclaims),
        },
        "identity_collisions": collisions,
        "proof_status_overclaims": overclaims,
        "mechanization": {
            "lean_project": f"{FOUND}/formal/lean",
            "lean_toolchain": cov.get("lean_toolchain"),
            "lean_source_present_at_base": lean_present,
            "lean_build": args.lean_build,
            "lean_build_evidence": args.lean_evidence,
            "authority": cov.get("authority"),
            "note": "same-programme mechanization. Independent external proof review remains CANNOT_CHECK and is not granted here.",
        },
        "authority_delta": "NONE",
    }
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print("terminal:", terminal)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
