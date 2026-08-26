"""Controlled finite-world P13B authenticated certificate successor."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import platform
from pathlib import Path
from typing import Any, Mapping

TRUSTED_ISSUER = "ORION_P13B_TRUST_ROOT_V1"
CURRENT_EPOCH = 2
REUSE_COST = 1
REOPEN_COST = 6

WORLDS = ("OMITTED_SUPPORT", "OVERBROAD_SUPPORT", "FORGED_SUPPORT", "STALE_EPOCH")
SUPPORTED = "P13B_AUTHENTICATED_CERTIFICATE_SAFETY_COST_SUPPORTED_FINITE_WORLD"
NOT_SUPPORTED = "P13B_AUTHENTICATED_CERTIFICATE_SAFETY_COST_GATE_NOT_MET"

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/orion-23-responsibility-carrying-state"
PROTOCOL = PAPER / "P13B_AUTHENTICATED_CERTIFICATE_CORRUPTION_PROTOCOL_V1.md"
GOLD_SPEC = PAPER / "P13B_GOLD_SUPPORT_SPEC_V1.json"


def canonical_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _digest_fields(certificate: Mapping[str, Any]) -> str:
    fields = {key: value for key, value in certificate.items() if key != "digest_sha256"}
    compact = json.dumps(fields, sort_keys=True, separators=(",", ":")).encode()
    return sha256(compact).hexdigest()


def load_gold_spec() -> dict[str, Any]:
    return json.loads(GOLD_SPEC.read_text(encoding="utf-8"))


def gold_support(spec: Mapping[str, Any], state_id: str, task_id: str) -> bool:
    available = set(spec["state_forms"][state_id])
    required = set(spec["task_requirements"][task_id])
    return required.issubset(available)


def valid_certificate(spec: Mapping[str, Any], state_id: str) -> dict[str, Any]:
    tasks = tuple(sorted(spec["task_requirements"]))
    certificate: dict[str, Any] = {
        "issuer": TRUSTED_ISSUER,
        "subject_state_id": state_id,
        "epoch": CURRENT_EPOCH,
        "declared_support": {
            task: gold_support(spec, state_id, task) for task in tasks
        },
        "state_variable_witness": list(spec["state_forms"][state_id]),
    }
    certificate["digest_sha256"] = _digest_fields(certificate)
    return certificate


def validate_certificate(
    certificate: Mapping[str, Any], spec: Mapping[str, Any], state_id: str
) -> bool:
    tasks = set(spec["task_requirements"])
    declared = certificate.get("declared_support")
    witness = certificate.get("state_variable_witness")
    if certificate.get("issuer") != TRUSTED_ISSUER:
        return False
    if certificate.get("subject_state_id") != state_id:
        return False
    if certificate.get("epoch") != CURRENT_EPOCH:
        return False
    if not isinstance(declared, dict) or set(declared) != tasks:
        return False
    if not isinstance(witness, list) or set(witness) != set(spec["state_forms"][state_id]):
        return False
    expected = {
        task: set(spec["task_requirements"][task]).issubset(set(witness))
        for task in tasks
    }
    if declared != expected:
        return False
    digest = certificate.get("digest_sha256")
    return isinstance(digest, str) and digest == _digest_fields(certificate)


def corrupt_certificate(
    valid: Mapping[str, Any], world: str, spec: Mapping[str, Any], state_id: str
) -> dict[str, Any]:
    certificate = deepcopy(valid)
    tasks = tuple(sorted(spec["task_requirements"]))
    if world == "OMITTED_SUPPORT":
        target = next(task for task in tasks if certificate["declared_support"][task])
        certificate["declared_support"][target] = False
        return certificate
    if world == "OVERBROAD_SUPPORT":
        target = next(
            (task for task in tasks if not certificate["declared_support"][task]),
            None,
        )
        if target is None:
            certificate["declared_support"]["OUT_OF_SCOPE"] = True
        else:
            certificate["declared_support"][target] = True
        return certificate
    if world == "FORGED_SUPPORT":
        target = next(
            (task for task in tasks if not certificate["declared_support"][task]),
            None,
        )
        certificate["issuer"] = "UNTRUSTED_FORGER"
        if target is not None:
            certificate["declared_support"][target] = True
        certificate["digest_sha256"] = _digest_fields(certificate)
        return certificate
    if world == "STALE_EPOCH":
        certificate["epoch"] = 1
        certificate["state_variable_witness"] = list(spec["state_forms"]["Z3"])
        certificate["declared_support"] = {
            task: gold_support(spec, "Z3", task) for task in tasks
        }
        certificate["digest_sha256"] = _digest_fields(certificate)
        return certificate
    raise ValueError(f"unknown P13B corruption world: {world}")


def _score_panel(spec: Mapping[str, Any], certificates: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    totals = {
        "AUTHENTICATED_RCS": {"unsafe_reuse": 0, "correct": 0, "cost": 0},
        "UNVERIFIED_RCS": {"unsafe_reuse": 0, "correct": 0, "cost": 0},
        "ALWAYS_RAW": {"unsafe_reuse": 0, "correct": 0, "cost": 0},
    }
    for state_id in sorted(spec["state_forms"]):
        certificate = certificates[state_id]
        valid = validate_certificate(certificate, spec, state_id)
        for task_id in sorted(spec["task_requirements"]):
            gold = gold_support(spec, state_id, task_id)
            declared = bool(certificate.get("declared_support", {}).get(task_id, False))
            actions = {
                "AUTHENTICATED_RCS": "REUSE" if valid and declared else "REOPEN",
                "UNVERIFIED_RCS": "REUSE" if declared else "REOPEN",
                "ALWAYS_RAW": "REOPEN",
            }
            for arm_id, action in actions.items():
                unsafe = action == "REUSE" and not gold
                correct = action == "REOPEN" or (action == "REUSE" and gold)
                totals[arm_id]["unsafe_reuse"] += int(unsafe)
                totals[arm_id]["correct"] += int(correct)
                totals[arm_id]["cost"] += REUSE_COST if action == "REUSE" else REOPEN_COST
            rows.append(
                {
                    "state_id": state_id,
                    "task_id": task_id,
                    "gold_supported": gold,
                    "certificate_valid": valid,
                    "declared_supported": declared,
                    "actions": actions,
                }
            )
    denominator = len(rows)
    return {
        "rows": rows,
        "denominator": denominator,
        "arms": {
            arm_id: {
                **counts,
                "unsafe_reuse_rate": counts["unsafe_reuse"] / denominator,
                "verified_correct_rate": counts["correct"] / denominator,
                "mean_cost": counts["cost"] / denominator,
            }
            for arm_id, counts in totals.items()
        },
    }


def build_core() -> dict[str, Any]:
    spec = load_gold_spec()
    valid = {
        state_id: valid_certificate(spec, state_id) for state_id in sorted(spec["state_forms"])
    }
    valid_panel = _score_panel(spec, valid)
    worlds: dict[str, Any] = {}
    for world in WORLDS:
        corrupt = {
            state_id: corrupt_certificate(certificate, world, spec, state_id)
            for state_id, certificate in valid.items()
        }
        opportunity_rows = 0
        rejected_certificates = 0
        for state_id in sorted(valid):
            changed_validity = validate_certificate(valid[state_id], spec, state_id) != validate_certificate(corrupt[state_id], spec, state_id)
            rejected_certificates += int(not validate_certificate(corrupt[state_id], spec, state_id))
            for task_id in sorted(spec["task_requirements"]):
                before = bool(valid[state_id]["declared_support"].get(task_id, False))
                after = bool(corrupt[state_id].get("declared_support", {}).get(task_id, False))
                opportunity_rows += int(changed_validity or before != after)
        panel = _score_panel(spec, corrupt)
        worlds[world] = {
            "mutation_opportunities": opportunity_rows,
            "rejected_certificates": rejected_certificates,
            "certificate_count": len(corrupt),
            "panel": panel,
        }
    return {
        "schema": "ORION.P13B.AuthenticatedCertificateCorruption.Core.v1",
        "paper_id": "P13",
        "claim_id": "P13B_AUTHENTICATED_CERTIFICATE_SAFETY_COST",
        "authority_boundary": "controlled_finite_world_not_external_validation",
        "protocol": str(PROTOCOL.relative_to(REPO_ROOT)),
        "protocol_sha256": file_sha256(PROTOCOL),
        "gold_spec": str(GOLD_SPEC.relative_to(REPO_ROOT)),
        "gold_spec_sha256": file_sha256(GOLD_SPEC),
        "gold_definition": "task_requirements_subset_of_state_variables",
        "gold_reads_certificate": False,
        "independent_unit": "complete_registered_state_task_panel",
        "n_state_forms": len(spec["state_forms"]),
        "n_tasks": len(spec["task_requirements"]),
        "panel_denominator": len(spec["state_forms"]) * len(spec["task_requirements"]),
        "subject_identity": {
            "trusted_issuer": TRUSTED_ISSUER,
            "current_epoch": CURRENT_EPOCH,
            "certificate_digest": "canonical_json_sha256_v1",
            "validator": "issuer_subject_epoch_mapping_witness_digest_v1",
        },
        "environment": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
        },
        "valid_panel": valid_panel,
        "corruption_worlds": worlds,
    }


def adjudicate(core: Mapping[str, Any], *, byte_identical_replay: bool) -> dict[str, Any]:
    candidate = deepcopy(core)
    worlds = candidate.get("corruption_worlds", {})
    world_register_complete = set(worlds) == set(WORLDS)
    opportunities = world_register_complete and all(
        worlds[world].get("mutation_opportunities", 0) > 0 for world in WORLDS
    )
    rejected = world_register_complete and all(
        worlds[world].get("rejected_certificates")
        == worlds[world].get("certificate_count")
        and worlds[world].get("certificate_count", 0) > 0
        for world in WORLDS
    )
    authenticated_zero = world_register_complete and all(
        worlds[world]["panel"]["arms"]["AUTHENTICATED_RCS"]["unsafe_reuse"] == 0
        for world in WORLDS
    )
    unverified_live = world_register_complete and all(
        worlds[world]["panel"]["arms"]["UNVERIFIED_RCS"]["unsafe_reuse"] > 0
        for world in ("OVERBROAD_SUPPORT", "FORGED_SUPPORT", "STALE_EPOCH")
    )
    valid = candidate.get("valid_panel", {})
    valid_rows = valid.get("rows", [])
    valid_acceptance = bool(valid_rows) and all(
        row.get("certificate_valid") is True
        and row["actions"]["AUTHENTICATED_RCS"]
        == ("REUSE" if row.get("gold_supported") else "REOPEN")
        for row in valid_rows
    )
    arms = valid.get("arms", {})
    authenticated = arms.get("AUTHENTICATED_RCS", {})
    always_raw = arms.get("ALWAYS_RAW", {})
    correct = authenticated.get("verified_correct_rate") == 1.0
    raw_cost = always_raw.get("mean_cost", 0.0)
    cost_ratio = authenticated.get("mean_cost", float("inf")) / raw_cost if raw_cost else float("inf")
    cost_gate = cost_ratio <= 0.70
    gold_independent = candidate.get("gold_reads_certificate") is False
    gates = {
        "every_corruption_world_has_nonzero_opportunities": opportunities,
        "every_mutated_certificate_rejected": rejected,
        "authenticated_zero_unsafe_reuse_each_world": authenticated_zero,
        "unverified_corruptions_have_live_violations": unverified_live,
        "valid_certificates_match_gold_supported_reuse": valid_acceptance,
        "valid_panel_verified_correct_rate_eq_1": correct,
        "valid_panel_authenticated_cost_le_0_70_always_raw": cost_gate,
        "gold_scorer_does_not_read_certificate": gold_independent,
        "byte_identical_replay": byte_identical_replay,
    }
    terminal = SUPPORTED if all(gates.values()) else NOT_SUPPORTED
    return {
        "schema": "ORION.P13B.AuthenticatedCertificateCorruption.Result.v1",
        "core": candidate,
        "summary": {
            "panel_denominator": candidate.get("panel_denominator"),
            "mutation_opportunities_by_world": {
                world: worlds[world]["mutation_opportunities"] for world in WORLDS
            } if world_register_complete else {},
            "authenticated_unsafe_reuse_by_world": {
                world: worlds[world]["panel"]["arms"]["AUTHENTICATED_RCS"]["unsafe_reuse"] for world in WORLDS
            } if world_register_complete else {},
            "unverified_unsafe_reuse_by_world": {
                world: worlds[world]["panel"]["arms"]["UNVERIFIED_RCS"]["unsafe_reuse"] for world in WORLDS
            } if world_register_complete else {},
            "valid_panel_authenticated_cost_ratio_vs_always_raw": cost_ratio,
        },
        "gates": gates,
        "terminal": terminal,
    }


__all__ = [
    "NOT_SUPPORTED",
    "SUPPORTED",
    "WORLDS",
    "adjudicate",
    "build_core",
    "canonical_text",
    "corrupt_certificate",
    "gold_support",
    "load_gold_spec",
    "valid_certificate",
    "validate_certificate",
]
