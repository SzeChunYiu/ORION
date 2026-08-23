from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .protocol import content_digest

CAMPAIGN_STATE_SCHEMA = "ORION.ResearchCampaignState.v1"
CAMPAIGN_DECISION_SCHEMA = "ORION.ResearchCampaignDecision.v1"
CAMPAIGN_TRANSITION_SCHEMA = "ORION.ResearchCampaignTransition.v1"
_HEX = set("0123456789abcdef")

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


def _require_string(value: Any, *, name: str, nonempty: bool = True) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if nonempty and not value.strip():
        raise ValueError(f"{name} must be non-empty")
    return value


def _require_bool(value: Any, *, name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a boolean")
    return value


def _require_nonnegative_int(value: Any, *, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def _require_digest(value: Any, *, name: str) -> str:
    digest = _require_string(value, name=name)
    if len(digest) != 64 or any(character not in _HEX for character in digest):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    return digest


def _require_array(value: Any, *, name: str) -> tuple[Any, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, (tuple, list)):
        raise TypeError(f"{name} must be an array")
    return tuple(value)


def _string_array(value: Any, *, name: str) -> tuple[str, ...]:
    return tuple(
        _require_string(item, name=f"{name} entry")
        for item in _require_array(value, name=name)
    )


def _unique_strings(value: Any, *, name: str) -> tuple[str, ...]:
    rows = _string_array(value, name=name)
    if len(rows) != len(set(rows)):
        raise ValueError(f"duplicate {name}")
    return tuple(sorted(rows))


def _require_authority_false(raw: Mapping[str, Any]) -> None:
    for key in _AUTHORITY_FIELDS:
        if raw.get(key) is not False:
            raise ValueError(f"campaign authority field must be false: {key}")


@dataclass(frozen=True)
class ProtectedReference:
    ref_id: str
    path: str
    blob: str
    released: bool = False

    def verify(self) -> None:
        _require_string(self.ref_id, name="protected ref_id")
        _require_string(self.path, name="protected path", nonempty=False)
        _require_string(self.blob, name="protected blob", nonempty=False)
        _require_bool(self.released, name="protected released")
        if not self.path and not self.blob:
            raise ValueError("protected reference requires path or blob")

    def as_dict(self) -> dict[str, Any]:
        self.verify()
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
        item = cls(
            ref_id=_require_string(raw.get("ref_id"), name="protected ref_id"),
            path=_require_string(
                raw.get("path", ""), name="protected path", nonempty=False
            ),
            blob=_require_string(
                raw.get("blob", ""), name="protected blob", nonempty=False
            ),
            released=_require_bool(
                raw.get("released", False), name="protected released"
            ),
        )
        item.verify()
        return item


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
        self.validate()
        return {**self.unsigned(), "state_digest": self.state_digest}

    def validate(self) -> None:
        if self.schema != CAMPAIGN_STATE_SCHEMA:
            raise ValueError("unsupported campaign state schema")
        _require_string(self.campaign_id, name="campaign_id")
        _require_string(self.claim_id, name="claim_id")
        _require_string(self.phase_id, name="phase_id")
        _require_nonnegative_int(self.cycle_index, name="cycle_index")
        _require_digest(self.manifest_digest, name="manifest_digest")
        _require_string(self.authority_ceiling, name="authority_ceiling")
        if len(self.observations) != len({key for key, _ in self.observations}):
            raise ValueError("duplicate campaign observation")
        for key, value in self.observations:
            _require_string(key, name="campaign observation key")
            _require_string(value, name="campaign observation value")
        _unique_strings(self.active_hard_obligations, name="active hard obligation")
        if len(self.protected_refs) != len({item.ref_id for item in self.protected_refs}):
            raise ValueError("duplicate protected reference")
        for item in self.protected_refs:
            if not isinstance(item, ProtectedReference):
                raise TypeError("protected_refs entries must be ProtectedReference")
            item.verify()
        for index, digest in enumerate(self.history_digests):
            _require_digest(digest, name=f"history_digests[{index}]")
        _require_digest(self.state_digest, name="state_digest")
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
        observation_rows = tuple(
            sorted(
                (
                    _require_string(key, name="campaign observation key"),
                    _require_string(value, name="campaign observation value"),
                )
                for key, value in observations.items()
            )
        )
        obligation_rows = _unique_strings(
            active_hard_obligations, name="active hard obligation"
        )
        protected_rows = _require_array(protected_refs, name="protected_refs")
        for item in protected_rows:
            if not isinstance(item, ProtectedReference):
                raise TypeError("protected_refs entries must be ProtectedReference")
            item.verify()
        history_rows = _string_array(history_digests, name="history_digests")
        for index, digest in enumerate(history_rows):
            _require_digest(digest, name=f"history_digests[{index}]")
        base = cls(
            campaign_id=_require_string(campaign_id, name="campaign_id"),
            claim_id=_require_string(claim_id, name="claim_id"),
            phase_id=_require_string(phase_id, name="phase_id"),
            cycle_index=_require_nonnegative_int(cycle_index, name="cycle_index"),
            manifest_digest=_require_digest(manifest_digest, name="manifest_digest"),
            observations=observation_rows,
            active_hard_obligations=obligation_rows,
            protected_refs=tuple(protected_rows),
            history_digests=history_rows,
            authority_ceiling=_require_string(
                authority_ceiling, name="authority_ceiling"
            ),
            state_digest="",
        )
        state = cls(**{**base.__dict__, "state_digest": content_digest(base.unsigned())})
        state.validate()
        return state

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "CampaignState":
        if not isinstance(raw, Mapping):
            raise TypeError("campaign state must be an object")
        if raw.get("schema") != CAMPAIGN_STATE_SCHEMA:
            raise ValueError("unsupported campaign state schema")
        _require_authority_false(raw)
        observations_raw = _require_array(raw.get("observations"), name="observations")
        observations: list[tuple[str, str]] = []
        for index, row in enumerate(observations_raw):
            pair = _require_array(row, name=f"observations[{index}]")
            if len(pair) != 2:
                raise ValueError(f"observations[{index}] must have two entries")
            observations.append(
                (
                    _require_string(pair[0], name=f"observations[{index}][0]"),
                    _require_string(pair[1], name=f"observations[{index}][1]"),
                )
            )
        state = cls(
            schema=CAMPAIGN_STATE_SCHEMA,
            campaign_id=_require_string(raw.get("campaign_id"), name="campaign_id"),
            claim_id=_require_string(raw.get("claim_id"), name="claim_id"),
            phase_id=_require_string(raw.get("phase_id"), name="phase_id"),
            cycle_index=_require_nonnegative_int(
                raw.get("cycle_index"), name="cycle_index"
            ),
            manifest_digest=_require_digest(
                raw.get("manifest_digest"), name="manifest_digest"
            ),
            observations=tuple(observations),
            active_hard_obligations=_unique_strings(
                raw.get("active_hard_obligations", ()),
                name="active hard obligation",
            ),
            protected_refs=tuple(
                ProtectedReference.from_dict(item)
                for item in _require_array(
                    raw.get("protected_refs", ()), name="protected_refs"
                )
            ),
            history_digests=_string_array(
                raw.get("history_digests", ()), name="history_digests"
            ),
            authority_ceiling=_require_string(
                raw.get("authority_ceiling"), name="authority_ceiling"
            ),
            state_digest=_require_digest(raw.get("state_digest"), name="state_digest"),
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
        self.validate()
        return {**self.unsigned(), "decision_digest": self.decision_digest}

    def validate(self) -> None:
        if self.schema != CAMPAIGN_DECISION_SCHEMA:
            raise ValueError("unsupported campaign decision schema")
        _require_string(self.phase_id, name="decision phase_id")
        if self.selected_kind is not None:
            _require_string(self.selected_kind, name="selected_kind")
        if self.selected_id is not None:
            _require_string(self.selected_id, name="selected_id")
        for name, value in (
            ("responsibility", self.responsibility),
            ("interface", self.interface),
            ("revision", self.revision),
            ("computation", self.computation),
            ("control", self.control),
        ):
            if not isinstance(value, Mapping):
                raise TypeError(f"{name} must be an object")
        if self.shadow_control is not None and not isinstance(self.shadow_control, Mapping):
            raise TypeError("shadow_control must be an object or null")
        _require_digest(self.decision_digest, name="decision_digest")
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
        self.validate()
        return {**self.unsigned(), "transition_digest": self.transition_digest}

    def validate(self) -> None:
        if self.schema != CAMPAIGN_TRANSITION_SCHEMA:
            raise ValueError("unsupported campaign transition schema")
        _require_string(self.campaign_id, name="transition campaign_id")
        _require_nonnegative_int(self.cycle_index, name="transition cycle_index")
        _require_digest(self.before_state_digest, name="before_state_digest")
        _require_digest(self.decision_digest, name="decision_digest")
        if self.capability_request_digest is not None:
            _require_digest(
                self.capability_request_digest, name="capability_request_digest"
            )
        if self.capability_result_digest is not None:
            _require_digest(
                self.capability_result_digest, name="capability_result_digest"
            )
        _require_digest(self.after_state_digest, name="after_state_digest")
        _require_string(self.terminal, name="transition terminal")
        _require_digest(self.transition_digest, name="transition_digest")
        if self.transition_digest != content_digest(self.unsigned()):
            raise ValueError("campaign transition digest mismatch")
