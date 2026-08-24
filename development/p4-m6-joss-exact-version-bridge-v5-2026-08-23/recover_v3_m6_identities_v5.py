#!/usr/bin/env python3
"""Recover only the nine exact V3 M6 identities required for V3/V4/V5 dedup."""
from __future__ import annotations
import datetime as dt, hashlib, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
V3 = ROOT.parent / "p4-source-universe-successor-v3"
EXPECTED_CANDIDATE_SHA = "612f7f00460af0f198dc5d160e979ac929c5bbdee45cf0b8ec11b5fea6ed35b5"
EXPECTED_RESULT_SHA = "3e556f15a0c872b3bbf8236227e6546ed14b3166979f343b071edb50cdb36a66"

def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical(v: object) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"

candidate_path = V3 / "CANDIDATES_V1.jsonl"
result_path = V3 / "RESULT_V1.json"
assert sha(candidate_path) == EXPECTED_CANDIDATE_SHA
assert sha(result_path) == EXPECTED_RESULT_SHA
result = json.loads(result_path.read_text())
selected: list[dict] = []
expected_ids: dict[str, str] = {}
for cell_id, cell in result["cells"].items():
    if cell.get("mechanism_id") != "M6_ARTICLE_TO_CODE_RELEASE":
        continue
    for cid in cell["candidate_ids"]:
        if cid in expected_ids:
            raise AssertionError(f"duplicate candidate id {cid}")
        expected_ids[cid] = cell_id
for line in candidate_path.open():
    if not line.strip():
        continue
    row = json.loads(line)
    cid = row.get("candidate_id")
    if cid not in expected_ids:
        continue
    if row.get("mechanism_id") != "M6_ARTICLE_TO_CODE_RELEASE" or row.get("strict_metadata_qualified") is not True:
        raise AssertionError(f"V3 reported M6 candidate lost its qualification: {cid}")
    selected.append({
        "candidate_id": cid,
        "cell_id": expected_ids[cid],
        "domain_discovery": row.get("domain_discovery"),
        "mechanism_id": row.get("mechanism_id"),
        "provider": row.get("provider"),
        "provider_family": row.get("provider_family"),
        "object_doi_exact": row.get("object_doi_exact"),
        "object_concept_doi": row.get("object_concept_doi"),
        "publication_doi": row.get("publication_doi"),
        "author_lineage_signature": row.get("author_lineage_signature"),
        "record_sha256": row.get("record_sha256"),
    })
selected.sort(key=lambda r: (r["cell_id"], r["candidate_id"]))
if {r["candidate_id"] for r in selected} != set(expected_ids):
    raise AssertionError("not all reported V3 M6 identities recovered")
identity_keys = [(r["object_concept_doi"], r["publication_doi"]) for r in selected]
if len(identity_keys) != len(set(identity_keys)):
    raise AssertionError("duplicate V3 M6 concept/publication identity")
per_domain: dict[str, int] = {}
for row in selected:
    per_domain[row["domain_discovery"]] = per_domain.get(row["domain_discovery"], 0) + 1
output = {
    "schema_version": "orion.p4.m6.v3-identity-recovery.v5",
    "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "authority": "RECOVERY_FROM_HASH_VERIFIED_V3_PUBLIC_METADATA_ARTIFACT__IDENTITY_ONLY",
    "source": {
        "candidate_jsonl": str(candidate_path),
        "candidate_jsonl_sha256_expected_and_observed": EXPECTED_CANDIDATE_SHA,
        "result_json": str(result_path),
        "result_json_sha256_expected_and_observed": EXPECTED_RESULT_SHA,
    },
    "counts": {
        "reported_v3_m6_candidate_ids": len(expected_ids),
        "recovered_exact_rows": len(selected),
        "unique_object_concept_publication_pairs": len(set(identity_keys)),
        "by_domain": dict(sorted(per_domain.items())),
    },
    "identities": selected,
    "boundary": {
        "omitted_payload_absence_treated_as_zero_overlap": False,
        "recovered_identities_are_new_units": False,
        "files_versions_search_hits_counted_as_units": False,
        "author_lineage_signature_proves_independence": False,
        "natural_pair_eligibility": "CANNOT_CHECK_EXTERNAL_ADJUDICATION_REQUIRED",
    },
    "terminal": "P4_V3_M6_EXACT_CONCEPT_PUBLICATION_IDENTITIES_RECOVERED_FOR_CROSS_PROVIDER_DEDUP_ONLY",
    "preserved_programme_terminal": "P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK",
}
(ROOT / "V3_M6_IDENTITY_RECOVERY_V5.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
print(json.dumps(output["counts"], indent=2, sort_keys=True))
