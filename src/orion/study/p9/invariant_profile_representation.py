"""The TYPED_INVARIANT_PROFILE_BAG arm the T4 successor freeze registers.

The frozen T4 defeat moved ``TYPED_SERIALIZED_BAG`` from 0.75 to 0.50 under a
symbol-remint orbit that is information-neutral for it (the design matrices
are bitwise-equal up to one column permutation).  The one-stage attribution
is ``answer_determination_numerics``: the raw value spelling of each token
keys the feature column, so a renaming both reorders the columns and lets a
rank-deficient matrix pick a different optimum.

This representation keys each token by an isomorphism-invariant *profile*
instead: its path, its corpus document frequency, and two Weisfeiler-Leman
refinement rounds over co-occurrence.  Under any injective renaming of value
atoms every colour string is unchanged, so the feature dict is bitwise
identical -- not merely isomorphic -- between a dataset and its orbit.

What it gives up is value identity, stated in the freeze: two tokens with
the same path and the same corpus statistics share one feature.  That is the
channel the attack reminted, and the loss is charged to the protocol's
performance endpoint rather than hidden.

Nothing here reads a label or an outcome.  The corpus is train + dev of the
variant being run; no protected-split instance enters it.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from typing import Mapping, Sequence

from orion.study.p9.d1 import D1Instance

ARM = "TYPED_INVARIANT_PROFILE_BAG"

#: Frozen by P9_U_T4_SUCCESSOR_INVARIANT_PROFILE_FREEZE_2026-08-24.
REFINEMENT_ROUNDS = 2

_TOKEN_PREFIX = "token:"
_PROFILE_PREFIX = "prof:"
_UNSEEN_PREFIX = "prof:unseen:"


def _path_of(token: str) -> str:
    """The path coordinate of a serialized token; never reminted by the orbit."""

    body = token[len(_TOKEN_PREFIX):] if token.startswith(_TOKEN_PREFIX) else token
    path, _, _value = body.partition("=")
    return path


def _colour_digest(payload: str) -> str:
    return sha256(payload.encode("utf-8")).hexdigest()[:16]


def build_colouring(
    train_dicts: Sequence[Mapping[str, object]],
    dev_dicts: Sequence[Mapping[str, object]],
    rounds: int = REFINEMENT_ROUNDS,
) -> dict[str, str]:
    """Profile colour of every corpus token, label-blind.

    The corpus is the train and dev feature dicts of one dataset variant.
    Initial colour: ``sha256('<path>|df=<df>')[:16]``.  Each refinement round
    hashes the sorted multiset of co-present token colours over corpus
    instances, the token itself excluded.  The raw value string never enters
    a colour, which is what makes the colouring invariant under renaming.
    """

    corpus = list(train_dicts) + list(dev_dicts)
    document_frequency: Counter[str] = Counter()
    for row in corpus:
        for key in row:
            if key != "sequence_length":
                document_frequency[key] += 1
    colour = {
        key: _colour_digest(f"{_path_of(key)}|df={document_frequency[key]}")
        for key in document_frequency
    }
    instances = [
        {key for key in row if key != "sequence_length"} for row in corpus
    ]
    for _ in range(rounds):
        neighbourhoods: dict[str, Counter[str]] = {key: Counter() for key in colour}
        for present in instances:
            for key in present:
                target = neighbourhoods[key]
                for other in present:
                    if other != key:
                        target[colour[other]] += 1
        colour = {
            key: _colour_digest(
                f"{colour[key]}|"
                + ",".join(sorted(f"{c}x{n}" for c, n in neighbourhoods[key].items()))
            )
            for key in colour
        }
    return colour


def features_with_colouring(
    row: Mapping[str, object], colouring: Mapping[str, str]
) -> dict[str, object]:
    """The successor's feature dict for one instance under a fixed colouring."""

    built: dict[str, object] = {"sequence_length": row["sequence_length"]}
    for key in row:
        if key == "sequence_length":
            continue
        built[f"{_PROFILE_PREFIX}{colouring.get(key, _UNSEEN_PREFIX + _path_of(key))}"] = 1.0
    return built


def feature_fn_for(
    train_dicts: Sequence[Mapping[str, object]],
    dev_dicts: Sequence[Mapping[str, object]],
) -> "callable":
    """A frozen-``run_arm``-shaped feature callable built on one colouring.

    ``run_arm`` calls ``feature_fn`` once per instance across the train, dev
    and protected splits of one variant; the colouring is computed from that
    variant's train and dev dicts before the callable is handed over, so no
    protected-split instance enters the corpus.
    """

    colouring = build_colouring(train_dicts, dev_dicts)

    def features(instance: D1Instance, _row: Mapping[str, object] | None = None) -> dict[str, object]:
        # The callable's argument is the raw dataset row; the serialized bag
        # dict is rebuilt through the frozen feature function so this module
        # never re-implements serialization.
        from .hostile_representation_attacks import FEATURE_FUNCTIONS

        row = _row if _row is not None else FEATURE_FUNCTIONS["TYPED_SERIALIZED_BAG"](instance)
        return features_with_colouring(row, colouring)

    return features
