#!/usr/bin/env python3
"""Gold-blind OpenAIRE identity bridge probe for AutoResearchBench Wide.

This is a development discriminator, not a benchmark result.  It asks one
question that blocked the matched Wide campaign: can a keyless scholarly graph
return *explicit structured arXiv PIDs* from public question text, without
calling the arXiv API and without treating digit-shaped strings as identity?

Gold never enters this process.  The caller supplies the public split produced by
``run_autoresearchbench_wide_compat.py prepare`` plus the frozen probe manifest.
Raw OpenAIRE responses are retained so an independent reviewer can verify every
admitted scorer identifier.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
KEYLESS_PATH = HERE / "run_autoresearchbench_wide_keyless.py"
DEFAULT_FREEZE = HERE.parent / "protocol" / "P2_OPENAIRE_IDENTITY_PROBE_FREEZE_V1.json"
OPENAIRE_ENDPOINT = "https://api.openaire.eu/graph/v3/research-products"
USER_AGENT = "ORION-P2-research/0.1 (+https://github.com/SzeChunYiu/ORION)"
HTTP_TIMEOUT_SECONDS = 30.0

MODERN_ARXIV = re.compile(r"^\d{4}\.\d{4,5}$")
LEGACY_ARXIV = re.compile(r"^[A-Za-z][A-Za-z0-9.-]*/\d{7}$")
VERSION_SUFFIX = re.compile(r"v\d+$", re.IGNORECASE)


def _load_keyless():
    spec = importlib.util.spec_from_file_location("orion_p2_wide_keyless_for_openaire", KEYLESS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load gold-blind Wide helpers at {KEYLESS_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_structured_arxiv(value: Any) -> str:
    """Normalize an explicit arXiv-scheme PID, rejecting non-arXiv shapes.

    This function is intentionally stricter than the benchmark compatibility
    normalizer: it is used to *establish identity*.  A modern-looking substring
    embedded in a DOI, ISSN or arbitrary text must never be admitted.
    """

    text = str(value or "").strip()
    text = re.sub(r"(?i)^arxiv:\s*", "", text).strip()
    if "/abs/" in text:
        text = text.split("/abs/", 1)[1]
    text = text.strip().strip("/")
    text = VERSION_SUFFIX.sub("", text)
    if MODERN_ARXIV.fullmatch(text) or LEGACY_ARXIV.fullmatch(text):
        return text
    return ""


def _pid_objects(product: dict[str, Any]) -> Iterable[dict[str, Any]]:
    """Yield only documented direct scheme/value PID objects.

    OpenAIRE data-model releases use ``pid`` while newer sparse-field naming may
    expose ``pids``.  We accept either container name but never infer identity
    from ``originalIds``, DOI fields, titles, or the raw JSON body.
    """

    for field in ("pid", "pids"):
        raw = product.get(field)
        if isinstance(raw, dict):
            if "scheme" in raw or "value" in raw:
                yield raw
        elif isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    yield item


def extract_structured_arxiv_ids(payload: dict[str, Any]) -> tuple[tuple[str, ...], dict[str, int]]:
    results = payload.get("results")
    if not isinstance(results, list):
        raise ValueError("OpenAIRE response missing results array")

    admitted: dict[str, None] = {}
    pid_objects = 0
    arxiv_scheme_objects = 0
    malformed_arxiv_objects = 0
    products_with_arxiv = 0
    for product in results:
        if not isinstance(product, dict):
            raise ValueError("OpenAIRE results entry is not an object")
        before = len(admitted)
        for pid in _pid_objects(product):
            pid_objects += 1
            scheme = str(pid.get("scheme") or "").strip().casefold()
            if scheme != "arxiv":
                continue
            arxiv_scheme_objects += 1
            normalized = normalize_structured_arxiv(pid.get("value"))
            if not normalized:
                malformed_arxiv_objects += 1
                continue
            admitted.setdefault(normalized, None)
        if len(admitted) > before:
            products_with_arxiv += 1

    return tuple(admitted), {
        "products": len(results),
        "pid_objects_examined": pid_objects,
        "arxiv_scheme_objects": arxiv_scheme_objects,
        "malformed_arxiv_scheme_objects": malformed_arxiv_objects,
        "products_adding_arxiv_identity": products_with_arxiv,
        "unique_arxiv_ids": len(admitted),
    }


def derive_openaire_query(question: str) -> str:
    keyless = _load_keyless()
    terms = keyless._salient_tokens(question, count=4)
    if len(terms) < 2:
        raise ValueError("could not derive at least two gold-blind topical terms")
    return " ".join(terms)


def validate_public_record(record: dict[str, Any]) -> None:
    keyless = _load_keyless()
    if set(record) != {"task_id", "question"}:
        raise AssertionError(f"candidate input schema drift: {sorted(record)}")
    leaked = keyless._hidden_paths(record)
    if leaked:
        raise AssertionError("candidate input contains hidden labels: " + ",".join(leaked))
    if not str(record.get("task_id") or "").strip():
        raise ValueError("public task missing task_id")


def build_url(query: str, *, page_size: int) -> str:
    return OPENAIRE_ENDPOINT + "?" + urllib.parse.urlencode(
        {
            "search": query,
            "type": "publication",
            "page": 1,
            "pageSize": page_size,
        }
    )


def fetch_response(query: str, *, page_size: int) -> tuple[int, bytes, str, str]:
    url = build_url(query, page_size=page_size)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            return int(response.status), response.read(), "", url
    except urllib.error.HTTPError as error:
        return int(error.code), error.read() if error.fp is not None else b"", f"http_error:{error.code}", url
    except (urllib.error.URLError, TimeoutError) as error:
        return 0, b"", f"transport_error:{type(error).__name__}", url


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
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


def run_probe(public_path: Path, freeze_path: Path, out_dir: Path) -> dict[str, Any]:
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze.get("schema_version") != "orion.p2.openaire-identity-probe-freeze.v1":
        raise ValueError("unexpected OpenAIRE identity probe freeze schema")
    if freeze.get("promotion") != "FORBIDDEN_FROM_THIS_PROBE":
        raise ValueError("probe freeze must prohibit publication promotion")

    records = _load_jsonl(public_path)
    by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        validate_public_record(record)
        task_id = str(record["task_id"])
        if task_id in by_id:
            raise ValueError(f"duplicate public task id: {task_id}")
        by_id[task_id] = record

    selected_ids = freeze["selection"]["task_ids"]
    if not isinstance(selected_ids, list) or not selected_ids:
        raise ValueError("freeze has no selected task ids")
    missing = [task_id for task_id in selected_ids if task_id not in by_id]
    if missing:
        raise ValueError(f"frozen task ids absent from public split: {missing[:5]}")

    page_size = int(freeze["provider"]["page_size"])
    out_dir.mkdir(parents=True, exist_ok=True)
    response_dir = out_dir / "responses"
    response_dir.mkdir(parents=True, exist_ok=True)

    traces: list[dict[str, Any]] = []
    http_ok = 0
    tasks_with_identity = 0
    total_admitted = 0
    for task_id in selected_ids:
        record = by_id[task_id]
        question = str(record["question"] or "").strip()
        if not question:
            traces.append(
                {
                    "task_id": task_id,
                    "query": None,
                    "status": "BENCHMARK_EMPTY_QUESTION",
                    "http_status": None,
                    "candidate_arxiv_ids": [],
                    "open_obligations": ["empty_public_question"],
                }
            )
            continue

        query = derive_openaire_query(question)
        status, body, note, url = fetch_response(query, page_size=page_size)
        raw_path = response_dir / f"{task_id}.json"
        if body:
            raw_path.write_bytes(body)
        trace: dict[str, Any] = {
            "task_id": task_id,
            "query": query,
            "url": url,
            "http_status": status,
            "response_sha256": _sha256_bytes(body) if body else None,
            "response_file": str(raw_path.relative_to(out_dir)) if body else None,
            "candidate_arxiv_ids": [],
            "open_obligations": [],
            "note": note,
        }
        if status != 200 or not body:
            trace["status"] = "UNAVAILABLE" if status in (0, 429, 503) else "ERROR"
            trace["open_obligations"].append(f"openaire_transport:{status}:{note}")
            traces.append(trace)
            continue

        http_ok += 1
        try:
            payload = json.loads(body)
            if not isinstance(payload, dict):
                raise ValueError("OpenAIRE JSON root is not an object")
            ids, audit = extract_structured_arxiv_ids(payload)
        except (json.JSONDecodeError, ValueError) as error:
            trace["status"] = "ERROR"
            trace["open_obligations"].append(f"openaire_parse:{type(error).__name__}:{error}")
            traces.append(trace)
            continue

        trace["status"] = "OK"
        trace["candidate_arxiv_ids"] = list(ids)
        trace["identity_audit"] = audit
        if ids:
            tasks_with_identity += 1
            total_admitted += len(ids)
        traces.append(trace)

    trace_path = out_dir / "OPENAIRE_IDENTITY_TRACES.jsonl"
    with trace_path.open("w", encoding="utf-8") as handle:
        for trace in traces:
            handle.write(json.dumps(trace, sort_keys=True) + "\n")

    criterion = freeze["bridge_criterion"]
    selected_n = len(selected_ids)
    http_ok_fraction = http_ok / selected_n if selected_n else 0.0
    observed = (
        http_ok_fraction >= float(criterion["minimum_http_ok_fraction"])
        and tasks_with_identity >= int(criterion["minimum_tasks_with_structured_arxiv_pid"])
    )
    terminal = criterion["positive_terminal"] if observed else criterion["negative_terminal"]
    result = {
        "schema_version": "orion.p2.openaire-identity-probe-result.v1",
        "authority": "DEVELOPMENT_DISCRIMINATOR_NOT_SCIENTIFIC_RESULT",
        "terminal": terminal,
        "promotion": "FORBIDDEN_FROM_THIS_PROBE",
        "public_split_sha256": _sha256_file(public_path),
        "freeze_sha256": _sha256_file(freeze_path),
        "selection": {
            "n": selected_n,
            "task_ids": selected_ids,
        },
        "transport": {
            "http_ok": http_ok,
            "http_ok_fraction": round(http_ok_fraction, 6),
        },
        "identity": {
            "tasks_with_structured_arxiv_pid": tasks_with_identity,
            "unique_ids_total_across_tasks": total_admitted,
            "raw_regex_identity_extraction": False,
            "accepted_scheme": "arxiv",
        },
        "frozen_criterion": criterion,
        "trace_sha256": _sha256_file(trace_path),
    }
    (out_dir / "OPENAIRE_IDENTITY_PROBE_RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("P2_OPENAIRE_IDENTITY_PROBE=" + json.dumps(result, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", required=True, type=Path)
    parser.add_argument("--freeze", type=Path, default=DEFAULT_FREEZE)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    run_probe(args.public, args.freeze, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
