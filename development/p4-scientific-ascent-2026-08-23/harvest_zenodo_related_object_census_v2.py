#!/usr/bin/env python3
"""Harvest the distinct, frozen V2 public Zenodo related-object census."""

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


def canonical_sha256(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_bytes(body.encode("utf-8"))


def fetch(url: str, attempts: int = 4) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ORION-P4-public-metadata-census/2.0 (research; no file downloads)"},
    )
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                return response.read()
        except Exception as exc:  # transport retry only; the protocol remains fixed
            last_error = exc
            time.sleep(2**attempt)
    raise RuntimeError(f"Zenodo request failed after {attempts} attempts: {last_error}")


def publication_typed(relation: dict[str, Any]) -> bool:
    resource_type = str(relation.get("resource_type", "")).lower()
    return resource_type == "publication" or resource_type.startswith("publication-")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--disclosure", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    existing_outputs = [path for path in (args.candidates, args.receipt) if path.exists()]
    if existing_outputs:
        raise RuntimeError(
            "refusing to overwrite frozen V2 outputs: "
            + ", ".join(str(path) for path in existing_outputs)
            + "; use a new successor identity for a new acquisition"
        )

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    disclosure_bytes = args.disclosure.read_bytes()
    if sha256_bytes(disclosure_bytes) != protocol["prefreeze_disclosure"]["sha256"]:
        raise RuntimeError("prefreeze disclosure digest does not match frozen V2 protocol")
    disclosure = json.loads(disclosure_bytes)
    excluded = set(disclosure["all_disclosed_record_ids"])
    args.cache.mkdir(parents=True, exist_ok=True)

    accepted_schemes = set(protocol["candidate_filter"]["accepted_relation_schemes"])
    accepted_relations = set(protocol["candidate_filter"]["accepted_relations"])
    accepted_licenses = set(protocol["candidate_filter"]["record_license_ids"])
    page_size = int(protocol["provider"]["page_size"])
    pages = list(protocol["provider"]["pages"])

    candidates: list[dict[str, Any]] = []
    query_receipts: list[dict[str, Any]] = []
    record_queries: defaultdict[str, set[str]] = defaultdict(set)
    schema_ok = True
    pagination_ok = True

    for query_number, query in enumerate(protocol["queries"], start=1):
        counts = Counter()
        seen_in_query: set[str] = set()
        page_receipts = []
        for page in pages:
            params = urllib.parse.urlencode(
                {
                    "q": query["q"],
                    "size": page_size,
                    "page": page,
                    "sort": protocol["provider"]["sort"],
                }
            )
            url = f"{protocol['provider']['endpoint']}?{params}"
            raw = fetch(url)
            raw_path = args.cache / f"{query_number:02d}_{query['query_id']}_page_{page:02d}.json"
            raw_path.write_bytes(raw)
            payload = json.loads(raw)
            hits = payload.get("hits", {}).get("hits", [])
            total = payload.get("hits", {}).get("total")
            page_schema_ok = isinstance(hits, list) and isinstance(total, int)
            if not page_schema_ok:
                schema_ok = False
                hits = []
            if len(hits) != page_size:
                pagination_ok = False
            page_receipts.append(
                {
                    "page": page,
                    "request_url_sha256": sha256_bytes(url.encode("utf-8")),
                    "raw_response_file": raw_path.name,
                    "raw_response_bytes": len(raw),
                    "raw_response_sha256": sha256_bytes(raw),
                    "reported_total_hits": total,
                    "returned_hits": len(hits),
                    "schema_passed": page_schema_ok,
                }
            )
            for hit in hits:
                counts["raw_hits"] += 1
                record_id = str(hit.get("id", ""))
                if not record_id:
                    counts["missing_record_id"] += 1
                    schema_ok = False
                    continue
                if record_id in seen_in_query:
                    counts["duplicate_within_query"] += 1
                    pagination_ok = False
                    continue
                seen_in_query.add(record_id)
                if record_id in excluded:
                    counts["prefreeze_exclusions"] += 1
                    continue

                metadata = hit.get("metadata") or {}
                license_id = str((metadata.get("license") or {}).get("id", ""))
                if license_id not in accepted_licenses:
                    continue
                counts["licence_eligible"] += 1

                files = hit.get("files") or []
                public_files = [
                    file_row
                    for file_row in files
                    if str((file_row.get("links") or {}).get("self", "")).startswith("https://")
                ]
                if not public_files:
                    continue
                counts["public_file_evidence_eligible"] += 1

                relations = metadata.get("related_identifiers") or []
                if not isinstance(relations, list):
                    counts["invalid_related_identifiers"] += 1
                    schema_ok = False
                    continue
                accepted = [
                    relation
                    for relation in relations
                    if isinstance(relation, dict)
                    and relation.get("scheme") in accepted_schemes
                    and relation.get("relation") in accepted_relations
                    and relation.get("identifier")
                ]
                if not accepted:
                    continue
                counts["typed_relation_eligible"] += 1
                publication_relations = [relation for relation in accepted if publication_typed(relation)]
                if not publication_relations:
                    continue
                counts["publication_typed_relation_eligible"] += 1

                record_queries[record_id].add(query["query_id"])
                candidates.append(
                    {
                        "schema_version": "orion.p4.zenodo-related-object-candidate.v2",
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
                        "public_file_count": len(public_files),
                        "creators": [str(item.get("name", "")) for item in metadata.get("creators") or []],
                        "publication_related_identifiers": publication_relations,
                        "record_api_url": str((hit.get("links") or {}).get("self", "")),
                        "record_canonical_sha256": canonical_sha256(hit),
                        "candidate_boundary": "PUBLIC_METADATA_AND_RECORD_LICENSE_ONLY__LINKED_OBJECT_RIGHTS_PAIR_IDENTITY_AND_CASE_ELIGIBILITY_UNADJUDICATED",
                    }
                )
            time.sleep(float(protocol["provider"]["inter_request_seconds"]))

        query_receipts.append(
            {
                "query_id": query["query_id"],
                "domain_id": query["domain_id"],
                "mechanism_id": query["mechanism_id"],
                "pages": page_receipts,
                "unique_raw_records": len(seen_in_query),
                **dict(counts),
            }
        )

    candidates.sort(key=lambda row: (row["query_id"], row["record_id"]))
    args.candidates.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in candidates),
        encoding="utf-8",
    )
    gate = int(protocol["positive_source_signal"]["minimum_per_cell"])
    per_cell = {
        row["query_id"]: {
            "domain_id": row["domain_id"],
            "mechanism_id": row["mechanism_id"],
            "publication_typed_relation_candidates": row.get("publication_typed_relation_eligible", 0),
            "passes_frozen_signal_gate": row.get("publication_typed_relation_eligible", 0) >= gate,
        }
        for row in query_receipts
    }
    all_pass = schema_ok and pagination_ok and all(
        cell["passes_frozen_signal_gate"] for cell in per_cell.values()
    )
    receipt = {
        "schema_version": "orion.p4.zenodo-related-object-census-receipt.v2",
        "date": "2026-08-23",
        "identity": "P4_ZENODO_RELATED_OBJECT_CENSUS_V2",
        "authority": protocol["authority"],
        "v1_retained_terminal": protocol["lineage"]["v1_retained_terminal"],
        "protocol_sha256": sha256_file(args.protocol),
        "prefreeze_disclosure_sha256": sha256_file(args.disclosure),
        "provider_schema_passed": schema_ok,
        "pagination_integrity_passed": pagination_ok,
        "query_count": len(query_receipts),
        "raw_response_count": sum(len(row["pages"]) for row in query_receipts),
        "query_receipts": query_receipts,
        "candidate_rows": len(candidates),
        "unique_candidate_records": len(record_queries),
        "cross_query_record_count": sum(len(queries) > 1 for queries in record_queries.values()),
        "candidate_jsonl_sha256": sha256_file(args.candidates),
        "per_cell": per_cell,
        "all_eight_cells_pass_frozen_signal_gate": all_pass,
        "files_downloaded": False,
        "case_outcomes_accessed": False,
        "model_outcomes_executed": False,
        "forbidden_claims": protocol["forbidden_claims"],
        "terminal": (
            "P4_ZENODO_RELATED_OBJECT_V2_EIGHT_CELL_PUBLICATION_SIGNAL_GATE_PASSED__CASE_ELIGIBILITY_CANNOT_CHECK"
            if all_pass
            else "P4_ZENODO_RELATED_OBJECT_V2_SOURCE_CELL_SHORTFALL__EXPAND_DISJOINT_PROVIDER"
            if schema_ok and pagination_ok
            else "P4_ZENODO_RELATED_OBJECT_V2_CANNOT_CHECK_SCHEMA_OR_PAGINATION"
        ),
    }
    args.receipt.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
