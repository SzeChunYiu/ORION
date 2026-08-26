"""The frozen ORION-P1 hidden-shift case suite must earn the right to be scored.

A benchmark that leaks its own answer produces a number, and the number means
nothing. These tests are the leak audit, not a smoke test: they load the frozen
suite from disk, assert the contract the protocol depends on, and run the
degeneracy probe over the panel as a whole. If the probe stops returning CLEAN,
the suite is at fault and the suite is what gets fixed.
"""

from __future__ import annotations

import random
import re
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from statistics import mean, pstdev

import pytest

from orion.benchmarks.degeneracy import DegeneracyStatus, LabeledRecord, probe_records
from orion.study.p1.arm_validity import find_lexical_separators
from orion.study.p1.cases import (
    AdjudicationStatus,
    HiddenShiftCase,
    Split,
    TaskFamily,
    load_cases,
    suite_fingerprint,
)

CASES_ROOT = (
    Path(__file__).resolve().parents[4]
    / "papers"
    / "orion-11-recursive-epistemic-reconstruction"
    / "protocol"
    / "cases"
)

CONTROLS = {TaskFamily.EVIDENCE_ONLY_CONTROL, TaskFamily.EXECUTION_ONLY_CONTROL}
PER_FAMILY = {Split.PILOT: 3, Split.TEST: 8}
FAMILY_ORDER = tuple(family.value for family in TaskFamily)

_TOKEN = re.compile(r"[a-z0-9]+")

# `only` is a structural adverb inside two frozen family names
# (`evidence_only_negative_control`, `execution_only_negative_control`). It
# carries no information about which family a case belongs to, so banning it from
# 22 prompts would police English rather than protect the label. Every other gold
# token, including every axis and target word, is banned outright.
DECLARED_STOPWORDS = frozenset({"only"})


def tokens(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower().replace("-", " ").replace("_", " ")))


def gold_vocabulary(case: HiddenShiftCase) -> set[str]:
    """Every word a solver would have to be told to answer this case for free."""

    raw: set[str] = set()
    for text in (
        case.task_family.value,
        case.protected_gold.responsibility_family,
        *case.protected_gold.target_coordinates,
    ):
        raw |= tokens(text)
    return {word for word in raw if len(word) >= 3 and word.isalpha()} - DECLARED_STOPWORDS


@pytest.fixture(scope="module")
def suites() -> dict[Split, tuple[HiddenShiftCase, ...]]:
    return {split: load_cases(CASES_ROOT, split=split) for split in Split}


# --------------------------------------------------------------------------- #
# the suite exists, loads, and is the size the protocol declares
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("split", list(Split))
def test_every_case_loads_and_validates(suites, split) -> None:
    """`load_cases` runs `__post_init__` on each file, so loading is validating.

    The count is asserted because `load_cases` returns an empty tuple for a
    missing directory: without it, a wrong path would read as a passing test.
    """

    cases = suites[split]
    assert len(cases) == PER_FAMILY[split] * len(TaskFamily)
    assert all(case.split is split for case in cases)
    assert len({case.case_id for case in cases}) == len(cases)


@pytest.mark.parametrize("split", list(Split))
def test_family_counts_are_exactly_as_specified(suites, split) -> None:
    counts = Counter(case.task_family for case in suites[split])
    assert counts == {family: PER_FAMILY[split] for family in TaskFamily}


@pytest.mark.parametrize("split", list(Split))
def test_the_whole_suite_is_mechanical_gold(suites, split) -> None:
    """The two human-adjudicated families are out of scope and stay open."""

    assert all(
        case.adjudication_status is AdjudicationStatus.MECHANICAL_GOLD
        for case in suites[split]
    )


@pytest.mark.parametrize("split", list(Split))
def test_budget_class_is_constant_across_the_suite(suites, split) -> None:
    """`budget_class` is public via `PublicView`.

    Any per-family variation would let a system read the family straight off the
    public view, which the protocol's `hidden_labels` policy forbids.
    """

    assert {case.budget_class for case in suites[split]} == {"p1_standard_v1"}


