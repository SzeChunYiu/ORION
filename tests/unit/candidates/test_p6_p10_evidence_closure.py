from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from orion.publication.prospective_protocol_freezes import (
    P10_PROTOCOL,
    P9_PROTOCOL,
    load_protocol,
    validate_p10,
    validate_p9,
    validate_repository,
)
from papers.candidates.reproducibility_generators_v3 import (
    ensure_distinct_source,
    load_schema,
    validate_records,
)

ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "papers/candidates/checkers/check_reproducibility_targets_v2.py"
HISTORY_CHECKER = ROOT / "papers/candidates/checkers/check_negative_null_history_v1.py"


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize(
    "path",
    [
        "papers/orion-16-formal-epistemic-structures-and-mechanics/formal/generate_assumption_countermodels_v2.py",
        "papers/orion-17-epistemic-navigation-open-worlds/benchmark/generate_instances_v2.py",
        "papers/orion-18-epistemic-authority-autonomous-science/benchmark/generate_authority_cases_v2.py",
    ],
)
def test_generators_reproduce_committed_bytes(path: str) -> None:
    completed = subprocess.run(
        [sys.executable, path, "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "MATCH" in completed.stdout


def test_empty_schema_and_duplicate_ids_fail_closed(tmp_path: Path) -> None:
    schema_path = tmp_path / "empty.schema.json"
    schema_path.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="enforceable"):
        load_schema(schema_path)

    schema_path.write_text(
        json.dumps(
            {
                "type": "object",
                "required": ["id"],
                "properties": {"id": {"type": "string", "minLength": 1}},
            }
        ),
        encoding="utf-8",
    )
    schema = load_schema(schema_path)
    with pytest.raises(ValueError, match="duplicate id"):
        validate_records([{"id": "same"}, {"id": "same"}], schema)


def test_generator_cannot_use_target_as_source(tmp_path: Path) -> None:
    target = tmp_path / "cases.jsonl"
    target.write_text('{"id":"x"}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="may not be its target"):
        ensure_distinct_source(target, target)


def test_p7_trace_has_nonzero_explicit_opportunities() -> None:
    path = (
        ROOT
        / "papers/orion-17-epistemic-navigation-open-worlds/benchmark/navigation_trace_v2.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["authority_scope"] == "REFERENCE_POLICY_PREFLIGHT_ONLY"
    assert payload["live_agent_executed"] is False
    assert payload["case_opportunities_registered"] == 8
    assert payload["case_opportunities_evaluated"] == 8
    assert len(payload["rows"]) == 8
    assert all(row["decision_opportunities_evaluated"] == 1 for row in payload["rows"])


def test_p7_zero_opportunity_trace_cannot_pass() -> None:
    module = load_script(
        ROOT
        / "papers/orion-17-epistemic-navigation-open-worlds/benchmark/generate_instances_v2.py",
        "p7_generate_v2_hostile",
    )
    with pytest.raises(ValueError, match="zero or missing"):
        module.trace_payload([], b"")


def test_p8_attack_denominator_and_local_authority_boundary() -> None:
    path = (
        ROOT
        / "papers/orion-18-epistemic-authority-autonomous-science/evidence/local/"
        "cross_capability_attack_replay_result_v2.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["attack_opportunities_registered"] == 5
    assert payload["attack_opportunities_evaluated"] == 5
    assert payload["attacks_blocked"] == 5
    assert payload["self_authorizing"] is True
    assert payload["independent_custody"] is False
    assert payload["grants_scientific_authority"] == "NONE"


def test_p8_zero_attack_opportunities_cannot_pass() -> None:
    module = load_script(
        ROOT
        / "papers/orion-18-epistemic-authority-autonomous-science/benchmark/"
        "generate_authority_cases_v2.py",
        "p8_generate_v2_hostile",
    )
    with pytest.raises(ValueError, match="five registered"):
        module.attack_payload([], b"")


def test_negative_history_is_content_bound() -> None:
    completed = subprocess.run(
        [sys.executable, str(HISTORY_CHECKER), "--root", str(ROOT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert completed.stdout.count("HISTORY: BOUND") == 3


def test_frozen_v1_manifests_were_not_rewritten() -> None:
    expected = {
        "papers/orion-16-formal-epistemic-structures-and-mechanics/CONTENT_MANIFEST_V1.json": "9de90db705fc0adaebcdac070b118d2c7a3051bdb7455522e6be2a11953dc5dc",
        "papers/orion-17-epistemic-navigation-open-worlds/CONTENT_MANIFEST_V1.json": "41d4e09f938c6be51856f1ea601b263d17ed06341a7e993ae46d155a9a4d4cee",
        "papers/orion-18-epistemic-authority-autonomous-science/CONTENT_MANIFEST_V1.json": "aa146862fc93077c21adaacceb05c69599ada9070b2dc55f34837e533a464101",
    }
    assert {path: sha256(ROOT / path) for path in expected} == expected


def test_p9_p10_protocols_validate_but_execution_stays_blocked() -> None:
    report = validate_repository(ROOT)
    assert len(report["P9"]["missing_inputs"]) == 5
    assert len(report["P10"]["missing_inputs"]) == 8

    p9 = load_protocol(ROOT / P9_PROTOCOL)
    assert p9["execution_authorized"] is False
    assert p9["outcome_artifact"] is None
    assert p9["multiplicity"]["worst_family_gate_is_noncompensatory"] is True

    p10 = load_protocol(ROOT / P10_PROTOCOL)
    assert p10["execution_authorized"] is False
    assert p10["outcome_artifact"] is None
    assert {claim["state"] for claim in p10["hypotheses"].values()} == {
        "PROSPECTIVE_NOT_EXECUTED"
    }
    assert p10["multiplicity"]["worst_domain_gates_are_noncompensatory"] is True


def test_p9_locked_environment_reproduction_failure_is_append_only() -> None:
    path = (
        ROOT
        / "papers/orion-19-structured-epistemic-learning/evidence/"
        "P9_D1V1_2_LOCKED_ENV_REPRODUCTION_2026-08-23.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["overall_outcome"] == "FAIL"
    assert payload["self_authorizing"] is True
    assert payload["independent_reproduction"] is False
    assert payload["independent_unit_credit"] == 0
    assert payload["scorer_identity"]["selected_config"] == "logistic-C1"
    serialized = payload["arms"]["TYPED_SERIALIZED_BAG"]
    assert serialized["environment_departures"] == []
    assert serialized["archived_accuracy"] == 0.5
    assert serialized["reproduced_accuracy"] == 0.75
    assert payload["successor"] == "P9.D1V1_3.ORDERED_MULTIPLICITY_ROBUSTNESS"


def test_p10_rejects_stale_subject_and_laundered_hypothesis() -> None:
    payload = load_protocol(ROOT / P10_PROTOCOL)
    stale = copy.deepcopy(payload)
    stale["subject"]["base_commit"] = "0" * 40
    with pytest.raises(ValueError, match="stale or unavailable"):
        validate_p10(ROOT, stale)

    laundered = copy.deepcopy(payload)
    laundered["hypotheses"]["H1"]["state"] = "PASS"
    with pytest.raises(ValueError, match="outcome laundering"):
        validate_p10(ROOT, laundered)


def test_p10_rejects_a_lock_digest_that_only_matches_the_moving_head() -> None:
    payload = load_protocol(ROOT / P10_PROTOCOL)
    moving = copy.deepcopy(payload)
    moving["subject"]["environment_lock_sha256"] = sha256(ROOT / "uv.lock")
    assert moving["subject"]["environment_lock_sha256"] != payload["subject"][
        "environment_lock_sha256"
    ]
    with pytest.raises(ValueError, match="frozen subject commit"):
        validate_p10(ROOT, moving)


def test_p9_rejects_zero_potency_and_weakened_worst_family_gate() -> None:
    payload = load_protocol(ROOT / P9_PROTOCOL)
    inert = copy.deepcopy(payload)
    inert["opportunity_gate"]["minimum_changed_fraction_per_registered_cell"] = 0
    with pytest.raises(ValueError, match="inert"):
        validate_p9(ROOT, inert)

    compensatory = copy.deepcopy(payload)
    compensatory["multiplicity"]["worst_family_gate_is_noncompensatory"] = False
    with pytest.raises(ValueError, match="worst-family"):
        validate_p9(ROOT, compensatory)


def test_self_attestation_and_replay_without_raw_inputs_fail(tmp_path: Path) -> None:
    module = __import__(
        "orion.publication.prospective_protocol_freezes",
        fromlist=["_validate_required_inputs"],
    )
    validate_inputs = module._validate_required_inputs
    fake = tmp_path / "fake.json"

    payload = {
        "execution_authorized": True,
        "required_inputs": [
            {
                "id": "independent_scorer",
                "required": True,
                "present": True,
                "artifact": "fake.json",
            }
        ],
    }
    fake.write_text(
        json.dumps({"self_authorizing": True, "raw_inputs": ["x"]}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="self-attestation"):
        validate_inputs(tmp_path, payload)

    fake.write_text(
        json.dumps({"self_authorizing": False, "raw_inputs": []}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="lacks raw inputs"):
        validate_inputs(tmp_path, payload)


def test_diagnostic_counts_close_only_local_targets() -> None:
    module = load_script(CHECKER, "candidate_reproducibility_v2_final")
    expected = {
        "P6": {"BOUND": 8, "CANNOT_CHECK": 1, "DEFERRED": 1, "PARTIAL": 0},
        # P7's subject-commit pin is deliberately unbound while its sealed evidence
        # sits at seal-time bytes; see the parametrisation in
        # test_candidate_reproducibility_targets_v2.py for the full reason, and
        # evidence/independent/SEAL_INTEGRITY_NOTE_V1.md for the incident.
        "P7": {"BOUND": 7, "CANNOT_CHECK": 1, "DEFERRED": 1, "PARTIAL": 1},
        "P8": {"BOUND": 7, "CANNOT_CHECK": 1, "DEFERRED": 1, "PARTIAL": 1},
    }
    for paper_id, counts in expected.items():
        report = module.derive_report(ROOT, paper_id)
        for state, count in counts.items():
            assert report["state_counts"][state] == count, (paper_id, report)
        independent = report["reproducibility_targets"]["independent_replay_attestation"]
        assert independent["status"] == "CANNOT_CHECK"
    p8 = module.derive_report(ROOT, "P8")
    custody = p8["reproducibility_targets"]["protected_labels_custody_and_attack_replay"]
    assert custody["status"] == "PARTIAL"
    assert "protected-label custody" in custody["blocker"]
