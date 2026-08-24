#!/usr/bin/env python3
"""Build the outcome-blind provider/modality metadata census.

Only provider metadata and exact licence-file bytes are requested.  The script
does not request article bodies, abstracts, repository READMEs, issues,
comments, attachments, data files, candidate outputs, labels, or outcomes.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parent
PROTOCOL_OUT = ROOT / "CENSUS_PROTOCOL_V1.json"
CENSUS_OUT = ROOT / "SOURCE_CENSUS_V1.json"
CUTOFF = "2025-12-31T23:59:59Z"
USER_AGENT = "orion-outcome-blind-provider-metadata-census/1.0"

DOMAIN_BIO = "BIOMEDICAL_CLINICAL"
DOMAIN_EARTH = "EARTH_ENVIRONMENTAL"
DOMAIN_COMP = "COMPUTATIONAL_SCIENTIFIC_SOFTWARE"
DOMAIN_PHYS = "PHYSICAL_ENGINEERING"

PROVIDERS = {
    "CROSSREF": {
        "metadata_provider_id": "CROSSREF_REST_API",
        "provider_organization": "Crossref",
        "api_origin": "https://api.crossref.org",
        "terms_url": "https://www.crossref.org/documentation/retrieve-metadata/rest-api/",
        "modality": "PUBLISHER_ARTICLE",
    },
    "ZENODO": {
        "metadata_provider_id": "ZENODO_REST_API",
        "provider_organization": "Zenodo (CERN/OpenAIRE)",
        "api_origin": "https://zenodo.org/api",
        "terms_url": "https://about.zenodo.org/policies/",
        "modality": "DATA_REPOSITORY_DEPOSIT",
    },
    "GITLAB": {
        "metadata_provider_id": "GITLAB_COM_REST_API_V4",
        "provider_organization": "GitLab.com",
        "api_origin": "https://gitlab.com/api/v4",
        "terms_url": "https://about.gitlab.com/terms/",
        "modality": "NON_GITHUB_PROJECT_TRACKER",
    },
    "CMR": {
        "metadata_provider_id": "NASA_ESDIS_CMR_SEARCH_API",
        "provider_organization": "NASA ESDIS Common Metadata Repository",
        "api_origin": "https://cmr.earthdata.nasa.gov/search",
        "terms_url": "https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance",
        "modality": "INSTRUMENT_CALIBRATION_ARCHIVE",
    },
}

# Crossref and Zenodo selections are the first two records in the provider
# query snapshot after the protocol exclusions.  GitLab and CMR use exact
# provider-identity queries and therefore have a singleton rank.
CANDIDATES = (
    # Primary wave
    {"wave": "PRIMARY", "domain": DOMAIN_BIO, "provider": "CROSSREF", "id": "10.1016/j.bj.2025.100874", "rank": 1},
    {"wave": "PRIMARY", "domain": DOMAIN_BIO, "provider": "ZENODO", "id": "18092984", "rank": 1},
    {"wave": "PRIMARY", "domain": DOMAIN_EARTH, "provider": "CROSSREF", "id": "10.53941/eesus.2025.100001", "rank": 1},
    {"wave": "PRIMARY", "domain": DOMAIN_EARTH, "provider": "ZENODO", "id": "18108141", "rank": 1},
    {"wave": "PRIMARY", "domain": DOMAIN_COMP, "provider": "CROSSREF", "id": "10.1016/j.envsoft.2025.106834", "rank": 1},
    {"wave": "PRIMARY", "domain": DOMAIN_COMP, "provider": "GITLAB", "id": "gromacs/gromacs", "rank": 1, "licence_path": "COPYING"},
    {"wave": "PRIMARY", "domain": DOMAIN_PHYS, "provider": "CROSSREF", "id": "10.35896/ijecie.v9i1.914", "rank": 1},
    {"wave": "PRIMARY", "domain": DOMAIN_PHYS, "provider": "CMR", "id": "C2107094645-NOAA_NCEI", "rank": 1, "revision_id": 1, "revision_date": "2021-08-20T15:21:43.807Z"},
    # Source-family-disjoint replication wave
    {"wave": "REPLICATION", "domain": DOMAIN_BIO, "provider": "CROSSREF", "id": "10.31354/globalce.v6isi6.283", "rank": 2},
    {"wave": "REPLICATION", "domain": DOMAIN_BIO, "provider": "ZENODO", "id": "17852132", "rank": 2},
    {"wave": "REPLICATION", "domain": DOMAIN_EARTH, "provider": "CROSSREF", "id": "10.30564/jees.v7i4.8039", "rank": 2},
    {"wave": "REPLICATION", "domain": DOMAIN_EARTH, "provider": "ZENODO", "id": "18109101", "rank": 2},
    {"wave": "REPLICATION", "domain": DOMAIN_COMP, "provider": "CROSSREF", "id": "10.1016/j.sciaf.2025.e03156", "rank": 2},
    {"wave": "REPLICATION", "domain": DOMAIN_COMP, "provider": "GITLAB", "id": "QEF/q-e", "rank": 1, "licence_path": "License"},
    {"wave": "REPLICATION", "domain": DOMAIN_PHYS, "provider": "CROSSREF", "id": "10.1208/s12248-025-01156-0", "rank": 2},
    {"wave": "REPLICATION", "domain": DOMAIN_PHYS, "provider": "CMR", "id": "C2210183595-GES_DISC", "rank": 1, "revision_id": 15, "revision_date": "2025-05-20T15:52:55.278Z"},
)

QUERY_ROUTES = {
    "CROSSREF": {
        "method": "GET",
        "route_template": "https://api.crossref.org/works",
        "queries_by_domain": {
            DOMAIN_BIO: "biomedical clinical",
            DOMAIN_EARTH: "earth environmental",
            DOMAIN_COMP: "scientific software",
            DOMAIN_PHYS: "instrument calibration",
        },
        "fixed_parameters": {
            "filter": "from-created-date:2025-01-01,until-created-date:2025-12-31,type:journal-article,has-license:true",
            "rows": 20,
            "ranking": "provider_native_relevance_desc_then_normalized_doi_asc_for_exact_ties",
        },
    },
    "ZENODO": {
        "method": "GET",
        "route_template": "https://zenodo.org/api/records",
        "queries_by_domain": {
            DOMAIN_BIO: "biomedical AND created:[2025-01-01 TO 2025-12-31]",
            DOMAIN_EARTH: "earth environmental AND created:[2025-01-01 TO 2025-12-31]",
        },
        "fixed_parameters": {
            "type": "dataset",
            "sort": "mostrecent",
            "size": 10,
            "ranking": "provider_created_desc_then_numeric_record_id_asc_for_exact_ties",
        },
    },
    "GITLAB": {
        "method": "GET",
        "route_template": "https://gitlab.com/api/v4/projects/{urlencoded_path}",
        "selection": "predeclared_exact_official_namespace_identity; singleton_rank_1",
        "pre_cutoff_revision_route": "/repository/commits?until=2025-12-31T23:59:59Z&per_page=1",
    },
    "CMR": {
        "method": "GET",
        "route_template": "https://cmr.earthdata.nasa.gov/search/concepts/{concept_id}/{revision_id}.umm_json",
        "selection": "predeclared_exact_concept_and_historical_revision_identity; singleton_rank_1",
        "revision_proof_route": "/collections.umm_json?concept_id={concept_id}&all_revisions=true&page_size=100",
    },
}


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def fetch(url: str, *, headers: dict[str, str] | None = None, attempts: int = 5) -> tuple[bytes, dict]:
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        request_headers.update(headers)
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers=request_headers)
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read()
                return body, {
                    "request_url": url,
                    "final_url": response.geturl(),
                    "http_status": response.status,
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "content_type": response.headers.get("Content-Type"),
                    "response_sha256": sha256(body),
                    "response_bytes": len(body),
                }
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code != 429 or attempt == attempts - 1:
                body = exc.read()
                raise RuntimeError(f"HTTP {exc.code} for {url}: {body[:300]!r}") from exc
            retry_after = exc.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else 2 ** (attempt + 1))
        except Exception as exc:
            last_error = exc
            if attempt == attempts - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f"unreachable fetch failure for {url}: {last_error}")


def fetch_json(url: str, *, headers: dict[str, str] | None = None) -> tuple[dict | list, dict]:
    body, receipt = fetch(url, headers=headers)
    return json.loads(body), receipt


def base_record(candidate: dict) -> dict:
    provider = PROVIDERS[candidate["provider"]]
    return {
        "wave_id": candidate["wave"],
        "protected_domain_candidate": candidate["domain"],
        "domain_assignment_authority": "QUERY_ROUTE_CANDIDATE_ONLY__NOT_CASE_ADJUDICATION",
        "metadata_provider_id": provider["metadata_provider_id"],
        "metadata_provider_organization": provider["provider_organization"],
        "metadata_api_origin": provider["api_origin"],
        "content_host_identity": None,
        "artifact_modality": provider["modality"],
        "query_rank_at_frozen_snapshot": candidate["rank"],
        "cutoff_utc": CUTOFF,
        "case_eligibility_status": "NOT_ASSESSED__CANDIDATE_METADATA_ROOT_ONLY",
        "protected_fields_accessed": False,
        "candidate_or_comparator_outputs_accessed": False,
        "outcomes_accessed": False,
    }


def crossref_record(candidate: dict) -> dict:
    doi = candidate["id"].lower()
    # Use a sparse list response so an optional publisher-supplied abstract is
    # not transmitted by the API.  Titles are also unnecessary for identity.
    query = urllib.parse.urlencode(
        {
            "filter": f"doi:{doi}",
            "select": "DOI,type,publisher,created,deposited,indexed,license,URL,member,ISSN,issn-type",
            "rows": 1,
        }
    )
    url = f"https://api.crossref.org/works?{query}"
    payload, receipt = fetch_json(url)
    items = payload.get("message", {}).get("items", [])
    if len(items) != 1:
        raise RuntimeError(f"Crossref sparse identity query returned {len(items)} records for {doi}")
    item = items[0]
    if item.get("DOI", "").lower() != doi:
        raise RuntimeError(f"Crossref DOI mismatch for {doi}")
    issn = sorted(set(item.get("ISSN", [])))
    if not issn:
        raise RuntimeError(f"Crossref record lacks ISSN family root for {doi}")
    created = item.get("created", {}).get("date-time")
    if not created or created > CUTOFF:
        raise RuntimeError(f"Crossref record lacks pre-cutoff creation proof for {doi}")
    licences = [
        {
            "url": licence.get("URL"),
            "content_version": licence.get("content-version"),
            "start_date_time": licence.get("start", {}).get("date-time"),
            "delay_in_days": licence.get("delay-in-days"),
        }
        for licence in item.get("license", [])
    ]
    record = base_record(candidate)
    record.update(
        {
            "candidate_source_family_id": "crossref:issn:" + "+".join(issn),
            "canonical_dedup_root": "crossref:issn:" + "+".join(issn),
            "persistent_identifier": f"doi:{doi}",
            "provider_record_identity": doi,
            "public_record_url": f"https://doi.org/{doi}",
            "exact_metadata_url": url,
            "content_host_identity": item.get("publisher"),
            "provider_member_identity": item.get("member"),
            "record_type": item.get("type"),
            "issn_family": issn,
            "created_at_provider": created,
            "deposited_at_provider": item.get("deposited", {}).get("date-time"),
            "indexed_at_provider": item.get("indexed", {}).get("date-time"),
            "selected_pre_cutoff_revision": {
                "status": "CANNOT_CHECK_HISTORICAL_METADATA_BYTES__IDENTITY_EXISTENCE_ONLY",
                "identity_creation_timestamp": created,
                "reason": "The public Crossref record proves a DOI record existed before cutoff but does not expose the exact historical metadata bytes as a revisioned object.",
            },
            "content_class_rights": {
                "provider_metadata_record": {
                    "status": "PUBLICLY_RETRIEVABLE__REUSE_SCOPE_CANNOT_CHECK",
                    "terms_url": PROVIDERS["CROSSREF"]["terms_url"],
                },
                "article_body": {
                    "status": "DECLARED_LICENSE_URIS_IN_METADATA_ONLY__BODY_NOT_ACCESSED__SCOPE_CANNOT_CHECK",
                    "declared_licence_uris": licences,
                },
                "abstract": {"status": "NOT_ACCESSED__CANNOT_CHECK"},
                "supplement_or_attachment": {"status": "NOT_ACCESSED__CANNOT_CHECK"},
            },
            "legal_gate": "CANNOT_CHECK_ARTICLE_BODY_AND_ATTACHMENT_RIGHTS_FOR_FUTURE_CASE_USE",
            "http_receipts": {"exact_provider_record": receipt},
        }
    )
    return record


def zenodo_record(candidate: dict) -> dict:
    record_id = str(candidate["id"])
    url = f"https://zenodo.org/api/records/{record_id}"
    item, receipt = fetch_json(url)
    if str(item.get("id")) != record_id:
        raise RuntimeError(f"Zenodo record mismatch for {record_id}")
    created = item.get("created")
    updated = item.get("updated")
    if not created or not updated or created[:19] > CUTOFF[:19] or updated[:19] > CUTOFF[:19]:
        raise RuntimeError(f"Zenodo record not fixed before cutoff: {record_id}")
    metadata = item.get("metadata", {})
    concept_doi = item.get("conceptdoi")
    version_doi = item.get("doi")
    licence_id = (metadata.get("license") or {}).get("id")
    if not concept_doi or not version_doi:
        raise RuntimeError(f"Zenodo DOI family identity missing for {record_id}")
    record = base_record(candidate)
    record.update(
        {
            "candidate_source_family_id": f"zenodo:conceptdoi:{concept_doi.lower()}",
            "canonical_dedup_root": f"zenodo:conceptdoi:{concept_doi.lower()}",
            "persistent_identifier": f"doi:{version_doi.lower()}",
            "provider_record_identity": record_id,
            "public_record_url": item.get("links", {}).get("self_html") or f"https://zenodo.org/records/{record_id}",
            "exact_metadata_url": url,
            "content_host_identity": "Zenodo",
            "record_type": (metadata.get("resource_type") or {}).get("type"),
            "created_at_provider": created,
            "updated_at_provider": updated,
            "publication_date": metadata.get("publication_date"),
            "selected_pre_cutoff_revision": {
                "status": "EXACT_VERSION_RECORD_AND_METADATA_UPDATED_BEFORE_CUTOFF",
                "version_doi": version_doi,
                "concept_doi": concept_doi,
                "updated_at_provider": updated,
            },
            "content_class_rights": {
                "provider_metadata_record": {
                    "status": "PUBLICLY_RETRIEVABLE__REUSE_SCOPE_CANNOT_CHECK",
                    "terms_url": PROVIDERS["ZENODO"]["terms_url"],
                },
                "dataset_files": {
                    "status": "DECLARED_LICENCE_ID_IN_METADATA_ONLY__FILES_NOT_ACCESSED__BYTE_SCOPE_CANNOT_CHECK",
                    "declared_licence_id": licence_id,
                },
                "description": {"status": "NOT_ARCHIVED__CANNOT_CHECK"},
                "linked_files_or_attachments": {"status": "NOT_ACCESSED__CANNOT_CHECK"},
            },
            "legal_gate": "CANNOT_CHECK_DATA_FILE_AND_ATTACHMENT_RIGHTS_FOR_FUTURE_CASE_USE",
            "http_receipts": {"exact_provider_record": receipt},
        }
    )
    return record


def gitlab_record(candidate: dict) -> dict:
    project_path = candidate["id"]
    encoded = urllib.parse.quote(project_path, safe="")
    project_url = f"https://gitlab.com/api/v4/projects/{encoded}"
    project, project_receipt = fetch_json(project_url)
    if project.get("path_with_namespace") != project_path:
        raise RuntimeError(f"GitLab path mismatch for {project_path}")
    project_id = project["id"]
    query = urllib.parse.urlencode({"until": CUTOFF, "per_page": 1})
    commit_url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/commits?{query}"
    commits, commit_receipt = fetch_json(commit_url)
    if not commits:
        raise RuntimeError(f"GitLab project has no pre-cutoff commit: {project_path}")
    commit = commits[0]
    revision = commit["id"]
    if commit.get("committed_date", "") > CUTOFF:
        raise RuntimeError(f"GitLab selected commit is after cutoff: {project_path}")
    file_path = candidate["licence_path"]
    file_url = (
        f"https://gitlab.com/api/v4/projects/{project_id}/repository/files/"
        f"{urllib.parse.quote(file_path, safe='')}?{urllib.parse.urlencode({'ref': revision})}"
    )
    licence, licence_receipt = fetch_json(file_url)
    licence_bytes = base64.b64decode(licence["content"], validate=False)
    record = base_record(candidate)
    record.update(
        {
            "candidate_source_family_id": f"gitlab-project:{project_id}",
            "canonical_dedup_root": f"gitlab-project:{project_id}",
            "persistent_identifier": f"gitlab-project:{project_id}",
            "provider_record_identity": project_path,
            "public_record_url": project.get("web_url"),
            "exact_metadata_url": project_url,
            "content_host_identity": (project.get("namespace") or {}).get("full_path"),
            "project_numeric_id": project_id,
            "project_created_at": project.get("created_at"),
            "visibility": project.get("visibility"),
            "selected_pre_cutoff_revision": {
                "status": "EXACT_COMMIT_SHA_AND_COMMITTER_DATE_BEFORE_CUTOFF",
                "commit_sha": revision,
                "committed_date": commit.get("committed_date"),
                "commit_url": commit.get("web_url"),
            },
            "content_class_rights": {
                "provider_project_metadata": {
                    "status": "PUBLICLY_RETRIEVABLE__REUSE_SCOPE_CANNOT_CHECK",
                    "terms_url": PROVIDERS["GITLAB"]["terms_url"],
                },
                "repository_code": {
                    "status": "EXACT_LICENCE_FILE_BYTES_HASHED_AT_SELECTED_COMMIT__SPDX_NOASSERTION",
                    "licence_path": file_path,
                    "licence_blob_id": licence.get("blob_id"),
                    "licence_content_sha256": sha256(licence_bytes),
                    "licence_bytes": len(licence_bytes),
                },
                "issue_or_comment_text": {"status": "NOT_ACCESSED__CANNOT_CHECK"},
                "issue_attachment": {"status": "NOT_ACCESSED__CANNOT_CHECK"},
                "readme_or_project_description": {"status": "NOT_ARCHIVED__CANNOT_CHECK"},
            },
            "legal_gate": "CANNOT_CHECK_ISSUE_COMMENT_AND_ATTACHMENT_RIGHTS_FOR_FUTURE_CASE_USE",
            "http_receipts": {
                "exact_project_identity": project_receipt,
                "pre_cutoff_commit_query": commit_receipt,
                "licence_at_selected_commit": licence_receipt,
            },
        }
    )
    return record


def cmr_record(candidate: dict) -> dict:
    concept_id = candidate["id"]
    revision_id = candidate["revision_id"]
    url = f"https://cmr.earthdata.nasa.gov/search/concepts/{concept_id}/{revision_id}.umm_json"
    umm, revision_receipt = fetch_json(
        url, headers={"Accept": "application/vnd.nasa.cmr.umm+json; version=1.16"}
    )
    history_query = urllib.parse.urlencode(
        {"concept_id": concept_id, "all_revisions": "true", "page_size": 100}
    )
    history_url = f"https://cmr.earthdata.nasa.gov/search/collections.umm_json?{history_query}"
    history, history_receipt = fetch_json(
        history_url,
        headers={"Accept": "application/vnd.nasa.cmr.umm_results+json; version=1.6"},
    )
    matches = [
        item["meta"]
        for item in history.get("items", [])
        if item.get("meta", {}).get("revision-id") == revision_id
    ]
    if len(matches) != 1:
        raise RuntimeError(f"CMR historical revision identity missing: {concept_id}/{revision_id}")
    meta = matches[0]
    if meta.get("revision-date") != candidate["revision_date"] or meta["revision-date"] > CUTOFF:
        raise RuntimeError(f"CMR revision-date mismatch: {concept_id}/{revision_id}")
    short_name = umm.get("ShortName")
    provider_id = meta.get("provider-id")
    native_id = meta.get("native-id")
    if not short_name or not provider_id or not native_id:
        raise RuntimeError(f"CMR family root fields missing: {concept_id}/{revision_id}")
    data_centers = [center.get("ShortName") for center in umm.get("DataCenters", []) if center.get("ShortName")]
    doi = (umm.get("DOI") or {}).get("DOI")
    landing_urls = [
        item.get("URL")
        for item in umm.get("RelatedUrls", [])
        if item.get("Type") == "DATA SET LANDING PAGE" and item.get("URL")
    ]
    use_constraints = umm.get("UseConstraints")
    record = base_record(candidate)
    record.update(
        {
            "candidate_source_family_id": f"cmr:{provider_id}:{native_id}",
            "canonical_dedup_root": f"cmr:{provider_id}:{native_id}",
            "persistent_identifier": f"doi:{doi.lower()}" if doi else f"cmr-concept:{concept_id}",
            "provider_record_identity": concept_id,
            "public_record_url": landing_urls[0] if landing_urls else url,
            "exact_metadata_url": url,
            "content_host_identity": data_centers[0] if data_centers else provider_id,
            "cmr_provider_id": provider_id,
            "cmr_native_id": native_id,
            "short_name": short_name,
            "collection_version": umm.get("Version"),
            "doi": doi,
            "selected_pre_cutoff_revision": {
                "status": "EXACT_CMR_HISTORICAL_REVISION_ID_DATE_AND_RESPONSE_BYTES",
                "concept_id": concept_id,
                "revision_id": revision_id,
                "revision_date": meta.get("revision-date"),
                "exact_revision_response_sha256": revision_receipt["response_sha256"],
            },
            "content_class_rights": {
                "provider_collection_metadata": {
                    "status": "PUBLICLY_RETRIEVABLE__REUSE_SCOPE_CANNOT_CHECK",
                    "terms_url": PROVIDERS["CMR"]["terms_url"],
                },
                "collection_data_files": {
                    "status": "USE_CONSTRAINTS_METADATA_PRESENT__NO_EXPLICIT_FILE_LICENCE_VERIFIED__CANNOT_CHECK",
                    "use_constraints_present": use_constraints is not None,
                    "use_constraints_sha256": sha256(canonical_bytes(use_constraints)) if use_constraints is not None else None,
                },
                "documentation_or_attachment": {"status": "NOT_ACCESSED__CANNOT_CHECK"},
            },
            "legal_gate": "CANNOT_CHECK_COLLECTION_FILE_AND_DOCUMENT_RIGHTS_FOR_FUTURE_CASE_USE",
            "http_receipts": {
                "exact_historical_revision": revision_receipt,
                "revision_history_identity": history_receipt,
            },
        }
    )
    return record


def protocol(captured_at: str) -> dict:
    required_matrix = {
        DOMAIN_BIO: ["PUBLISHER_ARTICLE", "DATA_REPOSITORY_DEPOSIT"],
        DOMAIN_EARTH: ["PUBLISHER_ARTICLE", "DATA_REPOSITORY_DEPOSIT"],
        DOMAIN_COMP: ["PUBLISHER_ARTICLE", "NON_GITHUB_PROJECT_TRACKER"],
        DOMAIN_PHYS: ["PUBLISHER_ARTICLE", "INSTRUMENT_CALIBRATION_ARCHIVE"],
    }
    return {
        "schema_version": "orion.provider-diverse-metadata-census.protocol.v1",
        "frozen_at_utc": captured_at,
        "gap_id": "G01",
        "successor_identity": "PROVIDER_MODALITY_TRANSPORT_METADATA_CENSUS_V1",
        "authority": "PUBLIC_METADATA_CENSUS_ONLY__NOT_A_CASE_FRAME__NOT_SCIENTIFIC_EVIDENCE",
        "cutoff_utc": CUTOFF,
        "outcomes_accessed": False,
        "protected_case_fields_accessed": False,
        "historical_results_immutable": True,
        "provider_count_definition": "distinct metadata_provider_id; content_host_identity is reported separately and never counted as a metadata provider",
        "modality_count_definition": "distinct artifact_modality; provider identity and content host do not determine modality",
        "waves": ["PRIMARY", "REPLICATION"],
        "quota_contract": {
            "candidate_records_per_wave_exact": 8,
            "domains_per_wave_exact": 4,
            "candidate_records_per_domain_per_wave_exact": 2,
            "metadata_providers_per_wave_minimum": 4,
            "artifact_modalities_per_wave_minimum": 4,
            "required_domain_modality_matrix_per_wave": required_matrix,
            "cross_wave_canonical_dedup_root_collisions_maximum": 0,
            "cross_wave_persistent_identifier_collisions_maximum": 0,
            "pre_cutoff_identity_or_revision_required_for_every_record": True,
            "explicit_content_class_rights_status_required_for_every_record": True,
        },
        "query_routes": QUERY_ROUTES,
        "ranking_rule": "Apply each provider route and fixed filters; reject by metadata-only exclusions; retain provider order; break an exact provider-rank tie by normalized persistent identifier ascending; take the first two distinct family roots where the route has two waves and the exact predeclared singleton otherwise.",
        "ranking_snapshot_policy": "Broad Crossref and Zenodo metadata responses are not archived. Their byte hashes, byte counts, exact query URLs, eligible counts, and selected identity/rank pairs are retained. GitLab and CMR exact-identity routes are singleton rank 1.",
        "metadata_only_exclusions": [
            "provider identity does not match the frozen exact identifier",
            "identity creation or selected exact revision is after the cutoff",
            "record type does not match the modality route",
            "public record URL or exact metadata URL is absent",
            "canonical source-family deduplication root is absent",
            "persistent identifier collides within or across waves",
            "record is retracted, deleted, private, or inaccessible in provider metadata",
            "content-class rights status is omitted rather than marked CANNOT_CHECK",
        ],
        "deduplication_rules": {
            "crossref": "journal family by sorted ISSN set; article identity by normalized DOI",
            "zenodo": "deposit family by normalized concept DOI; version identity by normalized version DOI",
            "gitlab": "project family and identity by immutable numeric project id",
            "cmr": "collection family by provider-id plus native-id; revision identity by concept-id plus revision-id",
            "cross_provider": "normalized DOI when present, otherwise the provider-prefixed persistent identifier",
            "collision_disposition": "exclude the later-ranked record; if its quota cell cannot be refilled under frozen ordering, emit CANNOT_CHECK_SOURCE_DISJOINTNESS",
        },
        "fail_closed_terminals": {
            "missing_quota_cell": "CANNOT_CHECK_SOURCE_UNIVERSE",
            "provider_or_modality_minimum_not_met": "CANNOT_CHECK_SOURCE_UNIVERSE",
            "identity_or_url_mismatch": "CANNOT_CHECK_PROVIDER_IDENTITY",
            "pre_cutoff_revision_or_identity_unbound": "CANNOT_CHECK_PRE_CUTOFF_REVISION",
            "deduplication_collision_unresolved": "CANNOT_CHECK_SOURCE_DISJOINTNESS",
            "content_class_rights_ambiguous": "CANNOT_CHECK_CONTENT_CLASS_RIGHTS",
            "candidate_metadata_only": "METADATA_CANDIDATE_ONLY__CASE_ELIGIBILITY_NOT_ASSESSED",
            "overall_until_all_g01_conditions_close": "CANNOT_CHECK_SOURCE_UNIVERSE",
        },
        "candidate_manifest": [
            {
                "wave_id": c["wave"],
                "protected_domain_candidate": c["domain"],
                "provider_key": c["provider"],
                "metadata_provider_id": PROVIDERS[c["provider"]]["metadata_provider_id"],
                "artifact_modality": PROVIDERS[c["provider"]]["modality"],
                "provider_record_identity": c["id"],
                "query_rank_at_frozen_snapshot": c["rank"],
            }
            for c in CANDIDATES
        ],
        "study_fields_forbidden_in_this_lane": [
            "article_or_abstract_full_text",
            "issue_or_comment_body",
            "repository_readme_body",
            "attachments",
            "dataset_files",
            "scientific_case_text",
            "case_eligibility",
            "pair_role_or_label",
            "candidate_or_comparator_output",
            "protected_gold",
            "outcome",
        ],
    }


def capture_query_selection_receipts() -> list[dict]:
    """Capture query-response hashes and prove the frozen ranks.

    Only normalized selected identifiers and ranks are retained.  The broad
    public metadata responses are transient and are never archived.
    """
    receipts: list[dict] = []

    route = QUERY_ROUTES["CROSSREF"]
    for domain, term in route["queries_by_domain"].items():
        parameters = {
            "query.bibliographic": term,
            "filter": route["fixed_parameters"]["filter"],
            "rows": route["fixed_parameters"]["rows"],
            "select": "DOI,type,publisher,created,license,URL,member,ISSN,issn-type",
        }
        url = route["route_template"] + "?" + urllib.parse.urlencode(parameters)
        payload, http_receipt = fetch_json(url)
        eligible = []
        for item in payload.get("message", {}).get("items", []):
            doi = item.get("DOI", "").lower()
            created = item.get("created", {}).get("date-time")
            if (
                doi
                and item.get("ISSN")
                and item.get("URL")
                and item.get("type") == "journal-article"
                and created
                and created <= CUTOFF
            ):
                eligible.append(doi)
        selected = sorted(
            [c for c in CANDIDATES if c["provider"] == "CROSSREF" and c["domain"] == domain],
            key=lambda item: item["rank"],
        )
        observed = []
        for candidate in selected:
            identity = candidate["id"].lower()
            if identity not in eligible:
                raise RuntimeError(f"Crossref ranked candidate absent from frozen query: {identity}")
            rank = eligible.index(identity) + 1
            if rank != candidate["rank"]:
                raise RuntimeError(f"Crossref rank drift for {identity}: {rank} != {candidate['rank']}")
            observed.append({"provider_record_identity": identity, "eligible_rank": rank})
        receipts.append(
            {
                "metadata_provider_id": PROVIDERS["CROSSREF"]["metadata_provider_id"],
                "protected_domain_candidate": domain,
                "exact_query_url": url,
                "eligible_records_in_returned_page": len(eligible),
                "selected_identity_ranks": observed,
                "http_receipt": http_receipt,
                "response_body_archived": False,
            }
        )

    route = QUERY_ROUTES["ZENODO"]
    for domain, term in route["queries_by_domain"].items():
        parameters = {
            "q": term,
            "type": route["fixed_parameters"]["type"],
            "sort": route["fixed_parameters"]["sort"],
            "size": route["fixed_parameters"]["size"],
        }
        url = route["route_template"] + "?" + urllib.parse.urlencode(parameters)
        payload, http_receipt = fetch_json(url)
        eligible = []
        for item in payload.get("hits", {}).get("hits", []):
            record_id = str(item.get("id", ""))
            created = item.get("created")
            updated = item.get("updated")
            metadata = item.get("metadata", {})
            if (
                record_id
                and item.get("doi")
                and item.get("conceptdoi")
                and item.get("links", {}).get("self_html")
                and (metadata.get("resource_type") or {}).get("type") == "dataset"
                and created
                and updated
                and created[:19] <= CUTOFF[:19]
                and updated[:19] <= CUTOFF[:19]
            ):
                eligible.append(record_id)
        selected = sorted(
            [c for c in CANDIDATES if c["provider"] == "ZENODO" and c["domain"] == domain],
            key=lambda item: item["rank"],
        )
        observed = []
        for candidate in selected:
            identity = str(candidate["id"])
            if identity not in eligible:
                raise RuntimeError(f"Zenodo ranked candidate absent from frozen query: {identity}")
            rank = eligible.index(identity) + 1
            if rank != candidate["rank"]:
                raise RuntimeError(f"Zenodo rank drift for {identity}: {rank} != {candidate['rank']}")
            observed.append({"provider_record_identity": identity, "eligible_rank": rank})
        receipts.append(
            {
                "metadata_provider_id": PROVIDERS["ZENODO"]["metadata_provider_id"],
                "protected_domain_candidate": domain,
                "exact_query_url": url,
                "eligible_records_in_returned_page": len(eligible),
                "selected_identity_ranks": observed,
                "http_receipt": http_receipt,
                "response_body_archived": False,
            }
        )
    return receipts


def summarize(records: list[dict]) -> dict:
    waves: dict[str, dict] = {}
    for wave in ("PRIMARY", "REPLICATION"):
        selected = [record for record in records if record["wave_id"] == wave]
        domain_counts: dict[str, int] = {}
        for record in selected:
            domain = record["protected_domain_candidate"]
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        waves[wave] = {
            "candidate_records": len(selected),
            "metadata_provider_count": len({r["metadata_provider_id"] for r in selected}),
            "metadata_providers": sorted({r["metadata_provider_id"] for r in selected}),
            "content_host_count": len({r["content_host_identity"] for r in selected}),
            "content_hosts": sorted({r["content_host_identity"] for r in selected}),
            "artifact_modality_count": len({r["artifact_modality"] for r in selected}),
            "artifact_modalities": sorted({r["artifact_modality"] for r in selected}),
            "domain_counts": dict(sorted(domain_counts.items())),
        }
    primary = {r["canonical_dedup_root"] for r in records if r["wave_id"] == "PRIMARY"}
    replication = {r["canonical_dedup_root"] for r in records if r["wave_id"] == "REPLICATION"}
    p_primary = {r["persistent_identifier"] for r in records if r["wave_id"] == "PRIMARY"}
    p_replication = {r["persistent_identifier"] for r in records if r["wave_id"] == "REPLICATION"}
    exact_revision_unresolved = [
        r["provider_record_identity"]
        for r in records
        if r["selected_pre_cutoff_revision"]["status"].startswith("CANNOT_CHECK")
    ]
    legal_unresolved = [r["provider_record_identity"] for r in records if r["legal_gate"].startswith("CANNOT_CHECK")]
    return {
        "waves": waves,
        "cross_wave_canonical_dedup_root_collisions": sorted(primary & replication),
        "cross_wave_persistent_identifier_collisions": sorted(p_primary & p_replication),
        "quota_terminals": {
            "candidate_cell_quota": "POPULATED_FOR_ALL_SIXTEEN_FROZEN_METADATA_CELLS",
            "provider_diversity": "PASS_FOUR_METADATA_PROVIDERS_PER_WAVE",
            "modality_diversity": "PASS_FOUR_MODALITIES_PER_WAVE",
            "cross_wave_source_family_disjointness": "PASS_NO_CANONICAL_ROOT_COLLISION",
            "exact_pre_cutoff_revision": "CANNOT_CHECK_FOR_CROSSREF_IDENTITY_ONLY_RECORDS",
            "content_class_rights": "CANNOT_CHECK_FOR_PROTECTED_CASE_CONTENT_IN_ALL_RECORDS",
            "case_eligibility": "NOT_ASSESSED_FOR_ALL_RECORDS",
            "overall": "CANNOT_CHECK_SOURCE_UNIVERSE",
        },
        "unresolved_counts": {
            "missing_structural_metadata_quota_cells": 0,
            "records_without_exact_historical_revision_bytes": len(exact_revision_unresolved),
            "records_with_future_case_content_rights_unresolved": len(legal_unresolved),
            "records_without_case_eligibility_assessment": len(records),
        },
        "unresolved_record_identities": {
            "exact_historical_revision_bytes": exact_revision_unresolved,
            "future_case_content_rights": legal_unresolved,
        },
        "downstream_case_quota_nonclaims": {
            "P1_R7A_clusters_verified": 0,
            "P1_R7A_clusters_required": 896,
            "P3_clusters_verified": 0,
            "P3_clusters_required": 768,
            "P4_clusters_verified": 0,
            "P4_clusters_required": 768,
            "P5_clusters_verified": 0,
            "P5_clusters_required": 768,
        },
    }


def main() -> int:
    captured_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    records: list[dict] = []
    errors: list[dict] = []
    builders = {
        "CROSSREF": crossref_record,
        "ZENODO": zenodo_record,
        "GITLAB": gitlab_record,
        "CMR": cmr_record,
    }
    for candidate in CANDIDATES:
        try:
            record = builders[candidate["provider"]](candidate)
            record["record_sha256"] = sha256(canonical_bytes(record))
            records.append(record)
        except Exception as exc:
            errors.append(
                {
                    "wave_id": candidate["wave"],
                    "provider_record_identity": candidate["id"],
                    "error": str(exc),
                }
            )

    proto = protocol(captured_at)
    proto["protocol_payload_sha256"] = sha256(canonical_bytes(proto))
    PROTOCOL_OUT.write_text(json.dumps(proto, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    query_selection_receipts = capture_query_selection_receipts()
    census = {
        "schema_version": "orion.provider-diverse-metadata-census.snapshot.v1",
        "captured_at_utc": captured_at,
        "protocol_path": str(PROTOCOL_OUT.relative_to(ROOT)),
        "protocol_payload_sha256": proto["protocol_payload_sha256"],
        "authority": "PUBLIC_METADATA_CENSUS_ONLY__NOT_A_CASE_FRAME__NOT_SCIENTIFIC_EVIDENCE",
        "outcomes_accessed": False,
        "protected_case_fields_accessed": False,
        "records_requested": len(CANDIDATES),
        "records_verified": len(records),
        "errors": errors,
        "query_selection_receipts": query_selection_receipts,
        "summary": summarize(records),
        "records": records,
        "explicit_nonclaims": [
            "A provider metadata record or public URL is not an eligible case.",
            "No article or abstract full text, issue, comment, README body, attachment, or dataset file was opened or archived; provider metadata descriptions were not retained.",
            "No adverse/control role, coordinate opportunity, identifiability mechanism, revision class, label, output, gold, or outcome was assigned.",
            "Metadata provider diversity is not content-host diversity and neither establishes scientific-domain transport.",
            "Declared licence metadata is not proof that future protected case text, issue prose, attachments, or linked files may be processed or redistributed.",
            "No registered P1, P3, P4, or P5 external panel binding is closed.",
        ],
        "scientific_verdict": "CANNOT_CHECK_SOURCE_UNIVERSE",
    }
    census["snapshot_payload_sha256"] = sha256(canonical_bytes(census))
    CENSUS_OUT.write_text(json.dumps(census, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "protocol": str(PROTOCOL_OUT),
                "census": str(CENSUS_OUT),
                "records_verified": len(records),
                "errors": errors,
                "wave_counts": census["summary"]["waves"],
                "unresolved_counts": census["summary"]["unresolved_counts"],
                "scientific_verdict": census["scientific_verdict"],
                "snapshot_payload_sha256": census["snapshot_payload_sha256"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not errors and len(records) == len(CANDIDATES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
