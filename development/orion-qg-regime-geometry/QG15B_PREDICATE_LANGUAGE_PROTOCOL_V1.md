# QG-15b predicate-language boundary protocol V1 — StabPrep donor-exact boundary under an enlarged frozen language, with cross-family calibration

Date: 2026-08-21
Parent programme: ORION-QG (PROGRAMME_CHARTER_V1.md, issue #740), wave-2 registered
successor of QG-15 (QG_WAVE2_RECORD.md, "QG-15b — predicate-language boundary").
Branch: `claude/orion-harness-verification-b17qdj`, checked out at `e221190f`.
Status: FROZEN BEFORE ANY QG-15b OUTCOME. No minimum-error value, no cell-purity
verdict, no zero-error achievability verdict, and no calibration number below has been
computed before this freeze. The only pre-freeze computations were engineering
feasibility probes of search-space SIZES (row counts, distinct feature-vector counts,
distinct literal truth-vector counts, per-instance evaluation timings); no label was
joined to any feature vector and no error of any predicate was evaluated.
Authority ceiling: development/research registration of a predicate-complexity
measurement; NOT_R6; no novelty credit, no new subject data, no network access. The
protected stretched-N2 subject is never read. Runtime cap: < 25 minutes per analyzer
run (double run < 50 minutes); all caps disclosed in section 8.

## 1. Scientific question

QG-15 refuted "boundary-is-low-order" for the StabPrep family: within the frozen
10-literal conjunctive ladder, the donor-exact boundary admitted no clean predicate
(best frozen form: 117/1080 training errors; P1 and P2 zero-false-positive on every
panel — receipted in QG15_THIRD_FAMILY_RESULTS.json). QG-15b freezes a strictly larger
predicate language L1 over the SAME feature vocabulary (thresholded literals, negation,
bounded conjunction and disjunction) and measures, by complete search:

- Q1 — is the StabPrep donor-exact boundary exactly expressible in L1 at the frozen
  budget (K=3, D=3)? Terminal branches: `EXACT_PREDICATE_FOUND_IN_L1` (zero training
  error; then the untouched held-out panel is evaluated and generalization reported
  honestly — a held-out failure is first-class) or `L1_INSUFFICIENT` (minimum
  achievable training error recorded).
- Q2 — the receipted predicate-complexity lower bound: the minimal budget (K', D') on
  the frozen lattice at which zero training error first becomes achievable, or the
  receipted proof that none achieves it. A feature-indistinguishability certificate
  (a training cell — a maximal set of instances with identical feature vectors —
  containing both a donor-exact and a trade instance) proves zero error unachievable
  at EVERY budget over this vocabulary, which is stronger than any lattice bound.
  When zero is unachievable, the secondary complexity number is the minimal budget
  attaining the vocabulary floor E_floor (defined in 3.2).
- Q3 — cross-family calibration: the IDENTICAL language and search machinery run on
  the SixLCU incumbent-exact boundary (exhaustive n=2 domain, 38,760 instances,
  committed QG-4 machinery imported unmodified). The pair
  (StabPrep minimal budget, SixLCU minimal budget) is the first quantitative
  measurement of the "boundary-is-low-order" property. Family choice per the lane
  brief: the TARE R6Q/QG-2 slice requires the heavy orion-q DP import chain
  (max_r6m/max_r6o/p10) and is declared not cheaply importable; the brief's explicit
  fallback (SixLCU n=2 via committed QG-4/QG-12 machinery) is taken. Recorded here
  pre-outcome.

## 2. The frozen language L1

### 2.1 Feature vocabularies (verbatim; no new features)

StabPrep arm — 13 integer features per instance, in this frozen index order. f0-f8 are
QG-15 protocol sections 2.4-2.5 verbatim; f9-f12 are exactly the derived combinations
already frozen inside QG-15's literal list L4-L9 (C_D==LB, C_D<=LB+1, c==n, nCN<=n-1,
C_D<=2n), re-expressed in threshold form so that L1 strictly contains the QG-15 ladder:

