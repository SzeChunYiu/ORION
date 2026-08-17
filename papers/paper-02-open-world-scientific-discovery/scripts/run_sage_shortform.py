#!/usr/bin/env python3
"""SAGE short-form retrieval as an external task family under declared scoring.

SAGE ships 600 short-form queries with public gold, but neither its 200k
retrieval corpus nor its evaluator was ever published. So this family can be
*run* faithfully and can never be *scored officially*: every number produced
here is a host-declared deviation, and the module refuses to describe any of
them as official.

Three commands, in custody order:

``prepare``  the only command allowed to read gold. It parses the four fetched
             SAGE files, builds the eligible task pool, and splits it into a
             public candidate file holding the query text alone and a host-only
             ground-truth file. It also measures the contamination that public
             plaintext gold implies, and checks the declared normalisations for
             collisions *before* anything is scored.

``run``      accepts the public file only and cannot be handed a gold path. Two
             systems execute under an identical per-task provider-request
             budget; a budget mismatch makes the family INVALID under the frozen
             statistical plan, so the command refuses rather than records it.

``score``    applies the declared normalisations, emits the frozen plan's
             required bindings, and marks every metric whose denominator is not
             established as CANNOT_CHECK rather than reporting a convenient
             number.

Deliberate non-goals, stated because their absence is easy to misread as an
oversight: no arXiv request is ever issued (the arXiv budget belongs to another
run), no credential is read, and the upstream data is fetched rather than
vendored because the pinned revision carries no licence.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:  # pragma: no cover - import wiring
    sys.path.insert(0, str(REPO_ROOT / "src"))

from orion.core.search import SearchRouteKind  # noqa: E402
from orion.knowledge.rate import (  # noqa: E402
    PROVIDER_BUDGETS,
    BudgetBasis,
    ProviderBudget,
    RateGate,
)
from orion.knowledge.route_control import (  # noqa: E402
    FrozenRouteControlPolicy,
    RouteAttempt,
    RouteControlState,
    decide_route,
)
from orion.knowledge.routes import RouteCapture, assess_pair  # noqa: E402

# --------------------------------------------------------------------------
# Upstream pin. HughieHu/Sage carries no LICENSE at this revision, so counts
# and hashes may be recorded but the records themselves are never committed.
# --------------------------------------------------------------------------
PINNED_SAGE_COMMIT = "bc62257a13d81ae233ecbd508037614746d2776b"
SAGE_UPSTREAM = "HughieHu/Sage"
SAGE_DOMAINS = ("computer_science", "healthcare", "humanities", "natural_science")
SHORT_FORM_SUBDIR = "Sage_Short_Form_Questions"

# Keys that carry the answer. `paper_id` and `paper_title` are included because
# this audit verified they are byte-identical to ground_truth.paperId/.title in
# every record that has gold: they are gold under a different name, and a
# custody check that only hid `ground_truth` would leak the answer twice.
GOLD_KEYS = frozenset(
    {"ground_truth", "paper_id", "paper_title", "paperid", "gold", "answer", "target"}
)
PUBLIC_RECORD_KEYS = frozenset({"task_id", "domain", "complete_query"})

# The statistical plan owns these; they are mirrored here as constants so a
# drift between script and plan is visible rather than silent.
PRECISION_TIERS = (
    ("TIER_A_full", 0.03, 1068),
    ("TIER_B_committed", 0.05, 385),
    ("TIER_C_reduced", 0.075, 171),
    ("TIER_D_minimum_inferential", 0.1, 97),
)
DELTA_SUP = 0.03
FROZEN_QUERY_COUNT_LADDER = (10, 20, 40, 80, 120, 200)
ANALYSIS_SEED = 20260816

PUBLICATION_STATS_PATH = Path("research/paper-programme-v1/protocols/publication_stats.py")


# --------------------------------------------------------------------------
# Frozen statistics library. The plan sets reimplementation_forbidden, so the
# interval must come from this file rather than from a local helper that merely
# agrees with it: the requirement is provenance, not numerical coincidence.
# --------------------------------------------------------------------------
def load_publication_stats(repo_root: Path | None = None) -> Any:
    root = repo_root or REPO_ROOT
    path = root / PUBLICATION_STATS_PATH
    if not path.is_file():
        raise FileNotFoundError(
            f"frozen statistics library missing at {path}; the plan forbids reimplementing it"
        )
    spec = importlib.util.spec_from_file_location("orion_publication_stats", path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load frozen statistics library at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# Small IO helpers, matching the house pattern in run_autoresearchbench_*.
# --------------------------------------------------------------------------
def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: record must be a JSON object")
            records.append(value)
    return records


def _gold_paths(value: Any, prefix: str = "$") -> list[str]:
    """Every path in `value` whose key names an answer field."""

    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{prefix}.{key}"
            if str(key).strip().lower().replace("-", "_") in GOLD_KEYS:
                found.append(child)
            found.extend(_gold_paths(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_gold_paths(item, f"{prefix}[{index}]"))
    return found


# --------------------------------------------------------------------------
# Declared title normalisation. Both variants are ordered transform lists so
# the protocol document and the code cannot drift; each step is separately
# testable, and neither variant is defensible without the collision check that
# `prepare` runs over the gold set.
# --------------------------------------------------------------------------
STRICT_TRANSFORMS = (
    "unicode_nfkd",
    "drop_combining_marks",
    "map_typographic_punctuation_to_ascii",
    "casefold",
    "non_alphanumeric_runs_to_single_space",
    "collapse_and_strip_whitespace",
)
RELAXED_TRANSFORMS = STRICT_TRANSFORMS + ("gold_token_run_contained_in_candidate",)

_PUNCT_MAP = {
    "’": "'", "‘": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "−": "-", " ": " ",
}


def normalise_title(value: str) -> str:
    """Apply STRICT_TRANSFORMS in order."""

    text = unicodedata.normalize("NFKD", value)
    text = "".join(char for char in text if not unicodedata.combining(char))
    for source, target in _PUNCT_MAP.items():
        text = text.replace(source, target)
    text = text.casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def title_digest(value: str) -> str:
    """Content identity for a retrieved rendition.

    Binding B4/B7 require a content digest rather than a provider-minted id:
    dedup on DBLP keys or DOIs would let one paper found by two routes look
    like two papers and inflate every unique-yield number built on overlap.
    """

    return "sha256:" + _sha256_bytes(normalise_title(value).encode("utf-8"))


def strict_match(candidate: str, gold: str) -> bool:
    return bool(normalise_title(gold)) and normalise_title(candidate) == normalise_title(gold)


def relaxed_match(candidate: str, gold: str) -> bool:
    """Strict, or the gold token run appears contiguously inside the candidate.

    This absorbs the trailing full stop DBLP appends and publisher-appended
    subtitles, without the far more destructive move of truncating titles at
    their first colon -- which collapses "ReConcile: ..." to "reconcile" and
    was rejected because `prepare` reports the collisions it causes.
    """

    gold_normalised = normalise_title(gold)
    candidate_normalised = normalise_title(candidate)
    if not gold_normalised or not candidate_normalised:
        return False
    if candidate_normalised == gold_normalised:
        return True
    gold_tokens = gold_normalised.split()
    candidate_tokens = candidate_normalised.split()
    if len(gold_tokens) < 3 or len(candidate_tokens) < len(gold_tokens):
        return False
    for start in range(len(candidate_tokens) - len(gold_tokens) + 1):
        if candidate_tokens[start : start + len(gold_tokens)] == gold_tokens:
            return True
    return False


MATCHERS: dict[str, Callable[[str, str], bool]] = {
    "strict": strict_match,
    "relaxed": relaxed_match,
}


# --------------------------------------------------------------------------
# Contamination, measured offline. Whether a backend's own index ingested SAGE
# is not measurable from here and is reported CANNOT_CHECK, which is a distinct
# outcome from "fine".
# --------------------------------------------------------------------------
def longest_common_token_run(left: str, right: str) -> int:
    left_tokens = normalise_title(left).split()
    right_tokens = normalise_title(right).split()
    if not left_tokens or not right_tokens:
        return 0
    best = 0
    for size in range(1, min(len(left_tokens), len(right_tokens)) + 1):
        right_grams = {
            tuple(right_tokens[index : index + size])
            for index in range(len(right_tokens) - size + 1)
        }
        if any(
            tuple(left_tokens[index : index + size]) in right_grams
            for index in range(len(left_tokens) - size + 1)
        ):
            best = size
        else:
            break
    return best


def gold_token_overlap(query: str, gold_title: str) -> float:
    gold_tokens = set(normalise_title(gold_title).split())
    if not gold_tokens:
        return 0.0
    query_tokens = set(normalise_title(query).split())
    return len(gold_tokens & query_tokens) / len(gold_tokens)


def contamination_report(records: list[dict[str, Any]]) -> dict[str, Any]:
    overlaps: list[float] = []
    runs: list[int] = []
    verbatim = 0
    for record in records:
        gold = record["gold_title"]
        query = record["complete_query"]
        overlaps.append(gold_token_overlap(query, gold))
        runs.append(longest_common_token_run(query, gold))
        if normalise_title(gold) and normalise_title(gold) in normalise_title(query):
            verbatim += 1
    total = len(records) or 1
    ordered = sorted(overlaps)
    median = ordered[len(ordered) // 2] if ordered else 0.0
    return {
        "measured_offline_without_network": True,
        "gold_is_public_plaintext_in_same_record_as_query": True,
        "gold_title_token_overlap_in_query": {
            "mean": round(sum(overlaps) / total, 4),
            "median": round(median, 4),
            "records_at_or_above_half": sum(1 for value in overlaps if value >= 0.5),
            "records_with_every_gold_token_present": sum(1 for value in overlaps if value >= 0.999),
        },
        "longest_common_token_run_with_gold_title": {
            "mean": round(sum(runs) / total, 3),
            "max": max(runs) if runs else 0,
            "records_at_or_above_five": sum(1 for value in runs if value >= 5),
        },
        "gold_title_verbatim_inside_query": verbatim,
        "interpretation": (
            "Queries describe the target by year, venue, title shape, a figure and co-citation "
            "structure, and quote the titles of OTHER papers rather than the target. Substantial "
            "token overlap with the gold title is therefore mostly shared topical vocabulary, not "
            "a copy of the answer; the verbatim count is the number that would make declared "
            "exact match a string-recovery task."
        ),
        "backend_index_ingested_sage": "CANNOT_CHECK",
        "backend_index_ingested_sage_reason": (
            "Whether OpenAIRE, DBLP or Crossref indexed the SAGE repository itself is not "
            "observable through their search APIs. Not checked is not the same as absent."
        ),
    }


def normalisation_collisions(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Do the declared normalisations make two distinct gold titles identical?

    A metric whose matcher cannot separate two gold answers is ambiguous at
    that setting, so this runs over the gold set alone before any scoring.
    """

    by_strict: dict[str, set[str]] = {}
    for record in records:
        by_strict.setdefault(normalise_title(record["gold_title"]), set()).add(
            record["gold_paper_id"]
        )
    strict_collisions = {key: sorted(ids) for key, ids in by_strict.items() if len(ids) > 1}

    relaxed_collisions: list[dict[str, Any]] = []
    distinct = sorted({record["gold_title"] for record in records})
    normalised = [(title, normalise_title(title)) for title in distinct]
    by_length = sorted(normalised, key=lambda item: len(item[1].split()))
    for index, (short_title, short_norm) in enumerate(by_length):
        if len(short_norm.split()) < 3:
            continue
        for long_title, long_norm in by_length[index + 1 :]:
            if short_norm != long_norm and relaxed_match(long_norm, short_norm):
                relaxed_collisions.append({"contained": short_title, "container": long_title})
    return {
        "strict": {
            "distinct_gold_titles_sharing_a_normalised_form": len(strict_collisions),
            "examples": [
                {"normalised": key, "gold_paper_ids": ids}
                for key, ids in sorted(strict_collisions.items())[:5]
            ],
        },
        "relaxed": {
            "gold_titles_contained_in_another_gold_title": len(relaxed_collisions),
            "examples": relaxed_collisions[:5],
        },
        "rule": (
            "A collision under a variant does not invalidate that variant globally; it bounds it. "
            "Collision counts are reported with the metric so a reader can see how much of the "
            "measured rate could be an ambiguous match."
        ),
    }


