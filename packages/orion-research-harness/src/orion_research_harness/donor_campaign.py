from __future__ import annotations

from typing import Any, Mapping

from orion import Problem
from orion.donors import DonorExecutionMode
from orion.engine.navigation import PaperParityNavigator


def _problem(problem_data: Mapping[str, Any]) -> Problem:
    return Problem(
        problem_id=str(problem_data["problem_id"]),
        question=str(problem_data["question"]),
        scope=str(problem_data.get("scope", "")),
        initial_domain_ids=tuple(str(x) for x in problem_data.get("initial_domain_ids", ())),
        success_criteria=tuple(str(x) for x in problem_data.get("success_criteria", ())),
    )


def build_donor_campaign_manifest(
    problem_data: Mapping[str, Any],
    *,
    navigation_profile: str | None = None,
) -> dict[str, Any]:
    profile = navigation_profile or str(problem_data.get("navigation_profile", "orion"))
    if profile not in {"orion", "orion-q"}:
        raise ValueError("navigation_profile must be 'orion' or 'orion-q'")
    problem = _problem(problem_data)
    navigator = PaperParityNavigator.orion_q() if profile == "orion-q" else PaperParityNavigator.normal()
    plan = navigator.plan(problem)
    registry = navigator.donor_registry

    applicable_ids: list[str] = []
    fibre_bindings: dict[str, list[str]] = {}
    for route in plan.fibre_routes:
        for capability_id in route.executable_donor_ids:
            capability = registry.get(capability_id)
            if capability.execution_mode is not DonorExecutionMode.EXTERNAL_HOST:
                continue
            fibre_bindings.setdefault(capability_id, []).append(route.mechanic_id)
            if capability_id not in applicable_ids:
                applicable_ids.append(capability_id)

    initial_observations = {
        f"DONOR_STATUS:{capability_id}": "PENDING" for capability_id in applicable_ids
    }
    phases: dict[str, Any] = {}
    capabilities: dict[str, Any] = {}
    for index, capability_id in enumerate(applicable_ids):
        donor = registry.get(capability_id)
        phase_id = f"DONOR_{index:03d}"
        next_phase = f"DONOR_{index + 1:03d}" if index + 1 < len(applicable_ids) else "DONOR_COMPLETE"
        status_key = f"DONOR_STATUS:{capability_id}"
        summary_key = f"DONOR_SUMMARY:{capability_id}"
        verifier_key = f"DONOR_VERIFIER:{capability_id}"
        resource_key = f"DONOR_RESOURCE:{capability_id}"
        capability_key = f"execute:{capability_id}"
        action_id = f"COMPUTE:{capability_id}"
        hypothesis_id = f"RESP:DONOR_UNEXECUTED:{capability_id}"
        revision_id = f"REV:ABSORB_DONOR:{capability_id}"
        obligation_id = f"OBLIGATION:EXECUTE_DONOR:{capability_id}"
        capabilities[capability_key] = {
            "host_capability": "DONOR_EXECUTE",
            "payload": {
                "capability": donor.as_dict(),
                "problem": {
                    "problem_id": problem.problem_id,
                    "question": problem.question,
                    "scope": problem.scope,
                    "initial_domain_ids": list(problem.initial_domain_ids),
                    "success_criteria": list(problem.success_criteria),
                },
                "navigation_plan_digest": plan.plan_digest,
                "atomization_digest": plan.atomization_digest,
                "donor_registry_digest": plan.donor_registry_digest,
                "fibre_ids": sorted(set(fibre_bindings[capability_id])),
                "instruction": (
                    "Execute the registered strongest-incumbent donor capability faithfully. "
                    "Return candidate_summary, verifier_status, resource_summary and status. "
                    "Do not claim ORION novelty or scientific authority; preserve donor failure/abstention."
                ),
            },
            "result_contract": {
                "kind": "DIRECT_JSON",
                "required_payload_values": [
                    {"path": ["capability_id"], "equals": capability_id},
                ],
                "evidence_rules": [
                    {"evidence_key": status_key, "path": ["status"], "transform": "STRING"},
                    {"evidence_key": summary_key, "path": ["candidate_summary"], "transform": "STRING"},
                    {"evidence_key": verifier_key, "path": ["verifier_status"], "transform": "STRING"},
                    {"evidence_key": resource_key, "path": ["resource_summary"], "transform": "STRING"},
                ],
            },
            "next_phase": next_phase,
        }
        phases[phase_id] = {
            "active_hard_obligations": [obligation_id],
            "responsibility_hypotheses": [
                {
                    "hypothesis_id": hypothesis_id,
                    "expected_observations": {status_key: ["PENDING"]},
                    "support_evidence_ids": [f"donor-registry:{capability_id}"],
                }
            ],
            "interface_checks": [
                {
                    "check_id": f"IFACE:DONOR_REGISTERED:{capability_id}",
                    "scope": "DONOR_CAPABILITY_CONTRACT",
                    "state": "PASS",
                    "required": True,
                    "evidence_ids": [f"donor-registry:{plan.donor_registry_digest}"],
                }
            ],
            "revision_mechanics": [
                {
                    "mechanic_id": revision_id,
                    "kind": "ABSORB_DONOR",
                    "read_coordinates": ["DONOR_REGISTRY", "M.ACTIVE_FIBRES"],
                    "write_coordinates": ["DONOR_BASELINE_CONTEXT"],
                    "preconditions": ["DONOR_EXECUTED"],
                    "preservation_obligations": [
                        "PRESERVE:SCIENTIFIC_TARGET",
                        "PRESERVE:AUTHORITY_BOUNDARY",
                    ],
                    "cost": 1.0,
                }
            ],
            "mechanic_obligation_states": {"DONOR_EXECUTED": "UNRESOLVED"},
            "computation_actions": [
                {
                    "action_id": action_id,
                    "kind": "EXECUTE_STRONGEST_DONOR",
                    "expected_decision_value": 1.0,
                    "cost": 1.0,
                    "discharges_obligations": [obligation_id],
                }
            ],
            "responsibility_bindings": {hypothesis_id: [revision_id]},
            "selected_capabilities": {action_id: capability_key},
        }

    if not applicable_ids:
        initial_phase = "DONOR_COMPLETE"
    else:
        initial_phase = "DONOR_000"
    phases["DONOR_COMPLETE"] = {
        "terminal": True,
        "terminal_name": "DONOR_BASELINE_SATURATED",
        "active_hard_obligations": [],
    }
    return {
        "schema": "ORION.ResearchCampaignManifest.v1",
        "campaign_id": f"donor-saturation:{profile}:{problem.problem_id}",
        "claim_id": f"donor-baseline:{problem.problem_id}",
        "description": "Exhaust strongest applicable external donor capabilities before ORION-only residual claims.",
        "authority_ceiling": "NON_AUTHORIZING_DONOR_BASELINE",
        "navigation_profile": profile,
        "navigation_plan_digest": plan.plan_digest,
        "atomization_digest": plan.atomization_digest,
        "donor_registry_id": plan.donor_registry_id,
        "donor_registry_digest": plan.donor_registry_digest,
        "deferred_donor_obligation_ids": list(plan.deferred_donor_obligation_ids),
        "initial_phase": initial_phase,
        "initial_observations": initial_observations,
        "protected_refs": [],
        "capabilities": capabilities,
        "phases": phases,
    }


__all__ = ["build_donor_campaign_manifest"]
