"""Section 3 -- the packet itself and its JSON publish/load round trip.

`FrozenLiveResearchPacket.body` is the exact payload the fingerprint is taken
over, so every string literal reachable from it is load-bearing. The writer
re-checks the serialized document against the environment before it touches the
disk, and the loader verifies the declared fingerprint rather than trusting it.
"""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from orion.self_orion.live_trial import FrozenLiveTrialPacket, FrozenTrialTask

from .constants import (
    BASELINE_ID,
    EVALUATION_EPOCH_ID,
    LIVE_RUNNER,
    LIVE_STACK_CONSTRUCTOR,
    PACKET_ID,
    PACKET_SCHEMA,
    PROTOCOL_PATH,
    SUCCESS_BOUNDARY,
    UNBOUND,
    _sha256,
)
from .identity import (
    CREDENTIAL_ENV_VARS,
    DEEP_CRITERIA,
    FROZEN_BASELINE,
    FROZEN_EVALUATOR,
    FROZEN_LIMITS,
    FROZEN_PROVIDERS,
    FrozenEvaluatorSpec,
    FrozenProviderIdentity,
    FrozenResourceLimits,
    MatchedBaselineSpec,
    WIDE_CRITERIA,
)
from .tasks import (
    DEEP_TASK_ID,
    FrozenTaskBinding,
    WIDE_TASK_ID,
    _DEEP_TASK,
    _DEEP_TASK_GOLD,
    _WIDE_TASK,
)


@dataclass(frozen=True)
class FrozenLiveResearchPacket:
    """The whole frozen trial: tasks, providers, limits, evaluator, baseline.

    `outcome_accessed` is structurally pinned to False. The freeze is only
    meaningful if nothing in it was chosen after seeing a result, so the object
    refuses to exist in a state that claims otherwise.
    """

    packet_id: str
    schema: str
    evaluation_epoch_id: str
    trial: FrozenLiveTrialPacket
    bindings: tuple[FrozenTaskBinding, ...]
    providers: tuple[FrozenProviderIdentity, ...]
    limits: FrozenResourceLimits
    evaluator: FrozenEvaluatorSpec
    baseline: MatchedBaselineSpec
    corpus_revision: str = UNBOUND
    outcome_accessed: bool = False

    def __post_init__(self) -> None:
        if self.outcome_accessed:
            raise ValueError(
                "a packet frozen after outcome access is not a frozen packet"
            )
        task_ids = {item.task_id for item in self.trial.tasks}
        binding_ids = [item.task_id for item in self.bindings]
        if len(set(binding_ids)) != len(binding_ids):
            raise ValueError("task bindings must be unique")
        if set(binding_ids) != task_ids:
            raise ValueError("every frozen task requires exactly one binding")
        roles = [item.role for item in self.providers]
        if len(set(roles)) != len(roles):
            raise ValueError("provider roles must be unique")
        if self.baseline.limits != self.limits:
            raise ValueError(
                "the baseline must be specified under the same limits as ORION"
            )

    @property
    def tasks(self) -> tuple[FrozenTrialTask, ...]:
        return self.trial.tasks

    def binding(self, task_id: str) -> FrozenTaskBinding | None:
        return next((item for item in self.bindings if item.task_id == task_id), None)

    def task(self, task_id: str) -> FrozenTrialTask | None:
        return next((item for item in self.tasks if item.task_id == task_id), None)

    @property
    def body(self) -> dict[str, object]:
        """The published packet, without its own fingerprint.

        The fingerprint is attached afterwards by `packet_document`. Hashing a
        payload that already contains the hash is a fixed point nobody can
        recompute, so the digest would verify only itself.
        """

        return {
            "schema": self.schema,
            "packet_id": self.packet_id,
            "issue": "SzeChunYiu/ORION#8",
            "status": "DESIGN_FROZEN",
            "outcome_accessed": self.outcome_accessed,
            "evaluation_epoch_id": self.evaluation_epoch_id,
            "success_boundary": SUCCESS_BOUNDARY,
            "corpus_revision": self.corpus_revision,
            "tasks": [
                {
                    "task_id": item.task_id,
                    "kind": item.kind.value,
                    "split_id": item.split_id,
                    "question": item.problem.question,
                    "scope": item.problem.scope,
                    "initial_domain_ids": list(item.problem.initial_domain_ids),
                    "success_criteria": list(item.problem.success_criteria),
                    "variation_signature": list(item.variation_signature),
                    "required_evidence_ids": list(item.required_evidence_ids),
                }
                for item in sorted(self.tasks, key=lambda entry: entry.task_id)
            ],
            "task_bindings": [
                item.payload
                for item in sorted(self.bindings, key=lambda entry: entry.task_id)
            ],
            "providers": [
                item.payload
                for item in sorted(self.providers, key=lambda entry: entry.role)
            ],
            "resource_limits": self.limits.payload,
            "evaluator": self.evaluator.payload,
            "matched_baseline": self.baseline.payload,
            "provider_manifest_hash": self.trial.provider_manifest_hash,
            "evaluator_artifact_hash": self.trial.evaluator_artifact_hash,
            "trial_fingerprint": self.trial.fingerprint,
            "execution": {
                "stack_constructor": LIVE_STACK_CONSTRUCTOR,
                "runner": LIVE_RUNNER,
                "credential_env_vars": list(CREDENTIAL_ENV_VARS),
                "command": "python -m orion.self_orion.live_packet --live",
            },
            "authority": {
                "model_output_may_increase_authority": False,
                "self_orion_may_merge_or_promote": False,
                "repairs": "proposal_only",
            },
        }

    @property
    def fingerprint(self) -> str:
        return _sha256(self.body)


