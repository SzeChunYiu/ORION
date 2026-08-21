# Exact Expressivity of Shared-Tag TARE Compilations: Donor Optimality, Two Coupling Trades, and Support-Two Sufficiency

Manuscript V1 — 2026-08-21. Branch `claude/orion-harness-verification-b17qdj`.
Every number in this manuscript is transcribed from a committed receipt or frozen
protocol; the receipt path is cited inline at first use. Receipt paths are relative
to the repository root. Nothing here carries R6 (compiled-resource novelty)
authority; the authority strings of all cited receipts contain `NOT_R6` or an
equivalent bounded-authority marker.

---

## Abstract

The TARE (Tag-and-Restore) block-encoding primitive of Schillo, Sturm and Quay
(arXiv:2601.05740) compiles linear combinations of Pauli strings without ancilla
state preparation, leaving free choices of auxiliary anticommuting frames, control
labels, Tag generators, Restore strings and target assignment. We give an exact,
witness-carrying expressivity map of the joint optimization family over shared-Tag
TARE compilations under a frozen support-count objective. (i) A support-dominance
exchange inequality — each unit of auxiliary-frame support costs at least its
maximum achievable Restore/factor saving — is machine-verified with zero violations
over 688,041,472 exhaustively enumerated local configurations. (ii) The weight-one
donor family is nevertheless not closed: two minimal, exactly verified coupling
trades break every weight-one family — Tag-anchor splitting, in which a weight-two
Y⊗Y shared Tag beats every common-anchor compilation (cost 8 versus 9), and a
frame-for-Tag borrow, in which a weight-two frame Pauli placed on the cheap central
multiplier purchases a weight-one Tag (cost ledger 0+0+2+2+1 = 5, versus 6 for the
best weight-one family member). (iii) Support two suffices: the donor family
enlarged to frames of global support at most 2 reproduces the unrestricted exact
dynamic-programming optimum on every verified domain — exhaustively at n=1 (4096
instances) and on the structured n=2 slice (9261 instances), on a 240-instance
seeded random panel at n=2–3, and on all 30 recorded chemistry matchings — closing all 559
previously critical instances witness-by-witness. (iv) A decidable structural
predicate, computable from the six target Paulis with no DP call, classifies
donor-exact instances with zero error on 9771 instances across four panels.
(v) On real DUCC Hamiltonian six-term batches (H4 and equilibrium N2) the
weight-one donor family is exactly optimal, and the predicate explains why rather
than merely observing it. The applied side is grounded by a split-TARE
coefficient-majorization theorem (0 failures in 8700 exhaustive partition
evaluations) and an implementation-aware compiler positive on a blob-locked public
H2O Hamiltonian. All results are bounded to frozen finite domains; every number
replays deterministically from committed receipts; refutations are reported as
results; the all-n composition theorem is stated as open.

---

## 1. Introduction

Block-encoding a linear combination of Pauli strings is a basic subroutine of
quantum simulation. The TARE primitive (Schillo–Sturm–Quay, arXiv:2601.05740)
replaces ancilla state preparation with a Tag-and-Restore construction: a batch of
target Pauli strings is carried by a freely chosen mutually anticommuting auxiliary
frame, a Tag operator marks control branches, and Restore strings repair each
target from its frame representative. The donor construction deliberately leaves
open a large joint design space — which anticommuting frame to use, how to assign
targets to frame elements, which Tag generators to take, and where to place the
cheap central axis of the anticommuting-rotation (Uanti) cascade.

The donor literature treats this space as a heuristic search space: it observes
that auxiliary choices and target matches affect circuit cost, and optimizes them
locally. The question this paper answers exactly, on frozen finite domains, is the
**compilation-family question**: for a fixed batch grammar and a fixed structural
cost objective, *which restricted compilation families achieve the unrestricted
joint optimum, on which instances, and why?*

Concretely, we study shared-Tag TARE compilations of six-term batches under a
frozen support-count objective, and characterize the expressivity gap between the
natural donor family (weight-one frames, weight-one shared Tag — the family the
donor construction actually produces) and the unrestricted exact optimum computed
by proof-carrying dynamic programming. The answer has four parts, all
witness-carrying:

1. a machine-verified **support-dominance inequality** explaining why exact optima
   concentrate on minimal-support frames (Section 3.1);
2. **two — and on all verified domains only two — coupling trades** that break
   weight-one families, each exhibited by a minimal explicit counterexample
   (Sections 3.2, 3.3);
3. a **support-two sufficiency** result: admitting frames of global support ≤ 2
   restores exact family closure on every verified domain (Section 3.4);
4. an **exact decidable regime predicate** separating donor-exact instances from
   the two trade regimes with zero error on all verified panels, which in
   particular explains the observed exact donor optimality on real chemistry
   batches (Sections 3.5, 3.6).

