from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MethodState:
    """M_t: current ORION method identity and protected evaluator binding."""

    method_version: str
    operator_ids: tuple[str, ...] = ()
    evaluator_id: str | None = None
    self_development_enabled: bool = False
