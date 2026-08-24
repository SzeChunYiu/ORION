#!/usr/bin/env python3
"""Aggregate frozen structured-action fields without retaining case identities."""

from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import re
import threading
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/billy/Documents/Codex/2026-08-23/can-x20")
LANE = ROOT / "work/lane-handoffs/p1-structured-action-semantics-v3"
RUNTIME = ROOT / "work/scratch/p1-structured-action-semantics-v3/v2-reconstruct/.runtime"
INPUT = RUNTIME / "allowlisted_families_v2.json"
SEARCH_CACHE = RUNTIME / "epmc_search_cache_v2.json"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
UA = "orion-p1-structured-action-semantics-v3/1.0 (aggregate metadata; no content retention)"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def chunks(values, n: int):
    values = sorted(values, key=int)
    for i in range(0, len(values), n):
        yield values[i : i + n]


def get_bytes(url: str, retries: int = 5, timeout: int = 60) -> bytes:
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, application/xml;q=0.9"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except Exception as exc:
            last = exc
            time.sleep(min(12, 0.8 * 2**attempt))
    raise RuntimeError(f"request failed after {retries}: {type(last).__name__}: {last}")


def normalize_license(value) -> str:
    if not value:
        return "CANNOT_CHECK_MISSING_LICENSE"
    text = " ".join(str(value).upper().replace("_", "-").split())
    text = re.sub(r"[- ]+", " ", text).strip()
    tokens = text.split()
    if tokens == ["CC0"] or (len(tokens) == 2 and tokens[0] == "CC0" and re.fullmatch(r"\d+(?:\.\d+)?", tokens[1])):
        return "ALLOW_CC0"
    if len(tokens) in (2, 3) and tokens[:2] == ["CC", "BY"] and (len(tokens) == 2 or re.fullmatch(r"\d+(?:\.\d+)?", tokens[2])):
        return "ALLOW_CC_BY"
    if len(tokens) in (3, 4) and tokens[:3] == ["CC", "BY", "SA"] and (len(tokens) == 3 or re.fullmatch(r"\d+(?:\.\d+)?", tokens[3])):
        return "ALLOW_CC_BY_SA"
    if "NC" in tokens or "ND" in tokens:
        return "EXCLUDE_NC_OR_ND"
    return "CANNOT_CHECK_CUSTOM_OR_UNPARSED_LICENSE"


def query_epmc_core(batch: list[str]) -> tuple[dict, str, int]:
    identifiers = " OR ".join("EXT_ID:" + item for item in batch)
    query = f"({identifiers}) AND SRC:MED"
    url = EPMC + "?" + urllib.parse.urlencode(
        {"query": query, "resultType": "core", "format": "json", "pageSize": 1000, "synonym": "false", "cursorMark": "*"}
    )
    raw = get_bytes(url)
    payload = json.loads(raw)
    if str(payload.get("version")) != "6.9":
        raise RuntimeError("Europe PMC provider version drift")
    if int(payload.get("hitCount", 0)) > len(batch):
        raise RuntimeError("unexpected nonunique core hit count")
    records = {}
    for source in payload.get("resultList", {}).get("result", []):
        # Sole semantic gateway: no title, abstract, author, journal, keyword,
        # mesh, chemical, URL, citation, or full-text field is indexed.
        if source.get("source") != "MED":
            raise RuntimeError("unexpected Europe PMC source")
        identifier = str(source.get("id") or source.get("pmid") or "")
        if identifier not in batch:
            raise RuntimeError("identifier outside frozen batch")
        pub_types = source.get("pubTypeList", {}).get("pubType", [])
        corrections = source.get("commentCorrectionList", {}).get("commentCorrection", [])
        record = {
            "pmcid": source.get("pmcid"),
            "license": source.get("license"),
            "is_open_access": source.get("isOpenAccess"),
            "in_pmc": source.get("inPMC"),
            "pub_types": sorted({str(x) for x in pub_types if isinstance(x, str)}),
            "correction_types": sorted(
                {str(x.get("type")) for x in corrections if isinstance(x, dict) and x.get("type")}
            ),
            "correction_rows": len(corrections),
            "correction_rows_with_id": sum(1 for x in corrections if isinstance(x, dict) and x.get("id")),
        }
        if identifier in records:
            records[identifier] = {"duplicate": True}
        else:
            records[identifier] = record
    return records, hashlib.sha256(raw).hexdigest(), int(payload.get("hitCount", 0))