Everything upstream of this expressivity map is donor-owned and is credited as
such (Section 6): the TARE primitive, shared-Tag circuit identity, Restore
factoring, anticommuting unitary partitioning, and Clifford/symplectic synthesis
are all absorbed with zero novelty credit, per the frozen hostile novelty search
of 2026-08-20
(`development/orion-q-max-r0/MAX_R6_EXACT_TARE3_FINAL_HOSTILE_NOVELTY_FREEZE.md`).
What is claimed as new is the exact expressivity map itself: the dominance
inequality, the minimal counterexamples for both trades, the proven-sufficient
support bound on verified domains, and the exact regime predicate — none of which
exists in the donor literature.

A methodological note: this study was produced under a receipts-first discipline.
Every protocol was frozen before its outcome; refuted hypotheses (Sections 3.2 and
3.3 each refute a frozen closure hypothesis) are reported with the same prominence
as confirmations; and every quantitative claim below cites the committed receipt
that replays it.

## 2. Setting and frozen definitions

### 2.1 Instances, encoding, subjects

Local Pauli letters are coded `0=I, 1=X, 2=Y, 3=Z`; n-qubit Paulis are serialized
in receipts as `(x, z)` bit-integer pairs, bit q addressing qubit q. All algebra
(products, symplectic form, weights) is the frozen `local_mul`/`local_symp`/
`local_wt` stack of `research/extensions/orion-q/max_r4d_h2o_ducc_confirmation.py`
(`development/orion-q-max-r0/MAX_R6N_SUPPORT_DOMINANCE_PROTOCOL.md`, "Frozen lemma
statements"). `w(·)` denotes support (number of non-identity letters).

An **instance** of the three-block grammar is six non-identity target Paulis on n
qubits grouped by a perfect matching into three ordered blocks A, B, C with target
pairs `(P_j0, P_j1)`. The two chemistry subjects are frozen six-term DUCC
Hamiltonian batches: H4 (n=8 qubits, term indices {12,18,22,25,27,31}) and
equilibrium N2 (n=12 qubits, term indices {0,7,11,24,31,32}), each with all 15
perfect matchings recorded
(`research/extensions/orion-q/MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json`;
matchings and indices also transcribed in
`research/extensions/orion-q/MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json`,
`frozen_subject_equality`). Subjects are loaded only through a source-blob-verified
frozen batch path; a protected stretched-N2 discriminator subject is never read
(gate `no_new_subject_data`/`reserved_stretched_n2_accessed: false` in every cited
receipt).

### 2.2 The two frozen grammars and the objective

**R6M grammar (three-block TARE-M2, shared one-bit Tag, factored Restore).** A
configuration assigns to each block j an ordered pair of anticommuting frame
Paulis `(R_j0, R_j1)`, a target permutation `π_j ∈ {0,1}`, and a central-branch
bit `c_j ∈ {0,1}`; globally, a shared Tag Pauli S with a common label orientation
`(l0, l1) ∈ {(0,1),(1,0)}` such that `⟨S, R_j0⟩ = l0`, `⟨S, R_j1⟩ = l1` for all j
(labels equal across blocks, distinct across branches). Restore strings are
`T_jk = P_{j,π_j(k)} · R_jk`. The frozen raw support-count objective is

```
C = Σ_j Uanti_j + 2 w(S) + Σ_{k∈{0,1}} F3(T_Ak, T_Bk, T_Ck)
```

with `Uanti_j = 4 (w(R_{j,nc}) − 1) + 2 (w(R_{j,c}) − 1)` (non-central branch
multiplier 4, central multiplier 2) and F3 the donor-owned all-three Restore
common-factor rule: per qubit, 1 if all three local letters are equal and
non-identity, else the sum of the three local weights
(`development/orion-q-max-r0/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_PROTOCOL.md`,
"Frozen D++ definition"; identical to the R6M DP objective). The unrestricted
exact optimum `C_DP` is computed by the frozen proof-carrying DP
`max_r6m_exact_three_tare2_shared_factor_dp.py`, whose exactness was itself
hostile-verified against an independent global brute-force enumerator
(`MAX_R6M_..._RESULTS.json`, gate `hostile_dp_vs_brute_exact: true`).

**R6I grammar (two-block rank-2 dependent TARE-3, shared two-bit Tag).** Two
blocks of three targets each; per block, frame Paulis `(R_0, R_1)` with dependent
third element `R_2 = R_0 R_1`; central choice `c ∈ {0,1,2}` gives multipliers
`(4,4,4)` with `m_c = 2`; shared Tag pair `(S_0, S_1)` costed at `2(w(S_0)+w(S_1))`;
plain (unfactored) Restore support. Objective
`C_SHARED = C_Uanti(A) + C_Uanti(B) + 2(w(S0)+w(S1)) + Σ_k w(T_Ak) + Σ_k w(T_Bk)`
(`research/extensions/orion-q/MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_RESULTS.json`,
`objective` field).

### 2.3 The compilation families

- **R6L (weight-one donor family, "D").** Three weight-one anticommuting frame
  letter pairs at a *common* anchor qubit, one shared weight-one Tag, both target
  permutations per block, donor-owned factored Restore. This is the family the
  donor construction produces; cost `C_R6L`
  (`development/orion-q-max-r0/MAX_R6N_SUPPORT_DOMINANCE_PROTOCOL.md`,
  "Weight-one-restricted families").
- **D+ (anchor-split enlargement).** Weight-one frames with *arbitrary per-block
  anchor qubits*, common label orientation, and the unique minimum-weight shared
  Tag (the forced letter at each distinct anchor, identity elsewhere;
  `w(S) = #distinct anchors`); cost `C_D+`. Tag minimality is machine-verified
  both locally (24 forced-letter cases) and by a full n=2 brute force over
  3456 combinations × 256 two-qubit Paulis
  (`research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`,
  `tag_minimality`).
- **D++ (support-two enlargement).** Frames whose six frame Paulis are nonzero
  with *global support ≤ 2* (arbitrary support sets), per-block central bit (now
  cost-relevant), minimum-weight shared Tag via an exact Tag-relaxation identity;
  cost `C_Dxx`
  (`research/extensions/orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json`,
  `dxx_definition`).
- **B(t) (borrow family, used by the predicate).** Weight-one Tag `S = v@q_t`;
  each block either anchored at `q_t` (extra cost 0) or "phantom" with frames
  `(m0@q_h, l@q_t · m1@q_h)`, `q_h` in the block's own target support, l
  anticommuting with v (extra cost +2, a weight-two frame on the central branch);
  minimum cost `f_B(t)`
  (`development/orion-q-max-r0/MAX_R6Q_REGIME_PREDICATE_PROTOCOL.md`, Section 3).

All memberships are proper, giving the hard containment sandwich, asserted
per-instance wherever both sides are computed:

```
C_DP ≤ C_Dxx ≤ C_D+ ≤ C_R6L        and        C_DP ≤ f_B
```

(`MAX_R6P_..._RESULTS.json`, `dxx_definition.containments`;
`MAX_R6Q_..._PROTOCOL.md`, Section 7).

## 3. Results

All results are stated with their exact verified domains. "Machine-verified
lemma" means: exhaustively checked on the stated finite domain with zero
violations, every violating configuration to be serialized verbatim (none exist).
"Machine-evidenced" means: verified on the stated finite instance panels, not
proven for all n.

### 3.1 The support-dominance exchange inequality

**Lemma 1 (support dominance; machine-verified on its full local domain).**
*Within the frozen TARE frame-grammar families and support-count objectives, each
unit of frame support costs at least 2 (central branch) or 4 (non-central branch)
in the raw Uanti term, while its maximum achievable savings in the Restore/factor
terms is at most 2 per unit; hence removing frame support never increases
structural cost faster than it releases Uanti cost.*
(`MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json`, `lemma.statement`;
protocol `MAX_R6N_SUPPORT_DOMINANCE_PROTOCOL.md`.)

Verified components, all with **zero violations over 688,041,472 local
configurations** (`MAX_R6N_..._RESULTS.json`, `local_verification`):

| Component | Domain | Configurations | Violations | Max savings/cost |
|---|---|---|---|---|
| Lemma N-M (per-qubit, R6M grammar) | 4^6 frames × 4 tags × 8 centrals × 4^6 targets | 536,870,912 | 0 | 1.000 |
| Lemma N-M′ (letterwise exchange monotonicity, F3 rule) | 343 letterwise pairs × 64 targets × 8 multiplier triples | 175,616 | 0 | — |
| Lemma N-I (per-qubit, R6I rank-2 grammar) | 4^4 frames × 16 tag pairs × 9 centrals × 4^6 targets | 150,994,944 | 0 | 0.333 |

The lemma has a **declared gap**, frozen before the outcome: truncating frames to
their anchors changes the Tag syndromes, and the repaired minimum-weight Tag can
cost more than the original spread-frame Tag; this Tag-repair coupling is not
bounded by the local inequalities (`MAX_R6N_..._RESULTS.json`,
`lemma.declared_gap`). The joint weight-one closure is therefore a separate,
finite-domain question — and it is exactly at this declared gap that the closure
fails (Section 3.2).

Consequences on the R6I grammar side: the weight-one closure of the R6I two-block
rank-2 grammar *survives* every joint check — equality of the unrestricted exact
DP with the weight-one-restricted optimum on all 20 recorded subject partitions
(10 × H4, values 15–16; 10 × N2, values 14–15) and all 7 synthetic panels
(`MAX_R6N_..._RESULTS.json`, `frozen_subject_equality.r6i`,
`synthetic_panels.r6i`; gate `r6i_weight_one_equality_on_frozen_subjects: true`).
Lemma 1 thereby *explains* the empirical collapses of three exact-DP campaigns
onto weight-one donor families: R6I, R6K and R6M all returned negatives —
unrestricted joint optimization added nothing beyond the weight-one donor family
on both open subjects
(`MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_RESULTS.json`, authority
`...DP_NEGATIVE__NOT_R6`;
`MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_RESULTS.json`, authority
`...DP_NEGATIVE__NOT_R6`;
`MAX_R6M_..._RESULTS.json`, responsibility
`RESP:RESIDUAL_COUPLED_OPTIMIZATION_ADDS_NOTHING_BEYOND_R6L_DONOR`). The
weight-one donor family itself was a *positive* absorption: it beat the prior
incumbent stack at 9 rotations versus 10 and set the donor cost floors H4 = 8,
N2 = 9 (`MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_RESULTS.json`,
`rotation_counts`, `donor_floor_after_r6l_absorption`).

### 3.2 Trade regime I: Tag-anchor splitting (weight-one closure refuted)

The R6N audit's joint gate failed — as the protocol's honest outcome space
anticipated — at exactly the declared Tag-repair gap, producing the first trade
regime (`MAX_R6N_..._RESULTS.json`, authority
`MAX_R6N_SUPPORT_DOMINANCE_REFUTED__NEW_REGIME_FOUND__NOT_R6`).

**Result 2 (minimal Tag-anchor counterexample, exact).** On the frozen synthetic
n=2 instance `n2_b` of the R6M grammar, with target pairs (decoded from the frozen
`_HOSTILE_N2_PANELS` table of
`research/extensions/orion-q/max_r6m_exact_three_tare2_shared_factor_dp.py`,
codes A=((3,1),(1,3)), B=((2,3),(3,2)), C=((1,0),(2,2))):

```
A: ( Y⊗X , Y⊗Z )     B: ( Z⊗Y , X⊗Y )     C: ( X⊗I , I⊗Y )
```

the unrestricted exact DP optimum is **8** while the weight-one donor family
optimum is **9** (`MAX_R6N_..._RESULTS.json`,
`discovery.joint_gaps_unrestricted_beats_weight_one`: `C_unrestricted_dp: 8`,
`C_weight_one_restricted: 9`). The DP witness uses *weight-one frames only*
(`dp_witness_max_frame_weight: 1`) but a *weight-two shared Tag*
(`dp_witness_tag_weight: 2`): block A anchors at qubit 0 and blocks B and C at
qubit 1, with shared Tag **Y⊗Y** — inexpressible in the R6L grammar, whose shared
weight-one Tag forces a common anchor qubit
(`development/orion-q-max-r0/MAX_R6O_ENLARGED_TAG_DONOR_PROTOCOL.md`,
"Scientific question"). An explicit realization at cost 8 is recorded as the D+
witness: A = (Y,Z)@q0, B = (Y,X)@q1, C = (Y,Z)@q1 (C with swapped targets),
labels (0,1), S = Y⊗Y of weight 2
(`MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`, `domains.r6n_panels`, row `n2_b`,
`dplus_witness`).

The diagnostic column `C_weight_one_frames_any_tag_diagnostic = 8` equals the
unrestricted DP, locating the broken mechanism precisely: *frame* support
dominance survives (consistent with Lemma 1); what fails is only the coupling of
the shared Tag to the frame anchors (`MAX_R6N_..._RESULTS.json`,
`discovery.characterization`). This trade costs `2·Δw(S) = 2` extra in Tag
support to buy ≥ 3 units of Restore-alignment savings on this instance.

### 3.3 Trade regime II: the frame-for-Tag borrow at the central multiplier (D+ closure refuted)

The natural repair — the enlarged family D+, which admits arbitrary per-block
anchors with the unique minimum-weight spread Tag — closes the n2_b gap and all of
n=1 exhaustively (4096/4096 equal), but is itself refuted on larger panels: on
**486 of 9261** exhaustive structured-n2 instances and **73 of 240** seeded random
instances (seed 20260821, n=2–3), the unrestricted DP is strictly below D+
(`MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`, authority
`MAX_R6O_ENLARGED_TAG_DONOR_CLOSURE_REFUTED__SECOND_NEW_REGIME_FOUND__NOT_R6`;
`domains.structured_n2.equal_count: 8775`, `domains.random_panel.equal_count: 167`).
Every observed gap is 1 or 2 support units
(`MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_PROTOCOL.md`, preamble).

**Result 3 (minimal borrow counterexample, exact, with cost ledger).** The
smallest counterexample is structured-n2 `instance_index 16`, targets (codes
`[[1,0],[1,0]], [[1,0],[1,0]], [[2,0],[2,2]]`):

```
A: ( X@q0 , X@q0 )     B: ( X@q0 , X@q0 )     C: ( X@q1 , Y@q1 )
```

with `C_DP = 5 < C_D+ = 6`
(`MAX_R6O_..._RESULTS.json`, `discovery.instances_with_dp_strictly_below_dplus[0]`).
The optimal witness (recorded and re-verified in
`MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json`,
`domains.structured_n2.critical_witness_samples[0]`) is: blocks A, B take
weight-one frames (X@q0, Z@q0); block C takes R_C0 = X@q1 (weight one,
non-central) and **R_C1 = Y⊗Y (weight two, placed on the central branch)**;
shared Tag S = X@q0 of weight one; labels (0,1). Its cost ledger is

```
Uanti(A) + Uanti(B) + Uanti(C) + 2·w(S) + F3(branch0) + F3(branch1)
   0     +    0     +    2     +   2    +      0      +      1       = 5
```

— the weight-two central frame pays `2·(2−1) = 2`, the Tag stays at weight one
(cost 2), branch-0 Restores are all identity (cost 0), and all three branch-1
Restores align to the common letter Y at qubit 0, which the donor-owned F3 factor
rule prices at 1. The mechanism, characterized before R6P was run: the DP
*spends a weight-2 frame Pauli at the cheap central multiplier to compress the
shared Tag to weight one and improve Restore-factor alignment*
(`MAX_R6P_..._PROTOCOL.md`, preamble). Block C's targets live on qubit 1 only;
anchoring C at qubit 1 would force Tag support there (weight-2 spread Tag,
cost 4), while the borrow buys the label constraint at the existing Tag qubit
for +2 Uanti.

The two regimes are distinct currencies of one coupling: regime I spends Tag
support to relax anchor agreement; regime II spends central-branch frame support
to avoid spending Tag support.

### 3.4 Support-two sufficiency

**Result 4 (D++ closure on all verified domains; machine-evidenced).** The
further-enlarged donor family D++ (frames of global support ≤ 2, minimum-weight
shared Tag, per-block central choice, donor-owned factoring) satisfies
`C_DP = C_Dxx` on **every instance of every verified domain**
(`MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json`, authority
`MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_VERIFIED__FAMILY_CLOSURE_RESTORED_AT_SUPPORT_TWO_ON_VERIFIED_DOMAINS__NOT_R6`):

| Domain | Instances | Equal | Receipt field |
|---|---|---|---|
| Exhaustive n=1 (all ordered target 6-tuples) | 4096 | 4096 | `domains.exhaustive_n1` |
| Exhaustive structured n=2 (all 21³ weight-one pair triples) | 9261 | 9261 | `domains.structured_n2` |
| Seeded random panel (seed 20260821; 120 × n=2, 120 × n=3) | 240 | 240 | `domains.random_panel` |
| R6N synthetic panels (incl. the refuting `n2_b`) | 5 | 5 | `domains.r6n_panels` |
| Chemistry matchings (H4, N2; exact containment pinch) | 30 | 30 | `domains.chemistry` |

In particular **all 559 critical instances** (486 structured + 73 random — the
complete set on which D+ failed) are closed at weight two, each with a
re-verified explicit D++ witness (frozen factored-Restore machinery with exact
phases, Tag-minimality brute force over all 4^n Paulis, recomputed cost equality;
`critical_set_summary.all_critical_closed: true`,
`gates.critical_set_closed_at_weight_two: true`,
`gates.witness_reverification_pass: true`). The critical set was cross-checked
row-by-row against the committed R6O receipt
(`gates.critical_set_receipt_crosscheck: true`). At chemistry scale the direct
D++ sweep is infeasible and was prespecified as not run; there `C_Dxx` is fixed by
the exact containment pinch `C_DP ≤ C_Dxx ≤ C_D+` with equal recorded endpoints —
a quadruple tie `C_DP = C_Dxx = C_D+ = C_R6L` on all 30 matchings
(`domains.chemistry.all_quadruple_tie: true`).

Support dominance (Lemma 1) *motivates* this closure — support beyond weight two
should never strictly pay once the observed trade currency is admitted — but does
not prove it; the coupling term remains analytically unbounded and the closure is
empirical family enlargement on frozen domains
(`MAX_R6P_..._RESULTS.json`, `claim_boundary.machine_evidenced_only`). A
counterexample requiring frame support ≥ 3 would be a third regime; none was
found on any verified domain.

### 3.5 The exact regime predicate

**Result 5 (decidable donor-exactness predicate; machine-evidenced, zero error).**
Define `donor_exact := (C_DP = C_R6L)`. The following predicate, frozen before
any panel label was computed and computable from the six targets alone with no DP
call, decides donor-exactness with zero classification error on every verified
panel (`MAX_R6Q_REGIME_PREDICATE_RESULTS.json`, `outcome:
EXACT_PREDICATE_FOUND`, quoted verbatim from `predicate.statement_formal`):

> `P(t) := [C_R6L(t) == C_Dplus(t)] AND [f_B(t) >= C_R6L(t)]`, with `C_R6L`,
> `C_Dplus` the frozen closed-form family minima and `f_B` the frozen
> borrow-family minimum defined in the protocol; all three are bounded explicit
> minimizations over target-derived letter choices; no DP is invoked.

In prose: an instance is donor-exact iff *neither trade is profitable* — anchor
splitting gains nothing (`Gsplit := C_R6L − C_D+ = 0`, regime I unprofitable) and
no borrow-family member beats the donor (`f_B ≥ C_R6L`, regime II unprofitable)
(`predicate.statement_prose`). Confusion matrices, all with zero errors
(`selected_confusion`):

| Panel | Instances | Donor-exact | Split regime | Borrow regime | Errors |
|---|---|---|---|---|---|
| Training: exhaustive structured n=2 | 9261 | 6453 | 2322 | 486 | 0 |
| Held-out random, seed 20260821 | 240 | 140 | 27 | 73 | 0 |
| Held-out random, seed 20260822 (generated after freeze) | 240 | 153 | 26 | 61 | 0 |
| Chemistry (30 matchings, H4 + N2) | 30 | 30 | 0 | 0 | 0 |

Two structural facts sharpen this. First, the single-clause ablation `P0 :=
(Gsplit = 0)` mis-classifies 486/66/49 instances on the three non-chemistry
panels (`panels.*.confusion.P0`) — the borrow clause is necessary, i.e. the two
regimes are genuinely distinct. Second, the **two-trade completeness identity**
`C_DP = min(C_R6L, C_D+, f_B)` holds on *every* instance of every panel
(`identity_two_trade_count` = 9261, 240, 240, 30 = the full panel sizes): on all
verified domains, the unrestricted exact optimum is realized by the donor family
or one of the two elementary trades — there is no third mechanism. This identity
is a theorem *candidate*; as recorded it is machine evidence on finite domains,
reported as a diagnostic, not a gate (`MAX_R6Q_..._PROTOCOL.md`, Section 4).

### 3.6 Chemistry: donor exactness explained

On the real DUCC six-term batches the exact DP campaigns returned equality with
the weight-one donor family on all 30 recorded matchings — H4 costs 8 or 11, N2
costs 9 or 10 per matching (`MAX_R6Q_..._RESULTS.json`, `panels.chemistry.rows`;
originally `MAX_R6M_..._RESULTS.json`, re-verified in R6N/R6O/R6P). Result 5
upgrades this from observation to explanation: every chemistry matching satisfies
`Gsplit = 0` and `f_B ≥ C_R6L` — the predicate holds, both trades are structurally
unprofitable, and donor exactness follows
(`gates.chemistry_all_predicted_donor_exact: true`,
`chemistry_all_truth_donor_exact: true`). The trade regimes are not exotic —
they cover 30% of the structured n=2 panel — but the chemistry batches' target
geometry (shared-support structure across the three blocks) puts all 30 recorded
matchings in the donor-exact regime. The weight-one donor family the TARE
construction naturally produces is, on these subjects and this objective, exactly
optimal — and we can certify that from the targets alone, without running the DP.

## 4. Applied grounding

Two receipts anchor the frozen support-count objective to applied compilation.

**R4B (split-TARE coefficient majorization theorem).** For split TARE with an
outer LCU over blocks, the equal-size sorted-contiguous coefficient partition
minimizes the outer-LCU subnormalization; proved by majorization and verified by
exhaustive deterministic check with **0 failures over 8700 partition evaluations**
across four exhaustive regimes (L6/m3: 300; L8/m2: 3150; L8/m4: 1050; L9/m3:
4200) (`research/extensions/orion-q/MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json`,
`exhaustive_checks`, terminal
`R4B_TARE_SPLIT_MAJORISATION_THEOREM_SUPPORTED__COEFFICIENT_COORDINATE_ONLY`). On
the public LiH subject the optimal split achieves subnormalization 0.9009 versus a
random-split mean of 1.1041 (an 18.4% reduction; overhead over the Pauli-L1 floor
0.42%); a 100-subject disordered-Heisenberg panel shows a median 12.4% reduction
versus random splits. Declared hard boundary: the theorem addresses the
coefficient coordinate only; Pauli/Restore structure can trade circuit cost
against the coefficient-optimal subnormalization
(`hard_boundary` field).

**R4D (implementation-aware compiler on a fresh public subject).** On the
blob-locked public H2O/cc-pVTZ DUCC Hamiltonian (repository
`npbauman/DUCC-Hamiltonian-Library`, commit `be306f58...`, blob `5f157e7b...`;
20 qubits, 8082 non-identity Pauli terms), the implementation-aware split-TARE
compiler at a 1% subnormalization tolerance reduces the TARE structural cost
coordinate C from 8078 to 4972 — a **38.45% reduction** — at a normalization
overhead of 9.1×10⁻⁶
(`research/extensions/orion-q/MAX_R4D_H2O_DUCC_CONFIRMATION_RESULTS.json`,
terminal
`R4D_IMPLEMENTATION_AWARE_SPLIT_TARE_COMPILER_SUPPORTED__REAL_PUBLIC_HAMILTONIAN`).
The receipt's non-claim is part of the result: direct anticommuting pairs avoid
TARE Tag/Restore but still have nonzero implementation cost, and the receipt
authorizes no full-circuit claims.

Together these bound the expressivity map's practical reading: the support-count
objective whose optima Sections 3.1–3.6 characterize exactly is the structural
coordinate that the R4B/R4D compilation results optimize on real Hamiltonians.

## 5. Discussion: what is theorem-grade, what is machine-evidenced, what is open

**Theorem-grade on their stated domains.**

- The three local support-dominance inequalities (Lemma 1): exhaustively verified
  over their complete finite domains (688,041,472 configurations, zero
  violations). Within those domains this is proof by finite enumeration.
- Both counterexamples (Results 2 and 3): explicit, re-verified witnesses with
  exact integer costs; a counterexample verified exactly is a theorem that the
  respective closure fails.
- The containment sandwich `C_DP ≤ C_Dxx ≤ C_D+ ≤ C_R6L` and the D+/D++ Tag
  minimality: proved structurally in the frozen protocols and enforced as hard
  runtime assertions on every computed instance.
- The R4B majorization theorem (proof plus 0/8700 deterministic check), on its
  declared coefficient-coordinate scope.

**Machine-evidenced only (finite frozen domains; not theorems for all n).**

- Weight-one closure of the R6I grammar (20 partitions + 7 panels).
- Support-two sufficiency (Result 4): exhaustive at n=1 and on the structured
  n=2 slice, sampled at n=2–3, pinched at chemistry scale. The Tag-repair
  coupling term remains analytically unbounded; the closure is repaired by
  family enlargement, not closed by proof
  (`MAX_R6P_..._RESULTS.json`, `claim_boundary`).
- The regime predicate (Result 5) and the two-trade completeness identity:
  zero error on 9771 classified instances, including a held-out panel generated
  after the predicate was frozen — but the borrow family is a frozen restricted
  enlargement, not a proof of DP-mechanism completeness
  (`MAX_R6Q_..._RESULTS.json`, `claim_boundary.machine_evidenced_only`).
- Chemistry donor exactness (Result 6): 30 recorded matchings on two subjects.

**Open.**

- **The all-n composition theorem**: does `C_DP = C_Dxx` (support-two
  sufficiency) hold for every n and every instance of the frozen grammar? The
  per-qubit inequalities hold for every n; what is missing is an analytic bound
  on the Tag-repair coupling. This is the natural target for a composition
  argument over qubits. **EXECUTED — THEOREM MACHINE-CHECKED**
  (`research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`): for
  every n and every target configuration of the frozen R6M grammar, frame
  Paulis of support ≥ 3 never strictly pay, so D++ equals the unrestricted DP
  unconditionally. The proof is an F₂²-pigeonhole zero-sum-subset exchange
  that never needs Tag repair, reduced to one exhaustive 18,432-case local
  inequality (0 violations) plus a three-line combinatorial lemma (43,688
  class tuples); the lemma's only failing patterns are exactly the four w=2
  configurations realizing the frame-for-Tag trade, so the weight-2 boundary
  is delineated analytically. This upgrades Result 3 (support-two
  sufficiency) to theorem-grade for all n in the R6M grammar. The three-family
  completeness identity and the R6I rank-2 grammar remain domain-bounded.
- **Support-3 necessity**: resolved by the theorem above — no instance at any n
  requires frame support ≥ 3 in the R6M grammar; no third regime exists there.
- **Prospective fresh-subject test — EXECUTED, PREDICTION CONFIRMED**
  (`research/extensions/orion-q/MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json`):
  under a selection rule frozen before any fresh coefficient was read, the
  first eligible subject — Benzene cc-pVDZ FrozenCoreCCSD 6Elec/6Orbs DUCC2
  (12 qubits, 390 Pauli terms, blob `5c02c72b…`) — was admitted on the first
  attempt; the predicate's stage-1 prediction (donor-exact on all 15 matchings,
  exact costs 9×9 and 6×8) was digest-stamped (`898f49a4…`) before any DP ran,
  and the unrestricted exact DP then confirmed cost and regime on **15/15
  matchings**, with all 14 gates true and byte-identical double runs. Honest
  bound: the fresh subject landed entirely donor-exact, so the split and borrow
  branches were exercised as non-profitability exclusions, not positive regime
  predictions; a boundary-region subject is the named escalation.
