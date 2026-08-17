"""Frozen scientific transfer-object schema and content-addressed payloads."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping

from orion.transfer.v2.canonical import content_digest, verify_digest

SCHEMA_VERSION = "ORION_SCIENTIFIC_TRANSFER_OBJECT_V1"

FORBIDDEN_OUTCOME_FIELDS = frozenset(
    {
        "heldout_answer",
        "heldout_labels",
        "target_label",
        "gold_output",
        "score",
        "net_transfer_gain",
        "negative_transfer_rate",
        "outcomes",
    }
)


def load_schema(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("transfer-object schema must be an object")
    return payload


def schema_digest(path: Path) -> str:
    return content_digest(load_schema(path))


def _walk_forbidden(value: Any) -> None:
    if isinstance(value, Mapping):
        forbidden = sorted(set(value) & FORBIDDEN_OUTCOME_FIELDS)
        if forbidden:
            raise ValueError(f"forbidden outcome field present: {forbidden}")
        for item in value.values():
            _walk_forbidden(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _walk_forbidden(item)


def _require_nonempty_strings(name: str, raw: Any) -> tuple[str, ...]:
    if not isinstance(raw, list) or not raw or not all(isinstance(v, str) and v for v in raw):
        raise ValueError(f"{name} must be a non-empty list of strings")
    if len(raw) != len(set(raw)):
        raise ValueError(f"{name} must not contain duplicates")
    return tuple(raw)


def _optional_strings(name: str, raw: Any) -> tuple[str, ...]:
    if not isinstance(raw, list) or not all(isinstance(v, str) and v for v in raw):
        raise ValueError(f"{name} must be a list of strings")
    if len(raw) != len(set(raw)):
        raise ValueError(f"{name} must not contain duplicates")
    return tuple(raw)


def _unit_interval(name: str, raw: Any) -> float:
    value = float(raw)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")
    return value


@dataclass(frozen=True)
class ProblemSignatureV3:
    signature_id: str
    family_id: str
    surface_domain: str
    hidden_state: str
    observability: str
    actions: tuple[str, ...]
    ground_truth_class: str
    dependence: float
    authority_risk: float
    nonstationarity: float
    reversibility: float

    def to_payload(self) -> dict[str, object]:
        return {
            "signature_id": self.signature_id,
            "family_id": self.family_id,
            "surface_domain": self.surface_domain,
            "hidden_state": self.hidden_state,
            "observability": self.observability,
            "actions": list(self.actions),
            "ground_truth_class": self.ground_truth_class,
            "dependence": self.dependence,
            "authority_risk": self.authority_risk,
            "nonstationarity": self.nonstationarity,
            "reversibility": self.reversibility,
        }


def problem_signature_from_payload(payload: Mapping[str, Any]) -> ProblemSignatureV3:
    required = {
        "signature_id",
        "family_id",
        "surface_domain",
        "hidden_state",
        "observability",
        "actions",
        "ground_truth_class",
        "dependence",
        "authority_risk",
        "nonstationarity",
        "reversibility",
    }
    if set(payload) != required:
        raise ValueError(f"problem signature fields mismatch: {sorted(set(payload) ^ required)}")
    return ProblemSignatureV3(
        signature_id=str(payload["signature_id"]),
        family_id=str(payload["family_id"]),
        surface_domain=str(payload["surface_domain"]),
        hidden_state=str(payload["hidden_state"]),
        observability=str(payload["observability"]),
        actions=_require_nonempty_strings("actions", payload["actions"]),
        ground_truth_class=str(payload["ground_truth_class"]),
        dependence=_unit_interval("dependence", payload["dependence"]),
        authority_risk=_unit_interval("authority_risk", payload["authority_risk"]),
        nonstationarity=_unit_interval("nonstationarity", payload["nonstationarity"]),
        reversibility=_unit_interval("reversibility", payload["reversibility"]),
    )


@dataclass(frozen=True)
class IOContract:
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    observables: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
            "observables": list(self.observables),
        }


@dataclass(frozen=True)
class AuthorityBoundaries:
    may_grant: tuple[str, ...]
    may_not_grant: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "may_grant": list(self.may_grant),
            "may_not_grant": list(self.may_not_grant),
        }


@dataclass(frozen=True)
class CostRequirements:
    context_budget: int
    tools_required: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "context_budget": self.context_budget,
            "tools_required": list(self.tools_required),
        }


@dataclass(frozen=True)
class ScientificTransferObject:
    schema_version: str
    object_id: str
    problem_signature: ProblemSignatureV3
    io_contract: IOContract
    obligations: tuple[str, ...]
    assumptions: tuple[str, ...]
    preconditions: tuple[str, ...]
    transformation_steps: tuple[str, ...]
    failure_modes: tuple[str, ...]
    verification_hooks: tuple[str, ...]
    falsifiers: tuple[str, ...]
    authority_boundaries: AuthorityBoundaries
    cost_requirements: CostRequirements
    evidence_level: str
    source_evidence_identities: tuple[str, ...]
    target_compatibility_tests: tuple[str, ...]
    forbidden_transfers: tuple[str, ...]
    content_hash: str

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "object_id": self.object_id,
            "problem_signature": self.problem_signature.to_payload(),
            "io_contract": self.io_contract.to_payload(),
            "obligations": list(self.obligations),
            "assumptions": list(self.assumptions),
            "preconditions": list(self.preconditions),
            "transformation_steps": list(self.transformation_steps),
            "failure_modes": list(self.failure_modes),
            "verification_hooks": list(self.verification_hooks),
            "falsifiers": list(self.falsifiers),
            "authority_boundaries": self.authority_boundaries.to_payload(),
            "cost_requirements": self.cost_requirements.to_payload(),
            "evidence_level": self.evidence_level,
            "source_evidence_identities": list(self.source_evidence_identities),
            "target_compatibility_tests": list(self.target_compatibility_tests),
            "forbidden_transfers": list(self.forbidden_transfers),
        }

    def to_payload(self) -> dict[str, object]:
        payload = self.unsigned_payload()
        payload["content_hash"] = self.content_hash
        return payload

    def verify(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported scientific transfer-object version")
        verify_digest(self.unsigned_payload(), self.content_hash)


def transfer_object_from_payload(payload: Mapping[str, Any]) -> ScientificTransferObject:
    _walk_forbidden(payload)
    required = {
        "schema_version",
        "object_id",
        "problem_signature",
        "io_contract",
        "obligations",
        "assumptions",
        "preconditions",
        "transformation_steps",
        "failure_modes",
        "verification_hooks",
        "falsifiers",
        "authority_boundaries",
        "cost_requirements",
        "evidence_level",
        "source_evidence_identities",
        "target_compatibility_tests",
        "forbidden_transfers",
        "content_hash",
    }
    extra = set(payload) - required
    if extra:
        raise ValueError(f"unexpected transfer-object fields: {sorted(extra)}")
    missing = required - set(payload)
    if missing:
        raise ValueError(f"missing transfer-object fields: {sorted(missing)}")
    signature_raw = payload["problem_signature"]
    io_raw = payload["io_contract"]
    authority_raw = payload["authority_boundaries"]
    cost_raw = payload["cost_requirements"]
    if not isinstance(signature_raw, Mapping):
        raise ValueError("problem_signature must be an object")
    if not isinstance(io_raw, Mapping) or set(io_raw) != {"inputs", "outputs", "observables"}:
        raise ValueError("io_contract fields mismatch")
    if not isinstance(authority_raw, Mapping) or set(authority_raw) != {"may_grant", "may_not_grant"}:
        raise ValueError("authority_boundaries fields mismatch")
    if not isinstance(cost_raw, Mapping) or set(cost_raw) != {"context_budget", "tools_required"}:
        raise ValueError("cost_requirements fields mismatch")
    if not authority_raw["may_not_grant"]:
        raise ValueError("authority_boundaries.may_not_grant must be non-empty")
    tools = cost_raw["tools_required"]
    if not isinstance(tools, list) or not all(isinstance(v, str) and v for v in tools):
        raise ValueError("tools_required must be a list of strings")
    obj = ScientificTransferObject(
        schema_version=str(payload["schema_version"]),
        object_id=str(payload["object_id"]),
        problem_signature=problem_signature_from_payload(signature_raw),
        io_contract=IOContract(
            inputs=_require_nonempty_strings("inputs", io_raw["inputs"]),
            outputs=_require_nonempty_strings("outputs", io_raw["outputs"]),
            observables=_require_nonempty_strings("observables", io_raw["observables"]),
        ),
        obligations=_require_nonempty_strings("obligations", payload["obligations"]),
        assumptions=_require_nonempty_strings("assumption", payload["assumptions"]),
        preconditions=_require_nonempty_strings("preconditions", payload["preconditions"]),
        transformation_steps=_optional_strings(
            "transformation_steps", payload["transformation_steps"]
        ),
        failure_modes=_require_nonempty_strings("failure_modes", payload["failure_modes"]),
        verification_hooks=_require_nonempty_strings(
            "verification_hooks", payload["verification_hooks"]
        ),
        falsifiers=_require_nonempty_strings("falsifiers", payload["falsifiers"]),
        authority_boundaries=AuthorityBoundaries(
            may_grant=_optional_strings("may_grant", authority_raw["may_grant"]),
            may_not_grant=_require_nonempty_strings("may_not_grant", authority_raw["may_not_grant"]),
        ),
        cost_requirements=CostRequirements(
            context_budget=int(cost_raw["context_budget"]),
            tools_required=tuple(tools),
        ),
        evidence_level=str(payload["evidence_level"]),
        source_evidence_identities=_require_nonempty_strings(
            "source_evidence_identities", payload["source_evidence_identities"]
        ),
        target_compatibility_tests=_require_nonempty_strings(
            "target_compatibility_tests", payload["target_compatibility_tests"]
        ),
        forbidden_transfers=_optional_strings(
            "forbidden_transfers", payload["forbidden_transfers"]
        ),
        content_hash=str(payload["content_hash"]),
    )
    obj.verify()
    return obj


def build_transfer_object(**fields: Any) -> ScientificTransferObject:
    payload = dict(fields)
    unsigned = {key: value for key, value in payload.items() if key != "content_hash"}
    payload["content_hash"] = content_digest(unsigned)
    return transfer_object_from_payload(payload)
