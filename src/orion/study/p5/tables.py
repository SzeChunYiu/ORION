"""Publication tables for ORION-P5 (issue #102) from archived raw records.

Archived records only. The glm-5.2 hidden-cause attribution JSONL is the only
result-bearing archive on the current subject. It supports the confusion matrix
(P5-3) and the retained residual-error ledger. It does **not** contain replay
scores, improvement rounds, baseline/ablation arms, recurrence annotations, or
protected-improvement cost, so P5-2/P5-4/P5-5/P5-6/P5-7 and Table P5-T2 remain
``CANNOT_CHECK`` with no fabricated numbers.

The frozen archive is 21/24 with three named residual errors. A 24/24 rewrite,
dropped errors, or a mismatched report.json is an integrity failure (exit 2),
not a success.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from orion.study.p5.freeze import ROOT_CAUSES
from orion.study.statistics import wilson_interval

EXIT_OK = 0
EXIT_ERROR = 2
EXIT_CANNOT_CHECK = 3

STATUS_OK = "OK"
STATUS_CANNOT_CHECK = "CANNOT_CHECK"

FAMILY_ORDER = (
    "RETRIEVAL_MISS",
    "ROUTING_PLANNING_MISS",
    "IMPLEMENTATION_BUG",
    "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE",
    "EVALUATOR_METRIC_BUG",
    "REPRESENTATION_GAP",
    "MEASUREMENT_SPECIFICATION_GAP",
    "METHOD_BASIS_GAP",
)

EXPECTED_TOTAL = 24
EXPECTED_CORRECT = 21
EXPECTED_INCORRECT = 3
EXPECTED_RESIDUAL_ERRORS = (
    ("P5-HC-002", "RETRIEVAL_MISS", "REPRESENTATION_GAP"),
    ("P5-HC-012", "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE", "IMPLEMENTATION_BUG"),
    ("P5-HC-018", "REPRESENTATION_GAP", "METHOD_BASIS_GAP"),
)

PAPER = Path("papers/paper-05-self-orion")
DEFAULT_ARCHIVE = PAPER / "evidence" / "glm-5.2-attribution" / "results.jsonl"
DEFAULT_REPORT = PAPER / "evidence" / "glm-5.2-attribution" / "report.json"
DEFAULT_OUTPUT = PAPER / "evidence" / "tables"
DEFAULT_TEX = PAPER / "manuscript" / "tables"

CAMPAIGN_PLOTS = (
    "P5-2_replay_vs_fresh_scatter",
    "P5-4_longitudinal_specialist_regression",
    "P5-5_improvement_integrity_frontier",
    "P5-6_failure_recurrence",
    "P5-7_cost_to_validated_improvement",
)

CAMPAIGN_MISSING_REASON = (
    "The archived glm-5.2 JSONL is a single-model hidden-cause attribution run. "
    "It has no motivating/replay/fresh score pairs, round identities, matched "
    "baseline/ablation arms, recurrence annotations, or protected-improvement "
    "cost. Numbers for this artifact are therefore CANNOT_CHECK; they are not "
    "imputed from attribution accuracy."
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_records(archive: Path) -> tuple[list[dict[str, Any]], str]:
    if not archive.exists():
        raise FileNotFoundError(f"attribution archive missing: {archive}")
    raw = archive.read_bytes()
    digest = _sha256_bytes(raw)
    records: list[dict[str, Any]] = []
    for line_no, line in enumerate(raw.decode("utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{archive}:{line_no} is not JSON") from exc
        if not isinstance(record, dict):
            raise ValueError(f"{archive}:{line_no} is not an object")
        records.append(record)
    if not records:
        raise ValueError(f"{archive} contains no records")
    return records, digest


def _require_str(record: Mapping[str, Any], key: str, case_id: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{case_id} missing string field {key!r}")
    return value


def verify_frozen_archive(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Recompute 21/24 from raw rows. Refuse 24/24 and dropped residual errors."""

    if len(records) != EXPECTED_TOTAL:
        raise ValueError(f"expected {EXPECTED_TOTAL} raw rows, found {len(records)}")

    case_ids: list[str] = []
    incorrect: list[dict[str, str]] = []
    confusion: dict[str, dict[str, int]] = {gold: {} for gold in FAMILY_ORDER}
    correct = 0
    for record in records:
        case_id = _require_str(record, "case_id", "?")
        if case_id in case_ids:
            raise ValueError(f"duplicate case_id {case_id}")
        case_ids.append(case_id)
        gold = _require_str(record, "gold_root_cause", case_id)
        attributed = _require_str(record, "attributed_root_cause", case_id)
        if gold not in ROOT_CAUSES:
            raise ValueError(f"{case_id} gold_root_cause {gold!r} is not a registered family")
        if attributed not in ROOT_CAUSES:
            raise ValueError(
                f"{case_id} attributed_root_cause {attributed!r} is not a registered family"
            )
        flagged = record.get("correct")
        expected_flag = gold == attributed
        if not isinstance(flagged, bool):
            raise ValueError(f"{case_id} field correct must be a boolean")
        if flagged is not expected_flag:
            raise ValueError(
                f"{case_id} correct={flagged} disagrees with gold vs attributed labels"
            )
        confusion[gold][attributed] = confusion[gold].get(attributed, 0) + 1
        if expected_flag:
            correct += 1
        else:
            incorrect.append(
                {
                    "case_id": case_id,
                    "gold": gold,
                    "attributed": attributed,
                    "confidence": _require_str(record, "confidence", case_id),
                }
            )

    incorrect_ids = tuple(item["case_id"] for item in incorrect)
    expected_ids = tuple(item[0] for item in EXPECTED_RESIDUAL_ERRORS)
    if correct == EXPECTED_TOTAL:
        raise ValueError(
            "archive reports 24/24 correct attributions; the frozen raw record is "
            "21/24 with three residual errors. Do not relabel errors as successes."
        )
    if correct != EXPECTED_CORRECT or len(incorrect) != EXPECTED_INCORRECT:
        raise ValueError(
            f"raw archive is {correct}/{len(records)} with {len(incorrect)} errors; "
            f"frozen expected {EXPECTED_CORRECT}/{EXPECTED_TOTAL} with "
            f"{EXPECTED_INCORRECT} residual errors"
        )
    if incorrect_ids != expected_ids:
        raise ValueError(
            f"residual error identities {incorrect_ids} do not match frozen "
            f"{expected_ids}; do not drop or relabel the three errors"
        )
    for item, expected in zip(incorrect, EXPECTED_RESIDUAL_ERRORS, strict=True):
        if (item["case_id"], item["gold"], item["attributed"]) != expected:
            raise ValueError(
                f"residual error {item} does not match frozen triple {expected}"
            )
    if set(case_ids) != {f"P5-HC-{index:03d}" for index in range(1, EXPECTED_TOTAL + 1)}:
        raise ValueError("case identities drifted from P5-HC-001..P5-HC-024")

    lo, hi = wilson_interval(correct, EXPECTED_TOTAL)
    per_family = []
    for family in FAMILY_ORDER:
        row = confusion[family]
        family_total = sum(row.values())
        family_correct = row.get(family, 0)
        tp = family_correct
        fp = sum(confusion[gold].get(family, 0) for gold in FAMILY_ORDER if gold != family)
        fn = family_total - tp
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
        per_family.append(
            {
                "family": family,
                "correct": family_correct,
                "total": family_total,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "tp": tp,
                "fp": fp,
                "fn": fn,
            }
        )
    macro_precision = sum(row["precision"] for row in per_family) / len(per_family)
    macro_recall = sum(row["recall"] for row in per_family) / len(per_family)
    macro_f1 = sum(row["f1"] for row in per_family) / len(per_family)
    return {
        "total_cases": EXPECTED_TOTAL,
        "correct_attributions": correct,
        "incorrect_attributions": len(incorrect),
        "accuracy": correct / EXPECTED_TOTAL,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "wilson95": {"low": lo, "high": hi},
        "confusion": confusion,
        "per_family": per_family,
        "residual_errors": incorrect,
        "case_ids": case_ids,
    }


