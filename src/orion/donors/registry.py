from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class DonorDisposition(str, Enum):
    EXACT_REUSE = "EXACT_REUSE"
    RECONSTRUCTED = "RECONSTRUCTED"
    TESTS_RESULTS_REUSED = "TESTS_RESULTS_REUSED"
    DEFER_WITH_TRIGGER = "DEFER_WITH_TRIGGER"
    REJECT_WITH_REASON = "REJECT_WITH_REASON"


class DonorExecutionMode(str, Enum):
    NATIVE = "NATIVE"
    EXTERNAL_HOST = "EXTERNAL_HOST"
    REGRESSION_ONLY = "REGRESSION_ONLY"
    DEFERRED = "DEFERRED"


@dataclass(frozen=True)
class DonorCapability:
    capability_id: str
    donor_id: str
    source_version: str
    disposition: DonorDisposition
    execution_mode: DonorExecutionMode
    mechanic_ids: tuple[str, ...]
    supported_task_classes: tuple[str, ...]
    required_representation_ids: tuple[str, ...] = ()
    required_access_ids: tuple[str, ...] = ()
    required_input_spec_ids: tuple[str, ...] = ()
    output_type: str = "DonorCandidate"
    verifier_contract_ids: tuple[str, ...] = ()
    resource_coordinates: tuple[str, ...] = ()
    adaptive_feedback_ids: tuple[str, ...] = ()
    reusable_state_ids: tuple[str, ...] = ()
    failure_modes: tuple[str, ...] = ()
    applicability_boundary: str = ""
    evidence_paths: tuple[str, ...] = ()
    reopen_trigger: str = ""
    host_capability: str | None = None
    can_modify_method_language: bool = False
    can_change_representation_or_access: bool = False
    can_carry_scientific_authority: bool = False
    can_transfer_research_operators_cross_domain: bool = False

    def __post_init__(self) -> None:
        for value, name in (
            (self.capability_id, "capability_id"),
            (self.donor_id, "donor_id"),
            (self.source_version, "source_version"),
            (self.output_type, "output_type"),
            (self.applicability_boundary, "applicability_boundary"),
        ):
            if not value.strip():
                raise ValueError(f"{name} is required")
        if not self.mechanic_ids or not self.supported_task_classes:
            raise ValueError("donor capability requires mechanic and task bindings")
        if self.execution_mode is DonorExecutionMode.EXTERNAL_HOST and not self.host_capability:
            raise ValueError("external donor capability requires host_capability")
        if self.execution_mode is DonorExecutionMode.DEFERRED and not self.reopen_trigger:
            raise ValueError("deferred donor capability requires reopen_trigger")
        if self.can_carry_scientific_authority:
            raise ValueError("donor capability may not directly carry scientific authority")

    @property
    def executable(self) -> bool:
        return self.execution_mode in {DonorExecutionMode.NATIVE, DonorExecutionMode.EXTERNAL_HOST}

    def as_dict(self) -> dict[str, object]:
        return {
            "capability_id": self.capability_id,
            "donor_id": self.donor_id,
            "source_version": self.source_version,
            "disposition": self.disposition.value,
            "execution_mode": self.execution_mode.value,
            "mechanic_ids": list(self.mechanic_ids),
            "supported_task_classes": list(self.supported_task_classes),
            "required_representation_ids": list(self.required_representation_ids),
            "required_access_ids": list(self.required_access_ids),
            "required_input_spec_ids": list(self.required_input_spec_ids),
            "output_type": self.output_type,
            "verifier_contract_ids": list(self.verifier_contract_ids),
            "resource_coordinates": list(self.resource_coordinates),
            "adaptive_feedback_ids": list(self.adaptive_feedback_ids),
            "reusable_state_ids": list(self.reusable_state_ids),
            "failure_modes": list(self.failure_modes),
            "applicability_boundary": self.applicability_boundary,
            "evidence_paths": list(self.evidence_paths),
            "reopen_trigger": self.reopen_trigger,
            "host_capability": self.host_capability,
            "can_modify_method_language": self.can_modify_method_language,
            "can_change_representation_or_access": self.can_change_representation_or_access,
            "can_carry_scientific_authority": False,
            "can_transfer_research_operators_cross_domain": self.can_transfer_research_operators_cross_domain,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_adoption_authority": False,
            "grants_promotion_authority": False,
            "grants_merge_authority": False,
            "grants_global_task_stop_authority": False,
        }


