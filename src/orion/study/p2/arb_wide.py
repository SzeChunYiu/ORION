"""AutoResearchBench Wide adapter: bundle loading, gold custody, frozen subsample.

Three jobs, deliberately kept in one place because they share one invariant.

1. **Custody.** The system under test receives a ``TaskPrompt`` carrying a task
   id and a question. Gold answers and gold arXiv ids stay inside
   ``GoldCustody`` and are never reachable from anything handed out. This is
   structural, not a convention: a ``TaskPrompt`` holds no reference to its
   ``WideTask``, to the custody object, or to any container holding either, so
   there is no object path from candidate to gold to follow.

2. **Identity bridge.** ORION works in canonical merged identities
   (``arxiv:2501.00001``, ``doi:10.1234/x``); the official scorer works in bare
   normalised arXiv id strings. Getting that conversion wrong yields IoU 0.0 for
   every task, which reads as a result rather than a bug, so the bridge is one
   named function with its own tests rather than an inline string split.

3. **Frozen subsample.** Which tasks run is fixed, hashed and written down
   before any system runs, so the selection cannot be tuned to an outcome.

The bundle itself is never committed. It is regenerated from the Hugging Face
dataset ``Lk123/AutoResearchBench`` and the upstream ``decrypt_benchmark.py``;
see ``REGENERATION_RECIPE`` below and the access evidence records.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import random
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

from orion.knowledge.identity import IdentityScheme, SourceIdentity, canonical_source_id

from .arb_scoring import compute_iou_recall, get_gt_arxiv_ids, get_predicted_arxiv_ids

__all__ = [
    "BUNDLE_ENV_VAR",
    "BUNDLE_SHA256",
    "GoldCustody",
    "REGENERATION_RECIPE",
    "TaskPrompt",
    "TaskScore",
    "WideTask",
    "achieved_half_width",
    "arxiv_predictions_from_identities",
    "build_subsample_manifest",
    "canonical_manifest_hash",
    "derive_task_id",
    "load_wide_tasks",
    "precision_tier",
    "publication_stats",
    "select_subsample",
]

BUNDLE_ENV_VAR = "ORION_ARB_BUNDLE"

#: sha256 of the decrypted ``AutoResearchBench.jsonl`` this adapter was built
#: against. Recorded in ``evidence/access/autoresearchbench_decrypt_record.json``
#: and in ``evidence/access/fetched_artifact_hashes.json``.
BUNDLE_SHA256 = "db1839438033a32dd7d76913575d4b76f144d5e442aaac29be4eda32326392c6"

REGENERATION_RECIPE = """\
1. Download AutoResearchBench.jsonl.obf.json from the Hugging Face dataset
   Lk123/AutoResearchBench (sha256
   e8d00086dc05bae823d75bf0776a9df5f8bcab59e0d683ea6479ac9e40db631d).
2. Check out CherYou/AutoResearchBench at commit
   a46c9bfb8968786f73f0a6a5b365b5384cd0f96d.
3. python3 decrypt_benchmark.py --input-file AutoResearchBench.jsonl.obf.json \\
       --output-file AutoResearchBench.jsonl
   No secret is required: the bundle stores its own canary string.
4. Verify sha256(AutoResearchBench.jsonl) == BUNDLE_SHA256.
5. Point ORION_ARB_BUNDLE at the result. Do not commit it: the upstream README
   asks that decrypted questions and answers are not reposted.
