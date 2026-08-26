#!/usr/bin/env python3
"""Fail-closed validator for the content-bound Q1-C resource/literature bundle."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
ARXIV_VERSION = re.compile(r"^\d{4}\.\d{4,5}v\d+$")
MAP_DIRECTIONS = {"equality", "upper bound", "lower bound", "heuristic proxy"}
REQUIRED_ROW_FIELDS = {
    "abstract_object", "production_object", "counting_map", "map_direction",
    "additional_moves", "ancilla_model", "measurement_and_feed_forward_model",
    "connectivity_model", "parallelism_model", "error_correction_model",
    "resource_metric", "conversion_theorem", "failure_cases", "measured_benchmark",
    "uncertainty_or_interval", "authority_ceiling",
}


def _run(repo: Path, *args: str) -> bytes:
    done = subprocess.run(args, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if done.returncode:
        raise AssertionError(f"command failed: {' '.join(args)}\n{done.stderr.decode(errors='replace')}")
    return done.stdout


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def validate_binding(repo: Path, binding: dict[str, Any]) -> None:
    assert binding["schema"] == "ORION.Q1C.SourceBindingR9.v1"
    commit = binding["base_commit_sha"]
    assert SHA40.fullmatch(commit)
    _run(repo, "git", "cat-file", "-e", f"{commit}^{{commit}}")
    _run(repo, "git", "merge-base", "--is-ancestor", commit, "HEAD")
    assert binding["selection"]["portfolio_authoritative_theorem_selected"] is False
    assert binding["authority"] == {
        "content_binding_complete_for_q1_c_inputs": True,
        "grants_journal_authority": False,
        "grants_novelty_authority": False,
        "grants_production_resource_authority": False,
        "proves_theorem": False,
    }
    assert binding["terminal"] == "Q1_C_INPUTS_CONTENT_BOUND__PORTFOLIO_AUTHORITY_BINDING_STILL_REQUIRED"
    roles = set()
    for record in binding["source_objects"]:
        roles.add(record["role"])
        assert SHA40.fullmatch(record["git_blob_sha"])
        assert SHA64.fullmatch(record["sha256"])
        path = record["path"]
        blob = _run(repo, "git", "rev-parse", f"{commit}:{path}").decode().strip()
        data = _run(repo, "git", "show", f"{commit}:{path}")
        assert blob == record["git_blob_sha"], path
        assert _sha(data) == record["sha256"], path
        assert len(data) == record["bytes"], path
    assert {"manuscript", "claim_ledger", "analytic_proof", "objective_definition", "registered_theorem_checker", "registered_theorem_receipt", "production_accounting_protocol", "production_accounting_receipt"} <= roles
    for record in binding["tree_objects"]:
        assert SHA40.fullmatch(record["git_tree_sha"])
        actual = _run(repo, "git", "rev-parse", f"{commit}:{record['path']}").decode().strip()
        assert actual == record["git_tree_sha"]


def validate_source_reference(repo: Path, value: dict[str, Any]) -> None:
    path = repo / value["file"]
    assert path.is_file()
    assert _sha(path.read_bytes()) == value["sha256"]
    assert SHA40.fullmatch(value["base_commit_sha"])


def validate_resource(repo: Path, resource: dict[str, Any]) -> None:
    assert resource["schema"] == "ORION.Q1.ProductionResourceMapR9.v1"
    validate_source_reference(repo, resource["source_binding"])
    assert resource["conversion_contract"]["status"] == "CONDITIONAL_EXACT_LOGICAL_CIRCUIT_ACCOUNTING"
    rows = resource["resource_rows"]
    assert len(rows) >= 6
    assert len({row["id"] for row in rows}) == len(rows)
    for row in rows:
        assert REQUIRED_ROW_FIELDS <= set(row), row.get("id")
        assert row["map_direction"] in MAP_DIRECTIONS
        for key in REQUIRED_ROW_FIELDS - {"additional_moves", "failure_cases"}:
            assert str(row[key]).strip() and "BIND_" not in str(row[key]), (row["id"], key)
        assert isinstance(row["additional_moves"], list)
        assert isinstance(row["failure_cases"], list) and row["failure_cases"]
        if row["map_direction"] == "equality":
            assert row["failure_cases"]
            assert "premise" in row["authority_ceiling"].lower() or "architecture" in row["authority_ceiling"].lower() or "frozen grammar" in row["authority_ceiling"].lower()
    assert resource["production_headline"]["terminal"] == "PARTIAL_RESOURCE_MAP"
    headline = resource["production_headline"]["text"].lower()
    for forbidden in ("t-count", "depth", "qubit", "spacetime", "quantum-advantage"):
        assert forbidden in headline
    unmapped = {row["metric"]: row["status"] for row in resource["unmapped_metrics"]}
    assert unmapped["T count / magic states"] == "NO_DIRECT_MAP"
    assert unmapped["T depth / magic-state throughput"] == "CANNOT_CHECK"
    assert unmapped["logical and physical qubits"] == "CANNOT_CHECK"
    assert unmapped["fault-tolerant spacetime volume and failure probability"] == "CANNOT_CHECK"
    authority = resource["authority"]
    assert authority["grants_conditional_logical_gate_count_authority"] is True
    for key in ("grants_general_production_resource_authority", "grants_fault_tolerant_resource_authority", "grants_hardware_authority", "grants_journal_authority"):
        assert authority[key] is False
    assert resource["review"]["independent_quantum_reviewer"] == "NOT_PRESENT"
    assert "donor-exact" in resource["internal_crosscheck"]["adverse_result_preserved"]


def validate_literature(repo: Path, literature: dict[str, Any]) -> None:
    assert literature["schema"] == "ORION.Q1C.CurrentLiteratureSubtractionR9.v1"
    validate_source_reference(repo, literature["source_binding"])
    manifest = literature["search_manifest"]
    assert manifest["lawful_access"]
    assert len(manifest["arxiv_queries"]) >= 7
    assert len(manifest["search_limits"]) >= 4
    for query in manifest["arxiv_queries"]:
        assert SHA64.fullmatch(query["response_sha256"])
        assert query["returned"] <= query["total_results"]
    rows = literature["nearest_work_rows"]
    assert len(rows) >= 15
    assert len({row["source_id"] for row in rows}) == len(rows)
    joined_categories = " ".join(row["category"].lower() for row in rows)
    for category in ("donor", "pauli", "symplectic", "matroid", "clifford+t", "block-encoding", "surface-code", "benchmark"):
        assert category in joined_categories, category
    for row in rows:
        identity = row["identity"]
        assert ARXIV_VERSION.fullmatch(identity["arxiv_version"]), row["source_id"]
        assert SHA64.fullmatch(identity["arxiv_metadata_sha256"])
        assert SHA64.fullmatch(identity["arxiv_pdf_sha256"])
        assert row["inspection_status"] == "PRIMARY_FULL_TEXT_INSPECTED"
        assert row["direct_equivalent_of_frozen_kappa_r6m_two_located"] is False
        assert row["external_novelty_authority"] is False
        assert row["what_source_owns"] and row["subtraction_from_q1"] and row["residual_q1_claim_after_subtraction"]
    summary = literature["subtraction_summary"]
    assert summary["direct_equivalent_located_in_bounded_search"] is False
    assert summary["novelty_established"] is False
    assert literature["review"] == {
        "independent_q1_d_reviewer_present": False,
        "review_terminal": "NOVELTY_NOT_ESTABLISHED",
        "same_lane_review_only": True,
        "submission_terminal": "Q1_NOVELTY_OPEN",
    }
    assert len(literature["cannot_check"]) >= 6
    assert literature["terminal"] == "NOVELTY_NOT_ESTABLISHED"
    for key in ("grants_external_novelty_authority", "grants_production_resource_authority", "grants_journal_authority"):
        assert literature["authority"][key] is False


def main() -> None:
    here = Path(__file__).resolve()
    repo = Path(_run(here.parent, "git", "rev-parse", "--show-toplevel").decode().strip())
    binding = _load(here.with_name("Q1_C_SOURCE_BINDING_R9.json"))
    resource = _load(here.with_name("Q1_C_PRODUCTION_RESOURCE_MAP_R9.json"))
    literature = _load(here.with_name("Q1_C_CURRENT_LITERATURE_SUBTRACTION_R9.json"))
    validate_binding(repo, binding)
    validate_resource(repo, resource)
    validate_literature(repo, literature)
    print(json.dumps({
        "schema": "ORION.Q1C.AuthorityCheckR9.v1",
        "binding_terminal": binding["terminal"],
        "resource_terminal": resource["production_headline"]["terminal"],
        "literature_terminal": literature["terminal"],
        "journal_authority": False,
        "ok": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
