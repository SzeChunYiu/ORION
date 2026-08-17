"""Model-based multi-judge adjudication panel for ORION-P1 (issue #98, Step 3).

THIS IS NOT HUMAN ADJUDICATION AND MUST NEVER BE REPORTED AS SUCH.

Issue #98 Step 3 requires "at least two independent adjudicators for whether/where a
reframe is warranted on non-mechanical cases" with a "written adjudication rubric +
agreement reporting". No human panel is available. This module satisfies every
*structural* requirement of that clause with a panel of language-model judges:

* a frozen written rubric (`ADJUDICATION_RUBRIC_V1.md`) bound by content hash;
* blinding — a judge sees only `PublicView`, never `ProtectedGold`, never a peer verdict;
* independence verified before any verdict is accepted, not asserted;
* Cohen's / Fleiss' kappa reported per question alongside raw agreement;
* a disagreement policy frozen inside the hashed rubric body and applied mechanically.

The provenance tier is `AdjudicationStatus.MODEL_ADJUDICATED`, distinct from `ADJUDICATED`
(human) and from `MECHANICAL_GOLD` (constructed). `AdjudicationRecord` refuses any other
status, so a model panel cannot claim a tier it did not earn.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Hashable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Protocol, runtime_checkable

from .cases import AdjudicationStatus, PublicView

ADJUDICATOR_KIND = "model_panel"
"""Recorded on every artifact. The panel is model-based; the label says so."""

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class AdjudicationError(RuntimeError):
    """Base class. Every failure here is fail-closed: no label is emitted."""


class RubricIntegrityError(AdjudicationError):
    """The rubric document does not hash to the digest it records."""


class RubricMismatchError(AdjudicationError):
    """A judge answered from a different rubric revision than the panel declared."""


class IndependenceError(AdjudicationError):
    """Judge independence could not be witnessed. The whole run is void."""


class PolicyError(AdjudicationError):
    """The runtime policy differs from the one frozen in the rubric body."""


# --------------------------------------------------------------------------- rubric

RUBRIC_BODY_BEGIN = "<!-- RUBRIC-BODY-BEGIN -->"
RUBRIC_BODY_END = "<!-- RUBRIC-BODY-END -->"
_RECORDED_HASH = re.compile(r"<!--\s*RUBRIC-CONTENT-SHA256:\s*([0-9a-f]{64})\s*-->")
_POLICY_BLOCK = re.compile(
    r"<!--\s*POLICY-BEGIN\s*-->\s*```json\s*(\{.*?\})\s*```\s*<!--\s*POLICY-END\s*-->",
    re.DOTALL,
)


def extract_rubric_body(text: str) -> str:
    """The bytes the content hash covers. Fails closed on missing/duplicated markers."""

    if text.count(RUBRIC_BODY_BEGIN) != 1 or text.count(RUBRIC_BODY_END) != 1:
        raise RubricIntegrityError(
            "rubric body markers must appear exactly once each; "
            f"found {text.count(RUBRIC_BODY_BEGIN)} begin / {text.count(RUBRIC_BODY_END)} end"
        )
    start = text.index(RUBRIC_BODY_BEGIN) + len(RUBRIC_BODY_BEGIN)
    end = text.index(RUBRIC_BODY_END)
    if end <= start:
        raise RubricIntegrityError("rubric end marker precedes its begin marker")
    return text[start:end]


def rubric_content_hash(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class FrozenRubric:
    """A rubric revision that has been verified against its own recorded digest."""

    rubric_id: str
    content_hash: str
    body: str
    source_path: str = ""


def load_rubric(path: Path, *, rubric_id: str = "P1.adjudication-rubric.v1") -> FrozenRubric:
    """Read, verify and freeze the rubric. A tampered document is refused, not warned about."""

    text = path.read_text(encoding="utf-8")
    body = extract_rubric_body(text)
    computed = rubric_content_hash(body)
    recorded = _RECORDED_HASH.findall(text)
    if len(recorded) != 1:
        raise RubricIntegrityError(
            f"rubric must record exactly one RUBRIC-CONTENT-SHA256 marker; found {len(recorded)}"
        )
    if recorded[0] != computed:
        raise RubricIntegrityError(
            f"rubric content hash mismatch: recorded {recorded[0]}, computed {computed}"
        )
    return FrozenRubric(
        rubric_id=rubric_id, content_hash=computed, body=body, source_path=str(path)
    )


# ------------------------------------------------------------------- rubric taxonomy


class ResponsibilityClass(str, Enum):
    """The six coordinate classes of rubric section 3. Four warrant a reframe; two do not."""

    FORMULATION = "formulation"
    REPRESENTATION = "representation"
    DECOMPOSITION = "decomposition"
    MEASUREMENT = "measurement"
    EVIDENCE = "evidence"
    EXECUTION = "execution"


REFRAME_WARRANTING_CLASSES: frozenset[ResponsibilityClass] = frozenset(
    {
        ResponsibilityClass.FORMULATION,
        ResponsibilityClass.REPRESENTATION,
        ResponsibilityClass.DECOMPOSITION,
        ResponsibilityClass.MEASUREMENT,
    }
)

COORDINATE_VOCABULARY: Mapping[ResponsibilityClass, frozenset[str]] = {
    ResponsibilityClass.FORMULATION: frozenset(
        {"objective", "parent_domain", "constraint_set", "scope_boundary"}
    ),
    ResponsibilityClass.REPRESENTATION: frozenset(
        {"state_encoding", "coordinate_system", "variable_set", "units_basis"}
    ),
    ResponsibilityClass.DECOMPOSITION: frozenset(
        {"subproblem_split", "interface_contract", "ordering", "coupling"}
    ),
    ResponsibilityClass.MEASUREMENT: frozenset(
        {"metric_definition", "estimator", "population", "normalization"}
    ),
    ResponsibilityClass.EVIDENCE: frozenset(),
    ResponsibilityClass.EXECUTION: frozenset(),
}
"""Published vocabulary a live backend injects into the judge prompt. Recorded, not enforced:
an out-of-vocabulary coordinate is surfaced as a panel diagnostic rather than silently dropped."""


class Question(str, Enum):
    """Agreement is reported per question. A single pooled number would hide the structure."""

    REFRAME_WARRANTED = "reframe_warranted"
    RESPONSIBILITY_CLASS = "responsibility_class"
    REOPEN_SET = "reopen_set"


PRIMARY_QUESTION = Question.REFRAME_WARRANTED


# --------------------------------------------------------------------------- verdicts


@dataclass(frozen=True)
class JudgeVerdict:
    """One judge's blinded answer on one case. `None` on a question means ABSTAIN.

    Coherence mirrors the invariants `HiddenShiftCase` enforces on gold: the reframe answer
    is a function of the responsibility class, a warranted reframe must name coordinates,
    and a non-warranted verdict may neither name coordinates nor reopen anything.
    """

    case_id: str
    judge_id: str
    lineage_id: str
    context_id: str
    rubric_hash: str
    reframe_warranted: bool | None
    responsibility_class: ResponsibilityClass | None = None
    coordinates: tuple[str, ...] = ()
    reopen: tuple[str, ...] | None = None
    confidence: float = 0.0
    rationale: str = ""

    def __post_init__(self) -> None:
        for name in ("case_id", "judge_id", "lineage_id", "context_id"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"JudgeVerdict.{name} is required")
        if not _HEX64.match(self.rubric_hash):
            raise ValueError("JudgeVerdict.rubric_hash must be a sha256 hex digest")
        if not self.rationale.strip():
            raise ValueError(
                f"{self.case_id}/{self.judge_id}: a verdict without a rationale is not auditable"
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"{self.case_id}/{self.judge_id}: confidence must lie in [0, 1]")

        object.__setattr__(self, "coordinates", tuple(dict.fromkeys(self.coordinates)))
        if self.reopen is not None:
            object.__setattr__(self, "reopen", tuple(sorted(set(self.reopen))))

        if self.reframe_warranted is None:
            if self.responsibility_class is not None or self.coordinates or self.reopen:
                raise ValueError(
                    f"{self.case_id}/{self.judge_id}: an abstention may not carry an answer"
                )
            return
        if self.responsibility_class is None:
            raise ValueError(
                f"{self.case_id}/{self.judge_id}: a non-abstaining verdict must name a class"
            )
        warranting = self.responsibility_class in REFRAME_WARRANTING_CLASSES
        if warranting != self.reframe_warranted:
            raise ValueError(
                f"{self.case_id}/{self.judge_id}: class "
                f"{self.responsibility_class.value} is incoherent with "
                f"reframe_warranted={self.reframe_warranted}"
            )
        if self.reframe_warranted and not self.coordinates:
            raise ValueError(
                f"{self.case_id}/{self.judge_id}: a warranted reframe must name coordinates"
            )
        if not self.reframe_warranted:
            if self.coordinates:
                raise ValueError(
                    f"{self.case_id}/{self.judge_id}: a non-reframe may not name coordinates"
                )
            if self.reopen:
                raise ValueError(
                    f"{self.case_id}/{self.judge_id}: a non-reframe may not reopen closures"
                )
            object.__setattr__(self, "reopen", ())

    def answer(self, question: Question) -> Hashable | None:
        """The judge's label for one question, or `None` for an abstention on it."""

        if question is Question.REFRAME_WARRANTED:
            return self.reframe_warranted
        if question is Question.RESPONSIBILITY_CLASS:
            return None if self.responsibility_class is None else self.responsibility_class.value
        return self.reopen

    def off_vocabulary_coordinates(self) -> tuple[str, ...]:
        if self.responsibility_class is None:
            return ()
        allowed = COORDINATE_VOCABULARY[self.responsibility_class]
        return tuple(name for name in self.coordinates if name not in allowed)


