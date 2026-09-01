"""The ORION-17 sealed-label seal must verify, and must stay reproducible.

A repository-wide rename pass (`3a1a83178`) rewrote three signed path strings and
nine lines of the hash-bound protocol, breaking an Ed25519 seal it had no key to
reissue. The break survived three weeks and a publication-readiness packet before
an audit sweep found it, because nothing in CI looked.

These tests look. See evidence/independent/SEAL_INTEGRITY_NOTE_V1.md.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "papers/orion-17-epistemic-navigation-open-worlds/evidence/independent"
SEALED = EVIDENCE / "P7_SUBSTITUTE_SEALED_LABELS_V1.json"
PROTOCOL = EVIDENCE / "P7_SUBSTITUTE_CAMPAIGN_PROTOCOL_V1.md"
CUSTODIAN = EVIDENCE / "p7_substitute_custodian_v1.py"
CHECKER = EVIDENCE / "check_p7_substitute_campaign_v1.py"

# The stem is a literal in the custodian, a value in the sealed manifest, and a
# documented recipe in the protocol. The rename pass changed exactly one of the
# three, which is the case a reader can least easily detect.
SEED_STEM = "P7-SUBSTITUTE-V1"


def _canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


@pytest.fixture(scope="module")
def sealed() -> dict:
    return json.loads(SEALED.read_text(encoding="utf-8"))


def test_the_sealed_facts_hash_to_the_signed_digest(sealed: dict) -> None:
    """The payload must still be the payload that was signed."""

    recomputed = hashlib.sha256(_canonical(sealed["facts"])).hexdigest()
    assert recomputed == sealed["payload_digest"].removeprefix("sha256:"), (
        "the sealed facts no longer hash to the digest carried beside the signature. "
        "Something edited signed content in place. Do not re-sign; find the edit."
    )


def test_the_manifest_binds_the_protocol_bytes_on_disk(sealed: dict) -> None:
    on_disk = "sha256:" + hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    assert on_disk == sealed["facts"]["protocol_sha256"], (
        "the protocol file has changed since it was sealed. Its bytes are the "
        "binding, not its wording."
    )


def test_the_signed_path_strings_are_the_paths_at_seal_time(sealed: dict) -> None:
    """These are a historical record, not references. PAPER_ALIASES.md is the map."""

    for key in ("protocol_path", "corpus_path", "labels_reveal_path"):
        assert sealed["facts"][key].startswith(
            "papers/paper-07-epistemic-navigation-open-worlds/"
        ), f"{key} was rewritten to the current namespace; that is signed content"
    assert sealed["facts"]["paper_id"] == "P7"


def test_the_seed_stem_agrees_across_code_manifest_and_published_recipe(
    sealed: dict,
) -> None:
    """A protocol that documents a different stem does not reproduce the corpus.

    Code, manifest and seal all agreed after the rename; only the published recipe
    disagreed, so a replicator would have generated a different corpus with nothing
    in the repository explaining the mismatch.
    """

    assert f'SEED_STEM = "{SEED_STEM}"' in CUSTODIAN.read_text(encoding="utf-8")
    assert sealed["facts"]["generator"]["stem"] == SEED_STEM
    assert f'sha256("{SEED_STEM}|' in PROTOCOL.read_text(encoding="utf-8")


def test_the_alias_registry_still_carries_the_mapping() -> None:
    """The historical names above are only navigable because this mapping exists."""

    aliases = (ROOT / "papers/PAPER_ALIASES.md").read_text(encoding="utf-8")
    assert "paper-07-epistemic-navigation-open-worlds" in aliases
    assert "orion-17-epistemic-navigation-open-worlds" in aliases


def test_the_independent_checker_passes_and_still_has_detection_power() -> None:
    """Green alone is not evidence. The self-test proves the checker can fail."""

    passed = subprocess.run(
        [sys.executable, str(CHECKER)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert passed.returncode == 0, passed.stdout
    assert "CHECK PASSED" in passed.stdout

    selftest = subprocess.run(
        [sys.executable, str(CHECKER), "--self-test"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert selftest.returncode == 0, selftest.stdout
    assert "SELF-TEST PASSED" in selftest.stdout
    # Six targeted mutations; a checker that catches fewer has lost coverage.
    assert selftest.stdout.count("caught") == 6, selftest.stdout
