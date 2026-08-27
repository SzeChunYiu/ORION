"""P5 tables preserve 21/24 and bound the later instrument-only 24/24 result."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.study.p5.tables import (
    CANNOT_CHECK_PRESENTATION,
    EXIT_ERROR,
    EXPECTED_CORRECT,
    EXPECTED_INCORRECT,
    EXPECTED_RESIDUAL_ERRORS,
    EXPECTED_TOTAL,
    STATUS_CANNOT_CHECK,
    STATUS_OK,
    cannot_check_artifact,
    generate,
    load_records,
    main,
    render_cannot_check_tex,
    verify_frozen_archive,
)


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "orion-15-self-orion"
ARCHIVE = PAPER / "evidence" / "glm-5.2-attribution" / "results.jsonl"
REPORT = PAPER / "evidence" / "glm-5.2-attribution" / "report.json"


def test_raw_jsonl_is_21_of_24_with_three_named_errors() -> None:
    records, digest = load_records(ARCHIVE)
    metrics = verify_frozen_archive(records)

    assert len(digest) == 64
    assert metrics["correct_attributions"] == EXPECTED_CORRECT
    assert metrics["incorrect_attributions"] == EXPECTED_INCORRECT
    assert metrics["total_cases"] == EXPECTED_TOTAL
    actual = tuple(
        (row["case_id"], row["gold"], row["attributed"]) for row in metrics["residual_errors"]
    )
    assert actual == EXPECTED_RESIDUAL_ERRORS


def test_twenty_four_of_twenty_four_is_refused(tmp_path: Path) -> None:
    records, _ = load_records(ARCHIVE)
    poisoned = []
    for record in records:
        row = dict(record)
        row["attributed_root_cause"] = row["gold_root_cause"]
        row["correct"] = True
        poisoned.append(row)

    with pytest.raises(ValueError, match="24/24"):
        verify_frozen_archive(poisoned)


def test_dropping_a_residual_error_is_refused() -> None:
    records, _ = load_records(ARCHIVE)
    dropped = []
    for record in records:
        row = dict(record)
        if row["case_id"] == "P5-HC-002":
            row["attributed_root_cause"] = row["gold_root_cause"]
            row["correct"] = True
        dropped.append(row)

    with pytest.raises(ValueError, match="21/24"):
        verify_frozen_archive(dropped)


def test_generate_populates_p5_3_and_leaves_campaign_tables_cannot_check(
    tmp_path: Path,
) -> None:
    out = tmp_path / "tables"
    tex = tmp_path / "tex"
    tables = generate(ARCHIVE, REPORT, out, tex)

    assert tables["P5-3_cause_confusion"]["status"] == STATUS_OK
    assert tables["P5-3_cause_confusion"]["correct"] == 21
    assert tables["P5-3_cause_confusion"]["incorrect"] == 3
    assert tables["P5-3_cause_confusion"]["macro_precision"] == pytest.approx(0.8958333333333334)
    assert tables["P5-3_cause_confusion"]["macro_recall"] == pytest.approx(0.875)
    assert tables["P5-3_cause_confusion"]["macro_f1"] == pytest.approx(0.8726190476190476)
    assert tables["P5-ATTRIBUTION_RESIDUAL_ERRORS"]["n_errors"] == 3
    for key in (
        "P5-2_replay_vs_fresh_scatter",
        "P5-4_longitudinal_specialist_regression",
        "P5-5_improvement_integrity_frontier",
        "P5-6_failure_recurrence",
        "P5-7_cost_to_validated_improvement",
        "P5-T2_baseline_ablation_results",
        "P5-T3_harmful_null_interventions",
    ):
        assert tables[key]["status"] == STATUS_CANNOT_CHECK
        assert tables[key]["numbers"] is None

    index = json.loads((out / "INDEX.json").read_text(encoding="utf-8"))
    assert index["headline"].startswith("21/24")
    assert index["empirical_authority_h1"] == STATUS_CANNOT_CHECK
    assert index["stale_24_of_24_rejected"] is True


def test_cli_verifies_frozen_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT)
    out = tmp_path / "tables"
    tex = tmp_path / "tex"
    code = main(
        [
            "--archive",
            str(ARCHIVE),
            "--report",
            str(REPORT),
            "--out",
            str(out),
            "--tex-out",
            str(tex),
        ]
    )
    assert code == 0
    tex_text = (tex / "P5-3_cause_confusion.tex").read_text(encoding="utf-8")
    assert "21/24" in tex_text
    assert "P5-HC-002" in tex_text
    assert "24/24" not in tex_text


def test_cli_refuses_relabeled_successes(tmp_path: Path) -> None:
    poisoned = tmp_path / "results.jsonl"
    rows = []
    for line in ARCHIVE.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        record["attributed_root_cause"] = record["gold_root_cause"]
        record["correct"] = True
        rows.append(record)
    poisoned.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps(
            {
                "metrics": {
                    "total_cases": 24,
                    "correct_attributions": 24,
                    "incorrect_attributions": 0,
                    "accuracy": 1.0,
                },
                "per_case_summary": [],
            }
        ),
        encoding="utf-8",
    )
    code = main(
        [
            "--archive",
            str(poisoned),
            "--report",
            str(report),
            "--out",
            str(tmp_path / "out"),
            "--tex-out",
            str(tmp_path / "tex"),
        ]
    )
    assert code == EXIT_ERROR


def test_claim_ledger_preserves_21_of_24_and_cannot_check_h1() -> None:
    ledger = json.loads(
        (PAPER / "evidence" / "CLAIM_LEDGER_V1.json").read_text(encoding="utf-8")
    )
    assert ledger["attribution"]["correct"] == 21
    assert ledger["attribution"]["total"] == 24
    assert ledger["attribution"]["incorrect"] == 3
    actual = [tuple(row) for row in ledger["attribution"]["residual_errors"]]
    assert actual == [tuple(item) for item in EXPECTED_RESIDUAL_ERRORS]
    assert ledger["hypotheses"]["H1"] == "CANNOT_CHECK"
    assert ledger["hypotheses"]["H2"] == "CANNOT_CHECK"
    assert ledger["hypotheses"]["H3"] == "CANNOT_CHECK"
    assert ledger["hypotheses"]["H4"] == "CANNOT_CHECK"
    assert ledger["empirical_authority"] == "CANNOT_CHECK"
    assert ledger["peer_review_ready"] is False
    assert ledger["stale_perfect_score_rejected"] is True

    instrument_claims = [claim for claim in ledger["claims"] if claim["claim_id"] == "P5-C21"]
    assert len(instrument_claims) == 1
    instrument_claim = instrument_claims[0]
    assert "21/24" in instrument_claim["sentence"]
    assert "instrument records 24/24" in instrument_claim["sentence"]
    assert instrument_claim["support_type"] == (
        "POST_OUTCOME_PUBLIC_SUITE_INSTRUMENT_DIAGNOSIS_ONLY__"
        "PREREGISTRATION_CHRONOLOGY_CANNOT_CHECK__"
        "NO_FRESH_TRANSFER_OR_MODEL_CAPABILITY_CLAIM"
    )
    assert "post-outcome 24/24 instrument result is diagnosis-only" in ledger["purpose"]
    assert "no general scientific authority" in ledger["purpose"]

    md = (PAPER / "evidence" / "CLAIM_LEDGER_V1.md").read_text(encoding="utf-8")
    assert "21/24" in md
    assert "ORION-15-HC-002" in md
    assert "ORION-15-HC-012" in md
    assert "ORION-15-HC-018" in md
    assert md.count("24/24") == 1
    assert "## NR-01 attribution-instrument V2 disposition" in md
    assert "treatment records 24/24" in md
    assert "independent pre-outcome registration chronology is `CANNOT_CHECK`" in md
    assert "`POST_OUTCOME_PUBLIC_SUITE_INSTRUMENT_DIAGNOSIS_ONLY`" in md
    assert "not new model capability, fresh\ntransfer, H1--H4, comparative performance or superiority" in md


def test_manuscript_does_not_claim_stale_perfect_score() -> None:
    sections = list((PAPER / "manuscript" / "sections").glob("*.tex"))
    sections.append(PAPER / "manuscript" / "main.tex")
    blob = "\n".join(path.read_text(encoding="utf-8") for path in sections)
    assert "21/24" in blob
    assert "P5-HC-002" in blob
    assert "perfect attribution" not in blob.lower()

    result_text = (
        PAPER / "manuscript" / "sections" / "09-results-attribution.tex"
    ).read_text(encoding="utf-8")
    assert result_text.count("24/24") == 1
    assert "Post-outcome public-suite instrument diagnosis" in result_text
    assert "instrument returns 24/24" in result_text
    assert "not evidence that a model acquired new attribution capability" in result_text
    assert "independent pre-outcome registration chronology is\n\\textsc{CannotCheck}" in result_text
    assert "H1--H4, protected freshness, comparative\nperformance and superiority remain \\textsf{CANNOT\\_CHECK}" in result_text

    limitation_text = (
        PAPER / "manuscript" / "sections" / "10-limitations.tex"
    ).read_text(encoding="utf-8")
    assert limitation_text.count("24/24") == 2
    assert "24/24 V2 attribution result is an instrument-stage diagnosis" in limitation_text
    assert "independent preregistration chronology is therefore \\textsc{CannotCheck}" in limitation_text
    assert "this result cannot establish model\nimprovement, general attribution accuracy, H1--H4 or superiority" in limitation_text

    other_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sections
        if path.name not in {"09-results-attribution.tex", "10-limitations.tex"}
    )
    assert "24/24" not in other_text


def _brace_balance(text: str) -> int:
    r"""Net brace depth, ignoring TeX's escaped literals ``\{`` and ``\}``."""

    depth = 0
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        index += 1
    return depth