@runtime_checkable
class JudgeBackend(Protocol):
    """One adjudicator. A live model adapter and a deterministic test double are the same shape.

    A live backend composes its prompt from `rubric_body` and calls out through
    `orion.providers.llm`; it must stamp the issued `context_id` and `rubric_hash` onto the
    verdict it returns, because the panel verifies both. No backend in this module makes a
    network call, and no test may use one that does.
    """

    judge_id: str
    lineage_id: str

    def new_context(self) -> str:
        """Open a fresh, isolated context and return its globally unique id."""
        ...

    def judge(
        self,
        view: PublicView,
        *,
        rubric_body: str,
        rubric_hash: str,
        context_id: str,
    ) -> JudgeVerdict: ...


# ----------------------------------------------------------------------- independence


@dataclass(frozen=True)
class IndependenceCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class IndependenceWitness:
    """Verified independence. `ok` is False whenever a check fails *or cannot be evaluated*."""

    ok: bool
    checks: tuple[IndependenceCheck, ...]

    @property
    def failures(self) -> tuple[str, ...]:
        return tuple(f"{c.name}: {c.detail}" for c in self.checks if not c.passed)


def _declared_id(judge: object, attribute: str) -> str | None:
    value = getattr(judge, attribute, None)
    if not isinstance(value, str) or not value.strip():
        return None
    return value