# --------------------------------------------------------------------------- #
# the gold contract each family carries
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("split", list(Split))
def test_hidden_shift_cases_carry_a_typed_reframe_and_a_reopen_set(suites, split) -> None:
    shifts = [c for c in suites[split] if c.task_family not in CONTROLS]
    assert len(shifts) == PER_FAMILY[split] * 4
    for case in shifts:
        gold = case.protected_gold
        assert gold.reframe_required
        assert len(gold.target_coordinates) == 2, case.case_id
        axis, target = gold.target_coordinates
        assert axis.split(".")[0] in {"W", "M"}, case.case_id
        assert ":" in target, case.case_id
        assert gold.dependencies_to_reopen, case.case_id
        assert 1 <= gold.dependency_depth <= 3, case.case_id
        assert gold.root_success_rubric.strip()


@pytest.mark.parametrize("split", list(Split))
def test_every_hidden_shift_family_spans_all_three_dependency_depths(suites, split) -> None:
    """H3 analyses reopening *by depth*; a family stuck at one depth measures nothing."""

    for family in set(TaskFamily) - CONTROLS:
        depths = {
            case.protected_gold.dependency_depth
            for case in suites[split]
            if case.task_family is family
        }
        assert depths == {1, 2, 3}, (family, depths)


@pytest.mark.parametrize("split", list(Split))
def test_negative_controls_require_no_reframe_and_no_reopen(suites, split) -> None:
    controls = [c for c in suites[split] if c.task_family in CONTROLS]
    assert len(controls) == PER_FAMILY[split] * 2
    for case in controls:
        gold = case.protected_gold
        assert not gold.reframe_required
        assert gold.target_coordinates == ()
        assert gold.dependencies_to_reopen == ()
        assert gold.dependency_depth == 0
        assert gold.responsibility_family in {"EVIDENCE", "EXECUTION"}


@pytest.mark.parametrize("split", list(Split))
def test_reopen_targets_are_visible_in_the_public_view(suites, split) -> None:
    """A reopen target no system can see makes reopen recall unmeasurable.

    Every dependency is named in the case's own `observable_resources`, so a
    system can answer in the same namespace the gold is scored in.
    """

    for case in suites[split]:
        blob = " ".join(case.observable_resources)
        for dependency in case.protected_gold.dependencies_to_reopen:
            assert dependency.startswith("closure:"), case.case_id
            assert dependency in blob, (case.case_id, dependency)


def named_closures(case: HiddenShiftCase) -> set[str]:
    return set(re.findall(r"(closure:[a-z0-9-]+)", " ".join(case.observable_resources)))


def reopen_f1(reopened: set[str], gold: tuple[str, ...]) -> float:
    if not gold or not reopened:
        return 0.0
    hits = len(reopened & set(gold))
    if not hits:
        return 0.0
    precision, recall = hits / len(reopened), hits / len(gold)
    return 2 * precision * recall / (precision + recall)


@pytest.mark.parametrize("split", list(Split))
def test_every_hidden_shift_case_carries_a_closure_that_must_survive(suites, split) -> None:
    """Reopen precision has to have something to lose, or H3 is unfalsifiable.

    If every closure a case names is also a gold dependency, then reopening
    everything is exactly right, and `full_reset_instead_of_dependency_reopen`
    cannot be distinguished from dependency-directed reopening. Each hidden-shift
    case therefore names at least one closed conclusion that does NOT rest on the
    formulation under revision and must be left alone.
    """

    for case in suites[split]:
        if case.task_family in CONTROLS:
            continue
        survivors = named_closures(case) - set(case.protected_gold.dependencies_to_reopen)
        assert survivors, case.case_id


@pytest.mark.parametrize("split", list(Split))
def test_reopening_everything_is_punished_on_every_hidden_shift_case(suites, split) -> None:
    """The discriminating cell H3 needs, asserted as the ablation would score it.

    A full-reset policy reopens every closure the case names. Scored against
    gold, it must lose precision on every single case — otherwise the ablation
    ties full ORION for free and the comparison measures nothing.
    """

    for case in suites[split]:
        if case.task_family in CONTROLS:
            continue
        gold = case.protected_gold.dependencies_to_reopen
        full_reset = reopen_f1(named_closures(case), gold)
        directed = reopen_f1(set(gold), gold)
        assert directed == 1.0, case.case_id
        assert full_reset < 1.0, case.case_id


def _resource_bulk(case: HiddenShiftCase) -> float:
    return float(sum(len(r) for r in case.observable_resources))


def _closure_count(case: HiddenShiftCase) -> float:
    return float(sum(r.startswith("closure:") for r in case.observable_resources))


