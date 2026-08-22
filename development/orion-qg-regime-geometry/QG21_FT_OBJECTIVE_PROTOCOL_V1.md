# ORION-QG lane QG-21 — real chemistry under a fault-tolerant objective: protocol V1

Date frozen: 2026-08-22 (frozen BEFORE any chemistry outcome under any QG-21 objective was
computed). Parent: `PROGRAMME_CHARTER_V1.md`. Branch `claude/orion-harness-verification-b17qdj`.
Authority ceiling: **NOT_R6**. `novelty_authority` false, `novelty_credit` false,
`donor_novelty_credit` false. The protected stretched-N2 subject
(`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt`) is never read;
the run asserts this structurally. No existing repository file is modified. No physical
quantum-advantage claim follows from any outcome of this lane: everything below is a
compilation-cost statement under a stated cost model, not a statement about hardware, about
a device, or about any algorithm's viability.

## 1. The weakness this lane attacks

Across every real DUCC chemistry matching the programme has refereed — the 30 receipted
H4 / equilibrium-N2 rows (R6M/R6O/R6Q, re-bound by QG-2) and the 90 QG-3 track-A library
rows, with the 180 R7 structural rows agreeing — **every matching is donor-exact** under the
committed unit support-count objective: the exact optimum `C_DP` equals the cost `C_R6L` of
the simple weight-one common-anchor donor construction. The programme's trade machinery
(D+, B′, B″) has therefore never produced a *better* compilation of anything real; it has
only proved the simple construction already optimal. That is the honest limit stated in the
papers.

QG-2 (`QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`) reported that under its frozen
T-count-weighted objective O1 = (t_nc, t_c, t_tag, t_r) = (7, 1, 4, 3), chemistry loses
donor-exactness on all 30 receipted rows (`objectives.O1.chemistry_donor_exact_count = 0`),
with 6,014 DONOR_EXACT→BORROW membership transitions on the structured slice. So *if* a
T-dominant reweighting of the four support coordinates were defensible, real chemistry would
sit in trade regimes and a strictly better compilation would exist.

QG-21 asks whether that objective is defensible from explicit fault-tolerant accounting, and
then — under whatever objective the accounting actually supports — whether real chemistry
compiles strictly better.

## 2. Q1 — the fault-tolerant accounting, derived (frozen before any QG-21 outcome)

### 2.1 What the four cost coordinates physically are

The committed objective is

`C = Σ_j [4·(w(R_{j,nc}) − 1) + 2·(w(R_{j,c}) − 1)] + 2·w(S) + U_factored`

over the frozen R6M three-block TARE-M2 shared-Tag grammar. Reading the committed
circuit-level protocols rather than the scalar:

- **Frame coordinates.** `MAX_R4D_EXACT_TARE_PAIR_RESOURCE_PROTOCOL.md`: TARE's explicit
  `Uanti` circuit for m = 2 is the three-exponential sandwich
  `exp(iθ0/2 R0) · exp(iθ1 R1) · exp(iθ0/2 R0)`, and for the standard all-to-all parity-ladder
  implementation of `exp(iθP)`, `E_exp(P) = 2·max(w(P) − 1, 0)` **two-qubit parity
  entanglers**, so `E_U = 2·E_exp(R0) + E_exp(R1)`. The outer axis is applied twice
  (2 exponentials × 2 entanglers per support unit = **4 per unit**), the central axis once
  (**2 per unit**). `MAX_R6_P10_..._PROTOCOL.md` says the same in the scalar: multiplicity 2
  on the central axis and 4 on the others, "matching the five-exponential TARE
  implementation's **parity-network support accounting**". The frame multipliers 4 and 2 are
  therefore *CNOT-ladder counts*, not T counts.
- **Non-Clifford content.** Each Pauli exponential `exp(iθP)` contains exactly **one**
  arbitrary-angle single-qubit rotation, conjugated by Clifford basis changes and the parity
  ladder. Its magic-state / T cost — `≈ 3·log2(1/ε)` T gates by Ross–Selinger-class synthesis,
  or one magic state per π/8 Pauli rotation in a lattice-surgery model — depends on the
  target precision ε, **not on w(P)**. The frozen grammar fixes the rotation count:
  `N_rot = 2m − 1 = 3` per TARE-M2 block, hence `ROTATIONS_R6M = 9` for the three-block
  family (committed constant, asserted in-run).
- **Tag.** `Tag` is Clifford ("Tag is Clifford", R4D); `2·w(S)` is Tag plus Tag†, i.e. one
  controlled-Pauli letter per support unit, applied twice.
