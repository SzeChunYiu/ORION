#!/usr/bin/env python3
"""Corrected P2 V2 Wide acquisition development runner.

This runner exists because the earlier V2 Wide development harness extracted
arXiv-looking identifiers from the complete Atom response body. Here scorer IDs
come only from parsed Atom entry identities. The script compares a deliberately
strong lexical arXiv baseline with one final diversified candidate generator
under the same three-request / twenty-candidate budget.

It is selection-agnostic: the caller supplies an exact frozen task-id JSON list.
The development and any later fresh-confirmation workflows therefore use the
same implementation without changing code after an outcome is observed.
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

from orion.knowledge.providers.arxiv import FetchStatus, parse_atom

HERE = Path(__file__).resolve().parent
CMP_PATH = HERE / "run_autoresearchbench_wide_comparison.py"


def _load_cmp():
    spec = importlib.util.spec_from_file_location("orion_p2_wide_cmp_dev3", CMP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load matched Wide helpers at {CMP_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cmp = _load_cmp()
base = cmp.base

BASELINE_ID = "wide_lexical_arxiv_atom_v3"
CANDIDATE_ID = "wide_diversified_arxiv_atom_v3"
REQUESTS_PER_TASK = 3
MAX_RESULTS_PER_CALL = 20
MAX_CANDIDATES = 20

_WORD = re.compile(r"[A-Za-z][A-Za-z0-9+]*(?:-[A-Za-z0-9+]+)*")
_VERSION = re.compile(r"v\d+$", re.I)
_YEAR_RANGE = (
    re.compile(r"\b(?:between|from)\s+(19\d{2}|20\d{2})\s+(?:and|to|through|-)\s+(19\d{2}|20\d{2})\b", re.I),
    re.compile(r"\b(19\d{2}|20\d{2})\s*[-–—]\s*(19\d{2}|20\d{2})\b"),
)

# Function words plus benchmark/research-instruction vocabulary. These terms
# were observed in Dev-2 query traces (e.g. "and", "identify") and are excluded
# prospectively because they carry little topical retrieval information.
GENERIC = frozenset(
    """
    a an the and or but if then than so as at by for from in into of on onto to up with
    without within between among around about across after before during over under through
    which what who whom whose when where why how this that these those it its they them their
    we our you your i me my is are was were be been being do does did doing have has had
    having can could may might must should would will shall not no nor only also both either
    each any all some such more most less least many much few several other another same
    paper papers article articles study studies work works research literature publication
    publications result results report reports reported recent recently key main notable
    identify identifies identified identifying find finds finding found looking look seek
    asks ask question questions specifically explicit explicitly include includes including
    focus focuses focused focusing examine examines examined examining investigate
    investigates investigated investigating compare compares compared comparison evaluate
    evaluates evaluated evaluation benchmark benchmarks dataset datasets method methods
    approach approaches technique techniques framework frameworks architecture architectures
    model models system systems task tasks objective objectives aim aims evidence empirical
    proposed propose proposes show shows shown demonstrate demonstrates demonstrated using
    used uses use based primarily particular roughly goal goals related relevant overview
    """.split()
)


def _is_content(raw: str) -> bool:
    token = raw.lower().strip("-")
    return (
        token not in GENERIC
        and token not in base.STOPWORDS
        and not token.isdigit()
        and not re.fullmatch(r"(?:19|20)\d{2}", token)
        and len(token) >= 3
    )


def _occurrences(question: str) -> list[tuple[int, int, str, str]]:
    out: list[tuple[int, int, str, str]] = []
    for match in _WORD.finditer(question):
        raw = match.group(0)
        if _is_content(raw):
            out.append((match.start(), match.end(), raw, raw.lower().strip("-")))
    return out


def ranked_tokens(question: str, limit: int = 8) -> list[str]:
    """Deterministic high-information tokens from public question text only."""
    best: dict[str, tuple[int, int]] = {}
    for start, _end, raw, token in _occurrences(question):
        score = len(token)
        if "-" in raw:
            score += 3
        if raw.isupper() and len(raw) >= 3:
            score += 4
        score += max(0, 6 - start // 45)
        current = best.get(token)
        candidate = (score, -start)
        if current is None or candidate > current:
            best[token] = candidate
    ordered = sorted(best, key=lambda token: (best[token][0], best[token][1], token), reverse=True)
    return ordered[:limit]


def explicit_year_range(question: str) -> tuple[int, int] | None:
    for pattern in _YEAR_RANGE:
        match = pattern.search(question)
        if match:
            lo, hi = sorted((int(match.group(1)), int(match.group(2))))
            if 1990 <= lo <= 2030 and 1990 <= hi <= 2030:
                return lo, hi
    return None


def with_date(query: str, question: str) -> str:
    years = explicit_year_range(question)
    if years is None:
        return query
    lo, hi = years
    return f"({query}) AND submittedDate:[{lo}01010000 TO {hi}12312359]"


def contiguous_bigrams(question: str, limit: int = 3) -> list[str]:
    matches = list(_WORD.finditer(question))
    candidates: list[tuple[int, int, str]] = []
    seen: set[str] = set()
    for left, right in zip(matches, matches[1:]):
        if not (_is_content(left.group(0)) and _is_content(right.group(0))):
            continue
        # Adjacent regex matches may still have punctuation/space between them,
        # which is acceptable; there is no omitted word by construction.
        phrase = f"{left.group(0).lower().strip('-')} {right.group(0).lower().strip('-')}"
        if phrase in seen:
            continue
        seen.add(phrase)
        score = len(phrase) + max(0, 6 - left.start() // 45)
        if "-" in left.group(0) or "-" in right.group(0):
            score += 3
        candidates.append((score, -left.start(), phrase))
    candidates.sort(reverse=True)
    return [phrase for _, _, phrase in candidates[:limit]]


def baseline_primary(question: str) -> str:
    tokens = ranked_tokens(question, 5)
    if len(tokens) < 2:
        raise ValueError("insufficient topical tokens for baseline primary")
    pairs = [f"(all:{a} AND all:{b})" for a, b in zip(tokens[:4], tokens[1:5])]
    return with_date(" OR ".join(pairs), question)


def baseline_core(question: str) -> str:
    tokens = ranked_tokens(question, 3)
    if len(tokens) < 2:
        raise ValueError("insufficient topical tokens for baseline core")
    return with_date(f"all:{tokens[0]} AND all:{tokens[1]}", question)


def baseline_broad(question: str) -> str:
    tokens = ranked_tokens(question, 6)
    if len(tokens) < 2:
        raise ValueError("insufficient topical tokens for baseline broad")
    return with_date(" OR ".join(f"all:{token}" for token in tokens), question)


def candidate_fielded(question: str) -> str:
    phrases = contiguous_bigrams(question, 3)
    if phrases:
        return with_date(
            " OR ".join(f'(ti:"{p}" OR abs:"{p}")' for p in phrases), question
        )
    return baseline_primary(question)


def candidate_broad(question: str) -> str:
    tokens = ranked_tokens(question, 8)
    if len(tokens) < 2:
        raise ValueError("insufficient topical tokens for candidate broad")
    return with_date(" OR ".join(f"all:{token}" for token in tokens), question)


def candidate_pairs(question: str) -> str:
    tokens = ranked_tokens(question, 6)
    if len(tokens) < 4:
        return baseline_primary(question)
    pairs = [(tokens[0], tokens[1]), (tokens[2], tokens[3]), (tokens[0], tokens[4])]
    return with_date(" OR ".join(f"(all:{a} AND all:{b})" for a, b in pairs), question)


BASELINE_PLAN: tuple[tuple[str, Callable[[str], str]], ...] = (
    ("BASE_PRIMARY", baseline_primary),
    ("BASE_CORE", baseline_core),
    ("BASE_BROAD", baseline_broad),
)
CANDIDATE_PLAN: tuple[tuple[str, Callable[[str], str]], ...] = (
    ("FIELD_BIGRAM", candidate_fielded),
    ("TOKEN_OR_8", candidate_broad),
    ("PAIR_DIVERSIFY", candidate_pairs),
)


def normalize_entry_id(value: str) -> str:
    text = str(value or "").strip()
    if "/abs/" in text:
        text = text.split("/abs/", 1)[1]
    text = re.sub(r"(?i)^arxiv:\s*", "", text).strip().strip("/")
    return _VERSION.sub("", text)


def arxiv_entry_route(query: str, *, clock: Any, max_results: int) -> tuple[str, tuple[str, ...], str]:
    """Fetch arXiv and admit only parsed Atom entry identities."""
    clock.wait("arxiv", cmp.DECLARED_CONSTANTS["arxiv_min_interval_seconds"])
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": query, "start": 0, "max_results": max_results, "sortBy": "relevance"}
    )
    status, body, note, attempts = cmp._http_get(
        url, timeout=cmp.DECLARED_CONSTANTS["http_timeout_seconds"]
    )
    suffix = f"attempts:{attempts}" if attempts > 1 else ""
    if status != 200 or not body:
        kind = "UNAVAILABLE" if status in (0, 429, 503) else "ERROR"
        return kind, (), " ".join(x for x in (note or f"status:{status}", suffix) if x)

    parsed_status, records, parsed_note = parse_atom(body.decode("utf-8", "replace"))
    if parsed_status is not FetchStatus.OK:
        return "ERROR", (), f"atom:{parsed_status.value}:{parsed_note}"
    ids = tuple(
        dict.fromkeys(
            normalized
            for record in records
            if (normalized := normalize_entry_id(record.versioned_id))
        )
    )
    if len(ids) > max_results:
        raise AssertionError(
            f"entry parser returned {len(ids)} scorer IDs above max_results={max_results}"
        )
    return "OK", ids, suffix


def run_system(
    system_id: str,
    plan: tuple[tuple[str, Callable[[str], str]], ...],
    task_id: str,
    question: str,
    *,
    clock: Any,
) -> Any:
    run = cmp.TaskRun(task_id=task_id, system_id=system_id)
    groups: list[tuple[str, ...]] = []
    for family, derive in plan:
        query = derive(question)
        started = time.monotonic()
        status, ids, note = arxiv_entry_route(
            query, clock=clock, max_results=MAX_RESULTS_PER_CALL
        )
        groups.append(ids)
        seen_before = {item for previous in groups[:-1] for item in previous}
        novel = tuple(item for item in ids if item not in seen_before)
        run.calls.append(
            cmp.RouteCall(
                route_id=f"arxiv-{system_id}",
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
            run.open_obligations.append(f"arxiv:{family}:{status}:{note}")
    if len(run.calls) != REQUESTS_PER_TASK:
        raise AssertionError("every non-empty task must spend exactly three provider requests")
    run.candidates = cmp.select_round_robin(MAX_CANDIDATES, groups)
    run.agreement_candidates = []
    run.multi_route_confirmed = []
    run.closed_as_complete = False
    return run


def load_selected_tasks(public_path: Path, task_ids_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    public = base._jsonl(public_path)
    requested = json.loads(task_ids_path.read_text(encoding="utf-8"))
    if not isinstance(requested, list) or not requested or not all(isinstance(x, str) for x in requested):
        raise ValueError("task id file must be a non-empty JSON string list")
    if len(requested) != len(set(requested)):
        raise ValueError("task id list contains duplicates")
    by_id = {str(row.get("task_id")): row for row in public}
    missing = [task_id for task_id in requested if task_id not in by_id]
    if missing:
        raise ValueError(f"unknown task ids: {missing[:5]}")
    selected = [by_id[task_id] for task_id in requested]
    leaked = [path for row in selected for path in base._hidden_paths(row)]
    if leaked:
        raise AssertionError("selected public tasks contain hidden labels: " + ",".join(leaked[:5]))
    return selected, requested


def run_comparison(public_path: Path, task_ids_path: Path, out_dir: Path, progress_every: int) -> dict[str, Any]:
    tasks, task_ids = load_selected_tasks(public_path, task_ids_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    clock = cmp.Clock()
    runs: dict[str, list[Any]] = {BASELINE_ID: [], CANDIDATE_ID: []}

    # Interleave systems within each task so provider drift cannot align entirely
    # with one system. The order is frozen baseline then candidate.
    for index, row in enumerate(tasks, start=1):
        question = str(row.get("question") or "").strip()
        task_id = str(row["task_id"])
        if not question:
            for sid in runs:
                runs[sid].append(cmp.TaskRun(task_id=task_id, system_id=sid))
        else:
            runs[BASELINE_ID].append(
                run_system(BASELINE_ID, BASELINE_PLAN, task_id, question, clock=clock)
            )
            runs[CANDIDATE_ID].append(
                run_system(CANDIDATE_ID, CANDIDATE_PLAN, task_id, question, clock=clock)
            )
        if progress_every and index % progress_every == 0:
            print(f"ARB_WIDE_DEV3 {index}/{len(tasks)}", flush=True)

    summary: dict[str, Any] = {
        "schema_version": "orion.p2.autoresearchbench-wide-acquisition-dev3.v1",
        "pinned_upstream_commit": base.PINNED_AUTORESEARCHBENCH_COMMIT,
        "public_sha256": base._sha256(public_path),
        "task_ids": task_ids,
        "task_ids_sha256": __import__("hashlib").sha256("\n".join(task_ids).encode()).hexdigest(),
        "systems": {},
    }
    question_by_id = {str(row["task_id"]): str(row.get("question") or "") for row in tasks}
    for sid, system_runs in runs.items():
        records = [cmp._scorer_record(question_by_id[run.task_id], run) for run in system_runs]
        candidate_path = out_dir / f"candidate_{sid}.jsonl"
        trace_path = out_dir / f"trace_{sid}.json"
        base._write_jsonl(candidate_path, records)
        trace_path.write_text(
            json.dumps({"system_id": sid, "tasks": [run.as_json() for run in system_runs]}, sort_keys=True, indent=1) + "\n",
            encoding="utf-8",
        )
        calls = sum(len(run.calls) for run in system_runs)
        statuses: dict[str, int] = {}
        for run in system_runs:
            for call in run.calls:
                statuses[call.status] = statuses.get(call.status, 0) + 1
        summary["systems"][sid] = {
            "provider_requests": calls,
            "provider_requests_per_task": calls / len(tasks),
            "route_status_counts": statuses,
            "tasks_with_open_obligations": sum(bool(run.open_obligations) for run in system_runs),
            "tasks_closed_as_complete": sum(bool(run.closed_as_complete) for run in system_runs),
            "mean_candidates_returned": sum(len(run.candidates) for run in system_runs) / len(tasks),
            "candidate_path": candidate_path.name,
            "candidate_sha256": base._sha256(candidate_path),
            "trace_path": trace_path.name,
            "trace_sha256": base._sha256(trace_path),
        }
    (out_dir / "DEV3_RUN_MANIFEST.json").write_text(json.dumps(summary, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--task-ids", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--progress-every", type=int, default=4)
    args = parser.parse_args(argv)
    payload = run_comparison(args.public, args.task_ids, args.out_dir, args.progress_every)
    print("ARB_WIDE_DEV3=" + json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