# `resource_count`, `closure_count` and `noncloture_count` are linearly
# dependent: the first is the sum of the other two. All three are audited,
# because balancing exactly two of them does not balance the family — it pushes
# the whole residual into the third, which is exactly how a leak once survived
# here. Character-class surfaces are covered for the same reason: a rule as
# cheap as "the prompt contains a digit" once separated controls from
# hidden-shift cases at 0.771 against a 0.667 baseline.
PUBLIC_SURFACES: dict[str, Callable[[HiddenShiftCase], float]] = {
    "prompt_len": lambda c: float(len(c.public_prompt)),
    "prompt_words": lambda c: float(len(c.public_prompt.split())),
    "prompt_sentences": lambda c: float(
        c.public_prompt.count(". ") + c.public_prompt.count("? ") + 1
    ),
    "resource_count": lambda c: float(len(c.observable_resources)),
    "resource_bulk": _resource_bulk,
    "closure_count": _closure_count,
    "noncloture_count": lambda c: float(len(c.observable_resources)) - _closure_count(c),
    "total_chars": lambda c: float(len(c.public_prompt)) + _resource_bulk(c),
    "prompt_share": lambda c: len(c.public_prompt) / (len(c.public_prompt) + _resource_bulk(c)),
    "mean_resource_len": lambda c: _resource_bulk(c) / len(c.observable_resources),
    "digit_density": lambda c: sum(ch.isdigit() for ch in c.public_prompt) / len(c.public_prompt),
    "has_digit": lambda c: float(any(ch.isdigit() for ch in c.public_prompt)),
    "uppercase_share": lambda c: sum(ch.isupper() for ch in c.public_prompt) / len(c.public_prompt),
    "comma_count": lambda c: float(c.public_prompt.count(",")),
    "digit_runs": lambda c: float(
        sum(
            1
            for i, ch in enumerate(c.public_prompt)
            if ch.isdigit() and (i == 0 or not c.public_prompt[i - 1].isdigit())
        )
    ),
}

# Excluded from the joint space only because they are exact functions of other
# members; including them would count one direction several times over.
_REDUNDANT_IN_JOINT_SPACE = frozenset({"total_chars", "resource_count"})


def max_between_group_mean_gap(values: Sequence[float], labels: Sequence[str]) -> float:
    grouped: dict[str, list[float]] = {}
    for value, label in zip(values, labels):
        grouped.setdefault(label, []).append(value)
    means = [mean(group) for group in grouped.values()]
    return max(means) - min(means)


def shuffle_null_p(values: Sequence[float], labels: Sequence[str], *, reps: int = 2000) -> float:
    """Probability of a gap this large when the labels carry no information.

    Deliberately not a best-single-threshold detector. A threshold is
    under-powered against a non-monotonic ordering, and it passed a real
    prompt-length leak whose family means ran high-middle-low-middle with no
    separating cut. Comparing group means catches that; a shuffle-equal-n null is
    what makes the number mean anything.
    """

    observed = max_between_group_mean_gap(values, labels)
    rng = random.Random(20260815)
    shuffled = list(labels)
    hits = 0
    for _ in range(reps):
        rng.shuffle(shuffled)
        hits += max_between_group_mean_gap(values, shuffled) >= observed
    return hits / reps


def surface_labels(cases: Sequence[HiddenShiftCase]) -> dict[str, list[str]]:
    return {
        "family": [case.task_family.value for case in cases],
        "control_vs_hidden_shift": [str(case.task_family in CONTROLS) for case in cases],
    }


def _standardised_rows(cases: Sequence[HiddenShiftCase]) -> list[tuple[float, ...]]:
    """The public surfaces as one point per case, each surface on a common scale."""

    columns = []
    for name, feature in PUBLIC_SURFACES.items():
        if name in _REDUNDANT_IN_JOINT_SPACE:
            continue
        raw = [feature(case) for case in cases]
        centre, spread = mean(raw), pstdev(raw) or 1.0
        columns.append([(value - centre) / spread for value in raw])
    return [tuple(row) for row in zip(*columns)]


