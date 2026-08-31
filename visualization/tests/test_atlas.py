from __future__ import annotations

import importlib.util
import hashlib
import json
import os
from pathlib import Path

import pytest


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


def execute_notebook_with_parameters(name: str, overrides: dict[str, object]) -> dict:
    notebook = json.loads((VIS / "notebooks" / name).read_text(encoding="utf-8"))
    namespace: dict[str, object] = {"__name__": "__review_test__"}
    previous = Path.cwd()
    try:
        os.chdir(VIS)
        for index, cell in enumerate(notebook["cells"]):
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell.get("source", []))
            exec(compile(source, f"{name}:{index}", "exec"), namespace, namespace)
            if "plt" in namespace:
                namespace["plt"].show = lambda *args, **kwargs: None
            if "parameters" in cell.get("metadata", {}).get("tags", []):
                namespace.update(overrides)
        return namespace
    finally:
        os.chdir(previous)


def test_atlas_has_exact_canonical_paper_and_source_counts() -> None:
    atlas = load_atlas()
    assert atlas["schema"] == "orion.visualization.evidence-atlas.v1"
    assert [row["paper"] for row in atlas["paper_states"]] == [f"P{i}" for i in range(1, 16)]
    assert len(atlas["gate_states"]) == 45
    assert len(atlas["sources"]) == 43
    assert len(atlas["anomalies"]) == 14
    assert sorted(atlas["metrics"]) == sorted(f"P{i}" for i in range(1, 16))
    assert atlas["authority_boundary"] == "REPOSITORY_RECEIPTS_ONLY__NO_EXTERNAL_AUTHORITY_DELTA"


def test_frozen_des_execution_layer_preserves_attempted_valid_and_authority_boundaries() -> None:
    atlas = load_atlas()
    rows = {row["paper"]: row for row in atlas["des_execution"]}
    assert list(rows) == [f"P{i}" for i in range(1, 16)]
    assert rows["P2"]["planned"] == rows["P2"]["observed"] == rows["P2"]["valid"] == 400
    assert rows["P4"]["planned"] == 1500
    assert rows["P4"]["observed"] == 900
    assert rows["P4"]["valid"] == 0
    assert rows["P7"]["planned"] == 738
    assert rows["P7"]["observed"] == 736
    assert rows["P7"]["valid"] == 0
    assert rows["P13"]["planned"] == 720
    assert rows["P13"]["observed"] == rows["P13"]["valid"] == 288
    assert all(row["external_authority_state"] == "CANNOT_CHECK" for row in rows.values())
    assert all(row["paper_authority_delta"] == "NONE" for row in rows.values())
    assert all(0 <= row["valid"] <= row["observed"] <= row["planned"] for row in rows.values())


def test_frozen_des_claim_ceilings_are_non_null_and_source_bound() -> None:
    atlas = load_atlas()
    rows = {row["paper"]: row for row in atlas["des_execution"]}

    assert all(
        isinstance(row["claim_ceiling"], str) and row["claim_ceiling"]
        for row in rows.values()
    )
    assert rows["P12"]["claim_ceiling"] == "THEORY_PLUS_STOP_GO_BOUNDARY"
    assert rows["P12"]["claim_ceiling_source_id"] == "portfolio_claim_ledger"


def test_p9_des_catalog_schema_matches_the_bound_packet() -> None:
    source = next(
        row for row in load_atlas()["sources"] if row["id"] == "p9_des_packet"
    )

    expected = "orion.p9-des.result-binding-packet.v1"
    assert source["declared_schema"] == expected
    assert source["detected_schema"] == expected


def test_des_source_manifest_rejects_declared_schema_mismatch(tmp_path: Path) -> None:
    builder = load_script("build_data.py")
    receipt = tmp_path / "receipt.json"
    receipt.write_text('{"schema":"actual.schema.v1"}\n', encoding="utf-8")
    catalog = {
        "sources": [
            {
                "id": "receipt",
                "paper": "P1",
                "path": "receipt.json",
                "schema": "declared.schema.v1",
                "role": "test receipt",
                "authority_tier": "TEST_ONLY",
                "transform_id": "des-coverage-v1",
                "fields": ["schema"],
            }
        ]
    }

    with pytest.raises(ValueError, match="declared schema mismatch"):
        builder.source_manifest(tmp_path, catalog)


