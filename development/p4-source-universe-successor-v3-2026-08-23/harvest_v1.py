#!/usr/bin/env python3
"""Bounded public-metadata harvest frozen by PROTOCOL_V1.json.

This is a source-feasibility collector only. It never downloads research files,
accesses outcomes, adjudicates natural-pair eligibility, or creates target labels.
"""

from __future__ import annotations

import concurrent.futures
import datetime as dt
import hashlib
import json
import os
import pathlib
import threading
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parent
RAW = ROOT / "raw"
INDEX = ROOT / "RAW_RESPONSE_INDEX_V1.jsonl"
ERRORS = ROOT / "TRANSPORT_ERRORS_V1.jsonl"
USER_AGENT = "ORION-P4-public-source-feasibility/1.0 (bounded metadata audit)"
MAX_WORKERS = 4
_lock = threading.Lock()
_rate_lock = threading.Lock()
_last_request_monotonic = 0.0
MIN_REQUEST_INTERVAL_SECONDS = 0.25


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_name(value: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in value)[:180]


def append_jsonl(path: pathlib.Path, row: dict) -> None:
    with _lock:
        with path.open("ab") as handle:
            handle.write(canonical_json(row))


def capture(
    *,
    provider: str,
    purpose: str,
    relpath: str,
    url: str,
    method: str = "GET",
    body: dict | None = None,
    retries: int = 3,
) -> object | None:
    global _last_request_monotonic
    destination = RAW / relpath
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        try:
            return json.loads(destination.read_bytes())
        except json.JSONDecodeError:
            destination.unlink()
    encoded = canonical_json(body).rstrip(b"\n") if body is not None else None
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if encoded is not None:
        headers["Content-Type"] = "application/json"
    last_error = None
    for attempt in range(1, retries + 1):
        started = now()
        try:
            with _rate_lock:
                elapsed = time.monotonic() - _last_request_monotonic
                if elapsed < MIN_REQUEST_INTERVAL_SECONDS:
                    time.sleep(MIN_REQUEST_INTERVAL_SECONDS - elapsed)
                _last_request_monotonic = time.monotonic()
            request = urllib.request.Request(url, data=encoded, headers=headers, method=method)
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
                status = int(response.status)
                media_type = response.headers.get_content_type()
                final_url = response.geturl()
            parsed = json.loads(raw)
            destination.write_bytes(raw)
            append_jsonl(
                INDEX,
                {
                    "provider": provider,
                    "purpose": purpose,
                    "request_url": url,
                    "final_url": final_url,
                    "method": method,
                    "request_body": body,
                    "captured_at": started,
                    "http_status": status,
                    "media_type": media_type,
                    "bytes": len(raw),
                    "sha256": sha256(raw),
                    "path": str(destination.relative_to(ROOT)),
                    "attempt": attempt,
                },
            )
            return parsed
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                if isinstance(exc, urllib.error.HTTPError) and exc.code in (403, 429, 503):
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    try:
                        pause = float(retry_after) if retry_after else 20.0 * attempt
                    except ValueError:
                        pause = 20.0 * attempt
                    time.sleep(min(pause, 90.0))
                else:
                    time.sleep(1.5 * attempt)
    append_jsonl(
        ERRORS,
        {
            "provider": provider,
            "purpose": purpose,
            "request_url": url,
            "method": method,
            "request_body": body,
            "failed_at": now(),
            "attempts": retries,
            "error": last_error,
            "terminal": "CANNOT_CHECK_TRANSPORT",
        },
    )
    return None


def load_protocol() -> dict:
    return json.loads((ROOT / "PROTOCOL_V1.json").read_text())


def harvest_dryad(protocol: dict) -> dict:
    spec = protocol["provider_freeze"]["DRYAD"]
    records: list[dict] = []
    failed_pages: list[int] = []
    for page in spec["requests"]["pages"]:
        query = urllib.parse.urlencode({"page": page, "per_page": spec["requests"]["per_page"]})
        payload = capture(
            provider="DRYAD",
            purpose="bounded_dataset_page",
            relpath=f"dryad/datasets_page_{page:03d}.json",
            url=f"{spec['endpoint']}?{query}",
        )
        if not isinstance(payload, dict):
            failed_pages.append(page)
            continue
        records.extend(payload.get("_embedded", {}).get("stash:datasets", []))
    return {"records": records, "failed_pages": failed_pages}


