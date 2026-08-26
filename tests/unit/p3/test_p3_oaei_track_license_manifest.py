"""The OAEI/SemTab licence manifest is verified-or-CANNOT_CHECK and frozen pre-download.

`OAEI_TRACK_LICENSE_MANIFEST_V1.json` is the only sanctioned record of which
external ontology-alignment sources may be downloaded and scored; the bound
`OAEI_MULTI_CASE_ANALYSIS_FREEZE_V1.json` freezes gates, arms and statistical
units before any scoring. Their guarantees are structural, so the tests pin
them against the artifacts themselves:

* **Verified-or-CANNOT_CHECK** -- the one selected primary source (bench23)
  carries a licence name with VERIFIED_WITH_URL_AND_DATE plus evidence URL,
  field and fetch hash; no CANNOT_CHECK entry ever wears a licence name, so an
  unverified licence cannot masquerade under a familiar name.
* **Exclusions recorded** -- the UMLS-associated tracks and eClass are excluded
  with bases, not silently dropped.
* **Natural-pair requirement** -- at least one natural ontology-pair candidate
  exists, licence-blocked, and bench23 is bound as single-seed insufficient.
* **Honest non-execution** -- nothing downloaded, MELT not executed, LogMap/AML
  arms CANNOT_CHECK with participation evidence but no execution claim.
* **Statistical unit** -- the inference unit is the ontology pair or track,
  never the correspondence row.

The checker tests follow the repo's standing rule: validate a guard against
both a conforming artifact (exit 0) and tampered copies (exit 1), and keep
"could not read" (exit 2) distinct from "checked and fine".
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

PAPER_DIR = Path(__file__).resolve().parents[3] / "papers" / "orion-13-global-knowledge-portrait"
MANIFEST_PATH = PAPER_DIR / "gold" / "OAEI_TRACK_LICENSE_MANIFEST_V1.json"
FREEZE_PATH = PAPER_DIR / "protocol" / "OAEI_MULTI_CASE_ANALYSIS_FREEZE_V1.json"
CHECKER_PATH = PAPER_DIR / "gold" / "check_oaei_track_license_manifest_v1.py"


def _load() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _load_freeze() -> dict:
    return json.loads(FREEZE_PATH.read_text(encoding="utf-8"))


def _checker():
    spec = importlib.util.spec_from_file_location("check_oaei_track_license_manifest_v1", CHECKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write(tmp_path: Path, doc: dict, name: str) -> Path:
    tampered = tmp_path / name
    tampered.write_text(json.dumps(doc), encoding="utf-8")
    return tampered


# --------------------------------------------------------------------------
# The manifest itself
# --------------------------------------------------------------------------


def test_bench23_licence_is_verified_with_url_date_and_fetch_hash() -> None:
    doc = _load()
    primaries = doc["primary_sources"]
    assert len(primaries) == 1, "exactly one selected primary source at freeze time"
    licence = primaries[0]["license"]
    assert licence["verification"] == "VERIFIED_WITH_URL_AND_DATE"
    assert licence["name"] == "CC-BY-4.0"
    assert licence["evidence_url"].startswith("https://")
    assert licence["evidence_field"]
    assert len(licence["evidence_fetch_sha256"]) == 64
    assert "NOT_DOWNLOADED" in primaries[0]["download_status"], (
        "verification must precede download; a download claim would break box 1"
    )
    assert primaries[0]["record"]["file_sha256_published"] is None and primaries[0]["record"][
        "integrity_note"
    ], "MD5-only publication must carry the compute-SHA-256-at-download note"


def test_cannot_check_licences_never_carry_a_name() -> None:
    doc = _load()
    checked = [entry["license"] for entry in doc["natural_pair_candidates"]]
    checked.append(doc["licensed_fallback"]["license"])
    for licence in checked:
        assert licence["verification"] == "CANNOT_CHECK"
        assert licence["name"] is None, "a CANNOT_CHECK licence must not wear a name"
        assert licence["reason"], "a CANNOT_CHECK licence must state why"


def test_issue_mandated_exclusions_are_recorded_with_bases() -> None:
    doc = _load()
    excluded = {entry["source_id"]: entry for entry in doc["excluded_tracks"]}
    for required in ("OAEI_LARGEBIO_LEGACY_2015", "OAEI_BIO_ML", "ECLASS"):
        assert required in excluded, f"issue box 1 exclusion {required} is missing"
        assert excluded[required]["exclusion_terminal"]
        assert excluded[required]["basis"]
        assert excluded[required]["evidence"]


def test_natural_pair_requirement_is_blocked_not_dropped() -> None:
    doc = _load()
    candidates = doc["natural_pair_candidates"]
    assert any("natural" in entry["role"] for entry in candidates), (
        "bench23 alone cannot satisfy the natural-pair requirement"
    )
    assert doc["primary_sources"][0]["composition_limitation"]
    assert doc["scoring_framework"]["name"] == "MELT"
    assert "NOT_EXECUTED" in doc["scoring_framework"]["execution_status"]
    assert doc["licensed_fallback"]["activation_status"] == "NOT_ACTIVATED"


def test_anatomy_is_not_mislabeled_as_uml_excluded() -> None:
    doc = _load()
    anatomy = next(
        entry for entry in doc["other_audited_families_not_selected"] if entry["source_id"] == "OAEI_ANATOMY"
    )
    assert "UMLS" not in anatomy["terminal"], (
        "the bound audit records MGI-derived references with CC BY 4.0 inputs; "
        "the UMLS exclusion must not bleed onto Anatomy"
    )


# --------------------------------------------------------------------------
# The bound analysis freeze
# --------------------------------------------------------------------------


def test_freeze_keeps_the_inference_unit_off_correspondence_rows() -> None:
    freeze = _load_freeze()
    unit = freeze["statistical_unit_rule"]["inference_unit"]
    assert "ontology pair" in unit and "track" in unit
    assert "correspondence" in unit and "never" in unit
    assert "bootstrap" in freeze["statistical_unit_rule"]["interval_method"].lower()


def test_freeze_arms_stay_honest_about_execution() -> None:
    freeze = _load_freeze()
    arms = {arm["arm_id"]: arm for arm in freeze["arms"]}
    for comparator in ("LOGMAP", "AML"):
        arm = arms[comparator]
        assert "NOT_EXECUTED" in arm["status"], f"{comparator} claims an execution that never happened"
        evidence = arm["public_participation_evidence"]
        assert evidence["url"].startswith("https://")
        assert len(evidence["page_sha256"]) == 64
    assert arms["ORION_FULL_POLICY"]["role"] == "candidate"
    assert "substitut" in freeze["unavailable_arm_policy"].lower()


def test_freeze_pass_gates_match_the_issue_verbatim() -> None:
    freeze = _load_freeze()
    gate = freeze["pass_gate"]
    assert "100%" in gate["valid_output_coverage"]
    assert "0.03" in gate["primary"] and "CI > 0" in gate["primary"]
    assert "0.01" in gate["alternative"] and "0.05" in gate["alternative"]
    assert "zero" in gate["logical_incoherence"].lower()
    assert "true negative" in freeze["open_world_boundary"]["rule"]


def test_freeze_declares_pre_execution_honestly() -> None:
    freeze = _load_freeze()
    assert freeze["freeze_status"] == "FROZEN_BEFORE_ANY_OAEI_SCORING"
    assert freeze["outcome_accessed"] is False
    preconditions = freeze["preconditions_at_freeze"]
    assert preconditions["melt_executed"] is False
    assert preconditions["reference_alignments_opened"] is False
    assert freeze["gold_standard_rule"]["rule"] == "OFFICIAL_RDF_REFERENCE_ALIGNMENTS_ONLY"


# --------------------------------------------------------------------------
# The checker
# --------------------------------------------------------------------------


def test_checker_passes_on_the_frozen_artifacts() -> None:
    assert _checker().run(MANIFEST_PATH, FREEZE_PATH) == 0


def test_checker_catches_a_manifest_edited_after_outcomes(tmp_path: Path) -> None:
    """The freeze's whole value: outcome_accessed=true must be a violation."""

    doc = _load()
    doc["outcome_accessed"] = True
    assert _checker().run(_write(tmp_path, doc, "tampered.json"), FREEZE_PATH) == 1


