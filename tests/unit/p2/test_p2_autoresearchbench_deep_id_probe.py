from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(
    "papers/paper-02-open-world-scientific-discovery/scripts/run_autoresearchbench_deep_id_probe.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("p2_arb_deep_id", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_prepare_splits_600_deep_tasks_without_answer_or_target_in_candidate(
    tmp_path: Path,
) -> None:
    module = _module()
    full = tmp_path / "full.jsonl"
    public = tmp_path / "public.jsonl"
    gt = tmp_path / "gt.jsonl"
    rows: list[dict] = []
    for index in range(400):
        rows.append(
            {
                "question": f"wide {index}",
                "answer": [f"wide hidden {index}"],
                "arxiv_id": [f"2401.{index:05d}"],
            }
        )
    for index in range(600):
        rows.append(
            {
                "question": "" if index == 0 else f"deep public question {index}",
                "answer": [f"deep hidden title {index}"],
                "arxiv_id": "" if index == 1 else f"2501.{index:05d}",
            }
        )
    _write_jsonl(full, rows)

    manifest = module.prepare(full, public, gt)
    assert manifest["deep_tasks"] == 600
    assert manifest["empty_question_task_count"] == 1
    assert manifest["empty_target_task_count"] == 1
    public_text = public.read_text(encoding="utf-8")
    assert "answer" not in public_text
    assert "arxiv_id" not in public_text
    assert "deep hidden" not in public_text
    public_rows = [json.loads(line) for line in public_text.splitlines()]
    gt_rows = [json.loads(line) for line in gt.read_text(encoding="utf-8").splitlines()]
    assert len(public_rows) == len(gt_rows) == 600
    assert set(public_rows[0]) == {"task_id", "question"}
    assert set(gt_rows[0]) == {"task_id", "question", "target_arxiv_id"}


def test_exact_id_evaluator_is_deterministic_and_explicitly_nonofficial(tmp_path: Path) -> None:
    module = _module()
    public = tmp_path / "public.jsonl"
    gt = tmp_path / "gt.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    output = tmp_path / "evaluation.json"

    _write_jsonl(
        public,
        [
            {"task_id": "arb-deep-0001", "question": "question one"},
            {"task_id": "arb-deep-0002", "question": "question two"},
        ],
    )
    _write_jsonl(
        gt,
        [
            {
                "task_id": "arb-deep-0001",
                "question": "question one",
                "target_arxiv_id": "2401.01234",
            },
            {
                "task_id": "arb-deep-0002",
                "question": "question two",
                "target_arxiv_id": "hep-th/9901001",
            },
        ],
    )
    _write_jsonl(
        candidate,
        [
            {
                "input_data": {"question": "question one"},
                "inference_results": [
                    {
                        "status": "ok",
                        "final_candidates": [
                            {"arxiv_id": "arXiv:2401.01234v2", "title": "hit"}
                        ],
                    }
                ],
            },
            {
                "input_data": {"question": "question two"},
                "inference_results": [
                    {
                        "status": "ok",
                        "final_candidates": [
                            {"arxiv_id": "cs/0501001", "title": "miss"}
                        ],
                    }
                ],
            },
        ],
    )

    result = module.evaluate(public, gt, candidate, output)
    assert result["official_deep_metric"] is False
    assert result["metric"] == "exact_target_arxiv_id_retrieval_success"
    assert result["scorable_records"] == 2
    assert result["target_hits"] == 1
    assert result["target_hit_rate"] == 0.5
    assert result["per_task"][0]["target_hit"] is True
    assert result["per_task"][1]["target_hit"] is False