def harvest_figshare(protocol: dict) -> dict:
    spec = protocol["provider_freeze"]["FIGSHARE"]
    lexicons = protocol["discovery_lexicons"]
    hits: dict[int, dict] = {}
    failed_queries: list[dict] = []
    for domain, lexicon in lexicons.items():
        for query in lexicon["queries"]:
            for item_type, mechanism in spec["item_types"].items():
                body = dict(spec["request_body"])
                body.update({"search_for": query, "item_type": int(item_type)})
                stem = f"{domain.lower()}__{safe_name(query)}__type_{item_type}"
                payload = capture(
                    provider="FIGSHARE",
                    purpose="frozen_domain_item_type_search",
                    relpath=f"figshare/search/{stem}.json",
                    url=spec["search_endpoint"],
                    method="POST",
                    body=body,
                )
                if not isinstance(payload, list):
                    failed_queries.append({"domain": domain, "query": query, "item_type": item_type})
                    continue
                for item in payload:
                    article_id = item.get("id")
                    if not isinstance(article_id, int):
                        continue
                    row = hits.setdefault(article_id, {"search_item": item, "memberships": []})
                    row["memberships"].append({"domain": domain, "query": query, "item_type": int(item_type), "mechanism": mechanism})

    skip_missing = os.environ.get("P4_SKIP_FIGSHARE_MISSING") == "1"

    def one(article_id: int) -> tuple[int, object | None]:
        destination = RAW / f"figshare/records/{article_id}.json"
        if skip_missing and not destination.exists():
            return article_id, None
        url = spec["full_record_endpoint_template"].format(article_id=article_id)
        payload = capture(
            provider="FIGSHARE",
            purpose="full_item_metadata",
            relpath=f"figshare/records/{article_id}.json",
            url=url,
        )
        return article_id, payload

    full: dict[int, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(one, article_id) for article_id in sorted(hits)]
        for future in concurrent.futures.as_completed(futures):
            article_id, payload = future.result()
            if isinstance(payload, dict):
                full[article_id] = payload
    return {"hits": hits, "records": full, "failed_queries": failed_queries, "failed_records": sorted(set(hits) - set(full))}


def harvest_dataverse(protocol: dict) -> dict:
    spec = protocol["provider_freeze"]["HARVARD_DATAVERSE"]
    lexicons = protocol["discovery_lexicons"]
    hits: dict[str, dict] = {}
    failed_queries: list[dict] = []
    for domain, lexicon in lexicons.items():
        for query in lexicon["queries"]:
            params = dict(spec["request_parameters"])
            params["q"] = query
            url = f"{spec['search_endpoint']}?{urllib.parse.urlencode(params)}"
            stem = f"{domain.lower()}__{safe_name(query)}"
            payload = capture(
                provider="HARVARD_DATAVERSE",
                purpose="frozen_domain_dataset_search",
                relpath=f"dataverse/search/{stem}.json",
                url=url,
            )
            if not isinstance(payload, dict) or payload.get("status") != "OK":
                failed_queries.append({"domain": domain, "query": query})
                continue
            for item in payload.get("data", {}).get("items", []):
                persistent_id = item.get("global_id")
                if not isinstance(persistent_id, str) or not persistent_id.lower().startswith("doi:"):
                    continue
                row = hits.setdefault(persistent_id, {"search_item": item, "memberships": []})
                row["memberships"].append({"domain": domain, "query": query})

    skip_missing = os.environ.get("P4_SKIP_DATAVERSE_MISSING") == "1"

    def one(persistent_id: str) -> tuple[str, object | None]:
        destination = RAW / f"dataverse/records/{safe_name(persistent_id)}.json"
        if skip_missing and not destination.exists():
            return persistent_id, None
        base = spec["full_record_endpoint_template"].split("?", 1)[0]
        url = f"{base}?{urllib.parse.urlencode({'persistentId': persistent_id})}"
        payload = capture(
            provider="HARVARD_DATAVERSE",
            purpose="full_dataset_metadata",
            relpath=f"dataverse/records/{safe_name(persistent_id)}.json",
            url=url,
        )
        return persistent_id, payload

    full: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(one, persistent_id) for persistent_id in sorted(hits)]
        for future in concurrent.futures.as_completed(futures):
            persistent_id, payload = future.result()
            if isinstance(payload, dict) and payload.get("status") == "OK":
                full[persistent_id] = payload
    return {"hits": hits, "records": full, "failed_queries": failed_queries, "failed_records": sorted(set(hits) - set(full))}


