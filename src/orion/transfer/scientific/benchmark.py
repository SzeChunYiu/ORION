"""Independent source/target family slots frozen before any transfer outcomes."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

FAMILY_IDS = (
    "debugging",
    "retrieval_stopping",
    "semantic_mapping",
    "protected_verification",
)

PAIR_KINDS = ("positive", "near_miss", "negative", "partial")

HOSTILE_FALSIFIER_KINDS = (
    "same_terms_incompatible_assumptions",
    "different_terms_same_mechanic",
    "omitted_precondition",
    "stale_source_evidence",
    "unavailable_tool",
    "corrupted_falsifier",
)

OUTCOME_KEYS = (
    "heldout_answer",
    "target_label",
    "net_transfer_gain",
    "negative_transfer_rate",
    "outcomes",
    "score",
)


@dataclass(frozen=True)
class SourceSlot:
    slot_id: str
    family_id: str
    transfer_object: dict[str, Any]


@dataclass(frozen=True)
class TargetSlot:
    slot_id: str
    family_id: str
    problem_signature: dict[str, Any]


@dataclass(frozen=True)
class TransferPair:
    pair_id: str
    source_slot_id: str
    target_slot_id: str
    source_family_id: str
    target_family_id: str
    pair_kind: str


@dataclass(frozen=True)
class HostileFalsifierSlot:
    kind: str
    source_slot_id: str
    target_slot_id: str
    expected_selector_admission: bool
    notes: str


@dataclass(frozen=True)
class BenchmarkDesign:
    family_ids: tuple[str, ...]
    freeze_status: str
    outcomes_accessed: bool
    source_slots: tuple[SourceSlot, ...]
    target_slots: tuple[TargetSlot, ...]
    pairs: tuple[TransferPair, ...]
    hostile_falsifiers: tuple[HostileFalsifierSlot, ...]
    raw_payload: dict[str, Any]


def _as_mapping(name: str, raw: Any) -> Mapping[str, Any]:
    if not isinstance(raw, Mapping):
        raise ValueError(f"{name} must be an object")
    return raw


def load_benchmark_design(path: Path) -> BenchmarkDesign:
    raw = json.loads(path.read_text(encoding="utf-8"))
    payload = _as_mapping("benchmark design", raw)
    blob = json.dumps(payload)
    for key in OUTCOME_KEYS:
        if key in payload:
            raise ValueError(f"benchmark design must not contain outcome field {key}")
        if key in blob and key in ("heldout_answer", "target_label", "net_transfer_gain"):
            raise ValueError(f"benchmark design must not mention {key}")
    family_ids = tuple(payload["family_ids"])
    source_slots = tuple(
        SourceSlot(
            slot_id=str(item["slot_id"]),
            family_id=str(item["family_id"]),
            transfer_object=dict(_as_mapping("transfer_object", item["transfer_object"])),
        )
        for item in payload["source_slots"]
    )
    target_slots = tuple(
        TargetSlot(
            slot_id=str(item["slot_id"]),
            family_id=str(item["family_id"]),
            problem_signature=dict(_as_mapping("problem_signature", item["problem_signature"])),
        )
        for item in payload["target_slots"]
    )
    pairs = tuple(
        TransferPair(
            pair_id=str(item["pair_id"]),
            source_slot_id=str(item["source_slot_id"]),
            target_slot_id=str(item["target_slot_id"]),
            source_family_id=str(item["source_family_id"]),
            target_family_id=str(item["target_family_id"]),
            pair_kind=str(item["pair_kind"]),
        )
        for item in payload["pairs"]
    )
    hostiles = tuple(
        HostileFalsifierSlot(
            kind=str(item["kind"]),
            source_slot_id=str(item["source_slot_id"]),
            target_slot_id=str(item["target_slot_id"]),
            expected_selector_admission=bool(item["expected_selector_admission"]),
            notes=str(item["notes"]),
        )
        for item in payload["hostile_falsifiers"]
    )
    if payload["outcomes_accessed"] is not False:
        raise ValueError("benchmark design must freeze pairs before outcomes")
    return BenchmarkDesign(
        family_ids=family_ids,
        freeze_status=str(payload["freeze_status"]),
        outcomes_accessed=False,
        source_slots=source_slots,
        target_slots=target_slots,
        pairs=pairs,
        hostile_falsifiers=hostiles,
        raw_payload=dict(payload),
    )