def test_framework_mechanics_layer_retains_finite_counts_failures_and_censoring() -> None:
    mechanics = load_atlas()["framework_mechanics"]
    collision = mechanics["collision"]
    assert collision["state_count"] == 144
    assert collision["same_terminal_pairs"] == 9201
    assert collision["different_action_pairs"] == 4355
    update = mechanics["update_algebra"]
    assert update["law_failures"] == 0
    assert update["mutations_killed"] == update["mutation_count"] == 6
    projection = mechanics["projection"]
    assert projection["matched_rows"] == projection["row_denominator"] == 5760
    assert projection["noninjective_groups"] == 7
    assert projection["action_divergent_groups"] == 6
    census = mechanics["census"]
    assert census["occurrences"] == 316842
    assert census["classified_occurrences"] + census["unclassified_occurrences"] == census["occurrences"]
    assert census["likely_text_cap_censored_count"] == 2
    assert census["terminal"] == "RESOURCE_CAP_CENSORED"


def test_load_bearing_anomaly_claims_are_bound_to_exact_registered_receipts() -> None:
    atlas = load_atlas()
    source_ids = {row["id"] for row in atlas["sources"]}
    expected = {
        "p9_replay_revival",
        "p12_active_authority",
        "p13_historical_boundary",
        "p14_external_pilot",
        "p15_active_authority",
    }
    assert expected <= source_ids

    anomalies = {row["paper"]: row for row in atlas["anomalies"]}
    assert anomalies["P9"]["source_ids"] == ["p9_diagnostic", "p9_replay_revival"]
    assert anomalies["P12"]["source_ids"] == [
        "p12_signal_complementarity",
        "p12_active_authority",
    ]
    assert anomalies["P13"]["source_ids"] == [
        "p13_composed_safety",
        "p13_historical_boundary",
    ]
    assert anomalies["P14"]["source_ids"] == ["p14_governance", "p14_external_pilot"]
    assert anomalies["P15"]["source_ids"] == ["p15_workflows", "p15_active_authority"]

    metrics = atlas["metrics"]
    assert metrics["P9"]["replay_boundary"]["archived_accuracy"] == 0.5
    assert metrics["P9"]["replay_boundary"]["locked_reproduction_accuracy"] == 0.75
    assert metrics["P12"]["forward_time_state"] == "CANNOT_CHECK"
    assert metrics["P12"]["public_data_campaign_executed"] is False
    assert metrics["P13"]["historical_negative"]["observed_max_deviation"] == 0.0556640625
    assert metrics["P14"]["external_pilot"]["authority_status"] == "NOT_AUTHORITY"
    assert metrics["P15"]["full_key_compromise"]["signature_detections"] == 0
    assert metrics["P15"]["full_key_compromise"]["false_promotions"] == 6


def test_evidence_snapshot_is_content_derived_and_non_self_referential() -> None:
    atlas = load_atlas()
    source_manifest = json.loads(
        (VIS / "data/manifests/source_manifest.json").read_text(encoding="utf-8")
    )
    snapshot = atlas["evidence_snapshot"]
    assert snapshot == source_manifest["evidence_snapshot"]
    assert snapshot["source_count"] == len(atlas["sources"])
    canonical = [
        {
            key: source[key]
            for key in ("bytes", "declared_schema", "id", "path", "sha256")
        }
        for source in atlas["sources"]
    ]
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    assert snapshot["source_set_sha256"] == hashlib.sha256(payload).hexdigest()
    for generated in (atlas, source_manifest):
        assert "subject_commit" not in generated
        assert "subject_tree" not in generated

    output_manifest = json.loads(
        (VIS / "generated/manifests/output_manifest.json").read_text(encoding="utf-8")
    )
    assert "python" not in output_manifest
    assert "renderers" not in output_manifest


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
    assert len(paths) == 6
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


def test_governance_notebook_nondefault_metric_uses_neutral_dynamic_copy() -> None:
    namespace = execute_notebook_with_parameters(
        "03_p11_p15_state_governance_harness.ipynb",
        {"METRIC_NAME": "compiled_minus_universal_delta", "MIN_VALUE": None},
    )
    ax = namespace["ax"]
    assert len(namespace["selected_metrics"]) == 30
    assert "compiled minus universal delta" in ax.get_title().lower()
    assert "unsafe reuse" not in ax.get_title().lower()
    assert "p13" not in ax.get_title().lower()
    assert "lower is better" not in ax.get_xlabel().lower()