"""

_REPO_ROOT = Path(__file__).resolve().parents[4]
_STATS_MODULE_PATH = (
    _REPO_ROOT / "research" / "paper-programme-v1" / "protocols" / "publication_stats.py"
)

#: Precision tiers, copied from STATISTICAL_PLAN_V1.json ``precision_plan``.
#: Required N is never typed here -- it is recomputed from the frozen planning
#: function so a drift between this table and the plan is a test failure.
PRECISION_TIERS: tuple[tuple[str, float], ...] = (
    ("TIER_A_full", 0.03),
    ("TIER_B_committed", 0.05),
    ("TIER_C_reduced", 0.075),
    ("TIER_D_minimum_inferential", 0.1),
)

#: Above this achieved half-width the family carries the mandatory
#: ``UNDERPOWERED`` label (MEASUREMENT_PLAN_V1.md section 5).
UNDERPOWERED_ABOVE_HALF_WIDTH = 0.03


def publication_stats() -> ModuleType:
    """Load the frozen statistics module. Reimplementing its functions is forbidden."""

    if not _STATS_MODULE_PATH.is_file():
        raise FileNotFoundError(
            f"frozen statistics module not found at {_STATS_MODULE_PATH}; "
            "the achieved-precision figures cannot be computed without it"
        )
    spec = importlib.util.spec_from_file_location(
        "orion_p2_publication_stats", _STATS_MODULE_PATH
    )
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load {_STATS_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Task objects and the custody boundary.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TaskPrompt:
    """Everything the system under test is allowed to see. Nothing else.

    Deliberately a flat value object with two strings. It carries no reference
    to the ``WideTask`` it came from, so no amount of attribute walking from a
    prompt reaches a gold id.
    """

    task_id: str
    question: str

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("a task prompt requires a task id")
        if not self.question.strip():
            raise ValueError("a task prompt requires a question")


@dataclass(frozen=True)
class WideTask:
    """One Wide benchmark record, host-side only. Never handed to a candidate."""

    task_id: str
    question: str
    gold_arxiv_ids: tuple[str, ...]
    answer_titles: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("a wide task requires a task id")
        if not self.gold_arxiv_ids:
            raise ValueError(
                f"wide task {self.task_id} has no gold arxiv ids; an empty gold "
                "set scores 1.0 against an empty prediction and would silently "
                "reward a system that returned nothing"
            )

    def prompt(self) -> TaskPrompt:
        """Build the candidate-visible view. A fresh object, not a projection."""

        return TaskPrompt(task_id=self.task_id, question=self.question)


@dataclass(frozen=True)
class TaskScore:
    """One task's official Wide score, produced host-side."""

    task_id: str
    iou: float
    recall: float
    precision: float
    gold_count: int
    predicted_count: int
    hit_count: int


def derive_task_id(question: str, occurrence: int = 0) -> str:
    """Content-derived, file-order independent task key.

    Order independence matters because the subsample must be reproducible from
    the bundle alone, not from the order a particular download happened to
    produce. ``occurrence`` disambiguates byte-identical duplicate rows.
    """

    digest = hashlib.sha256(question.encode("utf-8")).hexdigest()[:16]
    return f"wide-{digest}" if occurrence == 0 else f"wide-{digest}-{occurrence + 1}"


def count_wide_rows(path: str | Path | None = None) -> int:
    """Count raw ``type=wide`` rows before deduplication.

    Measured rather than asserted: the difference between this and
    ``len(load_wide_tasks(...))`` is exactly the duplicate-row count, and a
    manifest that hardcoded either number would keep claiming it after the
    bundle changed.
    """

    resolved = _resolve_bundle_path(path)
    rows = 0
    with resolved.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            if json.loads(stripped).get("type") == "wide":
                rows += 1
    return rows


def load_wide_tasks(path: str | Path | None = None) -> tuple[WideTask, ...]:
    """Read the decrypted bundle and return the Wide tasks, deduplicated.

    **Deduplication is deliberate and is a declared deviation.** The pinned
    bundle holds 400 Wide rows but only 399 distinct questions: one question
    appears twice as a byte-identical row. Scoring it twice would add a second
    copy of one task to the sample, inflating N with a unit that carries no
    independent information. Upstream's own ``load_gt_file`` keys ground truth
    by question and so collapses the pair the same way.

    A repeated question carrying *different* gold is a different situation and
    is kept as two tasks, disambiguated by ``derive_task_id`` occurrence.
    """

    resolved = _resolve_bundle_path(path)
    grouped: dict[str, list[WideTask]] = {}
    with resolved.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"{resolved}:{line_number} is not valid JSON: {error}"
                ) from error
            if record.get("type") != "wide":
                continue
            question = str(record.get("question", "")).strip()
            if not question:
                continue
            gold = tuple(
                sorted({str(item) for item in record.get("arxiv_id", []) or [] if item})
            )
            titles = tuple(str(item) for item in record.get("answer", []) or [])
            bucket = grouped.setdefault(question, [])
            if any(item.gold_arxiv_ids == gold for item in bucket):
                # Byte-identical duplicate row: one task, not two.
                continue
            bucket.append(
                WideTask(
                    task_id=derive_task_id(question, len(bucket)),
                    question=question,
                    gold_arxiv_ids=gold,
                    answer_titles=titles,
                )
            )
    tasks = [item for bucket in grouped.values() for item in bucket]
    if not tasks:
        raise ValueError(f"no Wide records found in {resolved}")
    return tuple(sorted(tasks, key=lambda item: item.task_id))


def _resolve_bundle_path(path: str | Path | None) -> Path:
    if path is not None:
        resolved = Path(path)
    else:
        raw = os.environ.get(BUNDLE_ENV_VAR, "").strip()
        if not raw:
            raise FileNotFoundError(
                f"no bundle path given and {BUNDLE_ENV_VAR} is unset. The "
                "AutoResearchBench bundle is deliberately not committed; "
                f"regenerate it:\n{REGENERATION_RECIPE}"
            )
        resolved = Path(raw)
    if not resolved.is_file():
        raise FileNotFoundError(f"AutoResearchBench bundle not found at {resolved}")
    return resolved


