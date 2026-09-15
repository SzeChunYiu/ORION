"""Section 2 -- the two frozen tasks and their bindings.

One wide-literature task and one deep-target task, plus the `ProtectedTargetGold`
whose plaintext never reaches the public document -- only its digest does.
"""

from __future__ import annotations

from dataclasses import dataclass

from orion.core.problem import Problem
from orion.self_orion.live_trial import FrozenTrialTask, ResearchTrialKind

from .constants import UNBOUND, _sha256
from .identity import CheckableCriterion, DEEP_CRITERIA, WIDE_CRITERIA


@dataclass(frozen=True)
class ProtectedTargetGold:
    """Ground truth held back from the public document.

    Only `digest` is published. A packet that printed the expected tokens would
    hand the system under test its own answer key, and every deep-target result
    measured against it would be a restatement of the packet rather than an
    observation of the run. This mirrors `protected_gold` in the P1 case suite,
    where the public view and the gold are separate objects by construction.
    """

    anchor_source_id: str
    required_answer_tokens: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.anchor_source_id.strip() or not self.required_answer_tokens:
            raise ValueError("protected gold requires an anchor and at least one token")

    @property
    def digest(self) -> str:
        return _sha256(
            {
                "anchor_source_id": self.anchor_source_id,
                "required_answer_tokens": sorted(self.required_answer_tokens),
            }
        )


WIDE_TASK_ID = "P5.LIVE.WIDE.stopping-rule-source-families"
DEEP_TASK_ID = "P5.LIVE.DEEP.flat-round-without-lineage"

_WIDE_TASK = FrozenTrialTask(
    task_id=WIDE_TASK_ID,
    kind=ResearchTrialKind.WIDE_LITERATURE,
    problem=Problem(
        problem_id=WIDE_TASK_ID,
        question=(
            "Which distinct research literatures state stopping rules for an "
            "evidence search, and for each one, what does it require before a "
            "flat search may be called saturated? Cite only material returned by "
            "the trial's own retrieval routes."
        ),
        scope=(
            "Wide literature sweep. Breadth across source families is the target; "
            "depth on any single family is not."
        ),
        initial_domain_ids=("domain:evidence-synthesis", "domain:information-retrieval"),
        success_criteria=tuple(item.description for item in WIDE_CRITERIA),
    ),
    variation_signature=("wide_literature", "route_family_breadth"),
    split_id="P5.shadow-live.wide",
    # UNBOUND on purpose. Naming the papers a correct answer must contain would
    # require inventing them, and a fabricated answer key is worse than none.
    # Present-but-missed is therefore CANNOT_CHECK for this task, and the
    # classifier says so rather than reporting zero misses.
    required_evidence_ids=(),
)

_DEEP_TASK = FrozenTrialTask(
    task_id=DEEP_TASK_ID,
    kind=ResearchTrialKind.DEEP_TARGET,
    problem=Problem(
        problem_id=DEEP_TASK_ID,
        question=(
            "Within the frozen ORION source corpus, determine what bounded "
            "saturation returns when a flat round declares no evidence lineage, "
            "name the module and function that decide it, and state why that "
            "guard exists instead of counting the round toward saturation."
        ),
        scope=(
            "Single deep target inside a corpus that is fixed at execution time. "
            "One exact answer exists and is held back from this packet."
        ),
        initial_domain_ids=("domain:orion-source",),
        success_criteria=tuple(item.description for item in DEEP_CRITERIA),
    ),
    variation_signature=("deep_target", "single_verdict_recovery"),
    split_id="P5.shadow-live.deep",
    required_evidence_ids=(),
)

#: Held back from every published artifact; see `ProtectedTargetGold`.
_DEEP_TASK_GOLD = ProtectedTargetGold(
    anchor_source_id="orion-corpus:src/orion/kernel/saturation.py",
    required_answer_tokens=("PARTIALLY_IDENTIFIED_LINEAGE",),
)


@dataclass(frozen=True)
class FrozenTaskBinding:
    """What the evaluator needs for one task, with the gold kept out of public view."""

    task_id: str
    criteria: tuple[CheckableCriterion, ...]
    gold: ProtectedTargetGold | None = None
    corpus_revision: str = UNBOUND

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.criteria:
            raise ValueError("task binding identity and criteria are required")

    @property
    def ground_truth_bound(self) -> bool:
        return self.gold is not None

    @property
    def payload(self) -> dict[str, object]:
        """Public view. Carries the gold's digest, never its content."""

        return {
            "task_id": self.task_id,
            "criteria": [item.payload for item in self.criteria],
            "protected_gold_digest": self.gold.digest if self.gold else None,
            "ground_truth_bound": self.ground_truth_bound,
            "corpus_revision": self.corpus_revision,
        }
