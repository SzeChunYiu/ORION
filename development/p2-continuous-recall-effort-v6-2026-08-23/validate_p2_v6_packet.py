#!/usr/bin/env python3
"""Scientific-integrity validator for the outcome-unopened P2 V6 packet."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TERMINAL = (
    "P2_KIFMS_V6_LAWFUL_EXACT_SOURCE_AND_LABEL_BLIND_DISJOINT_POPULATION_"
    "FROZEN__INDEPENDENT_PROTECTED_EXECUTION_CANNOT_CHECK"
)
CONTENT_HASH = "731d87e66b3e1195826c82e0a94fef19c044d63503ba2a36e41d38f811df0b12"
EMPTY_HASH = hashlib.sha256(b"").hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def main() -> None:
    json_paths = sorted(ROOT.rglob("*.json"))
    for path in json_paths:
        json.loads(path.read_text(encoding="utf-8"))
    python_paths = sorted(ROOT.glob("*.py"))
    for path in python_paths:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    rights = load("SOURCE_RIGHTS_PROVENANCE_RECEIPT_V6.json")
    overlap = load("LABEL_BLIND_OVERLAP_RECEIPT_V6.json")
    population = load("SOURCE_FAMILY_AND_POPULATION_FREEZE_V6.json")
    protocol = load("PROTOCOL_FREEZE_V6.json")
    result = load("SOURCE_FEASIBILITY_RESULT_V6.json")
    negative = load("NEGATIVE_RESULT_LEDGER_V6.json")
    next_discriminator = load("NEXT_DISCRIMINATOR_V7.json")

    require(rights["source"]["osf_node_id"] == "vt3n4", "wrong OSF node")
    require(rights["rights"]["osf_license_id"] == "563c1cf88c5e4a3877f9e96a", "wrong licence id")
    require(rights["rights"]["url"] == "https://creativecommons.org/licenses/by/4.0/legalcode", "wrong licence URL")
    files = rights["source"]["csv_files"]
    require(len(files) == 14, "expected fourteen exact CSV identities")
    require(all(item["version"] == 1 for item in files), "all CSVs must bind revision one")
    require(len({item["sha256"] for item in files}) == 14, "CSV hashes must be unique")
    require(sum(item["bytes"] for item in files) == 9_684_901, "unexpected total CSV bytes")
    require(rights["readiness"]["lawful_public_source_body_found"] is True, "lawful source finding missing")
    require(rights["readiness"]["scientific_confirmatory_execution_ready"] is False, "custody boundary erased")
    require(rights["custody"]["independent_custodian_bound"] is False, "false independent custody")
    require(rights["outcome_boundary"]["label_values_accessed"] is False, "labels opened")
    require(rights["prior_public_artifact_boundary"]["public_historical_simulations_exist"] is True, "prior public artifacts hidden")

    require(overlap["review_count"] == 14, "wrong review count")
    require(overlap["total_raw_rows"] == 5_074, "wrong raw row count")
    require(overlap["total_canonical_rows"] == 4_934, "wrong canonical count")
    require(overlap["canonical_union_content_set_sha256"] == CONTENT_HASH, "wrong canonical content hash")
    require(overlap["total_canonical_nonempty_pmids"] == 0, "unexpected nonempty KIFMS PMID")
    require(overlap["canonical_union_pmid_set_sha256"] == EMPTY_HASH, "empty PMID hash not explicit")
    require(overlap["label_boundary"]["label_values_accessed"] is False, "label values accessed")
    require(overlap["label_boundary"]["class_counts_accessed"] is False, "class counts accessed")
    require(overlap["overlap"]["shared_kifms_content_identities_before_exclusion"] == 65, "wrong shared count")
    require(sum(v["excluded_cross_review_content_rows"] for v in overlap["per_review"].values()) == 132, "wrong shared-row exclusion")
    require(sum(v["v5_content_matches"] for v in overlap["per_review"].values()) == 1, "must retain the one raw V5 match")
    require(sum(v["swift_content_matches"] for v in overlap["per_review"].values()) == 0, "unexpected raw SWIFT content match")
    for key in ["final_swift_content_matches", "final_swift_pmid_matches", "final_v5_content_matches", "final_v5_pmid_matches"]:
        require(overlap["overlap"][key] == 0, f"nonzero final overlap: {key}")
    require(sum(v["canonical_rows"] for v in overlap["per_review"].values()) == 4_934, "per-review sum mismatch")

    require(population["review_count"] == 14, "population freeze review count")
    require(population["population_counts"]["canonical_rows"] == 4_934, "population freeze row count")
    require(population["population_counts"]["canonical_union_content_set_sha256"] == CONTENT_HASH, "population content hash")
    require(population["population_counts"]["canonical_nonempty_pmids"] == 0, "population PMID boundary")
    require(population["no_further_exclusion_allowed"] is True, "post-outcome exclusion left open")

    binding_paths = {
        "source_rights_receipt": "SOURCE_RIGHTS_PROVENANCE_RECEIPT_V6.json",
        "population_freeze": "SOURCE_FAMILY_AND_POPULATION_FREEZE_V6.json",
        "overlap_receipt": "LABEL_BLIND_OVERLAP_RECEIPT_V6.json",
    }
    for key, name in binding_paths.items():
        require(protocol["bindings"][key]["path"] == name, f"wrong binding path {key}")
        require(protocol["bindings"][key]["sha256"] == sha256(ROOT / name), f"wrong binding hash {key}")
    require(protocol["outcome_access_status"].startswith("NO KIFMS LABEL VALUES"), "outcome boundary missing")
    require(protocol["metrics"]["cre20"].startswith("CRE20_r="), "CRE20 not frozen")
    require(protocol["estimands"]["coprimary"] == ["unweighted mean Delta_L(CRE20)", "unweighted mean Delta_L(R@10)"], "wrong coprimary endpoints")
    gates = protocol["gates"]
    require("0.010858985820770889" in gates["C1_CRE20_MAGNITUDE"], "CRE threshold drift")
    require("12 of 14" in gates["C2_CRE20_SIGN"], "CRE sign rule drift")
    require("0.010858985820770889" in gates["C3_R10_MAGNITUDE"], "R10 threshold drift")
    require("12 of 14" in gates["C4_R10_SIGN"], "R10 sign rule drift")
    require(">= 0" in gates["C5_LEARNER_WORK_SAVING"], "learner work-saving drift")
    require(">= -0.05" in gates["C6_LEARNER_HARM"], "learner harm drift")
    require(">= +0.05" in gates["G3_FULL_ARM_R10_MARGIN"], "full R10 margin drift")
    require(">= 0" in gates["G4_FULL_ARM_WORK_SAVING"], "full WSS drift")
    require(">= -0.05" in gates["G5_FULL_ARM_HARM"], "full harm drift")
    require("> 0" in gates["G6_ABSOLUTE_WORK_SAVING"], "absolute WSS drift")
    require(protocol["learners"]["L1_u4"]["C"] == 0.11, "u4 C drift")
    require(protocol["learners"]["L1_u4"]["balancer_ratio"] == 9.8, "u4 balance drift")

    require(result["terminal"] == TERMINAL, "result terminal drift")
    require(result["source_findings"]["lawful_public_source_body_found"] is True, "lawful source result missing")
    require(result["source_findings"]["confirmatory_execution_ready"] is False, "false readiness")
    require(result["protocol_findings"]["comparative_scoring_run"] is False, "comparative scoring claimed")
    require(result["population_findings"]["pmid_overlap_interpretation"].startswith("vacuous"), "vacuous PMID boundary hidden")
    require(negative["terminal"] == TERMINAL, "negative ledger terminal drift")
    by_id = {entry["id"]: entry for entry in negative["entries"]}
    require(by_id["N1"]["evidence"]["mean_delta_r10"] == 0.008834277869043594, "V5 adverse result lost")
    require(by_id["N8"]["status"] == "UNRESOLVED_INDEPENDENT_CUSTODY", "custody blocker lost")
    require(by_id["N10"]["status"] == "IDENTIFIER_CHANNEL_ABSENT_CONTENT_DISJOINTNESS_ONLY", "PMID negative lost")
    require(by_id["N11"]["status"] == "PRIOR_PUBLIC_METHOD_ARTIFACTS_DISCLOSED_NO_V6_METRICS_OPENED", "prior-artifact boundary lost")
    require(next_discriminator["parent_terminal"] == TERMINAL, "next discriminator parent drift")

    manifest_path = ROOT / "SHA256SUMS"
    manifest = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        require(rel not in manifest, f"duplicate manifest path {rel}")
        manifest[rel] = digest
    expected_paths = {
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS" and "__pycache__" not in path.parts
    }
    require(set(manifest) == expected_paths, "manifest path set mismatch")
    for rel, digest in manifest.items():
        require(sha256(ROOT / rel) == digest, f"manifest mismatch {rel}")

    print(
        f"PASS P2 V6 scientific packet: {len(json_paths)} JSON, {len(python_paths)} Python, "
        f"{len(manifest)} manifested files; terminal={TERMINAL}"
    )


if __name__ == "__main__":
    main()
