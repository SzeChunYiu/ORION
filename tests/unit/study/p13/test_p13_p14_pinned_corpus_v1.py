"""P13+P14 pinned-corpus + objective-gold contract freeze (issue #1086).

Tamper tests: each mutation of the frozen artifacts must flip the checker to
VIOLATIONS (exit 1); untouched copies must stay green (exit 0); absent
artifacts must return CANNOT_CHECK (exit 2).

Known boundary: a fully forged but well-formed licence record (spdx id +
evidence url + evidence sha all invented, counts patched consistently) on an
entry whose organisation already has eligible members passes the offline
checker. That class is defended by git byte history, the SHA256SUMS manifest
binding, and re-verification of evidence_url/evidence_fetch_sha256 against
the live API — the same layering as the P10 freeze, not by this checker.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/orion-23-responsibility-carrying-state"
CORPUS = PAPER / "P13_P14_PINNED_REPOSITORY_CORPUS_V1.json"
CONTRACT = PAPER / "P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1.json"
RULE = PAPER / "P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md"
CONTRACT_DOC = PAPER / "P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1.md"

EXPECTED_RULE_SHA = "3656565539ea89742dd0f876347ba0b7ec918dfe605d95ab691c5323b77f8ce9"
EXPECTED_CONTRACT_SHA = "43af90733fb1a1f7fadd261d1a9ff41fcb20c1ec2e394626be2850ed8f65aed0"

BOUND_FILES = (
    "P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md",
    "P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1.json",
    "P13_P14_OBJECTIVE_GOLD_DERIVATION_CONTRACT_V1.md",
    "P13_P14_PINNED_REPOSITORY_CORPUS_V1.json",
)


def _checker():
    spec = importlib.util.spec_from_file_location(
        "check_p13_p14_pinned_corpus_v1",
        PAPER / "check_p13_p14_pinned_corpus_v1.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _pristine_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Copy the four frozen artifacts into a scratch repo root and point the
    checker's REPO_ROOT at it, so mutations never touch the real tree."""
    module_root = tmp_path / "papers/orion-23-responsibility-carrying-state"
    module_root.mkdir(parents=True)
    for name in BOUND_FILES:
        shutil.copy(PAPER / name, module_root / name)
    repo_root = tmp_path
    return repo_root, module_root / CORPUS.name, module_root / CONTRACT.name


def _run_on_tree(tmp_path: Path, mutate=None) -> int:
    chk = _checker()
    repo_root, corpus_copy, contract_copy = _pristine_tree(tmp_path)
    if mutate is not None:
        doc = json.loads(corpus_copy.read_text(encoding="utf-8"))
        mutate(doc, corpus_copy, contract_copy)
        corpus_copy.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    chk.REPO_ROOT = repo_root
    return chk.run(corpus_copy, contract_copy)


def test_pristine_artifacts_pass() -> None:
    assert _checker().run(CORPUS, CONTRACT) == 0


def test_missing_artifact_returns_cannot_check(tmp_path: Path) -> None:
    chk = _checker()
    assert chk.run(tmp_path / "absent.json", tmp_path / "absent2.json") == 2


def test_unparseable_artifact_returns_cannot_check(tmp_path: Path) -> None:
    chk = _checker()
    repo_root, corpus_copy, contract_copy = _pristine_tree(tmp_path)
    corpus_copy.write_text("{not json", encoding="utf-8")
    chk.REPO_ROOT = repo_root
    assert chk.run(corpus_copy, contract_copy) == 2


def test_frozen_sha_bindings_are_the_committed_values() -> None:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    assert corpus["binding"]["rule"]["sha256"] == EXPECTED_RULE_SHA
    assert corpus["binding"]["derivation_contract"]["sha256"] == EXPECTED_CONTRACT_SHA
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["gold_rule_binding"]["sha256"] == EXPECTED_RULE_SHA


def test_box_minimums_hold_on_both_counts() -> None:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    entries = corpus["entries"]
    orgs = {e["org_login"] for e in entries}
    elig = [e for e in entries if e["gold_eligible"]]
    elig_orgs = {e["org_login"] for e in elig}
    assert 30 <= len(entries) <= 50
    assert len(orgs) >= 5
    assert 30 <= len(elig) <= 50
    assert len(elig_orgs) >= 5
    assert all(corpus["summary"]["box_minimums_met"].values())


def test_no_orion_or_szechunyiu_subject() -> None:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    lowered = {e["repo_id"].lower() for e in corpus["entries"]}
    assert not any("szechunyiu" in rid or "/orion" in rid or rid.startswith("orion/") for rid in lowered)


def test_gold_eligible_flip_is_detected(tmp_path: Path) -> None:
    def mutate(doc, _c, _ct):
        idx = next(i for i, e in enumerate(doc["entries"]) if not e["gold_eligible"])
        doc["entries"][idx]["gold_eligible"] = True
    assert _run_on_tree(tmp_path, mutate) == 1


def test_forged_verified_license_without_spdx_is_detected(tmp_path: Path) -> None:
    def mutate(doc, _c, _ct):
        idx = next(i for i, e in enumerate(doc["entries"]) if not e["gold_eligible"])
        doc["entries"][idx]["license"]["verification"] = "VERIFIED_WITH_URL_AND_DATE"
    assert _run_on_tree(tmp_path, mutate) == 1


