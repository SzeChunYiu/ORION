# MAX-R6Q Regime-Predicate Induction Protocol (frozen before classification outcome)

Status: FROZEN 2026-08-21, before any ground-truth label was computed for any panel
instance under this protocol and before any predicate was evaluated on any panel.
Author lane: ORION-Q max-r0 harness drive (branch claude/orion-harness-verification-b17qdj).
Not R6. No novelty credit. The protected stretched-N2 discriminator is never read.

## 1. Scientific question

R6M established the exact unrestricted joint DP optimum C_DP over the frozen
three-TARE2 shared-Tag / donor-factored grammar. R6L is the weight-one donor
family (three weight-one anticommuting frames at a common anchor qubit, one
weight-one shared Tag): cost C_R6L. R6N discovered the first trade regime
(anchor splitting: weight-2 spread Tag, C_D+ < C_R6L), R6O discovered the second
(Tag-borrow: a weight-2 frame Pauli on the central branch buys the label
anticommutation at the existing Tag qubit, keeping the Tag at weight one and
re-aligning the Restore triple; C_DP < C_D+ on 486/9261 structured-n2 and
73/240 seeded random instances per the committed R6O receipt).

Goal: a decidable predicate P(targets), computable from the six per-block target
Paulis alone with **no DP call**, such that P holds exactly on the instances
where the weight-one-Tag donor family (R6L) is DP-optimal
(donor-exact := C_DP == C_R6L). If exactness is out of reach, a sound sufficient
condition covering all chemistry instances, or an honest negative.

## 2. Provenance of the candidate features (declared before fitting)

The candidate feature set below was designed using ONLY:
(a) the committed receipts MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json (20 verbatim
    structured-n2 violations, 20 verbatim random violations, chemistry rows) and
    MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json (regime characterization), and
(b) analytic derivation from the frozen cost grammar (below).
No ground-truth label of any panel instance was computed before this freeze.

Analytic derivation used for the borrow family (recorded here so the family is
a stated mathematical object, not a fitted artifact). In the frozen grammar a
block's two frames must anticommute with each other, and the two branch labels
against the Tag S must be distinct and common across blocks. For weight-one
frames the pair is forced to share one qubit, and if that qubit carries Tag
support its commuting-branch letter is forced to the Tag letter (the D+ family,
R6O). The minimal enlargement beyond D+ is one branch of weight two. For a
weight-1 Tag S = v@q_t, a block not anchored at q_t ("phantom") is forced to:
- commuting-branch frame m0@q_h with q_h != q_t (any non-identity m0), and
- anticommuting-branch frame l@q_t * m1@q_h with l != v non-identity (2 choices)
  and m1 != m0 non-identity (else the pair fails to anticommute; and q_h inside
  supp(S) is infeasible because the label constraint forces m1 = S[q_h] = m0).
Its uanti cost is exactly +2 (weight-2 frame on the central branch, weight-one
frame non-central). This reproduces the R6O receipt's DP witness mechanism on
its verbatim violations.

## 3. Frozen definitions

Instance: targets t = ((tA0,tA1),(tB0,tB1),(tC0,tC1)), six non-identity Paulis
on n qubits, matched into three ordered blocks. supp_j := supp(t_j0) u supp(t_j1),
U := supp_A u supp_B u supp_C, E := the lowest-index qubit outside U (if any).

Ground-truth labels (committed machinery, imported unmodified):
- C_DP: structured-n2 panel via r6o.dp_cost_n2_reader; random panels via
  r6o.dp_cost_frozen_configs (per-instance _local_table cache clear, as in R6O);
  chemistry via the committed R6M receipt column C_R6M (heavy subject DP is not
  rerun, mirroring R6O).
- C_D+: r6o.dplus_pairs. C_R6L: r6m.donor_r6l_matching on r6m._synthetic_terms
  (panels) / on the frozen chemistry batch (chemistry), receipt-bound.
- donor_exact := (C_DP == C_R6L); regime_split := (C_DP == C_D+ < C_R6L);
  regime_borrow := (C_DP < C_D+).

Frozen feature set (all computed from targets alone; no DP):
1. Gsplit := C_R6L - C_D+ (both are closed-form structural family minima over
   explicitly enumerated weight-one frame/anchor/letter choices; no DP).
