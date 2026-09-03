#!/usr/bin/env python3
"""R2 PROSPECTIVE harvest: PMC Open Access subset linked records for M3/M4/M8.

Route R2_PMC_OA_LINKED_RECORDS (P4_NATURAL_PAIR_SOURCE_EXPANSION_FREEZE_V1.json):
content gate = "OA-package article-level licence plus separately enumerated linked
correction/protocol/supplement licence and byte hashes".

Interfaces (all official NCBI / PMC):
  - E-utilities esearch (db=pmc) for candidate discovery
  - PMC OAI-PMH v1 (https://pmc.ncbi.nlm.nih.gov/api/oai/v1/mh/) GetRecord /
    ListRecords with set=pmc-open for authoritative per-record licence
    (<ali:license_ref>) and typed <related-article> links
  - PMC article-instance binary endpoint for supplementary-file byte hashes

Network discipline: serial, one request in flight, >= 1.5 s between request
starts (NCBI published limit is 3 req/s; we run well under), retries with
backoff, every attempt appended to an access log. PROSPECTIVE harvesting only:
this script records identities, licences, typed relations and byte hashes. It
performs NO eligibility adjudication, NO pair adjudication, and accesses no
protected outcomes. It grants no scientific authority.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

MIN_INTERVAL_SECONDS = 1.5
RETRIES = 3
TIMEOUT_SECONDS = 90.0
USER_AGENT = "ORION-P4-A5-pmc-oa-linked-harvest-v1/1.0 (research source binding; https://github.com/SzeChunYiu/ORION)"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
OAI = "https://pmc.ncbi.nlm.nih.gov/api/oai/v1/mh/"
BIN_BASE = "https://pmc.ncbi.nlm.nih.gov/articles/instance"

RIGHTS_CLASS_RE = [
    (re.compile(r"creativecommons\.org/licenses/by/4\.0"), "CC_BY_40"),
    (re.compile(r"creativecommons\.org/licenses/by/3\.0"), "CC_BY_30"),
    (re.compile(r"creativecommons\.org/publicdomain/zero/1\.0"), "CC0_10"),
    (re.compile(r"creativecommons\.org/licenses/by-nc/4\.0"), "CC_BY_NC_40"),
    (re.compile(r"creativecommons\.org/licenses/by-nc-nd/4\.0"), "CC_BY_NC_ND_40"),
    (re.compile(r"creativecommons\.org/licenses/by-nc-sa/4\.0"), "CC_BY_NC_SA_40"),
    (re.compile(r"creativecommons\.org/licenses/by-sa/4\.0"), "CC_BY_SA_40"),
    (re.compile(r"creativecommons\.org/licenses/by/"), "CC_BY_OTHER"),
    (re.compile(r"creativecommons\.org/"), "CC_OTHER"),
]


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Fetcher:
    """Serial fetcher with interval enforcement and append-only access log."""

    def __init__(self, log_path: Path, interval: float = MIN_INTERVAL_SECONDS) -> None:
        self.log_path = log_path
        self.interval = interval
        self.last_request_at = 0.0
        self.requests = 0
        self._fh = log_path.open("a", encoding="utf-8")

    def _log(self, record: dict[str, Any]) -> None:
        self._fh.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
        self._fh.flush()

    def get(self, url: str, context: dict[str, Any] | None = None, timeout: float = TIMEOUT_SECONDS, expect_max_bytes: int = 256 * 1024 * 1024) -> tuple[bytes, int, str]:
        last: Exception | None = None
        for attempt in range(1, RETRIES + 1):
            delay = self.interval - (time.monotonic() - self.last_request_at)
            if delay > 0:
                time.sleep(delay)
            started_utc = utc_now()
            self.last_request_at = time.monotonic()
            self.requests += 1
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    status = getattr(response, "status", 200)
                    if status != 200:
                        raise RuntimeError(f"HTTP {status}")
                    data = response.read(expect_max_bytes + 1)
                    if len(data) > expect_max_bytes:
                        raise ValueError(f"response exceeds {expect_max_bytes} bytes")
                    self._log({"ts_utc": utc_now(), "event": "http_attempt", "request_started_utc": started_utc, "url": url, "http_status": status, "final_url": response.geturl(), "bytes": len(data), "sha256": sha256_bytes(data), "outcome": "OK", **(context or {})})
                    return data, status, response.geturl()
            except urllib.error.HTTPError as exc:
                last = exc
                body = b""
                try:
                    body = exc.read(2048)
                except Exception:
                    pass
                self._log({"ts_utc": utc_now(), "event": "http_attempt", "request_started_utc": started_utc, "url": url, "http_status": exc.code, "outcome": "FAILED" if attempt == RETRIES else "RETRY", "error": f"HTTPError {exc.code}: {body[:300]!r}", **(context or {})})
                if exc.code in (400, 401, 403, 404, 410):
                    raise  # non-retryable for our purposes
            except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, OSError) as exc:
                last = exc
                self._log({"ts_utc": utc_now(), "event": "http_attempt", "request_started_utc": started_utc, "url": url, "outcome": "FAILED" if attempt == RETRIES else "RETRY", "error": f"{type(exc).__name__}: {str(exc)[:300]}", **(context or {})})
            if attempt < RETRIES:
                time.sleep(self.interval * 2 * attempt)
        raise RuntimeError(f"failed after {RETRIES} attempts: {url}: {last}")

    def close(self) -> None:
        self._fh.close()


def rights_class(license_urls: list[str]) -> str:
    if not license_urls:
        return "NONE_DECLARED"
    classes = set()
    for url in license_urls:
        hit = "OTHER"
        for rx, cls in RIGHTS_CLASS_RE:
            if rx.search(url):
                hit = cls
                break
        classes.add(hit)
    if classes == {"CC_BY_40"}:
        return "CC_BY_40"
    if "CC0_10" in classes:
        return "CC0_10"
    if "CC_BY_30" in classes or "CC_BY_OTHER" in classes:
        return "CC_BY_NON40"
    return "||".join(sorted(classes))


def parse_record(xml: str) -> dict[str, Any] | None:
    """Parse one OAI record (pmc_fm or pmc) into identity/licence/relation dict."""
    h = re.search(r"<header>(.*?)</header>", xml, re.S)
    if not h:
        return None
    header = h.group(1)
    identifier = re.search(r"<identifier>([^<]+)</identifier>", header)
    if not identifier:
        return None
    sets = re.findall(r"<setSpec>([^<]+)</setSpec>", header)
    datestamp = re.search(r"<datestamp>([^<]+)</datestamp>", header)
    pmcid = identifier.group(1).rsplit(":", 1)[-1]
    article_types = re.findall(r'article-type="([a-zA-Z\-]+)"', xml)
    titles = re.findall(r"<article-title>(.*?)</article-title>", xml, re.S)
    title = re.sub(r"<[^>]+>", "", titles[0]).strip() if titles else None
    pmids = re.findall(r'<article-id pub-id-type="pmid">([^<]+)</article-id>', xml)
    dois = re.findall(r'<article-id pub-id-type="doi">([^<]+)</article-id>', xml)
    pmcaid = re.findall(r'<article-id pub-id-type="pmcaid">([^<]+)</article-id>', xml)
    lic_refs = re.findall(r"<ali:license_ref[^>]*>([^<]+)</ali:license_ref>", xml)
    lic_meta = re.findall(r"<ali:license_ref([^>]*)>", xml)
    related = []
    for tag in re.findall(r"<related-article[^>]*>", xml):
        rtype = re.search(r'related-article-type="([^"]+)"', tag)
        href = re.search(r'xlink:href="([^"]+)"', tag)
        rtitle = re.search(r'xlink:title="([^"]+)"', tag)
        related.append({"related_article_type": rtype.group(1) if rtype else None, "href": href.group(1) if href else None, "href_title": rtitle.group(1) if rtitle else None})
    trial_regs = re.findall(r'<article-id pub-id-type="trialregistry">([^<]+)</article-id>', xml)
    journal = re.findall(r"<journal-title>([^<]+)</journal-title>", xml)
    return {
        "oai_identifier": identifier.group(1),
        "pmcid": f"PMC{pmcid}" if not pmcid.startswith("PMC") else pmcid,
        "pmcaid": pmcaid[0] if pmcaid else None,
        "datestamp": datestamp.group(1) if datestamp else None,
        "oa_subset_member": "pmc-open" in sets,
        "sets": sets,
        "article_type": article_types[0] if article_types else None,
        "title": title,
        "pmid": pmids[0] if pmids else None,
        "doi": dois[0] if dois else None,
        "journal": journal[0] if journal else None,
        "license_urls": lic_refs,
        "license_ref_attrs": lic_meta,
        "rights_class": rights_class(lic_refs),
        "related_articles": related,
        "trial_registry_ids": trial_regs,
    }


def safe_get_record(fetcher: Fetcher, pmcid_num: str, prefix: str = "pmc_fm") -> dict[str, Any] | dict[str, str] | None:
    """GetRecord that never raises: returns a CANNOT_CHECK row on transport errors."""
    if not str(pmcid_num).isdigit():
        return {"pmcid_num": pmcid_num, "status": "NON_NUMERIC_DISCOVERY_ID_SKIPPED"}
    try:
        return get_record(fetcher, pmcid_num, prefix)
    except Exception as exc:
        return {"pmcid_num": pmcid_num, "status": "GET_RECORD_CANNOT_CHECK", "reason": f"{type(exc).__name__}: {str(exc)[:300]}"}


def get_record(fetcher: Fetcher, pmcid_num: str, prefix: str = "pmc_fm") -> dict[str, Any] | None:
    ident = urllib.parse.quote(f"oai:pubmedcentral.nih.gov:{pmcid_num}", safe=":")
    url = f"{OAI}?verb=GetRecord&identifier={ident}&metadataPrefix={prefix}"
    data, _, _ = fetcher.get(url, context={"phase": "get_record", "pmcid_num": pmcid_num, "prefix": prefix})
    xml = data.decode("utf-8", "replace")
    if "<error code=" in xml:
        return None
    rec = parse_record(xml)
    if rec:
        rec["nxml_sha256"] = sha256_bytes(data)
    return rec


def esearch_pmcids(fetcher: Fetcher, term: str, retmax: int) -> list[str]:
    url = f"{EUTILS}?db=pmc&retmode=json&sort=date&retmax={retmax}&term={urllib.parse.quote(term, safe='[]')}"
    data, _, _ = fetcher.get(url, context={"phase": "esearch", "term": term})
    js = json.loads(data.decode("utf-8"))
    return js.get("esearchresult", {}).get("idlist", [])


def harvest_m4(fetcher: Fetcher, out: Path, retmax: int) -> dict[str, Any]:
    term = '("erratum"[Title] OR "corrigendum"[Title] OR "correction"[Title]) AND "open access"[filter]'
    ids = esearch_pmcids(fetcher, term, retmax)
    rows: list[dict[str, Any]] = []
    with out.open("w", encoding="utf-8") as fh:
        def emit(row: dict[str, Any]) -> None:
            rows.append(row)
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
            fh.flush()
        partner_fetches = 0
        for pid in ids:
            rec = safe_get_record(fetcher, pid)
            if rec is None or rec.get("status") in ("GET_RECORD_CANNOT_CHECK", "NON_NUMERIC_DISCOVERY_ID_SKIPPED"):
                emit(rec or {"pmcid_num": pid, "status": "GET_RECORD_UNAVAILABLE"})
                continue
            corrected = [r for r in rec["related_articles"] if r["related_article_type"] in ("corrected-article", "corrected-and-republished-article")]
            row = {"mechanism": "M4_ARTICLE_TO_CORRECTION", "candidate_role": "CORRECTION_RECORD", "status": "PROSPECTIVE_LINKED_RECORD_HARVESTED", **{k: v for k, v in rec.items() if k != "related_articles"}, "related_articles": rec["related_articles"]}
            if rec["article_type"] == "correction" and corrected and rec["oa_subset_member"]:
                partner_pmcid = (corrected[0].get("href") or "").replace("PMC", "")
                if partner_pmcid and partner_fetches < 400:
                    partner_fetches += 1
                    prec = safe_get_record(fetcher, partner_pmcid)
                    if prec is not None and prec.get("status") not in ("GET_RECORD_CANNOT_CHECK", "NON_NUMERIC_DISCOVERY_ID_SKIPPED"):
                        row["partner"] = {k: v for k, v in prec.items() if k != "related_articles"}
                        row["pair_status"] = "BOTH_SIDES_HARVESTED_WITH_LICENCE" if prec["oa_subset_member"] and prec["license_urls"] else "PARTNER_OA_OR_LICENCE_MISSING"
                    else:
                        row["pair_status"] = "PARTNER_GET_RECORD_UNAVAILABLE"
                        if prec is not None and prec.get("reason"):
                            row["partner_error"] = prec["reason"]
                else:
                    row["pair_status"] = "PARTNER_ID_MISSING_FROM_RELATED_ARTICLE"
            else:
                row["pair_status"] = "NOT_A_TYPED_CORRECTION_RECORD_OR_NOT_OA"
            emit(row)
    both = [r for r in rows if r.get("pair_status") == "BOTH_SIDES_HARVESTED_WITH_LICENCE"]
    return {"discovered_n": len(ids), "harvested_n": len([r for r in rows if r.get("status") == "PROSPECTIVE_LINKED_RECORD_HARVESTED"]), "both_sides_with_licence_n": len(both), "both_sides_cc_by40_n": len([r for r in both if r["rights_class"] == "CC_BY_40" and r["partner"]["rights_class"] == "CC_BY_40"]), "term": term}


def harvest_m3(fetcher: Fetcher, out: Path, retmax: int) -> dict[str, Any]:
    term = '(protocol[Title]) AND "open access"[filter]'
    ids = esearch_pmcids(fetcher, term, retmax)
    rows: list[dict[str, Any]] = []
    with out.open("w", encoding="utf-8") as fh:
        def emit(row: dict[str, Any]) -> None:
            rows.append(row)
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
            fh.flush()
        partner_fetches = 0
        for pid in ids:
            rec = safe_get_record(fetcher, pid)
            if rec is None or rec.get("status") in ("GET_RECORD_CANNOT_CHECK", "NON_NUMERIC_DISCOVERY_ID_SKIPPED"):
                emit(rec or {"pmcid_num": pid, "status": "GET_RECORD_UNAVAILABLE"})
                continue
            row = {"mechanism": "M3_PROTOCOL_TO_RESULTS", "candidate_role": "PROTOCOL_RECORD", "status": "PROSPECTIVE_LINKED_RECORD_HARVESTED", **{k: v for k, v in rec.items() if k != "related_articles"}, "related_articles": rec["related_articles"]}
            linked_results = [r for r in rec["related_articles"] if r.get("href_title") in ("research-article", "article") or (r.get("related_article_type") or "") in ("commentary", "companion", "corrected-article")]
            if rec["oa_subset_member"] and rec["license_urls"] and (linked_results or rec["trial_registry_ids"]):
                partner = None
                if linked_results and partner_fetches < 250:
                    href = linked_results[0].get("href") or ""
                    pnum = href.replace("PMC", "")
                    if pnum:
                        partner_fetches += 1
                        partner = safe_get_record(fetcher, pnum)
                        if partner is not None and partner.get("status") in ("GET_RECORD_CANNOT_CHECK", "NON_NUMERIC_DISCOVERY_ID_SKIPPED"):
                            partner = None
                if partner is not None:
                    row["partner"] = {k: v for k, v in partner.items() if k != "related_articles"}
                    row["pair_status"] = "BOTH_SIDES_HARVESTED_WITH_LICENCE" if partner["oa_subset_member"] and partner["license_urls"] else "PARTNER_OA_OR_LICENCE_MISSING"
                else:
                    row["pair_status"] = "PROSPECTIVE_SINGLETON_WITH_REGISTRY_OR_RELATION_KEY"
            else:
                row["pair_status"] = "LICENCE_OR_LINKAGE_KEY_MISSING"
            emit(row)
    both = [r for r in rows if r.get("pair_status") == "BOTH_SIDES_HARVESTED_WITH_LICENCE"]
    return {"discovered_n": len(ids), "harvested_n": len([r for r in rows if r.get("status") == "PROSPECTIVE_LINKED_RECORD_HARVESTED"]), "both_sides_with_licence_n": len(both), "singleton_with_key_n": len([r for r in rows if r.get("pair_status") == "PROSPECTIVE_SINGLETON_WITH_REGISTRY_OR_RELATION_KEY"]), "both_sides_cc_by40_n": len([r for r in both if r["rights_class"] == "CC_BY_40" and r["partner"]["rights_class"] == "CC_BY_40"]), "term": term}


def harvest_m8(fetcher: Fetcher, out: Path, bytes_dir: Path, sample_from: str, cap_articles: int, cap_files: int) -> dict[str, Any]:
    """Recent pmc-open research articles -> full NXML -> supplementary-material byte hashes."""
    rows: list[dict[str, Any]] = []
    listed = 0
    token = None
    candidates: list[str] = []
    resumption = None
    from_date = sample_from
    while listed < 400 and len(candidates) < cap_articles:
        url = f"{OAI}?verb=ListRecords&set=pmc-open&metadataPrefix=pmc_fm&from={from_date}"
        if token:
            url = f"{OAI}?verb=ListRecords&resumptionToken={urllib.parse.quote(token)}"
        data, _, _ = fetcher.get(url, context={"phase": "list_records_m8_discovery"})
        xml = data.decode("utf-8", "replace")
        for chunk in re.findall(r"<record>.*?</record>", xml, re.S):
            listed += 1
            rec = parse_record(chunk)
            if rec and rec["article_type"] == "research-article" and rec["rights_class"] == "CC_BY_40":
                candidates.append(rec["pmcid"].replace("PMC", ""))
                if len(candidates) >= cap_articles:
                    break
        m = re.search(r"<resumptionToken[^>]*>([^<]+)</resumptionToken>", xml)
        token = m.group(1).strip() if m and m.group(1).strip() else None
        if not token:
            break
    files_fetched = 0
    for pnum in candidates:
        ident = urllib.parse.quote(f"oai:pubmedcentral.nih.gov:{pnum}", safe=":")
        full_bytes, _, _ = fetcher.get(f"{OAI}?verb=GetRecord&identifier={ident}&metadataPrefix=pmc", context={"phase": "get_record_full", "pmcid_num": pnum}, expect_max_bytes=256 * 1024 * 1024)
        full = full_bytes.decode("utf-8", "replace")
        if "<error code=" in full:
            continue
        rec = parse_record(full)
        if rec is None:
            continue
        rec["nxml_sha256"] = sha256_bytes(full_bytes)
        row = {"mechanism": "M8_ARTICLE_TO_LICENSED_SUPPLEMENT", "candidate_role": "ARTICLE_WITH_SUPPLEMENTS", "status": "PROSPECTIVE_LINKED_RECORD_HARVESTED", **{k: v for k, v in rec.items() if k != "related_articles"}}
        media = re.findall(r'<media[^>]*xlink:href="([^"]+)"[^>]*/?>', full) or re.findall(r'<self-uri[^>]*content-type="supplement"[^>]*xlink:href="([^"]+)"', full)
        sup_count = len(re.findall(r"<supplementary-material[ >]", full))
        row["supplementary_material_elements_n"] = sup_count
        row["supplement_files"] = []
        if rec.get("pmcaid"):
            for name in media[:3]:
                if files_fetched >= cap_files:
                    break
                furl = f"{BIN_BASE}/{rec['pmcaid']}/bin/{urllib.parse.quote(name)}"
                try:
                    fdata, status, final = fetcher.get(furl, context={"phase": "supplement_bytes", "pmcid": rec["pmcid"], "file": name}, expect_max_bytes=512 * 1024 * 1024)
                    files_fetched += 1
                    rel = f"bin/{rec['pmcid']}__{name}"
                    dest = bytes_dir / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(fdata)
                    row["supplement_files"].append({"file": name, "url": furl, "http_status": status, "bytes": len(fdata), "sha256": sha256_bytes(fdata), "bytes_relpath": rel, "licence_basis": "article-level PMC OA package licence (see license_urls); separately hashed file"})
                except Exception as exc:
                    row["supplement_files"].append({"file": name, "url": furl, "error": f"{type(exc).__name__}: {str(exc)[:200]}", "licence_basis": "byte hash unavailable"})
        rows.append(row)
    _write_jsonl(out, rows)
    with_sup = [r for r in rows if r.get("supplementary_material_elements_n", 0) > 0]
    return {"scanned_n": len(rows), "articles_with_supplementary_material_n": len(with_sup), "supplement_files_hashed_n": sum(len([f for f in r.get("supplement_files", []) if f.get("sha256")]) for r in rows), "from_date": from_date}


def snapshot_policies(fetcher: Fetcher, dirp: Path) -> list[dict[str, Any]]:
    dirp.mkdir(parents=True, exist_ok=True)
    targets = [
        ("pmc_oai_identify_2026-09-03.xml", f"{OAI}?verb=Identify"),
        ("pmc_oai_listsets_head_2026-09-03.xml", f"{OAI}?verb=ListSets"),
        ("ncbi_eutils_docs_2026-09-03.html", "https://www.ncbi.nlm.nih.gov/books/NBK25497/"),
        ("pmc_oa_tool_page_2026-09-03.html", "https://pmc.ncbi.nlm.nih.gov/tools/oa/"),
    ]
    manifest = []
    for name, url in targets:
        try:
            data, status, final = fetcher.get(url, context={"phase": "policy_snapshot", "target": name})
            (dirp / name).write_bytes(data)
            manifest.append({"file": name, "url": url, "final_url": final, "http_status": status, "bytes": len(data), "sha256": sha256_bytes(data)})
        except Exception as exc:
            manifest.append({"file": name, "url": url, "error": f"{type(exc).__name__}: {str(exc)[:200]}"})
    (dirp / "SNAPSHOT_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")


def main() -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=here)
    ap.add_argument("--bytes-dir", type=Path, required=True)
    ap.add_argument("--run-host", default="unknown")
    ap.add_argument("--m4-retmax", type=int, default=300)
    ap.add_argument("--m3-retmax", type=int, default=250)
    ap.add_argument("--m8-cap-articles", type=int, default=45)
    ap.add_argument("--m8-cap-files", type=int, default=40)
    ap.add_argument("--m8-from", default="2026-08-28")
    ap.add_argument("--skip-m4", action="store_true")
    ap.add_argument("--skip-m3", action="store_true")
    ap.add_argument("--skip-m8", action="store_true")
    ap.add_argument("--skip-policies", action="store_true")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher(args.out_dir / "ACCESS_LOG_V1.jsonl")
    started = utc_now()
    policies: list[dict[str, Any]] = []
    try:
        if not args.skip_policies:
            policies = snapshot_policies(fetcher, args.out_dir / "policy_snapshots")
        m4 = None if args.skip_m4 else harvest_m4(fetcher, args.out_dir / "CANDIDATES_M4_ARTICLE_TO_CORRECTION.jsonl", args.m4_retmax)
        m3 = None if args.skip_m3 else harvest_m3(fetcher, args.out_dir / "CANDIDATES_M3_PROTOCOL_TO_RESULTS.jsonl", args.m3_retmax)
        m8 = None if args.skip_m8 else harvest_m8(fetcher, args.out_dir / "CANDIDATES_M8_ARTICLE_TO_LICENSED_SUPPLEMENT.jsonl", args.bytes_dir, args.m8_from, args.m8_cap_articles, args.m8_cap_files)
    finally:
        fetcher.close()
    script_sha = sha256_bytes(Path(__file__).read_bytes())
    result = {
        "schema": "ORION.A5.PmcOaLinkedHarvest.v1",
        "route_id": "R2_PMC_OA_LINKED_RECORDS",
        "status": "PROSPECTIVE_HARVEST_EXECUTED",
        "run_provenance": {"run_host": args.run_host, "started_utc": started, "finished_utc": utc_now(), "script_sha256": script_sha, "http_requests": fetcher.requests},
        "network_policy": {"maximum_concurrency": 1, "minimum_request_interval_seconds": MIN_INTERVAL_SECONDS, "retries": RETRIES, "timeout_seconds": TIMEOUT_SECONDS, "providers": ["eutils.ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov"], "bytes_note": "supplement file bytes stored outside repository at --bytes-dir; NOT committed"},
        "policy_snapshots": policies,
        "m4_article_to_correction": m4,
        "m3_protocol_to_results": m3,
        "m8_article_to_licensed_supplement": m8,
        "interpretation_boundary": {
            "prospective_only": True,
            "case_eligibility_adjudicated": False,
            "route_specific_pair_adjudication_performed": False,
            "mechanism_counts_are_harvest_counts_not_eligible_pair_counts": True,
            "rights_recorded_per_record": "ali:license_ref per OAI record; supplement files hashed individually; no content rights inferred from metadata alone",
            "grants_scientific_authority": False,
            "protected_orion_predictions_accessed": False,
            "external_gold_accessed": False,
        },
    }
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    (args.out_dir / "RESULT_V1.json").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
