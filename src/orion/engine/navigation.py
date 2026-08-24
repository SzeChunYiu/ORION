from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

from orion.core.problem import Problem
from orion.donors import DonorRegistry, normal_orion_donor_registry, orion_q_donor_registry
from orion.mechanics.model import MechanicCell
from orion.mechanics.questioning import generate_mechanic_questions
from orion.mechanics.workflow import ORION_WORKFLOW_ROOT_ID
from .capability_router import CapabilityRouter

_WORD = re.compile(r"[A-Za-z0-9_]+")
_CORE_IDS = (
    ORION_WORKFLOW_ROOT_ID,
    "FRAME.v1",
    "SEARCH.v1",
    "ABSORB.v1",
    "RECONSTRUCT.v1",
    "DETECT.v1",
    "DIAGNOSE.v1",
    "REFRAME.v1",
    "REOPEN.v1",
    "SATURATE_BOUNDED.v3",
)


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _tokens(text: str) -> set[str]:
    return {item.lower() for item in _WORD.findall(text) if len(item) > 2}


def _cell_payload(cell: MechanicCell) -> dict[str, object]:
    return {
        "mechanic_id": cell.mechanic_id,
        "purpose": cell.purpose,
        "scope": cell.scope,
        "dependencies": list(cell.dependency_ids),
        "external_dependencies": list(cell.external_dependency_contract_ids),
        "children": list(cell.child_mechanic_ids),
        "reopen_triggers": list(cell.reopen_triggers),
        "search_coverage_obligations": list(cell.search_coverage_obligations),
        "parent_domain_hypotheses": list(cell.parent_domain_hypotheses),
        "saturation_criteria": list(cell.saturation_criteria),
        "empirical_open_coordinates": list(cell.empirical_open_coordinates),
        "provisional_dimensions": [item.value for item in cell.provisional_dimensions],
    }


@dataclass(frozen=True)
class ProblemAtom:
    mechanic_id: str
    parent_mechanic_ids: tuple[str, ...]
    child_mechanic_ids: tuple[str, ...]
    dependency_ids: tuple[str, ...]
    relevance_score: int
    cell_digest: str

    def as_dict(self) -> dict[str, object]:
        return {
            "mechanic_id": self.mechanic_id,
            "parent_mechanic_ids": list(self.parent_mechanic_ids),
            "child_mechanic_ids": list(self.child_mechanic_ids),
            "dependency_ids": list(self.dependency_ids),
            "relevance_score": self.relevance_score,
            "cell_digest": self.cell_digest,
        }


@dataclass(frozen=True)
class FibreNavigation:
    mechanic_id: str
    execution_modality: str
    llm_authority: str
    fallback: str
    executable_donor_ids: tuple[str, ...]
    deferred_donor_ids: tuple[str, ...]
    regression_donor_ids: tuple[str, ...]
    open_question_ids: tuple[str, ...]
    empirical_open_coordinates: tuple[str, ...]
    route_digest: str

    def as_dict(self) -> dict[str, object]:
        return {
            "mechanic_id": self.mechanic_id,
            "execution_modality": self.execution_modality,
            "llm_authority": self.llm_authority,
            "fallback": self.fallback,
            "executable_donor_ids": list(self.executable_donor_ids),
            "deferred_donor_ids": list(self.deferred_donor_ids),
            "regression_donor_ids": list(self.regression_donor_ids),
            "open_question_ids": list(self.open_question_ids),
            "empirical_open_coordinates": list(self.empirical_open_coordinates),
            "route_digest": self.route_digest,
        }