def check_report_agrees(report_path: Path) -> None:
    if not report_path.exists():
        raise ValueError(f"sidecar report missing: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    reported = report.get("metrics") or {}
    if int(reported.get("correct_attributions", -1)) != EXPECTED_CORRECT:
        raise ValueError(
            "report.json does not retain 21 correct attributions; refuse stale 24/24 prose"
        )
    if int(reported.get("incorrect_attributions", -1)) != EXPECTED_INCORRECT:
        raise ValueError("report.json dropped the three residual errors")
    if int(reported.get("total_cases", -1)) != EXPECTED_TOTAL:
        raise ValueError("report.json total_cases drifted from 24")
    summary = report.get("per_case_summary") or []
    reported_errors = [
        (row["case_id"], row["gold"], row["attributed"])
        for row in summary
        if row.get("correct") is False
    ]
    if tuple(reported_errors) != EXPECTED_RESIDUAL_ERRORS:
        raise ValueError("report.json residual-error identities drifted from the raw JSONL")
    if int(round(float(reported.get("accuracy", 0.0)) * EXPECTED_TOTAL)) != EXPECTED_CORRECT:
        raise ValueError("report.json accuracy is inconsistent with 21/24")


def cannot_check_artifact(table_id: str, title: str) -> dict[str, Any]:
    return {
        "paper_id": "P5",
        "issue": 102,
        "table_id": table_id,
        "title": title,
        "status": STATUS_CANNOT_CHECK,
        "empirical_authority": STATUS_CANNOT_CHECK,
        "reason": CAMPAIGN_MISSING_REASON,
        "numbers": None,
        "do_not_impute_from": "glm-5.2-attribution 21/24 accuracy",
    }


def build_p5_3(metrics: Mapping[str, Any], archive_digest: str) -> dict[str, Any]:
    return {
        "paper_id": "P5",
        "issue": 102,
        "table_id": "P5-3_cause_confusion",
        "title": "Hidden-cause attribution confusion matrix (diagnostic glm-5.2 archive)",
        "status": STATUS_OK,
        "empirical_authority": "DESCRIPTIVE_ONLY",
        "scope": (
            "Single-model, single-run diagnostic attribution on the archived "
            "24-case hidden-cause suite. Not a protected fresh-transfer campaign, "
            "not H1, and not a 24/24 result."
        ),
        "archive": str(DEFAULT_ARCHIVE),
        "archive_sha256": archive_digest,
        "n_cases": metrics["total_cases"],
        "correct": metrics["correct_attributions"],
        "incorrect": metrics["incorrect_attributions"],
        "accuracy": metrics["accuracy"],
        "macro_precision": metrics["macro_precision"],
        "macro_recall": metrics["macro_recall"],
        "macro_f1": metrics["macro_f1"],
        "wilson95": metrics["wilson95"],
        "confusion": metrics["confusion"],
        "per_family": metrics["per_family"],
        "residual_errors": metrics["residual_errors"],
        "residual_errors_are_failures": True,
    }


def build_residual_error_table(metrics: Mapping[str, Any], archive_digest: str) -> dict[str, Any]:
    return {
        "paper_id": "P5",
        "issue": 102,
        "table_id": "P5-ATTRIBUTION_RESIDUAL_ERRORS",
        "title": "Retained residual attribution errors (not successes)",
        "status": STATUS_OK,
        "empirical_authority": "DESCRIPTIVE_ONLY",
        "archive_sha256": archive_digest,
        "n_errors": len(metrics["residual_errors"]),
        "errors": metrics["residual_errors"],
        "promotion_forbidden": (
            "These three rows remain incorrect attributions. They must not be "
            "relabeled as successes, excluded from the denominator, or averaged away."
        ),
    }


def render_p5_3_markdown(table: Mapping[str, Any]) -> str:
    families = FAMILY_ORDER
    header = "| gold \\ attributed | " + " | ".join(families) + " |"
    sep = "|---|---" + "|---" * (len(families) - 1) + "|"
    rows = []
    for gold in families:
        cells = [gold]
        for attributed in families:
            cells.append(str(table["confusion"].get(gold, {}).get(attributed, 0)))
        rows.append("| " + " | ".join(cells) + " |")
    errors = "\n".join(
        f"- `{row['case_id']}`: gold `{row['gold']}` attributed `{row['attributed']}` "
        f"({row['confidence']})"
        for row in table["residual_errors"]
    )
    lo = table["wilson95"]["low"]
    hi = table["wilson95"]["high"]
    return (
        f"# {table['table_id']}\n\n"
        f"**Status:** {table['status']} / {table['empirical_authority']}\n\n"
        f"Accuracy **{table['correct']}/{table['n_cases']}** = {table['accuracy']:.3f} "
        f"(macro precision {table['macro_precision']:.6f}; macro recall "
        f"{table['macro_recall']:.6f}; standard macro-F1 {table['macro_f1']:.6f}; "
        f"nominal Wilson score interval {lo:.3f}–{hi:.3f}). This interval treats "
        "the 24 fixed cases as Bernoulli units and is not a population confidence "
        "interval. Three residual errors are retained.\n\n"
        f"{header}\n{sep}\n" + "\n".join(rows) + "\n\n"
        f"## Residual errors (not successes)\n\n{errors}\n\n"
        f"{table['scope']}\n"
    )


def render_residual_markdown(table: Mapping[str, Any]) -> str:
    rows = [
        f"| {row['case_id']} | {row['gold']} | {row['attributed']} | {row['confidence']} |"
        for row in table["errors"]
    ]
    return (
        f"# {table['table_id']}\n\n"
        f"{table['promotion_forbidden']}\n\n"
        "| case_id | gold | attributed | confidence |\n"
        "|---|---|---|---|\n" + "\n".join(rows) + "\n"
    )


def render_cannot_check_markdown(table: Mapping[str, Any]) -> str:
    return (
        f"# {table['table_id']}\n\n"
        f"**Status:** `CANNOT_CHECK`\n\n"
        f"{table['reason']}\n\n"
        "No numbers are published for this artifact.\n"
    )


def _tex_escape(text: str) -> str:
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("&", "\\&")
        .replace("%", "\\%")
    )