def test_fully_forged_license_is_detected_via_summary_drift(tmp_path: Path) -> None:
    def mutate(doc, _c, _ct):
        idx = next(i for i, e in enumerate(doc["entries"]) if not e["gold_eligible"])
        doc["entries"][idx]["license"].update({
            "verification": "VERIFIED_WITH_URL_AND_DATE",
            "spdx_id": "MIT",
            "evidence_url": "https://example.com/lic",
            "evidence_fetch_sha256": "a" * 64,
        })
        doc["entries"][idx]["gold_eligible"] = True
    assert _run_on_tree(tmp_path, mutate) == 1


def test_orion_subject_injection_is_detected(tmp_path: Path) -> None:
    def mutate(doc, _c, _ct):
        doc["entries"].append({
            "repo_id": "SzeChunYiu/ORION",
            "org_login": "SzeChunYiu",
            "owner_entity": "same owner",
            "url": "https://github.com/SzeChunYiu/ORION",
            "pinned_ref": "main",
            "pinned_sha": "0" * 40,
            "retrieval_utc": "2026-08-24T00:00:00+00:00",
            "license": {
                "spdx_id": None,
                "verification": "CANNOT_CHECK__LICENSE_UNCLEAR",
                "evidence_api": None,
                "evidence_field": None,
                "evidence_url": None,
                "evidence_fetch_sha256": None,
            },
            "gold_eligible": False,
        })
    assert _run_on_tree(tmp_path, mutate) == 1


def test_dropping_below_box_minimum_is_detected(tmp_path: Path) -> None:
    def mutate(doc, _c, _ct):
        doc["entries"] = doc["entries"][:29]
    assert _run_on_tree(tmp_path, mutate) == 1


def test_binding_sha_drift_is_detected(tmp_path: Path) -> None:
    def mutate(doc, _c, _ct):
        doc["binding"]["rule"]["sha256"] = "f" * 64
    assert _run_on_tree(tmp_path, mutate) == 1


def test_contract_binding_sha_drift_is_detected(tmp_path: Path) -> None:
    def mutate(doc, _c, _ct):
        doc["binding"]["derivation_contract"]["sha256"] = "e" * 64
    assert _run_on_tree(tmp_path, mutate) == 1


def test_summary_count_drift_is_detected(tmp_path: Path) -> None:
    def mutate(doc, _c, _ct):
        doc["summary"]["repository_count"] = 99
    assert _run_on_tree(tmp_path, mutate) == 1


def test_forged_results_exist_is_detected(tmp_path: Path) -> None:
    def mutate(doc, _c, _ct):
        doc["results_exist"] = True
    assert _run_on_tree(tmp_path, mutate) == 1


def test_forged_box_verdict_is_detected(tmp_path: Path) -> None:
    def mutate(doc, _c, _ct):
        doc["box_verdicts"]["box_pinned_repository_corpus"]["verdict"] = "DONE"
    assert _run_on_tree(tmp_path, mutate) == 1


def test_contract_verdict_forgery_is_detected(tmp_path: Path) -> None:
    def mutate(_doc, _c, contract_copy):
        contract = json.loads(contract_copy.read_text(encoding="utf-8"))
        contract["box_verdicts"]["box_objective_gold_derivation"]["verdict"] = "DONE"
        contract_copy.write_text(json.dumps(contract, indent=1), encoding="utf-8")
    assert _run_on_tree(tmp_path, mutate) == 1


def test_cannot_check_label_removed_from_fact_class_is_detected(tmp_path: Path) -> None:
    def mutate(_doc, _c, contract_copy):
        contract = json.loads(contract_copy.read_text(encoding="utf-8"))
        contract["admissible_fact_classes"][0]["predicate"]["label_type"] = (
            "EXISTS_DIGEST_MATCH | ABSENT | DIGEST_MISMATCH"
        )
        contract_copy.write_text(json.dumps(contract, indent=1), encoding="utf-8")
    assert _run_on_tree(tmp_path, mutate) == 1


def test_dropped_fact_class_is_detected(tmp_path: Path) -> None:
    def mutate(_doc, _c, contract_copy):
        contract = json.loads(contract_copy.read_text(encoding="utf-8"))
        contract["admissible_fact_classes"] = contract["admissible_fact_classes"][:4]
        contract_copy.write_text(json.dumps(contract, indent=1), encoding="utf-8")
    assert _run_on_tree(tmp_path, mutate) == 1


def test_weakened_license_gate_is_detected(tmp_path: Path) -> None:
    def mutate(_doc, _c, contract_copy):
        contract = json.loads(contract_copy.read_text(encoding="utf-8"))
        contract["derivation_preconditions"]["license_gate"] = "derive gold freely"
        contract_copy.write_text(json.dumps(contract, indent=1), encoding="utf-8")
    assert _run_on_tree(tmp_path, mutate) == 1


def test_broken_verbatim_rule_embed_is_detected(tmp_path: Path) -> None:
    chk = _checker()
    repo_root, corpus_copy, contract_copy = _pristine_tree(tmp_path)
    doc_copy = contract_copy.parent / CONTRACT_DOC.name
    doc_copy.write_text(
        doc_copy.read_text(encoding="utf-8").replace(
            "machine-checkable facts:", "machine-checkable facts (relaxed):", 1),
        encoding="utf-8")
    chk.REPO_ROOT = repo_root
    assert chk.run(corpus_copy, contract_copy) == 1


def test_tampered_rule_file_is_detected(tmp_path: Path) -> None:
    chk = _checker()
    repo_root, corpus_copy, contract_copy = _pristine_tree(tmp_path)
    rule_copy = contract_copy.parent / RULE.name
    rule_copy.write_text(rule_copy.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8")
    chk.REPO_ROOT = repo_root
    assert chk.run(corpus_copy, contract_copy) == 1
