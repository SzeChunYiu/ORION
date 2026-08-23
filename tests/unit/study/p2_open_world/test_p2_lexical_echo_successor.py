"""Tests for the P2 lexical-echo successor study.

The study's whole credibility rests on two things being checkable: that the
constructed world really carries the mechanism named in
`DEEP_ZERO_HIT_STAGE_ATTRIBUTION_2026-08-17.json`, and that the numbers in the
result artifact are the ones the frozen code produces. These tests check both,
plus the structural guarantees the freeze document claims (demote-not-delete,
matched query width, no gold leakage into any arm).
"""

from __future__ import annotations

import inspect
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from orion.study.p2 import echo_campaign as campaign
from orion.study.p2 import echo_mechanics as mech
from orion.study.p2 import echo_world as world_module

REPO_ROOT = Path(__file__).resolve().parents[4]
FREEZE_MD = REPO_ROOT / campaign.FREEZE_DOCUMENT
FREEZE_JSON = REPO_ROOT / campaign.FREEZE_TWIN
RESULT_JSON = REPO_ROOT / campaign.DEFAULT_OUTPUT


@pytest.fixture(scope="module")
def world() -> world_module.EchoWorld:
    return world_module.build_echo_world()


@pytest.fixture(scope="module")
def index(world: world_module.EchoWorld) -> mech.EchoIndex:
    return mech.build_index(world.documents)


@pytest.fixture(scope="module")
def payload() -> dict:
    return campaign.run_campaign()


# ---------------------------------------------------------------------------
# Freeze integrity
# ---------------------------------------------------------------------------


def test_freeze_documents_exist() -> None:
    assert FREEZE_MD.exists(), "the prose freeze must be in the record"
    assert FREEZE_JSON.exists(), "the machine-readable freeze twin must be in the record"


def test_runner_parameters_match_the_frozen_twin() -> None:
    twin = json.loads(FREEZE_JSON.read_text(encoding="utf-8"))
    assert twin["parameters_sha256"] == campaign.frozen_digest()
    assert campaign.verify_against_twin(REPO_ROOT)["parameters_sha256"] == (
        campaign.frozen_digest()
    )


def test_freeze_twin_records_the_environment_boundary() -> None:
    twin = json.loads(FREEZE_JSON.read_text(encoding="utf-8"))
    boundary = twin["environment_boundary"]
    assert boundary["official_rerun_possible"] is False
    assert boundary["official_input_present_in_repo"] is False
    assert twin["parameters"]["claim_scope"] == "CONSTRUCTED_REPRODUCTION_ONLY"


def test_main_requires_argv() -> None:
    """`orion.study.p2.echo_campaign.main` must not run on an implicit argv."""

    signature = inspect.signature(campaign.main)
    assert signature.parameters["argv"].default is inspect.Parameter.empty


