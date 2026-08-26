from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from orion.core.problem import Problem
from orion.core.residuals import Responsibility
from orion.core.search import RetrievedItem
from orion.core.solution import SolutionStatus
from orion.engine.solver import SolverConfig
from orion.providers.llm import CallableLLMProvider
from orion.providers.retrieval import InMemoryRetrievalProvider
from orion.providers.verification import InMemoryVerificationProvider
from orion.runtime import OrionRuntime
from orion.self_orion.revision_gate import RevisionGateReport, assess_revision_gate
from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.epistemic_responsibility import (
    ResponsibilityReport,
    ResponsibilityStatus,
    assess_responsibility,
    build_responsibility_hypothesis,
)
from orion.transfer.v2.higher_order_epistemic_mechanics import (
    ObligationState,
    assess_mechanic,
    build_mechanic,
)
from orion.transfer.v2.interface_adequacy import (
    InterfaceAdequacyReport,
    InterfaceCheckState,
    assess_interface_adequacy,
    build_interface_check,
)

ROOT = Path(__file__).resolve().parent
PROTOCOL = json.loads((ROOT / "NATIVE_PROTOCOL_V1.json").read_text())

CONTROL = str(PROTOCOL["control_class"])
UNRESOLVED = str(PROTOCOL["unresolved_class"])
PROBE_TO_CLASS: dict[str, str] = dict(PROTOCOL["probes"])
CLASS_TO_PROBE = {value: key for key, value in PROBE_TO_CLASS.items()}
PROBE_PRIORITY: tuple[str, ...] = tuple(PROTOCOL["active_probe_priority"])
NATIVE_TO_P1: dict[str, str] = dict(PROTOCOL["native_responsibility_to_p1"])
BUDGET = int(PROTOCOL["budget"])


@dataclass(frozen=True)
class NativeRootExecution:
    result: object
    provider_responsibilities: tuple[str, ...]
    operator_ids: tuple[str, ...]
    receipt_ids: tuple[str, ...]


@dataclass(frozen=True)
class NativeProbeExecution:
    probe_id: str
    observation: str
    trace_id: str
    operator_ids: tuple[str, ...]
    receipt_ids: tuple[str, ...]
    evidence_id: str