- **Restore.** `Restore` applies branch-controlled `T_k = P_k·R_k` — a controlled-Pauli, i.e.
  Clifford; `w(T_k)` is one controlled-Pauli letter per support unit, applied once per branch.
  R4D is explicit: "**Do not convert Clifford controlled-Pauli factors into T gates.**"

### 2.2 The accounting, stated

Let `c_T` be the cost of one two-qubit Clifford gate and `κ_T` the cost of synthesizing one
arbitrary-angle rotation, both in a common fault-tolerant unit (logical gate, or qubit·round
of lattice surgery). In the regime this lane cares about, `κ_T ≫ c_T` by two to three orders
of magnitude — that is exactly the fault-tolerant premise. Then for any member `x` of the
frozen grammar family compiling a fixed six-term batch,

> **θ_FT(x) = κ_T · N_rot(x) + c_T · [ 4·Σ_j (w(R_{j,nc}) − 1) + 2·Σ_j (w(R_{j,c}) − 1)
>            + 2·w(S) + 1·U_factored ]**

with one interpretive step made explicit: each controlled-Pauli letter (Tag, Restore) is
charged as **one** two-qubit Clifford gate, the same unit as one parity entangler. That single
conversion factor is the only free parameter in the Clifford half of the accounting, and §2.4
puts a frozen sensitivity band around it.

### 2.3 The two consequences, stated frozen and before any outcome

1. **A T-dominant weighting of the four support coordinates is not derivable.** Every one of
   the four coordinates is a *Clifford* count. Frame support buys CNOTs in a parity ladder; it
   does not buy T gates, because the rotation count of an exponential is 1 regardless of the
   axis weight. QG-2's O1 rationale — "the non-central branch of a TARE-M2 frame carries the
   arbitrary-angle rotation whose magic-state/T cost dominates — order 7 units per support
   unit" — misprices exactly this step: it charges T per *support unit* where the physics
   charges T per *rotation*. O1 is therefore retained by QG-21 as a **control point only**,
   labelled `derivable_from_ft_accounting: false`. If the outcome under O1 is an improvement
   and the outcome under θ_FT is not, the honest reading is that the improvement is an
   artifact of a cost model this lane cannot defend, not a compilation win.
2. **Within-family reduction lemma (frozen; verified in-run).** Every member of the frozen
   R6M grammar family (DP optimum, R6L donor, D+, D++, B′, B″) carries exactly
   `N_rot = ROTATIONS_R6M = 9` rotations, and — for a fixed matching — the same three blocks
   and hence the same rotation angles. Therefore, on a fixed matching,
   `θ_FT(x) − θ_FT(y) = c_T · [C_(4,2,2,1)(x) − C_(4,2,2,1)(y)]`: **θ_FT ranks family members
   exactly as the committed objective does, up to the additive family constant `9κ_T`.**
   This is disclosed *before* running: it means the primary-objective outcome on the 30
   receipted rows is *entailed* by the committed R6Q receipt (donor-exact), not newly
   discovered by QG-21. The new content of the lane is (i) this derivation and the refutation
   of the T-dominant reweighting in §2.3.1, (ii) the sensitivity band of §2.4, whose outcomes
   are genuinely unknown at freeze time, (iii) the extension rows, and (iv) the serialized
   improved compilations wherever any objective admits one.

### 2.4 Frozen objective set

All objectives are `C_ob = Σ_j [t_nc·(w_nc − 1) + t_c·(w_c − 1)] + t_tag·w(S) + t_r·U_factored`
plus the additive `κ_T·9` T-term, which is family-constant and therefore omitted from every
reported number (its magnitude is used only in the Q3 magnitude assessment). `t_c ≤ t_nc`
holds for every objective below.

| id | (t_nc, t_c, t_tag, t_r) | status | derivation |
|----|--------------------------|--------|-----------|
| **θ_FT** | **(4, 2, 2, 1)** | **PRIMARY** | §2.2 with controlled-Pauli letter = 1 two-qubit gate. Structurally identical to the committed objective O0 — that identity is the *result* of the derivation, not an assumption. |
| S1 | (4, 2, 4, 2) | sensitivity | controlled-Pauli letter costs 2 two-qubit gates (e.g. a compiled CY/CZ wrapper, or an ancilla-mediated controlled-Pauli); Tag/Restore doubled relative to the parity ladders. |
| S2 | (8, 4, 2, 1) | sensitivity | the opposite bound: controlled-Pauli letters half the cost of a parity entangler (measurement-assisted Clifford injection), equivalently frame ladders doubled. |
| S3 | (2, 2, 2, 1) | sensitivity | best-case parity-network sharing between the two outer exponentials of the m = 2 sandwich, so the outer axis is charged once rather than twice. |
| O1 | (7, 1, 4, 3) | **control point, not defensible** | QG-2's frozen T-count-weighted objective, bound verbatim for continuity; `derivable_from_ft_accounting: false` per §2.3.1. |