def test_the_runner_is_reachable_as_a_module() -> None:
    """A `main` nothing can invoke is not a runner.

    The freeze document commits to shipping this study as a runner. Without a
    `__main__` guard `python -m orion.study.p2.echo_campaign` imports the module,
    executes nothing and exits 0 -- success and no-op are the same character,
    which is the failure family this programme keeps finding one level down.
    `--print-digest` exercises the entry point without paying for a campaign.
    """

    completed = subprocess.run(
        [sys.executable, "-m", "orion.study.p2.echo_campaign", "--print-digest"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == campaign.frozen_digest()


# ---------------------------------------------------------------------------
# The world reproduces the named mechanism
# ---------------------------------------------------------------------------


def test_world_shape(world: world_module.EchoWorld) -> None:
    assert len(world.tasks) == sum(world_module.FAMILY_SIZES.values()) == 220
    for family, size in world_module.FAMILY_SIZES.items():
        assert len(world.tasks_in(family)) == size
    expected = (
        220  # needles
        + 220 * world_module.NEIGHBOURS_PER_TASK
        + world_module.FAMILY_SIZES[world_module.FAMILY_ECHO]
        * world_module.ECHO_DISTRACTORS_PER_ECHO_TASK
        + world_module.BACKGROUND_FILLERS
    )
    assert len(world.documents) == expected == 2760


def test_needles_never_carry_an_apparatus_term(world: world_module.EchoWorld) -> None:
    """Property 2 of the reproduction: the needle is the document that cannot
    match the question's apparatus vocabulary."""

    incidental = set(world_module.INCIDENTAL_LEXICON)
    targets = {task.target_doc_id for task in world.tasks}
    for document in world.documents:
        if document.doc_id not in targets:
            continue
        tokens = set(f"{document.title} {document.abstract}".lower().split())
        assert not (tokens & incidental), document.doc_id


def test_echo_distractors_have_the_supplementary_orbit_shape(
    world: world_module.EchoWorld,
) -> None:
    incidental = set(world_module.INCIDENTAL_LEXICON)
    domain = set(world_module.DOMAIN_LEXICON)
    seen = 0
    for document in world.documents:
        if "-echo" not in document.doc_id:
            continue
        seen += 1
        first, second = document.title.split()
        assert first.lower() in incidental
        assert second.lower() in domain
    assert seen == 720


def test_world_precondition_holds(
    world: world_module.EchoWorld, index: mech.EchoIndex
) -> None:
    """Apparatus words must really be non-discriminative and content words must
    really be discriminative, or the world is not the one the freeze specifies."""

    report = campaign.world_precondition(world, index)
    assert report["passed"] is True
    assert report["apparatus_df_fraction_median"] >= world_module.MIN_APPARATUS_DF_FRACTION
    assert report["content_df_fraction_median"] <= world_module.MAX_CONTENT_DF_FRACTION


def test_paraphrase_surface_leak_is_bounded_and_declared(
    world: world_module.EchoWorld, payload: dict
) -> None:
    """The freeze asks `paraphrase_gap` needles to share no content token with
    their question. The synonym map permutes the whole domain lexicon, so one of
    a task's own four terms can be the image of another and the guarantee does
    not hold everywhere. The world is not re-rolled to hide that — the defect is
    declared in the result artifact and pinned here."""

    by_id = world.world.by_id
    leaking = {}
    for task in world.tasks_in(world_module.FAMILY_PARAPHRASE):
        document = by_id[task.target_doc_id]
        tokens = set(f"{document.title} {document.abstract}".lower().split())
        overlap = tokens & set(task.content_terms)
        if overlap:
            leaking[task.task_id] = sorted(overlap)

    assert len(leaking) == 4
    assert all(len(terms) == 1 for terms in leaking.values())

    declared = payload["known_construction_defects"][0]
    assert declared["defect"] == "PARAPHRASE_SYNONYM_MAP_IS_NOT_TASK_DISJOINT"
    assert declared["tasks_affected"] == len(leaking)
    assert sorted(declared["affected_task_ids"]) == sorted(leaking)


def test_specificity_control_is_unaffected_by_the_leak(payload: dict) -> None:
    """The control's conclusion is that no lexical arm repairs a semantic gap.
    That holds only if every arm really scores zero there."""

    for arm, summary in payload["arms"][world_module.FAMILY_PARAPHRASE].items():
        assert summary["hit_at_10"] == 0.0, arm
        assert summary["hit_at_1"] == 0.0, arm


# ---------------------------------------------------------------------------
# Mechanics
# ---------------------------------------------------------------------------


def test_baseline_query_admits_the_apparatus_terms(
    world: world_module.EchoWorld,
) -> None:
    """The reproduction claim: D1 lets incidental vocabulary into the query."""

    for task in world.tasks_in(world_module.FAMILY_ECHO)[:20]:
        terms = mech.baseline_query(task.question)
        assert set(task.incidental_terms) <= set(terms)


def test_successor_query_rejects_every_apparatus_term(
    world: world_module.EchoWorld, index: mech.EchoIndex
) -> None:
    incidental = set(world_module.INCIDENTAL_LEXICON)
    for task in world.tasks_in(world_module.FAMILY_ECHO):
        terms = mech.successor_query(task.question, index)
        assert not (set(terms) & incidental)


def test_query_widths_are_matched(world: world_module.EchoWorld, index: mech.EchoIndex) -> None:
    """The successor must not win by being allowed a wider query."""

    for task in world.tasks:
        assert len(mech.baseline_query(task.question)) <= mech.QUERY_WIDTH
        assert len(mech.successor_query(task.question, index)) <= mech.QUERY_WIDTH


def test_no_arm_expands_beyond_the_question(
    world: world_module.EchoWorld, index: mech.EchoIndex
) -> None:
    """No arm may introduce a term the asker did not write: that would be
    deriving the query from the answer."""

    for task in world.tasks:
        asked = set(mech._content_tokens(task.question))
        assert set(mech.baseline_query(task.question)) <= asked
        assert set(mech.successor_query(task.question, index)) <= asked


def test_admission_demotes_and_never_deletes(index: mech.EchoIndex) -> None:
    """The topical-agreement rule must not be able to inflate recall at large k."""

    terms = ("orbit", "resonance", "manifold")
    scores = mech._weighted_scores(terms, index)
    matches = mech._match_counts(terms, index)
    ranking = mech._rank(index, scores, matches)
    assert len(ranking) == len(index.doc_ids)
    assert set(ranking) == set(index.doc_ids)

    positions = {doc_id: position for position, doc_id in enumerate(ranking)}
    admitted = [d for d in index.doc_ids if matches.get(d, 0) >= mech.MIN_CONTENT_MATCH]
    rejected = [d for d in index.doc_ids if matches.get(d, 0) < mech.MIN_CONTENT_MATCH]
    if admitted and rejected:
        assert max(positions[d] for d in admitted) < min(positions[d] for d in rejected)


def test_arms_never_receive_the_gold(
    world: world_module.EchoWorld, index: mech.EchoIndex
) -> None:
    """The package boundary rule: an arm sees the question and the index, and
    nothing that could identify the answer."""

    signature = inspect.signature(mech.generate_candidates)
    assert list(signature.parameters) == ["arm", "question", "index"]
    task = world.tasks_in(world_module.FAMILY_ECHO)[0]
    terms, ranking = mech.generate_candidates(mech.ARM_S1, task.question, index)
    via_host = mech.run_arm(mech.ARM_S1, task, index)
    assert terms == via_host.query_terms
    assert ranking[: mech.MRR_DEPTH] == via_host.ranking


def test_unknown_arm_is_rejected(index: mech.EchoIndex) -> None:
    with pytest.raises(ValueError):
        mech.generate_candidates("NOT_AN_ARM", "orbit resonance", index)


def test_ranking_is_deterministic(world: world_module.EchoWorld, index: mech.EchoIndex) -> None:
    task = world.tasks[0]
    first = mech.run_arm(mech.ARM_S1, task, index)
    second = mech.run_arm(mech.ARM_S1, task, index)
    assert first.ranking == second.ranking
    assert first.target_rank == second.target_rank


def test_mcnemar_exact_known_values() -> None:
    assert mech.mcnemar_exact([False] * 10, [False] * 10)["p_value"] == 1.0
    all_gain = mech.mcnemar_exact([False] * 10, [True] * 10)
    assert all_gain["b"] == 0 and all_gain["c"] == 10
    assert all_gain["p_value"] == pytest.approx(2.0 / 1024.0)
    symmetric = mech.mcnemar_exact([True, False], [False, True])
    assert symmetric["p_value"] == 1.0
    with pytest.raises(ValueError):
        mech.mcnemar_exact([True], [True, False])


# ---------------------------------------------------------------------------
# The recorded result
# ---------------------------------------------------------------------------


# Every arm field a gate consumes. G1, G2, G3 and G5 read hit_at_10; G4 reads
# hit_at_1. These are compared exactly -- the tolerance below must never be able
# to reach a number a gate acts on, or it would launder a real change.
GATE_READ_FIELDS = ("hit_at_1", "hit_at_10")

# A mean of reciprocal ranks is a floating-point sum, and its last bits depend on
# summation order, which moves between library versions. Bit-equality across
# environments is therefore not something any environment can promise, and a
# reproduction check that demands it is an unattainable gate rather than a failed
# one. Four mrr_at_50 values were observed at up to three units in the last
# place; the smallest gate threshold is 0.01, thirteen orders of magnitude away.
# See papers/paper-02-open-world-scientific-discovery/
# P2_LEXICAL_ECHO_REPRODUCTION_DIAGNOSIS_2026-08-23.json.
MAX_ULPS = 4


def _ulp_distance(left: float, right: float, cap: int = 4096) -> int:
    if left == right:
        return 0
    low, high = min(left, right), max(left, right)
    steps = 0
    while low < high and steps < cap:
        low = math.nextafter(low, math.inf)
        steps += 1
    return steps


def _assert_arms_reproduce(fresh, recorded, path: str = "arms") -> None:
    """Exact everywhere except reported floats no gate reads, which get MAX_ULPS."""

    assert type(fresh) is type(recorded), f"{path}: type changed"
    if isinstance(fresh, dict):
        assert set(fresh) == set(recorded), f"{path}: field set changed"
        for key in sorted(fresh):
            _assert_arms_reproduce(fresh[key], recorded[key], f"{path}/{key}")
        return
    if isinstance(fresh, list):
        assert len(fresh) == len(recorded), f"{path}: length changed"
        for index, (a, b) in enumerate(zip(fresh, recorded)):
            _assert_arms_reproduce(a, b, f"{path}[{index}]")
        return
    field = path.rsplit("/", 1)[-1]
    if isinstance(fresh, float) and isinstance(recorded, float) and field not in GATE_READ_FIELDS:
        distance = _ulp_distance(fresh, recorded)
        assert distance <= MAX_ULPS, (
            f"{path}: {recorded!r} -> {fresh!r} is {distance} ulps, beyond the "
            f"{MAX_ULPS}-ulp reproduction tolerance; this is a changed result, not float noise"
        )
        return
    assert fresh == recorded, f"{path}: {recorded!r} -> {fresh!r}"


def test_result_artifact_matches_a_fresh_run(payload: dict) -> None:
    """The archived numbers must be the ones the frozen code still produces."""

    assert RESULT_JSON.exists()
    recorded = json.loads(RESULT_JSON.read_text(encoding="utf-8"))
    assert recorded["parameters_sha256"] == campaign.frozen_digest()
    assert recorded["verdict"] == payload["verdict"]
    assert recorded["world_content_hash"] == payload["world_content_hash"]
    _assert_arms_reproduce(payload["arms"], recorded["arms"])
    assert recorded["gate_results"] == payload["gate_results"]


def test_the_reproduction_tolerance_cannot_hide_a_real_change(payload: dict) -> None:
    """The no-alarm case's twin: a tolerance that accepts anything checks nothing."""

    recorded = json.loads(RESULT_JSON.read_text(encoding="utf-8"))
    arm = dict(recorded["arms"]["echo"]["B0_CURRENT_D1_UNWEIGHTED"])
    arm["mrr_at_50"] = arm["mrr_at_50"] + 1e-9
    tampered = json.loads(json.dumps(recorded["arms"]))
    tampered["echo"]["B0_CURRENT_D1_UNWEIGHTED"] = arm
    with pytest.raises(AssertionError, match="ulps"):
        _assert_arms_reproduce(tampered, recorded["arms"])


def test_a_gate_read_field_is_never_given_any_tolerance() -> None:
    """One ulp on hit_at_10 must still fail: gates act on it."""

    fresh = {"echo": {"ARM": {"hit_at_10": math.nextafter(0.5, math.inf), "tasks": 1}}}
    recorded = {"echo": {"ARM": {"hit_at_10": 0.5, "tasks": 1}}}
    with pytest.raises(AssertionError):
        _assert_arms_reproduce(fresh, recorded)


def test_verdict_follows_the_frozen_rule(payload: dict) -> None:
    gates = payload["gate_results"]
    g1 = gates["G1_REPRODUCTION"]["passed"]
    g2 = gates["G2_SUCCESSOR"]["passed"]
    g3 = gates["G3_HARM"]["passed"]
    if not g1:
        expected = "REPRODUCTION_FAILED__NO_SUCCESSOR_CLAIM"
    elif g2 and g3:
        expected = "VALIDATED_ON_CONSTRUCTED_REPRODUCTION"
    elif g2:
        expected = "SUCCESSOR_GAIN_ON_MODE__HARMFUL_OFF_MODE__NO_SUCCESSOR_CLAIM"
    else:
        expected = "SUCCESSOR_NOT_VALIDATED__NEGATIVE_STANDS"
    assert payload["verdict"] == expected


def test_claim_scope_is_recorded_and_narrow(payload: dict) -> None:
    assert payload["claim_scope"] == "CONSTRUCTED_REPRODUCTION_ONLY"
    joined = " ".join(payload["not_licensed"]).lower()
    assert "target_hits" in joined
    assert "arxiv" in joined


def test_harm_guard_is_not_vacuous(payload: dict) -> None:
    """A harm guard whose baseline already fails would prove nothing."""

    guard = payload["gate_results"]["G3_HARM"]
    assert guard["vacuous"] is False


def test_archived_probe_artifacts_are_untouched() -> None:
    """This study adds records; it never rewrites the negative it repairs."""

    external = (
        REPO_ROOT
        / "papers/paper-02-open-world-scientific-discovery/evidence/external_results"
    )
    probe = json.loads((external / "AUTORESEARCHBENCH_DEEP_ID_PROBE_V1.json").read_text())
    attribution = json.loads(
        (external / "DEEP_ZERO_HIT_STAGE_ATTRIBUTION_2026-08-17.json").read_text()
    )
    control = json.loads((external / "DEEP_JUDGE_CONTROL_2026-08-17.json").read_text())
    assert probe["target_hits"] == 0
    assert probe["deep_tasks"] == 600
    assert attribution["counts"]["exact_title_recoveries"] == 0
    assert attribution["counts"]["token_overlap_ge_0.5_recoveries"] == 8
    assert control["verdict"] == "CONTROL_PASSED"
