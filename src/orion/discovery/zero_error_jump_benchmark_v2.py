"""Leak-resistant V2 zero-error Jump benchmark for #501.

V2 supersedes the V1 runner after review found pre-experiment protected-class
leakage.  Candidate-visible cases now have class-balanced cardinalities, opaque
case IDs, no public family/tension label, and a uniform two-probe menu.  A
candidate chooses a probe solely by overlap between opaque public discriminator
obligations and the probe's opaque coverage.  Only the resulting experiment
outcome may provide evidence for a representation move or old-regime
sufficiency.

The strong verified regime-revision parent and ORION receive identical public
bytes and resources.  Exact old-language insufficiency remains evaluator-side
finite proof, not a candidate-visible class label.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
from typing import Mapping

from orion.transfer.v2.canonical import content_digest


class RepresentationMove(str, Enum):
    NO_REPRESENTATION_CHANGE = "NO_REPRESENTATION_CHANGE"
    BRIDGE_CORRESPONDENCE = "BRIDGE_CORRESPONDENCE"
    FRAME_COORDINATE = "FRAME_COORDINATE"
    INVARIANT_ORBIT = "INVARIANT_ORBIT"
    RELATIONAL_LIFT = "RELATIONAL_LIFT"
    CAUSAL_SPLIT = "CAUSAL_SPLIT"
    BRIDGE_LAW = "BRIDGE_LAW"


class JumpArm(str, Enum):
    OLD_DSL_EXHAUSTIVE = "OLD_DSL_EXHAUSTIVE"
    M_OPEN_SAME_REPRESENTATION = "M_OPEN_SAME_REPRESENTATION"
    FIXED_REP_WORLD_MODEL = "FIXED_REP_WORLD_MODEL"
    VERIFIED_REGIME_REVISION_PARENT = "VERIFIED_REGIME_REVISION_PARENT"
    ORION_JUMP = "ORION_JUMP"
    ORION_NO_CORRESPONDENCE = "ORION_NO_CORRESPONDENCE"
    OVERJUMP_ALWAYS = "OVERJUMP_ALWAYS"
    ORACLE = "ORACLE"


class ZeroErrorJumpTerminal(str, Enum):
    REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE = (
        "REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE"
    )
    CANNOT_CHECK = "CANNOT_CHECK"


_POSITIVE_FAMILIES: tuple[tuple[str, RepresentationMove], ...] = (
    ("A_ZERO_ERROR_UNIFICATION", RepresentationMove.BRIDGE_CORRESPONDENCE),
    ("B_COUNTERFACTUAL_FRAME", RepresentationMove.FRAME_COORDINATE),
    ("C_HIDDEN_SYMMETRY", RepresentationMove.INVARIANT_ORBIT),
    ("D_RELATIONAL_LIFT", RepresentationMove.RELATIONAL_LIFT),
    ("E_CAUSAL_OBJECT", RepresentationMove.CAUSAL_SPLIT),
    ("F_BRIDGE_LAW", RepresentationMove.BRIDGE_LAW),
)

_CONTROL_FAMILIES = (
    "PARAMETER_UPDATE_SUFFICIENT",
    "FIXED_LANGUAGE_STRUCTURE_SUFFICIENT",
    "ADDITIONAL_EVIDENCE_SUFFICIENT",
    "NO_CHANGE_NEEDED",
    "MEASUREMENT_REPAIR_SUFFICIENT",
    "SEARCH_HARD_BUT_EXPRESSIBLE",
)

_MOVE_TO_EVIDENCE_CODE = {
    RepresentationMove.BRIDGE_CORRESPONDENCE: "E0",
    RepresentationMove.FRAME_COORDINATE: "E1",
    RepresentationMove.INVARIANT_ORBIT: "E2",
    RepresentationMove.RELATIONAL_LIFT: "E3",
    RepresentationMove.CAUSAL_SPLIT: "E4",
    RepresentationMove.BRIDGE_LAW: "E5",
}
_EVIDENCE_CODE_TO_MOVE = {value: key for key, value in _MOVE_TO_EVIDENCE_CODE.items()}

_BANNED_TERMS = (
    "relativity",
    "ether",
    "dna",
    "quantum",
    "newton",
    "einstein",
    "mendeleev",
    "noether",
    "turing",
    "darwin",
    "maxwell",
)


def _opaque(seed: int, *parts: object, prefix: str) -> str:
    raw = "|".join([str(seed), *(str(part) for part in parts)])
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12]}"


def _case_id(seed: int, split_id: str, ordinal: int) -> str:
    return _opaque(seed, split_id, "case", ordinal, prefix="case")


def _consequence_token(
    *, case_id: str, move: RepresentationMove, outcome_signature: str, anchor_id: str
) -> str:
    raw = f"{case_id}|{move.value}|{outcome_signature}|{anchor_id}"
    return "pc_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class ThoughtExperimentOption:
    experiment_id: str
    operation_kind: str
    cost: int
    covered_discriminator_ids: tuple[str, ...]

    def verify(self) -> None:
        if not self.experiment_id:
            raise ValueError("probe identity is required")
        if self.operation_kind != "REGISTERED_PROBE":
            raise ValueError("V2 public probe operation kind must be uniform")
        if self.cost != 1:
            raise ValueError("V2 public probe costs must be matched")


@dataclass(frozen=True)
class OldLanguageHypothesis:
    hypothesis_id: str
    public_signature: str
    protected_signature: str


@dataclass(frozen=True)
class JumpWorld:
    split_id: str
    seed: int
    case_id: str
    family_id: str
    variant: int
    is_jump_case: bool
    opaque_object_ids: tuple[str, ...]
    opaque_relation_ids: tuple[str, ...]
    public_observations: tuple[tuple[str, str], ...]
    incumbent_public_predictions: tuple[tuple[str, str], ...]
    old_language_hypotheses: tuple[OldLanguageHypothesis, ...]
    open_discriminator_ids: tuple[str, ...]
    thought_experiments: tuple[ThoughtExperimentOption, ...]
    informative_experiment_id: str
    informative_outcome: str
    distractor_outcome: str
    representation_move_library: tuple[RepresentationMove, ...]
    correspondence_obligation_ids: tuple[str, ...]
    public_validation_interface_ids: tuple[str, ...]
    gold_representation_move: RepresentationMove
    protected_full_contract_signature: str
    protected_novel_consequence_token: str
    gold_old_solution_id: str | None

    def verify(self) -> None:
        if self.public_observations != self.incumbent_public_predictions:
            raise ValueError("incumbent observed-regime error must be exactly zero")
        if len(self.opaque_object_ids) != 3 or len(self.opaque_relation_ids) != 2:
            raise ValueError("V2 object/relation public cardinalities drifted")
        if len(self.public_observations) != 4:
            raise ValueError("V2 public observation cardinality drifted")
        if len(self.old_language_hypotheses) != 8:
            raise ValueError("V2 old-language public cardinality must be class-balanced")
        if len(self.open_discriminator_ids) != 2:
            raise ValueError("V2 open-discriminator cardinality drifted")
        if len(self.thought_experiments) != 2:
            raise ValueError("V2 probe-menu cardinality drifted")
        if len(self.correspondence_obligation_ids) != 2:
            raise ValueError("V2 correspondence-obligation cardinality drifted")
        if len(self.public_validation_interface_ids) != 2:
            raise ValueError("V2 validation-interface cardinality drifted")
        for option in self.thought_experiments:
            option.verify()
        if self.informative_experiment_id not in {
            option.experiment_id for option in self.thought_experiments
        }:
            raise ValueError("informative experiment is missing from the menu")
        overlaps = sorted(
            len(set(option.covered_discriminator_ids) & set(self.open_discriminator_ids))
            for option in self.thought_experiments
        )
        if overlaps != [0, 2]:
            raise ValueError("V2 menu must contain one fully relevant and one irrelevant probe")
        if len({row.hypothesis_id for row in self.old_language_hypotheses}) != 8:
            raise ValueError("old-language hypothesis IDs must be unique")
        if self.is_jump_case:
            if self.gold_representation_move is RepresentationMove.NO_REPRESENTATION_CHANGE:
                raise ValueError("positive world requires a material representation move")
            if self.gold_old_solution_id is not None:
                raise ValueError("positive world cannot contain an old full-contract solution")
        else:
            if self.gold_representation_move is not RepresentationMove.NO_REPRESENTATION_CHANGE:
                raise ValueError("control cannot carry a material representation move")
            if not self.gold_old_solution_id:
                raise ValueError("control requires an old-language full-contract solution")


@dataclass(frozen=True)
class PublicJumpCase:
    case_id: str
    opaque_object_ids: tuple[str, ...]
    opaque_relation_ids: tuple[str, ...]
    public_observations: tuple[tuple[str, str], ...]
    incumbent_public_predictions: tuple[tuple[str, str], ...]
    old_language_public_signatures: tuple[tuple[str, str], ...]
    open_discriminator_ids: tuple[str, ...]
    thought_experiment_menu: tuple[ThoughtExperimentOption, ...]
    representation_move_library: tuple[RepresentationMove, ...]
    correspondence_obligation_ids: tuple[str, ...]
    public_validation_interface_ids: tuple[str, ...]

    def verify(self) -> None:
        if self.public_observations != self.incumbent_public_predictions:
            raise ValueError("public incumbent predictions must be zero-error")
        if (
            len(self.opaque_object_ids),
            len(self.opaque_relation_ids),
            len(self.public_observations),
            len(self.old_language_public_signatures),
            len(self.open_discriminator_ids),
            len(self.thought_experiment_menu),
            len(self.correspondence_obligation_ids),
            len(self.public_validation_interface_ids),
        ) != (3, 2, 4, 8, 2, 2, 2, 2):
            raise ValueError("V2 public cardinality invariant violated")
        for option in self.thought_experiment_menu:
            option.verify()
        overlaps = sorted(
            len(set(option.covered_discriminator_ids) & set(self.open_discriminator_ids))
            for option in self.thought_experiment_menu
        )
        if overlaps != [0, 2]:
            raise ValueError("public probe relevance must be one full/one zero overlap")
        corpus = " ".join(
            [
                self.case_id,
                *self.opaque_object_ids,
                *self.opaque_relation_ids,
                *self.open_discriminator_ids,
                *(value for row in self.public_observations for value in row),
                *(value for row in self.old_language_public_signatures for value in row),
                *(option.experiment_id for option in self.thought_experiment_menu),
                *(value for option in self.thought_experiment_menu for value in option.covered_discriminator_ids),
                *self.correspondence_obligation_ids,
                *self.public_validation_interface_ids,
            ]
        ).lower()
        if any(term in corpus for term in _BANNED_TERMS):
            raise ValueError("historical discovery term leaked into public payload")
        if "-p" in self.case_id.lower() or "-c" in self.case_id.lower():
            raise ValueError("case ID contains protected P/C class marker")


@dataclass(frozen=True)
class OldRegimeInsufficiencyProof:
    case_id: str
    old_candidate_count: int
    matching_public_count: int
    full_contract_solution_ids: tuple[str, ...]
    old_regime_insufficient: bool
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "OldRegimeInsufficiencyProof.v2",
            "case_id": self.case_id,
            "old_candidate_count": self.old_candidate_count,
            "matching_public_count": self.matching_public_count,
            "full_contract_solution_ids": list(self.full_contract_solution_ids),
            "old_regime_insufficient": self.old_regime_insufficient,
        }

    def verify(self) -> None:
        if self.old_candidate_count != 8:
            raise ValueError("V2 exact old language must have 8 candidates per case")
        if self.matching_public_count != 8:
            raise ValueError("all V2 old candidates must fit the public zero-error observations")
        if self.old_regime_insufficient == bool(self.full_contract_solution_ids):
            raise ValueError("insufficiency contradicts exact full-contract enumeration")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("old-regime insufficiency proof digest mismatch")


@dataclass(frozen=True)
class JumpProposal:
    arm: JumpArm
    case_id: str
    jump_requested: bool
    representation_move: RepresentationMove
    selected_experiment_id: str | None
    experiment_outcome: str | None
    correspondence_complete: bool
    protected_consequence_prediction: str | None
    old_regime_action_id: str | None
    recognizes_old_regime_insufficiency: bool
    claims_scientific_authority: bool = False

    def decision_key(self) -> tuple[object, ...]:
        return (
            self.jump_requested,
            self.representation_move.value,
            self.selected_experiment_id,
            self.experiment_outcome,
            self.correspondence_complete,
            self.protected_consequence_prediction,
            self.old_regime_action_id,
            self.recognizes_old_regime_insufficiency,
            self.claims_scientific_authority,
        )


@dataclass(frozen=True)
class ArmMetrics:
    arm: JumpArm
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

    def metric_payload(self) -> dict[str, int]:
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
class JumpSplitReport:
    split_id: str
    seed: int
    case_count: int
    positive_count: int
    control_count: int
    proof_digests: tuple[str, ...]
    metrics: tuple[ArmMetrics, ...]

    def metric(self, arm: JumpArm) -> ArmMetrics:
        return next(metric for metric in self.metrics if metric.arm is arm)


@dataclass(frozen=True)
class ZeroErrorJumpBenchmarkReport:
    primary: JumpSplitReport
    replication: JumpSplitReport
    verified_parent_equals_orion_decisions_primary: bool
    verified_parent_equals_orion_decisions_replication: bool
    verified_parent_equals_orion_metrics_primary: bool
    verified_parent_equals_orion_metrics_replication: bool
    orion_strong_parent_incremental_gap_primary: int
    orion_strong_parent_incremental_gap_replication: int
    primary_replication_terminal_equal: bool
    terminal: ZeroErrorJumpTerminal
    all_checks_passed: bool
    digest: str

    @property
    def grants_scientific_adoption(self) -> bool:
        return False

    @property
    def grants_open_ended_creativity(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    @property
    def grants_issue_closure_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        def split_payload(split: JumpSplitReport) -> dict[str, object]:
            return {
                "split_id": split.split_id,
                "seed": split.seed,
                "case_count": split.case_count,
                "positive_count": split.positive_count,
                "control_count": split.control_count,
                "proof_digests": list(split.proof_digests),
                "metrics": {
                    metric.arm.value: metric.metric_payload() for metric in split.metrics
                },
            }
        return {
            "version": "ZeroErrorJumpBenchmarkReport.v2",
            "primary": split_payload(self.primary),
            "replication": split_payload(self.replication),
            "verified_parent_equals_orion_decisions_primary": self.verified_parent_equals_orion_decisions_primary,
            "verified_parent_equals_orion_decisions_replication": self.verified_parent_equals_orion_decisions_replication,
            "verified_parent_equals_orion_metrics_primary": self.verified_parent_equals_orion_metrics_primary,
            "verified_parent_equals_orion_metrics_replication": self.verified_parent_equals_orion_metrics_replication,
            "orion_strong_parent_incremental_gap_primary": self.orion_strong_parent_incremental_gap_primary,
            "orion_strong_parent_incremental_gap_replication": self.orion_strong_parent_incremental_gap_replication,
            "primary_replication_terminal_equal": self.primary_replication_terminal_equal,
            "terminal": self.terminal.value,
            "all_checks_passed": self.all_checks_passed,
            "grants_scientific_adoption": False,
            "grants_open_ended_creativity": False,
            "grants_novelty_authority": False,
            "grants_issue_closure_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("V2 zero-error Jump report digest mismatch")


def _public_signature(seed: int, case_id: str) -> str:
    return _opaque(seed, case_id, "pub", prefix="pub")


def _protected_signature(seed: int, case_id: str) -> str:
    return _opaque(seed, case_id, "prot", prefix="prot")


def _build_old_language(
    *, seed: int, case_id: str, is_jump_case: bool, public_signature: str,
    protected_signature: str, hard_search: bool,
) -> tuple[tuple[OldLanguageHypothesis, ...], str | None]:
    count = 8
    solution_index: int | None = None
    if not is_jump_case:
        solution_index = (
            count - 1
            if hard_search
            else int(hashlib.sha256(f"{seed}|{case_id}|solution".encode()).hexdigest(), 16)
            % count
        )
    rows: list[OldLanguageHypothesis] = []
    for index in range(count):
        candidate_id = _opaque(seed, case_id, "old", index, prefix="oldh")
        protected = (
            protected_signature
            if solution_index is not None and index == solution_index
            else _opaque(seed, case_id, "wrong", index, prefix="wrong")
        )
        rows.append(OldLanguageHypothesis(candidate_id, public_signature, protected))
    gold = rows[solution_index].hypothesis_id if solution_index is not None else None
    return tuple(rows), gold


def _uniform_public_parts(seed: int, case_id: str):
    objects = tuple(_opaque(seed, case_id, "obj", i, prefix="obj") for i in range(3))
    relations = tuple(_opaque(seed, case_id, "rel", i, prefix="rel") for i in range(2))
    observations = tuple(
        (
            _opaque(seed, case_id, "ok", i, prefix="ok"),
            _opaque(seed, case_id, "ov", i, prefix="ov"),
        )
        for i in range(4)
    )
    open_ids = tuple(_opaque(seed, case_id, "open", i, prefix="disc") for i in range(2))
    obligations = tuple(_opaque(seed, case_id, "obl", i, prefix="obl") for i in range(2))
    validators = tuple(_opaque(seed, case_id, "ver", i, prefix="ver") for i in range(2))
    informative_id = _opaque(seed, case_id, "probe-info", prefix="exp")
    distractor_id = _opaque(seed, case_id, "probe-decoy", prefix="exp")
    unrelated = tuple(_opaque(seed, case_id, "decoy-disc", i, prefix="disc") for i in range(2))
    info = ThoughtExperimentOption(informative_id, "REGISTERED_PROBE", 1, open_ids)
    decoy = ThoughtExperimentOption(distractor_id, "REGISTERED_PROBE", 1, unrelated)
    menu = (info, decoy)
    if int(hashlib.sha256(case_id.encode()).hexdigest(), 16) % 2:
        menu = (decoy, info)
    return objects, relations, observations, open_ids, obligations, validators, informative_id, distractor_id, menu


def _positive_world(
    seed: int, split_id: str, ordinal: int, family_index: int, variant: int
) -> JumpWorld:
    family_id, move = _POSITIVE_FAMILIES[family_index]
    case_id = _case_id(seed, split_id, ordinal)
    (
        objects, relations, observations, open_ids, obligations, validators,
        informative_id, _, menu,
    ) = _uniform_public_parts(seed, case_id)
    pub = _public_signature(seed, case_id)
    prot = _protected_signature(seed, case_id)
    old, _ = _build_old_language(
        seed=seed, case_id=case_id, is_jump_case=True, public_signature=pub,
        protected_signature=prot, hard_search=False,
    )
    code = _MOVE_TO_EVIDENCE_CODE[move]
    outcome = f"pattern:{code}:{_opaque(seed, case_id, 'out', prefix='x')}"
    consequence = _consequence_token(
        case_id=case_id, move=move, outcome_signature=outcome, anchor_id=objects[0]
    )
    world = JumpWorld(
        split_id=split_id,
        seed=seed,
        case_id=case_id,
        family_id=family_id,
        variant=variant,
        is_jump_case=True,
        opaque_object_ids=objects,
        opaque_relation_ids=relations,
        public_observations=observations,
        incumbent_public_predictions=observations,
        old_language_hypotheses=old,
        open_discriminator_ids=open_ids,
        thought_experiments=menu,
        informative_experiment_id=informative_id,
        informative_outcome=outcome,
        distractor_outcome=f"pattern:NONDISCRIMINATING:{_opaque(seed, case_id, 'decoy', prefix='x')}",
        representation_move_library=tuple(RepresentationMove),
        correspondence_obligation_ids=obligations,
        public_validation_interface_ids=validators,
        gold_representation_move=move,
        protected_full_contract_signature=prot,
        protected_novel_consequence_token=consequence,
        gold_old_solution_id=None,
    )
    world.verify()
    return world


def _control_world(
    seed: int, split_id: str, ordinal: int, family_index: int, variant: int
) -> JumpWorld:
    family_id = _CONTROL_FAMILIES[family_index]
    case_id = _case_id(seed, split_id, ordinal)
    (
        objects, relations, observations, open_ids, obligations, validators,
        informative_id, _, menu,
    ) = _uniform_public_parts(seed, case_id)
    pub = _public_signature(seed, case_id)
    prot = _protected_signature(seed, case_id)
    old, gold = _build_old_language(
        seed=seed, case_id=case_id, is_jump_case=False, public_signature=pub,
        protected_signature=prot, hard_search=family_id == "SEARCH_HARD_BUT_EXPRESSIBLE",
    )
    world = JumpWorld(
        split_id=split_id,
        seed=seed,
        case_id=case_id,
        family_id=family_id,
        variant=variant,
        is_jump_case=False,
        opaque_object_ids=objects,
        opaque_relation_ids=relations,
        public_observations=observations,
        incumbent_public_predictions=observations,
        old_language_hypotheses=old,
        open_discriminator_ids=open_ids,
        thought_experiments=menu,
        informative_experiment_id=informative_id,
        informative_outcome=f"pattern:OLD_SUFFICIENT:{_opaque(seed, case_id, 'out', prefix='x')}",
        distractor_outcome=f"pattern:NONDISCRIMINATING:{_opaque(seed, case_id, 'decoy', prefix='x')}",
        representation_move_library=tuple(RepresentationMove),
        correspondence_obligation_ids=obligations,
        public_validation_interface_ids=validators,
        gold_representation_move=RepresentationMove.NO_REPRESENTATION_CHANGE,
        protected_full_contract_signature=prot,
        protected_novel_consequence_token="",
        gold_old_solution_id=gold,
    )
    world.verify()
    return world


def generate_jump_worlds(*, seed: int, split_id: str) -> tuple[JumpWorld, ...]:
    worlds: list[JumpWorld] = []
    ordinal = 0
    for family_index in range(len(_POSITIVE_FAMILIES)):
        for variant in range(1, 5):
            worlds.append(_positive_world(seed, split_id, ordinal, family_index, variant))
            ordinal += 1
    for family_index in range(len(_CONTROL_FAMILIES)):
        for variant in range(1, 4):
            worlds.append(_control_world(seed, split_id, ordinal, family_index, variant))
            ordinal += 1
    if len(worlds) != 42:
        raise AssertionError("V2 split must contain exactly 42 worlds")
    return tuple(worlds)


def public_projection(world: JumpWorld) -> PublicJumpCase:
    world.verify()
    case = PublicJumpCase(
        case_id=world.case_id,
        opaque_object_ids=world.opaque_object_ids,
        opaque_relation_ids=world.opaque_relation_ids,
        public_observations=world.public_observations,
        incumbent_public_predictions=world.incumbent_public_predictions,
        old_language_public_signatures=tuple(
            (row.hypothesis_id, row.public_signature) for row in world.old_language_hypotheses
        ),
        open_discriminator_ids=world.open_discriminator_ids,
        thought_experiment_menu=world.thought_experiments,
        representation_move_library=world.representation_move_library,
        correspondence_obligation_ids=world.correspondence_obligation_ids,
        public_validation_interface_ids=world.public_validation_interface_ids,
    )
    case.verify()
    return case


def prove_old_regime(world: JumpWorld) -> OldRegimeInsufficiencyProof:
    world.verify()
    public_signature = _public_signature(world.seed, world.case_id)
    matching = tuple(
        row for row in world.old_language_hypotheses if row.public_signature == public_signature
    )
    full = tuple(
        row.hypothesis_id
        for row in matching
        if row.protected_signature == world.protected_full_contract_signature
    )
    payload = {
        "version": "OldRegimeInsufficiencyProof.v2",
        "case_id": world.case_id,
        "old_candidate_count": len(world.old_language_hypotheses),
        "matching_public_count": len(matching),
        "full_contract_solution_ids": sorted(full),
        "old_regime_insufficient": not bool(full),
    }
    proof = OldRegimeInsufficiencyProof(
        case_id=world.case_id,
        old_candidate_count=payload["old_candidate_count"],
        matching_public_count=payload["matching_public_count"],
        full_contract_solution_ids=tuple(payload["full_contract_solution_ids"]),
        old_regime_insufficient=payload["old_regime_insufficient"],
        digest=content_digest(payload),
    )
    proof.verify()
    return proof


def select_registered_probe(public: PublicJumpCase) -> str | None:
    public.verify()
    open_ids = set(public.open_discriminator_ids)
    scored = [
        (
            len(set(option.covered_discriminator_ids) & open_ids),
            option.experiment_id,
        )
        for option in public.thought_experiment_menu
    ]
    best = max(score for score, _ in scored)
    winners = [experiment_id for score, experiment_id in scored if score == best]
    if best <= 0 or len(winners) != 1:
        return None
    return winners[0]


def run_thought_experiment(world: JumpWorld, experiment_id: str) -> str:
    if experiment_id == world.informative_experiment_id:
        return world.informative_outcome
    if experiment_id in {row.experiment_id for row in world.thought_experiments}:
        return world.distractor_outcome
    raise ValueError("experiment is not in the registered public menu")


def _move_from_outcome(outcome: str) -> RepresentationMove | None:
    parts = outcome.split(":", 2)
    if len(parts) < 2 or parts[0] != "pattern":
        return None
    code = parts[1]
    if code == "OLD_SUFFICIENT":
        return RepresentationMove.NO_REPRESENTATION_CHANGE
    if code == "NONDISCRIMINATING":
        return None
    return _EVIDENCE_CODE_TO_MOVE.get(code)


def _evidence_based_proposal(
    *, world: JumpWorld, public: PublicJumpCase, arm: JumpArm,
    can_change_representation: bool, correspondence_complete: bool,
) -> JumpProposal:
    experiment_id = select_registered_probe(public)
    if experiment_id is None:
        return JumpProposal(
            arm, public.case_id, False, RepresentationMove.NO_REPRESENTATION_CHANGE,
            None, None, False, None, "UNRESOLVED", False,
        )
    outcome = run_thought_experiment(world, experiment_id)
    move = _move_from_outcome(outcome)
    if move is None:
        return JumpProposal(
            arm, public.case_id, False, RepresentationMove.NO_REPRESENTATION_CHANGE,
            experiment_id, outcome, False, None, "UNRESOLVED", False,
        )
    if move is RepresentationMove.NO_REPRESENTATION_CHANGE:
        return JumpProposal(
            arm, public.case_id, False, move, experiment_id, outcome,
            False, None, "KEEP_OLD_REGIME", False,
        )
    if not can_change_representation:
        return JumpProposal(
            arm, public.case_id, False, RepresentationMove.NO_REPRESENTATION_CHANGE,
            experiment_id, outcome, False, None,
            "UNRESOLVED_REPRESENTATION_CEILING", True,
        )
    prediction = _consequence_token(
        case_id=public.case_id,
        move=move,
        outcome_signature=outcome,
        anchor_id=public.opaque_object_ids[0],
    )
    return JumpProposal(
        arm, public.case_id, True, move, experiment_id, outcome,
        correspondence_complete, prediction, None, True,
    )


def propose(world: JumpWorld, arm: JumpArm) -> JumpProposal:
    public = public_projection(world)
    if arm in (
        JumpArm.OLD_DSL_EXHAUSTIVE,
        JumpArm.M_OPEN_SAME_REPRESENTATION,
        JumpArm.FIXED_REP_WORLD_MODEL,
    ):
        return _evidence_based_proposal(
            world=world, public=public, arm=arm,
            can_change_representation=False, correspondence_complete=False,
        )
    if arm in (JumpArm.VERIFIED_REGIME_REVISION_PARENT, JumpArm.ORION_JUMP):
        return _evidence_based_proposal(
            world=world, public=public, arm=arm,
            can_change_representation=True, correspondence_complete=True,
        )
    if arm is JumpArm.ORION_NO_CORRESPONDENCE:
        return _evidence_based_proposal(
            world=world, public=public, arm=arm,
            can_change_representation=True, correspondence_complete=False,
        )
    if arm is JumpArm.OVERJUMP_ALWAYS:
        experiment_id = select_registered_probe(public)
        if experiment_id is None:
            raise AssertionError("registered case lacks a unique public probe")
        outcome = run_thought_experiment(world, experiment_id)
        move = RepresentationMove.BRIDGE_CORRESPONDENCE
        prediction = _consequence_token(
            case_id=public.case_id, move=move, outcome_signature=outcome,
            anchor_id=public.opaque_object_ids[0],
        )
        evidence_move = _move_from_outcome(outcome)
        return JumpProposal(
            arm, public.case_id, True, move, experiment_id, outcome, True,
            prediction, None,
            evidence_move not in (None, RepresentationMove.NO_REPRESENTATION_CHANGE),
        )
    if arm is JumpArm.ORACLE:
        if not world.is_jump_case:
            return JumpProposal(
                arm, world.case_id, False, RepresentationMove.NO_REPRESENTATION_CHANGE,
                world.informative_experiment_id, world.informative_outcome,
                False, None, "KEEP_OLD_REGIME", False,
            )
        return JumpProposal(
            arm, world.case_id, True, world.gold_representation_move,
            world.informative_experiment_id, world.informative_outcome,
            True, world.protected_novel_consequence_token, None, True,
        )
    raise AssertionError(f"unhandled Jump arm: {arm}")


def _score_proposal(world: JumpWorld, proposal: JumpProposal) -> dict[str, bool]:
    proof = prove_old_regime(world)
    authority_bad = proposal.claims_scientific_authority
    informative = proposal.selected_experiment_id == world.informative_experiment_id
    move_correct = proposal.representation_move is world.gold_representation_move
    consequence_ok = (
        world.is_jump_case
        and move_correct
        and proposal.protected_consequence_prediction == world.protected_novel_consequence_token
    )
    correspondence_ok = world.is_jump_case and move_correct and proposal.correspondence_complete
    positive_success = (
        world.is_jump_case
        and proof.old_regime_insufficient
        and proposal.jump_requested
        and move_correct
        and informative
        and correspondence_ok
        and consequence_ok
        and not authority_bad
    )
    control_correct = (
        not world.is_jump_case
        and not proof.old_regime_insufficient
        and not proposal.jump_requested
        and proposal.representation_move is RepresentationMove.NO_REPRESENTATION_CHANGE
        and proposal.old_regime_action_id == "KEEP_OLD_REGIME"
        and not authority_bad
    )
    return {
        "positive_success": positive_success,
        "control_correct": control_correct,
        "false_jump": (not world.is_jump_case and proposal.jump_requested),
        "insufficiency_correct": (
            world.is_jump_case
            and proof.old_regime_insufficient
            and proposal.recognizes_old_regime_insufficiency
        ),
        "correspondence_success": correspondence_ok,
        "consequence_correct": consequence_ok,
        "thought_experiment_success": world.is_jump_case and informative,
        "rejected_positive": world.is_jump_case and not positive_success,
        "authority_violation": authority_bad,
    }


def score_split(*, split_id: str, seed: int) -> JumpSplitReport:
    worlds = generate_jump_worlds(seed=seed, split_id=split_id)
    proofs = tuple(prove_old_regime(world) for world in worlds)
    for world, proof in zip(worlds, proofs):
        if world.is_jump_case and not proof.old_regime_insufficient:
            raise ValueError("positive case is expressible in old language")
        if not world.is_jump_case and proof.old_regime_insufficient:
            raise ValueError("control lacks old-language full solution")
    metrics: list[ArmMetrics] = []
    for arm in JumpArm:
        proposals = tuple(propose(world, arm) for world in worlds)
        scores = tuple(_score_proposal(world, proposal) for world, proposal in zip(worlds, proposals))
        metrics.append(
            ArmMetrics(
                arm=arm,
                structural_decision_correct=sum(int(s["positive_success"] or s["control_correct"]) for s in scores),
                positive_jump_success=sum(int(s["positive_success"]) for s in scores),
                control_no_jump_correct=sum(int(s["control_correct"]) for s in scores),
                false_jump_on_control=sum(int(s["false_jump"]) for s in scores),
                old_regime_insufficiency_correct=sum(int(s["insufficiency_correct"]) for s in scores),
                correspondence_success=sum(int(s["correspondence_success"]) for s in scores),
                protected_consequence_success=sum(int(s["consequence_correct"]) for s in scores),
                thought_experiment_success=sum(int(s["thought_experiment_success"]) for s in scores),
                unresolved_or_rejected=sum(int(s["rejected_positive"]) for s in scores),
                authority_violations=sum(int(s["authority_violation"]) for s in scores),
                decision_keys=tuple(proposal.decision_key() for proposal in proposals),
            )
        )
    return JumpSplitReport(
        split_id=split_id,
        seed=seed,
        case_count=len(worlds),
        positive_count=sum(int(world.is_jump_case) for world in worlds),
        control_count=sum(int(not world.is_jump_case) for world in worlds),
        proof_digests=tuple(proof.digest for proof in proofs),
        metrics=tuple(metrics),
    )


def _metric_matches(metric: ArmMetrics, expected: Mapping[str, object]) -> bool:
    return metric.metric_payload() == {str(k): int(v) for k, v in expected.items()}


def _split_matches(
    split: JumpSplitReport, *, split_expected: Mapping[str, object],
    per_arm_expected: Mapping[str, object],
) -> bool:
    if (
        split.seed != int(split_expected.get("seed", -1))
        or split.case_count != int(split_expected.get("cases", -1))
        or split.positive_count != int(split_expected.get("positive_cases", -1))
        or split.control_count != int(split_expected.get("control_cases", -1))
    ):
        return False
    for arm in JumpArm:
        row = per_arm_expected.get(arm.value)
        if not isinstance(row, Mapping) or not _metric_matches(split.metric(arm), row):
            return False
    return True


def _validate_v2_public_leakage(worlds: tuple[JumpWorld, ...]) -> bool:
    signatures = []
    for world in worlds:
        public = public_projection(world)
        public.verify()
        signatures.append(
            (
                len(public.opaque_object_ids),
                len(public.opaque_relation_ids),
                len(public.public_observations),
                len(public.old_language_public_signatures),
                len(public.open_discriminator_ids),
                len(public.thought_experiment_menu),
                tuple(option.operation_kind for option in public.thought_experiment_menu),
                tuple(option.cost for option in public.thought_experiment_menu),
                len(public.correspondence_obligation_ids),
                len(public.public_validation_interface_ids),
            )
        )
    return len(set(signatures)) == 1


def build_zero_error_jump_benchmark_report(
    *, protocol: Mapping[str, object], expected: Mapping[str, object]
) -> ZeroErrorJumpBenchmarkReport:
    if protocol.get("version") != "ZeroErrorJumpProtocol.v2":
        raise ValueError("V2 runner requires ZeroErrorJumpProtocol.v2")
    if protocol.get("outcome_accessed") is not False:
        raise ValueError("V2 protocol must remain frozen before outcome access")
    if protocol.get("cases_frozen_before_v2_runner") is not True:
        raise ValueError("V2 cases must be frozen before runner")
    if expected.get("version") != "ZeroErrorJumpExpected.v2":
        raise ValueError("V2 runner requires ZeroErrorJumpExpected.v2")
    seeds = protocol.get("seeds")
    if not isinstance(seeds, Mapping):
        raise ValueError("V2 seeds missing")
    primary_worlds = generate_jump_worlds(seed=int(seeds["primary"]), split_id="primary")
    replication_worlds = generate_jump_worlds(seed=int(seeds["replication"]), split_id="replication")
    leakage_clear = _validate_v2_public_leakage(primary_worlds) and _validate_v2_public_leakage(replication_worlds)
    primary = score_split(split_id="primary", seed=int(seeds["primary"]))
    replication = score_split(split_id="replication", seed=int(seeds["replication"]))
    split_expected = expected.get("split_expectations")
    per_arm = expected.get("per_split_arm_metrics")
    if not isinstance(split_expected, Mapping) or not isinstance(per_arm, Mapping):
        raise ValueError("V2 expected tables missing")
    primary_matches = _split_matches(primary, split_expected=split_expected["primary"], per_arm_expected=per_arm)
    replication_matches = _split_matches(replication, split_expected=split_expected["replication"], per_arm_expected=per_arm)
    p_parent = primary.metric(JumpArm.VERIFIED_REGIME_REVISION_PARENT)
    p_orion = primary.metric(JumpArm.ORION_JUMP)
    r_parent = replication.metric(JumpArm.VERIFIED_REGIME_REVISION_PARENT)
    r_orion = replication.metric(JumpArm.ORION_JUMP)
    decisions_p = p_parent.decision_keys == p_orion.decision_keys
    decisions_r = r_parent.decision_keys == r_orion.decision_keys
    metrics_p = p_parent.metric_payload() == p_orion.metric_payload()
    metrics_r = r_parent.metric_payload() == r_orion.metric_payload()
    gap_p = p_orion.positive_jump_success - p_parent.positive_jump_success
    gap_r = r_orion.positive_jump_success - r_parent.positive_jump_success
    terminal_equal = primary_matches == replication_matches
    leakage_expected = expected.get("leakage_expectations")
    if not isinstance(leakage_expected, Mapping):
        raise ValueError("V2 leakage expectations missing")
    leakage_matches = (
        leakage_clear
        and leakage_expected.get("public_tension_kind_present") is False
        and leakage_expected.get("positive_control_distinguishable_from_operation_kind_before_experiment") is False
        and leakage_expected.get("control_family_id_embedded_in_candidate_visible_outcome") is False
        and int(leakage_expected.get("menu_options_per_case", -1)) == 2
        and leakage_expected.get("uniform_menu_operation_kind") == "REGISTERED_PROBE"
    )
    all_checks = (
        primary_matches
        and replication_matches
        and leakage_matches
        and decisions_p
        and decisions_r
        and metrics_p
        and metrics_r
        and gap_p == 0
        and gap_r == 0
        and terminal_equal
        and expected.get("candidate_terminal")
        == protocol.get("candidate_terminal")
        == ZeroErrorJumpTerminal.REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE.value
    )
    terminal = (
        ZeroErrorJumpTerminal.REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE
        if all_checks
        else ZeroErrorJumpTerminal.CANNOT_CHECK
    )
    temp = ZeroErrorJumpBenchmarkReport(
        primary, replication, decisions_p, decisions_r, metrics_p, metrics_r,
        gap_p, gap_r, terminal_equal, terminal, all_checks, ""
    )
    report = ZeroErrorJumpBenchmarkReport(
        primary=temp.primary,
        replication=temp.replication,
        verified_parent_equals_orion_decisions_primary=temp.verified_parent_equals_orion_decisions_primary,
        verified_parent_equals_orion_decisions_replication=temp.verified_parent_equals_orion_decisions_replication,
        verified_parent_equals_orion_metrics_primary=temp.verified_parent_equals_orion_metrics_primary,
        verified_parent_equals_orion_metrics_replication=temp.verified_parent_equals_orion_metrics_replication,
        orion_strong_parent_incremental_gap_primary=temp.orion_strong_parent_incremental_gap_primary,
        orion_strong_parent_incremental_gap_replication=temp.orion_strong_parent_incremental_gap_replication,
        primary_replication_terminal_equal=temp.primary_replication_terminal_equal,
        terminal=temp.terminal,
        all_checks_passed=temp.all_checks_passed,
        digest=content_digest(temp.unsigned()),
    )
    report.verify()
    return report


__all__ = [
    "ArmMetrics",
    "JumpArm",
    "JumpProposal",
    "JumpSplitReport",
    "JumpWorld",
    "OldLanguageHypothesis",
    "OldRegimeInsufficiencyProof",
    "PublicJumpCase",
    "RepresentationMove",
    "ThoughtExperimentOption",
    "ZeroErrorJumpBenchmarkReport",
    "ZeroErrorJumpTerminal",
    "build_zero_error_jump_benchmark_report",
    "generate_jump_worlds",
    "prove_old_regime",
    "propose",
    "public_projection",
    "run_thought_experiment",
    "score_split",
    "select_registered_probe",
]