def render_p5_3_tex(table: Mapping[str, Any]) -> str:
    short = {
        "RETRIEVAL_MISS": "Retr",
        "ROUTING_PLANNING_MISS": "Rout",
        "IMPLEMENTATION_BUG": "Impl",
        "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE": "Env",
        "EVALUATOR_METRIC_BUG": "Eval",
        "REPRESENTATION_GAP": "Repr",
        "MEASUREMENT_SPECIFICATION_GAP": "Meas",
        "METHOD_BASIS_GAP": "Meth",
    }
    header = "gold / attr. & " + " & ".join(short[f] for f in FAMILY_ORDER) + " \\\\"
    body = []
    for gold in FAMILY_ORDER:
        cells = [_tex_escape(short[gold])]
        for attributed in FAMILY_ORDER:
            cells.append(str(table["confusion"].get(gold, {}).get(attributed, 0)))
        body.append(" & ".join(cells) + " \\\\")
    lo = table["wilson95"]["low"]
    hi = table["wilson95"]["high"]
    error_lines = " \n".join(
        f"{_tex_escape(row['case_id'])}: gold {_tex_escape(row['gold'])} $\\rightarrow$ "
        f"{_tex_escape(row['attributed'])} ({row['confidence']})"
        for row in table["residual_errors"]
    )
    return (
        "% Generated from archived glm-5.2 attribution JSONL. Do not edit by hand.\n"
        "\\begin{table}[t]\n"
        "  \\centering\n"
        "  \\caption{Hidden-cause attribution confusion matrix from the archived "
        "glm-5.2 diagnostic run over a fixed constructed suite. Accuracy is 21/24; "
        "the nominal Wilson score interval "
        f"[{lo:.3f}, {hi:.3f}] treats the 24 cases as Bernoulli units and is not a "
        "population confidence interval. Three residual errors are retained and are not "
        "relabeled as successes. This is not a protected fresh-transfer or H1 result.}\n"
        "  \\label{tab:P5-3}\n"
        "  \\small\n"
        "  \\begin{tabular}{lcccccccc}\n"
        "    \\toprule\n"
        f"    {header}\n"
        "    \\midrule\n"
        + "\n".join(f"    {row}" for row in body)
        + "\n"
        "    \\bottomrule\n"
        "  \\end{tabular}\n"
        "  \\par\\smallskip\n"
        "  \\textit{Residual errors:} "
        f"{error_lines}.\n"
        "\\end{table}\n"
    )