def _nearest_neighbour_index(rows: Sequence[tuple[float, ...]]) -> list[int]:
    nearest: list[int] = []
    for i, row in enumerate(rows):
        best_distance = None
        best_j = 0
        for j, other in enumerate(rows):
            if i == j:
                continue
            distance = sum((a - b) ** 2 for a, b in zip(row, other))
            if best_distance is None or distance < best_distance:
                best_distance, best_j = distance, j
        nearest.append(best_j)
    return nearest


def _neighbour_agreement(nearest: Sequence[int], labels: Sequence[str]) -> float:
    return sum(labels[i] == labels[j] for i, j in enumerate(nearest)) / len(labels)


def joint_null_p(
    cases: Sequence[HiddenShiftCase], labels: Sequence[str], *, reps: int = 2000
) -> float:
    """Do cases of one family sit near each other in the joint surface space?

    Comparing group means one surface at a time cannot see a cue carried by a
    *combination* of surfaces: an exclusive-or arrangement has identical group
    means on every axis and is still perfectly separable. Nearest-neighbour
    agreement is local, so it sees that, and the companion test plants exactly
    such an arrangement and requires this to fire on it.
    """

    nearest = _nearest_neighbour_index(_standardised_rows(cases))
    observed = _neighbour_agreement(nearest, labels)
    rng = random.Random(20260815)
    shuffled = list(labels)
    hits = 0
    for _ in range(reps):
        rng.shuffle(shuffled)
        hits += _neighbour_agreement(nearest, shuffled) >= observed
    return hits / reps


def best_threshold_lift(values: Sequence[float], labels: Sequence[str]) -> float:
    """How much the best single cut on one surface beats guessing the majority."""

    baseline = Counter(labels).most_common(1)[0][1] / len(labels)
    best = 0.0
    for cut in sorted(set(values)):
        low = [lab for value, lab in zip(values, labels) if value <= cut]
        high = [lab for value, lab in zip(values, labels) if value > cut]
        hits = sum(Counter(part).most_common(1)[0][1] for part in (low, high) if part)
        best = max(best, hits / len(labels))
    return best - baseline


def holm_rejects(p_values: Mapping[str, float], *, alpha: float = 0.05) -> list[str]:
    """Holm step-down, the correction the protocol's `multiplicity` clause names.

    This audit runs one comparison per surface per labelling per split. At that
    many comparisons a single uncorrected p just under 0.05 is what the null
    produces, not a finding: the full 180-comparison sweep over both batteries
    returned twelve such p-values and zero Holm rejections.
    """

    ordered = sorted(p_values.items(), key=lambda item: item[1])
    rejected = []
    for rank, (name, p) in enumerate(ordered):
        if p >= alpha / (len(ordered) - rank):
            break
        rejected.append(name)
    return rejected


@pytest.mark.parametrize("split", list(Split))
def test_the_digit_shortcut_stays_neutralised(suites, split) -> None:
    """The one cheap rule this suite actually handed away, pinned as a regression.

    "The prompt contains a digit" scored 0.771 against a 0.667 baseline on the
    control-versus-hidden split: 28 of 32 hidden prompts carried a figure
    against 7 of 16 controls. It needed no world knowledge and a model would
    have used it. Controls were given the numeric detail they should have had —
    rather than stripping figures from hidden prompts, which need them for the
    reframe to be derivable — and the rule now sits at or below the baseline on
    both splits. Asserted against the baseline, not against a chosen constant.
    """

    cases = suites[split]
    labels = surface_labels(cases)["control_vs_hidden_shift"]
    digits = [float(any(ch.isdigit() for ch in case.public_prompt)) for case in cases]
    assert best_threshold_lift(digits, labels) <= 0.0, split


@pytest.mark.parametrize("split", list(Split))
def test_no_surface_marginal_or_joint_separates_the_families(suites, split) -> None:
    """Every surface, plus the joint space, judged family-wise.

    `resource_count`, `closure_count` and `noncloture_count` are audited
    together on purpose: they are linearly dependent, so balancing two of them
    silently loads the third — which is how `noncloture_count` came to carry the
    whole residual at p=0.0024 after an earlier pass balanced the other two.
    """

    cases = suites[split]
    p_values = {}
    for name, feature in PUBLIC_SURFACES.items():
        values = [feature(case) for case in cases]
        for label_name, labels in surface_labels(cases).items():
            p_values[f"{name}/{label_name}"] = shuffle_null_p(values, labels)
    for label_name, labels in surface_labels(cases).items():
        p_values[f"joint/{label_name}"] = joint_null_p(cases, labels)

    assert holm_rejects(p_values) == [], sorted(p_values.items(), key=lambda kv: kv[1])[:3]


