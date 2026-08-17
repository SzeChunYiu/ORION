"""Frozen #288 protocol: scientific intent / operational objective / optimizer-evaluator."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

PROTOCOL_ID = "orion.protected-goal-evolution.v1"
PROTOCOL_RELATIVE_PATH = Path("research") / "goal-evolution" / "PROTOCOL_V1.json"


class LayerKind(str, Enum):
    SCIENTIFIC_INTENT = "SCIENTIFIC_INTENT"
    OPERATIONAL_OBJECTIVE = "OPERATIONAL_OBJECTIVE"
    OPTIMIZER_EVALUATOR = "OPTIMIZER_EVALUATOR"


@dataclass(frozen=True)
class ProtocolLayer:
    kind: LayerKind
    candidate_writable: bool
    candidate_readable: bool
    overwrite: bool
    candidate_proposable: bool = False
    evaluator_candidate_writable: bool = False
    simultaneous_objective_evaluator_change: bool = False


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / PROTOCOL_RELATIVE_PATH).is_file():
            return parent
    raise FileNotFoundError(f"frozen protocol missing: {PROTOCOL_RELATIVE_PATH}")


def protocol_path() -> Path:
    return _repo_root() / PROTOCOL_RELATIVE_PATH


def canonical_protocol_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def protocol_hash(value: Mapping[str, Any] | None = None) -> str:
    payload = load_protocol() if value is None else value
    return hashlib.sha256(canonical_protocol_bytes(payload)).hexdigest()


def load_protocol() -> dict[str, Any]:
    return json.loads(protocol_path().read_text(encoding="utf-8"))


def protocol_layers(protocol: Mapping[str, Any] | None = None) -> tuple[ProtocolLayer, ...]:
    raw = (protocol or load_protocol())["layers"]
    intent = raw["scientific_intent"]
    objective = raw["operational_objective"]
    machinery = raw["optimizer_evaluator"]
    return (
        ProtocolLayer(
            kind=LayerKind.SCIENTIFIC_INTENT,
            candidate_writable=bool(intent["candidate_writable"]),
            candidate_readable=bool(intent["candidate_readable"]),
            overwrite=bool(intent["overwrite"]),
        ),
        ProtocolLayer(
            kind=LayerKind.OPERATIONAL_OBJECTIVE,
            candidate_writable=bool(objective["candidate_writable"]),
            candidate_readable=bool(objective["candidate_readable"]),
            overwrite=bool(objective["overwrite"]),
            candidate_proposable=bool(objective["candidate_proposable"]),
        ),
        ProtocolLayer(
            kind=LayerKind.OPTIMIZER_EVALUATOR,
            candidate_writable=bool(machinery["candidate_writable"]),
            candidate_readable=bool(machinery["candidate_readable"]),
            overwrite=bool(machinery["overwrite"]),
            evaluator_candidate_writable=bool(machinery["evaluator_candidate_writable"]),
            simultaneous_objective_evaluator_change=bool(
                machinery["simultaneous_objective_evaluator_change"]
            ),
        ),
    )