- Other objectives (coefficient-weighted, rotation-count trade-offs beyond frozen
  counts), larger Tag ranks, and grammars outside the two frozen families are
  out of scope entirely, not open questions of this paper.

A remark on negatives: Results 2 and 3 are refutations of hypotheses this
programme itself froze (R6N's lemma-closure gate; R6O's D+ closure gate). Both
protocols pre-declared refutation as a fully acceptable outcome and required
verbatim serialization of every violating instance. The two trade regimes — the
paper's most novel objects — were discovered exactly there.

## 6. Related work and novelty subtraction

This section follows the frozen hostile novelty search of 2026-08-20
(`development/orion-q-max-r0/MAX_R6_EXACT_TARE3_FINAL_HOSTILE_NOVELTY_FREEZE.md`),
which was performed hostile to naming mismatch (an equivalent optimizer counts as
a donor even under a different name) and is a bounded search statement, not a
claim that all literature is enumerable. Donors own, with zero novelty credit to
this paper:

- **TARE itself** (Schillo–Sturm–Quay, arXiv:2601.05740): the Tag/Restore
  construction and stabilizer formalism, freely chosen mutually anticommuting
  auxiliary families, the 2m−1 Uanti Pauli-exponential construction,
  split/composed handling, and the observation that auxiliary choices and target
  matches affect circuit cost. The weight-one family R6L, and the machinery of
  D+ and D++, are donor-owned; the enlargements are bookkeeping
  (`MAX_R6O_..._RESULTS.json` and `MAX_R6P_..._RESULTS.json`, `claim_boundary`).