#: Readable names for the archive's cause classes.
#:
#: The class name is the value the archive records, and the JSON keeps it
#: verbatim. Printing it into the paper is a different question: a reader meets
#: ``ENVIRONMENT_DEPENDENCY_TOOL_FAILURE`` as a 35-character unbreakable word,
#: which is both an internal identifier in a results table and --- because it
#: cannot be hyphenated --- 27.7pt of overfull box. Naming the cause in words
#: fixes the same defect twice.
#:
#: Unknown classes are refused rather than passed through. A cause the archive
#: grows that nobody has named would otherwise reappear as a raw token in a
#: published table, which is the state this replaces.
CAUSE_LABELS = {
    "RETRIEVAL_MISS": "retrieval miss",
    "REPRESENTATION_GAP": "representation gap",
    "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE": "environment dependency or tool failure",
    "IMPLEMENTATION_BUG": "implementation bug",
    "METHOD_BASIS_GAP": "method basis gap",
}


class UnnamedCauseClass(KeyError):
    """Raised when the archive carries a cause class no label covers."""


def cause_label(cause: str) -> str:
    try:
        return CAUSE_LABELS[cause]
    except KeyError:
        raise UnnamedCauseClass(
            f"{cause!r} has no readable label; add one to CAUSE_LABELS rather than "
            "letting a raw class name reach the manuscript"
        ) from None