class FrozenNativeProviderHost:
    """Deterministic semantic host behind the canonical LLM provider boundary.

    The host only sees the normal ORION LLMRequest payload.  It is deliberately
    weaker than a live semantic model and exists to isolate native controller
    behavior.  It never receives evaluator gold, pair role, source class or the
    hidden unselected discriminator table.
    """

    def __init__(self, *, mode: str, probe_query_text: str | None = None) -> None:
        if mode not in {"root", "probe"}:
            raise ValueError("mode must be root or probe")
        self.mode = mode
        self.probe_query_text = probe_query_text
        self.calls: list[tuple[str, str]] = []
        self.last_native_responsibilities: tuple[str, ...] = ()

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join(value.lower().split())

    def _diagnose_native(self, dossier: str) -> tuple[str, ...]:
        cfg = PROTOCOL["provider"]
        text = self._normalize_text(dossier)
        scores: dict[str, int] = {}
        for responsibility in cfg["cue_order"]:
            scores[str(responsibility)] = sum(
                1 for keyword in cfg["keywords"][responsibility]
                if self._normalize_text(str(keyword)) in text
            )
        ordered = list(map(str, cfg["cue_order"]))
        best = max(ordered, key=lambda item: (scores[item], -ordered.index(item)))
        if scores[best] <= 0:
            best = str(cfg["fallback_alternative"])
        responsibilities = [str(cfg["always_consider_native_responsibility"])]
        if best not in responsibilities:
            responsibilities.append(best)
        responsibilities = responsibilities[: int(cfg["max_native_responsibilities"])]
        return tuple(responsibilities)

    def __call__(self, request) -> str:
        self.calls.append((str(request.task), str(request.user)))
        payload = json.loads(request.user)
        task = str(request.task)

        if task == "plan_search":
            if self.mode == "probe":
                if not self.probe_query_text:
                    raise RuntimeError("probe provider missing frozen query text")
                return json.dumps(
                    {
                        "queries": [
                            {
                                "query_id": "p1-r6-probe-query",
                                "text": self.probe_query_text,
                                "route_id": "p1-r6-native-probe-route",
                                "route_kind": "CURRENT_VOCABULARY",
                                "domain_hint": "p1-r6-protected-discriminator",
                            }
                        ]
                    }
                )
            # The typed reasoner contract rejects an empty search plan.  The
            # root diagnostic still receives no evidence because its retrieval
            # provider is empty, but it must exercise SEARCH before the
            # fail-closed ABSORB/RECONSTRUCT/DETECT/DIAGNOSE path can run.
            return json.dumps(
                {
                    "queries": [
                        {
                            "query_id": "p1-r6-root-query",
                            "text": "frozen P1-R6 root diagnostic context",
                            "route_id": "p1-r6-native-root-route",
                            "route_kind": "CURRENT_VOCABULARY",
                            "domain_hint": "p1-r6",
                        }
                    ]
                }
            )

        if task == "interpret":
            item = payload["retrieved_item"]
            return json.dumps(
                {
                    "contribution_id": f"contribution:{item['item_id']}",
                    "text": str(item["content"]),
                    "assimilation": "COMPLEMENTARY_FACET",
                    "discovered_domain_ids": [],
                    "representation_ids": [],
                    "contradicts_claim_ids": [],
                    "related_claim_ids": [],
                    "context_ids": [],
                    "referent_bindings": [],
                    "representation_mappings": [],
                    "assumption_ids": [],
                }
            )

        if task == "reconstruct":
            return json.dumps(
                {"summary": "Native ORION reconstruction under the frozen P1-R6 host."}
            )

        if task == "diagnose":
            problem = payload["problem"]
            responsibilities = self._diagnose_native(str(problem.get("scope", "")))
            self.last_native_responsibilities = responsibilities
            return json.dumps(
                {
                    "responsibilities": list(responsibilities),
                    "rationale": "Frozen native provider preserves evidence responsibility and one surface-supported alternative.",
                }
            )

        if task == "propose_reframe":
            return json.dumps(
                {
                    "add_domain_ids": [],
                    "add_representation_ids": [],
                    "note": "No provider-side material mutation; native gate owns later nomination.",
                }
            )

        if task == "compose_answer":
            claims = payload.get("verified_claims", [])
            answer = " | ".join(str(item.get("text", "")) for item in claims) or "No verified claim."
            return json.dumps({"answer": answer})

        raise KeyError(f"unsupported native provider task: {task}")


def _trace_operator_ids(result) -> tuple[str, ...]:
    return tuple(event.receipt.mechanic_id for event in result.trace.events)


def _trace_receipt_ids(result) -> tuple[str, ...]:
    return tuple(event.receipt.receipt_id for event in result.trace.events)


def _require_operator_ids(result, required: Sequence[str]) -> None:
    observed = set(_trace_operator_ids(result))
    missing = tuple(item for item in required if item not in observed)
    if missing:
        raise AssertionError(f"native runtime trace missing required mechanics: {missing}")


def _runtime(
    *,
    provider_host: FrozenNativeProviderHost,
    retrieval: InMemoryRetrievalProvider,
    verification: InMemoryVerificationProvider,
    max_iterations: int,
) -> OrionRuntime:
    model_id = str(PROTOCOL["provider"]["model_id"])
    return OrionRuntime.from_providers(
        llm=CallableLLMProvider(provider_host, model_id=model_id),
        retrieval=retrieval,
        verification=verification,
        config=SolverConfig(
            max_iterations=max_iterations,
            require_verified_answer=True,
        ),
        producer_process_lineage_hash="p1-r6-native-provider-v1",
        evaluator_artifact_hash="p1-r6-evaluator-pre-outcome",
    )


