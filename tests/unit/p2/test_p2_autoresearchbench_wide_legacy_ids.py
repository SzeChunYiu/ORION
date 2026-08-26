from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(
    "papers/orion-12-open-world-scientific-discovery/scripts/run_autoresearchbench_wide_compat.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("p2_arb_wide_compat", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_normalizer_matches_modern_and_legacy_scorer_domain() -> None:
    module = _module()
    assert module.normalize_arxiv_id("arXiv:2401.01234v3") == "2401.01234"
    assert module.normalize_arxiv_id("https://arxiv.org/abs/hep-th/9901001v2") == "hep-th/9901001"
    assert module.normalize_arxiv_id("cs/0501001") == "cs/0501001"
    assert module.normalize_arxiv_id("") == ""
    assert module.normalize_arxiv_id("   ") == ""


def test_prepare_uses_explicit_type_and_preserves_full_scorer_domain_without_candidate_leak(
    tmp_path: Path,
) -> None:
    module = _module()
    full = tmp_path / "full.jsonl"
    public = tmp_path / "public.jsonl"
    gt = tmp_path / "gt.jsonl"
    rows = []

    # Released Deep rows are also list-valued; they must not be mistaken for Wide.
    for index in range(600):
        rows.append(
            {
                "type": "deep",
                "question": f"deep public question {index}",
                "answer": [f"deep hidden title {index}"],
                "arxiv_id": ["" if index < 60 else f"23{index % 100:02d}.{index:05d}"],
            }
        )

    for index in range(400):
        if index == 0:
            target = ["hep-th/9901001"]
        elif index == 1:
            target = ["", None, "   "]
        else:
            target = [f"24{index % 100:02d}.{index:05d}"]
        if index == 2:
            question = ""
        elif index == 3:
            question = "Unique public research question 4 about representation learning"
        else:
            question = f"Unique public research question {index} about representation learning"
        rows.append(
            {
                "type": "wide",
                "question": question,
                "answer": [f"hidden title {index}"],
                "arxiv_id": target,
            }
        )
    full.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    manifest = module.prepare(full, public, gt)
    assert manifest["wide_tasks"] == 400
    assert manifest["release_task_type_counts"] == {"deep": 600, "wide": 400}
    assert manifest["legacy_target_id_count"] == 1
    assert manifest["empty_target_task_count"] == 1
    assert manifest["empty_question_task_count"] == 1
    assert manifest["duplicate_question_task_count"] == 1
    assert manifest["official_gt_mapping_question_count"] == 398
    public_text = public.read_text(encoding="utf-8")
    assert "arxiv_id" not in public_text
    assert "hidden title" not in public_text
    assert "deep public question" not in public_text
    public_rows = [json.loads(line) for line in public_text.splitlines()]
    gt_rows = [json.loads(line) for line in gt.read_text(encoding="utf-8").splitlines()]
    assert len(public_rows) == len(gt_rows) == 400
    assert public_rows[2]["question"] == ""
    assert public_rows[3]["question"] == public_rows[4]["question"]
    assert gt_rows[0]["arxiv_id"] == ["hep-th/9901001"]
    assert gt_rows[1]["arxiv_id"] == []


def test_empty_question_candidate_record_issues_no_provider_request(tmp_path: Path) -> None:
    module = _module()
    public = tmp_path / "public.jsonl"
    output = tmp_path / "candidate.jsonl"
    trace = tmp_path / "trace.jsonl"
    public.write_text(
        json.dumps({"task_id": "arb-wide-0001", "question": ""}) + "\n",
        encoding="utf-8",
    )

    manifest = module.run_candidate(
        public,
        output,
        trace,
        max_results=20,
        limit=None,
    )
    assert manifest["tasks_attempted"] == 1
    assert manifest["provider_requests"] == 0
    assert manifest["empty_question_records_without_provider_request"] == 1
    candidate = json.loads(output.read_text(encoding="utf-8"))
    assert candidate["input_data"] == {"question": ""}
    assert candidate["inference_results"][0]["final_candidates"] == []
    assert candidate["inference_results"][0]["status"] == "benchmark_empty_question"
