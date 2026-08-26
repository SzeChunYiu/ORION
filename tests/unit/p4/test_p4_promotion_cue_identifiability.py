"""P4-U-T2 asked for an identifiability audit. This runs one, on the real battery.

The protected V2 campaign is frozen and cannot be re-run here, but the case
generator that produced it is in the tree, is deterministic in its seed, and now
carries every construction it has ever emitted behind ``--construction``. So all
three can be regenerated and probed with one instrument:

``v1``
    what the published campaign ran against --- an empty evidence list, and
    ``len(evidence) == 0`` classifying ``CANNOT_CHECK`` at 420/420;
``v2``
    the first repair, which killed the object count and shipped a character
    count in its place;
``v3``
    the second repair, written against the property rather than a named cue, and
    frozen in ``research/campaigns/2026-08-21-p4-battery-v3-identifiable/``.

The file is two-sided in both directions. The v1 and v2 leaks are asserted at
their measured values, so the historical record cannot be quietly restated. The
v3 register is asserted *clean*, so a future edit that reopens any of the
fourteen cues reds this file rather than passing silently --- which is exactly
what nobody was in a position to notice when the V1 repair shipped the V2 leak.
"""

from __future__ import annotations

import collections
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

from orion.programme.benchmark_identifiability import (
    AuditedGuardVerdict,
    AuditedScore,
    IdentifiabilityReason,
)
from orion.programme.guard_exercise import assess_guard
from orion.programme.records import Outcome
from orion.study.p4 import (
    P4_SHORTCUT_PROBES,
    audit_promotion_terminal,
    extract_promotion_cues,
    false_promotion_exercise,
    labelled_case,
)

ROOT = Path(__file__).resolve().parents[3]
HOST = ROOT / "papers" / "orion-14-verified-scientific-discovery" / "host"
GENERATOR = HOST / "generate_protected_cases.py"
METRICS = (
    ROOT
    / "papers"
    / "orion-14-verified-scientific-discovery"
    / "evidence"
    / "protected_v2"
    / "PUBLICATION_METRICS_V2.json"
)

#: Any value works; the leaks are invariant under it, which is the point of
#: ``test_the_v2_leak_does_not_depend_on_the_secret_host_seed``.
SEED = "audit-probe-20260821"

#: The seed the V3 freeze document names for the register. Fixed there so that a
#: seed cannot be chosen after seeing which one makes the audit pass.
V3_SEED = "v3-audit-20260821"

#: The one probe in the register that measures noise rather than construction:
#: the leading nibble of a SHA-256 over seed-derived content. It is registered as
#: a control on the instrument, and on a 0.0 ceiling it will occasionally fire.
NOISE_PROBE = "digest-prefix"


def _host_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _generator():
    return _host_module("p4_case_generator", GENERATOR)


def _run_panel(cases: list[dict[str, Any]]) -> dict[str, tuple[int, int]]:
    """Run the frozen eleven-system panel and return ``(false promotions, correct CC)``.

    The runners are gold-blind by construction: they receive ``case_id`` and
    ``candidate_visible`` only, exactly as the host protocol hands them over.
    """

    baselines = _host_module("p4_run_baselines_v2", HOST / "run_baselines_v2.py")
    candidate = _host_module("p4_run_candidate", HOST / "run_candidate.py")
    runners = (*baselines._v1.RUNNERS, baselines._deepsci, candidate.evaluate_case)

    tally: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for case in cases:
        gold = case["expected_authority_terminal"]
        for runner in runners:
            row = runner(case["case_id"], case["candidate_visible"])
            counts = tally[row["system_id"]]
            if gold != "PROMOTE":
                counts["false_promotions"] += row["authority_terminal"] == "PROMOTE"
            if gold == "CANNOT_CHECK":
                counts["correct_cannot_check"] += row["authority_terminal"] == "CANNOT_CHECK"
    return {
        system: (counts["false_promotions"], counts["correct_cannot_check"])
        for system, counts in tally.items()
    }


