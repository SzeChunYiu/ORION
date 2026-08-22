#!/usr/bin/env python3
"""Re-derive each journal package's RENDER_CLOSURE_STATE.json from the tree.

``RENDER_INPUT_CLOSURE.json`` pins the inputs that produced a package's
``manuscript.pdf``. Nothing compared those digests to the repository, so editing
a manuscript afterwards left a package whose PDF renders something that no longer
exists, with nothing in the package saying so.

``RENDER_CLOSURE_STATE.json`` is that missing statement, and this regenerates it.
It is deliberately a generator with a committed output and a ``--check`` mode
rather than a file anyone maintains by hand: a declaration of freshness that a
human has to remember to update is the thing it exists to replace.

``CURRENT`` means every pinned input still hashes to its pinned value.
``SUPERSEDED`` means at least one has moved, so the PDF is a faithful record of
an earlier manuscript and the package must be re-rendered before submission.
That is a true statement about a package, not a defect in it; what is refused,
by ``tests/test_journal_package_render_closure.py``, is a package that has
drifted and still says it is current.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLOSURE_NAME = "RENDER_INPUT_CLOSURE.json"
STATE_NAME = "RENDER_CLOSURE_STATE.json"
SCHEMA = "orion.journal-package.render-closure-state.v1"

_CURRENT = (
    "manuscript.pdf is a render of the inputs RENDER_INPUT_CLOSURE.json pins, "
    "and every one of them still has the pinned bytes"
)
_SUPERSEDED = (
    "manuscript.pdf is a render of inputs that have since changed; it is a "
    "faithful record of an earlier manuscript, not of the current one, and "
    "the package must be re-rendered before it is submitted"
)


def drifted_inputs(closure: dict) -> list[str]:
    drifted = []
    for entry in closure["files"]:
        path = REPO_ROOT / entry["path"]
        if not path.exists():
            drifted.append(entry["path"])
        elif hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            drifted.append(entry["path"])
    return sorted(drifted)


def state_for(closure_path: Path) -> dict:
    closure = json.loads(closure_path.read_text(encoding="utf-8"))
    drifted = drifted_inputs(closure)
    package = closure_path.parent.relative_to(REPO_ROOT).as_posix()
    return {
        "schema": SCHEMA,
        "package": package,
        "state": "CURRENT" if not drifted else "SUPERSEDED",
        "pinned_input_count": len(closure["files"]),
        "drifted_inputs": drifted,
        "means": _CURRENT if not drifted else _SUPERSEDED,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if any committed state is stale")
    args = parser.parse_args(argv)

    closures = sorted(REPO_ROOT.glob(f"papers/*/journal_package/{CLOSURE_NAME}"))
    if not closures:
        print("no render closures found", file=sys.stderr)
        return 1

    stale: list[str] = []
    for closure_path in closures:
        derived = state_for(closure_path)
        state_path = closure_path.parent / STATE_NAME
        rendered = json.dumps(derived, indent=2, sort_keys=True) + "\n"
        if args.check:
            committed = state_path.read_text(encoding="utf-8") if state_path.exists() else ""
            if committed != rendered:
                stale.append(derived["package"])
            continue
        state_path.write_text(rendered, encoding="utf-8")
        print(f"{derived['package']}: {derived['state']} ({len(derived['drifted_inputs'])} drifted)")

    if args.check:
        for package in stale:
            print(f"stale render-closure state: {package}", file=sys.stderr)
        return 1 if stale else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
