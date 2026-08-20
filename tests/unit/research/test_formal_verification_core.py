from pathlib import Path
import importlib.util
import sys

MODULE = (
    Path(__file__).resolve().parents[3]
    / "research"
    / "extensions"
    / "meta-orion-recursive-scientific-evolution"
    / "formal_verification_core.py"
)
spec = importlib.util.spec_from_file_location("formal_verification_core", MODULE)
fv = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = fv
spec.loader.exec_module(fv)


def test_all_registered_executable_mechanics_verify():
    report = fv.build_closure_report()
    assert report["terminal"] == "RSE_FORMAL_MECHANICS_VERIFIED_WITH_DONOR_SUBSUMPTION"
    assert report["failed_ids"] == ()
    executable = [row for row in report["matrix"] if row["id"].startswith("RSE.T")]
    assert len(executable) == 5
    assert all(row["passed"] for row in executable)
    assert all(row["status"] != "FAILED" for row in executable)


def test_generic_justification_donor_strikes_bespoke_projection_superiority():
    row = fv.verify_generic_justification_subsumption()
    assert row["passed"]
    assert row["status"] == "DONOR_SUBSUMPTION_VERIFIED"
    assert row["terminal"] == "GENERIC_JUSTIFICATION_DONOR_SUFFICIENT"


def test_universal_state_and_jreach_are_not_misrepresented_as_theorems():
    matrix = {row["id"]: row for row in fv.formal_status_matrix()}
    assert matrix["RSE.D1"]["status"] == "DEFINITION_ONLY"
    assert matrix["RSE.D4"]["status"] == "PROTOCOL_RULE_ONLY"
    assert matrix["RSE.D5"]["status"] == "STRUCK_UNPROVED_UNIVERSAL"


def test_delayed_debt_requires_future_scientific_integrity_not_present_answer_only():
    row = fv.verify_delayed_epistemic_debt()
    assert row["passed"]
    assert row["status"] == "CAUSAL_DELAYED_DEBT_COUNTERMODEL_VERIFIED"


def test_finite_information_ceiling_is_explicitly_bounded():
    row = fv.verify_successor_nonidentifiability()
    assert row["passed"]
    assert row["status"] == "FINITE_INFORMATION_CEILING_VERIFIED"
    assert "finite registered families" in row["claim_boundary"]
