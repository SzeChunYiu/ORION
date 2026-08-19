"""Corrective P9 S3 access-attribution helpers.

The historical D1 typed-relational arm receives explicit coordinate-wise
left/right comparison features, whereas the historical typed-serialized arm is
vectorized as a bag of exact path/value tokens.  S3 asks whether the same
serialized payload becomes sufficient once a *generic* paired-coordinate
comparison operation is restored.

This module deliberately accepts only the serialized token sequence.  It does
not import or inspect D1Instance semantic objects, evaluator labels, mutation
metadata, domain/split identities, or the historical typed-relational feature
extractor.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .d1 import COMPARISON_COORDINATES, D1Label


_LEFT_PREFIX = "root.left."
_RIGHT_PREFIX = "root.right."
_UNKNOWN_SUFFIX = "unknown_coordinates[]"
_SCHEMA_TOKEN = "root.schema=P9.D1Typed.v1"


def _token_path(token: str) -> str:
    if not token:
        raise ValueError("empty serialized token")
    if ":LEN=" in token:
        path, _ = token.split(":LEN=", 1)
        return path
    if "=" in token:
        path, _ = token.split("=", 1)
        return path
    raise ValueError(f"unsupported serialized token: {token!r}")


def _coordinate_for_path(path: str, *, side_prefix: str) -> str | None:
    if not path.startswith(side_prefix):
        return None
    remainder = path[len(side_prefix) :]
    for coordinate in COMPARISON_COORDINATES:
        if remainder == coordinate:
            return coordinate
        if remainder.startswith(f"{coordinate}["):
            return coordinate
    return None


def _normalise_side_token(token: str, *, side_prefix: str) -> str:
    if not token.startswith(side_prefix):
        raise ValueError("token does not have expected side prefix")
    return "root.side." + token[len(side_prefix) :]


def _unknown_membership(sequence: Iterable[str], *, side_prefix: str) -> frozenset[str]:
    prefix = side_prefix + _UNKNOWN_SUFFIX
    values: set[str] = set()
    for token in sequence:
        if not token.startswith(prefix + "="):
            continue
        _, value = token.split("=", 1)
        if value not in COMPARISON_COORDINATES:
            raise ValueError(f"unknown-coordinate token names unsupported coordinate: {value}")
        values.add(value)
    return frozenset(values)


def serialized_generic_binding_features(sequence: list[str]) -> dict[str, object]:
    """Expose value-independent paired-coordinate comparison from D1 serialization.

    The input is exactly the token sequence emitted by
    ``D1View.TYPED_SERIALIZED``.  Semantic values remain opaque; equality is
    computed only by comparing the canonical token multisets for the same
    coordinate after stripping ``left``/``right`` from the path.
    """

    tokens = tuple(map(str, sequence))
    if not tokens:
        raise ValueError("serialized D1 sequence is required")

    left_unknown = _unknown_membership(tokens, side_prefix=_LEFT_PREFIX)
    right_unknown = _unknown_membership(tokens, side_prefix=_RIGHT_PREFIX)

    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
    for token in tokens:
        if token == _SCHEMA_TOKEN:
            continue
        path = _token_path(token)
        for side, prefix in (("left", _LEFT_PREFIX), ("right", _RIGHT_PREFIX)):
            coordinate = _coordinate_for_path(path, side_prefix=prefix)
            if coordinate is None:
                continue
            grouped[(side, coordinate)].append(
                _normalise_side_token(token, side_prefix=prefix)
            )
            break

    features: dict[str, object] = {}
    for coordinate in COMPARISON_COORDINATES:
        left_tokens = tuple(sorted(grouped.get(("left", coordinate), ())))
        right_tokens = tuple(sorted(grouped.get(("right", coordinate), ())))
        if not left_tokens or not right_tokens:
            raise ValueError(f"serialized coordinate is not recoverable on both sides: {coordinate}")
        unknown = coordinate in left_unknown or coordinate in right_unknown
        features[f"{coordinate}:unknown"] = unknown
        features[f"{coordinate}:equal"] = (not unknown) and left_tokens == right_tokens

    return features


def serialized_exact_generic_comparator(sequence: list[str]) -> str:
    """Exact D1 decision from serialized information plus generic comparison access."""

    features = serialized_generic_binding_features(sequence)
    if any(bool(features[f"{coordinate}:unknown"]) for coordinate in COMPARISON_COORDINATES):
        return D1Label.UNRESOLVED.value
    if any(not bool(features[f"{coordinate}:equal"]) for coordinate in COMPARISON_COORDINATES):
        return D1Label.OBSTRUCTION.value
    return D1Label.ALIGNED.value


__all__ = [
    "serialized_exact_generic_comparator",
    "serialized_generic_binding_features",
]