@dataclass(frozen=True)
class ProblemNavigationPlan:
    problem_id: str
    profile: str
    root_mechanic_id: str
    donor_registry_id: str
    donor_registry_digest: str
    atomization_digest: str
    atoms: tuple[ProblemAtom, ...]
    active_fibre_ids: tuple[str, ...]
    fibre_routes: tuple[FibreNavigation, ...]
    deferred_donor_obligation_ids: tuple[str, ...]
    plan_digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "schema": "ORION.ProblemNavigationPlan.v1",
            "problem_id": self.problem_id,
            "profile": self.profile,
            "root_mechanic_id": self.root_mechanic_id,
            "donor_registry_id": self.donor_registry_id,
            "donor_registry_digest": self.donor_registry_digest,
            "atomization_digest": self.atomization_digest,
            "atoms": [item.as_dict() for item in self.atoms],
            "active_fibre_ids": list(self.active_fibre_ids),
            "fibre_routes": [item.as_dict() for item in self.fibre_routes],
            "deferred_donor_obligation_ids": list(self.deferred_donor_obligation_ids),
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_adoption_authority": False,
            "grants_promotion_authority": False,
            "grants_merge_authority": False,
            "grants_global_task_stop_authority": False,
        }

    def as_dict(self) -> dict[str, object]:
        return {**self.unsigned(), "plan_digest": self.plan_digest}

    def validate(self) -> None:
        if self.plan_digest != _digest(self.unsigned()):
            raise ValueError("navigation plan digest mismatch")
        atom_ids = tuple(item.mechanic_id for item in self.atoms)
        if len(atom_ids) != len(set(atom_ids)):
            raise ValueError("duplicate problem atom")
        if self.root_mechanic_id not in atom_ids:
            raise ValueError("root mechanic missing from atomization")
        if any(item not in atom_ids for item in self.active_fibre_ids):
            raise ValueError("active fibre missing from atomization")
        route_ids = tuple(item.mechanic_id for item in self.fibre_routes)
        if route_ids != self.active_fibre_ids:
            raise ValueError("fibre routes must exactly bind active fibres")