# --------------------------------------------------------------------------
# prepare
# --------------------------------------------------------------------------
def _read_domain_file(source_dir: Path, domain: str) -> tuple[list[dict[str, Any]], str, int]:
    path = source_dir / f"short_{domain}.json"
    if not path.is_file():
        path = source_dir / f"{domain}.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"fetched SAGE short-form file for '{domain}' not found under {source_dir}"
        )
    payload = path.read_bytes()
    value = json.loads(payload)
    if not isinstance(value, list):
        raise ValueError(
            f"{path}: SAGE short-form files are JSON lists at the pinned commit, got "
            f"{type(value).__name__}"
        )
    return value, _sha256_bytes(payload), len(payload)


def build_eligible_pool(source_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Parse the four files and derive the scoreable population.

    Two upstream facts shape the pool and are recorded rather than smoothed
    over: one record ships without a `ground_truth` key, and thirteen queries
    appear twice. Both are verified here on every run.
    """

    per_file: dict[str, Any] = {}
    parsed: list[dict[str, Any]] = []
    for domain in SAGE_DOMAINS:
        records, digest, size = _read_domain_file(source_dir, domain)
        per_file[domain] = {"records": len(records), "sha256": digest, "bytes": size}
        for index, record in enumerate(records):
            parsed.append({"domain": domain, "source_index": index, "record": record})

    without_gold: list[dict[str, Any]] = []
    id_title_consistent = 0
    with_gold: list[dict[str, Any]] = []
    for item in parsed:
        record = item["record"]
        truth = record.get("ground_truth")
        if not isinstance(truth, dict) or not truth.get("title"):
            without_gold.append(
                {
                    "domain": item["domain"],
                    "source_index": item["source_index"],
                    "paper_id": record.get("paper_id"),
                }
            )
            continue
        if record.get("paper_id") == truth.get("paperId") and record.get("paper_title") == truth.get("title"):
            id_title_consistent += 1
        with_gold.append(item)

    # Identical query text with identical gold is the same task twice; keeping
    # both would inflate N and understate variance. Verified before dedup: no
    # duplicate query group disagrees about its gold, so this removes repeats
    # rather than resolving ambiguity.
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in with_gold:
        groups.setdefault(str(item["record"]["complete_query"]), []).append(item)
    ambiguous = [
        {
            "query_prefix": query[:120],
            "gold_paper_ids": sorted({str(entry["record"]["ground_truth"]["paperId"]) for entry in entries}),
        }
        for query, entries in groups.items()
        if len({str(entry["record"]["ground_truth"]["paperId"]) for entry in entries}) > 1
    ]
    if ambiguous:
        raise ValueError(
            "duplicate SAGE queries disagree about their gold answer; declared exact match is "
            f"undefined for {len(ambiguous)} group(s) and the pool cannot be built silently"
        )

    eligible: list[dict[str, Any]] = []
    duplicates_dropped = 0
    for query, entries in groups.items():
        ordered = sorted(entries, key=lambda entry: (SAGE_DOMAINS.index(entry["domain"]), entry["source_index"]))
        duplicates_dropped += len(ordered) - 1
        first = ordered[0]
        truth = first["record"]["ground_truth"]
        eligible.append(
            {
                "domain": first["domain"],
                "source_index": first["source_index"],
                "complete_query": query,
                "gold_paper_id": str(truth["paperId"]),
                "gold_title": str(truth["title"]),
            }
        )
    eligible.sort(key=lambda item: (SAGE_DOMAINS.index(item["domain"]), item["source_index"]))
    for position, item in enumerate(eligible, 1):
        item["task_id"] = f"sage-short-{position:04d}"

    distinct_targets = len({item["gold_paper_id"] for item in eligible})
    audit = {
        "per_file": per_file,
        "records_parsed": len(parsed),
        "records_with_gold": len(with_gold),
        "records_without_gold": without_gold,
        "paper_id_and_title_identical_to_gold": f"{id_title_consistent}/{len(with_gold)}",
        "paper_id_and_title_are_gold_under_another_name": id_title_consistent == len(with_gold),
        "duplicate_query_records_dropped": duplicates_dropped,
        "duplicate_query_groups_disagreeing_on_gold": len(ambiguous),
        "eligible_tasks": len(eligible),
        "distinct_gold_targets_in_eligible_pool": distinct_targets,
        "gold_targets_reused_across_tasks": len(eligible) - distinct_targets,
        "aggregation_unit": "query",
        "aggregation_unit_note": (
            "One task is one query. Some gold targets are the answer to two queries, so tasks are "
            "not fully independent Bernoulli trials; the reused-target count bounds that "
            "dependence and is reported with every interval."
        ),
    }
    return eligible, audit


def stratified_subsample(
    eligible: list[dict[str, Any]],
    *,
    test_size: int,
    pilot_size: int,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Seeded, domain-stratified draw. Pilot is drawn first and never re-enters.

    The frozen budget policy requires the cap to come from a declared pilot and
    forbids pilot tasks from the final test, so the two draws are disjoint by
    construction rather than by a later filter.
    """

    if test_size < 1 or pilot_size < 0:
        raise ValueError("test size must be positive and pilot size non-negative")
    if test_size + pilot_size > len(eligible):
        raise ValueError(
            f"cannot draw {test_size} test + {pilot_size} pilot tasks from {len(eligible)} eligible"
        )
    by_domain: dict[str, list[dict[str, Any]]] = {domain: [] for domain in SAGE_DOMAINS}
    for item in eligible:
        by_domain[item["domain"]].append(item)
    for domain in SAGE_DOMAINS:
        by_domain[domain].sort(key=lambda item: item["task_id"])
        random.Random(f"{seed}:{domain}").shuffle(by_domain[domain])

    def take(counts: dict[str, int]) -> list[dict[str, Any]]:
        drawn: list[dict[str, Any]] = []
        for domain in SAGE_DOMAINS:
            drawn.extend(by_domain[domain][: counts[domain]])
            by_domain[domain] = by_domain[domain][counts[domain] :]
        return sorted(drawn, key=lambda item: item["task_id"])

    def allocate(total: int) -> dict[str, int]:
        base, remainder = divmod(total, len(SAGE_DOMAINS))
        counts = {domain: base for domain in SAGE_DOMAINS}
        for domain in SAGE_DOMAINS[:remainder]:
            counts[domain] += 1
        return counts

    pilot = take(allocate(pilot_size)) if pilot_size else []
    test = take(allocate(test_size))
    return test, pilot


def prepare(
    source_dir: Path,
    public_path: Path,
    gt_path: Path,
    *,
    test_size: int,
    pilot_size: int,
    seed: int,
    pilot_path: Path | None = None,
) -> dict[str, Any]:
    eligible, audit = build_eligible_pool(source_dir)
    test, pilot = stratified_subsample(
        eligible, test_size=test_size, pilot_size=pilot_size, seed=seed
    )

    public = [
        {"task_id": item["task_id"], "domain": item["domain"], "complete_query": item["complete_query"]}
        for item in test
    ]
    gold = [
        {
            "task_id": item["task_id"],
            "domain": item["domain"],
            "gold_paper_id": item["gold_paper_id"],
            "gold_title": item["gold_title"],
        }
        for item in test
    ]

    leaked = [path for record in public for path in _gold_paths(record)]
    if leaked:
        raise AssertionError("gold crossed the candidate boundary: " + ",".join(leaked[:5]))
    for record in public:
        if set(record) != PUBLIC_RECORD_KEYS:
            raise AssertionError(f"candidate record schema drift: {sorted(record)}")
    _write_jsonl(public_path, public)
    _write_jsonl(gt_path, gold)
    if pilot_path is not None and pilot:
        _write_jsonl(
            pilot_path,
            [
                {"task_id": item["task_id"], "domain": item["domain"], "complete_query": item["complete_query"]}
                for item in pilot
            ],
        )

    subsample_ids = [item["task_id"] for item in test]
    manifest = {
        "schema_version": "orion.p2.sage-shortform-split.v1",
        "upstream": SAGE_UPSTREAM,
        "pinned_upstream_commit": PINNED_SAGE_COMMIT,
        "upstream_licence_at_pinned_commit": "ABSENT",
        "redistribution": "BLOCKED_NOT_VENDORED",
        "authority": "DECLARED_DEVIATION_NEVER_OFFICIAL",
        "official_scorer_available": False,
        "official_retrieval_corpus_available": False,
        "pool_audit": audit,
        "subsample": {
            "seed": seed,
            "stratified_by": "domain",
            "test_tasks": len(test),
            "pilot_tasks": len(pilot),
            "pilot_excluded_from_test": True,
            "per_domain_test": {
                domain: sum(1 for item in test if item["domain"] == domain) for domain in SAGE_DOMAINS
            },
            "task_ids_sha256": _sha256_bytes("\n".join(subsample_ids).encode("utf-8")),
            "task_ids": subsample_ids,
            "pilot_task_ids": [item["task_id"] for item in pilot],
        },
        "precision": achieved_precision(len(test)),
        "contamination": contamination_report(test),
        "normalisation": {
            "strict_transforms": list(STRICT_TRANSFORMS),
            "relaxed_transforms": list(RELAXED_TRANSFORMS),
            "collisions": normalisation_collisions(test),
        },
        "custody": {
            "gold_visible_to_candidate": False,
            "candidate_record_keys": sorted(PUBLIC_RECORD_KEYS),
            "gold_key_paths_in_candidate_file": leaked,
            "public_sha256": _sha256(public_path),
            "gold_sha256": _sha256(gt_path),
        },
    }
    return manifest


# --------------------------------------------------------------------------
# Transport. Typed outcomes keep three states apart that a bare exception
# would merge: a failed request, a successful request with no results, and a
# provider that was never reachable.
# --------------------------------------------------------------------------
class SageFetchStatus(str, Enum):
    OK = "OK"
    EMPTY = "EMPTY"
    RATE_LIMITED = "RATE_LIMITED"
    TRANSPORT_ERROR = "TRANSPORT_ERROR"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    SERVICE_ERROR = "SERVICE_ERROR"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class RawResponse:
    status: int
    body: str
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class BackendResult:
    backend: str
    status: SageFetchStatus
    titles: tuple[str, ...]
    note: str = ""

    @property
    def request_was_issued(self) -> bool:
        return self.status is not SageFetchStatus.UNAVAILABLE


USER_AGENT = "ORION-P2-SAGE/0.1 (+https://github.com/SzeChunYiu/ORION; mailto:sze-chun.yiu@fysik.su.se)"
CONTACT_EMAIL = "sze-chun.yiu@fysik.su.se"

# OpenAIRE and DBLP publish no per-second figure that this audit could verify,
# so they follow the europepmc precedent already in rate.py: ASSUMED, stated as
# assumed, and conservative -- the cost of being wrong is an IP block.
SAGE_PROVIDER_BUDGETS: dict[str, ProviderBudget] = {
    **PROVIDER_BUDGETS,
    "openaire": ProviderBudget(
        provider="openaire",
        min_interval_seconds=1.0,
        max_concurrent=1,
        basis=BudgetBasis.ASSUMED,
        citation=(
            "OpenAIRE publishes no explicit per-second limit for the legacy search API; "
            "1/s assumed conservatively because an unstated limit is not an absent one"
        ),
    ),
    "dblp": ProviderBudget(
        provider="dblp",
        min_interval_seconds=1.5,
        max_concurrent=1,
        basis=BudgetBasis.ASSUMED,
        citation=(
            "DBLP publishes no numeric rate limit and asks for considerate use, returning 429 "
            "under bursts; 1.5s assumed conservatively"
        ),
    ),
}

BACKEND_PROVIDER = {
    "openaire": "openaire",
    "dblp": "dblp",
    "crossref": "crossref_list",
}


def _http_get(url: str, *, timeout: float = 45.0) -> RawResponse:
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return RawResponse(
                status=int(response.status),
                body=response.read().decode("utf-8", errors="replace"),
                headers={key: value for key, value in response.headers.items()},
            )
    except urllib.error.HTTPError as error:
        return RawResponse(
            status=int(error.code),
            body=error.read().decode("utf-8", errors="replace"),
            headers={key: value for key, value in (error.headers or {}).items()},
        )
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return RawResponse(status=0, body=f"{type(error).__name__}: {error}", headers={})


def _classify(response: RawResponse) -> SageFetchStatus | None:
    if response.status == 0:
        return SageFetchStatus.TRANSPORT_ERROR
    if response.status == 429:
        return SageFetchStatus.RATE_LIMITED
    if response.status >= 500:
        return SageFetchStatus.SERVICE_ERROR
    if response.status >= 400:
        return SageFetchStatus.SERVICE_ERROR
    return None


def _openaire_titles(payload: Any) -> tuple[str, ...]:
    results = payload["response"]["results"]
    if not results:
        return ()
    entries = results.get("result") or []
    if isinstance(entries, dict):
        entries = [entries]
    titles: list[str] = []
    for entry in entries:
        result = entry["metadata"]["oaf:entity"]["oaf:result"]
        value = result.get("title")
        if isinstance(value, list):
            candidates = value
        else:
            candidates = [value]
        for candidate in candidates:
            if isinstance(candidate, dict):
                text = candidate.get("$")
            else:
                text = candidate
            if isinstance(text, str) and text.strip():
                titles.append(text.strip())
                break
    return tuple(titles)


def _dblp_titles(payload: Any) -> tuple[str, ...]:
    hits = payload["result"]["hits"]
    entries = hits.get("hit") or []
    if isinstance(entries, dict):
        entries = [entries]
    titles: list[str] = []
    for entry in entries:
        text = entry.get("info", {}).get("title")
        if isinstance(text, str) and text.strip():
            titles.append(text.strip())
    return tuple(titles)


def _crossref_titles(payload: Any) -> tuple[str, ...]:
    titles: list[str] = []
    for item in payload["message"].get("items") or []:
        value = item.get("title") or []
        if isinstance(value, str):
            value = [value]
        for text in value:
            if isinstance(text, str) and text.strip():
                titles.append(text.strip())
                break
    return tuple(titles)


def fetch_backend(
    backend: str,
    query: str,
    *,
    transport: Callable[[str], RawResponse],
    max_results: int,
) -> BackendResult:
    encoded = urllib.parse.quote(query)
    if backend == "openaire":
        url = f"https://api.openaire.eu/search/publications?keywords={encoded}&format=json&size={max_results}"
        parser = _openaire_titles
    elif backend == "dblp":
        url = f"https://dblp.org/search/publ/api?q={encoded}&format=json&h={max_results}"
        parser = _dblp_titles
    elif backend == "crossref":
        url = (
            f"https://api.crossref.org/works?query.bibliographic={encoded}"
            f"&rows={max_results}&mailto={CONTACT_EMAIL}&select=title,DOI"
        )
        parser = _crossref_titles
    else:
        raise ValueError(f"unknown backend '{backend}'")

    response = transport(url)
    failure = _classify(response)
    if failure is not None:
        return BackendResult(backend, failure, (), note=f"http_{response.status}")
    try:
        payload = json.loads(response.body)
        titles = parser(payload)
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as error:
        return BackendResult(
            backend, SageFetchStatus.MALFORMED_RESPONSE, (), note=f"{type(error).__name__}: {error}"
        )
    if not titles:
        return BackendResult(backend, SageFetchStatus.EMPTY, (), note="zero_results")
    return BackendResult(backend, SageFetchStatus.OK, titles[:max_results])


# --------------------------------------------------------------------------
# Query derivation. Three derivations drawing on genuinely different parts of
# the query: the target's own described content, its bibliographic shape, and
# the citation neighbourhood it sits in. Independence is constructed here and
# then checked by assess_pair rather than asserted.
# --------------------------------------------------------------------------
BOILERPLATE = re.compile(
    r"find me (?:the|a) paper(?: that)?(?: match(?:es)?)?(?: this)?(?: requirement)?\.?",
    re.IGNORECASE,
)
DOUBLE_QUOTED = re.compile(r"[\"“]([^\"“”]{8,300})[\"”]")
# The opening quote must not follow a letter, or the apostrophe in "Alzheimer's"
# opens a span that runs to the next quote and captures the surrounding prose
# ("The title ends with") as though it were the title hint.
SINGLE_QUOTED = re.compile(r"(?<![A-Za-z])['‘]([^'‘’\n]{2,60})['’]")
TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9-]{2,}")
BOILERPLATE_PHRASE = re.compile(
    r"\b(?:title (?:ends|begins|starts)|the paper|this paper|requirement|words in the)\b",
    re.IGNORECASE,
)
YEAR = re.compile(r"\b(19|20)\d{2}\b")
# The character class excludes '.' so the capture stops at the sentence
# boundary. With '.' allowed it ran past the venue and swallowed the next
# sentence, sending "the Journal of Neuroinflammation The title ends with" as
# though the instruction prose were part of the venue name.
VENUE_HINT = re.compile(
    r"(?:published in|appeared in|presented at|in)\s+((?:the\s+)?[A-Z][A-Za-z&\- ]{6,90})"
)