@pytest.mark.parametrize("table_id", sorted(CANNOT_CHECK_PRESENTATION))
def test_awaiting_campaign_tables_compile_and_name_what_is_absent(table_id: str) -> None:
    """A stub whose caption cannot compile reports nothing at all.

    The previous renderer built its caption by concatenating an f-string with a
    plain one, so the plain half's ``}}`` reached the file as two braces and TeX
    would have rejected every one of these tables. It also collapsed each table
    to a single ``Result`` column, which tells a reader that *something* could
    not be measured but never which measurement is missing. Both are checked
    here because both were invisible until a byte-identity gate caught the drift
    rather than a test.
    """

    rendered = render_cannot_check_tex(cannot_check_artifact(table_id, table_id))
    assert _brace_balance(rendered) == 0
    presentation = CANNOT_CHECK_PRESENTATION[table_id]
    headers = presentation["headers"]
    assert len(headers) >= 2, "a one-column stub names no measurement"
    assert len(presentation["column_spec"]) == len(headers)
    for header in headers:
        assert header in rendered
    assert f"\\multicolumn{{{len(headers)}}}" in rendered
    assert "CANNOT\\_CHECK" in rendered
    assert not rendered.endswith("\n")


def test_every_cannot_check_table_has_a_shape_declared(tmp_path: Path) -> None:
    """Adding a table without its columns must fail here, not at TeX time."""

    generated = generate(ARCHIVE, REPORT, tmp_path / "evidence", tmp_path / "tex")
    blocked = {
        key for key, table in generated.items() if table["status"] == STATUS_CANNOT_CHECK
    }
    assert blocked, "no CANNOT_CHECK tables; this test is inert"
    assert blocked == set(CANNOT_CHECK_PRESENTATION)
