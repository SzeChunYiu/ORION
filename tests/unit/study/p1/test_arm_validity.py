from __future__ import annotations

from orion.study.p1.arm_validity import (
    ArmVerdict,
    assess_arm_discrimination,
    assess_pair_discrimination,
)


def test_identical_systems_did_not_discriminate() -> None:
    """The observed case, reduced. On the frozen P1 pilot every mechanical
    system scored 5/90 and ORION reframed 0/90; H1 came back NOT_SUPPORTED with
    an interval of exactly [0.0000, 0.0000]. A paired bootstrap over identical
    vectors is zero by construction, so the statistics could not tell that null
    apart from a real one."""

    outcomes = {name: [1, 0, 0, 1, 0] for name in ("orion", "arex", "scion", "iris")}
    report = assess_arm_discrimination(outcomes)
    assert report.verdict is ArmVerdict.DID_NOT_DISCRIMINATE
    assert not report.permits_system_comparison
    assert report.distinct_behaviour_groups == 1
    assert len(report.largest_group) == 4


def test_one_differing_system_is_enough_to_discriminate() -> None:
    outcomes = {
        "orion": [1, 1, 0],
        "arex": [1, 0, 0],
        "scion": [1, 0, 0],
    }
    report = assess_arm_discrimination(outcomes)
    assert report.verdict is ArmVerdict.DISCRIMINATED
    assert report.permits_system_comparison
    assert report.distinct_behaviour_groups == 2


def test_a_single_system_cannot_be_compared_to_anything() -> None:
    report = assess_arm_discrimination({"orion": [1, 0]})
    assert report.verdict is ArmVerdict.CANNOT_CHECK
    assert not report.permits_system_comparison


def test_an_empty_arm_is_cannot_check_not_a_null_result() -> None:
    report = assess_arm_discrimination({"orion": [], "arex": []})
    assert report.verdict is ArmVerdict.CANNOT_CHECK
    assert "no outcomes recorded" in report.reasons[0]


def test_a_pair_that_never_differs_cannot_support_a_verdict() -> None:
    """A hypothesis verdict rests on one pair, so the pair is what must be
    checked. NOT_SUPPORTED asserts the subject is not better; CANNOT_CHECK
    asserts nothing was measured. Only the second is honest here."""

    report = assess_pair_discrimination([1, 0, 1], [1, 0, 1])
    assert report.verdict is ArmVerdict.DID_NOT_DISCRIMINATE


def test_mismatched_pair_lengths_refuse_rather_than_truncate() -> None:
    report = assess_pair_discrimination([1, 0, 1], [1, 0])
    assert report.verdict is ArmVerdict.CANNOT_CHECK
    assert "different lengths" in report.reasons[0]


def test_discrimination_is_about_the_vector_not_the_aggregate() -> None:
    """Two systems can share a rate while disagreeing case by case. That is a
    real difference the arm detected, and it must not be folded away — an
    aggregate-only check would call this degenerate."""

    report = assess_arm_discrimination({"a": [1, 0, 1, 0], "b": [0, 1, 0, 1]})
    assert report.verdict is ArmVerdict.DISCRIMINATED
    assert sum([1, 0, 1, 0]) == sum([0, 1, 0, 1])


def test_the_blind_reopen_floor_is_computed_from_the_suite_not_quoted() -> None:
    """A result at or below this number is graph shape, not reasoning.

    The floor is derived from the live cases rather than pasted as a literal,
    so it moves when the cases move. A quoted floor goes stale on the next
    re-freeze — which is exactly the moment it matters most.
    """

    import json
    from glob import glob

    from orion.study.p1.arm_validity import blind_largest_component_floor
    from orion.study.p1.baselines import descendants_of, public_closures
    from orion.study.p1.cases import Split, case_from_dict

    expected = {"pilot": 0.792, "test": 0.823}
    for split, target in expected.items():
        components: dict[str, list[list[str]]] = {}
        required: dict[str, tuple[str, ...]] = {}
        pattern = (
            "papers/paper-01-recursive-epistemic-reconstruction/protocol/cases/"
            f"{split}/*.json"
        )
        for path in sorted(glob(pattern)):
            case = case_from_dict(json.loads(open(path).read()), split=Split.TEST)
            if not case.protected_gold.reframe_required:
                continue
            closures = public_closures(case.public_view)
            seen: set[str] = set()
            groups: list[list[str]] = []
            for closure in closures:
                if closure.closure_id in seen:
                    continue
                component = set(descendants_of(closures, (closure.closure_id,)))
                component.add(closure.closure_id)
                if component & seen:
                    continue
                seen |= component
                groups.append(sorted(component))
            components[case.case_id] = groups
            required[case.case_id] = case.protected_gold.dependencies_to_reopen
        floor = blind_largest_component_floor(components, required)
        assert abs(floor.expected_f1 - target) < 0.02, (split, floor)


