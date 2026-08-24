#!/usr/bin/env python3
"""Harvest the frozen public Zenodo related-object metadata census."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(url: str, attempts: int = 4) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ORION-P4-public-metadata-census/1.0 (research; no file downloads)"},
    )
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                return response.read()
        except Exception as exc:  # network retry is transport-only
            last_error = exc
            time.sleep(2**attempt)
    raise RuntimeError(f"Zenodo request failed after {attempts} attempts: {last_error}")


def canonical_sha256(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_bytes(body.encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    args.cache.mkdir(parents=True, exist_ok=True)
    accepted_schemes = set(protocol["candidate_filter"]["accepted_relation_schemes"])
    accepted_relations = set(protocol["candidate_filter"]["accepted_relations"])
    accepted_licenses = set(protocol["candidate_filter"]["record_license_ids"])
    accepted_access = set(protocol["candidate_filter"]["access_status"])
    excluded = set(protocol["preflight_exclusions"]["record_ids"])

    candidates: list[dict[str, Any]] = []
    query_receipts: list[dict[str, Any]] = []
    record_queries: defaultdict[str, set[str]] = defaultdict(set)
    schema_ok = True
    for number, query in enumerate(protocol["queries"], start=1):
        params = urllib.parse.urlencode(
            {
                "q": query["q"],
                "size": protocol["provider"]["page_size"],
                "sort": protocol["provider"]["sort"],
            }
        )
        url = f"{protocol['provider']['endpoint']}?{params}"
        raw = fetch(url)
        raw_path = args.cache / f"{number:02d}_{query['query_id']}.json"
        raw_path.write_bytes(raw)
        payload = json.loads(raw)
        hits = payload.get("hits", {}).get("hits", [])
        total = payload.get("hits", {}).get("total")
        if not isinstance(hits, list) or not isinstance(total, int):
            schema_ok = False
            hits = []
        counts = Counter()
        for hit in hits:
            counts["raw_hits"] += 1
            record_id = str(hit.get("id", ""))
            if not record_id:
                counts["missing_record_id"] += 1
                schema_ok = False
                continue
            if record_id in excluded:
                counts["preflight_exclusions"] += 1
                continue
            metadata = hit.get("metadata") or {}
            license_id = str((metadata.get("license") or {}).get("id", ""))
            access_status = str((hit.get("access") or {}).get("status", ""))
            if license_id not in accepted_licenses or access_status not in accepted_access:
                continue
            counts["licence_eligible"] += 1
            relations = metadata.get("related_identifiers") or []
            accepted = [
                relation
                for relation in relations
                if relation.get("scheme") in accepted_schemes
                and relation.get("relation") in accepted_relations
                and relation.get("identifier")
            ]
            if not accepted:
                continue
            counts["typed_relation_eligible"] += 1
            publication_relations = [
                relation
                for relation in accepted
                if str(relation.get("resource_type", "")).startswith("publication")
                or str(relation.get("resource_type", "")) in {"preprint", "workingpaper"}
            ]
            if publication_relations:
                counts["publication_typed_relation_eligible"] += 1
            record_queries[record_id].add(query["query_id"])
            candidates.append(
                {
                    "schema_version": "orion.p4.zenodo-related-object-candidate.v1",
                    "query_id": query["query_id"],
                    "domain_id": query["domain_id"],
                    "mechanism_id": query["mechanism_id"],
                    "record_id": record_id,
                    "conceptrecid": str(hit.get("conceptrecid", "")),
                    "doi": str(metadata.get("doi", "")),
                    "title": str(metadata.get("title", "")),
                    "publication_date": str(metadata.get("publication_date", "")),
                    "resource_type": metadata.get("resource_type"),
                    "license_id": license_id,
                    "access_status": access_status,
                    "creators": [str(item.get("name", "")) for item in metadata.get("creators") or []],
                    "related_identifiers": accepted,
                    "publication_related_identifiers": publication_relations,
                    "record_api_url": str((hit.get("links") or {}).get("self", "")),
                    "record_canonical_sha256": canonical_sha256(hit),
                    "candidate_boundary": "PUBLIC_METADATA_AND_RECORD_LICENSE_ONLY__PAIR_IDENTITY_EXTERNAL_RIGHTS_AND_CASE_ELIGIBILITY_UNADJUDICATED",
                }
            )
        query_receipts.append(
            {
                "query_id": query["query_id"],
                "domain_id": query["domain_id"],
                "mechanism_id": query["mechanism_id"],
                "url_sha256": sha256_bytes(url.encode("utf-8")),
                "raw_response_file": raw_path.name,
                "raw_response_bytes": len(raw),
                "raw_response_sha256": sha256_bytes(raw),
                "reported_total_hits": total,
                **dict(counts),
            }
        )
        time.sleep(1.0)

    candidates.sort(key=lambda row: (row["query_id"], row["record_id"]))
    args.candidates.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in candidates),
        encoding="utf-8",
    )
    per_cell = {
        receipt["query_id"]: {
            "domain_id": receipt["domain_id"],
            "mechanism_id": receipt["mechanism_id"],
            "typed_relation_candidates": receipt.get("typed_relation_eligible", 0),
            "publication_typed_relation_candidates": receipt.get("publication_typed_relation_eligible", 0),
            "passes_frozen_48_signal_gate": receipt.get("typed_relation_eligible", 0) >= 48,
        }
        for receipt in query_receipts
    }
    receipt = {
        "schema_version": "orion.p4.zenodo-related-object-census-receipt.v1",
        "date": "2026-08-23",
        "authority": protocol["authority"],
        "protocol_sha256": sha256_file(args.protocol),
        "provider_schema_passed": schema_ok,
        "query_count": len(query_receipts),
        "raw_response_count": len(query_receipts),
        "query_receipts": query_receipts,
        "candidate_rows": len(candidates),
        "unique_candidate_records": len(record_queries),
        "cross_query_record_count": sum(len(queries) > 1 for queries in record_queries.values()),
        "candidate_jsonl_sha256": sha256_file(args.candidates),
        "per_cell": per_cell,
        "all_eight_cells_pass_48_signal_gate": schema_ok and all(
            cell["passes_frozen_48_signal_gate"] for cell in per_cell.values()
        ),
        "forbidden_claims": protocol["forbidden_claims"],
        "terminal": (
            "P4_ZENODO_RELATED_OBJECT_EIGHT_CELL_SIGNAL_GATE_PASSED__CASE_ELIGIBILITY_CANNOT_CHECK"
            if schema_ok and all(cell["passes_frozen_48_signal_gate"] for cell in per_cell.values())
            else "P4_ZENODO_RELATED_OBJECT_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_PROVIDER"
            if schema_ok
            else "P4_ZENODO_RELATED_OBJECT_CENSUS_CANNOT_CHECK_PROVIDER_SCHEMA"
        ),
    }
    args.receipt.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
