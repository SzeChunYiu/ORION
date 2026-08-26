"""The systems under test and the run harness, checked against the protocol.

Fixtures are authored here rather than loaded from ``protocol/cases/**``: these
tests must falsify *this* code, not the suite, and must keep working while the
frozen suite is still being written.

**Two panels, and the difference matters.**

``mechanism_panel`` states each formulation defect in prose the shared lexical
detector can read ("expressed in different forms", "the parts do not compose").
It exists to prove the decision policies differ as specified — that ORION
reframes the coordinate it diagnosed, that each ablation loses exactly its
organ, that reopening follows the transitive basis. **Its numbers are unit-test
outputs, not study results.** Nobody should quote them as benchmark scores.

``suite_shaped_panel`` imitates the frozen suite instead: the phenomenon is
described in symptoms and numbers, and the gold vocabulary appears nowhere,
because the suite author's degeneracy probe rejects any public field that lets a
blind responder recover the label. On those cases a mechanical system detects no
formulation residual and **abstains** — and `test_the_mechanical_arm_abstains_on
_suite_shaped_hidden_shift` pins that as the honest expected result rather than
letting it be discovered later as a surprise.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from orion.study.p1.baselines import (
    BASELINE_IDS,
    baseline_systems,
    budget_for,
    extract_cues,
    descendants_of,
    public_closures,
    readable_resources,
)
from orion.study.p1.cases import (
    AdjudicationStatus,
    load_cases,
    HiddenShiftCase,
    ProtectedGold,
    PublicView,
    Split,
    TaskFamily,
)
from orion.study.p1.harness import (
    PROTOCOL_PATH,
    RunStatus,
    default_seeds,
    read_archive,
    run_study,
    stochastic_repeats_from_protocol,
)
from orion.study.p1.orion_system import (
    ABLATION_IDS,
    OrionSystem,
    ablation_systems,
    full_orion,
    orion_systems,
)
from orion.study.p1.provider import (
    DEFAULT_MODEL,
    CREDENTIAL_ENV_VAR,
    AnthropicProvider,
    ProviderBackedSystem,
    ProviderStatus,
    ProviderUnavailable,
    credential_present,
)
from orion.study.p1.systems import ResourceUse, SystemTrace

BUDGET_CLASS = "p1_standard_v1"


def _case(
    case_id: str,
    family: TaskFamily,
    prompt: str,
    resources: tuple[str, ...],
    gold: ProtectedGold,
) -> HiddenShiftCase:
    return HiddenShiftCase(
        case_id=case_id,
        task_family=family,
        public_prompt=prompt,
        observable_resources=resources,
        protected_gold=gold,
        budget_class=BUDGET_CLASS,
        adjudication_status=AdjudicationStatus.PILOT_ONLY,
        split=Split.PILOT,
    )


def mechanism_panel() -> tuple[HiddenShiftCase, ...]:
    """Six families, nine cases, every gold responsibility represented.

    Instrumented: each formulation defect is stated in prose the lexical
    detector reads. Real suite cases do not read like this — see
    `suite_shaped_panel`.
    """

    return (
        _case(
            "p1-c001",
            TaskFamily.EVIDENCE_ONLY_CONTROL,
            "The projected Q3 total has no source in the workbook; it appears "
            "only on a slide. The chart is drawn on a log scale. Confirm the "
            "figure before the summary ships.",
            ("workbook:q3-projection", "slide:board-deck"),
            ProtectedGold(
                reframe_required=False,
                responsibility_family="EVIDENCE",
                target_coordinates=(),
                dependencies_to_reopen=(),
                root_success_rubric="the figure is traced to a primary record",
            ),
        ),
        _case(
            "p1-c002",
            TaskFamily.EXECUTION_ONLY_CONTROL,
            "The nightly job crashes on the third batch with a traceback in the "
            "index computation. The dashboard renders on a log scale. Get the "
            "run green again.",
            ("repo:etl-nightly", "log:nightly-run"),
            ProtectedGold(
                reframe_required=False,
                responsibility_family="EXECUTION",
                target_coordinates=(),
                dependencies_to_reopen=(),
                root_success_rubric="the job completes and the batch is correct",
            ),
        ),
        _case(
            "p1-c003",
            TaskFamily.HIDDEN_PARENT_DOMAIN,
            "Wait time explodes as arrival rate approaches service rate even "
            "though mean utilisation stays under 70 percent. The same behaviour is "
            "standard elsewhere. The team's metric dashboards show nothing "
            "wrong and no component is at fault.",
            (
                "closure:capacity-headroom closed under the assumption that no "
                "result from an adjacent field applies here",
                "dataset:arrival-log",
            ),
            ProtectedGold(
                reframe_required=True,
                responsibility_family="SEARCH",
                target_coordinates=("W.ACTIVE_DOMAINS", "parent_domain:queueing_theory"),
                dependencies_to_reopen=("closure:capacity-headroom",),
                root_success_rubric="capacity is predicted from the right model",
                dependency_depth=1,
            ),
        ),
        _case(
            "p1-c004",
            TaskFamily.HIDDEN_REPRESENTATION,
            "Two series that should agree diverge by three orders of magnitude; "
            "they are expressed in different forms. The metric dashboard was "
            "rebuilt last quarter and the data contract was reviewed.",
            (
                "closure:baseline-fit closed under the assumption that both "
                "series are in the same units",
                "closure:sampling-window closed under the assumption that the "
                "nightly export was complete",
                "dataset:series-a",
            ),
            ProtectedGold(
                reframe_required=True,
                responsibility_family="REPRESENTATION",
                target_coordinates=(
                    "W.REPRESENTATIONS",
                    "representation:unit_normalisation",
                ),
                dependencies_to_reopen=("closure:baseline-fit",),
                root_success_rubric="the two series are compared in one form",
                dependency_depth=1,
            ),
        ),
        _case(
            "p1-c005",
            TaskFamily.HIDDEN_DECOMPOSITION,
            "Each part passes on its own and the assembled pipeline still "
            "fails: the parts do not compose. The metric dashboard is "
            "unchanged and the sampling basis was not touched.",
            (
                "closure:stage-signoff closed under the assumption that the "
                "stages were assumed independent",
                "repo:pipeline",
            ),
            ProtectedGold(
                reframe_required=True,
                responsibility_family="DECOMPOSITION",
                target_coordinates=("W.DECOMPOSITION", "decomposition:stage_coupling"),
                dependencies_to_reopen=("closure:stage-signoff",),
                root_success_rubric="the pipeline succeeds end to end",
                dependency_depth=1,
            ),
        ),
        _case(
            "p1-c006",
            TaskFamily.HIDDEN_DECOMPOSITION,
            "Writes accepted by the producer are silently dropped by the "
            "consumer under load; the format expected by the consumer changed "
            "in March. The metric dashboard shows nothing and the literature "
            "was not consulted.",
            (
                "closure:delivery-guarantee closed under the assumption that "
                "the handoff format is stable",
                "service:consumer",
            ),
            ProtectedGold(
                reframe_required=True,
                responsibility_family="INTERFACE",
                target_coordinates=("W.INTERFACE", "interface:transactional_outbox"),
                dependencies_to_reopen=("closure:delivery-guarantee",),
                root_success_rubric="no accepted write is lost",
                dependency_depth=1,
            ),
        ),
        _case(
            "p1-c007",
            TaskFamily.HIDDEN_MEASUREMENT,
            "The reported average hides a bimodal distribution and the team "
            "keeps optimising the wrong thing. Literature on the topic is thin "
            "and the data contract is old.",
            (
                "closure:throughput-target closed under the assumption that the "
                "reported metric tracks user experience",
                "dataset:latency-histogram",
            ),
            ProtectedGold(
                reframe_required=True,
                responsibility_family="MEASUREMENT",
                target_coordinates=("M.MEASUREMENT", "measurement:goodput_definition"),
                dependencies_to_reopen=("closure:throughput-target",),
                root_success_rubric="the reported quantity tracks the objective",
                dependency_depth=1,
            ),
        ),
        _case(
            "p1-c008",
            TaskFamily.HIDDEN_MEASUREMENT,
            "Two reviewers using the same rubric disagree on half the items. "
            "Literature on the topic is thin and the sampling basis is unclear.",
            (
                "closure:accepted-answers closed under the assumption that the "
                "scoring function is faithful",
                "log:review-round-two",
            ),
            ProtectedGold(
                reframe_required=True,
                responsibility_family="EVALUATOR",
                target_coordinates=("M.EVALUATOR", "evaluator:acceptance_criteria"),
                dependencies_to_reopen=("closure:accepted-answers",),
                root_success_rubric="the acceptance decision is reproducible",
                dependency_depth=1,
            ),
        ),
        _case(
            "p1-c009",
            TaskFamily.HIDDEN_REPRESENTATION,
            "The forecast and the ledger disagree by three orders of magnitude "
            "and are expressed in different units; the metric dashboard shows "
            "nothing. The data contract is old.",
            (
                "closure:unit-audit closed under the assumption that both "
                "feeds are in the same units",
                "closure:capacity-plan closed under closure:unit-audit",
                "closure:board-brief closed under closure:capacity-plan",
                "dataset:ledger",
            ),
            ProtectedGold(
                reframe_required=True,
                responsibility_family="REPRESENTATION",
                target_coordinates=("W.REPRESENTATIONS", "representation:unit_scaling"),
                # A depth-3 chain: the coordinate is declared only on the head,
                # and the tail is reachable only transitively.
                dependencies_to_reopen=(
                    "closure:unit-audit",
                    "closure:capacity-plan",
                    "closure:board-brief",
                ),
                root_success_rubric="the two feeds are compared in one form",
                dependency_depth=3,
            ),
        ),
    )


def panel() -> tuple[HiddenShiftCase, ...]:
    """The panel the infrastructure tests run on.

    Deliberately the instrumented one: a harness test needs systems that
    actually act, and a panel where every system abstains would prove nothing
    about archiving, budgets or determinism.
    """

    return mechanism_panel()


def suite_shaped_panel() -> tuple[HiddenShiftCase, ...]:
    """What the frozen suite actually looks like.

    Symptoms and numbers; no gold vocabulary anywhere; closure chains spelled
    the way the suite author confirmed (`derived from closure:<slug>`); and
    negative controls that carry closure lines of their own with an empty
    `dependencies_to_reopen`, so resource bulk cannot separate control from
    hidden-shift.
    """

    return (
        _case(
            "p1-s001",
            TaskFamily.EVIDENCE_ONLY_CONTROL,
            "The Q3 total of 4.1M appears on slide 12 and in no workbook; it "
            "has not been retrieved from any primary record. Confirm it before "
            "the summary ships.",
            (
                "closure:forecast-band-v2 — closed; assumes the Q3 total is "
                "within 5 percent of the prior quarter",
                "slide:board-deck",
                "workbook:q3-projection",
            ),
            ProtectedGold(
                reframe_required=False,
                responsibility_family="EVIDENCE",
                target_coordinates=(),
                dependencies_to_reopen=(),
                root_success_rubric="the figure is traced to a primary record",
            ),
        ),
        _case(
            "p1-s002",
            TaskFamily.EXECUTION_ONLY_CONTROL,
            "The nightly job crashes on batch 3 of 40 with a traceback at "
            "line 214. Batches 1 and 2 wrote 1.2M rows correctly. Get the run "
            "green again.",
            (
                "closure:row-count-check — closed; assumes each batch writes "
                "between 300k and 500k rows",
                "repo:etl-nightly",
                "log:nightly-run",
            ),
            ProtectedGold(
                reframe_required=False,
                responsibility_family="EXECUTION",
                target_coordinates=(),
                dependencies_to_reopen=(),
                root_success_rubric="the job completes and batch 3 is correct",
            ),
        ),
        _case(
            "p1-s003",
            TaskFamily.HIDDEN_PARENT_DOMAIN,
            "Wait time rises from 40ms to 900ms as arrival rate goes from "
            "180/s to 195/s, while mean CPU usage stays at 0.62. Adding a "
            "third worker moved the knee but did not remove it.",
            (
                "closure:capacity-plan-v3 — closed; assumes headroom is "
                "linear in mean usage",
                "closure:alert-thresholds-v2 — closed; derived from "
                "closure:capacity-plan-v3, pages when mean usage exceeds 0.85",
                "dataset:arrival-log",
            ),
            ProtectedGold(
                reframe_required=True,
                responsibility_family="SEARCH",
                target_coordinates=("W.ACTIVE_DOMAINS", "parent_domain:queueing_theory"),
                dependencies_to_reopen=(
                    "closure:capacity-plan-v3",
                    "closure:alert-thresholds-v2",
                ),
                root_success_rubric="capacity is predicted from the right model",
                dependency_depth=2,
            ),
        ),
        _case(
            "p1-s004",
            TaskFamily.HIDDEN_MEASUREMENT,
            "The dashboard reports 99.2 percent success while three of the "
            "eight largest customers filed tickets the same week. Both numbers "
            "are computed from the same request table.",
            (
                "closure:sla-signoff-v1 — closed; assumes the reported rate "
                "reflects customer outcome",
                "dataset:request-table",
            ),
            ProtectedGold(
                reframe_required=True,
                responsibility_family="MEASUREMENT",
                target_coordinates=("M.MEASUREMENT", "measurement:per_customer_weighting"),
                dependencies_to_reopen=("closure:sla-signoff-v1",),
                root_success_rubric="the reported quantity tracks the objective",
                dependency_depth=1,
            ),
        ),
    )


def ambiguous_case() -> HiddenShiftCase:
    """Two strong formulation observations, no discriminator between them.

    Deliberately outside `panel()`: full ORION *declines* to reframe here, and
    that is the doctrine working, not a bug. `revision_allowed` blocks
    high-impact revision while responsibility is ambiguous, so the case is a
    conservative miss rather than a confident wrong reframe. Keeping it out of
    the panel keeps the honest 8/8 honest; keeping it tested means the branch
    is not discovered on the frozen suite.
    """

    return _case(
        "p1-c010",
        TaskFamily.HIDDEN_DECOMPOSITION,
        "The handoff format is stable on paper yet the stages were assumed "
        "independent, and either reading explains the loss.",
        ("service:consumer", "repo:pipeline"),
        ProtectedGold(
            reframe_required=True,
            responsibility_family="INTERFACE",
            target_coordinates=("W.INTERFACE", "interface:delivery_contract"),
            dependencies_to_reopen=(),
            root_success_rubric="the loss is eliminated",
            dependency_depth=1,
        ),
    )


def all_systems():
    return (*baseline_systems(), *orion_systems())


def case_by_id(case_id: str) -> HiddenShiftCase:
    return next(item for item in panel() if item.case_id == case_id)


CONTROL_IDS = ("p1-c001", "p1-c002")
HIDDEN_IDS = (
    "p1-c003",
    "p1-c004",
    "p1-c005",
    "p1-c006",
    "p1-c007",
    "p1-c008",
    "p1-c009",
)
SEEDS = (0, 1, 2, 3, 4)


# --------------------------------------------------------------------------
# Protocol conformance
# --------------------------------------------------------------------------


def test_system_ids_match_the_frozen_protocol():
    protocol = json.loads(PROTOCOL_PATH.read_text())
    assert list(BASELINE_IDS) == protocol["baselines"]
    assert list(ABLATION_IDS) == protocol["ablations"]
    assert [item.system_id for item in baseline_systems()] == protocol["baselines"]
    assert [item.system_id for item in ablation_systems()] == protocol["ablations"]


def test_every_system_satisfies_the_system_under_test_contract():
    for system in all_systems():
        assert isinstance(system.system_id, str) and system.system_id
        for case in panel():
            trace = system.run(case.public_view, seed=0)
            assert isinstance(trace, SystemTrace)
            assert trace.case_id == case.case_id
            assert trace.system_id == system.system_id
            assert trace.seed == 0
            # A non-reframe may not smuggle a target in.
            if not trace.reframed:
                assert trace.target_coordinates == ()


def test_seeds_default_to_the_protocol_repeat_count():
    assert stochastic_repeats_from_protocol() == 5
    assert len(default_seeds()) == 5


# --------------------------------------------------------------------------
# The access boundary
# --------------------------------------------------------------------------


def test_public_view_carries_no_gold_and_cannot_be_widened_silently():
    """The field set is the boundary; a later widening must fail this test."""

    assert {field.name for field in dataclasses.fields(PublicView)} == {
        "case_id",
        "public_prompt",
        "observable_resources",
        "budget_class",
    }
    view = case_by_id("p1-c004").public_view
    for forbidden in ("protected_gold", "task_family", "split", "adjudication_status"):
        assert not hasattr(view, forbidden)
    with pytest.raises(AttributeError):
        view.protected_gold  # type: ignore[attr-defined]


def test_harness_never_hands_a_case_to_a_system(tmp_path: Path):
    """A system may only ever be given the public view."""

    seen: list[object] = []

    class Spy:
        system_id = "spy"

        def run(self, view, *, seed: int) -> SystemTrace:
            seen.append(view)
            return SystemTrace(case_id=view.case_id, system_id=self.system_id, seed=seed, reframed=False)

    run_study(panel(), (Spy(),), seeds=(0,), archive_path=tmp_path / "spy.jsonl")

    assert len(seen) == len(panel())
    for observed in seen:
        assert isinstance(observed, PublicView)
        assert not isinstance(observed, HiddenShiftCase)
        assert not hasattr(observed, "protected_gold")


def test_a_system_cannot_reach_gold_through_the_view():
    """Even a system that tries gets a typed refusal, not a value."""

    class Cheater:
        system_id = "cheater"

        def run(self, view, *, seed: int) -> SystemTrace:
            gold = getattr(view, "protected_gold", None)
            family = getattr(view, "task_family", None)
            assert gold is None and family is None
            return SystemTrace(case_id=view.case_id, system_id=self.system_id, seed=seed, reframed=False)

    archive = run_study(panel(), (Cheater(),), seeds=(0,))
    assert all(record.status is RunStatus.OK for record in archive.records)


# --------------------------------------------------------------------------
# Baselines: genuine attempts, not strawmen
# --------------------------------------------------------------------------


def _outcomes(system) -> dict[str, list[bool]]:
    results: dict[str, list[bool]] = {}
    for case in panel():
        results[case.case_id] = [
            system.run(case.public_view, seed=seed).root_solved for seed in SEEDS
        ]
    return results


def test_every_baseline_is_non_degenerate():
    """Each baseline must score above zero somewhere and below one somewhere."""

    for system in baseline_systems():
        results = _outcomes(system)
        flat = [value for values in results.values() for value in values]
        assert any(flat), f"{system.system_id} scored 0 everywhere: strawman"
        assert not all(flat), f"{system.system_id} scored 1 everywhere: no signal"


def test_every_baseline_solves_both_negative_controls():
    """Not reframing is correct here, and every baseline must actually solve it."""

    for system in baseline_systems():
        for case_id in CONTROL_IDS:
            trace = system.run(case_by_id(case_id).public_view, seed=0)
            assert trace.root_solved, f"{system.system_id} failed control {case_id}"
            assert not trace.abstained, "abstention is not a correct non-reframe"


def test_baselines_win_the_cases_in_their_own_coordinate():
    """A baseline whose coordinate matches the defect must succeed on it."""

    by_id = {system.system_id: system for system in baseline_systems()}
    interface = by_id["arex_like_recursive_audit_followup"].run(
        case_by_id("p1-c006").public_view, seed=0
    )
    assert interface.root_solved and interface.reframed
    decomposition = by_id["scion_like_dependency_execution_plan"].run(
        case_by_id("p1-c005").public_view, seed=0
    )
    assert decomposition.root_solved and decomposition.reopened


def test_static_react_never_reframes_and_attributes_to_surface_layers():
    system = next(
        item
        for item in baseline_systems()
        if item.system_id == "static_react_tool_workflow"
    )
    for case in panel():
        trace = system.run(case.public_view, seed=0)
        assert not trace.reframed
        assert trace.responsibility_family in {"", "EVIDENCE", "EXECUTION"}


def test_tree_search_types_no_responsibility():
    system = next(
        item
        for item in baseline_systems()
        if item.system_id == "tree_search_iterative_research"
    )
    for case in panel():
        for seed in SEEDS:
            trace = system.run(case.public_view, seed=seed)
            assert trace.responsibility_family == ""
            assert trace.target_coordinates == ()


def test_iris_revises_only_the_claim_coordinate():
    system = next(
        item
        for item in baseline_systems()
        if item.system_id == "iris_like_information_state_revision"
    )
    trace = system.run(case_by_id("p1-c004").public_view, seed=0)
    assert trace.reframed
    assert trace.target_coordinates == ("K.CLAIMS",)
    # Naming the responsibility is not repairing the coordinate.
    assert not trace.root_solved


# --------------------------------------------------------------------------
# ORION and its ablations
# --------------------------------------------------------------------------


def test_full_orion_solves_the_hidden_shift_families():
    orion = full_orion()
    for case_id in HIDDEN_IDS:
        trace = orion.run(case_by_id(case_id).public_view, seed=0)
        assert trace.root_solved, f"ORION failed {case_id}"
        assert trace.reframed
        gold = case_by_id(case_id).protected_gold
        assert trace.responsibility_family == gold.responsibility_family
        assert trace.target_coordinates == gold.target_coordinates[:1]


def test_full_orion_does_not_reframe_the_negative_controls():
    orion = full_orion()
    for case_id in CONTROL_IDS:
        trace = orion.run(case_by_id(case_id).public_view, seed=0)
        assert not trace.reframed
        assert not trace.abstained
        assert trace.root_solved
        assert trace.reopened == ()


def test_full_orion_reopens_exactly_the_dependent_closure():
    orion = full_orion()
    for case_id in HIDDEN_IDS:
        case = case_by_id(case_id)
        trace = orion.run(case.public_view, seed=0)
        assert set(trace.reopened) == set(case.protected_gold.dependencies_to_reopen)


def test_every_system_spends_exactly_the_same_resources():
    """Matched in fact, not only capped.

    The protocol's `resource_policy` forbids winning on budget. Rounds and
    probes are planned from the shared perception layer before any policy
    branches, so a difference in outcome cannot be a difference in spend.
    """

    reference = full_orion()
    for case in panel():
        for seed in SEEDS:
            expected = reference.run(case.public_view, seed=seed).resources
            for system in all_systems():
                spent = system.run(case.public_view, seed=seed).resources
                assert spent.tool_calls == expected.tool_calls, system.system_id
                assert spent.search_queries == expected.search_queries, system.system_id
                assert spent.model_tokens == 0, "mechanical mode calls no model"
                assert spent.wallclock_seconds == 0.0, "latency belongs to the harness"


def test_ablations_are_resource_matched_to_full_orion():
    orion = full_orion()
    for case in panel():
        for seed in SEEDS:
            reference = orion.run(case.public_view, seed=seed).resources
            for ablation in ablation_systems():
                spent = ablation.run(case.public_view, seed=seed).resources
                assert spent.tool_calls == reference.tool_calls, ablation.system_id
                assert spent.search_queries == reference.search_queries, ablation.system_id


def test_each_ablation_loses_the_organ_it_removed():
    by_id = {system.system_id: system for system in ablation_systems()}

    without_w = by_id["orion_without_explicit_W"]
    assert not without_w.run(case_by_id("p1-c004").public_view, seed=0).root_solved
    assert without_w.run(case_by_id("p1-c007").public_view, seed=0).root_solved

    without_m = by_id["orion_without_explicit_M"]
    assert not without_m.run(case_by_id("p1-c007").public_view, seed=0).root_solved
    assert not without_m.run(case_by_id("p1-c008").public_view, seed=0).root_solved
    assert without_m.run(case_by_id("p1-c004").public_view, seed=0).root_solved

    retry = by_id["generic_retry_instead_of_typed_reframe"]
    for seed in SEEDS:
        assert retry.run(case_by_id("p1-c004").public_view, seed=seed).responsibility_family == ""

    reset = by_id["full_reset_instead_of_dependency_reopen"]
    case = case_by_id("p1-c004")
    reset_trace = reset.run(case.public_view, seed=0)
    orion_trace = full_orion().run(case.public_view, seed=0)
    assert set(orion_trace.reopened) < set(reset_trace.reopened)
    assert reset_trace.root_solved == orion_trace.root_solved


def test_dropping_the_self_audit_costs_control_selectivity():
    """H2's failure mode, produced by removing exactly one organ."""

    no_audit = next(
        item
        for item in ablation_systems()
        if item.system_id == "orion_without_mechanic_self_audit"
    )
    orion = full_orion()
    unnecessary = 0
    for case_id in CONTROL_IDS:
        view = case_by_id(case_id).public_view
        assert not orion.run(view, seed=0).reframed
        if no_audit.run(view, seed=0).reframed:
            unnecessary += 1
    assert unnecessary > 0


