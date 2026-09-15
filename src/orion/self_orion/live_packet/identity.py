"""Section 1 -- frozen provider identities, resource limits and evaluator.

Who answers, under what budget, and against which checkable criteria -- all
declared before any answer exists. No object in this module may carry a
credential value; `credential_env_vars` holds variable *names* only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .constants import BASELINE_ID, _sha256


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
