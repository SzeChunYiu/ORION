#!/usr/bin/env python3
"""Read-only validator for the completed P3 V21 packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    checks: list[tuple[str, bool]] = []

    def check(name: str, passed: bool) -> None:
        checks.append((name, bool(passed)))

    protocol = json.loads((ROOT / "PROTOCOL_V21.json").read_text())
    result = json.loads((ROOT / "BERTMAP_RESULT_V21.json").read_text())
    parser = json.loads((ROOT / "PARSER_RECEIPT_V21.json").read_text())
    metrics = json.loads((ROOT / "COMMON_PAIR_METRICS_V21.json").read_text())
    next_gate = json.loads((ROOT / "NEXT_DISCRIMINATOR_V22.json").read_text())

    check("protocol_identity", protocol["protocol_id"] == "P3_V21_FROZEN_V20_DIRECT_IRI_IDENTITY_DECODER_AND_COMMON_SCORING")
    check("identity_decoder", protocol["typed_decoder"]["decode_rule"] == "decoded_entity_iri = input_entity_iri")
    check("decoder_pass", result["typed_decoder_pass"] is True and result["typed_decoder"]["identity_transform"] is True)
    check("decoder_rows", result["typed_decoder"]["input_rows"] == result["typed_decoder"]["decoded_rows"] == 33)
    check("role_members", result["typed_decoder"]["exact_source_members"] == result["typed_decoder"]["exact_target_members"] == 33)
    check("parser_pass", parser["terminal"] == "STRUCTURAL_NATIVE_ARTIFACT_CONTRACT_PASS")
    check("parser_keys", parser["completed_source_key_count"] == parser["expected_source_key_count"] == 36)
    check("five_artifacts", len(parser["artifacts"]) == 5 and all(item["bytes"] > 0 for item in parser["artifacts"].values()))
    check("one_analysis_unit", metrics["analysis_unit"] == "one frozen OAEI 2004 test-103 case")
    check("no_population_inference", metrics["inference"]["population_estimand"] is False and metrics["inference"]["p_values"] is False and metrics["inference"]["confidence_intervals"] is False)
    primary = metrics["estimands"]["primary_common_class_pair"]
    secondary = metrics["estimands"]["secondary_full_equivalence_pair"]
    check("primary_counts", primary["BERTMAP_V21"]["true_positive"] == 33 and primary["BERTMAP_V21"]["false_positive"] == 0 and primary["BERTMAP_V21"]["false_negative"] == 0)
    check("primary_exact_f1", primary["BERTMAP_V21"]["f1"]["fraction"] == "1/1" and primary["AML_V3_2"]["f1"]["fraction"] == "16/41")
    check("primary_delta", primary["bertmap_minus_aml_f1"]["fraction"] == "25/41" and primary["finite_case_f1_winner"] == "BERTMAP")
    check("secondary_exact_f1", secondary["BERTMAP_V21"]["f1"]["fraction"] == "33/62" and secondary["AML_V3_2"]["f1"]["fraction"] == "16/137")
    check("secondary_coverage_visible", secondary["BERTMAP_V21"]["false_negative"] == 58 and secondary["BERTMAP_V21"]["recall"]["fraction"] == "33/91")
    check("gold_access_order", metrics["reference_first_semantically_opened_after_both_outputs_frozen"] is True)
    check("next_gate_source_disjoint", next_gate["required_case_family"]["source_disjoint_from_oaei_2004_test_103"] is True)

    for name, spec in protocol["frozen_code"].items():
        check(f"frozen_code_{name}", sha256(ROOT / name) == spec)
    for name, spec in protocol["frozen_inputs"].items():
        path = Path(spec["path"])
        check(f"frozen_input_{name}", path.is_file() and not path.is_symlink() and path.stat().st_size == spec["bytes"] and sha256(path) == spec["sha256"])

    sums_ok = True
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        sums_ok = sums_ok and path.is_file() and not path.is_symlink() and sha256(path) == expected
    check("sha256sums", sums_ok)

    failed = [name for name, passed in checks if not passed]
    if failed:
        print("P3_V21_VALIDATION_FAIL:" + ",".join(failed))
        return 1
    print(
        "P3_V21_PACKET_VALID__DIRECT_IRI_IDENTITY_DECODER_33_OF_33__"
        "STRUCTURAL_PARSER_PASS__PRIMARY_BERTMAP_F1_1_OF_1_VS_AML_16_OF_41__"
        "SECONDARY_COVERAGE_33_OF_91_VISIBLE__ONE_CASE_DESCRIPTIVE_ONLY__"
        f"{len(checks)}_CHECKS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
