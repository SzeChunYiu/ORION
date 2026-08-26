"""What the P4 manuscript says about saturation must stay true of the metrics.

P4 reports three hypotheses. H1 (false authority promotion) is a measurement: the
rate takes six distinct values across the eleven-system panel. H2 (clean coverage)
and H3 (correct `CANNOT_CHECK`) are not, because both quantities sit at 1.0 for
every system in the panel, and for every ablation that measures them.

That distinction is easy to lose. "H3 not supported" reads as a comparative
finding -- we looked for an advantage and there wasn't one -- when what actually
happened is that the instrument had no resolving power: a difference could not
have been observed had one existed. The manuscript now says so, and these tests
keep the claim and the data in step.

They are deliberately two-sided. If a future battery gives H2 or H3 real headroom,
the saturation language becomes false and must be removed; that is a failure here,
not a silent inconsistency. And if H1's headroom ever collapses, the paper's one
real axis has gone with it, which is worth failing loudly for.
"""

from __future__ import annotations

import json
from pathlib import Path

from orion.publication.manuscript_source import assemble

ROOT = Path(__file__).resolve().parents[3]
P4 = ROOT / "papers" / "orion-14-verified-scientific-discovery"
METRICS = P4 / "evidence" / "protected_v2" / "PUBLICATION_METRICS_V2.json"
MANUSCRIPT = P4 / "manuscript" / "main.tex"


def _manuscript_text() -> str:
    """The document LaTeX builds, not just its entry file.

    ``main.tex`` is a preamble and eleven ``\\input`` lines since the split, so
    reading it alone would find neither the phrases these tests require nor the
    ones they forbid, and would pass on both counts without checking anything.
    """

    return assemble(MANUSCRIPT)

SATURATED = ("clean_coverage", "correct_cannot_check_rate")
DISCRIMINATING = "false_promotion_rate"


def _metrics() -> dict:
    return json.loads(METRICS.read_text(encoding="utf-8"))


def test_the_discriminating_axis_still_discriminates() -> None:
    """H1 rests entirely on this one axis, so its headroom is load-bearing."""

    systems = _metrics()["systems"]
    values = {s[DISCRIMINATING] for s in systems.values() if DISCRIMINATING in s}
    assert len(values) > 1, (
        f"{DISCRIMINATING} no longer varies across the panel; H1 would then rest on an "
        f"axis with no resolving power, exactly as H2 and H3 already do"
    )
    assert systems["ORION"][DISCRIMINATING] == 0.0, (
        "ORION's false promotion rate is no longer 0/360; the headline claim moved"
    )


def test_the_saturated_axes_are_still_saturated() -> None:
    """The claim the manuscript now makes, checked against the data it cites.

    If this fails because a metric gained headroom, that is good news for the
    science and bad news for the text: the limitation paragraph has to go.
    """

    systems = _metrics()["systems"]
    assert len(systems) == 11, f"panel size changed to {len(systems)}; recheck the claim"
    for field in SATURATED:
        values = {s[field] for s in systems.values() if field in s}
        assert values == {1.0}, (
            f"{field} now takes values {sorted(values)} across the panel. The manuscript "
            f"states it is 1.0 for all eleven systems and calls H2/H3 design limits; that "
            f"text is now wrong and must be updated with the new result."
        )


def test_the_ablations_agree_about_where_the_headroom_is() -> None:
    ablations = _metrics()["ablations"]
    assert ablations, "ablations disappeared"
    rates = {a[DISCRIMINATING] for a in ablations.values() if DISCRIMINATING in a}
    assert len(rates) > 1, "ablations no longer separate on false promotion"
    coverage = {a["clean_coverage"] for a in ablations.values() if "clean_coverage" in a}
    assert coverage == {1.0}, (
        f"clean_coverage now varies across ablations ({sorted(coverage)}); the manuscript "
        f"claims it is 1.0 for all eight"
    )
    # Recorded as a fact, not asserted as desirable: the ablations never measure
    # correct_cannot_check_rate, which is half of why H3 has no evidence anywhere.
    measured = {key for a in ablations.values() for key in a}
    assert "correct_cannot_check_rate" not in measured, (
        "the ablations now measure correct_cannot_check_rate. That is an improvement, and "
        "the manuscript sentence saying they do not must be updated."
    )


def test_the_manuscript_states_the_limitation_it_now_relies_on() -> None:
    """Guard the text, so the finding cannot be quietly dropped in an edit."""

    text = _manuscript_text()
    assert "saturates" in text, "the saturation limitation is gone from the manuscript"
    assert "resolving power" in text, (
        "the H3 passage no longer explains that the comparison could not have detected a "
        "difference; without it, 'not supported' reads as a comparative finding"
    )
    # Matched on the distinction rather than one phrasing of it: the passage has been
    # reworded once already ("not as" -> "rather than as"), and a test that breaks on
    # that is testing prose style, not the claim.
    assert "evidence that no difference exists" in text, (
        "the H3 passage no longer distinguishes inability to discriminate from absence of "
        "an effect"
    )
    assert "empty" in text and "420" in text, (
        "the H3 passage no longer states the measured cause -- the empty-evidence "
        "construction that makes the terminal trivially separable across all 420 cases"
    )
