"""The `INSUFFICIENT_EVIDENCE` cases hand the candidate their answer.

P4's H3 asks whether ORION is better at correctly selecting `CANNOT_CHECK`. It
came back with `correct_cannot_check_rate` at 1.0 for all eleven panel systems --
no variance anywhere in the study.

The manifest supplies a mechanical explanation. All three `INSUFFICIENT_EVIDENCE`
cases end their candidate-visible evidence with a sentence naming the verdict:

    ... n=5. No confidence intervals reported. The study does not control for
    model size, training data, or evaluation methodology. The evidence is
    genuinely insufficient to support the comparative claim.

No case in the other twelve families does this. The contrast is instructive rather
than accidental: `POOLED_SUPPORT_WRONG_OWNER` cases also turn on insufficient
support and describe it structurally -- "the pooled evidence only demonstrates
refusal direction, not general steering" -- leaving the verdict to be inferred.

A system can score the leaking cases by reading. The facts preceding that sentence
(n=5, no confidence intervals, no controls) already determine the answer, so
removing it costs the case nothing and restores the inference.

These tests pin the finding and, more importantly, pin the detector's precision.
A leak checker that also fires on "no confidence intervals reported" would
condemn every well-built case, get switched off, and take the real finding with
it.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P4 = ROOT / "papers" / "orion-14-verified-scientific-discovery"
CHECKER = P4 / "protocol" / "check_verdict_leak_v1.py"
MANIFEST = P4 / "protocol" / "ATTACK_MANIFEST_V1.jsonl"


def _checker():
    spec = importlib.util.spec_from_file_location("verdict_leak", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _cases() -> list[dict]:
    return [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_the_leak_is_confined_to_the_family_that_sets_h3() -> None:
    """The finding itself, stated as a measurement rather than an impression."""

    checker = _checker()
    leaking = {c["attack_family"] for c in _cases() if checker.leaks_in(c)}
    assert leaking == {"INSUFFICIENT_EVIDENCE"}, (
        f"expected the verdict leak to be confined to INSUFFICIENT_EVIDENCE, found "
        f"{sorted(leaking)}. If it has spread, more families have stopped requiring "
        f"inference; if it has cleared, this test and the P4 limitation need updating."
    )
    insufficient = [c for c in _cases() if c["attack_family"] == "INSUFFICIENT_EVIDENCE"]
    assert insufficient, "the INSUFFICIENT_EVIDENCE family disappeared"
    assert all(checker.leaks_in(c) for c in insufficient), (
        "some INSUFFICIENT_EVIDENCE cases no longer state their verdict -- good, but "
        "the H3 limitation text now overstates the defect and must be updated"
    )


def test_the_detector_does_not_fire_on_ordinary_evidential_facts() -> None:
    """Precision, which is what decides whether this checker survives contact.

    Every phrase below is a fact a reader must weigh, and is exactly what a
    well-built insufficient-evidence case should contain. A detector that flagged
    them would condemn good cases and be switched off.
    """

    checker = _checker()
    innocuous = [
        "The study reports n=5 with high variance and no confidence intervals.",
        "The work is a preprint with no peer review.",
        "Tasks are not the same and evaluation metrics differ.",
        "No statistical significance tests are reported.",
        "The study does not control for model size or training data.",
        "The pooled evidence only demonstrates refusal direction, not general steering.",
        "Shows robustness to corruptions, not adversarial attacks.",
    ]
    for text in innocuous:
        case = {"candidate_visible": {"evidence_text": text}}
        assert checker.leaks_in(case) == [], f"false positive on evidential fact: {text!r}"


def test_the_detector_fires_on_a_stated_verdict() -> None:
    """Non-vacuity: it must catch the thing it exists for."""

    checker = _checker()
    for text in (
        "The evidence is genuinely insufficient to support the comparative claim.",
        "The evidence is insufficient to support the sweeping claim.",
        "This claim cannot be verified from the material provided.",
        "The source directly supports the claim in full.",
    ):
        case = {"candidate_visible": {"evidence_text": text}}
        assert checker.leaks_in(case), f"missed a stated verdict: {text!r}"


def test_removing_only_the_verdict_sentence_would_clear_the_case() -> None:
    """The fix is subtractive, and this shows it costs the case nothing.

    Each leaking case states its facts first and names the verdict last. Dropping
    the final sentence leaves the evidential content intact and the case clean, so
    the repair does not require inventing new material or changing a gold label.
    """

    checker = _checker()
    for case in _cases():
        if case["attack_family"] != "INSUFFICIENT_EVIDENCE":
            continue
        evidence = case["candidate_visible"]["evidence_text"]
        sentences = [s.strip() for s in evidence.split(".") if s.strip()]
        assert len(sentences) > 1, f"{case['case_id']} is a single sentence; cannot subtract"
        trimmed = ". ".join(sentences[:-1]) + "."
        probe = {"candidate_visible": {"evidence_text": trimmed}}
        assert checker.leaks_in(probe) == [], (
            f"{case['case_id']}: dropping the last sentence does not clear the leak, so "
            f"the verdict is stated earlier too and the repair needs rewriting, not trimming"
        )
        assert len(trimmed) > 60, (
            f"{case['case_id']}: what remains after trimming is too thin to judge from"
        )
