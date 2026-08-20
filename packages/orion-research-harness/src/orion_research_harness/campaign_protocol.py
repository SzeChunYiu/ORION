from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .protocol import content_digest

CAMPAIGN_STATE_SCHEMA = "ORION.ResearchCampaignState.v1"
CAMPAIGN_DECISION_SCHEMA = "ORION.ResearchCampaignDecision.v1"
CAMPAIGN_TRANSITION_SCHEMA = "ORION.ResearchCampaignTransition.v1"

_AUTHORITY_FIELDS = (
    "grants_scientific_authority",
    "grants_novelty_authority",
    "grants_adoption_authority",
    "grants_promotion_authority",
    "grants_merge_authority",
    "grants_global_task_stop_authority",
)


def _authority_false() -> dict[str, bool]:
    return {key: False for key in _AUTHORITY_FIELDS}


def _unique(values: Sequence[str]) -> tuple[str, ...]:
    rows = tuple(sorted({str(value) for value in values}))
    return rows


@dataclass(frozen=True)
class ProtectedReference:
    ref_id: str
    path: str
    blob: str
    released: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "ref_id": self.ref_id,
            "path": self.path,
            "blob": self.blob,
            "released": self.released,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ProtectedReference":
        return cls(
            ref_id=str(raw["ref_id"]),
            path=str(raw["path"]),
            blob=str(raw.get("blob", "")),
            released=bool(raw.get("released", False)),
        )


@dataclass(frozen=True)
class CampaignState:
    campaign_id: str
    claim_id: str
    phase_id: str
    cycle_index: int
    manifest_digest: str
    observations: tuple[tuple[str, str], ...]
    active_hard_obligations: tuple[str, ...]
    protected_refs: tuple[ProtectedReference, ...]
    history_digests: tuple[str, ...]
    authority_ceiling: str
    state_digest: str
    schema: str = CAMPAIGN_STATE_SCHEMA

    @property
    def observation_map(self) -> dict[str, str]:
        return dict(self.observations)

    def unsigned(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "campaign_id": self.campaign_id,
            "claim_id": self.claim_id,
            "phase_id": self.phase_id,
            "cycle_index": self.cycle_index,
            "manifest_digest": self.manifest_digest,
            "observations": [[key, value] for key, value in self.observations],
            "active_hard_obligations": list(self.active_hard_obligations),
            "protected_refs": [item.as_dict() for item in self.protected_refs],
            "history_digests": list(self.history_digests),
            "authority_ceiling": self.authority_ceiling,
            **_authority_false(),
        }

    def as_dict(self) -> dict[str, Any]:
        return {**self.unsigned(), "state_digest": self.state_digest}

    def validate(self) -> None:
        if self.schema != CAMPAIGN_STATE_SCHEMA:
            raise ValueError("unsupported campaign state schema")
        if not self.campaign_id or not self.claim_id or not self.phase_id:
            raise ValueError("campaign state identities are required")
        if self.cycle_index < 0:
            raise ValueError("campaign cycle index must be non-negative")
        if len(self.observations) != len({key for key, _ in self.observations}):
            raise ValueError("duplicate campaign observation")
        if len(self.protected_refs) != len({item.ref_id for item in self.protected_refs}):
            raise ValueError("duplicate protected reference")
        if self.state_digest != content_digest(self.unsigned()):
            raise ValueError("campaign state digest mismatch")

    @classmethod
    def create(
        cls,
        *,
        campaign_id: str,
        claim_id: str,
        phase_id: str,
        cycle_index: int,
        manifest_digest: str,
        observations: Mapping[str, str],
        active_hard_obligations: Sequence[str] = (),
        protected_refs: Sequence[ProtectedReference] = (),
        history_digests: Sequence[str] = (),
        authority_ceiling: str = "NON_AUTHORIZING_RESEARCH_CONTROL",
    ) -> "CampaignState":
        base = cls(
            campaign_id=str(campaign_id),
            claim_id=str(claim_id),
            phase_id=str(phase_id),
            cycle_index=int(cycle_index),
            manifest_digest=str(manifest_digest),
            observations=tuple(sorted((str(k), str(v)) for k, v in observations.items())),
            active_hard_obligations=_unique(active_hard_obligations),
            protected_refs=tuple(protected_refs),
            history_digests=tuple(map(str, history_digests)),
            authority_ceiling=str(authority_ceiling),
            state_digest="",
        )
        state = cls(**{**base.__dict__, "state_digest": content_digest(base.unsigned())})
        state.validate()
        return state

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "CampaignState":
        state = cls(
            schema=str(raw.get("schema", "")),
            campaign_id=str(raw["campaign_id"]),
            claim_id=str(raw["claim_id"]),
            phase_id=str(raw["phase_id"]),
            cycle_index=int(raw["cycle_index"]),
            manifest_digest=str(raw["manifest_digest"]),
            observations=tuple((str(k), str(v)) for k, v in raw["observations"]),
            active_hard_obligations=tuple(map(str, raw.get("active_hard_obligations", ()))),
            protected_refs=tuple(
                ProtectedReference.from_dict(item) for item in raw.get("protected_refs", ())
            ),
            history_digests=tuple(map(str, raw.get("history_digests", ()))),
            authority_ceiling=str(raw.get("authority_ceiling", "")),
            state_digest=str(raw["state_digest"]),
        )
        state.validate()
        return state


