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


def host_battery(
    dimension: MechanicDimension, target: MechanicCell | None = None
) -> tuple[MechanicCell, ...]:
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

    When a `target` is given, every member is that cell with only the judged
    dimension's fields replaced — identical identity, purpose, scope and every
    unrelated field. A predicate can then be separated from the members only
    by the judged content: keying on the mechanic id, the fixture prose, or an
    unrelated field's content leaves at least one member accepted and the
    check inadmissible. Without a target (order computation, standalone
    audits), the bare probe members are returned as before.
    """

    fields = writable_fields(dimension)
    if fields:
        empty = {name: () for name in fields}
        junk = {name: (JUNK_TOKEN,) for name in fields}
        envelope = {name: (_PROMPTS[dimension],) for name in fields}
    else:
        # HANDOFF and METRICS carry structured payloads rather than strings, so
        # a string-only battery would leave them at order 1 and readmit
        # `bool(cell.handoff_fields)` for exactly those two dimensions.
        junk = _structured_payload(dimension, JUNK_TOKEN)
        envelope = _structured_payload(dimension, _PROMPTS[dimension])
        empty = {name: () for name in junk}
        if not junk:
            return (_member(target, 0, {}),)
    return (
        _member(target, 0, empty),
        _member(target, 1, junk),
        _member(target, 2, envelope),
    )


def _member(
    target: MechanicCell | None, index: int, overrides: dict[str, tuple]
) -> MechanicCell:
    if target is None:
        return _cell(_BATTERY_IDS[index], **overrides)
    return replace(target, **overrides) if overrides else target


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
