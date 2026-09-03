#!/usr/bin/env python3
"""Outcome-blind A6 stratum-3 census: scientific-record transitions (public metadata only).

Article -> data/code release transitions are enumerated from the SUPPLEMENT
side: DataCite Dataset records declaring a DOI-typed `IsSupplementTo` relation
(the inverse of Crossref's `is-supplemented-by`), with the article side bound
from its Crossref work record (publisher lineage). Two sub-routes are recorded
as explicit CANNOT_CHECK blockers rather than padded:
- corrections: the Crossref relation vocabulary exposes no correction relation
  type and OpenAlex errata reach the original only via algorithmic
  related_works, so correction pairs are not mechanically bindable;
- software-side supplements: Software records declare IsSupplementTo via URL
  identifiers (GitHub links), not DOIs (15/15 sampled 2026-09-03), so no
  Crossref article record is mechanically reachable.
Metadata-only census: no fulltext is fetched, no stratum eligibility, gold
label, prediction or outcome is read or produced.
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
SNAPSHOT_DIR = HERE / "scientific-record-census-v1"
STRATUM = "scientific_record_transition"
UA = "ORION-A6-stratum3-census-v1/1.0 (mailto:orion-a6@example.org)"
CROSSREF = "https://api.crossref.org/works"
DATACITE = "https://api.datacite.org/dois"
DATACITE_QUERY = "relatedIdentifiers.relationType:IsSupplementTo AND types.resourceTypeGeneral:Dataset"
SUPPLEMENT_RESOURCE_TYPES = {"Dataset", "Software"}
CORRECTION_BLOCKER = (
    "Crossref relation vocabulary (server-enumerated 2026-09-03) contains no correction "
    "relation type (no is-correction-for/has-correction); OpenAlex type:erratum reaches the "
    "original work only through algorithmic related_works, not a typed relation, so "
    "article->correction pairs cannot be mechanically bound without fuzzy title matching; "
    "not padded."
)
SOFTWARE_BLOCKER = (
    "Software-side IsSupplementTo relations use URL identifiers (GitHub links; 15/15 "
    "sampled 2026-09-03), never DOIs, so the supplemented article record is not "
    "mechanically reachable for software; the bound sub-route is Dataset-side "
    "(DOI-typed IsSupplementTo enumerated from DataCite)."
)
MAX_BYTES = 32 * 1024 * 1024


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def slugify(text: Any) -> str:
    lowered = str(text or "").strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", lowered, flags=re.ASCII).strip("-") or "unattributed"


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
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                # A 404 is a permanent client-side miss (DOI not registered with
                # this registry); retrying only burns ~30s of backoff per DOI.
                raise
            last = exc
            if attempt + 1 < retries:
                # Transient upstream 5xx gateway overloads clear within seconds;
                # exponential backoff (1,2,4,8,16s) instead of aborting the census.
                time.sleep(2 ** attempt)
        except (urllib.error.URLError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"failed to fetch {url}: {last}")


def fetch_supplement_records(max_records: int) -> list[dict[str, Any]]:
    """Enumerate DataCite Dataset records declaring IsSupplementTo (page size 100)."""
    query = urllib.parse.quote(DATACITE_QUERY)
    items: list[dict[str, Any]] = []
    page = 1
    while len(items) < max_records and page <= 40:
        payload = request_json(f"{DATACITE}?page[size]=100&page[number]={page}&query={query}")
        batch = payload.get("data") or []
        items.extend(item for item in batch if isinstance(item, dict))
        if not batch:
            break
        page += 1
    return items[:max_records]


def supplement_attributes(record: dict[str, Any]) -> dict[str, Any]:
    return record.get("attributes") or {}


def supplement_resource_type(attrs: dict[str, Any]) -> str | None:
    return ((attrs.get("types") or {}).get("resourceTypeGeneral"))


def pick_article_doi(attrs: dict[str, Any]) -> str | None:
    """Deterministic lowest DOI-typed IsSupplementTo identifier."""
    dois = sorted({
        str(rel.get("relatedIdentifier")).lower()
        for rel in (attrs.get("relatedIdentifiers") or [])
        if isinstance(rel, dict)
        and rel.get("relationType") == "IsSupplementTo"
        and rel.get("relatedIdentifierType") == "DOI"
        and isinstance(rel.get("relatedIdentifier"), str)
        and rel.get("relatedIdentifier").strip()
    })
    return dois[0] if dois else None


def fetch_crossref_work(doi: str) -> dict[str, Any] | None:
    try:
        payload = request_json(f"{CROSSREF}/{urllib.parse.quote(doi, safe='')}")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    message = (payload or {}).get("message")
    return message if isinstance(message, dict) else None


def crossref_core(article: dict[str, Any]) -> dict[str, Any]:
    return {
        "DOI": article.get("DOI"),
        "title": (article.get("title") or [None])[0],
        "container-title": (article.get("container-title") or [None])[0],
        "publisher": article.get("publisher"),
        "issued": article.get("issued"),
        "type": article.get("type"),
    }


def datacite_core(attrs: dict[str, Any]) -> dict[str, Any]:
    titles = attrs.get("titles") or [{}]
    return {
        "doi": attrs.get("doi"),
        "title": (titles[0] or {}).get("title") if titles else None,
        "publisher": attrs.get("publisher"),
        "publicationYear": attrs.get("publicationYear"),
        "types": attrs.get("types"),
    }


def datacite_rights(attrs: dict[str, Any]) -> str:
    entries = attrs.get("rightsList") or []
    ids = sorted({str(e.get("rightsUri") or e.get("rights") or "").strip() for e in entries if isinstance(e, dict)})
    return "|".join(x for x in ids if x) or "unspecified"


def crossref_licenses(article: dict[str, Any]) -> list[str]:
    return sorted({str(entry.get("URL") or "").strip() for entry in (article.get("license") or []) if isinstance(entry, dict) and entry.get("URL")})


def build_row(article: dict[str, Any], attrs: dict[str, Any], article_doi: str, supplement_doi: str) -> dict[str, Any]:
    before_sha = canonical_json_sha(crossref_core(article))
    after_sha = canonical_json_sha(datacite_core(attrs))
    if before_sha == after_sha:
        raise ValueError("transition digests identical")
    return {
        "packet_id": f"a6-s3-dc-{supplement_doi}",
        "stratum": STRATUM,
        "source_family_id": f"crossref-supplement-family:doi:{article_doi}",
        "normalized_organization_lineage": f"crossref:publisher:{slugify(article.get('publisher'))}",
        "artifact_lineage_id": f"scientific-record:doi:{supplement_doi}",
        "before_version_id": f"crossref:doi:{article_doi}",
        "after_version_id": f"datacite:doi:{supplement_doi}",
        "before_sha256": before_sha,
        "after_sha256": after_sha,
        "license_or_rights_receipt_id": (
            f"crossref-metadata:CC0-1.0+datacite-metadata:CC0-1.0+datacite-rights:{datacite_rights(attrs)}:supplement:{supplement_doi}"
        ),
        "article_crossref_license_urls": crossref_licenses(article),
        "supplement_resource_type_general": supplement_resource_type(attrs),
        "transition_kind": "article_to_data_or_code_release",
        "enumeration_side": "DATACITE_SUPPLEMENT_SIDE",
        "content_binding_provenance": "A6_CROSSREF_ARTICLE_TO_DATACITE_SUPPLEMENT_PUBLIC_METADATA",
    }


def census_record(record: dict[str, Any]) -> dict[str, Any]:
    attrs = supplement_attributes(record)
    supplement_doi = str(attrs.get("doi") or "").lower()
    if supplement_resource_type(attrs) not in SUPPLEMENT_RESOURCE_TYPES:
        return {"id": supplement_doi, "status": "SKIP", "reason": "supplement_resource_type_mismatch"}
    article_doi = pick_article_doi(attrs)
    if not article_doi:
        return {"id": supplement_doi, "status": "SKIP", "reason": "no_doi_typed_supplement_relation"}
    article = fetch_crossref_work(article_doi)
    if article is None:
        return {"id": supplement_doi, "status": "SKIP", "reason": "article_side_not_in_crossref"}
    return {"id": supplement_doi, "status": "BOUND", "row": build_row(article, attrs, article_doi, supplement_doi)}


def census(records: int, workers: int, polite_delay: float = 0.15) -> dict[str, Any]:
    fetched = fetch_supplement_records(records)
    rows: list[dict[str, Any]] = []
    skips: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []

    def work(record: dict[str, Any]) -> dict[str, Any]:
        time.sleep(polite_delay)
        return census_record(record)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(work, record): str((record.get("attributes") or {}).get("doi") or "") for record in fetched}
        for future in concurrent.futures.as_completed(futures):
            doi = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                failures.append({"doi": doi, "reason": str(exc)[:240]})
                continue
            if result["status"] == "BOUND":
                rows.append(result["row"])
            else:
                skips.append({"doi": doi, "reason": result["reason"]})

    rows.sort(key=lambda r: r["packet_id"])
    return {
        "schema": "ORION.A6.Stratum3ScientificRecordTransitionCensusResult.v1",
        "stratum": STRATUM,
        "supplement_records_scanned": len(fetched),
        "universe_query": DATACITE_QUERY,
        "universe_ordering": "DataCite default ordering (most recently updated first), page[size]=100",
        "packet_candidate_n": len(rows),
        "skipped_record_n": len(skips),
        "skipped_records": skips,
        "cannot_check_record_failure_n": len(failures),
        "cannot_check_record_failures": failures,
        "correction_subroute_blocker": CORRECTION_BLOCKER,
        "software_subroute_blocker": SOFTWARE_BLOCKER,
        "distinct_normalized_organization_lineage_n": len({r["normalized_organization_lineage"] for r in rows}),
        "distinct_source_family_n": len({r["source_family_id"] for r in rows}),
        "distinct_artifact_lineage_n": len({r["artifact_lineage_id"] for r in rows}),
        "packet_candidates": rows,
        "metadata_only_no_fulltext_fetched": True,
        "stratum_eligibility_adjudicated": False,
        "gold_adjudicated": False,
        "protected_orion_predictions_accessed": False,
        "scientific_authority_delta": "NONE__OUTCOME_BLIND_SOURCE_CENSUS_ONLY",
    }


def write_snapshot(result: dict[str, Any], chunk_size: int = 100) -> dict[str, Any]:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    rows = result.pop("packet_candidates")
    result.pop("skipped_records", None)
    result.pop("cannot_check_record_failures", None)
    chunks = []
    for i in range(0, len(rows), chunk_size):
        part = rows[i:i + chunk_size]
        name = f"ROWS_{i + 1:03d}_{i + len(part):03d}.json"
        path = SNAPSHOT_DIR / name
        path.write_text(json.dumps({"schema": "ORION.A6.Stratum3CensusChunk.v1", "rows": part}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        chunks.append({"path": str(path.relative_to(ROOT)), "rows": len(part), "sha256": sha256_bytes(path.read_bytes())})
    capacity = result["packet_candidate_n"] >= 20 and result["distinct_normalized_organization_lineage_n"] >= 20
    manifest = {
        **result,
        "chunks": chunks,
        "packet_candidate_rows_sha256": canonical_json_sha(rows),
        "decision": (
            "A6_STRATUM3_SCIENTIFIC_RECORD_TRANSITION_CAPACITY_AT_LEAST_20_DISJOINT_ORG_LINEAGES"
            if capacity else "CANNOT_CHECK_A6_STRATUM3_CAPACITY_OR_DISJOINT_ORG_LINEAGES"
        ),
        "quota_note": "capacity statement only; the 20/20/20 primary quota and replication quota stay unallocated until the eligible pool and externally frozen replication quotas exist",
    }
    manifest_path = SNAPSHOT_DIR / "A6_STRATUM3_CENSUS_MANIFEST_V1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def self_test() -> dict[str, Any]:
    attrs = {
        "doi": "10.6084/m9.figshare.27999008",
        "titles": [{"title": "Supplementary Material"}],
        "publisher": "figshare",
        "publicationYear": 2024,
        "types": {"resourceTypeGeneral": "Dataset"},
        "rightsList": [{"rightsUri": "https://creativecommons.org/licenses/by/4.0/legalcode"}],
        "relatedIdentifiers": [
            {"relationType": "IsSupplementTo", "relatedIdentifierType": "DOI", "relatedIdentifier": "10.1159/000543005"},
            {"relationType": "IsSupplementTo", "relatedIdentifierType": "URL", "relatedIdentifier": "https://example.org/x"},
            {"relationType": "IsSupplementedBy", "relatedIdentifierType": "DOI", "relatedIdentifier": "10.1/zzz"},
            {"relationType": "IsSupplementTo", "relatedIdentifierType": "DOI", "relatedIdentifier": "10.1159/000543004"},
        ],
    }
    assert pick_article_doi(attrs) == "10.1159/000543004"  # deterministic lowest DOI-typed IsSupplementTo
    assert pick_article_doi({"relatedIdentifiers": []}) is None
    article = {
        "DOI": "10.1159/000543005",
        "title": ["A Case Report"],
        "container-title": ["J"],
        "publisher": "S. Karger AG",
        "issued": {"date-parts": [[2024, 12, 11]]},
        "type": "journal-article",
        "license": [{"URL": "https://example.org/tdm"}],
    }
    row = build_row(article, attrs, "10.1159/000543005", "10.6084/m9.figshare.27999008")
    assert row["packet_id"] == "a6-s3-dc-10.6084/m9.figshare.27999008"
    assert row["stratum"] == STRATUM
    assert row["normalized_organization_lineage"] == "crossref:publisher:s-karger-ag"
    assert row["artifact_lineage_id"] == "scientific-record:doi:10.6084/m9.figshare.27999008"
    assert row["source_family_id"] == "crossref-supplement-family:doi:10.1159/000543005"
    assert row["before_version_id"] == "crossref:doi:10.1159/000543005"
    assert row["after_version_id"] == "datacite:doi:10.6084/m9.figshare.27999008"
    assert row["before_sha256"] != row["after_sha256"]
    assert row["supplement_resource_type_general"] == "Dataset"
    assert row["enumeration_side"] == "DATACITE_SUPPLEMENT_SIDE"
    assert "creativecommons.org/licenses/by/4.0" in row["license_or_rights_receipt_id"]
    assert datacite_rights(attrs).startswith("https://creativecommons.org")
    software = {"types": {"resourceTypeGeneral": "Software"}, "titles": [{"title": "t"}], "doi": "10.1/d"}
    assert supplement_resource_type(software) == "Software"
    wrong_type = census_record({"attributes": {"doi": "10.1/w", "types": {"resourceTypeGeneral": "Text"}, "relatedIdentifiers": []}})
    assert wrong_type["status"] == "SKIP" and wrong_type["reason"] == "supplement_resource_type_mismatch"
    no_rel = census_record({"attributes": {"doi": "10.1/n", "types": {"resourceTypeGeneral": "Dataset"}, "relatedIdentifiers": []}})
    assert no_rel["status"] == "SKIP" and no_rel["reason"] == "no_doi_typed_supplement_relation"
    assert slugify("Elsevier BV") == "elsevier-bv" and slugify(None) == "unattributed"
    return {
        "decision": "GREEN",
        "supplement_pick_deterministic": True,
        "resource_type_filter_enforced": "Dataset/Software only",
        "article_side_crossref_bound": True,
        "publisher_slug_deterministic": True,
        "network_accessed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--records", type=int, default=300)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--no-snapshot", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        result = self_test()
        code = 0
    else:
        if not 1 <= args.workers <= 2:
            ap.error("--workers must be 1..2")
        if args.records < 1:
            ap.error("--records must be >=1")
        result = census(args.records, args.workers)
        if not args.no_snapshot:
            result = write_snapshot(result)
        code = 0 if result.get("decision", "CAPACITY_OK").startswith(("A6_STRATUM3", "CAPACITY_OK")) else 2
    print(json.dumps(result, indent=2, sort_keys=True)[:200000])
    return code


if __name__ == "__main__":
    raise SystemExit(main())