- f0 `nCZ`, f1 `nY`, f2 `nSignX`, f3 `nSignZ`, f4 `nCN`, f5 `C_D` (donor trace),
- f6 `r_X`, f7 `c`, f8 `LB` (structural),
- f9 `C_D-LB`, f10 `n-c`, f11 `nCN-(n-1)`, f12 `C_D-2n` (QG-15 literal-derived).

Raw `n` is NOT a feature (it never appears alone in QG-15's vocabulary, only in the
relative forms captured by f10-f12).

SixLCU arm — 11 integer features per instance, the QG-4 stage-4 literal-generating
scalars, frozen index order (QG4_SECOND_FAMILY_PROTOCOL.md / qg4_second_family.py
lines 320-346 verbatim):

- g0 `maxg2`, g1 `best2`, g2 `best3`, g3 `maxg3`, g4 `maxg4`, g5 `maxg5`, g6 `g6`,
- g7 `W`, g8 `wF6` (= wF[63]), g9 `maxwt` (= max_i wt_i), g10 `maxpair`
  (= max over pair masks of wF).

Target labels (verbatim from the parent lanes): StabPrep `donor_exact := (C_opt ==
C_D)`; SixLCU `incumbent_exact := (C_F == C_inc)`.

### 2.2 Threshold grid (frozen finite grid)

For each feature, grid(f) = the sorted set of values attained by f on that arm's
training domain. This is a frozen deterministic RULE fixed before any outcome; it
loses no expressiveness over the training domain: for ⋈ in {==, <=, >=}, any integer
threshold is training-equivalent to an attained threshold or to a constant predicate,
so completeness of the search over this grid is completeness over all integer
thresholds.

### 2.3 Literals, conjunctions, disjunctions, budgets

- Atomic literal: `[f ⋈ t]` with ⋈ in {==, <=, >=}, t in grid(f). The literal set is
  closed under negation: `NOT [f ⋈ t]` is a literal (equivalently ops {!=, >, <}).
- Member of L1(K, D): a disjunction of at most D conjunctions, each a conjunction of
  at most K literals. The empty disjunction (constant FALSE) and constant TRUE
  (tautological literal, e.g. `[f >= min grid value]`) are members of every L1(K, D).
- Q1 language: L1 = L1(K=3, D=3).
- Q2 budget lattice: K in {1, 2, 3}, D in {1, 2, 3, 4, 5, 6}, evaluated K-ascending
  then D-ascending. K=4 is excluded by frozen runtime arithmetic (choose(~300, 4) ≈
  3.6e8 conjunction evaluations exceeds the cap); this lattice truncation is frozen
  here and re-disclosed in RESULTS.