def _battery(seed: str = SEED, *, construction: str = "v2") -> list[dict[str, Any]]:
    """Regenerate the 420-case protected battery at one construction."""

    generator = _generator()
    cases: list[dict[str, Any]] = []
    ordinal = 0
    for family in generator.FAMILIES:
        for within_family in range(generator.COUNTS[family]):
            cases.append(
                generator._case(
                    seed, ordinal, family, within_family, construction=construction
                )
            )
            ordinal += 1
    return cases


def _recoveries(cases: list[dict[str, Any]], label: str) -> dict[str, float | None]:
    audit = audit_promotion_terminal(cases, label=label)
    return {result.probe_id: result.recovery for result in audit.results}


@pytest.fixture(scope="module")
def v2_battery() -> list[dict[str, Any]]:
    return _battery(construction="v2")


@pytest.fixture(scope="module")
def v3_battery() -> list[dict[str, Any]]:
    return _battery(V3_SEED, construction="v3")


# --------------------------------------------------------------------------
# The historical record: what v1 and v2 measured, kept measurable.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("construction", ["v1", "v2", "v3"])
def test_every_construction_regenerates_at_the_documented_shape(construction) -> None:
    """A guard on the fixtures themselves: 420 cases, 30 of them CANNOT_CHECK.

    The repair changes what must be reasoned about. It must not change what the
    answer is, in any construction.
    """

    battery = _battery(construction=construction)
    assert len(battery) == 420
    terminals = [case["expected_authority_terminal"] for case in battery]
    assert terminals.count("CANNOT_CHECK") == 30
    assert terminals.count("PROMOTE") == 60
    assert terminals.count("BLOCK") == 330


def test_the_v2_cannot_check_terminal_is_recoverable_from_construction_shape(
    v2_battery,
) -> None:
    """The finding. Fitted on public custody, scored on protected custody."""

    audit = audit_promotion_terminal(v2_battery)
    assert audit.outcome is Outcome.FAIL
    assert audit.reason is IdentifiabilityReason.LABEL_RECOVERED_BY_CUE

    by_probe = {result.probe_id: result for result in audit.results}
    length = by_probe["evidence-content-length"]
    assert length.recovery == 1.0
    assert (length.true_positive, length.positives) == (20, 20)
    assert (length.false_positive, length.negatives) == (0, 250)
    assert length.unscored == 0


def test_the_v1_repair_closed_one_cue_and_opened_another() -> None:
    """The reason this is a failure record and not a fix report.

    Under V1 the object-count probe recovers the label exactly. The repair was
    written against that probe and succeeds against it --- object count now
    recovers nothing. The character count of the evidence body recovers the same
    30 cases instead.
    """

    v1 = _recoveries(_battery(construction="v1"), "CANNOT_CHECK")
    v2 = _recoveries(_battery(construction="v2"), "CANNOT_CHECK")

    assert v1["evidence-object-count"] == 1.0
    assert v2["evidence-object-count"] == 0.0
    assert v2["evidence-content-length"] == 1.0


def test_the_v2_null_declared_hash_cue_leaks_half_the_family(v2_battery) -> None:
    """The missingness pattern #652 names, measured: 10 of 20, no false positives."""

    by_probe = {result.probe_id: result for result in audit_promotion_terminal(v2_battery).results}
    missingness = by_probe["declared-hash-missingness"]
    assert missingness.recovery == 0.5
    assert missingness.false_positive == 0


def test_the_v2_leak_does_not_depend_on_the_secret_host_seed() -> None:
    """The battery's protection is a seed the host never publishes. It does not help.

    Case ids and support tokens are seed-derived; the content templates they are
    interpolated into are fixed strings, so their lengths are the same for every
    campaign the generator will ever emit.
    """

    for seed in ("audit-probe-20260821", "another-seed-777", "third"):
        recoveries = _recoveries(_battery(seed, construction="v2"), "CANNOT_CHECK")
        assert recoveries["evidence-content-length"] == 1.0, seed


