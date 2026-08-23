#!/usr/bin/env python3
"""Gold-blind P2 V3 transport prerequisite for OpenAIRE V4 DOI filtering.

This probe is deliberately not a benchmark run. It validates one documented
DOI-filter request, persists the exact provider body before checking its yield,
and emits a final receipt only after independently re-reading those bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
V2_RUNNER_PATH = HERE / "run_autoresearchbench_wide_openaire_matched_v2.py"
DEFAULT_FREEZE = PAPER / "protocol" / "P2_WIDE_OPENAIRE_MATCHED_FREEZE_V3.json"
V4_ENDPOINT = "https://api-beta.openaire.eu/graph/v4/research-products"
SCHEMA = "orion.p2.openaire-v4-doi-filter-transport-probe.v1"
TERMINAL = "OPENAIRE_V4_DOI_FILTER_TRANSPORT_VALID"
USER_AGENT = "ORION-P2-research/0.1 (+https://github.com/SzeChunYiu/ORION)"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


v2 = _load_module("orion_p2_v2_for_v4_transport_probe", V2_RUNNER_PATH)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_blob_sha1(path: Path) -> str:
    body = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()


def _normalized_unique(dois: Iterable[str]) -> list[str]:
    normalized = [v2.v1.normalize_doi(doi) for doi in dois]
    return list(dict.fromkeys(doi for doi in normalized if doi))


def build_v4_crosswalk_url(dois: Iterable[str], *, page_size: int) -> str:
    normalized = _normalized_unique(dois)[:20]
    if not normalized:
        raise ValueError("V4 DOI crosswalk requires at least one canonical DOI")
    filter_value = "ids.doi:" + "|".join(normalized) + ",type:publication"
    params = [
        ("filter", filter_value),
        ("page", 1),
        ("page_size", page_size),
        ("select", "id,pids,type"),
    ]
    return V4_ENDPOINT + "?" + urllib.parse.urlencode(params)


def extract_requested_doi_matches(
    payload: dict[str, Any], requested_dois: Iterable[str]
) -> tuple[str, ...]:
    # V2's extractor already accepts both documented pid and pids containers and
    # admits only structured DOI scheme/value objects.
    return v2.extract_requested_doi_matches(payload, requested_dois)


def load_and_validate_freeze(path: Path) -> dict[str, Any]:
    freeze = json.loads(path.read_text(encoding="utf-8"))
    if freeze.get("schema_version") != "orion.p2.wide-openaire-matched-freeze.v3":
        raise ValueError("unexpected P2 V3 freeze schema")
    if freeze.get("frozen_before_any_v3_scientific_outcome") is not True:
        raise ValueError("V3 is not prospectively frozen")
    parent = freeze["parent_v2"]
    parent_path = PAPER / "protocol" / Path(parent["path"]).name
    actual_blob = git_blob_sha1(parent_path)
    if actual_blob != parent.get("git_blob_sha"):
        raise ValueError(f"V2 parent freeze drift: {actual_blob} != {parent.get('git_blob_sha')}")
    change = freeze["v3_transport_change"]
    if change.get("change_class") != "DOI_CROSSWALK_TRANSPORT_ONLY":
        raise ValueError("V3 transport-change class drift")
    if change.get("crosswalk_endpoint") != V4_ENDPOINT:
        raise ValueError("V3 V4 crosswalk endpoint drift")
    if change.get("filter_grammar") != "ids.doi:<doi1>|<doi2>|...,type:publication":
        raise ValueError("V3 V4 filter grammar drift")
    probe = freeze["transport_probe"]
    if probe.get("benchmark_gold_access") != "NONE":
        raise ValueError("V3 transport probe does not prohibit benchmark gold")
    if probe.get("raw_response_must_be_written_before_http_or_yield_assertion") is not True:
        raise ValueError("V3 does not require raw-before-validation custody")
    if probe.get("pending_receipt_must_be_written_before_yield_assertion") is not True:
        raise ValueError("V3 does not require a pre-yield pending receipt")
    if probe.get("final_receipt_only_after_raw_response_revalidation") is not True:
        raise ValueError("V3 does not require score-like raw response revalidation")
    return freeze


def validate_final_receipt(
    receipt_path: Path, raw_response_path: Path, freeze: dict[str, Any]
) -> dict[str, Any]:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    probe = freeze["transport_probe"]
    expected_dois = list(probe["probe_dois"])
    if receipt.get("schema_version") != SCHEMA:
        raise ValueError("V3 transport receipt schema mismatch")
    if receipt.get("terminal") != TERMINAL:
        raise ValueError("V3 transport receipt did not reach positive transport terminal")
    if receipt.get("benchmark_gold_accessed") is not False:
        raise ValueError("V3 transport receipt does not attest gold blindness")
    if receipt.get("promotion_authorized") is not False:
        raise ValueError("V3 transport receipt improperly grants scientific authority")
    if receipt.get("crosswalk_endpoint") != V4_ENDPOINT:
        raise ValueError("V3 receipt endpoint mismatch")
    if list(receipt.get("dois", [])) != expected_dois:
        raise ValueError("V3 receipt DOI list drift")
    expected_url = build_v4_crosswalk_url(expected_dois, page_size=int(probe["page_size"]))
    if receipt.get("url_sha256") != sha256_bytes(expected_url.encode()):
        raise ValueError("V3 receipt does not bind canonical V4 request")
    body = raw_response_path.read_bytes()
    if receipt.get("response_sha256") != sha256_bytes(body):
        raise ValueError("V3 receipt/raw response hash mismatch")
    if int(receipt.get("http_status", 0)) != 200:
        raise ValueError("V3 transport receipt lacks HTTP 200")
    payload = json.loads(body)
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ValueError("V3 raw response missing results array")
    if len(payload["results"]) != receipt.get("result_count"):
        raise ValueError("V3 receipt result count does not match raw response")
    if len(payload["results"]) < int(probe["minimum_result_count"]):
        raise ValueError("V3 transport response below frozen minimum yield")
    matched = list(extract_requested_doi_matches(payload, expected_dois))
    if matched != list(receipt.get("matched_dois", [])):
        raise ValueError("V3 receipt matched DOI list does not match raw response")
    if len(matched) < int(probe["minimum_requested_doi_matches"]):
        raise ValueError("V3 transport response lacks frozen requested DOI match")
    return receipt


def capture_probe(freeze_path: Path, out_dir: Path) -> dict[str, Any]:
    freeze = load_and_validate_freeze(freeze_path)
    probe = freeze["transport_probe"]
    dois = list(probe["probe_dois"])
    url = build_v4_crosswalk_url(dois, page_size=int(probe["page_size"]))
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    status = 0
    body = b""
    note = ""
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = int(response.status)
            body = response.read()
    except urllib.error.HTTPError as error:
        status = int(error.code)
        body = error.read() if error.fp is not None else b""
        note = f"http_error:{error.code}"
    except (urllib.error.URLError, TimeoutError) as error:
        note = f"transport_error:{type(error).__name__}"

    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "transport_probe_response.json"
    pending_path = out_dir / "transport_probe.pending.json"
    final_path = out_dir / "transport_probe.json"

    # Custody order is authority-bearing: bytes and a pending receipt exist before
    # any HTTP/yield/identity assertion can terminate this process.
    raw_path.write_bytes(body)
    pending = {
        "schema_version": SCHEMA,
        "terminal": "PENDING_VALIDATION",
        "http_status": status,
        "note": note,
        "crosswalk_endpoint": V4_ENDPOINT,
        "crosswalk_api_status": "BETA",
        "encoding": "v4_filter_ids_doi_or_list",
        "dois": dois,
        "url_sha256": sha256_bytes(url.encode()),
        "response_sha256": sha256_bytes(body),
        "response_bytes": len(body),
        "result_count": None,
        "matched_dois": [],
        "benchmark_gold_accessed": False,
        "promotion_authorized": False,
    }
    pending_path.write_text(json.dumps(pending, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if status != 200:
        raise RuntimeError(f"V3 transport probe HTTP terminal: status={status} note={note}")
    payload = json.loads(body)
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ValueError("V3 OpenAIRE V4 response missing results array")
    result_count = len(payload["results"])
    matched = list(extract_requested_doi_matches(payload, dois))
    if result_count < int(probe["minimum_result_count"]):
        raise ValueError(f"V3 transport probe zero/low yield: {result_count}")
    if len(matched) < int(probe["minimum_requested_doi_matches"]):
        raise ValueError(f"V3 transport probe has no requested structured DOI match: {matched}")

    final = dict(pending)
    final.update({"terminal": TERMINAL, "result_count": result_count, "matched_dois": matched})
    final_path.write_text(json.dumps(final, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validate_final_receipt(final_path, raw_path, freeze)
    print("P2_WIDE_V3_TRANSPORT_PROBE=" + json.dumps(final, sort_keys=True), flush=True)
    return final


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", type=Path, default=DEFAULT_FREEZE)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    capture_probe(args.freeze, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