def test_orion_reports_invariants_and_authority_truthfully():
    for system in orion_systems():
        for case in panel():
            trace = system.run(case.public_view, seed=0)
            assert trace.invariant_violations == (), trace.invariant_violations
            assert trace.max_recursion_depth >= 1
            assert set(trace.reopened) <= {
                item.closure_id for item in public_closures(case.public_view)
            }
            if trace.authority_violations:
                assert system.system_id == "orion_without_mechanic_self_audit"


def test_reopening_follows_the_transitive_dependency_basis():
    """`z in D*(c)`, not `z in D(c)`.

    Only the head of the chain declares the coordinate. A direct-only rule
    reopens one closure of three and reports two-thirds of the reopen
    obligations as met — on exactly the deep cases H3 exists to measure.
    """

    case = case_by_id("p1-c009")
    closures = {item.closure_id: item for item in public_closures(case.public_view)}
    assert closures["closure:capacity-plan"].own_coordinates == ()
    assert "W.REPRESENTATIONS" in closures["closure:board-brief"].dependency_coordinates
    assert closures["closure:board-brief"].parent_ids == ("closure:capacity-plan",)

    trace = full_orion().run(case.public_view, seed=0)
    assert set(trace.reopened) == set(case.protected_gold.dependencies_to_reopen)


