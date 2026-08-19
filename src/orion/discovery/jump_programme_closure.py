"""Static scientific closure checks for ORION Jump programme issue #500.

The checker can establish that the *research packet* is internally complete at
the registered resolution: all #500 deliverables have owners, no generic Jump
atom is manufactured by vocabulary, the frozen child dispositions are present,
and the local #501 benchmark has the expected strong-parent-subsumption result.

It cannot establish that dependency PRs merged, that exact-head CI passed, that
#287 novelty authority approved a claim, or that #500 may be closed.  Those are
external integration/authority transitions by construction.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import content_digest
from orion.discovery.zero_error_jump_benchmark import ZeroErrorJumpTerminal


class JumpProgrammeTerminal(str, Enum):
    REGIME_INVENTION_WITHOUT_INCREMENTAL_VALUE = (
        "REGIME_INVENTION_WITHOUT_INCREMENTAL_VALUE"
    )
    CANNOT_CHECK = "CANNOT_CHECK"


_REQUIRED_DELIVERABLE_IDS = (
    "STRUCTURAL_LITERATURE_MATRIX_AND_SATURATION",
    "FORMAL_JUMP_NONJUMP_DEFINITIONS_COUNTERMODELS",
    "ZERO_ERROR_EPISTEMIC_TENSION_TRIGGER",
    "THOUGHT_EXPERIMENT_MECHANICS_HOSTILE_CONTROLS",
    "REPRESENTATION_INVENTION_OPERATOR_FAMILY",
    "EXECUTABLE_AXIOM_CORRESPONDENCE_OBJECT",
    "PROTECTED_ZERO_ERROR_BENCHMARK",
    "STRONGEST_PARENT_STRUCTURAL_RECEIPTS",
    "DISJOINT_REPLICATION_INDEPENDENT_VERIFICATION",
    "PAPER_BY_PAPER_OWNERSHIP_UPDATE_MAP",
    "EXPLICIT_NEGATIVE_TERMINAL_IF_PARENT_SUBSUMED",
)

_REQUIRED_PAPER_PROGRAMME_IDS = (
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
    "P6_SUCCESSOR",
    "P7",
    "P8",
    "P9_P10",
    "HISTORICAL_ATLASES",
)

_REQUIRED_CHILD_TERMINALS = {
    (463, "FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS"),
    (516, "MULTIPLE_FAILURE_SIGNAL_ATOMS_REQUIRED"),
    (517, "TMS_NOGOOD_PLUS_RESPONSIBILITY_SUFFICIENT"),
    (518, "P7_TRANSPORT_SUFFICIENT"),
    (510, "MULTIPLE_TENSION_ATOMS_REQUIRED"),
    (511, "MULTIPLE_IMAGINATION_ATOMS_REQUIRED"),
    (512, "MULTIPLE_CONCEPT_ATOMS_REQUIRED"),
    (507, "RECURSIVE_ATOM_STUDY_CALCULUS_FROZEN"),
    (506, "USEFUL_MORPHOLOGY_BASIS_FOUND"),
    (509, "FAILURE_ATLAS_SCHEMA_STABLE"),
    (508, "FAILURE_MEMORY_USEFUL_BUT_STANDARD_METHODS_SUFFICIENT"),
    (501, "REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE"),
}


def _mapping(value: object, *, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _sequence(value: object, *, label: str) -> Sequence[object]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{label} must be an array")
    return value


@dataclass(frozen=True)
class JumpProgrammeClosureReport:
    deliverable_count: int
    missing_deliverable_ids: tuple[str, ...]
    paper_programme_owner_count: int
    missing_paper_programme_ids: tuple[str, ...]
    dependency_disposition_count: int
    missing_child_dispositions: tuple[str, ...]
    malformed_dependency_ids: tuple[str, ...]
    generic_new_jump_atoms_claimed: int
    composition_coordinate_count: int
    local_zero_error_terminal: ZeroErrorJumpTerminal
    local_zero_error_checks_passed: bool
    strong_parent_matches_orion: bool
    orion_incremental_protected_gap: int
    static_packet_certifies_merge_state: bool
    scientific_packet_ready_for_external_integration: bool
    terminal: JumpProgrammeTerminal
    digest: str

    @property
    def grants_scientific_adoption(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    @property
    def grants_issue_closure_authority(self) -> bool:
        return False

    @property
    def certifies_dependency_ci_or_merge(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "JumpProgrammeClosureReport.v1",
            "deliverable_count": self.deliverable_count,
            "missing_deliverable_ids": list(self.missing_deliverable_ids),
            "paper_programme_owner_count": self.paper_programme_owner_count,
            "missing_paper_programme_ids": list(self.missing_paper_programme_ids),
            "dependency_disposition_count": self.dependency_disposition_count,
            "missing_child_dispositions": list(self.missing_child_dispositions),
            "malformed_dependency_ids": list(self.malformed_dependency_ids),
            "generic_new_jump_atoms_claimed": self.generic_new_jump_atoms_claimed,
            "composition_coordinate_count": self.composition_coordinate_count,
            "local_zero_error_terminal": self.local_zero_error_terminal.value,
            "local_zero_error_checks_passed": self.local_zero_error_checks_passed,
            "strong_parent_matches_orion": self.strong_parent_matches_orion,
            "orion_incremental_protected_gap": self.orion_incremental_protected_gap,
            "static_packet_certifies_merge_state": self.static_packet_certifies_merge_state,
            "scientific_packet_ready_for_external_integration": self.scientific_packet_ready_for_external_integration,
            "terminal": self.terminal.value,
            "grants_scientific_adoption": False,
            "grants_novelty_authority": False,
            "grants_issue_closure_authority": False,
            "certifies_dependency_ci_or_merge": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("Jump programme closure digest mismatch")
        if self.static_packet_certifies_merge_state:
            raise ValueError("static Jump closure packet may not certify GitHub merge state")


def build_jump_programme_closure_report(
    *,
    ownership: Mapping[str, object],
    expected: Mapping[str, object],
    local_zero_error_terminal: ZeroErrorJumpTerminal,
    local_zero_error_checks_passed: bool,
    strong_parent_matches_orion: bool,
    orion_incremental_protected_gap: int,
) -> JumpProgrammeClosureReport:
    if ownership.get("version") != "JumpProgrammeOwnership.v1":
        raise ValueError("unexpected Jump programme ownership version")
    if expected.get("version") != "JumpProgrammeClosureExpected.v1":
        raise ValueError("unexpected Jump programme expected version")

    raw_deliverables = _sequence(ownership.get("deliverables", ()), label="deliverables")
    deliverable_ids: list[str] = []
    for raw in raw_deliverables:
        row = _mapping(raw, label="deliverable row")
        deliverable_id = str(row.get("id", ""))
        owners = _sequence(row.get("owners", ()), label=f"owners for {deliverable_id}")
        if not deliverable_id or not owners or not str(row.get("status", "")):
            raise ValueError("every #500 deliverable requires identity, owner, and status")
        deliverable_ids.append(deliverable_id)
    if len(deliverable_ids) != len(set(deliverable_ids)):
        raise ValueError("duplicate #500 deliverable identity")
    missing_deliverables = tuple(
        sorted(set(_REQUIRED_DELIVERABLE_IDS) - set(deliverable_ids))
    )

    raw_papers = _sequence(
        ownership.get("paper_programme_ownership", ()),
        label="paper/programme ownership",
    )
    paper_ids: list[str] = []
    for raw in raw_papers:
        row = _mapping(raw, label="paper/programme row")
        row_id = str(row.get("id", ""))
        if (
            not row_id
            or not str(row.get("jump_role", ""))
            or not str(row.get("update", ""))
            or not str(row.get("authority", ""))
        ):
            raise ValueError("paper/programme ownership rows must be complete")
        paper_ids.append(row_id)
    if len(paper_ids) != len(set(paper_ids)):
        raise ValueError("duplicate paper/programme ownership identity")
    missing_papers = tuple(
        sorted(set(_REQUIRED_PAPER_PROGRAMME_IDS) - set(paper_ids))
    )

    raw_dependencies = _sequence(
        expected.get("dependency_dispositions", ()),
        label="dependency dispositions",
    )
    child_dispositions: set[tuple[int, str]] = set()
    malformed_dependencies: list[str] = []
    for index, raw in enumerate(raw_dependencies):
        row = _mapping(raw, label="dependency disposition")
        pr = row.get("pr")
        issue = row.get("issue")
        head = str(row.get("head", ""))
        terminal = str(row.get("terminal", ""))
        if not isinstance(pr, int) or pr <= 0 or len(head) != 40 or not terminal:
            malformed_dependencies.append(f"dependency-{index}")
        if issue is not None:
            if not isinstance(issue, int) or issue <= 0:
                malformed_dependencies.append(f"dependency-{index}")
            else:
                child_dispositions.add((issue, terminal))
    missing_child = tuple(
        sorted(
            f"#{issue}:{terminal}"
            for issue, terminal in _REQUIRED_CHILD_TERMINALS - child_dispositions
        )
    )

    raw_composition = _sequence(
        ownership.get("composition_owners", ()),
        label="composition owners",
    )
    for raw in raw_composition:
        row = _mapping(raw, label="composition owner")
        if row.get("generic_new_jump_atom") is not False:
            raise ValueError("composition row may not self-promote a generic Jump atom")
        if not str(row.get("coordinate", "")) or not str(row.get("owner", "")):
            raise ValueError("composition row requires coordinate and owner")

    generic_atoms = int(ownership.get("generic_new_jump_atoms_claimed", -1))
    if generic_atoms != 0:
        raise ValueError("programme closure may not manufacture generic Jump atoms")

    programme = _mapping(
        expected.get("programme_disposition", {}), label="programme disposition"
    )
    integration = _mapping(expected.get("integration_gate", {}), label="integration gate")
    static_certifies_merge = bool(integration.get("static_packet_certifies_merge_state", True))

    ready = (
        len(raw_deliverables) == int(expected.get("deliverable_count", -1))
        and not missing_deliverables
        and not missing_papers
        and not malformed_dependencies
        and not missing_child
        and generic_atoms == 0
        and local_zero_error_terminal
        is ZeroErrorJumpTerminal.REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE
        and local_zero_error_checks_passed
        and strong_parent_matches_orion
        and orion_incremental_protected_gap == 0
        and programme.get("registered_regime_transition_required_on_positive_benchmark")
        is True
        and programme.get("same_representation_search_sufficient_on_positive_benchmark")
        is False
        and programme.get("strong_verified_regime_revision_parent_matches_orion")
        is True
        and int(programme.get("orion_incremental_protected_gap", -1)) == 0
        and programme.get("broad_jump_atoms_survive_as_monoliths") is False
        and programme.get("historical_cases_used_as_protected_gold") is False
        and programme.get("open_ended_real_world_creativity_established") is False
        and static_certifies_merge is False
        and expected.get("candidate_terminal")
        == JumpProgrammeTerminal.REGIME_INVENTION_WITHOUT_INCREMENTAL_VALUE.value
    )
    terminal = (
        JumpProgrammeTerminal.REGIME_INVENTION_WITHOUT_INCREMENTAL_VALUE
        if ready
        else JumpProgrammeTerminal.CANNOT_CHECK
    )

    payload = {
        "version": "JumpProgrammeClosureReport.v1",
        "deliverable_count": len(raw_deliverables),
        "missing_deliverable_ids": list(missing_deliverables),
        "paper_programme_owner_count": len(raw_papers),
        "missing_paper_programme_ids": list(missing_papers),
        "dependency_disposition_count": len(raw_dependencies),
        "missing_child_dispositions": list(missing_child),
        "malformed_dependency_ids": sorted(set(malformed_dependencies)),
        "generic_new_jump_atoms_claimed": generic_atoms,
        "composition_coordinate_count": len(raw_composition),
        "local_zero_error_terminal": local_zero_error_terminal.value,
        "local_zero_error_checks_passed": bool(local_zero_error_checks_passed),
        "strong_parent_matches_orion": bool(strong_parent_matches_orion),
        "orion_incremental_protected_gap": int(orion_incremental_protected_gap),
        "static_packet_certifies_merge_state": static_certifies_merge,
        "scientific_packet_ready_for_external_integration": ready,
        "terminal": terminal.value,
        "grants_scientific_adoption": False,
        "grants_novelty_authority": False,
        "grants_issue_closure_authority": False,
        "certifies_dependency_ci_or_merge": False,
    }
    report = JumpProgrammeClosureReport(
        deliverable_count=payload["deliverable_count"],
        missing_deliverable_ids=tuple(payload["missing_deliverable_ids"]),
        paper_programme_owner_count=payload["paper_programme_owner_count"],
        missing_paper_programme_ids=tuple(payload["missing_paper_programme_ids"]),
        dependency_disposition_count=payload["dependency_disposition_count"],
        missing_child_dispositions=tuple(payload["missing_child_dispositions"]),
        malformed_dependency_ids=tuple(payload["malformed_dependency_ids"]),
        generic_new_jump_atoms_claimed=payload["generic_new_jump_atoms_claimed"],
        composition_coordinate_count=payload["composition_coordinate_count"],
        local_zero_error_terminal=ZeroErrorJumpTerminal(payload["local_zero_error_terminal"]),
        local_zero_error_checks_passed=payload["local_zero_error_checks_passed"],
        strong_parent_matches_orion=payload["strong_parent_matches_orion"],
        orion_incremental_protected_gap=payload["orion_incremental_protected_gap"],
        static_packet_certifies_merge_state=payload["static_packet_certifies_merge_state"],
        scientific_packet_ready_for_external_integration=payload[
            "scientific_packet_ready_for_external_integration"
        ],
        terminal=JumpProgrammeTerminal(payload["terminal"]),
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "JumpProgrammeClosureReport",
    "JumpProgrammeTerminal",
    "build_jump_programme_closure_report",
]
