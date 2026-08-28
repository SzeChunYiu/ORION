"""P4's H3 claim must read on the measurement that could have come out either way.

Until 2026-08-22 ``journal_package/MANIFEST.json`` published H3 as
``NOT_SUPPORTED`` on ``evidence/protected_v2/PUBLICATION_METRICS_V2.json``. That
negative was not a finding about the systems.
``evidence/audit/P4_PANEL_RESOLUTION_2026-08-22.json`` records why: the metric it
was decided on, ``correct_cannot_check_rate``, is 1.0 for all eleven systems, so
the declared interval is [0.0, 0.0] and ``verdict_could_have_differed`` is false.
A guard no system in the panel can fail has not been failed either.

The replacement measurement is ``evidence/protected_v3/``, promoted into the
paper from ``research/campaigns/2026-08-21-p4-battery-v3-identifiable/`` so that
the paper's own content binding covers the bytes a claim rests on. These tests
hold four things together, because any one of them alone is quotable and wrong:

* the axis moves on the V3 battery (headroom),
* the register says the movement is not a construction cue (licence to quote),
* **both** margins are stated --- 1.0 against the H1-selected comparator and 0.5
  against ``deepsciverify``, which scores 15/30 --- everywhere the result is
  reported, and
* the V2 record survives unedited and still reads as an instrument with no
  resolving power.

The fourth is not decoration. ``research/campaigns/.../RESULT.md`` is explicit
that nothing about V3 licenses restating V2's number, so a change that improved
the new claim by quietly rewriting the old one would be the defect, not the fix.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.publication.manuscript_source import assemble

ROOT = Path(__file__).resolve().parents[3]
P4 = ROOT / "papers" / "orion-14-verified-scientific-discovery"
CAMPAIGN = ROOT / "research" / "campaigns" / "2026-08-21-p4-battery-v3-identifiable"

MANIFEST = P4 / "journal_package" / "MANIFEST.json"
SUMS = P4 / "journal_package" / "SHA256SUMS"
V3 = P4 / "evidence" / "protected_v3"
V2_METRICS = P4 / "evidence" / "protected_v2" / "PUBLICATION_METRICS_V2.json"
PANEL_AUDIT = P4 / "evidence" / "audit" / "P4_PANEL_RESOLUTION_2026-08-22.json"
CLAIM_AXIS_AUDIT = (
    "evidence/audit/P4_H3_V3_CLAIM_AXIS_ADJUDICATION_2026-08-22.json"
)
MANUSCRIPT = P4 / "manuscript" / "main.tex"

PROMOTED = ("FREEZE.md", "RESULT.md", "PANEL_V3.json", "IDENTIFIABILITY_V3.json")

#: Chosen by H1 --- lowest false-promotion rate --- not by H3. It scores 0/30, so
#: it is where the 1.0 comes from.
COMPARATOR = "provenai-citation-fidelity-influence"
#: Scores 15/30 and is *not* the comparator. Against it the margin is 0.5.
ESCALATOR = "deepsciverify-abstract-to-full-escalation"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _claim(claim_id: str) -> dict:
    claims = _json(MANIFEST)["claims"]
    matches = [claim for claim in claims if claim.get("id") == claim_id]
    assert len(matches) == 1, f"expected exactly one {claim_id} claim, found {len(matches)}"
    return matches[0]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sums() -> dict[str, str]:
    mapping = {}
    for raw in SUMS.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        digest, _, rest = line.partition("  ")
        mapping[rest] = digest
    return mapping


def _paragraphs(text: str) -> list[str]:
    return [block for block in text.split("\n\n") if block.strip()]


def test_the_h3_claim_reads_on_the_v3_artifacts_inside_the_paper() -> None:
    """Status and evidence path together; either alone can be true and useless."""

    claim = _claim("P4.H3")
    assert claim["status"] == "SUPPORTED", (
        "P4.H3 is not SUPPORTED. If the V3 panel has been re-run and came out null, that is "
        "a real negative and this test is what has to change; if the status was reverted "
        "without a new run, the claim is back on a saturated axis."
    )
    artifacts = claim["artifacts"]
    assert artifacts, "a SUPPORTED claim with no artifacts is an assertion"
    for relative in artifacts:
        assert relative.startswith("evidence/protected_v3/") or relative == CLAIM_AXIS_AUDIT, (
            f"P4.H3 cites {relative!r}, which is not the V3 measurement"
        )
        assert (P4 / relative).is_file(), f"P4.H3 cites a missing artifact: {relative}"
    assert "evidence/protected_v3/PANEL_V3.json" in artifacts
    assert "evidence/protected_v3/IDENTIFIABILITY_V3.json" in artifacts, (
        "the panel result is only quotable beside the register that licenses quoting it"
    )
    assert "evidence/protected_v3/FREEZE.md" in artifacts, (
        "a prospectively frozen result that does not cite its freeze is a retrospective one"
    )
    assert CLAIM_AXIS_AUDIT in artifacts, (
        "the exact-axis authority decision is missing from the supported claim"
    )


def test_the_claim_text_states_both_margins_and_the_pre_registered_reading() -> None:
    """The headline alone is true and misleading; the freeze fixed the honest reading."""

    text = _claim("P4.H3")["text"]
    for fragment in ("30/30", "0/360", "0/30", "15/30", "1.0", "0.5"):
        assert fragment in text, f"P4.H3 text omits {fragment!r}"
    assert COMPARATOR in text, "the claim does not name the comparator the 1.0 is against"
    assert ESCALATOR in text, (
        "the claim quotes a margin without naming the system that scores 15/30; against it "
        "the margin is 0.5, and both numbers belong in any sentence about H3"
    )
    assert "terminal expressiveness" in text, (
        "the pre-registered reading is gone from the claim; without it the number reads as "
        "a finer-grained scientific judgement, which FREEZE.md section 5 refused in advance"
    )
    assert "cannot emit CANNOT_CHECK" in text, (
        "the claim no longer says why nine comparators score 0 -- they have no such terminal"
    )


def test_the_panel_artifact_backs_every_number_the_claim_quotes() -> None:
    panel = _json(V3 / "PANEL_V3.json")
    assert panel["case_construction"] == "v3"
    assert panel["strongest_frozen_comparator"] == COMPARATOR, (
        "the comparator is selected by H1, not by H3; a different selection changes the 1.0"
    )
    h3 = panel["H3"]
    assert h3["status"] == "SUPPORTED"
    assert h3["orion_minus_baseline_correct_cannot_check"] == 1.0
    assert (h3["ci95_low"], h3["ci95_high"]) == (1.0, 1.0)
    assert h3["ci95_low"] > 0.0, "the pre-registered threshold for SUPPORTED"

    systems = panel["systems"]
    assert len(systems) == 11
    assert systems["ORION"]["correct_cannot_check"] == 30
    assert systems["ORION"]["false_promotions"] == 0
    assert systems[COMPARATOR]["correct_cannot_check"] == 0
    assert systems[ESCALATOR]["correct_cannot_check"] == 15, (
        "deepsciverify no longer scores 15/30; the 0.5 margin the claim states has moved"
    )
    zeros = [name for name, row in systems.items() if row["correct_cannot_check"] == 0]
    assert len(zeros) == 9, (
        f"nine comparators should score 0 because they have no CANNOT_CHECK terminal; "
        f"found {len(zeros)}. The claim's reading rests on that count."
    )


def test_the_score_is_quotable_only_because_the_register_clears() -> None:
    """Headroom without a passing audit is what the V2 construction had."""

    register = _json(V3 / "IDENTIFIABILITY_V3.json")
    assert register["informedness_ceiling"] == 0.0
    assert register["probe_count"] == 14

    clean = register["constructions"]["v3"]["terminals"]["CANNOT_CHECK"]
    assert clean["outcome"] == "PASS"
    assert clean["reason"] == "NO_CUE_RECOVERED_LABEL"
    assert clean["worst_recovery"] == 0.0
    assert len(clean["results"]) == 14
    for probe in clean["results"]:
        assert probe["recovery"] == 0.0, f"{probe['probe_id']} recovers the audited label"
        assert probe["unscored"] == 0, (
            f"{probe['probe_id']} left cases unscored; a probe that declines to predict "
            f"cannot be said to have failed to recover the label"
        )

    # The register does not clear on every axis, and the published claim says so.
    # All four non-clearing cells are the digest-prefix probe -- FREEZE.md section 3
    # declares it a noise control -- and none is on the axis H3 reads. A claim that
    # said "clears everywhere" would be false; one that omitted these would be the
    # same omission the 0.5 margin exists to prevent.
    residual = [
        (seed, label, t["worst_recovery"], t["worst_probe"])
        for seed, terminals in register["seed_invariance"].items()
        for label, t in terminals.items()
        if t["outcome"] != "PASS"
    ]
    assert len(residual) == 4
    assert {r[3] for r in residual} == {"digest-prefix"}
    assert {r[1] for r in residual} == {"BLOCK", "PROMOTE"}
    assert "CANNOT_CHECK" not in {r[1] for r in residual}
    assert max(r[2] for r in residual) < 0.09

    manifest = _json(MANIFEST)
    claim = next(c for c in manifest["claims"] if c["id"] == "P4.H3")
    assert "on the CANNOT_CHECK axis" in claim["text"]
    assert "does not clear everywhere" in claim["text"]
    assert "noise control" in claim["text"]

    seeds = register["seed_invariance"]
    assert len(seeds) == 13
    for seed, terminals in seeds.items():
        entry = terminals["CANNOT_CHECK"]
        assert entry["outcome"] == "PASS", f"CANNOT_CHECK audit fails on seed {seed}"
        assert entry["worst_recovery"] == 0.0, f"seed {seed} recovers the label"

    # The instrument has power: the same fourteen probes condemn the two earlier
    # constructions. A register that passes everything licenses nothing.
    for construction in ("v1", "v2"):
        earlier = register["constructions"][construction]["terminals"]["CANNOT_CHECK"]
        assert earlier["outcome"] == "FAIL", (
            f"the register now clears construction {construction}, whose CANNOT_CHECK label "
            f"a character count recovers; the audit has stopped being able to fail"
        )


def test_the_v2_record_survives_unedited_and_still_reads_as_a_saturated_instrument() -> None:
    """V3 is a different battery. Nothing about it licenses restating V2's number."""

    retained = _claim("P4.H3.V2")
    assert retained["status"] == "NOT_SUPPORTED", (
        "V2's H3 verdict has been rewritten. It is the record of what the V1 construction "
        "produced and is retained, not corrected."
    )
    assert "evidence/protected_v2/PUBLICATION_METRICS_V2.json" in retained["artifacts"]

    metrics = _json(V2_METRICS)
    assert metrics["hypotheses"]["H3"]["status"] == "NOT_SUPPORTED"
    rates = {row["correct_cannot_check_rate"] for row in metrics["systems"].values()}
    assert rates == {1.0}, (
        "V2's correct_cannot_check_rate is no longer 1.0 for every system. The V2 artifacts "
        "are not to be edited; a change here means one was."
    )

    audit = _json(PANEL_AUDIT)
    settled = audit["hypotheses_settled_before_any_system_ran"]
    assert any("PUBLICATION_METRICS_V2.json" in entry and "H3" in entry for entry in settled), (
        "the audit no longer records that V2's H3 was settled before any system ran"
    )