def test_tied_components_are_averaged_not_resolved_favourably() -> None:
    """A policy with no diagnosis cannot claim the best tied option. Averaging
    is what guessing actually scores; taking the max would flatter the floor and
    make a real result look worse than it is."""

    from orion.study.p1.arm_validity import blind_largest_component_floor

    floor = blind_largest_component_floor(
        {"c1": [["a", "b"], ["c", "d"]]}, {"c1": ("a", "b")}
    )
    assert abs(floor.expected_f1 - 0.5) < 1e-9


def test_a_case_with_no_closures_is_skipped_not_scored_zero() -> None:
    from orion.study.p1.arm_validity import blind_largest_component_floor

    floor = blind_largest_component_floor({"c1": [], "c2": [["a"]]}, {"c2": ("a",)})
    assert floor.n_cases == 1
    assert floor.expected_f1 == 1.0


def _surface_features(case_payload: dict) -> list[float]:
    import statistics

    prompt = case_payload["public_prompt"]
    resources = case_payload["observable_resources"]
    lengths = [len(item) for item in resources]
    return [
        float(len(prompt)),
        float(len(resources)),
        float(sum(lengths)),
        float(sum(1 for item in resources if item.startswith("closure:"))),
        statistics.mean(lengths) if lengths else 0.0,
        float(len(prompt.split())),
        float(max(lengths) if lengths else 0),
    ]


def test_no_interaction_between_surfaces_separates_the_families() -> None:
    """The gap every univariate leak check leaves open.

    Both lanes' checks look at one surface at a time. A cue that separates
    families only through the interaction of two surfaces — neither carrying the
    signal alone — passes all of them. The prompt-length leak that survived two
    audits was the same failure one dimension down: invisible to a single
    threshold because the ordering was non-monotonic.
    """

    import json
    from glob import glob

    from orion.study.p1.arm_validity import assess_joint_surface_separability

    for split in ("pilot", "test"):
        features: dict[str, list[float]] = {}
        labels: dict[str, str] = {}
        pattern = (
            "papers/paper-01-recursive-epistemic-reconstruction/protocol/cases/"
            f"{split}/*.json"
        )
        for path in sorted(glob(pattern)):
            payload = json.loads(open(path).read())
            features[payload["case_id"]] = _surface_features(payload)
            labels[payload["case_id"]] = payload["task_family"]
        report = assess_joint_surface_separability(features, labels, resamples=200)
        assert not report.leaks, (split, report)


def test_the_joint_separability_check_detects_a_planted_interaction() -> None:
    """Prove the alarm fires. A checker that has never alarmed on real data is
    an untested checker, and this suite has now had two leaks pass a check that
    was simply too weak to see them.

    The planted signal is deliberately invisible to either surface alone: both
    features are uniform across families in isolation, and only their product
    carries the label.
    """

    from orion.study.p1.arm_validity import assess_joint_surface_separability

    features: dict[str, list[float]] = {}
    labels: dict[str, str] = {}
    for index in range(40):
        family = "A" if index % 2 == 0 else "B"
        sign = 1.0 if index % 4 < 2 else -1.0
        second = sign if family == "A" else -sign
        features[f"c{index}"] = [sign, second]
        labels[f"c{index}"] = family
    report = assess_joint_surface_separability(features, labels, resamples=200)
    assert report.leaks, report
    assert report.accuracy > report.majority_baseline
