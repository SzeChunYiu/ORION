from __future__ import annotations

from dataclasses import asdict, dataclass

from .defeaters import Defeater, DefeaterPlanner, EvidenceAction
from .diagnosis import DiagnosticProbe, ResponsibilityDiagnoser, ResponsibilityHypothesis
from .discovery import ConservativeRouteAllocator
from .lenses import AffineLens, ConsistencyStatus, LensEdge, ScientificLensNetwork
from .staging import (
    CandidateRecord,
    CandidateVerdict,
    MultiStageCandidateGate,
    Stage,
    StageResult,
    StageVerdict,
)


@dataclass(frozen=True)
class ToyBenchmarkResult:
    paper: str
    mechanism: str
    baseline_value: float
    mechanism_value: float
    improvement: float
    passed: bool
    note: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def p1_active_diagnosis_toy() -> ToyBenchmarkResult:
    passive = ResponsibilityDiagnoser(
        [
            ResponsibilityHypothesis("evidence", 1.0),
            ResponsibilityHypothesis("execution", 1.0),
            ResponsibilityHypothesis("formulation", 1.0),
        ]
    )
    active = ResponsibilityDiagnoser(
        [
            ResponsibilityHypothesis("evidence", 1.0),
            ResponsibilityHypothesis("execution", 1.0),
            ResponsibilityHypothesis("formulation", 1.0),
        ]
    )
    probe = DiagnosticProbe(
        "active-representation-probe",
        {"evidence": 0.05, "execution": 0.05, "formulation": 0.98},
    )
    baseline = float(passive.licenses({"formulation"}, threshold=0.8))
    active.observe(probe, positive=True)
    mechanism = float(active.licenses({"formulation"}, threshold=0.8))
    return ToyBenchmarkResult(
        paper="P1",
        mechanism="responsibility-diagnosability-active-probe",
        baseline_value=baseline,
        mechanism_value=mechanism,
        improvement=mechanism - baseline,
        passed=mechanism > baseline,
        note="Known formulation fault is licensable only after a discriminating probe.",
    )


def p2_conservative_discovery_toy() -> ToyBenchmarkResult:
    allocator = ConservativeRouteAllocator(
        baseline_route="bm25", baseline_lower_bound=1.0, alpha=0.5
    )
    allocator.register("far-route")
    mechanism_reward = 0.0
    allocator.record("bm25", reward=1.0)
    mechanism_reward += 1.0
    selected = allocator.select()
    if selected != "far-route":
        raise AssertionError("toy world should earn enough safety credit to explore")
    allocator.record("far-route", reward=3.0, lower_bound=0.0)
    mechanism_reward += 3.0
    baseline_reward = 2.0
    return ToyBenchmarkResult(
        paper="P2",
        mechanism="conservative-censored-route-allocation",
        baseline_value=baseline_reward,
        mechanism_value=mechanism_reward,
        improvement=mechanism_reward - baseline_reward,
        passed=mechanism_reward > baseline_reward and allocator.safety_credit >= -1e-12,
        note="Exploration wins in the constructed world while the declared safety floor remains intact.",
    )


def p3_scientific_lens_toy() -> ToyBenchmarkResult:
    c_to_f = AffineLens(9 / 5, 32)
    c_to_k = AffineLens(1.0, 273.15)
    f_to_k = c_to_f.inverse().then(c_to_k)
    network = ScientificLensNetwork(
        [
            LensEdge("C", "F", c_to_f),
            LensEdge("F", "K", f_to_k),
            LensEdge("C", "K", c_to_k),
        ]
    )
    status = network.assess_cycle(["C", "F", "K", "C"], [-40.0, 0.0, 100.0])
    naive_false_contradiction = float(0.0 != 32.0)
    lens_false_contradiction = float(status is not ConsistencyStatus.GLOBALIZABLE)
    return ToyBenchmarkResult(
        paper="P3",
        mechanism="round-trip-scientific-lens-consistency",
        baseline_value=naive_false_contradiction,
        mechanism_value=lens_false_contradiction,
        improvement=naive_false_contradiction - lens_false_contradiction,
        passed=lens_false_contradiction < naive_false_contradiction,
        note="Typed transformation preserves a scientifically equivalent measurement across views.",
    )


def p4_defeater_planning_toy() -> ToyBenchmarkResult:
    defeaters = [Defeater("wrong-source", 0.9), Defeater("contamination", 0.8)]
    cheap = EvidenceAction(
        "cheap-format-check",
        frozenset({"wrong-source"}),
        success_probability=0.2,
        cost=1.0,
    )
    targeted = EvidenceAction(
        "protected-source-and-contamination-check",
        frozenset({"wrong-source", "contamination"}),
        success_probability=0.9,
        cost=2.0,
    )
    planner = DefeaterPlanner()
    selected = planner.choose_action(defeaters, [cheap, targeted])
    if selected is None:
        raise AssertionError("toy planner should select an evidence action")
    baseline_expected_reduction = 0.9 * 0.2
    mechanism_expected_reduction = (0.9 + 0.8) * 0.9
    return ToyBenchmarkResult(
        paper="P4",
        mechanism="defeater-directed-protected-evidence-acquisition",
        baseline_value=baseline_expected_reduction,
        mechanism_value=mechanism_expected_reduction,
        improvement=mechanism_expected_reduction - baseline_expected_reduction,
        passed=(
            selected.action_id == targeted.action_id
            and mechanism_expected_reduction > baseline_expected_reduction
        ),
        note="Planner spends evidence budget on the protected action with larger expected authority-risk reduction.",
    )


def p5_multistage_gate_toy() -> ToyBenchmarkResult:
    gate = MultiStageCandidateGate()
    harmful = CandidateRecord("replay-overfit")
    harmful.record(StageResult(Stage.STATIC, StageVerdict.PASS))
    harmful.record(StageResult(Stage.REPLAY, StageVerdict.PASS, score_delta=10.0))
    harmful.record(
        StageResult(Stage.FRESH, StageVerdict.FAIL, score_delta=-1.0, harmful=True)
    )
    greedy_replay_only_accepts = 1.0
    governed_accepts = float(gate.evaluate(harmful) is CandidateVerdict.RECOMMEND_HOST_PROMOTION)
    return ToyBenchmarkResult(
        paper="P5",
        mechanism="noncompensatory-multistage-evidence-gate",
        baseline_value=greedy_replay_only_accepts,
        mechanism_value=governed_accepts,
        improvement=greedy_replay_only_accepts - governed_accepts,
        passed=governed_accepts < greedy_replay_only_accepts,
        note="Fresh harm blocks a replay-overfit candidate regardless of its large replay gain.",
    )


def run_all_toys() -> tuple[ToyBenchmarkResult, ...]:
    return (
        p1_active_diagnosis_toy(),
        p2_conservative_discovery_toy(),
        p3_scientific_lens_toy(),
        p4_defeater_planning_toy(),
        p5_multistage_gate_toy(),
    )


if __name__ == "__main__":
    import json

    print(json.dumps([result.to_dict() for result in run_all_toys()], indent=2, sort_keys=True))
