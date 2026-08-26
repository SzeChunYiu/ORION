from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


RUNNER = Path(__file__).with_name("run_p3_des_01.py")
SPEC = importlib.util.spec_from_file_location("p3_des_runner", RUNNER)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_rights_manifest_fails_closed_over_full_p3_universe() -> None:
    repo = Path(__file__).resolve().parents[4]
    path = repo / "papers/orion-13-global-knowledge-portrait/gold/OAEI_TRACK_LICENSE_MANIFEST_V1.json"
    rows = MODULE.classify_strata(json.loads(path.read_text()))
    assert len(rows) == 4
    assert not any(row["admissible"] for row in rows)
    assert {row["stratum_id"] for row in rows} == {
        "OAEI_BENCH23_GENERATED",
        "OAEI_NATURAL_ONTOLOGY_PAIR",
        "SEMTAB_2025",
        "NATURAL_SCIENTIFIC_IDENTITY",
    }


def test_bench23_is_not_a_natural_pair_substitute() -> None:
    repo = Path(__file__).resolve().parents[4]
    path = repo / "papers/orion-13-global-knowledge-portrait/gold/OAEI_TRACK_LICENSE_MANIFEST_V1.json"
    rows = MODULE.classify_strata(json.loads(path.read_text()))
    bench = next(row for row in rows if row["stratum_id"] == "OAEI_BENCH23_GENERATED")
    assert bench["rights_state"] == "LICENSE_VERIFIED__SELECTED"
    assert bench["admissible"] is False
    assert "natural-pair requirement" in bench["reason"]