- Training error of a member = number of misclassified training instances (positives =
  the arm's exact label). "Minimal (K', D')": both the set of minimal cells achieving
  the target in the product partial order ((K,D) <= (K',D') iff K<=K' and D<=D') and,
  as the single headline number, the first achieving cell in the total order
  (K+D, K, D) ascending.

### 2.4 Domains

- StabPrep training domain: the union of the QG-15 exhaustive domains n = 1, 2, 3
  (6 + 60 + 1080 = 1,146 instances). Held-out panel: the QG-15 seeded n = 4 panel
  (seed 20260821, 120 states, regenerated by the imported committed `build_panel`),
  never touched during search (section 5).
- SixLCU training domain: the QG-4 exhaustive n=2 domain (38,760 instances,
  `gen_exhaustive_n2`). Cross-check panel (report-only, declared reuse of a domain
  QG-4 already refereed; not a prospective holdout): exhaustive n=1 (729 instances).

## 3. The frozen complete search (no heuristics; all reductions exactness-preserving and receipted)

### 3.1 Cell collapse

Group training instances by their full feature vector ("cells"). Every member of L1
(indeed every function of the features) is constant on each cell. Record: cell count,
per-cell (pos, neg) instance weights, the mixed cells (pos > 0 and neg > 0) verbatim
(capped at 20 rows; count always exact).

### 3.2 Vocabulary floor

delta(cell) = neg - pos. For any predicate phi (any budget):
err(phi) = P_total + sum over cells covered by phi of delta(cell), where P_total =
total positive count. Hence the floor over ALL predicates over this vocabulary is
`E_floor = P_total + sum over cells with delta<0 of delta = sum over cells of
min(pos, neg)`. E_floor > 0 (equivalently: a mixed cell exists) certifies that zero
training error is unachievable at every (K, D) — the grid-independent lower-bound
certificate of Q2.

### 3.3 Literal pool

Evaluate every atomic literal (both polarities) as a truth vector over cells.
Frozen enumeration order: feature index ascending, op in (==, <=, >=), threshold
ascending, plain before negated. Reductions (each with recorded counts):
(R1) constant-true/false literals dropped from the pool (constants are handled
directly: FALSE has err = P_total, TRUE has err = N_total, both always candidate
incumbents); (R2) literals with identical truth vectors deduplicated, keeping the
first in the frozen enumeration order as canonical description.

### 3.4 Conjunction pool per K

Enumerate all conjunctions of 1..K distinct pool literals in lexicographic
index-tuple order (size ascending). Reductions (recorded): (R3) conjunctions with
identical truth vectors deduplicated (first in order kept as description); (R4)
all-false conjunctions dropped; (R5) conjunctions with pot >= 0 dropped, where
pot(v) = sum over cells of v of min(delta, 0): since every marginal contribution of v
to any union is >= pot(v) >= 0, removing v from any disjunction never increases
error, so some optimum avoids such v — exactness preserved; (R6) surviving vectors
deduplicated by their restriction to cells with delta != 0 (delta = 0 cells cannot
affect error). Recorded per K: raw conjunction count, distinct vectors, drops per
reduction, final pool size M_K.

### 3.5 Complete branch-and-bound disjunction search per lattice cell (K, D)

Candidates = the K-pool sorted by (pot ascending, canonical description) — frozen
total order. Incumbent initialization (upper bound only; completeness unaffected,
disclosed): min of constant FALSE (P_total), constant TRUE (N_total), the frozen
greedy seed (up to D steps, each adding the candidate with the most negative marginal,
ties by pool order, stopping when no negative marginal exists), and the (K, D-1)
result for D > 1 (valid since L1(K, D-1) subset of L1(K, D)). Complete DFS over
candidate index-ascending subsets of size <= D; at each node the branch adding
candidate i is pruned iff score(U) + pot(v_i) + (sum of the (depth_left - 1) smallest
pots at indices > i) >= best_score — a valid lower bound because marginals are >=
pots. Search additionally terminates when best reaches E_floor (nothing lower exists).
best_witness updates on every strict improvement (deterministic). Node budget
(deterministic cap, wall-clock never used for control flow): 8,000,000 candidate
expansions per (K, D) cell; on exhaustion the cell is marked `truncated: true` and its
minerr is only an upper bound (any minimality claim touching a truncated cell is
downgraded, see terminals). Recorded per cell: M_K, DFS nodes, truncated flag,
minerr(K, D), witness predicate serialized as a list of conjunctions of literal
descriptions (feature name, op, threshold, negated).

The zero-error question of Q2 is decided by the same machinery: zero achievable at
(K, D) iff minerr(K, D) == 0 (untruncated). Floor attainment: minerr(K, D) == E_floor.

## 4. Prespecified hostile gates

- G1 `qg15_binding`: recomputed donor-exact censuses equal QG-15 RESULTS (5/6, 28/60,
  189/1080); recomputed P0/P1/P2 confusion matrices on n=1, n=2, n=3 equal QG-15
  component4 verbatim; the receipted zero-FP property of P1 and P2 re-verified on
  every panel (n=4 panel included, against QG-15's stored held-out matrices); the 8
  serialized QG-15 minimal witnesses' features (nCZ, nY, nSignX, nSignZ, nCN), C_D,
  LB, r_X, c spot-recomputed from their canonical keys and matched.
- G2 `qg4_binding` (Q3): recomputed P0 confusion on exhaustive n=2 equals QG-4
  stage-4 verbatim (TP,FP,FN,TN = 1,0,0,38759); recomputed positives count equals
  QG-4's coverage record.
- G3 `search_completeness_accounting`: every reduction R1-R6 and every budget cell
  reports exact counts (raw, deduped, dropped, pool, DFS nodes); no pruning exists in
  code beyond R1-R6 and the section-3.5 bound; the section-3.5 bound and R5 are
  exactness-preserving by the recorded arguments.
- G4 `surface_monotonicity`: minerr non-increasing in K at fixed D and in D at fixed
  K, over untruncated cells (a complete search must satisfy this; violation aborts).
- G5 `floor_consistency`: minerr(K, D) >= E_floor on every cell; any zero-error claim
  requires E_floor == 0; every reported witness's serialized predicate re-evaluated
  from its description achieves exactly the claimed error.
- G6 `heldout_discipline`: the StabPrep held-out panel's referee (n=4 Dijkstra) and
  labels are computed only AFTER the stage digest of all selected predicates and the
  full minerr surface is printed to stdout (code-structural flag, as QG-15 G8); the
  search never reads panel data.
- G7 `confusion_completeness`: every reported predicate (the (3,3) winner, every
  minimal-cell witness, and the QG-15 baselines P0/P1/P2) carries a complete
  TP/FP/FN/TN on every panel of its arm (StabPrep: n1, n2, n3, train-union, n4
  held-out; SixLCU: n2 fit, n1 cross-check).
- G8 `determinism`: no wall-clock content in stdout receipt lines or digest-covered
  RESULTS fields (timing only in the RESULTS `timing` key, excluded from the digest,
  and stderr); no unseeded randomness (the only rng is the committed panel seed
  20260821 inside the imported `build_panel`); double run byte-identical on stdout
  and on RESULTS-minus-timing.
- G9 `no_new_subject_data_no_network`: no chemistry source read, no network access,
  protected stretched-N2 never read, no existing file modified, committed machinery
  imported unmodified (qg15_third_family, qg4_second_family).

Any integrity failure aborts nonzero with the failing assertion; no authority string
is emitted.

## 5. Held-out discipline (StabPrep)

Stage order enforced in code: (1) both arms' training searches complete; (2) the
canonical JSON of {minerr surface, all witness predicates, Q1/Q2/Q3 training
verdicts} is serialized and its sha256 printed as the FIRST stdout receipt line
`ORIONQG_QG15B_SELECTED_PREDICATES_SHA256=<hex>`; (3) only then the n=4 referee runs
and the panel is labeled; (4) held-out confusions computed for the selected
predicates. A held-out failure of a training-exact predicate is a first-class
outcome, reported verbatim.

## 6. Terminals and authority

Q1 terminal: `EXACT_PREDICATE_FOUND_IN_L1` (minerr(3,3) == 0, untruncated; held-out
generalization then reported as HELDOUT_EXACT or HELDOUT_REFUTED with counts) /
`L1_INSUFFICIENT` (minerr(3,3) > 0 recorded; if the (3,3) cell is truncated the value
is reported as an upper bound and the terminal is `L1_UNDECIDED_CAP`).

Q2 terminal: `ZERO_ACHIEVABLE_AT(K',D')` (minimal cells + headline cell recorded) /
`ZERO_UNACHIEVABLE_ANY_BUDGET` (E_floor > 0, mixed-cell certificate; secondary number
= minimal floor-attaining cells on the lattice, or `FLOOR_UNATTAINED_ON_LATTICE`) /
`ZERO_UNREACHED_ON_LATTICE` (E_floor == 0 but no lattice cell reaches 0: the
receipted lower bound is then "complexity exceeds the (K<=3, D<=6) lattice") — any
minimality statement whose deciding cells include a truncated cell is downgraded to
`_CAPPED` with the truncation disclosed.

Q3 terminal: the same Q1/Q2 machinery verdicts on SixLCU; headline = the calibration
pair (StabPrep minimal budget or its certificate, SixLCU minimal budget).

Lane terminal: `QG15B_COMPLETE` (Q1, Q2, Q3 all decided under their honest outcome
spaces, gates pass) / `QG15B_PARTIAL__<Q>_UNDECIDED` (a named question undecidable
within the frozen caps; which and why receipted) / `CANNOT_CHECK` (infrastructure or
gate failure).

Authority string:
`ORION_QG15B_PREDICATE_LANGUAGE_<TERMINAL>__STABPREP_BOUNDARY_PREDICATE_COMPLEXITY_ON_VERIFIED_DOMAINS__NOT_R6`.

## 7. Claim boundary (restated in the receipt)

All measurements are over the frozen finite training domains and the frozen language
L1 only: StabPrep exhaustive n <= 3 (1,146 instances) with one seeded n = 4 panel;
SixLCU exhaustive n = 2 (38,760) with the n = 1 cross-check. Predicate-complexity
numbers are properties of the frozen vocabularies, grids, and budget lattice; nothing
is a theorem for all n, for other feature sets, for unbounded budgets (beyond the
grid-independent mixed-cell certificate, which does bind every predicate over the
frozen vocabulary on the training domain), or for other families. The donor, referee,
and label machinery is the committed QG-15/QG-4 machinery, imported unmodified, and
earns no new credit. NOT_R6. No new subject data.

## 8. Independent generic verification, runtime, caps, outputs

`development/orion-qg-regime-geometry/qg15b_generic_verify.py`: imports NOTHING from
the qg15b analyzer. StabPrep ground truth is rebuilt from primitives via the
committed independent rebuild (qg15_generic_verify's own tableau/referee/donor,
which shares no code with the analyzer chain); SixLCU ground truth via the committed
qg4_second_family (the same authority Q3 itself cites). It must: rebuild both
training feature/label tables and verify cell tables, E_floor, and any mixed-cell
certificate; re-evaluate every serialized witness predicate from its description and
confirm every claimed error and confusion matrix (train and held-out; its own n=4
referee and panel regeneration); independently re-run a COMPLETE brute-force search
on the frozen sub-lattice {K=1, D in {1,2,3}} and {D=1, K in {1,2,3}} for both arms
(no R5/R6 reductions, its own enumerator) and confirm the claimed minerr values
there; verify the stage digest and the result digest. Prints exactly one token line
`ORIONQG_QG15B_GENERIC_VERIFY={"decision":"ACCEPT"|"REJECT",...}`. Sub-lattice scope
(not the full lattice) is the verifier's disclosed cap.

Runtime caps (disclosed): analyzer < 25 min/run; node budget 8,000,000 expansions
per lattice cell; lattice bounded at K <= 3, D <= 6 (frozen truncation, section
2.3); mixed cells serialized verbatim capped at 20 (counts exact); witnesses: one
per lattice cell plus the Q1/Q2/Q3 headline predicates. Outputs (only these four
files are added; no existing file is modified):

- stdout line 1: `ORIONQG_QG15B_SELECTED_PREDICATES_SHA256=<hex>`;
  stdout line 2: `ORIONQG_QG15B_PREDICATE_LANGUAGE=<canonical sorted compact JSON receipt>`.
- `research/extensions/orion-qg/QG15B_PREDICATE_LANGUAGE_RESULTS.json` (pretty,
  sorted keys; byte-identical across runs after removing `timing`).
- `research/extensions/orion-qg/qg15b_predicate_language.py` (analyzer; scratchpad
  venv python, stdlib + numpy via the imported committed machinery only),
  `development/orion-qg-regime-geometry/qg15b_generic_verify.py` (verifier), this
  protocol.
- stderr: per-stage runtime seconds (the only non-deterministic output).
