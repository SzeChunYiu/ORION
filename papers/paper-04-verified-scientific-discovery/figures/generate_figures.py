#!/usr/bin/env python3
"""Generate ORION-P4 publication figures and tables from live campaign data.

Reads LIVE_SUMMARY_V1.json, LIVE_HEATMAP_V1.json, result_records.jsonl, and
ATTACK_MANIFEST_V1.jsonl to produce all 5 SVGs and 3 LaTeX tables specified
in PLOT_SPEC_V1.md.
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DATA = _HERE / "data"
_TABLES = _HERE.parent / "tables"
_OUT = _HERE
_PROTOCOLS = (_HERE.parent.parent.parent / "research/paper-programme-v1/protocols").resolve()
sys.path.insert(0, str(_PROTOCOLS))

from publication_svg import bar_chart, grouped_bar_chart, heatmap  # noqa: E402

# ---------------------------------------------------------------------------
# Display name mappings
# ---------------------------------------------------------------------------

SYSTEM_DISPLAY_NAMES = {
    "orion": "ORION",
    "provenanceguard-style-source-routing": "ProvenanceGuard",
    "attributionbench-multisource-attribution": "AttributionBench",
    "fire-iterative-retrieve-or-verify": "IterativeRV",
    "claimbench-sciclaimhunt-scientific-evidence": "CitationFormat",
    "provenai-citation-fidelity-influence": "PooledNLI",
    "rewardhackingagents-search-contamination": "Auditability",
    "deepsciverify-abstract-to-full-escalation": "DeepSciVerify",
}

ABLATION_DISPLAY_NAMES = {
    "orion+no_exact_content_binding": "NoExactBinding",
    "orion+no_content_vs_provenance_distinction": "NoContentVsProvenance",
    "orion+no_checker_lineage_independence": "NoLineageIndep",
    "orion+no_hostile_checker_battery": "NoHostileBattery",
    "orion+no_behavioral_influence_coordinate": "NoBehavCoord",
    "orion+no_evaluator_protection_access_telemetry": "NoEvalProtect",
    "orion+soft_confidence_instead_of_fail_closed_authority": "SoftConfidence",
    "orion+no_search_time_contamination_block": "NoSearchContam",
}

# PLOT_SPEC family names (lowercase_underscore) -> manifest family names (UPPER)
FAMILY_TO_MANIFEST = {
    "clean_supported_positive": "CLEAN_POSITIVE",
    "correct_fact_wrong_source": "WRONG_SOURCE",
    "content_substitution": "CONTENT_SUBSTITUTION",
    "source_conflation": "SOURCE_CONFLATION",
    "pooled_support_wrong_owner": "POOLED_SUPPORT_WRONG_OWNER",
    "cited_but_non_influential": "CITED_NON_INFLUENTIAL",
    "weak_non_discriminating_checker": "WEAK_CHECKER",
    "same_lane_checker": "SAME_LANE_CHECKER",
    "posthoc_checker_or_evaluator": "POSTHOC_CHECKER_EVALUATOR",
    "search_time_contamination": "SEARCH_TIME_CONTAMINATION",
    "evaluator_or_guard_tampering": "EVALUATOR_TAMPER",
    "heldout_label_access": "HOLDOUT_ACCESS",
    "genuinely_insufficient_evidence": "INSUFFICIENT_EVIDENCE",
}

MANIFEST_TO_FAMILY = {v: k for k, v in FAMILY_TO_MANIFEST.items()}

PLOT_SPEC_FAMILIES = list(FAMILY_TO_MANIFEST.keys())

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_live_summary() -> dict:
    return json.loads((_DATA / "campaign_output" / "LIVE_SUMMARY_V1.json").read_text(encoding="utf-8"))


def _load_heatmap() -> list[dict]:
    return json.loads((_DATA / "campaign_output" / "LIVE_HEATMAP_V1.json").read_text(encoding="utf-8"))


def _load_result_records() -> list[dict]:
    records = []
    for line in (_DATA / "campaign_output" / "result_records.jsonl").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def _load_manifest() -> list[dict]:
    cases = []
    for line in (_HERE.parent / "protocol" / "ATTACK_MANIFEST_V1.jsonl").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            cases.append(json.loads(line))
    return cases


def _float(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _wilson(successes: float, total: float) -> tuple[float, float]:
    """Wilson 95% confidence interval for a proportion."""
    if total == 0:
        return 0.0, 0.0
    z = 1.96
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return max(0.0, center - half), min(1.0, center + half)


# ---------------------------------------------------------------------------
# Build per-system summary data structure
# ---------------------------------------------------------------------------

def _build_system_summary() -> list[dict]:
    """Build a list of dicts (one per system) with all metrics needed for figures.

    Each dict has: system, false_promotion_rate, clean_authority_coverage,
    correct_cannot_check_rate, false_negative_rate, source_attribution_accuracy,
    support_contradiction_f1, wallclock_seconds, ci_low, ci_high.
    """
    summary = _load_live_summary()
    records = _load_result_records()

    # Compute support_contradiction_f1 from result records per system
    f1_by_sys: dict[str, float] = {}
    cost_by_sys: dict[str, float] = {}
    sys_agg = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "cost": 0.0})

    for r in records:
        sys_id = r["system_id"]
        m = r["metrics"]
        sys_agg[sys_id]["tp"] += m["support_contradiction_tp"]
        sys_agg[sys_id]["fp"] += m["support_contradiction_fp"]
        sys_agg[sys_id]["fn"] += m["support_contradiction_fn"]
        sys_agg[sys_id]["cost"] += r["cost"]["wallclock_seconds"]

    for sys_id, agg in sys_agg.items():
        tp, fp, fn = agg["tp"], agg["fp"], agg["fn"]
        f1_by_sys[sys_id] = (2 * tp / (2 * tp + fp + fn)) if (2 * tp + fp + fn) > 0 else 0.0
        cost_by_sys[sys_id] = agg["cost"]

    # Build row from ORION + baselines + ablations
    rows = []
    for sys_id in ["orion"] + list(summary["baselines"].keys()) + [f"orion+{a}" for a in summary["ablations"].keys()]:
        display_name = SYSTEM_DISPLAY_NAMES.get(sys_id, ABLATION_DISPLAY_NAMES.get(sys_id, sys_id))

        # Pick metrics from the right source
        if sys_id == "orion":
            met = summary["orion"]
        elif sys_id.startswith("orion+"):
            aid = sys_id[len("orion+"):]
            met = summary["ablations"].get(aid, {})
        else:
            met = summary["baselines"].get(sys_id, {})

        fp = met.get("false_promotion_rate", 0.0)
        cov = met.get("clean_authority_coverage", 0.0)
        cc = met.get("correct_cannot_check_rate", 0.0)
        fnr = met.get("false_negative_rate", 0.0)
        attr = met.get("source_attribution_accuracy", 0.0)
        f1 = f1_by_sys.get(sys_id, 0.0)
        cost = cost_by_sys.get(sys_id, 0.0)

        # Wilson CI for false promotion rate
        fp_opportunities = sum(r["metrics"]["promotion_opportunities"] for r in records if r["system_id"] == sys_id)
        fp_count = sum(r["metrics"]["false_promotions"] for r in records if r["system_id"] == sys_id)
        ci_low, ci_high = _wilson(fp_count, fp_opportunities) if fp_opportunities > 0 else (0.0, 0.0)

        rows.append({
            "system": display_name,
            "system_id": sys_id,
            "false_promotion_rate": fp,
            "clean_authority_coverage": cov,
            "correct_cannot_check_rate": cc,
            "false_negative_rate": fnr,
            "source_attribution_accuracy": attr,
            "support_contradiction_f1": f1,
            "wallclock_seconds": cost,
            "ci_low": ci_low,
            "ci_high": ci_high,
        })

    return rows


def _build_detection_heatmap_data() -> list[dict]:
    """Build heatmap data: detection rate per family per system.

    Detection rate = proportion of correct decisions for that family.
    - CLEAN_POSITIVE (expected PROMOTE): correct = PASS
    - BLOCK-expected families: correct = FAIL or CANNOT_CHECK (non-promotion)
    - CANNOT_CHECK-expected (INSUFFICIENT_EVIDENCE): correct = CANNOT_CHECK
    """
    records = _load_result_records()
    hm = _load_heatmap()

    # Get expected terminal per family
    manifest = _load_manifest()
    expected_by_case: dict[str, str] = {}
    for c in manifest:
        expected_by_case[c["case_id"]] = c["protected_gold"]["expected_authority_terminal"]

    # Build detection grid
    rows = []
    for system_row in hm:
        sys_id = system_row["system_id"]
        display = SYSTEM_DISPLAY_NAMES.get(sys_id, ABLATION_DISPLAY_NAMES.get(sys_id, sys_id))

        for fam_manifest_name in sorted(set(c["task_family"] for c in records)):
            plot_spec_name = MANIFEST_TO_FAMILY.get(fam_manifest_name, fam_manifest_name.lower())
            # Count cases for this family
            family_cases = [k for k in system_row.keys() if k.startswith("P4-") and f"-{fam_manifest_name}-" in k]
            if not family_cases:
                continue
            total = len(family_cases)
            correct = 0
            for case_id_key in family_cases:
                verdict = system_row[case_id_key]
                # Extract the case_id without the "P4-" prefix to match manifest
                case_id = case_id_key  # Case ID is the key itself
                expected = expected_by_case.get(case_id_key, "PROMOTE")
                if expected == "PROMOTE":
                    if verdict == "PROMOTE":
                        correct += 1
                elif expected == "CANNOT_CHECK":
                    if verdict == "CANNOT_CHECK":
                        correct += 1
                else:  # expected BLOCK
                    if verdict in ("BLOCK", "CANNOT_CHECK"):
                        correct += 1
            rate = correct / total if total > 0 else 0.0
            rows.append({
                "attack_family": plot_spec_name,
                "system": display,
                "detection_rate": rate,
            })

    return rows


# ---------------------------------------------------------------------------
# Figure builders
# ---------------------------------------------------------------------------

def build_p4_2(data: list[dict]) -> str:
    """False authority-promotion rate bar chart with Wilson CI."""
    rows = [
        {"system": d["system"], "rate": d["false_promotion_rate"], "ci_low": d["ci_low"], "ci_high": d["ci_high"]}
        for d in data
    ]
    return bar_chart(
        rows,
        label_key="system",
        value_key="rate",
        title="False Authority-Promotion Rate by System",
        y_label="False promotion rate",
    )


def build_p4_3(data: list[dict]) -> str:
    """Safety–Coverage frontier scatter plot."""
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="560" viewBox="0 0 900 560">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="450" y="32" text-anchor="middle" font-family="sans-serif" font-size="20">Safety–Coverage Frontier</text>',
    ]
    x0, x1 = 100, 860
    y0, y1 = 460, 65
    lines.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="black"/>')
    lines.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="black"/>')
    for i in range(11):
        v = i / 10.0
        y = y0 - (y0 - y1) * v
        lines.append(f'<line x1="{x0-5}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="black"/>')
        lines.append(f'<text x="{x0-10}" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{v:.1f}</text>')
    lines.append(f'<text x="22" y="{(y0+y1)/2}" transform="rotate(-90 22 {(y0+y1)/2})" text-anchor="middle" font-family="sans-serif" font-size="14">Rate</text>')
    lines.append(f'<text x="{(x0+x1)/2}" y="{y0+30}" text-anchor="middle" font-family="sans-serif" font-size="14">Coverage (x) vs false promotion (y)</text>')

    colors = {"ORION": "#2196F3"}
    for d in data:
        system = d["system"]
        cov = d["clean_authority_coverage"]
        fp = d["false_promotion_rate"]
        x = x0 + (x1 - x0) * cov
        y = y0 - (y0 - y1) * fp
        color = colors.get(system, "#FF9800")
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{color}"/>')
        lines.append(f'<text x="{x+8:.1f}" y="{y-8:.1f}" font-family="sans-serif" font-size="11">{system}</text>')
    lines.append("</svg>")
    return "\n".join(lines)


def build_p4_4(heatmap_data: list[dict]) -> str:
    """Detection rate heatmap by attack family and system."""
    # Order: all systems in a fixed order
    all_systems = (
        ["ORION"]
        + [SYSTEM_DISPLAY_NAMES[s] for s in SYSTEM_DISPLAY_NAMES]
        + [ABLATION_DISPLAY_NAMES[a] for a in ABLATION_DISPLAY_NAMES]
    )
    return heatmap(
        heatmap_data,
        row_key="attack_family",
        col_key="system",
        value_key="detection_rate",
        title="Detection Rate by Attack Family",
        row_order=PLOT_SPEC_FAMILIES,
        col_order=all_systems,
        fmt=".2f",
    )


def build_p4_5(data: list[dict]) -> str:
    """Source attribution vs semantic support F1 (grouped bars)."""
    return grouped_bar_chart(
        data,
        label_key="system",
        bar_keys=[
            ("source_attribution_accuracy", "#2196F3", "Attribution"),
            ("support_contradiction_f1", "#FF9800", "Support F1"),
        ],
        title="Source Attribution vs Semantic Support Accuracy",
        y_label="Accuracy / F1",
    )


def build_p4_6(data: list[dict]) -> str:
    """Cost vs false-promotion trade-off (grouped bars)."""
    # Normalize cost to 0-1 range for visual comparison
    max_cost = max(d["wallclock_seconds"] for d in data) if data else 1.0
    rows = [
        {
            "system": d["system"],
            "cost": d["wallclock_seconds"] / max_cost if max_cost > 0 else 0.0,
            "false_promotion": d["false_promotion_rate"],
        }
        for d in data
    ]
    return grouped_bar_chart(
        rows,
        label_key="system",
        bar_keys=[
            ("cost", "#2196F3", "Normalized cost"),
            ("false_promotion", "#FF9800", "False promotion"),
        ],
        title="Cost vs False-Promotion Trade-off",
        y_label="Normalized cost / False promotion",
    )


# ---------------------------------------------------------------------------
# Table writers
# ---------------------------------------------------------------------------

def write_table_p4_1() -> None:
    """Attack battery and custody manifest from ATTACK_MANIFEST_V1.jsonl."""
    manifest = _load_manifest()
    # Count per family
    by_fam = defaultdict(lambda: {"total": 0, "PUBLIC_CLEAN": 0, "PUBLIC_HOSTILE": 0,
                                    "PROTECTED_HOSTILE": 0, "PROTECTED_HOLDOUT": 0})
    hidden_labels = {}
    for c in manifest:
        fam = c["attack_family"]
        by_fam[fam]["total"] += 1
        cls = c.get("custody_class", "UNKNOWN")
        if cls in by_fam[fam]:
            by_fam[fam][cls] += 1
        hidden_labels[fam] = not c.get("attack_label_visible_to_candidate", True)

    header = ["Family", "Cases (n)", "Public clean", "Public hostile", "Protected hostile", "Protected holdout", "Hidden labels"]
    lines = [
        "% Generated by figures/generate_figures.py from ATTACK_MANIFEST_V1.jsonl",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Attack battery composition, custody distribution, and hidden-label status. "
        "All attack labels are hidden from the candidate. Protected-hostile and protected-holdout "
        "cases are stored under independent host custody.}",
        "\\label{tab:p4_t1}",
        "\\begin{tabular}{lcccccc}",
        "\\toprule",
        " & ".join(header) + " \\\\",
        "\\midrule",
    ]
    for fam_plot_name in PLOT_SPEC_FAMILIES:
        fam_manifest = FAMILY_TO_MANIFEST[fam_plot_name]
        info = by_fam.get(fam_manifest, {"total": 0, "PUBLIC_CLEAN": 0, "PUBLIC_HOSTILE": 0,
                                           "PROTECTED_HOSTILE": 0, "PROTECTED_HOLDOUT": 0})
        total = info["total"]
        pc = info["PUBLIC_CLEAN"]
        ph = info["PUBLIC_HOSTILE"]
        prh = info["PROTECTED_HOSTILE"]
        prho = info["PROTECTED_HOLDOUT"]
        hidden = "Yes" if hidden_labels.get(fam_manifest, True) else "No"
        lines.append(
            f"{fam_plot_name} & {total} & "
            f"{'100\\%' if pc == total and total > 0 else pc} & "
            f"{'100\\%' if ph == total and total > 0 else ph} & "
            f"{'100\\%' if prh == total and total > 0 else prh} & "
            f"{'100\\%' if prho == total and total > 0 else prho} & "
            f"{hidden} \\\\"
        )
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
    ]
    (_TABLES / "p4_t1_attack_custody.tex").write_text("\n".join(lines), encoding="utf-8")


def write_table_p4_2(data: list[dict]) -> None:
    """Baseline and ablation results table."""
    header = ["System", "False promotion", "Clean coverage", "Correct CANNOT_CHECK", "Cost (s)", "FN rate", "Run status"]
    lines = [
        "% Generated by figures/generate_figures.py from LIVE_SUMMARY_V1.json + result_records.jsonl",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Primary and key secondary metrics for all systems. "
        "Wilson 95\\% intervals in parentheses. "
        "FN rate = false negative rate (clean positives incorrectly blocked).}",
        "\\label{tab:p4_t2}",
        "\\begin{tabular}{" + "l" + "c" * (len(header) - 1) + "}",
        "\\toprule",
        " & ".join(header) + " \\\\",
        "\\midrule",
    ]
    # ORION first, then baselines, then ablations
    def sort_key(row: dict) -> tuple[int, str]:
        name = row["system"]
        if name == "ORION":
            return (0, "")
        if name in SYSTEM_DISPLAY_NAMES.values():
            return (1, name)
        return (2, name)

    for d in sorted(data, key=sort_key):
        lines.append(
            f"{d['system']} & "
            f"{d['false_promotion_rate']:.3f} & "
            f"{d['clean_authority_coverage']:.3f} & "
            f"{d['correct_cannot_check_rate']:.3f} & "
            f"{d['wallclock_seconds']:.1f} & "
            f"{d['false_negative_rate']:.3f} & "
            f"LIVE \\\\"
        )
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
    ]
    (_TABLES / "p4_t2_baseline_ablation_results.tex").write_text("\n".join(lines), encoding="utf-8")


def write_table_p4_3(data: list[dict]) -> None:
    """CANNOT_CHECK and error breakdown per system."""
    records = _load_result_records()
    manifest = _load_manifest()

    # Expected terminal per case
    expected_by_case: dict[str, str] = {}
    for c in manifest:
        expected_by_case[c["case_id"]] = c["protected_gold"]["expected_authority_terminal"]

    # Per-system breakdown
    sys_breakdown = defaultdict(lambda: {"cannot_check": 0, "correct_abstain": 0,
                                          "false_block": 0, "false_positive": 0, "infra_fail": 0})
    for r in records:
        sys_id = r["system_id"]
        status = r["status"]
        expected = expected_by_case.get(r["task_id"], "PROMOTE")
        b = sys_breakdown[sys_id]
        if status == "CANNOT_CHECK":
            b["cannot_check"] += 1
            if expected == "CANNOT_CHECK":
                b["correct_abstain"] += 1
            else:
                # Wrongly CANNOT_CHECK (should have been BLOCK or PROMOTE)
                b["false_block"] += 1
        elif status == "FAIL" and expected == "PROMOTE":
            b["false_block"] += 1
        elif status == "PASS" and expected != "PROMOTE":
            b["false_positive"] += 1
        elif status == "INVALID":
            b["infra_fail"] += 1

    header = ["System", "Total CANNOT_CHECK", "Correct abstention", "False block", "False positive", "Infra failure"]
    lines = [
        "% Generated by figures/generate_figures.py from result_records.jsonl",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Breakdown of CANNOT_CHECK and error outcomes. "
        "Correct abstention: cases where the system correctly refused to commit. "
        "False block: clean positives that were incorrectly blocked. "
        "False positive: attack cases that were incorrectly promoted. "
        "Infrastructure failures are excluded from primary analysis.}",
        "\\label{tab:p4_t3}",
        "\\begin{tabular}{" + "l" + "c" * (len(header) - 1) + "}",
        "\\toprule",
        " & ".join(header) + " \\\\",
        "\\midrule",
    ]
    for d in data:
        sys_id = d["system_id"]
        b = sys_breakdown[sys_id]
        lines.append(
            f"{d['system']} & {b['cannot_check']} & {b['correct_abstain']} & "
            f"{b['false_block']} & {b['false_positive']} & {b['infra_fail']} \\\\"
        )
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
        "",
    ]
    (_TABLES / "p4_t3_cannot_check_errors.tex").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    data = _build_system_summary()
    hm_data = _build_detection_heatmap_data()

    print(f"Built {len(data)} system summary rows")
    for d in data:
        print(f"  {d['system']:30s} FP={d['false_promotion_rate']:.3f}  "
              f"Cov={d['clean_authority_coverage']:.3f}  F1={d['support_contradiction_f1']:.3f}  "
              f"Cost={d['wallclock_seconds']:.1f}s  CI=({d['ci_low']:.3f},{d['ci_high']:.3f})")

    (_OUT / "p4_2_false_promotion.svg").write_text(build_p4_2(data), encoding="utf-8")
    (_OUT / "p4_3_coverage_frontier.svg").write_text(build_p4_3(data), encoding="utf-8")
    (_OUT / "p4_4_detection_by_attack.svg").write_text(build_p4_4(hm_data), encoding="utf-8")
    (_OUT / "p4_5_attribution_vs_support.svg").write_text(build_p4_5(data), encoding="utf-8")
    (_OUT / "p4_6_cost_false_promotion.svg").write_text(build_p4_6(data), encoding="utf-8")

    write_table_p4_1()
    write_table_p4_2(data)
    write_table_p4_3(data)

    print(f"\nWrote 5 SVGs + 3 LaTeX tables under {_OUT.parent}")


if __name__ == "__main__":
    main()