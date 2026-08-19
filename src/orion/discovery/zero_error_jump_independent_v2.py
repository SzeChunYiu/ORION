"""Independent V2 reconstruction for the leak-resistant #501 benchmark.

This verifier does not call/import the main V2 ``score_split`` or aggregate
benchmark-report builder. It regenerates frozen worlds, executes registered
policies, and independently reconstructs protected metrics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from orion.transfer.v2.canonical import content_digest
from orion.discovery.zero_error_jump_benchmark_v2 import (
    JumpArm,
    RepresentationMove,
    ZeroErrorJumpTerminal,
    generate_jump_worlds,
    propose,
    prove_old_regime,
)


@dataclass(frozen=True)
class IndependentArmMetrics:
    structural_decision_correct: int
    positive_jump_success: int
    control_no_jump_correct: int
    false_jump_on_control: int
    old_regime_insufficiency_correct: int
    correspondence_success: int
    protected_consequence_success: int
    thought_experiment_success: int
    unresolved_or_rejected: int
    authority_violations: int
    decision_keys: tuple[tuple[object, ...], ...]

    def payload(self) -> dict[str, int]:
        return {
            "structural_decision_correct": self.structural_decision_correct,
            "positive_jump_success": self.positive_jump_success,
            "control_no_jump_correct": self.control_no_jump_correct,
            "false_jump_on_control": self.false_jump_on_control,
            "old_regime_insufficiency_correct": self.old_regime_insufficiency_correct,
            "correspondence_success": self.correspondence_success,
            "protected_consequence_success": self.protected_consequence_success,
            "thought_experiment_success": self.thought_experiment_success,
            "unresolved_or_rejected": self.unresolved_or_rejected,
            "authority_violations": self.authority_violations,
        }


@dataclass(frozen=True)
class IndependentSplitVerification:
    split_id: str
    seed: int
    case_ids: tuple[str, ...]
    positive_count: int
    control_count: int
    old_insufficient_count: int
    control_old_solution_minimum: int
    metrics: tuple[tuple[JumpArm, IndependentArmMetrics], ...]

    def metric(self, arm: JumpArm) -> IndependentArmMetrics:
        return next(metric for row_arm, metric in self.metrics if row_arm is arm)


@dataclass(frozen=True)
class IndependentJumpVerificationReport:
    primary: IndependentSplitVerification
    replication: IndependentSplitVerification
    parent_orion_decisions_equal_primary: bool
    parent_orion_decisions_equal_replication: bool
    parent_orion_metrics_equal_primary: bool
    parent_orion_metrics_equal_replication: bool
    terminal: ZeroErrorJumpTerminal
    expected_match: bool
    digest: str

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        def split_payload(split: IndependentSplitVerification) -> dict[str, object]:
            return {
                "split_id": split.split_id,
                "seed": split.seed,
                "case_ids": list(split.case_ids),
                "positive_count": split.positive_count,
                "control_count": split.control_count,
                "old_insufficient_count": split.old_insufficient_count,
                "control_old_solution_minimum": split.control_old_solution_minimum,
                "metrics": {arm.value: metric.payload() for arm, metric in split.metrics},
            }
        return {
            "version": "IndependentZeroErrorJumpVerification.v2",
            "primary": split_payload(self.primary),
            "replication": split_payload(self.replication),
            "parent_orion_decisions_equal_primary": self.parent_orion_decisions_equal_primary,
            "parent_orion_decisions_equal_replication": self.parent_orion_decisions_equal_replication,
            "parent_orion_metrics_equal_primary": self.parent_orion_metrics_equal_primary,
            "parent_orion_metrics_equal_replication": self.parent_orion_metrics_equal_replication,
            "terminal": self.terminal.value,
            "expected_match": self.expected_match,
            "grants_scientific_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("independent V2 Jump verification digest mismatch")


def _score_split_independently(*, split_id: str, seed: int) -> IndependentSplitVerification:
    worlds = generate_jump_worlds(seed=seed, split_id=split_id)
    proofs = tuple(prove_old_regime(world) for world in worlds)
    rows: list[tuple[JumpArm, IndependentArmMetrics]] = []

    for arm in JumpArm:
        correct = positive_success = control_correct = false_jump = 0
        insufficiency = correspondence = consequence = thought = unresolved = authority = 0
        decisions: list[tuple[object, ...]] = []

        for world, proof in zip(worlds, proofs):
            proposal = propose(world, arm)
            decisions.append(proposal.decision_key())
            authority_bad = bool(proposal.claims_scientific_authority)
            authority += int(authority_bad)

            if world.is_jump_case:
                insufficiency += int(
                    proof.old_regime_insufficient
                    and proposal.recognizes_old_regime_insufficiency
                )
                informative = (
                    proposal.selected_experiment_id == world.informative_experiment_id
                )
                thought += int(informative)
                move_ok = proposal.representation_move is world.gold_representation_move
                corr_ok = move_ok and proposal.correspondence_complete
                cons_ok = (
                    move_ok
                    and proposal.protected_consequence_prediction
                    == world.protected_novel_consequence_token
                )
                correspondence += int(corr_ok)
                consequence += int(cons_ok)
                success = (
                    proof.old_regime_insufficient
                    and proposal.jump_requested
                    and move_ok
                    and informative
                    and corr_ok
                    and cons_ok
                    and not authority_bad
                )
                positive_success += int(success)
                correct += int(success)
                unresolved += int(not success)
            else:
                false_jump += int(proposal.jump_requested)
                no_jump_ok = (
                    not proof.old_regime_insufficient
                    and not proposal.jump_requested
                    and proposal.representation_move
                    is RepresentationMove.NO_REPRESENTATION_CHANGE
                    and proposal.old_regime_action_id == "KEEP_OLD_REGIME"
                    and not authority_bad
                )
                control_correct += int(no_jump_ok)
                correct += int(no_jump_ok)

        rows.append(
            (
                arm,
                IndependentArmMetrics(
                    structural_decision_correct=correct,
                    positive_jump_success=positive_success,
                    control_no_jump_correct=control_correct,
                    false_jump_on_control=false_jump,
                    old_regime_insufficiency_correct=insufficiency,
                    correspondence_success=correspondence,
                    protected_consequence_success=consequence,
                    thought_experiment_success=thought,
                    unresolved_or_rejected=unresolved,
                    authority_violations=authority,
                    decision_keys=tuple(decisions),
                ),
            )
        )

    control_counts = [
        len(proof.full_contract_solution_ids)
        for world, proof in zip(worlds, proofs)
        if not world.is_jump_case
    ]
    return IndependentSplitVerification(
        split_id=split_id,
        seed=seed,
        case_ids=tuple(world.case_id for world in worlds),
        positive_count=sum(int(world.is_jump_case) for world in worlds),
        control_count=sum(int(not world.is_jump_case) for world in worlds),
        old_insufficient_count=sum(
            int(world.is_jump_case and proof.old_regime_insufficient)
            for world, proof in zip(worlds, proofs)
        ),
        control_old_solution_minimum=min(control_counts),
        metrics=tuple(rows),
    )


def _matches_expected(
    split: IndependentSplitVerification,
    *, split_expected: Mapping[str, object], per_arm: Mapping[str, object]
) -> bool:
    if (
        split.seed != int(split_expected["seed"])
        or len(split.case_ids) != int(split_expected["cases"])
        or split.positive_count != int(split_expected["positive_cases"])
        or split.control_count != int(split_expected["control_cases"])
    ):
        return False
    for arm in JumpArm:
        expected_metric = per_arm.get(arm.value)
        if not isinstance(expected_metric, Mapping):
            return False
        if split.metric(arm).payload() != {
            str(key): int(value) for key, value in expected_metric.items()
        }:
            return False
    return True


def independently_verify_zero_error_jump(
    *, protocol: Mapping[str, object], expected: Mapping[str, object]
) -> IndependentJumpVerificationReport:
    if protocol.get("version") != "ZeroErrorJumpProtocol.v2":
        raise ValueError("independent V2 verifier requires V2 protocol")
    if protocol.get("outcome_accessed") is not False:
        raise ValueError("independent V2 verifier refuses outcome-accessed freeze")
    if expected.get("version") != "ZeroErrorJumpExpected.v2":
        raise ValueError("independent V2 verifier requires V2 expected table")
    seeds = protocol.get("seeds")
    split_expected = expected.get("split_expectations")
    per_arm = expected.get("per_split_arm_metrics")
    if not isinstance(seeds, Mapping) or not isinstance(split_expected, Mapping) or not isinstance(per_arm, Mapping):
        raise ValueError("V2 protocol/expected tables are incomplete")

    primary = _score_split_independently(
        split_id="primary", seed=int(seeds["primary"])
    )
    replication = _score_split_independently(
        split_id="replication", seed=int(seeds["replication"])
    )
    p_parent = primary.metric(JumpArm.VERIFIED_REGIME_REVISION_PARENT)
    p_orion = primary.metric(JumpArm.ORION_JUMP)
    r_parent = replication.metric(JumpArm.VERIFIED_REGIME_REVISION_PARENT)
    r_orion = replication.metric(JumpArm.ORION_JUMP)
    decisions_p = p_parent.decision_keys == p_orion.decision_keys
    decisions_r = r_parent.decision_keys == r_orion.decision_keys
    metrics_p = p_parent.payload() == p_orion.payload()
    metrics_r = r_parent.payload() == r_orion.payload()

    expected_match = (
        _matches_expected(primary, split_expected=split_expected["primary"], per_arm=per_arm)
        and _matches_expected(
            replication, split_expected=split_expected["replication"], per_arm=per_arm
        )
        and primary.old_insufficient_count == 24
        and replication.old_insufficient_count == 24
        and primary.control_old_solution_minimum >= 1
        and replication.control_old_solution_minimum >= 1
        and decisions_p
        and decisions_r
        and metrics_p
        and metrics_r
    )
    terminal = (
        ZeroErrorJumpTerminal.REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE
        if expected_match
        and expected.get("candidate_terminal")
        == ZeroErrorJumpTerminal.REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE.value
        else ZeroErrorJumpTerminal.CANNOT_CHECK
    )
    temp = IndependentJumpVerificationReport(
        primary,
        replication,
        decisions_p,
        decisions_r,
        metrics_p,
        metrics_r,
        terminal,
        expected_match,
        "",
    )
    report = IndependentJumpVerificationReport(
        primary=temp.primary,
        replication=temp.replication,
        parent_orion_decisions_equal_primary=temp.parent_orion_decisions_equal_primary,
        parent_orion_decisions_equal_replication=temp.parent_orion_decisions_equal_replication,
        parent_orion_metrics_equal_primary=temp.parent_orion_metrics_equal_primary,
        parent_orion_metrics_equal_replication=temp.parent_orion_metrics_equal_replication,
        terminal=temp.terminal,
        expected_match=temp.expected_match,
        digest=content_digest(temp.unsigned()),
    )
    report.verify()
    return report


__all__ = [
    "IndependentArmMetrics",
    "IndependentJumpVerificationReport",
    "IndependentSplitVerification",
    "independently_verify_zero_error_jump",
]
