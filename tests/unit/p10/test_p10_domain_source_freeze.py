"""Focused tests for the P10 domain/source freeze artifact and its checker.

Tamper discipline: every mutation test starts from a byte-identical copy of the real
artifact, so a failure can only come from the injected mutation. The clean-copy-passes
test proves the harness itself is neutral.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = REPO_ROOT / "papers/paper-10-structured-problem-solving/protocol/P10_DOMAIN_SOURCE_FREEZE_V1.json"
CHECKER = REPO_ROOT / "papers/paper-10-structured-problem-solving/protocol/check_p10_domain_source_freeze_v1.py"

_spec = importlib.util.spec_from_file_location("p10_domain_source_freeze_checker", CHECKER)
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _write(doc: dict, tmp_path: Path) -> Path:
    out = tmp_path / "tampered.json"
    out.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return out


def _violations_of(doc: dict) -> list[str]:
    return checker._violations(doc)


# --- clean state -----------------------------------------------------------------


def test_real_artifact_passes_the_checker() -> None:
    assert checker.run(ARTIFACT) == 0


def test_clean_copy_in_tmp_also_passes(tmp_path: Path) -> None:
    assert checker.run(_write(_load(), tmp_path)) == 0


def test_missing_file_is_cannot_check(tmp_path: Path) -> None:
    assert checker.run(tmp_path / "absent.json") == 2


def test_garbled_json_is_cannot_check(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert checker.run(bad) == 2


def test_wrong_schema_is_cannot_check(tmp_path: Path) -> None:
    doc = _load()
    doc["schema"] = "ORION.P9.SomethingElse.v1"
    assert checker.run(_write(doc, tmp_path)) == 2


# --- freeze banner ---------------------------------------------------------------


def test_results_exist_true_is_a_violation() -> None:
    doc = _load()
    doc["results_exist"] = True
    assert any("results_exist" in s for s in _violations_of(doc))


def test_campaign_executed_true_is_a_violation() -> None:
    doc = _load()
    doc["campaign_executed"] = True
    assert any("campaign_executed" in s for s in _violations_of(doc))


# --- domains and licences ---------------------------------------------------------


def test_dropped_domain_is_a_violation() -> None:
    doc = _load()
    doc["frozen_domains"] = doc["frozen_domains"][:3]
    assert any("exactly four domains" in s for s in _violations_of(doc))


def test_renamed_domain_is_a_violation() -> None:
    doc = _load()
    doc["frozen_domains"][0]["domain_id"] = "COQ_INTERACTIVE_THEOREM_PROVING"
    assert any("domain set drifted" in s for s in _violations_of(doc))


def test_miniF2F_cannot_get_a_licence_name_false_clearance() -> None:
    doc = _load()
    for d in doc["frozen_domains"]:
        for s in d["sources"]:
            if s["source_id"] == "MINIF2F":
                s["license"] = {
                    "name": "MIT",
                    "verification": "VERIFIED_WITH_URL_AND_DATE",
                    "verified_utc": "2026-08-24T10:39:25Z",
                    "evidence_url": "https://github.com/facebookresearch/miniF2F/blob/main/LICENSE",
                    "evidence_fetch_sha256": "0" * 64,
                }
    assert any("MINIF2F" in s for s in _violations_of(doc))


def test_cannot_check_licence_may_not_assert_a_name() -> None:
    doc = _load()
    for d in doc["frozen_domains"]:
        for s in d["sources"]:
            if s["source_id"] == "CVC5":
                s["license"]["name"] = "GPL-3.0"
    assert any("CVC5" in s and "not assert a name" in s for s in _violations_of(doc))


def test_verified_licence_requires_evidence_sha() -> None:
    doc = _load()
    for d in doc["frozen_domains"]:
        for s in d["sources"]:
            if s["source_id"] == "EVALPLUS":
                del s["license"]["evidence_fetch_sha256"]
    assert any("EVALPLUS" in s and "evidence_fetch_sha256" in s for s in _violations_of(doc))


def test_unknown_verification_mode_is_a_violation() -> None:
    doc = _load()
    for d in doc["frozen_domains"]:
        for s in d["sources"]:
            if s["source_id"] == "VAL":
                s["license"]["verification"] = "ASSUMED_CLEAN"
    assert any("VAL" in s and "VERIFIED_WITH_URL_AND_DATE or CANNOT_CHECK" in s for s in _violations_of(doc))


# --- committed minimums -------------------------------------------------------------


def test_tasks_per_domain_below_100_is_a_violation() -> None:
    doc = _load()
    doc["committed_minimums"]["independent_tasks_per_domain"] = 60
    assert any("independent_tasks_per_domain" in s for s in _violations_of(doc))


def test_controls_below_80_is_a_violation() -> None:
    doc = _load()
    doc["committed_minimums"]["known_method_controls"] = 40
    assert any("known_method_controls" in s for s in _violations_of(doc))


def test_claiming_minimums_satisfied_is_a_violation() -> None:
    doc = _load()
    doc["committed_minimums"]["satisfied_by_this_artifact"] = True
    assert any("satisfied_by_this_artifact" in s for s in _violations_of(doc))


# --- inference unit ------------------------------------------------------------------


def test_removing_a_forbidden_unit_is_a_violation() -> None:
    doc = _load()
    doc["inference_unit"]["forbidden_units"] = ["search seed", "model sample"]
    assert any("forbidden_units" in s for s in _violations_of(doc))


# --- box verdicts ----------------------------------------------------------------------


def test_executed_baseline_arm_is_a_violation() -> None:
    doc = _load()
    for a in doc["box_verdicts"]["box_2_implement_baselines"]["arms"]:
        if a["arm_id"] == "EXACT_SEARCH":
            a["status"] = "DONE"
    assert any("EXACT_SEARCH" in s and "execution-level" in s for s in _violations_of(doc))


def test_missing_baseline_arm_is_a_violation() -> None:
    doc = _load()
    arms = doc["box_verdicts"]["box_2_implement_baselines"]["arms"]
    doc["box_verdicts"]["box_2_implement_baselines"]["arms"] = [
        a for a in arms if a["arm_id"] != "STRONGEST_DONOR"
    ]
    assert any("missing arm STRONGEST_DONOR" in s for s in _violations_of(doc))


def test_box3_verdict_flipped_is_a_violation() -> None:
    doc = _load()
    doc["box_verdicts"]["box_3_run_h1_h6"]["verdict"] = "DONE"
    assert any("box_3" in s for s in _violations_of(doc))


def test_box1_must_admit_the_enumeration_is_not_populated() -> None:
    doc = _load()
    doc["box_verdicts"]["box_1_populate_frozen_design"]["detail"] = "all 400 tasks enumerated"
    assert any("NOT_POPULATED" in s for s in _violations_of(doc))


# --- bindings ---------------------------------------------------------------------------


def test_protocol_freeze_sha_drift_is_a_violation() -> None:
    doc = _load()
    doc["protocol_freeze_binding"]["sha256"] = "f" * 64
    vs = _violations_of(doc)
    assert any("drifted from the frozen value" in s for s in vs)
    assert any("does not match the on-disk" in s for s in vs)


def test_prior_receipt_bad_sha_is_a_violation() -> None:
    doc = _load()
    doc["prior_adverse_evidence"][0]["sha256"] = "not-a-sha"
    assert any("sha256 must be 64 lowercase hex" in s for s in _violations_of(doc))


def test_discharging_a_required_input_is_a_violation() -> None:
    doc = _load()
    doc["protocol_freeze_binding"]["inputs_discharged_by_this_artifact"] = ["native_verifier_backed_runner"]
    assert any("discharges no H1-H6 required input" in s for s in _violations_of(doc))
