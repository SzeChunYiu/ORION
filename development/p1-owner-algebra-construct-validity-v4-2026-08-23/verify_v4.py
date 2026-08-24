#!/usr/bin/env python3
"""Native bounded validator for the P1 V4 scientific packet (no network/pytest/CI)."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LANE = Path(__file__).resolve().parent
TERMINAL = (
    "P1_V4_PUBLIC_POSTPUBLICATION_STANDARD_SCAFFOLD_FEASIBLE__"
    "ZERO_OF_TWELVE_OWNER_ALGEBRA_GROUPS_SUFFICIENT__"
    "SCIENTIFIC_ACTION_GOLD_AND_CONSTRUCT_VALIDITY_CANNOT_CHECK"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> dict:
    return json.loads((LANE / name).read_text())


def main() -> None:
    write_receipt = "--write-receipt" in sys.argv
    checks: list[str] = []

    def must(condition: bool, label: str) -> None:
        assert condition, label
        checks.append(label)

    protocol = load("PROTOCOL_V4.json")
    freeze = load("PROTOCOL_FREEZE_RECEIPT_V4.json")
    amendment = load("SOURCE_INTERFACE_AMENDMENT_V4A.json")
    amend_freeze = load("AMENDMENT_FREEZE_RECEIPT_V4A.json")
    terminology = load("CLAIM_TERMINOLOGY_AMENDMENT_V4B.json")
    count_correction = load("AGGREGATE_COUNT_CORRECTION_V4C.json")
    source = load("SOURCE_CAPTURE_AND_RIGHTS_RECEIPT_V4.json")
    envelope = load("STANDARD_NATIVE_ACTION_ENVELOPE_V4.json")
    owner = load("OWNER_GROUP_FEASIBILITY_V4.json")
    result = load("RESULT_V4.json")

    must(freeze["protocol_sha256"] == digest(LANE / "PROTOCOL_V4.json"), "protocol freeze digest")
    must(freeze["source_capture_started"] is False, "protocol frozen before capture")
    must(freeze["case_or_outcome_accessed"] is False, "protocol freeze outcome blind")
    must(amend_freeze["amendment_sha256"] == digest(LANE / "SOURCE_INTERFACE_AMENDMENT_V4A.json"), "amendment freeze digest")
    must(amend_freeze["new_source_capture_started"] is False, "COPE PDF frozen before capture")
    must(amend_freeze["case_or_outcome_accessed"] is False, "amendment outcome blind")
    must(terminology["terminal_unchanged"] is True, "terminology correction keeps terminal")
    must(terminology["outcome_or_case_accessed"] is False, "terminology correction outcome blind")
    must(count_correction["after"]["exact_structural_analogue_groups"] == 9, "V4C exact structural analogue correction")
    must(count_correction["changed_scientific_terminal"] is False, "V4C keeps terminal")
    must(count_correction["case_or_outcome_accessed"] is False, "V4C outcome blind")

    for item in protocol["predecessors"].values():
        path = Path(item["path"])
        must(path.is_file(), f"predecessor exists: {path.name}")
        must(digest(path) == item["sha256"], f"predecessor digest: {path.name}")

    rows = source["sources"]
    must(len(rows) == 9, "nine frozen source routes after V4A")
    must(sum(r["http_status"] == 200 for r in rows) == 8, "eight HTTP 200 documents")
    must(sum(r["http_status"] != 200 for r in rows) == 1, "one fail-closed non-2xx document")
    must(source["capture_summary"]["accessible_institutional_family_count"] == 4, "four distinct institutional source families")
    must(source["capture_summary"]["raw_html_or_pdf_retained"] is False, "raw documents not retained")
    must(source["capture_summary"]["case_or_outcome_content_accessed"] is False, "source capture outcome blind")
    must(all(r["raw_response_retained"] is False for r in rows), "per-source raw retention false")

    by_id = {r["source_id"]: r for r in rows}
    expected_hashes = {
        "NISO_CREC_RP45_LANDING":"bc8e23ad13d11a47fd849435595bcb1470d901cdd5b0888282b0d69c35aa1dbc",
        "NISO_CREC_RP45_PDF":"110ff6008091aea1535d6242e2cb5ab1c56b353b932ac30afc4b075133ca86a1",
        "CROSSREF_CROSSMARK":"b4229ad75909d5d01e3448270dee36672b892208214a6996d47077c4518321a2",
        "CROSSREF_POLICY_PAGE":"7587874d117eaca3bbbdc7caa3ae5874d549ec0cc98813bbc51a82a97ad4397a",
        "CROSSREF_RELATIONSHIPS":"62dd1b1a2ae006ed24f9df0a430da8ea0f772f87e589859bc2fa3163925ef154",
        "NLM_JATS_RELATED_ARTICLE":"ec2df613a9fcf4a2b8c7342d111e99c444938c98cf55b2562e88a6364999dcd1",
        "COPE_RETRACTION_GUIDELINES":"e6e43f09e0af36f47b5007f1451b72d5d8c416f70e60727f2ee5d9d128d40281",
        "COPE_RETRACTION_GUIDELINES_PDF":"6fb39c51be6f61ae9629e7b298b58a5a761845b3b35110edbdc8f5d155b82f96",
        "ICMJE_CORRECTIONS_ROUTE":"01faee9f88020df6f121760a5b493da807ced28fd53326287465df9030a88853",
    }
    must(set(by_id) == set(expected_hashes), "source identities exact")
    must(all(by_id[k]["response_sha256"] == v for k, v in expected_hashes.items()), "all response hashes exact")
    initial_name_map = {
        "NISO_CREC_RP45_LANDING.html":"NISO_CREC_RP45_LANDING",
        "NISO_CREC_RP45_PDF.pdf":"NISO_CREC_RP45_PDF",
        "CROSSREF_CROSSMARK.html":"CROSSREF_CROSSMARK",
        "CROSSREF_POLICY_PAGE.html":"CROSSREF_POLICY_PAGE",
        "CROSSREF_RELATIONSHIPS.html":"CROSSREF_RELATIONSHIPS",
        "NLM_JATS_RELATED_ARTICLE.html":"NLM_JATS_RELATED_ARTICLE",
        "COPE_RETRACTION_GUIDELINES.html":"COPE_RETRACTION_GUIDELINES",
        "ICMJE_CORRECTIONS_ROUTE.html":"ICMJE_CORRECTIONS_ROUTE",
    }
    must(len(amendment["raw_capture_sha256_before_amendment"]) == 8, "eight pre-amendment raw hashes")
    must(all(amendment["raw_capture_sha256_before_amendment"][f] == by_id[s]["response_sha256"] for f, s in initial_name_map.items()), "pre-amendment hashes bind receipt")
    must(by_id["COPE_RETRACTION_GUIDELINES"]["requested_route"] == "https://publicationethics.org/retraction-guidelines", "COPE requested route retained")
    must(by_id["COPE_RETRACTION_GUIDELINES"]["final_url"] == "https://publicationethics.org/guidance/guideline/retraction-guidelines", "COPE canonical redirect retained")
    must(by_id["ICMJE_CORRECTIONS_ROUTE"]["http_status"] == 404, "ICMJE 404 retained")
    must(by_id["ICMJE_CORRECTIONS_ROUTE"]["disposition"] == "CANNOT_CHECK_HTTP_NON_2XX__NO_SUBSTITUTE", "ICMJE fail closed")
    must(by_id["NISO_CREC_RP45_PDF"]["pdf_pages"] == 66, "NISO PDF identity")
    must(by_id["COPE_RETRACTION_GUIDELINES_PDF"]["pdf_pages"] == 17, "COPE PDF identity")
    must("CC-BY-4.0" in by_id["CROSSREF_CROSSMARK"]["rights"], "Crossref documentation rights bound")
    must("CC-BY-NC-ND-4.0" in by_id["COPE_RETRACTION_GUIDELINES_PDF"]["rights"], "COPE PDF rights bound")
    must("NO_SPDX_ASSERTED" in by_id["NISO_CREC_RP45_PDF"]["rights"], "NISO custom rights boundary")
    must("NOT_BOUND" in by_id["NLM_JATS_RELATED_ARTICLE"]["rights"], "JATS rights cannot check retained")
    must(source["rights_boundary"]["legal_advice"] is False, "no legal advice claim")

    must(envelope["exact_construction"]["institutional_families_byte_bound"] == 4, "four-family envelope")
    must(envelope["exact_construction"]["scaffold_gate_pass"] is True, "scaffold gate passes")
    must(len(envelope["source_families"]) == 4, "four source-family semantics rows")
    must(all(r["closed_r7_action_algebra"] is False for r in envelope["source_families"]), "no source claims closed R7 algebra")
    must(all(r["r7_owner_or_delegation"] is False for r in envelope["source_families"]), "no source claims R7 ownership or delegation")
    must(len(envelope["forbidden_promotions"]) == 4, "four explicit promotion boundaries")

    decisions = owner["field_decisions"]
    must(len(decisions) == 12, "twelve unchanged owner groups")
    must([d["group_id"] for d in decisions] == [f"G{i:02d}" for i in range(1, 13)], "owner group identities exact")
    must(sum(d["structural_analogue_observed"] for d in decisions) == 9, "nine structural analogue groups")
    must(sum(d["named_custodian_authorship_or_explicit_delegation_evidenced"] for d in decisions) == 0, "zero named-custodian groups")
    must(sum(d["counts_as_sufficient_owner_group"] for d in decisions) == 0, "zero sufficient owner groups")
    must(all(d["sufficiency"] == "INSUFFICIENT" for d in decisions), "all group decisions insufficient")
    must(all(d["exact_r7_target_coverage_and_exhaustiveness"] is False for d in decisions), "exact target coverage absent")
    must(all(d["applicable_completed_target_algebra_rights_bound"] is False for d in decisions), "target-algebra rights absent")
    must(owner["counts"] == {"groups_with_named_custodian_or_delegation":0,"groups_with_source_native_structural_analogue":9,"requirement_groups":12,"scientific_action_gold_cells":0,"sufficient_owner_groups":0}, "owner count identity")
    must(owner["exact_nondelegation_upper_bound"]["maximum_sufficient_groups"] == 0, "exact nondelegation upper bound zero")
    must(owner["exact_nondelegation_upper_bound"]["future_owner_signed_algebra_impossible"] is False, "future algebra not declared impossible")
    must(owner["adapter_rerun"]["performed"] is False, "adapter rerun prohibited")
    must(owner["terminal"] == TERMINAL, "owner terminal exact")

    must(result["source_capture_receipt_sha256"] == digest(LANE / "SOURCE_CAPTURE_AND_RIGHTS_RECEIPT_V4.json"), "result source receipt digest")
    must(result["standard_native_envelope_sha256"] == digest(LANE / "STANDARD_NATIVE_ACTION_ENVELOPE_V4.json"), "result envelope digest")
    must(result["owner_group_feasibility_sha256"] == digest(LANE / "OWNER_GROUP_FEASIBILITY_V4.json"), "result owner feasibility digest")
    must(result["terminology_amendment_sha256"] == digest(LANE / "CLAIM_TERMINOLOGY_AMENDMENT_V4B.json"), "result terminology amendment digest")
    must(result["aggregate_count_correction_sha256"] == digest(LANE / "AGGREGATE_COUNT_CORRECTION_V4C.json"), "result aggregate correction digest")
    must(result["owner_algebra"] == {"named_custodian_or_delegation_groups":0,"requirement_groups":12,"structural_analogue_groups":9,"sufficient_groups":0}, "result owner algebra counts")
    must(result["scientific_action_gold_cells"] == 0, "zero scientific action gold")
    must(result["construct_validity"] == "CANNOT_CHECK", "construct validity cannot check")
    must(result["adapter"] == {"fully_certified_unchanged":0,"known_rejected_unchanged":116929,"not_disproved_but_uncertified_unchanged":720,"rerun":False}, "V8 map counts unchanged")
    must(result["readiness"]["before"] == "NOT_SUBMISSION_READY", "readiness before exact")
    must(result["readiness"]["after"] == "NOT_SUBMISSION_READY", "readiness after exact")
    must(result["readiness"]["changed"] is False, "readiness unchanged")
    must(result["current_terminal_supersedes_v3"] is False, "V3 terminal not rewritten")
    must(result["terminal"] == TERMINAL, "result terminal exact")
    must(TERMINAL in (LANE / "CONSTRUCT_VALIDITY_REPORT_V4.md").read_text(), "report terminal exact")
    must(TERMINAL in (LANE / "CLAIM_BOUNDARY_V4.md").read_text(), "claim-boundary terminal exact")
    must(TERMINAL in (LANE / "README.md").read_text(), "README terminal exact")
    must(not (LANE / ".capture_tmp").exists(), "temporary source directory deleted")
    must(not (LANE / "__pycache__").exists(), "bytecode cache absent")
    forbidden = [p.name for p in LANE.iterdir() if p.suffix.lower() in {".html", ".pdf", ".txt", ".pyc"}]
    must(forbidden == [], "no raw source or bytecode artifacts retained")

    # Every JSON artifact must parse.
    json_files = sorted(p for p in LANE.glob("*.json") if p.name != "VALIDATION_RECEIPT_V4.json")
    for path in json_files:
        json.loads(path.read_text())
    must(len(json_files) == 10, "ten non-validation JSON artifacts parse")

    artifact_names = sorted(
        p.name for p in LANE.iterdir()
        if p.is_file() and p.name not in {"VALIDATION_RECEIPT_V4.json", "SHA256SUMS"}
    )
    artifact_hashes = {name: digest(LANE / name) for name in artifact_names}
    if write_receipt:
        receipt = {
            "schema_version":"orion.p1.owner-algebra-construct-validity.validation-receipt.v4",
            "validated_at":datetime.now(timezone.utc).isoformat(),
            "status":"PASS",
            "scientific_assertion_count":len(checks),
            "validated_artifact_sha256":artifact_hashes,
            "validated_counts":{
                "source_routes":9,"http_200_documents":8,"distinct_institutional_families":4,
                "structural_analogue_groups":9,"sufficient_owner_groups":0,
                "scientific_action_gold_cells":0,"v8_cannot_check_maps":720,
            },
            "boundary":{"network_used_by_validator":False,"pytest_or_repo_ci_run":False,"case_or_outcome_accessed":False,"raw_source_documents_retained":False},
            "terminal":TERMINAL,
        }
        (LANE / "VALIDATION_RECEIPT_V4.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        receipt = load("VALIDATION_RECEIPT_V4.json")
        assert receipt["status"] == "PASS"
        assert receipt["scientific_assertion_count"] == len(checks)
        assert receipt["validated_artifact_sha256"] == artifact_hashes
        assert receipt["terminal"] == TERMINAL
        manifest = {}
        for line in (LANE / "SHA256SUMS").read_text().splitlines():
            value, name = line.split("  ", 1)
            manifest[name] = value
        expected_names = sorted(p.name for p in LANE.iterdir() if p.is_file() and p.name != "SHA256SUMS")
        assert sorted(manifest) == expected_names
        assert all(digest(LANE / name) == value for name, value in manifest.items())
    print(json.dumps({"status":"PASS","scientific_assertions":len(checks),"sufficient_owner_groups":0,"scientific_action_gold":0,"terminal":TERMINAL}, sort_keys=True))


if __name__ == "__main__":
    main()