def run_root_runtime(*, episode_id: str, dossier: str, domain: str) -> NativeRootExecution:
    host = FrozenNativeProviderHost(mode="root")
    cfg = PROTOCOL["root_runtime"]
    runtime = _runtime(
        provider_host=host,
        retrieval=InMemoryRetrievalProvider({}),
        verification=InMemoryVerificationProvider(frozenset()),
        max_iterations=int(cfg["max_iterations"]),
    )
    result = runtime.solve(
        Problem(
            problem_id=f"p1-r6-root:{episode_id}",
            question="What is the narrowest scientifically responsible next action for this unresolved episode?",
            scope=str(dossier),
            initial_domain_ids=(str(domain),),
            success_criteria=(
                "Preserve ambiguity when responsibility is not identified.",
                "Do not create scientific authority from diagnosis alone.",
            ),
        ),
        evaluation_epoch_id=str(cfg["evaluation_epoch_id"]),
        split_id=str(cfg["split_id"]),
    )
    _require_operator_ids(result, tuple(cfg["required_operator_ids"]))
    if not host.last_native_responsibilities:
        raise AssertionError("native root runtime did not execute DIAGNOSE")
    return NativeRootExecution(
        result=result,
        provider_responsibilities=host.last_native_responsibilities,
        operator_ids=_trace_operator_ids(result),
        receipt_ids=_trace_receipt_ids(result),
    )


class NativeProbeHost:
    """Evaluator boundary that reveals one discriminator only through a child runtime."""

    def __init__(
        self,
        *,
        episode_id: str,
        hidden_probes: Mapping[str, str],
        evidence_note: str,
    ) -> None:
        if set(hidden_probes) != set(PROBE_TO_CLASS):
            raise ValueError("hidden probe set mismatch")
        self.episode_id = str(episode_id)
        self._hidden = dict(hidden_probes)
        self._evidence_note = str(evidence_note)
        self.accessed: list[str] = []
        self.executions: list[NativeProbeExecution] = []

    def execute_probe(self, probe_id: str) -> NativeProbeExecution:
        if probe_id not in self._hidden:
            raise KeyError(probe_id)
        if probe_id in self.accessed:
            raise RuntimeError("native discriminator cannot be acquired twice")
        if len(self.accessed) >= BUDGET:
            raise RuntimeError("native discriminator budget exceeded")

        # Hidden observation is accessed here at the evaluator/provider boundary,
        # not by the candidate controller.  The controller receives it only after
        # the canonical runtime absorbs/verifies the selected retrieval item.
        observation = str(self._hidden[probe_id])
        if observation not in set(PROTOCOL["probe_observations"]):
            raise ValueError("invalid hidden probe observation")
        self.accessed.append(probe_id)

        query_text = f"p1-r6-native-probe:{self.episode_id}:{probe_id}"
        item_id = f"evidence:p1-r6:{self.episode_id}:{probe_id}"
        item = RetrievedItem(
            item_id=item_id,
            content=(
                f"P1_NATIVE_DISCRIMINATOR={probe_id}; OBSERVATION={observation}; "
                f"SOURCE_GROUNDED_NOTE={self._evidence_note}"
            ),
            source_uri=f"p1-r6://{self.episode_id}/{probe_id}",
            domain_ids=("p1-r6-protected-discriminator",),
        )
        host = FrozenNativeProviderHost(mode="probe", probe_query_text=query_text)
        cfg = PROTOCOL["probe_runtime"]
        runtime = _runtime(
            provider_host=host,
            retrieval=InMemoryRetrievalProvider({query_text: (item,)}),
            verification=InMemoryVerificationProvider(frozenset({item_id})),
            max_iterations=int(cfg["max_iterations"]),
        )
        result = runtime.solve(
            Problem(
                problem_id=f"p1-r6-probe:{self.episode_id}:{probe_id}",
                question=f"Acquire and verify the selected discriminator {probe_id}.",
                scope="Protected P1 discriminator acquisition. No evaluator gold is available.",
                initial_domain_ids=("p1-r6-protected-discriminator",),
                success_criteria=("Return only verified selected-discriminator evidence.",),
            ),
            evaluation_epoch_id=str(cfg["evaluation_epoch_id"]),
            split_id=str(cfg["split_id"]),
        )
        _require_operator_ids(result, tuple(cfg["required_operator_ids"]))
        if result.solution.status is not SolutionStatus.SOLVED_VERIFIED:
            raise AssertionError(
                f"native probe runtime did not produce verified evidence: {result.solution.status.value}"
            )
        record = next(
            (record for record in result.final_state.knowledge.evidence if record.evidence_id == item_id),
            None,
        )
        if record is None:
            raise AssertionError("native probe evidence missing from returned runtime state")
        match = re.search(r"OBSERVATION=(SUPPORT|REFUTE|INCONCLUSIVE)", record.content)
        if match is None:
            raise AssertionError("native probe runtime evidence lacks encoded observation")
        parsed = match.group(1)
        execution = NativeProbeExecution(
            probe_id=probe_id,
            observation=parsed,
            trace_id=result.trace.trace_id,
            operator_ids=_trace_operator_ids(result),
            receipt_ids=_trace_receipt_ids(result),
            evidence_id=item_id,
        )
        self.executions.append(execution)
        return execution