@dataclass
class GoldCustody:
    """Host-side owner of the gold. Scores candidate output; never reveals gold.

    There is no accessor that returns a gold id. Scoring happens *inside* this
    object and only aggregate numbers come back out, so a candidate cannot
    obtain the answer by asking politely, and cannot obtain it by asking
    repeatedly either -- ``TaskScore`` carries counts, not members.
    """

    _tasks: dict[str, WideTask] = field(repr=False)

    def __init__(self, tasks: Iterable[WideTask]) -> None:
        collected = {}
        for task in tasks:
            if task.task_id in collected:
                raise ValueError(f"duplicate task id in custody: {task.task_id}")
            collected[task.task_id] = task
        if not collected:
            raise ValueError("gold custody requires at least one task")
        self._tasks = collected

    @property
    def size(self) -> int:
        return len(self._tasks)

    def task_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._tasks))

    def prompts(self) -> tuple[TaskPrompt, ...]:
        """Candidate-visible views, in task-id order. Fresh objects each call."""

        return tuple(self._tasks[key].prompt() for key in sorted(self._tasks))

    def prompt(self, task_id: str) -> TaskPrompt:
        return self._require(task_id).prompt()

    def gold_count(self, task_id: str) -> int:
        """How many gold items exist. A count is not a membership oracle."""

        return len(self._require(task_id).gold_arxiv_ids)

    def score(self, task_id: str, predicted_arxiv_ids: Sequence[str]) -> TaskScore:
        """Score one task through the vendored official path.

        The prediction sequence is copied before use, so a candidate cannot hand
        in a live view and mutate it after the gold set has been intersected.
        """

        task = self._require(task_id)
        frozen_prediction = [str(item) for item in predicted_arxiv_ids]
        gold = get_gt_arxiv_ids({"arxiv_id": list(task.gold_arxiv_ids)}, use_jina=False)
        predicted = get_predicted_arxiv_ids(
            [{"arxiv_id": item} for item in frozen_prediction]
        )
        iou, recall, precision = compute_iou_recall(gold, predicted)
        return TaskScore(
            task_id=task_id,
            iou=iou,
            recall=recall,
            precision=precision,
            gold_count=len(gold),
            predicted_count=len(predicted),
            hit_count=len(gold & predicted),
        )

    def _require(self, task_id: str) -> WideTask:
        try:
            return self._tasks[task_id]
        except KeyError as error:
            raise KeyError(f"task {task_id!r} is not under custody") from error


# ---------------------------------------------------------------------------
# The identity bridge.
# ---------------------------------------------------------------------------


def arxiv_predictions_from_identities(
    identities: Iterable[SourceIdentity],
) -> tuple[str, ...]:
    """Convert merged ORION identities into bare arXiv ids for the official scorer.

    **Every** key of a merged identity is examined, not just its primary. A work
    reached first by DOI has a DOI primary key and an arXiv alias; the Wide gold
    is arXiv-only, so scoring the primary alone would miss a genuine hit and
    report it as a zero. Aliases are exactly what ``merge_identities`` exists to
    accumulate, and this is the point where that work has to pay off.

    Version suffixes are already stripped by ``canonical_source_id``; old-style
    ids (``cs/0409043``) are emitted unchanged because the official
    ``normalize_arxiv_id`` passes them through unchanged too, and 17 of the Wide
    gold ids are old-style.
    """

    found: list[str] = []
    for identity in identities:
        for key in sorted(identity.keys):
            try:
                canonical = canonical_source_id(key)
            except ValueError:
                continue
            if canonical.scheme is IdentityScheme.ARXIV and canonical.value:
                found.append(canonical.value)
    return tuple(dict.fromkeys(found))


# ---------------------------------------------------------------------------
# Frozen subsample and achieved precision.
# ---------------------------------------------------------------------------


def select_subsample(
    task_ids: Sequence[str], size: int | None = None, seed: int = 0
) -> tuple[str, ...]:
    """Deterministically choose which tasks run.

    With ``size`` at or above the population the selection is the identity map
    over all tasks and the seed does nothing -- that is the intended case for
    Wide, where the whole family is only 399 tasks. The seeded branch exists for
    a budget-forced reduction and is tested, so the reduced path is not first
    exercised on the day it is needed.
    """

    population = sorted(dict.fromkeys(task_ids))
    if not population:
        raise ValueError("cannot subsample an empty task population")
    if size is None or size >= len(population):
        return tuple(population)
    if size < 1:
        raise ValueError("subsample size must be positive")
    chosen = random.Random(seed).sample(population, size)
    return tuple(sorted(chosen))


