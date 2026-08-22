"""A packaged PDF must not silently become a render of a manuscript that changed.

``journal_package/RENDER_INPUT_CLOSURE.json`` pins every input that produced
``manuscript.pdf``: path, byte length and sha256. That is a good record of one
render, and it is exactly the wrong shape for noticing the next edit --- nothing
compares those digests to the tree, so editing the manuscript afterwards leaves a
package whose PDF is a faithful render of something that no longer exists, and
whose own files give no sign of it. Ask the package "are you current?" and it
answers with the same silence whether it is or not.

So each package declares its state, and the declaration is checked against the
bytes. ``CURRENT`` means every pinned input still hashes to its pinned value.
``SUPERSEDED`` means at least one has moved, the PDF records an earlier
manuscript, and the package must be re-rendered before submission --- which is
a true statement about a package, not a defect in it. What is refused is a
package that has drifted and still says it is current, and equally a package
re-rendered without updating what it says. Both directions fail here.

This is deliberately not folded into ``check_journal_package.py``. That checker
derives what to hash from the manifest's own ``required_files``, so it is
answering "is the package internally consistent"; this asks whether the package
still matches the repository it was cut from, which is a different question with
a different answer.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CLOSURES = sorted(ROOT.glob("papers/*/journal_package/RENDER_INPUT_CLOSURE.json"))
STATE_NAME = "RENDER_CLOSURE_STATE.json"


def _drifted(closure: dict) -> list[str]:
    drifted = []
    for entry in closure["files"]:
        path = ROOT / entry["path"]
        if not path.exists():
            drifted.append(entry["path"])
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            drifted.append(entry["path"])
    return sorted(drifted)


def test_there_is_something_to_check() -> None:
    assert CLOSURES, "no render closures found; this file would pass on an empty set"


@pytest.mark.parametrize("closure_path", CLOSURES, ids=lambda p: p.parent.parent.name)
def test_a_package_declares_whether_its_pdf_still_matches_the_tree(closure_path: Path) -> None:
    closure = json.loads(closure_path.read_text(encoding="utf-8"))
    assert closure["files"], f"{closure_path} pins nothing, so it can observe nothing"

    state_path = closure_path.parent / STATE_NAME
    assert state_path.exists(), (
        f"{closure_path.parent} pins render inputs but does not say whether they still "
        f"hold; add {STATE_NAME}"
    )
    state = json.loads(state_path.read_text(encoding="utf-8"))

    drifted = _drifted(closure)
    expected = "CURRENT" if not drifted else "SUPERSEDED"
    assert state["state"] == expected, (
        f"{closure_path.parent.parent.name} declares {state['state']} but "
        f"{len(drifted)} of {len(closure['files'])} pinned inputs measure as "
        f"{expected}: {drifted[:5]}"
    )
    assert state["pinned_input_count"] == len(closure["files"])
    assert sorted(state["drifted_inputs"]) == drifted, (
        "a superseded package must name every input that moved, or a reader cannot "
        "tell which part of the PDF is out of date"
    )


def test_the_drift_detector_reports_both_verdicts() -> None:
    """A detector that cannot say SUPERSEDED would pass every package forever.

    Asserted against the detector rather than against today's packages: pinning
    the repository to "one package must be stale" would make re-rendering P2
    break this file, which is the wrong incentive entirely.
    """

    real = ROOT / "README.md"
    true_digest = hashlib.sha256(real.read_bytes()).hexdigest()
    entry = {"path": "README.md", "bytes": real.stat().st_size}

    assert _drifted({"files": [{**entry, "sha256": true_digest}]}) == []
    assert _drifted({"files": [{**entry, "sha256": "0" * 64}]}) == ["README.md"]
    assert _drifted({"files": [{"path": "no/such/file", "sha256": "0" * 64}]}) == [
        "no/such/file"
    ]
