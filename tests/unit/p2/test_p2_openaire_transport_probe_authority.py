from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

RUNNER_PATH = Path(
    "papers/paper-02-open-world-scientific-discovery/scripts/"
    "run_autoresearchbench_wide_openaire_matched_v2.py"
)


def _load_runner():
    spec = importlib.util.spec_from_file_location("p2_v2_transport_authority_tested", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = _load_runner()


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


def _good_probe() -> dict:
    dois = _freeze()["transport_repair_evidence"]["probe_dois"]
    url = runner.build_openaire_crosswalk_url(
        dois, page_size=runner.TRANSPORT_PROBE_PAGE_SIZE
    )
    return {
        "schema_version": runner.PROBE_SCHEMA,
        "terminal": runner.PROBE_TERMINAL,
        "http_status": 200,
        "encoding": "repeated_pid_parameters",
        "dois": dois,
        "url_sha256": hashlib.sha256(url.encode()).hexdigest(),
        "response_sha256": "a" * 64,
        "result_count": 2,
        "matched_dois": [dois[1]],
        "benchmark_gold_accessed": False,
        "promotion_authorized": False,
    }


def test_transport_probe_binds_request_and_authority(tmp_path: Path) -> None:
    path = tmp_path / "probe.json"
    good = _good_probe()
    path.write_text(json.dumps(good), encoding="utf-8")
    assert runner.validate_transport_probe(path, _freeze())["terminal"] == runner.PROBE_TERMINAL

    bad_cases = (
        ("schema_version", "orion.p2.fake-probe.v1"),
        ("url_sha256", "0" * 64),
        ("response_sha256", "not-a-canonical-sha256"),
        ("result_count", 0),
        ("result_count", -1),
        ("matched_dois", []),
        ("matched_dois", ["10.9999/not-requested"]),
        ("matched_dois", [good["matched_dois"][0].upper()]),
        ("benchmark_gold_accessed", True),
        ("promotion_authorized", True),
    )
    for key, value in bad_cases:
        bad = dict(good)
        bad[key] = value
        path.write_text(json.dumps(bad), encoding="utf-8")
        with pytest.raises(ValueError):
            runner.validate_transport_probe(path, _freeze())

    dois = _freeze()["transport_repair_evidence"]["probe_dois"]
    reversed_matches = dict(good)
    reversed_matches["matched_dois"] = [dois[1], dois[0]]
    path.write_text(json.dumps(reversed_matches), encoding="utf-8")
    with pytest.raises(ValueError):
        runner.validate_transport_probe(path, _freeze())


def test_transport_probe_refuses_weakened_freeze(tmp_path: Path) -> None:
    path = tmp_path / "probe.json"
    path.write_text(json.dumps(_good_probe()), encoding="utf-8")

    freeze = _freeze()
    freeze["transport_repair_evidence"]["pre_benchmark_probe_required"] = False
    with pytest.raises(ValueError):
        runner.validate_transport_probe(path, freeze)

    freeze = _freeze()
    freeze["transport_repair_evidence"]["probe_gold_access"] = "ALLOWED"
    with pytest.raises(ValueError):
        runner.validate_transport_probe(path, freeze)

    freeze = _freeze()
    freeze["transport_repair_evidence"]["probe_min_result_count"] = 0
    with pytest.raises(ValueError):
        runner.validate_transport_probe(path, freeze)

    freeze = _freeze()
    freeze["transport_repair_evidence"]["probe_min_matched_doi_count"] = 0
    with pytest.raises(ValueError):
        runner.validate_transport_probe(path, freeze)


def test_transport_response_binds_raw_bytes_and_requested_identity(tmp_path: Path) -> None:
    freeze = _freeze()
    requested = freeze["transport_repair_evidence"]["probe_dois"]
    response = {
        "results": [
            {
                "pid": [
                    {"scheme": "doi", "value": requested[1]},
                    {"scheme": "arxiv", "value": "2306.11152"},
                ]
            }
        ]
    }
    body = json.dumps(response, sort_keys=True).encode()
    response_path = tmp_path / "transport_probe_response.json"
    response_path.write_bytes(body)
    probe = _good_probe()
    probe["response_sha256"] = hashlib.sha256(body).hexdigest()
    probe["result_count"] = 1
    probe["matched_dois"] = [requested[1]]
    assert runner.validate_transport_response(response_path, probe, freeze) == response

    unrelated = {"results": [{"pid": [{"scheme": "doi", "value": "10.9999/unrelated"}]}]}
    unrelated_body = json.dumps(unrelated, sort_keys=True).encode()
    response_path.write_bytes(unrelated_body)
    probe["response_sha256"] = hashlib.sha256(unrelated_body).hexdigest()
    probe["result_count"] = 1
    with pytest.raises(ValueError):
        runner.validate_transport_response(response_path, probe, freeze)
