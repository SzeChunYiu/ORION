"""Tests for the credential-free substrate of the frozen live research trial.

Every test here runs with no credential and makes no network call. The
`_no_network` fixture is autouse, so a connection attempt from any test in this
file fails that test rather than quietly succeeding on a developer machine that
happens to be online.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from orion.core.search import SearchRouteKind
from orion.experience.model import (
    EpisodeOutcome,
    FailurePatternCandidate,
    LessonAuthority,
)
from orion.mechanics.model import MechanicDimension
from orion.self_orion.live_packet import (
    CREDENTIAL_ENV_VARS,
    _sha256,
    EXIT_CANNOT_CHECK,
    EXIT_OK,
    FROZEN_LIMITS,
    ISSUE_8_DIMENSIONS,
    PROTOCOL_PATH,
    SUCCESS_BOUNDARY,
    UNBOUND,
    AuthorityDecision,
    AuthorityRequestKind,
    BoundedSaturationOutcome,
    BoundedSaturationState,
    CriterionStatus,
    EvidenceUseClass,
    FrozenEvaluatorSpec,
    FrozenResourceLimits,
    MatchedBaselineSpec,
    QueryTrace,
    RawTrialTrace,
    RepairProposal,
    ResearchTrialKind,
    TaskOutcomeInput,
    TraceItem,
    blocked_mechanic_ids,
    classify_evidence_use,
    emit_open_questions,
    evaluate_task,
    execution_manifest,
    failure_pattern_candidates,
    frozen_live_research_packet,
    live_trial_mechanic_cells,
    load_packet_document,
    main,
    missing_credential_env_vars,
    packet_document,
    pre_execution_saturation_state,
    preflight,
    propose_repair,
    question_surface_coverage,
    question_surface_summary,
    refusal_episodes,
    request_promotion,
    write_packet_document,
)

REPO_ROOT = Path(__file__).resolve().parents[3]

DEEP_TASK_ID = "P5.LIVE.DEEP.flat-round-without-lineage"
WIDE_TASK_ID = "P5.LIVE.WIDE.stopping-rule-source-families"

# The plaintext of the protected gold, restated here so the leak test asserts on
# the literal value rather than on the module constant it is meant to police.
GOLD_TOKEN = "PARTIALLY_IDENTIFIED_LINEAGE"
GOLD_ANCHOR = "orion-corpus:src/orion/kernel/saturation.py"


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Fail any test that opens a socket. The trial is credential-blocked."""

    def _blocked(*args, **kwargs):
        raise AssertionError("this test attempted a network connection")

    monkeypatch.setattr(socket.socket, "connect", _blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


@pytest.fixture
def no_credentials(monkeypatch):
    """Guarantee the no-credential path regardless of the developer's shell."""

    for name in CREDENTIAL_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("ORION_P5_REASONER_MODEL", raising=False)


def _trace(task_id: str = WIDE_TASK_ID) -> RawTrialTrace:
    """A synthetic trace. No provider produced it and none is claimed to have."""

    return RawTrialTrace(task_id).extend(
        QueryTrace(
            "q1",
            "stopping rules for evidence search",
            SearchRouteKind.CURRENT_VOCABULARY,
            "backend-a",
            "current-vocabulary",
            (TraceItem("item:used", "d1", "https://example.test/1"),),
        ),
        QueryTrace(
            "q2",
            "canonical treatment of search stopping in an established discipline",
            SearchRouteKind.PARENT_DISCIPLINE,
            "backend-b",
            "parent-discipline",
            (
                TraceItem("item:used", "d1", "https://example.test/1"),
                TraceItem("item:unused", "d2", "https://example.test/2"),
            ),
        ),
        QueryTrace(
            "q3",
            "recent advances in search stopping",
            SearchRouteKind.FRESHNESS,
            "backend-c",
            "freshness",
        ),
        QueryTrace(
            "q4",
            "critiques and failure modes of stopping rules",
            SearchRouteKind.ADVERSARIAL_OMISSION,
            "backend-d",
            "adversarial-omission",
            (),
            error="TimeoutError",
        ),
    )


# ---------------------------------------------------------------------------
# 1. The frozen packet
# ---------------------------------------------------------------------------


def test_packet_freezes_one_wide_and_one_deep_task_before_any_outcome():
    packet = frozen_live_research_packet()
    kinds = {item.kind for item in packet.tasks}
    assert ResearchTrialKind.WIDE_LITERATURE in kinds
    assert ResearchTrialKind.DEEP_TARGET in kinds
    assert packet.outcome_accessed is False
    assert packet.body["outcome_accessed"] is False
    assert {item.task_id for item in packet.tasks} == {WIDE_TASK_ID, DEEP_TASK_ID}


def test_packet_cannot_be_constructed_after_outcome_access():
    packet = frozen_live_research_packet()
    with pytest.raises(ValueError, match="frozen"):
        replace(packet, outcome_accessed=True)


def test_packet_fingerprint_is_deterministic_and_content_bound():
    first = frozen_live_research_packet()
    second = frozen_live_research_packet()
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64
    bound = frozen_live_research_packet(corpus_revision="abc123")
    assert bound.fingerprint != first.fingerprint


def test_provider_identity_limits_and_evaluator_are_frozen_into_the_fingerprint():
    packet = frozen_live_research_packet()
    body = packet.body
    assert body["provider_manifest_hash"] == packet.trial.provider_manifest_hash
    assert body["evaluator_artifact_hash"] == packet.evaluator.artifact_hash
    assert body["resource_limits"]["max_orion_to_baseline_ratio"] == 1.0
    assert {item["role"] for item in body["providers"]} == {
        "reasoner",
        "retrieval",
        "protected_verification",
    }
    assert all(item["secret_material_included"] is False for item in body["providers"])


def test_published_packet_matches_the_code_and_declares_its_own_fingerprint():
    assert PROTOCOL_PATH.exists(), "run --emit-protocol to publish the frozen packet"
    on_disk = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    assert on_disk == packet_document()
    # Recomputed, not trusted: a hand-edited packet must fail rather than pass.
    assert load_packet_document(PROTOCOL_PATH)["packet_fingerprint"] == (
        frozen_live_research_packet().fingerprint
    )


def test_tampered_packet_document_is_refused(tmp_path):
    path = tmp_path / "packet.json"
    write_packet_document(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["evaluation_epoch_id"] = "tampered"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="fingerprint mismatch"):
        load_packet_document(path)


def test_public_packet_never_contains_the_protected_gold():
    serialized = json.dumps(packet_document(), sort_keys=True)
    assert GOLD_TOKEN not in serialized
    assert GOLD_ANCHOR not in serialized
    assert "saturation.py" not in serialized
    deep = next(
        item
        for item in packet_document()["task_bindings"]
        if item["task_id"] == DEEP_TASK_ID
    )
    assert len(deep["protected_gold_digest"]) == 64
    assert deep["ground_truth_bound"] is True


def test_write_refuses_a_document_containing_a_live_credential_value(
    monkeypatch, tmp_path
):
    # A value long enough to be a real key and present in the document forces
    # the guard to fire; the guard is the reason a manifest can be published at
    # all without re-reading every field by eye.
    monkeypatch.setenv("OPENAI_API_KEY", "P5.shadow-live-research.v1")
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        write_packet_document(tmp_path / "leak.json")


def test_the_frozen_protocol_path_cannot_be_rewritten_with_a_corpus_bound_packet():
    """A frozen artifact any later command can overwrite in place is not frozen."""

    with pytest.raises(ValueError, match="refusing to overwrite"):
        write_packet_document(packet=frozen_live_research_packet(corpus_revision="rev-1"))
    # The checked-in packet is untouched and still matches the code.
    assert json.loads(PROTOCOL_PATH.read_text(encoding="utf-8")) == packet_document()


def test_a_corpus_bound_packet_may_be_written_anywhere_else(tmp_path):
    target = write_packet_document(
        tmp_path / "bound.json", packet=frozen_live_research_packet(corpus_revision="rev-1")
    )
    raw = json.loads(target.read_text(encoding="utf-8"))
    assert raw["corpus_revision"] == "rev-1"
    assert raw["packet_fingerprint"] != frozen_live_research_packet().fingerprint


def test_execution_manifest_binds_a_report_to_the_frozen_packet_and_corpus(tmp_path):
    """The runtime packet carries no corpus revision; the manifest is where it lands."""

    packet = frozen_live_research_packet(corpus_revision="rev-1")
    manifest = execution_manifest(
        packet, report_path=tmp_path / "report.json", report_document_hash="d" * 64
    )
    assert manifest["packet_fingerprint"] == packet.fingerprint
    assert manifest["corpus_revision"] == "rev-1"
    assert manifest["evaluator_artifact_hash"] == packet.evaluator.artifact_hash
    assert manifest["report_document_hash"] == "d" * 64
    assert manifest["success_boundary"] == SUCCESS_BOUNDARY
    assert len(manifest["manifest_hash"]) == 64
    # Recomputable: the hash covers the body and nothing else.
    body = {key: value for key, value in manifest.items() if key != "manifest_hash"}
    assert manifest["manifest_hash"] == _sha256(body)


def test_execution_manifest_refuses_an_unbound_corpus_or_an_unhashed_report(tmp_path):
    with pytest.raises(ValueError, match="UNBOUND"):
        execution_manifest(
            frozen_live_research_packet(),
            report_path=tmp_path / "r.json",
            report_document_hash="d" * 64,
        )
    with pytest.raises(ValueError, match="document hash"):
        execution_manifest(
            frozen_live_research_packet(corpus_revision="rev-1"),
            report_path=tmp_path / "r.json",
            report_document_hash="",
        )


def test_evaluator_may_not_depend_on_the_model_agreeing_it_succeeded():
    packet = frozen_live_research_packet()
    assert packet.evaluator.model_cooperation_required is False
    with pytest.raises(ValueError, match="cooperation"):
        FrozenEvaluatorSpec(
            "e", packet.evaluator.criteria, model_cooperation_required=True
        )


def test_matched_baseline_is_specified_under_the_identical_limits():
    packet = frozen_live_research_packet()
    assert packet.baseline.limits is packet.limits
    mismatched = MatchedBaselineSpec(
        "other",
        "orion.self_orion.baseline.SimpleLLMRetrievalBaseline",
        "a baseline given a different budget",
        FrozenResourceLimits(
            budget_units=FROZEN_LIMITS.budget_units * 4,
            max_model_calls=99,
            max_retrieval_calls=99,
            max_model_tokens=999_999,
            max_wallclock_seconds=9_999.0,
        ),
    )
    with pytest.raises(ValueError, match="same limits"):
        replace(packet, baseline=mismatched)


# ---------------------------------------------------------------------------
# 2. The mechanical question surface
# ---------------------------------------------------------------------------


def test_question_surface_runs_with_no_provider_and_no_credential(no_credentials):
    assert missing_credential_env_vars() == CREDENTIAL_ENV_VARS
    summary = question_surface_summary()
    assert summary["provider_required"] is False
    assert summary["open_questions_issue_8"] > 0
    assert emit_open_questions()


def test_question_surface_exposes_every_one_of_the_eight_named_dimensions(
    no_credentials,
):
    coverage = question_surface_coverage()
    assert coverage.missing == ()
    assert coverage.complete
    emitted = {item.dimension for item in emit_open_questions()}
    for dimension in ISSUE_8_DIMENSIONS:
        assert dimension in emitted, dimension


def test_question_surface_reports_the_unfiltered_total_too(no_credentials):
    summary = question_surface_summary()
    assert summary["open_questions_total"] >= summary["open_questions_issue_8"]
    assert summary["uncovered_dimensions"] == []


def test_every_question_names_a_real_cell_and_a_named_dimension():
    cells = live_trial_mechanic_cells()
    known = {cell.mechanic_id for cell in cells}
    assert len(known) == len(cells) == 8
    for question in emit_open_questions(cells):
        assert question.mechanic_id in known
        assert question.dimension in ISSUE_8_DIMENSIONS
        assert question.question.strip()


def test_surface_is_not_routed_through_the_starving_default_selector():
    """PARENT_DISCIPLINE, SATURATION and STORAGE rank below the default window.

    `plan_next_questions(limit=8)` would drop all three. The failure is silent —
    the run reports flat because the window never asked — so the guarantee is
    asserted here rather than left to the reader of `emit_open_questions`.
    """

    emitted = {item.dimension for item in emit_open_questions()}
    for dimension in (
        MechanicDimension.PARENT_DISCIPLINE,
        MechanicDimension.SATURATION,
        MechanicDimension.STORAGE,
    ):
        assert dimension in emitted


def test_importing_the_substrate_builds_no_live_provider_stack(tmp_path):
    """No live stack is imported by the credential-free path.

    The assertion is deliberately narrow. The repo's provider packages re-export
    their concrete adapters from `__init__`, so importing a Protocol base drags
    the adapter modules in; that is a repo-wide property, not something this
    module chooses. What matters, and what is checked, is that the module which
    *builds a live stack* is imported only inside `--live`, and that the surface
    computes to completion in a process with no credential in its environment.
    """

    script = (
        "import sys\n"
        "import orion.self_orion.live_packet as m\n"
        "summary = m.question_surface_summary()\n"
        "assert 'orion.providers.live_phase2' not in sys.modules\n"
        "assert summary['open_questions_issue_8'] > 0\n"
        "assert summary['uncovered_dimensions'] == []\n"
        "print('ok')\n"
    )
    env = {"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin"}
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        env=env,
        cwd=tmp_path,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


# ---------------------------------------------------------------------------
# 3. Raw trace retention and evidence-use classification
# ---------------------------------------------------------------------------


def test_raw_trace_retains_every_query_including_empties_and_errors():
    submitted = _trace()
    assert len(submitted.records) == 4
    assert len(submitted.empty_queries) == 2
    assert len(submitted.errored_queries) == 1
    # The empty and errored occasions survive verbatim: no filter exists to drop
    # them, so "all failures and nulls preserved" is a property of the type.
    assert submitted.errored_queries[0].error == "TimeoutError"
    assert submitted.empty_queries[0].query_text
    assert len(submitted.route_kinds) == 4
    assert len(submitted.productive_route_kinds) == 2


def test_trace_fingerprint_changes_when_a_null_result_is_dropped():
    full = _trace()
    pruned = RawTrialTrace(full.task_id).extend(
        *[item for item in full.records if item.items]
    )
    assert pruned.fingerprint != full.fingerprint


def test_retrieved_but_unused_is_distinguished_from_present_but_missed():
    report = classify_evidence_use(
        _trace(),
        cited_ids=("item:used",),
        corpus_present_ids=frozenset({"item:used", "item:unused", "item:never-seen"}),
    )
    assert report.ground_truth_bound is True
    assert report.used == ("item:used",)
    assert report.retrieved_but_unused == ("item:unused",)
    assert report.present_but_missed == ("item:never-seen",)
    assert report.cannot_check == ()


def test_present_but_missed_is_cannot_check_when_ground_truth_is_unbound():
    report = classify_evidence_use(_trace(), cited_ids=("item:used",))
    assert report.ground_truth_bound is False
    assert report.present_but_missed == ()
    assert report.cannot_check  # never silently zero
    assert "UNBOUND" in report.cannot_check_reason
    assert report.retrieved_but_unused == ("item:unused",)


def test_a_citation_absent_from_the_raw_trace_is_flagged_not_absorbed():
    report = classify_evidence_use(
        _trace(), cited_ids=("item:used", "item:not-in-trace")
    )
    assert report.cited_but_unretrieved == ("item:not-in-trace",)
    assert report.used == ("item:used",)


def test_classification_is_total_no_item_falls_out():
    trace = _trace()
    report = classify_evidence_use(
        trace,
        cited_ids=("item:used", "item:not-in-trace"),
        corpus_present_ids=frozenset({"item:never-seen"}),
    )
    classified = [item for item, _ in report.classes]
    assert len(classified) == len(set(classified))
    assert set(trace.item_ids).issubset(classified)
    assert "item:not-in-trace" in classified
    assert "item:never-seen" in classified
    by_item = dict(report.classes)
    assert by_item["item:never-seen"] is EvidenceUseClass.PRESENT_BUT_MISSED
    assert by_item["item:unused"] is EvidenceUseClass.RETRIEVED_BUT_UNUSED
    assert by_item["item:not-in-trace"] is EvidenceUseClass.CITED_BUT_UNRETRIEVED


# ---------------------------------------------------------------------------
# 4. The frozen evaluator, exercised without a model
# ---------------------------------------------------------------------------


def test_every_criterion_returns_a_result_including_cannot_check():
    packet = frozen_live_research_packet()
    results = evaluate_task(
        packet,
        TaskOutcomeInput(
            task_id=WIDE_TASK_ID,
            trace=_trace(),
            answer_text="an answer",
            cited_ids=("item:used",),
        ),
    )
    binding = packet.binding(WIDE_TASK_ID)
    assert binding is not None
    assert len(results) == len(binding.criteria)
    by_id = {item.criterion_id: item for item in results}
    assert by_id["W1.citations-grounded"].status is CriterionStatus.PASS
    # Two productive route families against a threshold of four: a real FAIL,
    # produced without asking the system under test whether it succeeded.
    assert by_id["W2.route-breadth"].status is CriterionStatus.FAIL
    assert by_id["W3.independent-corroboration"].status is CriterionStatus.PASS
    # Unobserved resource use is CANNOT_CHECK, never a pass and never a zero.
    assert by_id["W5.resource-matched"].status is CriterionStatus.CANNOT_CHECK


def test_resource_matching_is_judged_against_the_baseline_not_the_budget_alone():
    packet = frozen_live_research_packet()
    outcome = TaskOutcomeInput(
        task_id=WIDE_TASK_ID,
        trace=_trace(),
        answer_text="an answer",
        cited_ids=("item:used",),
        orion_resource_units=6.0,
        baseline_resource_units=2.0,
    )
    result = next(
        item
        for item in evaluate_task(packet, outcome)
        if item.criterion_id == "W5.resource-matched"
    )
    # Well inside the 24-unit budget, but three times the baseline's spend.
    assert result.status is CriterionStatus.FAIL
    matched = next(
        item
        for item in evaluate_task(packet, replace(outcome, orion_resource_units=2.0))
        if item.criterion_id == "W5.resource-matched"
    )
    assert matched.status is CriterionStatus.PASS


def test_deep_target_missing_the_gold_without_a_residual_fails():
    packet = frozen_live_research_packet()
    trace = RawTrialTrace(DEEP_TASK_ID).extend(
        QueryTrace(
            "d1",
            "bounded saturation flat round lineage",
            SearchRouteKind.CURRENT_VOCABULARY,
            "backend-a",
            "current-vocabulary",
            (TraceItem(GOLD_ANCHOR, "d9", "file://saturation"),),
        )
    )
    silent = evaluate_task(
        packet,
        TaskOutcomeInput(
            task_id=DEEP_TASK_ID,
            trace=trace,
            answer_text="the module decides something",
            cited_ids=(GOLD_ANCHOR,),
        ),
    )
    by_id = {item.criterion_id: item for item in silent}
    assert by_id["D2.gold-tokens"].status is CriterionStatus.FAIL
    assert by_id["D3.gold-anchor-cited"].status is CriterionStatus.PASS
    assert by_id["D4.non-recovery-declares-residual"].status is CriterionStatus.FAIL
    # The failure detail must not echo the answer key back into the run record.
    assert GOLD_TOKEN not in by_id["D2.gold-tokens"].detail

    declared = evaluate_task(
        packet,
        TaskOutcomeInput(
            task_id=DEEP_TASK_ID,
            trace=trace,
            answer_text="the module decides something",
            cited_ids=(GOLD_ANCHOR,),
            residual_ids=("residual:verdict-not-recovered",),
        ),
    )
    assert (
        next(
            item
            for item in declared
            if item.criterion_id == "D4.non-recovery-declares-residual"
        ).status
        is CriterionStatus.PASS
    )


def test_deep_target_recovering_the_protected_gold_passes():
    packet = frozen_live_research_packet()
    trace = RawTrialTrace(DEEP_TASK_ID).extend(
        QueryTrace(
            "d1",
            "bounded saturation flat round lineage",
            SearchRouteKind.CURRENT_VOCABULARY,
            "backend-a",
            "current-vocabulary",
            (TraceItem(GOLD_ANCHOR, "d9", "file://saturation"),),
        )
    )
    results = {
        item.criterion_id: item
        for item in evaluate_task(
            packet,
            TaskOutcomeInput(
                task_id=DEEP_TASK_ID,
                trace=trace,
                answer_text=f"assess_saturation returns {GOLD_TOKEN} in that case",
                cited_ids=(GOLD_ANCHOR,),
            ),
        )
    }
    assert results["D2.gold-tokens"].status is CriterionStatus.PASS
    assert results["D4.non-recovery-declares-residual"].status is CriterionStatus.PASS


def test_evaluating_an_unknown_task_is_an_error_not_a_silent_pass():
    with pytest.raises(ValueError, match="unknown task"):
        evaluate_task(
            frozen_live_research_packet(),
            TaskOutcomeInput("not-a-task", _trace(), "x", ()),
        )


# ---------------------------------------------------------------------------
# 5. Refusal episodes and failure-pattern matching
# ---------------------------------------------------------------------------


def test_no_credential_records_cannot_check_episodes_never_zeros(no_credentials):
    episodes = refusal_episodes()
    assert episodes
    for episode in episodes:
        assert episode.outcome is EpisodeOutcome.CANNOT_CHECK
        assert "provider:NO_CREDENTIAL" in episode.failure_signature
        assert episode.residual_ids
        assert episode.evidence_ids == ()
    # Both frozen tasks are represented, and every blocked fibre with them.
    assert {item.task_id for item in episodes} == {WIDE_TASK_ID, DEEP_TASK_ID}
    assert set(blocked_mechanic_ids()) == {item.mechanic_id for item in episodes}


def test_refusal_episodes_are_deterministic_and_immutable(no_credentials):
    first = refusal_episodes()
    second = refusal_episodes()
    assert first == second
    with pytest.raises(FrozenInstanceError):
        first[0].outcome = EpisodeOutcome.SUCCESS  # type: ignore[misc]


def test_refusal_episodes_support_later_failure_pattern_matching(no_credentials):
    candidates = failure_pattern_candidates(refusal_episodes())
    assert candidates, "immutable refusal episodes must be matchable"
    for candidate in candidates:
        assert candidate.authority is LessonAuthority.CANDIDATE
        assert "provider:NO_CREDENTIAL" in candidate.core_failure_signature
        assert len(candidate.supporting_episode_ids) >= 2
        assert len(candidate.variation_signatures) >= 2


def test_only_fibres_whose_provider_role_lacks_a_credential_are_blocked(no_credentials):
    blocked = set(blocked_mechanic_ids())
    # Retrieval uses open endpoints, so the search fibre is not credential-blocked;
    # collapsing the whole trial into "blocked" would hide that.
    assert "p5.live.search" not in blocked
    assert "p5.live.residual_detection" not in blocked
    assert {"p5.live.interpretation", "p5.live.verification"} <= blocked


# ---------------------------------------------------------------------------
# 6. Authority boundary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("kind", list(AuthorityRequestKind))
def test_every_promotion_attempt_is_refused(kind):
    decision = request_promotion(kind, requester="self-orion", model_output_digest="abc")
    assert decision.granted is False
    assert any("may not merge or promote" in item for item in decision.reasons)
    assert SUCCESS_BOUNDARY in decision.reasons


def test_a_granted_authority_decision_cannot_be_constructed():
    with pytest.raises(ValueError, match="may grant"):
        AuthorityDecision(AuthorityRequestKind.PROMOTE_SELF_ORION, "self-orion", True)


def test_a_strong_model_output_does_not_change_the_decision():
    weak = request_promotion(
        AuthorityRequestKind.MERGE_REPAIR, requester="self-orion", model_output_digest="a"
    )
    strong = request_promotion(
        AuthorityRequestKind.MERGE_REPAIR,
        requester="self-orion",
        model_output_digest="b" * 64,
    )
    assert weak.granted is strong.granted is False


def test_a_failure_pattern_cannot_self_assert_promoted_authority():
    """The invariant lives in the type, so this holds for every caller."""

    with pytest.raises(ValueError, match="cannot self-assert"):
        FailurePatternCandidate(
            pattern_id="p",
            mechanic_id="p5.live.interpretation",
            core_failure_signature=("provider:NO_CREDENTIAL",),
            variation_signatures=(("a",), ("b",)),
            supporting_episode_ids=("e1", "e2"),
            candidate_guard="guard",
            falsifier="falsifier",
            authority=LessonAuthority.VERIFIED_LOCAL,
        )


def test_self_orion_may_propose_a_repair_but_not_authorize_it(no_credentials):
    episodes = tuple(
        item
        for item in refusal_episodes()
        if item.mechanic_id == "p5.live.interpretation"
    )
    proposal = propose_repair(
        episodes,
        proposal_id="repair:interpretation",
        diagnosis="the reasoner role has no credential, so no claim can be extracted",
        proposed_repair="record CANNOT_CHECK and re-run once the role is configured",
    )
    assert proposal is not None
    assert proposal.authority is LessonAuthority.CANDIDATE
    assert proposal.merge_authorized is False
    with pytest.raises(ValueError, match="self-authorize"):
        replace(proposal, merge_authorized=True)
    with pytest.raises(ValueError, match="promoted authority"):
        replace(proposal, authority=LessonAuthority.CONDITIONALLY_REUSABLE)


def test_a_repair_proposal_needs_evidence():
    assert propose_repair((), proposal_id="p", diagnosis="d", proposed_repair="r") is None


def test_repair_proposal_requires_a_single_mechanic(no_credentials):
    assert (
        propose_repair(
            refusal_episodes(), proposal_id="p", diagnosis="d", proposed_repair="r"
        )
        is None
    )


def test_a_repair_proposal_cannot_be_born_promoted():
    with pytest.raises(ValueError, match="promoted authority"):
        RepairProposal(
            proposal_id="p",
            mechanic_id="m",
            diagnosis="d",
            proposed_repair="r",
            supporting_episode_ids=("e1",),
            authority=LessonAuthority.VERIFIED_LOCAL,
        )


# ---------------------------------------------------------------------------
# 7. Bounded saturation outcomes
# ---------------------------------------------------------------------------


def test_open_and_cannot_check_are_outcomes_rather_than_failures():
    for outcome in BoundedSaturationOutcome:
        state = BoundedSaturationState(outcome, ("reason",))
        assert state.is_failure is False
        assert state.certifies_recall is False


def test_pre_execution_saturation_is_cannot_check_with_a_reason():
    state = pre_execution_saturation_state()
    assert state.outcome is BoundedSaturationOutcome.CANNOT_CHECK
    assert state.is_failure is False
    assert any("has not executed" in item for item in state.reasons)


# ---------------------------------------------------------------------------
# 8. Preflight and the one command
# ---------------------------------------------------------------------------


def test_preflight_separates_the_credential_blocker_from_the_bindable_one(
    no_credentials,
):
    report = preflight()
    assert report.runnable is False
    assert report.corpus_revision == UNBOUND
    assert any("credential" in item for item in report.blockers)
    assert any("corpus revision" in item for item in report.blockers)
    assert report.saturation.outcome is BoundedSaturationOutcome.CANNOT_CHECK
    assert report.open_question_count > 0
    assert report.boundary == SUCCESS_BOUNDARY


def test_preflight_flags_an_evaluation_epoch_that_contradicts_the_freeze(monkeypatch):
    monkeypatch.setenv("ORION_PHASE2_EVALUATION_EPOCH_ID", "some-other-epoch")
    report = preflight()
    assert "differs from the frozen epoch" in report.epoch_conflict
    assert any("differs from the frozen epoch" in item for item in report.blockers)


def test_binding_the_corpus_revision_clears_that_blocker_only(no_credentials):
    report = preflight(frozen_live_research_packet(corpus_revision="rev-1"))
    assert not any("corpus revision" in item for item in report.blockers)
    assert any("credential" in item for item in report.blockers)
    assert report.runnable is False


def test_default_command_reports_the_frozen_packet_and_exits_ok(no_credentials, capsys):
    assert main([]) == EXIT_OK
    out = capsys.readouterr().out
    assert frozen_live_research_packet().fingerprint in out
    assert "WIDE_LITERATURE" in out and "DEEP_TARGET" in out
    assert "provider_required=False" in out
    assert SUCCESS_BOUNDARY in out


def test_live_refuses_before_constructing_anything_and_exits_cannot_check(
    no_credentials, capsys
):
    assert main(["--live"]) == EXIT_CANNOT_CHECK
    err = capsys.readouterr().err
    assert "refusing to start the live trial" in err
    # The refusal must be actionable: it names the real constructor, the real
    # variables and the immutable evidence it recorded instead of a zero.
    assert "build_phase2_live_provider_stack_from_env" in err
    for name in CREDENTIAL_ENV_VARS:
        assert name in err
    assert "CANNOT_CHECK episode" in err


def test_questions_command_prints_the_surface_with_no_provider(no_credentials, capsys):
    assert main(["--questions"]) == EXIT_OK
    out = capsys.readouterr().out
    for dimension in ISSUE_8_DIMENSIONS:
        assert dimension.value in out


def test_emit_protocol_reproduces_the_checked_in_packet(tmp_path, capsys):
    target = tmp_path / "LIVE_TRIAL_PACKET_V1.json"
    assert main(["--emit-protocol", str(target)]) == EXIT_OK
    capsys.readouterr()
    assert json.loads(target.read_text(encoding="utf-8")) == json.loads(
        PROTOCOL_PATH.read_text(encoding="utf-8")
    )
