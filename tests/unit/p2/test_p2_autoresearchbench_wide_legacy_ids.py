from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(
    "papers/paper-02-open-world-scientific-discovery/scripts/run_autoresearchbench_wide_compat.py"
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


def test_prepare_preserves_legacy_only_wide_targets_without_candidate_leak(tmp_path: Path) -> None:
    module = _module()
    full = tmp_path / "full.jsonl"
    public = tmp_path / "public.jsonl"
    gt = tmp_path / "gt.jsonl"
    rows = []
    for index in range(400):
        target = (
            [f"hep-th/{9901001 + index}"]
            if index == 0
            else [f"24{index % 100:02d}.{index:05d}"]
        )
        rows.append(
            {
                "question": f"Unique public research question {index} about representation learning",
                "answer": [f"hidden title {index}"],
                "arxiv_id": target,
            }
        )
    full.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    manifest = module.prepare(full, public, gt)
    assert manifest["wide_tasks"] == 400
    assert manifest["legacy_target_id_count"] == 1
    public_text = public.read_text(encoding="utf-8")
    assert "arxiv_id" not in public_text
    assert "hidden title" not in public_text
    gt_rows = [json.loads(line) for line in gt.read_text(encoding="utf-8").splitlines()]
    assert gt_rows[0]["arxiv_id"] == ["hep-th/9901001"]
