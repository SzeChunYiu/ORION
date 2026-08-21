from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ANALYZER_PATH = Path(
    "papers/paper-02-open-world-scientific-discovery/scripts/"
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
        }
    }


def _write_probe(path: Path) -> None:
    dois = _freeze()["transport_repair_evidence"]["probe_dois"]
    url = runner.build_openaire_crosswalk_url(
        dois, page_size=runner.TRANSPORT_PROBE_PAGE_SIZE
    )
    receipt = {
        "schema_version": runner.PROBE_SCHEMA,
        "terminal": runner.PROBE_TERMINAL,
        "http_status": 200,
        "encoding": "repeated_pid_parameters",
        "dois": dois,
        "url_sha256": hashlib.sha256(url.encode()).hexdigest(),
        "response_sha256": "a" * 64,
        "result_count": 2,
        "benchmark_gold_accessed": False,
        "promotion_authorized": False,
    }
    path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")


def _manifest(path: Path) -> dict:
    return {
        "campaign_version": 2,
        "transport_encoding": "repeated_pid_parameters",
        "transport_probe_terminal": runner.PROBE_TERMINAL,
        "transport_probe_sha256": runner.sha256_file(path),
    }


def test_score_time_transport_evidence_requires_exact_archived_bytes(tmp_path: Path) -> None:
    path = tmp_path / "transport_probe.json"
    _write_probe(path)
    manifest = _manifest(path)
    good = analyzer.transport_evidence_validity(_freeze(), manifest, path)
    assert good["valid"] is True
    assert good["probe_hash_matches_manifest"] is True
    assert good["receipt_valid"] is True

    receipt = json.loads(path.read_text())
    receipt["promotion_authorized"] = True
    path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
    forged = analyzer.transport_evidence_validity(_freeze(), manifest, path)
    assert forged["valid"] is False
    assert forged["probe_hash_matches_manifest"] is False
    assert forged["receipt_valid"] is False


def test_score_time_transport_evidence_refuses_manifest_only_authority(tmp_path: Path) -> None:
    path = tmp_path / "transport_probe.json"
    _write_probe(path)
    manifest = _manifest(path)
    manifest["transport_probe_sha256"] = "0" * 64
    validity = analyzer.transport_evidence_validity(_freeze(), manifest, path)
    assert validity["valid"] is False
    assert validity["receipt_valid"] is True
    assert validity["probe_hash_matches_manifest"] is False