def harvest_datacite(protocol: dict) -> dict:
    spec = protocol["provider_freeze"]["DATACITE"]
    lexicons = protocol["discovery_lexicons"]
    record_ids: set[str] = set()
    host_counts: dict[str, int] = {}
    failed_queries: list[dict] = []
    for domain, lexicon in lexicons.items():
        for query_term in lexicon["queries"]:
            for resource_type in ("Dataset", "Software"):
                query = (
                    f"types.resourceTypeGeneral:{resource_type} AND "
                    "relatedIdentifiers.relationType:IsSupplementTo AND "
                    f"titles.title:{query_term}"
                )
                params = {
                    "query": query,
                    "page[size]": spec["request_parameters"]["page_size"],
                    "page[number]": spec["request_parameters"]["page_number"],
                }
                url = f"{spec['endpoint']}?{urllib.parse.urlencode(params)}"
                stem = f"{domain.lower()}__{safe_name(query_term)}__{resource_type.lower()}"
                payload = capture(
                    provider="DATACITE",
                    purpose="discovery_cross_check_only",
                    relpath=f"datacite/search/{stem}.json",
                    url=url,
                )
                if not isinstance(payload, dict):
                    failed_queries.append({"domain": domain, "query": query_term, "resource_type": resource_type})
                    continue
                for item in payload.get("data", []):
                    identifier = item.get("id")
                    if isinstance(identifier, str):
                        record_ids.add(identifier.lower())
                    host = urllib.parse.urlparse(item.get("attributes", {}).get("url") or "").hostname or "MISSING_HOST"
                    host_counts[host] = host_counts.get(host, 0) + 1
    return {"unique_discovery_dois": sorted(record_ids), "host_hit_counts": dict(sorted(host_counts.items())), "failed_queries": failed_queries}


def main() -> None:
    protocol = load_protocol()
    RAW.mkdir(parents=True, exist_ok=True)
    INDEX.touch(exist_ok=True)
    ERRORS.touch(exist_ok=True)
    started = now()
    dryad = harvest_dryad(protocol)
    figshare = harvest_figshare(protocol)
    dataverse = harvest_dataverse(protocol)
    datacite = harvest_datacite(protocol)

    bundle = {
        "schema_version": "orion.p4.source-universe-harvest-bundle.v1",
        "started_at": started,
        "completed_at": now(),
        "protocol_sha256": sha256((ROOT / "PROTOCOL_V1.json").read_bytes()),
        "public_development_evidence_only": True,
        "outcomes_accessed": False,
        "dryad": dryad,
        "figshare": figshare,
        "dataverse": dataverse,
        "datacite": datacite,
    }
    (ROOT / "HARVEST_BUNDLE_V1.json").write_bytes(canonical_json(bundle))
    receipt = {
        "schema_version": "orion.p4.source-universe-harvest-receipt.v1",
        "started_at": started,
        "completed_at": bundle["completed_at"],
        "protocol_sha256": bundle["protocol_sha256"],
        "raw_response_count": sum(1 for _ in INDEX.open()),
        "transport_error_count": sum(1 for line in ERRORS.open() if line.strip()),
        "provider_counts": {
            "DRYAD": {"records": len(dryad["records"]), "failed_pages": len(dryad["failed_pages"])},
            "FIGSHARE": {"search_unique_ids": len(figshare["hits"]), "full_records": len(figshare["records"]), "failed_queries": len(figshare["failed_queries"]), "failed_records": len(figshare["failed_records"])},
            "HARVARD_DATAVERSE": {"search_unique_ids": len(dataverse["hits"]), "full_records": len(dataverse["records"]), "failed_queries": len(dataverse["failed_queries"]), "failed_records": len(dataverse["failed_records"])},
            "DATACITE": {"unique_discovery_dois": len(datacite["unique_discovery_dois"]), "failed_queries": len(datacite["failed_queries"]), "counting_authority": False},
        },
        "harvest_bundle_sha256": sha256((ROOT / "HARVEST_BUNDLE_V1.json").read_bytes()),
        "terminal_if_errors": "CANNOT_CHECK_TRANSPORT",
    }
    (ROOT / "HARVEST_RECEIPT_V1.json").write_bytes(canonical_json(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
