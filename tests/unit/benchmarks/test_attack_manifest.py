#!/usr/bin/env python3
"""Tests for the P4 ATTACK_MANIFEST_V1.jsonl and CUSTODY_MANIFEST_V1.json.

Validates schema conformance, calibration-corpus custody distribution, hash
integrity, and the fail-closed custody lifecycle for DESIGN_FROZEN or
EXECUTION_FROZEN protocol states.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = ROOT / "papers" / "orion-14-verified-scientific-discovery" / "protocol"
MANIFEST = PROTOCOL / "ATTACK_MANIFEST_V1.jsonl"
CUSTODY = PROTOCOL / "CUSTODY_MANIFEST_V1.json"
SCHEMA = PROTOCOL / "ATTACK_CASE_SCHEMA_V1.json"
GENERATOR = PROTOCOL / "generate_attack_manifest.py"

EXPECTED_FAMILIES = [
    "CLEAN_POSITIVE",
    "WRONG_SOURCE",
    "CONTENT_SUBSTITUTION",
    "SOURCE_CONFLATION",
    "POOLED_SUPPORT_WRONG_OWNER",
    "CITED_NON_INFLUENTIAL",
    "WEAK_CHECKER",
    "SAME_LANE_CHECKER",
    "POSTHOC_CHECKER_EVALUATOR",
    "SEARCH_TIME_CONTAMINATION",
    "EVALUATOR_TAMPER",
    "HOLDOUT_ACCESS",
    "INSUFFICIENT_EVIDENCE",
]

MIN_PER_FAMILY = 3


def _load_cases() -> list[dict]:
    assert MANIFEST.exists(), f"missing {MANIFEST}"
    lines = [ln for ln in MANIFEST.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return [json.loads(ln) for ln in lines]


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


@pytest.fixture(scope="module")
def cases() -> list[dict]:
    return _load_cases()


@pytest.fixture(scope="module")
def custody() -> dict:
    assert CUSTODY.exists()
    return json.loads(CUSTODY.read_text(encoding="utf-8"))


def test_manifest_exists_and_nonempty(cases):
    assert len(cases) >= 16, "attack manifest must have at least 16 cases"


def test_all_schema_files_exist():
    for p in (SCHEMA, CUSTODY, GENERATOR):
        assert p.exists(), f"missing {p.name}"


def test_every_family_present(cases):
    fams = {c["attack_family"] for c in cases}
    assert set(EXPECTED_FAMILIES) == fams, "family set must match schema enum"


def test_every_family_has_minimum_cases(cases):
    counts = Counter(c["attack_family"] for c in cases)
    for fam in EXPECTED_FAMILIES:
        assert counts[fam] >= MIN_PER_FAMILY, f"{fam} has {counts[fam]} < {MIN_PER_FAMILY} cases"


def test_schema_required_fields_present(cases):
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = set(schema["required"])
    for c in cases:
        missing = required - set(c.keys())
        assert not missing, f"{c['case_id']} missing {missing}"


def test_schema_enums_respected(cases):
    families = set(EXPECTED_FAMILIES)
    custody_classes = {"PUBLIC_CLEAN", "PUBLIC_HOSTILE", "PROTECTED_HOSTILE", "PROTECTED_HOLDOUT"}
    terminals = {"PROMOTE", "BLOCK", "CANNOT_CHECK"}
    for c in cases:
        assert c["attack_family"] in families
        assert c["custody_class"] in custody_classes
        assert c["expected_authority_terminal"] in terminals
        assert c["protected_gold"]["expected_authority_terminal"] in terminals
        assert c["protected_gold"]["semantic_support"] in {
            "SUPPORTED", "CONTRADICTED", "INSUFFICIENT", "UNRESOLVED"}
        assert c["attack_label_visible_to_candidate"] is False


def test_artifact_hash_integrity(cases):
    for c in cases:
        expected = c.pop("artifact_hash")
        serialized = json.dumps(c, sort_keys=True, separators=(",", ":"))
        assert _sha256(serialized) == expected, f"artifact_hash mismatch for {c['case_id']}"


def test_hash_computations_match_generator(cases):
    """Recompute the generator's hashes deterministically from the raw text."""
    def content_hash(case_id, evidence):
        return _sha256(evidence + case_id)

    def provenance_hash(case_id, source, evidence):
        return _sha256(source + evidence + case_id)

    for c in cases:
        ev = c["evidence_objects"][0]
        assert ev["content_hash"] == content_hash(c["case_id"], c["candidate_visible"]["evidence_text"])
        assert ev["provenance_hash"] == provenance_hash(
            c["case_id"], c["candidate_visible"]["source_text"], c["candidate_visible"]["evidence_text"])


def test_terminal_consistency_with_gold(cases):
    """expected_authority_terminal must match protected_gold.expected_authority_terminal."""
    for c in cases:
        assert c["expected_authority_terminal"] == c["protected_gold"]["expected_authority_terminal"]


