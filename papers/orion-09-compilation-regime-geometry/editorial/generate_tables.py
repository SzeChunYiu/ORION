#!/usr/bin/env python3
"""Generate manuscript tables directly from bound ORION-09 result records.

This script uses only the Python standard library and does not import any
scientific analyzer.  The generated LaTeX is reader-facing; internal record
identifiers remain confined to this implementation file.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-09-compilation-regime-geometry"
OUT = PAPER / "manuscript" / "generated_results_tables.tex"
SUPPORT_OUT = PAPER / "manuscript" / "generated_support_tables.tex"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text())


def main() -> None:
    shared = load("research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json")
    rank2 = load("research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json")
    rank2_parent = load("research/extensions/orion-qg/QG9_SUPPORT2_FULL_ACCEPTANCE_RESULTS.json")
    six = load("research/extensions/orion-qg/QG12_SIXLCU_P0_THEOREM_RESULTS.json")
    stab = load("research/extensions/orion-qg/QG15_THIRD_FAMILY_RESULTS.json")
    coarse = load("research/extensions/orion-qg/QG15B_PREDICATE_LANGUAGE_RESULTS.json")
    rich = load(
        "papers/orion-09-compilation-regime-geometry/evidence/"
        "R2_N2_STABPREP_L3_VOCABULARY_RESULTS.json"
    )
    phase = load("research/extensions/orion-qg/QG17R_CORRECTED_PHASE_SHARPNESS_RESULTS.json")
    slack = load("research/extensions/orion-qg/QG20_RANK_KAPPA_SLACK_RESULTS.json")

    assert shared["outcome"] == "THEOREM_MACHINE_CHECKED"
    assert rank2["intrinsic_support_number"] == 1
    assert six["blind_complete_regression"]["n2_count"] == 38_760
    assert stab["component5_prospective"]["regime_correct"] == 100
    assert coarse["q2"]["E_floor"] == 43
    assert rich["stage2"]["cv_parity_split_lookup"]["errors"] == 32

    panel_states = rich["stage2"]["panel_instances"]
    panel_singletons = rich["stage2"]["in_panel_singleton_cells"]
    panel_non_singleton_states = panel_states - panel_singletons
    assert panel_states == 120
    assert panel_singletons == 118
    assert panel_non_singleton_states == 2
    assert rich["stage2"]["in_panel_mixed_cell_count"] == 0
    # With 118 singleton cells and exactly two remaining states, the only
    # possible partition has one pure doubleton: 119 cells in total.
    panel_feature_cells = panel_singletons + 1
    assert panel_singletons + 2 == panel_states
    assert panel_feature_cells == 119

    headline = r"""% Automatically generated; do not edit by hand.
\begin{table*}[t]
\centering
\caption{The four compiler models answer different questions about exactness.  ``All sizes'' means all sizes admitted by the stated algebraic model, not arbitrary compiler or hardware settings.  Finite entries state the complete or frozen domain used.}
\label{tab:cross-model}
\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{0.21\textwidth}>{\raggedright\arraybackslash}p{0.18\textwidth}>{\raggedright\arraybackslash}p{0.22\textwidth}>{\raggedright\arraybackslash}X@{}}
\toprule
Model & Exact authority & Headline result & Boundary that remains \\
\midrule
Shared-tag Pauli block encoding & all sizes & exact optima need frame support at most 2 & the smallest named support-two trade vocabulary is still refinable \\
Rank-two dependent-triple block encoding & all sizes & intrinsic support number $\kappa=1$ under the unit objective & the support-one proof has an objective-dependent validity region \\
Six-term linear-combination compilation & all admitted batches; complete checks at $n=1,2$ & the reference compiler is exact exactly at the proved pair-gain boundary & transfer beyond the frozen cost model is not claimed \\
Weighted Clifford stabilizer-state preparation & complete graphs for $n\leq3$; frozen 120-state panel at $n=4$ & exact failures split into order, pivot, route and global mechanisms & an in-domain feature representation does not transfer to the frozen $n=4$ panel \\
\bottomrule
\end{tabularx}
\end{table*}

\begin{table}[t]
\centering
\footnotesize
\caption{Feature determination and transfer for weighted Clifford state preparation.  The 127-feature representation determines the complete $n\leq3$ labels but is nearly injective and fails the pre-specified transfer criterion.}
\label{tab:feature-transfer}
\begin{tabularx}{\columnwidth}{@{}>{\raggedright\arraybackslash}Xrr@{}}
\toprule
Quantity & Complete $n\leq3$ & Frozen $n=4$ panel \\
\midrule
States & 1,146 & 120 \\
Feature cells & 1,109 & 119 \\
Singleton cells & 1,072 & 118 \\
Mixed cells & 0 & 0 in-panel \\
Irreducible in-domain errors & 0 & 0 in-panel \\
Parity-split lookup errors & -- & 32 \\
Covered states in parity split & -- & 2 \\
Shuffle-null mean errors & -- & 32.41 \\
Empirical $p$ (errors no larger) & -- & 0.51 \\
\bottomrule
\end{tabularx}
\end{table}
"""

    support = f"""% Automatically generated; do not edit by hand.
