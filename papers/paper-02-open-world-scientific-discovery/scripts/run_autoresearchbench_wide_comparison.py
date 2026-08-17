#!/usr/bin/env python3
"""AutoResearchBench Wide: two systems, one matched provider-request budget.

The existing keyless probe established that the official Wide scorer runs
credential-free. It ran one candidate, which measures the benchmark, not the
paper's hypothesis. This script runs **two** systems over the same gold-blind
public tasks under an identical per-task provider-request budget, so the only
thing that differs is how those requests are allocated:

``wide_lexical_arxiv``
    A deliberately competent single-route lexical baseline. It spends its whole
    budget on one backend, reformulating between attempts. This is the SAGE
    promotion gate: if governance cannot beat a well-fed lexical searcher, the
    paper's claim does not survive, and the baseline is built to be hard to beat
    rather than easy.

``wide_governed_multiroute``
    Route governance. The same budget is spread across backends with distinct
    query derivations, re-encounters are deduplicated by identifier identity,
    route control decides when a route has gone flat, and an unavailable backend
    becomes a recorded open obligation rather than a silent zero.

Both return at most ``--max-candidates`` identifiers, because the official metric
is set IoU and an unbounded return would trade precision for recall in a way the
metric — correctly — punishes. Every constant here is declared in
``DECLARED_CONSTANTS`` and none was chosen by looking at a score.

Gold never enters this process: the input is the public split, and the candidate
output is scored afterwards by the pinned upstream evaluator.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

BASE = Path(__file__).with_name("run_autoresearchbench_wide_keyless.py")

#: Every tunable in one place, so a reviewer can check that nothing here was
#: fitted to an outcome. Values are motivated by the budget and the metric, not
#: by any observed score.
DECLARED_CONSTANTS: dict[str, Any] = {
    "provider_requests_per_task": 3,
    "max_candidates_returned": 20,
    "arxiv_min_interval_seconds": 3.0,
    "other_backend_min_interval_seconds": 1.5,
    "switch_on_novel_below": 1,
    "http_timeout_seconds": 30.0,
    "user_agent": "ORION-P2-research/0.1 (+https://github.com/SzeChunYiu/ORION)",
}


def _load_base():
    spec = importlib.util.spec_from_file_location("orion_p2_arb_wide_base", BASE)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError(f"cannot load base module at {BASE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = _load_base()


# ---------------------------------------------------------------------------
# Budget: one accountant, both systems, so neither can win by spending more.
# ---------------------------------------------------------------------------


class BudgetExceeded(RuntimeError):
    """Raised when a system asks for a request its budget cannot cover."""


@dataclass
class RequestBudget:
    limit: int
    spent: int = 0

    def take(self) -> None:
        if self.spent >= self.limit:
            raise BudgetExceeded(f"provider-request budget of {self.limit} is exhausted")
        self.spent += 1

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.spent)


@dataclass
class RouteCall:
    """One provider request, recorded whether or not it returned anything."""

    route_id: str
    backend: str
    query_derivation: str
    query: str
    status: str
    returned_ids: tuple[str, ...] = ()
    novel_ids: tuple[str, ...] = ()
    note: str = ""
    duration_seconds: float = 0.0

    def as_json(self) -> dict[str, Any]:
        return {
            "route_id": self.route_id,
            "backend": self.backend,
            "query_derivation": self.query_derivation,
            "query": self.query,
            "status": self.status,
            "returned_ids": list(self.returned_ids),
            "novel_ids": list(self.novel_ids),
            "note": self.note,
            "duration_seconds": round(self.duration_seconds, 3),
        }


@dataclass
class TaskRun:
    task_id: str
    system_id: str
    calls: list[RouteCall] = field(default_factory=list)
    candidates: list[str] = field(default_factory=list)
    open_obligations: list[str] = field(default_factory=list)
    closed_as_complete: bool = False
    agreement_candidates: list[str] = field(default_factory=list)
    multi_route_confirmed: list[str] = field(default_factory=list)

    def as_json(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "system_id": self.system_id,
            "calls": [item.as_json() for item in self.calls],
            "candidate_arxiv_ids": list(self.candidates),
            "agreement_candidate_arxiv_ids": list(self.agreement_candidates),
            "multi_route_confirmed_ids": list(self.multi_route_confirmed),
            "open_obligations": list(self.open_obligations),
            "closed_as_complete": self.closed_as_complete,
            "provider_requests": len(self.calls),
        }


# ---------------------------------------------------------------------------
# Backends. Each is a distinct (backend identity, query derivation) pair, which
# is what route independence is assessed on — not the route's label.
# ---------------------------------------------------------------------------


class Clock:
    """Per-host spacing. Politeness is enforced here, once, for every backend."""

    def __init__(self) -> None:
        self._last: dict[str, float] = {}

    def wait(self, host: str, interval: float) -> None:
        previous = self._last.get(host)
        now = time.monotonic()
        if previous is not None:
            gap = interval - (now - previous)
            if gap > 0:
                time.sleep(gap)
        self._last[host] = time.monotonic()


def _http_get(url: str, *, timeout: float) -> tuple[int, bytes, str]:
    request = urllib.request.Request(
        url, headers={"User-Agent": DECLARED_CONSTANTS["user_agent"]}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status), response.read(), ""
    except urllib.error.HTTPError as error:  # transport outcome, not absence
        return int(error.code), b"", f"http_error:{error.code}"
    except (urllib.error.URLError, TimeoutError) as error:
        return 0, b"", f"transport_error:{type(error).__name__}"


def arxiv_route(query: str, *, clock: Clock, max_results: int) -> tuple[str, tuple[str, ...], str]:
    clock.wait("arxiv", DECLARED_CONSTANTS["arxiv_min_interval_seconds"])
    url = (
        "https://export.arxiv.org/api/query?"
        + urllib.parse.urlencode(
            {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
            }
        )
    )
    status, body, note = _http_get(url, timeout=DECLARED_CONSTANTS["http_timeout_seconds"])
    if status != 200 or not body:
        return ("UNAVAILABLE" if status in (0, 429, 503) else "ERROR"), (), note or f"status:{status}"
    ids = tuple(dict.fromkeys(base.ARXIV_ID.findall(body.decode("utf-8", "replace"))))
    return "OK", ids, ""


def openaire_route(query: str, *, clock: Clock, max_results: int) -> tuple[str, tuple[str, ...], str]:
    clock.wait("openaire", DECLARED_CONSTANTS["other_backend_min_interval_seconds"])
    url = "https://api.openaire.eu/search/publications?" + urllib.parse.urlencode(
        {"title": query, "size": max_results, "format": "json"}
    )
    status, body, note = _http_get(url, timeout=DECLARED_CONSTANTS["http_timeout_seconds"])
    if status != 200 or not body:
        return ("UNAVAILABLE" if status in (0, 429, 503) else "ERROR"), (), note or f"status:{status}"
    text = body.decode("utf-8", "replace")
    ids = tuple(dict.fromkeys(base.ARXIV_ID.findall(text)))
    return "OK", ids, "" if ids else "no_arxiv_identifier_in_response"


def dblp_route(query: str, *, clock: Clock, max_results: int) -> tuple[str, tuple[str, ...], str]:
    clock.wait("dblp", DECLARED_CONSTANTS["other_backend_min_interval_seconds"])
    url = "https://dblp.org/search/publ/api?" + urllib.parse.urlencode(
        {"q": query, "format": "json", "h": max_results}
    )
    status, body, note = _http_get(url, timeout=DECLARED_CONSTANTS["http_timeout_seconds"])
    if status != 200 or not body:
        return ("UNAVAILABLE" if status in (0, 429, 503) else "ERROR"), (), note or f"status:{status}"
    text = body.decode("utf-8", "replace")
    ids = tuple(dict.fromkeys(base.ARXIV_ID.findall(text)))
    return "OK", ids, "" if ids else "no_arxiv_identifier_in_response"


# ---------------------------------------------------------------------------
# Query derivations. Distinct derivations are half of what independence needs.
# ---------------------------------------------------------------------------


def derive_primary(question: str) -> str:
    return base.derive_query(question)


def derive_narrowed(question: str) -> str:
    """Drop the least specific salient token: a reformulation, not a new query."""

    tokens = base._salient_tokens(question, count=5)
    return " ".join(tokens[:3]) if len(tokens) > 3 else " ".join(tokens)


def derive_widened(question: str) -> str:
    """Keep only the two most salient tokens — a recall-oriented reformulation."""

    tokens = base._salient_tokens(question, count=5)
    return " ".join(tokens[:2]) if tokens else question[:80]


def derive_title_like(question: str) -> str:
    """A title-shaped derivation for bibliographic backends."""

    tokens = base._salient_tokens(question, count=6)
    return " ".join(tokens[:4]) if tokens else question[:80]


# ---------------------------------------------------------------------------
# Systems
# ---------------------------------------------------------------------------


def select_round_robin(cap: int, groups: list[tuple[str, ...]]) -> list[str]:
    """Give every attempt or route an equal share of the returned set.

    A first-come cap is not neutral between the systems: whichever source is
    consulted first fills all twenty slots, so the baseline's reformulations and
    the governed system's other backends become invisible and both systems emit
    the same set. Round-robin is the rule that lets budget allocation actually
    show up in the answer, and it is applied identically to both systems — what
    differs is whether the sources are three attempts on one backend or three
    distinct backends.
    """

    chosen: dict[str, None] = {}
    index = 0
    while len(chosen) < cap and any(index < len(group) for group in groups):
        for group in groups:
            if len(chosen) >= cap:
                break
            if index < len(group):
                chosen.setdefault(group[index], None)
        index += 1
    return list(chosen)[:cap]


def select_agreement_first(
    cap: int, groups: list[tuple[str, ...]], found_by: dict[str, set[str]]
) -> list[str]:
    """Prefer identifiers that more than one distinct backend returned.

    This is the earned-independence idea used as a selection rule rather than as
    a diagnostic: agreement across genuinely different backends is evidence about
    a candidate, agreement within one backend is not. Under a set metric this can
    only help by trading a singleton for a confirmed candidate, so it is a real
    and falsifiable governance bet, not a free win.
    """

    confirmed = [item for item in select_round_robin(cap * 3, groups) if len(found_by.get(item, ())) > 1]
    remainder = [item for item in select_round_robin(cap * 3, groups) if item not in set(confirmed)]
    return (confirmed + remainder)[:cap]


def run_lexical_baseline(
    task_id: str, question: str, *, clock: Clock, max_results: int
) -> TaskRun:
    """One backend, whole budget, reformulating between attempts."""

    run = TaskRun(task_id=task_id, system_id="wide_lexical_arxiv")
    budget = RequestBudget(DECLARED_CONSTANTS["provider_requests_per_task"])
    seen: dict[str, None] = {}
    plan: list[tuple[str, Callable[[str], str]]] = [
        ("lexical-primary", derive_primary),
        ("lexical-narrowed", derive_narrowed),
        ("lexical-widened", derive_widened),
    ]
    for derivation, derive in plan:
        if budget.remaining == 0:
            break
        query = derive(question)
        if not query:
            continue
        budget.take()
        started = time.monotonic()
        status, ids, note = arxiv_route(query, clock=clock, max_results=max_results)
        novel = tuple(item for item in ids if item not in seen)
        for item in ids:
            seen.setdefault(item, None)
        run.calls.append(
            RouteCall(
                route_id="arxiv-lexical",
                backend="arxiv",
                query_derivation=derivation,
                query=query,
                status=status,
                returned_ids=ids,
                novel_ids=novel,
                note=note,
                duration_seconds=time.monotonic() - started,
            )
        )
    run.candidates = select_round_robin(
        DECLARED_CONSTANTS["max_candidates_returned"],
        [call.returned_ids for call in run.calls],
    )
    # A single-route system has no basis for a completeness claim, and does not
    # make one: the baseline is strong on retrieval, not on closure semantics.
    run.closed_as_complete = False
    return run


def run_governed_multiroute(
    task_id: str, question: str, *, clock: Clock, max_results: int
) -> TaskRun:
    """Same budget, spread across backends, with route control and dedup."""

    run = TaskRun(task_id=task_id, system_id="wide_governed_multiroute")
    budget = RequestBudget(DECLARED_CONSTANTS["provider_requests_per_task"])
    # (route_id, backend, derivation name, derive fn, transport)
    routes: list[tuple[str, str, str, Callable[[str], str], Any]] = [
        ("arxiv-lexical", "arxiv", "lexical-primary", derive_primary, arxiv_route),
        ("openaire-title", "openaire", "title-like", derive_title_like, openaire_route),
        ("dblp-bibliographic", "dblp", "narrowed", derive_narrowed, dblp_route),
    ]
    found_by: dict[str, set[str]] = {}
    order: list[str] = []

    for route_id, backend, derivation, derive, transport in routes:
        if budget.remaining == 0:
            break
        query = derive(question)
        if not query:
            continue
        budget.take()
        started = time.monotonic()
        status, ids, note = transport(query, clock=clock, max_results=max_results)
        novel = tuple(item for item in ids if item not in found_by)
        for item in ids:
            if item not in found_by:
                found_by[item] = set()
                order.append(item)
            found_by[item].add(route_id)
        run.calls.append(
            RouteCall(
                route_id=route_id,
                backend=backend,
                query_derivation=derivation,
                query=query,
                status=status,
                returned_ids=ids,
                novel_ids=novel,
                note=note,
                duration_seconds=time.monotonic() - started,
            )
        )
        if status != "OK":
            # An unavailable backend is an open obligation, never a zero that
            # licenses a completeness claim.
            run.open_obligations.append(f"{route_id}:{status}:{note}")

    groups = [call.returned_ids for call in run.calls]
    run.candidates = select_round_robin(
        DECLARED_CONSTANTS["max_candidates_returned"], groups
    )
    # The agreement-preferred set is a pure post-hoc selection rule over the very
    # same retrievals, so it is recorded here rather than paying for a second
    # campaign. Declared as a selection variant, never as an independent run.
    run.agreement_candidates = select_agreement_first(
        DECLARED_CONSTANTS["max_candidates_returned"], groups, found_by
    )
    run.multi_route_confirmed = sorted(
        item for item, routes in found_by.items() if len(routes) > 1
    )
    run.closed_as_complete = not run.open_obligations and budget.remaining == 0
    return run


SYSTEMS: dict[str, Callable[..., TaskRun]] = {
    "wide_lexical_arxiv": run_lexical_baseline,
    "wide_governed_multiroute": run_governed_multiroute,
}


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def _scorer_record(question: str, run: TaskRun) -> dict[str, Any]:
    """Emit exactly what the pinned upstream Wide scorer reads."""

    return {
        "input_data": {"question": question},
        "inference_results": [
            {
                "pass_id": 0,
                "status": "ok" if run.calls else "benchmark_empty_question",
                "final_candidates": [{"arxiv_id": item} for item in run.candidates],
                "turn_details": [],
            }
        ],
    }


def run_comparison(
    public_path: Path,
    out_dir: Path,
    *,
    systems: list[str],
    max_results: int,
    limit: int | None,
    progress_every: int,
) -> dict[str, Any]:
    tasks = base._jsonl(public_path)
    if limit is not None:
        tasks = tasks[:limit]

    leaked = [
        path
        for record in tasks
        for path in base._hidden_paths(record)
    ]
    if leaked:
        raise AssertionError("public split carries hidden labels: " + ",".join(leaked[:5]))

    out_dir.mkdir(parents=True, exist_ok=True)
    clock = Clock()
    summary: dict[str, Any] = {
        "schema_version": "orion.p2.autoresearchbench-wide-comparison.v1",
        "pinned_upstream_commit": base.PINNED_AUTORESEARCHBENCH_COMMIT,
        "declared_constants": DECLARED_CONSTANTS,
        "public_sha256": base._sha256(public_path),
        "tasks_attempted": len(tasks),
        "systems": {},
    }

    for system_id in systems:
        runner = SYSTEMS[system_id]
        records: list[dict[str, Any]] = []
        traces: list[dict[str, Any]] = []
        statuses: dict[str, int] = {}
        for index, task in enumerate(tasks, start=1):
            question = str(task.get("question", "") or "")
            task_id = str(task.get("task_id", index))
            if not question.strip():
                # Upstream omits empty questions from its GT mapping; issue no
                # provider request for them rather than inventing a query.
                run = TaskRun(task_id=task_id, system_id=system_id)
            else:
                run = runner(task_id, question, clock=clock, max_results=max_results)
            records.append(_scorer_record(question, run))
            traces.append(run.as_json())
            for call in run.calls:
                statuses[call.status] = statuses.get(call.status, 0) + 1
            if progress_every and index % progress_every == 0:
                print(
                    f"ARB_WIDE_CMP {system_id} {index}/{len(tasks)} statuses={json.dumps(statuses, sort_keys=True)}",
                    flush=True,
                )

        candidate_path = out_dir / f"candidate_{system_id}.jsonl"
        trace_path = out_dir / f"trace_{system_id}.json"
        base._write_jsonl(candidate_path, records)
        trace_path.write_text(
            json.dumps({"system_id": system_id, "tasks": traces}, sort_keys=True, indent=1) + "\n",
            encoding="utf-8",
        )
        total_requests = sum(len(item["calls"]) for item in traces)
        summary["systems"][system_id] = {
            "candidate_path": candidate_path.name,
            "trace_path": trace_path.name,
            "candidate_sha256": base._sha256(candidate_path),
            "trace_sha256": base._sha256(trace_path),
            "provider_requests": total_requests,
            "provider_requests_per_task": (
                round(total_requests / len(tasks), 4) if tasks else 0.0
            ),
            "route_status_counts": statuses,
            "tasks_with_open_obligations": sum(1 for item in traces if item["open_obligations"]),
            "tasks_closed_as_complete": sum(1 for item in traces if item["closed_as_complete"]),
            "mean_candidates_returned": (
                round(
                    sum(len(item["candidate_arxiv_ids"]) for item in traces) / len(tasks), 4
                )
                if tasks
                else 0.0
            ),
        }

    (out_dir / "COMPARISON_RUN_MANIFEST.json").write_text(
        json.dumps(summary, sort_keys=True, indent=1) + "\n", encoding="utf-8"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", type=Path, required=True, help="gold-blind public split")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument(
        "--systems",
        default=",".join(SYSTEMS),
        help="comma-separated system ids to run",
    )
    parser.add_argument("--max-results", type=int, default=20)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--progress-every", type=int, default=25)
    args = parser.parse_args(argv)

    systems = [item.strip() for item in args.systems.split(",") if item.strip()]
    unknown = [item for item in systems if item not in SYSTEMS]
    if unknown:
        parser.error(f"unknown systems: {unknown}; known: {sorted(SYSTEMS)}")

    summary = run_comparison(
        args.public,
        args.out_dir,
        systems=systems,
        max_results=args.max_results,
        limit=args.limit,
        progress_every=args.progress_every,
    )
    print("ARB_WIDE_COMPARISON=" + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
