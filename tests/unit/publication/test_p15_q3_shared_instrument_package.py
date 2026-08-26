import hashlib
import json
from pathlib import Path

from orion_research_harness.scientific_execution_integrity import ScientificExecutionRecord


ROOT = Path(__file__).resolve().parents[3]
BINDING = ROOT / "papers/P15_Q3_SHARED_INSTRUMENT_PACKAGE_V1.json"
P15 = ROOT / "papers/orion-25-orion-research-harness/top_tier"


def test_shared_package_binding_hashes_exact_files_and_denies_authority():
    binding = json.loads(BINDING.read_text())
    assert binding["release_status"] == "RELEASE_CANDIDATE_UNTAGGED"
    assert binding["declared_license_expression"] == "Apache-2.0"
    assert binding["license_osi_approved"] is True
    assert binding["relicensing_authority"] == "CANNOT_CHECK"
    for artifact in binding["artifacts"].values():
        observed = hashlib.sha256((ROOT / artifact["path"]).read_bytes()).hexdigest()
        assert observed == artifact["sha256"]
    assert binding["scientific_authority_delta"] == "NONE"
    assert binding["independent_authority"] == "CANNOT_CHECK"
    assert binding["external_adoption"] == "CANNOT_CHECK"
    assert binding["site_independence"] == "CANNOT_CHECK"
    assert binding["public_data_confers_custody"] is False
    assert binding["public_runtime_campaign"] == "NOT_RUN"
    assert binding["versioned_release"] == "NOT_CREATED"


def test_packaged_p15_evaluator_exactly_replays_frozen_18_case_gold():
    lines = (P15 / "sei_fault_cases_v1.jsonl").read_text().splitlines()
    cases = [json.loads(line) for line in lines if line]
    gold = json.loads((P15 / "sei_fault_gold_v1.json").read_text())
    assert len(cases) == 18
    predicted = {}
    fields = set(ScientificExecutionRecord.__dataclass_fields__) - {"record_id"}
    for case in cases:
        raw = {"record_id": case["id"], **{name: case[name] for name in fields}}
        predicted[case["id"]] = ScientificExecutionRecord.from_mapping(raw).disposition().value
    declared = {
        "AUTHORIZED_SCIENCE": "DECLARED_AUTHORIZED_SCIENCE",
        "VALID_BUT_NOT_AUTHORIZED": "DECLARED_VALID_BUT_NOT_AUTHORIZED",
        "INVALID_SCIENCE": "DECLARED_INVALID_SCIENCE",
    }
    assert predicted == {case_id: declared.get(value, value) for case_id, value in gold.items()}
