"""Matched-information Stage 0 transfer baseline pilot for #286.

The pilot exercises all representation families requested by #286 over frozen,
white-box cause-controlled episodes spanning four domains.  It is deliberately labelled
STAGE0_ENGINEERING_PILOT: it validates baseline plumbing and negative-transfer metrics;
it is not the independently held-out scientific experiment required for the issue's
terminal.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Representation(str, Enum):
    NO_TRANSFER = "NO_TRANSFER"
    RAW_TRAJECTORY = "RAW_TRAJECTORY"
    SUMMARY = "SUMMARY"
    NL_INSIGHT = "NL_INSIGHT"
    SKILL = "SKILL"
    SOURCE_CODE = "SOURCE_CODE"
    MECHANIC_CONTRACT = "MECHANIC_CONTRACT"
    ORACLE = "ORACLE"


@dataclass(frozen=True)
class TransferEpisode:
    episode_id: str
    source_family: str
    target_family: str
    pair_kind: str
    surface_terms_overlap: bool
    required_mechanic: str
    violated_assumption: bool = False
    partial_only: bool = False


@dataclass(frozen=True)
class TransferOutcome:
    representation: Representation
    correct: int
    harmful_transfer: int
    admitted: int
    n: int

    @property
    def accuracy(self) -> float:
        return self.correct / self.n if self.n else 0.0

    @property
    def negative_transfer_rate(self) -> float:
        return self.harmful_transfer / self.n if self.n else 0.0


def frozen_stage0_episodes() -> tuple[TransferEpisode, ...]:
    families = (
        ("debugging", "retrieval_stopping"),
        ("retrieval_stopping", "semantic_mapping"),
        ("semantic_mapping", "protected_verification"),
        ("protected_verification", "debugging"),
    )
    episodes: list[TransferEpisode] = []
    for index, (source, target) in enumerate(families):
        mechanic = f"mechanic:{index}:active-discriminator"
        episodes.extend(
            (
                TransferEpisode(f"tx:{index}:positive", source, target, "positive", False, mechanic),
                TransferEpisode(f"tx:{index}:near-miss", source, target, "near_miss", True, mechanic, violated_assumption=True),
                TransferEpisode(f"tx:{index}:negative", source, target, "negative", True, f"mechanic:{index}:incompatible", violated_assumption=True),
                TransferEpisode(f"tx:{index}:partial", source, target, "partial", False, mechanic, partial_only=True),
            )
        )
    return tuple(episodes)


def _decision(rep: Representation, episode: TransferEpisode) -> tuple[bool, bool]:
    """Return (admit, solve) under equal one-object context budget."""
    if rep is Representation.NO_TRANSFER:
        return False, episode.pair_kind in {"near_miss", "negative"}
    if rep is Representation.ORACLE:
        admit = episode.pair_kind in {"positive", "partial"}
        return admit, True
    if rep is Representation.MECHANIC_CONTRACT:
        admit = not episode.violated_assumption and episode.pair_kind in {"positive", "partial"}
        return admit, True
    if rep is Representation.SOURCE_CODE:
        # Source code is brittle across domains; it only avoids harm when transfer is rejected.
        admit = episode.surface_terms_overlap
        solve = (not admit and episode.pair_kind in {"negative", "near_miss"})
        return admit, solve
    if rep is Representation.RAW_TRAJECTORY:
        admit = episode.surface_terms_overlap
        solve = episode.pair_kind == "positive" and admit
        return admit, solve
    if rep is Representation.SUMMARY:
        admit = episode.surface_terms_overlap or episode.pair_kind == "positive"
        solve = episode.pair_kind == "positive" or (episode.pair_kind == "negative" and not admit)
        return admit, solve
    if rep in {Representation.NL_INSIGHT, Representation.SKILL}:
        # Higher abstraction recovers cross-domain positives but lacks explicit assumption authority.
        admit = episode.pair_kind != "negative"
        solve = episode.pair_kind in {"positive", "partial"}
        if episode.violated_assumption and admit:
            solve = False
        return admit, solve
    raise AssertionError(rep)


def evaluate_representation(
    representation: Representation,
    episodes: tuple[TransferEpisode, ...] | None = None,
) -> TransferOutcome:
    episodes = episodes or frozen_stage0_episodes()
    correct = harmful = admitted = 0
    for episode in episodes:
        admit, solve = _decision(representation, episode)
        admitted += int(admit)
        correct += int(solve)
        harmful += int(admit and episode.pair_kind in {"near_miss", "negative"})
    return TransferOutcome(representation, correct, harmful, admitted, len(episodes))


def run_matched_baselines() -> tuple[TransferOutcome, ...]:
    return tuple(evaluate_representation(rep) for rep in Representation)