def panel_independence_witness(
    judges: Sequence[object],
    *,
    context_ids: Sequence[str] | None = None,
    min_judges: int = 2,
) -> IndependenceWitness:
    """Fail-closed witness over a judge panel.

    Verified here: panel size, distinct judge *objects* (a reused instance shares state),
    declared and distinct `judge_id`, declared and distinct `lineage_id`, callable backend
    surface, and — when `context_ids` are supplied post-hoc — global context-id uniqueness.
    A missing or empty id fails the witness; "could not determine" is never "independent".

    Structural rather than checked: the panel never passes a verdict to a backend, so no
    judge can observe another's answer or its own answer on a previous case.
    """

    checks: list[IndependenceCheck] = []

    checks.append(
        IndependenceCheck(
            "panel_size",
            len(judges) >= min_judges,
            f"{len(judges)} judges, policy minimum {min_judges}",
        )
    )

    identities = [id(judge) for judge in judges]
    checks.append(
        IndependenceCheck(
            "distinct_judge_objects",
            len(set(identities)) == len(identities),
            "a judge instance used twice is one context, not two",
        )
    )

    for attribute, check_name in (("judge_id", "judge_id"), ("lineage_id", "lineage_id")):
        declared = [_declared_id(judge, attribute) for judge in judges]
        if any(value is None for value in declared):
            missing = [index for index, value in enumerate(declared) if value is None]
            checks.append(
                IndependenceCheck(
                    f"{check_name}_declared",
                    False,
                    f"judges at positions {missing} declare no non-empty {attribute}",
                )
            )
            checks.append(
                IndependenceCheck(
                    f"{check_name}_distinct", False, f"undeterminable: {attribute} missing"
                )
            )
            continue
        checks.append(IndependenceCheck(f"{check_name}_declared", True, "all judges declare one"))
        duplicates = sorted({v for v in declared if declared.count(v) > 1})
        checks.append(
            IndependenceCheck(
                f"{check_name}_distinct",
                not duplicates,
                f"shared {attribute}: {duplicates}" if duplicates else "all distinct",
            )
        )

    callable_surface = all(
        callable(getattr(judge, "new_context", None)) and callable(getattr(judge, "judge", None))
        for judge in judges
    )
    checks.append(
        IndependenceCheck(
            "backend_surface", callable_surface, "every judge exposes new_context() and judge()"
        )
    )

    if context_ids is not None:
        issued = list(context_ids)
        blank = [index for index, value in enumerate(issued) if not str(value).strip()]
        duplicates = sorted({v for v in issued if issued.count(v) > 1})
        checks.append(
            IndependenceCheck(
                "context_ids_declared",
                not blank,
                f"blank context ids at {blank}" if blank else "every invocation issued an id",
            )
        )
        checks.append(
            IndependenceCheck(
                "context_ids_globally_unique",
                not duplicates,
                f"shared context: {duplicates}" if duplicates else f"{len(issued)} distinct",
            )
        )

    return IndependenceWitness(ok=all(c.passed for c in checks), checks=tuple(checks))


# ------------------------------------------------------------------------- statistics


def _counts(labels: Sequence[Hashable]) -> dict[Hashable, int]:
    tally: dict[Hashable, int] = {}
    for label in labels:
        tally[label] = tally.get(label, 0) + 1
    return tally


def cohens_kappa(rater_a: Sequence[Hashable], rater_b: Sequence[Hashable]) -> float | None:
    """Cohen's kappa for exactly two raters. `None` when undefined (p_e == 1 or n < 2).

    kappa = (p_o - p_e) / (1 - p_e), p_e = sum_k P(a=k) * P(b=k).
    Computed over exact rationals so the degeneracy test `p_e == 1` is exact rather than
    an epsilon comparison.
    """

    if len(rater_a) != len(rater_b):
        raise ValueError("cohens_kappa needs one rating per item from each rater")
    n = len(rater_a)
    if n < 2:
        return None
    agree = sum(1 for a, b in zip(rater_a, rater_b, strict=True) if a == b)
    p_o = Fraction(agree, n)
    marg_a, marg_b = _counts(rater_a), _counts(rater_b)
    p_e = sum(
        (Fraction(marg_a[label], n) * Fraction(marg_b.get(label, 0), n) for label in marg_a),
        Fraction(0),
    )
    if p_e == 1:
        return None
    return float((p_o - p_e) / (1 - p_e))


