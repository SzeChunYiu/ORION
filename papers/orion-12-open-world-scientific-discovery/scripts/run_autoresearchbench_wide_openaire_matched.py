#!/usr/bin/env python3
"""Run the frozen P2 AutoResearchBench Wide OpenAIRE/Crossref acquisition capture.

The scientific comparison is deliberately *projection-only*: every reported
system sees the same three logical provider calls for a task.  The baseline and
ORION differ only in how they select at most twenty normalized arXiv identities
from that common capture.  Gold is not an input to this program.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
KEYLESS_PATH = HERE / "run_autoresearchbench_wide_keyless.py"
IDENTITY_PATH = HERE / "probe_autoresearchbench_wide_openaire_identity.py"
DEFAULT_FREEZE = PAPER / "protocol" / "P2_WIDE_OPENAIRE_MATCHED_FREEZE_V1.json"
DEFAULT_IDENTITY_RECEIPT = PAPER / "evidence" / "external_results" / "P2_OPENAIRE_IDENTITY_PROBE_V1.json"

OPENAIRE_ENDPOINT = "https://api.openaire.eu/graph/v3/research-products"
CROSSREF_ENDPOINT = "https://api.crossref.org/works"
USER_AGENT = "ORION-P2-research/0.1 (+https://github.com/SzeChunYiu/ORION)"
DOI = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
SYSTEM_IDS = (
    "wide_dual_backend_balanced",
    "wide_dual_backend_governed",
    "wide_dual_backend_direct_first",
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


keyless = _load_module("orion_p2_wide_keyless_matched", KEYLESS_PATH)
identity = _load_module("orion_p2_wide_identity_matched", IDENTITY_PATH)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: record must be an object")
            rows.append(value)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def derive_primary(question: str) -> str:
    terms = keyless._salient_tokens(question, count=4)
    if len(terms) < 2:
        raise ValueError("could not derive at least two gold-blind topical terms")
    return " ".join(terms)


def derive_widened(question: str) -> str:
    terms = keyless._salient_tokens(question, count=4)
    if len(terms) < 2:
        raise ValueError("could not derive widened gold-blind query")
    return " ".join(terms[:2])


def normalize_doi(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("https://doi.org/"):
        text = text[len("https://doi.org/") :]
    if text.startswith("doi:"):
        text = text[4:].strip()
    return text if DOI.fullmatch(text) else ""


def extract_crossref_dois(payload: dict[str, Any]) -> tuple[str, ...]:
    message = payload.get("message")
    if not isinstance(message, dict):
        raise ValueError("Crossref response missing message object")
    items = message.get("items")
    if not isinstance(items, list):
        raise ValueError("Crossref response missing message.items array")
    found: dict[str, None] = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Crossref work is not an object")
        doi = normalize_doi(item.get("DOI"))
        if doi:
            found.setdefault(doi, None)
    return tuple(found)


def build_openaire_search_url(query: str, *, page_size: int) -> str:
    return OPENAIRE_ENDPOINT + "?" + urllib.parse.urlencode(
        {"search": query, "type": "publication", "page": 1, "pageSize": page_size}
    )


def build_crossref_url(query: str, *, rows: int) -> str:
    return CROSSREF_ENDPOINT + "?" + urllib.parse.urlencode(
        {"query.bibliographic": query, "rows": rows, "select": "DOI,title"}
    )


def build_openaire_crosswalk_url(dois: Iterable[str], *, page_size: int) -> str:
    normalized = [normalize_doi(doi) for doi in dois]
    normalized = list(dict.fromkeys(doi for doi in normalized if doi))[:20]
    if not normalized:
        raise ValueError("OpenAIRE DOI crosswalk requires at least one DOI")
    expression = "(" + " OR ".join(json.dumps(doi) for doi in normalized) + ")"
    return OPENAIRE_ENDPOINT + "?" + urllib.parse.urlencode(
        {"pid": expression, "type": "publication", "page": 1, "pageSize": page_size}
    )


class HostClock:
    def __init__(self) -> None:
        self._last: dict[str, float] = {}

    def wait(self, host: str, interval: float) -> None:
        previous = self._last.get(host)
        now = time.monotonic()
        if previous is not None:
            remaining = interval - (now - previous)
            if remaining > 0:
                time.sleep(remaining)
        self._last[host] = time.monotonic()


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: bytes
    note: str
    attempts: int


def http_get(
    url: str,
    *,
    clock: HostClock,
    host: str,
    minimum_interval: float,
    timeout_seconds: float,
    maximum_retries: int,
    retry_sleep_seconds: float,
) -> HttpResult:
    attempts = 0
    last_status = 0
    last_body = b""
    last_note = "not_attempted"
    while attempts <= maximum_retries:
        attempts += 1
        clock.wait(host, minimum_interval)
        request = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                last_status = int(response.status)
                last_body = response.read()
                last_note = ""
        except urllib.error.HTTPError as error:
            last_status = int(error.code)
            last_body = error.read() if error.fp is not None else b""
            last_note = f"http_error:{error.code}"
        except (urllib.error.URLError, TimeoutError) as error:
            last_status = 0
            last_body = b""
            last_note = f"transport_error:{type(error).__name__}"
        if last_status not in (0, 429, 503):
            break
        if attempts <= maximum_retries:
            time.sleep(retry_sleep_seconds)
    return HttpResult(last_status, last_body, last_note, attempts)


def _save_response(response_dir: Path, task_id: str, call_index: int, body: bytes) -> str | None:
    if not body:
        return None
    response_dir.mkdir(parents=True, exist_ok=True)
    path = response_dir / f"{task_id}-call{call_index}.json"
    path.write_bytes(body)
    return str(path)


def _parse_json(body: bytes, *, source: str) -> dict[str, Any]:
    try:
        value = json.loads(body)
    except json.JSONDecodeError as error:
        raise ValueError(f"{source} returned invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{source} JSON root is not an object")
    return value


def _call_record(
    *,
    logical_index: int,
    kind: str,
    backend: str,
    query: str,
    url: str,
    http: HttpResult,
    response_path: str | None,
    status: str,
    structured_arxiv_ids: Iterable[str] = (),
    dois: Iterable[str] = (),
    parse_note: str = "",
) -> dict[str, Any]:
    return {
        "logical_index": logical_index,
        "kind": kind,
        "backend": backend,
        "query": query,
        "url": url,
        "status": status,
        "http_status": http.status,
        "physical_attempts": http.attempts,
        "response_sha256": sha256_bytes(http.body) if http.body else None,
        "response_file": response_path,
        "structured_arxiv_ids": list(structured_arxiv_ids),
        "dois": list(dois),
        "note": parse_note or http.note,
    }


def acquire_task(
    task_id: str,
    question: str,
    *,
    freeze: dict[str, Any],
    clock: HostClock,
    response_dir: Path,
) -> dict[str, Any]:
    if not question.strip():
        return {
            "task_id": task_id,
            "question": question,
            "query_primary": None,
            "query_widened": None,
            "calls": [],
            "direct_openaire_ids": [],
            "crossref_dois": [],
            "crossref_arxiv_ids": [],
            "fallback_openaire_ids": [],
            "cross_backend_confirmed_ids": [],
            "open_obligations": ["benchmark_empty_question"],
        }

    query = derive_primary(question)
    widened = derive_widened(question)
    acquisition = freeze["acquisition"]
    oa = acquisition["openaire"]
    cr = acquisition["crossref"]
    transport = acquisition["transport"]
    timeout = float(transport["timeout_seconds"])
    retries = int(transport["maximum_retries_per_logical_request"])
    retry_sleep = float(transport["retry_sleep_seconds"])
    calls: list[dict[str, Any]] = []
    obligations: list[str] = []

    # Logical request 1: direct OpenAIRE discovery.
    direct_url = build_openaire_search_url(query, page_size=int(oa["direct"]["parameters"]["pageSize"]))
    direct_http = http_get(
        direct_url,
        clock=clock,
        host="openaire",
        minimum_interval=float(oa["minimum_interval_seconds"]),
        timeout_seconds=timeout,
        maximum_retries=retries,
        retry_sleep_seconds=retry_sleep,
    )
    direct_path = _save_response(response_dir, task_id, 1, direct_http.body)
    direct_ids: tuple[str, ...] = ()
    direct_status = "ERROR"
    direct_note = ""
    if direct_http.status == 200 and direct_http.body:
        try:
            direct_payload = _parse_json(direct_http.body, source="OpenAIRE direct")
            direct_ids, _ = identity.extract_structured_arxiv_ids(direct_payload)
            direct_status = "OK"
        except ValueError as error:
            direct_note = f"parse_error:{error}"
    elif direct_http.status in (0, 429, 503):
        direct_status = "UNAVAILABLE"
    if direct_status != "OK":
        obligations.append(f"openaire_direct:{direct_status}:{direct_note or direct_http.note}")
    calls.append(
        _call_record(
            logical_index=1,
            kind="openaire_direct",
            backend="OPENAIRE",
            query=query,
            url=direct_url,
            http=direct_http,
            response_path=direct_path,
            status=direct_status,
            structured_arxiv_ids=direct_ids,
            parse_note=direct_note,
        )
    )

    # Logical request 2: Crossref discovery. DOI is the only admitted identity.
    crossref_url = build_crossref_url(query, rows=int(cr["parameters"]["rows"]))
    crossref_http = http_get(
        crossref_url,
        clock=clock,
        host="crossref",
        minimum_interval=float(cr["minimum_interval_seconds"]),
        timeout_seconds=timeout,
        maximum_retries=retries,
        retry_sleep_seconds=retry_sleep,
    )
    crossref_path = _save_response(response_dir, task_id, 2, crossref_http.body)
    dois: tuple[str, ...] = ()
    crossref_status = "ERROR"
    crossref_note = ""
    if crossref_http.status == 200 and crossref_http.body:
        try:
            crossref_payload = _parse_json(crossref_http.body, source="Crossref")
            dois = extract_crossref_dois(crossref_payload)
            crossref_status = "OK"
        except ValueError as error:
            crossref_note = f"parse_error:{error}"
    elif crossref_http.status in (0, 429, 503):
        crossref_status = "UNAVAILABLE"
    if crossref_status != "OK":
        obligations.append(f"crossref:{crossref_status}:{crossref_note or crossref_http.note}")
    calls.append(
        _call_record(
            logical_index=2,
            kind="crossref_discovery",
            backend="CROSSREF",
            query=query,
            url=crossref_url,
            http=crossref_http,
            response_path=crossref_path,
            status=crossref_status,
            dois=dois,
            parse_note=crossref_note,
        )
    )

    # Logical request 3: resolve Crossref-discovered DOIs through OpenAIRE, or
    # spend the same request on a predeclared OpenAIRE widened search if Crossref
    # returned no usable DOI.  Either way exactly one third logical call is made.
    crossref_ids: tuple[str, ...] = ()
    fallback_ids: tuple[str, ...] = ()
    if dois:
        third_kind = "openaire_doi_crosswalk"
        third_query = " OR ".join(dois[:20])
        third_url = build_openaire_crosswalk_url(
            dois[:20], page_size=int(oa["crosswalk"]["parameters"]["pageSize"])
        )
    else:
        third_kind = "openaire_widened_fallback"
        third_query = widened
        third_url = build_openaire_search_url(
            widened, page_size=int(oa["fallback"]["parameters"]["pageSize"])
        )
    third_http = http_get(
        third_url,
        clock=clock,
        host="openaire",
        minimum_interval=float(oa["minimum_interval_seconds"]),
        timeout_seconds=timeout,
        maximum_retries=retries,
        retry_sleep_seconds=retry_sleep,
    )
    third_path = _save_response(response_dir, task_id, 3, third_http.body)
    third_status = "ERROR"
    third_note = ""
    third_ids: tuple[str, ...] = ()
    if third_http.status == 200 and third_http.body:
        try:
            third_payload = _parse_json(third_http.body, source=third_kind)
            third_ids, _ = identity.extract_structured_arxiv_ids(third_payload)
            third_status = "OK"
        except ValueError as error:
            third_note = f"parse_error:{error}"
    elif third_http.status in (0, 429, 503):
        third_status = "UNAVAILABLE"
    if third_status != "OK":
        obligations.append(f"{third_kind}:{third_status}:{third_note or third_http.note}")
    if dois:
        crossref_ids = third_ids
    else:
        fallback_ids = third_ids
    calls.append(
        _call_record(
            logical_index=3,
            kind=third_kind,
            backend="OPENAIRE",
            query=third_query,
            url=third_url,
            http=third_http,
            response_path=third_path,
            status=third_status,
            structured_arxiv_ids=third_ids,
            parse_note=third_note,
        )
    )

    confirmed = sorted(set(direct_ids) & set(crossref_ids))
    return {
        "task_id": task_id,
        "question": question,
        "query_primary": query,
        "query_widened": widened,
        "calls": calls,
        "direct_openaire_ids": list(direct_ids),
        "crossref_dois": list(dois),
        "crossref_arxiv_ids": list(crossref_ids),
        "fallback_openaire_ids": list(fallback_ids),
        "cross_backend_confirmed_ids": confirmed,
        "open_obligations": obligations,
    }


def route_balanced_order(groups: list[list[str]]) -> list[str]:
    chosen: dict[str, None] = {}
    index = 0
    while any(index < len(group) for group in groups):
        for group in groups:
            if index < len(group):
                chosen.setdefault(group[index], None)
        index += 1
    return list(chosen)


def project_candidates(capture: dict[str, Any], *, system_id: str, cap: int) -> list[str]:
    direct = list(capture["direct_openaire_ids"])
    crossref = list(capture["crossref_arxiv_ids"])
    fallback = list(capture["fallback_openaire_ids"])
    secondary = crossref if crossref else fallback
    balanced = route_balanced_order([direct, secondary])

    if system_id == "wide_dual_backend_balanced":
        return balanced[:cap]
    if system_id == "wide_dual_backend_governed":
        confirmed = [item for item in balanced if item in set(capture["cross_backend_confirmed_ids"])]
        confirmed_set = set(confirmed)
        return (confirmed + [item for item in balanced if item not in confirmed_set])[:cap]
    if system_id == "wide_dual_backend_direct_first":
        ordered = list(dict.fromkeys(direct + secondary))
        return ordered[:cap]
    raise ValueError(f"unknown frozen system id: {system_id}")


def scorer_record(question: str, candidates: list[str], *, empty: bool) -> dict[str, Any]:
    return {
        "input_data": {"question": question},
        "inference_results": [
            {
                "pass_id": 0,
                "status": "benchmark_empty_question" if empty else "ok",
                "final_candidates": [{"arxiv_id": item} for item in candidates],
                "turn_details": [],
            }
        ],
    }


def validate_public_rows(rows: list[dict[str, Any]]) -> None:
    seen_task_ids: set[str] = set()
    for row in rows:
        identity.validate_public_record(row)
        task_id = str(row["task_id"])
        if task_id in seen_task_ids:
            raise ValueError(f"duplicate task_id in public split: {task_id}")
        seen_task_ids.add(task_id)


def run(public_path: Path, freeze_path: Path, identity_receipt_path: Path, out_dir: Path) -> dict[str, Any]:
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze.get("schema_version") != "orion.p2.wide-openaire-matched-freeze.v1":
        raise ValueError("unexpected matched Wide freeze schema")
    if not freeze.get("frozen_before_official_score"):
        raise ValueError("matched Wide protocol is not prospectively frozen")
    identity_receipt = json.loads(identity_receipt_path.read_text(encoding="utf-8"))
    required = freeze["parent_identity_receipt"]["terminal_required"]
    if identity_receipt.get("authority") != required or identity_receipt.get("outcome", {}).get("terminal") != required:
        raise ValueError("parent structured identity bridge is not authorized")

    rows = load_jsonl(public_path)
    validate_public_rows(rows)
    expected_rows = int(freeze["benchmark"]["released_wide_rows"])
    if len(rows) != expected_rows:
        raise ValueError(f"expected {expected_rows} Wide public rows, got {len(rows)}")

    out_dir.mkdir(parents=True, exist_ok=True)
    response_dir = out_dir / "responses"
    capture_path = out_dir / "SHARED_ACQUISITION_CAPTURE.jsonl"
    clock = HostClock()
    captures: list[dict[str, Any]] = []
    with capture_path.open("w", encoding="utf-8") as capture_handle:
        for index, row in enumerate(rows, start=1):
            capture = acquire_task(
                str(row["task_id"]),
                str(row["question"] or ""),
                freeze=freeze,
                clock=clock,
                response_dir=response_dir,
            )
            captures.append(capture)
            capture_handle.write(json.dumps(capture, sort_keys=True, ensure_ascii=False) + "\n")
            capture_handle.flush()
            if index % 20 == 0:
                ok = sum(call["status"] == "OK" for item in captures for call in item["calls"])
                calls = sum(len(item["calls"]) for item in captures)
                print(f"P2_WIDE_OPENAIRE_CAPTURE {index}/{len(rows)} ok={ok}/{calls}", flush=True)

    cap = int(freeze["acquisition"]["max_candidates_per_system"])
    candidate_hashes: dict[str, str] = {}
    system_summaries: dict[str, Any] = {}
    for system_id in SYSTEM_IDS:
        candidate_rows: list[dict[str, Any]] = []
        projection_rows: list[dict[str, Any]] = []
        for capture in captures:
            empty = not str(capture["question"]).strip()
            candidates = [] if empty else project_candidates(capture, system_id=system_id, cap=cap)
            if len(candidates) > cap:
                raise AssertionError("candidate cap exceeded")
            candidate_rows.append(scorer_record(str(capture["question"]), candidates, empty=empty))
            projection_rows.append(
                {
                    "task_id": capture["task_id"],
                    "system_id": system_id,
                    "candidate_arxiv_ids": candidates,
                    "candidate_count": len(candidates),
                    "same_shared_capture": True,
                    "cross_backend_confirmed_ids": capture["cross_backend_confirmed_ids"],
                    "open_obligations": capture["open_obligations"],
                }
            )
        candidate_path = out_dir / f"candidate_{system_id}.jsonl"
        projection_path = out_dir / f"projection_{system_id}.jsonl"
        write_jsonl(candidate_path, candidate_rows)
        write_jsonl(projection_path, projection_rows)
        candidate_hashes[system_id] = sha256_file(candidate_path)
        system_summaries[system_id] = {
            "candidate_file": candidate_path.name,
            "candidate_sha256": candidate_hashes[system_id],
            "projection_file": projection_path.name,
            "projection_sha256": sha256_file(projection_path),
            "mean_candidate_count": round(sum(x["candidate_count"] for x in projection_rows) / len(projection_rows), 6),
            "max_candidate_count": max((x["candidate_count"] for x in projection_rows), default=0),
        }

    nonempty = [capture for capture in captures if str(capture["question"]).strip()]
    logical_calls = [call for capture in nonempty for call in capture["calls"]]
    planned = len(nonempty) * int(freeze["acquisition"]["logical_requests_per_nonempty_task"])
    if len(logical_calls) != planned:
        raise AssertionError(f"logical request drift: {len(logical_calls)} != {planned}")
    logical_ok = sum(call["status"] == "OK" for call in logical_calls)
    physical_attempts = sum(int(call["physical_attempts"]) for call in logical_calls)
    manifest = {
        "schema_version": "orion.p2.wide-openaire-shared-capture.v1",
        "authority": "CANDIDATE_CAPTURE_FROZEN_BEFORE_EVALUATOR_GOLD",
        "freeze_sha256": sha256_file(freeze_path),
        "identity_receipt_sha256": sha256_file(identity_receipt_path),
        "public_split_sha256": sha256_file(public_path),
        "released_rows": len(rows),
        "nonempty_rows": len(nonempty),
        "shared_capture_sha256": sha256_file(capture_path),
        "logical_provider_calls_planned": planned,
        "logical_provider_calls_recorded": len(logical_calls),
        "logical_provider_calls_ok": logical_ok,
        "logical_provider_ok_fraction": round(logical_ok / planned, 6) if planned else 0.0,
        "physical_http_attempts": physical_attempts,
        "tasks_with_open_obligations": sum(bool(capture["open_obligations"]) for capture in nonempty),
        "candidate_cap": cap,
        "candidate_hashes": candidate_hashes,
        "systems": system_summaries,
        "same_acquisition_capture_for_all_systems": True,
        "raw_regex_arxiv_identity_extraction": False,
    }
    manifest_path = out_dir / "SHARED_ACQUISITION_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("P2_WIDE_OPENAIRE_CAPTURE_TERMINAL=" + json.dumps(manifest, sort_keys=True), flush=True)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", required=True, type=Path)
    parser.add_argument("--freeze", type=Path, default=DEFAULT_FREEZE)
    parser.add_argument("--identity-receipt", type=Path, default=DEFAULT_IDENTITY_RECEIPT)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    run(args.public, args.freeze, args.identity_receipt, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