def _mapped_p1_candidates(native_responsibilities: Sequence[str]) -> tuple[str, ...]:
    out: list[str] = []
    for responsibility in native_responsibilities:
        mapped = NATIVE_TO_P1.get(str(responsibility))
        if mapped and mapped not in out:
            out.append(mapped)
    return tuple(out)


def _runtime_candidate_report(*, episode_id: str, candidates: Sequence[str]) -> ResponsibilityReport:
    if not candidates:
        candidates = ("SEARCH_OR_EVIDENCE",)
    claim_id = f"p1-r6:{episode_id}:runtime-diagnosis"
    hypotheses = tuple(
        build_responsibility_hypothesis(
            hypothesis_id=str(candidate),
            claim_id=claim_id,
            expected_observations={"runtime_diagnosis": ("PRESENT",)},
            support_evidence_ids=(f"runtime-diagnosis:{episode_id}",),
        )
        for candidate in candidates
    )
    return assess_responsibility(hypotheses, observed_outcomes={"runtime_diagnosis": "PRESENT"})


def _stage_report(
    *,
    episode_id: str,
    stage: int,
    survivors: Sequence[str],
    pivot_class: str,
    probe_id: str,
    observation: str,
    evidence_id: str,
) -> ResponsibilityReport:
    claim_id = f"p1-r6:{episode_id}:ard-stage:{stage}"
    hypotheses = []
    for candidate in survivors:
        if candidate == pivot_class:
            allowed = ("SUPPORT", "INCONCLUSIVE")
        else:
            allowed = ("REFUTE", "INCONCLUSIVE")
        hypotheses.append(
            build_responsibility_hypothesis(
                hypothesis_id=str(candidate),
                claim_id=claim_id,
                expected_observations={probe_id: allowed},
                support_evidence_ids=(evidence_id,),
            )
        )
    return assess_responsibility(
        tuple(hypotheses),
        observed_outcomes={probe_id: observation},
    )


def _interface_report(
    *,
    episode_id: str,
    responsibility: ResponsibilityReport,
    observations: Mapping[str, str],
) -> InterfaceAdequacyReport:
    rep_probe = CLASS_TO_PROBE["REPRESENTATION_OR_INTERFACE"]
    rep_observation = observations.get(rep_probe)
    if rep_observation == "SUPPORT":
        state = InterfaceCheckState.FAIL
    elif rep_observation == "INCONCLUSIVE":
        state = InterfaceCheckState.UNRESOLVED
    elif rep_observation == "REFUTE":
        state = InterfaceCheckState.PASS
    elif (
        responsibility.status is ResponsibilityStatus.IDENTIFIED
        and responsibility.identified_hypothesis_id == "REPRESENTATION_OR_INTERFACE"
    ):
        state = InterfaceCheckState.UNRESOLVED
    else:
        state = InterfaceCheckState.PASS
    check = build_interface_check(
        check_id=f"p1-r6:{episode_id}:representation-interface",
        scope="W.REPRESENTATIONS",
        state=state,
        evidence_ids=tuple(f"probe:{key}:{value}" for key, value in sorted(observations.items())),
        required=True,
    )
    return assess_interface_adequacy((check,))


