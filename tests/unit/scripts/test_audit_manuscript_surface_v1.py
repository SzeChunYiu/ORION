"""The surface audit must fire on planted defects and stay quiet on the baseline.

The audit's own `--self-test` is the first line of defence, but a self-test the
suite never runs is no better than the two earlier scanners that reported these
manuscripts clean. These tests exercise it, and additionally require the audit to
find the *real* ORION-18 defect in the manuscript that still carries it.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "scripts/audit_manuscript_surface_v1.py"
UNFIXED = ROOT / "papers/orion-18-epistemic-authority-autonomous-science/manuscript/FINAL_V4.md"
FIXED = ROOT / "papers/orion-18-epistemic-authority-autonomous-science/manuscript/FINAL_V5.md"


def _load():
    spec = importlib.util.spec_from_file_location("_surface_audit", AUDIT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return _load()


def test_self_test_passes(mod):
    """If this fails, every clean verdict the audit gives is meaningless."""
    assert mod.main(["--self-test-only"]) == 0


def test_the_real_unfixed_manuscript_still_fires(mod):
    """FINAL_V4 carries the state-count conflict FINAL_V5 corrects."""
    if not UNFIXED.is_file():
        pytest.skip("FINAL_V4 is not present in this tree")
    findings = mod.audit(UNFIXED)
    conflicts = [f for f in findings if f["kind"] == "number_conflict"]
    assert any(
        set(f["values"]) == {"3,072", "39,936"} for f in conflicts
    ), "the audit no longer detects the ORION-18 state-count conflict"
    assert any(f["kind"] == "repeated_sentence" for f in findings)


def test_the_corrected_manuscript_has_no_repeated_sentence(mod):
    if not FIXED.is_file():
        pytest.skip("FINAL_V5 is not present in this tree")
    findings = mod.audit(FIXED)
    assert not [f for f in findings if f["kind"] == "repeated_sentence"]


def test_hard_wrapping_does_not_hide_a_sentence_boundary(mod):
    """The bug that made two earlier scanners report a duplicate file clean."""
    wrapped = (
        "The claim is that adaptive inference is crowded and the novel discriminator\n"
        "must be where the resource can be spent under one matched budget.\n"
        "The claim is that adaptive inference is crowded and the novel discriminator "
        "must be where the resource can be spent under one matched budget.\n"
    )
    assert mod.repeated_sentences(wrapped), "hard wrapping still hides the boundary"


def test_markdown_emphasis_does_not_hide_a_sentence_boundary(mod):
    """`...spent.**` puts no whitespace after the period."""
    # Both sentences must clear MIN_SENTENCE, or an empty result is correct
    # rather than a bug -- which is what a first version of this test asserted.
    body = (
        "The novel discriminator must be where the resource can be spent under one "
        "matched total budget"
    )
    emphasised = f"{body}.** {body} again, stated a second time.\n"
    found = mod.sentences(emphasised)
    assert len(found) == 2, (
        f"emphasis still hides the boundary: got {len(found)} sentence(s)"
    )


def test_number_conflict_survives_a_leading_adjective_or_trailing_verb(mod):
    """The bug that made the first key scheme miss the planted conflict."""
    text = (
        "The model exhausts 39,936 authority states replayed thirteen times over here.\n"
        "The model covers 3,072 distinct exact authority states in the frozen family.\n"
    )
    conflicts = mod.conflicting_numbers(text)
    assert any(set(c["values"]) == {"3,072", "39,936"} for c in conflicts)


def test_baseline_carries_a_judged_reason_for_every_entry(mod):
    """No entry may be suppressed without a stated reason."""
    if not mod.BASELINE.is_file():
        pytest.skip("no baseline committed")
    data = json.loads(mod.BASELINE.read_text(encoding="utf-8"))
    for key, reason in data["entries"].items():
        assert reason and "UNREVIEWED" not in reason, f"{key} was baselined unjudged"


def test_repository_is_clean_against_the_baseline(mod):
    """Exit 0 means: no finding outside the baseline, and none stale."""
    if not mod.BASELINE.is_file():
        pytest.skip("no baseline committed")
    assert mod.main([]) == 0


def test_a_planted_defect_reds_the_gate(mod, tmp_path):
    """The gate must red on a NEW finding, not merely report it."""
    planted = tmp_path / "planted.md"
    planted.write_text(
        "# Planted\n\n"
        "This sentence is long enough to be treated as substantive prose by the audit.\n\n"
        "This sentence is long enough to be treated as substantive prose by the audit.\n",
        encoding="utf-8",
    )
    assert mod.main([str(planted)]) == 2