def _mechanic_family(value: str) -> str:
    parts = [part for part in str(value).split(".") if not re.fullmatch(r"v\d+", part, re.IGNORECASE)]
    return ".".join(parts)


def _mechanic_match(left: str, right: str) -> bool:
    left_key = _mechanic_family(left)
    right_key = _mechanic_family(right)
    return (
        left_key == right_key
        or left_key.startswith(right_key + ".")
        or right_key.startswith(left_key + ".")
    )


class DonorRegistry:
    def __init__(self, capabilities: Iterable[DonorCapability], *, registry_id: str) -> None:
        rows = tuple(capabilities)
        if not registry_id.strip():
            raise ValueError("registry_id is required")
        ids = [item.capability_id for item in rows]
        if len(ids) != len(set(ids)):
            raise ValueError("donor capability ids must be unique")
        self.registry_id = registry_id
        self._capabilities = rows
        self._by_id = {item.capability_id: item for item in rows}

    @property
    def capabilities(self) -> tuple[DonorCapability, ...]:
        return self._capabilities

    @property
    def digest(self) -> str:
        payload = {
            "registry_id": self.registry_id,
            "capabilities": [item.as_dict() for item in sorted(self._capabilities, key=lambda x: x.capability_id)],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def get(self, capability_id: str) -> DonorCapability:
        return self._by_id[capability_id]

    def for_mechanic(
        self,
        mechanic_id: str,
        *,
        domain_ids: tuple[str, ...] = (),
        include_deferred: bool = True,
    ) -> tuple[DonorCapability, ...]:
        domains = {str(item).lower() for item in domain_ids}
        rows = []
        for item in self._capabilities:
            if not any(_mechanic_match(mechanic_id, bound) for bound in item.mechanic_ids):
                continue
            if not include_deferred and not item.executable:
                continue
            task_classes = {value.lower() for value in item.supported_task_classes}
            if domains and "general" not in task_classes and not (domains & task_classes):
                continue
            rows.append(item)
        return tuple(sorted(rows, key=lambda x: (not x.executable, x.capability_id)))

    def deferred_reopen_obligations(self) -> tuple[DonorCapability, ...]:
        return tuple(item for item in self._capabilities if item.execution_mode is DonorExecutionMode.DEFERRED)


def _rakl(
    capability_id: str,
    disposition: DonorDisposition,
    mechanic_ids: tuple[str, ...],
    evidence_paths: tuple[str, ...],
    trigger: str = "",
) -> DonorCapability:
    mode = (
        DonorExecutionMode.DEFERRED
        if disposition is DonorDisposition.DEFER_WITH_TRIGGER
        else DonorExecutionMode.REGRESSION_ONLY
        if disposition is DonorDisposition.TESTS_RESULTS_REUSED
        else DonorExecutionMode.NATIVE
    )
    return DonorCapability(
        capability_id=f"rakl:{capability_id}",
        donor_id="RAKL",
        source_version="70f5f7c4a6771ffd1158765b42ac9f8aee8a270f",
        disposition=disposition,
        execution_mode=mode,
        mechanic_ids=mechanic_ids,
        supported_task_classes=("GENERAL",),
        verifier_contract_ids=("ORION_NATIVE_VERIFICATION",),
        resource_coordinates=("time", "compute", "evidence"),
        failure_modes=("precondition_unsatisfied", "verification_failed", "scope_mismatch"),
        applicability_boundary="RAKL donor behavior is strongest-incumbent prior art/control; ORION receives no novelty credit for reproducing it.",
        evidence_paths=evidence_paths,
        reopen_trigger=trigger,
    )


_RAKL_SPECS = (
    ("method_assimilation", DonorDisposition.RECONSTRUCTED, ("ABSORB", "RECONSTRUCT"), ("src/orion/knowledge/assimilation.py", "src/orion/knowledge/nearest_work.py"), ""),
    ("atlas_gluing", DonorDisposition.DEFER_WITH_TRIGGER, ("RECONSTRUCT.GLUE",), ("src/orion/knowledge/assimilation.py", "src/orion/knowledge/semantics.py"), "Before promoting global-portrait reconstruction beyond proposal-only, execute the exact overlap/cycle/global-existence obstruction battery."),
    ("backward_multiseed", DonorDisposition.RECONSTRUCTED, ("SEARCH.ROUTE", "SEARCH.QUERY"), ("src/orion/knowledge/backward_multiseed.py",), ""),
    ("backward_multiseed_benchmark", DonorDisposition.EXACT_REUSE, ("CROSS.BENCHMARK",), ("src/orion/knowledge/backward_multiseed_benchmark.py",), ""),
    ("bridge_composition", DonorDisposition.DEFER_WITH_TRIGGER, ("RECONSTRUCT.GLUE", "REFRAME.REPRESENTATION"), ("src/orion/knowledge/generator_transport.py", "src/orion/knowledge/backward_multiseed.py"), "Before live multi-hop representation bridge search, execute donor bridge path/target-transfer falsifiers."),
    ("capability_shaping", DonorDisposition.RECONSTRUCTED, ("REFRAME.METHOD",), ("src/orion/self_orion/change_control.py", "src/orion/self_orion/readiness.py"), ""),
    ("challenge_failure_learning", DonorDisposition.RECONSTRUCTED, ("DIAGNOSE.EXPERIENCE_RETRIEVAL", "DETECT.FAILURE"), ("src/orion/experience", "src/orion/self_orion/issue_state.py", "src/orion/self_orion/evolution_archive.py"), ""),
    ("claim_evidence_binding", DonorDisposition.RECONSTRUCTED, ("ABSORB.EVIDENCE_BIND",), ("src/orion/kernel/evidence.py", "src/orion/mechanics/answers.py"), ""),
    ("context_compiler", DonorDisposition.EXACT_REUSE, ("CROSS.CONTEXT_POLICY",), ("src/orion/knowledge/context_compiler.py",), ""),
    ("core_projection_context_relations", DonorDisposition.RECONSTRUCTED, ("ABSORB.CONTEXT", "RECONSTRUCT.ATLAS_UPDATE"), ("src/orion/core", "src/orion/knowledge/semantics.py"), ""),
    ("formalism_mechanism_verification_packets", DonorDisposition.DEFER_WITH_TRIGGER, ("CROSS.EXECUTION", "CROSS.REVIEW"), ("src/orion/mechanics/mathematics.py", "src/orion/mechanics/verification.py", "src/orion/benchmarks/formal_engine.py"), "When a live formal-science task requires symbolic equation AST/mechanism-graph packets beyond current contracts, import the exact donor grammar first."),
    ("generator_transport", DonorDisposition.EXACT_REUSE, ("REFRAME.REPRESENTATION", "CROSS.EXECUTION"), ("src/orion/knowledge/generator_transport.py",), ""),
    ("evidence_identity", DonorDisposition.RECONSTRUCTED, ("ABSORB.REFERENCE_IDENTITY", "ABSORB.EVIDENCE_BIND"), ("src/orion/knowledge/identity.py", "src/orion/knowledge/ledger.py", "src/orion/kernel/evidence.py"), ""),
    ("identity_aware_saturation", DonorDisposition.TESTS_RESULTS_REUSED, ("SATURATE.KNOWLEDGE_FLATNESS", "SATURATE.STOP"), ("src/orion/kernel/saturation.py", "research/failures/2026-08-empty-lineage-false-saturation/README.md"), ""),
    ("source_identity", DonorDisposition.RECONSTRUCTED, ("SEARCH.SOURCE", "ABSORB.REFERENCE_IDENTITY"), ("src/orion/knowledge/identity.py", "src/orion/knowledge/ledger.py"), ""),
    ("invention_positive_goal_pareto", DonorDisposition.RECONSTRUCTED, ("REFRAME.METHOD", "CROSS.BENCHMARK"), ("src/orion/self_orion/invention_gate.py", "src/orion/mechanics/optimization.py", "src/orion/self_orion/rakl_donor_gate.py"), ""),
    ("measurement_relations", DonorDisposition.EXACT_REUSE, ("ABSORB.CONTEXT", "DIAGNOSE.ATTRIBUTION"), ("src/orion/knowledge/measurement.py",), ""),
    ("multiresolution_memory", DonorDisposition.DEFER_WITH_TRIGGER, ("CROSS.MEMORY", "CROSS.CONTEXT_POLICY"), ("src/orion/knowledge/ledger.py", "src/orion/self_orion/development_fibre.py"), "Before lossy memory compaction/rehydration, port SourcePin/canonical-closure and erasure-aware memory-view tests."),
    ("promotion", DonorDisposition.RECONSTRUCTED, ("CROSS.AUTHORITY",), ("src/orion/self_orion/readiness.py", "src/orion/kernel/gate.py"), ""),
    ("promotion_attestation", DonorDisposition.DEFER_WITH_TRIGGER, ("CROSS.AUTHORITY", "CROSS.EXECUTION"), ("src/orion/self_orion/readiness.py", "src/orion/benchmarks/external_evidence.py"), "When relying-party/host authorization is productionized, compare the exact donor attestation contract before adding a new receipt."),
    ("retrieval_benchmark", DonorDisposition.EXACT_REUSE, ("SEARCH.ROUTE", "CROSS.BENCHMARK"), ("src/orion/knowledge/retrieval_benchmark.py", "src/orion/knowledge/evaluation.py"), ""),
    ("route_family_health", DonorDisposition.RECONSTRUCTED, ("SEARCH.ROUTE_STOP", "DETECT.COVERAGE"), ("src/orion/knowledge/route_family_health.py",), ""),
    ("similarity_analogy_witnesses", DonorDisposition.EXACT_REUSE, ("RECONSTRUCT.ATLAS_UPDATE", "DIAGNOSE.DISCRIMINATOR"), ("src/orion/knowledge/similarity.py",), ""),
    ("subject_execution_identity_attestation", DonorDisposition.DEFER_WITH_TRIGGER, ("CROSS.EXECUTION", "CROSS.AUTHORITY"), ("src/orion/self_orion/readiness.py", "src/orion/kernel/evidence.py"), "When protected execution subject identity becomes a production relying-party boundary, run the frozen subject-attestation equivalence audit."),
)


def normal_orion_donor_registry() -> DonorRegistry:
    return DonorRegistry((_rakl(*spec) for spec in _RAKL_SPECS), registry_id="orion:donors:normal:v1")


def _quantum(capability_id: str, donor_id: str, mechanic_ids: tuple[str, ...], output_type: str) -> DonorCapability:
    return DonorCapability(
        capability_id=f"orion-q:{capability_id}",
        donor_id=donor_id,
        source_version="ORION-Q.DONOR_SUPERSYSTEM_V1.2026-08-20",
        disposition=DonorDisposition.EXACT_REUSE,
        execution_mode=DonorExecutionMode.EXTERNAL_HOST,
        mechanic_ids=mechanic_ids,
        supported_task_classes=("quantum", "quantum_algorithm", "qec", "quantum_formal", "quantum_resource"),
        required_input_spec_ids=("problem_contract", "representation_contract", "access_contract"),
        output_type=output_type,
        verifier_contract_ids=("DONOR_NATIVE_OR_EXTERNAL_VERIFIER", "ORION_INDEPENDENT_VERIFICATION"),
        resource_coordinates=("wall_time", "compute", "evaluation_cost", "quantum_resource_vector"),
        adaptive_feedback_ids=("feasibility", "verification", "resource", "failure"),
        reusable_state_ids=("verified_trace", "library_state", "scoped_failure_state"),
        failure_modes=("not_applicable", "verification_failed", "resource_infeasible", "interface_mismatch", "method_language_insufficient"),
        applicability_boundary="Strongest faithful donor capability; ORION receives no credit for wiring or reproducing this behavior.",
        host_capability="DONOR_EXECUTE",
    )


_Q_SPECS = (
    ("circuit_library_learning", "Sarra-Ellis-Marquardt/DreamCoder-style", ("REFRAME.METHOD", "CROSS.EXPERIENCE"), "ReusableCircuitLibrary"),
    ("verified_recursive_program_synthesis", "QSynth", ("REFRAME.METHOD", "CROSS.EXECUTION", "CROSS.REVIEW"), "VerifiedRecursiveQuantumProgram"),
    ("scalable_algorithm_family_search", "Rouillard-DSL-evolution", ("SEARCH.ROUTE", "REFRAME.METHOD"), "QuantumAlgorithmFamily"),
    ("verifier_in_loop_synthesis", "Vista", ("CROSS.EXPERIMENT_SELECTION", "CROSS.REVIEW", "REFRAME.METHOD"), "VerifiedSynthesisCandidate"),
    ("adaptive_solver_policy_discovery", "AutoQResearch", ("REFRAME.SEARCH_POLICY", "REFRAME.METHOD"), "AdaptiveSolverPolicy"),
    ("quantum_conjecture_reasoning", "SCALAR", ("SEARCH.ROUTE", "RECONSTRUCT.PORTRAIT", "CROSS.REVIEW"), "QuantumConjectureOrInvariant"),
    ("quantum_experiment_meta_design", "Arlt-meta-design", ("REFRAME.METHOD", "CROSS.EXPERIMENT_SELECTION"), "QuantumExperimentDesignRule"),
    ("qec_ai_scientist_codesign", "OmniQEC", ("REFRAME.METHOD", "CROSS.EXECUTION", "CROSS.BENCHMARK"), "QECDesignCandidate"),
    ("full_stack_resource_optimization", "AutoQuREO", ("CROSS.EXECUTION", "CROSS.BENCHMARK", "REFRAME.METHOD"), "QuantumStackResourcePlan"),
    ("autonomous_evolutionary_quantum_search", "OpenEvolve-CUDA-Q", ("SEARCH.ROUTE", "REFRAME.METHOD", "CROSS.EXECUTION"), "EvolutionaryQuantumCandidate"),
    ("formal_quantum_theorem_infrastructure", "Lean-QuantumAlg/Lean-quantum", ("CROSS.REVIEW", "CROSS.EXECUTION"), "MachineCheckedQuantumTheorem"),
    ("automated_oracle_reversible_synthesis", "MLIR-HDL-reversible-synthesis", ("REFRAME.REPRESENTATION", "CROSS.EXECUTION"), "QuantumOracleCircuit"),
    ("qsp_qsvt_simulation_family", "QSP-QSVT/simulation-family", ("SEARCH.ROUTE", "REFRAME.METHOD", "CROSS.EXECUTION"), "QuantumSimulationMethod"),
)


def orion_q_donor_registry() -> DonorRegistry:
    return DonorRegistry(
        (*normal_orion_donor_registry().capabilities, *(_quantum(*spec) for spec in _Q_SPECS)),
        registry_id="orion:donors:orion-q:v1",
    )


__all__ = [
    "DonorCapability",
    "DonorDisposition",
    "DonorExecutionMode",
    "DonorRegistry",
    "normal_orion_donor_registry",
    "orion_q_donor_registry",
]
