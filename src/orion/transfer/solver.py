from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .types import AlgorithmCell, ProblemSignature, TransferAssessment, assess_transfer


@dataclass(frozen=True)
class RankedTransfer:
    cell: AlgorithmCell
    assessment: TransferAssessment


@dataclass(frozen=True)
class ConfirmedTransfer:
    mechanism: str
    members: tuple[RankedTransfer, ...]

    @property
    def source_domains(self) -> frozenset[str]:
        return frozenset(member.cell.source_signature.source_domain for member in self.members)


class StructuralTransferSolver:
    """Retrieves structural analogues but promotes only verified transfers."""

    def rank(
        self,
        target: ProblemSignature,
        cells: Sequence[AlgorithmCell],
    ) -> tuple[AlgorithmCell, ...]:
        return tuple(
            sorted(
                cells,
                key=lambda cell: target.far_domain_score(cell.source_signature),
                reverse=True,
            )
        )

    def verify(
        self,
        target: ProblemSignature,
        cell: AlgorithmCell,
        *,
        assumption_truth: Mapping[str, bool | None],
        falsifier_results: Mapping[str, bool | None],
    ) -> TransferAssessment:
        return assess_transfer(target, cell, assumption_truth, falsifier_results)

    def select(
        self,
        target: ProblemSignature,
        cells: Sequence[AlgorithmCell],
        evidence_by_cell: Mapping[
            str, tuple[Mapping[str, bool | None], Mapping[str, bool | None]]
        ],
    ) -> RankedTransfer | None:
        """Return the highest-ranked *admissible* cell, never merely the closest analogue."""

        for cell in self.rank(target, cells):
            evidence = evidence_by_cell.get(cell.cell_id)
            if evidence is None:
                continue
            assessment = self.verify(
                target,
                cell,
                assumption_truth=evidence[0],
                falsifier_results=evidence[1],
            )
            if assessment.admissible:
                return RankedTransfer(cell=cell, assessment=assessment)
        return None

    def cross_confirm(
        self,
        target: ProblemSignature,
        cells: Sequence[AlgorithmCell],
        evidence_by_cell: Mapping[
            str, tuple[Mapping[str, bool | None], Mapping[str, bool | None]]
        ],
        *,
        mechanism: str,
        min_independent_domains: int = 2,
    ) -> ConfirmedTransfer | None:
        """Require a mechanism to survive in multiple independent source domains.

        This is an optional stronger gate for analogy hypotheses that may be accidental.
        Multiple cells from the same domain do not count as cross-confirmation.
        """

        if min_independent_domains < 2:
            raise ValueError("cross-confirmation requires at least two source domains")
        verified: list[RankedTransfer] = []
        seen_domains: set[str] = set()
        for cell in self.rank(target, cells):
            if cell.mechanism != mechanism:
                continue
            evidence = evidence_by_cell.get(cell.cell_id)
            if evidence is None:
                continue
            assessment = self.verify(
                target,
                cell,
                assumption_truth=evidence[0],
                falsifier_results=evidence[1],
            )
            domain = cell.source_signature.source_domain
            if assessment.admissible and domain not in seen_domains:
                verified.append(RankedTransfer(cell=cell, assessment=assessment))
                seen_domains.add(domain)
            if len(seen_domains) >= min_independent_domains:
                return ConfirmedTransfer(mechanism=mechanism, members=tuple(verified))
        return None
