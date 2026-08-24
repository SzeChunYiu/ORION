#!/usr/bin/env python3
"""Receipt, JSON, checksum and scientific-boundary verification for P4 M6 V4."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
CHECKOUT = Path("/Users/billy/Documents/Codex/2026-08-23/can-x20/work/orion-takeover")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text())


failures: list[str] = []
protocol = load(ROOT / "PROTOCOL_V4.json")
freeze = load(ROOT / "PROTOCOL_FREEZE_RECEIPT_V4.json")
transport = load(ROOT / "TRANSPORT_LOG_V4.json")
cell_counts = load(ROOT / "CELL_COUNTS_V4.json")
audit = load(ROOT / "RIGHTS_RELATION_TRANSPORT_AUDIT_V4.json")
ledger = load(ROOT / "NEGATIVE_RESULT_LEDGER_V4.json")
result = load(ROOT / "RESULT_V4.json")
crossref = load(ROOT / "CROSSREF_PAGE_V4.json")
strict = load(ROOT / "STRICT_CANDIDATES_V4.json")
rows = [json.loads(line) for line in (ROOT / "CANDIDATES_V4.jsonl").read_text().splitlines() if line]

top_level_json = sorted(ROOT.glob("*.json"))
for path in top_level_json:
    try:
        load(path)
    except Exception as exc:
        failures.append(f"JSON_PARSE:{path.name}:{exc}")

if freeze["protocol_json_sha256"] != digest(ROOT / "PROTOCOL_V4.json"):
    failures.append("FREEZE_PROTOCOL_JSON_HASH")
if freeze["protocol_markdown_sha256"] != digest(ROOT / "PROTOCOL_V4.md"):
    failures.append("FREEZE_PROTOCOL_MD_HASH")
if freeze.get("outcomes_accessed") or freeze.get("protected_data_accessed"):
    failures.append("FREEZE_AUTHORITY_BOUNDARY")

predecessor_hashes = {
    "development/p4-source-universe-successor-v3-2026-08-23/PROTOCOL_V1.json": "441d4f05a0efaab0ada32c12e0f0841a3997a41c6acc95e9b3c8ce32e15c64c9",
    "development/p4-source-universe-successor-v3-2026-08-23/RESULT_V1.json": "3e556f15a0c872b3bbf8236227e6546ed14b3166979f343b071edb50cdb36a66",
    "development/p4-source-universe-successor-v3-2026-08-23/TRANSPORT_AUDIT_V1.json": "5b3fc744af13048d0c6cfd0366aa1e052ea63d01e5240f0e23706933dfe98582",
}
for rel, expected in predecessor_hashes.items():
    if digest(CHECKOUT / rel) != expected:
        failures.append("PREDECESSOR_HASH:" + rel)

if len(rows) != 200 or len({r.get("publication_doi") for r in rows}) != 200:
    failures.append("FROZEN_200_PUBLICATION_FRAME")
if len((crossref.get("message") or {}).get("items") or []) != 200:
    failures.append("CROSSREF_ROW_COUNT")
if transport["candidate_sha256"] != digest(ROOT / "CANDIDATES_V4.jsonl"):
    failures.append("CANDIDATE_SHA")

qualified = [r for r in rows if r.get("strict_eligible")]
if len(qualified) != 80 or strict != qualified:
    failures.append("PROVIDER_QUALIFIED_PROJECTION")
if len({r["publication_doi"] for r in qualified}) != len(qualified):
    failures.append("QUALIFIED_PUBLICATION_DEDUP")
if len({r["repository"]["full_name"].casefold() for r in qualified}) != len(qualified):
    failures.append("QUALIFIED_REPOSITORY_DEDUP")

accepted = set(protocol["strict_candidate_unit"]["accepted_spdx"])
for row in qualified:
    checks = [
        (row["joss_relation"]["relation_status"] == "PASS", "RELATION"),
        (row["repository"]["private"] is False and row["repository"]["visibility"] == "public", "PUBLIC_REPO"),
        (not row["repository"]["archived"] and not row["repository"]["disabled"], "ACTIVE_REPO"),
        (bool(row.get("release")) and str(row["release"]["tarball_url"]).startswith("https://api.github.com/"), "RELEASE_TRANSPORT"),
        (row["tag_resolution"]["status"] == "PASS" and bool(re.fullmatch(r"[0-9a-f]{40}", row["tag_resolution"]["commit_sha"])), "IMMUTABLE_COMMIT"),
        (row["license_at_release"]["spdx_id"] in accepted and bool(re.fullmatch(r"[0-9a-f]{40}", row["license_at_release"]["license_blob_sha"])), "EXACT_TAG_LICENSE"),
        (row["domain_classification"]["status"] == "PASS", "DOMAIN"),
        (row.get("publication_release_version_alignment") == "CANNOT_CHECK_UNLESS_JOSS_PAGE_EXPLICITLY_BINDS_RELEASE_TAG", "VERSION_BOUNDARY"),
        (row.get("natural_pair_eligibility") == "CANNOT_CHECK_EXTERNAL_ADJUDICATION_REQUIRED", "NATURAL_PAIR_BOUNDARY"),
    ]
    for passed, label in checks:
        if not passed:
            failures.append(f"QUALIFIED_{label}:{row['publication_doi']}")

expected_domains = {"EARTH_ENVIRONMENT": 5, "LIFE_BIOMEDICAL": 7, "SCIENTIFIC_SOFTWARE": 62, "PHYSICAL_ENGINEERING": 6}
if result["provider_qualified_by_domain"] != expected_domains:
    failures.append("DOMAIN_COUNTS")
if sum(expected_domains.values()) != result["counts"]["provider_qualified_concept_candidates"]:
    failures.append("DOMAIN_COUNT_SUM")
if result["counts"]["explicit_joss_publication_to_exact_github_release_tag_alignment"] != 0:
    failures.append("VERSION_ALIGNMENT_INFLATION")
if result["claim_boundary"] != {
    "provider_qualified_concepts_are_natural_pairs": False,
    "quota_pass_claimed": False,
    "source_frame_ready_claimed": False,
    "model_or_system_outcomes_accessed": False,
    "protected_cases_or_labels_accessed": False,
    "performance_or_superiority_claim": False,
}:
    failures.append("CLAIM_BOUNDARY")
if result["preserved_programme_terminal"] != "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK":
    failures.append("PREDECESSOR_TERMINAL")
if cell_counts["all_four_m6_cells_pass"] or cell_counts["all_four_m6_cells_gate_evaluable"]:
    failures.append("CELL_GATE_INFLATION")
for entry in ledger["entries"]:
    for field in ("cause", "observed", "residual", "next_discriminator"):
        if not str(entry.get(field) or "").strip():
            failures.append(f"LEDGER_FIELD:{entry.get('issue')}:{field}")

for name, expected in result["artifact_hashes"].items():
    mapping = {
        "protocol_v4": "PROTOCOL_V4.json", "freeze_receipt": "PROTOCOL_FREEZE_RECEIPT_V4.json",
        "crossref_page": "CROSSREF_PAGE_V4.json", "candidate_jsonl": "CANDIDATES_V4.jsonl",
        "strict_candidates": "STRICT_CANDIDATES_V4.json", "transport_log": "TRANSPORT_LOG_V4.json",
        "cell_counts": "CELL_COUNTS_V4.json", "rights_relation_transport_audit": "RIGHTS_RELATION_TRANSPORT_AUDIT_V4.json",
        "negative_result_ledger": "NEGATIVE_RESULT_LEDGER_V4.json",
    }
    if expected != digest(ROOT / mapping[name]):
        failures.append("RESULT_ARTIFACT_HASH:" + name)

secret_patterns = [rb"gho_[A-Za-z0-9]+", rb"github_pat_[A-Za-z0-9_]+", rb"Authorization:\s*(?:token|Bearer)"]
for path in ROOT.iterdir():
    if not path.is_file():
        continue
    data = path.read_bytes()
    for pattern in secret_patterns:
        if re.search(pattern, data, re.I):
            failures.append("SECRET_PATTERN:" + path.name)

receipt = {
    "schema_version": "orion.p4.m6.source-provider-successor.verification-receipt.v4",
    "protocol_id": protocol["protocol_id"],
    "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "passed": not failures,
    "failures": failures,
    "checks": {
        "top_level_json_parse_count": len(top_level_json),
        "jsonl_rows_parsed": len(rows),
        "freeze_hashes": not any(f.startswith("FREEZE_") for f in failures),
        "predecessor_hashes": not any(f.startswith("PREDECESSOR_HASH") for f in failures),
        "provider_qualified_rows": len(qualified),
        "provider_qualified_exact_stage_checks": not any(f.startswith("QUALIFIED_") for f in failures),
        "domain_counts": expected_domains,
        "release_aligned_promotions": 0,
        "natural_pair_promotions": 0,
        "negative_ledger_entries": len(ledger["entries"]),
        "result_artifact_hashes": not any(f.startswith("RESULT_ARTIFACT_HASH") for f in failures),
        "secret_scan": not any(f.startswith("SECRET_PATTERN") for f in failures),
        "write_scope": str(ROOT),
        "checkout_written_by_v4_scripts": False,
    },
    "verification_boundary": "JSON, JSONL, hash, identity, rights, relation, domain, terminal and claim-boundary verification only; no pytest, repository CI, natural-pair adjudication or system outcome",
}
(ROOT / "VERIFY_RECEIPT_V4.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
raise SystemExit(0 if receipt["passed"] else 1)
