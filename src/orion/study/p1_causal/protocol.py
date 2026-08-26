"""Load and hash the frozen P1.causal-responsibility.v2 protocol."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from orion.kernel.store import canonical_bytes

PROTOCOL_ID = "P1.causal-responsibility.v2"
V1_PROTOCOL_ID = "P1.hidden-formulation.v1"
V1_PROTOCOL_VERSION = "P1.hidden-formulation.v1.1"

_REPO_ROOT = Path(__file__).resolve().parents[4]
PROTOCOL_PATH = (
    _REPO_ROOT
    / "research"
    / "revival"
    / "p1"
    / "protocol"
    / "P1.causal-responsibility.v2.json"
)
V1_PROTOCOL_PATH = (
    _REPO_ROOT
    / "papers"
    / "orion-11-recursive-epistemic-reconstruction"
    / "protocol"
    / "PROTOCOL_V1.json"
)


class ProtocolError(RuntimeError):
    """The V2 protocol is not in a state that may drive a run."""


@lru_cache(maxsize=1)
def load_protocol(path: Path = PROTOCOL_PATH) -> dict:
    payload = json.loads(path.read_text())
    if payload.get("protocol_id") != PROTOCOL_ID:
        raise ProtocolError(
            f"expected {PROTOCOL_ID}, found {payload.get('protocol_id')!r}"
        )
    if payload.get("outcome_accessed") is not False:
        raise ProtocolError("outcome_accessed must remain false until execution freeze")
    if payload.get("v1_protocol_mutated") is not False:
        raise ProtocolError("this protocol must not claim to mutate V1")
    return payload


def protocol_sha256(path: Path = PROTOCOL_PATH) -> str:
    return hashlib.sha256(canonical_bytes(load_protocol(path))).hexdigest()


def assert_v1_protocol_untouched() -> str:
    """Read-only check: V1 protocol identity is still the frozen version."""

    payload = json.loads(V1_PROTOCOL_PATH.read_text())
    if payload.get("protocol_version") != V1_PROTOCOL_VERSION:
        raise ProtocolError(
            "V1 protocol_version moved; refuse to treat it as the frozen object"
        )
    if payload.get("protocol_id") != V1_PROTOCOL_ID:
        raise ProtocolError("V1 protocol_id moved")
    return hashlib.sha256(V1_PROTOCOL_PATH.read_bytes()).hexdigest()
