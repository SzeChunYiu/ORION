#!/usr/bin/env python3
"""Generate Paper-IV result figures/tables from immutable public V2 aggregates.

This script intentionally reads only evidence/protected_v2/*.json.  It never
reads the exploratory 39-case live arm or protected per-case labels.
"""
from __future__ import annotations

import html
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
EVIDENCE = PAPER / "evidence" / "protected_v2"
TABLES = PAPER / "tables"
METRICS = json.loads((EVIDENCE / "PUBLICATION_METRICS_V2.json").read_text())
FAMILY = json.loads((EVIDENCE / "FAMILY_CONTRAST_V2.json").read_text())

PRIMARY = [
    "ORION",
    "provenanceguard-style-source-routing",
    "attributionbench-multisource-attribution",
    "fire-iterative-retrieve-or-verify",
    "claimbench-sciclaimhunt-scientific-evidence",
    "provenai-citation-fidelity-influence",
    "rewardhackingagents-search-contamination",
    "deepsciverify-abstract-to-full-escalation",
]
ALL = PRIMARY + [
    "citation-presence-format",
    "pooled-evidence-nli-support",
    "claim-level-auditability-provenance",
]
SHORT = {
    "ORION": "Governed",
    "provenanceguard-style-source-routing": "ProvGuard",
    "attributionbench-multisource-attribution": "AttribBench",
    "fire-iterative-retrieve-or-verify": "FIRE",
    "claimbench-sciclaimhunt-scientific-evidence": "CLAIM-B",
    "provenai-citation-fidelity-influence": "ProvenAI",
    "rewardhackingagents-search-contamination": "RHAgents",
    "deepsciverify-abstract-to-full-escalation": "DeepSci",
    "citation-presence-format": "Citation",
    "pooled-evidence-nli-support": "PooledNLI",
    "claim-level-auditability-provenance": "AuditProv",
}
HOSTILE = [
    "WRONG_SOURCE", "CONTENT_SUBSTITUTION", "SOURCE_CONFLATION",
    "POOLED_SUPPORT_WRONG_OWNER", "CITED_NON_INFLUENTIAL", "WEAK_CHECKER",
    "SAME_LANE_CHECKER", "POSTHOC_CHECKER_EVALUATOR",
    "SEARCH_TIME_CONTAMINATION", "EVALUATOR_TAMPER", "HOLDOUT_ACCESS",
    "INSUFFICIENT_EVIDENCE",
]
ABL = {
    "ablation-no-exact-content-binding": "Without exact content",
    "ablation-no-content-provenance-distinction": "Without source/provenance",
    "ablation-no-checker-lineage-independence": "Without checker lineage",
    "ablation-no-hostile-checker-battery": "Without hostile checker",
    "ablation-no-behavioral-influence": "Without influence",
    "ablation-no-evaluator-protection-telemetry": "Without evaluator protection",
    "ablation-soft-confidence": "Soft-confidence rule",
    "ablation-no-search-contamination-block": "Without search block",
}
W, H = 960, 600


def esc(x: object) -> str:
    return html.escape(str(x), quote=True)


def start(title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="480" y="32" text-anchor="middle" font-family="sans-serif" font-size="20" font-weight="bold">{esc(title)}</text>',
    ]