def test_the_v2_promote_terminal_survives_every_deterministic_probe(v2_battery) -> None:
    """The audit is capable of clearing an axis, which is what gives it standing.

    Clean coverage is saturated for a different reason: the clean cases are easy,
    not leaky. Every probe that reads a deterministic feature of the construction
    scores exactly 0.0 on PROMOTE. Only ``digest-prefix`` --- the declared noise
    control, sixteen buckets over a cryptographic digest --- exceeds it, and that
    is the control reporting on the ceiling rather than on the battery.
    """

    recoveries = _recoveries(v2_battery, "PROMOTE")
    deterministic = {
        probe: value for probe, value in recoveries.items() if probe != NOISE_PROBE
    }
    assert set(deterministic.values()) == {0.0}
    assert recoveries[NOISE_PROBE] is not None


def test_the_v2_block_terminal_leaks_only_through_the_cannot_check_cases(
    v2_battery,
) -> None:
    """H1's own discrimination is not what these probes recover.

    ``BLOCK`` fails the audit too, at informedness 0.4, but the confusion matrix
    says where that comes from: every true negative is a ``CANNOT_CHECK`` case
    and every false positive is a protected clean positive. The probe cannot tell
    a hostile case from a clean one, which is the comparison H1 rests on.
    """

    audit = audit_promotion_terminal(v2_battery, label="BLOCK")
    assert audit.outcome is Outcome.FAIL
    worst = max(
        (item for item in audit.results if item.probe_id != NOISE_PROBE),
        key=lambda result: result.recovery or 0.0,
    )
    assert worst.true_positive == worst.positives == 220
    assert worst.true_negative == 20, "true negatives should be exactly the CANNOT_CHECK cases"
    assert worst.false_positive == 30, "false positives should be exactly the clean positives"


def test_the_v1_reconstruction_reproduces_the_frozen_published_panel() -> None:
    """The reconstruction is faithful, checked against the artifact it reconstructs.

    Every claim in the failure record about what the published campaign measured
    depends on the V1 battery being the one that produced
    ``PUBLICATION_METRICS_V2.json``. That is not asserted: the frozen panel is
    re-run over the reconstruction and matched to the published rates, system by
    system, from a seed unrelated to the host's.
    """

    published = json.loads((METRICS).read_text(encoding="utf-8"))["systems"]
    measured = _run_panel(_battery(construction="v1"))

    assert set(measured) == set(published), "panel membership drifted from the frozen artifact"
    for system_id, (false_promotions, correct_cannot_check) in sorted(measured.items()):
        entry = published[system_id]
        assert false_promotions == round(entry["false_promotion_rate"] * 360), system_id
        assert correct_cannot_check == 30, system_id
        assert entry["correct_cannot_check_rate"] == 1.0, system_id


def test_the_v2_construction_would_have_reported_h3_as_a_result() -> None:
    """The V1 repair's real cost: a visibly broken axis becomes an invisibly broken one.

    On the V2 construction the CANNOT_CHECK axis had headroom for the first time,
    so a campaign run against it reports H3 supported with a wide margin. The
    margin is over cases a character count separates.
    """

    measured = _run_panel(_battery(construction="v2"))
    correct = {system: pair[1] for system, pair in measured.items()}
    assert correct["ORION"] == 30
    assert sum(1 for value in correct.values() if value == 0) == 9
    assert correct["deepsciverify-abstract-to-full-escalation"] == 15


def test_the_v2_headline_guard_passes_on_exercise_and_still_cannot_be_credited(
    v2_battery,
) -> None:
    """ORION's 0/360 is a real zero over a real denominator, and not yet evidence."""

    guard = assess_guard(
        false_promotion_exercise(arm_id="ORION", false_promotions=0, promotion_opportunities=360)
    )
    assert guard.outcome is Outcome.PASS

    joined = AuditedGuardVerdict(guard=guard, audit=audit_promotion_terminal(v2_battery))
    assert joined.outcome is Outcome.CANNOT_CHECK


def test_the_v2_h3_score_cannot_be_constructed(v2_battery) -> None:
    """``correct_cannot_check_rate`` is exactly the number the audit disqualifies."""

    with pytest.raises(ValueError, match="LABEL_RECOVERED_BY_CUE"):
        AuditedScore(
            score_name="correct_cannot_check_rate",
            value=1.0,
            audit=audit_promotion_terminal(v2_battery),
        )


# --------------------------------------------------------------------------
# The repair: the V3 construction, and the register it has to keep clearing.
# --------------------------------------------------------------------------


