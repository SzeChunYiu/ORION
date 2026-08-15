from __future__ import annotations

from dataclasses import replace

from orion.mechanics.answers import _STRING_FIELDS_BY_DIMENSION
from orion.mechanics.model import (
    HandoffField,
    MechanicCell,
    MechanicDimension,
    MetricDirection,
    MetricKind,
    MetricSpec,
)
from orion.mechanics.questioning import _PROMPTS

JUNK_TOKEN = "xxxxx"

_BATTERY_IDS = ("battery.empty", "battery.junk", "battery.envelope")


def writable_fields(dimension: MechanicDimension) -> tuple[str, ...]:
    """The cell fields an answer for this dimension is allowed to write."""

    return _STRING_FIELDS_BY_DIMENSION.get(dimension, ())


def _cell(mechanic_id: str, **fields: tuple[str, ...]) -> MechanicCell:
    base = MechanicCell(
        mechanic_id=mechanic_id,
        purpose="host-constructed adversarial negative",
        scope="check admissibility",
    )
    return replace(base, **fields) if fields else base


def host_battery(dimension: MechanicDimension) -> tuple[MechanicCell, ...]:
    """Negatives the host supplies, which the check's author does not choose.

    A check that only has to reject a negative of its own choosing proves
    nothing: the author can pick the empty cell, leaving `lambda c: bool(field)`
    admissible — which is precisely `questioning._satisfied`, the defect the
    whole authority ladder exists to close. The battery removes that freedom.

    Three members, each retiring one known attack:

    - `empty`     nothing written, so a check must demand *something*;
    - `junk`      every writable field carries a nonsense token, so a check
                  cannot be satisfied by mere non-emptiness;
    - `envelope`  every writable field carries the dimension's own audit
                  question restated as prose, so a check cannot be satisfied by
                  echoing the question back — the envelope-laundering failure
                  this loop pre-registered against.

    A check must reject all three. Admissibility therefore *entails* that the
    predicate is not any `bool(field)` for a field this dimension writes,
    because the junk member has every one of those fields non-empty.
    """

    fields = writable_fields(dimension)
    if fields:
        junk = {name: (JUNK_TOKEN,) for name in fields}
        envelope = {name: (_PROMPTS[dimension],) for name in fields}
    else:
        # HANDOFF and METRICS carry structured payloads rather than strings, so
        # a string-only battery would leave them at order 1 and readmit
        # `bool(cell.handoff_fields)` for exactly those two dimensions.
        junk = _structured_payload(dimension, JUNK_TOKEN)
        envelope = _structured_payload(dimension, _PROMPTS[dimension])
        if not junk:
            return (_cell(_BATTERY_IDS[0]),)
    return (
        _cell(_BATTERY_IDS[0]),
        _cell(_BATTERY_IDS[1], **junk),
        _cell(_BATTERY_IDS[2], **envelope),
    )


def _structured_payload(dimension: MechanicDimension, text: str) -> dict[str, tuple]:
    """Battery content for dimensions whose answers are typed objects."""

    if dimension is MechanicDimension.HANDOFF:
        return {
            "handoff_fields": (
                HandoffField(field_id=text, description=text, schema_ref=text),
            )
        }
    if dimension is MechanicDimension.METRICS:
        return {
            "metrics": (
                MetricSpec(
                    metric_id=text,
                    description=text,
                    kind=MetricKind.QUALITY,
                    direction=MetricDirection.OBSERVE_ONLY,
                    unit=text,
                ),
            )
        }
    return {}


def battery_order(dimension: MechanicDimension) -> int:
    """The host floor on a check's discrimination order for this dimension."""

    return len(host_battery(dimension))