def test_the_promoted_artifacts_are_the_campaign_artifacts_byte_for_byte() -> None:
    """Copies, so the duplication cannot become a divergence in silence."""

    for name in PROMOTED:
        promoted, origin = V3 / name, CAMPAIGN / name
        assert origin.is_file(), f"the campaign artifact {name} has gone"
        assert _sha256(promoted) == _sha256(origin), (
            f"{name} in the paper differs from the campaign copy. FREEZE.md is a frozen "
            f"protocol and RESULT.md reports one run; neither is edited on promotion."
        )


def test_every_artifact_the_h3_claim_cites_is_covered_by_the_paper_binding() -> None:
    """A claim whose evidence no digest covers is bound by nothing."""

    sums = _sums()
    cited = [*_claim("P4.H3")["artifacts"], *_claim("P4.H3.V2")["artifacts"]]
    for relative in cited:
        assert relative in sums, (
            f"{relative} is cited by an H3 claim but journal_package/SHA256SUMS does not "
            f"cover it; regenerate with check_journal_package.py --write-hashes"
        )
        assert sums[relative] == _sha256(P4 / relative), f"digest drift for {relative}"


def test_the_manuscript_never_reports_the_margin_without_the_other_one() -> None:
    """Whatever paragraph carries the 1.0 must carry the 15/30 and the 0.5 too."""

    text = assemble(MANUSCRIPT)
    carriers = [para for para in _paragraphs(text) if "$[1.0,1.0]$" in para]
    assert len(carriers) >= 3, (
        f"the repaired-battery interval appears in {len(carriers)} paragraphs; it is stated "
        f"in the abstract, the introduction's findings list and the results section"
    )
    for para in carriers:
        assert "15/30" in para, (
            "a paragraph states the H3 interval without the 15/30 that the one escalating "
            "comparator scores"
        )
        assert "$0.5$" in para, (
            "a paragraph states the 1.0 margin without the 0.5 margin against deepsciverify"
        )
    assert "outcome expressiveness" in text, (
        "the manuscript reports the number without the pre-registered reading of it"
    )
