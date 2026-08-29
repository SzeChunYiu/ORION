#!/usr/bin/env python3
"""Fail closed if P6's commutation contract drifts across canonical artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_ID = "P6.COMMUTE.RW_NONINTERFERENCE.V1"
# papers/PAPER_ALIASES.md records {old: P6, new: ORION-16} and calls itself the single
# source of truth for paper-id aliases. The R0 rename rewrote the contract id in the
# prose artifacts to the ORION-16 form and left it as P6 in the executable source and in
# the frozen mechanized JSON, which must not be rewritten because they are evidence. So
# the same contract is now legitimately written two ways, and the binding has to accept
# either spelling rather than force one side to move.
CONTRACT_ID_ALIASES = (CONTRACT_ID, "ORION-16.COMMUTE.RW_NONINTERFERENCE.V1")
FILES = (
    "src/orion/study/p6/separation_calculus_smt.py",
    "papers/orion-16-formal-epistemic-structures-and-mechanics/formal/mechanized/P6_SEPARATION_CALCULUS_MECHANIZED_2026-08-21.json",
    "papers/orion-16-formal-epistemic-structures-and-mechanics/manuscript/FINAL_V5.md",
    "papers/orion-16-formal-epistemic-structures-and-mechanics/manuscript/sections/03-general-theorems.tex",
    "papers/orion-16-formal-epistemic-structures-and-mechanics/manuscript/FORMAL_CORE_V2_1.md",
    "papers/orion-16-formal-epistemic-structures-and-mechanics/submission/AIJ_MANUSCRIPT.tex",
    "papers/orion-16-formal-epistemic-structures-and-mechanics/CLAIM_LEDGER_V4.md",
)
MANIFEST = "papers/orion-16-formal-epistemic-structures-and-mechanics/CONTENT_MANIFEST_V2.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root: Path = ROOT) -> dict[str, object]:
    missing_id = []
    for relative in FILES:
        text = (root / relative).read_text(encoding="utf-8")
        candidates = [
            alias.replace("_", r"\_") if relative.endswith(".tex") else alias
            for alias in CONTRACT_ID_ALIASES
        ]
        if not any(candidate in text for candidate in candidates):
            missing_id.append(relative)

    source = (root / FILES[0]).read_text(encoding="utf-8")
    machine = json.loads((root / FILES[1]).read_text(encoding="utf-8"))
    final_md = (root / FILES[2]).read_text(encoding="utf-8")
    final_tex = (root / FILES[3]).read_text(encoding="utf-8")
    formal_core = (root / FILES[4]).read_text(encoding="utf-8")
    submission = (root / FILES[5]).read_text(encoding="utf-8")
    ledger = (root / FILES[6]).read_text(encoding="utf-8")
    errors = [f"missing contract id: {path}" for path in missing_id]
    for token in ('wl != wr', 'Not(vocab["ReadsL"](wr))', 'Not(vocab["ReadsR"](wl))'):
        if token not in source:
            errors.append(f"executable premise missing: {token}")
    theorem_by_name = {row["name"]: row for row in machine.get("theorems", [])}
    commutation = theorem_by_name.get("SEPARATED_COMMUTATION", {})
    necessity = theorem_by_name.get("SEPARATION_IS_NECESSARY", {})
    if machine.get("all_discharged") is not True:
        errors.append("mechanized artifact is not all_discharged")
    if not any(str(commutation.get("statement", "")).startswith(f"{alias}:") for alias in CONTRACT_ID_ALIASES):
        errors.append("mechanized commutation theorem is not bound to the contract id")
    if necessity.get("detail") != (
        "disagreeing models exist for both cross-read directions with disjoint "
        "writes and explicit frame-faithful deterministic mechanics"
    ):
        errors.append("mechanized necessity theorem lacks the symmetric countermodels")
    if "every specific pair" not in str(necessity.get("why_it_matters", "")):
        errors.append("mechanized necessity theorem lacks the instance-level limitation")

    for path, text in ((FILES[2], final_md), (FILES[3], final_tex)):
        lowered = " ".join(text.lower().split())
        for phrase in (
            "read-footprint faithful",
            "write-footprint faithful",
            "neither mechanic reads",
            "scientific projection",
            "cross-read exclusions",
        ):
            if phrase not in lowered:
                errors.append(f"{path} missing premise/conclusion: {phrase}")
        for legacy in (
            "two mechanics whose frames are disjoint commute",
            "separation is necessary for commutation and not only sufficient",
        ):
            if legacy in lowered:
                errors.append(f"{path} retains legacy bare-write theorem: {legacy}")

    semantic_bindings = (
        (FILES[4], formal_core, ("read/write-footprint faithful", "fully scientifically separated", "pi_{sci}")),
        (FILES[5], submission, ("read-footprint faithful", "write-footprint faithful", "pi_{sci}")),
        (FILES[6], ledger, ("both cross-read exclusions", "current scientific projection", "every particular pair")),
    )
    for path, text, phrases in semantic_bindings:
        normalized = " ".join(text.lower().split())
        for phrase in phrases:
            if phrase not in normalized:
                errors.append(f"{path} missing bound semantics: {phrase}")

    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    recorded_hashes = {
        row["path"]: row["sha256"]
        for row in manifest.get("bound_files", [])
        if isinstance(row, dict)
        and isinstance(row.get("path"), str)
        and isinstance(row.get("sha256"), str)
    }
    bound_paths = set(recorded_hashes)
    required_bound = set(FILES)
    for path in sorted(required_bound - bound_paths):
        errors.append(f"content manifest omits contract artifact: {path}")
    if manifest.get("subject_commit_status") != "BOUND":
        errors.append("content manifest subject_commit_status is not BOUND")
    if manifest.get("subject_commit_unbound_paths") != []:
        errors.append("content manifest retains unbound contract paths")

    for path in sorted(required_bound):
        actual = _sha256(root / path)
        if recorded_hashes.get(path) != actual:
            errors.append(f"V2 content-manifest mismatch or omission: {path}")
    return {
        "schema": "orion.p6.commutation-contract-binding.v1",
        "contract_id": CONTRACT_ID,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "authority_boundary": (
            "SMT entailment under declared assumptions only; not necessity for every "
            "specific mechanic pair, kernel verification, independent formal review, "
            "or deployed-system validation."
        ),
    }


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