def test_descendants_complete_the_chain_from_an_identified_closure():
    """`D*(c)` in graph space, for the case coordinate space cannot reach.

    Coordinate-keyed staling is exact when a closure declares a basis and
    silent when it does not. On the frozen suite 37 of 44 hidden-shift cases
    have no closure with any publicly inferable coordinate, so a purely
    coordinate-keyed reopen stales nothing at all. Expanding from an identified
    closure is the same rule keyed on the graph instead.
    """

    closures = public_closures(case_by_id("p1-c009").public_view)
    assert descendants_of(closures, ("closure:unit-audit",)) == (
        "closure:unit-audit",
        "closure:capacity-plan",
        "closure:board-brief",
    )
    # Expansion is downward only: a child does not drag its parent in.
    assert descendants_of(closures, ("closure:board-brief",)) == (
        "closure:board-brief",
    )
    # An unrelated conclusion is never swept in.
    assert "closure:sampling-window" not in descendants_of(
        public_closures(case_by_id("p1-c004").public_view), ("closure:baseline-fit",)
    )
    assert descendants_of(closures, ()) == ()
    assert descendants_of(closures, ("closure:never-declared",)) == ()


def test_mechanical_orion_identifies_no_closure_and_says_so():
    """The hook is off by default, and that is the honest default.

    Naming the closure a reframe invalidates is a reasoning act. The public
    view does not disclose it, so a mechanical system must not pretend to have
    it — which is exactly why the shipping dependency-directed path scores
    reopen F1 0.000 on the frozen suite rather than the 1.000 an oracle root
    would give. The two numbers measure different things and must never be
    reported as one.
    """

    assert full_orion().identify_closures is None