- **Anticommuting unitary partitioning** (Izmaylov/Yen/Verteletskyi and related):
  anticommuting grouping, clique construction, the normalized direct
  anticommuting-unitary identity.
- **Clifford/symplectic synthesis** (incl. Rengaswamy–Calderbank–Kadhe–Pfister,
  arXiv:1803.06987): solving and optimizing symplectic constraints and
  Pauli-frame transformations.
- **Global binary-symplectic Pauli compilation** (Symphony, Yang et al.,
  arXiv:2608.11579), **low-ancilla block encodings** (Zhang–Shao,
  arXiv:2607.01843), **second-quantized block encodings** (Liu et al.,
  arXiv:2510.08644), **non-Clifford fusion** (Li et al., arXiv:2510.13573),
  **controlled-evolution sign-flip grouping** (Fujiwara–Yamamoto–Ishikawa,
  arXiv:2606.06070), and FOQCS-LCU outer controls: each holds first right of
  refusal in its own coordinate and jointly blocks any claim of global
  block-encoding or ancilla optimality here.

Dynamic programming as a technique, native matches as an idea, and PREP/SELECT
optimization are likewise anti-credited (freeze document, "Anti-credit rules").

**Residual claimed as new** (donor-subtracted): the exact, witness-carrying
expressivity map of the joint optimization family — the machine-verified
dominance inequality (Lemma 1), the minimal counterexamples for both coupling
trades (Results 2–3), the proven-sufficient-on-verified-domains support bound
(Result 4), and the exact decidable regime predicate with the two-trade
completeness identity (Result 5). The donor literature treats these grammars as
heuristic search spaces; to the bounded search's knowledge no donor exactly
characterizes them. Per the freeze document, the pre-outcome complete-object
donor search returned `NO_LOCATED_DONOR`, and novelty remains conditional on a
fresh hostile re-search dated at submission; if review locates a complete-object
donor, the claim must be narrowed or withdrawn regardless of the receipts.

