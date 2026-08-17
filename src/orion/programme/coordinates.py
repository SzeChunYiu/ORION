"""Typed state coordinates addressed by Phase-4 dependency and reopening records.

The vocabulary is not invented here. ``orion.registry.CORE_STATE_COORDINATES``
already fixes the three roots ``K``/``W``/``M``, and
``orion.core.history.IterationRecord.formulation_flat`` already reads dotted
formulation coordinates (``QUESTION``, ``FRAME``, ``W.REPRESENTATIONS``,
``METHOD``, ``EVALUATOR``). Phase-4 records address exactly those, so a reopen
event and an iteration record can be joined without a translation table.

``orion.registry`` is imported read-only. Adding a Phase-4 schema id to
``MECHANICS_SUBSTRATE_IDS`` is a shared-registry edit and is deliberately left
to the lane that owns that wave.
"""

from __future__ import annotations

from orion.registry import CORE_STATE_COORDINATES

FORMULATION_COORDINATES = ("QUESTION", "FRAME", "METHOD", "EVALUATOR")

ROOT_COORDINATES = tuple(dict.fromkeys((*CORE_STATE_COORDINATES, *FORMULATION_COORDINATES)))


def coordinate_root(coordinate: str) -> str:
    """Return the leading segment of a dotted coordinate."""

    return coordinate.split(".", 1)[0]


def is_valid_coordinate(coordinate: object) -> bool:
    """True when a coordinate is dotted, non-blank in every segment, and rooted."""

    if not isinstance(coordinate, str) or not coordinate.strip():
        return False
    segments = coordinate.split(".")
    if any(not segment.strip() for segment in segments):
        return False
    return segments[0] in ROOT_COORDINATES


def coordinate_errors(coordinates: object, label: str) -> tuple[str, ...]:
    """Errors for a tuple of coordinates. An empty tuple of coordinates is an error.

    A dependency record that names no coordinate cannot be invalidated by
    anything, which makes it indistinguishable from an unversioned assertion.
    """

    if not isinstance(coordinates, tuple) or not coordinates:
        return (f"{label} must be a non-empty tuple of coordinates",)
    errors = [
        f"{label}[{index}] is not a valid rooted coordinate: {value!r}"
        for index, value in enumerate(coordinates)
        if not is_valid_coordinate(value)
    ]
    return tuple(errors)


def covers(watched: str, changed: str) -> bool:
    """True when a change at ``changed`` falls inside the subtree ``watched``."""

    return changed == watched or changed.startswith(watched + ".")


__all__ = [
    "FORMULATION_COORDINATES",
    "ROOT_COORDINATES",
    "coordinate_errors",
    "coordinate_root",
    "covers",
    "is_valid_coordinate",
]