def fleiss_kappa(item_ratings: Sequence[Sequence[Hashable]]) -> float | None:
    """Fleiss' kappa for three or more interchangeable raters. `None` when undefined.

    P_i = (sum_j n_ij^2 - m) / (m(m-1))   — the proportion of agreeing rater pairs on item i
    kappa = (mean P_i - sum_j p_j^2) / (1 - sum_j p_j^2)
    """

    n = len(item_ratings)
    if n < 2:
        return None
    sizes = {len(row) for row in item_ratings}
    if len(sizes) != 1:
        raise ValueError("fleiss_kappa needs the same number of raters on every item")
    m = sizes.pop()
    if m < 2:
        raise ValueError("fleiss_kappa needs at least two raters")

    p_bar = Fraction(0)
    totals: dict[Hashable, int] = {}
    for row in item_ratings:
        tally = _counts(row)
        for label, count in tally.items():
            totals[label] = totals.get(label, 0) + count
        p_bar += Fraction(sum(c * c for c in tally.values()) - m, m * (m - 1))
    p_bar /= n
    p_e = sum((Fraction(total, n * m) ** 2 for total in totals.values()), Fraction(0))
    if p_e == 1:
        return None
    return float((p_bar - p_e) / (1 - p_e))


def mean_pairwise_agreement(item_ratings: Sequence[Sequence[Hashable]]) -> float | None:
    """Raw agreement: the mean over items of the fraction of agreeing rater pairs.

    For two raters this is exact agreement. Reported *alongside* kappa, never instead of it.
    """

    if not item_ratings:
        return None
    m = len(item_ratings[0])
    if m < 2:
        return None
    total = Fraction(0)
    for row in item_ratings:
        tally = _counts(row)
        total += Fraction(sum(c * c for c in tally.values()) - m, m * (m - 1))
    return float(total / len(item_ratings))


@dataclass(frozen=True)
class AgreementReport:
    """Agreement on one question. Undefined is reported as undefined, never as zero."""

    question: Question
    method: str
    n_judges: int
    n_items_complete: int
    n_items_abstained: int
    raw_agreement: float | None
    unanimity_rate: float | None
    kappa: float | None
    kappa_undefined_reason: str | None
    category_counts: tuple[tuple[str, int], ...]

    @property
    def degenerate(self) -> bool:
        """True when kappa is undefined because expected agreement is 1 (single category)."""

        return self.kappa_undefined_reason == "degenerate_marginals"

    def to_dict(self) -> dict[str, object]:
        return {
            "question": self.question.value,
            "method": self.method,
            "n_judges": self.n_judges,
            "n_items_complete": self.n_items_complete,
            "n_items_abstained": self.n_items_abstained,
            "raw_agreement": self.raw_agreement,
            "unanimity_rate": self.unanimity_rate,
            "kappa": self.kappa,
            "kappa_undefined_reason": self.kappa_undefined_reason,
            "degenerate": self.degenerate,
            "category_counts": [list(entry) for entry in self.category_counts],
        }


def _category_key(label: Hashable) -> str:
    if isinstance(label, tuple):
        return "reopen:" + json.dumps(sorted(str(item) for item in label))
    return f"{type(label).__name__}:{label}"


def build_agreement_report(
    question: Question,
    verdicts_by_case: Sequence[Sequence[JudgeVerdict]],
) -> AgreementReport:
    """Agreement on complete cases only, with the abstention drop count reported next to it."""

    n_judges = len(verdicts_by_case[0]) if verdicts_by_case else 0
    complete: list[list[Hashable]] = []
    dropped = 0
    for verdicts in verdicts_by_case:
        answers = [verdict.answer(question) for verdict in verdicts]
        if any(answer is None for answer in answers):
            dropped += 1
            continue
        complete.append([_category_key(answer) for answer in answers])

    tally: dict[str, int] = {}
    for row in complete:
        for key in row:
            tally[str(key)] = tally.get(str(key), 0) + 1
    category_counts = tuple(sorted(tally.items()))

    if n_judges < 2:
        return AgreementReport(
            question=question,
            method="undefined",
            n_judges=n_judges,
            n_items_complete=len(complete),
            n_items_abstained=dropped,
            raw_agreement=None,
            unanimity_rate=None,
            kappa=None,
            kappa_undefined_reason="insufficient_judges",
            category_counts=category_counts,
        )

    method = "cohen" if n_judges == 2 else "fleiss"
    raw = mean_pairwise_agreement(complete) if complete else None
    unanimity = (
        sum(1 for row in complete if len(set(row)) == 1) / len(complete) if complete else None
    )

    if len(complete) < 2:
        kappa, reason = None, "insufficient_items"
    else:
        kappa = (
            cohens_kappa([row[0] for row in complete], [row[1] for row in complete])
            if n_judges == 2
            else fleiss_kappa(complete)
        )
        reason = None if kappa is not None else "degenerate_marginals"

    return AgreementReport(
        question=question,
        method=method,
        n_judges=n_judges,
        n_items_complete=len(complete),
        n_items_abstained=dropped,
        raw_agreement=raw,
        unanimity_rate=unanimity,
        kappa=kappa,
        kappa_undefined_reason=reason,
        category_counts=category_counts,
    )


