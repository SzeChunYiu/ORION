# Plot and Table Specification — ORION-ORION-14 (V1)

**Protocol:** ORION-14.protected-authority.v1  
**Builder:** `publication_svg.py` (bar_chart, heatmap)  
**Status:** DESIGN_FROZEN

## Figure ORION-14-1: Authority pipeline

**File:** `figures/p4_1_authority_pipeline.svg`  
**Type:** Process flow diagram (manual — not built by publication_svg.py)

**Content:** The ORION authority pipeline showing:
1. Proposal-only content (no authority)
2. Evidence binding (exact content + provenance hash)
3. Checker admissibility (lineage, hostility discrimination)
4. Protected evaluation (evaluator/holdout frozen)
5. Non-escalating terminal states (PROMOTE / BLOCK / CANNOT_CHECK)

**LaTeX call:**
```latex
\begin{figure}[t]
\centering
\includegraphics[width=\textwidth]{figures/p4_1_authority_pipeline}
\caption{%
  ORION authority pipeline. Retrieved or generated content remains proposal-level;
  evidence references bind exact content and provenance. Attribution and semantic
  support are evaluated separately. Checker admissibility requires lineage and
  hostile-discrimination properties. Evaluation and holdout identity are protected.
  The terminal state is PROMOTE, BLOCK, or CANNOT_CHECK.
}
\label{fig:p4_1}
\end{figure}
```

## Figure ORION-14-2: False authority-promotion rate

**File:** `figures/p4_2_false_promotion.svg`  
**Builder:** `bar_chart`

**Data mapping:**
- `label_key`: system name (e.g., "ORION", "CitationFormat", "PooledNLI", "AttributionBench", "ProvenanceGuard", "IterativeRV", "Auditability")
- `value_key`: false_authority_promotion_rate (mean across 5 repeats)
- Bar groups: systems, with Wilson 95% CI error bars

**Rendering:**
```python
bar_chart(
    data=[
        {"system": "ORION", "rate": "...", "ci_low": "...", "ci_high": "..."},
        {"system": "CitationFormat", "rate": "...", "ci_low": "...", "ci_high": "..."},
        ...
    ],
    label_key="system",
    value_key="rate",
    title="False Authority-Promotion Rate by System",
    y_label="False promotion rate",
    y_min=0, y_max=0.5,
    bar_colors=["#2196F3", "#FF9800", "#FF9800", "#FF9800", "#FF9800", "#FF9800", "#FF9800"]
)
```

**LaTeX call:**
```latex
\begin{figure}[t]
\centering
\includegraphics[width=0.85\textwidth]{figures/p4_2_false_promotion}
\caption{%
  False authority-promotion rate by system. Error bars show Wilson 95\% confidence
  intervals. ORION is shown in blue; baselines in orange. The dashed horizontal line
  marks the −0.05 practical reduction target relative to the strongest baseline.
}
\label{fig:p4_2}
\end{figure}
```

## Figure ORION-14-3: Coverage vs false-promotion frontier

**File:** `figures/p4_3_coverage_frontier.svg`  
**Builder:** `bar_chart` (paired bars per system)

**Data mapping:**
- `label_key`: system name
- `value_key`: clean_authority_coverage (left bar), false_authority_promotion_rate (right bar, inverted)

**Rendering:**
```python
bar_chart(
    data=[
        {"system": "ORION", "coverage": "...", "false_promotion": "..."},
        ...
    ],
    label_key="system",
    value_key="coverage",  # primary bar
    # secondary bar: false_promotion overlaid or side-by-side
    title="Safety–Coverage Frontier",
    y_label="Rate",
    y_min=0, y_max=1.0,
)
```

**Interpretation:** Systems in the upper-left quadrant (high coverage, low false promotion) are preferred. The figure communicates the trade-off directly.

**LaTeX call:**
```latex
\begin{figure}[t]
\centering
\includegraphics[width=0.85\textwidth]{figures/p4_3_coverage_frontier}
\caption{%
  Authority coverage vs false-promotion rate. Clean-case coverage is shown in blue;
  false-promotion rate in orange. Systems in the upper-left region achieve both high
  coverage and low false promotion.
}
\label{fig:p4_3}
\end{figure}
```

## Figure ORION-14-4: Detection rate by attack family

**File:** `figures/p4_4_detection_by_attack.svg`  
**Builder:** `heatmap`

**Data mapping:**
- `row_key`: attack family (13 families)
- `col_key`: system (ORION + 6 baselines)
- `value_key`: detection rate (proportion correctly blocked or flagged)

**Rendering:**
```python
heatmap(
    data=[...],  # 13 × 7 grid
    row_key="attack_family",
    col_key="system",
    value_key="detection_rate",
    title="Detection Rate by Attack Family",
    color_min=0, color_max=1,
    annot=True,  # show numeric values
    fmt=".2f",
)
```

