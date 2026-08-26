"""The v2 mechanical-arm record re-observes without promoting itself.

The v1 record's `raw_artifact_replay` summary — *"only a limitations markdown
exists; 62/66 cannot be regenerated from a case table"* — stopped being true when
the case table landed. Correcting a statement of fact is not the same as raising
a verdict, and the difference is what these tests hold.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RECORDS = ROOT / "research" / "verification" / "records"
V1 = RECORDS / "P1.mechanical-arm-62-66.json"
V2 = RECORDS / "P1.mechanical-arm-62-66.v2.json"
INDEX = RECORDS / "INDEX.json"
TABLE = (
    ROOT
    / "papers"
    / "orion-11-recursive-epistemic-reconstruction"
    / "evidence"
    / "MECHANICAL_ARM_CASE_TABLE_V1.json"
)


def _srv():
    spec = importlib.util.spec_from_file_location(
        "srv", ROOT / "research" / "verification" / "scientific_result_verification.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_v2_validates_and_its_digest_matches() -> None:
    payload = json.loads(V2.read_text(encoding="utf-8"))
    assert _srv().validate_record(payload) == []


def test_v2_does_not_promote_the_verification_state() -> None:
    """Producing the artifact does not entitle the producer to raise the verdict."""

    v1 = json.loads(V1.read_text(encoding="utf-8"))
    v2 = json.loads(V2.read_text(encoding="utf-8"))
    assert v2["verification_state"] == v1["verification_state"] == "CANNOT_CHECK"
    assert v2["self_authorizing"] is False
    assert v2["claim_id"] == v1["claim_id"]


def test_index_does_not_promote_either() -> None:
    """The index is the surface consumers read, so it is the real promotion path."""

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    assert "P1.mechanical-arm-62-66.v2.json" in index["records"]
    assert index["states"]["P1.mechanical-arm-62-66.v2"] == "CANNOT_CHECK"
    assert index["states"]["P1.mechanical-arm-62-66"] == "CANNOT_CHECK"


def test_only_the_factually_false_layer_moved() -> None:
    v1 = json.loads(V1.read_text(encoding="utf-8"))
    v2 = json.loads(V2.read_text(encoding="utf-8"))
    moved = {
        name
        for name, layer in v2["layers"].items()
        if layer["status"] != v1["layers"][name]["status"]
    }
    assert moved == {"raw_artifact_replay"}
    assert v2["layers"]["raw_artifact_replay"]["status"] == "PASS"


def test_independent_scorer_stays_blocked_on_the_oracle_rule() -> None:
    """Replay is not independent scoring, and the record has to say why.

    `VERIFIER_STANDARD_V1` point 1 forbids importing original scorer internals as
    an oracle. The case table calls `orion.study.p1.contradiction` directly, so it
    is a replay however carefully it is built — a distinction that would be easy
    to lose once a per-case JSON exists and looks like scorer output.
    """

    v2 = json.loads(V2.read_text(encoding="utf-8"))
    layer = v2["layers"]["independent_scorer"]
    assert layer["status"] == "CANNOT_CHECK"
    assert "oracle" in layer["summary"]
    ids = {item["id"] for item in v2["discrepancies"]}
    assert "P1.mechanical-arm-replay-is-not-independent-scoring" in ids


def test_v2_binds_the_case_table_by_content() -> None:
    v2 = json.loads(V2.read_text(encoding="utf-8"))
    entry = next(
        item for item in v2["raw_artifacts"] if item["path"].endswith("MECHANICAL_ARM_CASE_TABLE_V1.json")
    )
    assert entry["present"] is True
    assert entry["sha256"] == hashlib.sha256(TABLE.read_bytes()).hexdigest()
    assert not any(item["role"] == "missing_required" for item in v2["raw_artifacts"])