DERIVATION_STOPWORDS = frozenset(
    """
    about above after against all also among and another any are because been before being
    below between both but came can cite cited cites come could does each else exactly find
    first following for from has have here how into its itself key largely largest like
    made main many may more most much must never next not now number observed one only order
    other our out over own paper papers per points published requirement same share shares
    shown shows side smaller some specifically still such than that the their them then there
    these they this those through thus title titles total under until using very was were
    what when where which while who whose with within without word words would year years
    both consistent related source used uses use both figure table visualization panel axis
    left right lower higher larger between total exactly appeared presented written authors
    """.split()
)


def _strip_boilerplate(query: str) -> str:
    return BOILERPLATE.sub(" ", query)


def _salient_tokens(text: str, *, count: int, longest_first: bool = False) -> list[str]:
    scored: list[tuple[int, int, str]] = []
    seen: set[str] = set()
    for position, raw in enumerate(TOKEN.findall(text)):
        token = raw.lower().strip("-")
        if token in DERIVATION_STOPWORDS or token in seen or len(token) < 4 or token.isdigit():
            continue
        seen.add(token)
        score = len(token)
        if "-" in raw:
            score += 3
        if raw.isupper() and len(raw) >= 3:
            score += 4
        if not longest_first:
            score += max(0, 6 - position // 10)
        scored.append((score, -position, token))
    scored.sort(reverse=True)
    return [token for _, _, token in scored[:count]]


# Four terms, fixed by the declared pilot rather than chosen for taste.
# OpenAIRE conjoins keyword terms, so recall collapses as terms are added: the
# pilot measured 16871 / 407 / 18 / 1 / 0 results at 2 / 3 / 4 / 5 / 8 terms for
# one probe. Four is the last count that is discriminating without being empty.
# The same string goes to every backend, so both systems receive identical
# derivations and the contrast stays a contrast of backend allocation.
CONTENT_TERM_COUNT = 4


def derive_content(query: str) -> str:
    """CURRENT_VOCABULARY: what the target itself is described as doing.

    Double-quoted spans are removed first: they are the titles of OTHER papers
    the target co-cites, and searching them retrieves those papers instead.
    """

    text = DOUBLE_QUOTED.sub(" ", _strip_boilerplate(query))
    terms = _salient_tokens(text, count=CONTENT_TERM_COUNT)
    if len(terms) < 2:
        raise ValueError("could not derive two content terms from the public query")
    return " ".join(terms)


def derive_bibliographic(query: str) -> str:
    """LEXICAL_VARIANT: venue, year and the title-shape hint.

    Signal of a different kind from the content route: metadata constraints the
    query states explicitly rather than topical vocabulary.
    """

    text = _strip_boilerplate(query)
    parts: list[str] = []
    for hint in SINGLE_QUOTED.findall(text):
        cleaned = hint.strip().strip(".,;:")
        # A hint that is itself instruction prose is a mis-capture, not a title.
        if cleaned and not cleaned.isdigit() and not BOILERPLATE_PHRASE.search(cleaned):
            parts.append(cleaned)
    venue = VENUE_HINT.search(text)
    if venue:
        parts.append(" ".join(venue.group(1).split()[:8]))
    year = YEAR.search(text)
    if year:
        parts.append(year.group(0))
    parts.extend(_salient_tokens(DOUBLE_QUOTED.sub(" ", text), count=3, longest_first=True))
    derived = " ".join(dict.fromkeys(" ".join(parts).split()))
    if not derived.strip():
        raise ValueError("could not derive a bibliographic probe from the public query")
    return derived


def derive_citation_neighbourhood(query: str) -> str:
    """CITATION_NEIGHBORHOOD: the co-cited titles the query names verbatim.

    A distinct information source -- the citation graph around the target --
    and the route least likely to return the target directly. Its low direct
    yield is a finding about the route, not a defect to tune away.
    """

    quoted = [text.strip() for text in DOUBLE_QUOTED.findall(query) if text.strip()]
    if quoted:
        longest = max(quoted, key=len)
        return " ".join(longest.split()[:16])
    return " ".join(_salient_tokens(_strip_boilerplate(query), count=6, longest_first=True))


@dataclass(frozen=True)
class Derivation:
    derivation_id: str
    route_kind: SearchRouteKind
    derive: Callable[[str], str]


DERIVATIONS = (
    Derivation("content_vocabulary", SearchRouteKind.CURRENT_VOCABULARY, derive_content),
    Derivation("bibliographic_shape", SearchRouteKind.LEXICAL_VARIANT, derive_bibliographic),
    Derivation("citation_neighbourhood", SearchRouteKind.CITATION_NEIGHBORHOOD, derive_citation_neighbourhood),
)

# Both systems use the same three derivations. Only the backend allocation
# differs, so the contrast isolates backend diversity plus route control rather
# than confounding it with a weaker query strategy -- the frozen plan is
# explicit that this family exists to run a real lexical baseline, not a straw
# man.
SINGLE_BACKEND = "crossref"
MULTIROUTE_BACKENDS = ("openaire", "dblp", "crossref")

ROUTE_POLICY = FrozenRouteControlPolicy(
    policy_id="sage_shortform_route_control_v1",
    reformulate_after_zero_novelty=1,
    switch_after_zero_novelty=2,
)


@dataclass
class SystemSpec:
    system_id: str
    backends: tuple[str, ...]
    role: str
    frozen_baseline: bool
    gate_id: str | None = None

    def backend_for(self, index: int) -> str:
        return self.backends[index % len(self.backends)]


SYSTEMS = (
    SystemSpec(
        system_id="sage_single_backend",
        backends=(SINGLE_BACKEND,),
        role="matched_budget_internal_contrast_lexical",
        frozen_baseline=False,
        gate_id="sage_lexical_gate_INFORMS_ONLY",
    ),
    SystemSpec(
        system_id="sage_governed_multiroute",
        backends=MULTIROUTE_BACKENDS,
        role="system_under_test",
        frozen_baseline=False,
    ),
)


def run_task(
    spec: SystemSpec,
    task: dict[str, Any],
    *,
    transport: Callable[[str], RawResponse],
    gate: RateGate,
    sleeper: Callable[[float], None],
    budget: int,
    max_results: int,
) -> dict[str, Any]:
    """One task for one system, under the shared per-task request budget."""

    query = task["complete_query"]
    seen_digests: set[str] = set()
    candidates: list[dict[str, str]] = []
    attempts: list[dict[str, Any]] = []
    captures: list[RouteCapture] = []
    requests_issued = 0
    unavailable: list[dict[str, str]] = []
    route_states: dict[str, RouteControlState] = {}

    for index in range(budget):
        derivation = DERIVATIONS[index % len(DERIVATIONS)]
        backend = spec.backend_for(index)
        route_id = f"{spec.system_id}:{derivation.derivation_id}"
        try:
            derived = derivation.derive(query)
        except ValueError as error:
            attempts.append(
                {
                    "attempt_index": index,
                    "route_id": route_id,
                    "route_kind": derivation.route_kind.value,
                    "derivation_id": derivation.derivation_id,
                    "backend": backend,
                    "status": SageFetchStatus.MALFORMED_RESPONSE.value,
                    "note": f"derivation_failed: {error}",
                    "requested": False,
                    "novel_digests": 0,
                    "retrieved_digests": 0,
                }
            )
            continue

        state = route_states.get(route_id) or RouteControlState(
            route_id=route_id,
            route_kind=derivation.route_kind,
            attempts=(),
            budget_units=float(budget),
            alternative_route_kinds=tuple(
                other.route_kind for other in DERIVATIONS if other.route_kind is not derivation.route_kind
            ),
        )
        decision = decide_route(state, ROUTE_POLICY)

        wait = gate.wait_seconds(BACKEND_PROVIDER[backend])
        if wait > 0:
            sleeper(wait)
        result = fetch_backend(backend, derived, transport=transport, max_results=max_results)
        gate.record_request(BACKEND_PROVIDER[backend])
        if result.request_was_issued:
            requests_issued += 1
        else:
            unavailable.append({"backend": backend, "reason": result.note})

        retrieved = tuple(dict.fromkeys(title_digest(title) for title in result.titles))
        novel = tuple(digest for digest in retrieved if digest not in seen_digests)
        for title in result.titles:
            digest = title_digest(title)
            if digest in seen_digests:
                continue
            seen_digests.add(digest)
            candidates.append({"title": title, "content_digest": digest, "backend": backend})

        failure_signatures: tuple[str, ...] = ()
        if result.status not in (SageFetchStatus.OK, SageFetchStatus.EMPTY):
            failure_signatures = (f"{backend}:{result.status.value}",)
        route_states[route_id] = RouteControlState(
            route_id=state.route_id,
            route_kind=state.route_kind,
            attempts=state.attempts
            + (
                RouteAttempt(
                    attempt_id=f"{route_id}:{index}",
                    query_id=f"{task['task_id']}:{derivation.derivation_id}",
                    retrieved_digests=retrieved,
                    novel_digests=novel,
                    cost_units=1.0,
                    execution_failure_signatures=failure_signatures,
                ),
            ),
            budget_units=state.budget_units,
            alternative_route_kinds=state.alternative_route_kinds,
        )
        captures.append(
            RouteCapture(
                route_kind=derivation.route_kind,
                backend=backend,
                query_derivation=derivation.derivation_id,
                captured=frozenset(retrieved),
            )
        )
        attempts.append(
            {
                "attempt_index": index,
                "route_id": route_id,
                "route_kind": derivation.route_kind.value,
                "derivation_id": derivation.derivation_id,
                "backend": backend,
                "derived_query": derived[:240],
                "status": result.status.value,
                "note": result.note,
                "requested": True,
                "retrieved_digests": len(retrieved),
                "novel_digests": len(novel),
                "consecutive_zero_novelty_before": state.consecutive_zero_novelty,
                "route_control_action": decision.action.value,
                "route_control_reasons": list(decision.reasons),
                "route_certifies_task_saturation": decision.certifies_task_saturation,
            }
        )

    independence = [
        {
            "left": pair.left.value,
            "right": pair.right.value,
            "verdict": pair.verdict.value,
            "overlap": pair.overlap,
            "independent": pair.independent,
        }
        for index, left in enumerate(captures)
        for right in captures[index + 1 :]
        for pair in (assess_pair(left, right),)
    ]
    return {
        "task_id": task["task_id"],
        "domain": task["domain"],
        "system_id": spec.system_id,
        "per_task_request_budget": budget,
        "provider_requests_issued": requests_issued,
        "candidate_titles": [item["title"] for item in candidates],
        "candidate_digests": [item["content_digest"] for item in candidates],
        "candidate_backends": [item["backend"] for item in candidates],
        # Which backend supplied rank 1. hit@1 is sensitive to this and the two
        # systems differ in it for reasons unrelated to backend diversity.
        "first_candidate_backend": candidates[0]["backend"] if candidates else None,
        "candidate_count": len(candidates),
        "attempts": attempts,
        "route_independence": independence,
        "backends_unavailable": unavailable,
        "status_counts": _count([item["status"] for item in attempts]),
    }


def _count(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def _candidate_row(item: dict[str, Any]) -> str:
    return json.dumps(
        {
            "task_id": item["task_id"],
            "domain": item["domain"],
            "system_id": item["system_id"],
            "candidate_titles": item["candidate_titles"],
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def _trace_row(item: dict[str, Any]) -> str:
    return json.dumps(
        {
            "task_id": item["task_id"],
            "system_id": item["system_id"],
            "provider_requests_issued": item["provider_requests_issued"],
            "candidate_count": item["candidate_count"],
            "status_counts": item["status_counts"],
            "first_candidate_backend": item["first_candidate_backend"],
            "route_independence_verdicts": _count(
                [pair["verdict"] for pair in item["route_independence"]]
            ),
            "attempts": [
                {
                    "attempt_index": attempt["attempt_index"],
                    "backend": attempt["backend"],
                    "derivation_id": attempt["derivation_id"],
                    "route_kind": attempt["route_kind"],
                    "status": attempt["status"],
                    "retrieved_digests": attempt["retrieved_digests"],
                    "novel_digests": attempt["novel_digests"],
                    "consecutive_zero_novelty_before": attempt.get(
                        "consecutive_zero_novelty_before"
                    ),
                    "route_control_action": attempt.get("route_control_action"),
                }
                for attempt in item["attempts"]
            ],
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def assert_budget_parity(per_system: dict[str, Any]) -> dict[str, Any]:
    """Refuse to report a family whose systems ran under different caps.

    The frozen policy calls such a family INVALID, so this raises rather than
    recording a mismatch and leaving a reader to notice it.
    """

    if not per_system:
        raise ValueError("budget parity is undefined with no systems")
    caps = {name: value["per_task_cap_from_frozen_ladder"] for name, value in per_system.items()}
    budgets = {name: value["per_task_request_budget"] for name, value in per_system.items()}
    if len(set(caps.values())) != 1 or len(set(budgets.values())) != 1:
        raise AssertionError(
            "matched-budget policy violated: a family in which any system's cap differs from "
            f"another's is INVALID and cannot be reported (caps={caps}, budgets={budgets})"
        )
    return {
        "caps": caps,
        "budgets": budgets,
        "parity_holds": True,
        "capped_resource": "query_count",
        "policy": "a family in which any system's cap differs from another's is INVALID",
    }


def run_systems(
    public_path: Path,
    output_dir: Path,
    *,
    budget: int,
    max_results: int,
    limit: int | None = None,
    transport: Callable[[str], RawResponse] | None = None,
    clock: Callable[[], float] | None = None,
    sleeper: Callable[[float], None] | None = None,
    progress_every: int = 25,
) -> dict[str, Any]:
    tasks = _jsonl(public_path)
    for record in tasks:
        leaked = _gold_paths(record)
        if leaked:
            raise AssertionError("candidate input carries gold: " + ",".join(leaked))
        if set(record) != PUBLIC_RECORD_KEYS:
            raise AssertionError(f"candidate input schema drift: {sorted(record)}")
    if limit is not None:
        tasks = tasks[:limit]
    if not tasks:
        raise ValueError("no candidate tasks to run")

    cap = next((rung for rung in FROZEN_QUERY_COUNT_LADDER if rung >= budget), None)
    if cap is None:
        raise ValueError(
            f"per-task budget {budget} exceeds the frozen query_count ladder ceiling "
            f"{FROZEN_QUERY_COUNT_LADDER[-1]}"
        )

    transport = transport or _http_get
    clock = clock or time.monotonic
    sleeper = sleeper or time.sleep
    gate = RateGate(clock, budgets=SAGE_PROVIDER_BUDGETS)

    # Systems are interleaved per task, not run one lane after the other. Two
    # reasons, both learned the hard way on this family: sequential lanes mean an
    # interruption leaves one system complete and the other empty, which is no
    # paired comparison at all, whereas interleaving leaves both systems complete
    # over the tasks that finished and the achieved N can be reported honestly.
    # It is also faster, because one system's rate-gate wait on a provider is
    # spent issuing the other system's request to a different provider.
    output_dir.mkdir(parents=True, exist_ok=True)
    collected: dict[str, list[dict[str, Any]]] = {spec.system_id: [] for spec in SYSTEMS}
    handles: dict[str, tuple[Any, Any]] = {}
    try:
        for spec in SYSTEMS:
            handles[spec.system_id] = (
                (output_dir / f"candidates_{spec.system_id}.jsonl").open("w", encoding="utf-8"),
                (output_dir / f"trace_{spec.system_id}.jsonl").open("w", encoding="utf-8"),
            )
        for position, task in enumerate(tasks, 1):
            for spec in SYSTEMS:
                item = run_task(
                    spec,
                    task,
                    transport=transport,
                    gate=gate,
                    sleeper=sleeper,
                    budget=budget,
                    max_results=max_results,
                )
                collected[spec.system_id].append(item)
                candidate_handle, trace_handle = handles[spec.system_id]
                candidate_handle.write(_candidate_row(item) + "\n")
                trace_handle.write(_trace_row(item) + "\n")
                candidate_handle.flush()
                trace_handle.flush()
            if progress_every and (position % progress_every == 0 or position == len(tasks)):
                print(f"SAGE_RUN paired {position}/{len(tasks)}", flush=True)
    finally:
        for candidate_handle, trace_handle in handles.values():
            candidate_handle.close()
            trace_handle.close()

    per_system: dict[str, Any] = {}
    for spec in SYSTEMS:
        results = collected[spec.system_id]
        candidate_path = output_dir / f"candidates_{spec.system_id}.jsonl"
        trace_path = output_dir / f"trace_{spec.system_id}.jsonl"
        issued = [item["provider_requests_issued"] for item in results]
        per_system[spec.system_id] = {
            "role": spec.role,
            "is_frozen_baseline": spec.frozen_baseline,
            "gate_id": spec.gate_id,
            "backends": list(spec.backends),
            "per_task_request_budget": budget,
            "per_task_cap_from_frozen_ladder": cap,
            "max_provider_requests_observed": max(issued),
            "total_provider_requests": sum(issued),
            "candidate_path": str(candidate_path),
            "trace_path": str(trace_path),
            "candidate_sha256": _sha256(candidate_path),
            "trace_sha256": _sha256(trace_path),
            "status_counts": _count(
                [attempt["status"] for item in results for attempt in item["attempts"]]
            ),
            "backends_unavailable": sorted(
                {entry["backend"] for item in results for entry in item["backends_unavailable"]}
            ),
            "route_independence_verdicts": _count(
                [pair["verdict"] for item in results for pair in item["route_independence"]]
            ),
            "first_candidate_backend_counts": _count(
                [
                    str(item["first_candidate_backend"])
                    for item in results
                    if item["first_candidate_backend"]
                ]
            ),
            "tasks_with_no_candidate": sum(1 for item in results if not item["candidate_count"]),
        }

    parity = assert_budget_parity(per_system)

    manifest = {
        "schema_version": "orion.p2.sage-shortform-run.v1",
        "upstream": SAGE_UPSTREAM,
        "pinned_upstream_commit": PINNED_SAGE_COMMIT,
        "authority": "DECLARED_DEVIATION_NEVER_OFFICIAL",
        "tasks_attempted": len(tasks),
        "candidate_input_sha256": _sha256(public_path),
        "gold_visible_to_candidate": False,
        "resource_limits": {
            "capped_resource": "query_count",
            "per_task_cap": cap,
            "cap_source": "frozen_ladder_rounded_up_from_declared_pilot_max",
            "identical_for_every_system": True,
            "absolute_ceiling_per_task": FROZEN_QUERY_COUNT_LADDER[-1],
        },
        "budget_parity": parity,
        "max_results_per_request": max_results,
        "provider_budgets": {
            name: {
                "min_interval_seconds": SAGE_PROVIDER_BUDGETS[name].min_interval_seconds,
                "basis": SAGE_PROVIDER_BUDGETS[name].basis.value,
                "citation": SAGE_PROVIDER_BUDGETS[name].citation,
            }
            for name in sorted({BACKEND_PROVIDER[b] for spec in SYSTEMS for b in spec.backends})
        },
        "arxiv_requests_issued": 0,
        "credentials_used": "NONE",
        "systems": per_system,
        "route_control_policy": {
            "policy_id": ROUTE_POLICY.policy_id,
            "reformulate_after_zero_novelty": ROUTE_POLICY.reformulate_after_zero_novelty,
            "switch_after_zero_novelty": ROUTE_POLICY.switch_after_zero_novelty,
            "certifies_task_saturation": False,
        },
    }
    return manifest


# --------------------------------------------------------------------------
# score
# --------------------------------------------------------------------------
def achieved_precision(n: int) -> dict[str, Any]:
    """Achieved tier and half-width for a standalone rate at this N."""

    stats = load_publication_stats()
    if n <= 0:
        return {
            "n": n,
            "achieved_tier": "CANNOT_CHECK",
            "reason": "no scoreable tasks",
            "underpowered": "CANNOT_CHECK",
        }
    half_width = None
    achieved = "BELOW_TIER_D"
    for tier, width, required in PRECISION_TIERS:
        if n >= required:
            achieved = tier
            half_width = width
            break
    # Worst-case half-width actually achieved at this N, from the frozen library.
    low, high = stats.wilson_interval(n // 2, n)
    observed_half_width = (high - low) / 2.0
    return {
        "n": n,
        "achieved_tier": achieved,
        "tier_half_width": half_width,
        "worst_case_half_width_at_this_n": round(observed_half_width, 4),
        "delta_sup": DELTA_SUP,
        "underpowered": observed_half_width > DELTA_SUP,
        "underpowered_label_is_mandatory": True,
        "descriptive_only": n < 97,
        "family_carries_primary": False,
        "family_role": "lexical_baseline_promotion_gate",
        "note": (
            "The frozen plan gives sage_scientific_retrieval no confirmatory primary: achieved "
            "precision is reported and no promotion rests on it. The UNDERPOWERED label is "
            "therefore descriptive here rather than a gate on a primary claim."
        ),
    }


# Ordering-insensitive by construction, so it is the comparison the gate rests
# on. hit@1 depends on which route happened to answer first, which differs
# between a one-backend and a three-backend system for reasons unrelated to
# backend diversity (see ordering_asymmetry in the summary).
GATE_COMPARISON_METRIC = "strict_hit_at_10"


def discriminate(
    candidate_point: float, baseline_point: float, interval: list[float]
) -> dict[str, Any]:
    """Three-state verdict on a paired difference of candidate minus baseline.

    A boolean `candidate >= baseline` is vacuously true when both rates are
    zero, which would report "the baseline at least matches the candidate" for
    a comparison that in fact distinguished nothing. Ordering is only claimed
    where the interval excludes zero.
    """

    low, high = interval[0], interval[1]
    at_floor = candidate_point == 0.0 and baseline_point == 0.0
    if low > 0.0:
        verdict = "CANDIDATE_AHEAD"
    elif high < 0.0:
        verdict = "BASELINE_AHEAD"
    else:
        verdict = "CANNOT_DISCRIMINATE"
    discriminating = verdict != "CANNOT_DISCRIMINATE"
    return {
        "verdict": verdict,
        "discriminating": discriminating,
        "at_floor": at_floor,
        "floor_artifact": at_floor and not discriminating,
        # Claimed only where the data supports an ordering.
        "candidate_at_least_matches_baseline": (
            candidate_point >= baseline_point if discriminating else None
        ),
        "note": (
            "Both systems scored zero, so this comparison distinguishes nothing and the interval "
            "is a floor artifact rather than a tight null."
            if at_floor and not discriminating
            else "Interval contains zero: no ordering is claimed."
            if not discriminating
            else "Interval excludes zero."
        ),
    }


def contrast_orientation(system_ids: set[str]) -> tuple[str, str] | None:
    """Return (candidate, baseline) for the paired difference, or None.

    The orientation is read from the declared roles rather than from sort order.
    Letting alphabetical order decide which system is subtracted from which
    silently sets the sign of every reported effect.
    """

    under_test = [spec.system_id for spec in SYSTEMS if spec.role == "system_under_test"]
    contrast = [spec.system_id for spec in SYSTEMS if spec.role != "system_under_test"]
    if len(under_test) != 1 or len(contrast) != 1:
        return None
    if not {under_test[0], contrast[0]} <= system_ids or len(system_ids) != 2:
        return None
    return under_test[0], contrast[0]


def _hit(candidates: list[str], gold: str, matcher: Callable[[str, str], bool], k: int | None) -> int:
    subset = candidates if k is None else candidates[:k]
    return int(any(matcher(candidate, gold) for candidate in subset))


def gold_rank(candidates: list[str], gold: str, matcher: Callable[[str, str], bool]) -> int | None:
    """One-based rank of the first matching candidate, or None if absent."""

    for position, candidate in enumerate(candidates, 1):
        if matcher(candidate, gold):
            return position
    return None


def score(
    gt_path: Path,
    run_manifest_path: Path,
    candidate_paths: dict[str, Path],
    *,
    rank_cutoffs: tuple[int, ...] = (1, 10, 50),
    per_task_path: Path | None = None,
    split_manifest_path: Path | None = None,
) -> dict[str, Any]:
    stats = load_publication_stats()
    gold_records = {item["task_id"]: item for item in _jsonl(gt_path)}
    run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))

    # Close the chain prepare -> run -> score. Without this a stale run could be
    # scored against a freshly split gold file and nothing would say so.
    chain: dict[str, Any] = {"checked": False}
    if split_manifest_path is not None:
        split_manifest = json.loads(split_manifest_path.read_text(encoding="utf-8"))
        expected = split_manifest["custody"]["public_sha256"]
        observed = run_manifest.get("candidate_input_sha256")
        if expected != observed:
            raise AssertionError(
                "stage hash chain broken: the run consumed a candidate file that is not the one "
                f"this split produced (split={expected}, run={observed})"
            )
        if _sha256(gt_path) != split_manifest["custody"]["gold_sha256"]:
            raise AssertionError("gold file does not match the split manifest that declared it")
        chain = {
            "checked": True,
            "split_public_sha256": expected,
            "run_candidate_input_sha256": observed,
            "gold_sha256_matches_split": True,
        }

    per_system_candidates: dict[str, dict[str, list[str]]] = {}
    for system_id, path in candidate_paths.items():
        per_system_candidates[system_id] = {
            item["task_id"]: list(item.get("candidate_titles") or []) for item in _jsonl(path)
        }

    # Pairwise-complete task set: only tasks with gold and a record from every
    # system may enter a paired comparison.
    task_ids = sorted(
        set(gold_records)
        & set.intersection(*(set(values) for values in per_system_candidates.values()))
    )
    if not task_ids:
        raise ValueError("no task is present in gold and in every system's output")

    metrics: dict[str, Any] = {}
    per_task_scores: dict[str, dict[str, list[float]]] = {}
    for variant, matcher in MATCHERS.items():
        for k in rank_cutoffs:
            metric_id = f"{variant}_hit_at_{k}"
            per_system: dict[str, Any] = {}
            for system_id, candidates in per_system_candidates.items():
                values = [
                    float(_hit(candidates[task_id], gold_records[task_id]["gold_title"], matcher, k))
                    for task_id in task_ids
                ]
                per_task_scores.setdefault(metric_id, {})[system_id] = values
                successes = int(sum(values))
                low, high = stats.wilson_interval(successes, len(values))
                per_system[system_id] = {
                    "point_estimate": round(successes / len(values), 6),
                    "successes": successes,
                    "n": len(values),
                    "interval_95": [round(low, 6), round(high, 6)],
                    "interval_estimator": "wilson_interval",
                    "aggregation_unit": "query",
                }
            paired: dict[str, Any] = {}
            oriented = contrast_orientation(set(per_system))
            if oriented is not None:
                candidate_id, baseline_id = oriented
                point, low, high = stats.paired_bootstrap_difference_ci(
                    per_task_scores[metric_id][candidate_id],
                    per_task_scores[metric_id][baseline_id],
                    resamples=10_000,
                    seed=ANALYSIS_SEED,
                )
                paired = {
                    "contrast": f"{candidate_id}_minus_{baseline_id}",
                    "absolute_effect_size": round(point, 6),
                    "interval_95": [round(low, 6), round(high, 6)],
                    "estimator": "paired_bootstrap_difference_ci",
                    "resamples": 10_000,
                    "analysis_seed": ANALYSIS_SEED,
                    "aggregation_unit": "query",
                    "n": len(task_ids),
                    "excludes_zero": low > 0.0 or high < 0.0,
                    "discrimination": discriminate(
                        per_system[candidate_id]["point_estimate"],
                        per_system[baseline_id]["point_estimate"],
                        [round(low, 6), round(high, 6)],
                    ),
                }
            metrics[metric_id] = {
                "declared_deviation": True,
                "official": False,
                "matcher": variant,
                "matcher_transforms": list(
                    STRICT_TRANSFORMS if variant == "strict" else RELAXED_TRANSFORMS
                ),
                "rank_cutoff": k,
                "per_system": per_system,
                "paired_difference": paired,
            }

    if per_task_path is not None:
        rows: list[dict[str, Any]] = []
        for task_id in task_ids:
            row: dict[str, Any] = {"task_id": task_id, "domain": gold_records[task_id]["domain"]}
            for system_id, candidates in sorted(per_system_candidates.items()):
                for variant, matcher in MATCHERS.items():
                    rank = gold_rank(
                        candidates[task_id], gold_records[task_id]["gold_title"], matcher
                    )
                    row[f"{system_id}.{variant}.gold_rank"] = rank
                row[f"{system_id}.candidates_returned"] = len(candidates[task_id])
            rows.append(row)
        _write_jsonl(per_task_path, rows)

    lexical = "sage_single_backend"
    governed = "sage_governed_multiroute"
    gate_verdict: dict[str, Any] = {
        "gate_id": "sage_lexical_gate",
        "status": "OPEN_NOT_CLOSED",
        "comparison_metric": GATE_COMPARISON_METRIC,
        "predeclared_reading": (
            "The frozen plan says this family exists because a strong in-call lexical baseline is "
            "competitive. If the lexical contrast beats the governed system on a DISCRIMINATING "
            "comparison, that is the gate firing and is reported as such. A comparison whose "
            "interval contains zero fires nothing in either direction."
        ),
        "closes_the_frozen_gate": False,
        "why_not_closed": (
            "The frozen gate is bm25_keyword over SAGE's own 200k corpus. That corpus is "
            "unpublished, so provider-side ranking over OpenAIRE/DBLP/Crossref indices can inform "
            "the gate but cannot close it."
        ),
    }
    gate_metric = metrics.get(GATE_COMPARISON_METRIC, {})
    gate_systems = gate_metric.get("per_system", {})
    gate_paired = gate_metric.get("paired_difference") or {}
    if lexical in gate_systems and governed in gate_systems and gate_paired:
        discrimination = gate_paired["discrimination"]
        fired = discrimination["verdict"] == "BASELINE_AHEAD"
        gate_verdict.update(
            {
                "lexical_point_estimate": gate_systems[lexical]["point_estimate"],
                "governed_point_estimate": gate_systems[governed]["point_estimate"],
                "paired_difference_governed_minus_lexical": gate_paired["absolute_effect_size"],
                "paired_interval_95": gate_paired["interval_95"],
                "discrimination": discrimination,
                "gate_fired": fired if discrimination["discriminating"] else None,
                "gate_informed": discrimination["discriminating"],
                "verdict_text": (
                    "The lexical contrast is ahead on a discriminating comparison: the gate fires."
                    if fired
                    else "The governed system is ahead on a discriminating comparison."
                    if discrimination["discriminating"]
                    else "Neither system is distinguishable at this budget, so this family informs "
                    "the gate in neither direction. Reported as CANNOT_DISCRIMINATE, not as a tie."
                ),
            }
        )

    invalid = {
        "route_stop_false_positive_rate": "CANNOT_CHECK",
        "route_stop_false_negative_rate": "CANNOT_CHECK",
        "premature_task_closure_rate": "CANNOT_CHECK",
        "complete_gold_recall": "CANNOT_CHECK",
        "unique_relevant_per_route": "CANNOT_CHECK",
        "marginal_relevant_gain": "CANNOT_CHECK",
        "screening_recall": "CANNOT_CHECK",
        "precision": "CANNOT_CHECK",
    }
    summary = {
        "schema_version": "orion.p2.sage-shortform-score.v1",
        "benchmark": "SAGE short-form scientific retrieval",
        "upstream": SAGE_UPSTREAM,
        "pinned_upstream_commit": PINNED_SAGE_COMMIT,
        "authority": "DECLARED_DEVIATION_NEVER_OFFICIAL",
        "official_scorer_used": False,
        "official_scorer_exists_publicly": False,
        "family_role": "lexical_baseline_promotion_gate",
        "family_carries_confirmatory_primary": False,
        "tasks_scored": len(task_ids),
        "gold_sha256": _sha256(gt_path),
        "stage_hash_chain": chain,
        "run_manifest_budget_parity": run_manifest.get("budget_parity"),
        "ordering_asymmetry": {
            "affects": [f"{variant}_hit_at_1" for variant in MATCHERS],
            "ordering_insensitive": [
                f"{variant}_hit_at_{k}" for variant in MATCHERS for k in rank_cutoffs if k > 1
            ],
            "explanation": (
                "sage_single_backend takes all three attempts on one backend, so its early "
                "candidates carry that provider's own ranking. sage_governed_multiroute fills its "
                "first slots from whichever route answered first, and its route-1 backend "
                "(OpenAIRE) frequently returns nothing. A hit@1 gap can therefore reflect candidate "
                "ordering rather than backend diversity, so the gate rests on "
                f"{GATE_COMPARISON_METRIC}, which is insensitive to order within the cutoff."
            ),
        },
        "precision": achieved_precision(len(task_ids)),
        "metrics": metrics,
        "lexical_gate": gate_verdict,
        "valid_metrics": sorted(metrics),
        "invalid_metrics_cannot_check": invalid,
        "invalid_metrics_reason": (
            "Bindings B8 (oracle.route_residual_yield) and B10 "
            "(oracle.task_residual_discoverable_within_budget) are defined under a frozen "
            "corpus/index. SAGE's retrieval corpus is unpublished, so no residual-yield oracle "
            "exists and every metric derived from one is CANNOT_CHECK rather than zero."
        ),
        "required_bindings_emitted": required_bindings_status(),
        "statistics_library": str(PUBLICATION_STATS_PATH),
        "statistics_library_reimplemented": False,
    }
    return summary


def required_bindings_status() -> dict[str, Any]:
    """Which frozen required bindings this family can and cannot carry."""

    return {
        "B1_result_record_task_id": "EMITTED",
        "B2_route_trial_attempt_index": "EMITTED",
        "B3_route_trial_consecutive_zero_novelty_before": "EMITTED",
        "B4_captures_merged_source_id": "EMITTED_AS_CONTENT_DIGEST",
        "B5_oracle_gold_items": "EMITTED_SINGLE_TARGET",
        "B6_oracle_gold_set_complete": "DECLARED_TRUE_FOR_TARGETED_IDENTIFICATION",
        "B6_declaration": (
            "Short-form asks for one target paper and upstream ships exactly one gold record per "
            "query, so the denominator is 1 by construction. This is a declared reading of a "
            "targeted-identification task, not an upstream statement."
        ),
        "B7_captures_content_digest": "EMITTED",
        "B8_oracle_route_residual_yield": "CANNOT_CHECK",
        "B9_task_closure_declared": "NOT_APPLICABLE_FIXED_BUDGET_NO_CLOSURE_DECLARATION",
        "B10_task_residual_discoverable_within_budget": "CANNOT_CHECK",
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    prepare_parser = sub.add_parser("prepare", help="split fetched SAGE records; the only gold reader")
    prepare_parser.add_argument("--source-dir", type=Path, required=True)
    prepare_parser.add_argument("--public", type=Path, required=True)
    prepare_parser.add_argument("--gt", type=Path, required=True)
    prepare_parser.add_argument("--pilot", type=Path)
    prepare_parser.add_argument("--manifest", type=Path, required=True)
    prepare_parser.add_argument("--test-size", type=int, default=385)
    prepare_parser.add_argument("--pilot-size", type=int, default=8)
    prepare_parser.add_argument("--seed", type=int, default=ANALYSIS_SEED)

    run_parser = sub.add_parser("run", help="run both systems under an identical budget")
    run_parser.add_argument("--public", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--manifest", type=Path, required=True)
    run_parser.add_argument("--budget", type=int, default=3)
    run_parser.add_argument("--max-results", type=int, default=50)
    run_parser.add_argument("--limit", type=int)

    score_parser = sub.add_parser("score", help="declared scoring; refuses invalid denominators")
    score_parser.add_argument("--gt", type=Path, required=True)
    score_parser.add_argument("--run-manifest", type=Path, required=True)
    score_parser.add_argument("--candidates", type=Path, nargs="+", required=True)
    score_parser.add_argument("--output", type=Path, required=True)
    score_parser.add_argument("--per-task", type=Path)
    score_parser.add_argument("--split-manifest", type=Path)
    score_parser.add_argument("--rank-cutoffs", type=int, nargs="+", default=[1, 10, 50])

    args = parser.parse_args(argv)
    if args.command == "prepare":
        manifest = prepare(
            args.source_dir,
            args.public,
            args.gt,
            test_size=args.test_size,
            pilot_size=args.pilot_size,
            seed=args.seed,
            pilot_path=args.pilot,
        )
        _write_json(args.manifest, manifest)
        print("SAGE_SPLIT=" + json.dumps(manifest["subsample"], sort_keys=True))
        return 0
    if args.command == "run":
        manifest = run_systems(
            args.public,
            args.output_dir,
            budget=args.budget,
            max_results=args.max_results,
            limit=args.limit,
        )
        _write_json(args.manifest, manifest)
        print("SAGE_RUN_MANIFEST=" + json.dumps(manifest["budget_parity"], sort_keys=True))
        return 0
    if args.command == "score":
        candidate_paths: dict[str, Path] = {}
        for path in args.candidates:
            records = _jsonl(path)
            if not records:
                raise ValueError(f"{path}: no candidate records")
            candidate_paths[str(records[0]["system_id"])] = path
        summary = score(
            args.gt,
            args.run_manifest,
            candidate_paths,
            rank_cutoffs=tuple(args.rank_cutoffs),
            per_task_path=args.per_task,
            split_manifest_path=args.split_manifest,
        )
        _write_json(args.output, summary)
        print("SAGE_SCORE=" + json.dumps(summary["metrics"]["strict_hit_at_1"]["per_system"], sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
