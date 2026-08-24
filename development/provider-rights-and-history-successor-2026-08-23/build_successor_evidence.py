#!/usr/bin/env python3
"""Build the G01 provider-rights and historical-byte successor evidence.

Only public metadata, legal/policy pages, robots directives, licence texts, and
archive indexes are retrieved.  No case text, article body, issue/comment,
attachment, dataset payload, label, system output, or outcome is requested.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parent
PARENT_ROOT = ROOT.parent / "provider-diverse-metadata-census-2026-08-23"
PARENT_CENSUS = PARENT_ROOT / "SOURCE_CENSUS_V1.json"
PROTOCOL_OUT = ROOT / "PROTOCOL_V1.json"
EVIDENCE_OUT = ROOT / "EVIDENCE_SNAPSHOT_V1.json"
LEDGER_OUT = ROOT / "ROOT_RIGHTS_HISTORY_LEDGER_V1.json"
GAPS_OUT = ROOT / "SUCCESSOR_GAP_LEDGER_V1.json"
CUTOFF = "2025-12-31T23:59:59Z"
USER_AGENT = "orion-provider-rights-history-audit/1.0"

CROSSREF_2025_INFOHASH = "e0eda0104902d61c025e27e4846b66491d4c9f98"
CROSSREF_2025_TORRENT = (
    "https://academictorrents.com/download/"
    f"{CROSSREF_2025_INFOHASH}.torrent"
)

OFFICIAL_EVIDENCE = (
    {
        "evidence_id": "CR_SNAPSHOT_DOC",
        "authority": "Crossref",
        "kind": "HISTORICAL_SNAPSHOT_POLICY",
        "url": "https://www.crossref.org/documentation/metadata-plus/metadata-plus-snapshots/",
        "assertions": [
            "New snapshots are created each month",
            "providing all records up to and including the previous month",
            "snapshots are available to Metadata Plus users only",
            "Snapshots are available for current and previous quarters",
        ],
    },
    {
        "evidence_id": "CR_PUBLIC_DATA_DOC",
        "authority": "Crossref",
        "kind": "ANNUAL_PUBLIC_FILE_POLICY",
        "url": "https://www.crossref.org/services/metadata-retrieval/public-data-file/",
        "assertions": [
            "With the public data file you have access to every DOI ever registered with Crossref",
            "Metadata is supplied by our members",
        ],
    },
    {
        "evidence_id": "CR_2025_RELEASE_DOC",
        "authority": "Crossref",
        "kind": "ANNUAL_PUBLIC_FILE_RELEASE",
        "url": "https://www.crossref.org/blog/2025-public-data-file-now-available/",
        "assertions": [
            "2025 March 12",
            "available in JSON-lines format",
            "https://doi.org/10.13003/87bfgcee6g",
        ],
    },
    {
        "evidence_id": "CR_METADATA_PLUS_TERMS",
        "authority": "Crossref",
        "kind": "SUBSCRIBER_METADATA_RIGHTS",
        "url": "https://www.crossref.org/services/metadata-retrieval/metadata-plus/terms/",
        "assertions": [
            "fully-paid, non-exclusive, worldwide license",
            "use, reproduce, transmit, distribute, display and sublicense Metadata without restriction",
            "grants Subscriber",
        ],
    },
    {
        "evidence_id": "CR_LICENSE_METADATA_DOC",
        "authority": "Crossref",
        "kind": "LICENSE_FIELD_LIMITATION",
        "url": "https://www.crossref.org/documentation/principles-practices/best-practices/license/",
        "assertions": [
            "Members registering licensing information in their metadata",
            "we make sure the URLs provided are URLs, but don’t verify that they resolve to an active license",
        ],
    },
    {
        "evidence_id": "CR_ROBOTS",
        "authority": "Crossref",
        "kind": "ROBOTS_POLICY",
        "url": "https://www.crossref.org/robots.txt",
        "assertions": ["User-agent: *", "Allow: /", "Disallow: /_"],
    },
    {
        "evidence_id": "ZENODO_TERMS",
        "authority": "Zenodo/CERN",
        "kind": "TERMS_OF_USE",
        "url": "https://about.zenodo.org/terms/",
        "assertions": [
            "Unless specified otherwise, Zenodo metadata may be freely reused under the CC0 waiver",
            "Users of content",
            "shall respect applicable license conditions",
            "does not transfer any intellectual property rights",
        ],
    },
    {
        "evidence_id": "ZENODO_POLICIES",
        "authority": "Zenodo/CERN",
        "kind": "CONTENT_AND_METADATA_POLICY",
        "url": "https://about.zenodo.org/policies/",
        "assertions": [
            "Users must specify a license for all publicly available files",
            "Use and re-use is subject to the license under which the data objects were deposited",
            "Metadata is licensed under CC0, except for email addresses",
            "All uploaded content remains the property of the parties prior to submission",
        ],
    },
    {
        "evidence_id": "ZENODO_ROBOTS",
        "authority": "Zenodo/CERN",
        "kind": "ROBOTS_POLICY",
        "url": "https://zenodo.org/robots.txt",
        "assertions": [
            "Disallow: /api",
            "Allow: /api/records/*/files",
            "Crawl-delay: 10",
        ],
    },
    {
        "evidence_id": "GITLAB_API_TERMS",
        "authority": "GitLab Inc.",
        "kind": "API_TERMS",
        "url": "https://handbook.gitlab.com/handbook/legal/api-terms/",
        "assertions": [
            "Not to use the GitLab APIs for the bulk collection or scraping of information",
            "you do not acquire ownership of any rights in them, or the content that is accessed through them",
            "Last modified February 9, 2026",
        ],
    },
    {
        "evidence_id": "GITLAB_WEBSITE_TERMS",
        "authority": "GitLab Inc.",
        "kind": "WEBSITE_TERMS",
        "url": "https://handbook.gitlab.com/handbook/legal/policies/website-terms-of-use/",
        "assertions": [
            "This Agreement does not transfer any GitLab, or third party intellectual property, to you",
            "scrape",
            "unless otherwise permitted under applicable content licensing permissions",
        ],
    },
    {
        "evidence_id": "GITLAB_REST_DOC",
        "authority": "GitLab Inc.",
        "kind": "API_DOCUMENTATION",
        "url": "https://docs.gitlab.com/api/rest/",
        "assertions": [
            "Automate your workflows and build integrations with the GitLab REST API",
            "REST API requests are subject to rate limit settings",
        ],
    },
    {
        "evidence_id": "GITLAB_ROBOTS",
        "authority": "GitLab.com",
        "kind": "ROBOTS_POLICY",
        "url": "https://gitlab.com/robots.txt",
        "assertions": ["Crawl-delay: 1", "Disallow: /api/v*", "Disallow: /*/uploads/"],
    },
    {
        "evidence_id": "NASA_DATA_USE",
        "authority": "NASA Earthdata/ESDIS",
        "kind": "DATA_USE_POLICY",
        "url": "https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance",
        "assertions": [
            "Non-NASA data available through the ESDIS project is subject to the license arrangements of the sponsoring organization",
            "Unless the content is marked with a use restriction or license, data provided from a NASA-led mission are licensed as Creative Commons Zero (CC0)",
            "NASA material is not protected by copyright within the United States, unless noted",
        ],
    },
    {
        "evidence_id": "NASA_OPEN_POLICY",
        "authority": "NASA Earthdata/ESDIS",
        "kind": "OPEN_DATA_POLICY",
        "url": "https://www.earthdata.nasa.gov/engage/open-data-services-software-policies",
        "assertions": [
            "promotes the full and open sharing of all data, metadata, documentation, models, images, and research results",
            "EOSDIS makes a number of APIs available",
        ],
    },
    {
        "evidence_id": "CMR_ROBOTS",
        "authority": "NASA ESDIS CMR",
        "kind": "ROBOTS_POLICY",
        "url": "https://cmr.earthdata.nasa.gov/robots.txt",
        "assertions": ["Disallow: /search/collections/", "Disallow: /search/granules/"],
    },
    {
        "evidence_id": "NCEI_ROBOTS",
        "authority": "NOAA NCEI",
        "kind": "ROBOTS_POLICY",
        "url": "https://www.ncei.noaa.gov/robots.txt",
        "assertions": ["Disallow: /data*", "Disallow: /orders*"],
    },
    {
        "evidence_id": "CC_BY_4_LEGAL",
        "authority": "Creative Commons",
        "kind": "LICENSE_TEXT",
        "url": "https://creativecommons.org/licenses/by/4.0/legalcode.txt",
        "assertions": ["Creative Commons Attribution 4.0 International Public License"],
    },
    {
        "evidence_id": "CC_BY_NC_4_LEGAL",
        "authority": "Creative Commons",
        "kind": "LICENSE_TEXT",
        "url": "https://creativecommons.org/licenses/by-nc/4.0/legalcode.txt",
        "assertions": ["Creative Commons Attribution-NonCommercial 4.0 International Public License"],
    },
    {
        "evidence_id": "CC_BY_NC_ND_4_LEGAL",
        "authority": "Creative Commons",
        "kind": "LICENSE_TEXT",
        "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.txt",
        "assertions": ["Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International Public License"],
    },
    {
        "evidence_id": "CC0_1_LEGAL",
        "authority": "Creative Commons",
        "kind": "WAIVER_TEXT",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt",
        "assertions": ["CC0 1.0 Universal"],
    },
)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def normalized_text(payload: bytes) -> str:
    text = payload.decode("utf-8", "replace")
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
    text = text.replace("&nbsp;", " ").replace("&ldquo;", '"').replace("&rdquo;", '"')
    text = text.replace("&rsquo;", "’").replace("&#x27;", "'")
    return re.sub(r"\s+", " ", text).strip()


def request_bytes(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    attempts: int = 4,
    timeout: int = 30,
) -> tuple[bytes, dict]:
    request_headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        request_headers.update(headers)
    for attempt in range(attempts):
        request = urllib.request.Request(url, headers=request_headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read() if method != "HEAD" else b""
                return body, {
                    "request_url": url,
                    "final_url": response.geturl(),
                    "method": method,
                    "http_status": response.status,
                    "content_type": response.headers.get("Content-Type"),
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "content_length_header": response.headers.get("Content-Length"),
                    "response_sha256": sha256(body) if method != "HEAD" else None,
                    "response_bytes": len(body),
                }
        except urllib.error.HTTPError as exc:
            body = exc.read() if method != "HEAD" else b""
            if exc.code == 429 and attempt < attempts - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            return body, {
                "request_url": url,
                "final_url": exc.geturl(),
                "method": method,
                "http_status": exc.code,
                "content_type": exc.headers.get("Content-Type"),
                "etag": exc.headers.get("ETag"),
                "last_modified": exc.headers.get("Last-Modified"),
                "content_length_header": exc.headers.get("Content-Length"),
                "response_sha256": sha256(body) if method != "HEAD" else None,
                "response_bytes": len(body),
            }
        except Exception as exc:
            if attempt == attempts - 1:
                return b"", {
                    "request_url": url,
                    "final_url": None,
                    "method": method,
                    "http_status": None,
                    "error": str(exc),
                    "response_sha256": None,
                    "response_bytes": 0,
                }
            time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


def protocol(census: dict, frozen_at: str) -> dict:
    value = {
        "schema_version": "orion.provider-rights-history-successor.protocol.v1",
        "frozen_at_utc": frozen_at,
        "parent_successor_identity": "PROVIDER_MODALITY_TRANSPORT_METADATA_CENSUS_V1",
        "successor_identity": "PROVIDER_ROOT_RIGHTS_AND_HISTORICAL_BYTE_PROVENANCE_V1",
        "parent_census_payload_sha256": census["snapshot_payload_sha256"],
        "cutoff_utc": CUTOFF,
        "authority": "PUBLIC_POLICY_METADATA_AND_ARCHIVE_INDEX_AUDIT_ONLY__NOT_LEGAL_ADVICE__NOT_CASE_AUTHORITY",
        "outcomes_accessed": False,
        "protected_case_fields_accessed": False,
        "root_count": 16,
        "crossref_history_root_count": 8,
        "questions": [
            "Can exact pre-cutoff Crossref metadata bytes be bound to every article root through official snapshots, public files, deposit evidence, or independent content-addressed archives?",
            "Can metadata, body/file/code, issue/comment, documentation, and attachment rights be bound separately for every root without opening candidate content?",
        ],
        "historical_evidence_hierarchy": [
            "exact provider historical revision bytes plus provider timestamp and content hash",
            "content-addressed official snapshot containing the exact root plus extraction proof",
            "independent archive capture of the exact provider metadata response with timestamp and digest",
            "provider creation/deposit/index timestamp only, which is identity evidence but not byte provenance",
        ],
        "rights_status_vocabulary": {
            "ROOT_BOUND_PERMISSION": "An authoritative root-bound licence or policy covers the named content class; this is not a legal opinion or case-eligibility finding.",
            "DECLARED_PERMISSION_AUTHORITY_UNVERIFIED": "The provider requires a declaration and the record supplies one, but uploader/depositor authority or byte scope is not independently established.",
            "ACCESS_ONLY_NOT_REUSE": "The provider permits or exposes acquisition but gives no root-bound reuse grant for this content class.",
            "CANNOT_CHECK": "The evidence does not establish the content-class right, historical bytes, or scope.",
            "NOT_ACCESSED": "The content class remained unopened and unarchived.",
        },
        "robots_boundary": "robots.txt is an acquisition/crawling directive, not copyright permission, a content licence, case eligibility, or scientific authority",
        "history_positive_condition": "For each Crossref DOI, an exact pre-cutoff metadata object is extracted from a provider or independent content-addressed archive with timestamp, digest, and identity proof.",
        "rights_positive_condition": "Every intended acquired content class has a root-bound authoritative permission and acquisition policy compatible with the frozen use; uploader/depositor authority ambiguities are separately closed.",
        "fail_closed_terminals": {
            "history": "CANNOT_CHECK_EXACT_CROSSREF_HISTORICAL_BYTES",
            "rights": "CANNOT_CHECK_ROOT_CONTENT_CLASS_RIGHTS",
            "eligibility": "METADATA_ROOT_ONLY__CASE_ELIGIBILITY_NOT_ASSESSED",
            "overall": "CANNOT_CHECK_RIGHTS_AND_HISTORY_BINDING",
        },
        "forbidden_access": [
            "article_or_abstract_body",
            "dataset_payload",
            "issue_or_comment_body",
            "attachment",
            "repository_readme_or_project_description",
            "case_label_or_pair_role",
            "candidate_or_comparator_output",
            "protected_gold_or_outcome",
        ],
    }
    value["protocol_payload_sha256"] = sha256(canonical_bytes(value))
    return value


def fetch_official_evidence() -> tuple[list[dict], dict[str, bytes]]:
    records: list[dict] = []
    bodies: dict[str, bytes] = {}
    for spec in OFFICIAL_EVIDENCE:
        body, receipt = request_bytes(spec["url"])
        text = normalized_text(body)
        matches = []
        for assertion in spec["assertions"]:
            present = assertion.casefold() in text.casefold()
            matches.append(
                {
                    "assertion": assertion,
                    "present": present,
                    "assertion_sha256": sha256(assertion.encode("utf-8")),
                }
            )
        records.append(
            {
                **spec,
                "captured_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
                "receipt": receipt,
                "assertion_checks": matches,
                "all_assertions_present": all(item["present"] for item in matches),
                "body_archived": False,
            }
        )
        bodies[spec["evidence_id"]] = body
    return records, bodies


def bdecode(payload: bytes) -> dict:
    def parse(i: int = 0):
        marker = payload[i : i + 1]
        if marker == b"i":
            end = payload.index(b"e", i)
            return int(payload[i + 1 : end]), end + 1
        if marker == b"l":
            values = []
            i += 1
            while payload[i : i + 1] != b"e":
                value, i = parse(i)
                values.append(value)
            return values, i + 1
        if marker == b"d":
            value = {}
            i += 1
            while payload[i : i + 1] != b"e":
                key, i = parse(i)
                item, i = parse(i)
                value[key] = item
            return value, i + 1
        colon = payload.index(b":", i)
        length = int(payload[i:colon])
        start = colon + 1
        return payload[start : start + length], start + length

    result, end = parse()
    if end != len(payload) or not isinstance(result, dict):
        raise ValueError("invalid bencoded dictionary")
    return result


def bencode(value: object) -> bytes:
    if isinstance(value, int):
        return b"i" + str(value).encode() + b"e"
    if isinstance(value, bytes):
        return str(len(value)).encode() + b":" + value
    if isinstance(value, list):
        return b"l" + b"".join(bencode(item) for item in value) + b"e"
    if isinstance(value, dict):
        return b"d" + b"".join(bencode(key) + bencode(value[key]) for key in sorted(value)) + b"e"
    raise TypeError(type(value))


def fetch_torrent_evidence() -> dict:
    body, receipt = request_bytes(CROSSREF_2025_TORRENT)
    parsed = bdecode(body) if receipt["http_status"] == 200 else {}
    info = parsed.get(b"info", {})
    observed_infohash = hashlib.sha1(bencode(info)).hexdigest() if info else None
    files = info.get(b"files", []) if isinstance(info, dict) else []
    return {
        "evidence_id": "CR_2025_PUBLIC_FILE_TORRENT",
        "authority": "Academic Torrents linked by Crossref DOI 10.13003/87bfgcee6g",
        "kind": "CONTENT_ADDRESSED_CORPUS_MANIFEST",
        "url": CROSSREF_2025_TORRENT,
        "captured_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "receipt": receipt,
        "expected_infohash_sha1": CROSSREF_2025_INFOHASH,
        "observed_infohash_sha1": observed_infohash,
        "infohash_match": observed_infohash == CROSSREF_2025_INFOHASH,
        "torrent_file_count": len(files),
        "torrent_piece_length": info.get(b"piece length") if info else None,
        "torrent_piece_count": len(info.get(b"pieces", b"")) // 20 if info else None,
        "root_membership_checked": False,
        "root_membership_status": "CANNOT_CHECK_WITHOUT_197GB_CORPUS_EXTRACTION_OR_PROVIDER_INDEX",
        "body_archived": False,
    }


def archive_query(doi: str, target: str) -> dict:
    params = [
        ("url", target),
        ("from", "2025"),
        ("to", "2025"),
        ("output", "json"),
        ("fl", "timestamp,original,statuscode,digest,mimetype,length"),
        ("filter", "statuscode:200"),
        ("collapse", "digest"),
    ]
    url = "https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(params)
    body, receipt = request_bytes(
        url, headers={"Accept": "application/json"}, attempts=1, timeout=15
    )
    captures: list = []
    parse_error = None
    if receipt["http_status"] == 200 and body.strip():
        try:
            captures = json.loads(body)
        except Exception as exc:
            parse_error = str(exc)
    data_rows = captures[1:] if captures and isinstance(captures[0], list) else []
    return {
        "doi": doi,
        "target": target,
        "query_url": url,
        "receipt": receipt,
        "capture_rows": data_rows,
        "capture_count": len(data_rows),
        "parse_error": parse_error,
        "archive_body_fetched": False,
    }


def crossref_current(record: dict) -> tuple[dict, dict]:
    doi = record["provider_record_identity"].lower()
    select = "DOI,type,publisher,created,deposited,indexed,license,URL,member,ISSN,issn-type"
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"filter": f"doi:{doi}", "select": select, "rows": 1}
    )
    body, receipt = request_bytes(url, headers={"Accept": "application/json"})
    payload = json.loads(body) if receipt["http_status"] == 200 else {}
    items = payload.get("message", {}).get("items", [])
    item = items[0] if len(items) == 1 else {}
    normalized = {
        "doi": item.get("DOI", "").lower(),
        "publisher": item.get("publisher"),
        "created": item.get("created", {}).get("date-time"),
        "deposited": item.get("deposited", {}).get("date-time"),
        "indexed": item.get("indexed", {}).get("date-time"),
        "issn": sorted(set(item.get("ISSN", []))),
        "license": [
            {
                "url": value.get("URL"),
                "content_version": value.get("content-version"),
                "start": value.get("start", {}).get("date-time"),
                "delay_in_days": value.get("delay-in-days"),
            }
            for value in item.get("license", [])
        ],
    }
    return normalized, {"url": url, "receipt": receipt, "normalized_sha256": sha256(canonical_bytes(normalized))}


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def gap(
    root_id: str,
    content_class: str,
    current_status: str,
    successor_prefix: str,
    discriminator: str,
    positive: str,
    negative: str,
) -> dict:
    return {
        "root_id": root_id,
        "unresolved_cell": content_class,
        "current_status": current_status,
        "successor_identity": f"{successor_prefix}__{safe_id(root_id)}",
        "next_discriminator": discriminator,
        "positive_condition": positive,
        "negative_condition": negative,
        "cannot_check_condition": "The named authoritative byte, permission scope, identity, or independent custody evidence remains absent.",
    }


def crossref_rights(record: dict, current: dict) -> tuple[dict, list[dict]]:
    doi = current["doi"]
    licences = current["license"]
    content_licences = [
        item
        for item in licences
        if item.get("content_version") in {"vor", "unspecified"}
    ]
    cc_licences = [item for item in content_licences if "creativecommons.org/licenses/" in (item.get("url") or "")]
    if cc_licences:
        body_status = "DECLARED_PERMISSION_AUTHORITY_UNVERIFIED"
        body_reason = "A current Crossref member-deposited VOR/unspecified Creative Commons URI exists, but Crossref states it does not verify licence URLs and no article bytes or publisher root statement were opened."
    else:
        body_status = "CANNOT_CHECK"
        body_reason = "No current Crossref VOR/unspecified Creative Commons licence URI establishes article-body reuse; TDM or STM policy links are not promoted to a body licence."
    rights = {
        "provider_metadata_record": {
            "status": "CANNOT_CHECK",
            "reason": "Crossref describes public/open access and Metadata Plus grants subscribers broad metadata rights, but no equally explicit public-REST caller reuse grant was bound here; site CC BY is not assumed to cover member-supplied record fields.",
            "evidence_ids": ["CR_PUBLIC_DATA_DOC", "CR_METADATA_PLUS_TERMS", "CR_ROBOTS"],
        },
        "article_body": {
            "status": body_status,
            "reason": body_reason,
            "declared_content_licences": content_licences,
            "evidence_ids": ["CR_LICENSE_METADATA_DOC"],
        },
        "supplement_or_attachment": {
            "status": "CANNOT_CHECK",
            "reason": "No root-bound supplement or attachment licence was identified without opening those content classes.",
            "evidence_ids": ["CR_LICENSE_METADATA_DOC"],
        },
        "case_eligibility": {
            "status": "NOT_ACCESSED",
            "reason": "Metadata identity and rights declarations do not establish case inclusion, labels, pairing, or scientific strata.",
            "evidence_ids": [],
        },
    }
    gaps = [
        gap(
            doi,
            "PROVIDER_METADATA_REUSE",
            rights["provider_metadata_record"]["status"],
            "CROSSREF_PUBLIC_REST_METADATA_REUSE_GRANT",
            "Obtain an authoritative Crossref public-REST/public-data licence applying to member-supplied record fields, including exclusions for abstracts or other copyrighted fields.",
            "The authoritative grant covers the exact retained field whitelist and permits the frozen processing and retention.",
            "The provider expressly excludes one or more retained fields or the planned use.",
        ),
        gap(
            doi,
            "ARTICLE_BODY_RIGHTS",
            rights["article_body"]["status"],
            "PUBLISHER_ROOT_LICENSE_SCOPE_BINDING",
            "Without acquiring article text, bind a publisher-signed root-specific VOR licence assertion and its effective date to the DOI and intended processing.",
            "The publisher-root assertion covers the exact VOR and intended processing at acquisition time.",
            "The publisher disclaims the declared licence, restricts the intended use, or maps it to a different version.",
        ),
        gap(
            doi,
            "SUPPLEMENT_ATTACHMENT_RIGHTS",
            "CANNOT_CHECK",
            "PUBLISHER_SUPPLEMENT_ATTACHMENT_RIGHTS_BINDING",
            "Bind a publisher root policy enumerating supplement and attachment rights separately from the article licence before any bytes are opened.",
            "Every intended supplement/attachment class is covered by a root-bound permission.",
            "The host excludes or separately licenses a required class.",
        ),
        gap(
            doi,
            "CASE_ELIGIBILITY",
            "NOT_ACCESSED",
            "OUTCOME_BLIND_ARTICLE_ROOT_ELIGIBILITY_CUSTODY",
            "An external custodian applies frozen metadata and rights gates and reports counts/exclusions only before content or outcomes are released.",
            "The root supplies at least one legally admissible eligible case under the frozen cell.",
            "The root has zero eligible cases under the frozen rules.",
        ),
    ]
    return rights, gaps


def zenodo_rights(record: dict) -> tuple[dict, list[dict]]:
    root_id = record["provider_record_identity"]
    licence_id = record["content_class_rights"]["dataset_files"]["declared_licence_id"]
    rights = {
        "provider_metadata_record": {
            "status": "ROOT_BOUND_PERMISSION",
            "reason": "Zenodo terms and policies explicitly place metadata under CC0 except email addresses; no email fields are retained in the census.",
            "evidence_ids": ["ZENODO_TERMS", "ZENODO_POLICIES", "CC0_1_LEGAL"],
        },
        "dataset_files": {
            "status": "DECLARED_PERMISSION_AUTHORITY_UNVERIFIED",
            "reason": "The exact record declares CC BY 4.0 and Zenodo requires a licence for public files, but Zenodo assigns uploader responsibility and does not independently establish uploader authority.",
            "declared_licence_id": licence_id,
            "evidence_ids": ["ZENODO_TERMS", "ZENODO_POLICIES", "CC_BY_4_LEGAL", "ZENODO_ROBOTS"],
        },
        "linked_or_derived_attachments": {
            "status": "CANNOT_CHECK",
            "reason": "The record declaration is not extended to third-party linked objects or derived external attachments without a root-specific relation.",
            "evidence_ids": ["ZENODO_TERMS", "ZENODO_POLICIES"],
        },
        "case_eligibility": {
            "status": "NOT_ACCESSED",
            "reason": "Files were not opened; metadata and declared licence do not establish scientific case eligibility.",
            "evidence_ids": [],
        },
    }
    gaps = [
        gap(
            root_id,
            "DATASET_FILE_UPLOADER_AUTHORITY",
            rights["dataset_files"]["status"],
            "ZENODO_UPLOADER_RIGHTS_ASSURANCE",
            "Obtain a depositor-signed authority statement or independent rights audit binding CC BY 4.0 to the exact version DOI and all intended files.",
            "Uploader authority and file-level scope are independently established.",
            "The uploader lacks authority or one file falls outside the declared licence.",
        ),
        gap(
            root_id,
            "LINKED_DERIVED_ATTACHMENT_RIGHTS",
            "CANNOT_CHECK",
            "ZENODO_LINKED_OBJECT_RIGHTS_BINDING",
            "Enumerate only metadata links under external custody and bind each external object's own licence before retrieval.",
            "Every intended linked object has an independently verified root-bound permission.",
            "Any required linked object is unlicensed or incompatible.",
        ),
        gap(
            root_id,
            "CASE_ELIGIBILITY",
            "NOT_ACCESSED",
            "OUTCOME_BLIND_ZENODO_ROOT_ELIGIBILITY_CUSTODY",
            "An external custodian opens files only after rights assurance and returns eligibility counts/exclusions without labels or outcomes.",
            "The root supplies an eligible case in its frozen cell.",
            "No file in the root satisfies the frozen case rules.",
        ),
    ]
    return rights, gaps


def gitlab_rights(record: dict) -> tuple[dict, list[dict]]:
    root_id = record["provider_record_identity"]
    code = record["content_class_rights"]["repository_code"]
    licence_name = "LGPL-2.1 license text" if root_id == "gromacs/gromacs" else "GPL-2.0 license text"
    rights = {
        "provider_project_metadata": {
            "status": "ACCESS_ONLY_NOT_REUSE",
            "reason": "GitLab documents bounded API access but its API terms grant no ownership in accessed content and prohibit bulk collection except where law permits.",
            "evidence_ids": ["GITLAB_API_TERMS", "GITLAB_REST_DOC", "GITLAB_ROBOTS"],
        },
        "repository_code": {
            "status": "ROOT_BOUND_PERMISSION",
            "reason": f"An exact {licence_name} is hashed at the selected pre-cutoff commit; this does not extend to issue prose or attachments.",
            "licence_path": code["licence_path"],
            "licence_content_sha256": code["licence_content_sha256"],
            "evidence_ids": [],
        },
        "issue_or_comment_text": {
            "status": "CANNOT_CHECK",
            "reason": "Neither project code licence nor GitLab API/website terms supplies a root-bound public reuse grant for user issue/comment prose.",
            "evidence_ids": ["GITLAB_API_TERMS", "GITLAB_WEBSITE_TERMS", "GITLAB_ROBOTS"],
        },
        "issue_attachment": {
            "status": "CANNOT_CHECK",
            "reason": "GitLab robots disallow upload paths and no project/root attachment licence is bound.",
            "evidence_ids": ["GITLAB_API_TERMS", "GITLAB_WEBSITE_TERMS", "GITLAB_ROBOTS"],
        },
        "case_eligibility": {
            "status": "NOT_ACCESSED",
            "reason": "No issue, comment, attachment, label, or outcome was opened.",
            "evidence_ids": [],
        },
    }
    gaps = [
        gap(
            root_id,
            "PROJECT_METADATA_REUSE",
            rights["provider_project_metadata"]["status"],
            "GITLAB_BOUNDED_API_DATA_REUSE_SCOPE",
            "Obtain GitLab and project-owner authorization for the exact retained project metadata fields and non-bulk frozen acquisition pattern.",
            "Both API terms and project-owner rights permit the exact processing and retention.",
            "The API or project owner forbids a required use.",
        ),
        gap(
            root_id,
            "ISSUE_COMMENT_RIGHTS",
            "CANNOT_CHECK",
            "GITLAB_PROJECT_ISSUE_COMMENT_RIGHTS_BINDING",
            "Obtain a project-owner policy or contributor consent mechanism covering issue and comment prose before any text is opened.",
            "Every intended issue/comment unit is covered by an authoritative permission.",
            "Required user prose lacks permission or consent.",
        ),
        gap(
            root_id,
            "ISSUE_ATTACHMENT_RIGHTS",
            "CANNOT_CHECK",
            "GITLAB_PROJECT_ATTACHMENT_RIGHTS_BINDING",
            "Bind upload/attachment ownership and licence separately and respect provider acquisition policy before any attachment URL is followed.",
            "Every intended attachment is covered and lawfully retrievable.",
            "Any required attachment is prohibited, private, or unlicensed.",
        ),
        gap(
            root_id,
            "CASE_ELIGIBILITY",
            "NOT_ACCESSED",
            "OUTCOME_BLIND_GITLAB_ROOT_ELIGIBILITY_CUSTODY",
            "After rights binding, an external custodian reports only eligible counts and exclusion codes for the frozen project root.",
            "The project yields an eligible case in the frozen cell.",
            "The project yields zero eligible cases.",
        ),
    ]
    return rights, gaps


def cmr_rights(record: dict) -> tuple[dict, list[dict]]:
    root_id = record["provider_record_identity"]
    nasa_led = root_id.endswith("-GES_DISC")
    if nasa_led:
        data_status = "ROOT_BOUND_PERMISSION"
        data_reason = "The exact historical CMR root is NASA GES DISC/Aqua AIRS; its use-constraints object cites NASA guidance and declares no conflicting licence. NASA policy places unmarked NASA-led mission data under CC0."
        data_evidence = ["NASA_DATA_USE", "NASA_OPEN_POLICY", "CC0_1_LEGAL", "CMR_ROBOTS"]
    else:
        data_status = "CANNOT_CHECK"
        data_reason = "The root is NOAA-hosted non-NASA data. NASA guidance expressly defers to the sponsoring organization, the historical UMM has no use-constraints grant, and no root-bound NOAA permission was located."
        data_evidence = ["NASA_DATA_USE", "CMR_ROBOTS", "NCEI_ROBOTS"]
    rights = {
        "provider_collection_metadata": {
            "status": "ROOT_BOUND_PERMISSION" if nasa_led else "CANNOT_CHECK",
            "reason": "NASA full-and-open/CC0 policy covers the NASA-led CMR metadata root." if nasa_led else "The NASA CMR record is accessible, but non-NASA NOAA metadata rights are deferred to the sponsor and remain unbound.",
            "evidence_ids": data_evidence,
        },
        "collection_data_files": {
            "status": data_status,
            "reason": data_reason,
            "evidence_ids": data_evidence,
        },
        "documentation_or_third_party_attachment": {
            "status": "CANNOT_CHECK",
            "reason": "NASA policy warns that third-party copyrighted material may require separate permission; documents and attachments were not opened or classified.",
            "evidence_ids": ["NASA_DATA_USE", "CMR_ROBOTS"],
        },
        "case_eligibility": {
            "status": "NOT_ACCESSED",
            "reason": "No collection file or documentation was opened; rights policy does not establish scientific case eligibility.",
            "evidence_ids": [],
        },
    }
    gaps = []
    if not nasa_led:
        gaps.extend(
            [
                gap(
                    root_id,
                    "NOAA_COLLECTION_METADATA_RIGHTS",
                    "CANNOT_CHECK",
                    "NOAA_NCEI_ROOT_METADATA_RIGHTS_BINDING",
                    "Obtain an authoritative NOAA NCEI root-specific metadata licence or public-domain statement tied to the EXISINCAL native identifier.",
                    "The NOAA statement covers the exact metadata root and intended retention/reuse.",
                    "NOAA identifies a restriction or third-party field incompatible with use.",
                ),
                gap(
                    root_id,
                    "NOAA_COLLECTION_FILE_RIGHTS",
                    "CANNOT_CHECK",
                    "NOAA_NCEI_EXISINCAL_FILE_RIGHTS_BINDING",
                    "Obtain a root-specific NOAA file-use statement before any collection file is opened.",
                    "The exact collection files have a compatible authoritative permission.",
                    "The files are restricted or permission cannot be granted.",
                ),
            ]
        )
    gaps.extend(
        [
            gap(
                root_id,
                "DOCUMENTATION_THIRD_PARTY_ATTACHMENT_RIGHTS",
                "CANNOT_CHECK",
                "CMR_DOCUMENT_ATTACHMENT_PROVENANCE_BINDING",
                "Enumerate document/attachment metadata under external custody and bind NASA versus third-party provenance and permission before retrieval.",
                "Every intended document/attachment has compatible provenance and permission.",
                "A required item is third-party restricted or unlicensed.",
            ),
            gap(
                root_id,
                "CASE_ELIGIBILITY",
                "NOT_ACCESSED",
                "OUTCOME_BLIND_CMR_ROOT_ELIGIBILITY_CUSTODY",
                "After content-class rights close, an external custodian reports eligibility counts/exclusions without releasing file content or outcomes.",
                "The root supplies an eligible case in its frozen cell.",
                "The root supplies zero eligible cases.",
            ),
        ]
    )
    return rights, gaps


def main() -> int:
    census = json.loads(PARENT_CENSUS.read_text(encoding="utf-8"))
    captured_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    proto = protocol(census, captured_at)
    PROTOCOL_OUT.parent.mkdir(parents=True, exist_ok=True)
    PROTOCOL_OUT.write_text(json.dumps(proto, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    evidence_records, _ = fetch_official_evidence()
    evidence_records.append(fetch_torrent_evidence())
    jan_snapshot_url = "https://api.crossref.org/snapshots/monthly/2026/01/all.json.tar.gz"
    _, jan_receipt = request_bytes(jan_snapshot_url, method="HEAD")
    evidence_records.append(
        {
            "evidence_id": "CR_2026_01_SNAPSHOT_HEAD",
            "authority": "Crossref Metadata Plus route",
            "kind": "IDEAL_CUTOFF_SNAPSHOT_AVAILABILITY",
            "url": jan_snapshot_url,
            "captured_at_utc": captured_at,
            "receipt": jan_receipt,
            "interpretation": "The January 2026 snapshot would cover records through December 2025 under Crossref documentation, but the current anonymous HEAD is 404 and the documented service is subscriber-only with limited retention.",
            "historical_bytes_obtained": False,
            "body_archived": False,
        }
    )

    root_ledger = []
    gaps: list[dict] = []
    archive_queries = []
    licence_urls: set[str] = set()
    crossref_history_counts = {
        "exact_pre_cutoff_bytes": 0,
        "current_deposit_after_cutoff": 0,
        "internet_archive_exact_api_captures": 0,
        "internet_archive_doi_redirect_captures": 0,
    }

    for record in census["records"]:
        provider = record["metadata_provider_id"]
        root_id = record["provider_record_identity"]
        history = None
        if provider == "CROSSREF_REST_API":
            current, current_receipt = crossref_current(record)
            for value in current["license"]:
                if value.get("url"):
                    licence_urls.add(value["url"])
            api_target = f"api.crossref.org/works/{current['doi']}"
            doi_target = f"doi.org/{current['doi']}"
            api_archive = archive_query(current["doi"], api_target)
            doi_archive = archive_query(current["doi"], doi_target)
            archive_queries.extend([api_archive, doi_archive])
            crossref_history_counts["internet_archive_exact_api_captures"] += api_archive["capture_count"]
            crossref_history_counts["internet_archive_doi_redirect_captures"] += doi_archive["capture_count"]
            post_cutoff_deposit = bool(current["deposited"] and current["deposited"] > CUTOFF)
            crossref_history_counts["current_deposit_after_cutoff"] += int(post_cutoff_deposit)
            annual_2025_relation = (
                "POSSIBLY_IN_RELEASE__ROOT_MEMBERSHIP_NOT_EXTRACTED"
                if current["created"] and current["created"] <= "2025-03-12T23:59:59Z"
                else "NOT_IN_2025_RELEASE_BY_PROVIDER_CREATION_TIME_AFTER_RELEASE"
            )
            history = {
                "status": "CANNOT_CHECK_EXACT_CROSSREF_HISTORICAL_BYTES",
                "current_sparse_metadata": current,
                "current_sparse_metadata_receipt": current_receipt,
                "current_deposit_after_cutoff": post_cutoff_deposit,
                "official_2025_public_file_relation": annual_2025_relation,
                "official_2025_public_file_root_membership_checked": False,
                "official_2026_01_snapshot_bytes_obtained": False,
                "internet_archive_exact_api_capture_count": api_archive["capture_count"],
                "internet_archive_doi_redirect_capture_count": doi_archive["capture_count"],
                "negative_identity": (
                    f"POST_CUTOFF_REDEPOSIT_DIVERGENCE__{safe_id(current['doi'])}"
                    if post_cutoff_deposit
                    else f"UNCOMMITTED_PRE_CUTOFF_DEPOSIT_BYTES__{safe_id(current['doi'])}"
                ),
                "evidence_ids": [
                    "CR_SNAPSHOT_DOC",
                    "CR_PUBLIC_DATA_DOC",
                    "CR_2025_RELEASE_DOC",
                    "CR_2025_PUBLIC_FILE_TORRENT",
                    "CR_2026_01_SNAPSHOT_HEAD",
                ],
            }
            gaps.append(
                gap(
                    current["doi"],
                    "EXACT_PRE_CUTOFF_METADATA_BYTES",
                    history["status"],
                    "CROSSREF_MEMBER_DEPOSIT_OR_2026_01_SNAPSHOT_BYTE_BINDING",
                    "Obtain the member's original pre-cutoff XML deposit plus Crossref submission receipt and hash, or an independently preserved January 2026 Metadata Plus snapshot with root extraction proof.",
                    "Exact bytes, timestamp, DOI identity, and independent digest agree across provider/depositor or snapshot custody.",
                    "The preserved bytes differ from the current assumed fields or no pre-cutoff root exists.",
                )
            )
            rights, new_gaps = crossref_rights(record, current)
        elif provider == "ZENODO_REST_API":
            rights, new_gaps = zenodo_rights(record)
        elif provider == "GITLAB_COM_REST_API_V4":
            rights, new_gaps = gitlab_rights(record)
        elif provider == "NASA_ESDIS_CMR_SEARCH_API":
            rights, new_gaps = cmr_rights(record)
        else:
            raise RuntimeError(f"unsupported provider {provider}")
        gaps.extend(new_gaps)
        root_ledger.append(
            {
                "wave_id": record["wave_id"],
                "protected_domain_candidate": record["protected_domain_candidate"],
                "metadata_provider_id": provider,
                "content_host_identity": record["content_host_identity"],
                "artifact_modality": record["artifact_modality"],
                "root_id": root_id,
                "canonical_dedup_root": record["canonical_dedup_root"],
                "persistent_identifier": record["persistent_identifier"],
                "historical_byte_provenance": history,
                "content_class_rights": rights,
                "case_content_accessed": False,
                "case_eligibility_assessed": False,
                "labels_or_outcomes_accessed": False,
            }
        )

    # Verify every current Crossref-declared licence/policy URL without treating
    # HTTP accessibility as proof of root scope.
    for index, url in enumerate(sorted(licence_urls), start=1):
        body, receipt = request_bytes(url)
        evidence_records.append(
            {
                "evidence_id": f"CR_DECLARED_LICENSE_URL_{index:02d}",
                "authority": "Target named in current Crossref member-deposited licence metadata",
                "kind": "DECLARED_LICENSE_OR_TDM_POLICY_URL",
                "url": url,
                "captured_at_utc": captured_at,
                "receipt": receipt,
                "live": receipt["http_status"] is not None and 200 <= receipt["http_status"] < 400,
                "root_scope_verified": False,
                "interpretation": "URL liveness and bytes are evidence only; Crossref states licence URLs are not verified, and this audit did not open publisher body bytes.",
                "body_archived": False,
            }
        )

    evidence_snapshot = {
        "schema_version": "orion.provider-rights-history-successor.evidence.v1",
        "captured_at_utc": captured_at,
        "authority": "PUBLIC_POLICY_METADATA_AND_ARCHIVE_INDEX_EVIDENCE_ONLY",
        "outcomes_accessed": False,
        "protected_case_fields_accessed": False,
        "evidence_records": evidence_records,
        "internet_archive_queries": archive_queries,
        "crossref_history_counts": crossref_history_counts,
        "explicit_boundary": "No Internet Archive replay body, publisher article, dataset file, issue/comment, attachment, label, or outcome was fetched.",
    }
    evidence_snapshot["evidence_payload_sha256"] = sha256(canonical_bytes(evidence_snapshot))
    EVIDENCE_OUT.write_text(json.dumps(evidence_snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rights_counts: dict[str, int] = {}
    content_class_count = 0
    for root in root_ledger:
        for value in root["content_class_rights"].values():
            rights_counts[value["status"]] = rights_counts.get(value["status"], 0) + 1
            content_class_count += 1
    ledger = {
        "schema_version": "orion.provider-rights-history-successor.root-ledger.v1",
        "captured_at_utc": captured_at,
        "protocol_payload_sha256": proto["protocol_payload_sha256"],
        "parent_census_payload_sha256": census["snapshot_payload_sha256"],
        "evidence_payload_sha256": evidence_snapshot["evidence_payload_sha256"],
        "authority": "ROOT_BY_ROOT_RIGHTS_AND_HISTORY_PREFLIGHT_ONLY",
        "root_count": len(root_ledger),
        "content_class_cell_count": content_class_count,
        "rights_status_counts": dict(sorted(rights_counts.items())),
        "crossref_history_status_counts": {
            "CANNOT_CHECK_EXACT_CROSSREF_HISTORICAL_BYTES": sum(
                root["historical_byte_provenance"] is not None
                and root["historical_byte_provenance"]["status"] == "CANNOT_CHECK_EXACT_CROSSREF_HISTORICAL_BYTES"
                for root in root_ledger
            ),
            "EXACT_PRE_CUTOFF_BYTES": 0,
        },
        "roots": root_ledger,
        "scientific_terminal": "CANNOT_CHECK_RIGHTS_AND_HISTORY_BINDING",
        "case_eligibility_terminal": "METADATA_ROOT_ONLY__CASE_ELIGIBILITY_NOT_ASSESSED",
        "explicit_nonclaim": "A policy or licence preflight is not case eligibility, legal advice, cross-provider transport evidence, or a scientific result.",
    }
    ledger["ledger_payload_sha256"] = sha256(canonical_bytes(ledger))
    LEDGER_OUT.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    gap_ledger = {
        "schema_version": "orion.provider-rights-history-successor.gap-ledger.v1",
        "captured_at_utc": captured_at,
        "recursion_rule": "Every unresolved root/content-class or historical-byte cell retains its negative status and receives a narrower successor identity and discriminator; no missing evidence is converted to permission or positivity.",
        "gap_count": len(gaps),
        "gaps": gaps,
        "overall_terminal": "CANNOT_CHECK_RIGHTS_AND_HISTORY_BINDING",
    }
    gap_ledger["gap_ledger_payload_sha256"] = sha256(canonical_bytes(gap_ledger))
    GAPS_OUT.write_text(json.dumps(gap_ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "protocol": str(PROTOCOL_OUT),
                "evidence": str(EVIDENCE_OUT),
                "root_ledger": str(LEDGER_OUT),
                "gap_ledger": str(GAPS_OUT),
                "roots": len(root_ledger),
                "rights_status_counts": ledger["rights_status_counts"],
                "crossref_exact_pre_cutoff_bytes": 0,
                "crossref_history_cannot_check": 8,
                "successor_gap_count": len(gaps),
                "scientific_terminal": ledger["scientific_terminal"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