def test_the_joint_check_sees_an_interaction_every_marginal_check_misses() -> None:
    """Plant a cue no per-surface test can see and require the joint one to catch it.

    Two surfaces, two families, each family on one diagonal. Every group mean is
    identical on both axes, so mean-gap finds nothing; the families are
    nonetheless perfectly separated locally.
    """

    corners = [(1.0, 1.0), (-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0)]
    labels = ["A", "A", "B", "B"] * 12
    jitter = random.Random(4)
    rows = [
        (x + jitter.gauss(0, 0.05), y + jitter.gauss(0, 0.05))
        for _ in range(12)
        for x, y in corners
    ]

    for axis in (0, 1):
        assert shuffle_null_p([row[axis] for row in rows], labels) >= 0.05

    nearest = _nearest_neighbour_index(rows)
    observed = _neighbour_agreement(nearest, labels)
    rng = random.Random(20260815)
    shuffled = list(labels)
    hits = 0
    for _ in range(2000):
        rng.shuffle(shuffled)
        hits += _neighbour_agreement(nearest, shuffled) >= observed
    assert observed == 1.0
    assert hits / 2000 < 0.05


def test_the_surface_leak_check_detects_a_planted_imbalance(suites) -> None:
    """The clean result above is only worth having if the alarm can fire.

    Plants exactly the defect that was missed: one family's prompts made
    systematically longer, with no separating threshold created.
    """

    cases = suites[Split.TEST]
    labels = [case.task_family.value for case in cases]
    honest = [float(len(case.public_prompt)) for case in cases]
    assert shuffle_null_p(honest, labels) >= 0.05

    planted = [
        value + (120.0 if case.task_family is TaskFamily.HIDDEN_PARENT_DOMAIN else 0.0)
        for value, case in zip(honest, cases)
    ]
    assert shuffle_null_p(planted, labels) < 0.05



@pytest.mark.parametrize("surface", ["prompt", "prompt_and_resources", "resource_stems"])
def test_no_single_token_separates_control_from_hidden_shift(suites, surface) -> None:
    """The leak every statistical battery here was blind to.

    The gold-vocabulary checker asks whether a prompt names the *answer*; the
    distributional batteries ask whether derived numeric surfaces separate the
    families. Neither asks the simplest question there is: does one word predict
    the label? On the suite as first frozen the answer was total — `framing` and
    `team's` appeared in all 44 hidden-shift prompts and no control, so H2's
    control-versus-hidden split was answerable by grep. `plan` leaked the
    opposite way in 17 of 22 controls, which is the same defect with the sign
    reversed, so both directions are tested.

    Resource path stems are covered too: a `/(proposal|trial)/` regex once
    recovered 10 of 11 DECOMPOSITION cases with no false positives, because only
    those cases carried a proposed fix as an artefact.
    """

    cases = [case for split in Split for case in suites[split]]
    texts = {
        "prompt": {c.case_id: c.public_prompt for c in cases},
        "prompt_and_resources": {
            c.case_id: c.public_prompt + " " + " ".join(c.observable_resources) for c in cases
        },
        "resource_stems": {
            c.case_id: " ".join(r.split(" — ")[0] for r in c.observable_resources) for c in cases
        },
    }[surface]
    labels = {c.case_id: c.task_family not in CONTROLS for c in cases}
    report = find_lexical_separators(texts, labels)
    assert report.separators == (), [
        (s.token, round(s.accuracy, 3)) for s in report.separators
    ]
    assert report.tokens_examined > 500


def closure_components(case: HiddenShiftCase) -> list[set[str]]:
    """Group the closures a case names into chains, by the parent edges in the prose.

    A closure line names its parent as `derived from closure:<slug>`; a line with
    no such reference is a chain head.
    """

    parent: dict[str, str | None] = {}
    for line in case.observable_resources:
        head = re.match(r"(closure:[a-z0-9-]+) —", line)
        if not head:
            continue
        refs = re.findall(r"derived from (closure:[a-z0-9-]+)", line[head.end() :])
        parent[head.group(1)] = refs[0] if refs else None

    def root(node: str) -> str:
        while parent.get(node):
            node = parent[node]  # type: ignore[assignment]
        return node

    grouped: dict[str, set[str]] = {}
    for node in parent:
        grouped.setdefault(root(node), set()).add(node)
    return list(grouped.values())