\\newcommand{{\\ProofObligationsTable}}{{%
\\begin{{table}}[!htbp]
\\centering
\\caption{{Finite obligations supporting the two all-size normalization results.  These enumerations discharge local cases inside the analytic compositions; they are not samples from a deployment population.}}
\\label{{tab:proof-obligations}}
\\begin{{tabularx}}{{\\textwidth}}{{@{{}}>{{\\raggedright\\arraybackslash}}p{{0.24\\textwidth}}rr>{{\\raggedright\\arraybackslash}}X@{{}}}}
\\toprule
Model & Obligation & Rows & Outcome \\\\
\\midrule
Shared-tag Pauli & local exchange inequality & {shared['lemma_e']['domain_size']:,} & 0 violations \\\\
Shared-tag Pauli & parity-class tuples & {shared['lemma_b']['total_odd_alpha_tuples_checked']:,} & exact support-two boundary; 0 failures for support $3$--$8$ \\\\
Rank-two dependent triple & precursor action profiles & {rank2_parent['parent_v3']['support3_broad_type_cases']:,} & 21 unsafe before full acceptance; 0 accepted unsafe \\\\
Rank-two dependent triple & deletion cases & {rank2['finite_lemmas']['deletion']['rows']:,} & worst changes $-4$ and $-7$ \\\\
Rank-two dependent triple & core alignment & {rank2['finite_lemmas']['core_alignment']['rows']:,} & maximum increase $+3$ \\\\
Rank-two dependent triple & same-core tag rigidity & {rank2['finite_lemmas']['same_qubit_tag_rigidity']['rows']:,} & 0 different-basis counterexamples \\\\
Rank-two dependent triple & distinct-core tag lower bound & {rank2['finite_lemmas']['distinct_qubit_tag']['rows']:,} & minimum tag cost 8 \\\\
\\bottomrule
\\end{{tabularx}}
\\end{{table}}%
}}

\\newcommand{{\\StateCountsTable}}{{%
\\begin{{table}}[!htbp]
\\centering
\\caption{{Complete and prospective state-preparation counts retained in the analysis.}}
\\label{{tab:state-counts}}
\\begin{{tabular}}{{@{{}}lrr@{{}}}}
\\toprule
Domain & States & Reference compiler exact \\\\
\\midrule
$n=1$ complete & {stab['component1_regime_map']['per_n']['n1']['instances']:,} & {stab['component1_regime_map']['per_n']['n1']['donor_exact']:,} \\\\
$n=2$ complete & {stab['component1_regime_map']['per_n']['n2']['instances']:,} & {stab['component1_regime_map']['per_n']['n2']['donor_exact']:,} \\\\
$n=3$ complete & {stab['component1_regime_map']['per_n']['n3']['instances']:,} & {stab['component1_regime_map']['per_n']['n3']['donor_exact']:,} \\\\
$n=4$ frozen panel & 120 & {rich['stage2']['panel_donor_exact']:,} \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}%
}}

\\newcommand{{\\AdverseResultsTable}}{{%
\\begin{{table}}[!htbp]
\\centering
\\caption{{Adverse and conditional results that constrain interpretation.}}
\\label{{tab:adverse}}
\\begin{{tabularx}}{{\\textwidth}}{{@{{}}>{{\\raggedright\\arraybackslash}}p{{0.25\\textwidth}}>{{\\raggedright\\arraybackslash}}p{{0.24\\textwidth}}>{{\\raggedright\\arraybackslash}}X@{{}}}}
\\toprule
Question & Exact result & Allowed interpretation \\\\
\\midrule
Prospective state-preparation forecast & {stab['component5_prospective']['regime_correct']}/120 regime labels and {stab['component5_prospective']['cost_correct']}/120 exact costs matched & the frozen forecast failed; no success-rate generalization follows \\\\
Support increase outside the certificate region & {phase['candidate_count']:,} candidates, 0 strict witnesses under four objectives & a frozen-domain negative only; the global boundary remains open \\\\
Rank versus intrinsic support & slack equals the measured exchange margin on two models & a two-point, rewrite-dependent observation rather than a law \\\\
Rich state representation & 1,109 cells for 1,146 states; 1,072 singleton cells & finite-domain vocabulary existence, not compact structure or transfer \\\\
\\bottomrule
\\end{{tabularx}}
\\end{{table}}%
}}