def test_an_identified_closure_completes_a_reopen_the_basis_would_miss():
    """The live arm's path, exercised end to end without any leak.

    The chain head declares no coordinate, so coordinate-keyed staling reopens
    nothing. Supplying the identified closure — as a reasoning system would —
    recovers the whole chain.
    """

    case = _case(
        "p1-c012",
        TaskFamily.HIDDEN_REPRESENTATION,
        "The forecast and the ledger disagree by three orders of magnitude and "
        "are expressed in different units.",
        (
            "closure:ledger-tieout — closed; rests on the month-end freeze",
            "closure:board-brief — closed; derived from closure:ledger-tieout",
        ),
        ProtectedGold(
            reframe_required=True,
            responsibility_family="REPRESENTATION",
            target_coordinates=("W.REPRESENTATIONS", "representation:unit_scaling"),
            dependencies_to_reopen=("closure:ledger-tieout", "closure:board-brief"),
            root_success_rubric="the two feeds are compared in one form",
            dependency_depth=2,
        ),
    )
    closures = public_closures(case.public_view)
    assert all(item.dependency_coordinates == () for item in closures), (
        "this fixture exists because the basis is not publicly inferable"
    )

    blind = full_orion().run(case.public_view, seed=0)
    assert blind.reframed and blind.reopened == ()

    informed = OrionSystem(
        system_id="orion_full",
        identify_closures=lambda view: ("closure:ledger-tieout",),
    )
    trace = informed.run(case.public_view, seed=0)
    assert set(trace.reopened) == set(case.protected_gold.dependencies_to_reopen)
    assert trace.invariant_violations == ()


