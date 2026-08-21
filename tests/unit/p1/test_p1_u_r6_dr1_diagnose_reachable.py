"""P1-U R6-DR1: the repaired root encoding must actually reach DIAGNOSE.

The campaign this succeeds scored 48 episodes from a root world where
``DetectOperator`` could not emit a residual --- one domain already searched, one
claim already ``VERIFIED`` --- so ``DIAGNOSE`` never ran and the ablation arm was
inert. These tests pin both halves of the repair: the repaired world reaches
``DIAGNOSE``, and the failed world is now refused loudly rather than scored.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
DR1 = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r6_dr1"
FREEZE = DR1 / "FREEZE_2026-08-21_DIAGNOSE_REACHABLE_V1.md"
RECEIPT = DR1 / "P1_R6_DR1_RECEIPT_V1.json"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def _repair():
    return _load(DR1 / "repaired_root_v1.py", "p1_r6_dr1_repaired_root_test")


def _episode_id() -> str:
    return "dr1-unit-representation"


def _dossier() -> str:
    return (
        "A coordinate transformation and schema mapping remain uncertain while the "
        "scientific target is unchanged."
    )


def test_repaired_root_reaches_diagnose_with_evidence_present():
    repair = _repair()
    core = repair.load_frozen_native()._CORE
    ledger = repair.RootCoverageLedger()
    with repair.repaired_root(core, arm="UNIT", ledger=ledger):
        root = core.run_root_runtime(
            episode_id=_episode_id(), dossier=_dossier(), domain="synthetic"
        )

    coverage = repair.root_operator_coverage(root)
    assert "DIAGNOSE" in coverage["executed"]
    assert ledger.diagnose_reached("UNIT") == 1
    # The repair is not "run in an empty world": the dossier really is searched
    # for, retrieved and absorbed, and DIAGNOSE is reached anyway.
    assert {"SEARCH", "ABSORB", "RECONSTRUCT", "DETECT"} <= set(coverage["executed"])
    assert root.result.final_state.knowledge.evidence
    assert root.provider_responsibilities


def test_failed_encoding_is_refused_by_name_instead_of_scored():
    from orion_research_harness.operator_coverage import OperatorNotExercised

    repair = _repair()
    core = repair.load_frozen_native()._CORE
    original = repair.InMemoryVerificationProvider
    item_id = f"evidence:p1-r6-dr1:{_episode_id()}"
    try:
        # Certify the absorbed dossier: this is exactly the world the failed
        # campaign handed the runtime, and DETECT then has no branch to fire.
        repair.InMemoryVerificationProvider = lambda _ids: original(frozenset({item_id}))
        with repair.repaired_root(core, arm="NEGATIVE_CONTROL"):
            with pytest.raises(OperatorNotExercised) as raised:
                core.run_root_runtime(
                    episode_id=_episode_id(), dossier=_dossier(), domain="synthetic"
                )
    finally:
        repair.InMemoryVerificationProvider = original

    message = str(raised.value)
    assert "DIAGNOSE" in message
    assert "NEGATIVE_CONTROL" in message


def test_installing_the_repair_does_not_mutate_the_frozen_core():
    repair = _repair()
    core = repair.load_frozen_native()._CORE
    before = core.run_root_runtime
    with repair.repaired_root(core, arm="UNIT"):
        assert core.run_root_runtime is not before
    assert core.run_root_runtime is before


def test_receipt_binds_its_freeze_document_and_its_own_digest():
    from orion.transfer.v2.canonical import content_digest

    receipt = json.loads(RECEIPT.read_text())
    assert receipt["campaign_id"] == "P1U-R6-DR1"
    assert receipt["freeze_sha256"] == hashlib.sha256(FREEZE.read_bytes()).hexdigest()

    payload = {key: value for key, value in receipt.items() if key != "digest"}
    assert content_digest(payload) == receipt["digest"]


def test_receipt_records_diagnose_reached_on_every_scored_episode():
    receipt = json.loads(RECEIPT.read_text())
    precondition = receipt["operator_precondition"]
    assert precondition["required"] == ["DIAGNOSE"]
    n = int(receipt["n_episodes"])
    assert n == 48
    for arm, reached in precondition["diagnose_reached"].items():
        assert reached == n, arm
        assert precondition["root_runs_checked"][arm] == n
    assert receipt["base_native_diagnosis_nonempty"] == n
    assert receipt["grants_promotion_authority"] is False
