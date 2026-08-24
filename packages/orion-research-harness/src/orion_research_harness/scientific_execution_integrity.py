"""Fail-closed P15 scientific-execution-integrity contract.

Execution evidence, scientific validity and claim authority are deliberately
separate caller-declared inputs. The evaluator prefixes science dispositions with
``DECLARED_`` because it does not verify the referenced contracts and never
creates scientific or independent authority itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class ScientificDisposition(str, Enum):
    DECLARED_AUTHORIZED_SCIENCE = "DECLARED_AUTHORIZED_SCIENCE"
    DECLARED_VALID_BUT_NOT_AUTHORIZED = "DECLARED_VALID_BUT_NOT_AUTHORIZED"
    DECLARED_INVALID_SCIENCE = "DECLARED_INVALID_SCIENCE"
    EXECUTION_INVALID = "EXECUTION_INVALID"
    CANNOT_CHECK = "CANNOT_CHECK"


_EXECUTION_FIELDS = (
    "spawn_ok",
    "host_ok",
    "timeout",
    "exit_zero",
    "output_present",
    "output_complete",
    "reaped",
    "finalized_after_reap",
    "cleanup_complete",
    "retry_accounting_valid",
    "invocation_match",
    "input_digest_match",
    "result_digest_match",
    "occurrence_unique",
    "fresh",
    "coverage_complete",
)


def _bool(raw: Mapping[str, Any], name: str) -> bool:
    value = raw.get(name)
    if type(value) is not bool:
        raise TypeError(f"{name} must be a boolean")
    return value


@dataclass(frozen=True)
class ScientificExecutionRecord:
    record_id: str
    spawn_ok: bool
    host_ok: bool
    timeout: bool
    exit_zero: bool
    output_present: bool
    output_complete: bool
    reaped: bool
    finalized_after_reap: bool
    cleanup_complete: bool
    retry_accounting_valid: bool
    invocation_match: bool
    input_digest_match: bool
    result_digest_match: bool
    occurrence_unique: bool
    fresh: bool
    coverage_complete: bool
    scientific_contract_available: bool
    scientific_contract_valid: bool
    claim_authority_available: bool
    claim_authority: bool

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ScientificExecutionRecord":
        if not isinstance(raw, Mapping):
            raise TypeError("execution record must be an object")
        expected = {"record_id", *_EXECUTION_FIELDS, "scientific_contract_available",
                    "scientific_contract_valid", "claim_authority_available", "claim_authority"}
        if set(raw) != expected:
            raise ValueError(
                f"execution record fields must be exact; missing={sorted(expected - set(raw))!r}; "
                f"extra={sorted(set(raw) - expected)!r}"
            )
        record_id = raw["record_id"]
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("record_id must be a non-empty string")
        values = {name: _bool(raw, name) for name in expected - {"record_id"}}
        return cls(record_id=record_id, **values)

    def execution_integrity(self) -> bool:
        return all(
            (
                self.spawn_ok,
                self.host_ok,
                not self.timeout,
                self.exit_zero,
                self.output_present,
                self.output_complete,
                self.reaped,
                self.finalized_after_reap,
                self.cleanup_complete,
                self.retry_accounting_valid,
                self.invocation_match,
                self.input_digest_match,
                self.result_digest_match,
                self.occurrence_unique,
                self.fresh,
                self.coverage_complete,
            )
        )

    def disposition(self) -> ScientificDisposition:
        if not self.execution_integrity():
            return ScientificDisposition.EXECUTION_INVALID
        if not self.scientific_contract_available:
            return ScientificDisposition.CANNOT_CHECK
        if not self.scientific_contract_valid:
            return ScientificDisposition.DECLARED_INVALID_SCIENCE
        if not self.claim_authority_available:
            return ScientificDisposition.CANNOT_CHECK
        if not self.claim_authority:
            return ScientificDisposition.DECLARED_VALID_BUT_NOT_AUTHORIZED
        return ScientificDisposition.DECLARED_AUTHORIZED_SCIENCE

    def as_dict(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in ("record_id", *_EXECUTION_FIELDS,
            "scientific_contract_available", "scientific_contract_valid",
            "claim_authority_available", "claim_authority")}


__all__ = ["ScientificDisposition", "ScientificExecutionRecord"]
