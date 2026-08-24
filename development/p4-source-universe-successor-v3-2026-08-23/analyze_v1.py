#!/usr/bin/env python3
"""Analyze the frozen P4 public source-universe harvest without adjudication."""

from __future__ import annotations

import collections
import datetime as dt
import hashlib
import html
import json
import pathlib
import re
import urllib.parse


ROOT = pathlib.Path(__file__).resolve().parent
PROTOCOL = json.loads((ROOT / "PROTOCOL_V1.json").read_text())
BUNDLE = json.loads((ROOT / "HARVEST_BUNDLE_V1.json").read_text())
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>]+", re.I)
DOMAINS = PROTOCOL["scope"]["domains"]
MECHANISMS = PROTOCOL["scope"]["mechanisms"]
KNOWN_REPOSITORY_DOI_PREFIXES = (
    "10.5281/zenodo",
    "10.6084/m9.figshare",
    "10.15131/shef.data",
    "10.17632/",
    "10.7910/dvn/",
    "10.5061/dryad.",
    "10.17605/osf.io/",
)


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def norm_doi(value: object, *, concept: bool = False) -> str | None:
    if not isinstance(value, str):
        return None
    decoded = urllib.parse.unquote(html.unescape(value)).strip().lower()
    decoded = re.sub(r"^(?:doi:|https?://(?:dx\.)?doi\.org/)", "", decoded)
    match = DOI_RE.search(decoded)
    if not match:
        return None
    doi = match.group(0).rstrip(".,;:)]}")
    if concept:
        doi = re.sub(r"\.v\d+$", "", doi)
    return doi


def plausibly_publication_typed_doi(doi: str) -> bool:
    return not doi.startswith(KNOWN_REPOSITORY_DOI_PREFIXES)


def flatten_text(*values: object) -> str:
    parts: list[str] = []

    def walk(value: object) -> None:
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, dict):
            for inner in value.values():
                walk(inner)
        elif isinstance(value, list):
            for inner in value:
                walk(inner)

    for value in values:
        walk(value)
    return " ".join(parts).lower()


def classify_domain(text: str) -> tuple[str | None, dict[str, int], str]:
    scores: dict[str, int] = {}
    for domain, spec in PROTOCOL["discovery_lexicons"].items():
        scores[domain] = sum(1 for token in spec["tokens"] if token.lower() in text)
    best = max(scores.values()) if scores else 0
    if best < 1:
        return None, scores, "CANNOT_CHECK_DOMAIN_UNCLASSIFIED"
    winners = [domain for domain, score in scores.items() if score == best]
    if len(winners) != 1:
        return None, scores, "CANNOT_CHECK_DOMAIN_AMBIGUOUS"
    return winners[0], scores, "DISCOVERY_CLASSIFICATION_ONLY"


def normalized_authors(authors: object) -> tuple[list[str], str | None, str]:
    identities: list[str] = []
    if isinstance(authors, list):
        for author in authors:
            if not isinstance(author, dict):
                continue
            orcid = author.get("orcid") or author.get("orcid_id") or author.get("authorIdentifier")
            name = author.get("full_name") or author.get("name")
            if not name:
                first = author.get("firstName") or author.get("first_name") or ""
                last = author.get("lastName") or author.get("last_name") or ""
                name = f"{first} {last}".strip()
            if isinstance(orcid, str) and orcid.strip():
                identity = "orcid:" + orcid.lower().replace("https://orcid.org/", "").strip()
            elif isinstance(name, str) and name.strip():
                identity = "name:" + re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
            else:
                continue
            if identity not in identities:
                identities.append(identity)
    identities.sort()
    if not identities:
        return [], None, "CANNOT_CHECK_AUTHOR_LINEAGE"
    signature = sha256("\n".join(identities).encode("utf-8"))
    status = "ORCID_OR_NAME_BOUND__HOMONYM_EXTERNAL_CHECK_REQUIRED"
    return identities, signature, status


def dataverse_field_value(field: object) -> object:
    return field.get("value") if isinstance(field, dict) else None