@dataclass(frozen=True)
class CampaignDecision:
    phase_id: str
    selected_kind: str | None
    selected_id: str | None
    responsibility: Mapping[str, Any]
    interface: Mapping[str, Any]
    revision: Mapping[str, Any]
    computation: Mapping[str, Any]
    control: Mapping[str, Any]
    shadow_control: Mapping[str, Any] | None
    decision_digest: str
    schema: str = CAMPAIGN_DECISION_SCHEMA

    def unsigned(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "phase_id": self.phase_id,
            "selected_kind": self.selected_kind,
            "selected_id": self.selected_id,
            "responsibility": dict(self.responsibility),
            "interface": dict(self.interface),
            "revision": dict(self.revision),
            "computation": dict(self.computation),
            "control": dict(self.control),
            "shadow_control": None if self.shadow_control is None else dict(self.shadow_control),
            **_authority_false(),
        }

    def as_dict(self) -> dict[str, Any]:
        return {**self.unsigned(), "decision_digest": self.decision_digest}

    def validate(self) -> None:
        if self.schema != CAMPAIGN_DECISION_SCHEMA:
            raise ValueError("unsupported campaign decision schema")
        if self.decision_digest != content_digest(self.unsigned()):
            raise ValueError("campaign decision digest mismatch")


@dataclass(frozen=True)
class CampaignTransition:
    campaign_id: str
    cycle_index: int
    before_state_digest: str
    decision_digest: str
    capability_request_digest: str | None
    capability_result_digest: str | None
    after_state_digest: str
    terminal: str
    transition_digest: str
    schema: str = CAMPAIGN_TRANSITION_SCHEMA

    def unsigned(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "campaign_id": self.campaign_id,
            "cycle_index": self.cycle_index,
            "before_state_digest": self.before_state_digest,
            "decision_digest": self.decision_digest,
            "capability_request_digest": self.capability_request_digest,
            "capability_result_digest": self.capability_result_digest,
            "after_state_digest": self.after_state_digest,
            "terminal": self.terminal,
            **_authority_false(),
        }

    def as_dict(self) -> dict[str, Any]:
        return {**self.unsigned(), "transition_digest": self.transition_digest}

    def validate(self) -> None:
        if self.schema != CAMPAIGN_TRANSITION_SCHEMA:
            raise ValueError("unsupported campaign transition schema")
        if self.transition_digest != content_digest(self.unsigned()):
            raise ValueError("campaign transition digest mismatch")
