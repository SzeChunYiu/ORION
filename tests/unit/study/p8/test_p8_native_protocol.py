"""Tests for P8's frozen native cross-system execution protocol.

A protocol that claims to cover "every ordered cross-system pair with clean and
hostile cases" is checkable before any native system runs: the pair structure,
the slot ids, the distinctness of the hostile mechanisms and the honesty of the
CANNOT_CHECK execution status are all properties of the frozen design. These
tests pin them, pin the tamper-detection (a mutated protocol must fail
validation), and pin the cross-artifact binding.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/orion-18-epistemic-authority-autonomous-science"
TWIN = PAPER / "formal/P8_NATIVE_CROSS_SYSTEM_PROTOCOL_2026-08-24.json"
DOC = PAPER / "formal/P8_NATIVE_CROSS_SYSTEM_PROTOCOL_V1.md"
CHECKER = PAPER / "formal/check_p8_native_protocol_binding_v1.py"

SYSTEM_IDS = ("OPA", "CDR", "ITT", "SIG")


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_p8_native_protocol_binding_v1", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def twin() -> dict:
    return json.loads(TWIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def checker():
    return _load_checker()


class TestTheFrozenStructure:
    def test_four_type_distinct_systems(self, twin: dict) -> None:
        assert {s["id"] for s in twin["systems"]} == set(SYSTEM_IDS)
        assert len({s["evidence_type"] for s in twin["systems"]}) == 4

    def test_every_ordered_pair_exactly_once(self, twin: dict) -> None:
        seen = [(p["emitter"], p["consumer"]) for p in twin["ordered_pairs"]]
        expected = [(e, c) for e in SYSTEM_IDS for c in SYSTEM_IDS if e != c]
        assert sorted(seen) == sorted(expected)
        assert len(seen) == len(set(seen)) == 12

    def test_every_pair_has_clean_and_hostile_slots(self, twin: dict) -> None:
        for pair in twin["ordered_pairs"]:
            e, c = pair["emitter"], pair["consumer"]
            assert pair["clean_case_id"] == f"P8.NC.{e}_{c}.CLEAN"
            assert pair["hostile_case_id"] == f"P8.NC.{e}_{c}.HOSTILE"
        assert twin["slot_count"] == 24

    def test_hostile_mechanisms_are_distinct_and_named(self, twin: dict) -> None:
        mechanisms = [p["hostile_mechanism"] for p in twin["ordered_pairs"]]
        assert all(m.strip() for m in mechanisms)
        assert len(set(mechanisms)) == 12

    def test_validation_accepts_the_committed_protocol(self, checker, twin) -> None:
        assert checker.validate_protocol(twin) == []


class TestTheApparatusCanFail:
    """The validator only means something if it rejects a changed protocol."""

    def test_a_dropped_pair_is_rejected(self, checker, twin: dict) -> None:
        tampered = copy.deepcopy(twin)
        tampered["ordered_pairs"] = tampered["ordered_pairs"][:-1]
        errors = checker.validate_protocol(tampered)
        assert any("ordered pairs" in e for e in errors)

    def test_a_duplicated_slot_id_is_rejected(self, checker, twin: dict) -> None:
        tampered = copy.deepcopy(twin)
        tampered["ordered_pairs"][1]["clean_case_id"] = tampered["ordered_pairs"][0][
            "clean_case_id"
        ]
        errors = checker.validate_protocol(tampered)
        assert any("case id" in e for e in errors)

    def test_an_executed_claim_is_rejected(self, checker, twin: dict) -> None:
        """Quietly upgrading the status would launder a design into a run."""

        tampered = copy.deepcopy(twin)
        tampered["execution_status"] = "EXECUTED"
        errors = checker.validate_protocol(tampered)
        assert any("CANNOT_CHECK" in e for e in errors)

    def test_a_vacuous_mechanism_is_rejected(self, checker, twin: dict) -> None:
        tampered = copy.deepcopy(twin)
        tampered["ordered_pairs"][0]["hostile_mechanism"] = "   "
        errors = checker.validate_protocol(tampered)
        assert any("hostile mechanism" in e for e in errors)

    def test_a_missing_binary_pin_is_rejected(self, checker, twin: dict) -> None:
        tampered = copy.deepcopy(twin)
        tampered["tooling_gap"]["required_binaries"] = ["opa"]
        errors = checker.validate_protocol(tampered)
        assert any("cosign" in e for e in errors)


class TestHonesty:
    def test_execution_is_cannot_check_with_the_gap_stated(self, twin: dict) -> None:
        assert twin["execution_status"] == "CANNOT_CHECK"
        gap = " ".join(str(x) for x in twin["tooling_gap"].values())
        for binary in ("opa", "cedar", "cosign", "in-toto-verify"):
            assert binary in gap or binary in str(twin["tooling_gap"])

    def test_simulation_is_a_prohibited_inference(self, twin: dict) -> None:
        joined = " ".join(twin["prohibited_inference"])
        assert "simulating" in joined
        assert "partial run" in joined

    def test_the_document_matches_the_issue_box_language(self) -> None:
        doc = " ".join(DOC.read_text(encoding="utf-8").lower().split())
        for phrase in (
            "every ordered cross-system pair",
            "clean and hostile",
            "Nothing in this protocol is simulated",
            "Execution status: `CANNOT_CHECK`",
        ):
            assert phrase.lower() in doc

    def test_the_denied_cannot_check_calibration_is_not_re_derived(self) -> None:
        doc = " ".join(DOC.read_text(encoding="utf-8").split())
        assert "does not re-derive" in doc


class TestTheBinding:
    def test_the_cross_artifact_audit_passes(self, checker) -> None:
        report = checker.audit()
        assert report["status"] == "PASS", report["errors"]
        assert report["contract_id"] == "P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1"

    def test_the_manuscript_appends_are_bound(self) -> None:
        final = (PAPER / "manuscript/FINAL_V3.md").read_text(encoding="utf-8")
        core = (PAPER / "manuscript/FORMAL_CORE_V2_1.md").read_text(encoding="utf-8")
        assert "P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1" in final
        assert "P8.NATIVE.CROSS_SYSTEM_PROTOCOL.V1" in core
        assert "CANNOT_CHECK" in final and "is not executed" in core

    def test_the_ledger_addendum_is_additive_only(self) -> None:
        ledger = (PAPER / "CLAIM_LEDGER_ADDENDUM_V3.md").read_text(encoding="utf-8")
        assert "additive rows only" in ledger
        assert "CANNOT_CHECK" in ledger
        assert "prohibited inference" in ledger.lower()


class TestScope:
    def test_the_boundary_is_stated(self, checker) -> None:
        report = checker.audit()
        boundary = str(report["authority_boundary"])
        assert "no native system was executed" in boundary
        assert "simulated" in boundary
