"""Hidden scientific-intent benchmark scaffold. Unbound tasks remain CANNOT_CHECK."""
from __future__ import annotations

from dataclasses import dataclass

from .protocol import load_protocol


@dataclass(frozen=True)
class HiddenIntentFamily:
    family_id: str
    domain: str
    misspecification_class: str
    operational_objective: str
    intent_hidden: bool
    tasks_bound: bool


@dataclass(frozen=True)
class ProtectedIntentScore:
    status: str
    value: float | None


@dataclass(frozen=True)
class HiddenIntentBenchmark:
    families: tuple[HiddenIntentFamily, ...]
    status: str
    task_bindings: str

    def family(self, family_id: str) -> HiddenIntentFamily:
        for item in self.families:
            if item.family_id == family_id:
                return item
        raise KeyError(family_id)

    def candidate_view(self, family_id: str) -> dict[str, object]:
        family = self.family(family_id)
        return {
            "family_id": family.family_id,
            "domain": family.domain,
            "misspecification_class": family.misspecification_class,
            "operational_objective": family.operational_objective,
            "tasks_bound": family.tasks_bound,
        }

    def protected_intent_score(self, family_id: str) -> ProtectedIntentScore:
        self.family(family_id)
        return ProtectedIntentScore(status="CANNOT_CHECK", value=None)


def load_hidden_intent_benchmark() -> HiddenIntentBenchmark:
    protocol = load_protocol()
    benchmark = protocol["benchmark"]
    families = tuple(
        HiddenIntentFamily(
            family_id=item["family_id"],
            domain=item["domain"],
            misspecification_class=item["misspecification_class"],
            operational_objective=item["operational_objective"],
            intent_hidden=bool(item["intent_hidden"]),
            tasks_bound=bool(item["tasks_bound"]),
        )
        for item in benchmark["families"]
    )
    return HiddenIntentBenchmark(
        families=families,
        status=str(benchmark["status"]),
        task_bindings=str(benchmark["task_bindings"]),
    )
