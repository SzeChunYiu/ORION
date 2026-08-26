"""Credential-free substrate for the frozen Shadow Self-ORION live research trial.

This module builds everything issue #8 requires *except* the live execution, and
freezes it before any outcome can be observed. Nothing here makes a network call,
reads a credential value, or needs a provider to be constructed. What it produces:

* a frozen task packet (one wide-literature task, one deep-target task) whose
  provider identities, resource limits, evaluator and matched baseline are fixed
  and bound by content hash, exactly as the ORION-P1 suite binds its cases;
* a mechanical question surface built from fixed mechanic cells, so the eight
  dimensions the issue names -- observability, mathematics, handoff, failure,
  storage, verification, parent-discipline and saturation -- are exposed by a
  fixed audit grammar rather than by asking a model what it forgot;
* raw query/retrieval trace retention, with retrieved-but-unused distinguished
  from present-but-missed *where ground truth permits* and reported as
  CANNOT_CHECK where it does not;
* immutable episodes for every failed, partial or refused mechanic execution,
  shaped so `orion.experience.learning.propose_failure_pattern` can match them;
* an authority boundary that refuses promotion structurally rather than by
  convention.

**Success boundary (issue #8, honoured verbatim).** Success for this trial means
the live stack exercises ORION's governed loop and yields interpretable evidence
about failures. It does not by itself establish general autonomous-science
capability, and it does not establish Self-ORION readiness. No object, verdict or
field in this module may be read as evidence of either. `AuthorityDecision` can
only ever be a refusal, and `BoundedSaturationState.certifies_recall` is fixed at
False for the same reason `orion.kernel.saturation.SaturationReport` fixes it.

**Credential handling.** Follows `orion.study.p1.provider`: presence is tested via
`os.environ`, the value is never read into a variable, never stored on an object,
never serialized. Absence is a typed refusal that records CANNOT_CHECK, never a
zero -- "could not check" and "checked and found wrong" are different facts, and a
substrate that records the first as the second reports a missing environment
variable as a failed trial. The refusal is defined locally rather than imported so
that paper-05 substrate does not drag the P1 case/system modules or P1's subject
model id into its dependency surface; what is shared is the contract, not the code.

**No fabrication.** The packet defines tasks. It contains no literature, no
citations, no results and no provider responses. The deep-target ground truth is
a protected gold whose plaintext never reaches the public document -- only its
digest does -- following the `protected_gold` separation in the P1 case suite.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path

from orion.core.problem import Problem
from orion.core.search import SearchRouteKind
from orion.experience.learning import propose_failure_pattern
from orion.experience.model import (
    EpisodeOutcome,
    FailurePatternCandidate,
    LessonAuthority,
    TaskEpisode,
)
from orion.mechanics.model import (
    HandoffField,
    MechanicCell,
    MechanicDimension,
    MetricDirection,
    MetricKind,
    MetricSpec,
)
from orion.mechanics.questioning import MechanicQuestion, generate_mechanic_questions
from orion.self_orion.live_trial import (
    FrozenLiveTrialPacket,
    FrozenTrialTask,
    ResearchTrialKind,
    ShadowLiveTrialRunner,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_RELATIVE_PATH = (
    "papers/orion-15-self-orion/protocol/LIVE_TRIAL_PACKET_V1.json"
)
PROTOCOL_PATH = REPO_ROOT / PROTOCOL_RELATIVE_PATH

PACKET_SCHEMA = "orion.self-orion.live-research-packet.v1"
PACKET_ID = "P5.shadow-live-research.v1"
EVALUATION_EPOCH_ID = "P5.shadow-live-research.epoch-1"
BASELINE_ID = "simple_llm_retrieval_baseline.v1"

#: Sentinel for a field that cannot honestly be filled before execution. Copied
#: from the P5 protocol convention (`dataset_revisions: UNBOUND`): a result
#: reported against an unbound coordinate is unverifiable, so the coordinate is
#: named and left visibly empty rather than guessed at freeze time.
UNBOUND = "UNBOUND"

#: Deterministic stamp for pre-execution artifacts. Wall-clock time here would
#: make the refusal episodes and their fingerprints irreproducible, and a record
#: that cannot be recomputed cannot be checked.
PREFLIGHT_TIMESTAMP = "P5.shadow-live-research.preflight"

EXIT_OK = 0
EXIT_ERROR = 2
EXIT_CANNOT_CHECK = 3

SUCCESS_BOUNDARY = (
    "Exercising the governed loop and yielding interpretable failure evidence is "
    "the whole of the success claim. This packet does not establish autonomous-"
    "science capability, and it does not establish Self-ORION readiness."
)

#: The concrete stack this packet would run against. Named as a dotted path so
#: the one-command property is checkable by reading, not by trusting prose.
LIVE_STACK_CONSTRUCTOR = (
    "orion.providers.live_phase2.build_phase2_live_provider_stack_from_env"
)
LIVE_RUNNER = "orion.self_orion.live_trial.ShadowLiveTrialRunner.from_providers"


def _sha256(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


# ---------------------------------------------------------------------------
# 1. Frozen identities, limits and evaluator
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FrozenProviderIdentity:
    """Who answers, declared before any answer exists -- and never the key.

    `credential_env_vars` names the variables the role needs. It holds names
    only; no field of this object may ever carry a credential value, which is
    why the writer re-checks the serialized document against the environment
    before it touches the disk.
    """

    role: str
    adapter: str
    identity: tuple[tuple[str, str], ...]
    credential_env_vars: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.role.strip() or not self.adapter.strip():
            raise ValueError("provider role and adapter are required")
        keys = [key for key, _ in self.identity]
        if len(set(keys)) != len(keys):
            raise ValueError("provider identity keys must be unique")
        if len(set(self.credential_env_vars)) != len(self.credential_env_vars):
            raise ValueError("provider credential env var names must be unique")

    @property
    def payload(self) -> dict[str, object]:
        return {
            "role": self.role,
            "adapter": self.adapter,
            "identity": dict(self.identity),
            "credential_env_vars": list(self.credential_env_vars),
            "secret_material_included": False,
        }


FROZEN_PROVIDERS: tuple[FrozenProviderIdentity, ...] = (
    FrozenProviderIdentity(
        role="reasoner",
        adapter="orion.providers.llm.openai_responses.OpenAIResponsesLLMProvider",
        identity=(
            ("model_env_var", "ORION_P5_REASONER_MODEL"),
            ("store", "false"),
            ("transport", "https"),
        ),
        credential_env_vars=("OPENAI_API_KEY",),
    ),
    FrozenProviderIdentity(
        role="retrieval",
        adapter=(
            "orion.providers.retrieval.literature."
            "MultiSourceLiteratureRetrievalProvider"
        ),
        identity=(
            ("policy", "strict-all-sources"),
            ("source_a", "europe-pmc-rest"),
            ("source_b", "crossref-rest"),
        ),
        # Both literature sources are open endpoints. The trial is therefore
        # not uniformly credential-blocked: retrieval and the mechanical
        # fibres could run today, which is why the blocked set below is
        # computed per fibre rather than asserted for the whole trial.
        credential_env_vars=(),
    ),
    FrozenProviderIdentity(
        role="protected_verification",
        adapter=(
            "orion.providers.verification.protected_http."
            "ProtectedHTTPVerificationProvider"
        ),
        identity=(
            ("endpoint_env_var", "ORION_PROTECTED_VERIFIER_URL"),
            ("custody", "outside_the_answering_lane"),
        ),
        credential_env_vars=(
            "ORION_PROTECTED_VERIFIER_TOKEN",
            "ORION_PROTECTED_VERIFIER_ARTIFACT_HASH",
            "ORION_PHASE2_EVALUATION_EPOCH_ID",
            "ORION_PROTECTED_VERIFIER_URL",
        ),
    ),
)

#: Every environment variable the frozen stack needs, in a stable order.
CREDENTIAL_ENV_VARS: tuple[str, ...] = tuple(
    dict.fromkeys(
        name for provider in FROZEN_PROVIDERS for name in provider.credential_env_vars
    )
)


@dataclass(frozen=True)
class FrozenResourceLimits:
    """The budget both arms receive. Frozen so the comparison is a comparison.

    `max_orion_to_baseline_ratio` is the matching constraint: ORION may not buy
    a result with resources the baseline was never offered. At 1.0 the two arms
    are budget-identical, which is the only setting under which a difference in
    outcome is attributable to method rather than to spend.
    """

    budget_units: float
    max_model_calls: int
    max_retrieval_calls: int
    max_model_tokens: int
    max_wallclock_seconds: float
    max_orion_to_baseline_ratio: float = 1.0

    def __post_init__(self) -> None:
        if self.budget_units <= 0 or self.max_wallclock_seconds <= 0:
            raise ValueError("trial budget and wallclock limit must be positive")
        if min(self.max_model_calls, self.max_retrieval_calls, self.max_model_tokens) < 1:
            raise ValueError("trial call/token limits must be positive")
        if self.max_orion_to_baseline_ratio <= 0:
            raise ValueError("resource matching ratio must be positive")

    @property
    def payload(self) -> dict[str, object]:
        return {
            "budget_units": self.budget_units,
            "max_model_calls": self.max_model_calls,
            "max_retrieval_calls": self.max_retrieval_calls,
            "max_model_tokens": self.max_model_tokens,
            "max_wallclock_seconds": self.max_wallclock_seconds,
            "max_orion_to_baseline_ratio": self.max_orion_to_baseline_ratio,
        }


FROZEN_LIMITS = FrozenResourceLimits(
    budget_units=24.0,
    max_model_calls=12,
    max_retrieval_calls=12,
    max_model_tokens=120_000,
    max_wallclock_seconds=900.0,
)


@dataclass(frozen=True)
class MatchedBaselineSpec:
    """The comparator, specified under the *same* limits object.

    Sharing the object rather than restating the numbers is deliberate: a
    baseline whose limits are typed out separately drifts from the system it is
    supposed to bound, and then the study reports a demonstration.
    """

    baseline_id: str
    implementation: str
    description: str
    limits: FrozenResourceLimits

    @property
    def payload(self) -> dict[str, object]:
        return {
            "baseline_id": self.baseline_id,
            "implementation": self.implementation,
            "description": self.description,
            "limits": self.limits.payload,
        }


FROZEN_BASELINE = MatchedBaselineSpec(
    baseline_id=BASELINE_ID,
    implementation="orion.self_orion.baseline.SimpleLLMRetrievalBaseline",
    description=(
        "One current-vocabulary retrieval call plus one completion, answering "
        "only from returned item ids. No ORION mechanics, no route ensemble, no "
        "residual detection, no failure learning. Runs under the identical "
        "FrozenResourceLimits object the ORION arm receives."
    ),
    limits=FROZEN_LIMITS,
)


class CriterionCheck(str, Enum):
    """The mechanical checks available to the frozen evaluator.

    Every member is computable from the raw trace, the answer text and the
    protected gold. None of them asks the system under test whether it
    succeeded, which is what "checkable without the model's cooperation" means:
    a self-reported `solved: true` is an input to be audited, never an outcome.
    """

    EVERY_CITATION_IN_RAW_TRACE = "EVERY_CITATION_IN_RAW_TRACE"
    DISTINCT_ROUTE_FAMILIES = "DISTINCT_ROUTE_FAMILIES"
    INDEPENDENT_CORROBORATION = "INDEPENDENT_CORROBORATION"
    RETRIEVAL_FULLY_CLASSIFIED = "RETRIEVAL_FULLY_CLASSIFIED"
    PROTECTED_GOLD_TOKENS_RECOVERED = "PROTECTED_GOLD_TOKENS_RECOVERED"
    PROTECTED_GOLD_ANCHOR_CITED = "PROTECTED_GOLD_ANCHOR_CITED"
    NON_RECOVERY_DECLARES_RESIDUAL = "NON_RECOVERY_DECLARES_RESIDUAL"
    RESOURCE_WITHIN_MATCHED_LIMIT = "RESOURCE_WITHIN_MATCHED_LIMIT"


@dataclass(frozen=True)
class CheckableCriterion:
    criterion_id: str
    check: CriterionCheck
    description: str
    threshold: int = 0

    def __post_init__(self) -> None:
        if not self.criterion_id.strip() or not self.description.strip():
            raise ValueError("criterion identity and description are required")
        if self.threshold < 0:
            raise ValueError("criterion threshold cannot be negative")

    @property
    def payload(self) -> dict[str, object]:
        return {
            "criterion_id": self.criterion_id,
            "check": self.check.value,
            "description": self.description,
            "threshold": self.threshold,
        }


@dataclass(frozen=True)
class FrozenEvaluatorSpec:
    """The evaluator, fixed before an outcome exists.

    `model_cooperation_required` is structurally pinned to False: a frozen
    evaluator that needs the system under test to agree it succeeded is not an
    evaluator. Construction refuses rather than warns.
    """

    evaluator_id: str
    criteria: tuple[CheckableCriterion, ...]
    model_cooperation_required: bool = False

    def __post_init__(self) -> None:
        if not self.evaluator_id.strip() or not self.criteria:
            raise ValueError("evaluator identity and criteria are required")
        ids = [item.criterion_id for item in self.criteria]
        if len(set(ids)) != len(ids):
            raise ValueError("evaluator criterion ids must be unique")
        if self.model_cooperation_required:
            raise ValueError(
                "a frozen evaluator may not depend on the model's cooperation"
            )

    @property
    def payload(self) -> dict[str, object]:
        return {
            "evaluator_id": self.evaluator_id,
            "criteria": [item.payload for item in self.criteria],
            "model_cooperation_required": False,
        }

    @property
    def artifact_hash(self) -> str:
        return _sha256(self.payload)

    def criterion(self, criterion_id: str) -> CheckableCriterion | None:
        return next(
            (item for item in self.criteria if item.criterion_id == criterion_id), None
        )


WIDE_CRITERIA: tuple[CheckableCriterion, ...] = (
    CheckableCriterion(
        "W1.citations-grounded",
        CriterionCheck.EVERY_CITATION_IN_RAW_TRACE,
        "Every cited item id appears verbatim in the retained raw retrieval trace.",
    ),
    CheckableCriterion(
        "W2.route-breadth",
        CriterionCheck.DISTINCT_ROUTE_FAMILIES,
        "At least four distinct route families returned at least one item.",
        threshold=4,
    ),
    CheckableCriterion(
        "W3.independent-corroboration",
        CriterionCheck.INDEPENDENT_CORROBORATION,
        "At least one item was captured by two route families with distinct backends.",
        threshold=1,
    ),
    CheckableCriterion(
        "W4.retrieval-classified",
        CriterionCheck.RETRIEVAL_FULLY_CLASSIFIED,
        "Every retrieved item is classified used / unused, with none dropped.",
    ),
    CheckableCriterion(
        "W5.resource-matched",
        CriterionCheck.RESOURCE_WITHIN_MATCHED_LIMIT,
        "ORION spend is within the frozen budget and the baseline-matched ratio.",
    ),
)

DEEP_CRITERIA: tuple[CheckableCriterion, ...] = (
    CheckableCriterion(
        "D1.citations-grounded",
        CriterionCheck.EVERY_CITATION_IN_RAW_TRACE,
        "Every cited item id appears verbatim in the retained raw retrieval trace.",
    ),
    CheckableCriterion(
        "D2.gold-tokens",
        CriterionCheck.PROTECTED_GOLD_TOKENS_RECOVERED,
        "The answer contains every protected gold token, checked against the "
        "held-out gold rather than against a self-report.",
    ),
    CheckableCriterion(
        "D3.gold-anchor-cited",
        CriterionCheck.PROTECTED_GOLD_ANCHOR_CITED,
        "The protected anchor source is among the cited evidence ids.",
    ),
    CheckableCriterion(
        "D4.non-recovery-declares-residual",
        CriterionCheck.NON_RECOVERY_DECLARES_RESIDUAL,
        "If the target is not recovered, a residual is declared; silence is a failure.",
    ),
    CheckableCriterion(
        "D5.retrieval-classified",
        CriterionCheck.RETRIEVAL_FULLY_CLASSIFIED,
        "Every retrieved item is classified used / unused, with none dropped.",
    ),
    CheckableCriterion(
        "D6.resource-matched",
        CriterionCheck.RESOURCE_WITHIN_MATCHED_LIMIT,
        "ORION spend is within the frozen budget and the baseline-matched ratio.",
    ),
)

FROZEN_EVALUATOR = FrozenEvaluatorSpec(
    evaluator_id="P5.shadow-live-research.evaluator.v1",
    criteria=WIDE_CRITERIA + DEEP_CRITERIA,
)


# ---------------------------------------------------------------------------
# 2. The two frozen tasks
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# 3. The packet
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FrozenLiveResearchPacket:
    """The whole frozen trial: tasks, providers, limits, evaluator, baseline.

    `outcome_accessed` is structurally pinned to False. The freeze is only
    meaningful if nothing in it was chosen after seeing a result, so the object
    refuses to exist in a state that claims otherwise.
    """

    packet_id: str
    schema: str
    evaluation_epoch_id: str
    trial: FrozenLiveTrialPacket
    bindings: tuple[FrozenTaskBinding, ...]
    providers: tuple[FrozenProviderIdentity, ...]
    limits: FrozenResourceLimits
    evaluator: FrozenEvaluatorSpec
    baseline: MatchedBaselineSpec
    corpus_revision: str = UNBOUND
    outcome_accessed: bool = False

    def __post_init__(self) -> None:
        if self.outcome_accessed:
            raise ValueError(
                "a packet frozen after outcome access is not a frozen packet"
            )
        task_ids = {item.task_id for item in self.trial.tasks}
        binding_ids = [item.task_id for item in self.bindings]
        if len(set(binding_ids)) != len(binding_ids):
            raise ValueError("task bindings must be unique")
        if set(binding_ids) != task_ids:
            raise ValueError("every frozen task requires exactly one binding")
        roles = [item.role for item in self.providers]
        if len(set(roles)) != len(roles):
            raise ValueError("provider roles must be unique")
        if self.baseline.limits != self.limits:
            raise ValueError(
                "the baseline must be specified under the same limits as ORION"
            )

    @property
    def tasks(self) -> tuple[FrozenTrialTask, ...]:
        return self.trial.tasks

    def binding(self, task_id: str) -> FrozenTaskBinding | None:
        return next((item for item in self.bindings if item.task_id == task_id), None)

    def task(self, task_id: str) -> FrozenTrialTask | None:
        return next((item for item in self.tasks if item.task_id == task_id), None)

    @property
    def body(self) -> dict[str, object]:
        """The published packet, without its own fingerprint.

        The fingerprint is attached afterwards by `packet_document`. Hashing a
        payload that already contains the hash is a fixed point nobody can
        recompute, so the digest would verify only itself.
        """

        return {
            "schema": self.schema,
            "packet_id": self.packet_id,
            "issue": "SzeChunYiu/ORION#8",
            "status": "DESIGN_FROZEN",
            "outcome_accessed": self.outcome_accessed,
            "evaluation_epoch_id": self.evaluation_epoch_id,
            "success_boundary": SUCCESS_BOUNDARY,
            "corpus_revision": self.corpus_revision,
            "tasks": [
                {
                    "task_id": item.task_id,
                    "kind": item.kind.value,
                    "split_id": item.split_id,
                    "question": item.problem.question,
                    "scope": item.problem.scope,
                    "initial_domain_ids": list(item.problem.initial_domain_ids),
                    "success_criteria": list(item.problem.success_criteria),
                    "variation_signature": list(item.variation_signature),
                    "required_evidence_ids": list(item.required_evidence_ids),
                }
                for item in sorted(self.tasks, key=lambda entry: entry.task_id)
            ],
            "task_bindings": [
                item.payload
                for item in sorted(self.bindings, key=lambda entry: entry.task_id)
            ],
            "providers": [
                item.payload
                for item in sorted(self.providers, key=lambda entry: entry.role)
            ],
            "resource_limits": self.limits.payload,
            "evaluator": self.evaluator.payload,
            "matched_baseline": self.baseline.payload,
            "provider_manifest_hash": self.trial.provider_manifest_hash,
            "evaluator_artifact_hash": self.trial.evaluator_artifact_hash,
            "trial_fingerprint": self.trial.fingerprint,
            "execution": {
                "stack_constructor": LIVE_STACK_CONSTRUCTOR,
                "runner": LIVE_RUNNER,
                "credential_env_vars": list(CREDENTIAL_ENV_VARS),
                "command": "python -m orion.self_orion.live_packet --live",
            },
            "authority": {
                "model_output_may_increase_authority": False,
                "self_orion_may_merge_or_promote": False,
                "repairs": "proposal_only",
            },
        }

    @property
    def fingerprint(self) -> str:
        return _sha256(self.body)


def _provider_manifest_hash(
    providers: Sequence[FrozenProviderIdentity],
) -> str:
    return _sha256(
        {
            "schema": "P5.shadow-live-research.provider-manifest.v1",
            "providers": [item.payload for item in sorted(providers, key=lambda e: e.role)],
            "secret_material_included": False,
        }
    )


def frozen_live_research_packet(
    *, corpus_revision: str = UNBOUND
) -> FrozenLiveResearchPacket:
    """Build the frozen packet. Deterministic: same inputs, same fingerprint.

    `corpus_revision` is the one field bound at execution rather than at freeze.
    The deep-target corpus is a working checkout under concurrent edit, so a
    digest baked in here would be stale on arrival; the preflight refuses to
    call the trial runnable while it is UNBOUND.
    """

    tasks = (_WIDE_TASK, _DEEP_TASK)
    bindings = (
        FrozenTaskBinding(WIDE_TASK_ID, WIDE_CRITERIA, None, corpus_revision),
        FrozenTaskBinding(DEEP_TASK_ID, DEEP_CRITERIA, _DEEP_TASK_GOLD, corpus_revision),
    )
    trial = FrozenLiveTrialPacket(
        packet_id=PACKET_ID,
        evaluation_epoch_id=EVALUATION_EPOCH_ID,
        tasks=tasks,
        provider_manifest_hash=_provider_manifest_hash(FROZEN_PROVIDERS),
        evaluator_artifact_hash=FROZEN_EVALUATOR.artifact_hash,
        baseline_id=BASELINE_ID,
        resource_budget_units=FROZEN_LIMITS.budget_units,
        max_orion_to_baseline_resource_ratio=FROZEN_LIMITS.max_orion_to_baseline_ratio,
    )
    return FrozenLiveResearchPacket(
        packet_id=PACKET_ID,
        schema=PACKET_SCHEMA,
        evaluation_epoch_id=EVALUATION_EPOCH_ID,
        trial=trial,
        bindings=bindings,
        providers=FROZEN_PROVIDERS,
        limits=FROZEN_LIMITS,
        evaluator=FROZEN_EVALUATOR,
        baseline=FROZEN_BASELINE,
        corpus_revision=corpus_revision,
    )


def packet_document(packet: FrozenLiveResearchPacket | None = None) -> dict[str, object]:
    """The exact JSON published to `papers/.../LIVE_TRIAL_PACKET_V1.json`."""

    resolved = packet or frozen_live_research_packet()
    document = dict(resolved.body)
    document["packet_fingerprint"] = resolved.fingerprint
    return document


def _reject_secret_material(serialized: str) -> None:
    """Refuse to write a document containing any credential currently in the env.

    Mirrors `write_live_phase2_provider_manifest`. Short values are skipped: a
    variable set to something like `1` would match everywhere and turn a real
    guard into noise, and a checker that cries wolf on its first run is switched
    off before it ever catches anything.
    """

    for name in CREDENTIAL_ENV_VARS:
        value = os.environ.get(name, "")
        if len(value) >= 12 and value in serialized:
            raise RuntimeError(
                f"packet serialization attempted to include the value of {name}"
            )


def write_packet_document(
    path: Path | str = PROTOCOL_PATH,
    *,
    packet: FrozenLiveResearchPacket | None = None,
) -> Path:
    """Publish the packet, refusing to rewrite the frozen one at a new fingerprint.

    The canonical protocol path is the freeze. Binding a corpus revision changes
    the fingerprint, so writing an execution-bound packet over the checked-in one
    would replace the frozen artifact with a different document under the same
    name -- and an artifact any later command can rewrite in place is not frozen,
    whatever it is hashed with. Execution-bound packets go somewhere else.
    """

    resolved = packet or frozen_live_research_packet()
    target = Path(path)
    if (
        target.resolve() == PROTOCOL_PATH.resolve()
        and resolved.corpus_revision != UNBOUND
    ):
        raise ValueError(
            "refusing to overwrite the frozen protocol packet with a corpus-bound "
            f"one (revision {resolved.corpus_revision!r}); write it to another path"
        )
    serialized = json.dumps(packet_document(resolved), indent=2, sort_keys=True) + "\n"
    _reject_secret_material(serialized)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(serialized, encoding="utf-8")
    return target


def load_packet_document(path: Path | str = PROTOCOL_PATH) -> dict[str, object]:
    """Read the published packet and verify its declared fingerprint.

    A hand-edited packet fails here rather than being trusted, which is the only
    reason freezing a document by content hash is worth doing.
    """

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("packet document must be a JSON object")
    declared = raw.get("packet_fingerprint")
    body = {key: value for key, value in raw.items() if key != "packet_fingerprint"}
    if declared != _sha256(body):
        raise ValueError("packet document fingerprint mismatch")
    return raw


# ---------------------------------------------------------------------------
# 4. The mechanical question surface
# ---------------------------------------------------------------------------

#: The eight dimensions issue #8 names. They are exposed by the fixed audit
#: grammar in `orion.mechanics.questioning`, so completeness is a property of
#: the grammar rather than of a model's willingness to volunteer a gap.
ISSUE_8_DIMENSIONS: tuple[MechanicDimension, ...] = (
    MechanicDimension.OBSERVABILITY,
    MechanicDimension.MATHEMATICS,
    MechanicDimension.HANDOFF,
    MechanicDimension.FAILURE,
    MechanicDimension.STORAGE,
    MechanicDimension.VERIFICATION,
    MechanicDimension.PARENT_DISCIPLINE,
    MechanicDimension.SATURATION,
)

#: Which provider role each fibre needs. A fibre with no role runs today; the
#: rest are blocked exactly when their role's variables are absent, which is why
#: the trial is partially rather than wholly credential-blocked.
FIBRE_PROVIDER_ROLES: dict[str, str] = {
    "p5.live.search": "retrieval",
    "p5.live.interpretation": "reasoner",
    "p5.live.absorption": "reasoner",
    "p5.live.reconstruction": "reasoner",
    "p5.live.residual_detection": "",
    "p5.live.diagnosis": "reasoner",
    "p5.live.saturation": "",
    "p5.live.verification": "protected_verification",
}

_SHARED_AUTHORITY = (
    "may emit evidence, residuals and proposals",
    "may never raise its own lesson authority",
    "may never merge, promote or modify the evaluator",
)
_SHARED_RESOURCES = (
    "resource:model_calls",
    "resource:retrieval_calls",
    "resource:model_tokens",
    "resource:wallclock_seconds",
)
_SHARED_ENGINEERING = (
    "every execution emits a receipt, including refusals",
    "no exclusion path: failed and empty executions are retained verbatim",
)
_SHARED_PROVENANCE = (
    "evidence is identified by content digest, never by retrieval id",
    "the frozen packet fingerprint is recorded on every artifact",
)
_SHARED_REOPEN = (
    "a provider identity, limit or evaluator change voids the freeze",
    "a corpus revision change voids every deep-target result",
)


def _fibre(
    mechanic_id: str,
    purpose: str,
    scope: str,
    **fields: object,
) -> MechanicCell:
    return MechanicCell(
        mechanic_id=mechanic_id,
        purpose=purpose,
        scope=scope,
        authority_boundaries=_SHARED_AUTHORITY,
        resource_coordinates=_SHARED_RESOURCES,
        engineering_contracts=_SHARED_ENGINEERING,
        provenance_contracts=_SHARED_PROVENANCE,
        reopen_triggers=_SHARED_REOPEN,
        **fields,  # type: ignore[arg-type]
    )


def live_trial_mechanic_cells() -> tuple[MechanicCell, ...]:
    """The eight fibres issue #8's development protocol asks for, as fixed cells.

    Each cell states what the packet genuinely determines and leaves open what
    only execution can settle. Two mechanisms produce an open question, and both
    are honest: an unfilled field, and a field that is filled but listed in
    `provisional_dimensions` because the contract is stated while its adequacy is
    unestablished. Nothing is blanked to manufacture a question -- if a cell were
    padded to force a dimension open, the surface would be measuring the padding.
    """

    return (
        _fibre(
            "p5.live.search",
            "Issue route-family queries against live retrieval backends and retain every raw query and result.",
            "One frozen task at a time; retrieval only, no interpretation.",
            input_ids=("frozen_task", "route_binding_set"),
            output_ids=("raw_query_trace", "route_captures"),
            handoff_fields=(
                HandoffField(
                    "raw_query_trace",
                    "Every query issued and every item returned, including empties and errors.",
                    "orion.self_orion.live_packet.RawTrialTrace",
                ),
            ),
            state_ids=("issued_query_count", "retained_item_digests"),
            observable_ids=(
                "queries_issued",
                "items_per_route",
                "zero_result_queries",
                "route_errors",
                "distinct_backends",
            ),
            action_ids=("action:issue_query", "action:record_capture"),
            transition_semantics=(
                "stochastic: a live backend may return different results for the same query",
            ),
            mathematical_semantics=(
                "route overlap as capture occasions; Lincoln-Petersen on independent pairs only",
            ),
            objective_ids=("objective:breadth_before_depth",),
            metrics=(
                MetricSpec(
                    metric_id="distinct_route_families",
                    description="Route families that returned at least one item.",
                    kind=MetricKind.COVERAGE,
                    direction=MetricDirection.NON_COMPENSATORY_GATE,
                    unit="families",
                    required_for_handoff=True,
                    threshold_semantics="at least four; breadth cannot be bought with depth",
                ),
            ),
            uncertainty_semantics=(
                "an unavailable route is a coverage gap, never an absence of results",
            ),
            failure_signatures=("route_unavailable", "zero_results", "backend_error"),
            falsifiers=(
                "a later route with a distinct backend returns items this ensemble missed",
            ),
            diagnosis_rules=("separate backend error from genuine empty result",),
            storage_contracts=("the raw trace is persisted verbatim before any use",),
            verification_contracts=(
                "cited ids are checked against the raw trace by the frozen evaluator",
            ),
            dependency_ids=(),
            external_dependency_contract_ids=("provider:retrieval",),
            search_coverage_obligations=(
                "current vocabulary, function-only, parent-discipline and adversarial-omission routes",
            ),
            parent_domain_hypotheses=(
                "information retrieval: recall-oriented query expansion",
                "systematic review screening: source-family coverage",
                "capture-recapture: unseen-mass estimation from occasion overlap",
            ),
            # Stated but unestablished: whether these backends are independent
            # occasions at all is exactly what the live run would measure.
            provisional_dimensions=(
                MechanicDimension.VERIFICATION,
                MechanicDimension.SATURATION,
            ),
            saturation_criteria=(
                "flat when an added route family yields no new content digest",
            ),
        ),
        _fibre(
            "p5.live.interpretation",
            "Turn retrieved documents into typed claims without inventing evidence identifiers.",
            "Per retrieved document; no binding to the knowledge state.",
            input_ids=("retrieved_item", "open_question"),
            output_ids=("typed_claim", "unknown_id_report"),
            handoff_fields=(
                HandoffField(
                    "typed_claims",
                    "Claims with the exact item id each rests on.",
                    "orion.core.solution.Solution.evidence_ids",
                ),
            ),
            state_ids=("claims_extracted",),
            observable_ids=("citation_grounding_rate", "unknown_id_rate", "parse_errors"),
            action_ids=("action:extract_claim", "action:reject_ungrounded_claim"),
            transition_semantics=("stochastic: model output varies across identical prompts",),
            objective_ids=("objective:no_ungrounded_claim",),
            uncertainty_semantics=("an unparseable response is CANNOT_CHECK, never zero claims",),
            failure_signatures=("ungrounded_citation", "unparseable_response"),
            falsifiers=("a claimed item id is absent from the raw trace",),
            diagnosis_rules=("separate transport failure from refusal from malformed output",),
            verification_contracts=("every cited id must appear verbatim in the raw trace",),
            external_dependency_contract_ids=("provider:reasoner",),
            search_coverage_obligations=("re-read a document per question, not per corpus",),
            parent_domain_hypotheses=(
                "information extraction and argumentation mining",
                "citation verification in evidence synthesis",
            ),
            saturation_criteria=("flat when re-reading a document yields no new claim id",),
            # MATHEMATICS and STORAGE stay empty: no formalism for extraction
            # fidelity is committed here, and what must persist from an
            # interpretation pass is genuinely unsettled before a run.
        ),
        _fibre(
            "p5.live.absorption",
            "Bind interpreted claims into the knowledge state under content digests.",
            "Per claim; idempotent under repeated absorption of the same content.",
            input_ids=("typed_claim", "knowledge_state"),
            output_ids=("bound_evidence_id", "absorption_receipt"),
            handoff_fields=(
                HandoffField(
                    "absorbed_evidence_ids",
                    "Evidence ids now bound into the knowledge state.",
                    "orion.experience.model.TaskEpisode.evidence_bindings",
                ),
            ),
            state_ids=("knowledge_state_hash",),
            observable_ids=("absorbed_count", "duplicate_rate", "digest_drift_events"),
            action_ids=("action:bind_evidence",),
            transition_semantics=("deterministic given content: same digest, same binding",),
            invariant_ids=("invariant:every_evidence_id_is_content_bound",),
            objective_ids=("objective:no_unbound_evidence",),
            uncertainty_semantics=("a digest that changed between capture and binding is a hard error",),
            storage_contracts=("bindings are append-only and content-addressed",),
            verification_contracts=("binding digests are recomputed on replay, never trusted",),
            external_dependency_contract_ids=("provider:reasoner",),
            search_coverage_obligations=("absorption never adds sources the trace does not contain",),
            parent_domain_hypotheses=("knowledge-base construction and entity resolution",),
            # Signatures without falsifiers: we know how absorption breaks, and
            # we do not yet know what observation would show it worked.
            failure_signatures=("duplicate_absorption", "digest_drift"),
            provisional_dimensions=(MechanicDimension.SATURATION,),
            saturation_criteria=("flat when no new content digest binds in a round",),
        ),
        _fibre(
            "p5.live.reconstruction",
            "Assemble an answer to the frozen task from absorbed evidence only.",
            "Per task; no new retrieval, no unbound assertion.",
            input_ids=("frozen_task", "absorbed_evidence"),
            output_ids=("answer_text", "cited_evidence_ids"),
            handoff_fields=(
                HandoffField(
                    "answer",
                    "Answer text plus the exact evidence ids it rests on.",
                    "orion.core.solution.Solution",
                ),
            ),
            state_ids=("answer_draft_hash",),
            observable_ids=("cited_count", "uncited_assertion_count", "answer_length"),
            action_ids=("action:compose_answer",),
            transition_semantics=("stochastic: composition varies across identical inputs",),
            objective_ids=("objective:answer_entirely_from_bound_evidence",),
            uncertainty_semantics=("an unsupported span is a residual, not a hedge",),
            failure_signatures=("assertion_without_evidence", "target_not_named"),
            falsifiers=("the protected gold tokens are absent from the answer",),
            diagnosis_rules=("separate a missing retrieval from a present-but-unused document",),
            storage_contracts=("answer text and cited ids are stored together, immutably",),
            external_dependency_contract_ids=("provider:reasoner",),
            search_coverage_obligations=("reconstruction may not silently widen the evidence base",),
            saturation_criteria=("flat when recomposition changes no cited id",),
            # PARENT_DISCIPLINE left empty: which mature discipline owns
            # "reconstruct a claim from retrieved evidence" is contested across
            # evidence synthesis, argumentation and KB construction, and naming
            # one here would be a guess dressed as a hypothesis.
            provisional_dimensions=(MechanicDimension.VERIFICATION,),
            verification_contracts=("the frozen evaluator checks tokens and anchors, not self-reports",),
        ),
        _fibre(
            "p5.live.residual_detection",
            "Name what the answer does not cover, so silence cannot pass as coverage.",
            "Per answer; produces residuals, never repairs them.",
            input_ids=("answer_text", "frozen_task"),
            output_ids=("residual_ids",),
            handoff_fields=(
                HandoffField(
                    "residual_ids",
                    "Named gaps between the task and the answer.",
                    "orion.core.solution.Solution.residual_ids",
                ),
            ),
            state_ids=("declared_residuals",),
            action_ids=("action:declare_residual",),
            transition_semantics=("deterministic given the answer and the task criteria",),
            mathematical_semantics=("set difference between task criteria and satisfied criteria",),
            objective_ids=("objective:no_silent_gap",),
            uncertainty_semantics=("an undetectable gap is CANNOT_CHECK, not an empty residual set",),
            storage_contracts=("residuals are stored on the episode, not recomputed later",),
            verification_contracts=("a non-recovering answer with no residual fails criterion D4",),
            parent_domain_hypotheses=("gap analysis in systematic reviews",),
            saturation_criteria=("flat when a round declares no new residual kind",),
            # OBSERVABILITY empty and FAILURE without falsifiers: what signal
            # distinguishes a declared residual from an undetected one is the
            # open question this fibre exists to expose.
            failure_signatures=("undetected_gap", "residual_without_evidence"),
        ),
        _fibre(
            "p5.live.diagnosis",
            "Separate retrieved-but-unused from present-but-missed and from absent-from-corpus.",
            "Per task, over the raw trace and, where bound, the ground truth.",
            input_ids=("raw_query_trace", "cited_evidence_ids", "ground_truth_or_none"),
            output_ids=("evidence_use_report",),
            handoff_fields=(
                HandoffField(
                    "evidence_use_report",
                    "Every trace item classified, with CANNOT_CHECK where ground truth is unbound.",
                    "orion.self_orion.live_packet.EvidenceUseReport",
                ),
            ),
            state_ids=("classified_item_count",),
            observable_ids=("used", "retrieved_but_unused", "present_but_missed", "cannot_check"),
            action_ids=("action:classify_evidence_use",),
            transition_semantics=("deterministic given trace, citations and ground truth",),
            mathematical_semantics=("set algebra over trace ids, cited ids and corpus ids",),
            objective_ids=("objective:attribute_failure_to_one_stage",),
            uncertainty_semantics=(
                "unbound ground truth yields CANNOT_CHECK for present-but-missed, never zero",
            ),
            storage_contracts=("the report is stored on an immutable episode",),
            verification_contracts=("classification totality is checked: every trace id appears once",),
            parent_domain_hypotheses=(
                "fault localization: separating a missing signal from an ignored one",
                "recall-oriented IR error analysis",
            ),
            # FAILURE without falsifiers and SATURATION empty: with the wide
            # task's ground truth UNBOUND, what would falsify a diagnosis is
            # unestablished, and so is what a saturated diagnosis would mean.
            failure_signatures=("misattributed_stage", "ground_truth_unbound"),
        ),
        _fibre(
            "p5.live.saturation",
            "Decide whether repeated route challenges are flat under a declared basis.",
            "Per task; a budget decision, never a recall claim.",
            input_ids=("growth_vectors", "saturation_basis"),
            output_ids=("bounded_saturation_state",),
            handoff_fields=(
                HandoffField(
                    "bounded_saturation_state",
                    "OPEN, CANNOT_CHECK or a bounded flat verdict, with reasons.",
                    "orion.self_orion.live_packet.BoundedSaturationState",
                ),
            ),
            state_ids=("flat_streak", "basis_fingerprint"),
            observable_ids=("flat_rounds", "independent_flat_rounds", "growth_magnitude"),
            action_ids=("action:assess_saturation",),
            transition_semantics=("deterministic given the growth vectors and the basis",),
            mathematical_semantics=(
                "non-compensatory growth magnitude; rule of three on independent flat rounds",
            ),
            invariant_ids=("invariant:no_verdict_certifies_recall",),
            objective_ids=("objective:stop_honestly",),
            uncertainty_semantics=("OPEN and CANNOT_CHECK are outcomes, not failures",),
            failure_signatures=("false_flatness_by_starvation", "unidentified_lineage"),
            falsifiers=("a new route family produces growth after a flat verdict",),
            diagnosis_rules=("check selection-window starvation before calling a run flat",),
            storage_contracts=("growth vectors are persisted per round with the basis fingerprint",),
            parent_domain_hypotheses=(
                "qualitative research: a priori thematic saturation",
                "technology-assisted review: stopping rules and target recall",
            ),
            # Both provisional: the basis is declared, and whether it measures
            # anything for a live trial is precisely unestablished.
            provisional_dimensions=(
                MechanicDimension.SATURATION,
                MechanicDimension.VERIFICATION,
            ),
            saturation_criteria=("two independent flat rounds under a fixed basis",),
            verification_contracts=("the basis fingerprint is recomputed, never trusted",),
        ),
        _fibre(
            "p5.live.verification",
            "Obtain verification from a lane that did not produce the answer.",
            "Per task; the only fibre that may close a criterion.",
            input_ids=("answer_text", "cited_evidence_ids", "frozen_evaluator"),
            output_ids=("criterion_results",),
            handoff_fields=(
                HandoffField(
                    "criterion_results",
                    "One result per frozen criterion, including CANNOT_CHECK.",
                    "orion.self_orion.live_packet.CriterionResult",
                ),
            ),
            state_ids=("closed_criteria",),
            observable_ids=("passed", "failed", "cannot_check"),
            action_ids=("action:evaluate_criterion",),
            transition_semantics=("deterministic given the answer, the trace and the gold",),
            mathematical_semantics=("predicate evaluation per criterion; no scalar aggregate",),
            invariant_ids=("invariant:verification_never_originates_in_the_answering_lane",),
            objective_ids=("objective:independent_closure",),
            uncertainty_semantics=("an unreachable verifier is CANNOT_CHECK, never a fail",),
            failure_signatures=("verifier_unreachable", "evaluator_hash_mismatch"),
            falsifiers=("a criterion passes under a different evaluator artifact hash",),
            diagnosis_rules=("separate verifier transport failure from a genuine criterion failure",),
            external_dependency_contract_ids=("provider:protected_verification",),
            parent_domain_hypotheses=("independent replication and protected-holdout evaluation",),
            saturation_criteria=("flat when no criterion changes state across rounds",),
            # HANDOFF and VERIFICATION provisional, STORAGE empty: the receipt
            # schema is stated but not shown to make the receipt independently
            # checkable, and what must persist from a verification pass is
            # unsettled until a protected verifier has actually answered.
            provisional_dimensions=(
                MechanicDimension.HANDOFF,
                MechanicDimension.VERIFICATION,
            ),
            verification_contracts=("the evaluator artifact hash is bound into every receipt",),
        ),
    )


def emit_open_questions(
    cells: Sequence[MechanicCell] | None = None,
    *,
    dimensions: Sequence[MechanicDimension] = ISSUE_8_DIMENSIONS,
) -> tuple[MechanicQuestion, ...]:
    """Emit the open questions for the named dimensions. No provider involved.

    Deliberately calls `generate_mechanic_questions` per cell and filters, rather
    than routing through `plan_next_questions`: that selector's default window is
    eight slots taken in `_PRIORITY` order, which cuts PARENT_DISCIPLINE,
    SATURATION and STORAGE -- three of the eight this issue requires -- before
    they are ever asked. A selection window that never asks is the starvation
    failure the kernel already names; it must not be reintroduced here.
    """

    wanted = tuple(dimensions)
    resolved = tuple(cells) if cells is not None else live_trial_mechanic_cells()
    questions: list[MechanicQuestion] = []
    for cell in resolved:
        questions.extend(
            item
            for item in generate_mechanic_questions(cell)
            if item.dimension in wanted
        )
    return tuple(questions)


@dataclass(frozen=True)
class QuestionSurfaceCoverage:
    covered: tuple[MechanicDimension, ...]
    missing: tuple[MechanicDimension, ...]

    @property
    def complete(self) -> bool:
        return not self.missing


def question_surface_coverage(
    cells: Sequence[MechanicCell] | None = None,
) -> QuestionSurfaceCoverage:
    """Which of the eight dimensions the fixed cells actually expose."""

    emitted = {item.dimension for item in emit_open_questions(cells)}
    return QuestionSurfaceCoverage(
        covered=tuple(item for item in ISSUE_8_DIMENSIONS if item in emitted),
        missing=tuple(item for item in ISSUE_8_DIMENSIONS if item not in emitted),
    )


def question_surface_summary(
    cells: Sequence[MechanicCell] | None = None,
) -> dict[str, object]:
    """Machine-readable view of the surface, filtered and unfiltered.

    Both counts are reported so the eight-dimension filter cannot hide the rest
    of the audit grammar: a surface that showed only what it was asked for would
    be the completeness problem this substrate exists to remove.
    """

    resolved = tuple(cells) if cells is not None else live_trial_mechanic_cells()
    total = sum(len(generate_mechanic_questions(cell)) for cell in resolved)
    emitted = emit_open_questions(resolved)
    by_dimension: dict[str, int] = {}
    for item in emitted:
        by_dimension[item.dimension.value] = by_dimension.get(item.dimension.value, 0) + 1
    coverage = question_surface_coverage(resolved)
    return {
        "provider_required": False,
        "mechanic_cells": len(resolved),
        "open_questions_total": total,
        "open_questions_issue_8": len(emitted),
        "by_dimension": dict(sorted(by_dimension.items())),
        "uncovered_dimensions": [item.value for item in coverage.missing],
        "question_ids": [item.question_id for item in emitted],
    }


# ---------------------------------------------------------------------------
# 5. Raw trace retention and evidence-use classification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TraceItem:
    item_id: str
    content_digest: str
    source_uri: str

    def __post_init__(self) -> None:
        if not self.item_id.strip() or not self.content_digest.strip():
            raise ValueError("trace item identity and content digest are required")


@dataclass(frozen=True)
class QueryTrace:
    """One raw retrieval occasion, retained whether or not it produced anything.

    An errored or empty query is kept with the same status as a productive one.
    A trace that drops its empties cannot distinguish "this route found nothing"
    from "this route was never tried", and those are different failures.
    """

    query_id: str
    query_text: str
    route_kind: SearchRouteKind
    backend: str
    query_derivation: str
    items: tuple[TraceItem, ...] = ()
    error: str = ""

    def __post_init__(self) -> None:
        if not self.query_id.strip() or not self.query_text.strip():
            raise ValueError("query trace identity and text are required")
        if not self.backend.strip() or not self.query_derivation.strip():
            raise ValueError(
                "a query trace must declare its backend and query derivation; "
                "independence is constructed, not assumed"
            )

    @property
    def productive(self) -> bool:
        return bool(self.items) and not self.error


@dataclass(frozen=True)
class RawTrialTrace:
    """Append-only record of every query issued for one task.

    There is no filter, predicate or `skip_if_empty` on this path by design:
    "preserve all failures and nulls" is only true if there is nowhere for a
    record to be dropped.
    """

    task_id: str
    records: tuple[QueryTrace, ...] = ()

    def extend(self, *queries: QueryTrace) -> RawTrialTrace:
        return replace(self, records=self.records + tuple(queries))

    @property
    def item_ids(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(item.item_id for record in self.records for item in record.items)
        )

    @property
    def empty_queries(self) -> tuple[QueryTrace, ...]:
        return tuple(item for item in self.records if not item.items)

    @property
    def errored_queries(self) -> tuple[QueryTrace, ...]:
        return tuple(item for item in self.records if item.error)

    @property
    def route_kinds(self) -> tuple[SearchRouteKind, ...]:
        return tuple(dict.fromkeys(item.route_kind for item in self.records))

    @property
    def productive_route_kinds(self) -> tuple[SearchRouteKind, ...]:
        return tuple(
            dict.fromkeys(item.route_kind for item in self.records if item.productive)
        )

    def routes_for(self, item_id: str) -> tuple[tuple[SearchRouteKind, str], ...]:
        """(route, backend) pairs that returned this item."""

        return tuple(
            dict.fromkeys(
                (record.route_kind, record.backend)
                for record in self.records
                if any(item.item_id == item_id for item in record.items)
            )
        )

    @property
    def fingerprint(self) -> str:
        return _sha256(
            {
                "task_id": self.task_id,
                "records": [
                    {
                        "query_id": record.query_id,
                        "query_text": record.query_text,
                        "route_kind": record.route_kind.value,
                        "backend": record.backend,
                        "query_derivation": record.query_derivation,
                        "error": record.error,
                        "items": [
                            {
                                "item_id": item.item_id,
                                "content_digest": item.content_digest,
                                "source_uri": item.source_uri,
                            }
                            for item in record.items
                        ],
                    }
                    for record in self.records
                ],
            }
        )


class EvidenceUseClass(str, Enum):
    """Why a piece of evidence did or did not reach the answer."""

    USED = "USED"
    RETRIEVED_BUT_UNUSED = "RETRIEVED_BUT_UNUSED"
    PRESENT_BUT_MISSED = "PRESENT_BUT_MISSED"
    CITED_BUT_UNRETRIEVED = "CITED_BUT_UNRETRIEVED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class EvidenceUseReport:
    task_id: str
    classes: tuple[tuple[str, EvidenceUseClass], ...]
    ground_truth_bound: bool
    cannot_check_reason: str = ""

    def _of(self, kind: EvidenceUseClass) -> tuple[str, ...]:
        return tuple(item for item, value in self.classes if value is kind)

    @property
    def used(self) -> tuple[str, ...]:
        return self._of(EvidenceUseClass.USED)

    @property
    def retrieved_but_unused(self) -> tuple[str, ...]:
        return self._of(EvidenceUseClass.RETRIEVED_BUT_UNUSED)

    @property
    def present_but_missed(self) -> tuple[str, ...]:
        return self._of(EvidenceUseClass.PRESENT_BUT_MISSED)

    @property
    def cited_but_unretrieved(self) -> tuple[str, ...]:
        return self._of(EvidenceUseClass.CITED_BUT_UNRETRIEVED)

    @property
    def cannot_check(self) -> tuple[str, ...]:
        return self._of(EvidenceUseClass.CANNOT_CHECK)


def classify_evidence_use(
    trace: RawTrialTrace,
    *,
    cited_ids: Sequence[str],
    corpus_present_ids: frozenset[str] | None = None,
) -> EvidenceUseReport:
    """Classify every trace item, every citation and every known-present item.

    The distinction issue #8 asks for lives in `corpus_present_ids`. When ground
    truth is bound, an item the corpus contains but the trace never returned is
    PRESENT_BUT_MISSED: a search failure, not an answering failure. When it is
    unbound, the same item is unobservable, and the report says CANNOT_CHECK
    rather than reporting zero misses -- an unbound answer key that silently
    reads as "nothing was missed" is the exact conflation the P1 provider's
    typed refusal exists to prevent.

    Classification is total: every id from the trace, the citations and the
    corpus appears exactly once, so no item can fall out of the report.
    """

    cited = tuple(dict.fromkeys(cited_ids))
    retrieved = set(trace.item_ids)
    classes: list[tuple[str, EvidenceUseClass]] = []
    seen: set[str] = set()

    def _add(item_id: str, kind: EvidenceUseClass) -> None:
        if item_id in seen:
            return
        seen.add(item_id)
        classes.append((item_id, kind))

    for item_id in cited:
        _add(
            item_id,
            EvidenceUseClass.USED
            if item_id in retrieved
            else EvidenceUseClass.CITED_BUT_UNRETRIEVED,
        )
    for item_id in trace.item_ids:
        _add(item_id, EvidenceUseClass.RETRIEVED_BUT_UNUSED)
    if corpus_present_ids is not None:
        for item_id in sorted(corpus_present_ids):
            _add(item_id, EvidenceUseClass.PRESENT_BUT_MISSED)
        reason = ""
    else:
        reason = (
            "ground truth for this task is UNBOUND, so present-but-missed cannot "
            "be separated from absent-from-corpus; this is CANNOT_CHECK, not zero"
        )
        _add(f"{trace.task_id}:present_but_missed", EvidenceUseClass.CANNOT_CHECK)
    return EvidenceUseReport(
        task_id=trace.task_id,
        classes=tuple(classes),
        ground_truth_bound=corpus_present_ids is not None,
        cannot_check_reason=reason,
    )


# ---------------------------------------------------------------------------
# 6. Frozen evaluation over a trace (no model cooperation anywhere)
# ---------------------------------------------------------------------------


class CriterionStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class CriterionResult:
    criterion_id: str
    check: CriterionCheck
    status: CriterionStatus
    detail: str = ""
    observed: int | None = None


@dataclass(frozen=True)
class TaskOutcomeInput:
    """Everything the frozen evaluator reads. None of it is a self-report."""

    task_id: str
    trace: RawTrialTrace
    answer_text: str
    cited_ids: tuple[str, ...]
    residual_ids: tuple[str, ...] = ()
    orion_resource_units: float | None = None
    baseline_resource_units: float | None = None


def evaluate_task(
    packet: FrozenLiveResearchPacket,
    outcome: TaskOutcomeInput,
) -> tuple[CriterionResult, ...]:
    """Run every frozen criterion for one task. Every criterion returns a result.

    There is no early exit and no exclusion: an uncheckable criterion produces
    CANNOT_CHECK rather than being skipped, because "could not check" and
    "checked and passed" are different facts and a suite that drops the first
    reports the second.
    """

    binding = packet.binding(outcome.task_id)
    if binding is None:
        raise ValueError(f"unknown task for this packet: {outcome.task_id}")
    report = classify_evidence_use(outcome.trace, cited_ids=outcome.cited_ids)
    gold = binding.gold
    results: list[CriterionResult] = []
    for criterion in binding.criteria:
        results.append(_evaluate_criterion(criterion, packet, binding, outcome, report, gold))
    return tuple(results)


def _evaluate_criterion(
    criterion: CheckableCriterion,
    packet: FrozenLiveResearchPacket,
    binding: FrozenTaskBinding,
    outcome: TaskOutcomeInput,
    report: EvidenceUseReport,
    gold: ProtectedTargetGold | None,
) -> CriterionResult:
    check = criterion.check
    if check is CriterionCheck.EVERY_CITATION_IN_RAW_TRACE:
        ungrounded = report.cited_but_unretrieved
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if not ungrounded else CriterionStatus.FAIL,
            "" if not ungrounded else f"ungrounded citations: {list(ungrounded)}",
            observed=len(ungrounded),
        )
    if check is CriterionCheck.DISTINCT_ROUTE_FAMILIES:
        observed = len(outcome.trace.productive_route_kinds)
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if observed >= criterion.threshold else CriterionStatus.FAIL,
            f"{observed} productive route families, {criterion.threshold} required",
            observed=observed,
        )
    if check is CriterionCheck.INDEPENDENT_CORROBORATION:
        observed = sum(
            1
            for item_id in outcome.trace.item_ids
            if len({backend for _, backend in outcome.trace.routes_for(item_id)}) > 1
        )
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if observed >= criterion.threshold else CriterionStatus.FAIL,
            f"{observed} items captured by distinct backends",
            observed=observed,
        )
    if check is CriterionCheck.RETRIEVAL_FULLY_CLASSIFIED:
        classified = {item for item, _ in report.classes}
        unclassified = [item for item in outcome.trace.item_ids if item not in classified]
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if not unclassified else CriterionStatus.FAIL,
            "" if not unclassified else f"unclassified retrieval: {unclassified}",
            observed=len(unclassified),
        )
    if check is CriterionCheck.PROTECTED_GOLD_TOKENS_RECOVERED:
        if gold is None:
            return CriterionResult(
                criterion.criterion_id,
                check,
                CriterionStatus.CANNOT_CHECK,
                "no protected gold is bound for this task",
            )
        missing = [item for item in gold.required_answer_tokens if item not in outcome.answer_text]
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if not missing else CriterionStatus.FAIL,
            # The tokens themselves are never echoed: a failure detail that
            # printed the answer key would leak the gold into the run record.
            f"{len(missing)} of {len(gold.required_answer_tokens)} gold tokens absent",
            observed=len(missing),
        )
    if check is CriterionCheck.PROTECTED_GOLD_ANCHOR_CITED:
        if gold is None:
            return CriterionResult(
                criterion.criterion_id,
                check,
                CriterionStatus.CANNOT_CHECK,
                "no protected gold is bound for this task",
            )
        cited = gold.anchor_source_id in outcome.cited_ids
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if cited else CriterionStatus.FAIL,
            "anchor cited" if cited else "protected anchor absent from cited evidence",
            observed=int(cited),
        )
    if check is CriterionCheck.NON_RECOVERY_DECLARES_RESIDUAL:
        if gold is None:
            return CriterionResult(
                criterion.criterion_id,
                check,
                CriterionStatus.CANNOT_CHECK,
                "recovery cannot be judged without bound ground truth",
            )
        recovered = all(item in outcome.answer_text for item in gold.required_answer_tokens)
        ok = recovered or bool(outcome.residual_ids)
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if ok else CriterionStatus.FAIL,
            "" if ok else "target not recovered and no residual declared",
            observed=len(outcome.residual_ids),
        )
    if check is CriterionCheck.RESOURCE_WITHIN_MATCHED_LIMIT:
        if outcome.orion_resource_units is None or outcome.baseline_resource_units is None:
            return CriterionResult(
                criterion.criterion_id,
                check,
                CriterionStatus.CANNOT_CHECK,
                "resource use for one or both arms was not observed",
            )
        ceiling = min(
            packet.limits.budget_units,
            outcome.baseline_resource_units * packet.limits.max_orion_to_baseline_ratio,
        )
        within = outcome.orion_resource_units <= ceiling
        return CriterionResult(
            criterion.criterion_id,
            check,
            CriterionStatus.PASS if within else CriterionStatus.FAIL,
            f"{outcome.orion_resource_units} units against a ceiling of {ceiling}",
        )
    # Unreachable while CriterionCheck and this dispatch stay in step; kept so a
    # new member surfaces as CANNOT_CHECK rather than as a silent pass.
    return CriterionResult(  # pragma: no cover - defensive
        criterion.criterion_id,
        check,
        CriterionStatus.CANNOT_CHECK,
        f"no frozen check is implemented for {check.value}",
    )


# ---------------------------------------------------------------------------
# 7. Typed provider refusal and immutable episodes
# ---------------------------------------------------------------------------


class LiveProviderStatus(str, Enum):
    """Why a live call did or did not happen. Mirrors `study.p1.provider`."""

    OK = "OK"
    NO_CREDENTIAL = "NO_CREDENTIAL"
    TRANSPORT_UNAVAILABLE = "TRANSPORT_UNAVAILABLE"
    PROVIDER_ERROR = "PROVIDER_ERROR"


NO_CREDENTIAL_SIGNATURE: tuple[str, ...] = (
    "provider:NO_CREDENTIAL",
    "trial:UNEXECUTED",
)


def credential_present(name: str) -> bool:
    """Whether a credential exists, without reading or returning its value."""

    return bool(os.environ.get(name))


def missing_credential_env_vars() -> tuple[str, ...]:
    """Names only. No value from the environment is ever returned or logged."""

    return tuple(name for name in CREDENTIAL_ENV_VARS if not credential_present(name))


def blocked_mechanic_ids(missing: Sequence[str] | None = None) -> tuple[str, ...]:
    """Fibres that cannot execute because their provider role lacks a credential."""

    absent = set(missing_credential_env_vars() if missing is None else missing)
    roles = {
        provider.role
        for provider in FROZEN_PROVIDERS
        if any(name in absent for name in provider.credential_env_vars)
    }
    return tuple(
        sorted(
            mechanic_id
            for mechanic_id, role in FIBRE_PROVIDER_ROLES.items()
            if role and role in roles
        )
    )


def _state_hash(packet: FrozenLiveResearchPacket, phase: str, task_id: str) -> str:
    return _sha256(
        {"packet": packet.fingerprint, "phase": phase, "task_id": task_id}
    )


def refusal_episodes(
    packet: FrozenLiveResearchPacket | None = None,
    *,
    missing: Sequence[str] | None = None,
    timestamp: str = PREFLIGHT_TIMESTAMP,
) -> tuple[TaskEpisode, ...]:
    """One immutable episode per (task, blocked fibre), recording CANNOT_CHECK.

    This is the refusal path made real rather than claimed. With no credential
    the trial produces evidence about itself -- which fibres could not run, on
    which tasks, under which frozen packet -- instead of producing nothing, and
    an unexecuted run that leaves no trace is indistinguishable from one that
    should never have existed.

    The episodes are shaped for `propose_failure_pattern`: same `mechanic_id`
    across tasks, distinct `run_id` per task, distinct `variation_signature` per
    task, and a shared core failure signature. That is what "suitable for later
    failure-pattern matching" has to mean if it is to be checkable.
    """

    resolved = packet or frozen_live_research_packet()
    absent = tuple(missing_credential_env_vars() if missing is None else missing)
    blocked = blocked_mechanic_ids(absent)
    episodes: list[TaskEpisode] = []
    for task in sorted(resolved.tasks, key=lambda item: item.task_id):
        run_id = f"{resolved.packet_id}:{task.task_id}:no-credential"
        for mechanic_id in blocked:
            episodes.append(
                TaskEpisode(
                    episode_id=f"episode:{run_id}:{mechanic_id}",
                    task_id=task.task_id,
                    run_id=run_id,
                    parent_run_id=None,
                    evaluation_epoch_id=resolved.evaluation_epoch_id,
                    split_id=task.split_id,
                    mechanic_id=mechanic_id,
                    problem_signature=(task.kind.value, *task.variation_signature),
                    variation_signature=task.variation_signature,
                    pre_state_hash=_state_hash(resolved, "pre", task.task_id),
                    action_ids=("action:credential_preflight",),
                    observation_ids=tuple(f"missing_env_var:{name}" for name in absent),
                    outcome=EpisodeOutcome.CANNOT_CHECK,
                    failure_signature=(
                        *NO_CREDENTIAL_SIGNATURE,
                        f"mechanic:{mechanic_id}",
                    ),
                    residual_ids=(f"residual:{mechanic_id}:unexecuted",),
                    evidence_ids=(),
                    evidence_bindings=(),
                    post_state_hash=_state_hash(resolved, "post", task.task_id),
                    timestamp=timestamp,
                    provenance_ids=(f"packet:{resolved.fingerprint}",),
                )
            )
    return tuple(episodes)


def failure_pattern_candidates(
    episodes: Sequence[TaskEpisode],
) -> tuple[FailurePatternCandidate, ...]:
    """Group immutable episodes by mechanic and propose candidate patterns.

    Proposal only. `FailurePatternCandidate` refuses to be constructed with any
    authority above CANDIDATE, so this path cannot raise authority even by
    mistake -- the invariant lives in the type, not in this function's manners.
    """

    by_mechanic: dict[str, list[TaskEpisode]] = {}
    for episode in sorted(episodes, key=lambda item: item.episode_id):
        by_mechanic.setdefault(episode.mechanic_id, []).append(episode)
    candidates: list[FailurePatternCandidate] = []
    for mechanic_id, group in sorted(by_mechanic.items()):
        candidate = propose_failure_pattern(
            tuple(group),
            pattern_id=f"pattern:{mechanic_id}",
            candidate_guard=(
                f"refuse to report a score for {mechanic_id} when its provider "
                "role has no credential; record CANNOT_CHECK instead"
            ),
            falsifier=(
                f"{mechanic_id} executes and is independently verified while its "
                "provider role remains unconfigured"
            ),
        )
        if candidate is not None:
            candidates.append(candidate)
    return tuple(candidates)


# ---------------------------------------------------------------------------
# 8. Authority boundary
# ---------------------------------------------------------------------------


class AuthorityRequestKind(str, Enum):
    PROMOTE_SELF_ORION = "PROMOTE_SELF_ORION"
    MERGE_REPAIR = "MERGE_REPAIR"
    RAISE_LESSON_AUTHORITY = "RAISE_LESSON_AUTHORITY"
    MODIFY_EVALUATOR = "MODIFY_EVALUATOR"


@dataclass(frozen=True)
class AuthorityDecision:
    """A refusal, structurally.

    `granted` exists so the refusal is explicit in the record, and construction
    raises if it is True. A boundary enforced by convention is a boundary one
    future caller flips; this one cannot be flipped without editing the type.
    """

    request_kind: AuthorityRequestKind
    requester: str
    granted: bool = False
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.granted:
            raise ValueError(
                "no model output, trial result or Self-ORION proposal may grant "
                "authority; promotion is reserved to the protected host"
            )
        if not self.requester.strip():
            raise ValueError("an authority request must name its requester")


def request_promotion(
    request_kind: AuthorityRequestKind,
    *,
    requester: str,
    model_output_digest: str = "",
) -> AuthorityDecision:
    """Always refuse. Model output is an input to governance, never a grant.

    `model_output_digest` is recorded so the refusal is attributable to a
    specific output, not so the output can influence the answer -- a stronger
    or more confident response produces the identical refusal.
    """

    reasons = [
        "no model output may directly increase authority",
        "Self-ORION may diagnose and propose repairs but may not merge or promote them",
        SUCCESS_BOUNDARY,
    ]
    if model_output_digest:
        reasons.append(f"refused request bound to model output {model_output_digest}")
    return AuthorityDecision(request_kind, requester, False, tuple(reasons))


@dataclass(frozen=True)
class RepairProposal:
    """A diagnosis plus a proposed repair, with no route to being applied here."""

    proposal_id: str
    mechanic_id: str
    diagnosis: str
    proposed_repair: str
    supporting_episode_ids: tuple[str, ...]
    authority: LessonAuthority = LessonAuthority.CANDIDATE
    merge_authorized: bool = False

    def __post_init__(self) -> None:
        if not self.proposal_id.strip() or not self.diagnosis.strip():
            raise ValueError("repair proposal identity and diagnosis are required")
        if not self.proposed_repair.strip() or not self.supporting_episode_ids:
            raise ValueError("repair proposal requires a repair and supporting episodes")
        if self.authority is not LessonAuthority.CANDIDATE or self.merge_authorized:
            raise ValueError(
                "a Self-ORION repair proposal cannot carry promoted authority or "
                "self-authorize its own merge"
            )


def propose_repair(
    episodes: Sequence[TaskEpisode],
    *,
    proposal_id: str,
    diagnosis: str,
    proposed_repair: str,
) -> RepairProposal | None:
    """Turn immutable episodes into a proposal. Returns None without evidence."""

    grouped = sorted(episodes, key=lambda item: item.episode_id)
    if not grouped:
        return None
    mechanic_ids = {item.mechanic_id for item in grouped}
    if len(mechanic_ids) != 1:
        return None
    return RepairProposal(
        proposal_id=proposal_id,
        mechanic_id=grouped[0].mechanic_id,
        diagnosis=diagnosis,
        proposed_repair=proposed_repair,
        supporting_episode_ids=tuple(item.episode_id for item in grouped),
    )


# ---------------------------------------------------------------------------
# 9. Bounded saturation as an outcome
# ---------------------------------------------------------------------------


class BoundedSaturationOutcome(str, Enum):
    OPEN = "OPEN"
    CANNOT_CHECK = "CANNOT_CHECK"
    A_PRIORI_FRAME_FLAT = "A_PRIORI_FRAME_FLAT"


@dataclass(frozen=True)
class BoundedSaturationState:
    """OPEN and CANNOT_CHECK are outcomes of the trial, not failures of it.

    A run that ends OPEN has measured that the search was still growing; a run
    that ends CANNOT_CHECK has measured that it could not tell. Both are
    findings. Treating either as an error is what pushes a system to manufacture
    a flat verdict, and `certifies_recall` stays False for all three outcomes
    for the same reason `orion.kernel.saturation` fixes it: N flat rounds under
    a frozen basis is a budget stop, not a recall claim.
    """

    outcome: BoundedSaturationOutcome
    reasons: tuple[str, ...] = ()

    @property
    def is_failure(self) -> bool:
        return False

    @property
    def certifies_recall(self) -> bool:
        return False


def pre_execution_saturation_state() -> BoundedSaturationState:
    """The honest saturation state before the trial has run a single round."""

    return BoundedSaturationState(
        BoundedSaturationOutcome.CANNOT_CHECK,
        (
            "no round has been observed because the live trial has not executed",
            "flatness is undefined without at least one growth vector under the basis",
        ),
    )


# ---------------------------------------------------------------------------
# 10. Preflight and the one command
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LiveTrialPreflight:
    packet_fingerprint: str
    missing_credential_env_vars: tuple[str, ...]
    blocked_mechanic_ids: tuple[str, ...]
    runnable_mechanic_ids: tuple[str, ...]
    corpus_revision: str
    open_question_count: int
    epoch_conflict: str
    saturation: BoundedSaturationState
    blockers: tuple[str, ...]

    @property
    def runnable(self) -> bool:
        return not self.blockers

    @property
    def boundary(self) -> str:
        return SUCCESS_BOUNDARY


def preflight(packet: FrozenLiveResearchPacket | None = None) -> LiveTrialPreflight:
    """Everything knowable about the trial without executing it.

    Two independent classes of blocker are reported separately on purpose. The
    credential blocker is not ours to clear; the unbound corpus revision is, and
    collapsing them into one "not ready" would hide a task the operator can
    actually do.
    """

    resolved = packet or frozen_live_research_packet()
    missing = missing_credential_env_vars()
    blocked = blocked_mechanic_ids(missing)
    env_epoch = os.environ.get("ORION_PHASE2_EVALUATION_EPOCH_ID", "")
    conflict = (
        ""
        if not env_epoch or env_epoch == resolved.evaluation_epoch_id
        else (
            f"environment evaluation epoch {env_epoch!r} differs from the frozen "
            f"epoch {resolved.evaluation_epoch_id!r}"
        )
    )
    blockers: list[str] = []
    if missing:
        blockers.append(
            "missing credential environment variables: " + ", ".join(missing)
        )
    if resolved.corpus_revision == UNBOUND:
        blockers.append(
            "deep-target corpus revision is UNBOUND; bind it with --corpus-revision"
        )
    if conflict:
        blockers.append(conflict)
    return LiveTrialPreflight(
        packet_fingerprint=resolved.fingerprint,
        missing_credential_env_vars=missing,
        blocked_mechanic_ids=blocked,
        runnable_mechanic_ids=tuple(
            sorted(set(FIBRE_PROVIDER_ROLES) - set(blocked))
        ),
        corpus_revision=resolved.corpus_revision,
        open_question_count=len(emit_open_questions()),
        epoch_conflict=conflict,
        saturation=pre_execution_saturation_state(),
        blockers=tuple(blockers),
    )


def _print_status(packet: FrozenLiveResearchPacket) -> None:
    report = preflight(packet)
    surface = question_surface_summary()
    print(f"packet          : {packet.packet_id}")
    print(f"fingerprint     : {report.packet_fingerprint}")
    print(f"outcome accessed: {packet.outcome_accessed}")
    print(f"corpus revision : {report.corpus_revision}")
    print("tasks           :")
    for task in sorted(packet.tasks, key=lambda item: item.task_id):
        print(f"  - {task.kind.value:<16} {task.task_id}")
    print(
        f"question surface: {surface['open_questions_issue_8']} open across the eight "
        f"named dimensions ({surface['open_questions_total']} open in total), "
        f"provider_required={surface['provider_required']}"
    )
    for dimension, count in sorted(surface["by_dimension"].items()):  # type: ignore[union-attr]
        print(f"  - {dimension:<20} {count}")
    print(f"saturation      : {report.saturation.outcome.value} (outcome, not failure)")
    print(f"blocked fibres  : {', '.join(report.blocked_mechanic_ids) or 'none'}")
    print(f"runnable fibres : {', '.join(report.runnable_mechanic_ids) or 'none'}")
    if report.blockers:
        print("blockers        :")
        for item in report.blockers:
            print(f"  - {item}")
    print(f"\nboundary        : {report.boundary}")


EXECUTION_MANIFEST_SCHEMA = "orion.self-orion.live-trial-execution-manifest.v1"


def execution_manifest(
    packet: FrozenLiveResearchPacket,
    *,
    report_path: Path | str,
    report_document_hash: str,
) -> dict[str, object]:
    """Bind a written trial report to the exact frozen packet that produced it.

    `FrozenLiveTrialPacket` -- the runtime object the runner consumes -- carries
    no corpus revision, so the revision preflight insisted on would otherwise
    never reach the run record. A deep-target result written against an
    unrecorded corpus is unverifiable after the fact, which is the failure the
    UNBOUND sentinel exists to prevent; the manifest is where the outer freeze
    meets the written outcome.
    """

    if not report_document_hash.strip():
        raise ValueError("an execution manifest requires the report's document hash")
    if packet.corpus_revision == UNBOUND:
        raise ValueError(
            "refusing to bind a run to an UNBOUND corpus revision; the deep-target "
            "result would not be reproducible"
        )
    body = {
        "schema": EXECUTION_MANIFEST_SCHEMA,
        "packet_id": packet.packet_id,
        "packet_fingerprint": packet.fingerprint,
        "trial_fingerprint": packet.trial.fingerprint,
        "evaluation_epoch_id": packet.evaluation_epoch_id,
        "corpus_revision": packet.corpus_revision,
        "provider_manifest_hash": packet.trial.provider_manifest_hash,
        "evaluator_artifact_hash": packet.evaluator.artifact_hash,
        "baseline_id": packet.baseline.baseline_id,
        "resource_limits": packet.limits.payload,
        "report_path": str(report_path),
        "report_document_hash": report_document_hash,
        "outcome_accessed_at_freeze": False,
        "success_boundary": SUCCESS_BOUNDARY,
    }
    return {**body, "manifest_hash": _sha256(body)}


def _run_live(packet: FrozenLiveResearchPacket) -> int:
    """Execute the frozen trial, or refuse in a typed, actionable way.

    Refusal is checked before anything is constructed. Starting a trial whose
    every live cell would record CANNOT_CHECK spends the mechanical fibres'
    run too, and a half-live archive is harder to reason about than none --
    the same reason `orion.study.p1.run_trial` refuses up front.
    """

    report = preflight(packet)
    if report.blockers:
        print("refusing to start the live trial:", file=sys.stderr)
        for item in report.blockers:
            print(f"  - {item}", file=sys.stderr)
        print(
            f"\nEvery blocked fibre ({', '.join(report.blocked_mechanic_ids) or 'none'}) "
            "would record CANNOT_CHECK rather than a score.\n"
            f"Build the stack with {LIVE_STACK_CONSTRUCTOR} once these are exported:\n"
            + "".join(f"  {name}\n" for name in CREDENTIAL_ENV_VARS)
            + f"then this command runs {LIVE_RUNNER} against packet "
            f"{report.packet_fingerprint}.",
            file=sys.stderr,
        )
        episodes = refusal_episodes(packet)
        print(
            f"recorded {len(episodes)} immutable CANNOT_CHECK episode(s); "
            f"{len(failure_pattern_candidates(episodes))} candidate failure "
            "pattern(s) available for later matching.",
            file=sys.stderr,
        )
        return EXIT_CANNOT_CHECK

    # Imported here, not at module scope. Everything above this line -- the
    # packet, the question surface, the trace model, the episodes, the frozen
    # evaluator -- resolves without the module that builds a live stack ever
    # being imported, which is what makes "runs with no provider" checkable
    # rather than asserted.
    from orion.providers.live_phase2 import build_phase2_live_provider_stack_from_env
    from orion.self_orion.baseline import SimpleLLMRetrievalBaseline
    from orion.self_orion.trial_io import write_shadow_live_trial_report

    model = os.environ.get("ORION_P5_REASONER_MODEL", "")
    if not model:
        print(
            "refusing to start: ORION_P5_REASONER_MODEL is not set, so the frozen "
            "provider identity cannot be bound to a specific model.",
            file=sys.stderr,
        )
        return EXIT_CANNOT_CHECK
    stack = build_phase2_live_provider_stack_from_env(reasoner_model=model)
    baseline = SimpleLLMRetrievalBaseline(llm=stack.llm, retrieval=stack.retrieval)
    runner = ShadowLiveTrialRunner.from_providers(
        llm=stack.llm,
        retrieval=stack.retrieval,
        verification=stack.verification,
        baseline=baseline,
        evaluator_artifact_hash=stack.evaluator_artifact_hash,
    )
    result = runner.run(packet.trial)
    out = PROTOCOL_PATH.parent.parent / "results"
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / "shadow_live_trial_report.json"
    write_shadow_live_trial_report(result, report_path)
    written = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = execution_manifest(
        packet,
        report_path=report_path,
        report_document_hash=str(written.get("document_hash", "")),
    )
    manifest_path = out / "shadow_live_execution_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"trial complete. report -> {report_path}")
    print(f"bound to packet {packet.fingerprint} -> {manifest_path}")
    print(f"boundary: {SUCCESS_BOUNDARY}")
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Frozen Shadow Self-ORION live research packet (issue #8). Prints the "
            "frozen packet and its mechanical question surface with no provider; "
            "--live executes the trial or refuses in a typed way."
        )
    )
    parser.add_argument(
        "--emit-protocol",
        nargs="?",
        const=str(PROTOCOL_PATH),
        default=None,
        help="write the frozen packet JSON (default: the checked-in protocol path)",
    )
    parser.add_argument(
        "--questions",
        action="store_true",
        help="print every open question across the eight named dimensions",
    )
    parser.add_argument(
        "--corpus-revision",
        default=UNBOUND,
        help="bind the deep-target corpus revision at execution time",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="execute the frozen trial; refuses with exit 3 while any blocker stands",
    )
    args = parser.parse_args(argv)

    packet = frozen_live_research_packet(corpus_revision=args.corpus_revision)
    if args.emit_protocol is not None:
        written = write_packet_document(args.emit_protocol, packet=packet)
        print(f"wrote {written}")
        print(f"fingerprint: {packet.fingerprint}")
        return EXIT_OK
    if args.questions:
        for question in emit_open_questions():
            print(f"{question.question_id}\n    {question.question}")
        return EXIT_OK
    _print_status(packet)
    if args.live:
        return _run_live(packet)
    return EXIT_OK


__all__ = [
    "BASELINE_ID",
    "CREDENTIAL_ENV_VARS",
    "EVALUATION_EPOCH_ID",
    "EXECUTION_MANIFEST_SCHEMA",
    "EXIT_CANNOT_CHECK",
    "EXIT_ERROR",
    "EXIT_OK",
    "FIBRE_PROVIDER_ROLES",
    "FROZEN_BASELINE",
    "FROZEN_EVALUATOR",
    "FROZEN_LIMITS",
    "FROZEN_PROVIDERS",
    "ISSUE_8_DIMENSIONS",
    "NO_CREDENTIAL_SIGNATURE",
    "PACKET_ID",
    "PACKET_SCHEMA",
    "PREFLIGHT_TIMESTAMP",
    "PROTOCOL_PATH",
    "PROTOCOL_RELATIVE_PATH",
    "SUCCESS_BOUNDARY",
    "UNBOUND",
    "AuthorityDecision",
    "AuthorityRequestKind",
    "BoundedSaturationOutcome",
    "BoundedSaturationState",
    "CheckableCriterion",
    "CriterionCheck",
    "CriterionResult",
    "CriterionStatus",
    "EvidenceUseClass",
    "EvidenceUseReport",
    "FrozenEvaluatorSpec",
    "FrozenLiveResearchPacket",
    "FrozenProviderIdentity",
    "FrozenResourceLimits",
    "FrozenTaskBinding",
    "LiveProviderStatus",
    "LiveTrialPreflight",
    "MatchedBaselineSpec",
    "ProtectedTargetGold",
    "QueryTrace",
    "QuestionSurfaceCoverage",
    "RawTrialTrace",
    "RepairProposal",
    "TaskOutcomeInput",
    "TraceItem",
    "blocked_mechanic_ids",
    "classify_evidence_use",
    "credential_present",
    "emit_open_questions",
    "evaluate_task",
    "execution_manifest",
    "failure_pattern_candidates",
    "frozen_live_research_packet",
    "live_trial_mechanic_cells",
    "load_packet_document",
    "main",
    "missing_credential_env_vars",
    "packet_document",
    "pre_execution_saturation_state",
    "preflight",
    "propose_repair",
    "question_surface_coverage",
    "question_surface_summary",
    "refusal_episodes",
    "request_promotion",
    "write_packet_document",
]


if __name__ == "__main__":
    raise SystemExit(main())
