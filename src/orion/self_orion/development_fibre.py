from __future__ import annotations

import hashlib
from dataclasses import dataclass

from orion.experience.model import TaskEpisode
from orion.mechanics.model import MechanicCell
from orion.mechanics.questioning import MechanicQuestion, generate_mechanic_questions
from orion.self_orion.development_driver import EmpiricalWorkItem, empirical_frontier
from orion.self_orion.rakl_transfer import RaklTransferReceipt, rakl_transfer_receipts


@dataclass(frozen=True)
class DevelopmentFibre:
    mechanic_id: str
    cell: MechanicCell
    open_questions: tuple[MechanicQuestion, ...]
    empirical_work: tuple[EmpiricalWorkItem, ...]
    related_episode_ids: tuple[str, ...]
    failure_episode_ids: tuple[str, ...]
    transfer_receipt: RaklTransferReceipt | None
    unresolved_warnings: tuple[str, ...]
    snapshot_hash: str


def _snapshot_hash(*parts: object) -> str:
    return hashlib.sha256(repr(parts).encode("utf-8")).hexdigest()


def compile_development_fibre(
    mechanic_id: str,
    cells: tuple[MechanicCell, ...],
    *,
    episodes: tuple[TaskEpisode, ...] = (),
    top_k_episodes: int = 24,
) -> DevelopmentFibre:
    """Compile the target-conditioned Self-ORION working view for one mechanic.

    This is the ORION-native successor of RAKL ProblemFibre. It is a derived working
    view only: co-retrieval does not imply compatibility or authority, and the fibre
    cannot promote its own lessons/contracts.
    """

    if top_k_episodes < 1:
        raise ValueError("top_k_episodes must be positive")
    by_id = {cell.mechanic_id: cell for cell in cells}
    cell = by_id.get(mechanic_id)
    if cell is None:
        raise KeyError(f"unknown mechanic: {mechanic_id}")
    questions = generate_mechanic_questions(cell)
    work = tuple(item for item in empirical_frontier((cell,)) if item.mechanic_id == mechanic_id)
    related = tuple(item for item in episodes if item.mechanic_id == mechanic_id)[:top_k_episodes]
    failures = tuple(
        item
        for item in related
        if item.failure_signature or item.residual_ids
    )
    receipt = next(
        (item for item in rakl_transfer_receipts(cells) if item.mechanic_id == mechanic_id),
        None,
    )
    warnings: list[str] = []
    if questions:
        warnings.append("structural_questions_open")
    if not related:
        warnings.append("no_mechanic_experience_available")
    if receipt is None:
        warnings.append("no_local_or_rakl_transfer_receipt")
    if work:
        warnings.append("empirical_frontier_open")
    snapshot = _snapshot_hash(
        mechanic_id,
        cell,
        tuple(item.question_id for item in questions),
        tuple(item.work_id for item in work),
        tuple(item.episode_id for item in related),
        tuple(warnings),
        receipt,
    )
    return DevelopmentFibre(
        mechanic_id=mechanic_id,
        cell=cell,
        open_questions=questions,
        empirical_work=work,
        related_episode_ids=tuple(item.episode_id for item in related),
        failure_episode_ids=tuple(item.episode_id for item in failures),
        transfer_receipt=receipt,
        unresolved_warnings=tuple(warnings),
        snapshot_hash=snapshot,
    )


def rank_development_fibres(
    cells: tuple[MechanicCell, ...],
    *,
    episodes: tuple[TaskEpisode, ...] = (),
    limit: int = 12,
) -> tuple[DevelopmentFibre, ...]:
    if limit < 1:
        raise ValueError("fibre limit must be positive")
    fibres = tuple(
        compile_development_fibre(cell.mechanic_id, cells, episodes=episodes)
        for cell in cells
    )
    return tuple(
        sorted(
            fibres,
            key=lambda item: (
                -max((work.priority for work in item.empirical_work), default=0),
                -len(item.failure_episode_ids),
                -len(item.open_questions),
                item.mechanic_id,
            ),
        )[:limit]
    )


__all__ = ["DevelopmentFibre", "compile_development_fibre", "rank_development_fibres"]
