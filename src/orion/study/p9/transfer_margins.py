"""Point the comparator-response instrument at P9's shipped D1 transfer archive.

The numbers audited here are the ones the manuscript quotes. They are read from
``research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json``
and the committed ``result_digest`` is rebuilt from the committed bytes before
any claim is transcribed, for the reason ``orion.study.p7.closure_premises`` and
``orion.study.p8.authority_terminals`` do the same: an instrument that only ever
runs on its own fixture is the failure it was written to catch.

The view-collapse measurement below needs no fitted model and no scikit-learn. A
``DictVectorizer`` learns its vocabulary on train and drops every key it did not
see, so the number of *distinct in-vocabulary feature signatures* a split
presents is an upper bound on how many different answers any estimator in the
grid can give --- computable from the frozen dataset alone, before a single fit.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from orion.programme.comparator_response import (
    ComparatorResponse,
    CompositionSensitivity,
    ContrastMargin,
    measure_composition_sensitivity,
    measure_contrast_margin,
    score_comparator,
)
from orion.programme.refutation_capacity import TheoryDivergence, divergence_of
from orion.transfer.v2.canonical import content_digest

_REPO_ROOT = Path(__file__).resolve().parents[4]

D1_RESULT_PATH = (
    _REPO_ROOT
    / "research"
    / "extensions"
    / "p9-structured-neural"
    / "execution"
    / "D1_EXECUTION_RESULT_V1_2.json"
)

D1_RESULT_DIGEST = "sha256:34003fb8ffcecec6ed01654e40c644ff05b7640be56b398a45efc1e52a30141a"

D1_TREATED_ARM = "TYPED_RELATIONAL"

# The three arms the manuscript reports differences against, in the order its
# results paragraph names them.
D1_COMPARATOR_ARMS = ("TRANSCRIPT_BAG", "UNTYPED_PAIR", "TYPED_SERIALIZED_BAG")

_ARM_RESPONSE_DEFINITION: Mapping[str, str] = {
    "TRANSCRIPT_BAG": (
        "reminted surface action tokens plus three arity counts, fitted on the numerical and "
        "graph domains and scored on transactional workflows"
    ),
    "UNTYPED_PAIR": (
        "per-coordinate presence, unknown flag and length for both methods plus a dependency "
        "topology match, fitted on two domains and scored on a third"
    ),
    "TYPED_SERIALIZED_BAG": (
        "a canonical token sequence over the same typed coordinate values, fitted on two "
        "domains and scored on a third"
    ),
    "TYPED_RELATIONAL": (
        "per-coordinate equality and unknown flags over the typed method coordinates, fitted "
        "on two domains and scored on a third"
    ),
}


def load_shipped_d1_result() -> dict[str, Any]:
    """Load the archived D1 result and rebuild its published digest from its bytes."""

    data = json.loads(D1_RESULT_PATH.read_text(encoding="utf-8"))
    published = data.get("result_digest")
    if published != D1_RESULT_DIGEST:
        raise ValueError(f"unexpected D1 result digest: {published!r}")
    body = {key: value for key, value in data.items() if key != "result_digest"}
    rebuilt = content_digest(body)
    if rebuilt != D1_RESULT_DIGEST:
        raise ValueError(
            f"D1 archive does not reproduce its own digest: {rebuilt} != {D1_RESULT_DIGEST}"
        )
    return data


def _arm_rows(result: Mapping[str, Any], arm: str) -> list[Mapping[str, Any]]:
    arms = result["results"]
    if arm not in arms:
        raise KeyError(f"D1 archive carries no arm {arm!r}")
    rows = arms[arm]["test_predictions"]
    # Every arm scored the same protected cases; sorting by instance id is what
    # makes the vectors paired rather than merely equal in length.
    return sorted(rows, key=lambda row: str(row["instance_id"]))


def d1_arm_responses(result: Mapping[str, Any] | None = None) -> dict[str, ComparatorResponse]:
    """Score every archived D1 arm on what it did with the 128 protected cases."""

    data = result if result is not None else load_shipped_d1_result()
    responses: dict[str, ComparatorResponse] = {}
    for arm in (D1_TREATED_ARM, *D1_COMPARATOR_ARMS):
        rows = _arm_rows(data, arm)
        responses[arm] = score_comparator(
            arm,
            gold=[str(row["target"]) for row in rows],
            predicted=[str(row["prediction"]) for row in rows],
            response_definition=_ARM_RESPONSE_DEFINITION[arm],
        )
    return responses


def d1_contrast_margins(result: Mapping[str, Any] | None = None) -> tuple[ContrastMargin, ...]:
    """The three published D1 differences, each with its comparator's response attached."""

    data = result if result is not None else load_shipped_d1_result()
    responses = d1_arm_responses(data)
    return tuple(
        measure_contrast_margin(
            f"D1 {D1_TREATED_ARM} minus {arm}",
            treated=responses[D1_TREATED_ARM],
            comparator=responses[arm],
        )
        for arm in D1_COMPARATOR_ARMS
    )