The sensitivity ratios span the defensible range of the *one* free conversion factor and the
*one* genuinely uncertain circuit fact (ladder sharing). No objective in this table may be
added, removed or re-weighted after any QG-21 outcome is seen.

## 3. Frozen domains (complete; sizes recorded, no silent truncation)

- **D1 — receipted chemistry (complete).** Both committed subjects via `r6f._frozen_batch`
  with blob verification: H4 (n = 8) and equilibrium N2 (n = 12), all 15 perfect matchings
  each = **30 rows**. Baseline quadruples bound row-by-row to the committed R6M/R6O/R6Q
  receipts exactly as QG-2 binds them.
- **D2 — QG-3 track-A library chemistry.** The admitted batches of
  `QG3_BOUNDARY_PROSPECTIVE_RESULTS.json` `track_a.admitted_batches`, taken in the frozen
  QG-3 candidate order, capped at **K_ext = 4** subjects (2 × 12-qubit and 2 × 14-qubit
  Benzene batches), all 15 matchings each = **60 rows**. The cap is a disclosed runtime cap
  fixed before any QG-21 outcome (§7), not a selection: the order is QG-3's, and the four
  subjects are its first four. Their baseline quadruples are bound row-by-row to the QG-3
  receipt.
- **D3 — hostile brute-force panels.** The committed QG-2 hostile n = 1 and n = 2 panels,
  under **every** objective of §2.4, DP versus independent brute force over all 32 configs.

The R7 subjects beyond QG-3's four are not opened by this lane; the 16-qubit R7 candidates are
recorded as out of the frozen cap. The protected subject is in no domain and is never read.

## 4. Frozen staging rule (Q2 — prediction before ground truth)

1. **Stage 1 (prediction).** For every row of D1 ∪ D2 and every objective of §2.4, compute the
   objective-independent family primitives (`s*`, `u_d`, `u_p`) and score the committed trade
   families: `C_R6L(ob) = t_tag + t_r·s*`, `C_D+(ob) = min_d [t_tag·d + t_r·u_d]`,
   `f_B′(ob) = t_tag + min_p [t_c·p + t_r·u_p]`. The predicted optimum is the committed
   two-trade identity `Ĉ = min(C_R6L, C_D+, f_B′)` and the predicted regime is the frozen
   trichotomy (DONOR_EXACT / SPLIT / BORROW). `f_B″` (QG-7b weight-2-Tag hybrid) is
   **infeasible at n ≥ 8** (its option tensor is ~10^8 per Tag pair) and is recorded as
   NOT_EVALUATED; since B″ can only lower the family minimum, `Ĉ` is an upper bound on the
   family minimum and any `Ĉ > C_DP` is reported as a prediction failure, never repaired.
   During stage 1 the exact referee is **structurally unavailable**: `dp_cost_pairs_ob`,
   `dp_cost_n2_ob`, `dp_config_cost_ob`, `dp_witness_ob` and `dxx_cost_ob` are replaced by
   stubs that raise, and a counter records that zero referee calls occurred.
2. **Stamp.** The staged predictions are serialized to
   `research/extensions/orion-qg/QG21_STAGE1_PREDICTIONS.json` and digested
   (sha256 of canonical sorted JSON). The digest is printed as the **first stdout line**
   (`ORIONQG_QG21_STAGE1_DIGEST=<sha256>`) before the referee is restored.
3. **Stage 2 (referee).** The referee is restored and `C_DP(ob)` computed for every row and
   objective by the committed objective-parameterized DP. Per row and objective the run
   reports donor cost `C_R6L`, predicted optimum `Ĉ`, referee optimum `C_DP`, the strict
   improvement `Δ = C_R6L − C_DP`, and whether prediction matched ground truth.
4. **Stage 3 (artifact, Q3).** For every row with `Δ > 0` under any objective, the improved
   compilation is serialized verbatim from the DP backtrack: relative permutations, centrals,
   the three frames `R_{j,k}`, the shared Tag `S`, per-frame supports, factored Restore units,
   and an in-run independent cost recomputation from the witness.