def test_the_v3_construction_is_shape_uniform(v3_battery) -> None:
    """The property the register measures, asserted directly on the battery.

    Every case carries the same containers, the same keys, no nulls, and bodies
    of one single length. A family cannot be told from the shape of its case
    because there is only one shape.
    """

    lengths: set[int] = set()
    for case in v3_battery:
        view = case["candidate_visible"]
        pool = view["retrieval_pool"]
        assert len(view["evidence"]) == 1
        assert len(pool) == 2
        assert len(view["behavioral_trace"]["used_evidence_ids"]) == 1
        assert len(view["access_requests"]) == 2
        assert len(view["search_trace"]) == 1
        assert len({item["source_id"] for item in pool}) == 2
        for item in pool:
            lengths.add(len(item["content"]))
            assert item["declared_content_hash"] is not None
            assert item["declared_provenance_hash"] is not None
            assert "SUPPORT::" in item["content"], (
                "every record carries the marker, so its presence carries nothing"
            )
    assert len(lengths) == 1, f"evidence bodies take {sorted(lengths)} lengths, not one"


def test_the_v3_construction_clears_the_whole_register(v3_battery) -> None:
    """The repair, measured by the instrument that condemned its predecessor.

    Not "the named cue is gone" --- every probe in the register, at the ceiling
    the freeze document declared, with the confusion matrix showing that no probe
    ever predicts the label for any protected case.
    """

    audit = audit_promotion_terminal(v3_battery, max_recovery=0.0)
    assert audit.outcome is Outcome.PASS
    assert audit.reason is IdentifiabilityReason.NO_CUE_RECOVERED_LABEL
    assert audit.worst_recovery == 0.0
    assert len(audit.results) == len(P4_SHORTCUT_PROBES) >= 14
    for result in audit.results:
        assert result.recovery == 0.0, result.probe_id
        assert result.true_positive == 0 and result.false_positive == 0, result.probe_id
        assert result.unscored == 0, result.probe_id
        assert result.positives == 20 and result.negatives == 250


@pytest.mark.parametrize("label", ["CANNOT_CHECK", "PROMOTE", "BLOCK"])
def test_the_v3_construction_clears_every_terminal(v3_battery, label) -> None:
    """Closing the CANNOT_CHECK leak took BLOCK's 0.4 with it, as predicted.

    The failure record read ``BLOCK``'s 0.4 as the same leak through a one-vs-rest
    lens rather than a second one, and said removing the ``CANNOT_CHECK`` leak
    would remove it. This is that prediction, checked.
    """

    audit = audit_promotion_terminal(v3_battery, label=label, max_recovery=0.0)
    assert audit.outcome is Outcome.PASS, audit.detail
    assert audit.worst_recovery == 0.0


def test_the_v3_cannot_check_axis_is_clean_for_every_seed(v3_battery) -> None:
    """The host's secret seed protected nothing before. Now nothing needs it to."""

    for seed in (V3_SEED, "v3-audit-alt-a", "v3-audit-alt-b", "unrelated-9911"):
        audit = audit_promotion_terminal(
            _battery(seed, construction="v3"), max_recovery=0.0
        )
        assert audit.outcome is Outcome.PASS, f"{seed}: {audit.detail}"
        assert audit.worst_recovery == 0.0, seed


