from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from .full_registry import normal_orion_donor_registry, orion_q_donor_registry
from .registry import DonorRegistry


@dataclass(frozen=True)
class DonorCompositionRoute:
    route_id: str
    purpose: str
    stage_ids: tuple[str, ...]
    required_capability_ids: tuple[str, ...]
    optional_capability_ids: tuple[str, ...] = ()
    hard_obligations: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "route_id": self.route_id,
            "purpose": self.purpose,
            "stage_ids": list(self.stage_ids),
            "required_capability_ids": list(self.required_capability_ids),
            "optional_capability_ids": list(self.optional_capability_ids),
            "hard_obligations": list(self.hard_obligations),
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_promotion_authority": False,
        }


@dataclass(frozen=True)
class DonorCompositionGraph:
    graph_id: str
    registry_id: str
    registry_digest: str
    routes: tuple[DonorCompositionRoute, ...]
    graph_digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "schema": "ORION.DonorCompositionGraph.v1",
            "graph_id": self.graph_id,
            "registry_id": self.registry_id,
            "registry_digest": self.registry_digest,
            "routes": [item.as_dict() for item in self.routes],
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_adoption_authority": False,
            "grants_promotion_authority": False,
            "grants_merge_authority": False,
        }

    def validate(self, registry: DonorRegistry) -> None:
        if registry.registry_id != self.registry_id or registry.digest != self.registry_digest:
            raise ValueError("donor composition graph is bound to a different registry")
        known = {item.capability_id for item in registry.capabilities}
        route_ids = [item.route_id for item in self.routes]
        if len(route_ids) != len(set(route_ids)):
            raise ValueError("donor composition route ids must be unique")
        for route in self.routes:
            if not route.route_id or not route.purpose or not route.stage_ids:
                raise ValueError("donor composition route is incomplete")
            missing = (set(route.required_capability_ids) | set(route.optional_capability_ids)) - known
            if missing:
                raise ValueError("donor composition route references unknown capabilities: " + ",".join(sorted(missing)))
        expected = hashlib.sha256(
            json.dumps(self.unsigned(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if expected != self.graph_digest:
            raise ValueError("donor composition graph digest mismatch")


def _build(graph_id: str, registry: DonorRegistry, routes: tuple[DonorCompositionRoute, ...]) -> DonorCompositionGraph:
    seed = DonorCompositionGraph(graph_id, registry.registry_id, registry.digest, routes, "")
    digest = hashlib.sha256(
        json.dumps(seed.unsigned(), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    graph = DonorCompositionGraph(graph_id, registry.registry_id, registry.digest, routes, digest)
    graph.validate(registry)
    return graph


def normal_orion_donor_graph() -> DonorCompositionGraph:
    registry = normal_orion_donor_registry()
    routes = (
        DonorCompositionRoute(
            "normal:problem-to-strongest-native-donor",
            "Route each fibre through the strongest already-absorbed native donor mechanic before ORION-only residual claims.",
            ("ATOMIZE", "FIBRE_SELECT", "DONOR_MATCH", "NATIVE_EXECUTE", "VERIFY", "RECONSTRUCT"),
            (),
            tuple(item.capability_id for item in registry.capabilities if item.executable),
            ("NO_DONOR_OMISSION", "NO_DONOR_AUTHORITY_ESCALATION"),
        ),
        DonorCompositionRoute(
            "normal:failure-to-reopen",
            "Turn failed/native donor traces into scoped failure state and reopen only dependent fibres.",
            ("FAILURE_RECEIPT", "RESPONSIBILITY", "EXPERIENCE", "REOPEN", "RESATURATE"),
            (),
            tuple(
                item.capability_id
                for item in registry.capabilities
                if item.capability_id in {
                    "rakl:challenge_failure_learning",
                    "rakl:route_family_health",
                    "rakl:identity_aware_saturation",
                    "rakl-engineering:E4",
                    "rakl-engineering:E9",
                    "rakl-engineering:E16",
                }
            ),
            ("NEGATIVE_HISTORY_PRESERVED", "DEPENDENT_CLOSURE_REOPENED"),
        ),
    )
    return _build("orion:donor-composition:normal:v1", registry, routes)


def orion_q_donor_graph() -> DonorCompositionGraph:
    registry = orion_q_donor_registry()
    q = lambda suffix: f"orion-q:{suffix}"
    routes = (
        DonorCompositionRoute(
            "q:problem-representation-access-specialist",
            "problem -> representation/access analysis -> strongest donor specialist selection",
            ("ATOMIZE", "REPRESENTATION_ACCESS", "SPECIALIST_SELECT"),
            (),
            (q("automated_oracle_reversible_synthesis"), q("qsp_qsvt_simulation_family"), q("full_stack_resource_optimization")),
            ("ACCESS_CONTRACT_PRESERVED", "STRONGEST_APPLICABLE_SPECIALIST_CHECKED"),
        ),
        DonorCompositionRoute(
            "q:staged-verification-resource",
            "specialist proposal -> cheap verifier -> expensive verifier -> resource estimator",
            ("PROPOSE", "CHEAP_VERIFY", "EXPENSIVE_VERIFY", "RESOURCE_ESTIMATE"),
            (),
            (q("verifier_in_loop_synthesis"), q("formal_quantum_theorem_infrastructure"), q("full_stack_resource_optimization")),
            ("CORRECTNESS_VERIFIED", "RESOURCE_VECTOR_BOUND"),
        ),
        DonorCompositionRoute(
            "q:successful-trace-abstraction",
            "verified successful traces -> library/DSL abstraction learner",
            ("VERIFIED_TRACE", "ABSTRACT", "LIBRARY_UPDATE"),
            (q("circuit_library_learning"),),
            (q("scalable_algorithm_family_search"),),
            ("ONLY_VERIFIED_TRACES_ABSTRACTED",),
        ),
        DonorCompositionRoute(
            "q:failed-trace-scoped-recovery",
            "failed traces -> scoped failure store -> reopen/abstain/verify decision",
            ("FAILURE_RECEIPT", "SCOPED_FAILURE", "RESPONSIBILITY", "REOPEN_OR_ABSTAIN"),
            (),
            (q("adaptive_solver_policy_discovery"), q("verifier_in_loop_synthesis")),
            ("FAILURE_DOES_NOT_SELF_PROMOTE", "DEPENDENT_FIBRES_ONLY_REOPEN"),
        ),
        DonorCompositionRoute(
            "q:conjecture-to-proof",
            "candidate theorem/conjecture -> formal proof tool",
            ("CONJECTURE", "FORMALIZE", "PROVE", "VERIFY"),
            (q("formal_quantum_theorem_infrastructure"),),
            (q("quantum_conjecture_reasoning"),),
            ("FORMAL_PROOF_REQUIRED_FOR_THEOREM_AUTHORITY",),
        ),
        DonorCompositionRoute(
            "q:stack-resource-closure",
            "candidate quantum stack -> oracle/state-preparation/resource closure",
            ("STACK", "ACCESS_ORACLE", "STATE_PREP", "RESOURCE_CLOSE"),
            (q("full_stack_resource_optimization"),),
            (q("automated_oracle_reversible_synthesis"), q("qsp_qsvt_simulation_family")),
            ("END_TO_END_RESOURCE_OBLIGATIONS_CLOSED",),
        ),
        DonorCompositionRoute(
            "q:qec-design-evaluation",
            "candidate QEC design -> code proxy -> syndrome circuit -> decoder evaluation",
            ("QEC_DESIGN", "CODE_PROXY", "SYNDROME_CIRCUIT", "DECODER_EVAL"),
            (q("qec_ai_scientist_codesign"),),
            (),
            ("MATCHED_QEC_EVALUATION",),
        ),
        DonorCompositionRoute(
            "q:algorithm-to-stack-optimization",
            "candidate algorithm -> QSVT/simulation/compiler family -> stack optimization",
            ("ALGORITHM", "SIMULATION_ROUTE", "COMPILE", "STACK_OPTIMIZE", "VERIFY"),
            (q("qsp_qsvt_simulation_family"), q("full_stack_resource_optimization")),
            (q("scalable_algorithm_family_search"), q("autonomous_evolutionary_quantum_search")),
            ("MATCHED_ACCESS", "MATCHED_RESOURCE_VECTOR", "INDEPENDENT_VERIFICATION"),
        ),
    )
    return _build("orion:donor-composition:orion-q:v1", registry, routes)


__all__ = [
    "DonorCompositionGraph",
    "DonorCompositionRoute",
    "normal_orion_donor_graph",
    "orion_q_donor_graph",
]
