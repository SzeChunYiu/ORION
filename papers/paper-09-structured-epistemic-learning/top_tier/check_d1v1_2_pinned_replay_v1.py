#!/usr/bin/env python3
"""Binding checker for the P9 D1 v1.2 pinned-replay increment (issue #1086).

Verifies, from the committed artifacts alone (no execution of the replay):

1. R1/R2 receipts are two clean replays: identical deterministic cores, honestly
   computed identical result digests, ARCHIVE_MATCH attractor, per-case equality
   with the archived result on all four arms.
2. The binary-build toggle receipt is internally consistent: bit-identical design
   digests across sides, identical scipy/scikit-learn versions, the same frozen
   selection rule and selected config, side A = 0.50 with zero flips, side B =
   0.75 with exactly the 32 UNRESOLVED-truth knife-edge cases flipped, side C an
   independent same-version env with a bit-identical canary to side B.
3. The numeric-canary constants are duplicated identically in the two executable
   scripts (mechanized duplication, not trust).
4. History is append-only: the locked-environment failure receipt still carries
   P9_D1V1_2_LOCKED_ENV_REPRODUCTION_FAILED, and the two pre-existing historical
   files are byte-anchored to the values they had before this increment.
5. SHA256SUMS binds every listed file to its bytes on disk.

Exit codes: 0 all checks pass; 1 any check fails; 3 CANNOT_CHECK (artifacts
missing).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
REPO = PAPER.parents[1]

EVIDENCE = PAPER / "evidence"
TOGGLE = EVIDENCE / "P9_D1V1_2_BINARY_BUILD_TOGGLE_2026-08-24.json"
R1 = EVIDENCE / "P9_D1V1_2_PINNED_REPLAY_R1_2026-08-24.json"
R2 = EVIDENCE / "P9_D1V1_2_PINNED_REPLAY_R2_2026-08-24.json"
REPLAY_SCRIPT = PAPER / "top_tier/replay_d1v1_2_pinned.py"
TOGGLE_SCRIPT = PAPER / "top_tier/demonstrate_d1v1_2_build_toggle.py"
SHA256SUMS = PAPER / "SHA256SUMS"
ARCHIVED_RESULT = REPO / "research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json"
LOCKED_ENV_RECEIPT = EVIDENCE / "P9_D1V1_2_LOCKED_ENV_REPRODUCTION_2026-08-23.json"

# Byte anchors for pre-existing historical files, computed from the files as
# they stood on origin/main before this increment (re-derivable from git
# history; recorded here so tampering is detected without executing anything).
HISTORICAL_FILE_ANCHORS = {
    str(ARCHIVED_RESULT.relative_to(REPO)): (
        "bdd23c39d419aac3c8df7e8cd5c675c572e4cafb1cb8cc7d666522c265babc4a"
    ),
    str(LOCKED_ENV_RECEIPT.relative_to(REPO)): (
        "5022889c95dc97d6fc499b6d7d1eab6a29533245c949dc7c2d708d8722c8f377"
    ),
}

ARCHIVE_MATCH_COEF = "494186ed594e077904dea4adbd75dbf8104496825e4cdf18d7e075316ecaf3de"
ARCHIVE_MATCH_INTERCEPT = "af3a6c166e56cceb9cef6caed28776cf949f022049c180051774fb5c75711d1e"
DIVERGENT_PREFIX = "9b56df6a102b9b57"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(core: dict) -> str:
    blob = json.dumps(core, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main() -> int:
    failures: list[str] = []

    for path in (TOGGLE, R1, R2, REPLAY_SCRIPT, TOGGLE_SCRIPT, SHA256SUMS):
        if not path.is_file():
            print(json.dumps({"status": "CANNOT_CHECK", "missing": str(path)}))
            return 3

    r1 = json.loads(R1.read_text(encoding="utf-8"))
    r2 = json.loads(R2.read_text(encoding="utf-8"))
    toggle = json.loads(TOGGLE.read_text(encoding="utf-8"))
    replay_src = REPLAY_SCRIPT.read_text(encoding="utf-8")
    toggle_src = TOGGLE_SCRIPT.read_text(encoding="utf-8")
    archived = json.loads(ARCHIVED_RESULT.read_text(encoding="utf-8"))

    # --- 1. Two clean replays -------------------------------------------------
    if r1["core"] != r2["core"]:
        failures.append("R1/R2 deterministic cores differ")
    if r1["result_digest"] != r2["result_digest"]:
        failures.append("R1/R2 result digests differ")
    for tag, r in (("R1", r1), ("R2", r2)):
        if canonical_digest(r["core"]) != r["result_digest"]:
            failures.append(f"{tag} result_digest is not the honest digest of its core")
        if r["core"]["observed_attractor"] != "ARCHIVE_MATCH":
            failures.append(f"{tag} attractor is not ARCHIVE_MATCH")
        if not all(r["core"]["per_arm_archive_match"].values()):
            failures.append(f"{tag} does not per-case match the archive on all four arms")
        if r["serialized_arm_summary"]["knife_edge_cases"] != 32:
            failures.append(f"{tag} knife-edge band is not the historical 32")
        canary = r["core"]["numeric_canary"]
        if canary["coef_sha256"] != ARCHIVE_MATCH_COEF or canary["intercept_sha256"] != ARCHIVE_MATCH_INTERCEPT:
            failures.append(f"{tag} numeric canary is not the archive-matching canary")

    # Per-case equality with the archive, recomputed here rather than trusted.
    for family_value, arm in r1["core"]["arms"].items():
        arch_pred = {
            p["instance_id"]: p["prediction"]
            for p in archived["results"][family_value]["test_predictions"]
        }
        if len(arch_pred) != 128 or len(arm["predictions"]) != 128:
            failures.append(f"{family_value} per-case record is not 128 rows")
            continue
        for p in arm["predictions"]:
            if arch_pred.get(p["instance_id"]) != p["prediction"]:
                failures.append(f"{family_value} per-case mismatch vs archive at {p['instance_id']}")
                break

    # --- 2. Toggle receipt internal consistency -------------------------------
    sides = toggle["sides"]
    a, b, c = sides["A_archive_matching"], sides["B_divergent"], sides["C_divergent_independent_env"]
    for key, val in toggle["cross_side_invariants"].items():
        if isinstance(val, bool) and not val:
            failures.append(f"toggle cross-side invariant false: {key}")
    if a["test_accuracy"] != 0.5 or a["flips_vs_archive"]["count"] != 0:
        failures.append("toggle side A is not the 0.50 zero-flip archive match")
    if b["test_accuracy"] != 0.75 or b["flips_vs_archive"]["count"] != 32:
        failures.append("toggle side B is not the 0.75 32-flip divergent side")
    if b["flips_vs_archive"]["targets"] != ["UNRESOLVED"]:
        failures.append("toggle side B flips are not all UNRESOLVED-truth cases")
    if a["numeric_canary"]["n_iter"] != 480 or b["numeric_canary"]["n_iter"] != 439:
        failures.append("toggle sides do not record the distinct lbfgs iteration counts")
    if b["numeric_canary"] != c["numeric_canary"]:
        failures.append("independent same-version envs do not share a bit-identical canary")
    if a["numeric_canary"]["coef_sha256"] != ARCHIVE_MATCH_COEF:
        failures.append("toggle side A canary is not the archive-matching canary")
    if not b["numeric_canary"]["coef_sha256"].startswith(DIVERGENT_PREFIX):
        failures.append("toggle side B canary does not match the divergent prefix")
    for name, s in (("A", a), ("B", b), ("C", c)):
        if s["within_build_determinism"]["max_abs_coef_delta"] != 0.0:
            failures.append(f"toggle side {name} is not deterministic within build")
        if s["convergence_warnings_on_selected"]:
            failures.append(f"toggle side {name} reported convergence warnings")
        if s["margins"]["n_below"] != 32:
            failures.append(f"toggle side {name} knife-edge band is not 32")
    # The pinned replays and toggle side A must be the same build class.
    if r1["core"]["numeric_canary"] != a["numeric_canary"]:
        failures.append("R1 canary differs from toggle side A canary")

    # --- 3. Mechanized constant duplication -----------------------------------
    for const in (ARCHIVE_MATCH_COEF, ARCHIVE_MATCH_INTERCEPT, DIVERGENT_PREFIX):
        if const not in replay_src:
            failures.append(f"pinned replay script lost the constant {const[:16]}...")
        if const not in toggle_src:
            failures.append(f"toggle script lost the constant {const[:16]}...")

    # --- 4. Append-only history ------------------------------------------------
    locked = json.loads(LOCKED_ENV_RECEIPT.read_text(encoding="utf-8"))
    locked_text = json.dumps(locked)
    if "P9_D1V1_2_LOCKED_ENV_REPRODUCTION_FAILED" not in locked_text:
        failures.append("historical locked-environment terminal was rewritten")
    for rel, anchor in HISTORICAL_FILE_ANCHORS.items():
        observed = sha256_file(REPO / rel)
        if observed != anchor:
            failures.append(f"historical file byte-anchor mismatch: {rel}")

    # --- 5. SHA256SUMS binding -------------------------------------------------
    n_sum = 0
    for line in SHA256SUMS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, _, rel = line.partition("  ")
        target = REPO / rel
        if not target.is_file():
            failures.append(f"SHA256SUMS lists missing file {rel}")
            continue
        if sha256_file(target) != digest:
            failures.append(f"SHA256SUMS hash mismatch for {rel}")
        n_sum += 1
    expected_bound = {
        "papers/paper-09-structured-epistemic-learning/top_tier/replay_d1v1_2_pinned.py",
        "papers/paper-09-structured-epistemic-learning/top_tier/demonstrate_d1v1_2_build_toggle.py",
        "papers/paper-09-structured-epistemic-learning/top_tier/check_d1v1_2_pinned_replay_v1.py",
        "papers/paper-09-structured-epistemic-learning/evidence/P9_D1V1_2_BINARY_BUILD_TOGGLE_2026-08-24.json",
        "papers/paper-09-structured-epistemic-learning/evidence/P9_D1V1_2_PINNED_REPLAY_R1_2026-08-24.json",
        "papers/paper-09-structured-epistemic-learning/evidence/P9_D1V1_2_PINNED_REPLAY_R2_2026-08-24.json",
    }
    listed = {
        line.strip().partition("  ")[2]
        for line in SHA256SUMS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    for path in expected_bound:
        if path not in listed:
            failures.append(f"SHA256SUMS does not bind {path}")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "checks_run": {
            "r1_r2_identity": True,
            "digest_honesty": True,
            "archive_per_case_all_four_arms": True,
            "toggle_internal_consistency": True,
            "constant_duplication_binding": True,
            "append_only_history": True,
            "sha256sums_files_verified": n_sum,
        },
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