def test_a_closure_chain_does_not_reopen_unrelated_conclusions():
    """The transitive rule must not become a full reset by another name."""

    case = case_by_id("p1-c004")
    trace = full_orion().run(case.public_view, seed=0)
    assert "closure:sampling-window" not in trace.reopened


def test_orion_declines_to_reframe_under_ambiguous_attribution():
    """Blocking a high-impact revision is the doctrine, not a failure to act.

    This is a documented conservative miss: ORION reports the case unsolved
    rather than guessing between two equally supported responsibilities.
    """

    case = ambiguous_case()
    trace = full_orion().run(case.public_view, seed=0)
    assert not trace.reframed
    assert not trace.root_solved
    assert not trace.abstained
    assert "DISCRIMINATOR_REQUIRED" in trace.notes
    assert "ambiguous_responsibility_blocks_high_impact_revision" in trace.notes

    # The un-audited ablation has no such obligation and commits anyway.
    no_audit = next(
        item
        for item in ablation_systems()
        if item.system_id == "orion_without_mechanic_self_audit"
    )
    assert no_audit.run(case.public_view, seed=0).reframed


def test_a_present_tense_observation_discriminates_an_ambiguous_case():
    """The discriminator is real, and it needs no privileged channel.

    An observation of the failure happening now (the prompt) outranks a
    statement of what some earlier closure was assumed to hold (a resource
    line). That is the only tie-breaker available without world knowledge, and
    it leaks nothing.
    """

    base = ambiguous_case()
    discriminating = _case(
        "p1-c011",
        base.task_family,
        "The format expected by the consumer changed in March and the loss "
        "persists.",
        (
            "closure:stage-plan closed under the assumption that the stages "
            "were assumed independent",
            "service:consumer",
        ),
        base.protected_gold,
    )
    trace = full_orion().run(discriminating.public_view, seed=0)
    assert trace.reframed
    assert trace.responsibility_family == "INTERFACE"
    assert "discriminator_applied" in trace.notes


