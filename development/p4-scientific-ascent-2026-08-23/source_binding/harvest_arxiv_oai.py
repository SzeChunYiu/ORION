#!/usr/bin/env python3
"""Outcome-blind arXiv CC BY candidate-frame harvest for P4 naturalistic V1.

This script harvests author-written scientific records from arXiv's official
OAI-PMH endpoint.  It binds only the latest version recorded in each harvested
metadata record and accepts article content only when that record explicitly
declares CC BY 4.0.  It does not adjudicate scientific-case eligibility and it
does not create P4 outcomes.
"""

from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


BASE = "https://export.arxiv.org/oai2"
USER_AGENT = "ORION-P4-public-source-audit/1.0 (research metadata harvest)"
LICENSE = "http://creativecommons.org/licenses/by/4.0/"
FROM_DATE = "2018-01-01"
UNTIL_DATE = "2026-08-20"
PLANNED_CASES_PER_DOMAIN = 192
CANDIDATES_PER_DOMAIN = 384
REQUEST_INTERVAL_SECONDS = 3.1

DOMAINS = [
    {
        "domain_id": "EARTH_ENVIRONMENT",
        "sets": [
            "physics:physics:ao-ph",
            "physics:physics:geo-ph",
            "physics:astro-ph:EP",
        ],
        "per_set_quota": {
            "physics:physics:ao-ph": 128,
            "physics:physics:geo-ph": 128,
            "physics:astro-ph:EP": 128,
        },
        "scope": "atmospheric/oceanic physics, geophysics, earth/planetary astrophysics",
    },
    {
        "domain_id": "LIFE_BIOMEDICAL",
        "sets": ["q-bio"],
        "scope": "quantitative biology, including computational biomedical work",
    },
    {
        "domain_id": "SCIENTIFIC_SOFTWARE",
        "sets": ["cs:cs:SE"],
        "scope": "software engineering research",
    },
    {
        "domain_id": "PHYSICAL_ENGINEERING",
        "sets": ["eess"],
        "scope": "electrical engineering and systems science",
    },
]

NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "raw": "http://arxiv.org/OAI/arXivRaw/",
}


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as response:
        return response.read()


def initial_url(set_spec: str) -> str:
    params = {
        "verb": "ListRecords",
        "metadataPrefix": "arXivRaw",
        "set": set_spec,
        "from": FROM_DATE,
        "until": UNTIL_DATE,
    }
    return BASE + "?" + urllib.parse.urlencode(params)


def continuation_url(token: str) -> str:
    return BASE + "?" + urllib.parse.urlencode(
        {"verb": "ListRecords", "resumptionToken": token}
    )


def parse_record(record: ET.Element, domain: dict, set_spec: str) -> tuple[dict | None, str]:
    header = record.find("oai:header", NS)
    if header is None or header.get("status") == "deleted":
        return None, "deleted"
    raw = record.find("oai:metadata/raw:arXivRaw", NS)
    if raw is None:
        return None, "missing_metadata"

    def value(name: str) -> str:
        node = raw.find(f"raw:{name}", NS)
        return clean(node.text if node is not None else "")

    license_url = value("license")
    if license_url.replace("https://", "http://") != LICENSE:
        return None, "content_license_not_cc_by_4"

    arxiv_id = value("id")
    title = value("title")
    authors = value("authors")
    abstract = value("abstract")
    categories = value("categories").split()
    comments = value("comments")
    versions = []
    for node in raw.findall("raw:version", NS):
        label = node.get("version", "")
        date_node = node.find("raw:date", NS)
        source_node = node.find("raw:source_type", NS)
        size_node = node.find("raw:size", NS)
        versions.append(
            {
                "version": label,
                "date": clean(date_node.text if date_node is not None else ""),
                "source_type": clean(source_node.text if source_node is not None else ""),
                "size": clean(size_node.text if size_node is not None else ""),
            }
        )
    if not arxiv_id or not title or not authors or len(abstract) < 200 or not versions:
        return None, "incomplete_record"
    if "withdrawn" in (comments + " " + abstract).lower():
        return None, "withdrawal_marker"

    def version_number(item: dict) -> int:
        match = re.fullmatch(r"v(\d+)", item["version"])
        return int(match.group(1)) if match else -1

    latest = max(versions, key=version_number)
    exact_id = arxiv_id + latest["version"]
    header_datestamp_node = header.find("oai:datestamp", NS)
    set_nodes = header.findall("oai:setSpec", NS)
    doi = value("doi")
    journal_ref = value("journal-ref")

    row = {
        "schema_version": "orion.p4.arxiv-ccby-source-frame.v1",
        "domain_id": domain["domain_id"],
        "domain_scope": domain["scope"],
        "acquisition_set": set_spec,
        "arxiv_id": arxiv_id,
        "exact_version": latest["version"],
        "exact_arxiv_id": exact_id,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "abstract_sha256": hashlib.sha256(abstract.encode("utf-8")).hexdigest(),
        "categories": categories,
        "comments": comments,
        "doi": doi or None,
        "journal_ref": journal_ref or None,
        "version_history": versions,
        "oai_identifier": clean(
            (header.find("oai:identifier", NS).text if header.find("oai:identifier", NS) is not None else "")
        ),
        "oai_datestamp": clean(header_datestamp_node.text if header_datestamp_node is not None else ""),
        "oai_sets": [clean(node.text) for node in set_nodes],
        "content_license": "CC BY 4.0",
        "content_license_url": "https://creativecommons.org/licenses/by/4.0/",
        "metadata_license": "CC0 1.0 (arXiv metadata policy)",
        "immutable_abs_url": f"https://arxiv.org/abs/{exact_id}",
        "immutable_pdf_url": f"https://arxiv.org/pdf/{exact_id}",
        "immutable_source_url": f"https://export.arxiv.org/e-print/{exact_id}",
        "attribution": f"{authors}, {title}, arXiv:{exact_id}, CC BY 4.0",
        "binding_state": "CONTENT_LICENSE_CONFIRMED__CASE_ELIGIBILITY_UNADJUDICATED",
    }
    return row, "accepted"