# ----------------------------------------------------------------------------- policy


@dataclass(frozen=True)
class DisagreementPolicy:
    """Frozen before any verdict was seen, and covered by the rubric's content hash.

    `policy_hash` is content-addressed, so a threshold that moved after the fact is visible
    as a changed digest — the freeze is checkable, not a claim in prose.
    """

    policy_id: str
    min_judges: int
    quorum: int
    kappa_threshold: float
    require_defined_kappa_for_majority: bool
    require_strict_majority: bool

    def __post_init__(self) -> None:
        if self.min_judges < 2:
            raise ValueError("a panel of fewer than two judges cannot report agreement")
        if self.quorum < 2:
            raise ValueError("quorum must require at least two non-abstaining verdicts")
        if not 0.0 <= self.kappa_threshold <= 1.0:
            raise ValueError("kappa_threshold must lie in [0, 1]")

    def to_dict(self) -> dict[str, object]:
        return {
            "policy_id": self.policy_id,
            "min_judges": self.min_judges,
            "quorum": self.quorum,
            "kappa_threshold": self.kappa_threshold,
            "require_defined_kappa_for_majority": self.require_defined_kappa_for_majority,
            "require_strict_majority": self.require_strict_majority,
        }

    @property
    def policy_hash(self) -> str:
        return hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


V1_POLICY = DisagreementPolicy(
    policy_id="P1.model-panel-adjudication.v1",
    min_judges=2,
    quorum=2,
    kappa_threshold=0.6,
    require_defined_kappa_for_majority=True,
    require_strict_majority=True,
)
"""Landis & Koch's lower bound for "substantial" agreement. Must equal the rubric's block."""


def policy_from_rubric(body: str) -> DisagreementPolicy:
    """Parse the policy frozen inside the hashed rubric body.

    Binding the two freeze artifacts means one digest witnesses both the decision procedure
    and the thresholds, so "the policy predates the verdicts" is provable from the document.
    """

    match = _POLICY_BLOCK.search(body)
    if match is None:
        raise PolicyError("rubric body carries no POLICY-BEGIN/POLICY-END json block")
    payload = json.loads(match.group(1))
    try:
        return DisagreementPolicy(
            policy_id=str(payload["policy_id"]),
            min_judges=int(payload["min_judges"]),
            quorum=int(payload["quorum"]),
            kappa_threshold=float(payload["kappa_threshold"]),
            require_defined_kappa_for_majority=bool(payload["require_defined_kappa_for_majority"]),
            require_strict_majority=bool(payload["require_strict_majority"]),
        )
    except KeyError as error:  # pragma: no cover - defensive
        raise PolicyError(f"frozen policy block is missing {error}") from error


# ------------------------------------------------------------------------- resolution


class PanelOutcome(str, Enum):
    UNANIMOUS = "UNANIMOUS"
    MAJORITY_WITH_DISSENT = "MAJORITY_WITH_DISSENT"
    CANNOT_CHECK = "CANNOT_CHECK"


class CannotCheckReason(str, Enum):
    NO_QUORUM = "NO_QUORUM"
    ABSTENTION_BREAKS_QUORUM = "ABSTENTION_BREAKS_QUORUM"
    NO_MAJORITY = "NO_MAJORITY"
    AGREEMENT_UNDEFINED = "AGREEMENT_UNDEFINED"
    AGREEMENT_BELOW_THRESHOLD = "AGREEMENT_BELOW_THRESHOLD"


@dataclass(frozen=True)
class QuestionResolution:
    """One question resolved on one case. `included` gates the metric, not the case status."""

    question: Question
    outcome: PanelOutcome
    label: bool | str | tuple[str, ...] | None
    dissenting_judges: tuple[str, ...]
    abstaining_judges: tuple[str, ...]
    cannot_check_reason: CannotCheckReason | None
    kappa_at_decision: float | None

    @property
    def included(self) -> bool:
        return self.outcome is not PanelOutcome.CANNOT_CHECK

    def to_dict(self) -> dict[str, object]:
        label = list(self.label) if isinstance(self.label, tuple) else self.label
        return {
            "question": self.question.value,
            "outcome": self.outcome.value,
            "label": label,
            "dissenting_judges": list(self.dissenting_judges),
            "abstaining_judges": list(self.abstaining_judges),
            "cannot_check_reason": (
                None if self.cannot_check_reason is None else self.cannot_check_reason.value
            ),
            "kappa_at_decision": self.kappa_at_decision,
            "included": self.included,
        }