def _provider_manifest_hash(
    providers: Sequence[FrozenProviderIdentity],
) -> str:
    return _sha256(
        {
            "schema": "P5.shadow-live-research.provider-manifest.v1",
            "providers": [item.payload for item in sorted(providers, key=lambda e: e.role)],
            "secret_material_included": False,
        }
    )


def frozen_live_research_packet(
    *, corpus_revision: str = UNBOUND
) -> FrozenLiveResearchPacket:
    """Build the frozen packet. Deterministic: same inputs, same fingerprint.

    `corpus_revision` is the one field bound at execution rather than at freeze.
    The deep-target corpus is a working checkout under concurrent edit, so a
    digest baked in here would be stale on arrival; the preflight refuses to
    call the trial runnable while it is UNBOUND.
    """

    tasks = (_WIDE_TASK, _DEEP_TASK)
    bindings = (
        FrozenTaskBinding(WIDE_TASK_ID, WIDE_CRITERIA, None, corpus_revision),
        FrozenTaskBinding(DEEP_TASK_ID, DEEP_CRITERIA, _DEEP_TASK_GOLD, corpus_revision),
    )
    trial = FrozenLiveTrialPacket(
        packet_id=PACKET_ID,
        evaluation_epoch_id=EVALUATION_EPOCH_ID,
        tasks=tasks,
        provider_manifest_hash=_provider_manifest_hash(FROZEN_PROVIDERS),
        evaluator_artifact_hash=FROZEN_EVALUATOR.artifact_hash,
        baseline_id=BASELINE_ID,
        resource_budget_units=FROZEN_LIMITS.budget_units,
        max_orion_to_baseline_resource_ratio=FROZEN_LIMITS.max_orion_to_baseline_ratio,
    )
    return FrozenLiveResearchPacket(
        packet_id=PACKET_ID,
        schema=PACKET_SCHEMA,
        evaluation_epoch_id=EVALUATION_EPOCH_ID,
        trial=trial,
        bindings=bindings,
        providers=FROZEN_PROVIDERS,
        limits=FROZEN_LIMITS,
        evaluator=FROZEN_EVALUATOR,
        baseline=FROZEN_BASELINE,
        corpus_revision=corpus_revision,
    )


def packet_document(packet: FrozenLiveResearchPacket | None = None) -> dict[str, object]:
    """The exact JSON published to `papers/.../LIVE_TRIAL_PACKET_V1.json`."""

    resolved = packet or frozen_live_research_packet()
    document = dict(resolved.body)
    document["packet_fingerprint"] = resolved.fingerprint
    return document


def _reject_secret_material(serialized: str) -> None:
    """Refuse to write a document containing any credential currently in the env.

    Mirrors `write_live_phase2_provider_manifest`. Short values are skipped: a
    variable set to something like `1` would match everywhere and turn a real
    guard into noise, and a checker that cries wolf on its first run is switched
    off before it ever catches anything.
    """

    for name in CREDENTIAL_ENV_VARS:
        value = os.environ.get(name, "")
        if len(value) >= 12 and value in serialized:
            raise RuntimeError(
                f"packet serialization attempted to include the value of {name}"
            )


def write_packet_document(
    path: Path | str = PROTOCOL_PATH,
    *,
    packet: FrozenLiveResearchPacket | None = None,
) -> Path:
    """Publish the packet, refusing to rewrite the frozen one at a new fingerprint.

    The canonical protocol path is the freeze. Binding a corpus revision changes
    the fingerprint, so writing an execution-bound packet over the checked-in one
    would replace the frozen artifact with a different document under the same
    name -- and an artifact any later command can rewrite in place is not frozen,
    whatever it is hashed with. Execution-bound packets go somewhere else.
    """

    resolved = packet or frozen_live_research_packet()
    target = Path(path)
    if (
        target.resolve() == PROTOCOL_PATH.resolve()
        and resolved.corpus_revision != UNBOUND
    ):
        raise ValueError(
            "refusing to overwrite the frozen protocol packet with a corpus-bound "
            f"one (revision {resolved.corpus_revision!r}); write it to another path"
        )
    serialized = json.dumps(packet_document(resolved), indent=2, sort_keys=True) + "\n"
    _reject_secret_material(serialized)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(serialized, encoding="utf-8")
    return target


def load_packet_document(path: Path | str = PROTOCOL_PATH) -> dict[str, object]:
    """Read the published packet and verify its declared fingerprint.

    A hand-edited packet fails here rather than being trusted, which is the only
    reason freezing a document by content hash is worth doing.
    """

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("packet document must be a JSON object")
    declared = raw.get("packet_fingerprint")
    body = {key: value for key, value in raw.items() if key != "packet_fingerprint"}
    if declared != _sha256(body):
        raise ValueError("packet document fingerprint mismatch")
    return raw