**LaTeX call:**
```latex
\begin{figure}[t]
\centering
\includegraphics[width=\textwidth]{figures/p4_4_detection_by_attack}
\caption{%
  Detection rate (blocked or flagged) by attack family and system. Darker cells
  indicate higher detection. ORION should show systematically darker columns
  on attack rows while maintaining lighter (lower disruption) on clean rows.
}
\label{fig:p4_4}
\end{figure}
```

## Figure ORION-14-5: Source accuracy vs semantic support accuracy

**File:** `figures/p4_5_attribution_vs_support.svg`  
**Builder:** `bar_chart` (grouped bars)

**Data mapping:**
- `label_key`: system
- `value_key`: source_attribution_accuracy (left bar), support_contradiction_f1 (right bar)

**Rendering:**
```python
bar_chart(
    data=[
        {"system": "ORION", "attribution": "...", "support_f1": "..."},
        ...
    ],
    label_key="system",
    value_key="attribution",
    title="Source Attribution vs Semantic Support Accuracy",
    y_label="Accuracy / F1",
    y_min=0, y_max=1.0,
)
```

**LaTeX call:**
```latex
\begin{figure}[t]
\centering
\includegraphics[width=0.85\textwidth]{figures/p4_5_attribution_vs_support}
\caption{%
  Source attribution accuracy (blue) and support/contradiction F1 (orange) by system.
  Cross-source conflation attacks primarily affect attribution accuracy, revealing
  systems that conflate sources while maintaining plausible support scores.
}
\label{fig:p4_5}
\end{figure}
```

## Figure ORION-14-6: Cost vs false-promotion trade-off

**File:** `figures/p4_6_cost_false_promotion.svg`  
**Builder:** `bar_chart` (grouped bars)

**Data mapping:**
- `label_key`: system
- `value_key`: wallclock_seconds (normalized, left bar), false_authority_promotion_rate (right bar)

**Rendering:**
```python
bar_chart(
    data=[
        {"system": "ORION", "cost": "...", "false_promotion": "..."},
        ...
    ],
    label_key="system",
    value_key="cost",
    title="Cost vs False-Promotion Trade-off",
    y_label="Normalized cost / False promotion",
    y_min=0,
)
```

**LaTeX call:**
```latex
\begin{figure}[t]
\centering
\includegraphics[width=0.85\textwidth]{figures/p4_6_cost_false_promotion}
\caption{%
  Resource cost (wall-clock seconds, normalized; blue) vs false-promotion rate (orange).
  Systems with higher cost but lower false promotion may be justified for safety-critical
  scientific authority decisions.
}
\label{fig:p4_6}
\end{figure}
```

## Table ORION-14-1: Attack battery and custody manifest

**File:** `tables/p4_t1_attack_custody.tex`  
**Type:** LaTeX table (generated from ATTACK_MANIFEST_V1.jsonl)

**Columns:**
| Family | Cases (n) | Public clean | Public hostile | Protected hostile | Protected holdout | Hidden labels |
|---|---|---|---|---|---|---|
| clean_supported_positive | N | 100% | 0% | 0% | 0% | No |
| correct_fact_wrong_source | N | 0% | 100% | 0% | 0% | Yes |
| content_substitution | N | 0% | 0% | 100% | 0% | Yes |
| ... | ... | ... | ... | ... | ... | ... |

**Caption:** Attack battery composition, custody distribution, and hidden-label status. All attack labels are hidden from the candidate. Protected-hostile and protected-holdout cases are stored under independent host custody.

## Table ORION-14-2: Baseline and ablation results

**File:** `tables/p4_t2_baseline_ablation_results.tex`  
**Type:** LaTeX table

**Columns:**
| System | False promotion | Clean coverage | Correct CANNOT_CHECK | Cost (s) | ∆ vs baseline |
|---|---|---|---|---|---|
| ORION (full) | ... | ... | ... | ... | — |
| Baseline 1 | ... | ... | ... | ... | ∆_1 |
| ... | ... | ... | ... | ... | ... |
| Ablation 1 | ... | ... | ... | ... | ∆_a1 |
| ... | ... | ... | ... | ... | ... |

**Caption:** Primary and key secondary metrics for all systems. ∆ shows the difference from the full ORION system. Wilson 95% intervals in parentheses. Paired bootstrap CIs for differences.

## Table ORION-14-3: CANNOT_CHECK and error analysis

**File:** `tables/p4_t3_cannot_check_errors.tex`  
**Type:** LaTeX table

**Columns:**
| System | Total CANNOT_CHECK | Correct abstention | False block | False positive | Infra failure |
|---|---|---|---|---|---|
| ORION (full) | N | N_c | N_fb | N_fp | N_i |
| Baseline 1 | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... |

**Caption:** Breakdown of CANNOT_CHECK and error outcomes. Correct abstention: cases where the system correctly refused to commit. False block: clean positives that were incorrectly blocked. False positive: attack cases that were incorrectly promoted. Infrastructure failures are excluded from primary analysis (archived).