def render_residual_tex(table: Mapping[str, Any]) -> str:
    rows = []
    for row in table["errors"]:
        rows.append(
            f"    {_tex_escape(row['case_id'])} & {cause_label(row['gold'])} & "
            f"{cause_label(row['attributed'])} & {row['confidence'].lower()} \\\\"
        )
    return (
        "% Generated from archived glm-5.2 attribution JSONL. Do not edit by hand.\n"
        "\\begin{table}[t]\n"
        "  \\centering\n"
        "  \\caption{Retained residual attribution errors from the archived glm-5.2 "
        "diagnostic run. These three cases remain incorrect; they are not successes.}\n"
        "  \\label{tab:P5-residual-errors}\n"
        "  \\small\n"
        "  \\begin{tabular}{lp{0.30\\linewidth}p{0.26\\linewidth}l}\n"
        "    \\toprule\n"
        "    case & gold cause & attributed cause & confidence \\\\\n"
        "    \\midrule\n"
        + "\n".join(rows)
        + "\n"
        "    \\bottomrule\n"
        "  \\end{tabular}\n"
        "\\end{table}\n"
    )


#: What each awaiting-campaign table would show, and what the archive lacks.
#:
#: The generic stub these used to render printed a single ``Result`` column
#: containing the word ``CANNOT_CHECK``, which says *that* a measurement is
#: missing without saying *which* measurement, and its caption carried an
#: unbalanced brace that no TeX run would accept. Neither is a property of the
#: archive, so the shape each table would have --- its columns, and what a live
#: campaign would put in them --- is data here rather than prose a human keeps
#: in the committed file by hand. A reader then sees the measurement that is
#: absent, and the committed ``.tex`` is exactly what this path produces.
CANNOT_CHECK_PRESENTATION: dict[str, dict[str, Any]] = {
    "P5-T2_baseline_ablation_results": {
        "absent": (
            "the archived attribution run has no matched baseline/ablation",
            "arms, round identities, or campaign-level outcomes. Numbers are not imputed from",
            "the 21/24 diagnostic accuracy.",
        ),
        "caption": (
            "Baseline and ablation transfer/integrity results: no admissible rows in the "
            "archived glm-5.2 attribution run. The archive contains a single-model "
            "hidden-cause diagnostic over 24 cases and no baseline/ablation arm data. This "
            "table will be populated when a live campaign produces matched "
            "baseline-vs-ablation transfer and integrity measurements."
        ),
        "column_spec": "lccc",
        "headers": (
            "Condition",
            "Transfer score",
            "Integrity score",
            "$\\Delta$ vs.\\ baseline",
        ),
    },
    "P5-T3_harmful_null_interventions": {
        "absent": (
            "the archived attribution run has no campaign intervention",
            "annotations, outcome labels, or round identities. Numbers are not imputed from",
            "the 21/24 diagnostic accuracy.",
        ),
        "caption": (
            "Campaign harmful/null interventions: no admissible rows in the archived "
            "glm-5.2 attribution run. The archive contains a single-model hidden-cause "
            "diagnostic over 24 cases and no intervention-level outcome annotations. This "
            "table will be populated when a live campaign records which interventions were "
            "harmful, null, or beneficial relative to the incumbent."
        ),
        "column_spec": "lccc",
        "headers": (
            "Intervention",
            "Outcome",
            "Effect size",
            "Recovery",
        ),
    },
    "P5-2_replay_vs_fresh_scatter": {
        "absent": (
            "the archived attribution run has no motivating/replay/fresh",
            "score pairs, round identities, or matched-sample arms. Numbers are not imputed",
            "from the 21/24 diagnostic accuracy.",
        ),
        "caption": (
            "Replay-vs-fresh scatter: no admissible rows in the archived glm-5.2 "
            "attribution run. The archive contains a single-model hidden-cause diagnostic "
            "over 24 cases and no campaign-level replay/fresh score pairs. This table will "
            "be populated when a live protected-transfer campaign produces matched replay "
            "and fresh-task measurements."
        ),
        "column_spec": "lcc",
        "headers": (
            "Round",
            "Replay score",
            "Fresh score",
        ),
    },
    "P5-4_longitudinal_specialist_regression": {
        "absent": (
            "the archived attribution run has no round identities,",
            "longitudinal specialist-designation annotations, or matched baseline/ablation",
            "arms. Numbers are not imputed from the 21/24 diagnostic accuracy.",
        ),
        "caption": (
            "Longitudinal specialist regression: no admissible rows in the archived glm-5.2 "
            "attribution run. The archive contains a single-model hidden-cause diagnostic "
            "over 24 cases and no longitudinal specialist-designation data. This table will "
            "be populated when a live campaign produces round-by-round specialist scores "
            "with regression annotations."
        ),
        "column_spec": "lccc",
        "headers": (
            "Round",
            "Specialist",
            "Prior score",
            "Current score",
        ),
    },
    "P5-5_improvement_integrity_frontier": {
        "absent": (
            "the archived attribution run has no improvement/integrity",
            "frontier pairs, no matched-score arms, and no round identities. Numbers are not",
            "imputed from the 21/24 diagnostic accuracy.",
        ),
        "caption": (
            "Improvement-integrity frontier: no admissible rows in the archived glm-5.2 "
            "attribution run. The archive contains a single-model hidden-cause diagnostic "
            "over 24 cases and no frontier-pair data. This table will be populated when a "
            "live campaign produces matched improvement and integrity scores across rounds."
        ),
        "column_spec": "lcc",
        "headers": (
            "Round",
            "Improvement score",
            "Integrity score",
        ),
    },
    "P5-6_failure_recurrence": {
        "absent": (
            "the archived attribution run has no recurrence annotations,",
            "round identities, or matched-score arms. Numbers are not imputed from the 21/24",
            "diagnostic accuracy.",
        ),
        "caption": (
            "Failure recurrence: no admissible rows in the archived glm-5.2 attribution "
            "run. The archive contains a single-model hidden-cause diagnostic over 24 cases "
            "and no recurrence annotations. This table will be populated when a live "
            "campaign records which previously resolved failures recur across rounds."
        ),
        "column_spec": "lccc",
        "headers": (
            "Original failure",
            "Round resolved",
            "Round recurred",
            "Outcome",
        ),
    },
    "P5-7_cost_to_validated_improvement": {
        "absent": (
            "the archived attribution run has no protected-improvement",
            "cost annotations, round identities, or matched-score arms. Numbers are not imputed",
            "from the 21/24 diagnostic accuracy.",
        ),
        "caption": (
            "Cost to validated improvement: no admissible rows in the archived glm-5.2 "
            "attribution run. The archive contains a single-model hidden-cause diagnostic "
            "over 24 cases and no cost-to-improvement annotations. This table will be "
            "populated when a live campaign records the resource cost (e.g., API calls, "
            "rounds, wall time) required to reach validated improvement."
        ),
        "column_spec": "lccc",
        "headers": (
            "Improvement",
            "Validation",
            "Cost metric",
            "Value",
        ),
    },
}