def test_no_single_pool_rule_classifies_the_v3_cannot_check_family(v3_battery) -> None:
    """The rules that classified V1 and V2, and the one V2's own comment feared.

    ``CANNOT_CHECK`` is a strict subset of "the assigned record does not support
    the claim" --- a set that also holds 30 ``BLOCK`` cases --- and subtype B puts
    supporting records in the pools of half the family, so "nothing in the pool
    supports" does not classify it either.
    """

    def _assigned_lacks_support(view: dict[str, Any]) -> bool:
        token = view["claim"]["support_token"]
        return f"SUPPORT::{token}" not in view["evidence"][0]["content"]

    def _pool_lacks_support(view: dict[str, Any]) -> bool:
        token = view["claim"]["support_token"]
        return not any(
            f"SUPPORT::{token}" in item["content"] for item in view["retrieval_pool"]
        )

    rules = {
        "evidence list is empty": lambda v: not v["evidence"],
        "pool is empty": lambda v: not v["retrieval_pool"],
        "no evidence was used": lambda v: not v["behavioral_trace"]["used_evidence_ids"],
        "some record lacks a declared hash": lambda v: any(
            item["declared_content_hash"] is None for item in v["retrieval_pool"]
        ),
        "the assigned record does not support the claim": _assigned_lacks_support,
        "nothing in the pool supports the claim": _pool_lacks_support,
    }
    for name, rule in rules.items():
        hits = sum(
            rule(case["candidate_visible"])
            == (case["expected_authority_terminal"] == "CANNOT_CHECK")
            for case in v3_battery
        )
        assert hits < len(v3_battery), (
            f"{name!r} classifies all 420 cases without judging support; a system "
            f"implementing it scores correct_cannot_check_rate 1.0 without reasoning"
        )


def test_the_v3_h3_axis_has_headroom_and_an_audit_that_licenses_reporting_it() -> None:
    """H3's value on the repaired battery, and the audit that lets it be quoted.

    Both halves matter and neither is sufficient. Headroom without a passing
    audit is what the V2 construction had --- a clean 1.0-vs-0.0 margin over
    cases a character count separates. A passing audit without headroom is V1's
    saturation. Reported together, ORION 30/30 against nine systems at 0/30 is a
    measurement of terminal expressiveness under a hard-gate lattice, which is
    what ``research/campaigns/2026-08-21-p4-battery-v3-identifiable/`` says it is.
    """

    battery = _battery("p4-v3-panel-20260821", construction="v3")
    audit = audit_promotion_terminal(battery, max_recovery=0.0)
    assert audit.outcome is Outcome.PASS

    correct = {system: pair[1] for system, pair in _run_panel(battery).items()}
    assert correct["ORION"] == 30
    assert correct["deepsciverify-abstract-to-full-escalation"] == 15
    assert sum(1 for value in correct.values() if value == 0) == 9

    score = AuditedScore(
        score_name="correct_cannot_check_rate", value=1.0, audit=audit
    )
    assert score.value == 1.0

    guard = assess_guard(
        false_promotion_exercise(
            arm_id="ORION", false_promotions=0, promotion_opportunities=360
        )
    )
    assert AuditedGuardVerdict(guard=guard, audit=audit).outcome is Outcome.PASS


# --------------------------------------------------------------------------
# Properties of the instrument, not of any one construction.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("construction", ["v1", "v2", "v3"])
def test_cue_extraction_reads_nothing_a_promotion_obligation_is_defined_over(
    construction,
) -> None:
    """No cue value may be a string.

    Every P4 obligation is a statement about content --- a support token, a source
    id, a hash, a lineage, an integrity status. All of them are strings in the
    candidate-visible view. Reducing every cue to a count, a boolean or an integer
    fingerprint is what makes "this probe does not implement the task" checkable
    rather than asserted, and it is why a probe that recovers the label is damning.
    """

    for case in _battery(construction=construction):
        for name, value in extract_promotion_cues(case["candidate_visible"]).items():
            values = value if isinstance(value, tuple) else (value,)
            assert all(isinstance(item, (int, bool)) for item in values), (
                f"cue {name} carries {value!r}; a probe could read content through it"
            )


def test_every_registered_probe_names_cues_the_extractor_emits(v3_battery) -> None:
    """A probe whose cue no case carries is scored as nothing and reads as clean."""

    emitted = set(extract_promotion_cues(v3_battery[0]["candidate_visible"]))
    for probe in P4_SHORTCUT_PROBES:
        missing = set(probe.cue_names) - emitted
        assert not missing, f"{probe.probe_id} names unemitted cues {sorted(missing)}"


def test_an_unclassified_custody_class_is_refused_rather_than_dropped(v3_battery) -> None:
    """A case with no declared split would leave the eval set without saying so."""

    row = dict(v3_battery[0])
    row["custody_class"] = "SOMETHING_NEW"
    with pytest.raises(ValueError, match="no declared split"):
        labelled_case(row)