def test_a_declared_signal_channel_is_refused():
    """A leak guard, not a parser.

    The suite author measured a `signal:<phenomenon>` resource as DEGENERATE:
    a blind responder doing a dict lookup scored 1.000 while reading nothing
    substantive. The channel is refused, so a case that reintroduces one cannot
    silently hand every system the hidden label.
    """

    leaked = PublicView(
        case_id="p1-leak",
        public_prompt="Throughput fell from 900/s to 240/s after the March release.",
        observable_resources=("signal:scale-mismatch", "dataset:throughput"),
        budget_class=BUDGET_CLASS,
    )
    assert "signal:scale-mismatch" not in readable_resources(leaked)
    assert extract_cues(leaked) == ()
    trace = full_orion().run(leaked, seed=0)
    assert trace.abstained
    assert not trace.reframed
    assert not trace.root_solved


def test_the_mechanical_arm_abstains_on_suite_shaped_hidden_shift():
    """The honest null result, pinned so it cannot be mistaken for success.

    On cases written the way the frozen suite writes them, no mechanical system
    can recover a formulation responsibility from symptoms and numbers — that
    needs world knowledge. Every system must therefore ABSTAIN, and abstention
    must never be scored as root success. Before this was enforced, a system
    that detected nothing reported `root_solved=True`, which would have
    reported the mechanical arm as flawless on precisely the cases it cannot
    read.
    """

    hidden = [
        case
        for case in suite_shaped_panel()
        if case.protected_gold.reframe_required
    ]
    assert hidden
    for system in all_systems():
        for case in hidden:
            for seed in SEEDS:
                trace = system.run(case.public_view, seed=seed)
                assert trace.abstained, f"{system.system_id} claimed to see {case.case_id}"
                assert not trace.root_solved, (
                    f"{system.system_id} claimed success without detecting a residual"
                )
                assert not trace.reframed
                assert trace.reopened == ()


def test_suite_shaped_controls_stay_solvable_and_unreframed():
    """Where the phenomenon *is* the responsibility, mechanical systems work.

    A missing source reads as a missing source and a crash reads as a crash, so
    the controls remain winnable — which is what keeps the abstention result
    above a finding about hidden formulation rather than about the detector
    being blind in general.
    """

    controls = [
        case
        for case in suite_shaped_panel()
        if not case.protected_gold.reframe_required
    ]
    assert controls
    for case in controls:
        for system in all_systems():
            trace = system.run(case.public_view, seed=0)
            assert trace.root_solved, f"{system.system_id} failed {case.case_id}"
            assert not trace.abstained
            # Controls carry closure lines of their own; nothing may be
            # reopened, because the formulation stood.
            assert trace.reopened == (), system.system_id


def test_suite_shaped_controls_carry_closures_without_inviting_a_reopen():
    """The control's closure lines are real and parsed, and still not reopened."""

    controls = [
        case
        for case in suite_shaped_panel()
        if not case.protected_gold.reframe_required
    ]
    for case in controls:
        closures = public_closures(case.public_view)
        assert closures, f"{case.case_id} should carry a closure line"
        assert case.protected_gold.dependencies_to_reopen == ()


FROZEN_SUITE = (
    Path(__file__).resolve().parents[4]
    / "papers"
    / "orion-11-recursive-epistemic-reconstruction"
    / "protocol"
    / "cases"
)