def main() -> int:
    out_dir = Path(__file__).resolve().parent
    frame_path = out_dir / "ARXIV_CC_BY_SOURCE_POOL_V1.jsonl"
    log_path = out_dir / "ARXIV_CC_BY_POOL_HARVEST_LOG_V1.json"
    binding_path = out_dir / "ARXIV_CC_BY_SOURCE_POOL_BINDING_V1.json"
    raw_dir = out_dir / "raw_oai_pages"
    raw_dir.mkdir(exist_ok=True)
    for stale in raw_dir.glob("*.xml.gz"):
        stale.unlink()

    selected: list[dict] = []
    global_ids: set[str] = set()
    request_log: list[dict] = []
    exclusion_counts: dict[str, int] = {}
    per_domain: dict[str, int] = {}
    last_request_at = 0.0

    for domain in DOMAINS:
        domain_rows: list[dict] = []
        for set_spec in domain["sets"]:
            set_quota = domain.get("per_set_quota", {}).get(set_spec, CANDIDATES_PER_DOMAIN)
            accepted_for_set = 0
            url: str | None = initial_url(set_spec)
            while url and accepted_for_set < set_quota and len(domain_rows) < CANDIDATES_PER_DOMAIN:
                delay = REQUEST_INTERVAL_SECONDS - (time.monotonic() - last_request_at)
                if delay > 0:
                    time.sleep(delay)
                payload = fetch(url)
                last_request_at = time.monotonic()
                payload_sha = hashlib.sha256(payload).hexdigest()
                request_number = len(request_log) + 1
                safe_set = re.sub(r"[^A-Za-z0-9_.-]+", "_", set_spec)
                raw_name = f"{request_number:03d}_{domain['domain_id']}_{safe_set}.xml.gz"
                raw_path = raw_dir / raw_name
                raw_path.write_bytes(gzip.compress(payload, compresslevel=9, mtime=0))
                raw_gzip_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()
                root = ET.fromstring(payload)
                error = root.find("oai:error", NS)
                if error is not None:
                    raise RuntimeError(f"OAI error for {set_spec}: {error.get('code')} {clean(error.text)}")
                records = root.findall(".//oai:record", NS)
                accepted_here = 0
                for record in records:
                    row, reason = parse_record(record, domain, set_spec)
                    if row is None:
                        exclusion_counts[reason] = exclusion_counts.get(reason, 0) + 1
                        continue
                    if row["arxiv_id"] in global_ids:
                        exclusion_counts["duplicate_across_sets_or_domains"] = (
                            exclusion_counts.get("duplicate_across_sets_or_domains", 0) + 1
                        )
                        continue
                    global_ids.add(row["arxiv_id"])
                    domain_rows.append(row)
                    accepted_for_set += 1
                    accepted_here += 1
                    if accepted_for_set == set_quota or len(domain_rows) == CANDIDATES_PER_DOMAIN:
                        break
                token_node = root.find(".//oai:resumptionToken", NS)
                token = clean(token_node.text if token_node is not None else "")
                request_log.append(
                    {
                        "set": set_spec,
                        "request_url": url,
                        "response_sha256": payload_sha,
                        "retained_response_path": str(raw_path.relative_to(out_dir)),
                        "retained_response_gzip_sha256": raw_gzip_sha,
                        "record_count": len(records),
                        "accepted_before_domain_cap": accepted_here,
                        "resumption_cursor": token_node.get("cursor") if token_node is not None else None,
                        "resumption_complete_list_size": token_node.get("completeListSize") if token_node is not None else None,
                    }
                )
                url = continuation_url(token) if token else None
        if len(domain_rows) != CANDIDATES_PER_DOMAIN:
            raise RuntimeError(
                f"{domain['domain_id']} produced {len(domain_rows)} eligible rows, expected {CANDIDATES_PER_DOMAIN}"
            )
        selected.extend(domain_rows)
        per_domain[domain["domain_id"]] = len(domain_rows)

    with frame_path.open("w", encoding="utf-8") as handle:
        for row in selected:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    frame_sha = hashlib.sha256(frame_path.read_bytes()).hexdigest()
    harvested_at = dt.datetime.now(dt.timezone.utc).isoformat()
    log = {
        "schema_version": "orion.p4.arxiv-ccby-harvest-log.v1",
        "harvested_at": harvested_at,
        "endpoint": BASE,
        "metadata_prefix": "arXivRaw",
        "from": FROM_DATE,
        "until": UNTIL_DATE,
        "selection_rule": "first 384 unique complete non-withdrawn CC BY 4.0 records per declared domain in OAI response order; Earth/environment is balanced 128/128/128 across atmospheric-oceanic physics, geophysics, and earth-planetary astrophysics; this is a 2:1 source pool for the planned 192 adjudicated clusters per domain; domain and set order frozen in script",
        "request_interval_seconds": REQUEST_INTERVAL_SECONDS,
        "raw_response_retention": "all OAI XML pages retained as deterministic gzip members under raw_oai_pages/",
        "requests": request_log,
        "exclusion_counts": exclusion_counts,
        "per_domain": per_domain,
        "selected_total": len(selected),
        "frame_path": frame_path.name,
        "frame_sha256": frame_sha,
    }
    log_path.write_text(json.dumps(log, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    log_sha = hashlib.sha256(log_path.read_bytes()).hexdigest()

    binding = {
        "schema_version": "orion.p4.public-naturalistic-source-binding.v1",
        "binding_id": "P4.NAT.AXIS.768.ARXIV_CC_BY_POOL_1536.V1",
        "created_at": harvested_at,
        "source": "arXiv official OAI-PMH arXivRaw metadata",
        "source_endpoint": BASE,
        "official_policy_urls": {
            "api": "https://info.arxiv.org/help/api/index.html",
            "oai": "https://info.arxiv.org/help/oa/index.html",
            "license": "https://info.arxiv.org/help/license/index.html",
            "versions": "https://info.arxiv.org/help/versions.html",
        },
        "rights": {
            "metadata": "arXiv states that CC0 1.0 applies to all metadata",
            "article_content_filter": "exact arXivRaw license must be CC BY 4.0",
            "excluded_for_content": [
                "arXiv non-exclusive distribution license",
                "CC BY-NC-ND",
                "CC BY-NC-SA",
                "CC BY-SA (excluded to avoid share-alike ambiguity in later case adaptations)",
                "missing/unknown license",
            ],
            "attribution_required": True,
            "third_party_content_warning": "CC BY record eligibility does not by itself clear third-party figures, datasets, or publisher versions; V1 case construction is text-only unless separately cleared",
        },
        "immutability": {
            "unit": "versioned arXiv identifier",
            "rule": "bind only exact latest vN present in the harvested OAI record; unversioned URLs are forbidden",
            "official_basis": "arXiv states each public version is a permanent part of the scientific record and may be cited with the full versioned identifier",
        },
        "frame": {
            "path": frame_path.name,
            "sha256": frame_sha,
            "rows": len(selected),
            "per_domain": per_domain,
            "planned_adjudicated_cases_per_domain": PLANNED_CASES_PER_DOMAIN,
            "candidate_to_planned_ratio": 2.0,
        },
        "harvest_log": {"path": log_path.name, "sha256": log_sha},
        "case_eligibility": {
            "status": "UNADJUDICATED_SOURCE_CANDIDATES_ONLY",
            "not_yet_established": [
                "claim is scientifically material and atomic",
                "full-text evidence licenses the target claim",
                "restricted-view member is genuinely unidentifiable",
                "paired control is identifiable",
                "one of eight naturalistic mechanisms applies",
                "independent evaluator agreement",
                "source-disjoint replication eligibility",
                "full-text bytes fetched and hashed for eligible cases",
                "provider and modality diversity",
                "24 eligible clusters in every domain-by-mechanism cell",
            ],
        },
        "outcomes_accessed": False,
        "grants_scientific_authority": False,
        "terminal": "PUBLIC_CC_BY_SOURCE_POOL_BOUND__NATURALISTIC_CASE_ADJUDICATION_REQUIRED",
    }
    binding_path.write_text(json.dumps(binding, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"frame": str(frame_path), "rows": len(selected), "sha256": frame_sha, "per_domain": per_domain}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
