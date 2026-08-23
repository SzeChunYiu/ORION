"""Candidate-visible R7 boundary with byte-identical arm payloads.

Gold, role, source/query identity and evaluator state do not exist on this
object.  Probe observations are available only through metered opaque handles.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping, Sequence


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


@dataclass(frozen=True)
class EvidenceObject:
    handle: str
    text: str

    def as_dict(self) -> dict[str, str]:
        return {"handle": self.handle, "text": self.text}


@dataclass(frozen=True)
class CandidateVisibleEpisode:
    opaque_episode_handle: str
    dossier: str
    source_evidence: tuple[EvidenceObject, ...]
    probe_handles: tuple[str, ...]
    action_handles: tuple[str, ...]

    def payload(self) -> dict[str, object]:
        return {
            "opaque_episode_handle": self.opaque_episode_handle,
            "dossier": self.dossier,
            "source_evidence": [item.as_dict() for item in self.source_evidence],
            "probe_handles": list(self.probe_handles),
            "action_handles": list(self.action_handles),
        }

    def to_bytes(self) -> bytes:
        return _canonical(self.payload())

    def digest(self) -> str:
        return "sha256:" + hashlib.sha256(self.to_bytes()).hexdigest()


class ProbeBudgetExceeded(RuntimeError):
    pass


class UnknownProbeHandle(KeyError):
    pass


class GuardedProbeBank:
    """Evaluator-owned probe map; candidates see only opaque handles."""

    def __init__(self, observations: Mapping[str, str], *, limit: int) -> None:
        if limit < 0:
            raise ValueError("probe limit must be non-negative")
        if any(not isinstance(key, str) or not key for key in observations):
            raise ValueError("probe handles must be non-empty strings")
        self.__observations = dict(observations)
        self.limit = int(limit)
        self._transcript: list[dict[str, object]] = []

    @property
    def handles(self) -> tuple[str, ...]:
        return tuple(sorted(self.__observations))

    @property
    def transcript(self) -> tuple[dict[str, object], ...]:
        return tuple(dict(row) for row in self._transcript)

    def request(self, handle: str) -> str:
        if handle not in self.__observations:
            self._transcript.append(
                {"sequence": len(self._transcript), "handle": handle, "status": "UNKNOWN"}
            )
            raise UnknownProbeHandle(handle)
        if sum(row["status"] == "REVEALED" for row in self._transcript) >= self.limit:
            self._transcript.append(
                {"sequence": len(self._transcript), "handle": handle, "status": "BUDGET_EXCEEDED"}
            )
            raise ProbeBudgetExceeded(handle)
        value = self.__observations[handle]
        self._transcript.append(
            {
                "sequence": len(self._transcript),
                "handle": handle,
                "status": "REVEALED",
                "observation": value,
            }
        )
        return value


def arm_visibility_receipt(
    episode: CandidateVisibleEpisode, arm_ids: Sequence[str]
) -> dict[str, object]:
    if not arm_ids or len(set(arm_ids)) != len(arm_ids):
        raise ValueError("arm ids must be a non-empty unique sequence")
    payload = episode.to_bytes()
    digest = episode.digest()
    return {
        "payload_bytes": len(payload),
        "payload_digest_by_arm": {arm: digest for arm in sorted(arm_ids)},
        "all_arm_payload_digests_equal": True,
    }


def assert_arm_visibility_equal(receipt: Mapping[str, object]) -> None:
    by_arm = receipt.get("payload_digest_by_arm")
    if not isinstance(by_arm, Mapping) or not by_arm:
        raise ValueError("missing per-arm payload digests")
    values = {str(value) for value in by_arm.values()}
    if len(values) != 1:
        raise ValueError("candidate-visible payload differs across arms")
    if receipt.get("all_arm_payload_digests_equal") is not True:
        raise ValueError("visibility equality was not attested")

