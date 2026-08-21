"""P4-U-T2 asked for an identifiability audit. This runs one, on the real battery.

The protected V2 campaign is frozen and cannot be re-run here, but the case
generator that produced it is in the tree and is deterministic in its seed, so
the construction can be regenerated and probed. That is the measurement behind
``research/failures/2026-08-label-recoverable-from-construction-cue/``.

These tests are two-sided in the way ``test_p4_metric_headroom.py`` is. The leak
is asserted, so a future repair to the construction reds this file rather than
passing silently --- at which point the failure record's numbers are historical
and the assertions should move to the passing side. A repair that closes the leak
is good news; a repair that moves it, as the V1 to V2 repair did, must not read as
good news, and the only way to tell the two apart is to keep measuring.
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
    audit_promotion_terminal,
    extract_promotion_cues,
    false_promotion_exercise,
    labelled_case,
)

ROOT = Path(__file__).resolve().parents[3]
HOST = ROOT / "papers" / "paper-04-verified-scientific-discovery" / "host"
GENERATOR = HOST / "generate_protected_cases.py"
METRICS = (
    ROOT
    / "papers"
    / "paper-04-verified-scientific-discovery"
    / "evidence"
    / "protected_v2"
    / "PUBLICATION_METRICS_V2.json"
)

#: Any value works; the leak is invariant under it, which is the point of
#: ``test_the_leak_does_not_depend_on_the_secret_host_seed``.
SEED = "audit-probe-20260821"


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


def _battery(seed: str = SEED, *, v1_insufficient_evidence: bool = False) -> list[dict[str, Any]]:
    """Regenerate the 420-case protected battery.

    ``v1_insufficient_evidence`` restores the construction the generator's own
    comment describes as V1 --- an empty evidence list --- so the audit can be
    pointed at both sides of the repair with one instrument.
    """

    generator = _generator()
    cases: list[dict[str, Any]] = []
    ordinal = 0
    for family in generator.FAMILIES:
        for within_family in range(generator.COUNTS[family]):
            case = generator._case(seed, ordinal, family, within_family)
            if v1_insufficient_evidence and family == "INSUFFICIENT_EVIDENCE":
                case["candidate_visible"]["evidence"] = []
                case["candidate_visible"]["retrieval_pool"] = []
            cases.append(case)
            ordinal += 1
    return cases


@pytest.fixture(scope="module")
def battery() -> list[dict[str, Any]]:
    return _battery()


def test_the_battery_regenerates_at_the_documented_shape(battery) -> None:
    """A guard on the fixture itself: 420 cases, 30 of them CANNOT_CHECK."""

    assert len(battery) == 420
    terminals = [case["expected_authority_terminal"] for case in battery]
    assert terminals.count("CANNOT_CHECK") == 30
    assert terminals.count("PROMOTE") == 60
    assert terminals.count("BLOCK") == 330


def test_the_cannot_check_terminal_is_recoverable_from_construction_shape(battery) -> None:
    """The finding. Fitted on public custody, scored on protected custody."""

    audit = audit_promotion_terminal(battery)
    assert audit.outcome is Outcome.FAIL
    assert audit.reason is IdentifiabilityReason.LABEL_RECOVERED_BY_CUE

    by_probe = {result.probe_id: result for result in audit.results}
    length = by_probe["evidence-content-length"]
    assert length.recovery == 1.0
    assert (length.true_positive, length.positives) == (20, 20)
    assert (length.false_positive, length.negatives) == (0, 250)
    assert length.unscored == 0


def test_the_v1_repair_closed_one_cue_and_opened_another(battery) -> None:
    """The reason this is a failure record and not a fix report.

    Under V1 the object-count probe recovers the label exactly. The repair was
    written against that probe and succeeds against it --- object count now
    recovers nothing. The character count of the evidence body recovers the same
    30 cases instead.
    """

    v1_audit = audit_promotion_terminal(_battery(v1_insufficient_evidence=True))
    v1 = {result.probe_id: result for result in v1_audit.results}
    v2 = {result.probe_id: result for result in audit_promotion_terminal(battery).results}

    assert v1["evidence-object-count"].recovery == 1.0
    assert v2["evidence-object-count"].recovery == 0.0
    assert v2["evidence-content-length"].recovery == 1.0


def test_the_null_declared_hash_cue_leaks_half_the_family(battery) -> None:
    """The missingness pattern #652 names, measured: 10 of 20, no false positives."""

    by_probe = {result.probe_id: result for result in audit_promotion_terminal(battery).results}
    missingness = by_probe["declared-hash-missingness"]
    assert missingness.recovery == 0.5
    assert missingness.false_positive == 0


