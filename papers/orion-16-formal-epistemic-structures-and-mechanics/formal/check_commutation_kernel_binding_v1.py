#!/usr/bin/env python3
"""Fail closed if P6's exact-Theorem-7 kernel contract drifts across artifacts.

Binds the kernel mechanization (``P6.COMMUTE.EXACT_THEOREM7.V1``) the way
``check_commutation_contract_binding_v1`` binds the SMT contract: the id and
the load-bearing phrases must appear in the executable, the mechanized record,
the manuscript surfaces and the ledgers, and the hashes must match. The SMT
contract of #1096 stays bound by its own checker; this one covers the kernel
statement only.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_ID = "P6.COMMUTE.EXACT_THEOREM7.V1"
# papers/PAPER_ALIASES.md records {old: P6, new: ORION-16} and calls itself the single
# source of truth for paper-id aliases. The R0 rename rewrote the contract id in the prose
# artifacts to the ORION-16 form and left it as P6 in the executable source and in the
# frozen mechanized JSON, which are evidence and must not be rewritten. The same contract is
# therefore legitimately written two ways, and the binding accepts either spelling.
CONTRACT_ID_ALIASES = (CONTRACT_ID, CONTRACT_ID.replace("P6.", "ORION-16.", 1))
FILES = (
    "src/orion/study/p6/commutation_kernel.py",
    "papers/orion-16-formal-epistemic-structures-and-mechanics/formal/mechanized/P6_COMMUTATION_KERNEL_MECHANIZED_2026-08-24.json",
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
    for token in ("EXACT_STATEMENT", "W1M_SCI_WRITE", "W1N_SCI_WRITE",
                  "FIDM_READ_FOOTPRINT", "FIDN_READ_FOOTPRINT",
                  "SEP1_WRITES_DISJOINT", "H5_INDEP_SWAP", "H7_EQ_IMPLIES_HEQ",
                  "trusted_computing_base"):
        if token not in source:
            errors.append(f"kernel source missing vocabulary: {token}")

    replay = machine.get("replay") or {}
    if replay.get("conclusion_matches") is not True:
        errors.append("mechanized kernel replay did not reproduce the conclusion")
    if replay.get("residual_hypotheses_within_theory") is not True:
        errors.append("mechanized kernel replay left hypotheses outside the theory")
    if machine.get("z3_cross_check", {}).get("outcome") != "PROVED":
        errors.append("z3 cross-check of the kernel statement is not PROVED")
    rule_count = machine.get("kernel_rule_applications")
    if not isinstance(rule_count, int) or rule_count != len(machine.get("proof_log", [])):
        errors.append("recorded rule count does not match the serialized proof log")
    if not any(str(machine.get("statement", "")).startswith(f"{alias}:") for alias in CONTRACT_ID_ALIASES):
        errors.append("mechanized statement is not bound to the contract id")
    if "ORION-authored Python" not in str(machine.get("trusted_computing_base", "")):
        errors.append("mechanized record omits the trusted-computing-base boundary")
    if not machine.get("assumed_not_derived"):
        errors.append("mechanized record omits the assumed-not-derived list")

    for path, text in ((FILES[2], final_md), (FILES[3], final_tex)):
        normalized = " ".join(text.lower().split())
        for phrase in (
            "read-footprint faithful",
            "write-footprint faithful",
            "fully scientifically separated",
            "independent events",
            "kernel",
            "replay",
        ):
            if phrase not in normalized:
                errors.append(f"{path} missing bound semantics: {phrase}")

    semantic_bindings = (
        (FILES[4], formal_core, ("450", "replayed", "independence symmetry")),
        (FILES[5], submission, ("read-footprint faithful", "write-footprint faithful")),
        (FILES[6], ledger, ("exact theorem 7", "kernel", "replay")),
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

    for path in sorted(required_bound):
        actual = _sha256(root / path)
        if recorded_hashes.get(path) != actual:
            errors.append(f"V2 content-manifest mismatch or omission: {path}")
    return {
        "schema": "orion.p6.commutation-kernel-binding.v1",
        "contract_id": CONTRACT_ID,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "authority_boundary": (
            "kernel proof in an ORION-authored LCF-style Python kernel plus a z3 "
            "cross-check; replay re-checks the recorded steps but cannot detect a "
            "defect shared by every copy of the rules; not Lean, not independent "
            "formal review, not deployed-system validation."
        ),
    }


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