def parallel_epmc_core(pmids: set[str]) -> tuple[dict, list[str], int, int]:
    batches = list(chunks(pmids, 80))
    records = {}
    hashes = []
    hit_count = 0
    failures = []
    with cf.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(query_epmc_core, batch): batch for batch in batches}
        for future in cf.as_completed(futures):
            try:
                found, digest, hits = future.result()
            except Exception as exc:
                failures.append({"batch_size": len(futures[future]), "error": f"{type(exc).__name__}: {exc}"})
                continue
            records.update(found)
            hashes.append(digest)
            hit_count += hits
    if failures:
        raise RuntimeError(f"Europe PMC core failures: {failures[:3]} total={len(failures)}")
    return records, sorted(hashes), hit_count, len(batches)


class Limiter:
    def __init__(self, interval: float):
        self.interval = interval
        self.last = 0.0
        self.lock = threading.Lock()

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            delay = self.interval - (now - self.last)
            if delay > 0:
                time.sleep(delay)
            self.last = time.monotonic()


def query_pubmed(batch: list[str], limiter: Limiter) -> tuple[dict, str]:
    limiter.wait()
    url = EFETCH + "?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": ",".join(batch), "retmode": "xml", "rettype": "xml"}
    )
    raw = get_bytes(url)
    root = ET.fromstring(raw)
    records = {}
    for article in root.findall("PubmedArticle"):
        citation = article.find("MedlineCitation")
        if citation is None:
            continue
        identifier_node = citation.find("PMID")
        identifier = (identifier_node.text or "").strip() if identifier_node is not None else ""
        if identifier not in batch:
            raise RuntimeError("PubMed identifier outside frozen batch")
        # Sole XML gateway: only PublicationType and CommentsCorrections RefType
        # plus related PMID are materialized. RefSource, title, abstract, author,
        # journal, chemicals, headings, grants, and notes are never indexed.
        pub_types = sorted(
            {
                (node.text or "").strip()
                for node in citation.findall("Article/PublicationTypeList/PublicationType")
                if (node.text or "").strip()
            }
        )
        correction_nodes = citation.findall("CommentsCorrectionsList/CommentsCorrections")
        ref_types = sorted({str(node.get("RefType")) for node in correction_nodes if node.get("RefType")})
        related_pmid_count = sum(1 for node in correction_nodes if node.find("PMID") is not None and (node.findtext("PMID") or "").strip())
        if identifier in records:
            records[identifier] = {"duplicate": True}
        else:
            records[identifier] = {
                "pub_types": pub_types,
                "ref_types": ref_types,
                "correction_rows": len(correction_nodes),
                "correction_rows_with_pmid": related_pmid_count,
            }
    return records, hashlib.sha256(raw).hexdigest()


def parallel_pubmed(pmids: set[str]) -> tuple[dict, list[str], int]:
    batches = list(chunks(pmids, 200))
    limiter = Limiter(0.36)
    records = {}
    hashes = []
    failures = []
    with cf.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(query_pubmed, batch, limiter): batch for batch in batches}
        for future in cf.as_completed(futures):
            try:
                found, digest = future.result()
            except Exception as exc:
                failures.append({"batch_size": len(futures[future]), "error": f"{type(exc).__name__}: {exc}"})
                continue
            records.update(found)
            hashes.append(digest)
    if failures:
        raise RuntimeError(f"PubMed failures: {failures[:3]} total={len(failures)}")
    return records, sorted(hashes), len(batches)


def digest_multiset(values: list[str]) -> str:
    return hashlib.sha256(("\n".join(sorted(values)) + "\n").encode()).hexdigest()


def aggregate_record_tokens(records: dict, pub_key: str, relation_key: str) -> dict:
    pub = Counter()
    relation = Counter()
    correction_row_total = 0
    correction_rows_with_id = 0
    for record in records.values():
        if record.get("duplicate"):
            continue
        for value in record.get(pub_key, []):
            pub[value] += 1
        for value in record.get(relation_key, []):
            relation[value] += 1
        correction_row_total += record.get("correction_rows", 0)
        correction_rows_with_id += record.get("correction_rows_with_id", record.get("correction_rows_with_pmid", 0))
    return {
        "publication_type_record_frequencies": dict(sorted(pub.items())),
        "relation_type_record_frequencies": dict(sorted(relation.items())),
        "structured_relation_row_total": correction_row_total,
        "structured_relation_rows_with_related_identifier": correction_rows_with_id,
    }


