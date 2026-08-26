"""Fail-closed manuscript and ledger binding for the P2-DES-01 result."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "paper-02-open-world-scientific-discovery"
RESULT = ROOT / "research" / "orion-epistemic-state-v1" / "results" / "P2-DES-01"
TERMINAL = "CANNOT_CHECK_STRONG_DONOR_OR_TRANSFER_BINDING_UNAVAILABLE"
PACKAGE_TERMINAL = "P2_NARROWED_RETAINED__CURRENT_PACKAGE_NOT_SUBMISSION_READY"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_integrated_sidecar_binds_p2_des_without_promotion() -> None:
    sidecar = load(PAPER / "evidence" / "P2_INTEGRATED_CLAIM_BINDINGS_V1.json")
    facts = sidecar["facts"]["p2_des_01"]

    assert facts["topic_count"] == 50
    assert facts["policy_count"] == 8
    assert facts["case_policy_rows"] == 400
    assert facts["licensed_jump_topic_count"] == 0
    assert facts["structural_minus_ideal_mean_recall"] == -0.004218226241746187
    assert facts["structural_vs_ideal_harmful_topic_count"] == 33
    assert facts["material_donor_status"] == "CANNOT_CHECK_UNAVAILABLE_NOT_SUBSTITUTED"
    assert facts["transfer_terminal"] == "CANNOT_CHECK_TRANSFER_WORLDS_UNAVAILABLE"
    assert facts["external_independence"] == "CANNOT_CHECK"
    assert facts["terminal"] == TERMINAL
    assert facts["grants_paper_authority"] is False

    for artifact_id in facts["source_artifact_ids"]:
        binding = sidecar["source_artifacts"][artifact_id]
        path = ROOT / binding["path"]
        payload = path.read_bytes()
        assert len(payload) == binding["bytes"]
        assert hashlib.sha256(payload).hexdigest() == binding["sha256"]


def test_p2_des_is_visible_in_manuscript_and_both_ledgers() -> None:
    results = (PAPER / "manuscript" / "sections" / "results.tex").read_text(
        encoding="utf-8"
    )
    normalized_results = " ".join(results.split())
    main = (PAPER / "manuscript" / "main.tex").read_text(encoding="utf-8")
    normalized_main = " ".join(main.split())
    machine = load(PAPER / "protocol" / "CLAIM_LEDGER_V1.json")
    human = (PAPER / "evidence" / "CLAIM_LEDGER_V2.md").read_text(encoding="utf-8")
    normalized_human = " ".join(human.split())

    assert "\\label{tab:p2-evidence-authority}" in results
    assert "P2-DES-01" in normalized_results
    assert "50 topics" in normalized_results
    assert "eight policies" in normalized_results
    assert "400 case--policy rows" in normalized_results
    assert "no structural jump" in normalized_results
    assert "internal ideal donor product" in normalized_results
    assert (
        "not comparable across changed access, world or authority contracts"
        in normalized_main
    )

    asserted = {
        row["claim_id"]: row
        for row in machine["claims"]
        if row.get("manuscript_status") == "ASSERTED"
    }
    for claim_id in ("P2-I-R18", "P2-I-L16", "P2-I-C26"):
        assert claim_id in asserted
        assert asserted[claim_id]["support_artifacts"]

    assert "P2-DES-01 bounded donor/route discriminator" in normalized_human
    assert TERMINAL in normalized_human
    assert "no full P2 superiority" in normalized_human


def test_p2_readiness_surfaces_match_superseded_open_package() -> None:
    manifest = load(PAPER / "journal_package" / "MANIFEST.json")
    current_package = next(
        claim for claim in manifest["claims"] if claim["id"] == "P2.CURRENT_PACKAGE"
    )

    assert manifest["declared_paper_terminal"] == PACKAGE_TERMINAL
    assert manifest["package_status"] == "SUPERSEDED"
    assert current_package["status"] == "OPEN"
    assert current_package["current_claim"] is True

    readme = (PAPER / "README.md").read_text(encoding="utf-8")
    assert PACKAGE_TERMINAL in readme
    assert "PEER_REVIEW_READY" not in readme
    assert "current submission authority false" in readme
    assert "`P2.CURRENT_PACKAGE` still `OPEN`" in readme

    historical = (
        PAPER / "evidence" / "PEER_REVIEW_READY_BOUNDED_V2.md"
    ).read_text(encoding="utf-8")
    superseded_marker = (
        "SUPERSEDED_HISTORICAL_ATTESTATION__NOT_CURRENT_SUBMISSION_AUTHORITY"
    )
    historical_terminal = "`ORION-P2 = PEER_REVIEW_READY`"
    assert superseded_marker in historical
    assert PACKAGE_TERMINAL in historical
    assert historical_terminal in historical
    assert historical.index(superseded_marker) < historical.index(historical_terminal)