def test_checker_catches_a_name_snuck_onto_a_cannot_check_licence(tmp_path: Path) -> None:
    doc = _load()
    doc["natural_pair_candidates"][0]["license"]["name"] = "CC0-1.0"
    assert _checker().run(_write(tmp_path, doc, "tampered.json"), FREEZE_PATH) == 1


def test_checker_catches_a_dropped_issue_exclusion(tmp_path: Path) -> None:
    doc = _load()
    doc["excluded_tracks"] = [
        entry for entry in doc["excluded_tracks"] if entry["source_id"] != "ECLASS"
    ]
    assert _checker().run(_write(tmp_path, doc, "tampered.json"), FREEZE_PATH) == 1


def test_checker_catches_a_download_claim_on_the_primary(tmp_path: Path) -> None:
    doc = _load()
    doc["primary_sources"][0]["download_status"] = "DOWNLOADED"
    assert _checker().run(_write(tmp_path, doc, "tampered.json"), FREEZE_PATH) == 1


def test_checker_catches_a_softened_licence_verification(tmp_path: Path) -> None:
    doc = _load()
    doc["primary_sources"][0]["license"]["verification"] = "ASSUMED_UPSTREAM"
    assert _checker().run(_write(tmp_path, doc, "tampered.json"), FREEZE_PATH) == 1


def test_checker_catches_a_row_level_inference_unit(tmp_path: Path) -> None:
    freeze = _load_freeze()
    freeze["statistical_unit_rule"]["inference_unit"] = "correspondence row"
    assert _checker().run(MANIFEST_PATH, _write(tmp_path, freeze, "tampered_freeze.json")) == 1


def test_checker_catches_softened_pass_gates(tmp_path: Path) -> None:
    freeze = _load_freeze()
    freeze["pass_gate"]["primary"] = "macro-F1 advantage >= 0.01 with paired bootstrap lower CI > 0"
    assert _checker().run(MANIFEST_PATH, _write(tmp_path, freeze, "tampered_freeze.json")) == 1


def test_checker_catches_an_executed_comparator_arm(tmp_path: Path) -> None:
    freeze = _load_freeze()
    for arm in freeze["arms"]:
        if arm["arm_id"] == "AML":
            arm["status"] = "EXECUTED_LOCALLY"
    assert _checker().run(MANIFEST_PATH, _write(tmp_path, freeze, "tampered_freeze.json")) == 1


def test_checker_treats_a_missing_bound_freeze_as_a_violation(tmp_path: Path) -> None:
    assert _checker().run(MANIFEST_PATH, tmp_path / "missing_freeze.json") == 1


def test_checker_cannot_check_is_distinct_from_clean(tmp_path: Path) -> None:
    assert _checker().run(tmp_path / "does_not_exist.json", FREEZE_PATH) == 2
    garbled = tmp_path / "garbled.json"
    garbled.write_text("{not json", encoding="utf-8")
    assert _checker().run(garbled, FREEZE_PATH) == 2
