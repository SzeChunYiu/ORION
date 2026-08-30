"""The model panel is only as good as the checks on it, so these are checks on the checks.

Nothing here touches a network. Every judge is a deterministic script; `JudgeBackend` exists
so a live model adapter can be dropped in later without a test ever reaching for one.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, fields, replace
from pathlib import Path

import pytest

from orion.study.p1.adjudication import (
    ADJUDICATOR_KIND,
    V1_POLICY,
    AdjudicationRecord,
    CannotCheckReason,
    DisagreementPolicy,
    IndependenceError,
    JudgeVerdict,
    PanelOutcome,
    PolicyError,
    Question,
    ResponsibilityClass,
    RubricIntegrityError,
    RubricMismatchError,
    adjudicate,
    cohens_kappa,
    extract_rubric_body,
    fleiss_kappa,
    load_rubric,
    mean_pairwise_agreement,
    panel_independence_witness,
    policy_from_rubric,
    rubric_content_hash,
)
from orion.study.p1.cases import (
    AdjudicationStatus,
    HiddenShiftCase,
    ProtectedGold,
    PublicView,
    Split,
    TaskFamily,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
RUBRIC_PATH = (
    REPO_ROOT
    / "papers"
    / "orion-11-recursive-epistemic-reconstruction"
    / "protocol"
    / "ADJUDICATION_RUBRIC_V1.md"
)

# Frozen. A change to either document breaks these literals on purpose: that is what makes
# "the rubric and the policy predate the verdicts" a checkable claim rather than a promise.
FROZEN_RUBRIC_HASH = "543139fb00d71258c7fa11fb025bd8e307f981fe9c7562049f3852fd5d2914b8"
FROZEN_POLICY_HASH = "d93b30f5a030d366acba2d0be47045cfca43f839cd2be6bfc7ccc2c9ff2e7978"

OTHER_HASH = "f" * 64


# --------------------------------------------------------------------------- doubles


@dataclass
class ScriptedJudge:
    """A deterministic stand-in for one adjudicator. Never calls out."""

    judge_id: str
    lineage_id: str
    script: dict[str, dict]
    forced_rubric_hash: str | None = None
    forced_context_id: str | None = None
    constant_context: bool = False
    seen_views: list[PublicView] | None = None
    _issued: int = 0

    def new_context(self) -> str:
        if self.constant_context:
            return f"{self.judge_id}::ctx-reused"
        self._issued += 1
        return f"{self.judge_id}::ctx{self._issued}"

    def judge(
        self,
        view: PublicView,
        *,
        rubric_body: str,
        rubric_hash: str,
        context_id: str,
    ) -> JudgeVerdict:
        # The blinding boundary, asserted from inside the judge: this is the whole object
        # a judge is ever handed, and it carries no gold.
        assert isinstance(view, PublicView)
        assert not hasattr(view, "protected_gold")
        if self.seen_views is not None:
            self.seen_views.append(view)
        return JudgeVerdict(
            case_id=view.case_id,
            judge_id=self.judge_id,
            lineage_id=self.lineage_id,
            context_id=self.forced_context_id or context_id,
            rubric_hash=self.forced_rubric_hash or rubric_hash,
            **self.script[view.case_id],
        )


def warranted(reopen: tuple[str, ...] | None = ("C-baseline-estimate",)) -> dict:
    return {
        "reframe_warranted": True,
        "responsibility_class": ResponsibilityClass.MEASUREMENT,
        "coordinates": ("metric_definition",),
        "reopen": reopen,
        "confidence": 0.8,
        "rationale": "R3(4): the stated metric does not measure the stated construct.",
    }


def not_warranted() -> dict:
    return {
        "reframe_warranted": False,
        "responsibility_class": ResponsibilityClass.EVIDENCE,
        "confidence": 0.7,
        "rationale": "R2: the missing record is listed in observable_resources.",
    }


def abstained() -> dict:
    return {
        "reframe_warranted": None,
        "confidence": 0.2,
        "rationale": "Section 5: no observable artifact discriminates evidence from measurement.",
    }


def view(case_id: str) -> PublicView:
    return PublicView(
        case_id=case_id,
        public_prompt=f"task {case_id}",
        observable_resources=("notes.md",),
        budget_class="standard",
    )


def views(*case_ids: str) -> list[PublicView]:
    return [view(case_id) for case_id in case_ids]


def panel(*scripts: dict[str, dict]) -> list[ScriptedJudge]:
    return [
        ScriptedJudge(judge_id=f"judge-{index}", lineage_id=f"lineage-{index}", script=script)
        for index, script in enumerate(scripts)
    ]


def run(case_ids: list[str], judges: list[ScriptedJudge], **kwargs):
    return adjudicate(views(*case_ids), judges, rubric_hash=FROZEN_RUBRIC_HASH, **kwargs)


# -------------------------------------------------------------------- frozen artifacts


def test_rubric_document_hashes_to_the_digest_it_records():
    rubric = load_rubric(RUBRIC_PATH)
    assert rubric.content_hash == FROZEN_RUBRIC_HASH
    assert rubric_content_hash(rubric.body) == FROZEN_RUBRIC_HASH

    # The freeze must cover the provenance declaration itself, not only the decision rules:
    # otherwise the "model-based" labelling could be stripped without changing the digest.
    body = rubric.body.lower()
    assert "model-based" in body
    assert "model_adjudicated" in body
    assert "may be reported, cited or re-tiered as human adjudication" in body
    assert "abstain" in body


def test_tampered_rubric_is_refused_not_warned_about(tmp_path):
    text = RUBRIC_PATH.read_text()
    tampered = tmp_path / "rubric.md"
    tampered.write_text(text.replace("Never split the difference.", "Split the difference."))
    with pytest.raises(RubricIntegrityError, match="content hash mismatch"):
        load_rubric(tampered)

    missing = tmp_path / "no-markers.md"
    missing.write_text("# rubric with no body markers\n")
    with pytest.raises(RubricIntegrityError, match="exactly once"):
        extract_rubric_body(missing.read_text())


def test_policy_is_frozen_inside_the_hashed_rubric_body():
    rubric = load_rubric(RUBRIC_PATH)
    # One digest witnesses both the decision procedure and the thresholds it is applied with.
    assert policy_from_rubric(rubric.body) == V1_POLICY
    assert V1_POLICY.policy_hash == FROZEN_POLICY_HASH
    assert (V1_POLICY.kappa_threshold, V1_POLICY.quorum, V1_POLICY.min_judges) == (0.6, 2, 2)
    assert V1_POLICY.require_defined_kappa_for_majority is True


def test_a_runtime_policy_that_drifts_from_the_frozen_one_is_refused():
    rubric = load_rubric(RUBRIC_PATH)
    loosened = replace(V1_POLICY, kappa_threshold=0.1)
    with pytest.raises(PolicyError, match="differs from the policy frozen"):
        adjudicate(
            views("P1-C001"),
            panel({"P1-C001": warranted()}, {"P1-C001": warranted()}),
            rubric_hash=rubric.content_hash,
            rubric_body=rubric.body,
            policy=loosened,
        )


def test_rubric_hash_mismatch_refuses_on_both_sides_of_the_boundary():
    # (a) a judge that answered from a different rubric revision is refused, not pooled.
    judges = panel({"P1-C001": warranted()}, {"P1-C001": warranted()})
    judges[1].forced_rubric_hash = OTHER_HASH
    with pytest.raises(RubricMismatchError, match="answered from rubric"):
        run(["P1-C001"], judges)

    # (b) a rubric body that does not hash to the declared digest is refused up front.
    with pytest.raises(RubricIntegrityError, match="does not hash to the declared"):
        adjudicate(
            views("P1-C001"),
            panel({"P1-C001": warranted()}, {"P1-C001": warranted()}),
            rubric_hash=FROZEN_RUBRIC_HASH,
            rubric_body="a body that is not the rubric",
        )


# ------------------------------------------------------------------- kappa hand-checks


def test_cohens_kappa_matches_the_hand_computed_two_by_two_table():
    # Classic 2x2, N = 50: both-yes 20, A-yes/B-no 5, A-no/B-yes 10, both-no 15.
    #   p_o = (20 + 15) / 50                      = 0.70
    #   A marginals: yes 25/50 = 0.5, no 25/50 = 0.5
    #   B marginals: yes 30/50 = 0.6, no 20/50 = 0.4
    #   p_e = 0.5 * 0.6 + 0.5 * 0.4               = 0.50
    #   kappa = (0.70 - 0.50) / (1 - 0.50)        = 0.20 / 0.50 = 0.40
    a = ["yes"] * 20 + ["yes"] * 5 + ["no"] * 10 + ["no"] * 15
    b = ["yes"] * 20 + ["no"] * 5 + ["yes"] * 10 + ["no"] * 15
    assert len(a) == len(b) == 50
    assert cohens_kappa(a, b) == pytest.approx(0.40, abs=1e-12)
    assert mean_pairwise_agreement(list(zip(a, b, strict=True))) == pytest.approx(0.70)


def test_kappa_is_chance_corrected_so_ninety_percent_agreement_can_be_worth_nothing():
    """The whole reason kappa gates this panel and raw agreement does not.

    The brief's literal phrasing — two judges, 90% agreement, both at 90% prevalence — is
    arithmetically impossible to drive to zero, so both tables are pinned: the one that
    phrasing produces, and the one that realises its intent.
    """

    # Table 1 — both judges at 90% prevalence, agreeing on 90 of 100 items:
    #   both-yes 85, A-yes/B-no 5, A-no/B-yes 5, both-no 5
    #   p_o = (85 + 5) / 100                        = 0.90
    #   marginals: A yes 90/100, B yes 90/100
    #   p_e = 0.9 * 0.9 + 0.1 * 0.1                 = 0.82
    #   kappa = (0.90 - 0.82) / (1 - 0.82)          = 0.08 / 0.18 = 0.4444...
    a = ["yes"] * 85 + ["yes"] * 5 + ["no"] * 5 + ["no"] * 5
    b = ["yes"] * 85 + ["no"] * 5 + ["yes"] * 5 + ["no"] * 5
    assert cohens_kappa(a, b) == pytest.approx(4 / 9, abs=1e-12)  # 0.08 / 0.18

    # Table 2 — the headline. A judge that always answers "yes" agrees with a discriminating
    # judge on 90 of 100 items when the label is 90% prevalent, and contributes exactly zero
    # chance-corrected information:
    #   both-yes 90, A-yes/B-no 10, A-no/B-yes 0, both-no 0
    #   p_o = 90 / 100                              = 0.90
    #   A marginals: yes 100/100 = 1.0, no 0.0
    #   B marginals: yes  90/100 = 0.9, no 0.1
    #   p_e = 1.0 * 0.9 + 0.0 * 0.1                 = 0.90
    #   kappa = (0.90 - 0.90) / (1 - 0.90)          = 0.00 / 0.10 = 0.0
    always_yes = ["yes"] * 100
    discriminating = ["yes"] * 90 + ["no"] * 10
    assert mean_pairwise_agreement(
        list(zip(always_yes, discriminating, strict=True))
    ) == pytest.approx(0.90)
    assert cohens_kappa(always_yes, discriminating) == pytest.approx(0.0, abs=1e-12)
    # Raw agreement would have called this a 0.90 panel and licensed the label.
    assert cohens_kappa(always_yes, discriminating) < V1_POLICY.kappa_threshold


def test_cohens_kappa_is_undefined_rather_than_zero_on_degenerate_marginals():
    assert cohens_kappa(["yes"] * 8, ["yes"] * 8) is None  # p_e == 1, not kappa == 0
    assert cohens_kappa(["yes"], ["yes"]) is None  # fewer than two items
    assert cohens_kappa(["a", "b", "a", "b"], ["a", "b", "a", "b"]) == pytest.approx(1.0)


def test_fleiss_kappa_matches_the_hand_computed_three_rater_table():
    # 3 raters, 4 items, 2 categories. P_i = (sum_j n_ij^2 - m) / (m(m-1)), m = 3.
    #   item 1 (3,0): (9 + 0 - 3) / 6 = 1
    #   item 2 (0,3): (0 + 9 - 3) / 6 = 1
    #   item 3 (2,1): (4 + 1 - 3) / 6 = 1/3
    #   item 4 (1,2): (1 + 4 - 3) / 6 = 1/3
    #   P_bar   = (1 + 1 + 1/3 + 1/3) / 4          = 2/3
    #   p_true  = 6/12 = 0.5, p_false = 6/12 = 0.5
    #   P_bar_e = 0.25 + 0.25                      = 0.5
    #   kappa   = (2/3 - 1/2) / (1 - 1/2)          = (1/6) / (1/2) = 1/3
    ratings = [
        ["T", "T", "T"],
        ["F", "F", "F"],
        ["T", "T", "F"],
        ["T", "F", "F"],
    ]
    assert fleiss_kappa(ratings) == pytest.approx(1 / 3, abs=1e-12)
    #   raw (mean pairwise) agreement = P_bar = 2/3
    assert mean_pairwise_agreement(ratings) == pytest.approx(2 / 3, abs=1e-12)


def test_fleiss_kappa_endpoints():
    perfect = [["T", "T", "T"], ["T", "T", "T"], ["F", "F", "F"], ["F", "F", "F"]]
    assert fleiss_kappa(perfect) == pytest.approx(1.0)
    assert fleiss_kappa([["T", "T", "T"], ["T", "T", "T"]]) is None  # p_e == 1
    with pytest.raises(ValueError, match="same number of raters"):
        fleiss_kappa([["T", "T", "T"], ["T", "T"]])


# ------------------------------------------------------------------------ independence


def test_two_judges_sharing_a_lineage_fail_the_independence_witness():
    twins = [
        ScriptedJudge("judge-0", "lineage-shared", {"P1-C001": warranted()}),
        ScriptedJudge("judge-1", "lineage-shared", {"P1-C001": warranted()}),
    ]
    witness = panel_independence_witness(twins)
    assert witness.ok is False
    assert any("lineage_id" in failure for failure in witness.failures)

    with pytest.raises(IndependenceError, match="lineage_id"):
        run(["P1-C001"], twins)


def test_a_reused_judge_instance_and_a_shared_context_both_fail_the_witness():
    one = ScriptedJudge("judge-0", "lineage-0", {"P1-C001": warranted()})
    assert panel_independence_witness([one, one]).ok is False  # one object, not two judges

    a = ScriptedJudge("judge-0", "lineage-0", {"P1-C001": warranted()})
    b = ScriptedJudge("judge-1", "lineage-1", {"P1-C001": warranted()})
    shared = panel_independence_witness([a, b], context_ids=["ctx-1", "ctx-1"])
    assert shared.ok is False
    assert any("context" in failure for failure in shared.failures)

    # A backend that reuses one context across cases carries memory between them, so the
    # post-hoc witness voids the run rather than reporting a correlated panel as independent.
    two_cases = {"P1-C001": warranted(), "P1-C002": warranted()}
    leaky = ScriptedJudge("judge-1", "lineage-1", dict(two_cases), constant_context=True)
    with pytest.raises(IndependenceError, match="context"):
        adjudicate(
            views("P1-C001", "P1-C002"),
            [leaky, ScriptedJudge("judge-2", "lineage-2", dict(two_cases))],
            rubric_hash=FROZEN_RUBRIC_HASH,
        )


def test_the_witness_fails_closed_when_an_id_cannot_be_determined():
    class NoLineage:
        judge_id = "judge-0"

        def new_context(self) -> str:  # pragma: no cover - never reached
            return "ctx"

        def judge(self, view, **kwargs):  # pragma: no cover - never reached
            raise AssertionError("must not be invoked")

    missing = panel_independence_witness(
        [NoLineage(), ScriptedJudge("judge-1", "lineage-1", {})]
    )
    assert missing.ok is False
    assert any("lineage_id_declared" in failure for failure in missing.failures)
    # "could not determine" is never reported as "checked and distinct".
    assert any("undeterminable" in failure for failure in missing.failures)

    blank = panel_independence_witness(
        [ScriptedJudge("judge-0", "", {}), ScriptedJudge("judge-1", "lineage-1", {})]
    )
    assert blank.ok is False

    assert panel_independence_witness([ScriptedJudge("judge-0", "lineage-0", {})]).ok is False


def test_a_verdict_stamped_with_an_unissued_context_voids_the_run():
    judges = panel({"P1-C001": warranted()}, {"P1-C001": warranted()})
    judges[1].forced_context_id = "some-other-context"
    with pytest.raises(IndependenceError, match="did not issue"):
        run(["P1-C001"], judges)


# ---------------------------------------------------------------------- the gold boundary


def test_a_judge_can_never_reach_protected_gold():
    case = HiddenShiftCase(
        case_id="P1-C900",
        task_family=TaskFamily.EVIDENCE_ONLY_CONTROL,
        public_prompt="report the subsidiary revenue",
        observable_resources=("filings_index.csv",),
        protected_gold=ProtectedGold(
            reframe_required=False,
            responsibility_family="evidence",
            target_coordinates=(),
            dependencies_to_reopen=(),
            root_success_rubric="the standalone filing figure",
        ),
        budget_class="standard",
        adjudication_status=AdjudicationStatus.PILOT_ONLY,
        split=Split.PILOT,
    )

    # The type boundary: PublicView has no gold field at all, so blinding is not a discipline.
    assert "protected_gold" not in {f.name for f in fields(PublicView)}
    assert not hasattr(case.public_view, "protected_gold")

    # And the panel refuses the gold-carrying object outright rather than trusting the caller
    # to have projected it first.
    with pytest.raises(TypeError, match="PublicView only"):
        adjudicate(
            [case],  # type: ignore[list-item]
            panel({"P1-C900": not_warranted()}, {"P1-C900": not_warranted()}),
            rubric_hash=FROZEN_RUBRIC_HASH,
        )

    seen: list[PublicView] = []
    judges = panel({"P1-C900": not_warranted()}, {"P1-C900": not_warranted()})
    judges[0].seen_views = seen
    adjudicate([case.public_view], judges, rubric_hash=FROZEN_RUBRIC_HASH)
    assert seen == [case.public_view]


# -------------------------------------------------------------------- panel resolution


def test_unanimous_panel_labels_every_case_on_a_non_degenerate_batch():
    script = {
        "P1-C001": warranted(),
        "P1-C002": warranted(),
        "P1-C003": not_warranted(),
        "P1-C004": not_warranted(),
    }
    report = run(list(script), panel(dict(script), dict(script)))

    assert len(report.records) == 4
    assert len(report.adjudicated_records) == 4
    for record in report.records:
        assert record.status is AdjudicationStatus.MODEL_ADJUDICATED
        assert record.outcome is PanelOutcome.UNANIMOUS
        assert record.adjudicator_kind == ADJUDICATOR_KIND
        assert record.resolution(Question.REFRAME_WARRANTED).dissenting_judges == ()
    assert report.records[0].resolved_reframe_warranted is True
    assert report.records[0].resolved_responsibility_class == "measurement"
    assert report.records[0].resolved_reopen == ("C-baseline-estimate",)
    assert report.records[3].resolved_reframe_warranted is False

    # Two labels, two judges, perfect agreement: kappa is defined and equals exactly 1.
    primary = report.agreement_for(Question.REFRAME_WARRANTED)
    assert primary.method == "cohen"
    assert primary.kappa == pytest.approx(1.0)
    assert primary.raw_agreement == pytest.approx(1.0)
    assert primary.unanimity_rate == pytest.approx(1.0)
    assert primary.degenerate is False
    # Agreement is reported per question, never as one pooled number.
    assert {r.question for r in report.agreement} == set(Question)


def test_a_batch_with_one_category_labels_but_is_flagged_degenerate():
    script = {"P1-C001": warranted(), "P1-C002": warranted(), "P1-C003": warranted()}
    report = run(list(script), panel(dict(script), dict(script)))

    assert len(report.adjudicated_records) == 3
    primary = report.agreement_for(Question.REFRAME_WARRANTED)
    assert primary.kappa is None
    assert primary.kappa_undefined_reason == "degenerate_marginals"
    assert primary.degenerate is True
    assert primary.raw_agreement == pytest.approx(1.0)
    # Unanimity labels without a kappa gate; the caveat is published, not swallowed.
    assert report.records[0].resolution(Question.REFRAME_WARRANTED).kappa_at_decision is None


def test_a_one_one_split_yields_cannot_check_and_never_a_coin_flip():
    left = {"P1-C001": warranted(), "P1-C002": not_warranted(), "P1-C003": warranted()}
    right = {"P1-C001": warranted(), "P1-C002": not_warranted(), "P1-C003": not_warranted()}
    report = run(["P1-C001", "P1-C002", "P1-C003"], panel(left, right))

    split = report.records[2]
    assert split.case_id == "P1-C003"
    assert split.status is None
    assert split.outcome is PanelOutcome.CANNOT_CHECK
    resolution = split.resolution(Question.REFRAME_WARRANTED)
    assert resolution.cannot_check_reason is CannotCheckReason.NO_MAJORITY
    assert resolution.label is None
    assert split.resolved_reframe_warranted is None
    assert split.included_in_adjudicated_analysis is False

    # Excluded from adjudicated analysis, retained in the archive with both verdicts intact.
    assert split in report.excluded_records
    assert split in report.records
    assert len(split.verdicts) == 2
    assert {v.reframe_warranted for v in split.verdicts} == {True, False}

    # Reversing the judge order cannot change the outcome: order is not a tiebreak.
    mirrored = run(["P1-C001", "P1-C002", "P1-C003"], panel(right, left))
    assert mirrored.records[2].status is None


def test_an_abstention_that_breaks_quorum_yields_cannot_check():
    left = {"P1-C001": warranted(), "P1-C002": not_warranted(), "P1-C003": warranted()}
    right = {"P1-C001": warranted(), "P1-C002": not_warranted(), "P1-C003": abstained()}
    report = run(["P1-C001", "P1-C002", "P1-C003"], panel(left, right))

    record = report.records[2]
    assert record.status is None
    resolution = record.resolution(Question.REFRAME_WARRANTED)
    assert resolution.cannot_check_reason is CannotCheckReason.ABSTENTION_BREAKS_QUORUM
    assert resolution.abstaining_judges == ("judge-1",)
    assert resolution.label is None

    # The abstained item is dropped from kappa and the drop is reported, not hidden.
    primary = report.agreement_for(Question.REFRAME_WARRANTED)
    assert primary.n_items_abstained == 1
    assert primary.n_items_complete == 2
    # The other two cases still resolve — one abstention does not void the batch.
    assert len(report.adjudicated_records) == 2


def test_majority_below_the_kappa_floor_degrades_to_cannot_check():
    # Fleiss table hand-checked above: kappa = 1/3, below the frozen 0.6 floor.
    #   c1 (T,T,T)  c2 (F,F,F)  c3 (T,T,F)  c4 (T,F,F)
    a = {"P1-C001": warranted(), "P1-C002": not_warranted(), "P1-C003": warranted(),
         "P1-C004": warranted()}
    b = {"P1-C001": warranted(), "P1-C002": not_warranted(), "P1-C003": warranted(),
         "P1-C004": not_warranted()}
    c = {"P1-C001": warranted(), "P1-C002": not_warranted(), "P1-C003": not_warranted(),
         "P1-C004": not_warranted()}
    report = run(["P1-C001", "P1-C002", "P1-C003", "P1-C004"], panel(a, b, c))

    primary = report.agreement_for(Question.REFRAME_WARRANTED)
    assert primary.method == "fleiss"
    assert primary.kappa == pytest.approx(1 / 3, abs=1e-12)

    for case_id in ("P1-C003", "P1-C004"):
        record = next(r for r in report.records if r.case_id == case_id)
        resolution = record.resolution(Question.REFRAME_WARRANTED)
        assert resolution.outcome is PanelOutcome.CANNOT_CHECK
        assert resolution.cannot_check_reason is CannotCheckReason.AGREEMENT_BELOW_THRESHOLD
        assert resolution.label is None  # 2-1 majority existed and was NOT taken
        assert record.status is None

    # Unanimous cases are unaffected: kappa gates majorities, not unanimity.
    assert {r.case_id for r in report.adjudicated_records} == {"P1-C001", "P1-C002"}


def test_majority_above_the_kappa_floor_labels_and_records_the_dissent():
    # 3 judges, 5 items: four unanimous, one 2-1.
    #   P_bar   = (1 + 1 + 1 + 1 + 1/3) / 5 = 13/15
    #   p_T = 8/15, p_F = 7/15 -> P_bar_e = 113/225
    #   kappa = (13/15 - 113/225) / (1 - 113/225) = 82/112 = 41/56 = 0.7321...
    base = {
        "P1-C001": warranted(),
        "P1-C002": warranted(),
        "P1-C003": not_warranted(),
        "P1-C004": not_warranted(),
        "P1-C005": warranted(),
    }
    dissenter = dict(base) | {"P1-C005": not_warranted()}
    report = run(list(base), panel(dict(base), dict(base), dissenter))

    primary = report.agreement_for(Question.REFRAME_WARRANTED)
    assert primary.kappa == pytest.approx(41 / 56, abs=1e-12)
    assert primary.kappa >= V1_POLICY.kappa_threshold

    record = next(r for r in report.records if r.case_id == "P1-C005")
    resolution = record.resolution(Question.REFRAME_WARRANTED)
    assert resolution.outcome is PanelOutcome.MAJORITY_WITH_DISSENT
    assert resolution.label is True
    assert resolution.dissenting_judges == ("judge-2",)
    assert record.status is AdjudicationStatus.MODEL_ADJUDICATED
    assert len(report.adjudicated_records) == 5


def test_a_single_case_panel_can_be_unanimous_but_never_a_majority():
    # kappa needs items, so a one-case panel has none: unanimity is the only route to a label.
    unanimous = run(["P1-C001"], panel({"P1-C001": warranted()}, {"P1-C001": warranted()}))
    assert unanimous.records[0].status is AdjudicationStatus.MODEL_ADJUDICATED
    assert unanimous.agreement_for(Question.REFRAME_WARRANTED).kappa_undefined_reason == (
        "insufficient_items"
    )

    three = panel(
        {"P1-C001": warranted()}, {"P1-C001": warranted()}, {"P1-C001": not_warranted()}
    )
    split = run(["P1-C001"], three)
    resolution = split.records[0].resolution(Question.REFRAME_WARRANTED)
    assert resolution.cannot_check_reason is CannotCheckReason.AGREEMENT_UNDEFINED
    assert split.records[0].status is None


def test_questions_resolve_independently_of_one_another():
    left = {"P1-C001": warranted(), "P1-C002": warranted(reopen=("C-a",))}
    right = {"P1-C001": warranted(), "P1-C002": warranted(reopen=None)}
    report = run(["P1-C001", "P1-C002"], panel(left, right))

    record = report.records[1]
    # The primary question is labelled; the reopen question abstained past quorum.
    assert record.status is AdjudicationStatus.MODEL_ADJUDICATED
    assert record.resolved_reframe_warranted is True
    reopen = record.resolution(Question.REOPEN_SET)
    assert reopen.outcome is PanelOutcome.CANNOT_CHECK
    assert reopen.cannot_check_reason is CannotCheckReason.ABSTENTION_BREAKS_QUORUM
    assert record.resolved_reopen is None
    # Per-question inclusion, not case status, is what gates a metric.
    assert record.resolution(Question.REFRAME_WARRANTED).included is True
    assert reopen.included is False
    assert report.agreement_for(Question.REOPEN_SET).n_items_abstained == 1


# -------------------------------------------------------------------- provenance tiers


def test_the_panel_can_only_ever_claim_the_model_tier():
    assert AdjudicationStatus.MODEL_ADJUDICATED.value == "MODEL_ADJUDICATED"
    assert AdjudicationStatus.MODEL_ADJUDICATED is not AdjudicationStatus.ADJUDICATED
    assert AdjudicationStatus.MODEL_ADJUDICATED is not AdjudicationStatus.MECHANICAL_GOLD

    report = run(["P1-C001"], panel({"P1-C001": warranted()}, {"P1-C001": warranted()}))
    record = report.records[0]
    for forbidden in (
        AdjudicationStatus.ADJUDICATED,
        AdjudicationStatus.MECHANICAL_GOLD,
        AdjudicationStatus.DOUBLE_ANNOTATED,
        AdjudicationStatus.PILOT_ONLY,
    ):
        with pytest.raises(ValueError, match="may only emit MODEL_ADJUDICATED"):
            replace(record, status=forbidden)
    with pytest.raises(ValueError, match="adjudicator_kind is fixed"):
        replace(record, adjudicator_kind="human_panel")


def test_the_report_is_model_based_and_machine_readable():
    report = run(
        ["P1-C001", "P1-C002"],
        panel(
            {"P1-C001": warranted(), "P1-C002": not_warranted()},
            {"P1-C001": warranted(), "P1-C002": not_warranted()},
        ),
    )
    assert report.human_adjudication is False
    assert report.adjudicator_kind == ADJUDICATOR_KIND == "model_panel"
    with pytest.raises(ValueError, match="may not be recorded as human"):
        replace(report, human_adjudication=True)

    payload = json.loads(json.dumps(report.to_dict()))
    assert payload["adjudicator_kind"] == "model_panel"
    assert payload["human_adjudication"] is False
    assert payload["rubric_hash"] == FROZEN_RUBRIC_HASH
    assert payload["policy_hash"] == FROZEN_POLICY_HASH
    assert payload["independence"]["ok"] is True
    assert len(payload["agreement"]) == 3
    assert payload["records"][0]["status"] == "MODEL_ADJUDICATED"
    # panel_id is content-addressed over rubric, policy, judges and cases.
    assert len(report.panel_id) == 64


def test_a_record_may_not_claim_a_status_its_resolutions_do_not_support():
    split = run(
        ["P1-C001", "P1-C002", "P1-C003"],
        panel(
            {"P1-C001": warranted(), "P1-C002": not_warranted(), "P1-C003": warranted()},
            {"P1-C001": warranted(), "P1-C002": not_warranted(), "P1-C003": not_warranted()},
        ),
    ).records[2]
    with pytest.raises(ValueError, match="status disagrees"):
        AdjudicationRecord(
            case_id=split.case_id,
            verdicts=split.verdicts,
            resolutions=split.resolutions,
            agreement=split.agreement,
            status=AdjudicationStatus.MODEL_ADJUDICATED,
        )


# ------------------------------------------------------------------- verdict coherence


def test_a_verdict_must_be_internally_coherent_with_the_rubric():
    def build(**overrides) -> JudgeVerdict:
        payload = {
            "case_id": "P1-C001",
            "judge_id": "judge-0",
            "lineage_id": "lineage-0",
            "context_id": "ctx-1",
            "rubric_hash": FROZEN_RUBRIC_HASH,
            "reframe_warranted": True,
            "responsibility_class": ResponsibilityClass.MEASUREMENT,
            "coordinates": ("metric_definition",),
            "rationale": "R3(4)",
        }
        payload.update(overrides)
        return JudgeVerdict(**payload)  # type: ignore[arg-type]

    build()  # the coherent baseline

    # R2: evidence and execution never warrant a reframe.
    with pytest.raises(ValueError, match="incoherent"):
        build(responsibility_class=ResponsibilityClass.EVIDENCE)
    with pytest.raises(ValueError, match="incoherent"):
        build(reframe_warranted=False, responsibility_class=ResponsibilityClass.MEASUREMENT)
    # R5: a warranted reframe must name what it revises.
    with pytest.raises(ValueError, match="must name coordinates"):
        build(coordinates=())
    # Section 5: an abstention carries no answer to smuggle back in.
    with pytest.raises(ValueError, match="may not carry an answer"):
        build(reframe_warranted=None)
    # An unexplained verdict is not auditable.
    with pytest.raises(ValueError, match="not auditable"):
        build(rationale="   ")
    with pytest.raises(ValueError, match="confidence"):
        build(confidence=1.5)
    with pytest.raises(ValueError, match="sha256"):
        build(rubric_hash="not-a-digest")

    # A non-reframe reopens nothing, as a derived claim rather than an abstention.
    negative = build(
        reframe_warranted=False,
        responsibility_class=ResponsibilityClass.EXECUTION,
        coordinates=(),
    )
    assert negative.reopen == ()
    # Reopen sets are canonicalised so set identity, not authoring order, drives agreement.
    assert build(reopen=("C-b", "C-a", "C-b")).reopen == ("C-a", "C-b")


def test_off_vocabulary_coordinates_are_surfaced_rather_than_silently_dropped():
    script = {
        "P1-C001": warranted() | {"coordinates": ("metric_definition", "vibes")},
    }
    report = run(["P1-C001"], panel(dict(script), dict(script)))
    assert report.off_vocabulary_coordinates == ("judge-0:vibes", "judge-1:vibes")


def test_duplicate_cases_and_undersized_panels_are_refused():
    with pytest.raises(ValueError, match="duplicate case ids"):
        adjudicate(
            [view("P1-C001"), view("P1-C001")],
            panel({"P1-C001": warranted()}, {"P1-C001": warranted()}),
            rubric_hash=FROZEN_RUBRIC_HASH,
        )
    with pytest.raises(IndependenceError, match="panel_size"):
        run(["P1-C001"], panel({"P1-C001": warranted()}))
    with pytest.raises(ValueError, match="fewer than two judges"):
        DisagreementPolicy(
            policy_id="bad",
            min_judges=1,
            quorum=2,
            kappa_threshold=0.6,
            require_defined_kappa_for_majority=True,
            require_strict_majority=True,
        )
