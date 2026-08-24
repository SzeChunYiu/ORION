#!/usr/bin/env python3
"""Execute the frozen outcome-blind P4 DataCite M5 V2 metadata census."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


USER_AGENT = "ORION-P4-DataCite-M5-metadata-census/1.0 (public metadata only; no files)"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def request_bytes(url: str, *, attempts: int = 4, timeout: int = 120) -> tuple[bytes, dict[str, Any]]:
    last_error: Exception | None = None
    for attempt in range(attempts):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json,text/markdown,text/html;q=0.8,*/*;q=0.5"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read()
                return body, {
                    "request_url": url,
                    "final_url": response.geturl(),
                    "http_status": response.status,
                    "content_type": response.headers.get("Content-Type"),
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "response_bytes": len(body),
                    "response_sha256": sha256_bytes(body),
                    "attempt": attempt + 1,
                }
        except Exception as exc:  # bounded transport retry; protocol and query stay unchanged
            last_error = exc
            if attempt < attempts - 1:
                time.sleep(2**attempt)
    return b"", {
        "request_url": url,
        "final_url": None,
        "http_status": None,
        "response_bytes": 0,
        "response_sha256": None,
        "attempt": attempts,
        "error": str(last_error),
    }


def normalized_text(payload: bytes) -> str:
    text = payload.decode("utf-8", "replace")
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def normalize_doi(value: Any) -> str:
    doi = str(value or "").strip().casefold()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.startswith(prefix):
            doi = doi[len(prefix) :]
    return doi


def extract_relationship_id(item: dict[str, Any], name: str) -> str:
    data = ((item.get("relationships") or {}).get(name) or {}).get("data") or {}
    return str(data.get("id") or "").casefold()


def content_urls(value: Any) -> list[str]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        values = []
    return sorted({str(item) for item in values if str(item).startswith("https://")})


def normalized_rights_uri(value: Any) -> str:
    uri = str(value or "").strip().casefold().rstrip("/")
    if uri.endswith("/legalcode"):
        uri = uri[: -len("/legalcode")]
    return uri


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--disclosure", type=Path, required=True)
    parser.add_argument("--zenodo-candidates", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    existing = [path for path in (args.candidates, args.receipt) if path.exists()]
    if existing:
        raise RuntimeError("refusing to overwrite frozen outputs; use a successor identity: " + ", ".join(map(str, existing)))

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    protocol_copy = dict(protocol)
    observed_protocol_payload_hash = protocol_copy.pop("protocol_payload_sha256")
    if canonical_sha256(protocol_copy) != observed_protocol_payload_hash:
        raise RuntimeError("protocol payload hash mismatch")
    if sha256_file(args.zenodo_candidates) != protocol["lineage"]["zenodo_v2_candidates_sha256"]:
        raise RuntimeError("bound Zenodo V2 candidate file hash mismatch")
    if sha256_file(args.disclosure) != protocol["prefreeze_disclosure"]["file_sha256"]:
        raise RuntimeError("V2 prefreeze disclosure file hash mismatch")
    disclosure = json.loads(args.disclosure.read_text(encoding="utf-8"))
    disclosure_copy = dict(disclosure)
    observed_disclosure_payload_hash = disclosure_copy.pop("disclosure_payload_sha256")
    if canonical_sha256(disclosure_copy) != observed_disclosure_payload_hash:
        raise RuntimeError("V2 prefreeze disclosure payload hash mismatch")
    if observed_disclosure_payload_hash != protocol["prefreeze_disclosure"]["payload_sha256"]:
        raise RuntimeError("protocol does not bind the V2 prefreeze disclosure payload")
    v1_disclosed_dois = {normalize_doi(value) for value in disclosure["all_disclosed_dois"]}
    if len(v1_disclosed_dois) != protocol["prefreeze_disclosure"]["unique_disclosed_dois"]:
        raise RuntimeError("V1 disclosed DOI count mismatch")

    prior_zenodo_dois: set[str] = set()
    with args.zenodo_candidates.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                doi = normalize_doi(row.get("doi"))
                if doi:
                    prior_zenodo_dois.add(doi)

    evidence_records: list[dict[str, Any]] = []
    evidence_ok = True
    for spec in protocol["authoritative_evidence"]:
        body, receipt = request_bytes(spec["url"], timeout=60)
        text = normalized_text(body).casefold()
        assertion_checks = [
            {
                "assertion": assertion,
                "assertion_sha256": sha256_bytes(assertion.encode("utf-8")),
                "present": assertion.casefold() in text,
            }
            for assertion in spec["assertions"]
        ]
        record = {
            **spec,
            "captured_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
            "receipt": receipt,
            "assertion_checks": assertion_checks,
            "all_assertions_present": receipt.get("http_status") == 200 and all(item["present"] for item in assertion_checks),
            "body_archived": False,
        }
        evidence_records.append(record)
        evidence_ok &= record["all_assertions_present"]

    args.cache.mkdir(parents=True, exist_ok=True)
    accepted_rights_ids = {value.casefold() for value in protocol["candidate_filter"]["accepted_exact_record_rights_identifiers"]}
    accepted_rights_uris = {normalized_rights_uri(value) for value in protocol["candidate_filter"]["accepted_exact_record_rights_uris"]}
    accepted_identifier_types = set(protocol["candidate_filter"]["accepted_relation_identifier_types"])
    accepted_relations = set(protocol["candidate_filter"]["accepted_relations"])
    accepted_publication_types = set(protocol["candidate_filter"]["accepted_publication_target_resource_types"])
    excluded_clients = {value.casefold() for value in protocol["provider_disjointness"]["exclude_datacite_client_ids"]}
    excluded_publishers = {value.casefold() for value in protocol["provider_disjointness"]["exclude_publishers_casefold"]}
    excluded_prefixes = tuple(value.casefold() for value in protocol["provider_disjointness"]["exclude_doi_prefixes_casefold"])

    query_receipts: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    record_domains: collections.defaultdict[str, set[str]] = collections.defaultdict(set)
    transport_schema_ok = evidence_ok
    pagination_ok = True

    for query_number, query in enumerate(protocol["queries"], start=1):
        params = {
            "resource-type-id": protocol["provider"]["resource_type_id"],
            "query": query["query"],
            "page[size]": protocol["provider"]["page_size"],
            "page[number]": 1,
            "sort": protocol["provider"]["sort"],
            "disable-facets": "true",
            "fields[dois]": ",".join(protocol["provider"]["fields_dois"]),
        }
        url = protocol["provider"]["endpoint"] + "?" + urllib.parse.urlencode(params)
        raw, receipt = request_bytes(url)
        raw_path = args.cache / f"{query_number:02d}_{query['query_id']}_page_01.json"
        raw_path.write_bytes(raw)
        counts: collections.Counter[str] = collections.Counter()
        seen: set[str] = set()
        page_schema_ok = False
        total = None
        data: list[Any] = []
        parse_error = None
        if receipt.get("http_status") == 200:
            try:
                payload = json.loads(raw)
                data = payload.get("data") or []
                meta = payload.get("meta") or {}
                total = meta.get("total")
                page_schema_ok = isinstance(data, list) and isinstance(total, int)
            except Exception as exc:
                parse_error = str(exc)
        if not page_schema_ok:
            transport_schema_ok = False
            data = []
        expected_returned = min(int(protocol["provider"]["page_size"]), total or 0)
        if page_schema_ok and len(data) != expected_returned:
            pagination_ok = False

        for item in data:
            counts["raw_hits"] += 1
            attributes = item.get("attributes") or {}
            doi = normalize_doi(attributes.get("doi") or item.get("id"))
            if not doi:
                counts["missing_doi"] += 1
                transport_schema_ok = False
                continue
            if doi in seen:
                counts["duplicate_within_query"] += 1
                pagination_ok = False
                continue
            seen.add(doi)

            client_id = extract_relationship_id(item, "client")
            provider_id = extract_relationship_id(item, "provider")
            publisher = str(attributes.get("publisher") or "")
            if doi in v1_disclosed_dois:
                counts["v1_prefreeze_exclusions"] += 1
                continue
            if not client_id:
                counts["missing_client_exclusions"] += 1
                continue
            if client_id in excluded_clients:
                counts["zenodo_client_exclusions"] += 1
                continue
            if publisher.casefold() in excluded_publishers or doi.startswith(excluded_prefixes):
                counts["zenodo_publisher_or_prefix_exclusions"] += 1
                continue
            if doi in prior_zenodo_dois:
                counts["bound_zenodo_v2_root_exclusions"] += 1
                continue
            counts["provider_disjoint_eligible"] += 1

            resource_type = str((attributes.get("types") or {}).get("resourceTypeGeneral") or "")
            if attributes.get("state") != "findable" or attributes.get("isActive") is not True or resource_type != "Dataset":
                counts["state_or_type_exclusions"] += 1
                continue
            counts["findable_active_dataset_eligible"] += 1

            rights_matches = []
            for rights in attributes.get("rightsList") or []:
                if not isinstance(rights, dict):
                    continue
                rights_id = str(rights.get("rightsIdentifier") or "").casefold()
                rights_uri = normalized_rights_uri(rights.get("rightsUri"))
                if rights_id in accepted_rights_ids or rights_uri in accepted_rights_uris:
                    rights_matches.append(
                        {
                            "rights": str(rights.get("rights") or ""),
                            "rightsIdentifier": str(rights.get("rightsIdentifier") or ""),
                            "rightsUri": str(rights.get("rightsUri") or ""),
                        }
                    )
            if not rights_matches:
                continue
            counts["exact_rights_declaration_eligible"] += 1

            public_urls = content_urls(attributes.get("contentUrl"))
            if not public_urls:
                continue
            counts["public_content_url_eligible"] += 1

            accepted_typed = []
            for relation in attributes.get("relatedIdentifiers") or []:
                if not isinstance(relation, dict):
                    continue
                if (
                    relation.get("relatedIdentifierType") in accepted_identifier_types
                    and relation.get("relationType") in accepted_relations
                    and relation.get("relatedIdentifier")
                ):
                    accepted_typed.append(relation)
            if not accepted_typed:
                continue
            counts["accepted_typed_relation_eligible"] += 1

            publication_relations = [
                {
                    "identifier": str(relation.get("relatedIdentifier") or ""),
                    "identifier_type": str(relation.get("relatedIdentifierType") or ""),
                    "relation": str(relation.get("relationType") or ""),
                    "resource_type": str(relation.get("resourceTypeGeneral") or ""),
                }
                for relation in accepted_typed
                if relation.get("resourceTypeGeneral") in accepted_publication_types
            ]
            if not publication_relations:
                continue
            counts["publication_typed_relation_eligible"] += 1
            record_domains[doi].add(query["domain_id"])

            titles = attributes.get("titles") or []
            creators = attributes.get("creators") or []
            record_subset = {
                "doi": doi,
                "client_id": client_id,
                "provider_id": provider_id,
                "publisher": publisher,
                "types": attributes.get("types"),
                "rightsList": attributes.get("rightsList"),
                "contentUrl": attributes.get("contentUrl"),
                "relatedIdentifiers": attributes.get("relatedIdentifiers"),
                "created": attributes.get("created"),
                "updated": attributes.get("updated"),
                "url": attributes.get("url"),
            }
            candidates.append(
                {
                    "schema_version": "orion.p4.datacite-m5-candidate.v2",
                    "query_id": query["query_id"],
                    "domain_id": query["domain_id"],
                    "mechanism_id": protocol["mechanism_id"],
                    "doi": doi,
                    "client_id": client_id,
                    "provider_id": provider_id,
                    "publisher": publisher,
                    "title": str(titles[0].get("title") if titles and isinstance(titles[0], dict) else ""),
                    "creators": [str(value.get("name") or "") for value in creators if isinstance(value, dict)],
                    "publication_year": attributes.get("publicationYear"),
                    "resource_type_general": resource_type,
                    "rights_declarations": rights_matches,
                    "public_content_urls": public_urls,
                    "publication_related_identifiers": publication_relations,
                    "record_api_url": f"https://api.datacite.org/dois/{urllib.parse.quote(doi, safe='')}",
                    "record_subset_canonical_sha256": canonical_sha256(record_subset),
                    "candidate_boundary": protocol["candidate_filter"]["candidate_boundary"],
                }
            )

        query_receipts.append(
            {
                "query_id": query["query_id"],
                "domain_id": query["domain_id"],
                "mechanism_id": protocol["mechanism_id"],
                "request_url_sha256": sha256_bytes(url.encode("utf-8")),
                "raw_response_file": raw_path.name,
                "raw_response_bytes": len(raw),
                "raw_response_sha256": sha256_bytes(raw) if raw else None,
                "reported_total_hits": total,
                "returned_hits": len(data),
                "unique_raw_dois": len(seen),
                "http_receipt": receipt,
                "schema_passed": page_schema_ok,
                "pagination_passed": page_schema_ok and len(data) == expected_returned,
                "parse_error": parse_error,
                **dict(counts),
            }
        )
        time.sleep(float(protocol["provider"]["inter_request_seconds"]))

    candidates.sort(key=lambda row: (row["query_id"], row["doi"]))
    args.candidates.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in candidates), encoding="utf-8")

    gate = int(protocol["frozen_gate"]["minimum_unique_signal_records_per_domain_mechanism_cell"])
    base_counts = protocol["frozen_gate"]["existing_zenodo_m5_signal_counts"]
    by_domain = {receipt["domain_id"]: receipt for receipt in query_receipts}
    per_cell = {}
    for domain in protocol["frozen_gate"]["domains"]:
        new_count = int(by_domain[domain].get("publication_typed_relation_eligible", 0))
        combined = int(base_counts[domain]) + new_count
        per_cell[domain] = {
            "mechanism_id": protocol["mechanism_id"],
            "zenodo_v2_signal_count": int(base_counts[domain]),
            "datacite_disjoint_signal_count": new_count,
            "overlap_with_zenodo_v2": 0,
            "combined_unique_signal_count": combined,
            "frozen_gate": gate,
            "deficit_or_surplus_to_48": combined - gate,
            "passes_combined_frozen_signal_gate": combined >= gate,
            "content_rights_terminal": "DECLARED_PERMISSION_AUTHORITY_UNVERIFIED",
            "natural_pair_eligibility": "NOT_ADJUDICATED",
        }

    all_combined_pass = transport_schema_ok and pagination_ok and all(cell["passes_combined_frozen_signal_gate"] for cell in per_cell.values())
    if not transport_schema_ok or not pagination_ok:
        terminal = protocol["terminals"]["transport_or_schema"]
        source_signal_terminal = terminal
    elif not all_combined_pass:
        terminal = protocol["terminals"]["source_shortfall"]
        source_signal_terminal = terminal
    else:
        terminal = protocol["terminals"]["combined_signal_gate_passed_rights_unbound"]
        source_signal_terminal = "P4_DATACITE_M5_DISJOINT_PROVIDER_V2_COMBINED_48_SIGNAL_GATE_PASSED__NO_CASES_ADJUDICATED"

    result: dict[str, Any] = {
        "schema_version": "orion.p4.datacite-m5-disjoint-provider-census-result.v2",
        "date": "2026-08-23",
        "captured_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "identity": protocol["identity"],
        "authority": protocol["authority"],
        "protocol_file_sha256": sha256_file(args.protocol),
        "protocol_payload_sha256": protocol["protocol_payload_sha256"],
        "lineage": protocol["lineage"],
        "v1_retained_terminal": protocol["lineage"]["v1_retained_terminal"],
        "prefreeze_disclosure_file_sha256": sha256_file(args.disclosure),
        "prefreeze_disclosure_payload_sha256": observed_disclosure_payload_hash,
        "prefreeze_unique_disclosed_dois": len(v1_disclosed_dois),
        "evidence_records": evidence_records,
        "evidence_assertions_passed": evidence_ok,
        "provider_schema_passed": transport_schema_ok,
        "pagination_integrity_passed": pagination_ok,
        "query_count": len(query_receipts),
        "raw_response_count": len(query_receipts),
        "query_receipts": query_receipts,
        "candidate_rows": len(candidates),
        "unique_candidate_dois": len(record_domains),
        "cross_domain_candidate_dois": sum(len(domains) > 1 for domains in record_domains.values()),
        "candidate_jsonl_sha256": sha256_file(args.candidates),
        "per_cell": per_cell,
        "all_four_m5_cells_pass_combined_frozen_signal_gate": all_combined_pass,
        "source_signal_terminal": source_signal_terminal,
        "scientific_terminal": terminal,
        "metadata_permission": "DATACITE_METADATA_CC0_ROOT_BOUND",
        "dataset_content_permission": "DECLARED_PERMISSION_AUTHORITY_UNVERIFIED",
        "linked_publication_rights": "CANNOT_CHECK",
        "natural_pair_eligibility": "NOT_ADJUDICATED",
        "metadata_descriptions_requested_or_accessed": False,
        "candidate_content_bytes_requested_or_accessed": False,
        "files_downloaded": False,
        "case_outcomes_accessed": False,
        "model_outcomes_executed": False,
        "forbidden_claims": protocol["forbidden_claims"],
        "explicit_nonclaim": "A DataCite metadata signal and deposited rights declaration do not establish repository content permission, linked-publication rights, natural-pair identity, case eligibility, scientific performance, confirmation, provider generality, or ORION superiority.",
    }
    result["result_payload_sha256"] = canonical_sha256(result)
    args.receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("candidate_rows", "unique_candidate_dois", "per_cell", "source_signal_terminal", "scientific_terminal", "result_payload_sha256")}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
