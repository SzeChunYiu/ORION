from __future__ import annotations
from collections import defaultdict
from dataclasses import replace
from .types import MechanicSpec, MacroSpec


def _dedupe_provenance(items):
    seen=set(); merged=[]
    for p in items:
        key=(p.donor,p.source_id,p.revision,p.step)
        if key not in seen:
            seen.add(key); merged.append(p)
    return tuple(merged)


class MechanicLibrary:
    """Provenance-preserving mechanic registry.

    Canonicalization is fail-closed: a shared mechanic ID does not authorize
    ORION to erase different families, compatibility keys, costs, or
    prerequisites.  Donor-specific protected traits are unioned and retained.
    """
    def __init__(self) -> None:
        self._mechanics: dict[str, MechanicSpec] = {}
        self._aliases: dict[str, str] = {}
        self._macros: dict[str, MacroSpec] = {}

    def register(self, spec: MechanicSpec) -> None:
        if spec.cost < 0:
            raise ValueError("mechanic cost must be non-negative")
        if spec.mechanic_id not in self._mechanics:
            self._mechanics[spec.mechanic_id] = spec
            return

        old=self._mechanics[spec.mechanic_id]
        if old.family != spec.family:
            raise ValueError(f"family collision for {spec.mechanic_id}: {old.family} vs {spec.family}")
        if old.compatibility_key and spec.compatibility_key and old.compatibility_key != spec.compatibility_key:
            raise ValueError(f"semantic collision for {spec.mechanic_id}")
        if abs(old.cost-spec.cost) > 1e-12:
            raise ValueError(f"cost collision for {spec.mechanic_id}: {old.cost} vs {spec.cost}")
        if tuple(old.prerequisites) != tuple(spec.prerequisites):
            raise ValueError(f"prerequisite collision for {spec.mechanic_id}")

        prov=_dedupe_provenance(old.provenance+spec.provenance)
        traits=tuple(sorted(set(old.protected_traits)|set(spec.protected_traits)))
        compat=old.compatibility_key or spec.compatibility_key
        self._mechanics[spec.mechanic_id]=replace(old,provenance=prov,protected_traits=traits,compatibility_key=compat)

    def alias(self, alias: str, mechanic_id: str) -> None:
        if mechanic_id not in self._mechanics:
            raise KeyError(mechanic_id)
        self._aliases[alias] = mechanic_id

    def resolve(self, mechanic_id: str) -> MechanicSpec:
        mechanic_id = self._aliases.get(mechanic_id, mechanic_id)
        return self._mechanics[mechanic_id]

    def register_macro(self, macro: MacroSpec) -> None:
        old=self._macros.get(macro.macro_id)
        if old and old.sequence != macro.sequence:
            raise ValueError(f"macro collision for {macro.macro_id}")
        self._macros[macro.macro_id] = macro

    @property
    def mechanics(self) -> tuple[MechanicSpec, ...]:
        return tuple(self._mechanics[k] for k in sorted(self._mechanics))

    @property
    def macros(self) -> tuple[MacroSpec, ...]:
        return tuple(self._macros[k] for k in sorted(self._macros))

    def families(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = defaultdict(list)
        for m in self.mechanics:
            out[m.family].append(m.mechanic_id)
        return dict(out)
