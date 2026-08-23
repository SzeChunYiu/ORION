from __future__ import annotations

import hashlib
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from orion_research_harness.protocol import CapabilityRequest
from orion_research_harness.runner import run_problem
from orion_research_harness.workspace import ResearchWorkspace
from orion.self_orion.revision_gate import RevisionGateStatus, assess_revision_gate
from orion.transfer.v2.epistemic_responsibility import (
    ResponsibilityReport,
    ResponsibilityStatus,
    assess_responsibility,
    build_responsibility_hypothesis,
)
from orion.transfer.v2.higher_order_epistemic_mechanics import (
    AssessmentStatus,
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
PROTOCOL = json.loads((ROOT / "gpt_r2" / "PROTOCOL_V1.json").read_text())
PROBE_TO_CLASS: dict[str, str] = dict(PROTOCOL["probes"])
CLASS_TO_PROBE = {value: key for key, value in PROBE_TO_CLASS.items()}
SUBSTANTIVE = tuple(PROBE_TO_CLASS.values())
HIGH = {"OBJECTIVE_OR_MODEL_CLASS", "PROBLEM_BOUNDARY"}
LOW = set(SUBSTANTIVE) - HIGH
CONTROL = "NO_HIGH_LEVEL_REFORMULATION"
UNRESOLVED = "UNRESOLVED"
ALL_OBSERVATIONS = ("SUPPORT", "REFUTE", "INCONCLUSIVE")

CLASS_TO_NATIVE = {
    "SEARCH_OR_EVIDENCE": "SEARCH",
    "REPRESENTATION_OR_INTERFACE": "REPRESENTATION",
    "IMPLEMENTATION_OR_ENVIRONMENT": "EXECUTION",
    "MEASUREMENT_OR_EVALUATOR": "MEASUREMENT",
    "OBJECTIVE_OR_MODEL_CLASS": "METHOD",
    "PROBLEM_BOUNDARY": "QUESTION",
}
NATIVE_TO_CLASS = {value: key for key, value in CLASS_TO_NATIVE.items()}

CLASS_TO_MECHANIC = {
    "SEARCH_OR_EVIDENCE": "p1:repair-evidence",
    "REPRESENTATION_OR_INTERFACE": "p1:repair-representation",
    "IMPLEMENTATION_OR_ENVIRONMENT": "p1:repair-execution",
    "MEASUREMENT_OR_EVALUATOR": "p1:repair-measurement",
    "OBJECTIVE_OR_MODEL_CLASS": "p1:revise-objective",
    "PROBLEM_BOUNDARY": "p1:revise-boundary",
    CONTROL: "p1:preserve-formulation",
}
MECHANIC_TO_CLASS = {value: key for key, value in CLASS_TO_MECHANIC.items()}


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _hex64(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


class ProbeGate(Mapping[str, str]):
    """Hide all frozen probe outcomes until the ARD adapter explicitly acquires one."""

    def __init__(self, hidden: Mapping[str, str]) -> None:
        if set(hidden) != set(PROBE_TO_CLASS):
            raise ValueError("probe set mismatch")
        self._hidden = {str(key): str(value) for key, value in hidden.items()}
        self.revealed: list[tuple[str, str]] = []

    def __getitem__(self, key: str) -> str:
        if key not in self._hidden:
            raise KeyError(key)
        value = self._hidden[key]
        self.revealed.append((key, value))
        return value

    def __iter__(self):
        raise RuntimeError("candidate may not enumerate hidden probes")

    def __len__(self) -> int:
        return len(self._hidden)


def semantic_scores(dossier: str) -> dict[str, int]:
    """Frozen dossier-only acquisition heuristic; it carries no scientific authority."""

    text = " ".join(dossier.lower().split())
    keywords = PROTOCOL["surface_prior"]["keywords"]
    return {
        cls: sum(1 for keyword in keywords[cls] if str(keyword).lower() in text)
        for cls in PROTOCOL["classes"]
    }


def semantic_first_class(dossier: str) -> str:
    scores = semantic_scores(dossier)
    order = {cls: index for index, cls in enumerate(SUBSTANTIVE)}
    return max(SUBSTANTIVE, key=lambda cls: (scores.get(cls, 0), -order[cls]))


def semantic_native_diagnosis(dossier: str) -> str | None:
    scores = semantic_scores(dossier)
    first = semantic_first_class(dossier)
    if scores.get(CONTROL, 0) > scores.get(first, 0):
        return None
    return CLASS_TO_NATIVE[first]


@dataclass
class HarnessHost:
    dossier: str
    source_uri: str
    diagnosis_tokens: list[str]
    request_payloads: list[dict[str, object]]

    def service(self, workspace: ResearchWorkspace, request: CapabilityRequest) -> None:
        self.request_payloads.append(dict(request.payload))
        payload = request.payload
        if request.capability == "LLM_COMPLETE":
            task = str(payload["task"])
            if task == "plan_search":
                content = json.dumps(
                    {
                        "queries": [
                            {
                                "query_id": "frozen-source-projection",
                                "text": "retrieve the fixed source-grounded case projection",
                                "route_id": "fixed-primary-universe",
                                "route_kind": "FRESHNESS",
                                "domain_hint": "scientific_case",
                            }
                        ]
                    }
                )
            elif task == "interpret":
                contribution_id = "contribution:" + _digest(self.dossier)[:24]
                content = json.dumps(
                    {
                        "contribution_id": contribution_id,
                        "text": self.dossier,
                        "assimilation": "COMPLEMENTARY_FACET",
                        "discovered_domain_ids": ["scientific_case"],
                        "representation_ids": [],
                        "contradicts_claim_ids": [],
                        "related_claim_ids": [],
                        "context_ids": [],
                        "referent_bindings": [],
                        "representation_mappings": [],
                        "assumption_ids": [],
                    }
                )
            elif task == "reconstruct":
                content = json.dumps(
                    {
                        "summary": (
                            "The fixed source-grounded dossier is the complete visible evidence "
                            "projection for this episode; preserve uncertainty beyond it."
                        )
                    }
                )
            elif task == "diagnose":
                token = semantic_native_diagnosis(self.dossier)
                responsibilities = [] if token is None else [token]
                if token is not None:
                    self.diagnosis_tokens.append(token)
                content = json.dumps(
                    {
                        "responsibilities": responsibilities,
                        "rationale": (
                            "Dossier-only frozen semantic triage; this is a non-authorizing "
                            "runtime proposal and is not the evaluator gold label."
                        ),
                    }
                )
            elif task == "propose_reframe":
                content = json.dumps(
                    {
                        "add_domain_ids": [],
                        "add_representation_ids": [],
                        "note": "Do not broaden the formulation without protected discriminator evidence.",
                    }
                )
            elif task == "compose_answer":
                content = json.dumps(
                    {
                        "answer": (
                            "Retain only conclusions supported by the fixed dossier and native "
                            "verification receipts."
                        )
                    }
                )
            else:
                raise AssertionError(f"unexpected LLM task: {task}")
            workspace.ingest_result(
                request.request_id,
                success=True,
                output={"content": content, "model_id": "p1-r6-frozen-semantic-host"},
                executor="p1-r6-frozen-semantic-host",
            )
            return

        if request.capability == "WEB_SEARCH":
            item_id = "source-projection:" + _digest(self.source_uri)[:24]
            workspace.ingest_result(
                request.request_id,
                success=True,
                output={
                    "items": [
                        {
                            "item_id": item_id,
                            "content": self.dossier,
                            "source_uri": self.source_uri,
                            "domain_ids": ["scientific_case"],
                        }
                    ]
                },
                executor="p1-r6-fixed-source-universe",
            )
            return

        if request.capability == "VERIFY_EVIDENCE":
            certificate = "certificate:p1-r6:" + _digest(self.source_uri + "|" + self.dossier)[:24]
            workspace.ingest_result(
                request.request_id,
                success=True,
                output={
                    "passed": True,
                    "certificate_ids": [certificate],
                    "reason": "The contribution is a direct projection of the fixed dossier.",
                },
                executor="p1-r6-independent-fixed-projection-check",
            )
            return

        raise AssertionError(f"unexpected capability: {request.capability}")


def _mechanics(claim_id: str):
    preserve_all = (
        "PRESERVE_EVIDENCE",
        "PRESERVE_REPRESENTATION",
        "PRESERVE_EXECUTION",
        "PRESERVE_MEASUREMENT",
        "PRESERVE_OBJECTIVE",
        "PRESERVE_BOUNDARY",
    )
    common = ("RESPONSIBILITY_IDENTIFIED", "INTERFACE_CHECKED")
    broad_low = ("K:evidence", "K:representation", "M:execution", "K:measurement")
    return {
        CONTROL: build_mechanic(
            mechanic_id=CLASS_TO_MECHANIC[CONTROL],
            claim_id=claim_id,
            kind="PRESERVE_CURRENT_FORMULATION",
            read_coordinates=("K", "W", "M"),
            write_coordinates=(),
            preconditions=common,
            preservation_obligations=preserve_all,
            cost=0.0,
        ),
        "SEARCH_OR_EVIDENCE": build_mechanic(
            mechanic_id=CLASS_TO_MECHANIC["SEARCH_OR_EVIDENCE"],
            claim_id=claim_id,
            kind="EVIDENCE_REPAIR",
            read_coordinates=("K:evidence", "W:objective", "W:boundary"),
            write_coordinates=("K:evidence",),
            preconditions=common,
            preservation_obligations=("PRESERVE_OBJECTIVE", "PRESERVE_BOUNDARY"),
            cost=1.0,
        ),
        "REPRESENTATION_OR_INTERFACE": build_mechanic(
            mechanic_id=CLASS_TO_MECHANIC["REPRESENTATION_OR_INTERFACE"],
            claim_id=claim_id,
            kind="INTERFACE_REPAIR",
            read_coordinates=("K:representation", "W:objective", "W:boundary"),
            write_coordinates=("K:representation",),
            preconditions=common,
            preservation_obligations=("PRESERVE_OBJECTIVE", "PRESERVE_BOUNDARY"),
            cost=1.0,
        ),
        "IMPLEMENTATION_OR_ENVIRONMENT": build_mechanic(
            mechanic_id=CLASS_TO_MECHANIC["IMPLEMENTATION_OR_ENVIRONMENT"],
            claim_id=claim_id,
            kind="EXECUTION_REPAIR",
            read_coordinates=("M:execution", "W:objective", "W:boundary"),
            write_coordinates=("M:execution",),
            preconditions=common,
            preservation_obligations=("PRESERVE_OBJECTIVE", "PRESERVE_BOUNDARY"),
            cost=1.0,
        ),
        "MEASUREMENT_OR_EVALUATOR": build_mechanic(
            mechanic_id=CLASS_TO_MECHANIC["MEASUREMENT_OR_EVALUATOR"],
            claim_id=claim_id,
            kind="MEASUREMENT_INTERFACE_REPAIR",
            read_coordinates=("K:measurement", "W:objective", "W:boundary"),
            write_coordinates=("K:measurement",),
            preconditions=common,
            preservation_obligations=("PRESERVE_OBJECTIVE", "PRESERVE_BOUNDARY"),
            cost=1.0,
        ),
        "OBJECTIVE_OR_MODEL_CLASS": build_mechanic(
            mechanic_id=CLASS_TO_MECHANIC["OBJECTIVE_OR_MODEL_CLASS"],
            claim_id=claim_id,
            kind="OBJECTIVE_REVISION",
            read_coordinates=("K", "W", "M"),
            write_coordinates=(*broad_low, "W:objective"),
            preconditions=common,
            preservation_obligations=("PRESERVE_BOUNDARY",),
            cost=2.0,
        ),
        "PROBLEM_BOUNDARY": build_mechanic(
            mechanic_id=CLASS_TO_MECHANIC["PROBLEM_BOUNDARY"],
            claim_id=claim_id,
            kind="BOUNDARY_REVISION",
            read_coordinates=("K", "W", "M"),
            write_coordinates=(*broad_low, "W:objective", "W:boundary"),
            preconditions=common,
            preservation_obligations=(),
            cost=3.0,
        ),
    }


def _bindings_for_class(cls: str) -> tuple[str, ...]:
    if cls == CONTROL:
        return (
            CLASS_TO_MECHANIC[CONTROL],
            CLASS_TO_MECHANIC["OBJECTIVE_OR_MODEL_CLASS"],
            CLASS_TO_MECHANIC["PROBLEM_BOUNDARY"],
        )
    if cls in LOW:
        return (
            CLASS_TO_MECHANIC[cls],
            CLASS_TO_MECHANIC["OBJECTIVE_OR_MODEL_CLASS"],
            CLASS_TO_MECHANIC["PROBLEM_BOUNDARY"],
        )
    if cls == "OBJECTIVE_OR_MODEL_CLASS":
        return (
            CLASS_TO_MECHANIC["OBJECTIVE_OR_MODEL_CLASS"],
            CLASS_TO_MECHANIC["PROBLEM_BOUNDARY"],
        )
    if cls == "PROBLEM_BOUNDARY":
        return (CLASS_TO_MECHANIC["PROBLEM_BOUNDARY"],)
    raise KeyError(cls)


def _assess_all(mechanics):
    states = {
        "RESPONSIBILITY_IDENTIFIED": ObligationState.SATISFIED,
        "INTERFACE_CHECKED": ObligationState.SATISFIED,
    }
    assessments = tuple(
        assess_mechanic(mechanic, obligation_states=states)
        for mechanic in mechanics.values()
    )
    if not all(item.status is AssessmentStatus.ADMISSIBLE for item in assessments):
        raise AssertionError("frozen candidate mechanics must be formally admissible for nomination")
    return assessments


def _interface_from_observations(
    selected: tuple[tuple[str, str], ...],
    *,
    source_evidence_id: str,
) -> InterfaceAdequacyReport:
    checks = [
        build_interface_check(
            check_id="interface:source-projection",
            scope="source_projection_binding",
            state=InterfaceCheckState.PASS,
            evidence_ids=(source_evidence_id,),
        )
    ]
    for probe, observation in selected:
        cls = PROBE_TO_CLASS[probe]
        if cls not in {"REPRESENTATION_OR_INTERFACE", "MEASUREMENT_OR_EVALUATOR"}:
            continue
        if observation == "SUPPORT":
            state = InterfaceCheckState.FAIL
        elif observation == "REFUTE":
            state = InterfaceCheckState.PASS
        else:
            state = InterfaceCheckState.UNRESOLVED
        checks.append(
            build_interface_check(
                check_id="interface:" + probe.lower(),
                scope=(
                    "representation_interface"
                    if cls == "REPRESENTATION_OR_INTERFACE"
                    else "measurement_evaluator_interface"
                ),
                state=state,
                evidence_ids=(source_evidence_id,),
            )
        )
    return assess_interface_adequacy(tuple(checks))


def _base_responsibility(claim_id: str, diagnosis_token: str | None) -> ResponsibilityReport:
    hypotheses = tuple(
        build_responsibility_hypothesis(
            hypothesis_id="responsibility:base:" + cls.lower(),
            claim_id=claim_id,
            expected_observations={"D_RUNTIME_DIAGNOSIS": (token,)},
        )
        for cls, token in CLASS_TO_NATIVE.items()
    )
    observed = {} if diagnosis_token is None else {"D_RUNTIME_DIAGNOSIS": diagnosis_token}
    return assess_responsibility(hypotheses, observed_outcomes=observed)


def _ard_responsibility(
    claim_id: str,
    first_probe: str,
    second_probe: str,
    observations: Mapping[str, str],
) -> tuple[ResponsibilityReport, dict[str, str]]:
    first_cls = PROBE_TO_CLASS[first_probe]
    second_cls = PROBE_TO_CLASS[second_probe]
    ids = {
        "first": "responsibility:ard:first",
        "second": "responsibility:ard:second",
        "control": "responsibility:ard:control",
    }
    hypotheses = (
        build_responsibility_hypothesis(
            hypothesis_id=ids["first"],
            claim_id=claim_id,
            expected_observations={first_probe: ("SUPPORT",)},
        ),
        build_responsibility_hypothesis(
            hypothesis_id=ids["second"],
            claim_id=claim_id,
            expected_observations={
                first_probe: ("REFUTE", "INCONCLUSIVE"),
                second_probe: ("SUPPORT",),
            },
        ),
        build_responsibility_hypothesis(
            hypothesis_id=ids["control"],
            claim_id=claim_id,
            expected_observations={first_probe: ("REFUTE",), second_probe: ("REFUTE",)},
        ),
        build_responsibility_hypothesis(
            hypothesis_id="responsibility:ard:unresolved:a",
            claim_id=claim_id,
            expected_observations={
                first_probe: ("INCONCLUSIVE",),
                second_probe: ("INCONCLUSIVE",),
                "D_TIEBREAKER": ("A",),
            },
        ),
        build_responsibility_hypothesis(
            hypothesis_id="responsibility:ard:unresolved:b",
            claim_id=claim_id,
            expected_observations={
                first_probe: ("INCONCLUSIVE",),
                second_probe: ("INCONCLUSIVE",),
                "D_TIEBREAKER": ("B",),
            },
        ),
    )
    report = assess_responsibility(hypotheses, observed_outcomes=observations)
    classes = {ids["first"]: first_cls, ids["second"]: second_cls, ids["control"]: CONTROL}
    return report, classes


def _gate_choice(
    claim_id: str,
    responsibility: ResponsibilityReport,
    responsibility_classes: Mapping[str, str],
    interface: InterfaceAdequacyReport,
):
    mechanics = _mechanics(claim_id)
    assessments = _assess_all(mechanics)
    bindings = {
        hypothesis_id: _bindings_for_class(cls)
        for hypothesis_id, cls in responsibility_classes.items()
    }
    repair_ids: tuple[str, ...] = ()
    interface_coordinates: tuple[str, ...] = ()
    if responsibility.status is ResponsibilityStatus.IDENTIFIED:
        cls = responsibility_classes.get(str(responsibility.identified_hypothesis_id))
        if cls == "REPRESENTATION_OR_INTERFACE":
            repair_ids = (CLASS_TO_MECHANIC[cls],)
            interface_coordinates = ("K:representation",)
        elif cls == "MEASUREMENT_OR_EVALUATOR":
            repair_ids = (CLASS_TO_MECHANIC[cls],)
            interface_coordinates = ("K:measurement",)
    gate = assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=tuple(mechanics.values()),
        assessments=assessments,
        responsibility_bindings=bindings,
        interface_repair_mechanic_ids=repair_ids,
        interface_coordinates=interface_coordinates,
    )
    if gate.status is RevisionGateStatus.CANDIDATE_SELECTED:
        choice = MECHANIC_TO_CLASS[str(gate.selected_mechanic_id)]
    else:
        choice = UNRESOLVED
    return choice, gate, mechanics, assessments


def _native_base(
    claim_id: str,
    diagnosis_token: str | None,
    source_evidence_id: str,
):
    responsibility = _base_responsibility(claim_id, diagnosis_token)
    interface = _interface_from_observations((), source_evidence_id=source_evidence_id)
    classes = {
        "responsibility:base:" + cls.lower(): cls for cls in CLASS_TO_NATIVE
    }
    choice, gate, mechanics, assessments = _gate_choice(
        claim_id, responsibility, classes, interface
    )
    return choice, responsibility, interface, gate, mechanics, assessments


def _native_ard(
    claim_id: str,
    dossier: str,
    probes: ProbeGate,
    source_evidence_id: str,
):
    first_cls = semantic_first_class(dossier)
    first_probe = CLASS_TO_PROBE[first_cls]
    if first_cls == "OBJECTIVE_OR_MODEL_CLASS":
        second_probe = CLASS_TO_PROBE["PROBLEM_BOUNDARY"]
    else:
        second_probe = CLASS_TO_PROBE["OBJECTIVE_OR_MODEL_CLASS"]
    if second_probe == first_probe:
        raise AssertionError("ARD probes must be distinct")
    first_obs = probes[first_probe]
    second_obs = probes[second_probe]
    selected = ((first_probe, first_obs), (second_probe, second_obs))
    responsibility, classes = _ard_responsibility(
        claim_id,
        first_probe,
        second_probe,
        dict(selected),
    )
    interface = _interface_from_observations(
        selected, source_evidence_id=source_evidence_id
    )
    choice, gate, mechanics, assessments = _gate_choice(
        claim_id, responsibility, classes, interface
    )
    return choice, selected, responsibility, interface, gate, mechanics, assessments


def run_native_episode(
    *,
    dossier: str,
    source_uri: str,
    hidden_probes: Mapping[str, str],
    max_replays: int = 24,
) -> dict[str, object]:
    """Run one candidate-visible episode through canonical ORION and the native P1 adapter.

    The function intentionally has no gold label, pair role, source class, query ID, or evaluator
    disposition parameter. Those fields cannot cross this candidate boundary.
    """

    claim_id = "p1-r6:" + _digest(dossier)[:24]
    problem_id = "p1r6-" + _digest("problem|" + dossier)[:24]
    source_evidence_id = "source-projection:" + _digest(source_uri)[:24]
    host = HarnessHost(dossier, source_uri, [], [])
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        workspace = ResearchWorkspace.initialize(root / "workspace", project_root=root)
        problem = {
            "problem_id": problem_id,
            "question": "What is the narrowest defensible next scientific revision?",
            "scope": (
                dossier
                + " Use only this fixed source-grounded projection. Preserve uncertainty and do "
                "not broaden the objective or problem boundary without protected evidence."
            ),
            "initial_domain_ids": ["scientific_case"],
            "success_criteria": [
                "Use canonical ORION runtime receipts.",
                "Do not escalate beyond evidence.",
            ],
        }
        for _ in range(max_replays):
            outcome = run_problem(
                workspace,
                problem,
                max_iterations=2,
                require_verified_answer=True,
            )
            if outcome["status"] == "COMPLETE":
                break
            if outcome["status"] == "HOST_CAPABILITY_FAILED":
                raise AssertionError(outcome)
            host.service(workspace, CapabilityRequest.from_dict(outcome["request"]))
        else:
            raise AssertionError("canonical harness replay did not terminate")

        if outcome["status"] != "COMPLETE":
            raise AssertionError(outcome)
        run_record = workspace.load_run(str(outcome["run_id"]))
        trace = run_record["trace"]
        events = list(trace["events"])
        if not events:
            raise AssertionError("native runtime trace is empty")
        operators = list(outcome["operator_sequence"])
        for required in ("FRAME", "SEARCH", "ABSORB", "RECONSTRUCT"):
            if required not in operators:
                raise AssertionError(f"required native operator absent: {required}")
        receipt_ids = [str(event["receipt"]["receipt_id"]) for event in events]
        if len(receipt_ids) != len(set(receipt_ids)):
            raise AssertionError("runtime receipt identities are not unique")
        for event in events:
            if not _hex64(str(event["pre_state_hash"])) or not _hex64(str(event["post_state_hash"])):
                raise AssertionError("runtime state endpoint is not SHA-256 bound")
        final_state_digest = _digest(
            json.dumps(run_record["final_state"], sort_keys=True, separators=(",", ":"))
        )

        diagnosis_token = host.diagnosis_tokens[-1] if host.diagnosis_tokens else None
        base = _native_base(claim_id, diagnosis_token, source_evidence_id)
        base_choice, base_resp, base_interface, base_gate, base_mechanics, base_assess = base

        probe_gate = ProbeGate(hidden_probes)
        ard = _native_ard(claim_id, dossier, probe_gate, source_evidence_id)
        ard_choice, ard_selected, ard_resp, ard_interface, ard_gate, ard_mechanics, ard_assess = ard
        if len(probe_gate.revealed) > int(PROTOCOL["budget"]):
            raise AssertionError("ARD exceeded the frozen action budget")
        if tuple(probe_gate.revealed) != tuple(ard_selected):
            raise AssertionError("ARD trace does not match hidden-probe accesses")

        for gate in (base_gate, ard_gate):
            if gate.grants_adoption_authority or gate.grants_promotion_authority or gate.grants_merge_authority:
                raise AssertionError("native revision gate leaked authority")

        return {
            "schema": "P1U.R6NativeEpisode.v1",
            "claim_id": claim_id,
            "runtime": {
                "trace_id": outcome["trace_id"],
                "operator_sequence": operators,
                "receipt_ids": receipt_ids,
                "pre_state_hash": events[0]["pre_state_hash"],
                "post_state_hash": events[-1]["post_state_hash"],
                "final_state_digest": final_state_digest,
                "solution_status": outcome["solution_status"],
            },
            "base": {
                "choice": base_choice,
                "diagnosis_token": diagnosis_token,
                "responsibility_status": base_resp.status.value,
                "responsibility_digest": base_resp.digest,
                "interface_status": base_interface.status.value,
                "interface_digest": base_interface.digest,
                "revision_gate_status": base_gate.status.value,
                "revision_gate_digest": base_gate.digest,
                "mechanic_digests": sorted(item.digest for item in base_mechanics.values()),
                "assessment_digests": sorted(item.digest for item in base_assess),
            },
            "ard": {
                "choice": ard_choice,
                "probe_trace": [list(item) for item in ard_selected],
                "cost": len(ard_selected),
                "responsibility_status": ard_resp.status.value,
                "responsibility_digest": ard_resp.digest,
                "interface_status": ard_interface.status.value,
                "interface_digest": ard_interface.digest,
                "revision_gate_status": ard_gate.status.value,
                "revision_gate_digest": ard_gate.digest,
                "mechanic_digests": sorted(item.digest for item in ard_mechanics.values()),
                "assessment_digests": sorted(item.digest for item in ard_assess),
            },
            "request_payloads": host.request_payloads,
        }
