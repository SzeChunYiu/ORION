#!/usr/bin/env python3
"""Verify metadata identities, frozen quotas, and fail-closed terminals.

This verifier deliberately follows only exact provider metadata endpoints and
terms-page HEAD requests.  It does not follow DOI landing pages, download data
files, open article text, inspect issues, or retrieve repository prose.
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
PROTOCOL_PATH = ROOT / "CENSUS_PROTOCOL_V1.json"
CENSUS_PATH = ROOT / "SOURCE_CENSUS_V1.json"
RECEIPT_PATH = ROOT / "VERIFICATION_RECEIPT_V1.json"
USER_AGENT = "orion-outcome-blind-provider-metadata-verifier/1.0"


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def payload_hash(value: dict, field: str) -> str:
    copy = dict(value)
    copy.pop(field, None)
    return sha256(canonical_bytes(copy))


def fetch(url: str, *, headers: dict[str, str] | None = None, attempts: int = 5) -> tuple[bytes, dict]:
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        request_headers.update(headers)
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers=request_headers)
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read()
                return body, {
                    "request_url": url,
                    "final_url": response.geturl(),
                    "http_status": response.status,
                    "response_sha256": sha256(body),
                    "response_bytes": len(body),
                }
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == attempts - 1:
                body = exc.read()
                raise RuntimeError(f"HTTP {exc.code} for {url}: {body[:300]!r}") from exc
            retry_after = exc.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else 2 ** (attempt + 1))
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f"unreachable fetch failure: {url}")


def fetch_json(url: str, *, headers: dict[str, str] | None = None) -> tuple[dict | list, dict]:
    body, receipt = fetch(url, headers=headers)
    return json.loads(body), receipt


def head(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return {
                "request_url": url,
                "final_url": response.geturl(),
                "http_status": response.status,
                "content_type": response.headers.get("Content-Type"),
                "method": "HEAD",
            }
    except urllib.error.HTTPError as exc:
        return {
            "request_url": url,
            "final_url": exc.geturl(),
            "http_status": exc.code,
            "content_type": exc.headers.get("Content-Type"),
            "method": "HEAD",
            "status": "CANNOT_CHECK_LIVE_TERMS_URL",
        }


def add(checks: list[dict], check_id: str, passed: bool, evidence: object) -> None:
    checks.append(
        {
            "check_id": check_id,
            "status": "PASS" if passed else "FAIL",
            "evidence": evidence,
        }
    )


def verify_remote_record(record: dict) -> dict:
    provider = record["metadata_provider_id"]
    if provider == "CROSSREF_REST_API":
        payload, receipt = fetch_json(record["exact_metadata_url"])
        items = payload.get("message", {}).get("items", [])
        if len(items) != 1:
            raise RuntimeError("Crossref sparse identity query did not return exactly one record")
        observed = items[0].get("DOI", "").lower()
        expected = record["provider_record_identity"].lower()
        if observed != expected:
            raise RuntimeError(f"Crossref identity mismatch: {observed} != {expected}")
        return {
            "provider_identity_match": True,
            "observed_identity": observed,
            "historical_revision_terminal": "CANNOT_CHECK_HISTORICAL_METADATA_BYTES__IDENTITY_EXISTENCE_ONLY",
            "receipt": receipt,
        }

    if provider == "ZENODO_REST_API":
        payload, receipt = fetch_json(record["exact_metadata_url"])
        observed = str(payload.get("id"))
        expected = record["provider_record_identity"]
        if observed != expected or payload.get("doi", "").lower() != record["persistent_identifier"][4:]:
            raise RuntimeError(f"Zenodo identity mismatch for {expected}")
        return {
            "provider_identity_match": True,
            "observed_identity": observed,
            "observed_version_doi": payload.get("doi"),
            "receipt": receipt,
        }

    if provider == "GITLAB_COM_REST_API_V4":
        project, project_receipt = fetch_json(record["exact_metadata_url"])
        expected_path = record["provider_record_identity"]
        if project.get("path_with_namespace") != expected_path or project.get("id") != record["project_numeric_id"]:
            raise RuntimeError(f"GitLab identity mismatch for {expected_path}")
        revision = record["selected_pre_cutoff_revision"]["commit_sha"]
        licence_info = record["content_class_rights"]["repository_code"]
        licence_path = licence_info["licence_path"]
        file_url = (
            f"https://gitlab.com/api/v4/projects/{record['project_numeric_id']}/repository/files/"
            f"{urllib.parse.quote(licence_path, safe='')}?{urllib.parse.urlencode({'ref': revision})}"
        )
        licence, licence_receipt = fetch_json(file_url)
        licence_bytes = base64.b64decode(licence["content"], validate=False)
        observed_sha = sha256(licence_bytes)
        if observed_sha != licence_info["licence_content_sha256"]:
            raise RuntimeError(f"GitLab licence-byte mismatch for {expected_path}")
        return {
            "provider_identity_match": True,
            "observed_identity": expected_path,
            "commit_sha": revision,
            "licence_content_sha256": observed_sha,
            "project_receipt": project_receipt,
            "licence_receipt": licence_receipt,
        }

    if provider == "NASA_ESDIS_CMR_SEARCH_API":
        body, receipt = fetch(
            record["exact_metadata_url"],
            headers={"Accept": "application/vnd.nasa.cmr.umm+json; version=1.16"},
        )
        observed_sha = sha256(body)
        expected_sha = record["selected_pre_cutoff_revision"]["exact_revision_response_sha256"]
        if observed_sha != expected_sha:
            raise RuntimeError(f"CMR exact historical revision-byte mismatch for {record['provider_record_identity']}")
        umm = json.loads(body)
        if umm.get("ShortName") != record["short_name"]:
            raise RuntimeError(f"CMR short-name mismatch for {record['provider_record_identity']}")
        return {
            "provider_identity_match": True,
            "observed_identity": record["provider_record_identity"],
            "revision_id": record["selected_pre_cutoff_revision"]["revision_id"],
            "exact_revision_response_sha256": observed_sha,
            "receipt": receipt,
        }

    raise RuntimeError(f"unknown metadata provider: {provider}")


def main() -> int:
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    census = json.loads(CENSUS_PATH.read_text(encoding="utf-8"))
    checks: list[dict] = []

    add(
        checks,
        "PROTOCOL_PAYLOAD_HASH",
        payload_hash(protocol, "protocol_payload_sha256") == protocol["protocol_payload_sha256"],
        protocol["protocol_payload_sha256"],
    )
    add(
        checks,
        "CENSUS_PAYLOAD_HASH",
        payload_hash(census, "snapshot_payload_sha256") == census["snapshot_payload_sha256"],
        census["snapshot_payload_sha256"],
    )
    add(
        checks,
        "PROTOCOL_BINDING_HASH",
        census["protocol_payload_sha256"] == protocol["protocol_payload_sha256"],
        census["protocol_payload_sha256"],
    )

    records = census["records"]
    add(checks, "RECORD_COUNT", len(records) == 16 == census["records_verified"], len(records))
    record_hash_failures = []
    for record in records:
        observed = dict(record)
        expected = observed.pop("record_sha256")
        if sha256(canonical_bytes(observed)) != expected:
            record_hash_failures.append(record["provider_record_identity"])
    add(checks, "RECORD_PAYLOAD_HASHES", not record_hash_failures, record_hash_failures or "16/16")

    manifest = {
        (
            item["wave_id"],
            item["protected_domain_candidate"],
            item["metadata_provider_id"],
            item["artifact_modality"],
            item["provider_record_identity"],
        )
        for item in protocol["candidate_manifest"]
    }
    observed_manifest = {
        (
            item["wave_id"],
            item["protected_domain_candidate"],
            item["metadata_provider_id"],
            item["artifact_modality"],
            item["provider_record_identity"],
        )
        for item in records
    }
    add(checks, "EXACT_CANDIDATE_MANIFEST", observed_manifest == manifest, {"expected": len(manifest), "observed": len(observed_manifest)})

    rank_receipts = census.get("query_selection_receipts", [])
    ranked_pairs = {
        (
            receipt["metadata_provider_id"],
            receipt["protected_domain_candidate"],
            selected["provider_record_identity"].lower(),
            selected["eligible_rank"],
        )
        for receipt in rank_receipts
        for selected in receipt["selected_identity_ranks"]
    }
    expected_ranked_pairs = {
        (
            item["metadata_provider_id"],
            item["protected_domain_candidate"],
            item["provider_record_identity"].lower(),
            item["query_rank_at_frozen_snapshot"],
        )
        for item in protocol["candidate_manifest"]
        if item["metadata_provider_id"] in {"CROSSREF_REST_API", "ZENODO_REST_API"}
    }
    rank_pass = (
        len(rank_receipts) == 6
        and ranked_pairs == expected_ranked_pairs
        and all(receipt["response_body_archived"] is False for receipt in rank_receipts)
        and all(receipt["http_receipt"]["http_status"] == 200 for receipt in rank_receipts)
    )
    add(
        checks,
        "FROZEN_QUERY_SELECTION_RANK_RECEIPTS",
        rank_pass,
        {
            "query_receipts": len(rank_receipts),
            "selected_rank_pairs": len(ranked_pairs),
            "broad_response_bodies_archived": False,
        },
    )

    required_matrix = protocol["quota_contract"]["required_domain_modality_matrix_per_wave"]
    quota_evidence = {}
    quota_pass = True
    for wave in protocol["waves"]:
        selected = [record for record in records if record["wave_id"] == wave]
        providers = {record["metadata_provider_id"] for record in selected}
        modalities = {record["artifact_modality"] for record in selected}
        hosts = {record["content_host_identity"] for record in selected}
        domain_counts = {
            domain: sum(record["protected_domain_candidate"] == domain for record in selected)
            for domain in required_matrix
        }
        matrix_missing = []
        for domain, required_modalities in required_matrix.items():
            observed_modalities = {
                record["artifact_modality"]
                for record in selected
                if record["protected_domain_candidate"] == domain
            }
            matrix_missing.extend(
                f"{domain}:{modality}" for modality in required_modalities if modality not in observed_modalities
            )
        wave_pass = (
            len(selected) == protocol["quota_contract"]["candidate_records_per_wave_exact"]
            and len(providers) >= protocol["quota_contract"]["metadata_providers_per_wave_minimum"]
            and len(modalities) >= protocol["quota_contract"]["artifact_modalities_per_wave_minimum"]
            and all(value == 2 for value in domain_counts.values())
            and not matrix_missing
        )
        quota_pass = quota_pass and wave_pass
        quota_evidence[wave] = {
            "candidate_records": len(selected),
            "metadata_provider_count": len(providers),
            "metadata_providers": sorted(providers),
            "content_host_count_reported_separately": len(hosts),
            "content_hosts": sorted(hosts),
            "artifact_modality_count": len(modalities),
            "artifact_modalities": sorted(modalities),
            "domain_counts": domain_counts,
            "missing_matrix_cells": matrix_missing,
        }
    add(checks, "WAVE_PROVIDER_MODALITY_DOMAIN_QUOTAS", quota_pass, quota_evidence)

    primary = {record["canonical_dedup_root"] for record in records if record["wave_id"] == "PRIMARY"}
    replication = {record["canonical_dedup_root"] for record in records if record["wave_id"] == "REPLICATION"}
    cross_wave_collisions = sorted(primary & replication)
    persistent_ids = [record["persistent_identifier"] for record in records]
    persistent_collisions = sorted({value for value in persistent_ids if persistent_ids.count(value) > 1})
    add(
        checks,
        "DEDUPLICATION_AND_CROSS_WAVE_DISJOINTNESS",
        not cross_wave_collisions and not persistent_collisions,
        {"cross_wave_family_collisions": cross_wave_collisions, "persistent_identifier_collisions": persistent_collisions},
    )

    protected_flags_pass = (
        census["outcomes_accessed"] is False
        and census["protected_case_fields_accessed"] is False
        and all(record["protected_fields_accessed"] is False for record in records)
        and all(record["candidate_or_comparator_outputs_accessed"] is False for record in records)
        and all(record["outcomes_accessed"] is False for record in records)
    )
    add(checks, "OUTCOME_AND_PROTECTED_FIELD_BOUNDARY", protected_flags_pass, "16/16 metadata-only flags false")

    revision_unknown = [
        record["provider_record_identity"]
        for record in records
        if record["selected_pre_cutoff_revision"]["status"].startswith("CANNOT_CHECK")
    ]
    legal_unknown = [record["provider_record_identity"] for record in records if record["legal_gate"].startswith("CANNOT_CHECK")]
    case_unknown = [record["provider_record_identity"] for record in records if record["case_eligibility_status"].startswith("NOT_ASSESSED")]
    fail_closed_pass = (
        len(revision_unknown) == 8
        and len(legal_unknown) == 16
        and len(case_unknown) == 16
        and census["scientific_verdict"] == "CANNOT_CHECK_SOURCE_UNIVERSE"
    )
    add(
        checks,
        "FAIL_CLOSED_TERMINALS_PRESERVED",
        fail_closed_pass,
        {
            "exact_historical_revision_cannot_check": len(revision_unknown),
            "future_case_content_rights_cannot_check": len(legal_unknown),
            "case_eligibility_not_assessed": len(case_unknown),
            "scientific_verdict": census["scientific_verdict"],
        },
    )

    remote_results = []
    remote_errors = []
    for record in records:
        try:
            result = verify_remote_record(record)
            result["metadata_provider_id"] = record["metadata_provider_id"]
            result["provider_record_identity"] = record["provider_record_identity"]
            remote_results.append(result)
        except Exception as exc:
            remote_errors.append(
                {
                    "metadata_provider_id": record["metadata_provider_id"],
                    "provider_record_identity": record["provider_record_identity"],
                    "error": str(exc),
                }
            )
    add(checks, "LIVE_EXACT_PROVIDER_IDENTITY", not remote_errors and len(remote_results) == 16, remote_errors or "16/16")

    terms_urls = sorted(
        {
            status["terms_url"]
            for record in records
            for status in record["content_class_rights"].values()
            if isinstance(status, dict) and status.get("terms_url")
        }
    )
    terms_receipts = [head(url) for url in terms_urls]
    # Terms liveness is informational.  A 200 response does not settle content
    # class rights, and a provider rejecting HEAD remains CANNOT_CHECK.
    terms_live = sum(200 <= receipt["http_status"] < 400 for receipt in terms_receipts)
    add(checks, "TERMS_URL_HEAD_RECEIPTS", True, {"live_2xx_3xx": terms_live, "total": len(terms_receipts)})

    passed = sum(check["status"] == "PASS" for check in checks)
    failed = [check["check_id"] for check in checks if check["status"] != "PASS"]
    receipt = {
        "schema_version": "orion.provider-diverse-metadata-census.verification-receipt.v1",
        "verified_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "authority": "METADATA_CENSUS_CONFORMANCE_ONLY__NOT_CASE_OR_OUTCOME_AUTHORITY",
        "outcomes_accessed": False,
        "protected_case_fields_accessed": False,
        "article_or_issue_or_dataset_body_accessed": False,
        "checks_passed": passed,
        "checks_total": len(checks),
        "failed_checks": failed,
        "checks": checks,
        "remote_identity_receipts": remote_results,
        "remote_identity_errors": remote_errors,
        "terms_url_head_receipts": terms_receipts,
        "conformance_terminal": "METADATA_CENSUS_CONFORMANCE_PASS" if not failed else "METADATA_CENSUS_CONFORMANCE_FAIL",
        "scientific_terminal_unchanged": "CANNOT_CHECK_SOURCE_UNIVERSE",
        "explicit_nonclaim": "Passing this verifier does not create an eligible case, settle rights, establish provider transport, or authorize a P1/P3/P4/P5 result.",
    }
    receipt["receipt_payload_sha256"] = sha256(canonical_bytes(receipt))
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "receipt": str(RECEIPT_PATH),
                "checks_passed": passed,
                "checks_total": len(checks),
                "failed_checks": failed,
                "remote_identities_verified": len(remote_results),
                "terms_urls_head_checked": len(terms_receipts),
                "conformance_terminal": receipt["conformance_terminal"],
                "scientific_terminal_unchanged": receipt["scientific_terminal_unchanged"],
                "receipt_payload_sha256": receipt["receipt_payload_sha256"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