class PaperParityNavigator:
    """Mechanical atomization/fibre/capability/donor planner used by every root solve.

    The complete registered mechanic graph is retained in `atoms`; the active fibre set
    is a deterministic target-conditioned working view. No atom or deferred donor is
    deleted merely because it is not selected for the first working view.
    """

    def __init__(
        self,
        *,
        cells: tuple[MechanicCell, ...] | None = None,
        donors: DonorRegistry | None = None,
        profile: str = "orion",
        max_active_fibres: int = 24,
    ) -> None:
        if max_active_fibres < len(_CORE_IDS):
            raise ValueError("max_active_fibres must retain all core workflow fibres")
        if profile not in {"orion", "orion-q"}:
            raise ValueError("unknown ORION navigation profile")
        if not cells:
            from orion.self_orion.completion_program import completion_program_cells

            cells = tuple(completion_program_cells())
        self._cells = cells
        self._donors = donors or (
            orion_q_donor_registry() if profile == "orion-q" else normal_orion_donor_registry()
        )
        self._profile = profile
        self._max_active = max_active_fibres
        self._router = CapabilityRouter()

    @classmethod
    def normal(cls) -> "PaperParityNavigator":
        return cls(profile="orion")

    @classmethod
    def orion_q(cls) -> "PaperParityNavigator":
        return cls(profile="orion-q")

    @property
    def donor_registry(self) -> DonorRegistry:
        return self._donors

    def _relevance(self, problem: Problem, cell: MechanicCell) -> int:
        if cell.mechanic_id == ORION_WORKFLOW_ROOT_ID:
            return 10_000
        if cell.mechanic_id in _CORE_IDS:
            return 5_000 - _CORE_IDS.index(cell.mechanic_id)
        problem_tokens = _tokens(
            " ".join((problem.question, problem.scope, *problem.success_criteria, *problem.initial_domain_ids))
        )
        cell_tokens = _tokens(
            " ".join((cell.mechanic_id, cell.purpose, cell.scope, *cell.parent_domain_hypotheses))
        )
        overlap = len(problem_tokens & cell_tokens)
        score = overlap * 100
        if cell.mechanic_id.startswith("CROSS."):
            score += 20
        if cell.empirical_open_coordinates:
            score += 5
        if cell.provisional_dimensions:
            score += 3
        return score

    def plan(self, problem: Problem) -> ProblemNavigationPlan:
        cells = {cell.mechanic_id: cell for cell in self._cells}
        if ORION_WORKFLOW_ROOT_ID not in cells:
            raise ValueError("mechanics program is missing ORION root")
        parents: dict[str, list[str]] = {key: [] for key in cells}
        for parent in cells.values():
            for child in parent.child_mechanic_ids:
                if child not in cells:
                    raise ValueError(f"unknown child mechanic in navigation graph: {child}")
                parents[child].append(parent.mechanic_id)

        atoms = tuple(
            ProblemAtom(
                mechanic_id=cell.mechanic_id,
                parent_mechanic_ids=tuple(sorted(parents[cell.mechanic_id])),
                child_mechanic_ids=tuple(cell.child_mechanic_ids),
                dependency_ids=tuple(cell.dependency_ids),
                relevance_score=self._relevance(problem, cell),
                cell_digest=_digest(_cell_payload(cell)),
            )
            for cell in sorted(cells.values(), key=lambda item: item.mechanic_id)
        )
        atomization_digest = _digest([item.as_dict() for item in atoms])
        ranked = sorted(atoms, key=lambda item: (-item.relevance_score, item.mechanic_id))
        active: list[str] = list(_CORE_IDS)
        for atom in ranked:
            if atom.mechanic_id in active:
                continue
            active.append(atom.mechanic_id)
            if len(active) >= self._max_active:
                break
        active_ids = tuple(active)

        routes: list[FibreNavigation] = []
        for mechanic_id in active_ids:
            cell = cells[mechanic_id]
            route = self._router.route(mechanic_id)
            donor_rows = self._donors.for_mechanic(
                mechanic_id,
                domain_ids=problem.initial_domain_ids,
                include_deferred=True,
            )
            executable = tuple(item.capability_id for item in donor_rows if item.executable)
            deferred = tuple(
                item.capability_id
                for item in donor_rows
                if item.execution_mode.value == "DEFERRED"
            )
            regression = tuple(
                item.capability_id
                for item in donor_rows
                if item.execution_mode.value == "REGRESSION_ONLY"
            )
            open_questions = tuple(item.question_id for item in generate_mechanic_questions(cell))
            unsigned = {
                "mechanic_id": mechanic_id,
                "execution_modality": route.modality.value,
                "llm_authority": route.llm_authority,
                "fallback": route.fallback,
                "executable_donor_ids": list(executable),
                "deferred_donor_ids": list(deferred),
                "regression_donor_ids": list(regression),
                "open_question_ids": list(open_questions),
                "empirical_open_coordinates": list(cell.empirical_open_coordinates),
            }
            routes.append(
                FibreNavigation(
                    mechanic_id=mechanic_id,
                    execution_modality=route.modality.value,
                    llm_authority=route.llm_authority,
                    fallback=route.fallback,
                    executable_donor_ids=executable,
                    deferred_donor_ids=deferred,
                    regression_donor_ids=regression,
                    open_question_ids=open_questions,
                    empirical_open_coordinates=tuple(cell.empirical_open_coordinates),
                    route_digest=_digest(unsigned),
                )
            )

        deferred_obligations = tuple(
            item.capability_id for item in self._donors.deferred_reopen_obligations()
        )
        seed = ProblemNavigationPlan(
            problem_id=problem.problem_id,
            profile=self._profile,
            root_mechanic_id=ORION_WORKFLOW_ROOT_ID,
            donor_registry_id=self._donors.registry_id,
            donor_registry_digest=self._donors.digest,
            atomization_digest=atomization_digest,
            atoms=atoms,
            active_fibre_ids=active_ids,
            fibre_routes=tuple(routes),
            deferred_donor_obligation_ids=tuple(sorted(deferred_obligations)),
            plan_digest="",
        )
        plan = ProblemNavigationPlan(**{**seed.__dict__, "plan_digest": _digest(seed.unsigned())})
        plan.validate()
        return plan


__all__ = [
    "FibreNavigation",
    "PaperParityNavigator",
    "ProblemAtom",
    "ProblemNavigationPlan",
]
