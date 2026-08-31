"""Every content-binding pin must name a commit reachable from HEAD.

`_subject_identity` resolves each bound file with `git show <subject_commit>:<path>`.
If `subject_commit` is not an ancestor of HEAD, that resolution fails and every bound
file silently degrades to PARTIAL.

This is not hypothetical. All four V2-manifest papers carried dangling pins
simultaneously, because `scripts/regen_paper_manifests.py` takes the pin from
`git rev-parse HEAD` while this repository squash-merges: the branch commit never
lands. It cost five CI failures whose cause was invisible locally, since the dead
commit still exists in the authoring clone.

The check is deliberately "ancestor of HEAD" rather than "ancestor of origin/main".
On a feature branch a freshly written pin is an ancestor of HEAD and passes; after a
squash merge the branch commit is not an ancestor of main and this fails -- which is
exactly where the defect becomes real.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
MANIFESTS = sorted(ROOT.glob("papers/*/CONTENT_MANIFEST_V2.json"))


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )


def test_there_are_v2_manifests_to_check() -> None:
    """Guard against this suite silently passing because it found nothing."""
    assert MANIFESTS, "no CONTENT_MANIFEST_V2.json found; this test would be vacuous"


@pytest.mark.parametrize("manifest", MANIFESTS, ids=lambda p: p.parent.name)
def test_subject_commit_is_reachable_from_head(manifest: Path) -> None:
    pin = json.loads(manifest.read_text()).get("subject_commit")
    if not pin or pin == "UNBOUND":
        pytest.skip(f"{manifest.parent.name} has no bound subject_commit")

    exists = _git("cat-file", "-e", f"{pin}^{{commit}}")
    if exists.returncode != 0:
        pytest.skip(
            f"{pin[:12]} is not present in this clone (shallow checkout); "
            "reachability cannot be decided here"
        )

    reachable = _git("merge-base", "--is-ancestor", pin, "HEAD")
    assert reachable.returncode == 0, (
        f"{manifest.parent.name}: subject_commit {pin[:12]} is not an ancestor of HEAD.\n"
        "Every bound file will fail `git show <commit>:<path>` and degrade to PARTIAL.\n"
        "Re-pin to a commit that is already on main and contains the bound bytes, then "
        "rebind the manifest digest in the same commit."
    )