def render_cannot_check_tex(table: Mapping[str, Any]) -> str:
    table_id = table["table_id"]
    label = table_id.split("_", 1)[0]
    presentation = CANNOT_CHECK_PRESENTATION[table_id]
    headers = presentation["headers"]
    absent = presentation["absent"]
    comment = "\n".join(
        f"% Status: CANNOT_CHECK \u2014 {line}" if index == 0 else f"% {line}"
        for index, line in enumerate(absent)
    )
    return (
        "% Generated from archived glm-5.2 attribution JSONL. Do not edit by hand.\n"
        f"{comment}\n"
        "\\begin{table}[t]\n"
        "  \\centering\n"
        f"  \\caption{{{presentation['caption']}}}\n"
        f"  \\label{{tab:{label}}}\n"
        "  \\small\n"
        f"  \\begin{{tabular}}{{{presentation['column_spec']}}}\n"
        "    \\toprule\n"
        f"    {' & '.join(headers)} \\\\\n"
        "    \\midrule\n"
        f"    \\multicolumn{{{len(headers)}}}{{c}}{{\\texttt{{CANNOT\\_CHECK}} --- "
        "no admissible data in archive} \\\\\n"
        "    \\bottomrule\n"
        "  \\end{tabular}\n"
        "  \\par\\smallskip\n"
        "  \\textit{Empirical authority:} DESCRIPTIVE\\_ONLY (diagnostic attribution). "
        "Not a protected fresh-transfer or H1 result.\n"
        "\\end{table}"
    )


