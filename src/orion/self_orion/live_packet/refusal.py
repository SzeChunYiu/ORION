"""Section 7 -- typed provider refusal and immutable episode minting.

Credential presence is tested via `os.environ`; the value is never read into a
variable, never stored on an object, never serialized. Absence is a typed
refusal recording CANNOT_CHECK -- "could not check" and "checked and found
wrong" are different facts.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from enum import Enum

from orion.experience.learning import propose_failure_pattern
from orion.experience.model import EpisodeOutcome, FailurePatternCandidate, TaskEpisode

from .constants import PREFLIGHT_TIMESTAMP, _sha256
from .identity import CREDENTIAL_ENV_VARS, FROZEN_PROVIDERS
from .mechanic_cells import FIBRE_PROVIDER_ROLES
from .packet import FrozenLiveResearchPacket, frozen_live_research_packet


class LiveProviderStatus(str, Enum):
    """Why a live call did or did not happen. Mirrors `study.p1.provider`."""

    OK = "OK"
    NO_CREDENTIAL = "NO_CREDENTIAL"
    TRANSPORT_UNAVAILABLE = "TRANSPORT_UNAVAILABLE"
    PROVIDER_ERROR = "PROVIDER_ERROR"


NO_CREDENTIAL_SIGNATURE: tuple[str, ...] = (
    "provider:NO_CREDENTIAL",
    "trial:UNEXECUTED",
)


def credential_present(name: str) -> bool:
    """Whether a credential exists, without reading or returning its value."""

    return bool(os.environ.get(name))


def missing_credential_env_vars() -> tuple[str, ...]:
    """Names only. No value from the environment is ever returned or logged."""

    return tuple(name for name in CREDENTIAL_ENV_VARS if not credential_present(name))


def blocked_mechanic_ids(missing: Sequence[str] | None = None) -> tuple[str, ...]:
    """Fibres that cannot execute because their provider role lacks a credential."""

    absent = set(missing_credential_env_vars() if missing is None else missing)
    roles = {
        provider.role
        for provider in FROZEN_PROVIDERS
        if any(name in absent for name in provider.credential_env_vars)
    }
    return tuple(
        sorted(
            mechanic_id
            for mechanic_id, role in FIBRE_PROVIDER_ROLES.items()
            if role and role in roles
        )
    )


def _state_hash(packet: FrozenLiveResearchPacket, phase: str, task_id: str) -> str:
    return _sha256(
        {"packet": packet.fingerprint, "phase": phase, "task_id": task_id}
    )


def refusal_episodes(
    packet: FrozenLiveResearchPacket | None = None,
    *,
    missing: Sequence[str] | None = None,
    timestamp: str = PREFLIGHT_TIMESTAMP,
) -> tuple[TaskEpisode, ...]:
    """One immutable episode per (task, blocked fibre), recording CANNOT_CHECK.

    This is the refusal path made real rather than claimed. With no credential
    the trial produces evidence about itself -- which fibres could not run, on
    which tasks, under which frozen packet -- instead of producing nothing, and
    an unexecuted run that leaves no trace is indistinguishable from one that
    should never have existed.

    The episodes are shaped for `propose_failure_pattern`: same `mechanic_id`
    across tasks, distinct `run_id` per task, distinct `variation_signature` per
    task, and a shared core failure signature. That is what "suitable for later
    failure-pattern matching" has to mean if it is to be checkable.
    """

    resolved = packet or frozen_live_research_packet()
    absent = tuple(missing_credential_env_vars() if missing is None else missing)
    blocked = blocked_mechanic_ids(absent)
    episodes: list[TaskEpisode] = []
    for task in sorted(resolved.tasks, key=lambda item: item.task_id):
        run_id = f"{resolved.packet_id}:{task.task_id}:no-credential"
        for mechanic_id in blocked:
            episodes.append(
                TaskEpisode(
                    episode_id=f"episode:{run_id}:{mechanic_id}",
                    task_id=task.task_id,
                    run_id=run_id,
                    parent_run_id=None,
                    evaluation_epoch_id=resolved.evaluation_epoch_id,
                    split_id=task.split_id,
                    mechanic_id=mechanic_id,
                    problem_signature=(task.kind.value, *task.variation_signature),
                    variation_signature=task.variation_signature,
                    pre_state_hash=_state_hash(resolved, "pre", task.task_id),
                    action_ids=("action:credential_preflight",),
                    observation_ids=tuple(f"missing_env_var:{name}" for name in absent),
                    outcome=EpisodeOutcome.CANNOT_CHECK,
                    failure_signature=(
                        *NO_CREDENTIAL_SIGNATURE,
                        f"mechanic:{mechanic_id}",
                    ),
                    residual_ids=(f"residual:{mechanic_id}:unexecuted",),
                    evidence_ids=(),
                    evidence_bindings=(),
                    post_state_hash=_state_hash(resolved, "post", task.task_id),
                    timestamp=timestamp,
                    provenance_ids=(f"packet:{resolved.fingerprint}",),
                )
            )
    return tuple(episodes)


def failure_pattern_candidates(
    episodes: Sequence[TaskEpisode],
) -> tuple[FailurePatternCandidate, ...]:
    """Group immutable episodes by mechanic and propose candidate patterns.

    Proposal only. `FailurePatternCandidate` refuses to be constructed with any
    authority above CANDIDATE, so this path cannot raise authority even by
    mistake -- the invariant lives in the type, not in this function's manners.
    """

    by_mechanic: dict[str, list[TaskEpisode]] = {}
    for episode in sorted(episodes, key=lambda item: item.episode_id):
        by_mechanic.setdefault(episode.mechanic_id, []).append(episode)
    candidates: list[FailurePatternCandidate] = []
    for mechanic_id, group in sorted(by_mechanic.items()):
        candidate = propose_failure_pattern(
            tuple(group),
            pattern_id=f"pattern:{mechanic_id}",
            candidate_guard=(
                f"refuse to report a score for {mechanic_id} when its provider "
                "role has no credential; record CANNOT_CHECK instead"
            ),
            falsifier=(
                f"{mechanic_id} executes and is independently verified while its "
                "provider role remains unconfigured"
            ),
        )
        if candidate is not None:
            candidates.append(candidate)
    return tuple(candidates)
