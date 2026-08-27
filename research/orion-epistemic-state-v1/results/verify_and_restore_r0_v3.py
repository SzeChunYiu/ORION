#!/usr/bin/env python3
"""R0 frozen-artifact batch repair, layer 3: generalize the DES-CENSUS-01
byte-restore to every R0-corrupted frozen/terminal artifact under research/.

Method identical to layer 2 (`DES-CENSUS-01/verify_and_restore_r0_v2.py`,
imported for its move vocabulary): a file is admitted for restore ONLY if
  1. git history shows its only post-creation touch is R0 (3a1a8317);
  2. applying the FORWARD R0 rename vocabulary to its last pre-R0 bytes
     reproduces the R0 bytes exactly — JSON files leaf-by-leaf, text files
     (.py/.md/.sh) byte-exact on the whole file;
so R0's edit is proven to be a pure name rewrite with no content change, and
restore = return to the authored state (which also re-heals any self-recorded
digest pin authored pre-R0).

Classification (restore / leave / defer) — restore only high-confidence
TERMINAL evidence (freezes, receipts, manifests, records, archived campaign +
failure + exec artifacts, frozen-study executors); LEAVE living state that
must track the current namespace (inventories, ledgers, matrices, backlogs,
progress logs, publication tooling); DEFER ambiguous classes (test fixtures,
programme prose) to explicit per-file decisions.

Run from the repository root. Writes one batch receipt next to this script.
Fails loudly (exit 1) if any RESTORE-class file fails the gate; never writes
a file that did not pass.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "DES-CENSUS-01"))
from verify_and_restore_r0_v2 import (  # noqa: E402
    move_vocabulary, vocab_rewrite, vocab_rewrite_guarded, leaf_diffs,
)

REPO = Path(__file__).resolve().parents[3]
R0 = "3a1a8317"
SCAN_ROOT = "research/"
EXCLUDE_PREFIXES = (
    "research/orion-v1-freeze/",          # R0's own exclusion zone
    "research/orion-epistemic-state-v1/results/DES-CENSUS-01/",  # repaired in layer 2
)
TERMINAL_PREFIXES = (
    "research/failures/",
    "research/campaigns/",
    "research/campaign-runs/",
    "research/orion-epistemic-state-v1/results/",
    "research/verification/records/",
    "research/orion-discovery-v2/exec/",
    "research/revival/",
    "research/assimilation/",
    "research/self-orion-v3/confirmatory/",
    "research/p3-coordinate-necessity-v1/",
    "research/p3-partial-observation-record-gold-v1/",
    "research/p4-partial-evidence-acquisition-v2/",
    "research/phase2/",
    "research/extensions/",
    "research/paper-programme-v1/p6-clean-room/",
    "research/paper-programme-v1/acquisition/",
)
TERMINAL_NAMES = ("PACKET.md",)  # freeze-contract packets under development/
TERMINAL_NAME_SUBSTR = ("RETENTION_RECEIPT",)
LIVING = {
    "research/development/cannot_check_inventory.json": "living inventory (42 commits)",
    "research/development/sweep_self_comparison.py": "living sweep tooling",
    "research/claim_expansion/p3/claude_t5/PROGRESS.md": "progress log tracks current namespace",
    "research/claim_expansion/p7/claude_t1/PROGRESS.md": "progress log tracks current namespace",
    "research/claim_expansion/p9/claude_t3_t4/PROGRESS.md": "progress log tracks current namespace",
    "research/publication/README.md": "living navigation",
    "research/publication/publication_status.json": "living status (6 commits)",
    "research/publication/scoreboard.py": "living tooling (6 commits)",
    "research/verification/audit.py": "living tooling (4 commits)",
    "research/paper-programme-v1/journal_package/check_journal_package.py": "living tooling (5 commits)",
    "research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.json": "living backlog (12 commits)",
    "research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json": "living ledger (7 commits)",
    "research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_2026-08-21.md": "living ledger (7 commits)",
    "research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_REPORT_2026-08-21.json": "living report (11 commits)",
    "research/paper-programme-v1/P1_P15_ACTIVE_BLOCKER_MATRIX_2026-08-22.json": "living matrix",
    "research/paper-programme-v1/P1_P15_RECURSIVE_RESOLUTION_LEDGER_2026-08-23.json": "living ledger (10 commits)",
    "research/paper-programme-v1/REVIVAL_BACKLOG_V1.md": "living backlog",
}
DEFER = {
    "research/novelty/fixtures/adv_broad-claim-narrow-residual.json": "test fixture — consumed by live test code; forward-update vs restore is a CI-lane decision",
    "research/novelty/self-application/orion_P3_280.json": "same fixture-class concern",
    "research/paper-programme-v1/P3_BOUNDED_PUBLICATION_TRACK_2026-08-18.md": "programme prose",
    "research/paper-programme-v1/PAPER_05_SELF_ORION.md": "programme prose",
    "research/paper-programme-v1/REGISTERED_DISCRIMINATIONS_THE_ARTIFACT_CANNOT_EXPRESS.md": "programme prose",
    "research/paper-programme-v1/SELF_ORION_V3_T8_HANDOFF_2026-08-18.md": "programme prose (handoff)",
}


def git(*args: str, binary: bool = False):
    out = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, check=True)
    return out.stdout if binary else out.stdout.decode()


def classify(rel: str) -> str:
    if rel in LIVING:
        return "LEAVE"
    if rel in DEFER:
        return "DEFER"
    if rel.startswith(TERMINAL_PREFIXES) or rel.rsplit("/", 1)[-1] in TERMINAL_NAMES:
        return "RESTORE"
    if any(s in rel for s in TERMINAL_NAME_SUBSTR):
        return "RESTORE"
    return "DEFER"


def self_pin_report(data, own_hash: str, old_hash: str) -> list[str]:
    """Any 64-hex field inside the artifact: does it pin this file's pre-R0
    bytes (heals on restore), its R0 bytes (breaks on restore!), or neither?"""
    found: list[str] = []

    def scan(o, p="$"):
        if isinstance(o, dict):
            for k, v in o.items():
                scan(v, f"{p}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                scan(v, f"{p}[{i}]")
        elif isinstance(o, str) and len(o) == 64 and all(c in "0123456789abcdef" for c in o):
            role = ("PRE-R0 OWN (heals)" if o == old_hash else
                    "R0 OWN (would break!)" if o == own_hash else "external/other")
            found.append(f"{p}={o[:12]}… -> {role}")
    scan(data)
    return found


def main() -> int:
    V = move_vocabulary()
    vocab_rewrite("", V)  # build cache once

    diff = git("diff", "--name-only", f"{R0}^..{R0}", "--", SCAN_ROOT).splitlines()
    rows, failures = {}, []
    for rel in diff:
        if any(rel.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        log = git("log", "--format=%h", "--", rel).split()
        if not log or log[0] != R0:
            continue  # not last-touched by R0
        verdict = classify(rel)
        pre = next((c for c in log[1:] if c != R0), None)
        row = {"class": verdict, "pre_r0_commit": pre, "commits": len(log)}
        if verdict != "RESTORE":
            row["reason"] = LIVING.get(rel) or DEFER.get(rel) or "no terminal rule matched"
            rows[rel] = row
            continue
        if pre is None:
            failures.append(f"{rel}: R0 is the only commit (created by R0) — not a restore target")
            rows[rel] = {**row, "gate": "FAIL", "reason": "created BY R0"}
            continue
        orig = git("show", f"{pre}:{rel}", binary=True)
        r0b = git("show", f"HEAD:{rel}", binary=True)
        gate_mode = None
        try:
            if rel.endswith(".json"):
                diffs = leaf_diffs(json.loads(orig), json.loads(r0b))
                explained = lambda rw: all(  # noqa: E731
                    isinstance(a, str) and isinstance(b, str) and rw(a) == b
                    for _, a, b in diffs)
                ok = explained(lambda s: vocab_rewrite(s, V))
                if not ok:  # R0's pass-B guard (candidates/, 2026-08-pre-unification/)
                    ok, gate_mode = explained(lambda s: vocab_rewrite_guarded(s, V)), "guarded-passB"
                row["diffs"] = len(diffs)
            else:
                ok = vocab_rewrite(orig.decode(), V) == r0b.decode()
                if not ok:
                    ok = vocab_rewrite_guarded(orig.decode(), V) == r0b.decode()
                    gate_mode = "guarded-passB"
                row["diffs"] = "text-byte-exact"
        except Exception as e:  # gate failure, never a silent pass
            ok, row["gate_error"] = False, f"{type(e).__name__}: {e}"
        if gate_mode:
            row["gate_mode"] = gate_mode
        if not ok:
            failures.append(f"{rel}: forward vocabulary does NOT reproduce R0 bytes — content changed beyond pure renames; left untouched")
            rows[rel] = {**row, "gate": "FAIL"}
            continue
        old_hash = hashlib.sha256(orig).hexdigest()
        (REPO / rel).write_bytes(orig)
        own_hash = hashlib.sha256((REPO / rel).read_bytes()).hexdigest()
        assert own_hash == old_hash
        row.update(gate="PASS", restored_sha256=old_hash, bytes=len(orig))
        if rel.endswith(".json"):
            row["self_pins"] = self_pin_report(json.loads(orig), own_hash,
                                               hashlib.sha256(r0b).hexdigest())
        rows[rel] = row
        print(f"[restore] {rel}  preR0={pre} {len(orig)}B sha={old_hash[:12]}")

    n = {k: sum(1 for r in rows.values() if r["class"] == k) for k in ("RESTORE", "LEAVE", "DEFER")}
    restored = [r for r, v in rows.items() if v.get("gate") == "PASS"]
    print(f"\nclassified: RESTORE={n['RESTORE']} (passed-gate+written={len(restored)}) LEAVE={n['LEAVE']} DEFER={n['DEFER']}")
    pins_breaking = [f"{rel}: {p}" for rel, v in rows.items()
                     for p in v.get("self_pins", []) if "would break" in p]
    if pins_breaking:
        print("SELF-PIN WARNINGS (artifact pins its own R0 bytes — restore invalidates):")
        for p in pins_breaking:
            print("  -", p)
        failures += pins_breaking

    out = REPO / "research/orion-epistemic-state-v1/results/R0_BATCH_RESTORE_RECEIPT_V1.json"
    out.write_text(json.dumps({
        "schema": "orion.r0-frozen-artifact-batch-restore-receipt.v1",
        "date": "2026-08-27",
        "r0_commit": R0,
        "method": "layer-3 generalization of the DES-CENSUS-01 byte-restore: forward R0 move "
                  "vocabulary applied to last-pre-R0 bytes must reproduce R0 bytes exactly "
                  "(JSON leaf-wise, text byte-exact) before any write; restore = authored state. "
                  "Fallback gate `guarded-passB` mirrors R0's own pass-B guard (receipt "
                  "rebind.passes: bare basenames guarded against candidates/ and "
                  "2026-08-pre-unification/ contexts); files passing only that gate are "
                  "flagged `gate_mode` in their row",
        "counts": {**n, "gate_passed_and_restored": len(restored)},
        "files": rows,
        "failures": failures,
    }, indent=1, sort_keys=True) + "\n")
    print(f"receipt -> {out.relative_to(REPO)}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures:
            print("  -", f)
        return 1
    print("ALL INVARIANTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