def find_dataverse_publication_dois(value: object) -> list[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        if "publicationIDType" in value and "publicationIDNumber" in value:
            kind = str(dataverse_field_value(value["publicationIDType"]) or "").lower()
            identifier = dataverse_field_value(value["publicationIDNumber"])
            if kind == "doi" or "doi" in kind:
                doi = norm_doi(identifier)
                if doi:
                    found.add(doi)
        for inner in value.values():
            found.update(find_dataverse_publication_dois(inner))
    elif isinstance(value, list):
        for inner in value:
            found.update(find_dataverse_publication_dois(inner))
    return sorted(found)


def dataverse_authors(value: object) -> list[dict]:
    found: list[dict] = []
    if isinstance(value, dict):
        if value.get("typeName") == "author" and isinstance(value.get("value"), list):
            for compound in value["value"]:
                if not isinstance(compound, dict):
                    continue
                name = dataverse_field_value(compound.get("authorName"))
                identifier = dataverse_field_value(compound.get("authorIdentifier"))
                found.append({"name": name, "authorIdentifier": identifier})
        for inner in value.values():
            found.extend(dataverse_authors(inner))
    elif isinstance(value, list):
        for inner in value:
            found.extend(dataverse_authors(inner))
    return found


def license_normalized(provider: str, mechanism: str, raw_license: object) -> tuple[str | None, bool]:
    text = flatten_text(raw_license)
    normalized = None
    if "cc0" in text or "publicdomain/zero/1.0" in text:
        normalized = "CC0-1.0"
    elif "cc by 4.0" in text or "licenses/by/4.0" in text:
        normalized = "CC-BY-4.0"
    elif re.search(r"\bmit\b", text):
        normalized = "MIT"
    elif "apache 2.0" in text or "apache-2.0" in text:
        normalized = "Apache-2.0"
    elif "gpl 2.0+" in text or "gpl-2.0-or-later" in text:
        normalized = "GPL-2.0-or-later"
    elif "gpl 3.0+" in text or "gpl-3.0-or-later" in text:
        normalized = "GPL-3.0-or-later"
    elif "gpl-2.0-only" in text:
        normalized = "GPL-2.0-only"
    elif "gpl-3.0-only" in text:
        normalized = "GPL-3.0-only"
    if provider == "DRYAD":
        accepted = set(PROTOCOL["provider_freeze"]["DRYAD"]["accepted_licenses"])
        return normalized, normalized == "CC0-1.0" and any("CC0" in item for item in accepted)
    if provider == "FIGSHARE":
        key = "accepted_m5_licenses" if mechanism == MECHANISMS[0] else "accepted_m6_licenses"
        return normalized, normalized in set(PROTOCOL["provider_freeze"]["FIGSHARE"][key])
    if provider == "HARVARD_DATAVERSE":
        return normalized, normalized in set(PROTOCOL["provider_freeze"]["HARVARD_DATAVERSE"]["accepted_licenses"])
    return normalized, False


def base_candidate(provider: str, mechanism: str, record: dict, object_exact: str | None, publications: list[str], authors: object, text: str) -> dict:
    object_concept = norm_doi(object_exact, concept=True)
    publication = sorted(set(publications))[0] if publications else None
    identities, author_signature, author_status = normalized_authors(authors)
    domain, scores, domain_status = classify_domain(text)
    identity = f"{provider}|{object_concept or object_exact or 'missing'}|{publication or 'missing'}"
    return {
        "candidate_id": sha256(identity.encode("utf-8"))[:24],
        "provider": provider,
        "provider_family": provider,
        "mechanism_id": mechanism,
        "object_doi_exact": norm_doi(object_exact),
        "object_concept_doi": object_concept,
        "publication_doi": publication,
        "structured_publication_doi_count": len(set(publications)),
        "domain_discovery": domain,
        "domain_scores": scores,
        "domain_status": domain_status,
        "author_identities": identities,
        "author_lineage_signature": author_signature,
        "author_lineage_status": author_status,
        "record_sha256": sha256(canonical_json(record)),
    }


def dryad_candidates() -> list[dict]:
    rows: list[dict] = []
    for record in BUNDLE["dryad"]["records"]:
        relations = []
        relation_evidence = []
        for relation in record.get("relatedWorks") or []:
            if relation.get("relationship") != "primary_article" or str(relation.get("identifierType", "")).lower() != "doi":
                continue
            doi = norm_doi(relation.get("identifier"))
            if doi:
                relations.append(doi)
                relation_evidence.append(relation)
        text = flatten_text(record.get("title"), record.get("abstract"), record.get("usageNotes"), record.get("keywords"))
        row = base_candidate("DRYAD", MECHANISMS[0], record, record.get("identifier"), relations, record.get("authors"), text)
        raw_license = record.get("license")
        normalized, rights_ok = license_normalized("DRYAD", MECHANISMS[0], raw_license)
        href = (record.get("_links") or {}).get("stash:download", {}).get("href")
        download = urllib.parse.urljoin("https://datadryad.org", href) if isinstance(href, str) else None
        advertised = [download] if download and download.startswith("https://") else []
        row.update(
            {
                "relation_evidence": relation_evidence,
                "relation_qualified": bool(relations),
                "license_raw": raw_license,
                "license_normalized": normalized,
                "rights_qualified": rights_ok,
                "direct_download_urls": advertised,
                "direct_download_qualified": False,
                "direct_download_status": "CANNOT_CHECK_ANONYMOUS_DIRECT_DOWNLOAD_AUTHORITY__BOUNDED_RANGE_PROBES_HTTP_401",
                "exact_version_file_lineage_status": "CANNOT_CHECK_EXACT_VERSION_FILE_LINEAGE",
                "mirror_excluded": False,
                "raw_record_pointer": "HARVEST_BUNDLE_V1.json#/dryad/records",
            }
        )
        rows.append(row)
    return rows


def figshare_relation_dois(record: dict) -> tuple[list[str], list[dict]]:
    dois: list[str] = []
    evidence: list[dict] = []
    resource_doi = norm_doi(record.get("resource_doi"))
    if resource_doi:
        dois.append(resource_doi)
        evidence.append({"field": "resource_doi", "value": record.get("resource_doi")})
    allowed = {"issupplementto", "isderivedfrom", "references"}
    for material in record.get("related_materials") or []:
        if not isinstance(material, dict):
            continue
        relation = str(material.get("relation") or material.get("relation_type") or material.get("relationType") or "").replace("_", "").lower()
        if relation not in allowed:
            continue
        for key in ("identifier", "doi", "url", "identifier_value"):
            doi = norm_doi(material.get(key))
            if doi:
                dois.append(doi)
                evidence.append(material)
                break
    object_doi = norm_doi(record.get("doi"), concept=True)
    filtered = [
        doi
        for doi in sorted(set(dois))
        if norm_doi(doi, concept=True) != object_doi and plausibly_publication_typed_doi(doi)
    ]
    return filtered, evidence


def figshare_candidates() -> list[dict]:
    rows: list[dict] = []
    for article_id_text, record in BUNDLE["figshare"]["records"].items():
        article_id = int(article_id_text)
        hit = BUNDLE["figshare"]["hits"].get(str(article_id)) or BUNDLE["figshare"]["hits"].get(article_id_text) or {}
        mechanisms = sorted({membership.get("mechanism") for membership in hit.get("memberships", []) if membership.get("mechanism")})
        mechanism = mechanisms[0] if len(mechanisms) == 1 else "CANNOT_CHECK_MECHANISM_AMBIGUOUS"
        relations, relation_evidence = figshare_relation_dois(record)
        text = flatten_text(record.get("title"), record.get("description"), record.get("tags"), record.get("keywords"), record.get("categories"))
        row = base_candidate("FIGSHARE", mechanism, record, record.get("doi"), relations, record.get("authors"), text)
        raw_license = record.get("license")
        normalized, rights_ok = license_normalized("FIGSHARE", mechanism, raw_license)
        downloads = [
            file.get("download_url")
            for file in record.get("files") or []
            if isinstance(file, dict)
            and file.get("is_link_only") is not True
            and isinstance(file.get("download_url"), str)
            and file["download_url"].startswith("https://")
        ]
        object_doi = row.get("object_doi_exact") or ""
        mirror = object_doi.startswith("10.5281/zenodo") or "zenodo.org" in flatten_text(record.get("url"), record.get("references"))
        row.update(
            {
                "relation_evidence": relation_evidence,
                "relation_qualified": bool(relations),
                "license_raw": raw_license,
                "license_normalized": normalized,
                "rights_qualified": rights_ok,
                "direct_download_urls": downloads,
                "direct_download_qualified": record.get("download_disabled") is not True and bool(downloads),
                "mirror_excluded": mirror,
                "search_memberships": hit.get("memberships", []),
                "raw_record_pointer": f"raw/figshare/records/{article_id}.json",
            }
        )
        rows.append(row)
    return rows


def dataverse_candidates() -> list[dict]:
    rows: list[dict] = []
    for persistent_id, payload in BUNDLE["dataverse"]["records"].items():
        record = payload.get("data") or {}
        version = record.get("latestVersion") or {}
        metadata = version.get("metadataBlocks") or {}
        relations_all = find_dataverse_publication_dois(metadata)
        relations = [doi for doi in relations_all if plausibly_publication_typed_doi(doi)]
        authors = dataverse_authors(metadata)
        text = flatten_text(metadata)
        object_exact = persistent_id
        row = base_candidate("HARVARD_DATAVERSE", MECHANISMS[0], record, object_exact, relations, authors, text)
        raw_license = version.get("license")
        normalized, rights_ok = license_normalized("HARVARD_DATAVERSE", MECHANISMS[0], raw_license)
        downloads: list[str] = []
        for file_entry in version.get("files") or []:
            if not isinstance(file_entry, dict) or file_entry.get("restricted") is not False:
                continue
            data_file = file_entry.get("dataFile") or {}
            file_id = data_file.get("id")
            if file_id is not None and data_file.get("storageIdentifier"):
                downloads.append(f"https://dataverse.harvard.edu/api/access/datafile/{file_id}")
        row.update(
            {
                "relation_evidence": relations_all,
                "repository_typed_relation_dois_excluded": sorted(set(relations_all) - set(relations)),
                "relation_qualified": bool(relations),
                "license_raw": raw_license,
                "license_normalized": normalized,
                "rights_qualified": rights_ok,
                "direct_download_urls": downloads,
                "direct_download_qualified": bool(downloads),
                "mirror_excluded": False,
                "search_memberships": (BUNDLE["dataverse"]["hits"].get(persistent_id) or {}).get("memberships", []),
                "raw_record_pointer": f"raw/dataverse/records/{re.sub(r'[^A-Za-z0-9_.-]', '_', persistent_id)}.json",
            }
        )
        rows.append(row)
    return rows


def strict_candidate(row: dict) -> bool:
    return all(
        [
            row.get("mechanism_id") in MECHANISMS,
            row.get("object_concept_doi"),
            row.get("publication_doi"),
            row.get("object_concept_doi") != row.get("publication_doi"),
            row.get("relation_qualified"),
            row.get("rights_qualified"),
            row.get("direct_download_qualified"),
            not row.get("mirror_excluded"),
            row.get("domain_discovery") in DOMAINS,
            row.get("author_lineage_signature"),
        ]
    )


def stage_counts(rows: list[dict]) -> dict:
    return {
        "raw_objects": len(rows),
        "object_doi_bound": sum(bool(row.get("object_concept_doi")) for row in rows),
        "structured_publication_relation_qualified": sum(bool(row.get("relation_qualified")) for row in rows),
        "rights_qualified": sum(bool(row.get("rights_qualified")) for row in rows),
        "direct_download_qualified": sum(bool(row.get("direct_download_qualified")) for row in rows),
        "domain_discovery_classified": sum(row.get("domain_discovery") in DOMAINS for row in rows),
        "author_lineage_bound": sum(bool(row.get("author_lineage_signature")) for row in rows),
        "mirror_excluded": sum(bool(row.get("mirror_excluded")) for row in rows),
        "strict_metadata_qualified_before_dedup": sum(strict_candidate(row) for row in rows),
    }


def dedup_cell(rows: list[dict]) -> list[dict]:
    accepted: list[dict] = []
    seen_objects: set[str] = set()
    seen_publications: set[str] = set()
    for row in sorted(rows, key=lambda item: (item["provider"], item["object_concept_doi"], item["publication_doi"], item["candidate_id"])):
        if row["object_concept_doi"] in seen_objects or row["publication_doi"] in seen_publications:
            continue
        seen_objects.add(row["object_concept_doi"])
        seen_publications.add(row["publication_doi"])
        accepted.append(row)
    return accepted


def provisional_partition(rows: list[dict]) -> dict:
    by_provider: dict[str, list[dict]] = collections.defaultdict(list)
    for row in rows:
        by_provider[row["provider_family"]].append(row)
    for provider in by_provider:
        by_provider[provider].sort(key=lambda item: item["candidate_id"])
    attempts = []
    for primary_provider in sorted(by_provider):
        primary = by_provider[primary_provider][:24]
        if len(primary) < 24:
            continue
        used_author = {row["author_lineage_signature"] for row in primary}
        for replication_provider in sorted(by_provider):
            if replication_provider == primary_provider:
                continue
            replication = [row for row in by_provider[replication_provider] if row["author_lineage_signature"] not in used_author][:8]
            if len(replication) < 8:
                continue
            used_ids = {row["candidate_id"] for row in primary + replication}
            used_author_2 = used_author | {row["author_lineage_signature"] for row in replication}
            reserve = [
                row
                for row in sorted(rows, key=lambda item: item["candidate_id"])
                if row["candidate_id"] not in used_ids and row["author_lineage_signature"] not in used_author_2
            ][:16]
            attempts.append(
                {
                    "primary_provider": primary_provider,
                    "replication_provider": replication_provider,
                    "primary_candidate_ids": [row["candidate_id"] for row in primary],
                    "replication_candidate_ids": [row["candidate_id"] for row in replication],
                    "reserve_candidate_ids": [row["candidate_id"] for row in reserve],
                    "complete": len(reserve) == 16,
                }
            )
            if len(reserve) == 16:
                return attempts[-1]
    return {
        "primary_provider": None,
        "replication_provider": None,
        "primary_candidate_ids": [],
        "replication_candidate_ids": [],
        "reserve_candidate_ids": [],
        "complete": False,
        "attempt_count": len(attempts),
    }


def main() -> None:
    rows = dryad_candidates() + figshare_candidates() + dataverse_candidates()
    for row in rows:
        row["strict_metadata_qualified"] = strict_candidate(row)
        row["scientific_authority"] = False
        row["external_natural_pair_adjudication_required"] = True
    rows.sort(key=lambda item: (item["provider"], item.get("object_concept_doi") or "", item["candidate_id"]))
    with (ROOT / "CANDIDATES_V1.jsonl").open("wb") as handle:
        for row in rows:
            handle.write(canonical_json(row))

    cells: dict[str, dict] = {}
    any_short = False
    any_transport = bool(BUNDLE["dryad"]["failed_pages"] or BUNDLE["figshare"]["failed_queries"] or BUNDLE["figshare"]["failed_records"] or BUNDLE["dataverse"]["failed_queries"] or BUNDLE["dataverse"]["failed_records"] or BUNDLE["datacite"]["failed_queries"])
    for domain in DOMAINS:
        for mechanism in MECHANISMS:
            key = f"{domain}__{mechanism}"
            strict = [row for row in rows if strict_candidate(row) and row["domain_discovery"] == domain and row["mechanism_id"] == mechanism]
            deduped = dedup_cell(strict)
            provider_counts = dict(sorted(collections.Counter(row["provider_family"] for row in deduped).items()))
            partition = provisional_partition(deduped)
            quota_pass = len(deduped) >= 48
            source_disjoint_pass = partition["complete"]
            observed_cell_pass = quota_pass and source_disjoint_pass
            cell_pass = None if any_transport else observed_cell_pass
            any_short = any_short or not observed_cell_pass
            cells[key] = {
                "domain_id": domain,
                "mechanism_id": mechanism,
                "strict_metadata_qualified_before_cell_dedup": len(strict),
                "unique_candidate_units_after_concept_and_publication_dedup": len(deduped),
                "provider_family_counts": provider_counts,
                "observed_gap_to_48": max(0, 48 - len(deduped)),
                "observed_gap_is_a_confirmed_deficit": not any_transport,
                "quota_48_passed": quota_pass,
                "provisional_source_disjoint_partition": partition,
                "source_disjoint_replication_gate_passed": source_disjoint_pass,
                "cell_source_frame_passed": cell_pass,
                "cell_gate_evaluable": not any_transport,
                "candidate_ids": [row["candidate_id"] for row in deduped],
                "authority_boundary": "PUBLIC_METADATA_SOURCE_FEASIBILITY_ONLY__EXTERNAL_ADJUDICATION_REQUIRED",
            }

    if any_transport:
        terminal = "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK"
    elif any_short:
        terminal = PROTOCOL["allocation_gate"]["shortfall_terminal"]
    else:
        terminal = PROTOCOL["allocation_gate"]["positive_terminal"]

    per_provider = {provider: stage_counts([row for row in rows if row["provider"] == provider]) for provider in sorted({row["provider"] for row in rows})}
    license_counts: dict[str, dict] = {}
    for provider in sorted({row["provider"] for row in rows}):
        provider_rows = [row for row in rows if row["provider"] == provider]
        counts = collections.Counter((row.get("license_normalized") or "UNMAPPED") for row in provider_rows)
        license_counts[provider] = dict(sorted(counts.items()))
    provenance_path = ROOT / "PROVENANCE_URLS_V1.json"
    provenance = json.loads(provenance_path.read_text()) if provenance_path.exists() else {"captures": []}
    rights_capture_ids = [
        capture.get("id")
        for capture in provenance.get("captures", [])
        if any(token in str(capture.get("id", "")) for token in ("license", "terms", "article_", "dataset_", "datafile_", "file_"))
    ]
    rights = {
        "schema_version": "orion.p4.source-universe-rights-evidence.v1",
        "created_at": now(),
        "protocol_sha256": sha256((ROOT / "PROTOCOL_V1.json").read_bytes()),
        "provenance_urls_sha256": sha256(provenance_path.read_bytes()) if provenance_path.exists() else None,
        "supporting_capture_ids": rights_capture_ids,
        "accepted_license_rules": {provider: spec for provider, spec in PROTOCOL["provider_freeze"].items() if provider != "DATACITE"},
        "observed_normalized_license_counts": license_counts,
        "rights_qualified_counts": {provider: counts["rights_qualified"] for provider, counts in per_provider.items()},
        "boundary": "item metadata rights only; linked publication rights and natural-pair eligibility remain unadjudicated",
        "cannot_check_rule": "unmapped, missing, generic GPL, host-only, collection-only or linked-object-only rights are not accepted",
    }
    (ROOT / "RIGHTS_EVIDENCE_V1.json").write_bytes(canonical_json(rights))

    cell_artifact = {
        "schema_version": "orion.p4.source-universe-cell-counts.v1",
        "created_at": now(),
        "protocol_sha256": sha256((ROOT / "PROTOCOL_V1.json").read_bytes()),
        "candidate_jsonl_sha256": sha256((ROOT / "CANDIDATES_V1.jsonl").read_bytes()),
        "candidate_rows": len(rows),
        "per_provider_stage_counts": per_provider,
        "cells": cells,
    }
    (ROOT / "CELL_COUNTS_V1.json").write_bytes(canonical_json(cell_artifact))

    transport_audit_path = ROOT / "TRANSPORT_AUDIT_V1.json"
    transport_audit = json.loads(transport_audit_path.read_text()) if transport_audit_path.exists() else None

    if any_transport:
        next_discriminator = "Resume only the 1,804 frozen Figshare and 1,028 frozen Harvard Dataverse missing full-record identities after public API access recovers; add no pages or queries. If a completed eight-cell recount remains short or M6 remains single-family, open a separately frozen JOSS/GitHub, Bioconductor/CRAN, OSF or other exact-rights software-provider lane."
    else:
        next_discriminator = "For each short M6 cell, add a non-Figshare software content provider with exact item-level software licence, structured publication DOI relation and unrestricted bytes; then repeat cross-provider concept/publication/author-lineage deduplication before external adjudication."
    result = {
        "schema_version": "orion.p4.source-universe-successor-result.v1",
        "paper_id": "P4",
        "lane_id": PROTOCOL["lane_id"],
        "created_at": now(),
        "authority": "PUBLIC_DEVELOPMENT_EVIDENCE_ONLY",
        "outcomes_accessed": False,
        "protected_confirmation": False,
        "natural_pair_adjudication_executed": False,
        "model_outcomes_executed": False,
        "protocol_sha256": sha256((ROOT / "PROTOCOL_V1.json").read_bytes()),
        "harvest_bundle_sha256": sha256((ROOT / "HARVEST_BUNDLE_V1.json").read_bytes()),
        "candidate_jsonl_sha256": cell_artifact["candidate_jsonl_sha256"],
        "provenance_urls_sha256": rights["provenance_urls_sha256"],
        "candidate_rows": len(rows),
        "transport_incomplete": any_transport,
        "transport_audit_sha256": sha256(transport_audit_path.read_bytes()) if transport_audit_path.exists() else None,
        "transport_completeness": transport_audit.get("full_record_completeness") if transport_audit else None,
        "gate_evaluable": not any_transport,
        "all_eight_cells_passed": None if any_transport else not any_short,
        "terminal": terminal,
        "overall_scientific_terminal_unchanged": PROTOCOL["allocation_gate"]["overall_scientific_terminal"],
        "per_provider_stage_counts": per_provider,
        "cells": cells,
        "datacite_discovery_only": {
            "unique_dois": len(BUNDLE["datacite"]["unique_discovery_dois"]),
            "host_hit_counts": BUNDLE["datacite"]["host_hit_counts"],
            "counted_as_independent_units": 0,
        },
        "provider_evidence_terminals": provenance.get("provider_terminals", {}),
        "provider_evidence_errors_and_cannot_check": provenance.get("errors_and_cannot_check", []),
        "predecessor_negative_identities_preserved": [item["identity"] for item in PROTOCOL["predecessors"]],
        "cannot_check_residuals": [
            "domain labels are discovery-only until outcome-blind external adjudication",
            "normalized author names/ORCIDs do not independently establish complete author-lineage disjointness",
            "same exact target claim and one-coordinate information-state change were not adjudicated",
            "linked-publication content rights were not inferred from item rights",
            "DataCite discovery records were not counted as provider-disjoint content units"
        ],
        "forbidden_claims": PROTOCOL["claim_boundary"]["forbidden"],
        "next_discriminator": next_discriminator,
    }
    (ROOT / "RESULT_V1.json").write_bytes(canonical_json(result))

    lines = [
        "# P4 source-universe successor V3 result",
        "",
        f"**Terminal:** `{terminal}`",
        "",
        "This is a bounded public-metadata source-feasibility audit. It is not protected confirmation, a natural-pair adjudication, a model evaluation, or evidence of ORION superiority.",
        "",
        "## Frozen gate",
        "",
        "Each of the four domains x M5/M6 cells required 24 primary, 8 source-family-disjoint replication, and 16 reserve units (48 unique candidates), with exact structured publication relation, accepted item licence, unrestricted direct-download identity, and concept/publication/artifact deduplication. Surplus could not compensate for a short cell.",
        "",
        "## Counts",
        "",
        "| Cell | Observed strict unique units | Observed gap to 48 | Provider counts | Observed source-disjoint gate |",
        "|---|---:|---:|---|---|",
    ]
    for cell in cells.values():
        providers = ", ".join(f"{provider}={count}" for provider, count in cell["provider_family_counts"].items()) or "none"
        lines.append(f"| {cell['domain_id']} / {cell['mechanism_id']} | {cell['unique_candidate_units_after_concept_and_publication_dedup']} | {cell['observed_gap_to_48']} | {providers} | {'PASS' if cell['source_disjoint_replication_gate_passed'] else 'FAIL'} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A metadata-qualified candidate is not an eligible natural pair. Public discovery classifications, author-lineage normalization, same-claim identity, the one-coordinate intervention, and material-claim resolvability still require outcome-blind external adjudication. Files, versions, queries, mirrors, and DataCite metadata were never counted as independent units. When transport is incomplete, observed gaps are not treated as confirmed deficits and the eight-cell gate is `CANNOT_CHECK`.",
            "",
            "## Negative-result recursion",
            "",
            result["next_discriminator"],
            "",
            "All predecessor negative and `CANNOT_CHECK` identities remain unchanged; the overall scientific terminal remains `P4_NATURALISTIC_V2_IDENTITY_COMPLETE__FEASIBILITY_AND_EXTERNAL_PANEL_CANNOT_CHECK`.",
        ]
    )
    if transport_audit:
        lines.extend(
            [
                "",
                "## Transport completeness",
                "",
                f"Figshare full records: {transport_audit['full_record_completeness']['FIGSHARE']['captured_full_records']}/{transport_audit['full_record_completeness']['FIGSHARE']['search_unique_ids']}; Harvard Dataverse full records: {transport_audit['full_record_completeness']['HARVARD_DATAVERSE']['captured_full_records']}/{transport_audit['full_record_completeness']['HARVARD_DATAVERSE']['search_unique_ids']}. Frozen search pages were complete, but full-record HTTP 403/429 responses left the cell gate unevaluable. The missing identities remain frozen for a resume-only retry; no pages or queries may be added in this iteration.",
            ]
        )
    (ROOT / "RESULT_REPORT.md").write_text("\n".join(lines) + "\n")

    if any_transport:
        gate_sentence = "The frozen 48-unit and source-disjoint-replication gate was applied separately in every domain-mechanism cell, but provider transport incompleteness prevented a definitive eight-cell decision; all observed gaps are reported only as lower-bound diagnostics."
    else:
        gate_sentence = "The frozen 48-unit and source-disjoint-replication gate was evaluated separately in every domain-mechanism cell; surplus was not pooled across cells."
    wording = [
        "# Evidence-licensed manuscript-ready wording",
        "",
        "No manuscript was edited by this lane. The following negative/source-feasibility wording is licensed by the V3 receipts:",
        "",
        f"> A preregistered public-source expansion audited Dryad, Figshare, Harvard Dataverse, and DataCite for the article-to-data and article-to-code mechanisms. We counted at most one candidate per concept DOI and linked publication DOI, excluded mirrors and metadata aggregators as independent providers, and required an exact accepted item licence, a structured publication relation, and an unrestricted direct-download identity. {gate_sentence} This audit establishes only bounded source feasibility. Natural-pair identity, author-lineage disjointness, same-claim preservation, and scientific resolvability remain subject to outcome-blind external adjudication, and no model-performance or superiority claim follows.",
        "",
        f"> The resulting source-feasibility terminal was `{terminal}`; all predecessor negative and `CANNOT_CHECK` terminals were retained.",
    ]
    (ROOT / "MANUSCRIPT_READY_WORDING.md").write_text("\n".join(wording) + "\n")
    print(json.dumps({"terminal": terminal, "candidate_rows": len(rows), "transport_incomplete": any_transport, "cells": {key: value["unique_candidate_units_after_concept_and_publication_dedup"] for key, value in cells.items()}}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
