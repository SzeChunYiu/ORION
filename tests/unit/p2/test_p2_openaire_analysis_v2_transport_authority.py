from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ANALYZER_PATH = Path(
    "papers/orion-12-open-world-scientific-discovery/scripts/"
    "analyze_autoresearchbench_wide_openaire_matched_v2.py"
)


def _load_analyzer():
    spec = importlib.util.spec_from_file_location("p2_v2_analysis_transport_tested", ANALYZER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


analyzer = _load_analyzer()
runner = analyzer.v2_runner


def _freeze() -> dict:
    return {
        "transport_repair_evidence": {
            "pre_benchmark_probe_required": True,
            "probe_gold_access": "NONE",
            "probe_dois": ["10.5281/zenodo.8217359", "10.1038/s41586-023-06221-2"],
            "probe_min_result_count": 1,
            "probe_min_matched_doi_count": 1,
        }
    }


def _write_bundle(root: Path) -> tuple[Path, Path]:
    root.mkdir(parents=True, exist_ok=True)
    probe_path = root / "transport_probe.json"
    response_path = root / "transport_probe_response.json"
    dois = _freeze()["transport_repair_evidence"]["probe_dois"]
    url = runner.build_openaire_crosswalk_url(
        dois, page_size=runner.TRANSPORT_PROBE_PAGE_SIZE
    )
    response = {
        "results": [
            {"pid": [{"scheme": "doi", "value": dois[1]}]},
            {"pid": [{"scheme": "arxiv", "value": "2306.11152"}]},
        ]
    }
    body = json.dumps(response, sort_keys=True).encode()
    response_path.write_bytes(body)
    receipt = {
        "schema_version": runner.PROBE_SCHEMA,
        "terminal": runner.PROBE_TERMINAL,
        "http_status": 200,
        "encoding": "repeated_pid_parameters",
        "dois": dois,
        "url_sha256": hashlib.sha256(url.encode()).hexdigest(),
        "response_sha256": hashlib.sha256(body).hexdigest(),
        "result_count": 2,
        "matched_dois": [dois[1]],
        "benchmark_gold_accessed": False,
        "promotion_authorized": False,
    }
    probe_path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
    return probe_path, response_path


def _manifest(probe_path: Path, response_path: Path) -> dict:
    return {
        "campaign_version": 2,
        "transport_encoding": "repeated_pid_parameters",
        "transport_probe_terminal": runner.PROBE_TERMINAL,
        "transport_probe_sha256": runner.sha256_file(probe_path),
        "transport_probe_response_sha256": runner.sha256_file(response_path),
    }


def test_score_time_transport_evidence_requires_exact_archived_bytes(tmp_path: Path) -> None:
    probe_path, response_path = _write_bundle(tmp_path)
    manifest = _manifest(probe_path, response_path)
    good = analyzer.transport_evidence_validity(
        _freeze(), manifest, probe_path, response_path
    )
    assert good["valid"] is True
    assert good["probe_hash_matches_manifest"] is True
    assert good["response_hash_matches_manifest"] is True
    assert good["receipt_valid"] is True
    assert good["response_valid"] is True

    receipt = json.loads(probe_path.read_text())
    receipt["promotion_authorized"] = True
    probe_path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
    forged = analyzer.transport_evidence_validity(
        _freeze(), manifest, probe_path, response_path
    )
    assert forged["valid"] is False
    assert forged["probe_hash_matches_manifest"] is False
    assert forged["receipt_valid"] is False


def test_score_time_transport_evidence_refuses_raw_response_substitution(tmp_path: Path) -> None:
    probe_path, response_path = _write_bundle(tmp_path)
    manifest = _manifest(probe_path, response_path)
    response_path.write_text(
        json.dumps({"results": [{"pid": [{"scheme": "doi", "value": "10.9999/unrelated"}]}]}),
        encoding="utf-8",
    )
    validity = analyzer.transport_evidence_validity(
        _freeze(), manifest, probe_path, response_path
    )
    assert validity["valid"] is False
    assert validity["receipt_valid"] is True
    assert validity["response_valid"] is False
    assert validity["response_hash_matches_manifest"] is False


def test_score_time_transport_evidence_refuses_manifest_only_authority(tmp_path: Path) -> None:
    probe_path, response_path = _write_bundle(tmp_path)
    manifest = _manifest(probe_path, response_path)
    manifest["transport_probe_sha256"] = "0" * 64
    validity = analyzer.transport_evidence_validity(
        _freeze(), manifest, probe_path, response_path
    )
    assert validity["valid"] is False
    assert validity["receipt_valid"] is True
    assert validity["response_valid"] is True
    assert validity["probe_hash_matches_manifest"] is False

    manifest = _manifest(probe_path, response_path)
    manifest["transport_probe_response_sha256"] = "0" * 64
    validity = analyzer.transport_evidence_validity(
        _freeze(), manifest, probe_path, response_path
    )
    assert validity["valid"] is False
    assert validity["response_hash_matches_manifest"] is False


def test_zero_yield_probe_is_invalid_at_score_time(tmp_path: Path) -> None:
    probe_path, response_path = _write_bundle(tmp_path)
    receipt = json.loads(probe_path.read_text())
    receipt["result_count"] = 0
    probe_path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
    manifest = _manifest(probe_path, response_path)
    validity = analyzer.transport_evidence_validity(
        _freeze(), manifest, probe_path, response_path
    )
    assert validity["valid"] is False
    assert validity["receipt_valid"] is False
    assert "minimum identity yield" in str(validity["validation_error"])


def test_missing_archived_bundle_is_invalid_evidence_not_exception(tmp_path: Path) -> None:
    manifest_path = tmp_path / "capture" / "SHARED_ACQUISITION_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True)
    manifest = {
        "campaign_version": 2,
        "transport_encoding": "repeated_pid_parameters",
        "transport_probe_terminal": runner.PROBE_TERMINAL,
        "transport_probe_sha256": "a" * 64,
        "transport_probe_response_sha256": "b" * 64,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    validity = analyzer.resolve_transport_evidence(
        _freeze(), manifest, manifest_path, None
    )
    assert validity["valid"] is False
    assert validity["receipt_valid"] is False
    assert validity["response_valid"] is False
    assert "not found" in str(validity["validation_error"])


def test_missing_raw_response_is_invalid_evidence_not_exception(tmp_path: Path) -> None:
    manifest_path = tmp_path / "capture" / "SHARED_ACQUISITION_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True)
    probe_path, response_path = _write_bundle(manifest_path.parent)
    response_path.unlink()
    manifest = {
        "campaign_version": 2,
        "transport_encoding": "repeated_pid_parameters",
        "transport_probe_terminal": runner.PROBE_TERMINAL,
        "transport_probe_sha256": runner.sha256_file(probe_path),
        "transport_probe_response_sha256": "b" * 64,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    validity = analyzer.resolve_transport_evidence(
        _freeze(), manifest, manifest_path, None
    )
    assert validity["valid"] is False
    assert validity["response_valid"] is False
    assert "not found" in str(validity["validation_error"])


def test_ambiguous_archived_bundles_are_invalid_evidence_not_exception(tmp_path: Path) -> None:
    manifest_path = tmp_path / "capture" / "SHARED_ACQUISITION_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True)
    manifest = {
        "campaign_version": 2,
        "transport_encoding": "repeated_pid_parameters",
        "transport_probe_terminal": runner.PROBE_TERMINAL,
        "transport_probe_sha256": "a" * 64,
        "transport_probe_response_sha256": "b" * 64,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    _write_bundle(manifest_path.parent / "a")
    _write_bundle(manifest_path.parent / "b")
    validity = analyzer.resolve_transport_evidence(
        _freeze(), manifest, manifest_path, None
    )
    assert validity["valid"] is False
    assert validity["receipt_valid"] is False
    assert "ambiguous" in str(validity["validation_error"])


def test_missing_bundle_forces_frozen_cannot_check_terminal(monkeypatch, tmp_path: Path) -> None:
    freeze = _freeze()
    freeze.update(
        {
            "schema_version": analyzer.V2_SCHEMA,
            "terminal_rule": {
                "invalid_or_transport_terminal": "P2_WIDE_EXTERNAL_V2_CANNOT_CHECK",
                "positive_terminal": "P2_WIDE_EXTERNAL_V2_SUPPORTED",
                "negative_valid_terminal": "P2_WIDE_EXTERNAL_V2_NOT_SUPPORTED",
            },
            "claim_boundary": "test-boundary",
        }
    )
    freeze_path = tmp_path / "freeze.json"
    freeze_path.write_text(json.dumps(freeze), encoding="utf-8")
    manifest_path = tmp_path / "capture" / "SHARED_ACQUISITION_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True)
    manifest = {
        "campaign_version": 2,
        "transport_encoding": "repeated_pid_parameters",
        "transport_probe_terminal": runner.PROBE_TERMINAL,
        "transport_probe_sha256": "a" * 64,
        "transport_probe_response_sha256": "b" * 64,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    output_path = tmp_path / "result.json"

    monkeypatch.setattr(
        analyzer.v1,
        "analyze",
        lambda **kwargs: {
            "schema_version": "orion.p2.wide-openaire-matched-result.v1",
            "terminal": "P2_WIDE_EXTERNAL_V2_SUPPORTED",
            "validity": {},
            "all_validity_conditions": True,
            "scientific_supported": True,
            "scientific_rule": {},
        },
    )

    result = analyzer.analyze_v2(
        freeze_path=freeze_path,
        manifest_path=manifest_path,
        transport_probe_path=None,
        transport_probe_response_path=None,
        baseline_eval_path=tmp_path / "baseline.json",
        orion_eval_path=tmp_path / "orion.json",
        diagnostic_eval_path=tmp_path / "diagnostic.json",
        baseline_candidate_path=tmp_path / "baseline-candidate.jsonl",
        orion_candidate_path=tmp_path / "orion-candidate.jsonl",
        diagnostic_candidate_path=tmp_path / "diagnostic-candidate.jsonl",
        output_path=output_path,
    )
    assert result["terminal"] == "P2_WIDE_EXTERNAL_V2_CANNOT_CHECK"
    assert result["all_validity_conditions"] is False
    assert result["validity"]["v2_transport_probe_receipt_valid"] is False
    assert result["validity"]["v2_transport_probe_response_valid"] is False
    assert output_path.exists()
