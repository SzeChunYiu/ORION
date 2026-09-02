#!/usr/bin/env python3
"""Ratchet: no NEW dangling commit pin may enter papers/.

tests/unit/programme/test_content_binding_pin_is_reachable.py already guards this
class, but only over `papers/*/CONTENT_MANIFEST_V2.json`. Every dangling pin found
so far lives somewhere else -- in ALL_25_BOUNDED_SCIENCE_FREEZE_V2.json's
`source_result_commits`, and in V1 manifests -- so the guard has never seen them.

Two failure modes, deliberately distinguished:

  ABSENT      the object does not exist here and the remote refuses it. Nothing can
              re-derive it; a record citing it cannot be checked by anyone.
  OFF_MAIN    the object exists but is not an ancestor of origin/main, so it lives on
              a branch. Resolvable today, gone if that branch is pruned. This is the
              class #1989 repaired and that the freeze anchor itself fell into.

Known entries are carried in a baseline. An entry leaves the baseline by becoming
reachable -- never by being deleted to make this pass.

Exit codes: 0 clean, 2 a new dangling pin, 3 could not check.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "papers/COMMIT_PIN_REACHABILITY_BASELINE_V1.json"
PIN_KEYS = {"subject_commit", "source_result_commit"}
PIN_LIST_KEYS = {"source_result_commits"}
MAX_JSON_BYTES = 3_000_000


def git_ok(*args: str) -> bool:
    return subprocess.run(["/usr/bin/git", *args], cwd=ROOT, capture_output=True).returncode == 0


def collect() -> dict[str, list[str]]:
    """commit -> sorted list of repo-relative files that pin it."""
    found: dict[str, set[str]] = {}

    def walk(node, source: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in PIN_KEYS and isinstance(value, str) and len(value) == 40:
                    found.setdefault(value, set()).add(source)
                elif key in PIN_LIST_KEYS and isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and len(item) == 40:
                            found.setdefault(item, set()).add(source)
                else:
                    walk(value, source)
        elif isinstance(node, list):
            for item in node:
                walk(item, source)

    for path in sorted(ROOT.glob("papers/**/*.json")):
        if path.stat().st_size > MAX_JSON_BYTES:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        walk(payload, path.relative_to(ROOT).as_posix())
    return {commit: sorted(sources) for commit, sources in found.items()}


def classify(commit: str) -> str | None:
    if not git_ok("cat-file", "-e", f"{commit}^{{commit}}"):
        return "ABSENT"
    if not git_ok("merge-base", "--is-ancestor", commit, "origin/main"):
        return "OFF_MAIN"
    return None


def main() -> int:
    if not git_ok("rev-parse", "origin/main"):
        print("CANNOT CHECK: origin/main is not available in this checkout")
        return 3
    if not BASELINE.is_file():
        print(f"CANNOT CHECK: baseline missing at {BASELINE.relative_to(ROOT)}")
        return 3

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    known = {entry["commit"]: entry["state"] for entry in baseline["entries"]}

    pins = collect()
    current = {c: s for c, s in ((c, classify(c)) for c in pins) if s}

    new = sorted(c for c in current if c not in known)
    healed = sorted(c for c in known if c not in current)
    worsened = sorted(c for c in current if c in known and known[c] != current[c])

    print(json.dumps({
        "record": "COMMIT_PIN_REACHABILITY_V1",
        "pins_scanned": len(pins),
        "dangling_now": len(current),
        "baseline_entries": len(known),
        "new": [{"commit": c, "state": current[c], "pinned_by": pins[c]} for c in new],
        "healed": healed,
        "state_changed": [{"commit": c, "was": known[c], "now": current[c]} for c in worsened],
    }, indent=2, sort_keys=True))

    if new or worsened:
        for commit in new:
            print(f"FINDING: new dangling pin {commit[:12]} ({current[commit]}) "
                  f"in {', '.join(pins[commit])}")
        for commit in worsened:
            print(f"FINDING: {commit[:12]} degraded {known[commit]} -> {current[commit]}")
        return 2
    if healed:
        print(f"{len(healed)} baseline entr(y/ies) became reachable; remove them from the "
              f"baseline in the same change that made them reachable: {healed}")
    print(f"no new dangling commit pins ({len(current)} known, {len(pins)} pins scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
