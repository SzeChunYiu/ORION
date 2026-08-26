from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VIS = ROOT / "visualization"


def load_atlas() -> dict:
    return json.loads((VIS / "data/derived/atlas.json").read_text(encoding="utf-8"))


def load_script(name: str):
    path = VIS / "scripts" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_atlas_has_exact_canonical_paper_and_source_counts() -> None:
    atlas = load_atlas()
    assert atlas["schema"] == "orion.visualization.evidence-atlas.v1"
    assert [row["paper"] for row in atlas["paper_states"]] == [f"P{i}" for i in range(1, 16)]
    assert len(atlas["gate_states"]) == 45
    assert len(atlas["sources"]) == 18
    assert len(atlas["anomalies"]) == 14
    assert sorted(atlas["metrics"]) == sorted(f"P{i}" for i in range(1, 16))
    assert atlas["authority_boundary"] == "REPOSITORY_RECEIPTS_ONLY__NO_EXTERNAL_AUTHORITY_DELTA"


def test_adverse_and_cannot_check_rows_are_not_hidden() -> None:
    atlas = load_atlas()
    by_paper = {row["paper"]: row for row in atlas["anomalies"]}
    assert by_paper["P2"]["severity"] == "FAIL"
    assert "175.7%" in by_paper["P2"]["finding"]
    assert by_paper["P5"]["severity"] == "ADVERSE"
    assert "glm-5.2" in by_paper["P5"]["finding"]
    assert by_paper["P7"]["severity"] == "FAIL"
    assert by_paper["P9"]["severity"] == "CANNOT_CHECK"
    assert by_paper["P10"]["severity"] == "CANNOT_CHECK"
    assert by_paper["P11"]["severity"] == "FAIL"
    assert by_paper["P14"]["severity"] == "NOT_AUTHORITY"
    assert by_paper["P15"]["severity"] == "MIXED"


def test_receipt_denominators_and_terminals_match_expected_sources() -> None:
    metrics = load_atlas()["metrics"]
    assert metrics["P2"]["topic_count"] == 50
    assert metrics["P2"]["gate"]["overall"] == "FAIL"
    assert metrics["P3"]["case_count"] == 32
    assert metrics["P5"]["requested_model"] == "glm-5.2"
    assert {model for row in metrics["P5"]["arms"] for model in row["served_models"]} == {"glm-5.3"}
    assert metrics["P6"]["state_evaluations"] == 320
    assert metrics["P6"]["distinct_state_evaluations"] == 64
    assert (metrics["P7"]["planned_cases"], metrics["P7"]["observed_cases"]) == (738, 736)
    assert metrics["P9"]["scored_rows"] == 4
    assert metrics["P9"]["cannot_check_rows"] == 1
    assert metrics["P10"]["outcome_accessed"] is False
    assert metrics["P11"]["support_counts"] == {"KNN": 5, "LINEAR": 3, "RBF": 5}
    assert metrics["P11"]["terminal"].endswith("GATE_NOT_MET")
    assert len(metrics["P12"]["families"]) == 32
    assert len(metrics["P13"]["arms"]) == 5
    assert len(metrics["P13"]["worlds"]) == 4
    assert metrics["P14"]["case_count"] == 28
    assert (metrics["P15"]["authorized_count"], metrics["P15"]["cannot_check_count"]) == (3, 1)


def test_metric_records_keep_one_exact_metric_and_unit_per_row() -> None:
    atlas = load_atlas()
    records = atlas["metric_records"]
    assert len(records) >= 200
    for row in records:
        assert row["paper_id"] in {f"P{i}" for i in range(1, 16)}
        assert isinstance(row["metric"], str) and row["metric"]
        assert isinstance(row["unit"], str) and row["unit"]
        assert isinstance(row["value"], (int, float)) and not isinstance(row["value"], bool)
        assert row["source_id"] in {source["id"] for source in atlas["sources"]}


def test_source_validator_distinguishes_checked_drift_and_absence(tmp_path: Path) -> None:
    validator = load_script("validate_sources.py")
    root = tmp_path / "repo"
    catalog = root / "visualization/source_catalog.json"
    source = root / "receipt.json"
    catalog.parent.mkdir(parents=True)
    catalog.write_text("{}\n", encoding="utf-8")
    source.write_text('{"status":"FAIL"}\n', encoding="utf-8")
    manifest = {
        "source_catalog_sha256": validator.sha256(catalog),
        "sources": [{"id": "receipt", "path": "receipt.json", "sha256": validator.sha256(source)}],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert validator.validate(root, manifest_path)["overall"] == "CHECKED"
    source.write_text('{"status":"PASS"}\n', encoding="utf-8")
    assert validator.validate(root, manifest_path)["overall"] == "DRIFT"
    source.unlink()
    assert validator.validate(root, manifest_path)["overall"] == "CANNOT_CHECK"


def test_notebooks_are_valid_json_with_latex_parameters_and_compilable_code() -> None:
    paths = sorted((VIS / "notebooks").glob("*.ipynb"))
    assert len(paths) == 5
    for path in paths:
        notebook = json.loads(path.read_text(encoding="utf-8"))
        assert notebook["nbformat"] == 4
        assert any(
            "parameters" in cell.get("metadata", {}).get("tags", []) for cell in notebook["cells"]
        )
        markdown = "\n".join(
            "".join(cell.get("source", []))
            for cell in notebook["cells"]
            if cell["cell_type"] == "markdown"
        )
        assert "$$" in markdown
        assert "Claim ceiling" in markdown or "Claim Ceiling" in markdown
        for index, cell in enumerate(notebook["cells"]):
            if cell["cell_type"] == "code":
                compile("".join(cell.get("source", [])), f"{path.name}:{index}", "exec")


def test_interactive_html_is_self_contained_and_filterable() -> None:
    text = (VIS / "figures/interactive/evidence_atlas.html").read_text(encoding="utf-8")
    lower = text.lower()
    assert "http://" not in lower and "https://" not in lower
    assert "<script src=" not in lower and "<link rel=" not in lower
    for required in ("atlas-data", 'id="paper"', 'id="metric"', 'id="anomalies"'):
        assert required in text
    for responsive_or_signed in (
        "@media(max-width:650px)",
        ".bar-row{grid-template-columns:1fr}",
        'class="zero"',
        "x.value<0?'negative'",
    ):
        assert responsive_or_signed in text


def test_static_figure_set_uses_audited_plot_grammars() -> None:
    names = {path.stem for path in (VIS / "figures/static/png").glob("*.png")}
    assert names == {
        "00_framework_map",
        "01_paper_gate_matrix",
        "02_p1_hidden_shift_forest",
        "03_p1_cost_success_pareto",
        "04_p2_retrieval_rates",
        "05_p3_accuracy_forest",
        "06_p6_p7_formal_counts",
        "07_p11_delta_ecdf",
        "08_p11_delta_strip",
        "09_p12_family_blocks_by_sigma",
        "10_p13_three_objective_tradeoff",
        "11_p14_governance_rates",
        "12_p15_workflow_matrix",
    }
    audit = (VIS / "reports/FIGURE_QA.md").read_text(encoding="utf-8")
    assert "no KDE" in audit
