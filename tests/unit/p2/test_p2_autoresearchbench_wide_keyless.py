from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(
    "papers/orion-12-open-world-scientific-discovery/scripts/run_autoresearchbench_wide_keyless.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("p2_arb_wide", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_prepare_splits_all_400_wide_tasks_before_candidate_custody(tmp_path: Path) -> None:
    module = _module()
    full = tmp_path / "full.jsonl"
    public = tmp_path / "public.jsonl"
    gt = tmp_path / "gt.jsonl"
    rows = [
        {
            "question": f"Which event-based representation study number {index} uses masked modeling?",
            "answer": [f"Secret paper {index}"],
            "arxiv_id": [f"24{index % 100:02d}.{index:05d}"],
        }
        for index in range(400)
    ]
    rows.append(
        {
            "question": "deep task",
            "answer": ["secret deep paper"],
            "arxiv_id": "2401.01234",
        }
    )
    full.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    manifest = module.prepare(full, public, gt)
    assert manifest["wide_tasks"] == 400
    assert manifest["candidate_hidden_label_paths"] == []
    public_rows = [json.loads(line) for line in public.read_text(encoding="utf-8").splitlines()]
    gt_rows = [json.loads(line) for line in gt.read_text(encoding="utf-8").splitlines()]
    assert len(public_rows) == len(gt_rows) == 400
    assert set(public_rows[0]) == {"task_id", "question"}
    assert "answer" not in json.dumps(public_rows)
    assert "arxiv_id" not in json.dumps(public_rows)
    assert "arxiv_id" in gt_rows[0]


def test_query_derivation_is_public_question_only_and_deterministic() -> None:
    module = _module()
    question = (
        "Which event-based vision methods use masked self-supervised modeling "
        "with neuromorphic deployment and voxel representations?"
    )
    first = module.derive_query(question)
    second = module.derive_query(question)
    assert first == second
    assert "all:" in first
    assert "answer" not in first.lower()


def test_candidate_output_matches_official_wide_contract_without_gold(tmp_path: Path) -> None:
    module = _module()
    public = tmp_path / "public.jsonl"
    output = tmp_path / "candidate.jsonl"
    trace = tmp_path / "trace.jsonl"
    public.write_text(
        json.dumps(
            {
                "task_id": "arb-wide-0001",
                "question": "Which masked event modeling methods use neuromorphic vision transformers?",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    atom = """<?xml version='1.0' encoding='UTF-8'?>
    <feed xmlns='http://www.w3.org/2005/Atom'>
      <entry>
        <id>http://arxiv.org/abs/2401.01234v1</id>
        <title>Masked Event Modeling</title>
        <summary>event camera pretraining</summary>
      </entry>
    </feed>"""

    module._transport = lambda url: module.TransportResponse(200, atom, {})
    manifest = module.run_candidate(public, output, trace, max_results=20, limit=None)
    assert manifest["hidden_labels_visible_to_candidate"] is False
    record = json.loads(output.read_text(encoding="utf-8"))
    assert set(record["input_data"]) == {"question"}
    candidates = record["inference_results"][0]["final_candidates"]
    assert candidates == [{"arxiv_id": "2401.01234", "title": "Masked Event Modeling"}]