def generate(
    archive: Path,
    report: Path,
    output: Path,
    tex_output: Path,
) -> dict[str, dict[str, Any]]:
    records, digest = load_records(archive)
    metrics = verify_frozen_archive(records)
    check_report_agrees(report)

    tables: dict[str, dict[str, Any]] = {
        "P5-3_cause_confusion": build_p5_3(metrics, digest),
        "P5-ATTRIBUTION_RESIDUAL_ERRORS": build_residual_error_table(metrics, digest),
        "P5-T2_baseline_ablation_results": cannot_check_artifact(
            "P5-T2_baseline_ablation_results",
            "Baseline and ablation transfer/integrity results",
        ),
        "P5-T3_harmful_null_interventions": cannot_check_artifact(
            "P5-T3_harmful_null_interventions",
            "Campaign harmful/null interventions",
        ),
    }
    for plot_id in CAMPAIGN_PLOTS:
        tables[plot_id] = cannot_check_artifact(plot_id, plot_id.replace("_", " "))

    output.mkdir(parents=True, exist_ok=True)
    tex_output.mkdir(parents=True, exist_ok=True)

    p53 = tables["P5-3_cause_confusion"]
    residual = tables["P5-ATTRIBUTION_RESIDUAL_ERRORS"]
    _write_json(output / "P5-3_cause_confusion.json", p53)
    _write_text(output / "P5-3_cause_confusion.md", render_p5_3_markdown(p53))
    _write_text(tex_output / "P5-3_cause_confusion.tex", render_p5_3_tex(p53))
    _write_json(output / "P5-ATTRIBUTION_RESIDUAL_ERRORS.json", residual)
    _write_text(output / "P5-ATTRIBUTION_RESIDUAL_ERRORS.md", render_residual_markdown(residual))
    _write_text(tex_output / "P5-ATTRIBUTION_RESIDUAL_ERRORS.tex", render_residual_tex(residual))

    for key in (
        "P5-T2_baseline_ablation_results",
        "P5-T3_harmful_null_interventions",
        *CAMPAIGN_PLOTS,
    ):
        table = tables[key]
        _write_json(output / f"{key}.json", table)
        _write_text(output / f"{key}.md", render_cannot_check_markdown(table))
        _write_text(tex_output / f"{key}.tex", render_cannot_check_tex(table))

    index = {
        "paper_id": "P5",
        "issue": 102,
        "archive": str(archive),
        "archive_sha256": digest,
        "headline": "21/24 diagnostic attribution; three residual errors preserved",
        "empirical_authority_h1": STATUS_CANNOT_CHECK,
        "populated": ["P5-3_cause_confusion", "P5-ATTRIBUTION_RESIDUAL_ERRORS"],
        "cannot_check": [
            "P5-T2_baseline_ablation_results",
            "P5-T3_harmful_null_interventions",
            *CAMPAIGN_PLOTS,
        ],
        "live_campaign": STATUS_CANNOT_CHECK,
        "stale_24_of_24_rejected": True,
    }
    _write_json(output / "INDEX.json", index)
    return tables


