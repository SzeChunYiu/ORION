from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class TaskFamily(str, Enum):
    HIDDEN_PARENT_DOMAIN = "hidden_parent_domain"
    HIDDEN_REPRESENTATION = "hidden_representation_or_coordinate_system"
    HIDDEN_DECOMPOSITION = "hidden_decomposition_or_interface"
    HIDDEN_MEASUREMENT = "hidden_measurement_or_operationalization"
    EVIDENCE_ONLY_CONTROL = "evidence_only_negative_control"
    EXECUTION_ONLY_CONTROL = "execution_only_negative_control"


class AdjudicationStatus(str, Enum):
    MECHANICAL_GOLD = "MECHANICAL_GOLD"
    DOUBLE_ANNOTATED = "DOUBLE_ANNOTATED"
    ADJUDICATED = "ADJUDICATED"
    # Labelled by the blinded model panel in `adjudication.py`, never by humans. A distinct
    # tier from ADJUDICATED (human) and MECHANICAL_GOLD (constructed): promotion out of it
    # requires a real human record, which no model panel can supply.
    MODEL_ADJUDICATED = "MODEL_ADJUDICATED"
    PILOT_ONLY = "PILOT_ONLY"


class Split(str, Enum):
    PILOT = "PILOT"
    TEST = "TEST"


@dataclass(frozen=True)
class ProtectedGold:
    """Host-owned labels. Never handed to a system under test."""

    reframe_required: bool
    responsibility_family: str
    target_coordinates: tuple[str, ...]
    dependencies_to_reopen: tuple[str, ...]
    root_success_rubric: str
    dependency_depth: int = 0


@dataclass(frozen=True)
class PublicView:
    """Exactly what a system under test may read. No gold, no family label.

    The family is withheld because four of the six families are hidden-shift
    and two are negative controls: knowing which is which is the answer to H2.
    """

    case_id: str
    public_prompt: str
    observable_resources: tuple[str, ...]
    budget_class: str


@dataclass(frozen=True)
class HiddenShiftCase:
    case_id: str
    task_family: TaskFamily
    public_prompt: str
    observable_resources: tuple[str, ...]
    protected_gold: ProtectedGold
    budget_class: str
    adjudication_status: AdjudicationStatus
    split: Split
    source_provenance: tuple[str, ...] = ()
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.case_id.strip() or not self.public_prompt.strip():
            raise ValueError("case identity and public prompt are required")
        control = self.task_family in {
            TaskFamily.EVIDENCE_ONLY_CONTROL,
            TaskFamily.EXECUTION_ONLY_CONTROL,
        }
        if control and self.protected_gold.reframe_required:
            raise ValueError(f"{self.case_id}: a negative control cannot require a reframe")
        if not control and not self.protected_gold.reframe_required:
            raise ValueError(f"{self.case_id}: a hidden-shift case must require a reframe")
        if self.protected_gold.reframe_required and not self.protected_gold.target_coordinates:
            raise ValueError(f"{self.case_id}: a required reframe needs target coordinates")
        # The case id must not leak the answer — the degeneracy probe checks the
        # panel as a whole, but an id naming its own family is refused up front.
        lowered = self.case_id.lower().replace("-", "_")
        if self.task_family.value in lowered or self.protected_gold.responsibility_family.lower() in lowered:
            raise ValueError(f"{self.case_id}: case id leaks its own label")

    @property
    def public_view(self) -> PublicView:
        return PublicView(
            case_id=self.case_id,
            public_prompt=self.public_prompt,
            observable_resources=self.observable_resources,
            budget_class=self.budget_class,
        )


def case_from_dict(payload: dict, *, split: Split) -> HiddenShiftCase:
    gold = payload["protected_gold"]
    return HiddenShiftCase(
        case_id=payload["case_id"],
        task_family=TaskFamily(payload["task_family"]),
        public_prompt=payload["public_prompt"],
        observable_resources=tuple(payload.get("observable_resources", ())),
        protected_gold=ProtectedGold(
            reframe_required=bool(gold["reframe_required"]),
            responsibility_family=gold["responsibility_family"],
            target_coordinates=tuple(gold.get("target_coordinates", ())),
            dependencies_to_reopen=tuple(gold.get("dependencies_to_reopen", ())),
            root_success_rubric=gold["root_success_rubric"],
            dependency_depth=int(gold.get("dependency_depth", 0)),
        ),
        budget_class=payload["budget_class"],
        adjudication_status=AdjudicationStatus(payload["adjudication_status"]),
        split=split,
        source_provenance=tuple(payload.get("source_provenance", ())),
        notes=payload.get("notes", ""),
    )


def load_cases(root: Path, *, split: Split) -> tuple[HiddenShiftCase, ...]:
    directory = root / split.value.lower()
    if not directory.is_dir():
        return ()
    cases = [
        case_from_dict(json.loads(path.read_text()), split=split)
        for path in sorted(directory.glob("*.json"))
    ]
    ids = [case.case_id for case in cases]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate case ids in suite")
    return tuple(cases)


def suite_fingerprint(cases: tuple[HiddenShiftCase, ...]) -> str:
    """Content hash binding the exact frozen suite, gold included.

    The protocol's `dataset_revisions` field is UNBOUND until this is written
    into it; a result reported against an unbound suite is unverifiable.
    """

    digest = hashlib.sha256()
    for case in sorted(cases, key=lambda item: item.case_id):
        digest.update(
            json.dumps(
                {
                    "case_id": case.case_id,
                    "task_family": case.task_family.value,
                    "public_prompt": case.public_prompt,
                    "observable_resources": list(case.observable_resources),
                    "gold": {
                        "reframe_required": case.protected_gold.reframe_required,
                        "responsibility_family": case.protected_gold.responsibility_family,
                        "target_coordinates": list(case.protected_gold.target_coordinates),
                        "dependencies_to_reopen": list(case.protected_gold.dependencies_to_reopen),
                        "dependency_depth": case.protected_gold.dependency_depth,
                    },
                },
                sort_keys=True,
            ).encode()
        )
    return digest.hexdigest()


__all__ = [
    "AdjudicationStatus",
    "HiddenShiftCase",
    "ProtectedGold",
    "PublicView",
    "Split",
    "TaskFamily",
    "case_from_dict",
    "load_cases",
    "suite_fingerprint",
]
