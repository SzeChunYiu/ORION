"""Host-owned execution boundary for P1 mutation-necessity worlds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .necessity_cases import NecessityProtectedWorld, NecessityPublicWorld, ProbeResponse, RepairResponse


@dataclass(frozen=True)
class TestedRepair:
    repair_id: str
    response: RepairResponse


@dataclass(frozen=True)
class TestedProbe:
    probe_id: str
    response: ProbeResponse


class NecessityInteractor(Protocol):
    @property
    def public(self) -> NecessityPublicWorld: ...

    @property
    def remaining_budget(self) -> float: ...

    def test_repair(self, repair_id: str) -> TestedRepair | None: ...

    def run_probe(self, probe_id: str) -> TestedProbe | None: ...


class FrozenWorldSession:
    """Expose only budgeted observations, never the protected matrix itself."""

    def __init__(
        self,
        public: NecessityPublicWorld,
        protected: NecessityProtectedWorld,
        *,
        budget: float,
    ) -> None:
        self._public = public
        self._protected = protected
        self._remaining = float(budget)
        self._spent = 0.0
        self._tested_repairs: dict[str, TestedRepair] = {}
        self._tested_probes: dict[str, TestedProbe] = {}

    @property
    def public(self) -> NecessityPublicWorld:
        return self._public

    @property
    def remaining_budget(self) -> float:
        return self._remaining

    @property
    def spent_budget(self) -> float:
        return self._spent

    @property
    def tested_repair_ids(self) -> tuple[str, ...]:
        return tuple(self._tested_repairs)

    @property
    def tested_probe_ids(self) -> tuple[str, ...]:
        return tuple(self._tested_probes)

    def _spend(self, cost: float) -> bool:
        if cost < 0:
            raise ValueError("negative intervention cost")
        if cost > self._remaining + 1e-12:
            return False
        self._remaining -= cost
        self._spent += cost
        return True

    def test_repair(self, repair_id: str) -> TestedRepair | None:
        if repair_id in self._tested_repairs:
            return self._tested_repairs[repair_id]
        repair = next((item for item in self._public.repairs if item.repair_id == repair_id), None)
        if repair is None:
            raise KeyError(repair_id)
        if not self._spend(repair.declared_cost):
            return None
        tested = TestedRepair(repair_id, self._protected.repair_response(repair_id))
        self._tested_repairs[repair_id] = tested
        return tested

    def run_probe(self, probe_id: str) -> TestedProbe | None:
        if probe_id in self._tested_probes:
            return self._tested_probes[probe_id]
        probe = next((item for item in self._public.diagnostic_probes if item.probe_id == probe_id), None)
        if probe is None:
            raise KeyError(probe_id)
        if not self._spend(probe.declared_cost):
            return None
        tested = TestedProbe(probe_id, self._protected.probe_response(probe_id))
        self._tested_probes[probe_id] = tested
        return tested


__all__ = ["FrozenWorldSession", "NecessityInteractor", "TestedProbe", "TestedRepair"]
