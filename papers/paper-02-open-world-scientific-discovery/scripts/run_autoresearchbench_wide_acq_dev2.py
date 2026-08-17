#!/usr/bin/env python3
"""P2 V2 acquisition Dev-2: diversified scorer-native arXiv candidate generation.

This is a DEVELOPMENT-ONLY runner over the already-burned 24-task Wide slice
frozen in P2_V2_ACQUISITION_DEV2_FREEZE_2026-08-18.json. It may improve the
candidate generator selected for a later fresh-slice freeze, but its outcomes
can never serve as final V2 confirmation.

The system spends exactly three arXiv provider requests per non-empty task:

1. FIELD_AWARE_PHRASES -- title/abstract phrase clauses from public text;
2. DIVERSIFIED_OR -- a broad OR over high-information public-question anchors;
3. CORE_CONJUNCTION -- a compact AND over early topical concepts.

All three calls share one backend. Query-family agreement is therefore only a
ranking signal; it is NEVER represented as route independence.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CMP_PATH = HERE / "run_autoresearchbench_wide_comparison.py"


def _load_cmp():
    spec = importlib.util.spec_from_file_location("orion_p2_wide_cmp", CMP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load matched Wide runner at {CMP_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cmp = _load_cmp()
base = cmp.base

SYSTEM_ID = "wide_diversified_arxiv_dev2"
QUERY_FAMILIES = (
    "FIELD_AWARE_PHRASES",
    "DIVERSIFIED_OR",
    "CORE_CONJUNCTION",
)
PROVIDER_REQUESTS_PER_TASK = 3
MAX_CANDIDATES_RETURNED = 20
DEFAULT_SUBSAMPLE = 24
DEFAULT_SEED = 20260818

_WORD = re.compile(r"[A-Za-z][A-Za-z0-9+]*(?:-[A-Za-z0-9+]+)*")
_RANGE_PATTERNS = (
    re.compile(r"\b(?:between|from)\s+(19\d{2}|20\d{2})\s+(?:and|to|through|-)\s+(19\d{2}|20\d{2})\b", re.I),
    re.compile(r"\b(19\d{2}|20\d{2})\s*[-–—]\s*(19\d{2}|20\d{2})\b"),
)
_EXTRA_GENERIC = frozenset(
    """
    aim aims identify identifies identified investigating investigate investigated
    examining examine examined focus focuses focused focusing literature articles
    article relevant most recent recent key notable specifically explicit explicitly
    ask asks question questions consider considering considered evidence empirical
    paper papers study studies research works work result results report reports
    approach approaches method methods technique techniques framework frameworks
    system systems model models dataset datasets benchmark benchmarks compare comparison
    looking find finding including include includes propose proposes proposed show shows
    demonstrated demonstrate using used uses based primarily roughly particular
    """.split()
)


def _content_words(question: str) -> list[tuple[int, str, str]]:
    """Ordered public-question words as (position, raw, normalized)."""

    rows: list[tuple[int, str, str]] = []
    for match in _WORD.finditer(question):
        raw = match.group(0)
        token = raw.lower().strip("-")
        if token in base.STOPWORDS or token in _EXTRA_GENERIC:
            continue
        if token.isdigit() or re.fullmatch(r"(?:19|20)\d{2}", token):
            continue
        if len(token) < 3:
            continue
        rows.append((match.start(), raw, token))
    return rows


def _explicit_year_range(question: str) -> tuple[int, int] | None:
    """Return only an explicit public-text year RANGE, never inferred gold time."""

    for pattern in _RANGE_PATTERNS:
        match = pattern.search(question)
        if match:
            lo, hi = sorted((int(match.group(1)), int(match.group(2))))
            if 1990 <= lo <= 2030 and 1990 <= hi <= 2030:
                return lo, hi
    return None


def _date_clause(question: str) -> str:
    years = _explicit_year_range(question)
    if years is None:
        return ""
    lo, hi = years
    return f"submittedDate:[{lo}01010000 TO {hi}12312359]"


def _with_date(query: str, question: str) -> str:
    date = _date_clause(question)
    return f"({query}) AND {date}" if date else query


def _phrase_candidates(question: str) -> list[str]:
    """High-information contiguous public-text 2/3-grams, deterministic."""

    matches = list(_WORD.finditer(question))
    content = {
        match.start(): (
            match.group(0),
            match.group(0).lower().strip("-"),
        )
        for match in matches
        if match.group(0).lower().strip("-") not in base.STOPWORDS
        and match.group(0).lower().strip("-") not in _EXTRA_GENERIC
        and not re.fullmatch(r"(?:19|20)\d{2}", match.group(0))
        and len(match.group(0).strip("-")) >= 3
    }
    ordered = [match for match in matches if match.start() in content]
    candidates: list[tuple[int, int, str]] = []
    seen: set[str] = set()

    for n in (3, 2):
        for index in range(0, max(0, len(ordered) - n + 1)):
            window = ordered[index : index + n]
            # Require actual contiguity in the original question: punctuation or
            # whitespace is fine; an omitted generic/content word is not.
            left = window[0].start()
            right = window[-1].end()
            raw_segment = question[left:right]
            segment_tokens = _WORD.findall(raw_segment)
            if len(segment_tokens) != n:
                continue
            phrase = " ".join(item.lower().strip("-") for item in segment_tokens)
            if phrase in seen:
                continue
            seen.add(phrase)
            score = sum(len(item) for item in segment_tokens)
            score += sum(4 for item in segment_tokens if "-" in item)
            score += sum(3 for item in segment_tokens if item.isupper() and len(item) >= 3)
            # A light early-position prior keeps the task's central noun phrase
            # ahead of later examples without overwhelming technical specificity.
            score += max(0, 6 - left // 35)
            candidates.append((score, -left, phrase))

    candidates.sort(reverse=True)
    return [phrase for _, _, phrase in candidates[:3]]


def derive_field_aware_phrases(question: str) -> str:
    phrases = _phrase_candidates(question)
    if not phrases:
        anchors = base._salient_tokens(question, count=3)
        if not anchors:
            raise ValueError("could not derive field-aware query")
        clauses = [f"(ti:{token} OR abs:{token})" for token in anchors]
    else:
        clauses = [f'(ti:"{phrase}" OR abs:"{phrase}")' for phrase in phrases]
    return _with_date(" OR ".join(clauses), question)


def derive_diversified_or(question: str) -> str:
    anchors = base._salient_tokens(question, count=6)
    if len(anchors) < 2:
        anchors = [token for _, _, token in _content_words(question)[:6]]
    if len(anchors) < 2:
        raise ValueError("could not derive diversified OR query")
    return _with_date(" OR ".join(f"all:{token}" for token in anchors[:6]), question)


def derive_core_conjunction(question: str) -> str:
    ordered = [token for _, _, token in _content_words(question)]
    distinct: list[str] = []
    seen: set[str] = set()
    for token in ordered:
        if token in seen:
            continue
        seen.add(token)
        distinct.append(token)
    if len(distinct) < 2:
        distinct = base._salient_tokens(question, count=3)
    if len(distinct) < 2:
        raise ValueError("could not derive core conjunction query")
    # Two terms is intentionally recall-first; a third term is used only when it
    # immediately belongs to the same early topical phrase.
    core = distinct[:3] if len(distinct) >= 3 else distinct[:2]
    return _with_date(" AND ".join(f"all:{token}" for token in core), question)


DERIVERS = (
    (QUERY_FAMILIES[0], derive_field_aware_phrases),
    (QUERY_FAMILIES[1], derive_diversified_or),
    (QUERY_FAMILIES[2], derive_core_conjunction),
)


def _agreement_first(
    cap: int,
    groups: list[tuple[str, ...]],
    found_by: dict[str, set[str]],
) -> list[str]:
    """Query-family agreement first, then deterministic round-robin.

    This function intentionally does NOT use cmp.select_agreement_first because
    that helper documents cross-backend agreement. Here all families share
    arXiv, so agreement is ranking evidence only, never independence evidence.
    """

    stream = cmp.select_round_robin(cap * 4, groups)
    confirmed = [item for item in stream if len(found_by.get(item, ())) >= 2]
    remainder = [item for item in stream if item not in set(confirmed)]
    return (confirmed + remainder)[:cap]


def run_task(task_id: str, question: str, *, clock: Any, max_results: int) -> Any:
    run = cmp.TaskRun(task_id=task_id, system_id=SYSTEM_ID)
    budget = cmp.RequestBudget(PROVIDER_REQUESTS_PER_TASK)
    found_by: dict[str, set[str]] = {}

    for family, derive in DERIVERS:
        if budget.remaining <= 0:
            break
        query = derive(question)
        budget.take()
        started = time.monotonic()
        status, ids, note = cmp.arxiv_route(query, clock=clock, max_results=max_results)
        novel = tuple(item for item in ids if item not in found_by)
        for item in ids:
            found_by.setdefault(item, set()).add(family)
        run.calls.append(
            cmp.RouteCall(
                route_id="arxiv-dev2-shared-backend",
                backend="arxiv",
                query_derivation=family,
                query=query,
                status=status,
                returned_ids=ids,
                novel_ids=novel,
                note=note,
                duration_seconds=time.monotonic() - started,
            )
        )
        if status != "OK":
            run.open_obligations.append(f"arxiv-dev2:{family}:{status}:{note}")

    groups = [call.returned_ids for call in run.calls]
    run.candidates = _agreement_first(MAX_CANDIDATES_RETURNED, groups, found_by)
    run.agreement_candidates = list(run.candidates)
    run.multi_route_confirmed = []  # same backend: never route independence
    run.closed_as_complete = False  # acquisition development never certifies closure
    return run


def run_dev2(
    public_path: Path,
    out_dir: Path,
    *,
    max_results: int,
    subsample: int,
    seed: int,
    progress_every: int,
) -> dict[str, Any]:
    tasks = base._jsonl(public_path)
    tasks, selection = cmp.select_subsample(tasks, size=subsample, seed=seed)
    leaked = [path for record in tasks for path in base._hidden_paths(record)]
    if leaked:
        raise AssertionError("public split carries hidden labels: " + ",".join(leaked[:5]))

    out_dir.mkdir(parents=True, exist_ok=True)
    clock = cmp.Clock()
    outputs: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    statuses: dict[str, int] = {}

    for index, task in enumerate(tasks, start=1):
        question = str(task.get("question", "") or "")
        task_id = str(task.get("task_id", index))
        if not question.strip():
            run = cmp.TaskRun(task_id=task_id, system_id=SYSTEM_ID)
        else:
            run = run_task(task_id, question, clock=clock, max_results=max_results)
        outputs.append(cmp._scorer_record(question, run))
        traces.append(run.as_json())
        for call in run.calls:
            statuses[call.status] = statuses.get(call.status, 0) + 1
        if progress_every and index % progress_every == 0:
            print(
                f"ARB_WIDE_DEV2 {index}/{len(tasks)} statuses={json.dumps(statuses, sort_keys=True)}",
                flush=True,
            )

    candidate_path = out_dir / f"candidate_{SYSTEM_ID}.jsonl"
    trace_path = out_dir / f"trace_{SYSTEM_ID}.json"
    base._write_jsonl(candidate_path, outputs)
    trace_path.write_text(
        json.dumps({"system_id": SYSTEM_ID, "tasks": traces}, sort_keys=True, indent=1) + "\n",
        encoding="utf-8",
    )
    total_requests = sum(len(item["calls"]) for item in traces)
    manifest = {
        "schema_version": "orion.p2.autoresearchbench-wide-acquisition-dev2.v1",
        "authority": "DEVELOPMENT_ONLY_NOT_CONFIRMATION",
        "pinned_upstream_commit": base.PINNED_AUTORESEARCHBENCH_COMMIT,
        "public_sha256": base._sha256(public_path),
        "selection": selection,
        "system_id": SYSTEM_ID,
        "shared_backend": "arxiv",
        "query_families": list(QUERY_FAMILIES),
        "query_family_agreement_is_route_independence": False,
        "provider_requests": total_requests,
        "provider_requests_per_task": round(total_requests / len(tasks), 4) if tasks else 0.0,
        "max_candidates_returned": MAX_CANDIDATES_RETURNED,
        "max_results_per_call": max_results,
        "route_status_counts": statuses,
        "tasks_with_open_obligations": sum(1 for item in traces if item["open_obligations"]),
        "tasks_closed_as_complete": sum(1 for item in traces if item["closed_as_complete"]),
        "mean_candidates_returned": (
            round(sum(len(item["candidate_arxiv_ids"]) for item in traces) / len(tasks), 4)
            if tasks else 0.0
        ),
        "candidate_path": candidate_path.name,
        "candidate_sha256": base._sha256(candidate_path),
        "trace_path": trace_path.name,
        "trace_sha256": base._sha256(trace_path),
    }
    (out_dir / "DEV2_RUN_MANIFEST.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=1) + "\n", encoding="utf-8"
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--max-results", type=int, default=20)
    parser.add_argument("--subsample", type=int, default=DEFAULT_SUBSAMPLE)
    parser.add_argument("--subsample-seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--progress-every", type=int, default=4)
    args = parser.parse_args(argv)

    if args.subsample != DEFAULT_SUBSAMPLE or args.subsample_seed != DEFAULT_SEED:
        parser.error("Dev-2 is frozen to n=24 and seed=20260818")
    if args.max_results != 20:
        parser.error("Dev-2 is frozen to max-results=20")

    payload = run_dev2(
        args.public,
        args.out_dir,
        max_results=args.max_results,
        subsample=args.subsample,
        seed=args.subsample_seed,
        progress_every=args.progress_every,
    )
    print("ARB_WIDE_DEV2=" + json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