def test_the_leak_does_not_depend_on_the_secret_host_seed() -> None:
    """The battery's protection is a seed the host never publishes. It does not help.

    Case ids and support tokens are seed-derived; the content templates they are
    interpolated into are fixed strings, so their lengths are the same for every
    campaign the generator will ever emit.
    """

    for seed in ("audit-probe-20260821", "another-seed-777", "third"):
        audit = audit_promotion_terminal(_battery(seed))
        by_probe = {result.probe_id: result for result in audit.results}
        assert by_probe["evidence-content-length"].recovery == 1.0, seed


def test_the_promote_terminal_survives_the_same_probes(battery) -> None:
    """The audit is capable of passing, so its failure on CANNOT_CHECK carries weight.

    Clean coverage is saturated for a different reason: every panel system scores
    1.0 because the clean cases are easy, not because their label leaks.
    """

    audit = audit_promotion_terminal(battery, label="PROMOTE")
    assert audit.outcome is Outcome.PASS
    assert audit.worst_recovery == 0.0


def test_the_block_terminal_leaks_only_through_the_cannot_check_cases(battery) -> None:
    """H1's own discrimination is not what these probes recover.

    ``BLOCK`` fails the audit too, at informedness 0.4, but the confusion matrix
    says where that comes from: every true negative is a ``CANNOT_CHECK`` case
    and every false positive is a protected clean positive. The probe cannot tell
    a hostile case from a clean one, which is the comparison H1 rests on.
    """

    audit = audit_promotion_terminal(battery, label="BLOCK")
    assert audit.outcome is Outcome.FAIL
    worst = max(audit.results, key=lambda result: result.recovery or 0.0)
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
    measured = _run_panel(_battery(v1_insufficient_evidence=True))

    assert set(measured) == set(published), "panel membership drifted from the frozen artifact"
    for system_id, (false_promotions, correct_cannot_check) in sorted(measured.items()):
        entry = published[system_id]
        assert false_promotions == round(entry["false_promotion_rate"] * 360), system_id
        assert correct_cannot_check == 30, system_id
        assert entry["correct_cannot_check_rate"] == 1.0, system_id


def test_the_repaired_construction_would_report_h3_as_a_result() -> None:
    """The repair's real cost: a visibly broken axis becomes an invisibly broken one.

    On the construction now on disk the CANNOT_CHECK axis has headroom for the
    first time, so a campaign run today reports H3 supported with a wide margin.
    The margin is over cases a character count separates.
    """

    measured = _run_panel(_battery())
    correct = {system: pair[1] for system, pair in measured.items()}
    assert correct["ORION"] == 30
    assert sum(1 for value in correct.values() if value == 0) == 9
    assert correct["deepsciverify-abstract-to-full-escalation"] == 15


def test_the_headline_guard_passes_on_exercise_and_still_cannot_be_credited(battery) -> None:
    """ORION's 0/360 is a real zero over a real denominator, and not yet evidence."""

    guard = assess_guard(
        false_promotion_exercise(arm_id="ORION", false_promotions=0, promotion_opportunities=360)
    )
    assert guard.outcome is Outcome.PASS

    joined = AuditedGuardVerdict(guard=guard, audit=audit_promotion_terminal(battery))
    assert joined.outcome is Outcome.CANNOT_CHECK


def test_the_reported_h3_score_cannot_be_constructed(battery) -> None:
    """``correct_cannot_check_rate`` is exactly the number the audit disqualifies."""

    with pytest.raises(ValueError, match="LABEL_RECOVERED_BY_CUE"):
        AuditedScore(
            score_name="correct_cannot_check_rate",
            value=1.0,
            audit=audit_promotion_terminal(battery),
        )


def test_cue_extraction_reads_nothing_a_promotion_obligation_is_defined_over(battery) -> None:
    """No cue value may be a string.

    Every P4 obligation is a statement about content --- a support token, a source
    id, a hash, a lineage, an integrity status. All of them are strings in the
    candidate-visible view. Reducing every cue to a count or a boolean is what
    makes "this probe does not implement the task" checkable rather than asserted,
    and it is why a probe that recovers the label is damning.
    """

    for case in battery:
        for name, value in extract_promotion_cues(case["candidate_visible"]).items():
            values = value if isinstance(value, tuple) else (value,)
            assert all(isinstance(item, (int, bool)) for item in values), (
                f"cue {name} carries {value!r}; a probe could read content through it"
            )


def test_an_unclassified_custody_class_is_refused_rather_than_dropped(battery) -> None:
    """A case with no declared split would leave the eval set without saying so."""

    row = dict(battery[0])
    row["custody_class"] = "SOMETHING_NEW"
    with pytest.raises(ValueError, match="no declared split"):
        labelled_case(row)
