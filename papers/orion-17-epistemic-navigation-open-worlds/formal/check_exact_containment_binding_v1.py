#!/usr/bin/env python3
"""Fail closed if P7's exact-containment contract drifts across artifacts.

Binds ``P7.CONTAIN.EXACT_BRIDGE_RULE.V1`` across the executable, the mechanized
receipt, the manuscript surfaces, the addendum ledger, the content manifest and
their V2 content digests --- the same discipline as orion-16's kernel-contract
checker. The
composition calculus's own contract stays bound by its own checkers; this one
covers the replacement rule only.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_ID = "P7.CONTAIN.EXACT_BRIDGE_RULE.V1"
# papers/PAPER_ALIASES.md records {old: P7, new: ORION-17} and calls itself the single
# source of truth for paper-id aliases. The R0 rename rewrote the contract id in the prose
# artifacts to the ORION-17 form and left it as P7 in the executable source and in the
# frozen mechanized JSON, which are evidence and must not be rewritten. The same contract is
# therefore legitimately written two ways, and the binding accepts either spelling.
CONTRACT_ID_ALIASES = (CONTRACT_ID, CONTRACT_ID.replace("P7.", "ORION-17.", 1))
FILES = (
    "src/orion/study/p7/exact_containment.py",
    "papers/orion-17-epistemic-navigation-open-worlds/formal/mechanized/"
    "P7_EXACT_CONTAINMENT_MECHANIZED_2026-08-24.json",
    "papers/orion-17-epistemic-navigation-open-worlds/formal/"
    "check_exact_containment_binding_v1.py",
    "papers/orion-17-epistemic-navigation-open-worlds/manuscript/FINAL_V4.md",
    "papers/orion-17-epistemic-navigation-open-worlds/manuscript/FORMAL_CORE_V2.md",
    "papers/orion-17-epistemic-navigation-open-worlds/CLAIM_LEDGER_ADDENDUM_V3.md",
)
MANIFEST = (
    "papers/orion-17-epistemic-navigation-open-worlds/CONTENT_MANIFEST_V2.json"
)

REQUIRED_THEOREMS = (
    "REFLEXIVITY_OF_CONTAINMENT",
    "TRANSITIVITY_OF_CONTAINMENT",
    "EXACT_RULE_IS_SOUND",
    "EXACT_RULE_IS_NOT_DROPPABLE",
    "EXACT_RULE_SUBSUMES_THE_BRIDGE_RULE",
    "CONTAINMENT_STRICTLY_WEAKER_THAN_MATCH",
    "LEFT_IDENTITY_UNDER_EXACT_RULE",
    "RIGHT_IDENTITY_UNDER_EXACT_RULE",
    "IDENTITY_STRICT_UNDER_EXACT_RULE",
    "ASSOCIATIVITY_OBSERVABLE_UNDER_EXACT_RULE",
    "ASSOCIATIVITY_STRICT_UNDER_EXACT_RULE",
    "EXACT_CALCULUS_IS_SATISFIABLE",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root: Path = ROOT) -> dict[str, object]:
    errors: list[str] = []
    texts: dict[str, str] = {}
    for relative in FILES:
        path = root / relative
        if not path.exists():
            errors.append(f"missing file: {relative}")
            continue
        texts[relative] = path.read_text(encoding="utf-8")
        if not any(alias in texts[relative] for alias in CONTRACT_ID_ALIASES):
            errors.append(f"missing contract id: {relative}")

    source = texts.get(FILES[0], "")
    for token in (
        "Contains(a, b)  :=  forall o. Demands(b, o) -> Demands(a, o)",
        "contains_def_axiom",
        "exact_calculus_axioms",
        "EXACT_RULE_IS_SOUND",
        "CONTAINMENT_STRICTLY_WEAKER_THAN_MATCH",
        "not_licensed",
    ):
        if token not in source:
            errors.append(f"source missing vocabulary: {token}")

    machine = json.loads(texts[FILES[1]]) if FILES[1] in texts else {}
    if machine:
        if machine.get("contract_id") not in CONTRACT_ID_ALIASES:
            errors.append("mechanized record is not bound to the contract id")
        if machine.get("all_discharged") is not True:
            errors.append("mechanized record has undischarged theorems")
        outcomes = {t["name"]: t["outcome"] for t in machine.get("theorems", [])}
        for name in REQUIRED_THEOREMS:
            if outcomes.get(name) != "PROVED":
                errors.append(f"mechanized record did not prove {name}")
        replaced = str(machine.get("replaces", ""))
        if "Match(a,b) := a = b OR Bridge(a,b)" not in replaced:
            errors.append("mechanized record does not name the rule it replaces")
        not_licensed = " ".join(str(x) for x in machine.get("not_licensed", []))
        if "incompleteness" not in not_licensed:
            errors.append("mechanized record may retract the old incompleteness")
        if "data-heavy" not in not_licensed:
            errors.append("mechanized record omits the open data-heavy sub-box")

    final_md = texts.get(FILES[3], "")
    formal_core = texts.get(FILES[4], "")
    ledger = texts.get(FILES[5], "")
    for path, text, phrases in (
        (FILES[3], final_md, (
            "sound but incomplete",
            "exact containment",
            "twelve discharges",
            "remains open",
        )),
        (FILES[4], formal_core, (
            "EXACT_RULE_IS_SOUND",
            "EXACT_RULE_IS_NOT_DROPPABLE",
            "EXACT_CALCULUS_IS_SATISFIABLE",
            "is not retracted",
        )),
        (FILES[5], ledger, (
            "cannot_check".upper(),
            "additive rows only",
            "prohibited inference",
        )),
    ):
        normalized = " ".join(text.lower().split())
        for phrase in phrases:
            if phrase.lower() not in normalized:
                errors.append(f"{path} missing bound semantics: {phrase}")

    # The old rule's incompleteness must still be on record, append-only.
    if "provably" not in final_md.lower() or "incomplete" not in final_md.lower():
        errors.append("FINAL_V4 no longer records the old rule's incompleteness")

    manifest_path = root / MANIFEST
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        recorded_hashes = {
            row["path"]: row["sha256"]
            for row in manifest.get("bound_files", [])
            if isinstance(row, dict)
            and isinstance(row.get("path"), str)
            and isinstance(row.get("sha256"), str)
        }
        bound_paths = set(recorded_hashes)
        required_bound = {p for p in FILES if p.startswith("papers/orion-17-")}
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
    else:
        errors.append(f"missing manifest: {MANIFEST}")

    return {
        "schema": "orion.p7.exact-containment-binding.v1",
        "contract_id": CONTRACT_ID,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "authority_boundary": (
            "solver discharges (z3 refutation for validity, closed finite "
            "witnesses for possibility) produced and checked in the producing "
            "lane; the old rule's incompleteness theorem stands un-retracted; "
            "no empirical coverage, no independent formal review."
        ),
    }


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
