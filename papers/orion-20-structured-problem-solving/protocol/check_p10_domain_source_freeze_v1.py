#!/usr/bin/env python3
"""Checker for P10_DOMAIN_SOURCE_FREEZE_V1.json (ORION.P10.DomainSourceFreeze.v1).

Exit codes:
  0 — the frozen artifact is intact and internally consistent
  1 — VIOLATIONS: the artifact was edited in a way that breaks the freeze contract
  2 — CANNOT_CHECK: artifact missing, unparseable, or the bound H1-H6 protocol
      freeze is absent from disk so the sha binding cannot be recomputed
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_FREEZE_REL = "papers/orion-20-structured-problem-solving/protocol/P10_H1_H6_PROTOCOL_FREEZE_V1.json"
EXPECTED_PROTOCOL_FREEZE_SHA = "8e32c2bee514d246bcd503fc2f0ef078bcc52adb7f40abdbcb642b703aec355c"

EXPECTED_DOMAIN_IDS = {
    "LEAN_INTERACTIVE_THEOREM_PROVING",
    "SYGUS_SYNTAX_GUIDED_SYNTHESIS",
    "IPC_PLANNING",
    "CODE_GENERATION",
}

ARM_STATUSES_FORBIDDEN_TO_CLAIM_EXECUTION = {
    "DONE",
    "EXECUTED",
    "PARTIAL",
    "RUNNING",
    "COMPLETE",
    "IMPLEMENTED",
    "AVAILABLE",
}

HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _violations(doc: dict) -> list[str]:
    v: list[str] = []

    # --- frozen-protocol banner -------------------------------------------------
    if doc.get("artifact_class") != "FROZEN_PROTOCOL":
        v.append("artifact_class must be FROZEN_PROTOCOL")
    for flag in ("results_exist", "campaign_executed", "outcome_accessed"):
        if doc.get(flag) is not False:
            v.append(f"{flag} must be false (frozen protocol, no results)")
    if "never be cited as evidence" not in doc.get("labeling_rule", ""):
        v.append("labeling_rule must forbid citing this artifact as empirical evidence")

    # --- protocol freeze binding (live recompute against disk) ------------------
    binding = doc.get("protocol_freeze_binding", {})
    declared = binding.get("sha256", "")
    if declared != EXPECTED_PROTOCOL_FREEZE_SHA:
        v.append(f"protocol_freeze_binding.sha256 drifted from the frozen value: {declared!r}")
    freeze_path = REPO_ROOT / PROTOCOL_FREEZE_REL
    if freeze_path.is_file():
        live = _sha256_of(freeze_path)
        if live != declared:
            v.append("protocol_freeze_binding.sha256 does not match the on-disk H1-H6 protocol freeze")
    # freeze file absent on disk -> run() returns CANNOT_CHECK before _violations is reached
    if not binding.get("inputs_remaining_absent"):
        v.append("protocol_freeze_binding.inputs_remaining_absent must stay nonempty (6 required inputs absent)")
    if binding.get("inputs_discharged_by_this_artifact") != []:
        v.append("this artifact discharges no H1-H6 required input")

    # --- domains ----------------------------------------------------------------
    domains = doc.get("frozen_domains", [])
    ids = [d.get("domain_id") for d in domains]
    if len(domains) != 4:
        v.append(f"exactly four domains are frozen, found {len(domains)}")
    if set(ids) != EXPECTED_DOMAIN_IDS:
        v.append(f"domain set drifted from the frozen four: {sorted(set(ids))}")
    seen_sources: set[str] = set()
    for d in domains:
        did = d.get("domain_id", "<none>")
        if not d.get("verifier"):
            v.append(f"{did}: verifier must be named")
        sources = d.get("sources", [])
        if not sources:
            v.append(f"{did}: at least one source must be frozen")
        for s in sources:
            sid = s.get("source_id", "<none>")
            key = (did, sid)
            if key in seen_sources:
                v.append(f"{key}: duplicate source entry")
            seen_sources.add(key)
            if not s.get("url", "").startswith("https://"):
                v.append(f"{key}: source url must be an https URL")
            lic = s.get("license")
            if not isinstance(lic, dict):
                v.append(f"{key}: license object required")
                continue
            _check_license(key, lic, v)

    # miniF2F upstream has no licence file: a licence NAME on it is a false clearance
    for d in domains:
        for s in d.get("sources", []):
            if s.get("source_id") == "MINIF2F":
                lic = s.get("license", {})
                if lic.get("name") is not None or lic.get("verification") != "CANNOT_CHECK":
                    v.append("MINIF2F upstream licence must stay CANNOT_CHECK with name null (no licence file upstream)")

    # --- committed minimums ------------------------------------------------------
    mins = doc.get("committed_minimums", {})
    if mins.get("domains", 0) < 4:
        v.append("committed_minimums.domains must be >= 4")
    if mins.get("independent_tasks_per_domain", 0) < 100:
        v.append("committed_minimums.independent_tasks_per_domain must be >= 100")
    if mins.get("total_independent_tasks", 0) < 400:
        v.append("committed_minimums.total_independent_tasks must be >= 400")
    if mins.get("known_method_controls", 0) < 80:
        v.append("committed_minimums.known_method_controls must be >= 80")
    if mins.get("satisfied_by_this_artifact") is not False:
        v.append("committed_minimums.satisfied_by_this_artifact must be false (commitments, not executed counts)")

    # --- inference unit ----------------------------------------------------------
    unit = doc.get("inference_unit", {})
    if unit.get("primary") != "one protected verifier-backed theorem or task":
        v.append("inference_unit.primary must be one protected verifier-backed theorem or task")
    for fu in ("search seed", "model sample", "generated row", "technical repeat"):
        if fu not in unit.get("forbidden_units", []):
            v.append(f"inference_unit.forbidden_units must contain {fu!r}")

    # --- box verdicts ------------------------------------------------------------
    boxes = doc.get("box_verdicts", {})

    box1 = boxes.get("box_1_populate_frozen_design", {})
    if box1.get("verdict") != "DONE_AT_DOMAIN_SOURCE_LICENSE_LAYER":
        v.append("box_1 verdict must be DONE_AT_DOMAIN_SOURCE_LICENSE_LAYER")
    if "NOT_POPULATED" not in box1.get("detail", ""):
        v.append("box_1 must state the per-task enumeration is NOT_POPULATED")
    if not box1.get("open_remainder"):
        v.append("box_1 must record its open remainder")

    box2 = boxes.get("box_2_implement_baselines", {})
    if box2.get("verdict") != "CANNOT_CHECK":
        v.append("box_2 verdict must be CANNOT_CHECK")
    arm_ids = [a.get("arm_id") for a in box2.get("arms", [])]
    for expected in ("NATIVE", "EXACT_SEARCH", "SYNTHESIS", "REPRESENTATION_ONLY", "STRONGEST_DONOR"):
        if expected not in arm_ids:
            v.append(f"box_2 is missing arm {expected}")
    for a in box2.get("arms", []):
        status = a.get("status", "")
        if status in ARM_STATUSES_FORBIDDEN_TO_CLAIM_EXECUTION:
            v.append(f"box_2 arm {a.get('arm_id')} claims execution-level status {status!r}")
        if not a.get("reason"):
            v.append(f"box_2 arm {a.get('arm_id')} must carry a reason")
    if "forbidden" not in box2.get("no_weak_proxy_substitution", ""):
        v.append("box_2 must forbid weak-proxy substitution")

    box3 = boxes.get("box_3_run_h1_h6", {})
    if box3.get("verdict") != "CANNOT_CHECK":
        v.append("box_3 verdict must be CANNOT_CHECK")
    if len(box3.get("reasons", [])) < 3:
        v.append("box_3 must carry its three frozen reasons (unauthorized execution, absent inputs, H4 witness boundary)")
    joined3 = " ".join(box3.get("reasons", []))
    if "execution_authorized=false" not in joined3:
        v.append("box_3 reasons must cite execution_authorized=false")
    if "self-certifying" not in joined3:
        v.append("box_3 reasons must cite the H4 external-witness self-certification ban")

    box4 = boxes.get("box_4_machine_check_candidate_edits", {})
    if box4.get("verdict") != "CANNOT_CHECK":
        v.append("box_4 verdict must be CANNOT_CHECK")
    if not box4.get("reason"):
        v.append("box_4 must carry a reason")
    if not box4.get("frozen_contract"):
        v.append("box_4 must freeze the machine-check contract for future candidate edits")
    for r in box4.get("prior_receipts", []):
        if not r.get("artifact") or not HEX64.match(r.get("sha256", "") or ""):
            v.append("box_4 prior receipts must bind artifact + 64-hex sha256")

    # --- prior adverse evidence ---------------------------------------------------
    if len(doc.get("prior_adverse_evidence", [])) < 2:
        v.append("prior_adverse_evidence must bind at least the attainability and generated-OCME receipts")
    for p in doc.get("prior_adverse_evidence", []):
        if not p.get("artifact"):
            v.append("prior_adverse_evidence entry missing artifact path")
        if not HEX64.match(p.get("sha256", "") or ""):
            v.append(f"prior_adverse_evidence {p.get('artifact', '<none>')}: sha256 must be 64 lowercase hex")
        if not p.get("binding_role"):
            v.append(f"prior_adverse_evidence {p.get('artifact', '<none>')}: binding_role required")

    # --- boundaries ----------------------------------------------------------------
    if len(doc.get("non_bypass_boundaries", [])) < 5:
        v.append("non_bypass_boundaries must keep all five frozen boundary statements")

    return v


def _check_license(key: tuple[str, str], lic: dict, v: list[str]) -> None:
    verification = lic.get("verification")
    if verification == "VERIFIED_WITH_URL_AND_DATE":
        if not lic.get("name"):
            v.append(f"{key}: VERIFIED licence must name the SPDX id")
        if not lic.get("verified_utc"):
            v.append(f"{key}: VERIFIED licence must carry verified_utc")
        if not lic.get("evidence_url", "").startswith("https://"):
            v.append(f"{key}: VERIFIED licence must carry an https evidence_url")
        if not HEX64.match(lic.get("evidence_fetch_sha256", "") or ""):
            v.append(f"{key}: VERIFIED licence must carry a 64-hex evidence_fetch_sha256")
    elif verification == "CANNOT_CHECK":
        if lic.get("name") is not None:
            v.append(f"{key}: CANNOT_CHECK licence must not assert a name")
        if len(lic.get("reason", "") or "") < 40:
            v.append(f"{key}: CANNOT_CHECK licence must carry a precise reason")
    else:
        v.append(f"{key}: licence verification must be VERIFIED_WITH_URL_AND_DATE or CANNOT_CHECK, got {verification!r}")


def run(path: Path) -> int:
    if not path.is_file():
        print(f"CANNOT_CHECK: artifact not found: {path}")
        return 2
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"CANNOT_CHECK: artifact unparseable: {exc}")
        return 2
    if not isinstance(doc, dict) or doc.get("schema") != "ORION.P10.DomainSourceFreeze.v1":
        print("CANNOT_CHECK: artifact is not ORION.P10.DomainSourceFreeze.v1")
        return 2

    freeze_path = REPO_ROOT / PROTOCOL_FREEZE_REL
    if not freeze_path.is_file():
        print(f"CANNOT_CHECK: bound H1-H6 protocol freeze absent from disk, sha binding not recomputable: {PROTOCOL_FREEZE_REL}")
        return 2

    violations = _violations(doc)
    if violations:
        print(f"VIOLATIONS ({len(violations)}):")
        for item in violations:
            print(f"  - {item}")
        return 1
    print("P10_DOMAIN_SOURCE_FREEZE_V1: intact (4 domains, minimums committed not executed, licences verified-or-CANNOT_CHECK, protocol-freeze sha binding recomputed)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(__file__).resolve().parent / "P10_DOMAIN_SOURCE_FREEZE_V1.json"
    parser.add_argument("artifact", nargs="?", default=default, type=Path)
    args = parser.parse_args()
    return run(args.artifact)


if __name__ == "__main__":
    sys.exit(main())
