from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "paper-02-open-world-scientific-discovery"
RUNNER_PATH = PAPER / "scripts" / "run_autoresearchbench_wide_openaire_matched_v3.py"
ANALYZER_PATH = PAPER / "scripts" / "analyze_autoresearchbench_wide_openaire_matched_v3.py"
V3_FREEZE = PAPER / "protocol" / "P2_WIDE_OPENAIRE_MATCHED_FREEZE_V3.json"
V2_FREEZE = PAPER / "protocol" / "P2_WIDE_OPENAIRE_MATCHED_FREEZE_V2.json"
IDENTITY = PAPER / "evidence" / "external_results" / "P2_OPENAIRE_IDENTITY_PROBE_V1.json"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _transport_bundle(module, tmp_path: Path) -> tuple[Path, Path]:
    freeze = json.loads(V3_FREEZE.read_text())
    dois = freeze["transport_probe"]["probe_dois"]
    matched = dois[1]
    body = json.dumps(
        {
            "header": {"numFound": 1},
            "results": [
                {
                    "id": "synthetic-structured-product",
                    "pids": [{"scheme": "doi", "value": matched}],
                    "type": "publication",
                }
            ],
        },
        separators=(",", ":"),
    ).encode()
    response = tmp_path / "transport_probe_response.json"
    response.write_bytes(body)
    url = module.v4.build_v4_crosswalk_url(
        dois, page_size=int(freeze["transport_probe"]["page_size"])
    )
    receipt = {
        "schema_version": module.v4.SCHEMA,
        "terminal": module.v4.TERMINAL,
        "http_status": 200,
        "note": "",
        "crosswalk_endpoint": module.v4.V4_ENDPOINT,
        "crosswalk_api_status": "BETA",
        "encoding": "v4_filter_ids_doi_or_list",
        "dois": dois,
        "url_sha256": hashlib.sha256(url.encode()).hexdigest(),
        "response_sha256": hashlib.sha256(body).hexdigest(),
        "response_bytes": len(body),
        "result_count": 1,
        "matched_dois": [matched],
        "benchmark_gold_accessed": False,
        "promotion_authorized": False,
    }
    probe = tmp_path / "transport_probe.json"
    probe.write_text(json.dumps(receipt, sort_keys=True))
    return probe, response


def test_v3_runner_delegates_science_to_exact_v2_and_changes_only_crosswalk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = _load("p2_v3_runner_test", RUNNER_PATH)
    probe, response = _transport_bundle(runner, tmp_path)
    public = tmp_path / "public.jsonl"
    public.write_text("{}\n")
    out = tmp_path / "out"
    observed = {}

    def fake_v2_run(public_path, freeze_path, identity_path, probe_path, out_dir):
        assert Path(freeze_path) == V2_FREEZE
        assert Path(identity_path) == IDENTITY
        assert Path(probe_path) == probe
        url = runner.v2.build_openaire_crosswalk_url(
            ["10.5281/zenodo.8217359", "10.1038/s41586-023-06221-2"],
            page_size=100,
        )
        observed["url"] = url
        assert url.startswith(runner.v4.V4_ENDPOINT + "?")
        assert "filter=" in url and "ids.doi%3A" in url and "%7C" in url
        validated = runner.v2.validate_transport_probe(probe, json.loads(V2_FREEZE.read_text()))
        assert validated["terminal"] == runner.v4.TERMINAL
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "campaign_version": 2,
            "authority": "CANDIDATE_CAPTURE_FROZEN_BEFORE_EVALUATOR_GOLD",
            "freeze_sha256": runner.sha256_file(V2_FREEZE),
            "transport_probe_sha256": runner.sha256_file(probe),
            "transport_probe_response_sha256": runner.sha256_file(response),
            "transport_probe_terminal": "OLD_V2_LABEL",
            "transport_encoding": "repeated_pid_parameters",
            "candidate_hashes": {},
            "same_acquisition_capture_for_all_systems": True,
            "candidate_cap": 20,
            "raw_regex_arxiv_identity_extraction": False,
        }
        (out_dir / "SHARED_ACQUISITION_MANIFEST.json").write_text(json.dumps(manifest))
        return manifest

    monkeypatch.setattr(runner.v2, "run", fake_v2_run)
    before_builder = runner.v2.build_openaire_crosswalk_url
    before_validator = runner.v2.validate_transport_probe
    manifest = runner.run(
        public,
        V3_FREEZE,
        V2_FREEZE,
        IDENTITY,
        probe,
        response,
        out,
    )
    assert observed["url"]
    assert runner.v2.build_openaire_crosswalk_url is before_builder
    assert runner.v2.validate_transport_probe is before_validator
    assert manifest["campaign_version"] == 3
    assert manifest["transport_encoding"] == "v4_filter_ids_doi_or_list"
    assert manifest["transport_probe_terminal"] == runner.v4.TERMINAL
    assert manifest["v3_transport_only_change"] is True
    assert manifest["v3_beta_transport_is_scientific_evidence"] is False
    assert manifest["freeze_sha256"] == runner.sha256_file(V3_FREEZE)
    assert manifest["parent_v2_freeze_sha256"] == runner.sha256_file(V2_FREEZE)


def test_v3_runner_rejects_tampered_raw_provider_bytes(tmp_path: Path) -> None:
    runner = _load("p2_v3_runner_tamper_test", RUNNER_PATH)
    probe, response = _transport_bundle(runner, tmp_path)
    response.write_bytes(response.read_bytes() + b" ")
    with pytest.raises(ValueError, match="hash mismatch"):
        runner.run(
            tmp_path / "unused-public.jsonl",
            V3_FREEZE,
            V2_FREEZE,
            IDENTITY,
            probe,
            response,
            tmp_path / "out",
        )


def test_v3_analyzer_manifest_gate_rejects_v2_labels_and_beta_promotion(tmp_path: Path) -> None:
    analyzer = _load("p2_v3_analyzer_manifest_test", ANALYZER_PATH)
    probe, response = _transport_bundle(analyzer, tmp_path)
    base = {
        "campaign_version": 3,
        "transport_encoding": "v4_filter_ids_doi_or_list",
        "transport_probe_terminal": analyzer.v4.TERMINAL,
        "v3_crosswalk_endpoint": analyzer.v4.V4_ENDPOINT,
        "v3_transport_only_change": True,
        "v3_beta_transport_is_scientific_evidence": False,
        "freeze_sha256": analyzer.sha256_file(V3_FREEZE),
        "parent_v2_freeze_sha256": analyzer.sha256_file(V2_FREEZE),
        "transport_probe_sha256": analyzer.sha256_file(probe),
        "transport_probe_response_sha256": analyzer.sha256_file(response),
    }
    analyzer.validate_v3_manifest(base, V3_FREEZE, V2_FREEZE, probe, response)
    bad = dict(base, campaign_version=2)
    with pytest.raises(ValueError, match="campaign version"):
        analyzer.validate_v3_manifest(bad, V3_FREEZE, V2_FREEZE, probe, response)
    bad = dict(base, v3_beta_transport_is_scientific_evidence=True)
    with pytest.raises(ValueError, match="improperly promotes beta transport"):
        analyzer.validate_v3_manifest(bad, V3_FREEZE, V2_FREEZE, probe, response)