def achieved_half_width(n: int, assumed_p: float = 0.5, tolerance: float = 1e-6) -> float:
    """Smallest half-width this N supports, derived from the frozen function.

    Computed by inverting ``publication_stats.required_n_for_proportion_half_width``
    by bisection rather than by re-typing its formula, because
    ``MEASUREMENT_PLAN_V1.md`` forbids reimplementing the statistics module. The
    returned value satisfies ``required_n(h) <= n`` while ``required_n(h -
    tolerance) > n``, which is asserted by the caller-facing test.
    """

    if n < 1:
        raise ValueError("achieved half-width needs at least one task")
    stats = publication_stats()
    required_n = stats.required_n_for_proportion_half_width

    low, high = tolerance, 0.999999
    if required_n(high, assumed_p) > n:
        raise ValueError(f"n={n} is too small to support any half-width below 1.0")
    for _ in range(200):
        mid = (low + high) / 2.0
        if required_n(mid, assumed_p) <= n:
            high = mid
        else:
            low = mid
    # Round up to a reproducible 6 decimal places, then confirm the rounding did
    # not land on a half-width this N cannot actually support.
    candidate = math.ceil(high * 1_000_000) / 1_000_000
    if required_n(candidate, assumed_p) > n:  # pragma: no cover - defensive
        candidate = math.ceil((high + tolerance) * 1_000_000) / 1_000_000
    return candidate


def precision_tier(half_width: float) -> str:
    """Name the tightest frozen tier this half-width satisfies."""

    for name, bound in PRECISION_TIERS:
        if half_width <= bound:
            return name
    return "BELOW_TIER_D_DESCRIPTIVE_ONLY"


def canonical_manifest_hash(payload: Mapping[str, object]) -> str:
    """Hash a manifest over a canonical serialisation so it reproduces."""

    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_subsample_manifest(
    tasks: Sequence[WideTask],
    *,
    selected_task_ids: Sequence[str],
    seed: int,
    raw_wide_rows: int,
    bundle_sha256: str = BUNDLE_SHA256,
) -> dict[str, object]:
    """Assemble the frozen subsample record, hash included.

    The manifest carries task **ids** only. It carries no question text, no
    answer title and no gold id, so it is safe to commit while the bundle is
    not.
    """

    selected = tuple(sorted(dict.fromkeys(selected_task_ids)))
    population = tuple(sorted(item.task_id for item in tasks))
    unknown = [item for item in selected if item not in set(population)]
    if unknown:
        raise ValueError(f"selected task ids are not in the population: {unknown[:5]}")

    n = len(selected)
    half_width = achieved_half_width(n)
    tier = precision_tier(half_width)
    stats = publication_stats()
    body: dict[str, object] = {
        "schema_version": "orion.p2.arb-wide-subsample.v1",
        "paper_id": "P2",
        "protocol_id": "P2.open-world-discovery.v1",
        "task_family": "autoresearchbench_wide",
        "benchmark": {
            "dataset": "Lk123/AutoResearchBench",
            "code_revision": "CherYou/AutoResearchBench@a46c9bfb8968786f73f0a6a5b365b5384cd0f96d",
            "bundle_sha256": bundle_sha256,
            "licence": "Apache-2.0",
        },
        "population": {
            "wide_rows_in_bundle": raw_wide_rows,
            "distinct_tasks": len(population),
            "duplicate_rows_collapsed": raw_wide_rows - len(population),
            "deduplication": (
                "byte-identical duplicate Wide rows are one task, not two. "
                "Upstream load_gt_file keys ground truth by question and "
                "collapses them the same way. A repeated question carrying "
                "different gold is kept as two tasks."
            ),
        },
        "selection": {
            "rule": (
                "all distinct Wide tasks"
                if n == len(population)
                else f"seeded random sample of {n} without replacement"
            ),
            "seed": seed,
            "seed_is_inert": n == len(population),
            "n": n,
            "task_ids": list(selected),
        },
        "precision": {
            "assumed_p": 0.5,
            "achieved_half_width": half_width,
            "achieved_tier": tier,
            "required_n_for_achieved_half_width": stats.required_n_for_proportion_half_width(
                half_width, 0.5
            ),
            "underpowered": half_width > UNDERPOWERED_ABOVE_HALF_WIDTH,
            "underpowered_rule": (
                "MEASUREMENT_PLAN_V1.md section 5: any family whose achieved "
                "half-width exceeds 0.03 is labelled UNDERPOWERED."
            ),
            "tier_a_would_require_n": stats.required_n_for_proportion_half_width(
                0.03, 0.5
            ),
        },
        "custody": (
            "task ids only. No question text, answer title or gold arXiv id "
            "appears in this manifest."
        ),
    }
    body["content_hash"] = canonical_manifest_hash(body)
    return body
