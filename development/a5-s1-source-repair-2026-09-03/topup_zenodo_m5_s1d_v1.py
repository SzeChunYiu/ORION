#!/usr/bin/env python3
"""A5 S1d: top up the M5 (article-to-data-documentation) source cells with
additional licence-eligible publication-typed Zenodo records.

Extends the frozen V2 Zenodo related-object census (same queries, same filter
sets, same provider conventions, sort=mostrecent, page size 25) to deeper
pages for the three M5 cells that the A5 census scored short:
EARTH_DATA (gap 5), PHYSICAL_DATA (gap 15), SOFTWARE_DATA (gap 15).

Every harvested record is deduplicated against the committed V2 candidate
rows and the V2 prefreeze disclosure ids, and within this run.  No file bytes
are downloaded (files_downloaded = false, mirroring the V2 census); the unit
of evidence is public record metadata + record licence + public file link
evidence + a publication-typed related identifier.  No outcome access, no
eligibility adjudication, no domain or mechanism reassignment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

V2_PROTOCOL_SHA256 = "01c1bb250accfaee4103a162565cd2107515cd306adf690713a5c1372e953d1f"
V2_CANDIDATES_SHA256 = "d6f767e88cdc401dd1f7643ed76e4460645fcc3dff9744dc504fed01351c1247"
V2_DISCLOSURE_SHA256 = "76eab6d8d7c1f32df141d16dbbe57d3007ba183a8d3e9a44818626f6a2644178"
V2_PROTOCOL_PATH = "development/p4-scientific-ascent-2026-08-23/P4_ZENODO_RELATED_OBJECT_CENSUS_PROTOCOL_V2.json"
V2_CANDIDATES_PATH = "development/p4-scientific-ascent-2026-08-23/P4_ZENODO_RELATED_OBJECT_CANDIDATES_V2.jsonl"
V2_DISCLOSURE_PATH = "development/p4-scientific-ascent-2026-08-23/P4_ZENODO_V2_PREFREEZE_PROBE_DISCLOSURE.json"
V3_CELL_COUNTS_PATH = "development/p4-source-universe-successor-v3-2026-08-23/CELL_COUNTS_V1.json"
V3_CELL_COUNTS_SHA256 = "3abb1ef76ecb97f84494b08d13f3b2553661a514e7aae8f56c26bfe12b767b0b"

# Frozen V2 pages consumed pages 1..9; the top-up starts after the last one.
START_PAGE = 10
MAX_PAGES_PER_QUERY = 40
# Cell gaps from A5_SOURCE_FEASIBILITY_RESULT_V1.json + safety margin.
TARGETS = {
    "EARTH_DATA": {"gap": 5, "margin": 10},
    "PHYSICAL_DATA": {"gap": 15, "margin": 10},
    "SOFTWARE_DATA": {"gap": 15, "margin": 10},
}
INTER_REQUEST_S = 0.5
ATTEMPTS = 4
UA = "ORION-A5-S1d-M5-topup/1.0 (research; no file downloads)"
SCHEMA = "ORION.A5.S1d.ZenodoM5TopUp.v1"


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


def fetch(url: str, log_path: Path) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    last_error: Exception | None = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                body = response.read()
                with log_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps({"ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "request_url": url, "attempt": attempt, "http_status": response.status, "body_bytes": len(body)}, sort_keys=True) + "\n")
                return body
        except Exception as exc:  # transport retry only; the protocol stays fixed
            last_error = exc
            time.sleep(2 ** (attempt - 1))
    raise RuntimeError(f"Zenodo request failed after {ATTEMPTS} attempts: {url}: {last_error}")


def publication_typed(relation: dict[str, Any]) -> bool:
    resource_type = str(relation.get("resource_type", "")).lower()
    return resource_type == "publication" or resource_type.startswith("publication-")


def load_pinned(repo_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], set[str], dict[str, int]]:
    protocol_path = repo_root / V2_PROTOCOL_PATH
    candidates_path = repo_root / V2_CANDIDATES_PATH
    disclosure_path = repo_root / V2_DISCLOSURE_PATH
    cell_counts_path = repo_root / V3_CELL_COUNTS_PATH
    for path, expected in (
        (protocol_path, V2_PROTOCOL_SHA256),
        (candidates_path, V2_CANDIDATES_SHA256),
        (disclosure_path, V2_DISCLOSURE_SHA256),
        (cell_counts_path, V3_CELL_COUNTS_SHA256),
    ):
        digest = sha256_file(path)
        if digest != expected:
            raise RuntimeError(f"CANNOT_CHECK_S1D_INPUT_DIGEST_MISMATCH {path.name}: {digest}")
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    candidates = [json.loads(line) for line in candidates_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    disclosure = json.loads(disclosure_path.read_text(encoding="utf-8"))
    cell_counts = json.loads(cell_counts_path.read_text(encoding="utf-8"))
    v3_units: dict[str, int] = {}
    for key, cell in cell_counts["cells"].items():
        if "M5_ARTICLE_TO_DATA_DOCUMENTATION" in key:
            domain = key.split("__")[0]
            v3_units[domain] = int(cell["unique_candidate_units_after_concept_and_publication_dedup"])
    return protocol, candidates, set(disclosure["all_disclosed_record_ids"]), v3_units


def run(args: argparse.Namespace) -> dict[str, Any]:
    protocol, v2_candidates, excluded, v3_units = load_pinned(args.repo_root)
    accepted_schemes = set(protocol["candidate_filter"]["accepted_relation_schemes"])
    accepted_relations = set(protocol["candidate_filter"]["accepted_relations"])
    accepted_licenses = set(protocol["candidate_filter"]["record_license_ids"])
    page_size = int(protocol["provider"]["page_size"])
    sort = protocol["provider"]["sort"]
    endpoint = protocol["provider"]["endpoint"]
    queries = {q["query_id"]: q for q in protocol["queries"]}

    known_ids = {str(row["record_id"]) for row in v2_candidates} | excluded
    v2_per_cell = Counter(str(row["query_id"]) for row in v2_candidates)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.cache.mkdir(parents=True, exist_ok=True)
    log_path = args.out_dir / "ACCESS_LOG_S1D.jsonl"
    candidates_path = args.out_dir / "A5_S1D_ZENODO_M5_TOPUP_CANDIDATES_V1.jsonl"

    existing_rows = []
    if candidates_path.exists():
        existing_rows = [json.loads(line) for line in candidates_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for row in existing_rows:
            known_ids.add(str(row["record_id"]))
    new_candidates: list[dict[str, Any]] = list(existing_rows)

    query_receipts = []
    for query_id, target in TARGETS.items():
        query = queries[query_id]
        counts: Counter = Counter()
        seen: set[str] = set()
        pages_receipts = []
        stop_reason = None
        page = START_PAGE
        last_page = START_PAGE + MAX_PAGES_PER_QUERY - 1
        while page <= last_page:
            params = urllib.parse.urlencode({"q": query["q"], "size": page_size, "page": page, "sort": sort})
            url = f"{endpoint}?{params}"
            raw = fetch(url, log_path)
            raw_path = args.cache / f"{query_id}_page_{page:02d}.json"
            raw_path.write_bytes(raw)
            payload = json.loads(raw)
            hits = payload.get("hits", {}).get("hits", [])
            total = payload.get("hits", {}).get("total")
            pages_receipts.append({
                "page": page,
                "request_url_sha256": sha256_bytes(url.encode("utf-8")),
                "raw_response_file": raw_path.name,
                "raw_response_bytes": len(raw),
                "raw_response_sha256": sha256_bytes(raw),
                "reported_total_hits": total,
                "returned_hits": len(hits),
            })
            if not hits:
                stop_reason = "exhausted"
                break
            for hit in hits:
                counts["raw_hits"] += 1
                record_id = str(hit.get("id", ""))
                if not record_id:
                    counts["missing_record_id"] += 1
                    continue
                if record_id in seen:
                    counts["duplicate_within_query"] += 1
                    continue
                seen.add(record_id)
                if record_id in known_ids:
                    counts["already_known_v2_or_disclosure_or_this_run"] += 1
                    continue
                metadata = hit.get("metadata") or {}
                license_id = str((metadata.get("license") or {}).get("id", ""))
                if license_id not in accepted_licenses:
                    continue
                counts["licence_eligible"] += 1
                files = hit.get("files") or []
                public_files = [f for f in files if str((f.get("links") or {}).get("self", "")).startswith("https://")]
                if not public_files:
                    continue
                counts["public_file_evidence_eligible"] += 1
                relations = metadata.get("related_identifiers") or []
                if not isinstance(relations, list):
                    counts["invalid_related_identifiers"] += 1
                    continue
                accepted = [
                    relation for relation in relations
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
                known_ids.add(record_id)
                new_candidates.append({
                    "schema_version": "orion.a5.s1d.zenodo-m5-topup-candidate.v1",
                    "source_query_id": query_id,
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
                })
            time.sleep(INTER_REQUEST_S)
            if counts["publication_typed_relation_eligible"] >= target["gap"] + target["margin"]:
                stop_reason = "target_reached"
                break
            if len(hits) < page_size:
                stop_reason = "short_page_end_of_results"
                break
            page += 1
        if stop_reason is None:
            stop_reason = "page_budget_exhausted"
        query_receipts.append({
            "query_id": query_id,
            "domain_id": query["domain_id"],
            "mechanism_id": query["mechanism_id"],
            "frozen_query_q": query["q"],
            "pages": pages_receipts,
            "unique_raw_records_this_run": len(seen),
            "stop_reason": stop_reason,
            **dict(counts),
        })

    new_candidates.sort(key=lambda row: (row["source_query_id"], row["record_id"]))
    candidates_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in new_candidates), encoding="utf-8")

    topup_per_cell = Counter(row["source_query_id"] for row in new_candidates)
    per_cell = {}
    for query_id in TARGETS:
        domain = queries[query_id]["domain_id"]
        before = int(v2_per_cell.get(query_id, 0))
        topup = int(topup_per_cell.get(query_id, 0))
        zenodo_route = before + topup
        # The census M5 counting rule admits the provider-disjoint route
        # families as a sum: Zenodo (V2 + this top-up) + V3 units.
        v3_route = int(v3_units.get(domain, 0))
        projected_census_bound = zenodo_route + v3_route
        per_cell[query_id] = {
            "domain_id": domain,
            "mechanism_id": queries[query_id]["mechanism_id"],
            "v2_candidates": before,
            "s1d_topup_new": topup,
            "zenodo_route_combined": zenodo_route,
            "v3_route_units": v3_route,
            "projected_census_bound_zenodo_plus_v3": projected_census_bound,
            "quota_48": 48,
            "quota_48_passed": projected_census_bound >= 48,
        }

    result = {
        "schema_version": SCHEMA,
        "date": "2026-09-03",
        "identity": "A5_S1D_ZENODO_M5_TOPUP_V1",
        "authority_boundary": {
            "authority": "PUBLIC_METADATA_SOURCE_FEASIBILITY_ONLY",
            "grants_scientific_authority": False,
            "protected_outcomes_accessed": False,
            "comparator_outputs_accessed": False,
            "terminal_gold_accessed": False,
            "counts_are_not_eligible_pair_counts": True,
            "domain_or_mechanism_reassignment_performed": False,
            "interpretation": (
                "Candidate-substrate counts only.  The M5 census counting rule admits the "
                "Zenodo route family as publication-typed relation candidates with accepted "
                "record licence and public file evidence; this top-up extends the same frozen "
                "filters to deeper pages and deduplicates against every previously committed "
                "Zenodo candidate row.  Natural-pair eligibility and external screening "
                "remain open and can only reduce these counts."
            ),
        },
        "inputs": {
            "v2_protocol": {"path": V2_PROTOCOL_PATH, "sha256": V2_PROTOCOL_SHA256},
            "v2_candidates": {"path": V2_CANDIDATES_PATH, "sha256": V2_CANDIDATES_SHA256},
            "v2_prefreeze_disclosure": {"path": V2_DISCLOSURE_PATH, "sha256": V2_DISCLOSURE_SHA256},
            "v3_cell_counts": {"path": V3_CELL_COUNTS_PATH, "sha256": V3_CELL_COUNTS_SHA256, "role": "M5 provider-disjoint route family units summed by the census M5 counting rule"},
        },
        "provider_conventions": {
            "endpoint": endpoint,
            "sort": sort,
            "page_size": page_size,
            "start_page": START_PAGE,
            "max_pages_per_query": MAX_PAGES_PER_QUERY,
            "inter_request_seconds": INTER_REQUEST_S,
            "user_agent": UA,
            "files_downloaded": False,
        },
        "dedup_rule": "record_id not in (V2 candidate ids | prefreeze disclosure ids | this-run ids); conceptrecid not used as a unit key, mirroring the frozen V2 census",
        "query_receipts": query_receipts,
        "candidate_rows": len(new_candidates),
        "candidate_jsonl_sha256": sha256_file(candidates_path),
        "per_cell": per_cell,
        "execution_boundary": {"host": "billy-old", "raw_response_cache_outside_repository": str(args.cache)},
        "forbidden_claims": [
            "natural-pair eligibility",
            "article identity equivalence without adjudication",
            "content rights beyond exact Zenodo record licence",
            "linked external object rights",
            "case resolution",
            "scientific performance",
            "confirmation",
            "ORION superiority",
        ],
        "scientific_authority_delta": "NONE__OUTCOME_BLIND_SOURCE_TOPUP_ONLY",
    }
    result_path = args.out_dir / "A5_S1D_ZENODO_M5_TOPUP_RESULT_V1.json"
    result_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result


def self_test() -> int:
    assert publication_typed({"resource_type": "publication"}) is True
    assert publication_typed({"resource_type": "publication-article"}) is True
    assert publication_typed({"resource_type": "dataset"}) is False
    # tamper: a dataset-typed relation must never be admitted as publication-typed
    forged = {"resource_type": "dataset", "relation": "isDocumentedBy"}
    assert not publication_typed(forged)
    # canonical json determinism
    assert canonical_sha256({"b": 1, "a": 2}) == canonical_sha256({"a": 2, "b": 1})
    print(json.dumps({"self_test": "PASS", "schema": SCHEMA}, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent / "s1d-topup")
    parser.add_argument("--cache", type=Path, default=Path.home() / "orion-a5-sources" / "s1d-zenodo-cache")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    result = run(args)
    print(json.dumps({
        "identity": result["identity"],
        "candidate_rows": result["candidate_rows"],
        "per_cell": {k: {"s1d_topup_new": v["s1d_topup_new"], "zenodo_route_combined": v["zenodo_route_combined"], "projected_census_bound_zenodo_plus_v3": v["projected_census_bound_zenodo_plus_v3"], "quota_48_passed": v["quota_48_passed"]} for k, v in result["per_cell"].items()},
    }, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