2. f_B := minimum cost over the frozen **borrow family** B(t):
   - Tag S = v@q_t, v in {X,Y,Z}, q_t in Q_t := U u {E} (E included only if it
     exists; restricting the Tag qubit to U plus one empty representative is
     lossless for this family by permutation symmetry of empty qubits, since
     all other special qubits below lie in U).
   - Each block j independently chooses:
     (a) anchored at q_t: frames (v@q_t, c@q_t), c in {X,Y,Z}\{v} (2), target
         routing sigma_j in {0,1} (2); extra cost 0; or
     (b) phantom: home q_h in supp_j \ {q_t} (family-definitional restriction
         of the home to the block's own target support), l in the 2 letters
         anticommuting with v, ordered (m0,m1) distinct non-identity (6),
         sigma_j (2); frames (m0@q_h, l@q_t * m1@q_h); extra cost +2.
   - At least one block phantom (zero-phantom configs are exactly R6L at q_t and
     are excluded so that f_B isolates the borrow mechanism).
   - Branch k=0 ("commuting") restore T_j = t_{j,sigma_j} * R_comm; branch k=1
     T_j = t_{j,1-sigma_j} * R_anti; cost = 2 (Tag) + sum_j extra_j + FS_0 + FS_1
     with FS the frozen donor-owned all-three factoring (per qubit: 1 if all
     three letters equal and non-identity, else the sum of local weights; the
     r6m F3 table, binding asserted).
   - Branch orientation (which global branch commutes with S) is cost-symmetric
     in this family and is therefore not enumerated.
   Soundness: every member of B(t) is a valid configuration of the frozen R6M
   grammar, so C_DP <= f_B; asserted per instance wherever C_DP is computed.
3. Simple boolean/counting features (for the fallback ladder and diagnosis):
   s1 := [supp_A n supp_B n supp_C nonempty];
   s2 := [some block's supp_j disjoint from the union of the other two];
   s3 := [some block has t_j0 == t_j1];
   a3 := #{q : exists v != I with every block having >=1 target with letter v at q};
   a2max := max over block pairs of #{q : exists v != I present in both blocks' targets at q}.

## 4. Frozen induction procedure

Fit domain: ONLY the exhaustive structured-n2 panel (all 21^3 = 9261 instances
of unordered pairs over the six weight-one two-qubit Paulis, exactly the R6O
enumeration order).

Candidate predicates, evaluated in this fixed order:
- P1 := (Gsplit == 0) AND (f_B >= C_R6L).
  Prose: "neither splitting the Tag anchors (R6N trade) nor borrowing a single
  Tag-qubit letter on a weight-two central-branch frame (R6O trade) achieves
  cost below the weight-one donor family."
- P0 := (Gsplit == 0) (diagnostic: is the borrow clause necessary?).
- P2 (fallback): exhaustive search over conjunctions of at most 3 literals from
  the frozen literal list {s1, !s1, s2, !s2, s3, !s3, [a3==0], [a3>=1], [a3>=2],
  [a2max==0], [a2max>=1], [a2max>=2], [Gsplit==0], [f_B>=C_R6L]}, ranked by
  (training error, conjunction size, lexicographic literal indices). No other
  model class. Fully deterministic.
Selection rule: P1 if it has zero training error; else P0 if zero; else the best
P2 conjunction. All confusion matrices are reported regardless of selection.

Also reported (theorem-candidate diagnostic, not a gate): the count of training
instances with C_DP == min(C_R6L, C_D+, f_B) ("two-trade completeness identity").

## 5. Frozen held-out tests (all run AFTER the predicate is fixed by Section 4)

- H1: the 240-instance random panel, seed 20260821, regenerated with the exact
  committed R6O sampling code path (numpy default_rng, n in (2,3), 120 each,
  rejection of identity keys, same draw order). Binding gate: every row's
  (C_DP, C_D+, C_R6L) must equal the committed R6O receipt's random_panel rows.
  The final predicate classifies all 240; target zero error, honest report else.
- H2: a NEW random panel, seed 20260822, identical recipe (240 >= 200 instances,
  n = 2..3), generated only after P is fixed. Zero-error target, honest report.
- Chemistry: all 30 recorded chemistry matchings (H4, N2 from the committed R6M
  receipt; C_R6L and C_D+ recomputed and receipt-bound; source blobs verified).
  P must classify every matching donor-exact.

## 6. Frozen outcome space

- EXACT_PREDICATE_FOUND: the selected predicate has zero classification error on
  the training panel, H1, H2, and chemistry (all 30 classified donor-exact and
  ground-truth donor-exact). The claim is machine-evidenced on these finite
  domains only; it is NOT a theorem for all n.
- SUFFICIENT_CONDITION_ONLY: not exact, but the selected predicate has zero
  false positives on every panel (P true implies donor-exact everywhere tested),
  P is true on all 30 chemistry matchings, and every instance labeled
  regime_split or regime_borrow is classified non-donor-exact. Coverage
  (recall on donor-exact instances, per panel) is reported.
- NO_CLEAN_PREDICATE: otherwise. The best candidate's confusion matrices on all
  panels are reported verbatim.

## 7. Integrity gates (hard assertions)

- Sandwich C_DP <= C_D+ <= C_R6L on every panel instance.
- Borrow soundness C_DP <= f_B on every instance where both are computed.
- F3-table binding between the predicate module's local algebra and r6m._F3.
- H1 full-row binding to the committed R6O receipt (240 rows) and structured-n2
  equal-count binding (8775) plus the 20 verbatim violation rows.
- Chemistry receipt binding (C_R6M, C_R6L, C_Dplus columns; source blobs).
- Authority string contains NOT_R6; reserved stretched-N2 never accessed;
  no committed file modified; deterministic double run (byte-identical RESULTS
  JSON and stdout receipt line; runtime reported on stderr only).

## 8. Runtime and outputs

Single run under 25 minutes with the session venv python. Outputs:
- stdout: ORIONQ_MAX_R6Q_REGIME_PREDICATE=<canonical sorted JSON receipt>.
- research/extensions/orion-q/MAX_R6Q_REGIME_PREDICATE_RESULTS.json (pretty).
- No existing file is modified; only the two new files above plus this protocol.