## 7. Reproducibility

Every quantitative statement in this manuscript replays deterministically from
committed artifacts:

- **Receipts** (all under `research/extensions/orion-q/`):
  `MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json`,
  `MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`,
  `MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json`,
  `MAX_R6Q_REGIME_PREDICATE_RESULTS.json`,
  `MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_RESULTS.json`,
  `MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_RESULTS.json`,
  `MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_RESULTS.json`,
  `MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json`,
  `MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json`,
  `MAX_R4D_H2O_DUCC_CONFIRMATION_RESULTS.json`, with generating modules
  (`max_r6n_support_dominance_audit.py`, `max_r6o_enlarged_tag_donor_closure.py`,
  `max_r6p_weight2_frame_donor_closure.py`, `max_r6q_regime_predicate.py`, etc.)
  alongside them.
- **Frozen protocols** (all under `development/orion-q-max-r0/`), each committed
  before its outcome, each fixing gates, domains, seeds, tie-breaks and the
  honest outcome space including refutation.
- **Receipt index**: the sha256-anchored provenance appendix at
  `papers/Q-paper-02-recursive-recovery/RECEIPT_INDEX.md` covers the
  chain through R6N (40 receipts); the R6O/R6P/R6Q rows are to be appended by the
  same generator at submission.

Determinism properties used throughout: seeded panels
(`numpy.random.default_rng(20260821)`, `20260822`); R6P and R6Q receipts are
byte-identical under double runs up to the single `runtime_seconds` field
(`MAX_R6P_..._PROTOCOL.md`, "Receipt"; `MAX_R6Q_..._PROTOCOL.md`, Section 7);
chemistry sources enter only through blob-verified frozen batch paths; DP
exactness is hostile-verified against independent brute-force enumerators inside
the receipts themselves; and cross-receipt bindings (R6P re-deriving R6O's
critical set row-by-row, R6Q binding H1 to R6O's 240 recorded rows) make the
chain mutually checking. Independent replay of all cited receipts was performed
once this session per the publication plan
(`papers/Q-paper-02-recursive-recovery/PUBLICATION_PLAN.md`, Paper Q1
submission gates) and must be repeated at submission.

## 8. Claim boundary

This paper claims exactly: (a) Lemma 1 on its three exhaustive local domains;
(b) the two trade-regime counterexamples as exact refutations of the weight-one
and D+ closures of the frozen R6M grammar; (c) support-two sufficiency, the
regime predicate, and the two-trade completeness identity as machine evidence on
the frozen finite domains enumerated in Sections 3.4–3.5 (exhaustive n=1 and
structured n=2; seeded n=2–3 panels; 30 recorded chemistry matchings on two
subjects); (d) the R4B theorem on the coefficient coordinate and the R4D
compiler positive on one blob-locked public subject. It does not claim: theorems
for all n; anything about other objectives, rotation-count trade-offs beyond the
frozen counts, larger Tag ranks, or grammars outside the two frozen families;
any full-circuit, hardware, or global block-encoding optimality; any donor-owned
machinery as novel; or any R6 compiled-resource authority. The protected
stretched-N2 subject was never read by any receipt cited here and remains sealed
unless a new pre-outcome freeze releases it for the prospective section. Numbers
not present in the cited receipts do not appear in this manuscript.