@dataclass(frozen=True)
class AdjudicationRecord:
    """One case, archived in full: every verdict, the agreement in force, the resolved label.

    A `CANNOT_CHECK` record is excluded from adjudicated analysis and *retained* here, per
    `PROTOCOL_V1.json` -> `exclusion_policy`. The status whitelist is the mechanical guarantee
    that a model panel cannot claim the human (`ADJUDICATED`), double-annotated or mechanical
    tiers: only `MODEL_ADJUDICATED` or nothing.
    """

    case_id: str
    verdicts: tuple[JudgeVerdict, ...]
    resolutions: tuple[QuestionResolution, ...]
    agreement: tuple[AgreementReport, ...]
    status: AdjudicationStatus | None
    adjudicator_kind: str = ADJUDICATOR_KIND

    _ALLOWED_STATUSES = (None, AdjudicationStatus.MODEL_ADJUDICATED)

    def __post_init__(self) -> None:
        if self.status not in self._ALLOWED_STATUSES:
            raise ValueError(
                f"{self.case_id}: a model panel may only emit MODEL_ADJUDICATED or no status; "
                f"{self.status} requires a real human or mechanical record"
            )
        if self.adjudicator_kind != ADJUDICATOR_KIND:
            raise ValueError(f"{self.case_id}: adjudicator_kind is fixed at {ADJUDICATOR_KIND!r}")
        primary = self.resolution(PRIMARY_QUESTION)
        labelled = primary is not None and primary.included
        if labelled != (self.status is AdjudicationStatus.MODEL_ADJUDICATED):
            raise ValueError(f"{self.case_id}: status disagrees with the primary resolution")

    def resolution(self, question: Question) -> QuestionResolution | None:
        for resolution in self.resolutions:
            if resolution.question is question:
                return resolution
        return None

    @property
    def outcome(self) -> PanelOutcome:
        primary = self.resolution(PRIMARY_QUESTION)
        return PanelOutcome.CANNOT_CHECK if primary is None else primary.outcome

    @property
    def included_in_adjudicated_analysis(self) -> bool:
        return self.status is AdjudicationStatus.MODEL_ADJUDICATED

    @property
    def resolved_reframe_warranted(self) -> bool | None:
        resolution = self.resolution(Question.REFRAME_WARRANTED)
        label = None if resolution is None else resolution.label
        return label if isinstance(label, bool) else None

    @property
    def resolved_responsibility_class(self) -> str | None:
        resolution = self.resolution(Question.RESPONSIBILITY_CLASS)
        label = None if resolution is None else resolution.label
        return label if isinstance(label, str) else None

    @property
    def resolved_reopen(self) -> tuple[str, ...] | None:
        resolution = self.resolution(Question.REOPEN_SET)
        label = None if resolution is None else resolution.label
        return label if isinstance(label, tuple) else None

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "adjudicator_kind": self.adjudicator_kind,
            "status": None if self.status is None else self.status.value,
            "outcome": self.outcome.value,
            "included_in_adjudicated_analysis": self.included_in_adjudicated_analysis,
            "resolutions": [resolution.to_dict() for resolution in self.resolutions],
            "verdicts": [
                {
                    "judge_id": verdict.judge_id,
                    "lineage_id": verdict.lineage_id,
                    "context_id": verdict.context_id,
                    "reframe_warranted": verdict.reframe_warranted,
                    "responsibility_class": (
                        None
                        if verdict.responsibility_class is None
                        else verdict.responsibility_class.value
                    ),
                    "coordinates": list(verdict.coordinates),
                    "reopen": None if verdict.reopen is None else list(verdict.reopen),
                    "confidence": verdict.confidence,
                    "rationale": verdict.rationale,
                }
                for verdict in self.verdicts
            ],
        }


@dataclass(frozen=True)
class PanelReport:
    """The archived panel run. Machine-readable via `to_dict`; never a human adjudication record."""

    panel_id: str
    rubric_id: str
    rubric_hash: str
    policy: DisagreementPolicy
    judge_ids: tuple[str, ...]
    lineage_ids: tuple[str, ...]
    independence: IndependenceWitness
    agreement: tuple[AgreementReport, ...]
    records: tuple[AdjudicationRecord, ...]
    off_vocabulary_coordinates: tuple[str, ...] = ()
    adjudicator_kind: str = ADJUDICATOR_KIND
    human_adjudication: bool = field(default=False)

    def __post_init__(self) -> None:
        if self.human_adjudication or self.adjudicator_kind != ADJUDICATOR_KIND:
            raise ValueError("this panel is model-based; it may not be recorded as human")

    def agreement_for(self, question: Question) -> AgreementReport | None:
        for report in self.agreement:
            if report.question is question:
                return report
        return None

    @property
    def adjudicated_records(self) -> tuple[AdjudicationRecord, ...]:
        return tuple(record for record in self.records if record.included_in_adjudicated_analysis)

    @property
    def excluded_records(self) -> tuple[AdjudicationRecord, ...]:
        return tuple(
            record for record in self.records if not record.included_in_adjudicated_analysis
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "panel_id": self.panel_id,
            "adjudicator_kind": self.adjudicator_kind,
            "human_adjudication": self.human_adjudication,
            "rubric_id": self.rubric_id,
            "rubric_hash": self.rubric_hash,
            "policy": self.policy.to_dict(),
            "policy_hash": self.policy.policy_hash,
            "judge_ids": list(self.judge_ids),
            "lineage_ids": list(self.lineage_ids),
            "independence": {
                "ok": self.independence.ok,
                "checks": [
                    {"name": c.name, "passed": c.passed, "detail": c.detail}
                    for c in self.independence.checks
                ],
            },
            "agreement": [report.to_dict() for report in self.agreement],
            "off_vocabulary_coordinates": list(self.off_vocabulary_coordinates),
            "records": [record.to_dict() for record in self.records],
        }


