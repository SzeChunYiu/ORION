from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .protocol import content_digest

_STATE_SCHEMA = "ORION.ResearchCampaignState.v1"
_DECISION_SCHEMA = "ORION.ResearchCampaignDecision.v1"
_TRANSITION_SCHEMA = "ORION.ResearchCampaignTransition.v1"
CAMPAIGN_STATE_SCHEMA = _STATE_SCHEMA
CAMPAIGN_DECISION_SCHEMA = _DECISION_SCHEMA
CAMPAIGN_TRANSITION_SCHEMA = _TRANSITION_SCHEMA
_AUTHORITY_FIELDS = (
    "grants_scientific_authority",
    "grants_novelty_authority",
    "grants_adoption_authority",
    "grants_promotion_authority",
    "grants_merge_authority",
    "grants_global_task_stop_authority",
)


def authority_false() -> dict[str, bool]:
    return {key: False for key in _AUTHORITY_FIELDS}


def _string(value: Any, name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not allow_empty and not value.strip():
        raise ValueError(f"{name} must be non-empty")
    return value


def _digest(value: Any, name: str) -> str:
    value = _string(value, name)
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return value


def _strings(value: Any, name: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise TypeError(f"{name} must be an array")
    rows = tuple(_string(item, f"{name} entry") for item in value)
    if len(rows) != len(set(rows)):
        raise ValueError(f"{name} must not contain duplicates")
    return rows


def _authority_must_be_false(raw: Mapping[str, Any]) -> None:
    for key in _AUTHORITY_FIELDS:
        if raw.get(key) is not False:
            raise ValueError(f"campaign authority field must be false: {key}")


@dataclass(frozen=True)
class ProtectedReference:
    ref_id: str
    path: str = ""
    blob: str = ""
    released: bool = False

    def __post_init__(self) -> None:
        _string(self.ref_id, "ref_id")
        _string(self.path, "path", allow_empty=True)
        _string(self.blob, "blob", allow_empty=True)
        if not isinstance(self.released, bool):
            raise TypeError("released must be a boolean")
        if not self.path and not self.blob:
            raise ValueError("protected reference requires path or blob")

    def as_dict(self) -> dict[str, Any]:
        return {
            "ref_id": self.ref_id,
            "path": self.path,
            "blob": self.blob,
            "released": self.released,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ProtectedReference":
        if not isinstance(raw, Mapping):
            raise TypeError("protected reference must be an object")
        released = raw.get("released", False)
        if not isinstance(released, bool):
            raise TypeError("released must be a boolean")
        return cls(
            ref_id=_string(raw.get("ref_id"), "ref_id"),
            path=_string(raw.get("path", ""), "path", allow_empty=True),
            blob=_string(raw.get("blob", ""), "blob", allow_empty=True),
            released=released,
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
    schema: str = _STATE_SCHEMA

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
            "observations": [[k, v] for k, v in self.observations],
            "active_hard_obligations": list(self.active_hard_obligations),
            "protected_refs": [item.as_dict() for item in self.protected_refs],
            "history_digests": list(self.history_digests),
            "authority_ceiling": self.authority_ceiling,
            **authority_false(),
        }

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {**self.unsigned(), "state_digest": self.state_digest}

    def validate(self) -> None:
        if self.schema != _STATE_SCHEMA:
            raise ValueError("unsupported campaign state schema")
        _string(self.campaign_id, "campaign_id")
        _string(self.claim_id, "claim_id")
        _string(self.phase_id, "phase_id")
        if not isinstance(self.cycle_index, int) or isinstance(self.cycle_index, bool) or self.cycle_index < 0:
            raise ValueError("cycle_index must be a non-negative integer")
        _digest(self.manifest_digest, "manifest_digest")
        _string(self.authority_ceiling, "authority_ceiling")
        if len(self.observations) != len({k for k, _ in self.observations}):
            raise ValueError("duplicate campaign observation")
        for key, value in self.observations:
            _string(key, "observation key")
            _string(value, "observation value")
        _strings(self.active_hard_obligations, "active_hard_obligations")
        if len(self.protected_refs) != len({item.ref_id for item in self.protected_refs}):
            raise ValueError("duplicate protected reference")
        for item in self.protected_refs:
            if not isinstance(item, ProtectedReference):
                raise TypeError("protected_refs entries must be ProtectedReference")
        for index, value in enumerate(self.history_digests):
            _digest(value, f"history_digests[{index}]")
        _digest(self.state_digest, "state_digest")
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
        if not isinstance(observations, Mapping):
            raise TypeError("observations must be an object")
        rows = tuple(sorted((_string(k, "observation key"), _string(v, "observation value")) for k, v in observations.items()))
        obligations = _strings(tuple(active_hard_obligations), "active_hard_obligations")
        refs = tuple(protected_refs)
        history = tuple(history_digests)
        seed = cls(
            campaign_id=_string(campaign_id, "campaign_id"),
            claim_id=_string(claim_id, "claim_id"),
            phase_id=_string(phase_id, "phase_id"),
            cycle_index=cycle_index,
            manifest_digest=_digest(manifest_digest, "manifest_digest"),
            observations=rows,
            active_hard_obligations=obligations,
            protected_refs=refs,
            history_digests=history,
            authority_ceiling=_string(authority_ceiling, "authority_ceiling"),
            state_digest="",
        )
        state = cls(**{**seed.__dict__, "state_digest": content_digest(seed.unsigned())})
        state.validate()
        return state

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "CampaignState":
        if not isinstance(raw, Mapping) or raw.get("schema") != _STATE_SCHEMA:
            raise ValueError("unsupported campaign state schema")
        _authority_must_be_false(raw)
        obs_raw = raw.get("observations", ())
        if not isinstance(obs_raw, list):
            raise TypeError("observations must be an array")
        observations = []
        for row in obs_raw:
            if not isinstance(row, list) or len(row) != 2:
                raise ValueError("observation row must contain two entries")
            observations.append((_string(row[0], "observation key"), _string(row[1], "observation value")))
        state = cls(
            campaign_id=_string(raw.get("campaign_id"), "campaign_id"),
            claim_id=_string(raw.get("claim_id"), "claim_id"),
            phase_id=_string(raw.get("phase_id"), "phase_id"),
            cycle_index=raw.get("cycle_index"),
            manifest_digest=_digest(raw.get("manifest_digest"), "manifest_digest"),
            observations=tuple(observations),
            active_hard_obligations=_strings(raw.get("active_hard_obligations", ()), "active_hard_obligations"),
            protected_refs=tuple(ProtectedReference.from_dict(item) for item in raw.get("protected_refs", ())),
            history_digests=_strings(raw.get("history_digests", ()), "history_digests"),
            authority_ceiling=_string(raw.get("authority_ceiling"), "authority_ceiling"),
            state_digest=_digest(raw.get("state_digest"), "state_digest"),
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
    decision_digest: str
    schema: str = _DECISION_SCHEMA

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
            **authority_false(),
        }

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {**self.unsigned(), "decision_digest": self.decision_digest}

    def validate(self) -> None:
        if self.schema != _DECISION_SCHEMA:
            raise ValueError("unsupported campaign decision schema")
        _string(self.phase_id, "phase_id")
        if self.selected_kind is not None:
            _string(self.selected_kind, "selected_kind")
        if self.selected_id is not None:
            _string(self.selected_id, "selected_id")
        _digest(self.decision_digest, "decision_digest")
        if self.decision_digest != content_digest(self.unsigned()):
            raise ValueError("campaign decision digest mismatch")


@dataclass(frozen=True)
class CampaignTransition:
    campaign_id: str
    cycle_index: int
    before_state_digest: str
    decision_digest: str
    request_digest: str | None
    result_digest: str | None
    after_state_digest: str
    terminal: str
    transition_digest: str
    schema: str = _TRANSITION_SCHEMA

    def unsigned(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "campaign_id": self.campaign_id,
            "cycle_index": self.cycle_index,
            "before_state_digest": self.before_state_digest,
            "decision_digest": self.decision_digest,
            "request_digest": self.request_digest,
            "result_digest": self.result_digest,
            "after_state_digest": self.after_state_digest,
            "terminal": self.terminal,
            **authority_false(),
        }

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {**self.unsigned(), "transition_digest": self.transition_digest}

    def validate(self) -> None:
        if self.schema != _TRANSITION_SCHEMA:
            raise ValueError("unsupported campaign transition schema")
        _string(self.campaign_id, "campaign_id")
        if not isinstance(self.cycle_index, int) or isinstance(self.cycle_index, bool) or self.cycle_index < 0:
            raise ValueError("cycle_index must be a non-negative integer")
        for value, name in (
            (self.before_state_digest, "before_state_digest"),
            (self.decision_digest, "decision_digest"),
            (self.after_state_digest, "after_state_digest"),
            (self.transition_digest, "transition_digest"),
        ):
            _digest(value, name)
        if self.request_digest is not None:
            _digest(self.request_digest, "request_digest")
        if self.result_digest is not None:
            _digest(self.result_digest, "result_digest")
        _string(self.terminal, "terminal")
        if self.transition_digest != content_digest(self.unsigned()):
            raise ValueError("campaign transition digest mismatch")


__all__ = [
    "CAMPAIGN_DECISION_SCHEMA",
    "CAMPAIGN_STATE_SCHEMA",
    "CAMPAIGN_TRANSITION_SCHEMA",
    "CampaignDecision",
    "CampaignState",
    "CampaignTransition",
    "ProtectedReference",
    "authority_false",
]
