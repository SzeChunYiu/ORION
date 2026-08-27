#!/usr/bin/env python3
"""V1-Q-RESOURCE-01 quantum production-resource closure build.

Ledger: research/orion-v1-freeze/V1_EXECUTION_JOB_LEDGER_V1.json, job
V1-Q-RESOURCE-01, class QUANTUM_RESOURCE_ACCOUNTING, depends_on
[V1-Q-CENSUS-01], paper_authority_delta NONE.

Question (ledger, verbatim): "Do claimed quantum-structural gains survive
complete oracle, compiler, verification, sampling, and recovery costs?"

Protocol (ledger, verbatim): bind source theorem and target mapping; enumerate
all information, oracle, compiler, verification, hardware, and recovery
resources; construct information-matched classical/structural donor products;
retain equality or adverse outcomes as first-class results.

Execution mode "x": every input under research/orion-v1-freeze/ and every
frozen result artifact is opened READ-ONLY; outputs are additive and written
outside the freeze package; all arithmetic is integer/exact-rational
(fractions.Fraction serialized as "p/q" strings); no float is ever
constructed into an emitted artifact (machine-enforced below).

Negative terminals (frozen vocabulary):
  HIDDEN_ORACLE, COMPILER_COST_UNBOUND, VERIFICATION_COST_UNBOUND,
  DONOR_EQUIVALENT, CANNOT_CHECK.

Exit codes: 0 ok; 2 missing input; 3 frozen-binding check failure;
4 float discipline violation; 5 census coverage hole; 6 output-location
violation (inside freeze package).
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from fractions import Fraction
from itertools import combinations
from math import comb

SCHEMA_BASE = "ORION.V1.QuantumResource"
FREEZE_DIR = "research/orion-v1-freeze"
LEDGER_REL = FREEZE_DIR + "/V1_EXECUTION_JOB_LEDGER_V1.json"
CENSUS_REL = FREEZE_DIR + "/V1_QUANTUM_CENSUS_V1.json"
JOB_ID = "V1-Q-RESOURCE-01"
TERMINALS = [
    "HIDDEN_ORACLE",
    "COMPILER_COST_UNBOUND",
    "VERIFICATION_COST_UNBOUND",
    "DONOR_EQUIVALENT",
    "CANNOT_CHECK",
]

QG = "research/extensions/orion-qg/"
QN = "research/extensions/orion-qn/"
OQ = "research/extensions/orion-q/"
DISC = "research/orion-discovery-v2/exec/DISC-Q-TRANSFER-01/"
DEV = "development/orion-qg-regime-geometry/"

INPUT_FILES = [
    LEDGER_REL,
    CENSUS_REL,
    QG + "QG21_FT_CHEMISTRY_RESULTS.json",
    QG + "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json",
    QG + "QG11C_FT_LIFT_CLOSURE_RESULTS.json",
    QG + "QG32C_OBSERVATION_COST_HIERARCHY_RESULTS.json",
    QG + "QG7F_CHAIN_REPRESENTATION_AUDIT_RESULTS.json",
    QG + "QG40_PRODUCTION_COMPILER_SEPARATION_RESULTS.json",
    QG + "QG41_SIXLCU_BROAD_CLASS_RESULTS.json",
    QG + "QG42_PRODUCTION_COMPILER_TRANSFER_RESULTS.json",
    QG + "QG_PORTFOLIO_CLOSURE_RESULTS.json",
    QG + "QG10C_INTERVAL_CLOSURE_RESULTS.json",
    QG + "QG13V2_COMBINED_EDIT_RESULTS.json",
    QG + "QG14C_COMPOSITION_CLOSURE_RESULTS.json",
    QG + "QG17R_CORRECTED_PHASE_SHARPNESS_RESULTS.json",
    QG + "QG20_RANK_KAPPA_SLACK_RESULTS.json",
    QG + "QG35_SUMMARY_CONDITIONED_FIXED_RESULTS.json",
    QG + "QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json",
    QG + "QG30_BULK_COARSE_GRAIN_RESULTS.json",
    OQ + "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json",
    DISC + "MATCHED_RESOURCE_RECEIPT.json",
    DEV + "QG_COST_UNITS_STATEMENT_V1.md",
    QN + "S1A_CLASSICAL_QUERY_CEILING_AMENDMENT_V1.md",
    "papers/orion-05-tare-expressivity/CLAIM_LEDGER_V3.md",
]

RAW_CENSUS = [
    FREEZE_DIR + "/quantumcensus-20260826/raw/issue-1368.json",
    FREEZE_DIR + "/quantumcensus-20260826/raw/issue-1416.json",
    FREEZE_DIR + "/quantumcensus-20260826/raw/issue-734.json",
    FREEZE_DIR + "/quantumcensus-20260826/raw/issue-743.json",
    FREEZE_DIR + "/quantumcensus-20260826/raw/issue-881.json",
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def frac_str(x):
    x = Fraction(x)
    return "{}/{}".format(x.numerator, x.denominator)


def frac_pct_floor(x):
    """Floor percentage as an integer; exact, no rounding up, no float."""
    x = Fraction(x) * 100
    return x.numerator // x.denominator


def get(doc, dotted):
    cur = doc
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None, False
    return cur, True


def assert_no_float(obj, path="$"):
    if isinstance(obj, float):
        raise _FloatLeak(path)
    if isinstance(obj, dict):
        for k, v in obj.items():
            assert_no_float(v, path + "." + str(k))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            assert_no_float(v, path + "[{}]".format(i))


class _FloatLeak(Exception):
    pass


def median_exact(sorted_vals):
    n = len(sorted_vals)
    if n % 2 == 1:
        return Fraction(sorted_vals[n // 2])
    return Fraction(sorted_vals[n // 2 - 1] + sorted_vals[n // 2], 2)


# ---------------------------------------------------------------------------
# Frozen donor table (pre-registered): every quantum/frontier donor the
# census kept, its claimed resource requirement, the information-matched
# classical/structural donor product, and its negative terminal.
# census_issues bind issue numbers in V1_QUANTUM_CENSUS_V1.json; artifact
# paths are the files ACTUALLY present on this branch (origin/main), not the
# census's defect paths (see NEGATIVE_CONTROLS.census_binding_defects).
# ---------------------------------------------------------------------------

def _row(did, fam, issues, src, claim, rclasses, donor, terminal, justif,
         artifacts, residual_open, defect=None):
    return {
        "donor_id": did,
        "family": fam,
        "census_issues": issues,
        "source_theorem_or_result": src,
        "claimed_resource_requirement": claim,
        "resource_classes": rclasses,
        "classical_or_structural_donor": donor,
        "terminal": terminal,
        "terminal_justification": justif,
        "artifact_bindings": artifacts,
        "residual_open": residual_open,
        "census_binding_defect": defect,
    }

DONOR_TABLE = [
    _row(
        "QR-D01",
        "QG-9 / R6I-R6S support-cap ladder + all-n composition theorem",
        [762, 793, 801, 803, 790],
        ("Rank-2 support-five tightness and support<=1 / support<=2 sufficiency "
         "normalization (QG9 V5/V6, QG9T1, QG9-T2), support<=4 cumulative theorem "
         "(QG-13V4), and the all-n composition theorem (unrestricted exact DP "
         "optimum equals D++ optimum for every n)."),
        ("Support-count reductions in the frozen (4,2,2,1) role-weighted tally: "
         "fewer frame/Tag/Restore support units claimed as cheaper compilations."),
        ["compiler_units"],
        ("The stipulated exchange rates themselves: QG_COST_UNITS_STATEMENT_V1.md "
         "records rotations priced at zero and rates stipulated, not measured; the "
         "programme's own O1 (T-count) reweighting is the information-matched "
         "alternative accounting."),
        "COMPILER_COST_UNBOUND",
        ("Support tallies are not counts of any physical resource. Under the "
         "programme's own declared O1 T-count reweighting, 7752/9261 structured "
         "instances change regime and chemistry donor-exactness falls 30/30 to "
         "0/30 (NEGATIVE_CONTROLS.c3_qg2_o1_inversion). No compiler cost is "
         "bound by these units, so the claimed gain cannot survive compilation."),
        [QG + "QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json",
         QG + "QG9_V5_SUPPORT2_TIGHTNESS_RESULTS.json",
         QG + "QG13V4_SUPPORT4_RESULTS.json",
         OQ + "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json",
         DEV + "QG_COST_UNITS_STATEMENT_V1.md"],
        False,
    ),
    _row(
        "QR-D02",
        "QG-10 / QG-10C certified interval regime geometry",
        [763],
        ("Sound certification of regime geometry by certified interval "
         "arithmetic without an exact geometry oracle; closure terminal: "
         "incremental interval value donor-dependent or weak."),
        ("Cheaper certification: interval certificates claimed to certify regime "
         "geometry at lower exact-compute cost than exact solving."),
        ["verification", "sampling"],
        ("Direct exact DP over the same frozen instance set: the closure's own "
         "terminal (donor-dependent or weak value) concedes the interval route's "
         "incremental value does not separate from the exact-verification donor."),
        "VERIFICATION_COST_UNBOUND",
        ("The certified-interval route's claimed saving is a verification-cost "
         "claim. Its own committed terminal records the incremental value as "
         "donor-dependent or weak, i.e. the saving is not established against the "
         "exact-verification baseline; the verification resource actually spent "
         "(protected-run receipts) is accounted but the claimed verification "
         "advantage is not bounded below by any committed artifact."),
        [QG + "QG10_INTERVAL_GEOMETRY_RESULTS.json",
         QG + "QG10C_INTERVAL_CLOSURE_RESULTS.json",
         QG + "QG10C_PROTECTED_RUN_RECEIPT_2026-08-21.json"],
        False,
    ),
    _row(
        "QR-D03",
        "QG-11 / QG-11C / QG-11D fault-tolerant lift",
        [764, 907],
        ("Affine FT phase pullback proved with nonlinear factory counterexample; "
         "real-estimator leg terminal: REAL_ESTIMATOR_CANNOT_CHECK; architecture-"
         "conditioned successor protocol frozen but not executed."),
        ("Regime geometry claimed to lift into fault-tolerant hardware cost "
         "hierarchies (compile-time structural choice reduces FT cost)."),
        ["compiler_units", "hardware"],
        ("The nonlinear counterexample inside the committed result: the lift is "
         "refuted wherever the cost map is nonlinear, and the real-estimator leg "
         "cannot be checked inside the freeze."),
        "CANNOT_CHECK",
        ("The FT lift's resource claim cannot be charged: the committed closure "
         "itself states the real-estimator leg cannot be checked, and the "
         "architecture-conditioned successor (QG-11D) is a frozen protocol with "
         "no executed result. No FT cost number exists to compare against."),
        [QG + "QG11C_FT_LIFT_CLOSURE_RESULTS.json",
         QG + "QG11D_ARCHITECTURE_CONDITIONED_RESPONSIBILITY_PROTOCOL_V1.md"],
        True,
    ),
]
DONOR_TABLE += [
    _row(
        "QR-D04",
        "QG-13 V2/V3 combined-deletion theorem mining",
        [777, 785],
        ("Combined-edit obstruction theorems: minimal combined-edit mined and "
         "obstructed (QG13V2), three-column combined-edit theorem mining "
         "(QG13V3)."),
        ("Compositional editing of the Tag/frame structure claimed to reduce "
         "the support tally at fixed coverage."),
        ["compiler_units"],
        ("The obstruction theorems themselves: the committed terminals record "
         "obstruction, i.e. the structural donor (unedited grammar) matches or "
         "beats every mined combined edit on the frozen tally."),
        "COMPILER_COST_UNBOUND",
        ("The mined edits trade one stipulated unit for another inside the same "
         "unbound (4,2,2,1) tally; the obstruction results already concede no "
         "tally reduction, and even a tally reduction would bind no compiler "
         "cost (same unit defect as QR-D01)."),
        [QG + "QG13V2_COMBINED_EDIT_RESULTS.json",
         QG + "QG13V3_THREE_COLUMN_RESULTS.json"],
        False,
    ),
    _row(
        "QR-D05",
        "QG-14 / QG-14C compositional regime calculus",
        [768],
        ("Separable composition proved; hidden coupling refutes local "
         "selection; coupling-aware summary recovers control."),
        ("Local subproblem selection claimed to compose into globally cheaper "
         "compilations without re-solving."),
        ["compiler_units", "information"],
        ("The hidden-coupling counterexample inside the committed result: local "
         "selection is refuted and only a coupling-aware (global-information) "
         "summary recovers control, i.e. the global exact donor is required."),
        "COMPILER_COST_UNBOUND",
        ("Composition's claimed saving is a compile-time saving in the same "
         "unbound support tally; the committed result's own claim boundary "
         "states bounded theorem/counterexample control only, no universal "
         "interface compression claim. No compiler cost is bound."),
        [QG + "QG14C_COMPOSITION_CLOSURE_RESULTS.json"],
        False,
    ),
    _row(
        "QR-D06",
        "QG-17 / QG-17R phase sharpness attacks",
        [814],
        ("Adversarial sharpness attack on the R6I support-one objective phase; "
         "corrected phase sharpness finds no support-two witness in the frozen "
         "V5 domain; tie-locus analysis."),
        ("Phase-boundary sharpness claimed as certificate-margin strength for "
         "the support-one sufficiency statement."),
        ["verification", "compiler_units"],
        ("The corrected sharpness run itself: no support-two witness exists in "
         "the frozen domain, so the certificate margin claimed by sharpness is "
         "matched by the exhaustive-search donor on the same domain."),
        "COMPILER_COST_UNBOUND",
        ("Certificate margins are measured in the same unbound stipulated tally; "
         "the sharpness certificate does not price the verification compute it "
         "would license, and the domain-bound no-witness result means no "
         "compilation-cost differential is established."),
        [QG + "QG17_R6I_PHASE_SHARPNESS_RESULTS.json",
         QG + "QG17R_CORRECTED_PHASE_SHARPNESS_RESULTS.json",
         QG + "QG17B_TIE_LOCUS_RESULTS.json"],
        False,
    ),
    _row(
        "QR-D07",
        "QG-19 outside-cone hostile novelty attack",
        [862],
        ("Hostile outside-cone sharpness attack on the novelty statement."),
        ("Novelty of the regime geometry claimed robust outside the constructing "
         "cone, i.e. no cheaper classical re-derivation anticipated."),
        ["information", "verification"],
        ("No committed artifact is bound: the census evidence path "
         "QG19_HOSTILE_NOVELTY_RESULTS.json is absent from origin/main."),
        "CANNOT_CHECK",
        ("The hostile novelty attack's committed artifact is missing from "
         "origin/main under the census-bound name; without it neither the "
         "claimed margin nor the hostile control can be charged. Recorded as a "
         "census binding defect, not as a pass."),
        [],
        True,
        defect="census evidence path QG19_HOSTILE_NOVELTY_RESULTS.json "
               "absent from origin/main despite present:origin_main=true",
    ),
    _row(
        "QR-D08",
        "QG-20 rank-kappa slack columns",
        [863],
        ("Rank-kappa slack measured exactly on two families under QG-6 certified "
         "ranks; fails under the margin-aligned block rewrite; third family not "
         "derivable; alternative accounts not excluded by the data."),
        ("Slack-column structure claimed to predict cheap regime state without "
         "full recomputation (a representation-compression resource claim)."),
        ["information", "compiler_units"],
        ("The committed claim boundary itself: alternative closed-form accounts "
         "(slack = mu; slack = rank-1 indicators; etc.) are not excluded by the "
         "data, so an information-matched simpler account matches the claim."),
        "CANNOT_CHECK",
        ("Partial by its own terminal and non-exclusive against simpler "
         "classical accounts; a third measured family is not derivable. The "
         "compression claim cannot be bound to any resource without excluding "
         "the simpler donors, which the data do not."),
        [QG + "QG20_RANK_KAPPA_SLACK_RESULTS.json",
         QG + "QG20_SIXLCU_OBJECTIVE_SCOPE_RESULTS.json"],
        True,
        defect="QG20_RECOVERY_PLAN.md census path absent from origin/main",
    ),
]
DONOR_TABLE += [
    _row(
        "QR-D09",
        "QG-21 certificate-margin map (theta_FT primary objective)",
        [864],
        ("theta_FT(x) = t_nc*N_rot(x) + c_T*[support units]; N_rot = 9 "
         "family-constant, so theta_FT differences reduce exactly to the "
         "two-qubit Clifford count difference (reduction lemma); donor-exact "
         "90/90 rows at the PRIMARY objective; S1 18/90 improved by exactly 2 "
         "Cliffords."),
        ("T-weighted objective claimed to capture fault-tolerant cost "
         "differentials between compilations inside the frozen family."),
        ["compiler_units", "hardware"],
        ("The donor subtraction executed in the committed result: theta_FT is "
         "donor-exact on 90/90 real chemistry rows; the entire non-Clifford "
         "term is the family constant 9*kappa_T and cancels from every "
         "comparison, so the T-ratio between any two family members is exactly "
         "1 (recomputed in NEGATIVE_CONTROLS.c1/c2)."),
        "DONOR_EQUIVALENT",
        ("The information-matched donor (the donor construction itself, already "
         "optimal on 90/90 rows at the primary objective) matches the claimed "
         "gain exactly; the residual defensible improvement is 2 two-qubit "
         "Cliffords on 18/90 rows, at most 1/11 of the Clifford-side cost and "
         "at most 2/270 of the family-constant T backdrop (exact fractions in "
         "NEGATIVE_CONTROLS.c2_ft_dominance). Equality retained as a "
         "first-class result."),
        [QG + "QG21_FT_CHEMISTRY_RESULTS.json"],
        False,
    ),
    _row(
        "QR-D10",
        "QG-22 exact five-predicate oracle state",
        [868],
        ("Exact joint state of the five certification predicates claimed as an "
         "oracle construction."),
        ("Joint predicate state claimed queryable, licensing predicate-"
         "certified selection without paying for each predicate separately."),
        ["oracle", "information"],
        ("The construction itself is an oracle resource: preparing/querying the "
         "exact joint state presupposes the answer the five predicates "
         "certify. The information-matched classical donor is exhaustive "
         "evaluation of the five predicates, which contains exactly that "
         "information at bookkept cost (the DISC-Q oracle-charging precedent, "
         "QR-D27)."),
        "HIDDEN_ORACLE",
        ("The claimed joint state is available only by charging the hidden "
         "oracle/producer of the state; uncharged, it embeds the certified "
         "information for free. The census evidence path "
         "QG22_EXACT_FIVE_PREDICATE_STATE.json is additionally absent from "
         "origin/main (binding defect), but the terminal follows from the "
         "access model itself."),
        [],
        True,
        defect="census evidence path QG22_EXACT_FIVE_PREDICATE_STATE.json "
               "absent from origin/main despite present:origin_main=true",
    ),
    _row(
        "QR-D11",
        "QG-7e V2 partial-polytope phase",
        [872],
        ("Partial-polytope phase for R6I claimed to refine the certificate "
         "geometry cheaply."),
        ("Polytope relaxation claimed to certify phase membership at lower "
         "exact-compute cost."),
        ["verification", "compiler_units"],
        ("Partial (relaxed) certification is weaker than the exact witness "
         "donor; where the relaxation is partial, the exact DP donor already "
         "certifies strictly more."),
        "CANNOT_CHECK",
        ("No committed artifact on origin/main binds the partial-polytope phase "
         "(census path absent); the relaxation's claimed verification saving "
         "cannot be charged or compared."),
        [],
        True,
        defect="census evidence path QG7E_V2_PARTIAL_POLYTOPE_PHASE_RESULTS.json "
               "absent from origin/main despite present:origin_main=true",
    ),
    _row(
        "QR-D12",
        "QG-24 two-coordinate reduction attack",
        [874],
        ("Claim that the R6 chain's accounting reduces to two coordinates."),
        ("Reduction claimed to shrink the certificate/accounting state space "
         "(fewer coordinates to certify)."),
        ["information", "compiler_units"],
        ("The committed QG7F chain-representation audit: the two-coordinate "
         "reduction is REFUTED by a TAG3 multi-comm S2 configuration; both "
         "representations accept, so the full-coordinate incumbent donor "
         "remains necessary and the claimed shrink does not exist."),
        "DONOR_EQUIVALENT",
        ("Adverse outcome retained as first-class: the reduced representation "
         "is refuted and the incumbent full-grammar donor matches every "
         "accepted configuration; the claimed resource saving is void. Census "
         "path QG24C_REDUCTION_BOUNDARY_COUNTEREXAMPLES.json is absent from "
         "origin/main; the refutation is bound to the QG7F audit artifact that "
         "IS present (and exists at both frozen base and origin/main)."),
        [QG + "QG7F_CHAIN_REPRESENTATION_AUDIT_RESULTS.json"],
        False,
        defect="census evidence path QG24C_REDUCTION_BOUNDARY_COUNTEREXAMPLES.json "
               "absent from origin/main; refutation re-bound to QG7F audit artifact",
    ),
    _row(
        "QR-D13",
        "QG-25 tropical transfer spectra / asymptotic compiler phases",
        [881],
        ("Tropical transfer spectra and asymptotic compiler phases for periodic "
         "TARE families (raw issue title; census row titles the issue QG-7f "
         "physical-resource lower-bound engineering)."),
        ("Asymptotic tropical/compiler-phase analysis claimed to bound resource "
         "growth for periodic families."),
        ["compiler_units", "hardware"],
        ("No executed tropical-transfer resource product exists; the "
         "physical-resource lower-bound engineering named by the census row "
         "(QG-7f honest ceiling audit) was never executed either."),
        "CANNOT_CHECK",
        ("Title conflict in the census binding (issue #881 raw title is the "
         "QG-25 tropical lane; the census row calls it QG-7f) plus a missing "
         "census evidence path: neither the tropical asymptotics nor the "
         "honest lower-bound audit has a committed artifact to charge. "
         "FROZEN_EXECUTION_SUCCESSOR: open."),
        [QG + "QG7F_CHAIN_REPRESENTATION_AUDIT_RESULTS.json"],
        True,
        defect="issue #881 census title (QG-7f) conflicts with raw capture "
               "title (QG-25 tropical); census path "
               "QG7F_RESOURCE_LOWER_BOUND_ENGINEERING.md absent from origin/main",
    ),
]
DONOR_TABLE += [
    _row(
        "QR-D14",
        "QG wave-3 lanes (QG-26/27/28/29/31/33/37)",
        [879, 880, 884, 886, 888, 890, 920],
        ("Wave-3 regime-geometry extensions (Nerode minimality, Parikh "
         "histograms, etc. per the actual wave-3 artifacts on main)."),
        ("Extended regime-geometry certificates claimed to carry over to new "
         "structural coordinates."),
        ["compiler_units", "verification"],
        ("Same unit defect as QR-D01: wave-3 certificates are tallies in the "
         "stipulated (4,2,2,1) units with rotations priced at zero."),
        "CANNOT_CHECK",
        ("All seven census-bound wave-3 artifact paths "
         "(QG26/27/28/29/31/33/37_WAVE3_RESULTS.json) are absent from "
         "origin/main despite present:origin_main=true; the actually-present "
         "wave-3 artifacts carry different names and were not re-bound by the "
         "census. Resource claims cannot be charged against unbound "
         "artifacts; recorded as census binding defects."),
        [QG + "QG26_NERODE_MINIMALITY_RESULTS.json",
         QG + "QG26_PARIKH_HISTOGRAM_RESULTS.json"],
        True,
        defect="seven census wave-3 paths *_WAVE3_RESULTS.json absent from "
               "origin/main despite present:origin_main=true",
    ),
    _row(
        "QR-D15",
        "QG-32 early variant / QG-32C observation-cost hierarchy",
        [918],
        ("Observation-cost hierarchy independently recomputed from main: "
         "adaptive D*=3 < class-conditioned F*=4 < universal U*=5; four-probe "
         "cover refuted by exhaustive enumeration of 32018910 subsets."),
        ("Adaptive probing claimed to identify orbit type at strictly lower "
         "observation cost (3 vs 4 vs 5 probes)."),
        ["sampling", "information"],
        ("The adaptive strategy itself is a CLASSICAL probing scheme: the "
         "information-matched classical donor (adaptive query order over the "
         "same probe alphabet) attains the 3-probe bound. No coherent-oracle "
         "resource is used."),
        "DONOR_EQUIVALENT",
        ("The observation-cost separation is real but entirely classical: the "
         "adaptive classical donor attains the minimum; no quantum-structural "
         "resource advantage exists to survive charging (recomputed in "
         "NEGATIVE_CONTROLS.c5_observation_hierarchy). Census path "
         "QG32C_F_STAR_RESULTS.json absent; re-bound to the committed QG32C "
         "artifact present on main."),
        [QG + "QG32C_OBSERVATION_COST_HIERARCHY_RESULTS.json"],
        False,
        defect="census evidence path QG32C_F_STAR_RESULTS.json absent from "
               "origin/main; re-bound to QG32C_OBSERVATION_COST_HIERARCHY_RESULTS.json",
    ),
    _row(
        "QR-D16",
        "QG-35/35b/36 selection split, null-model audit, post-null residual",
        [942, 893, 904],
        ("Selection-split headline retracted after the null-model audit; "
         "summary-conditioned fixed-probe complexity machine-checked; "
         "instance-level residual failure."),
        ("Selection between equal-spectrum compilations claimed to carry "
         "measurable cost signal."),
        ["information", "sampling"],
        ("The null model itself: qg_null_model_check.py reproduces the "
         "selection headlines under the null, so the information-matched "
         "null donor matches the claimed signal; the QG-41 instance-level "
         "arm reproduces the same failure on a second family "
         "(3651063/5862960 failing probe pairs)."),
        "DONOR_EQUIVALENT",
        ("Headline retracted in favour of the null donor: the claimed selection "
         "signal is matched by the null model and the residual instance-level "
         "failure reproduces cross-family. Equality/adverse outcome retained "
         "as first-class. Census path QG36_POST_NULL_RESULTS.json absent; "
         "residual re-bound via the QG-41 instance-level arm."),
        [QG + "QG35_SUMMARY_CONDITIONED_FIXED_RESULTS.json",
         QG + "QG_RETRACTION_SELECTION_HEADLINES_V1.md",
         QG + "qg_null_model_check.py",
         QG + "QG41_SIXLCU_BROAD_CLASS_RESULTS.json"],
        False,
        defect="census evidence path QG36_POST_NULL_RESULTS.json absent from "
               "origin/main; residual re-bound to QG41 instance-level arm",
    ),
    _row(
        "QR-D17",
        "QG-39 post-retraction depth-distribution residual",
        [924],
        ("Depth-distribution non-null residual claimed after the selection "
         "retraction."),
        ("Residual depth signal claimed to survive the null-model retraction."),
        ["compiler_units"],
        ("The exact recomputation in QG_COST_UNITS_STATEMENT_V1.md: the frame "
         "term is identically 18 at n=1 under EVERY weight vector, the Tag "
         "weight cancels, and K = t_tag + t_r*dF3 is affine in one structural "
         "count with t_r unmeasured across the declared span {0,1,3}."),
        "COMPILER_COST_UNBOUND",
        ("The claimed residual magnitude is unbound: the regret is exactly "
         "5*t_r factored-Restore Pauli letters and t_r is unmeasured across "
         "the programme's own declared span (0, 1, or 3 giving regret 0, 5 or "
         "15). Nothing in the construction fixes which; the depth claim "
         "cannot be priced. Census path "
         "QG39_POST_NULL_RESIDUAL_RESULTS.json absent; deflation bound to the "
         "committed cost-units statement."),
        [DEV + "QG_COST_UNITS_STATEMENT_V1.md"],
        False,
        defect="census evidence path QG39_POST_NULL_RESIDUAL_RESULTS.json "
               "absent from origin/main; deflation re-bound to "
               "QG_COST_UNITS_STATEMENT_V1.md",
    ),
]
DONOR_TABLE += [
    _row(
        "QR-D18",
        "QG-40/41/42 production-compiler transfers",
        [928, 932, 933],
        ("Existence/selection separation probed in Qiskit 2.5.2 (existence NOT "
         "free in 5/10 classes, selection reproduces, one instrument defect "
         "caught and repaired), SixLCU broad class (existence FREE, selection "
         "impossible, shape determined; instance-level failure reproduces), "
         "and phenomenon transfer (validated deterministic maps, relabelling "
         "covariance 8/8)."),
        ("Structural choice phenomena claimed to transfer to production "
         "compilers, implying compile-time savings measurable in production "
         "compiler cost."),
        ["compiler_units"],
        ("The committed WARNING in the transfer artifact itself: "
         "phenomenon-transfer check only, NOT a performance comparison, and "
         "no cost number is comparable to ORION config_cost."),
        "COMPILER_COST_UNBOUND",
        ("The transfer artifacts transfer a PHENOMENON, not a cost: no "
         "production-compiler cost differential is measured anywhere in the "
         "committed results, so the claimed compile-time saving is unbound in "
         "the target compiler's own cost units. Census paths "
         "QG40_QISKET_TRANSFER_RESULTS.json / QG41_PYTKET_TRANSFER_RESULTS.json "
         "/ QG42_TRANSFER_INTERPRETATION.md absent; re-bound to the actual "
         "committed artifacts."),
        [QG + "QG40_PRODUCTION_COMPILER_SEPARATION_RESULTS.json",
         QG + "QG41_SIXLCU_BROAD_CLASS_RESULTS.json",
         QG + "QG42_PRODUCTION_COMPILER_TRANSFER_RESULTS.json"],
        False,
        defect="census evidence paths QG40_QISKET_TRANSFER_RESULTS.json, "
               "QG41_PYTKET_TRANSFER_RESULTS.json, QG42_TRANSFER_INTERPRETATION.md "
               "absent from origin/main; re-bound to actual committed artifacts",
    ),
    _row(
        "QR-D19",
        "QG-3 track-A dual-harness baseline",
        [927],
        ("qg3-positive-forecast track A: no green baseline; stage-1 exceeds the "
         "frozen 120s harness cap."),
        ("Track-A positive forecast claimed executable inside the frozen "
         "harness budget."),
        ["verification", "sampling"],
        ("The harness budget itself: the frozen dual-harness cap (120s stage-1) "
         "is the declared verification resource, and the track-A run exceeds "
         "it."),
        "VERIFICATION_COST_UNBOUND",
        ("The claimed result cannot be verified inside its declared "
         "verification budget: stage-1 exceeds the harness 120s cap and no "
         "green baseline exists (LOCAL_REPAIR lane still open in the census). "
         "The verification cost is unbound relative to the declared "
         "resources."),
        [QG + "run_qg3_dual_harness.py"],
        True,
    ),
    _row(
        "QR-D20",
        "Unbound outcome receipt + committed-file identity defect",
        [937, 1034],
        ("Protected-run outcome receipt that stayed unbound until the "
         "2026-08-26 amendment (ATOMIC_AUDIT_CONTENT_BOUND); dual-welded "
         "identity defect on a committed result file."),
        ("Outcome receipts claimed to certify protected-run results without "
         "the underlying artifact or with a defective file identity."),
        ["verification", "recovery"],
        ("The receipt-verification procedure itself: an unbound receipt cannot "
         "be re-verified from the tree, and a dual-welded identity defeats "
         "content-hash binding."),
        "VERIFICATION_COST_UNBOUND",
        ("Verification of the claimed outcomes was unbound: #937's receipt "
         "had no located artifact until the 2026-08-26 amendment bound it "
         "via CI artifacts and in-tree digest pins (ATOMIC_AUDIT_CONTENT_"
         "BOUND) and #1034's committed file carries a dual identity defect "
         "(LOCAL_REPAIR lane open). Both are first-class negatives: the "
         "verification resource required to certify these claims exceeds "
         "what the receipts declare."),
        [],
        True,
        defect="#937 evidence rows have null paths; #1034 evidence is "
               "'(see issue body for exact file)' — no tree binding",
    ),
    _row(
        "QR-D21",
        "ORION-QN quantum-native lanes (S1A, negative lane, S1B/Q0-Q1)",
        [734, 738, 743],
        ("Quantum-native S1A run (mission: explicit access model, oracle "
         "construction, measurement, verification, end-to-end resource cost, "
         "strongest same-information classical incumbent), the negative "
         "outcome lane, and the S1B/Q0-Q1 successor execution lane — all "
         "unexecuted at freeze."),
        ("Quantum-native query-complexity separation claimed over the "
         "classical query ceiling (Grover-type r versus classical K)."),
        ["oracle", "sampling", "hardware", "information"],
        ("THIS JOB CONSTRUCTS THE CLASSICAL DONOR PRODUCT: the corrected "
         "classical query ceiling p_c(K) = (K+1)/N with free final guess, "
         "K_match = max(0, ceil(p_q*N) - 1), E_C = K_match - "
         "K_match*(K_match-1)/(2N), with exact-rational Grover success "
         "p_q = W_r((N-1)/N)^2 / N via the even Chebyshev recurrence W_{r+1} "
         "= (4u-2)W_r - W_{r-1}, and brute-force strategy enumeration "
         "verifying the ceiling for N <= 8 (NEGATIVE_CONTROLS.c4)."),
        "CANNOT_CHECK",
        ("The quantum-native arm was never executed (census "
         "has_merged_material_result=false for #734/#743; QN protocol "
         "artifacts absent from origin/main), so no quantum-side resource "
         "number exists to charge. What CAN be done is done here: the "
         "information-matched classical donor product is constructed and "
         "machine-checked so the successor run has a binding comparator. "
         "The S1A fairness amendment explicitly licenses no physical or "
         "end-to-end advantage."),
        [QN + "S1A_CLASSICAL_QUERY_CEILING_AMENDMENT_V1.md"],
        True,
        defect="QN_S1A_PROTOCOL.md, QN_S1_NEGATIVE_RESULTS.json, "
               "QN_Q0_Q1_EXECUTION_PROTOCOL.md census paths absent from "
               "origin/main (unexecuted lanes)",
    ),
]
DONOR_TABLE += [
    _row(
        "QR-D22",
        "ORION-Q lane closures (Q3-Q6) and charter",
        [903, 908, 914, 921, 980],
        ("Protected rung triplet closure (Q3), Q4 closure, Q5, Q6/QG "
         "publication closure, and the ORION-Q charter authority statement."),
        ("ORION-Q lane closures claimed to retire quantum-structural questions "
         "with committed evidence."),
        ["verification", "information"],
        ("The actually-delivered bulk coarse-grain artifact (QG30: TARE bulk "
         "geometry compresses exactly to 45 signature counts, defect "
         "information remains) is the only committed main-tree product in "
         "this cluster."),
        "CANNOT_CHECK",
        ("The census-bound closure artifacts (Q3_PROTECTED_RUNG_CLOSURE.json, "
         "Q4_CLOSURE_RESULTS.json, Q5_RESULTS.json, Q_PUBLICATION_CLOSURE.md, "
         "Q_CHARTER_V1.md) are all absent from origin/main despite "
         "present:origin_main=true on four of them; the charter and several "
         "closures are unexecuted at freeze. Resource claims cannot be "
         "charged against absent artifacts."),
        [QG + "QG30_BULK_COARSE_GRAIN_RESULTS.json"],
        True,
        defect="Q3/Q4/Q5/Q_PUBLICATION/Q_CHARTER census paths absent from "
               "origin/main despite present:origin_main=true on #903/#908/#914/#921",
    ),
    _row(
        "QR-D23",
        "Q1 / TARE manuscript resource claims",
        [1389, 1409, 1418],
        ("TARE expressivity manuscript lane: sharp support-two theorem "
         "(kappa_R6M = 2) with EXACT SHARPNESS, and the receipt-bound "
         "manuscript update lane."),
        ("Support-count expressivity theorems claimed as compilation-cost "
         "statements in the manuscript."),
        ["compiler_units"],
        ("The manuscript's own claim ledger: the sharp support-two result "
         "EXPLICITLY EXCLUDES fault-tolerant resource advantage and physical "
         "quantum advantage from its claim scope."),
        "COMPILER_COST_UNBOUND",
        ("The manuscript's support-count claims are in the stipulated "
         "(4,2,2,1) tally (QR-D01 unit defect): the dominant fault-tolerant "
         "term is the family-constant 9 rotations and is invariant under "
         "every compilation choice inside the grammar, so no FT resource "
         "advantage is claimable from these theorems — exactly as the claim "
         "ledger's exclusion states. External blocker lanes (#1389) remain "
         "open."),
        ["papers/orion-05-tare-expressivity/CLAIM_LEDGER_V3.md"],
        True,
    ),
    _row(
        "QR-D24",
        "Q1-C production-resource literature map (partial)",
        [1416],
        ("PARTIAL_RESOURCE_MAP: six support-unit configurations mapped to "
         "conditional logical two-qubit Clifford counts with 9 "
         "family-constant rotations, refusing T-count/T-depth/qubit/spacetime/"
         "hardware claims; internal cross-check PRESERVES the adverse QG-21 "
         "result; literature subtraction over 16 version-bound sources; "
         "NOVELTY_NOT_ESTABLISHED. Draft PR #1449 (unmerged, base "
         "chatgpt/r9-q1-independent-audit-packet-20260826)."),
        ("Conditional Clifford-count resource map claimed as the strongest "
         "defensible resource statement for the TARE family."),
        ["compiler_units", "verification"],
        ("The donor subtraction already executed in the draft: subtracting 16 "
         "version-bound literature sources leaves the conditional Clifford "
         "map donor-matched (novelty not established), and the internal "
         "cross-check preserves the QG-21 donor-exactness adverse result."),
        "DONOR_EQUIVALENT",
        ("The strongest defensible map is conditional, partial, and "
         "donor-matched: it preserves the QG-21 adverse cross-check (90/90 "
         "donor-exact, 18/90 improved by 2 Cliffords) and its literature "
         "subtraction leaves no residual capability. Equality/adverse "
         "outcome retained as first-class. NOTE: this row binds an UNMERGED "
         "draft (PR #1449), not origin/main — weaker evidence class, "
         "recorded as such."),
        [],
        True,
        defect="evidence is draft PR #1449 (unmerged; base is not main); "
               "census path QG21_CERTIFICATE_MARGIN_MAP.json absent from "
               "origin/main",
    ),
    _row(
        "QR-D25",
        "Q1 external validation blocker",
        [1427],
        ("External validation of Q1 claims blocked (no reviewer-external "
         "execution)."),
        ("Manuscript claims held pending external validation."),
        ["verification", "hardware"],
        ("No external validator exists inside the freeze; external validation "
         "is by definition outside the executable scope."),
        "CANNOT_CHECK",
        ("External validation is not executable inside the frozen base; the "
         "authority ceiling assigns external_validation = CANNOT_CHECK. "
         "Blocked lane, retained open."),
        [],
        True,
    ),
    _row(
        "QR-D26",
        "ORION-RG QLDPC decoder transfer",
        [897],
        ("Quantum LDPC decoder transfer lane (census-class "
         "FROZEN_EXECUTION_SUCCESSOR, not executed)."),
        ("Quantum code decoder transfer claimed as a resource-relevant "
         "structural result."),
        ["hardware", "recovery"],
        ("No executed arm; no classical decoder comparison constructed."),
        "CANNOT_CHECK",
        ("Unexecuted successor lane (has_merged_material_result=false, null "
         "evidence rows): nothing to charge. Retained open."),
        [],
        True,
    ),
    _row(
        "QR-D27",
        "DISC-Q matched-resource transfer (oracle-charging control)",
        [1306],
        ("Exact cross-domain transfer with matched-resource accounting: "
         "terminal SURFACE_ANALOGY_OR_RESOURCE_ADVANTAGE_ONLY; verdict "
         "APPARENT_ADVANTAGE_DISAPPEARS_UNDER_ORACLE_CHARGING; donor arm "
         "total enumeration resource vector [524287, 524287, 1536, 763, 0]; "
         "anti-laundering note: kappa is not available a priori in the "
         "target and the transferred arm is charged oracle subsets."),
        ("Cross-domain structural transfer claimed to carry a cost advantage "
         "into the target domain."),
        ["oracle", "information"],
        ("The donor arm itself: total enumeration with the same adequacy "
         "predicate and validator, same instance and obligation set."),
        "HIDDEN_ORACLE",
        ("Control precedent executed with integers only: the transfer's "
         "apparent advantage disappears once the hidden oracle that produced "
         "kappa is charged (disjuncts "
         "RESOURCE_ADVANTAGE_DOES_NOT_SURVIVE_ORACLE_CHARGING and "
         "DONOR_SUBTRACTION_RESIDUAL_CAPABILITY_EMPTY both fired; "
         "gate.passed=false). This row is the executed template for every "
         "HIDDEN_ORACLE charge in this ledger."),
        [DISC + "MATCHED_RESOURCE_RECEIPT.json",
         DISC + "disc_q_transfer_01.py"],
        False,
    ),
    _row(
        "QR-D28",
        "QG portfolio closure and upper-bound-only authority honesty",
        [911],
        ("QG earned portfolio lanes adjudicated closed with mixed "
         "theorem/refutation and boundaries preserved; upper-bound-only "
         "authority conceded by the programme."),
        ("No uncharged advantage is claimed: the portfolio's authority "
         "statements are upper-bound-only."),
        ["information"],
        ("Every bound artifact in this ledger: physical_quantum_advantage_claim "
         "= false is machine-checked in the QG-21 result (the primary "
         "objective artifact)."),
        "CANNOT_CHECK",
        ("The honesty lane concedes the vacuity: with upper-bound-only "
         "authority and physical_quantum_advantage_claim=false machine-"
         "recorded in the primary artifacts, there is no claimed resource "
         "advantage whose survival could be checked beyond the per-donor "
         "accounting above. Retained as a first-class negative: the question "
         "is vacuous here, not satisfied."),
        [QG + "QG_PORTFOLIO_CLOSURE_RESULTS.json",
         QG + "QG21_FT_CHEMISTRY_RESULTS.json"],
        False,
    ),
]

OUT_OF_SCOPE = {
    1359: "shadow/orion-v1-quantum-issue-disposition packet handoff "
          "(governance lane; no claimed resource gain)",
    1368: "denominator-complete open-issue census + tranche terminal "
          "vocabulary (governance parent of this job; no resource claim)",
    1362: "paper candidate blocked on quantum-freeze evidence (paper-authority "
          "blocker lane; resource accounting supplied by QR-D23/QR-D24; no "
          "independent resource claim)",
}


# ---------------------------------------------------------------------------
# Frozen-binding checks: values this job's accounting RELIES ON, verified
# against the committed artifacts at run time. (path, dotted key, expected)
# ---------------------------------------------------------------------------

BINDING_CHECKS = [
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "per_objective_summary.theta_FT.donor_exact_rows", 90),
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "per_objective_summary.theta_FT.rows", 90),
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "per_objective_summary.S1.donor_exact_rows", 72),
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "per_objective_summary.S1.strictly_improved_rows", 18),
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "per_objective_summary.S1.delta_max", 2),
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "per_objective_summary.S1.derivable_from_ft_accounting", True),
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "per_objective_summary.O1_control.donor_exact_rows", 0),
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "per_objective_summary.O1_control.derivable_from_ft_accounting", False),
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "physical_quantum_advantage_claim", False),
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "q3_magnitude.family_constant_non_clifford_backdrop."
     "implied_t_gate_backdrop_range", [270, 900]),
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "q3_magnitude.defensible_only_distribution.delta_max", 2),
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "qg2_binding.O0_census_match", True),
    (QG + "QG21_FT_CHEMISTRY_RESULTS.json",
     "qg2_binding.O1_census_match", True),
    (QG + "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json",
     "baseline_control_O0.chemistry_summary.donor_exact_count", 30),
    (QG + "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json",
     "objectives.O1.chemistry_donor_exact_count", 0),
    (QG + "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json",
     "objectives.O1.membership_transitions.DONOR_EXACT->BORROW", 6014),
    (QG + "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json",
     "objectives.O1.membership_transitions.SPLIT->BORROW", 1738),
    (QG + "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json",
     "objectives.O1.panels.structured_n2.instances", 9261),
    (QG + "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json",
     "objectives.O1.panels.structured_n2.donor_exact_count", 549),
    (QG + "QG32C_OBSERVATION_COST_HIERARCHY_RESULTS.json",
     "results.adaptive_D_star", 3),
    (QG + "QG32C_OBSERVATION_COST_HIERARCHY_RESULTS.json",
     "results.class_conditioned_F_star", 4),
    (QG + "QG32C_OBSERVATION_COST_HIERARCHY_RESULTS.json",
     "results.universal_U_star", 5),
    (QG + "QG32C_OBSERVATION_COST_HIERARCHY_RESULTS.json",
     "universal_minimum_is_exactly_5.four_probe_cover_exists", False),
    (QG + "QG7F_CHAIN_REPRESENTATION_AUDIT_RESULTS.json",
     "both_accept", True),
    (QG + "QG40_PRODUCTION_COMPILER_SEPARATION_RESULTS.json",
     "results.classes_tested", 10),
    (QG + "QG40_PRODUCTION_COMPILER_SEPARATION_RESULTS.json",
     "results.classes_where_optimal_cost_differs", 5),
    (QG + "QG41_SIXLCU_BROAD_CLASS_RESULTS.json",
     "instance_level.failing_probe_pairs", 3651063),
    (QG + "QG41_SIXLCU_BROAD_CLASS_RESULTS.json",
     "instance_level.probes", 5862960),
    (DISC + "MATCHED_RESOURCE_RECEIPT.json", "gate.passed", False),
    (DISC + "MATCHED_RESOURCE_RECEIPT.json",
     "terminal", "SURFACE_ANALOGY_OR_RESOURCE_ADVANTAGE_ONLY"),
    (DISC + "MATCHED_RESOURCE_RECEIPT.json",
     "terminal_reading.disjuncts_fired",
     ["RESOURCE_ADVANTAGE_DOES_NOT_SURVIVE_ORACLE_CHARGING",
      "DONOR_SUBTRACTION_RESIDUAL_CAPABILITY_EMPTY"]),
    (DISC + "MATCHED_RESOURCE_RECEIPT.json",
     "arms.D1_donor_total_enumeration.resource_vector",
     [524287, 524287, 1536, 763, 0]),
    (OQ + "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json",
     "runtime_seconds", None),  # existence + type only
]


def run_binding_checks(repo):
    results = []
    ok = True
    for path, dotted, expected in BINDING_CHECKS:
        full = os.path.join(repo, path)
        if not os.path.exists(full):
            results.append({"path": path, "key": dotted,
                            "status": "MISSING_FILE"})
            ok = False
            continue
        doc = json.load(open(full))
        val, found = get(doc, dotted)
        if not found:
            results.append({"path": path, "key": dotted,
                            "status": "MISSING_KEY"})
            ok = False
            continue
        if expected is None:
            status = "OK_TYPE_{}".format(type(val).__name__)
        elif val == expected and type(val) is type(expected):
            status = "OK"
        else:
            status = "MISMATCH_got={!r}".format(val)
            ok = False
        results.append({"path": path, "key": dotted, "status": status})
    return ok, results


# ---------------------------------------------------------------------------
# C1 — QG-21 donor-exactness recomputation per objective (from raw rows).
# ---------------------------------------------------------------------------

def c1_donor_exactness(repo):
    """Recompute per-objective donor-exactness from the committed artifact's
    own witness list (improvements) and prediction column (rows), then
    cross-check against the committed per_objective_summary."""
    doc = json.load(open(os.path.join(
        repo, QG + "QG21_FT_CHEMISTRY_RESULTS.json")))
    rows = doc["rows"]
    row_accounting = {}
    for r in rows:
        for o, pred in r["predictions"].items():
            a = row_accounting.setdefault(
                o, {"rows": 0, "delta_zero": 0, "delta_positive": 0})
            a["rows"] += 1
            dl = pred.get("predicted_delta_vs_donor")
            if dl == 0:
                a["delta_zero"] += 1
            elif dl is not None and dl > 0:
                a["delta_positive"] += 1
    witness = {}
    for imp in doc["improvements"]:
        w = witness.setdefault(imp["objective"],
                               {"witness_improved": 0, "delta_max": 0})
        w["witness_improved"] += 1
        w["delta_max"] = max(w["delta_max"], imp["delta_vs_donor"])
    summary = {}
    for o, s in doc["per_objective_summary"].items():
        ra = row_accounting.get(o, {})
        wi = witness.get(o, {"witness_improved": 0, "delta_max": 0})
        pred_column_referee_matched = s["prediction_cost_match_rows"] == s["rows"]
        delta_accounting_match = (
            pred_column_referee_matched
            and ra.get("delta_zero") == s["donor_exact_rows"]
            and ra.get("delta_positive") == s["strictly_improved_rows"])
        witness_match = (wi["witness_improved"]
                         == s["strictly_improved_rows"])
        summary[o] = {
            "committed_rows": s["rows"],
            "committed_donor_exact_rows": s["donor_exact_rows"],
            "committed_strictly_improved_rows": s["strictly_improved_rows"],
            "committed_prediction_cost_match_rows":
                s["prediction_cost_match_rows"],
            "row_accounting": ra,
            "witness_accounting": wi,
            "witness_count_matches_committed": witness_match,
            "delta_accounting_matches_committed": delta_accounting_match,
            "note": None,
        }
        if not pred_column_referee_matched:
            summary[o]["note"] = (
                "prediction column NOT referee-matched under this objective "
                "({}/{}); the witness list is authoritative and gives {} "
                "strict improvements, donor_exact {}".format(
                    s["prediction_cost_match_rows"], s["rows"],
                    wi["witness_improved"], s["donor_exact_rows"]))
        summary[o]["recomputation_consistent"] = bool(
            witness_match and (delta_accounting_match
                               or not pred_column_referee_matched))
    return {
        "control": "c1_qg21_donor_exactness",
        "recomputed_from": ("rows.predictions and improvements of "
                            "QG21_FT_CHEMISTRY_RESULTS.json"),
        "per_objective": summary,
        "headline": {
            "theta_FT_donor_exact": "90/90",
            "S1_improved_by_exactly_delta": "18/90 rows at delta 2",
            "O1_control_control_not_defensible": (
                "90/90 strictly improved under the control reweighting but "
                "0/90 prediction-cost match: the control objective does not "
                "carry referee-matched predictions (CONTROL_NOT_DEFENSIBLE), "
                "exactly as committed"),
        },
        "all_objectives_consistent": all(
            v["recomputation_consistent"] for v in summary.values()),
    }


# ---------------------------------------------------------------------------
# C2 — exact-rational FT-dominance bound for the defensible improvement.
# ---------------------------------------------------------------------------

def c2_ft_dominance(repo):
    doc = json.load(open(os.path.join(
        repo, QG + "QG21_FT_CHEMISTRY_RESULTS.json")))
    defensible = [i for i in doc["improvements"]
                  if i.get("objective_defensible")]
    deltas = sorted(i["delta_vs_donor"] for i in defensible)
    costs = sorted(i["donor_cost_C_R6L"] for i in defensible)
    dmax = deltas[-1]
    cmin = costs[0]
    backdrop = doc["q3_magnitude"]["family_constant_non_clifford_backdrop"]
    t_min = backdrop["implied_t_gate_backdrop_range"][0]
    rot = backdrop["rotations_per_compilation"]
    t_per_rot_min = backdrop["t_gates_per_rotation_range"][0]
    # exact fractions; generous equivalence 1 two-qubit Clifford = 1 T gate
    frac_of_own_clifford_cost = Fraction(dmax, cmin + dmax)
    frac_of_t_backdrop = Fraction(dmax, t_min)
    median_delta = median_exact(deltas)
    median_cost = median_exact(costs)
    return {
        "control": "c2_ft_dominance",
        "defensible_improvements": len(defensible),
        "delta_max_two_qubit_cliffords": dmax,
        "delta_median_exact": frac_str(median_delta),
        "donor_cost_C_min": cmin,
        "donor_cost_C_median_exact": frac_str(median_cost),
        "rotations_per_compilation_family_constant": rot,
        "t_backdrop_min": t_min,
        "t_backdrop_min_check": "{} x {}".format(rot, t_per_rot_min),
        "max_fraction_of_own_clifford_cost_exact":
            frac_str(frac_of_own_clifford_cost),
        "max_fraction_of_own_clifford_cost_pct_floor":
            frac_pct_floor(frac_of_own_clifford_cost),
        "max_fraction_of_t_backdrop_exact":
            frac_str(frac_of_t_backdrop),
        "max_fraction_of_t_backdrop_pct_floor":
            frac_pct_floor(frac_of_t_backdrop),
        "statement": (
            "The strongest defensible improvement inside the frozen family is "
            "{} two-qubit Cliffords on {}/90 rows; that is at most {}/{} of "
            "the Clifford-side cost and, under the generous 1-Clifford-equals-"
            "1-T equivalence, at most {}/{} of the family-constant T backdrop "
            "of {} gates; the entire non-Clifford term is the constant "
            "{}*kappa_T and cancels from every comparison."
        ).format(dmax, len(defensible),
                 frac_of_own_clifford_cost.numerator,
                 frac_of_own_clifford_cost.denominator,
                 frac_of_t_backdrop.numerator,
                 frac_of_t_backdrop.denominator, t_min, rot),
    }


# ---------------------------------------------------------------------------
# C3 — QG-2 O1 inversion recomputation.
# ---------------------------------------------------------------------------

def c3_qg2_o1_inversion(repo):
    doc = json.load(open(os.path.join(
        repo, QG + "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json")))
    o1 = doc["objectives"]["O1"]
    tr = o1["membership_transitions"]
    n_trans = tr["DONOR_EXACT->BORROW"] + tr["SPLIT->BORROW"]
    structured = o1["panels"]["structured_n2"]
    instances = structured["instances"]
    base_struct = doc["baseline_control_O0"]["structured_summary"]
    return {
        "control": "c3_qg2_o1_inversion",
        "baseline_O0_chemistry_donor_exact":
            "{}/30".format(
                doc["baseline_control_O0"]["chemistry_summary"]
                ["donor_exact_count"]),
        "O1_chemistry_donor_exact":
            "{}/30".format(o1["chemistry_donor_exact_count"]),
        "O1_structured_instances": instances,
        "O1_structured_donor_exact": structured["donor_exact_count"],
        "O1_structured_regime_borrow": structured["regime_borrow_count"],
        "O1_membership_transitions": tr,
        "O1_membership_transition_total": n_trans,
        "O1_transition_fraction_exact": frac_str(Fraction(n_trans, instances)),
        "O1_transition_fraction_pct_floor":
            frac_pct_floor(Fraction(n_trans, instances)),
        "baseline_O0_structured_donor_exact":
            base_struct["donor_exact_count"],
        "verdict": (
            "Under the programme's own declared T-count reweighting the "
            "support-tally conclusions invert: {}/{} structured instances "
            "({}%) change regime and chemistry donor-exactness falls from "
            "30/30 to 0/30. Cross-bound to QG-21 via "
            "qg2_binding.O0/O1_census_match=true."
        ).format(n_trans, instances,
                 frac_pct_floor(Fraction(n_trans, instances))),
    }


# ---------------------------------------------------------------------------
# C4 — S1A information-matched classical query-ceiling donor product.
# Exact rational Grover success: p_q = W_r((N-1)/N)^2 / N with the even
# Chebyshev recurrence W_{r+1}(u) = (4u-2) W_r(u) - W_{r-1}(u), integer
# arithmetic in u = (N-1)/N via Fractions. No float anywhere.
# ---------------------------------------------------------------------------

def grover_pq(N, r):
    """Exact success probability of r Grover iterations, N items, 1 marked."""
    u = Fraction(N - 1, N)
    if r < 0:
        raise ValueError("negative r")
    w_prev, w_cur = Fraction(1), Fraction(4) * u - 1  # W_0, W_1
    if r == 0:
        w = w_prev
    elif r == 1:
        w = w_cur
    else:
        for _ in range(r - 1):
            w_prev, w_cur = w_cur, (4 * u - 2) * w_cur - w_prev
        w = w_cur
    return w * w / N


def classical_ceiling_verification(N):
    """Brute-force verify p_c(K) = (K+1)/N over ALL deterministic strategies
    (K-subset of queries + one guessed location) for hidden-uniform marked
    item: every strategy with guess outside the queried set achieves exactly
    (K+1)/N; no strategy exceeds it."""
    rows = []
    for K in range(N):
        best = Fraction(-1)
        worst = Fraction(N + 1)
        n_strat = 0
        for S in combinations(range(N), K):
            sset = set(S)
            for g in range(N):
                n_strat += 1
                # success probability under hidden-uniform marked item
                wins = sum(1 for m in range(N) if m in sset or m == g)
                p = Fraction(wins, N)
                best = max(best, p)
                worst = min(worst, p)
                expected = Fraction(K + 1, N) if g not in sset else None
                if expected is not None and p != expected:
                    return None
        rows.append({
            "K": K,
            "strategies_enumerated": n_strat,
            "max_success_exact": frac_str(best),
            "min_success_exact": frac_str(worst),
            "ceiling_formula": "{}/{}".format(K + 1, N),
            "max_equals_ceiling": best == Fraction(K + 1, N),
            "no_strategy_exceeds_ceiling": best <= Fraction(K + 1, N),
        })
    return rows


def c4_classical_query_ceiling():
    ladder = []
    for n in range(3, 11):
        N = 2 ** n
        r_cap = 8 * N  # generous integer cap; r_half is always O(sqrt(N))
        # smallest r whose single-run success reaches at least 1/2: the
        # efficient fixed query count of plain Grover for this N
        r_half = None
        for r in range(0, r_cap + 1):
            if grover_pq(N, r) >= Fraction(1, 2):
                r_half = r
                break
        assert r_half is not None
        pq = grover_pq(N, r_half)
        ceil_val = pq * N
        # ceil(ceil_val) via the floor(-x) identity on Fractions, minus 1
        K_match = -((-ceil_val.numerator) // ceil_val.denominator) - 1
        K_match = max(0, min(K_match, N - 1))
        e_c = Fraction(K_match) - Fraction(K_match * (K_match - 1), 2 * N)
        ladder.append({
            "n": n,
            "N": N,
            "smallest_r_with_p_at_least_half": r_half,
            "p_at_that_r_exact": frac_str(pq),
            "classical_K_match": K_match,
            "classical_E_C_exact": frac_str(e_c),
            "query_ratio_r_half_over_K_match_exact":
                frac_str(Fraction(r_half, K_match)) if K_match else
                "unbounded",
        })
    verify = {}
    for N in (4, 8):
        rows = classical_ceiling_verification(N)
        verify[str(N)] = {
            "rows": rows,
            "all_ceilings_verified":
                rows is not None and all(r["max_equals_ceiling"]
                                         and r["no_strategy_exceeds_ceiling"]
                                         for r in rows),
        }
    return {
        "control": "c4_s1a_classical_query_ceiling",
        "formulas": {
            "classical_ceiling": "p_c(K) = (K+1)/N (free final guess allowed)",
            "K_match": "max(0, ceil(p_q*N) - 1), capped at N-1",
            "E_C": "K_match - K_match*(K_match-1)/(2N)",
            "grover_exact":
                "p_q = W_r((N-1)/N)^2 / N, W_{r+1}=(4u-2)W_r-W_{r-1}",
            "r_definition": ("smallest r with single-run success >= 1/2 "
                             "(the efficient fixed query count of plain "
                             "Grover; larger dense-oscillation r with "
                             "marginally higher success are NOT used, since "
                             "they are not the canonical query count)"),
            "integer_discipline":
                "all values exact rationals; no float constructed",
        },
        "ladder_n3_to_n10": ladder,
        "brute_force_strategy_enumeration": verify,
        "classical_free_final_guess_allowed": True,
        "external_output_verification_is_separate_resource": True,
        "statement": (
            "The corrected classical comparator dominates the prior K/N rule "
            "and is verified by exhaustive strategy enumeration at N=4 and "
            "N=8; against it, the Grover query counts retain a query gap on "
            "the ladder but no physical or end-to-end advantage is licensed "
            "(S1A amendment, frozen pre-outcome). The quantum-native arm "
            "remains unexecuted, so this product stands as the "
            "information-matched classical donor for the successor run."
        ),
    }


# ---------------------------------------------------------------------------
# C5 — QG-32C observation-hierarchy consistency recompute.
# ---------------------------------------------------------------------------

def c5_observation_hierarchy(repo):
    doc = json.load(open(os.path.join(
        repo, QG + "QG32C_OBSERVATION_COST_HIERARCHY_RESULTS.json")))
    hist = doc["per_class_minimum_fixed_probe_histogram"]
    hist_total = sum(int(v) for v in hist.values())
    res = doc["results"]
    return {
        "control": "c5_observation_hierarchy",
        "histogram": hist,
        "histogram_class_total": hist_total,
        "adaptive_D_star": res["adaptive_D_star"],
        "class_conditioned_F_star": res["class_conditioned_F_star"],
        "universal_U_star": res["universal_U_star"],
        "hierarchy_strict": (
            res["adaptive_D_star"] < res["class_conditioned_F_star"]
            < res["universal_U_star"]),
        "four_probe_cover_exists":
            doc["universal_minimum_is_exactly_5"]["four_probe_cover_exists"],
        "four_subsets_enumerated":
            doc["universal_minimum_is_exactly_5"]
            ["four_subsets_enumerated_exhaustively"],
        "statement": (
            "The hierarchy 3 < 4 < 5 is real and machine-checked, but the "
            "adaptive 3-probe optimum is attained by a classical adaptive "
            "probing donor; no quantum-structural resource is used or "
            "claimed, so the observation-cost separation is a classical "
            "donor product (DONOR_EQUIVALENT for QR-D15)."
        ),
    }


# ---------------------------------------------------------------------------
# C6 — DISC-Q oracle-charging binding.
# ---------------------------------------------------------------------------

def c6_oracle_charging(repo):
    doc = json.load(open(os.path.join(
        repo, DISC + "MATCHED_RESOURCE_RECEIPT.json")))
    return {
        "control": "c6_oracle_charging_binding",
        "job_id": doc["job_id"],
        "terminal": doc["terminal"],
        "verdict": doc["verdict"],
        "disjuncts_fired": doc["terminal_reading"]["disjuncts_fired"],
        "gate_passed": doc["gate"]["passed"],
        "arithmetic": doc["arithmetic"],
        "donor_resource_vector":
            doc["arms"]["D1_donor_total_enumeration"]["resource_vector"],
        "anti_laundering_note": doc["anti_laundering_note"],
        "statement": (
            "The executed control precedent: an apparent transfer advantage "
            "disappears under oracle charging with residual capability empty "
            "after donor subtraction. This is the binding template for every "
            "HIDDEN_ORACLE terminal assigned in this ledger."
        ),
    }


# ---------------------------------------------------------------------------
# C7 — census coverage: every census issue mapped to a donor row or
# explicitly out of scope. C8 — census binding-defect audit recomputed live
# against the tree this job runs on.
# ---------------------------------------------------------------------------

def c7_census_coverage(census):
    issue_ids = [i["issue"] for i in census["issues"]]
    mapped = {}
    for row in DONOR_TABLE:
        for n in row["census_issues"]:
            mapped.setdefault(n, []).append(row["donor_id"])
    oos = set(OUT_OF_SCOPE)
    unmapped = [n for n in issue_ids if n not in mapped and n not in oos]
    orphans = sorted(n for n in mapped if n not in issue_ids)
    return {
        "control": "c7_census_coverage",
        "census_issue_count": len(issue_ids),
        "issues_mapped_to_donor_rows": len([n for n in issue_ids
                                            if n in mapped]),
        "issues_explicitly_out_of_scope": sorted(oos & set(issue_ids)),
        "out_of_scope_reasons": {str(k): v for k, v in OUT_OF_SCOPE.items()},
        "unmapped_issues": unmapped,
        "donor_rows_referencing_unknown_issues": orphans,
        "coverage_complete": (not unmapped and not orphans
                              and len(issue_ids) == len(set(issue_ids))),
    }


def c8_census_binding_defects(repo, census):
    """Recompute, against the tree this job runs on, which census evidence
    paths resolve. Placeholders ('(see issue body...)', null, empty) are
    counted separately from hard misses on rows claiming a merged result."""
    placeholders = ("(", "", None)
    defects = []
    stats = {"evidence_rows": 0, "resolved": 0, "placeholder": 0,
             "missing": 0}
    for i in census["issues"]:
        for e in (i.get("evidence") or []):
            p = e.get("path")
            stats["evidence_rows"] += 1
            if p is None or not str(p).strip() or "(" in str(p):
                stats["placeholder"] += 1
                continue
            cands = [p, os.path.join(FREEZE_DIR, p)]
            if any(os.path.exists(os.path.join(repo, c)) for c in cands):
                stats["resolved"] += 1
            else:
                stats["missing"] += 1
                defects.append({"issue": i["issue"], "path": p,
                                "census_has_merged_material_result":
                                    bool(i.get("has_merged_material_result"))})
    by_issue = {}
    for d in defects:
        by_issue.setdefault(d["issue"], []).append(d["path"])
    hard = sorted(n for n, v in by_issue.items()
                  if census_issues_with_merged(census, n)
                  and not issue_has_any_resolved(repo, census, n))
    return {
        "control": "c8_census_binding_defects",
        "statistics": stats,
        "missing_path_count": len(defects),
        "issues_claiming_merged_result_with_zero_resolvable_artifacts":
            hard,
        "issue_count_of_hard_defects": len(hard),
        "all_missing_paths": defects,
        "statement": (
            "The census binds {} evidence paths that do not exist in the "
            "tree this job executed on; {} issues claim "
            "has_merged_material_result=true with ZERO resolvable artifact "
            "paths. This job's donor table re-binds every affected family to "
            "the artifacts actually present (recorded per row in "
            "census_binding_defect) and retains the defects as first-class "
            "data notes rather than silently trusting the census paths."
        ).format(len(defects), len(hard)),
    }


def census_issues_with_merged(census, n):
    for i in census["issues"]:
        if i["issue"] == n:
            return bool(i.get("has_merged_material_result"))
    return False


def issue_has_any_resolved(repo, census, n):
    for i in census["issues"]:
        if i["issue"] != n:
            continue
        for e in (i.get("evidence") or []):
            p = e.get("path")
            if p is None or not str(p).strip() or "(" in str(p):
                continue
            if any(os.path.exists(os.path.join(repo, c))
                   for c in (p, os.path.join(FREEZE_DIR, p))):
                return True
    return False


# ---------------------------------------------------------------------------
# Emission.
# ---------------------------------------------------------------------------

def build_resource_ledger():
    classes = ["oracle", "information", "compiler_units", "verification",
               "sampling", "recovery", "hardware"]
    ledger = {}
    for cls in classes:
        rows = [r for r in DONOR_TABLE if cls in r["resource_classes"]]
        ledger[cls] = {
            "donor_rows": [r["donor_id"] for r in rows],
            "terminal_counts": {
                t: len([r for r in rows if r["terminal"] == t])
                for t in TERMINALS if any(r["terminal"] == t for r in rows)},
            "surviving_resource_advantage_count": 0,
            "residual_open_rows": [r["donor_id"] for r in rows
                                   if r["residual_open"]],
        }
    ledger["totals"] = {
        "donor_rows": len(DONOR_TABLE),
        "terminal_counts": {
            t: len([r for r in DONOR_TABLE if r["terminal"] == t])
            for t in TERMINALS},
        "surviving_resource_advantage_count": 0,
        "residual_open_rows": [r["donor_id"] for r in DONOR_TABLE
                               if r["residual_open"]],
        "census_issues_out_of_scope": sorted(OUT_OF_SCOPE),
    }
    return ledger


def write_json(path, obj):
    assert_no_float(obj)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
        f.write("\n")
    return {"path": os.path.basename(path), "sha256": sha256_file(path),
            "bytes": os.path.getsize(path)}


def build_results_md(primary, ledger, controls, defects):
    lines = []
    a = lines.append
    a("# V1-Q-RESOURCE-01 — quantum production-resource closure (RESULTS)")
    a("")
    a("- Ledger job: `V1-Q-RESOURCE-01` (class QUANTUM_RESOURCE_ACCOUNTING, "
      "depends_on V1-Q-CENSUS-01, paper_authority_delta NONE)")
    a("- Question: *{}*".format(
        "Do claimed quantum-structural gains survive complete oracle, "
        "compiler, verification, sampling, and recovery costs?"))
    a("- Terminal: **{}**".format(primary["terminal"]))
    a("- Answer: **{}**".format(primary["answer"]))
    a("- Arithmetic discipline: integers and exact rationals only; "
      "no float constructed (machine-enforced).")
    a("")
    a("## Per-donor disposition ({})".format(len(DONOR_TABLE)))
    a("")
    a("| Donor | Census issues | Terminal | Honest disposition |")
    a("|---|---|---|---|")
    for r in DONOR_TABLE:
        a("| {} | {} | **{}** | {} |".format(
            r["donor_id"],
            ",".join(str(n) for n in r["census_issues"]) or "-",
            r["terminal"],
            r["terminal_justification"].split(". ")[0].replace("|", "/").rstrip(".") + "."))
    a("")
    a("### Terminal counts")
    a("")
    for t in TERMINALS:
        n = ledger["totals"]["terminal_counts"][t]
        a("- {}: {} donor rows".format(t, n))
    a("")
    a("Surviving resource advantage count: **0** (no donor retains an "
      "uncharged resource advantage; equalities and adverse outcomes are "
      "retained as first-class results, not rewritten).")
    a("")
    a("## Classical/structural donor products constructed")
    a("")
    a("- C1 QG-21 donor-exactness recomputed per objective from raw rows "
      "(theta_FT 90/90 donor-exact; S1 18/90 improved by exactly 2 "
      "Cliffords) — all objectives match the committed summary.")
    a("- C2 FT dominance in exact fractions: the strongest defensible "
      "improvement is at most {}/{} of the Clifford-side cost and {}/{} of "
      "the family-constant T backdrop ({} gates).".format(
          controls["c2"]["max_fraction_of_own_clifford_cost_exact"].split(
              "/")[0],
          controls["c2"]["max_fraction_of_own_clifford_cost_exact"].split(
              "/")[1],
          controls["c2"]["max_fraction_of_t_backdrop_exact"].split("/")[0],
          controls["c2"]["max_fraction_of_t_backdrop_exact"].split("/")[1],
          controls["c2"]["t_backdrop_min"]))
    a("- C3 QG-2 O1 inversion: {}/{} structured instances change regime "
      "under the programme's own T-count reweighting; chemistry "
      "donor-exactness falls 30/30 to 0/30.".format(
          controls["c3"]["O1_membership_transition_total"],
          controls["c3"]["O1_structured_instances"]))
    a("- C4 S1A classical query ceiling: corrected p_c(K)=(K+1)/N donor "
      "built and brute-force verified (N=4, N=8 exhaustive strategy "
      "enumeration); exact-rational Grover table for n=3..10; "
      "quantum-native arm remains unexecuted (CANNOT_CHECK side).")
    a("- C5 observation-cost hierarchy: 3 < 4 < 5 real but classical "
      "(adaptive probing donor attains the minimum).")
    a("- C6 DISC-Q oracle-charging control re-bound: apparent advantage "
      "disappears under oracle charging; residual capability empty.")
    a("")
    a("## Census binding defects (first-class data notes)")
    a("")
    a(defects["statement"])
    a("")
    a("Issues claiming a merged result with zero resolvable census-bound "
      "artifacts: {}.".format(
          ", ".join(str(n) for n in defects[
              "issues_claiming_merged_result_with_zero_resolvable_artifacts"])))
    a("")
    a("Affected donor rows carry a `census_binding_defect` note and are "
      "re-bound to the artifacts actually present on this branch.")
    a("")
    a("## Residual open lanes (why the tranche stays open)")
    a("")
    a("Census follow-up lanes, reconciled 2026-08-27 to the live issue "
      "states: successors 734, 743, 881, 897, 907, 980, 1389, 1409, 1416, "
      "1418, 1427 remain open; of the local-repair lane only 1034 is still "
      "open and unrepaired — 927 is repaired-and-closed via #941 and 1306 "
      "is closed/redirected; 937 is content-bound "
      "(ATOMIC_AUDIT_CONTENT_BOUND; no issue remains pending atomic "
      "audit). This job supplies the resource accounting those successors "
      "will be charged against; it does not execute them.")
    a("")
    a("## Authority ceiling")
    a("")
    a("physical_quantum_validity / quantum_advantage / novelty / "
      "external_validation remain CANNOT_CHECK by the frozen ceiling; "
      "paper_authority_delta = NONE. Negatives are never rewritten as "
      "success.")
    a("")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True,
                    help="repository root (extracted source tree)")
    ap.add_argument("--out", required=True,
                    help="output directory (must be outside the freeze "
                         "package)")
    ap.add_argument("--complete-subdir", default="complete")
    args = ap.parse_args()

    repo = os.path.abspath(args.repo)
    out = os.path.abspath(args.out)
    freeze_abs = os.path.abspath(os.path.join(repo, FREEZE_DIR))
    if os.path.commonpath([out, freeze_abs]) == freeze_abs:
        print("FATAL: output directory inside freeze package", file=sys.stderr)
        return 6
    os.makedirs(out, exist_ok=True)
    comp = os.path.join(out, args.complete_subdir)
    os.makedirs(comp, exist_ok=True)

    # inputs
    manifest = []
    missing = []
    for rel in INPUT_FILES + RAW_CENSUS:
        full = os.path.join(repo, rel)
        if not os.path.exists(full):
            missing.append(rel)
            continue
        manifest.append({"path": rel, "sha256": sha256_file(full),
                         "bytes": os.path.getsize(full)})
    if missing:
        print("FATAL: missing inputs: {}".format(missing), file=sys.stderr)
        return 2

    census = json.load(open(os.path.join(repo, CENSUS_REL)))
    ledger_doc = json.load(open(os.path.join(repo, LEDGER_REL)))
    job_entry = None
    for j in ledger_doc["jobs"]:
        if j.get("job_id") == JOB_ID:
            job_entry = j
            break
    if job_entry is None:
        print("FATAL: ledger entry for {} not found".format(JOB_ID),
              file=sys.stderr)
        return 3

    ok, checks = run_binding_checks(repo)
    if not ok:
        for c in checks:
            if c["status"] != "OK" and not c["status"].startswith("OK_TYPE"):
                print("BINDING FAILURE: {} {}".format(
                    c["path"], c["key"]), file=sys.stderr)
        return 3

    controls = {
        "c1": c1_donor_exactness(repo),
        "c2": c2_ft_dominance(repo),
        "c3": c3_qg2_o1_inversion(repo),
        "c4": c4_classical_query_ceiling(),
        "c5": c5_observation_hierarchy(repo),
        "c6": c6_oracle_charging(repo),
        "c7": c7_census_coverage(census),
        "c8": c8_census_binding_defects(repo, census),
    }
    if not controls["c7"]["coverage_complete"]:
        print("FATAL: census coverage hole: {}".format(
            controls["c7"]["unmapped_issues"]), file=sys.stderr)
        return 5
    if not controls["c1"]["all_objectives_consistent"]:
        print("FATAL: C1 recomputation inconsistent", file=sys.stderr)
        return 3
    if not controls["c5"]["hierarchy_strict"]:
        print("FATAL: C5 hierarchy not strict", file=sys.stderr)
        return 3
    for N in ("4", "8"):
        if not controls["c4"]["brute_force_strategy_enumeration"][N][
                "all_ceilings_verified"]:
            print("FATAL: C4 brute-force ceiling verification failed at "
                  "N={}".format(N), file=sys.stderr)
            return 3

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rledger = build_resource_ledger()

    primary = {
        "schema": SCHEMA_BASE + ".PrimaryResult.v1",
        "job_id": JOB_ID,
        "generated_utc": now,
        "question": ("Do claimed quantum-structural gains survive complete "
                     "oracle, compiler, verification, sampling, and recovery "
                     "costs?"),
        "answer": ("No. Across {} donor families spanning all {} census "
                   "issues, every claimed quantum-structural resource gain "
                   "terminates in a negative terminal: {} HIDDEN_ORACLE, {} "
                   "COMPILER_COST_UNBOUND, {} VERIFICATION_COST_UNBOUND, {} "
                   "DONOR_EQUIVALENT, {} CANNOT_CHECK. No donor retains an "
                   "uncharged resource advantage; equalities and adverse "
                   "outcomes are retained as first-class results."
                   ).format(
                       len(DONOR_TABLE), controls["c7"]["census_issue_count"],
                       *[rledger["totals"]["terminal_counts"][t]
                         for t in TERMINALS]),
        "terminal": "V1_QUANTUM_RESOURCE_ACCOUNTING_COMPLETE",
        "negative_terminals_allowed": TERMINALS,
        "paper_authority_delta": "NONE",
        "authority_ceiling": {
            "physical_quantum_validity": "CANNOT_CHECK",
            "quantum_advantage": "CANNOT_CHECK",
            "novelty": "CANNOT_CHECK",
            "external_validation": "CANNOT_CHECK",
        },
        "surviving_resource_advantage_count": 0,
        "gap_ledger_binding": census["terminal"],
        "ledger_entry_status_bound": job_entry.get("status"),
    }

    emitted = []

    freeze_manifest = {
        "schema": SCHEMA_BASE + ".FreezeManifest.v1",
        "job_id": JOB_ID,
        "generated_utc": now,
        "mode": "x",
        "freeze_package": FREEZE_DIR,
        "freeze_read_only": True,
        "inputs": manifest,
        "input_count": len(manifest),
        "input_manifest_sha256_combined": hashlib.sha256(
            "".join(m["sha256"] for m in manifest).encode()).hexdigest(),
        "base_main_per_ledger": ledger_doc.get("base_main"),
        "note": ("inputs opened READ-ONLY; digests above are the content "
                 "binding of this accounting"),
    }
    emitted.append(write_json(os.path.join(comp, "FREEZE_MANIFEST_V1.json"),
                              freeze_manifest))

    raw_manifest = {
        "schema": SCHEMA_BASE + ".RawManifest.v1",
        "job_id": JOB_ID,
        "generated_utc": now,
        "raw_census_captures": [m for m in manifest
                                if m["path"].startswith(FREEZE_DIR)],
        "committed_artifacts_read": [m for m in manifest
                                     if not m["path"].startswith(FREEZE_DIR)],
        "census_binding_defect_audit": controls["c8"],
        "evidence_class_note": (
            "main-tree committed artifacts (sha256-bound above) are the "
            "strong class; census raw captures are freeze-internal; draft "
            "PR #1449 evidence (QR-D24) is UNMERGED and recorded as a "
            "weaker evidence class inside the donor row, not here"),
    }
    emitted.append(write_json(os.path.join(comp, "RAW_MANIFEST_V1.json"),
                              raw_manifest))

    emitted.append(write_json(os.path.join(comp, "PRIMARY_RESULT_V1.json"),
                              primary))

    donor_result = {
        "schema": SCHEMA_BASE + ".DonorResult.v1",
        "job_id": JOB_ID,
        "generated_utc": now,
        "donor_count": len(DONOR_TABLE),
        "census_issues_covered":
            controls["c7"]["issues_mapped_to_donor_rows"],
        "census_issues_out_of_scope":
            controls["c7"]["issues_explicitly_out_of_scope"],
        "donors": DONOR_TABLE,
        "terminal_counts": rledger["totals"]["terminal_counts"],
        "surviving_resource_advantage_count": 0,
    }
    emitted.append(write_json(os.path.join(comp, "DONOR_RESULT_V1.json"),
                              donor_result))

    negative_controls = {
        "schema": SCHEMA_BASE + ".NegativeControls.v1",
        "job_id": JOB_ID,
        "generated_utc": now,
        "controls": controls,
        "binding_checks": checks,
        "binding_checks_all_ok": True,
        "no_alarm_checks": {
            "census_issue_count_is_56": controls["c7"]["census_issue_count"]
            == 56,
            "coverage_complete": controls["c7"]["coverage_complete"],
            "c1_all_objectives_consistent": controls["c1"]["all_objectives_consistent"],
            "c5_hierarchy_strict": controls["c5"]["hierarchy_strict"],
            "c4_bruteforce_all_verified": all(
                v["all_ceilings_verified"] for v in
                controls["c4"]["brute_force_strategy_enumeration"].values()),
            "census_56_distinct":
                len(set(i["issue"] for i in census["issues"])) == 56,
        },
    }
    emitted.append(write_json(os.path.join(comp, "NEGATIVE_CONTROLS_V1.json"),
                              negative_controls))

    resource_ledger = {
        "schema": SCHEMA_BASE + ".ResourceLedger.v1",
        "job_id": JOB_ID,
        "generated_utc": now,
        "resource_classes": ["oracle", "information", "compiler_units",
                             "verification", "sampling", "recovery",
                             "hardware"],
        "ledger": rledger,
        "statement": ("Complete enumeration of information, oracle, compiler, "
                      "verification, sampling, recovery and hardware "
                      "resources claimed by the census-kept donors; no class "
                      "contains a donor whose claimed advantage survives "
                      "complete charging."),
    }
    emitted.append(write_json(os.path.join(comp, "RESOURCE_LEDGER_V1.json"),
                              resource_ledger))

    transfer_result = {
        "schema": SCHEMA_BASE + ".TransferResult.v1",
        "job_id": JOB_ID,
        "generated_utc": now,
        "paper_authority_delta": "NONE",
        "residual_open_lanes": {
            "FROZEN_EXECUTION_SUCCESSOR": [734, 743, 881, 897, 907, 980,
                                           1389, 1409, 1416, 1418, 1427],
            "LOCAL_REPAIR": [927, 1034, 1306],
            "PENDING_ATOMIC_AUDIT": [],
        },
        "next_job": None,
        "next_job_note": ("no successor job is scheduled by this lane; the "
                          "freeze ledger lists no job depending on "
                          "V1-Q-RESOURCE-01; successor scheduling belongs to "
                          "the freeze owner. The classical donor product "
                          "built here (C4) is the binding comparator for the "
                          "QN successor lanes."),
        "classical_donor_products_supplied": [
            "C1 per-objective donor-exactness recomputation",
            "C2 exact FT-dominance fractions",
            "C3 objective-reweighting inversion recomputation",
            "C4 S1A classical query ceiling + brute-force verification",
            "C5 observation-hierarchy classical probing donor",
            "C6 oracle-charging control binding",
        ],
    }
    emitted.append(write_json(os.path.join(comp, "TRANSFER_RESULT_V1.json"),
                              transfer_result))

    packet_core = {
        "schema": SCHEMA_BASE + ".ResultBindingPacket.v1",
        "job_id": JOB_ID,
        "generated_utc": now,
        "ledger_path": LEDGER_REL,
        "ledger_sha256": sha256_file(os.path.join(repo, LEDGER_REL)),
        "census_path": CENSUS_REL,
        "census_sha256": sha256_file(os.path.join(repo, CENSUS_REL)),
        "input_manifest_sha256_combined":
            freeze_manifest["input_manifest_sha256_combined"],
        "terminal": primary["terminal"],
        "paper_authority_delta": "NONE",
        "mode": "x",
        "slurm_job_id": os.environ.get("QRES_SLURM_JOB_ID", "unset-local"),
        "emitted_files": emitted,
    }
    emitted.append(write_json(os.path.join(comp, "RESULT_BINDING_PACKET_V1.json"),
                              packet_core))

    md_path = os.path.join(out, "RESULTS.md")
    with open(md_path, "w") as f:
        f.write(build_results_md(primary, rledger, controls,
                                 controls["c8"]))

    # job receipt (mode x)
    receipt = {
        "schema": SCHEMA_BASE + ".JobReceipt.v1",
        "job_id": JOB_ID,
        "ledger_class": "QUANTUM_RESOURCE_ACCOUNTING",
        "depends_on": ["V1-Q-CENSUS-01"],
        "execution_mode": "x",
        "mode_x_statement": (
            "frozen inputs opened read-only; outputs additive and written "
            "outside the freeze package; integer/exact-rational arithmetic "
            "only; no float constructed into any emitted artifact "
            "(machine-enforced); every emitted file sha256-bound in "
            "RESULT_BINDING_PACKET_V1.json"),
        "generated_utc": now,
        "slurm_job_id": os.environ.get("QRES_SLURM_JOB_ID", "unset-local"),
        "executed_on": os.uname().nodename,
        "python": sys.version.split()[0],
        "input_count": len(manifest),
        "input_manifest_sha256_combined":
            freeze_manifest["input_manifest_sha256_combined"],
        "terminal": primary["terminal"],
        "paper_authority_delta": "NONE",
        "negative_terminal_counts": rledger["totals"]["terminal_counts"],
        "surviving_resource_advantage_count": 0,
        "binding_checks_all_ok": True,
        "exit_code": 0,
        "outputs": [{"path": os.path.relpath(p, out), "sha256":
                     sha256_file(p), "bytes": os.path.getsize(p)}
                    for p in [os.path.join(comp, e["path"]) for e in emitted]
                    + [md_path]],
    }
    write_json(os.path.join(comp, "V1_Q_RESOURCE_JOB_RECEIPT_V1.json"),
               receipt)

    print("terminal:", primary["terminal"])
    print("donor rows:", len(DONOR_TABLE),
          "terminal counts:", rledger["totals"]["terminal_counts"])
    print("census coverage complete:", controls["c7"]["coverage_complete"])
    print("binding defects: {} paths, {} hard issues".format(
        controls["c8"]["missing_path_count"],
        controls["c8"]["issue_count_of_hard_defects"]))
    print("outputs written to", out)
    return 0


class _FloatLeakExit(Exception):
    pass


if __name__ == "__main__":
    try:
        sys.exit(main())
    except _FloatLeak as fl:
        print("FATAL: float leaked into emitted artifact: {}".format(fl),
              file=sys.stderr)
        sys.exit(4)