def test_no_system_claims_success_while_abstaining_on_the_frozen_suite():
    """Validated against the real frozen cases, not only against fixtures.

    A fixture panel is written by the same hand as the code it checks, so it
    can agree with a wrong rule. This runs every system over the actual frozen
    suite and pins the one invariant that must never break: a system that saw
    no residual may not report the root task solved.

    It also records the honest headline — the mechanical arm abstains on nearly
    every frozen case, because recovering a formulation responsibility from
    symptoms and numbers needs world knowledge the live provider supplies and a
    lexical detector does not.
    """

    cases = load_cases(FROZEN_SUITE, split=Split.TEST)
    if not cases:
        pytest.skip("frozen TEST split not present in this checkout")

    abstentions = 0
    for system in all_systems():
        for case in cases:
            trace = system.run(case.public_view, seed=0)
            if trace.abstained:
                abstentions += 1
                assert not trace.root_solved, (
                    f"{system.system_id} claimed {case.case_id} solved while abstaining"
                )
                assert not trace.reframed
                assert trace.reopened == ()
    total = len(all_systems()) * len(cases)
    # Recorded as a floor rather than an equality so a later suite revision
    # that makes some cases mechanically legible does not fail the build.
    assert abstentions > total * 0.8, (
        "the mechanical arm was expected to abstain on the frozen suite; "
        f"only {abstentions}/{total} abstained"
    )


def test_abstention_is_never_scored_as_root_success():
    """The rule, stated directly rather than only as a consequence."""

    empty = PublicView(
        case_id="p1-empty",
        public_prompt="Latency moved from 12ms to 47ms after the release.",
        observable_resources=("dataset:latency",),
        budget_class=BUDGET_CLASS,
    )
    for system in all_systems():
        trace = system.run(empty, seed=0)
        assert trace.abstained, system.system_id
        assert not trace.root_solved, system.system_id


def test_the_invariant_checkers_actually_fire():
    """A guard that has never fired is a guard nobody has tested.

    The normal path cannot produce these, which is the point — so they are
    driven directly, to prove the no-violation results reported everywhere else
    mean "checked and clean" rather than "never looked".
    """

    system = full_orion()
    found: list[str] = []
    system._check_policy_scope(("M.METHOD",), found)
    assert found == ["coordinate_outside_policy:M.METHOD"]

    found = []
    system._check_reopen_scope(
        ("closure:invented",), public_closures(case_by_id("p1-c004").public_view), found
    )
    assert found == ["reopened_unknown_closure:closure:invented"]

    # And the clean case must stay silent, or the checker cries wolf.
    quiet: list[str] = []
    system._check_policy_scope(("W.REPRESENTATIONS",), quiet)
    system._check_reopen_scope(
        ("closure:baseline-fit",),
        public_closures(case_by_id("p1-c004").public_view),
        quiet,
    )
    assert quiet == []


def test_orion_escalates_a_method_reframe_instead_of_attempting_it():
    """The engine refuses; the study records who tried.

    Full ORION recognises that method revision is a governed Self-ORION
    transition and escalates. The un-audited ablation attempts it and the real
    `ReframeOperator` raises — the violation is the engine's verdict, not a
    simulated one.
    """

    view = PublicView(
        case_id="probe-method",
        public_prompt=(
            "The team argues the method itself is what must change here; "
            "no source backs the current step."
        ),
        observable_resources=(),
        budget_class=BUDGET_CLASS,
    )
    orion_trace = full_orion().run(view, seed=0)
    assert orion_trace.authority_violations == ()
    assert "escalated_to_protected_gate:M.METHOD" in orion_trace.notes

    no_audit = next(
        item
        for item in ablation_systems()
        if item.system_id == "orion_without_mechanic_self_audit"
    )
    ablated = no_audit.run(view, seed=0)
    assert ablated.authority_violations == (
        "attempted_method_reframe_without_protected_gate",
    )


def test_generic_retry_still_reopens_by_dependency():
    """The retry ablation is not a re-labelled tree search."""

    retry = next(
        item
        for item in ablation_systems()
        if item.system_id == "generic_retry_instead_of_typed_reframe"
    )
    tree = next(
        item
        for item in baseline_systems()
        if item.system_id == "tree_search_iterative_research"
    )
    case = case_by_id("p1-c004")
    reopened = {
        tuple(retry.run(case.public_view, seed=seed).reopened) for seed in SEEDS
    }
    assert any(item for item in reopened), "the retry ablation kept the reopen organ"
    assert all(
        tree.run(case.public_view, seed=seed).reopened == () for seed in SEEDS
    )


# --------------------------------------------------------------------------
# Determinism
# --------------------------------------------------------------------------


def test_every_system_is_deterministic_given_a_seed():
    """Full trace equality, resources included.

    `wallclock_seconds` is 0.0 by construction for mechanical systems and
    measured elapsed time lives on the archive record, so the trace itself is
    reproducible and can be compared whole.
    """

    for system in all_systems():
        for case in panel():
            for seed in SEEDS:
                first = system.run(case.public_view, seed=seed)
                second = system.run(case.public_view, seed=seed)
                assert first == second, system.system_id


def test_seeds_actually_vary_a_stochastic_system():
    tree = next(
        item
        for item in baseline_systems()
        if item.system_id == "tree_search_iterative_research"
    )
    outcomes = {
        tree.run(case_by_id("p1-c004").public_view, seed=seed).root_solved
        for seed in SEEDS
    }
    assert outcomes == {True, False}, "repeats must exercise real seed variation"


def test_no_system_exceeds_the_shared_budget():
    for system in all_systems():
        for case in panel():
            budget = budget_for(case.public_view)
            for seed in SEEDS:
                usage = system.run(case.public_view, seed=seed).resources
                assert usage.tool_calls <= budget.tool_calls
                assert usage.search_queries <= budget.search_queries
                assert usage.model_tokens <= budget.model_tokens


# --------------------------------------------------------------------------
# Harness
# --------------------------------------------------------------------------