@pytest.mark.parametrize("split", list(Split))
def test_the_gold_reopen_set_is_exactly_one_closure_chain(suites, split) -> None:
    """Dependency-directed reopening must be able to recover gold exactly.

    The survivors are disconnected from the reopened chain, so a system that
    finds the closure resting on the reframed formulation and expands parent
    edges transitively reaches the gold set and nothing else. If a survivor ever
    joined the gold chain, the paper's own rule would stop being the winning rule.
    """

    for case in suites[split]:
        if case.task_family in CONTROLS:
            continue
        gold = set(case.protected_gold.dependencies_to_reopen)
        touching = [comp for comp in closure_components(case) if comp & gold]
        assert len(touching) == 1, case.case_id
        assert touching[0] == gold, (case.case_id, touching[0] - gold)


# The floor a reopen result has to clear. Reported as measured, with tolerance:
# these are properties of the frozen suite, so they move only if the suite moves.
BLIND_LARGEST_COMPONENT_F1 = {Split.PILOT: 0.792, Split.TEST: 0.823}


@pytest.mark.parametrize("split", list(Split))
def test_the_mechanism_free_reopen_floor_is_the_blind_largest_component(
    suites, split
) -> None:
    """Beating full reset is NOT by itself evidence of dependency-directed reasoning.

    A responder that never reads the prompt, performs no attribution, and simply
    reopens the largest closure chain — breaking ties at random — already scores
    far above full reset, because the gold chain runs 1-3 links while a survivor
    chain is a single closure. That is the null a reopen result must clear, and
    it is pinned here rather than left in prose because a number that lives only
    in a message is a number nobody scoring P1-4 will ever see.

    The suite is not re-frozen to erase this. Dependency-directed still separates
    at 1.000 with a wide margin, and no finite constructed suite has zero
    structural regularity; publishing the floor is the defence, not chasing it.
    If a future edit re-inflates the signal, this fails loudly.
    """

    cases = [c for c in suites[split] if c.task_family not in CONTROLS]
    scores = []
    for case in cases:
        gold = case.protected_gold.dependencies_to_reopen
        components = closure_components(case)
        widest = max(len(comp) for comp in components)
        tied = [comp for comp in components if len(comp) == widest]
        # expected F1 under uniform random tie-breaking
        scores.append(sum(reopen_f1(comp, gold) for comp in tied) / len(tied))
    blind = sum(scores) / len(scores)

    full_reset = sum(
        reopen_f1(named_closures(c), c.protected_gold.dependencies_to_reopen) for c in cases
    ) / len(cases)

    assert blind == pytest.approx(BLIND_LARGEST_COMPONENT_F1[split], abs=0.02)
    assert full_reset < blind, (full_reset, blind)
    assert blind < 1.0


@pytest.mark.parametrize("split", list(Split))
def test_a_control_punishes_reopening_anything_at_all(suites, split) -> None:
    """Controls carry closures too, and the correct reopen set is still empty.

    They are listed so that the presence of a `closure:` line, the resource count
    and the resource bulk carry no information about the family. A system that
    reopens on merely seeing one is wrong here, which is what H2 should punish.
    """

    carriers = 0
    for case in suites[split]:
        if case.task_family not in CONTROLS:
            continue
        assert case.protected_gold.dependencies_to_reopen == ()
        carriers += bool(named_closures(case))
    assert carriers == PER_FAMILY[split] * 2


@pytest.mark.parametrize("split", list(Split))
def test_closure_lines_are_unique_within_a_case(suites, split) -> None:
    for case in suites[split]:
        listed = [
            resource.split(" ", 1)[0]
            for resource in case.observable_resources
            if resource.startswith("closure:")
        ]
        assert len(listed) == len(set(listed)), case.case_id


@pytest.mark.parametrize("split", list(Split))
def test_every_case_carries_resources_and_a_rubric(suites, split) -> None:
    """`case_from_dict` reads `observable_resources` with `.get`.

    A file missing the key would load to an empty tuple and pass every other
    test here, since the reopen check iterates a control's empty dependency list
    and the rubric is otherwise only asserted on the hidden-shift half.
    """

    for case in suites[split]:
        assert case.observable_resources, case.case_id
        assert case.protected_gold.root_success_rubric.strip(), case.case_id
        assert case.protected_gold.responsibility_family.strip(), case.case_id