## 5. Frozen terminals

- `QG21_REAL_CHEMISTRY_STRICTLY_IMPROVED_UNDER_FT_OBJECTIVE` — ≥ 1 referee-confirmed strict
  improvement on a real subject **under θ_FT or a §2.4 sensitivity objective**, predicted
  before ground truth. Improvements found only at the O1 control point do **not** reach this
  terminal and are reported as control-point observations.
- `QG21_NO_IMPROVEMENT__CHEMISTRY_DONOR_EXACT_UNDER_FT_OBJECTIVE` — every real row is
  donor-exact under θ_FT and every sensitivity objective.
- `QG21_OBJECTIVE_NOT_DEFENSIBLE` — the Q1 accounting fails to support any fault-tolerant
  objective at all.
- `QG21_CANNOT_CHECK` — a gate fails, a domain is unreachable, or the referee cannot run.

A mixed outcome (donor-exact under θ_FT, improvement under some sensitivity objective) reaches
the first terminal and must state exactly which objectives improve.

## 6. Frozen hostile gates (failure aborts or forces `QG21_CANNOT_CHECK`)

1. `stage1_referee_calls == 0` and the stage-1 stub was installed (structural, not a promise).
2. Stage-1 digest recomputed from the on-disk staging artifact equals the printed digest.
3. Every row's baseline `(C_DP, C_R6L, C_D+, f_B)` at (4,2,2,1) equals the committed
   R6M/R6O/R6Q receipt (D1) or the QG-3 track-A receipt (D2), exactly.
4. QG-2 binding: the QG-21 objective evaluator reproduces
   `QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json` chemistry rows under O0 and O1 on all 30 D1 rows
   (`C_DP`, `C_R6L`, `C_Dplus`, `f_B`), and QG-2's headline
   `objectives.O1.chemistry_donor_exact_count` is re-derived.
5. D3: parameterized DP equals the independent parameterized brute force on every hostile
   panel, every config, **every objective** of §2.4.
6. Sandwich `C_DP ≤ C_D+ ≤ C_R6L` and borrow soundness `C_DP ≤ f_B′` on every row and
   objective.
7. `ROTATIONS_R6M == 9` asserted (premise of the §2.3.2 reduction lemma).
8. The protected path is never opened: an audited `open` guard raises on any access to it, and
   `reserved_stretched_n2_accessed: false` is recorded.
9. Every claimed strict improvement is recomputed independently from its serialized witness by
   the in-run recompute *and* by `development/orion-qg-regime-geometry/qg21_generic_verify.py`,
   a from-primitives verifier that imports **no** QG-21 or QG-2 analyzer code and re-derives
   the donor cost, the witness cost, the grammar constraints and the staging digest, emitting
   ACCEPT/REJECT.
10. Domain sizes recorded exactly; any row that fails to load aborts the run.

## 7. Determinism, runtime, receipts

Single deterministic run, no RNG. Runtime cap **< 25 minutes** per run on the session venv
python, excluding the one-time pinned DUCC tree fetch used by D2 (a network clone into the
`ORIONQ_R6R_CACHE` directory; pre-warmed exactly as R7's execution record did). K_ext = 4 was
fixed from timing probes that recomputed **only receipted O0 values** on the D2 subjects; no
non-baseline chemistry outcome was computed before this protocol was frozen. Outputs:
`research/extensions/orion-qg/QG21_FT_CHEMISTRY_RESULTS.json` (indent 2, sorted keys),
`research/extensions/orion-qg/QG21_STAGE1_PREDICTIONS.json`, and two stdout receipt lines —
the stage-1 digest first, and the canonical token
`ORIONQG_QG21_FT_CHEMISTRY=<canonical sorted JSON>` last. Runtime goes to stderr only, so a
double run is byte-identical in stdout and in both artifacts; the run is executed twice and
compared before the receipt is accepted.

## 8. Honesty constraints

θ_FT and the sensitivity set are frozen by this document and may **not** be tuned after any
outcome is seen; that single move would make the lane worthless. The §2.3.2 reduction lemma is
disclosed in advance precisely because it makes the primary-objective outcome on D1 entailed
rather than discovered. Improvement magnitudes are reported in the physically meaningful unit
implied by §2.2 — two-qubit Clifford gates against a family-constant backdrop of nine
arbitrary-angle rotations (≈ 9·κ_T, i.e. several hundred T gates or nine magic states per
compilation) — and the report must state plainly whether an improvement is large or negligible
in that unit. No physical quantum-advantage claim, no novelty credit, no R6 authority.
