"""Fail-closed validation for the outcome-free P9/P10 protocol freezes."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping

P9_PROTOCOL = Path(
    "papers/orion-19-structured-epistemic-learning/protocol/"
    "P9_D1V1_3_ORDERED_MULTIPLICITY_FREEZE_2026-08-23.json"
)
P10_PROTOCOL = Path(
    "papers/orion-20-structured-problem-solving/protocol/P10_H1_H6_PROTOCOL_FREEZE_V1.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_protocol(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: object required")
    return payload


def _validate_required_inputs(root: Path, payload: Mapping[str, Any]) -> tuple[str, ...]:
    values = payload.get("required_inputs")
    if not isinstance(values, list) or not values:
        raise ValueError("required_inputs must be a non-empty list")
    missing: list[str] = []
    seen: set[str] = set()
    all_present = True
    for item in values:
        if not isinstance(item, dict):
            raise ValueError("required input must be an object")
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("required input id must be unique and non-empty")
        seen.add(identifier)
        if item.get("required") is not True:
            raise ValueError(f"{identifier}: every registered input is required")
        present = item.get("present")
        artifact = item.get("artifact")
        if not isinstance(present, bool):
            raise ValueError(f"{identifier}: present must be Boolean")
        if present:
            if not isinstance(artifact, str) or not artifact:
                raise ValueError(f"{identifier}: present input lacks an artifact")
            path = (root / artifact).resolve()
            try:
                path.relative_to(root.resolve())
            except ValueError as exc:
                raise ValueError(f"{identifier}: artifact escapes repository") from exc
            if not path.is_file():
                raise ValueError(f"{identifier}: artifact is missing")
            if "independent" in identifier or "custod" in identifier or "gold" in identifier:
                try:
                    attestation = json.loads(path.read_text(encoding="utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError(f"{identifier}: independent input must be machine-readable") from exc
                if not isinstance(attestation, dict) or attestation.get("self_authorizing") is not False:
                    raise ValueError(f"{identifier}: self-attestation cannot establish independence")
                raw = attestation.get("raw_inputs")
                if not isinstance(raw, list) or not raw:
                    raise ValueError(f"{identifier}: independent replay lacks raw inputs")
        else:
            all_present = False
            if artifact is not None:
                raise ValueError(f"{identifier}: absent input cannot name an authoritative artifact")
            missing.append(identifier)
    if bool(payload.get("execution_authorized")) != all_present:
        raise ValueError("execution_authorized must equal complete required-input availability")
    return tuple(missing)


def _validate_common(root: Path, payload: Mapping[str, Any]) -> tuple[str, ...]:
    if payload.get("lifecycle_state") != "PROSPECTIVE_FROZEN_NOT_EXECUTED":
        raise ValueError("protocol must remain prospective and not executed")
    if payload.get("positive_authority_granted") is not False:
        raise ValueError("an outcome-free protocol cannot grant positive authority")
    if payload.get("outcome_artifact") is not None:
        raise ValueError("this freeze cannot absorb an outcome artifact")
    if payload.get("missing_run_policy") is None:
        raise ValueError("missing-run policy is required")
    return _validate_required_inputs(root, payload)


def validate_p9(root: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    missing = _validate_common(root, payload)
    if payload.get("schema_version") != "orion.p9.d1v1_3-protocol-freeze.v1":
        raise ValueError("wrong P9 protocol schema")
    representation = payload.get("representation_contract")
    if not isinstance(representation, dict) or not (
        representation.get("preserves_order") is True
        and representation.get("preserves_multiplicity") is True
        and representation.get("round_trip_required") is True
    ):
        raise ValueError("P9 successor must preserve order and multiplicity round-trip")
    design = payload.get("design")
    if not isinstance(design, dict):
        raise ValueError("P9 design is missing")
    if design.get("minimum_families", 0) < 4 or design.get("minimum_total_independent_cases", 0) < 512:
        raise ValueError("P9 wide-family independent-unit floor was weakened")
    attacks = design.get("attack_families")
    if not isinstance(attacks, list) or len(set(attacks)) != 4:
        raise ValueError("P9 attack-family register is incomplete")
    opportunity = payload.get("opportunity_gate")
    if not isinstance(opportunity, dict) or opportunity.get("zero_opportunity_pass_prohibited") is not True:
        raise ValueError("P9 zero-opportunity PASS is forbidden")
    if not 0 < float(opportunity.get("minimum_changed_fraction_per_registered_cell", 0)) <= 1:
        raise ValueError("P9 attack-potency gate is unattainable or inert")
    gates = payload.get("confirmatory_gates")
    if not isinstance(gates, dict) or gates.get("all_gates_required") is not True:
        raise ValueError("P9 confirmatory gates must be conjunctive")
    multiplicity = payload.get("multiplicity")
    if not isinstance(multiplicity, dict) or not (
        multiplicity.get("method") == "HOLM_BONFERRONI"
        and multiplicity.get("worst_family_gate_is_noncompensatory") is True
    ):
        raise ValueError("P9 multiplicity or worst-family gate was weakened")
    predecessor = payload.get("historical_predecessor")
    if not isinstance(predecessor, dict) or predecessor.get("immutable") is not True:
        raise ValueError("P9 adverse predecessor must remain immutable")
    result = predecessor.get("result")
    if not isinstance(result, str) or not (root / result).is_file():
        raise ValueError("P9 adverse predecessor result is missing")
    return {"protocol": payload["protocol_id"], "missing_inputs": list(missing)}


def validate_p10(root: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    missing = _validate_common(root, payload)
    if payload.get("schema_version") != "orion.p10.h1-h6-protocol-freeze.v1":
        raise ValueError("wrong P10 protocol schema")
    subject = payload.get("subject")
    if not isinstance(subject, dict):
        raise ValueError("P10 subject binding is missing")
    commit = subject.get("base_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("P10 subject commit is invalid")
    try:
        subprocess.run(
            ["git", "-C", str(root), "cat-file", "-e", f"{commit}^{{commit}}"],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("P10 subject commit is stale or unavailable") from exc
    lock = subject.get("environment_lock")
    lock_digest = subject.get("environment_lock_sha256")
    if not isinstance(lock, str) or not isinstance(lock_digest, str):
        raise ValueError("P10 environment binding is incomplete")
    lock_path = Path(lock)
    if lock_path.is_absolute() or ".." in lock_path.parts:
        raise ValueError("P10 environment lock escapes the repository")
    try:
        frozen_lock = subprocess.run(
            ["git", "-C", str(root), "show", f"{commit}:{lock_path.as_posix()}"],
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("P10 environment lock is absent from the frozen subject commit") from exc
    if hashlib.sha256(frozen_lock).hexdigest() != lock_digest:
        raise ValueError("P10 environment lock binding disagrees with the frozen subject commit")
    design = payload.get("design")
    if not isinstance(design, dict) or not (
        design.get("minimum_domains", 0) >= 4
        and design.get("minimum_total_independent_tasks", 0) >= 400
        and design.get("minimum_known_method_controls", 0) >= 80
        and design.get("target_specific_refitting_allowed") is False
    ):
        raise ValueError("P10 wide independent-unit design was weakened")
    hypotheses = payload.get("hypotheses")
    if not isinstance(hypotheses, dict) or set(hypotheses) != {f"H{i}" for i in range(1, 7)}:
        raise ValueError("P10 must map exactly H1--H6")
    for claim_id, claim in hypotheses.items():
        if not isinstance(claim, dict) or claim.get("state") != "PROSPECTIVE_NOT_EXECUTED":
            raise ValueError(f"{claim_id}: outcome laundering is forbidden")
        if not isinstance(claim.get("gate"), str) or not claim["gate"]:
            raise ValueError(f"{claim_id}: nonempty gate required")
    multiplicity = payload.get("multiplicity")
    if not isinstance(multiplicity, dict) or not (
        multiplicity.get("method") == "HOLM_BONFERRONI"
        and set(multiplicity.get("family", [])) == {"H1", "H2", "H3", "H5", "H6"}
        and multiplicity.get("worst_domain_gates_are_noncompensatory") is True
    ):
        raise ValueError("P10 multiplicity or worst-domain gate was weakened")
    guards = payload.get("catastrophic_guards")
    if not isinstance(guards, dict) or any(value != 0 for value in guards.values()):
        raise ValueError("P10 catastrophic guards must remain zero-tolerance")
    return {"protocol": payload["protocol_id"], "missing_inputs": list(missing)}


def validate_repository(root: Path) -> dict[str, Any]:
    root = root.resolve()
    return {
        "P9": validate_p9(root, load_protocol(root / P9_PROTOCOL)),
        "P10": validate_p10(root, load_protocol(root / P10_PROTOCOL)),
    }