\\newcommand{{\\SixShapeTable}}{{%
\\begin{{table}}[!htbp]
\\centering
\\footnotesize
\\caption{{Complete shape ledger for the six-term equivalence.  $T_m$ is the affine gain of one factored block of size $m$; $g_i$ denotes a pair gain.}}
\\label{{tab:six-shapes}}
\\begin{{tabularx}}{{\\textwidth}}{{@{{}}l r >{{\\raggedright\\arraybackslash}}X >{{\\raggedright\\arraybackslash}}X@{{}}}}
\\toprule
Shape & Partitions & Exact gain form & Bound under $P_0$ \\\\
\\midrule
$1+1+1+1+1+1$ & 1 & $0$ & equality \\\\
$2+1+1+1+1$ & 15 & $g_1$ & pair clause \\\\
$2+2+1+1$ & 45 & $g_1+g_2+1$ & two-disjoint-pair clause \\\\
$2+2+2$ & 15 & $g_1+g_2+g_3+2$ & perfect-matching clause \\\\
$3+1+1+1$ & 20 & $T_3-1$ & $T_3\\le0$ \\\\
$3+2+1$ & 60 & $T_3+g_1$ & both nonpositive \\\\
$3+3$ & 10 & $T_3+T_3'$ & both nonpositive \\\\
$4+1+1$ & 15 & $T_4-1$ & $T_4\\le0$ \\\\
$4+2$ & 15 & $T_4+g_1$ & both nonpositive \\\\
$5+1$ & 6 & $T_5-3$ & $T_5\\le0$ \\\\
$6$ & 1 & $23f-2s+1$ & at most $-f-3$ \\\\
\\bottomrule
\\end{{tabularx}}
\\end{{table}}%
}}

\\newcommand{{\\NearestWorkTable}}{{%
\\begin{{table}}[!htbp]
\\centering
\\scriptsize
\\caption{{Claim-by-claim nearest-work subtraction.  The comparison identifies the residual mathematical object and its consequence; it is not a priority certificate.}}
\\label{{tab:nearest-work}}
\\begin{{tabularx}}{{\\textwidth}}{{@{{}}>{{\\raggedright\\arraybackslash}}p{{0.16\\textwidth}}>{{\\raggedright\\arraybackslash}}p{{0.20\\textwidth}}>{{\\raggedright\\arraybackslash}}p{{0.29\\textwidth}}>{{\\raggedright\\arraybackslash}}X@{{}}}}
\\toprule
Advance & Closest work & Difference in object, assumptions and guarantee & Consequence retained here \\\\
\\midrule
Typed exact-regime record & Instance-space analysis and algorithm selection \\cite{{rice1976algorithm,smithmiles2023isa}} & Prior work maps features to performance or choices; the typed record separately represents theorem, certificate, representation and transfer fields with explicit missing-value semantics. & Numerical fields cannot borrow authority across type, objective or domain. \\\\
Shared-tag support two & Pauli compilation and cluster diagonalization \\cite{{peres2023pbc,vandenberg2020diagonalization}} & Prior work supplies Pauli compilation constructions; the present object is the declared three-block shared-tag grammar and the guarantee is an all-size support-two normal form under Eq.~(S4). & Search may be restricted to support two in this grammar; no hardware claim follows. \\\\
Rank-two intrinsic support one & Verified and exact circuit optimization \\cite{{hietala2021verified,iten2022patterns}} & Prior work establishes correct rewrites or exact matching; the present guarantee is tight support one for the dependent-triple grammar, with an objective-indexed proof region. & A conserved proof ceiling of five is not intrinsic support. \\\\
Six-term pair-gain boundary & Unitary partitioning and Pauli optimization \\cite{{izmaylov2020unitary,paykin2023pcoast}} & Prior work motivates grouping and Pauli optimization; the present object fixes six terms, 203 encodings and one structural objective, and proves an if-and-only-if three-clause boundary. & Reference exactness is decidable from pair-derived gains in this family only. \\\\
Adverse feature transfer & Quantum compiler prediction and bounded optimal Clifford synthesis \\cite{{quetschlich2023options,quetschlich2025predictor,bravyi2022clifford}} & Prior work predicts compilation choices or computes bounded optima; the present study couples a complete finite feature partition to a frozen next-size exact referee and retains failure. & Finite determination does not imply next-size coverage or transfer. \\\\
\\bottomrule
\\end{{tabularx}}
\\end{{table}}%
}}

"""

    # Guard the two conditional values used in prose but not interpolated above.
    assert slack["q2_relation"]["relation_holds_on_measured_families"] is True
    assert phase["candidate_count"] == 211_248
    OUT.write_text(headline)
    SUPPORT_OUT.write_text(support)


if __name__ == "__main__":
    main()
