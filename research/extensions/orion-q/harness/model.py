from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from orion.transfer.v2.canonical import content_digest


AUTHORITY_FALSE_FIELDS = (
    "grants_scientific_authority",
    "grants_novelty_authority",
    "grants_revision_authority",
    "grants_adoption_authority",
    "grants_promotion_authority",
    "grants_merge_authority",
    "grants_global_task_stop_authority",
    "r6_authority",
)


def _uniq(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(v) for v in values}))


def _obs(values: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(k), str(v)) for k, v in values.items()))


@dataclass(frozen=True)
class ProtectedReference:
    ref_id: str
    path: str
    blob: str
    released: bool = False

    def unsigned(self) -> dict[str, object]:
        return {
            "ref_id": self.ref_id,
            "path": self.path,
            "blob": self.blob,
            "released": self.released,
        }


@dataclass(frozen=True)
class ResearchState:
    campaign_id: str
    claim_id: str
    phase_id: str
    cycle_index: int
    manifest_digest: str
    protocol_ids: tuple[str, ...]
    observations: tuple[tuple[str, str], ...]
    active_hard_obligations: tuple[str, ...]
    protected_refs: tuple[ProtectedReference, ...]
    history_receipt_digests: tuple[str, ...]
    authority_ceiling: str
    digest: str

    @property
    def observation_map(self) -> dict[str, str]:
        return dict(self.observations)

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "ORIONQ.ResearchState.v1",
            "campaign_id": self.campaign_id,
            "claim_id": self.claim_id,
            "phase_id": self.phase_id,
            "cycle_index": self.cycle_index,
            "manifest_digest": self.manifest_digest,
            "protocol_ids": list(self.protocol_ids),
            "observations": [[k, v] for k, v in self.observations],
            "active_hard_obligations": list(self.active_hard_obligations),
            "protected_refs": [ref.unsigned() for ref in self.protected_refs],
            "history_receipt_digests": list(self.history_receipt_digests),
            "authority_ceiling": self.authority_ceiling,
            **{name: False for name in AUTHORITY_FALSE_FIELDS},
        }

    def verify(self) -> None:
        if not self.campaign_id or not self.claim_id or not self.phase_id:
            raise ValueError("research state identities are required")
        if self.cycle_index < 0:
            raise ValueError("cycle index must be non-negative")
        if len(self.observations) != len({k for k, _ in self.observations}):
            raise ValueError("duplicate observation key")
        if len(self.protected_refs) != len({r.ref_id for r in self.protected_refs}):
            raise ValueError("duplicate protected reference")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("research state digest mismatch")


def build_state(
    *,
    campaign_id: str,
    claim_id: str,
    phase_id: str,
    cycle_index: int,
    manifest_digest: str,
    protocol_ids: Sequence[str],
    observations: Mapping[str, str],
    active_hard_obligations: Sequence[str] = (),
    protected_refs: Sequence[ProtectedReference] = (),
    history_receipt_digests: Sequence[str] = (),
    authority_ceiling: str = "NON_AUTHORIZING_RESEARCH_CONTROL",
) -> ResearchState:
    tmp = ResearchState(
        campaign_id=str(campaign_id),
        claim_id=str(claim_id),
        phase_id=str(phase_id),
        cycle_index=int(cycle_index),
        manifest_digest=str(manifest_digest),
        protocol_ids=_uniq(protocol_ids),
        observations=_obs(observations),
        active_hard_obligations=_uniq(active_hard_obligations),
        protected_refs=tuple(protected_refs),
        history_receipt_digests=tuple(map(str, history_receipt_digests)),
        authority_ceiling=str(authority_ceiling),
        digest="",
    )
    state = ResearchState(**{**tmp.__dict__, "digest": content_digest(tmp.unsigned())})
    state.verify()
    return state


@dataclass(frozen=True)
class NativeDecisionReceipt:
    phase_id: str
    selected_kind: str | None
    selected_id: str | None
    responsibility: Mapping[str, object]
    interface: Mapping[str, object]
    revision: Mapping[str, object]
    computation: Mapping[str, object]
    control: Mapping[str, object]
    shadow_control: Mapping[str, object] | None
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "ORIONQ.NativeDecisionReceipt.v1",
            "phase_id": self.phase_id,
            "selected_kind": self.selected_kind,
            "selected_id": self.selected_id,
            "responsibility": dict(self.responsibility),
            "interface": dict(self.interface),
            "revision": dict(self.revision),
            "computation": dict(self.computation),
            "control": dict(self.control),
            "shadow_control": None if self.shadow_control is None else dict(self.shadow_control),
            **{name: False for name in AUTHORITY_FALSE_FIELDS},
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("native decision receipt digest mismatch")


@dataclass(frozen=True)
class CapabilityExecutionReceipt:
    capability_id: str
    status: str
    command: tuple[str, ...]
    exit_code: int | None
    stdout_sha256: str
    stderr_sha256: str
    parsed_payload_sha256: str | None
    evidence_updates: tuple[tuple[str, str], ...]
    failure_class: str | None
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "ORIONQ.CapabilityExecutionReceipt.v1",
            "capability_id": self.capability_id,
            "status": self.status,
            "command": list(self.command),
            "exit_code": self.exit_code,
            "stdout_sha256": self.stdout_sha256,
            "stderr_sha256": self.stderr_sha256,
            "parsed_payload_sha256": self.parsed_payload_sha256,
            "evidence_updates": [[k, v] for k, v in self.evidence_updates],
            "failure_class": self.failure_class,
            **{name: False for name in AUTHORITY_FALSE_FIELDS},
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("capability execution receipt digest mismatch")


@dataclass(frozen=True)
class TransitionReceipt:
    before_state_digest: str
    decision_digest: str
    execution_digest: str | None
    after_state_digest: str
    terminal: str
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "ORIONQ.ResearchTransitionReceipt.v1",
            "before_state_digest": self.before_state_digest,
            "decision_digest": self.decision_digest,
            "execution_digest": self.execution_digest,
            "after_state_digest": self.after_state_digest,
            "terminal": self.terminal,
            **{name: False for name in AUTHORITY_FALSE_FIELDS},
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("transition receipt digest mismatch")
