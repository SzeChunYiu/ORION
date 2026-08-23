#!/usr/bin/env python3
"""Run P2 Wide V2 with transport-valid repeated OpenAIRE pid parameters.

V1 is retained as an immutable CANNOT_CHECK campaign.  V2 changes only the
DOI-to-OpenAIRE transport encoding and binds a pre-benchmark public transport
probe.  Candidate projections, budgets, identity admission and scientific
thresholds are inherited unchanged from the frozen matched campaign.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
V1_PATH = HERE / "run_autoresearchbench_wide_openaire_matched.py"
PAPER = HERE.parent
DEFAULT_FREEZE = PAPER / "protocol" / "P2_WIDE_OPENAIRE_MATCHED_FREEZE_V2.json"
DEFAULT_IDENTITY_RECEIPT = PAPER / "evidence" / "external_results" / "P2_OPENAIRE_IDENTITY_PROBE_V1.json"
EXPECTED_SCHEMA = "orion.p2.wide-openaire-matched-freeze.v2"
PROBE_SCHEMA = "orion.p2.openaire-repeated-pid-transport-probe.v1"
PROBE_TERMINAL = "OPENAIRE_REPEATED_PID_TRANSPORT_VALID"
TRANSPORT_PROBE_PAGE_SIZE = 10


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


v1 = _load_module("orion_p2_wide_openaire_matched_v1_for_v2", V1_PATH)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _is_sha256_hex(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return value == value.lower()


def build_openaire_crosswalk_url(dois: Iterable[str], *, page_size: int) -> str:
    """Encode OR semantics as repeated pid parameters, not an expression parser input."""
    normalized = [v1.normalize_doi(doi) for doi in dois]
    normalized = list(dict.fromkeys(doi for doi in normalized if doi))[:20]
    if not normalized:
        raise ValueError("OpenAIRE DOI crosswalk requires at least one DOI")
    params: list[tuple[str, str | int]] = [("pid", doi) for doi in normalized]
    params.extend((("type", "publication"), ("page", 1), ("pageSize", page_size)))
    return v1.OPENAIRE_ENDPOINT + "?" + urllib.parse.urlencode(params)


def extract_requested_doi_matches(
    payload: dict[str, Any], requested_dois: Iterable[str]
) -> tuple[str, ...]:
    """Return requested DOIs explicitly present in structured OpenAIRE PID objects."""
    requested = [v1.normalize_doi(doi) for doi in requested_dois]
    requested = list(dict.fromkeys(doi for doi in requested if doi))
    expected = set(requested)
    results = payload.get("results")
    if not isinstance(results, list):
        raise ValueError("OpenAIRE transport response missing results array")
    matched: set[str] = set()
    for product in results:
        if not isinstance(product, dict):
            raise ValueError("OpenAIRE transport result is not an object")
        for field in ("pid", "pids"):
            raw = product.get(field)
            items = [raw] if isinstance(raw, dict) else raw if isinstance(raw, list) else []
            for item in items:
                if not isinstance(item, dict):
                    continue
                scheme = str(item.get("scheme") or "").strip().casefold()
                if scheme not in {"doi", "digital object identifier"}:
                    continue
                doi = v1.normalize_doi(item.get("value"))
                if doi in expected:
                    matched.add(doi)
    return tuple(doi for doi in requested if doi in matched)


def validate_transport_probe(path: Path, freeze: dict[str, Any]) -> dict[str, Any]:
    probe = json.loads(path.read_text(encoding="utf-8"))
    transport = freeze["transport_repair_evidence"]
    if transport.get("pre_benchmark_probe_required") is not True:
        raise ValueError("V2 freeze does not require a pre-benchmark transport probe")
    if transport.get("probe_gold_access") != "NONE":
        raise ValueError("V2 freeze does not forbid benchmark-gold access in the transport probe")
    if probe.get("schema_version") != PROBE_SCHEMA:
        raise ValueError("V2 transport probe schema mismatch")
    if probe.get("terminal") != PROBE_TERMINAL:
        raise ValueError("V2 transport probe did not reach the required terminal")
    if int(probe.get("http_status", 0)) != 200:
        raise ValueError("V2 transport probe did not return HTTP 200")
    if probe.get("encoding") != "repeated_pid_parameters":
        raise ValueError("V2 transport probe encoding mismatch")
    expected = list(transport["probe_dois"])
    if list(probe.get("dois", [])) != expected:
        raise ValueError("V2 transport probe DOI set drifted from freeze")
    expected_url = build_openaire_crosswalk_url(expected, page_size=TRANSPORT_PROBE_PAGE_SIZE)
    expected_url_sha256 = hashlib.sha256(expected_url.encode()).hexdigest()
    if probe.get("url_sha256") != expected_url_sha256:
        raise ValueError("V2 transport probe URL digest does not bind the canonical repeated-pid request")
    if not _is_sha256_hex(probe.get("response_sha256")):
        raise ValueError("V2 transport probe response hash is not canonical SHA-256 hex")
    if probe.get("benchmark_gold_accessed") is not False:
        raise ValueError("V2 transport probe must explicitly attest that benchmark gold was not accessed")
    if probe.get("promotion_authorized") is not False:
        raise ValueError("V2 transport probe cannot grant scientific promotion authority")
    minimum_result_count = transport.get("probe_min_result_count")
    if type(minimum_result_count) is not int or minimum_result_count < 1:
        raise ValueError("V2 freeze does not require a positive transport-probe identity yield")
    result_count = probe.get("result_count")
    if type(result_count) is not int or result_count < minimum_result_count:
        raise ValueError("V2 transport probe did not return the frozen minimum identity yield")
    minimum_matched_doi_count = transport.get("probe_min_matched_doi_count")
    if type(minimum_matched_doi_count) is not int or minimum_matched_doi_count < 1:
        raise ValueError("V2 freeze does not require a requested DOI identity match")
    matched_dois = probe.get("matched_dois")
    if not isinstance(matched_dois, list):
        raise ValueError("V2 transport probe does not bind matched DOI identities")
    normalized_matched = [v1.normalize_doi(doi) for doi in matched_dois]
    if any(not doi for doi in normalized_matched):
        raise ValueError("V2 transport probe matched DOI list is malformed")
    if matched_dois != normalized_matched:
        raise ValueError("V2 transport probe matched DOI list is not canonical normalized DOI text")
    if len(normalized_matched) != len(set(normalized_matched)):
        raise ValueError("V2 transport probe matched DOI list contains duplicates")
    normalized_expected = [v1.normalize_doi(doi) for doi in expected]
    if any(not doi for doi in normalized_expected):
        raise ValueError("V2 freeze transport probe DOI list is malformed")
    expected_set = set(normalized_expected)
    if any(doi not in expected_set for doi in normalized_matched):
        raise ValueError("V2 transport probe matched DOI is outside the frozen request")
    canonical_order = [doi for doi in normalized_expected if doi in set(normalized_matched)]
    if normalized_matched != canonical_order:
        raise ValueError("V2 transport probe matched DOI list does not follow frozen request order")
    if len(normalized_matched) < minimum_matched_doi_count:
        raise ValueError("V2 transport probe did not match the frozen minimum requested DOI count")
    return probe


def validate_transport_response(
    path: Path, probe: dict[str, Any], freeze: dict[str, Any]
) -> dict[str, Any]:
    """Bind the archived raw OpenAIRE response to the receipt and requested DOI identities."""
    body = path.read_bytes()
    actual_sha = hashlib.sha256(body).hexdigest()
    if actual_sha != probe.get("response_sha256"):
        raise ValueError("V2 archived transport response hash does not match receipt")
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise ValueError("V2 archived transport response root is not an object")
    results = payload.get("results")
    if not isinstance(results, list):
        raise ValueError("V2 archived transport response missing results array")
    if len(results) != probe.get("result_count"):
        raise ValueError("V2 archived transport response count does not match receipt")
    matched = list(
        extract_requested_doi_matches(
            payload, freeze["transport_repair_evidence"]["probe_dois"]
        )
    )
    if matched != list(probe.get("matched_dois", [])):
        raise ValueError("V2 archived transport response DOI matches do not match receipt")
    minimum = freeze["transport_repair_evidence"].get("probe_min_matched_doi_count")
    if type(minimum) is not int or minimum < 1 or len(matched) < minimum:
        raise ValueError("V2 archived transport response does not prove a requested DOI match")
    return payload


def acquire_task_v2(*args: Any, **kwargs: Any) -> dict[str, Any]:
    old = v1.build_openaire_crosswalk_url
    v1.build_openaire_crosswalk_url = build_openaire_crosswalk_url
    try:
        return v1.acquire_task(*args, **kwargs)
    finally:
        v1.build_openaire_crosswalk_url = old


def run(
    public_path: Path,
    freeze_path: Path,
    identity_receipt_path: Path,
    transport_probe_path: Path,
    out_dir: Path,
) -> dict[str, Any]:
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze.get("schema_version") != EXPECTED_SCHEMA:
        raise ValueError("unexpected matched Wide V2 freeze schema")
    if not freeze.get("frozen_before_official_score"):
        raise ValueError("matched Wide V2 protocol is not prospectively frozen")
    crosswalk = freeze["acquisition"]["openaire"]["crosswalk"]
    if crosswalk.get("transport_encoding") != "repeated_pid_parameters":
        raise ValueError("V2 requires repeated pid transport encoding")
    probe = validate_transport_probe(transport_probe_path, freeze)

    identity_receipt = json.loads(identity_receipt_path.read_text(encoding="utf-8"))
    required = freeze["parent_identity_receipt"]["terminal_required"]
    if identity_receipt.get("authority") != required or identity_receipt.get("outcome", {}).get("terminal") != required:
        raise ValueError("parent structured identity bridge is not authorized")

    rows = v1.load_jsonl(public_path)
    v1.validate_public_rows(rows)
    expected_rows = int(freeze["benchmark"]["released_wide_rows"])
    if len(rows) != expected_rows:
        raise ValueError(f"expected {expected_rows} Wide public rows, got {len(rows)}")

    out_dir.mkdir(parents=True, exist_ok=True)
    response_dir = out_dir / "responses"
    capture_path = out_dir / "SHARED_ACQUISITION_CAPTURE.jsonl"
    clock = v1.HostClock()
    captures: list[dict[str, Any]] = []
    with capture_path.open("w", encoding="utf-8") as capture_handle:
        for index, row in enumerate(rows, start=1):
            capture = acquire_task_v2(
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
                print(f"P2_WIDE_V2_CAPTURE {index}/{len(rows)} ok={ok}/{calls}", flush=True)

    cap = int(freeze["acquisition"]["max_candidates_per_system"])
    candidate_hashes: dict[str, str] = {}
    system_summaries: dict[str, Any] = {}
    for system_id in v1.SYSTEM_IDS:
        candidate_rows: list[dict[str, Any]] = []
        projection_rows: list[dict[str, Any]] = []
        for capture in captures:
            empty = not str(capture["question"]).strip()
            candidates = [] if empty else v1.project_candidates(capture, system_id=system_id, cap=cap)
            if len(candidates) > cap:
                raise AssertionError("candidate cap exceeded")
            candidate_rows.append(v1.scorer_record(str(capture["question"]), candidates, empty=empty))
            projection_rows.append({
                "task_id": capture["task_id"],
                "system_id": system_id,
                "candidate_arxiv_ids": candidates,
                "candidate_count": len(candidates),
                "same_shared_capture": True,
                "cross_backend_confirmed_ids": capture["cross_backend_confirmed_ids"],
                "open_obligations": capture["open_obligations"],
            })
        candidate_path = out_dir / f"candidate_{system_id}.jsonl"
        projection_path = out_dir / f"projection_{system_id}.jsonl"
        v1.write_jsonl(candidate_path, candidate_rows)
        v1.write_jsonl(projection_path, projection_rows)
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
        "campaign_version": 2,
        "authority": "CANDIDATE_CAPTURE_FROZEN_BEFORE_EVALUATOR_GOLD",
        "freeze_sha256": sha256_file(freeze_path),
        "identity_receipt_sha256": sha256_file(identity_receipt_path),
        "transport_probe_sha256": sha256_file(transport_probe_path),
        "transport_probe_response_sha256": probe["response_sha256"],
        "transport_probe_terminal": probe["terminal"],
        "transport_encoding": "repeated_pid_parameters",
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
    print("P2_WIDE_V2_CAPTURE_TERMINAL=" + json.dumps(manifest, sort_keys=True), flush=True)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", required=True, type=Path)
    parser.add_argument("--freeze", type=Path, default=DEFAULT_FREEZE)
    parser.add_argument("--identity-receipt", type=Path, default=DEFAULT_IDENTITY_RECEIPT)
    parser.add_argument("--transport-probe", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    run(args.public, args.freeze, args.identity_receipt, args.transport_probe, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())