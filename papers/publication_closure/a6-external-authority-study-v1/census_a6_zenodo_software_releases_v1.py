#!/usr/bin/env python3
"""Outcome-blind A6 stratum-1 census: Zenodo software release transitions.

Enumerates open Zenodo software record families (conceptrecid), requires a
licence on both selected versions (rights permit), and takes the two most
recent versions ordered by (publication_date, record id) as the release
transition. Content identity is a durable digest over each version's public
files manifest (key, size, md5 checksum) plus record id and version tag; no
file payload is downloaded. No stratum eligibility, gold label, prediction or
outcome is read or produced.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SNAPSHOT_DIR = HERE / "zenodo-census-v1"
STRATUM = "scientific_software_release_provenance_attestation"
UA = "ORION-A6-stratum1-census-v1/1.0 (mailto:orion-a6@example.org)"
API = "https://zenodo.org/api/records"
MAX_BYTES = 32 * 1024 * 1024
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def request_json(url: str, *, timeout: float = 40.0, retries: int = 6) -> Any:
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if getattr(response, "status", 200) != 200:
                    raise RuntimeError(f"HTTP {response.status} for {url}")
                data = response.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise RuntimeError(f"response too large for census: {url}")
                return json.loads(data)
        except (urllib.error.URLError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
            last = exc
            if attempt + 1 < retries:
                # Zenodo intermittently 504s on the sorted scan query; back off
                # exponentially (1,2,4,8,16s) so a transient gateway overload
                # clears instead of aborting the stratum universe enumeration.
                time.sleep(2 ** attempt)
    raise RuntimeError(f"failed to fetch {url}: {last}")


def paginate(url: str, *, page_param: str = "page", max_pages: int = 60, stop_after: int | None = None) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    page = 1
    for _ in range(max_pages):
        separator = "&" if urllib.parse.urlparse(url).query else "?"
        payload = request_json(f"{url}{separator}{page_param}={page}")
        batch = payload.get("hits", {}).get("hits", [])
        hits.extend(item for item in batch if isinstance(item, dict))
        if not batch:
            break
        if stop_after is not None and len(hits) >= stop_after:
            break
        page += 1
    else:
        raise RuntimeError(f"pagination hit max_pages before exhaustion: {url}")
    return hits


def license_id(record: dict[str, Any]) -> str | None:
    lic = (record.get("metadata") or {}).get("license")
    if isinstance(lic, dict):
        value = lic.get("id") or lic.get("title")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def files_manifest_digest(record: dict[str, Any]) -> str | None:
    files = record.get("files")
    if not isinstance(files, list) or not files:
        return None
    entries = []
    for f in files:
        if not isinstance(f, dict):
            continue
        entries.append({
            "key": f.get("key"),
            "size": f.get("size"),
            "checksum": f.get("checksum"),
        })
    if not entries:
        return None
    entries.sort(key=lambda e: str(e.get("key")))
    core = {
        "record_id": str(record.get("id")),
        "conceptrecid": str(record.get("conceptrecid")),
        "version": (record.get("metadata") or {}).get("version"),
        "files": entries,
    }
    return canonical_json_sha(core)


def version_sort_key(record: dict[str, Any]) -> tuple[str, int]:
    metadata = record.get("metadata") or {}
    pub = metadata.get("publication_date") or ""
    rid = record.get("id")
    return (str(pub), int(rid) if str(rid).isdigit() else 0)


def fetch_family_versions(conceptrecid: str) -> list[dict[str, Any]]:
    query = urllib.parse.quote(f'conceptrecid:"{conceptrecid}"')
    # Unauthenticated Zenodo caps page size at 25; mostrecent ordering means the
    # newest versions are always present even when a huge family is truncated.
    # stop_after=100 converts the 4-page cap into a clean truncation instead of
    # a max_pages violation for families with more than 100 versions.
    hits = paginate(f"{API}?q={query}&all_versions=true&size=25&sort=mostrecent", max_pages=4, stop_after=100)
    return hits


def build_row(record_before: dict[str, Any], record_after: dict[str, Any]) -> dict[str, Any]:
    conceptrecid = str(record_after.get("conceptrecid"))
    conceptdoi = record_after.get("conceptdoi") or f"zenodo-concept:{conceptrecid}"
    owner_id = ""
    owners = record_after.get("owners")
    if isinstance(owners, list) and owners and isinstance(owners[0], dict):
        owner_id = str(owners[0].get("id", ""))
    before_sha = files_manifest_digest(record_before)
    after_sha = files_manifest_digest(record_after)
    assert before_sha and after_sha and before_sha != after_sha
    return {
        "packet_id": f"a6-s1-zenodo-{conceptrecid}",
        "stratum": STRATUM,
        "source_family_id": f"zenodo:record-family:{conceptrecid}",
        "normalized_organization_lineage": f"zenodo:owner:{owner_id or 'unattributed'}",
        "artifact_lineage_id": f"zenodo:software:{str(conceptdoi).lower()}",
        "before_version_id": str((record_before.get("metadata") or {}).get("version") or record_before.get("id")),
        "after_version_id": str((record_after.get("metadata") or {}).get("version") or record_after.get("id")),
        "before_record_id": str(record_before.get("id")),
        "after_record_id": str(record_after.get("id")),
        "before_sha256": before_sha,
        "after_sha256": after_sha,
        "license_or_rights_receipt_id": (
            f"zenodo:version-licenses:{license_id(record_before) or 'none'}|{license_id(record_after) or 'none'}|concept:{conceptrecid}"
        ),
        "license_before": license_id(record_before),
        "license_after": license_id(record_after),
        "access_right": (record_after.get("metadata") or {}).get("access_right"),
        "transition_title": (record_after.get("metadata") or {}).get("title"),
        "content_binding_provenance": "A6_ZENODO_REST_PUBLIC_METADATA",
    }


def census_family(latest: dict[str, Any]) -> dict[str, Any]:
    conceptrecid = str(latest.get("conceptrecid"))
    versions = fetch_family_versions(conceptrecid)
    licensed_open = [
        r for r in versions
        if license_id(r) and (r.get("metadata") or {}).get("access_right") == "open"
    ]
    if len(licensed_open) < 2:
        return {"conceptrecid": conceptrecid, "status": "SKIP", "reason": f"licensed_open_versions={len(licensed_open)}"}
    licensed_open.sort(key=version_sort_key)
    record_before, record_after = licensed_open[-2], licensed_open[-1]
    if files_manifest_digest(record_before) is None or files_manifest_digest(record_after) is None:
        return {"conceptrecid": conceptrecid, "status": "SKIP", "reason": "missing_files_manifest"}
    return {"conceptrecid": conceptrecid, "status": "BOUND", "row": build_row(record_before, record_after)}


def census(families: int, workers: int, polite_delay: float = 0.25) -> dict[str, Any]:
    # Unauthenticated page-size cap is 25 (size>25 -> HTTP 400); scan at 25/page.
    # Zenodo holds thousands of open software records, so stop paginating once
    # the requested families plus license/dedup headroom are in hand instead of
    # exhausting the corpus.
    latest_hits = paginate(
        f"{API}?resource_type=software&access_right=open&sort=mostrecent&size=25",
        max_pages=60,
        stop_after=families + families // 3,
    )[:families]
    seen_concepts: set[str] = set()
    latest_records: list[dict[str, Any]] = []
    for hit in latest_hits:
        concept = str(hit.get("conceptrecid"))
        if not concept or concept in seen_concepts:
            continue
        if not license_id(hit):
            continue
        seen_concepts.add(concept)
        latest_records.append(hit)
    rows: list[dict[str, Any]] = []
    skips: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []

    def work(record: dict[str, Any]) -> dict[str, Any]:
        time.sleep(polite_delay)
        return census_family(record)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(work, record): str(record.get("conceptrecid")) for record in latest_records}
        for future in concurrent.futures.as_completed(futures):
            concept = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                failures.append({"conceptrecid": concept, "reason": str(exc)[:240]})
                continue
            if result["status"] == "BOUND":
                rows.append(result["row"])
            else:
                skips.append({"conceptrecid": concept, "reason": result["reason"]})

    rows.sort(key=lambda r: r["packet_id"])
    return {
        "schema": "ORION.A6.Stratum1ZenodoSoftwareReleaseCensusResult.v1",
        "stratum": STRATUM,
        "latest_software_hits_scanned": len(latest_hits),
        "licensed_latest_families_attempted": len(latest_records),
        "packet_candidate_n": len(rows),
        "skipped_family_n": len(skips),
        "skipped_families": skips,
        "cannot_check_family_failure_n": len(failures),
        "cannot_check_family_failures": failures,
        "distinct_normalized_organization_lineage_n": len({r["normalized_organization_lineage"] for r in rows}),
        "distinct_source_family_n": len({r["source_family_id"] for r in rows}),
        "distinct_artifact_lineage_n": len({r["artifact_lineage_id"] for r in rows}),
        "packet_candidates": rows,
        "version_order_rule": "ascending (publication_date, record id); two most recent licensed open versions form the release transition",
        "stratum_eligibility_adjudicated": False,
        "gold_adjudicated": False,
        "protected_orion_predictions_accessed": False,
        "scientific_authority_delta": "NONE__OUTCOME_BLIND_SOURCE_CENSUS_ONLY",
    }


def write_snapshot(result: dict[str, Any], chunk_size: int = 100) -> dict[str, Any]:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    rows = result.pop("packet_candidates")
    result.pop("skipped_families", None)
    result.pop("cannot_check_family_failures", None)
    chunks = []
    for i in range(0, len(rows), chunk_size):
        part = rows[i:i + chunk_size]
        name = f"ROWS_{i + 1:03d}_{i + len(part):03d}.json"
        path = SNAPSHOT_DIR / name
        path.write_text(json.dumps({"schema": "ORION.A6.Stratum1CensusChunk.v1", "rows": part}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        chunks.append({"path": str(path.relative_to(ROOT)), "rows": len(part), "sha256": sha256_bytes(path.read_bytes())})
    capacity = result["packet_candidate_n"] >= 20 and result["distinct_normalized_organization_lineage_n"] >= 20
    manifest = {
        **result,
        "chunks": chunks,
        "packet_candidate_rows_sha256": canonical_json_sha(rows),
        "decision": (
            "A6_STRATUM1_ZENODO_SOFTWARE_RELEASE_CAPACITY_AT_LEAST_20_DISJOINT_ORG_LINEAGES"
            if capacity else "CANNOT_CHECK_A6_STRATUM1_CAPACITY_OR_DISJOINT_ORG_LINEAGES"
        ),
        "quota_note": "capacity statement only; the 20/20/20 primary quota and replication quota stay unallocated until the eligible pool and externally frozen replication quotas exist",
    }
    manifest_path = SNAPSHOT_DIR / "A6_STRATUM1_CENSUS_MANIFEST_V1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def synthetic_record(rid: int, concept: str, version: str, pub: str, lic: str | None, keys: list[str]) -> dict[str, Any]:
    return {
        "id": rid,
        "conceptrecid": concept,
        "conceptdoi": f"10.5281/zenodo.{concept}",
        "owners": [{"id": "42"}],
        "files": [{"key": k, "size": 100, "checksum": f"md5:{rid}-{i}"} for i, k in enumerate(keys)],
        "metadata": {"version": version, "publication_date": pub, "license": {"id": lic} if lic else None, "access_right": "open"},
    }


def self_test() -> dict[str, Any]:
    r1 = synthetic_record(101, "100", "v1.0", "2026-01-01", "Apache-2.0", ["a.zip"])
    r2 = synthetic_record(102, "100", "v1.1", "2026-02-01", "Apache-2.0", ["a.zip", "b.zip"])
    r3 = synthetic_record(103, "100", "v0.9", "2026-02-01", None, ["a.zip"])
    assert version_sort_key(r1) < version_sort_key(r2)
    assert [license_id(x) for x in (r1, r2, r3)] == ["Apache-2.0", "Apache-2.0", None]
    d1, d2 = files_manifest_digest(r1), files_manifest_digest(r2)
    assert d1 and d2 and d1 != d2 and HEX64.fullmatch(d1)
    same_day = [r2, r3]
    same_day.sort(key=version_sort_key)
    assert same_day[-1]["id"] == 103  # same publication_date tie broken by higher (later) record id
    row = build_row(r1, r2)
    assert row["packet_id"] == "a6-s1-zenodo-100"
    assert row["stratum"] == STRATUM
    assert row["normalized_organization_lineage"] == "zenodo:owner:42"
    assert row["artifact_lineage_id"] == "zenodo:software:10.5281/zenodo.100"
    assert row["before_sha256"] != row["after_sha256"]
    assert row["license_or_rights_receipt_id"] == "zenodo:version-licenses:Apache-2.0|Apache-2.0|concept:100"
    no_files = synthetic_record(104, "101", "v2", "2026-03-01", "MIT", [])
    assert files_manifest_digest(no_files) is None
    try:
        build_row(no_files, no_files)
    except AssertionError:
        identical_manifest_rejected = True
    else:
        raise AssertionError("manifest-less family accepted")
    return {
        "decision": "GREEN",
        "version_ordering_deterministic": True,
        "manifest_digests_differ": True,
        "identical_manifest_rejected": identical_manifest_rejected,
        "network_accessed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--families", type=int, default=400)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--no-snapshot", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        result = self_test()
        code = 0
    else:
        if not 1 <= args.workers <= 2:
            ap.error("--workers must be 1..2")
        if args.families < 1:
            ap.error("--families must be >=1")
        result = census(args.families, args.workers)
        if not args.no_snapshot:
            result = write_snapshot(result)
        code = 0 if result.get("decision", "CAPACITY_OK").startswith(("A6_STRATUM1", "CAPACITY_OK")) else 2
    print(json.dumps(result, indent=2, sort_keys=True)[:200000])
    return code


if __name__ == "__main__":
    raise SystemExit(main())