def axes(lines: list[str], y_min: float, y_max: float, label: str) -> tuple[int,int,int,int]:
    x0, x1, y0, y1 = 110, 920, 500, 70
    lines += [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="black"/>',
              f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="black"/>']
    for i in range(6):
        v = y_min + (y_max-y_min)*i/5
        y = y0-(y0-y1)*(v-y_min)/(y_max-y_min)
        lines += [f'<line x1="{x0-5}" y1="{y:.1f}" x2="{x0}" y2="{y:.1f}" stroke="black"/>',
                  f'<text x="{x0-10}" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="11">{v:.2f}</text>']
    lines.append(f'<text x="28" y="285" transform="rotate(-90 28 285)" text-anchor="middle" font-family="sans-serif" font-size="13">{esc(label)}</text>')
    return x0,x1,y0,y1


def p4_2() -> str:
    lines=start("False authority-promotion rate — safety battery")
    x0,x1,y0,y1=axes(lines,0,1,"False promotion rate")
    slot=(x1-x0)/len(ALL); bw=slot*.62
    for i,sid in enumerate(ALL):
        row=METRICS["systems"][sid]; v=row["false_promotion_rate"]; lo,hi=row["false_promotion_ci95"]
        cx=x0+slot*(i+.5); y=y0-(y0-y1)*v
        fill="#2f5597" if sid=="ORION" else "#777"
        lines.append(f'<rect x="{cx-bw/2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{y0-y:.1f}" fill="{fill}"/>')
        ylo=y0-(y0-y1)*lo; yhi=y0-(y0-y1)*hi
        lines += [f'<line x1="{cx:.1f}" y1="{ylo:.1f}" x2="{cx:.1f}" y2="{yhi:.1f}" stroke="black"/>',
                  f'<text x="{cx:.1f}" y="518" transform="rotate(38 {cx:.1f} 518)" text-anchor="start" font-family="sans-serif" font-size="10">{SHORT[sid]}</text>']
    lines += ['<text x="480" y="585" text-anchor="middle" font-family="sans-serif" font-size="10">Whiskers: Wilson 95% CI. Comparator names denote protocol-matched mechanism reimplementations.</text>', '</svg>']
    return "\n".join(lines)


def p4_3() -> str:
    lines=start("Safety–coverage result")
    x0,x1,y0,y1=120,920,500,80
    lines += [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="black"/>', f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="black"/>']
    for i in range(6):
        v=i/5; x=x0+(x1-x0)*v
        lines += [f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0+5}" stroke="black"/>', f'<text x="{x:.1f}" y="522" text-anchor="middle" font-family="sans-serif" font-size="11">{v:.1f}</text>']
    lines += ['<text x="520" y="552" text-anchor="middle" font-family="sans-serif" font-size="13">False authority-promotion rate</text>', '<text x="28" y="285" transform="rotate(-90 28 285)" text-anchor="middle" font-family="sans-serif" font-size="13">Clean authority coverage</text>']
    offsets=[12,30,48,66,84,102,120,138]
    for sid,dy in zip(PRIMARY,offsets):
        v=METRICS["systems"][sid]["false_promotion_rate"]; x=x0+(x1-x0)*v; y=100
        fill="#2f5597" if sid=="ORION" else "#777"
        lines += [f'<circle cx="{x:.1f}" cy="{y}" r="6" fill="{fill}"/>', f'<text x="{max(5,x+8):.1f}" y="{y+dy}" font-family="sans-serif" font-size="10">{SHORT[sid]}</text>']
    lines += ['<text x="480" y="585" text-anchor="middle" font-family="sans-serif" font-size="10">All primary mechanisms promoted 60/60 clean positives; paired coverage difference is zero.</text>', '</svg>']
    return "\n".join(lines)


def p4_4() -> str:
    lines=start("False promotion by hostile family")
    x0,y0,cw,ch=360,75,220,38
    cols=["ORION","provenai-citation-fidelity-influence"]
    for c,sid in enumerate(cols):
        lines.append(f'<text x="{x0+(c+.5)*cw}" y="60" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold">{SHORT[sid]}</text>')
    for r,name in enumerate(HOSTILE):
        y=y0+r*ch; lines.append(f'<text x="{x0-12}" y="{y+24}" text-anchor="end" font-family="sans-serif" font-size="10">{esc(name.replace("_"," ").title())}</text>')
        for c,sid in enumerate(cols):
            v=FAMILY["families"][name][sid]["false_promotion_rate"]; x=x0+c*cw
            fill="#d9e2f3" if v==0 and sid=="ORION" else ("#555" if v==1 else "#ddd")
            lines += [f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" fill="{fill}" stroke="white"/>', f'<text x="{x+cw/2}" y="{y+24}" text-anchor="middle" font-family="sans-serif" font-size="11">{v:.0%}</text>']
    lines += ['<text x="480" y="585" text-anchor="middle" font-family="sans-serif" font-size="10">ProvenAI-style false-promotes all 30 cases in six governance/checker families; governed pipeline false-promotes none.</text>', '</svg>']
    return "\n".join(lines)


def grouped(metric_a: str, metric_b: str, title: str) -> str:
    lines=start(title); x0,x1,y0,y1=axes(lines,.7,1,"Accuracy / F1")
    slot=(x1-x0)/len(PRIMARY); bw=slot*.28
    for i,sid in enumerate(PRIMARY):
        row=METRICS["systems"][sid]; cx=x0+slot*(i+.5)
        for j,(key,fill) in enumerate(((metric_a,"#444"),(metric_b,"#aaa"))):
            v=row[key]; y=y0-(y0-y1)*(v-.7)/.3; x=cx+(-.6 if j==0 else .6)*bw-bw/2
            lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{y0-y:.1f}" fill="{fill}"/>')
        lines.append(f'<text x="{cx:.1f}" y="518" transform="rotate(35 {cx:.1f} 518)" text-anchor="start" font-family="sans-serif" font-size="10">{SHORT[sid]}</text>')
    lines += ['<rect x="720" y="75" width="12" height="12" fill="#444"/><text x="738" y="86" font-family="sans-serif" font-size="10">Source attribution</text>', '<rect x="720" y="94" width="12" height="12" fill="#aaa"/><text x="738" y="105" font-family="sans-serif" font-size="10">Support F1</text>', '</svg>']
    return "\n".join(lines)


def p4_6() -> str:
    lines=start("Deterministic latency vs false promotion")
    x0,x1,y0,y1=120,920,500,80
    vals=[METRICS["systems"][s]["mean_latency_seconds"]*1e6 for s in PRIMARY]; logs=[math.log10(v) for v in vals]; lo,hi=min(logs),max(logs)
    # Fixed direct-label layout.  Two comparator points are almost coincident;
    # name them together rather than jittering data or drawing leader arrows.
    label_layout = {
        "ORION": (-8, -8, "end"),
        "provenanceguard-style-source-routing": (-8, -12, "end"),
        "attributionbench-multisource-attribution": (8, -12, "start"),
        "fire-iterative-retrieve-or-verify": (8, -12, "start"),
        "claimbench-sciclaimhunt-scientific-evidence": (8, -12, "start"),
        "provenai-citation-fidelity-influence": (8, 22, "start"),
    }
    lines += [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="black"/>', f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="black"/>']
    for sid,us,lg in zip(PRIMARY,vals,logs):
        fp=METRICS["systems"][sid]["false_promotion_rate"]; x=x0+(x1-x0)*(lg-lo)/(hi-lo); y=y0-(y0-y1)*fp; fill="#2f5597" if sid=="ORION" else "#777"
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{fill}"/>')
        if sid in label_layout:
            dx,dy,anchor=label_layout[sid]
            lines.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{anchor}" font-family="sans-serif" font-size="10">{SHORT[sid]}</text>')
    overlap_x=max(x0+(x1-x0)*(logs[PRIMARY.index(sid)]-lo)/(hi-lo) for sid in ("rewardhackingagents-search-contamination", "deepsciverify-abstract-to-full-escalation"))
    overlap_y=y0-(y0-y1)*METRICS["systems"]["rewardhackingagents-search-contamination"]["false_promotion_rate"]
    lines += [
        f'<text x="{overlap_x+9:.1f}" y="{overlap_y-20:.1f}" font-family="sans-serif" font-size="10">RHAgents /</text>',
        f'<text x="{overlap_x+9:.1f}" y="{overlap_y-8:.1f}" font-family="sans-serif" font-size="10">DeepSci (overlap)</text>',
    ]
    lines += ['<text x="520" y="552" text-anchor="middle" font-family="sans-serif" font-size="13">Mean latency (microseconds; log scale)</text>', '<text x="28" y="285" transform="rotate(-90 28 285)" text-anchor="middle" font-family="sans-serif" font-size="13">False promotion rate</text>', '<text x="480" y="585" text-anchor="middle" font-family="sans-serif" font-size="10">Mechanism-level deterministic timing; no model/network serving latency is included.</text>', '</svg>']
    return "\n".join(lines)


def tables() -> None:
    TABLES.mkdir(parents=True,exist_ok=True)
    (TABLES/"p4_t1_attack_custody.tex").write_text(r'''\begin{table}[t]
\centering\scriptsize
\caption{Protected safety battery and custody. Hidden labels remained evaluator-only until all mechanisms were scored.}\label{tab:p4_t1}
\begin{tabular}{lrrrr}\toprule
Slice & Cases & Clean & Hostile & Candidate labels \\\midrule
Post-run public slice & 150 & 30 & 120 & hidden during execution \\
Protected hostile & 120 & 0 & 120 & hidden \\
Protected holdout & 150 & 30 & 120 & hidden \\\midrule
Total & 420 & 60 & 360 & hidden \\\bottomrule
\end{tabular}\end{table}
''')
    rows=[]
    for sid in ALL:
        r=METRICS["systems"][sid]; display="Governed pipeline" if sid=="ORION" else r["display_name"]; rows.append(f"{display} & {r['false_promotion_rate']:.3f} & {r['clean_coverage']:.3f} & {r['clean_false_negative_count']} & {1000*r['mean_latency_seconds']:.4f} & {r['resource_units']:.1f} \\\\")
    for sid,label in ABL.items():
        r=METRICS["ablations"][sid]; rows.append(f"{label} & {r['false_promotion_rate']:.3f} & {r['clean_coverage']:.3f} & {r['clean_false_negative_count']} & {1000*r['mean_latency_seconds']:.4f} & 9.0 \\\\")
    (TABLES/"p4_t2_baseline_ablation_results.tex").write_text("\\begin{table}[t]\n\\centering\\scriptsize\n\\caption{Protected safety-battery results. Comparator names denote protocol-matched mechanism reimplementations, not original external software. FP is over 360 hostile opportunities; clean is over 60 clean positives.}\\label{tab:p4_t2}\n\\resizebox{\\textwidth}{!}{%\n\\begin{tabular}{lrrrrr}\\toprule\nSystem / variant & FP & Clean & Clean FN & Latency (ms) & Resource \\\\ \\midrule\n"+"\n".join(rows)+"\n\\bottomrule\\end{tabular}}\n\\end{table}\n")
    strongest=METRICS["strongest_frozen_comparator"]
    lines=["Governed pipeline & 30/30 & 0/360 & 0/60 \\\\", f"ProvenAI-style & 30/30 & {METRICS['reproduction']['comparator_false_promotions']}/360 & 0/60 \\\\"]
    (TABLES/"p4_t3_cannot_check_errors.tex").write_text("\\begin{table}[t]\n\\centering\\small\n\\caption{Fail-closed outcomes and false-negative cost in the protected safety battery. The only gold family whose correct outcome is `undetermined' contains 30 insufficient-evidence cases.}\\label{tab:p4_t3}\n\\begin{tabular}{lrrr}\\toprule\nSystem & Correctly undetermined & False promotions & Clean FN \\\\ \\midrule\n"+"\n".join(lines)+"\n\\bottomrule\\end{tabular}\\end{table}\n")


def main() -> None:
    HERE.mkdir(parents=True,exist_ok=True); tables()
    (HERE/"p4_2_false_promotion.svg").write_text(p4_2())
    (HERE/"p4_3_coverage_frontier.svg").write_text(p4_3())
    (HERE/"p4_4_detection_by_attack.svg").write_text(p4_4())
    (HERE/"p4_5_attribution_vs_support.svg").write_text(grouped("source_attribution_accuracy","support_contradiction_f1","Source attribution vs semantic support"))
    (HERE/"p4_6_cost_false_promotion.svg").write_text(p4_6())
    print("generated 5 V2 result SVGs + 3 tables from immutable public metrics")

if __name__ == "__main__":
    main()