def _resolve_question(
    question: Question,
    verdicts: Sequence[JudgeVerdict],
    agreement: AgreementReport,
    policy: DisagreementPolicy,
) -> QuestionResolution:
    """The frozen policy of rubric section 7, applied mechanically. No branch consults a label."""

    abstaining = tuple(v.judge_id for v in verdicts if v.answer(question) is None)
    effective = [(v.judge_id, v.answer(question)) for v in verdicts if v.answer(question) is not None]

    def cannot_check(reason: CannotCheckReason) -> QuestionResolution:
        return QuestionResolution(
            question=question,
            outcome=PanelOutcome.CANNOT_CHECK,
            label=None,
            dissenting_judges=(),
            abstaining_judges=abstaining,
            cannot_check_reason=reason,
            kappa_at_decision=agreement.kappa,
        )

    if len(effective) < policy.quorum:
        return cannot_check(
            CannotCheckReason.ABSTENTION_BREAKS_QUORUM
            if abstaining
            else CannotCheckReason.NO_QUORUM
        )

    tally: dict[str, int] = {}
    label_by_key: dict[str, Hashable] = {}
    for _judge_id, answer in effective:
        key = _category_key(answer)
        tally[key] = tally.get(key, 0) + 1
        label_by_key.setdefault(key, answer)

    top = max(tally.values())
    winners = [key for key, count in tally.items() if count == top]
    if len(winners) > 1:
        return cannot_check(CannotCheckReason.NO_MAJORITY)

    winning_key = winners[0]
    winning_label = label_by_key[winning_key]
    dissent = tuple(
        judge_id for judge_id, answer in effective if _category_key(answer) != winning_key
    )

    if top == len(effective):
        return QuestionResolution(
            question=question,
            outcome=PanelOutcome.UNANIMOUS,
            label=winning_label,  # type: ignore[arg-type]
            dissenting_judges=(),
            abstaining_judges=abstaining,
            cannot_check_reason=None,
            kappa_at_decision=agreement.kappa,
        )

    if policy.require_strict_majority and top * 2 <= len(effective):
        return cannot_check(CannotCheckReason.NO_MAJORITY)
    if agreement.kappa is None:
        if policy.require_defined_kappa_for_majority:
            return cannot_check(CannotCheckReason.AGREEMENT_UNDEFINED)
    elif agreement.kappa < policy.kappa_threshold:
        return cannot_check(CannotCheckReason.AGREEMENT_BELOW_THRESHOLD)

    return QuestionResolution(
        question=question,
        outcome=PanelOutcome.MAJORITY_WITH_DISSENT,
        label=winning_label,  # type: ignore[arg-type]
        dissenting_judges=dissent,
        abstaining_judges=abstaining,
        cannot_check_reason=None,
        kappa_at_decision=agreement.kappa,
    )


