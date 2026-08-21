from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import urllib.parse
from pathlib import Path

import pytest

RUNNER_PATH = Path(
    "papers/paper-02-open-world-scientific-discovery/scripts/"
    "run_autoresearchbench_wide_openaire_matched_v2.py"
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runner = _load("p2_openaire_matched_v2_runner_tested", RUNNER_PATH)


def test_crosswalk_v2_uses_repeated_pid_parameters() -> None:
    url = runner.build_openaire_crosswalk_url(
        ["10.1000/A", "https://doi.org/10.2000/B", "10.1000/A"], page_size=100
    )
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    assert query["pid"] == ["10.1000/a", "10.2000/b"]
    assert query["type"] == ["publication"]
    assert query["page"] == ["1"]
    assert query["pageSize"] == ["100"]
    assert "search" not in query
    assert " OR " not in parsed.query


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


def test_transport_probe_is_bound_and_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "probe.json"
    dois = _freeze()["transport_repair_evidence"]["probe_dois"]
    url = runner.build_openaire_crosswalk_url(
        dois, page_size=runner.TRANSPORT_PROBE_PAGE_SIZE
    )
    good = {
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
    path.write_text(json.dumps(good), encoding="utf-8")
    assert runner.validate_transport_probe(path, _freeze())["terminal"] == runner.PROBE_TERMINAL

    for key, bad_value in (
        ("terminal", "CANNOT_CHECK"),
        ("http_status", 400),
        ("encoding", "legacy_expression"),
        ("response_sha256", ""),
        ("result_count", 0),
        ("matched_dois", []),
    ):
        bad = dict(good)
        bad[key] = bad_value
        path.write_text(json.dumps(bad), encoding="utf-8")
        with pytest.raises(ValueError):
            runner.validate_transport_probe(path, _freeze())


def test_v2_acquisition_keeps_three_logical_calls(monkeypatch, tmp_path: Path) -> None:
    oa = lambda *ids: json.dumps(
        {"results": [{"pid": [{"scheme": "arxiv", "value": value}]} for value in ids]}
    ).encode()
    cr = lambda *dois: json.dumps(
        {"message": {"items": [{"DOI": value} for value in dois]}}
    ).encode()
    responses = iter([
        runner.v1.HttpResult(200, oa("2601.00001", "2601.00002"), "", 1),
        runner.v1.HttpResult(200, cr("10.1000/a", "10.2000/b"), "", 1),
        runner.v1.HttpResult(200, oa("2601.00002", "2601.00003"), "", 1),
    ])
    monkeypatch.setattr(runner.v1, "http_get", lambda *args, **kwargs: next(responses))
    freeze = {
        "acquisition": {
            "logical_requests_per_nonempty_task": 3,
            "max_candidates_per_system": 20,
            "openaire": {
                "direct": {"parameters": {"pageSize": 20}},
                "crosswalk": {
                    "parameters": {"pageSize": 100},
                    "transport_encoding": "repeated_pid_parameters",
                },
                "fallback": {"parameters": {"pageSize": 20}},
                "minimum_interval_seconds": 0,
            },
            "crossref": {"parameters": {"rows": 20}, "minimum_interval_seconds": 0},
            "transport": {
                "timeout_seconds": 1,
                "maximum_retries_per_logical_request": 0,
                "retry_sleep_seconds": 0,
            },
        }
    }
    capture = runner.acquire_task_v2(
        "arb-wide-v2-0001",
        "adaptive scientific retrieval across distributed evidence",
        freeze=freeze,
        clock=runner.v1.HostClock(),
        response_dir=tmp_path,
    )
    assert len(capture["calls"]) == 3
    assert [call["kind"] for call in capture["calls"]] == [
        "openaire_direct",
        "crossref_discovery",
        "openaire_doi_crosswalk",
    ]
    assert capture["cross_backend_confirmed_ids"] == ["2601.00002"]
    assert capture["open_obligations"] == []