def _revision_gate(
    *,
    episode_id: str,
    responsibility: ResponsibilityReport,
    observations: Mapping[str, str],
) -> tuple[InterfaceAdequacyReport, RevisionGateReport]:
    interface = _interface_report(
        episode_id=episode_id,
        responsibility=responsibility,
        observations=observations,
    )
    mechanics = []
    assessments = []
    bindings: dict[str, tuple[str, ...]] = {}
    obligation_states = {
        "P1_EVIDENCE_BOUND": ObligationState.SATISFIED,
        "P1_NON_AUTHORIZING": ObligationState.SATISFIED,
    }
    for p1_class, spec in PROTOCOL["mechanics"].items():
        mechanic = build_mechanic(
            mechanic_id=str(spec["mechanic_id"]),
            claim_id=responsibility.claim_id,
            kind=str(spec["kind"]),
            read_coordinates=("K", "W", "M"),
            write_coordinates=tuple(map(str, spec["write_coordinates"])),
            preconditions=("P1_EVIDENCE_BOUND",),
            hard_requirements=("P1_NON_AUTHORIZING",),
            preservation_obligations=("P1_PRESERVE_SOURCE_SET", "P1_PRESERVE_AUTHORITY_BOUNDARY"),
            required_authorities=(),
            cost=0.0 if p1_class == CONTROL else 1.0,
        )
        mechanics.append(mechanic)
        assessments.append(
            assess_mechanic(
                mechanic,
                obligation_states=obligation_states,
                granted_authorities=(),
                forbidden_writes=(),
            )
        )
        bindings[str(p1_class)] = (mechanic.mechanic_id,)

    rep_mechanic_id = str(PROTOCOL["mechanics"]["REPRESENTATION_OR_INTERFACE"]["mechanic_id"])
    gate = assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=tuple(mechanics),
        assessments=tuple(assessments),
        responsibility_bindings=bindings,
        interface_repair_mechanic_ids=(rep_mechanic_id,),
        interface_coordinates=("W.REPRESENTATIONS",),
    )
    return interface, gate


def _decision_payload(
    *,
    arm: str,
    episode_id: str,
    root: NativeRootExecution,
    responsibility: ResponsibilityReport,
    interface: InterfaceAdequacyReport,
    gate: RevisionGateReport,
    probe_host: NativeProbeHost | None,
    observations: Mapping[str, str],
) -> dict[str, object]:
    choice = (
        responsibility.identified_hypothesis_id
        if responsibility.status is ResponsibilityStatus.IDENTIFIED
        else UNRESOLVED
    )
    probe_executions = []
    if probe_host is not None:
        probe_executions = [
            {
                "probe_id": item.probe_id,
                "observation": item.observation,
                "trace_id": item.trace_id,
                "operator_ids": list(item.operator_ids),
                "receipt_ids": list(item.receipt_ids),
                "evidence_id": item.evidence_id,
            }
            for item in probe_host.executions
        ]
    payload: dict[str, object] = {
        "schema": "P1U.NativeOrionDecision.v1",
        "arm": arm,
        "episode_id": episode_id,
        "choice": choice,
        "root": {
            "solution_status": root.result.solution.status.value,
            "trace_id": root.result.trace.trace_id,
            "operator_ids": list(root.operator_ids),
            "receipt_ids": list(root.receipt_ids),
            "provider_native_responsibilities": list(root.provider_responsibilities),
        },
        "probe_accesses": list(probe_host.accessed if probe_host is not None else ()),
        "probe_executions": probe_executions,
        "observed_discriminators": dict(sorted(observations.items())),
        "responsibility_status": responsibility.status.value,
        "responsibility_digest": responsibility.digest,
        "interface_status": interface.status.value,
        "interface_digest": interface.digest,
        "revision_gate_status": gate.status.value,
        "revision_gate_digest": gate.digest,
        "selected_mechanic_id": gate.selected_mechanic_id,
        "grants_adoption_authority": gate.grants_adoption_authority,
        "grants_promotion_authority": gate.grants_promotion_authority,
        "grants_merge_authority": gate.grants_merge_authority,
    }
    payload["digest"] = content_digest(payload)
    return payload