def scan_forbidden_success_prose(root: Path) -> list[str]:
    """Refuse stale 24/24 success claims in P5 journal-facing files."""

    forbidden = ("24/24", "24 of 24", "all 24 cases correct", "perfect attribution")
    hits: list[str] = []
    targets = [
        root / "papers" / "paper-05-self-orion" / "evidence" / "CLAIM_LEDGER_V1.md",
        root / "papers" / "paper-05-self-orion" / "evidence" / "CLAIM_LEDGER_V1.json",
        root / "papers" / "paper-05-self-orion" / "JOURNAL_READINESS.md",
        root / "papers" / "paper-05-self-orion" / "manuscript" / "main.tex",
        *sorted((root / "papers" / "paper-05-self-orion" / "manuscript" / "sections").glob("*.tex")),
        *sorted((root / "papers" / "paper-05-self-orion" / "evidence" / "tables").glob("*.md")),
    ]
    for path in targets:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for needle in forbidden:
            if needle in text:
                hits.append(f"{path}:{needle}")
    return hits


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m orion.study.p5.tables",
        description=(
            "Regenerate ORION-P5 publication tables from the archived glm-5.2 "
            "attribution JSONL. Populates P5-3 and the residual-error ledger; "
            "emits CANNOT_CHECK stubs for campaign plots/tables."
        ),
    )
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    args = parser.parse_args(argv)

    try:
        tables = generate(args.archive, args.report, args.out, args.tex_out)
    except FileNotFoundError as error:
        print(f"P5 tables: CANNOT_CHECK — {error}", file=sys.stderr)
        return EXIT_CANNOT_CHECK
    except ValueError as error:
        print(f"P5 tables: archive refused: {error}", file=sys.stderr)
        return EXIT_ERROR

    populated = [key for key, table in tables.items() if table["status"] == STATUS_OK]
    blocked = [key for key, table in tables.items() if table["status"] == STATUS_CANNOT_CHECK]
    print("P5 tables: 21/24 verified from raw records; residual errors preserved")
    print(f"P5 tables: populated {populated}")
    print(f"P5 tables: CANNOT_CHECK {blocked}")
    print(f"P5 tables: written to {args.out} and {args.tex_out}")
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