def test_harness_archives_failed_runs(tmp_path: Path):
    """The exclusion policy forbids dropping a candidate-caused failure."""

    class Exploding:
        system_id = "exploding"

        def run(self, view, *, seed: int) -> SystemTrace:
            raise RuntimeError("candidate crashed mid-action")

    archive_path = tmp_path / "runs.jsonl"
    archive = run_study(
        panel(), (Exploding(),), seeds=(0, 1), archive_path=archive_path
    )

    expected = len(panel()) * 2
    assert len(archive.records) == expected
    assert len(archive.failures) == expected
    assert all(record.trace is None for record in archive.failures)
    assert all("candidate crashed" in record.error for record in archive.failures)

    lines = read_archive(archive_path)
    assert len(lines) == expected
    assert {line["status"] for line in lines} == {"CANDIDATE_FAILURE"}
    assert all(line["trace"] is None for line in lines)


def test_archive_binds_the_suite_fingerprint_and_subject_revision(tmp_path: Path):
    archive_path = tmp_path / "runs.jsonl"
    archive = run_study(
        panel(), (full_orion(),), seeds=(0,), archive_path=archive_path
    )
    assert len(archive.suite_fingerprint) == 64
    assert archive.subject_revision
    assert archive.protocol_id == "P1.hidden-formulation.v1"
    for line in read_archive(archive_path):
        assert line["suite_fingerprint"] == archive.suite_fingerprint
        assert line["subject_revision"] == archive.subject_revision
        assert line["trace"]["case_id"] == line["case_id"]
        assert "resources" in line["trace"]


def test_harness_records_one_line_per_case_system_seed(tmp_path: Path):
    archive_path = tmp_path / "runs.jsonl"
    systems = all_systems()
    archive = run_study(panel(), systems, seeds=SEEDS, archive_path=archive_path)
    assert len(archive.records) == len(panel()) * len(systems) * len(SEEDS)
    keys = {(item.case_id, item.system_id, item.seed) for item in archive.records}
    assert len(keys) == len(archive.records)
    assert len(read_archive(archive_path)) == len(archive.records)


def test_harness_flags_malformed_traces_without_dropping_them():
    class Liar:
        system_id = "liar"

        def run(self, view, *, seed: int) -> SystemTrace:
            return SystemTrace(
                case_id="not-the-case",
                system_id="not-the-system",
                seed=seed + 1,
                reframed=False,
                target_coordinates=("W.REPRESENTATIONS",),
                resources=ResourceUse(tool_calls=10_000, search_queries=10_000),
            )

    archive = run_study(panel()[:1], (Liar(),), seeds=(0,))
    record = archive.records[0]
    assert record.status is RunStatus.OK
    assert record.trace is not None
    assert set(record.integrity) == {
        "case_id_mismatch",
        "system_id_mismatch",
        "seed_mismatch",
        "target_without_reframe",
        "tool_call_budget_exceeded",
        "search_budget_exceeded",
    }


def test_integrity_flags_stay_silent_on_a_well_formed_run():
    """A checker that flags a clean run is worse than one that misses."""

    archive = run_study(panel(), (full_orion(),), seeds=(0,))
    assert all(record.integrity == () for record in archive.records)


# --------------------------------------------------------------------------
# Provider
# --------------------------------------------------------------------------


def test_provider_refuses_cleanly_without_a_credential(monkeypatch):
    monkeypatch.delenv(CREDENTIAL_ENV_VAR, raising=False)
    assert not credential_present()
    response = AnthropicProvider().complete("anything")
    assert response.status is ProviderStatus.NO_CREDENTIAL
    assert response.text == ""
    # Assert the configured default, not a literal: the subject model is an
    # operator choice and changing it must not break a test about refusal.
    assert response.model == DEFAULT_MODEL
    assert CREDENTIAL_ENV_VAR in response.detail


def test_provider_never_stores_the_credential():
    """No field may hold the key, so no repr or archive can leak it."""

    names = {field.name for field in dataclasses.fields(AnthropicProvider)}
    assert names == {"model", "max_tokens"}
    assert "key" not in repr(AnthropicProvider()).lower()


def test_harness_records_cannot_check_when_the_provider_refuses(
    monkeypatch, tmp_path: Path
):
    """A missing credential is never a zero score and never a silent skip."""

    monkeypatch.delenv(CREDENTIAL_ENV_VAR, raising=False)
    archive_path = tmp_path / "runs.jsonl"
    archive = run_study(
        panel(), (ProviderBackedSystem(),), seeds=(0,), archive_path=archive_path
    )
    assert len(archive.cannot_check) == len(panel())
    assert not archive.failures
    for record in archive.records:
        assert record.status is RunStatus.CANNOT_CHECK
        assert record.trace is None
        assert record.error.startswith(ProviderStatus.NO_CREDENTIAL.value)
    assert len(read_archive(archive_path)) == len(panel())


def test_provider_backed_system_raises_before_touching_the_network(monkeypatch):
    monkeypatch.delenv(CREDENTIAL_ENV_VAR, raising=False)
    with pytest.raises(ProviderUnavailable) as error:
        ProviderBackedSystem().run(case_by_id("p1-c001").public_view, seed=0)
    assert error.value.status is ProviderStatus.NO_CREDENTIAL


# --------------------------------------------------------------------------
# Perception layer is shared, not per-system
# --------------------------------------------------------------------------


def test_all_systems_read_the_same_observations():
    """No system may win by perceiving more than another."""

    for case in panel():
        cues = extract_cues(case.public_view)
        assert cues, f"{case.case_id} produced no observable cue"
        materials = [cue for cue in cues if cue.material]
        assert materials, f"{case.case_id} has no discriminating observation"


def test_controls_expose_no_material_formulation_cue():
    """If a control carried one, declining to reframe would be wrong."""

    for case_id in CONTROL_IDS:
        cues = extract_cues(case_by_id(case_id).public_view)
        assert not [cue for cue in cues if cue.material and cue.formulation]
        assert [cue for cue in cues if not cue.material and cue.formulation], (
            "a control needs a weak decoy or it cannot test selectivity"
        )