@pytest.mark.parametrize("split", list(Split))
def test_every_case_declares_constructed_provenance(suites, split) -> None:
    """These are authored benchmark cases, not empirical findings, and say so."""

    for case in suites[split]:
        assert "CONSTRUCTED_FOR_ORION_P1" in case.source_provenance, case.case_id


# --------------------------------------------------------------------------- #
# the gold vocabulary never reaches the public view
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("split", list(Split))
def test_no_case_states_its_own_gold_vocabulary(suites, split) -> None:
    """Checked over the loaded suite, every case, not a spot check.

    The public view is `case_id`, `public_prompt` and `observable_resources`. The
    gold cause must be inferable from the phenomena described there; naming it is
    handing over the answer. `__post_init__` already refuses an id that names its
    own family, which is the narrower half of this.
    """

    offenders: list[tuple[str, list[str]]] = []
    for case in suites[split]:
        banned = gold_vocabulary(case)
        public = " ".join((case.case_id, case.public_prompt, *case.observable_resources))
        leaked = sorted(banned & tokens(public))
        if leaked:
            offenders.append((case.case_id, leaked))
    assert offenders == []


def test_the_gold_vocabulary_check_detects_a_planted_leak(suites) -> None:
    """Assert the alarm fires, or the clean run above proves nothing.

    A checker only ever seen passing has not been shown to work. This plants the
    exact failure the suite is built to avoid and requires it to be caught.
    """

    case = next(c for c in suites[Split.TEST] if c.task_family not in CONTROLS)
    banned = gold_vocabulary(case)
    assert banned, case.case_id

    word = sorted(banned)[0]
    leaked = replace(case, public_prompt=f"{case.public_prompt} Consider {word}.")
    assert word in tokens(leaked.public_prompt) & gold_vocabulary(leaked)

    in_resource = replace(case, observable_resources=(*case.observable_resources, f"n.md {word}"))
    public = " ".join((in_resource.case_id, in_resource.public_prompt, *in_resource.observable_resources))
    assert word in tokens(public) & gold_vocabulary(in_resource)


# --------------------------------------------------------------------------- #
# fingerprint stability
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("split", list(Split))
def test_suite_fingerprint_is_stable_across_two_loads(suites, split) -> None:
    """`dataset_revisions` is unbound until a fingerprint is written into it.

    A fingerprint that moved between loads could not bind anything.
    """

    first = suite_fingerprint(load_cases(CASES_ROOT, split=split))
    second = suite_fingerprint(load_cases(CASES_ROOT, split=split))
    assert first == second == suite_fingerprint(suites[split])
    assert len(first) == 64


@pytest.mark.parametrize("split", list(Split))
def test_suite_fingerprint_changes_when_a_gold_label_changes(suites, split) -> None:
    """The fingerprint binds the gold, not merely the public text.

    `root_success_rubric` is deliberately not probed here: `suite_fingerprint`
    does not hash it, so mutating it would assert nothing about the binding.
    """

    cases = suites[split]
    baseline = suite_fingerprint(cases)
    case = next(c for c in cases if c.task_family not in CONTROLS)

    other_responsibility = replace(
        case,
        protected_gold=replace(case.protected_gold, responsibility_family="ROUTING"),
    )
    deeper = replace(
        case,
        protected_gold=replace(
            case.protected_gold, dependency_depth=case.protected_gold.dependency_depth + 1
        ),
    )
    retargeted = replace(
        case,
        protected_gold=replace(
            case.protected_gold,
            target_coordinates=(case.protected_gold.target_coordinates[0], "parent_domain:other"),
        ),
    )
    rest = tuple(c for c in cases if c.case_id != case.case_id)
    for mutated in (other_responsibility, deeper, retargeted):
        assert suite_fingerprint((*rest, mutated)) != baseline


# --------------------------------------------------------------------------- #
# the degeneracy probe over the whole panel
# --------------------------------------------------------------------------- #


def _records(cases: tuple[HiddenShiftCase, ...]) -> list[LabeledRecord]:
    return [
        LabeledRecord(
            record_id=case.case_id,
            features={
                "case_id": case.case_id,
                "prompt_len": len(case.public_prompt),
                "n_resources": len(case.observable_resources),
            },
            label=case.task_family.value,
        )
        for case in cases
    ]


