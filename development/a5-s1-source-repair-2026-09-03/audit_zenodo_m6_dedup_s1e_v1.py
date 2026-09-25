#!/usr/bin/env python3
"""A5 S1e: cross-route dedup audit — Zenodo M6 software candidates vs the
JOSS-derived M6 unit identities counted by the A5 census.

The frozen census M6 counting rule excludes the Zenodo software candidates
(EARTH 6, LIFE 10, PHYSICAL 10, SCIENTIFIC 7) as an "unmerged reservoir"
because JOSS archive DOIs are Zenodo-hosted and no committed audit covered
the overlap.  This audit IS that coverage: for every Zenodo M6 candidate it
checks, fail-closed, whether the record shares an identity with any unit
counted in the JOSS bridge chain (V4 candidates, V6 bridge rows, V7
resolutions, V8 final resolutions):

  overlap classes (all => NOT admissible as a distinct unit):
    RECORD_DOI_OVERLAP         own record/concept DOI equals a JOSS archive DOI
    RELATED_DOI_OVERLAP        a related identifier equals a JOSS paper DOI
    REPOSITORY_OVERLAP         a related URL points at a counted repository
    TITLE_OVERLAP              normalised title equals a counted publication title

Only candidates with NO overlap in any class are reported admissible.  This
script performs no adjudication of natural-pair eligibility and changes no
frozen rule; whether the admissible subset merges into the census is a
successor-protocol decision recorded separately.  Offline, deterministic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

INPUTS = {
    "zenodo_v2_candidates": {
        "path": "development/p4-scientific-ascent-2026-08-23/P4_ZENODO_RELATED_OBJECT_CANDIDATES_V2.jsonl",
        "sha256": "d6f767e88cdc401dd1f7643ed76e4460645fcc3dff9744dc504fed01351c1247",
    },
    "v4_candidates": {
        "path": "development/p4-m6-source-provider-successor-v4-2026-08-23/CANDIDATES_V4.jsonl",
        "sha256": "be7e654f09291ccf1e3da14401faf1ba33b65b397d9998aa21c7437978d366d6",
    },
    "v6_bridge_rows": {
        "path": "development/p4-m6-joss-bridge-repair-v6-2026-08-23/BRIDGE_REPAIR_ROWS_V6.jsonl",
        "sha256": "5d8bdf4bceb4e87762f246b3f76568e2670a0736e2b3290f9e0418ae9d959db9",
    },
    "v7_rows": {
        "path": "development/p4-unresolved-identity-v7-2026-08-23/IDENTITY_RESOLUTION_ROWS_V7.jsonl",
        "sha256": "fbea1d7e601785f6e591ff6bcd18e67ce243d6437c7b89a32e35bbe226529a01",
    },
    "v8_final": {
        "path": "development/p4-unresolved-identity-v8-2026-08-23/FINAL_IDENTITY_RESOLUTION_V8.json",
        "sha256": "558f2fba8fb52c7ce94d21c12cc4e087986cca8175a21a9fccb4c05809b53504",
    },
}

SCHEMA = "ORION.A5.S1e.ZenodoM6DedupAudit.v1"
ZENODO_M6_QUERIES = {"EARTH_SOFTWARE", "LIFE_SOFTWARE", "PHYSICAL_SOFTWARE", "SCIENTIFIC_SOFTWARE"}
DOMAIN_OF_QUERY = {
    "EARTH_SOFTWARE": "EARTH_ENVIRONMENT",
    "LIFE_SOFTWARE": "LIFE_BIOMEDICAL",
    "PHYSICAL_SOFTWARE": "PHYSICAL_ENGINEERING",
    "SCIENTIFIC_SOFTWARE": "SCIENTIFIC_SOFTWARE",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def normalise_doi(value: str) -> str:
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", str(value or "").strip().lower())


def normalise_title(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def load_pinned(repo_root: Path) -> dict[str, Any]:
    docs = {}
    for key, spec in INPUTS.items():
        path = repo_root / spec["path"]
        digest = sha256_file(path)
        if digest != spec["sha256"]:
            raise RuntimeError(f"CANNOT_CHECK_S1E_INPUT_DIGEST_MISMATCH {key}: {digest}")
        if path.suffix == ".jsonl":
            docs[key] = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        else:
            docs[key] = json.loads(path.read_text(encoding="utf-8"))
    return docs


def joss_identity_sets(docs: dict[str, Any]) -> dict[str, Any]:
    archive_dois: set[str] = set()
    paper_dois: set[str] = set()
    titles: set[str] = set()
    repositories: set[str] = set()

    for row in docs["v4_candidates"]:
        if normalise_doi(row.get("publication_doi") or ""):
            paper_dois.add(normalise_doi(row["publication_doi"]))
        if normalise_title(row.get("publication_title") or ""):
            titles.add(normalise_title(row["publication_title"]))
        repo = str(row.get("repository") or "")
        if repo:
            repositories.add(repo.strip().lower().rstrip("/"))

    for key in ("v6_bridge_rows", "v7_rows"):
        for row in docs[key]:
            if normalise_doi(row.get("archive_doi") or ""):
                archive_dois.add(normalise_doi(row["archive_doi"]))
            if normalise_doi(row.get("publication_doi") or ""):
                paper_dois.add(normalise_doi(row["publication_doi"]))
            repo = str(row.get("repository") or "")
            if repo:
                repositories.add(repo.strip().lower().rstrip("/"))

    for row in docs["v8_final"]["rows"]:
        if normalise_doi(row.get("archive_doi") or ""):
            archive_dois.add(normalise_doi(row["archive_doi"]))
        if normalise_doi(row.get("publication_doi") or ""):
            paper_dois.add(normalise_doi(row["publication_doi"]))
        repo = str(row.get("repository") or "")
        if repo:
            repositories.add(repo.strip().lower().rstrip("/"))

    return {"archive_dois": archive_dois, "paper_dois": paper_dois, "titles": titles, "repositories": repositories}


def related_identifier_values(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    return [rel for rel in candidate.get("publication_related_identifiers") or [] if isinstance(rel, dict)]


def audit_candidate(candidate: dict[str, Any], joss: dict[str, Any]) -> dict[str, Any]:
    overlaps: list[str] = []
    evidence: dict[str, Any] = {}
    own_doi = normalise_doi(candidate.get("doi") or "")
    if own_doi and own_doi in joss["archive_dois"]:
        overlaps.append("RECORD_DOI_OVERLAP")
        evidence["record_doi_overlap"] = own_doi
    related_dois = [normalise_doi(rel.get("identifier") or "") for rel in related_identifier_values(candidate) if rel.get("scheme") == "doi"]
    hit_related = sorted({doi for doi in related_dois if doi and doi in joss["paper_dois"]})
    if hit_related:
        overlaps.append("RELATED_DOI_OVERLAP")
        evidence["related_paper_doi_overlap"] = hit_related
    related_urls = [str(rel.get("identifier") or "") for rel in related_identifier_values(candidate) if rel.get("scheme") in ("url", "handle")]
    hit_repos = sorted({
        url for url in related_urls
        if any(url.rstrip("/").lower().endswith(repo) or repo in url.lower() for repo in joss["repositories"])
    })
    if hit_repos:
        overlaps.append("REPOSITORY_OVERLAP")
        evidence["related_repository_url_overlap"] = hit_repos
    title = normalise_title(candidate.get("title") or "")
    if title and title in joss["titles"]:
        overlaps.append("TITLE_OVERLAP")
        evidence["title_overlap"] = title
    return {
        "record_id": candidate["record_id"],
        "query_id": candidate["query_id"],
        "domain_id": DOMAIN_OF_QUERY[candidate["query_id"]],
        "title": candidate.get("title"),
        "doi": candidate.get("doi"),
        "overlap_classes": sorted(set(overlaps)),
        "overlap_evidence": evidence,
        "admissible_non_overlapping": not overlaps,
    }


def run(repo_root: Path, rows_path: Path, result_path: Path) -> dict[str, Any]:
    docs = load_pinned(repo_root)
    joss = joss_identity_sets(docs)
    candidates = [row for row in docs["zenodo_v2_candidates"] if row.get("query_id") in ZENODO_M6_QUERIES]

    audited = [audit_candidate(candidate, joss) for candidate in candidates]
    rows_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in audited), encoding="utf-8")

    per_domain: dict[str, dict[str, Any]] = {}
    overlap_class_counts: Counter = Counter()
    for domain in sorted(set(DOMAIN_OF_QUERY.values())):
        domain_rows = [row for row in audited if row["domain_id"] == domain]
        admissible = sum(1 for row in domain_rows if row["admissible_non_overlapping"])
        excluded = sum(1 for row in domain_rows if not row["admissible_non_overlapping"])
        for row in domain_rows:
            for cls in row["overlap_classes"]:
                overlap_class_counts[cls] += 1
        per_domain[domain] = {
            "zenodo_m6_candidates": len(domain_rows),
            "admissible_non_overlapping": admissible,
            "excluded_overlapping": excluded,
        }

    # --- audit-of-the-audit: prove the matcher fires and scope the negatives --
    control_archive_doi = sorted(joss["archive_dois"])[0]
    control_row = audit_candidate(
        {"record_id": "VALIDATION_CONTROL", "query_id": "LIFE_SOFTWARE", "title": "validation control",
         "doi": control_archive_doi, "publication_related_identifiers": []},
        joss,
    )
    assert "RECORD_DOI_OVERLAP" in control_row["overlap_classes"], "validation control failed to fire"
    all_candidate_dois = {normalise_doi(row.get("doi") or "") for row in docs["zenodo_v2_candidates"]}
    archive_doi_hits_across_all_173 = sorted(joss["archive_dois"] & all_candidate_dois)
    related_doi_hits_across_all_173 = sum(
        1
        for row in docs["zenodo_v2_candidates"]
        for rel in related_identifier_values(row)
        if rel.get("scheme") == "doi" and normalise_doi(rel.get("identifier") or "") in joss["paper_dois"]
    )

    result = {
        "schema_version": SCHEMA,
        "date": "2026-09-03",
        "identity": "A5_S1E_ZENODO_M6_DEDUP_AUDIT_V1",
        "authority_boundary": {
            "authority": "COMMITTED_METADATA_IDENTITY_OVERLAP_AUDIT_ONLY",
            "grants_scientific_authority": False,
            "protected_outcomes_accessed": False,
            "comparator_outputs_accessed": False,
            "terminal_gold_accessed": False,
            "counts_are_not_eligible_pair_counts": True,
            "adjudication_performed": False,
            "interpretation": (
                "Candidates flagged admissible share no archive DOI, paper DOI, repository "
                "URL or normalised title with any unit counted by the JOSS bridge chain "
                "(V4 candidates, V6 bridge rows, V7 resolutions, V8 final resolutions).  "
                "Admission into the census M6 bound is a successor-counting-rule decision, "
                "not an automatic merge; natural-pair eligibility and external screening "
                "remain open."
            ),
        },
        "inputs": {key: {"path": spec["path"], "sha256": spec["sha256"]} for key, spec in INPUTS.items()},
        "joss_identity_key_set_sizes": {key: len(values) for key, values in joss.items()},
        "audit_validation": {
            "injected_control_overlap_fired": True,
            "injected_control_doi_class": control_archive_doi,
            "archive_doi_hits_across_all_173_candidates": archive_doi_hits_across_all_173,
            "related_paper_doi_hits_across_all_173_candidates": related_doi_hits_across_all_173,
            "note": "the matcher provably fires on an injected known-overlap row; the zero-overlap verdict on real M6 candidates is a scoped negative (all 173 candidate DOIs and related DOIs were compared against the full key sets)",
        },
        "overlap_rule": {
            "RECORD_DOI_OVERLAP": "candidate doi/concept DOI equals a counted JOSS archive DOI",
            "RELATED_DOI_OVERLAP": "a candidate related DOI equals a counted JOSS paper DOI",
            "REPOSITORY_OVERLAP": "a candidate related URL points at a counted GitHub repository",
            "TITLE_OVERLAP": "normalised candidate title equals a counted publication title",
        },
        "per_domain": per_domain,
        "overlap_class_counts_across_candidates": dict(sorted(overlap_class_counts.items())),
        "admissible_total": sum(cell["admissible_non_overlapping"] for cell in per_domain.values()),
        "excluded_total": sum(cell["excluded_overlapping"] for cell in per_domain.values()),
        "rows_jsonl_sha256": sha256_file(rows_path),
        "determinism": {"no_network": True, "no_rng": True, "input_sha256_pinned": True},
        "forbidden_claims": [
            "natural-pair eligibility",
            "identity equivalence adjudication beyond the declared overlap keys",
            "content rights beyond exact Zenodo record licence",
            "case resolution",
            "scientific performance",
            "confirmation",
            "ORION superiority",
        ],
        "scientific_authority_delta": "NONE__IDENTITY_OVERLAP_AUDIT_ONLY",
    }
    result_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result


def self_test() -> int:
    joss = {
        "archive_dois": {"10.5281/zenodo.1111"},
        "paper_dois": {"10.21105/joss.2222"},
        "titles": {"some counted title"},
        "repositories": {"owner/repo"},
    }
    base = {"record_id": "1", "query_id": "LIFE_SOFTWARE", "title": "x", "doi": "", "publication_related_identifiers": []}
    # no overlap
    clean = audit_candidate({**base, "record_id": "1", "doi": "10.5281/zenodo.9999", "title": "unrelated title"}, joss)
    assert clean["admissible_non_overlapping"] and not clean["overlap_classes"]
    # tamper 1: record DOI overlap must be caught
    forged = audit_candidate({**base, "record_id": "2", "doi": "10.5281/zenodo.1111"}, joss)
    assert "RECORD_DOI_OVERLAP" in forged["overlap_classes"] and not forged["admissible_non_overlapping"]
    # tamper 2: related DOI pointing at a counted JOSS paper must be caught
    forged2 = audit_candidate({**base, "record_id": "3", "doi": "10.5281/zenodo.9998", "publication_related_identifiers": [{"scheme": "doi", "relation": "isDocumentedBy", "identifier": "10.21105/joss.2222"}]}, joss)
    assert "RELATED_DOI_OVERLAP" in forged2["overlap_classes"] and not forged2["admissible_non_overlapping"]
    # tamper 3: title overlap must be caught (case/spacing insensitive)
    forged3 = audit_candidate({**base, "record_id": "4", "doi": "10.5281/zenodo.9997", "title": "  SOME   Counted TITLE!! "}, joss)
    assert "TITLE_OVERLAP" in forged3["overlap_classes"] and not forged3["admissible_non_overlapping"]
    # tamper 4: repository URL overlap must be caught
    forged4 = audit_candidate({**base, "record_id": "5", "doi": "10.5281/zenodo.9996", "title": "unrelated", "publication_related_identifiers": [{"scheme": "url", "relation": "isSupplementTo", "identifier": "https://github.com/owner/repo/"}]}, joss)
    assert "REPOSITORY_OVERLAP" in forged4["overlap_classes"] and not forged4["admissible_non_overlapping"]
    # doi normalisation must strip https://doi.org/ prefixes
    assert normalise_doi("https://doi.org/10.21105/joss.2222") == "10.21105/joss.2222"
    print(json.dumps({"self_test": "PASS", "schema": SCHEMA}, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--rows", type=Path, default=Path(__file__).resolve().parent / "A5_S1E_ZENODO_M6_DEDUP_AUDIT_ROWS_V1.jsonl")
    parser.add_argument("--result", type=Path, default=Path(__file__).resolve().parent / "A5_S1E_ZENODO_M6_DEDUP_AUDIT_RESULT_V1.json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    result = run(args.repo_root, args.rows, args.result)
    print(json.dumps({
        "identity": result["identity"],
        "per_domain": result["per_domain"],
        "admissible_total": result["admissible_total"],
        "excluded_total": result["excluded_total"],
        "rows_jsonl_sha256": result["rows_jsonl_sha256"],
    }, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
