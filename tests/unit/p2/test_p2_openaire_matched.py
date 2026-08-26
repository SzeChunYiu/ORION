from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

RUNNER_PATH = Path(
    "papers/orion-12-open-world-scientific-discovery/scripts/"
    "run_autoresearchbench_wide_openaire_matched.py"
)
ANALYZER_PATH = Path(
    "papers/orion-12-open-world-scientific-discovery/scripts/"
    "analyze_autoresearchbench_wide_openaire_matched.py"
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runner = _load("p2_openaire_matched_runner_tested", RUNNER_PATH)
analyzer = _load("p2_openaire_matched_analyzer_tested", ANALYZER_PATH)


def _oa(*ids: str) -> bytes:
    return json.dumps(
        {
            "results": [
                {"pid": [{"scheme": "arxiv", "value": value}]}
                for value in ids
            ]
        }
    ).encode()


def _crossref(*dois: str) -> bytes:
    return json.dumps({"message": {"items": [{"DOI": value} for value in dois]}}).encode()


def _freeze() -> dict:
    return {
        "acquisition": {
            "logical_requests_per_nonempty_task": 3,
            "max_candidates_per_system": 20,
            "openaire": {
                "direct": {"parameters": {"pageSize": 20}},
                "crosswalk": {"parameters": {"pageSize": 100}},
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


def test_crossref_admits_only_doi_field() -> None:
    payload = {
        "message": {
            "items": [
                {"DOI": "10.1000/ABC", "title": ["2604.25256"]},
                {"DOI": "not-a-doi", "URL": "https://doi.org/10.1234/2604.25256"},
                {"DOI": "https://doi.org/10.5555/XYZ"},
            ]
        }
    }
    assert runner.extract_crossref_dois(payload) == ("10.1000/abc", "10.5555/xyz")


def test_crosswalk_url_uses_pid_or_expression_not_search_text() -> None:
    url = runner.build_openaire_crosswalk_url(["10.1000/a", "10.2000/b"], page_size=100)
    parsed = __import__("urllib.parse").parse.urlparse(url)
    query = __import__("urllib.parse").parse.parse_qs(parsed.query)
    assert "pid" in query
    assert "search" not in query
    assert '"10.1000/a" OR "10.2000/b"' in query["pid"][0]
    assert query["pageSize"] == ["100"]


def test_shared_capture_uses_exactly_three_calls_and_cross_backend_confirmation(monkeypatch, tmp_path: Path) -> None:
    responses = iter(
        [
            runner.HttpResult(200, _oa("2601.00001", "2601.00002"), "", 1),
            runner.HttpResult(200, _crossref("10.1000/a", "10.1000/b"), "", 1),
            runner.HttpResult(200, _oa("2601.00003", "2601.00002"), "", 1),
        ]
    )
    monkeypatch.setattr(runner, "http_get", lambda *args, **kwargs: next(responses))
    capture = runner.acquire_task(
        "arb-wide-0001",
        "conformal adaptive scientific retrieval censored routes",
        freeze=_freeze(),
        clock=runner.HostClock(),
        response_dir=tmp_path,
    )
    assert len(capture["calls"]) == 3
    assert [call["kind"] for call in capture["calls"]] == [
        "openaire_direct",
        "crossref_discovery",
        "openaire_doi_crosswalk",
    ]
    assert capture["direct_openaire_ids"] == ["2601.00001", "2601.00002"]
    assert capture["crossref_arxiv_ids"] == ["2601.00003", "2601.00002"]
    assert capture["cross_backend_confirmed_ids"] == ["2601.00002"]
    assert capture["open_obligations"] == []


def test_no_doi_spends_third_call_on_predeclared_fallback(monkeypatch, tmp_path: Path) -> None:
    responses = iter(
        [
            runner.HttpResult(200, _oa("2601.00001"), "", 1),
            runner.HttpResult(200, _crossref(), "", 1),
            runner.HttpResult(200, _oa("2601.00002"), "", 1),
        ]
    )
    monkeypatch.setattr(runner, "http_get", lambda *args, **kwargs: next(responses))
    capture = runner.acquire_task(
        "arb-wide-0002",
        "multimodal transformer scientific generalization benchmark",
        freeze=_freeze(),
        clock=runner.HostClock(),
        response_dir=tmp_path,
    )
    assert len(capture["calls"]) == 3
    assert capture["calls"][2]["kind"] == "openaire_widened_fallback"
    assert capture["crossref_arxiv_ids"] == []
    assert capture["fallback_openaire_ids"] == ["2601.00002"]
    assert capture["cross_backend_confirmed_ids"] == []


def test_primary_baseline_is_route_balanced_not_direct_first() -> None:
    capture = {
        "direct_openaire_ids": ["A", "B", "C"],
        "crossref_arxiv_ids": ["X", "Y", "Z"],
        "fallback_openaire_ids": [],
        "cross_backend_confirmed_ids": [],
    }
    assert runner.project_candidates(capture, system_id="wide_dual_backend_balanced", cap=6) == [
        "A", "X", "B", "Y", "C", "Z"
    ]
    assert runner.project_candidates(capture, system_id="wide_dual_backend_direct_first", cap=6) == [
        "A", "B", "C", "X", "Y", "Z"
    ]


def test_orion_only_prioritizes_true_cross_backend_confirmation() -> None:
    capture = {
        "direct_openaire_ids": ["A", "B"],
        "crossref_arxiv_ids": ["C", "B"],
        "fallback_openaire_ids": [],
        "cross_backend_confirmed_ids": ["B"],
    }
    assert runner.project_candidates(capture, system_id="wide_dual_backend_balanced", cap=3) == ["A", "C", "B"]
    assert runner.project_candidates(capture, system_id="wide_dual_backend_governed", cap=3) == ["B", "A", "C"]

    same_backend_only = {
        "direct_openaire_ids": ["A", "B"],
        "crossref_arxiv_ids": [],
        "fallback_openaire_ids": ["B", "D"],
        "cross_backend_confirmed_ids": [],
    }
    assert runner.project_candidates(same_backend_only, system_id="wide_dual_backend_governed", cap=4) == [
        "A", "B", "D"
    ]


def test_all_projections_share_cap_and_pool() -> None:
    capture = {
        "direct_openaire_ids": [f"D{i}" for i in range(30)],
        "crossref_arxiv_ids": [f"C{i}" for i in range(30)],
        "fallback_openaire_ids": [],
        "cross_backend_confirmed_ids": ["D1"],
    }
    pool = set(capture["direct_openaire_ids"] + capture["crossref_arxiv_ids"])
    for system_id in runner.SYSTEM_IDS:
        projected = runner.project_candidates(capture, system_id=system_id, cap=20)
        assert len(projected) <= 20
        assert len(projected) == len(set(projected))
        assert set(projected) <= pool


def test_last_write_question_semantics_collapses_duplicate_inference_unit() -> None:
    evaluation = {
        "per_record_results": [
            {"question": "same", "pass_results": [{"pass_id": 0, "iou": 0.1}]},
            {"question": "other", "pass_results": [{"pass_id": 0, "iou": 0.2}]},
            {"question": "same", "pass_results": [{"pass_id": 0, "iou": 0.9}]},
        ]
    }
    mapping = analyzer.pass0_by_question_last_write(evaluation)
    assert set(mapping) == {"same", "other"}
    assert mapping["same"]["iou"] == 0.9


def test_paired_bootstrap_is_deterministic_and_counts_wins_ties_losses() -> None:
    first = analyzer.paired_bootstrap([0.1, 0.0, -0.05, 0.2], resamples=1000, seed=20260818)
    second = analyzer.paired_bootstrap([0.1, 0.0, -0.05, 0.2], resamples=1000, seed=20260818)
    assert first == second
    assert first["wins"] == 2
    assert first["ties"] == 1
    assert first["losses"] == 1
    assert first["ci95_low"] <= first["mean"] <= first["ci95_high"]


def _candidate_file(path: Path, questions: list[str], candidates: list[list[str]]) -> None:
    rows = []
    for question, ids in zip(questions, candidates, strict=True):
        rows.append(
            {
                "input_data": {"question": question},
                "inference_results": [
                    {
                        "pass_id": 0,
                        "status": "ok",
                        "final_candidates": [{"arxiv_id": value} for value in ids],
                        "turn_details": [],
                    }
                ],
            }
        )
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _eval(path: Path, questions: list[str], ious: list[float], recall: float) -> None:
    path.write_text(
        json.dumps(
            {
                "aggregate_stats": {
                    "avg_iou": sum(ious) / len(ious),
                    "avg_recall": recall,
                    "avg_precision": 0.5,
                },
                "per_record_results": [
                    {
                        "question": question,
                        "pass_results": [
                            {
                                "pass_id": 0,
                                "iou": iou,
                                "recall": recall,
                                "precision": 0.5,
                            }
                        ],
                    }
                    for question, iou in zip(questions, ious, strict=True)
                ],
            }
        ),
        encoding="utf-8",
    )


def test_terminal_known_positive_and_transport_invalid(tmp_path: Path) -> None:
    questions = ["q1", "q2"]
    candidate_paths = {name: tmp_path / f"{name}.jsonl" for name in runner.SYSTEM_IDS}
    for path in candidate_paths.values():
        _candidate_file(path, questions, [["2601.00001"], ["2601.00002"]])

    freeze = {
        "schema_version": "orion.p2.wide-openaire-matched-freeze.v1",
        "benchmark": {"expected_distinct_nonempty_question_units": 2, "released_wide_rows": 2},
        "acquisition": {"max_candidates_per_system": 20},
        "evaluation": {"paired_inference": {"bootstrap_resamples": 1000, "seed": 20260818}},
        "validity": {"minimum_logical_provider_ok_fraction": 0.9},
        "terminal_rule": {
            "supported": {
                "official_avg_iou_delta_orion_minus_baseline_at_least": 0.03,
                "paired_iou_ci95_low_strictly_greater_than": 0.0,
                "official_avg_recall_orion_minus_baseline_at_least": 0.0,
            },
            "positive_terminal": "P2_WIDE_EXTERNAL_SUPPORTED",
            "negative_valid_terminal": "P2_WIDE_EXTERNAL_NOT_SUPPORTED",
            "invalid_or_transport_terminal": "P2_WIDE_EXTERNAL_CANNOT_CHECK",
        },
        "claim_boundary": "test",
    }
    freeze_path = tmp_path / "freeze.json"
    freeze_path.write_text(json.dumps(freeze), encoding="utf-8")

    manifest = {
        "schema_version": "orion.p2.wide-openaire-shared-capture.v1",
        "logical_provider_ok_fraction": 1.0,
        "same_acquisition_capture_for_all_systems": True,
        "raw_regex_arxiv_identity_extraction": False,
        "logical_provider_calls_planned": 6,
        "logical_provider_calls_recorded": 6,
        "freeze_sha256": analyzer.sha256_file(freeze_path),
        "candidate_hashes": {name: analyzer.sha256_file(path) for name, path in candidate_paths.items()},
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    baseline_eval = tmp_path / "baseline.json"
    orion_eval = tmp_path / "orion.json"
    diagnostic_eval = tmp_path / "diagnostic.json"
    _eval(baseline_eval, questions, [0.10, 0.20], 0.5)
    _eval(orion_eval, questions, [0.20, 0.30], 0.6)
    _eval(diagnostic_eval, questions, [0.10, 0.20], 0.5)

    result = analyzer.analyze(
        freeze_path=freeze_path,
        manifest_path=manifest_path,
        baseline_eval_path=baseline_eval,
        orion_eval_path=orion_eval,
        diagnostic_eval_path=diagnostic_eval,
        baseline_candidate_path=candidate_paths["wide_dual_backend_balanced"],
        orion_candidate_path=candidate_paths["wide_dual_backend_governed"],
        diagnostic_candidate_path=candidate_paths["wide_dual_backend_direct_first"],
        output_path=tmp_path / "out.json",
    )
    assert result["terminal"] == "P2_WIDE_EXTERNAL_SUPPORTED"
    assert result["paired_distinct_question_iou"]["ci95_low"] > 0

    manifest["logical_provider_ok_fraction"] = 0.5
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    invalid = analyzer.analyze(
        freeze_path=freeze_path,
        manifest_path=manifest_path,
        baseline_eval_path=baseline_eval,
        orion_eval_path=orion_eval,
        diagnostic_eval_path=diagnostic_eval,
        baseline_candidate_path=candidate_paths["wide_dual_backend_balanced"],
        orion_candidate_path=candidate_paths["wide_dual_backend_governed"],
        diagnostic_candidate_path=candidate_paths["wide_dual_backend_direct_first"],
        output_path=tmp_path / "invalid.json",
    )
    assert invalid["terminal"] == "P2_WIDE_EXTERNAL_CANNOT_CHECK"