def _id_only_responders(cases: tuple[HiddenShiftCase, ...]) -> dict:
    """Responders that read the case id and nothing else.

    These are the real leak vectors for an opaque sequential id: families
    assigned in blocks, in a repeating cycle, or keyed off the numeric suffix.
    A hash-based guesser is deliberately not used — on six balanced classes it
    clears the probe's margin by luck often enough to make the assertion a
    coin toss rather than a check.
    """

    position = {cid: i for i, cid in enumerate(sorted(c.case_id for c in cases))}
    block = max(len(cases) // len(FAMILY_ORDER), 1)

    def suffix(case_id: str) -> int:
        return int(re.search(r"(\d+)$", case_id).group(1))

    return {
        "constant_first_family": lambda r: FAMILY_ORDER[0],
        "id_sorted_position_block": lambda r: FAMILY_ORDER[
            min(position[r.features["case_id"]] // block, len(FAMILY_ORDER) - 1)
        ],
        "id_sorted_position_cycle": lambda r: FAMILY_ORDER[
            position[r.features["case_id"]] % len(FAMILY_ORDER)
        ],
        "id_numeric_suffix_mod": lambda r: FAMILY_ORDER[
            suffix(r.features["case_id"]) % len(FAMILY_ORDER)
        ],
        "id_numeric_suffix_parity": lambda r: FAMILY_ORDER[suffix(r.features["case_id"]) % 2],
    }


@pytest.mark.parametrize("split", list(Split))
def test_the_degeneracy_probe_returns_clean_over_the_suite(suites, split) -> None:
    """If this stops being CLEAN the suite leaks; fix the suite, never the probe."""

    cases = suites[split]
    report = probe_records(
        _records(cases),
        surface=f"orion-p1-hidden-shift-{split.value.lower()}",
        blind_responders=_id_only_responders(cases),
    )
    assert report.status is DegeneracyStatus.CLEAN, [f.detail for f in report.findings]
    assert report.permits_score_as_evidence
    assert report.records_probed == len(cases)


@pytest.mark.parametrize("split", list(Split))
def test_a_blind_responder_reading_the_id_cannot_beat_the_majority_baseline(
    suites, split
) -> None:
    """Stated directly rather than left implicit in the probe's margin."""

    cases = suites[split]
    labels = [case.task_family.value for case in cases]
    baseline = Counter(labels).most_common(1)[0][1] / len(labels)
    records = _records(cases)
    for name, responder in _id_only_responders(cases).items():
        hits = sum(responder(record) == label for record, label in zip(records, labels))
        assert hits / len(records) <= baseline, (split, name, hits, baseline)


def test_the_probe_catches_a_public_field_that_determines_the_family(suites) -> None:
    """The no-alarm result above is only meaningful if the alarm can fire.

    This is the concrete proposal the suite refuses: one extra public resource
    naming the phenomenon, one token per responsibility. It leaks whether or not
    the phenomenon-to-responsibility table is stored inside the case.
    """

    cases = suites[Split.TEST]
    signal = {
        "SEARCH": "signal:response-explodes-near-limit",
        "REPRESENTATION": "signal:two-forms-disagree",
        "DECOMPOSITION": "signal:parts-pass-whole-fails",
        "INTERFACE": "signal:accepted-then-lost",
        "MEASUREMENT": "signal:summary-hides-shape",
        "EVALUATOR": "signal:reviewers-disagree",
        "EVIDENCE": "signal:unsourced-figure",
        "EXECUTION": "signal:run-aborts",
    }
    leaky = [
        LabeledRecord(
            record_id=record.record_id,
            features={**record.features, "signal": signal[case.protected_gold.responsibility_family]},
            label=record.label,
        )
        for record, case in zip(_records(cases), cases)
    ]
    lookup = {rec.features["signal"]: rec.label for rec in leaky}
    report = probe_records(
        leaky, blind_responders={"signal_lookup": lambda r: lookup[r.features["signal"]]}
    )
    assert report.status is DegeneracyStatus.DEGENERATE
    assert not report.permits_score_as_evidence
    assert {finding.probe for finding in report.findings} == {
        "single_feature_determines_label",
        "blind_responder_ceiling",
    }