def adjudicate(
    case_views: Sequence[PublicView],
    judges: Sequence[JudgeBackend],
    *,
    rubric_hash: str,
    rubric_body: str = "",
    policy: DisagreementPolicy = V1_POLICY,
) -> PanelReport:
    """Run the blinded model panel over a batch of cases and resolve it under the frozen policy.

    Every judge sees exactly one thing per case — the `PublicView` — plus the rubric it was
    frozen against. Verdicts are collected into a local list and never handed back to a
    backend, which is what makes the judges independent by construction rather than by
    promise. Kappa is a batch statistic, so the panel is a batch operation: a single case
    can be resolved by unanimity but never by the majority-plus-kappa branch.
    """

    if not _HEX64.match(rubric_hash):
        raise RubricIntegrityError("rubric_hash must be a sha256 hex digest")
    if rubric_body and rubric_content_hash(rubric_body) != rubric_hash:
        raise RubricIntegrityError(
            "rubric_body does not hash to the declared rubric_hash; refusing to adjudicate"
        )
    if rubric_body:
        frozen = policy_from_rubric(rubric_body)
        if frozen != policy:
            raise PolicyError(
                "runtime policy differs from the policy frozen in the rubric body: "
                f"{policy.to_dict()} != {frozen.to_dict()}"
            )

    for view in case_views:
        if not isinstance(view, PublicView) or hasattr(view, "protected_gold"):
            raise TypeError(
                "adjudicate accepts PublicView only: a judge may never be handed a "
                f"HiddenShiftCase or its ProtectedGold (got {type(view).__name__})"
            )
    ordered = sorted(case_views, key=lambda view: view.case_id)
    ids = [view.case_id for view in ordered]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate case ids in the adjudication batch")

    preflight = panel_independence_witness(judges, min_judges=policy.min_judges)
    if not preflight.ok:
        raise IndependenceError(
            "panel independence not witnessed: " + "; ".join(preflight.failures)
        )

    verdicts_by_case: list[tuple[JudgeVerdict, ...]] = []
    issued_contexts: list[str] = []
    for view in ordered:
        row: list[JudgeVerdict] = []
        for backend in judges:
            context_id = backend.new_context()
            issued_contexts.append(context_id)
            verdict = backend.judge(
                view,
                rubric_body=rubric_body,
                rubric_hash=rubric_hash,
                context_id=context_id,
            )
            if not isinstance(verdict, JudgeVerdict):
                raise TypeError(f"{backend.judge_id} returned {type(verdict).__name__}")
            if verdict.rubric_hash != rubric_hash:
                raise RubricMismatchError(
                    f"{view.case_id}/{backend.judge_id} answered from rubric "
                    f"{verdict.rubric_hash[:12]}…, panel declared {rubric_hash[:12]}…"
                )
            if verdict.case_id != view.case_id or verdict.judge_id != backend.judge_id:
                raise AdjudicationError(
                    f"verdict identity mismatch for {view.case_id}/{backend.judge_id}"
                )
            if verdict.context_id != context_id:
                raise IndependenceError(
                    f"{view.case_id}/{backend.judge_id} answered from a context the panel "
                    "did not issue; per-invocation isolation is unverifiable"
                )
            row.append(replace(verdict, lineage_id=backend.lineage_id))
        verdicts_by_case.append(tuple(row))

    posthoc = panel_independence_witness(
        judges, context_ids=issued_contexts, min_judges=policy.min_judges
    )
    if not posthoc.ok:
        raise IndependenceError(
            "panel independence not witnessed: " + "; ".join(posthoc.failures)
        )

    agreement = tuple(
        build_agreement_report(question, verdicts_by_case) for question in Question
    )
    agreement_by_question = {report.question: report for report in agreement}

    records: list[AdjudicationRecord] = []
    for view, verdicts in zip(ordered, verdicts_by_case, strict=True):
        resolutions = tuple(
            _resolve_question(question, verdicts, agreement_by_question[question], policy)
            for question in Question
        )
        primary = next(r for r in resolutions if r.question is PRIMARY_QUESTION)
        records.append(
            AdjudicationRecord(
                case_id=view.case_id,
                verdicts=verdicts,
                resolutions=resolutions,
                agreement=agreement,
                status=(
                    AdjudicationStatus.MODEL_ADJUDICATED
                    if primary.included
                    else None  # CANNOT_CHECK: excluded from analysis, retained in the archive
                ),
            )
        )

    off_vocabulary = sorted(
        {
            f"{verdict.judge_id}:{name}"
            for verdicts in verdicts_by_case
            for verdict in verdicts
            for name in verdict.off_vocabulary_coordinates()
        }
    )
    judge_ids = tuple(backend.judge_id for backend in judges)
    lineage_ids = tuple(backend.lineage_id for backend in judges)
    panel_id = hashlib.sha256(
        json.dumps(
            {
                "rubric_hash": rubric_hash,
                "policy_hash": policy.policy_hash,
                "judges": sorted(judge_ids),
                "lineages": sorted(lineage_ids),
                "cases": ids,
                "adjudicator_kind": ADJUDICATOR_KIND,
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()

    return PanelReport(
        panel_id=panel_id,
        rubric_id="P1.adjudication-rubric.v1",
        rubric_hash=rubric_hash,
        policy=policy,
        judge_ids=judge_ids,
        lineage_ids=lineage_ids,
        independence=posthoc,
        agreement=agreement,
        records=tuple(records),
        off_vocabulary_coordinates=tuple(off_vocabulary),
    )


__all__ = [
    "ADJUDICATOR_KIND",
    "AdjudicationError",
    "AdjudicationRecord",
    "AgreementReport",
    "COORDINATE_VOCABULARY",
    "CannotCheckReason",
    "DisagreementPolicy",
    "FrozenRubric",
    "IndependenceCheck",
    "IndependenceError",
    "IndependenceWitness",
    "JudgeBackend",
    "JudgeVerdict",
    "PRIMARY_QUESTION",
    "PanelOutcome",
    "PanelReport",
    "PolicyError",
    "Question",
    "QuestionResolution",
    "REFRAME_WARRANTING_CLASSES",
    "ResponsibilityClass",
    "RubricIntegrityError",
    "RubricMismatchError",
    "V1_POLICY",
    "adjudicate",
    "build_agreement_report",
    "cohens_kappa",
    "extract_rubric_body",
    "fleiss_kappa",
    "load_rubric",
    "mean_pairwise_agreement",
    "panel_independence_witness",
    "policy_from_rubric",
    "rubric_content_hash",
]