def test_des_notebook_keeps_planned_observed_valid_and_authority_separate() -> None:
    namespace = execute_notebook_with_parameters("05_frozen_des_execution.ipynb", {})
    rows = {row["paper"]: row for row in namespace["selected_des"]}
    assert len(rows) == 15
    assert rows["P4"]["planned"] == 1500
    assert rows["P4"]["observed"] == 900
    assert rows["P4"]["valid"] == 0
    assert rows["P7"]["planned"] == 738
    assert rows["P7"]["observed"] == 736
    assert rows["P7"]["valid"] == 0
    assert all(row["external_authority_state"] == "CANNOT_CHECK" for row in rows.values())


def test_anomaly_notebook_has_no_unsupported_ordinal_severity_filter() -> None:
    path = VIS / "notebooks/04_anomaly_audit.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    code = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )
    assert "SEVERITY_RANK" not in code
    assert "MIN_SEVERITY_RANK" not in code

    namespace = execute_notebook_with_parameters(path.name, {})
    assert len(namespace["selected_anomalies"]) == 14
    assert {row["severity"] for row in namespace["selected_anomalies"]} == {
        "ADVERSE",
        "BOUNDARY",
        "CANNOT_CHECK",
        "FAIL",
        "MIXED",
        "NOT_AUTHORITY",
        "NULL",
    }


def test_interactive_html_is_self_contained_and_filterable() -> None:
    text = (VIS / "figures/interactive/evidence_atlas.html").read_text(encoding="utf-8")
    lower = text.lower()
    assert "http://" not in lower and "https://" not in lower
    assert "<script src=" not in lower and "<link rel=" not in lower
    for required in (
        "atlas-data",
        'id="paper"',
        'id="metric"',
        'id="des-execution"',
        'id="anomalies"',
    ):
        assert required in text
    for responsive_or_signed in (
        "@media(max-width:650px)",
        ".bar-row{grid-template-columns:1fr}",
        ".controls{display:grid;grid-template-columns:minmax(0,1fr);position:static}",
        ".controls select,.controls input{margin-left:0;max-width:100%;width:100%;min-width:0}",
        ".boundary{overflow-wrap:anywhere}",
        ".source-table{min-width:",
        ".source-hash{white-space:nowrap}",
        'class="zero"',
        'class="des-zero"',
        "x.value<0?'negative'",
    ):
        assert responsive_or_signed in text


def test_figure_copy_separates_receipt_disposition_from_external_authority() -> None:
    gate_svg = (VIS / "figures/static/svg/01_paper_gate_matrix.svg").read_text(
        encoding="utf-8"
    )
    assert ">MIXED<" in gate_svg

    p15_svg = (VIS / "figures/static/svg/12_p15_workflow_matrix.svg").read_text(
        encoding="utf-8"
    )
    assert "3 receipt-level AUTHORIZED_SCIENCE" in p15_svg
    assert "not publication or external authority" in p15_svg

    p14_svg = (VIS / "figures/static/svg/11_p14_governance_rates.svg").read_text(
        encoding="utf-8"
    )
    assert "fixed 0–1 scale; padded endpoints" in p14_svg

    p12_svg = (VIS / "figures/static/svg/09_p12_family_blocks_by_sigma.svg").read_text(
        encoding="utf-8"
    )
    assert "mean labels use a separate top annotation band" in p12_svg

    des_svg = (VIS / "figures/static/svg/13_des_execution_coverage.svg").read_text(
        encoding="utf-8"
    )
    assert "not performance" in des_svg
    assert "external-authority states remain CANNOT CHECK" in des_svg

    mechanics_svg = (
        VIS / "figures/static/svg/14_framework_mechanics_receipts.svg"
    ).read_text(encoding="utf-8")
    assert "finite internal receipts only" in mechanics_svg


def test_generated_svgs_have_no_trailing_whitespace() -> None:
    paths = sorted((VIS / "figures/static/svg").glob("*.svg"))
    assert len(paths) == 15
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        assert all(line == line.rstrip() for line in lines), path.name


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
        "13_des_execution_coverage",
        "14_framework_mechanics_receipts",
    }
    audit = (VIS / "reports/FIGURE_QA.md").read_text(encoding="utf-8")
    assert "no KDE" in audit