def test_semantic_support_implies_terminal(cases):
    """INSUFFICIENT support implies CANNOT_CHECK or BLOCK; CONTRADICTED implies BLOCK."""
    for c in cases:
        support = c["protected_gold"]["semantic_support"]
        terminal = c["protected_gold"]["expected_authority_terminal"]
        if support == "INSUFFICIENT":
            assert terminal in ("CANNOT_CHECK", "BLOCK"), (
                f"{c['case_id']}: INSUFFICIENT support with terminal {terminal} "
                f"(expected CANNOT_CHECK or BLOCK)")
        if support == "CONTRADICTED":
            assert terminal == "BLOCK", c["case_id"]


def test_clean_positive_custody(cases):
    for c in cases:
        if c["attack_family"] == "CLEAN_POSITIVE":
            assert c["custody_class"] == "PUBLIC_CLEAN"
            assert c["protected_gold"]["expected_authority_terminal"] == "PROMOTE"
            assert not c["protected_gold"]["contaminated"]


def test_protected_holdout_families(cases):
    for c in cases:
        if c["attack_family"] in ("SEARCH_TIME_CONTAMINATION", "EVALUATOR_TAMPER", "HOLDOUT_ACCESS"):
            assert c["custody_class"] == "PROTECTED_HOLDOUT"


def test_protected_hostile_families(cases):
    for c in cases:
        if c["attack_family"] in ("CONTENT_SUBSTITUTION", "WEAK_CHECKER",
                                  "SAME_LANE_CHECKER", "POSTHOC_CHECKER_EVALUATOR"):
            assert c["custody_class"] == "PROTECTED_HOSTILE"


def test_custody_manifest_counts_match(cases, custody):
    dist = Counter(c["custody_class"] for c in cases)
    assert dist["PUBLIC_CLEAN"] == custody["custody_distribution"]["PUBLIC_CLEAN"]
    assert dist["PUBLIC_HOSTILE"] == custody["custody_distribution"]["PUBLIC_HOSTILE"]
    assert dist["PROTECTED_HOSTILE"] == custody["custody_distribution"]["PROTECTED_HOSTILE"]
    assert dist["PROTECTED_HOLDOUT"] == custody["custody_distribution"]["PROTECTED_HOLDOUT"]
    assert len(cases) == custody["total_cases"]


def test_custody_manifest_frozen(custody):
    assert custody["protocol_id"] == "P4.protected-authority.v1"
    assert custody["created_before_outcome_access"] is True
    assert custody["control"]["evaluator_hash_frozen"] is True
    assert custody["control"]["access_telemetry_retained"] is True

    split_hashes = custody["control"]["split_hashes"]
    final = custody.get("final_protected_campaign")
    if final is None:
        # DESIGN_FROZEN lifecycle: execution identities remain prospective.
        assert all(v == "UNBOUND" for v in split_hashes.values())
        return

    # EXECUTION_FROZEN lifecycle: no stale UNBOUND values are admissible and the
    # public custody ledger must agree exactly with the independently prepared
    # hidden campaign commitments.
    assert split_hashes == {
        "public_claim_evidence": final["public_claim_evidence_sha256"],
        "protected_attack_set": final["protected_attack_set_sha256"],
        "clean_positive_set": final["clean_positive_set_sha256"],
    }
    assert all(v != "UNBOUND" for v in split_hashes.values())
    assert final["attack_label_visible_to_candidate"] is False
    assert final["case_count"] == 420
    assert final["ambiguous_cases"] == 0


def test_generator_regenerates_identical_manifest():
    """The committed calibration manifest is byte-identical to a fresh generator run."""
    import subprocess
    original = Path(MANIFEST).read_text(encoding="utf-8")
    out = subprocess.run(
        ["python3", str(GENERATOR)], capture_output=True, text=True, cwd=str(PROTOCOL))
    assert out.returncode == 0, out.stderr
    # The generator writes to MANIFEST; verify it did not change.
    regenerated = Path(MANIFEST).read_text(encoding="utf-8")
    assert regenerated == original, "generator run changed the manifest — not deterministic"


def test_unique_case_ids(cases):
    ids = [c["case_id"] for c in cases]
    assert len(ids) == len(set(ids)), "case_id must be unique"


def test_label_hiding_covers_sensitive_fields(custody):
    hidden = set(custody["label_hiding"]["hidden_from_candidate"])
    sensitive = {
        "attack_family",
        "protected_gold.claim_correct",
        "protected_gold.source_owner_correct",
        "protected_gold.semantic_support",
        "protected_gold.contaminated",
        "expected_authority_terminal",
        "custody_class",
    }
    assert sensitive.issubset(hidden)


def test_custody_distribution_sums_to_total(custody):
    dist = custody["custody_distribution"]
    assert sum(dist.values()) == custody["total_cases"]