def run_native_base(episode: Mapping[str, object]) -> dict[str, object]:
    episode_id = str(episode["id"])
    root = run_root_runtime(
        episode_id=episode_id,
        dossier=str(episode["dossier"]),
        domain=str(episode.get("actual_domain", "p1-r6")),
    )
    candidates = _mapped_p1_candidates(root.provider_responsibilities)
    responsibility = _runtime_candidate_report(episode_id=episode_id, candidates=candidates)
    interface, gate = _revision_gate(
        episode_id=episode_id,
        responsibility=responsibility,
        observations={},
    )
    return _decision_payload(
        arm="ORION_NATIVE_BASE",
        episode_id=episode_id,
        root=root,
        responsibility=responsibility,
        interface=interface,
        gate=gate,
        probe_host=None,
        observations={},
    )


def run_native_ard(
    episode: Mapping[str, object],
    *,
    evidence_note: str,
) -> dict[str, object]:
    episode_id = str(episode["id"])
    root = run_root_runtime(
        episode_id=episode_id,
        dossier=str(episode["dossier"]),
        domain=str(episode.get("actual_domain", "p1-r6")),
    )
    candidates = list(_mapped_p1_candidates(root.provider_responsibilities))
    if not candidates:
        candidates = ["SEARCH_OR_EVIDENCE"]
    survivors = list(dict.fromkeys((*candidates, CONTROL)))
    probe_host = NativeProbeHost(
        episode_id=episode_id,
        hidden_probes=episode["probes"],
        evidence_note=evidence_note,
    )
    observations: dict[str, str] = {}
    responsibility: ResponsibilityReport | None = None
    probed_classes: set[str] = set()

    for stage in range(1, BUDGET + 1):
        pivot = next(
            (
                p1_class
                for p1_class in PROBE_PRIORITY
                if p1_class in survivors and p1_class not in probed_classes
            ),
            None,
        )
        if pivot is None:
            break
        probed_classes.add(pivot)
        probe_id = CLASS_TO_PROBE[pivot]
        execution = probe_host.execute_probe(probe_id)
        observations[probe_id] = execution.observation
        responsibility = _stage_report(
            episode_id=episode_id,
            stage=stage,
            survivors=survivors,
            pivot_class=pivot,
            probe_id=probe_id,
            observation=execution.observation,
            evidence_id=execution.evidence_id,
        )
        if responsibility.status is ResponsibilityStatus.IDENTIFIED:
            break
        if responsibility.status is ResponsibilityStatus.AMBIGUOUS:
            survivors = list(responsibility.surviving_hypothesis_ids)
            continue
        break

    if responsibility is None:
        responsibility = _runtime_candidate_report(
            episode_id=episode_id,
            candidates=tuple(survivors),
        )

    interface, gate = _revision_gate(
        episode_id=episode_id,
        responsibility=responsibility,
        observations=observations,
    )
    return _decision_payload(
        arm="ORION_NATIVE_ARD",
        episode_id=episode_id,
        root=root,
        responsibility=responsibility,
        interface=interface,
        gate=gate,
        probe_host=probe_host,
        observations=observations,
    )


__all__ = [
    "CONTROL",
    "NATIVE_TO_P1",
    "NativeProbeHost",
    "PROTOCOL",
    "UNRESOLVED",
    "run_native_ard",
    "run_native_base",
    "run_root_runtime",
]
