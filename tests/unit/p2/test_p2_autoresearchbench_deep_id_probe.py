from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(
    "papers/orion-12-open-world-scientific-discovery/scripts/run_autoresearchbench_deep_id_probe.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("p2_arb_deep_id", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_prepare_uses_type_for_600_deep_tasks_without_gold_in_candidate(
    tmp_path: Path,
) -> None:
    module = _module()
    full = tmp_path / "full.jsonl"
    public = tmp_path / "public.jsonl"
    gt = tmp_path / "gt.jsonl"
    rows: list[dict] = []

    # Wide and Deep are both list-valued in the released bundle.
    for index in range(400):
        rows.append(
            {
                "type": "wide",
                "question": f"wide {index}",
                "answer": [f"wide hidden {index}"],
                "arxiv_id": [f"2401.{index:05d}"],
            }
        )
    for index in range(600):
        if index == 0:
            question = ""
        elif index == 1:
            # Public question prose may legitimately contain hidden-field words;
            # custody is a schema boundary, not a substring filter.
            question = "what is the answer to this public research question?"
        else:
            question = f"deep public question {index}"
        rows.append(
            {
                "type": "deep",
                "question": question,
                "answer": ["None" if index < 60 else f"deep hidden title {index}"],
                "arxiv_id": ["" if index < 60 else f"2501.{index:05d}"],
            }
        )
    _write_jsonl(full, rows)

    manifest = module.prepare(full, public, gt)
    assert manifest["deep_tasks"] == 600
    assert manifest["release_task_type_counts"] == {"wide": 400, "deep": 600}
    assert manifest["empty_question_task_count"] == 1
    assert manifest["empty_target_task_count"] == 60
    assert manifest["exact_id_scorable_task_count"] == 540
    assert manifest["candidate_public_fields"] == ["question", "task_id"]

    public_text = public.read_text(encoding="utf-8")
    assert "deep hidden" not in public_text
    assert "wide 0" not in public_text
    public_rows = [json.loads(line) for line in public_text.splitlines()]
    gt_rows = [json.loads(line) for line in gt.read_text(encoding="utf-8").splitlines()]
    assert len(public_rows) == len(gt_rows) == 600
    assert all(set(row) == {"task_id", "question"} for row in public_rows)
    assert public_rows[1]["question"] == "what is the answer to this public research question?"
    assert set(gt_rows[0]) == {
        "task_id",
        "question",
        "target_arxiv_id",
        "ground_truth_titles",
    }
    assert gt_rows[0]["target_arxiv_id"] == ""
    assert gt_rows[0]["ground_truth_titles"] == ["None"]


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
                "ground_truth_titles": ["Paper One"],
            },
            {
                "task_id": "arb-deep-0002",
                "question": "question two",
                "target_arxiv_id": "hep-th/9901001",
                "ground_truth_titles": ["Paper Two"],
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
                            {"arxiv_id": "arXiv:2401.01234v2", "title": "Paper One"}
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
                            {"arxiv_id": "cs/0501001", "title": "Other Paper"}
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


def test_build_official_input_joins_titles_only_after_candidate_freeze(tmp_path: Path) -> None:
    module = _module()
    public = tmp_path / "public.jsonl"
    gt = tmp_path / "gt.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    official = tmp_path / "official-input.jsonl"

    _write_jsonl(public, [{"task_id": "arb-deep-0001", "question": "public question"}])
    _write_jsonl(
        gt,
        [
            {
                "task_id": "arb-deep-0001",
                "question": "public question",
                "target_arxiv_id": "2401.01234",
                "ground_truth_titles": ["Ground Truth Paper"],
            }
        ],
    )
    _write_jsonl(
        candidate,
        [
            {
                "input_data": {"question": "public question"},
                "inference_results": [
                    {
                        "status": "ok",
                        "pass_id": 0,
                        "final_candidates": [
                            {"arxiv_id": "2401.01234", "title": "Ground Truth Paper"}
                        ],
                    }
                ],
            }
        ],
    )

    manifest = module.build_official_input(public, gt, candidate, official)
    assert manifest["candidate_labels_visible"] is False
    joined = json.loads(official.read_text(encoding="utf-8"))
    assert joined["input_data"]["answer"] == ["Ground Truth Paper"]
    assert joined["inference_results"][0]["final_candidate_state"] == "candidate"
    assert joined["inference_results"][0]["final_candidates"] == [
        {"metadata": {"title": "Ground Truth Paper"}}
    ]
