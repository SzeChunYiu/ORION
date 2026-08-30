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
import io
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLOSURE_NAME = "RENDER_INPUT_CLOSURE.json"
STATE_NAME = "RENDER_CLOSURE_STATE.json"
SCHEMA = "orion.journal-package.render-closure-state.v1"

#: Papers whose package ships a PDF but pins no input closure.
#:
#: P3 is one. Its packaged manuscript.pdf is 18 pages against a manuscript that
#: is now 21, and it was already 18 against 19 on the default branch --- so the
#: staleness predates this work and is not something a rewrite introduced. The
#: only place it showed up was a CI step, which means the repository itself could
#: not answer "is this package current?" from anything in the tree.
#:
#: There are no pinned digests to compare, so the evidence is the artifact
#: itself: the packaged PDF against the manuscript PDF the paper now builds,
#: which is the same comparison the CI step makes. Declaring it does not make the
#: CI step pass and is not intended to --- the package still has to be re-rendered
#: before submission. It makes the obligation visible to a reader of the tree
#: instead of only to a reader of a failed job.
_MANUSCRIPT_PDF_NAME = "manuscript.pdf"


def _pdf_pages_and_text(data: bytes) -> tuple[int, str]:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return len(reader.pages), "\n".join(page.extract_text() or "" for page in reader.pages)


def rendered_pdf_state(package: Path) -> dict | None:
    """State for a package that ships a PDF but pins no inputs."""

    packaged = package / _MANUSCRIPT_PDF_NAME
    built = package.parent / "manuscript" / "main.pdf"
    if not packaged.exists() or not built.exists():
        return None

    packaged_pages, packaged_text = _pdf_pages_and_text(packaged.read_bytes())
    built_pages, built_text = _pdf_pages_and_text(built.read_bytes())
    matches = packaged_pages == built_pages and packaged_text == built_text
    return {
        "schema": SCHEMA,
        "package": package.relative_to(REPO_ROOT).as_posix(),
        "state": "CURRENT" if matches else "SUPERSEDED",
        "evidence": "RENDERED_PDF",
        "packaged_pdf_pages": packaged_pages,
        "built_manuscript_pages": built_pages,
        "means": _CURRENT_PDF if matches else _SUPERSEDED_PDF,
    }


_CURRENT_PDF = (
    "the packaged manuscript.pdf has the same page count and extracted text as "
    "the manuscript this paper builds today"
)
_SUPERSEDED_PDF = (
    "the packaged manuscript.pdf is a render of an earlier manuscript; it must "
    "be re-rendered, and its claim-to-PDF audit re-run, before the package is "
    "submitted"
)

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
        "evidence": "PINNED_INPUTS",
        "pinned_input_count": len(closure["files"]),
        "drifted_inputs": drifted,
        "means": _CURRENT if not drifted else _SUPERSEDED,
    }


def derived_states() -> list[tuple[Path, dict]]:
    """Every package that can say whether it is current, and its state."""

    states: list[tuple[Path, dict]] = []
    for closure_path in sorted(REPO_ROOT.glob(f"papers/*/journal_package*/{CLOSURE_NAME}")):
        states.append((closure_path.parent, state_for(closure_path)))
    pinned = {package for package, _ in states}
    for package in sorted(REPO_ROOT.glob("papers/*/journal_package*")):
        if package in pinned:
            continue
        state = rendered_pdf_state(package)
        if state is not None:
            states.append((package, state))
    return states


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if any committed state is stale")
    args = parser.parse_args(argv)

    states = derived_states()
    if not states:
        print("no packages can report a render state", file=sys.stderr)
        return 1

    stale: list[str] = []
    for package, derived in states:
        state_path = package / STATE_NAME
        rendered = json.dumps(derived, indent=2, sort_keys=True) + "\n"
        if args.check:
            committed = state_path.read_text(encoding="utf-8") if state_path.exists() else ""
            if committed != rendered:
                stale.append(derived["package"])
            continue
        state_path.write_text(rendered, encoding="utf-8")
        if derived["evidence"] == "PINNED_INPUTS":
            detail = f"{len(derived['drifted_inputs'])} drifted"
        else:
            detail = (
                f"packaged {derived['packaged_pdf_pages']}pp vs built "
                f"{derived['built_manuscript_pages']}pp"
            )
        print(f"{derived['package']}: {derived['state']} ({detail})")

    if args.check:
        for package in stale:
            print(f"stale render-closure state: {package}", file=sys.stderr)
        return 1 if stale else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
