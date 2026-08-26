"""The SciFact label-to-state adapter is total, decisive, and frozen pre-scoring.

`SCIFACT_LABEL_STATE_MAP_V1.json` is the only sanctioned bridge from external
SciFact gold labels into P4 states. Its guarantees are structural, so the tests
pin them against the artifact itself:

* **Totality** -- every label in the SciFact claim-verdict vocabulary has a
  mapping row, and nothing outside that vocabulary smuggles in a row. A partial
  mapping would leave uncovered labels to ad-hoc judgement, and an invented
  label row would let an external system coin its own coordinates.
* **Decisiveness** -- a gold REFUTE can only BLOCK, a NOT_ENOUGH_INFO can only
  fail closed to CANNOT_CHECK, and a gold SUPPORT is never sufficient for
  BLOCK: external support clears one coordinate, it does not discharge ORION's
  promotion obligations.
* **No UNRESOLVED** -- UNRESOLVED is ORION-internal (the label could not be
  read); a readable SciFact label must never map into it.
* **Crossref/RW exactness** -- the allowed-use set is exactly the three
  coordinate uses; an active retraction forces a revocation BLOCK.

The checker tests follow the repo's standing rule: validate a guard against
both the conforming artifact (exit 0) and a tampered one (exit 1), so it can
neither cry wolf nor rubber-stamp.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P4 = ROOT / "papers" / "orion-14-verified-scientific-discovery"
MAP_PATH = P4 / "protocol" / "SCIFACT_LABEL_STATE_MAP_V1.json"
CHECKER = P4 / "protocol" / "check_scifact_label_state_map_v1.py"


def _load() -> dict:
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def _checker():
    spec = importlib.util.spec_from_file_location("scifact_label_state_map", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _rows(doc: dict) -> dict[str, dict]:
    return {row["scifact_label"]: row for row in doc["frozen_mapping"]}


# --------------------------------------------------------------------------
# The mapping itself
# --------------------------------------------------------------------------


def test_mapping_is_total_over_the_scifact_vocabulary() -> None:
    doc = _load()
    rows = _rows(doc)
    for label in doc["scifact_label_vocabulary"]["claim_verdict_labels"]:
        assert label in rows, f"claim-verdict label {label!r} has no mapping row"
    assert set(rows) == set(doc["scifact_label_vocabulary"]["claim_verdict_labels"]), (
        "frozen_mapping rows must be exactly the claim-verdict vocabulary"
    )
    semantic = set(doc["p4_state_vocabulary"]["semantic_support"])
    for label, row in rows.items():
        assert row["p4_semantic_support"] in semantic, (
            f"{label}: {row['p4_semantic_support']!r} is outside the P4 semantic vocabulary"
        )


def test_negative_labels_are_decisive_and_fail_closed() -> None:
    rows = _rows(_load())
    refute = rows["REFUTE"]
    assert refute["p4_semantic_support"] == "CONTRADICTED"
    assert refute["terminal"] == "BLOCK"
    assert "terminal_on_all_obligations_discharged" not in refute, (
        "REFUTE must not be upgradable by discharged obligations"
    )
    nei = rows["NOT_ENOUGH_INFO"]
    assert nei["p4_semantic_support"] == "INSUFFICIENT"
    assert nei["terminal"] == "CANNOT_CHECK"


def test_support_is_never_sufficient_for_block_and_never_unconditional_promote() -> None:
    rows = _rows(_load())
    support = rows["SUPPORT"]
    assert support["p4_semantic_support"] == "SUPPORTED"
    assert support["never_terminal"] == "BLOCK"
    assert support["terminal_on_all_obligations_discharged"] == "PROMOTE"
    assert support["terminal_on_any_unresolved_obligation"] == "CANNOT_CHECK"
    assert len(support["required_promotion_obligations"]) >= 1, (
        "without obligations a gold SUPPORT would promote unconditionally"
    )


def test_no_readable_label_maps_to_unresolved() -> None:
    doc = _load()
    image = {row["p4_semantic_support"] for row in doc["frozen_mapping"]}
    assert "UNRESOLVED" not in image


def test_crossref_rw_allowed_uses_are_exactly_the_three_coordinate_uses() -> None:
    doc = _load()
    rw = doc["crossref_retraction_watch_constraint"]
    assert set(rw["allowed_uses"]) == {
        "DOI_METADATA_UPDATE",
        "EVALUATION_EPOCH",
        "REVOCATION_CONFORMANCE",
    }
    assert rw["forbidden_uses"], "a whitelist without forbidden counterparts is decorative"
    retraction = rw["conformance_rules"]["active_retraction_on_gold_evidence_doi"]
    assert retraction["forced_terminal"] == "BLOCK"
    assert retraction["revocation_nonconformant"] is True
    assert retraction["recorded_as"] == "REVOCATION_BLOCK"


def test_contradiction_dominates_in_claim_composition() -> None:
    doc = _load()
    assert "contradiction_dominates" in doc["claim_verdict_composition"]["rules"]


# --------------------------------------------------------------------------
# The checker
# --------------------------------------------------------------------------


def test_checker_passes_on_the_frozen_artifact() -> None:
    assert _checker().run(MAP_PATH) == 0


def test_checker_catches_a_mapping_edited_after_outcomes(tmp_path: Path) -> None:
    """The freeze's whole value: outcome_accessed=true must be a violation."""

    doc = _load()
    doc["outcome_accessed"] = True
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(doc), encoding="utf-8")
    assert _checker().run(tampered) == 1


def test_checker_catches_a_softened_negative_label(tmp_path: Path) -> None:
    doc = _load()
    for row in doc["frozen_mapping"]:
        if row["scifact_label"] == "REFUTE":
            row["terminal"] = "CANNOT_CHECK"
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(doc), encoding="utf-8")
    assert _checker().run(tampered) == 1


def test_checker_catches_an_expanded_crossref_whitelist(tmp_path: Path) -> None:
    doc = _load()
    doc["crossref_retraction_watch_constraint"]["allowed_uses"].append(
        "SEMANTIC_SUPPORT_ADJUDICATION"
    )
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(doc), encoding="utf-8")
    assert _checker().run(tampered) == 1


def test_checker_catches_unresolved_in_the_mapping_image(tmp_path: Path) -> None:
    doc = _load()
    for row in doc["frozen_mapping"]:
        if row["scifact_label"] == "NOT_ENOUGH_INFO":
            row["p4_semantic_support"] = "UNRESOLVED"
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(doc), encoding="utf-8")
    assert _checker().run(tampered) == 1


def test_checker_cannot_check_is_distinct_from_clean(tmp_path: Path) -> None:
    assert _checker().run(tmp_path / "does_not_exist.json") == 2