def _protected_compositions(gold: Sequence[str]) -> tuple[tuple[int, ...], ...]:
    """Sub-multisets of the frozen protected split, declared by label mix.

    Nothing here is a new case. The D1 protocol's 1:1:1:1 mix of aligned,
    single-corruption, unresolved and double-corruption test instances is a free
    protocol choice --- no part of the transfer claim fixes it --- so these are
    the splits the same experiment could equally have been frozen against.
    """

    positions: dict[str, list[int]] = {}
    for index, label in enumerate(gold):
        positions.setdefault(label, []).append(index)
    mixes = (
        ("as-frozen", {"ALIGNED": 32, "OBSTRUCTION": 64, "UNRESOLVED": 32}),
        ("balanced", {"ALIGNED": 32, "OBSTRUCTION": 32, "UNRESOLVED": 32}),
        ("aligned-heavy", {"ALIGNED": 32, "OBSTRUCTION": 2, "UNRESOLVED": 2}),
        ("aligned-dominant", {"ALIGNED": 32, "OBSTRUCTION": 1, "UNRESOLVED": 1}),
        ("obstruction-heavy", {"ALIGNED": 2, "OBSTRUCTION": 64, "UNRESOLVED": 2}),
        ("unresolved-heavy", {"ALIGNED": 2, "OBSTRUCTION": 2, "UNRESOLVED": 32}),
    )
    built: list[tuple[int, ...]] = []
    for _name, mix in mixes:
        selection: list[int] = []
        for label, count in sorted(mix.items()):
            selection.extend(positions.get(label, ())[:count])
        built.append(tuple(selection))
    return tuple(built)


def d1_composition_sensitivity(
    result: Mapping[str, Any] | None = None,
) -> dict[str, CompositionSensitivity]:
    """Re-score the archived predictions on re-composed protected splits.

    No model is refitted, no representation is touched and no case is invented,
    so whatever moves is a property of the split.
    """

    data = result if result is not None else load_shipped_d1_result()
    treated_rows = _arm_rows(data, D1_TREATED_ARM)
    gold = [str(row["target"]) for row in treated_rows]
    treated = [str(row["prediction"]) for row in treated_rows]
    compositions = _protected_compositions(gold)
    out: dict[str, CompositionSensitivity] = {}
    for arm in D1_COMPARATOR_ARMS:
        out[arm] = measure_composition_sensitivity(
            f"D1 {D1_TREATED_ARM} minus {arm}",
            gold=gold,
            treated=treated,
            comparator=[str(row["prediction"]) for row in _arm_rows(data, arm)],
            compositions=compositions,
        )
    return out


def d1_view_collapse() -> dict[str, dict[str, int]]:
    """How many protected cases each view can still tell apart after the vocabulary is fixed.

    A feature key absent from the training split is dropped at transform time, so
    a view whose surviving keys take one value across the protected split presents
    a single row to every estimator in the grid. That arm's prediction is then a
    constant for structural reasons, before any solver, seed or library version
    is chosen.
    """

    # Local: importing d1_experiment at module scope would drag scikit-learn into
    # every caller of the archive readers above, which need none of it.
    from .d1 import generate_d1_dataset
    from .d1_experiment import D1FeatureFamily, features

    dataset = generate_d1_dataset(seed="p9-d1-method-transfer-v1")
    report: dict[str, dict[str, int]] = {}
    for family in D1FeatureFamily:
        train = [features(row, family) for row in dataset.train]
        test = [features(row, family) for row in dataset.test]
        vocabulary = set().union(*(set(row) for row in train))
        signatures = {
            tuple(sorted((key, str(row[key])) for key in set(row) & vocabulary)) for row in test
        }
        report[family.value] = {
            "train_vocabulary": len(vocabulary),
            "test_keys": len(set().union(*(set(row) for row in test))),
            "test_keys_in_train_vocabulary": len(
                set().union(*(set(row) for row in test)) & vocabulary
            ),
            "distinct_in_vocabulary_test_signatures": len(signatures),
        }
    return report


def d1_oracle_divergence() -> TheoryDivergence:
    """Ask whether D1's ``D1_EVALUATOR_FAILURE`` branch could ever be taken.

    ``run_d1`` emits that terminal when its "exact typed relational comparator"
    scores below 1.0. The comparator recomputes the evaluator's own gold rule
    over the same coordinates, so this is P6's question and P6's instrument
    answers it; it is measured here rather than re-implemented.
    """

    from .d1 import classify_methods, generate_d1_dataset
    from .d1_experiment import exact_relational_comparator

    dataset = generate_d1_dataset(seed="p9-d1-method-transfer-v1")
    return divergence_of(
        exact_relational_comparator,
        theory_id="D1 exact typed relational comparator vs D1 evaluator gold",
        reference=lambda instance: classify_methods(instance.left, instance.right).value,
        space=(*dataset.train, *dataset.dev, *dataset.test),
    )


__all__ = [
    "D1_COMPARATOR_ARMS",
    "D1_RESULT_DIGEST",
    "D1_RESULT_PATH",
    "D1_TREATED_ARM",
    "d1_arm_responses",
    "d1_composition_sensitivity",
    "d1_contrast_margins",
    "d1_oracle_divergence",
    "d1_view_collapse",
    "load_shipped_d1_result",
]