def main() -> None:
    protocol = json.loads((LANE / "PROTOCOL_V3.json").read_text())
    parser_rules = json.loads((LANE / "PARSER_RULES_V3.json").read_text())
    freeze = json.loads((LANE / "PARSER_FREEZE_RECEIPT_V3.json").read_text())
    normalization = json.loads((LANE / "SOURCE_INTERFACE_NORMALIZATION_AMENDMENT_A_V3.json").read_text())
    normalization_freeze = json.loads(
        (LANE / "SOURCE_INTERFACE_NORMALIZATION_FREEZE_RECEIPT_A_V3.json").read_text()
    )
    initial_raw_census = json.loads((LANE / "PROVIDER_STRUCTURED_ACTION_CENSUS_RAW_INTERFACE_V3.json").read_text())
    assert freeze["parser_rules_sha256"] == sha(LANE / "PARSER_RULES_V3.json")
    assert normalization_freeze["amendment_sha256"] == sha(
        LANE / "SOURCE_INTERFACE_NORMALIZATION_AMENDMENT_A_V3.json"
    )
    assert normalization_freeze["raw_census_sha256"] == sha(
        LANE / "PROVIDER_STRUCTURED_ACTION_CENSUS_RAW_INTERFACE_V3.json"
    )
    assert protocol["inherited_pool"]["exact_rights_relations"] == 12038

    families = json.loads(INPUT.read_text())["families"]
    relations = []
    for family in families:
        for relation in family["relations"]:
            if relation["original"]["pmid"] and relation["notice"]["pmid"]:
                relations.append((family["family_key"], relation["original"]["pmid"][0], relation["notice"]["pmid"][0]))
    all_pmids = {value for _, original, notice in relations for value in (original, notice)}
    cache = json.loads(SEARCH_CACHE.read_text())
    hits = cache["allowlist_search_matches"]
    candidate_pmids = {identifier for identifier, pmcids in hits.items() if len(pmcids) == 1}

    epmc, epmc_hashes, epmc_hits, epmc_batches = parallel_epmc_core(candidate_pmids)
    allowed = {"ALLOW_CC0", "ALLOW_CC_BY", "ALLOW_CC_BY_SA"}
    rights_status = {}
    pmcids = {}
    license_counts = Counter()
    for identifier in candidate_pmids:
        record = epmc.get(identifier)
        if not record:
            rights_status[identifier] = "CANNOT_CHECK_CORE_ABSENCE"
            continue
        if record.get("duplicate"):
            rights_status[identifier] = "CANNOT_CHECK_MULTIPLE_CORE_ROWS"
            continue
        if not record.get("pmcid"):
            rights_status[identifier] = "CANNOT_CHECK_CORE_MISSING_PMCID"
            continue
        if str(record.get("is_open_access")).strip().casefold() not in {"y", "yes", "true", "1"}:
            rights_status[identifier] = "CANNOT_CHECK_CORE_OPEN_ACCESS_FLAG"
            continue
        if str(record.get("in_pmc")).strip().casefold() not in {"y", "yes", "true", "1"}:
            rights_status[identifier] = "CANNOT_CHECK_CORE_IN_PMC_FLAG"
            continue
        status = normalize_license(record.get("license"))
        rights_status[identifier] = status
        pmcids[identifier] = str(record.get("pmcid"))
        license_counts[status] += 1

    pass_relations = []
    relation_status = Counter()
    for family, original, notice in relations:
        if original not in rights_status or notice not in rights_status:
            relation_status["CANNOT_CHECK_EPMC_ALLOWLIST_SEARCH_ABSENCE"] += 1
        elif rights_status[original] not in allowed or rights_status[notice] not in allowed:
            relation_status["CANNOT_CHECK_OR_EXCLUDE_EXACT_LICENSE"] += 1
        elif pmcids.get(original) == pmcids.get(notice):
            relation_status["CANNOT_CHECK_EPMC_ENDPOINT_RESOLUTION_COLLISION"] += 1
        else:
            pass_relations.append((family, original, notice))
            relation_status["EXACT_BOTH_ENDPOINT_CONTENT_RIGHTS_PASS"] += 1

    if len(pass_relations) != protocol["inherited_pool"]["exact_rights_relations"]:
        raise RuntimeError(f"V2 exact relation reconstruction drift: {len(pass_relations)}")
    if len({family for family, _, _ in pass_relations}) != protocol["inherited_pool"]["exact_rights_families"]:
        raise RuntimeError("V2 exact family reconstruction drift")
    notice_pmids = {notice for _, _, notice in pass_relations}
    epmc_notices = {identifier: epmc[identifier] for identifier in notice_pmids if identifier in epmc}

    pubmed, pubmed_hashes, pubmed_batches = parallel_pubmed(notice_pmids)

    epmc_freq = aggregate_record_tokens(epmc_notices, "pub_types", "correction_types")
    pubmed_freq = aggregate_record_tokens(pubmed, "pub_types", "ref_types")

    epmc_pub_map = parser_rules["epmc_pub_type_exact"]
    ref_map = parser_rules["pubmed_ref_type_exact"]
    record_classes = Counter()
    relation_classes = Counter()
    ambiguous_records = 0
    no_class_records = 0
    for identifier in notice_pmids:
        record = epmc_notices.get(identifier, {})
        classes = {epmc_pub_map[value] for value in record.get("pub_types", []) if value in epmc_pub_map}
        classes |= {ref_map[value] for value in record.get("correction_types", []) if value in ref_map}
        if len(classes) == 1:
            record_classes[next(iter(classes))] += 1
        elif len(classes) > 1:
            ambiguous_records += 1
        else:
            no_class_records += 1
    for _, _, notice in pass_relations:
        record = epmc_notices.get(notice, {})
        classes = {epmc_pub_map[value] for value in record.get("pub_types", []) if value in epmc_pub_map}
        classes |= {ref_map[value] for value in record.get("correction_types", []) if value in ref_map}
        if len(classes) == 1:
            relation_classes[next(iter(classes))] += 1
        elif len(classes) > 1:
            relation_classes["AMBIGUOUS_MULTIPLE_STRATA"] += 1
        else:
            relation_classes["OTHER_OR_CANNOT_CHECK"] += 1

    comparable = 0
    exact_pub_type_sets = 0
    exact_relation_type_sets = 0
    normalized_exact_pub_type_sets = 0
    normalized_exact_relation_type_sets = 0
    epmc_added_jats_type_frequencies = Counter()
    epmc_added_jats_affected_records = 0
    unmapped_epmc_relation_type_frequencies = Counter()
    unmapped_epmc_relation_affected_records = 0
    normalized_pub_epmc_only = Counter()
    normalized_pub_pubmed_only = Counter()
    normalized_relation_epmc_only = Counter()
    normalized_relation_pubmed_only = Counter()
    epmc_relation_map = normalization["relation_type_normalization"]["epmc_display_to_pubmed_dtd_token"]
    epmc_added_jats_types = set(normalization["publication_type_normalization"]["epmc_added_jats_pmc_tokens"])
    for identifier in notice_pmids:
        left = epmc_notices.get(identifier)
        right = pubmed.get(identifier)
        if not left or not right or left.get("duplicate") or right.get("duplicate"):
            continue
        comparable += 1
        left_pub_raw = set(left["pub_types"])
        right_pub = set(right["pub_types"])
        left_relation_raw = set(left["correction_types"])
        right_relation = set(right["ref_types"])
        exact_pub_type_sets += left_pub_raw == right_pub
        exact_relation_type_sets += left_relation_raw == right_relation

        epmc_added = left_pub_raw & epmc_added_jats_types
        if epmc_added:
            epmc_added_jats_affected_records += 1
            epmc_added_jats_type_frequencies.update(epmc_added)
        left_pub_normalized = left_pub_raw - epmc_added_jats_types
        normalized_exact_pub_type_sets += left_pub_normalized == right_pub
        normalized_pub_epmc_only.update(left_pub_normalized - right_pub)
        normalized_pub_pubmed_only.update(right_pub - left_pub_normalized)

        unmapped = {value for value in left_relation_raw if value not in epmc_relation_map}
        if unmapped:
            unmapped_epmc_relation_affected_records += 1
            unmapped_epmc_relation_type_frequencies.update(unmapped)
        left_relation_normalized = {
            epmc_relation_map.get(value, f"EPMC_UNMAPPED::{value}") for value in left_relation_raw
        }
        normalized_exact_relation_type_sets += left_relation_normalized == right_relation
        normalized_relation_epmc_only.update(left_relation_normalized - right_relation)
        normalized_relation_pubmed_only.update(right_relation - left_relation_normalized)

    result = {
        "schema_version": "orion.p1.structured-action-semantics.provider-census.v3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "authority": protocol["authority"],
        "protocol_sha256": sha(LANE / "PROTOCOL_V3.json"),
        "parser_rules_sha256": sha(LANE / "PARSER_RULES_V3.json"),
        "v2_pool_reconstruction": {
            "admitted_relations": sum(len(f["relations"]) for f in families),
            "both_pmid_relations": len(relations),
            "unique_endpoint_pmids": len(all_pmids),
            "search_candidate_pmids": len(candidate_pmids),
            "exact_rights_relations": len(pass_relations),
            "exact_rights_families": len({family for family, _, _ in pass_relations}),
            "unique_notice_records": len(notice_pmids),
            "relation_status_counts": dict(sorted(relation_status.items())),
            "endpoint_license_status_counts": dict(sorted(license_counts.items())),
            "matches_v2_relations_and_families": True,
        },
        "epmc_core": {
            "provider_version": "6.9",
            "queried_candidate_pmids": len(candidate_pmids),
            "returned_records": len(epmc),
            "hit_count_sum": epmc_hits,
            "batch_count": epmc_batches,
            "response_sha256_multiset_digest": digest_multiset(epmc_hashes),
            "notice_records": len(epmc_notices),
            **epmc_freq,
        },
        "pubmed_efetch": {
            "queried_notice_pmids": len(notice_pmids),
            "returned_records": len(pubmed),
            "batch_count": pubmed_batches,
            "response_sha256_multiset_digest": digest_multiset(pubmed_hashes),
            **pubmed_freq,
        },
        "initial_raw_interface_comparison": {
            "artifact_path": "PROVIDER_STRUCTURED_ACTION_CENSUS_RAW_INTERFACE_V3.json",
            "artifact_sha256": sha(LANE / "PROVIDER_STRUCTURED_ACTION_CENSUS_RAW_INTERFACE_V3.json"),
            **initial_raw_census["cross_provider_structural_agreement"],
            "preservation": "Immutable first-pass interface-format failure; retained rather than silently overwritten.",
        },
        "cross_provider_structural_agreement": {
            "comparable_notice_records": comparable,
            "raw_exact_publication_type_set_matches_on_requery": exact_pub_type_sets,
            "raw_exact_relation_type_set_matches_on_requery": exact_relation_type_sets,
            "normalized_exact_publication_type_set_matches": normalized_exact_pub_type_sets,
            "normalized_exact_relation_type_set_matches": normalized_exact_relation_type_sets,
            "epmc_added_jats_pmc_publication_type_affected_records": epmc_added_jats_affected_records,
            "epmc_added_jats_pmc_publication_type_record_frequencies": dict(
                sorted(epmc_added_jats_type_frequencies.items())
            ),
            "unmapped_epmc_relation_type_affected_records": unmapped_epmc_relation_affected_records,
            "unmapped_epmc_relation_type_record_frequencies": dict(
                sorted(unmapped_epmc_relation_type_frequencies.items())
            ),
            "normalized_publication_type_epmc_only_token_frequencies": dict(sorted(normalized_pub_epmc_only.items())),
            "normalized_publication_type_pubmed_only_token_frequencies": dict(
                sorted(normalized_pub_pubmed_only.items())
            ),
            "normalized_relation_type_epmc_only_token_frequencies": dict(
                sorted(normalized_relation_epmc_only.items())
            ),
            "normalized_relation_type_pubmed_only_token_frequencies": dict(
                sorted(normalized_relation_pubmed_only.items())
            ),
            "normalization_amendment_sha256": sha(LANE / "SOURCE_INTERFACE_NORMALIZATION_AMENDMENT_A_V3.json"),
            "interpretation": "Agreement is metadata conformance only, not independent gold or owner semantics.",
        },
        "classified_structured_action_records": {
            "single_stratum_counts": dict(sorted(record_classes.items())),
            "ambiguous_multiple_strata": ambiguous_records,
            "other_or_cannot_check": no_class_records,
        },
        "classified_exact_rights_relations": dict(sorted(relation_classes.items())),
        "boundary": {
            "case_text_semantically_accessed": False,
            "title_abstract_author_journal_or_reason_fields_accessed": False,
            "raw_responses_persisted": False,
            "identifier_or_record_pairings_retained_in_result": False,
            "scientific_action_gold_assigned": 0,
            "owner_algebra_fields_assigned": 0,
            "model_or_comparator_executed": False,
            "protected_outcomes_accessed": False,
        },
    }
    (LANE / "PROVIDER_STRUCTURED_ACTION_CENSUS_V3.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "exact_rights_relations": len(pass_relations),
                "exact_rights_families": len({family for family, _, _ in pass_relations}),
                "notice_records": len(notice_pmids),
                "record_classes": dict(record_classes),
                "relation_classes": dict(relation_classes),
                "comparable": comparable,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
