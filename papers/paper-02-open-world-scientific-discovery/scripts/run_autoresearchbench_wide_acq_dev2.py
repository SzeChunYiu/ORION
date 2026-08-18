#!/usr/bin/env python3
"""P2 V2 acquisition Dev-2: diversified scorer-native arXiv candidate generation.

Development-only runner over the already-burned 24-task Wide slice frozen in
P2_V2_ACQUISITION_DEV2_FREEZE_2026-08-18.json. Outcomes from this slice can
select a candidate generator for a later fresh-slice freeze, but can never serve
as final V2 confirmation.

Exactly three arXiv requests are spent per non-empty task:
1. FIELD_AWARE_PHRASES -- title/abstract phrase clauses from public text;
2. DIVERSIFIED_OR -- broad OR over high-information public-question anchors;
3. CORE_CONJUNCTION -- recall-first conjunction of two early topical terms, with
   a third only when all three are contiguous in the original public question.

All calls share the arXiv backend. Query-family agreement is a ranking signal
only and is never represented as route independence.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
CMP_PATH = HERE / "run_autoresearchbench_wide_comparison.py"


def _load_cmp():
    spec = importlib.util.spec_from_file_location("orion_p2_wide_cmp", CMP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load matched Wide runner at {CMP_PATH}")
    module = importlib.util.module_from_spec(spec)
    # dataclasses and other runtime type machinery resolve the defining module
    # through sys.modules while the file is executing.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cmp = _load_cmp()
base = cmp.base

SYSTEM_ID = "wide_diversified_arxiv_dev2"
QUERY_FAMILIES = ("FIELD_AWARE_PHRASES", "DIVERSIFIED_OR", "CORE_CONJUNCTION")
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
    """aim aims identify identifies identified investigating investigate investigated
    examining examine examined focus focuses focused focusing literature articles article
    relevant most recent key notable specifically explicit explicitly ask asks question
    questions consider considering considered evidence empirical paper papers study studies
    research works work result results report reports approach approaches method methods
    technique techniques framework frameworks system systems model models dataset datasets
    benchmark benchmarks compare comparison looking find finding including include includes
    propose proposes proposed show shows demonstrated demonstrate using used uses based
    primarily roughly particular""".split()
)


def _eligible_match(match: re.Match[str]) -> bool:
    raw = match.group(0)
    token = raw.lower().strip("-")
    return (
        token not in base.STOPWORDS
        and token not in _EXTRA_GENERIC
        and not token.isdigit()
        and not re.fullmatch(r"(?:19|20)\d{2}", token)
        and len(token) >= 3
    )


def _content_words(question: str) -> list[tuple[int, int, str, str]]:
    return [
        (m.start(), m.end(), m.group(0), m.group(0).lower().strip("-"))
        for m in _WORD.finditer(question)
        if _eligible_match(m)
    ]


def _explicit_year_range(question: str) -> tuple[int, int] | None:
    for pattern in _RANGE_PATTERNS:
        match = pattern.search(question)
        if match:
            lo, hi = sorted((int(match.group(1)), int(match.group(2))))
            if 1990 <= lo <= 2030 and 1990 <= hi <= 2030:
                return lo, hi
    return None


def _with_date(query: str, question: str) -> str:
    years = _explicit_year_range(question)
    if years is None:
        return query
    lo, hi = years
    return f"({query}) AND submittedDate:[{lo}01010000 TO {hi}12312359]"


def _phrase_candidates(question: str) -> list[str]:
    """Return deterministic high-information contiguous 2/3-grams."""
    matches = list(_WORD.finditer(question))
    eligible = [m for m in matches if _eligible_match(m)]
    candidates: list[tuple[int, int, str]] = []
    seen: set[str] = set()
    for n in (3, 2):
        for i in range(len(eligible) - n + 1):
            window = eligible[i : i + n]
            left, right = window[0].start(), window[-1].end()
            segment = question[left:right]
            # If a filtered-out word lies between the eligible terms, this is not
            # a contiguous topical phrase and must not be silently contracted.
            tokens = _WORD.findall(segment)
            if len(tokens) != n:
                continue
            phrase = " ".join(t.lower().strip("-") for t in tokens)
            if phrase in seen:
                continue
            seen.add(phrase)
            score = sum(len(t) for t in tokens)
            score += sum(4 for t in tokens if "-" in t)
            score += sum(3 for t in tokens if t.isupper() and len(t) >= 3)
            score += max(0, 6 - left // 35)
            candidates.append((score, -left, phrase))
    candidates.sort(reverse=True)
    return [phrase for _, _, phrase in candidates[:3]]


def derive_field_aware_phrases(question: str) -> str:
    phrases = _phrase_candidates(question)
    if phrases:
        clauses = [f'(ti:"{phrase}" OR abs:"{phrase}")' for phrase in phrases]
    else:
        anchors = base._salient_tokens(question, count=3)
        if not anchors:
            raise ValueError("could not derive field-aware query")
        clauses = [f"(ti:{token} OR abs:{token})" for token in anchors]
    return _with_date(" OR ".join(clauses), question)


def derive_diversified_or(question: str) -> str:
    anchors = base._salient_tokens(question, count=6)
    if len(anchors) < 2:
        anchors = [row[3] for row in _content_words(question)[:6]]
    if len(anchors) < 2:
        raise ValueError("could not derive diversified OR query")
    return _with_date(" OR ".join(f"all:{token}" for token in anchors[:6]), question)


def _core_terms(question: str) -> list[str]:
    """Two early topical terms; add a third only for a true contiguous 3-gram."""
    rows = _content_words(question)
    distinct: list[tuple[int, int, str]] = []
    seen: set[str] = set()
    for start, end, _raw, token in rows:
        if token in seen:
            continue
        seen.add(token)
        distinct.append((start, end, token))
    if len(distinct) < 2:
        fallback = base._salient_tokens(question, count=2)
        if len(fallback) < 2:
            raise ValueError("could not derive core conjunction query")
        return fallback[:2]

    core = [distinct[0][2], distinct[1][2]]
    if len(distinct) >= 3:
        left, right = distinct[0][0], distinct[2][1]
        if len(_WORD.findall(question[left:right])) == 3:
            core.append(distinct[2][2])
    return core


def derive_core_conjunction(question: str) -> str:
    return _with_date(" AND ".join(f"all:{token}" for token in _core_terms(question)), question)


DERIVERS: tuple[tuple[str, Callable[[str], str]], ...] = (
    (QUERY_FAMILIES[0], derive_field_aware_phrases),
    (QUERY_FAMILIES[1], derive_diversified_or),
    (QUERY_FAMILIES[2], derive_core_conjunction),
)


def _arxiv_fielded_route(query: str, *, clock: Any, max_results: int) -> tuple[str, tuple[str, ...], str]:
    """Execute an already-formed arXiv search_query without adding ``all:``."""
    clock.wait("arxiv", cmp.DECLARED_CONSTANTS["arxiv_min_interval_seconds"])
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
        }
    )
    status, body, note, attempts = cmp._http_get(
        url, timeout=cmp.DECLARED_CONSTANTS["http_timeout_seconds"]
    )
    suffix = f" attempts:{attempts}" if attempts > 1 else ""
    if status != 200 or not body:
        return (
            "UNAVAILABLE" if status in (0, 429, 503) else "ERROR",
            (),
            (note or f"status:{status}") + suffix,
        )
    ids = tuple(dict.fromkeys(base.ARXIV_ID.findall(body.decode("utf-8", "replace"))))
    return "OK", ids, suffix.strip()


def _agreement_first(cap: int, groups: list[tuple[str, ...]], found_by: dict[str, set[str]]) -> list[str]:
    stream = cmp.select_round_robin(cap * 4, groups)
    confirmed = [item for item in stream if len(found_by.get(item, ())) >= 2]
    confirmed_set = set(confirmed)
    remainder = [item for item in stream if item not in confirmed_set]
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
        status, ids, note = _arxiv_fielded_route(query, clock=clock, max_results=max_results)
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
    run.multi_route_confirmed = []
    run.closed_as_complete = False
    return run


def run_dev2(public_path: Path, out_dir: Path, *, max_results: int, subsample: int, seed: int, progress_every: int) -> dict[str, Any]:
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
        run = cmp.TaskRun(task_id=task_id, system_id=SYSTEM_ID) if not question.strip() else run_task(
            task_id, question, clock=clock, max_results=max_results
        )
        outputs.append(cmp._scorer_record(question, run))
        traces.append(run.as_json())
        for call in run.calls:
            statuses[call.status] = statuses.get(call.status, 0) + 1
        if progress_every and index % progress_every == 0:
            print(f"ARB_WIDE_DEV2 {index}/{len(tasks)} statuses={json.dumps(statuses, sort_keys=True)}", flush=True)

    candidate_path = out_dir / f"candidate_{SYSTEM_ID}.jsonl"
    trace_path = out_dir / f"trace_{SYSTEM_ID}.json"
    base._write_jsonl(candidate_path, outputs)
    trace_path.write_text(json.dumps({"system_id": SYSTEM_ID, "tasks": traces}, sort_keys=True, indent=1) + "\n", encoding="utf-8")
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
        "mean_candidates_returned": round(sum(len(item["candidate_arxiv_ids"]) for item in traces) / len(tasks), 4) if tasks else 0.0,
        "candidate_path": candidate_path.name,
        "candidate_sha256": base._sha256(candidate_path),
        "trace_path": trace_path.name,
        "trace_sha256": base._sha256(trace_path),
    }
    (out_dir / "DEV2_RUN_MANIFEST.json").write_text(json.dumps(manifest, sort_keys=True, indent=1) + "\n", encoding="utf-8")
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
