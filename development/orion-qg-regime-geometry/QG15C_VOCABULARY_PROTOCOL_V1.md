# QG-15c feature-vocabulary protocol V1 — enlarging the StabPrep vocabulary against the QG-15b information-theoretic floor

Date: 2026-08-22
Parent programme: ORION-QG (PROGRAMME_CHARTER_V1.md, issue #740), reopen-adjudicated
successor of QG-15b (`QG_REOPEN_ADJUDICATION_PROTOCOL_V1.md`; the QG-15b outcome was
classified `FAILED_DEFINITION` — what failed was the definition of the feature object,
not the search over it).
Branch: `claude/orion-harness-verification-b17qdj`, checked out at `f7d6898a`.

Status: **FROZEN BEFORE ANY QG-15c OUTCOME.** The enlarged feature list in section 3 is
the scientific core of this lane and is frozen verbatim here. No cell table, no
mixed-cell count, no error floor, no minimum-error value, and no held-out number over
the enlarged vocabulary has been computed before this freeze.

Pre-freeze computations actually performed, disclosed in full:

1. The **Q1 collision diagnosis** (section 2). This is a required input to the freeze:
   the reopen adjudication demands that the redefinition be *motivated* by the
   diagnosis. The diagnosis inspected, for each of the 12 QG-15b mixed cells, one
   positive and one negative member and a battery of structural descriptors
   (donor per-step cost profile, route sequence, pivot weights/signs, X-rank profile,
   Pauli weight enumerator, letter census, negative-sign census, tensor-factor donor
   costs). No error of any predicate, no cell table over any enlarged vocabulary, and
   no floor was computed.
2. **Runtime probes only**: wall-clock timings of `ladder_min` at n=3 (all 1146 states)
   and at n=4 (10 panel states), used to decide whether schedule-enlargement features
   fit the runtime cap. No labels were joined.

Hard honesty constraint acknowledged and binding: the vocabulary below may **not** be
revised after seeing the error floor it produces. If it fails, that is the result.

Authority ceiling: development/research registration of a feature-vocabulary
measurement; **NOT_R6**; no novelty credit, no new subject data, no network access.
The protected stretched-N2 subject is never read. Runtime cap: **< 25 minutes per
analyzer run** (double run < 50 minutes); all caps disclosed in section 8.

## 1. Inherited negative (bound verbatim)

From `research/extensions/orion-qg/QG15_THIRD_FAMILY_RESULTS.json`:
- StabPrep family: stabilizer-state preparation from |0..0> over {H(1), S(1), SDG(1),
  CNOT(3)}; exact Dijkstra referee over the complete stabilizer-state graph;
  frozen greedy-echelon (GE) donor, ascending qubit order, min-key pivot, X-route.
- Donor-exact censuses: n=1 5/6, n=2 28/60, n=3 189/1080.
- Component 4 terminal `NO_CLEAN_PREDICATE`.

From `research/extensions/orion-qg/QG15B_PREDICATE_LANGUAGE_RESULTS.json`:
- Vocabulary V1 = 13 integer features
  (`nCZ, nY, nSignX, nSignZ, nCN, C_D, r_X, c, LB, C_D-LB, n-c, nCN-(n-1), C_D-2n`).
- Training domain: exhaustive n=1..3 union, **1146 instances**, 243 V1-cells.
- **12 mixed cells**, vocabulary floor **E_floor = 43** — budget- and grid-independent.
- Calibration: SixLCU incumbent-exact boundary is exact at one literal (`maxg2 == -2`),
  E_floor = 0.

Gate G1 of this lane re-derives all of the above from primitives and asserts byte-level
agreement with the two stored receipts (the 12 mixed-cell records verbatim, the floor
43, the three donor censuses, the QG-15 P0/P1/P2/selected confusion matrices).

## 2. Q1 — diagnosis of the collision (pre-freeze, motivating)

For each of the 12 QG-15b mixed cells the diagnosis extracted the colliding stabilizer
states and compared a minimal distinguishing pair (the canonically-first donor-exact
member against the canonically-first trade member). The finding, stated before the
freeze:

> **In every one of the 12 mixed cells the two members differ in the ORDERED PER-STEP
> COST PROFILE of the frozen GE donor schedule, while agreeing on the total donor cost
> `C_D` and on every aggregate event counter (`nCZ, nY, nSignX, nSignZ, nCN`).**

V1 is a *bag of donor events plus a total*. It records how many Y-corrections, how many
sign-corrections and how many CNOTs the donor performed, and what they cost in total; it
does not record **how those events were distributed over the elimination steps**. The
donor's local suboptimality is a per-step property: a step that pays both a Y-correction
and a sign-correction on the same weight-1 pivot costs 4 where the exact referee pays 2
(the n=1 witness: `+Y` has `C_opt = 2`, `C_D = 4`), whereas the same two events on two
*different* steps cost 2 and 3 and are both exact. V1 cannot see that pairing.

Two sub-patterns appear, both invisible to V1:

- **Multiset differs** (cells 1, 3, 4, 5, 6, 7, 9, 10, 11): e.g. cell 4 (n=2)
  `[2,3]` (donor-exact) versus `[1,4]` (trade, gap 2) — same `nY=1`, same `nSignX=1`,
  same `C_D=5`.
- **Multiset agrees, ORDER differs** (cells 0, 2, 8): e.g. cell 8 (n=3) `[7,4,0]`
  (donor-exact) versus `[4,7,0]` (trade, gap 2); cell 0 `[6,0,4]` versus `[0,6,4]`.
  Any order-insensitive summary of the profile is therefore *also* insufficient; the
  enlarged vocabulary must carry order-sensitive statistics of the schedule.

Consequence for the freeze: the enlargement is a **schedule/path-aware** block —
order-sensitive statistics of the donor's own step sequence, per-step event
co-occurrence counters, the X-rank profile across the elimination, tensor-factor
locality, and the donor family's schedule-enlargement optimum. Section 3 is that block.

## 3. The frozen enlarged vocabulary V2 (33 integer features)

V2 = V1 (13, verbatim, same index order) followed by 20 new features in the frozen
index order below. V1 ⊂ V2 by construction, so `E_floor(V2) <= E_floor(V1) = 43`.

### 3.1 The donor schedule trace (definition)

Replay the frozen GE donor on the target state exactly as QG-15 defines it: qubits in
ascending order q = 0..n-1; at step q take `x_candidates(st, q, processed, n)` and, if
non-empty, the min-`_pivot_key` candidate with route X; otherwise the forced `-Z_q`
pivot with route Z, or, when `+Z_q` is already present, an empty step (route N).
Step q records:
- `c_q` = cost of the micro-step word (H/S/SDG = 1, CNOT = 3),
- event counts `nY_q, nCZ_q, nSignX_q, nSignZ_q, nCN_q` (QG-15 `micro_steps` events),
- `w_q` = Pauli weight of the chosen pivot, `sigma_q` = sign bit of the chosen pivot,
- `r_q` in {X, Z, N} = the route taken,
- `rho_q` = `r_X` of the state as it stands **before** step q; `rho_n := 0`.

Binding assertion (gate G3): `sum_q c_q == C_D` for every instance in every domain.

### 3.2 The 20 new features (frozen, verbatim)

Schedule-shape block (order-sensitive statistics of `c`):
- f13 `sched_cost_max` = max_q c_q
- f14 `sched_cost_argmax` = min { q : c_q = max_q c_q }
- f15 `sched_cost_first` = c_0
- f16 `sched_cost_last` = c_{n-1}
- f17 `sched_cost_descents` = #{ q < n-1 : c_q > c_{q+1} }
- f18 `sched_cost_moment` = sum_q q * c_q
- f19 `sched_steps_ge4` = #{ q : c_q >= 4 }
- f20 `sched_steps_zero` = #{ q : c_q = 0 }

Per-step event co-occurrence block (the diagnosed blindness):
- f21 `sched_events_max` = max_q (nY_q + nCZ_q + nSignX_q + nSignZ_q + nCN_q)
- f22 `sched_steps_Y_and_sign` = #{ q : nY_q >= 1 and nSignX_q + nSignZ_q >= 1 }
- f23 `sched_steps_Y_only` = #{ q : nY_q >= 1 and nSignX_q + nSignZ_q = 0 }
- f24 `sched_steps_sign_only` = #{ q : nY_q = 0 and nSignX_q + nSignZ_q >= 1 }

Pivot / route block:
- f25 `sched_pivot_sign_count` = #{ q : sigma_q = 1 }
- f26 `sched_pivot_wt_max` = max_q w_q
- f27 `sched_route_Z` = #{ q : r_q = Z }

Rank-profile block:
- f28 `sched_rank_drops` = #{ q in 0..n-1 : rho_q > rho_{q+1} }

Tensor-locality block (restriction of the state to each tensor factor of the frozen
`tensor_factors` cut, then the frozen GE donor applied to the restricted sub-state on
its own qubits, relabelled in ascending order):
- f29 `fac_size_max` = max factor size (in qubits)
- f30 `fac_cost_max` = max over factors of `C_D` of the restricted sub-state

Schedule-enlargement block (QG-15's frozen E3 ladder: adaptive qubit ORDER, free PIVOT,
free ROUTE, minimised over the donor family — `ladder_min(state, n, True, True)`):
- f31 `C_E3`
- f32 `C_D - C_E3`

### 3.3 Computability class (admissibility — gate G4)

Every one of the 33 features is a function of the target state and n alone, computed
from the donor family and F2 linear algebra. **No feature calls the exact referee, and
no feature uses `C_opt` or any quantity derived from it.** A feature that needs the
optimum would be circular and is inadmissible. This is enforced structurally in code:
during the entire feature-computation phase the referee entry points are replaced by a
raising stub, so any referee call inside feature computation aborts the run (gate G4).
The complexity class is: exponential in n (the state has 2^n group elements and the E3
ladder explores the donor family), polynomial in the size of the state description; no
shortest-path oracle.

## 4. Domains (frozen)

- **Training / fit domain**: exhaustive StabPrep n = 1, 2, 3 — 6 + 60 + 1080 = **1146**
  instances. Identical to QG-15b.
- **Held-out panel**: the QG-15 seeded n=4 panel (seed 20260821, 120 distinct states,
  24-gate random words), regenerated by the committed generator. **Untouched during all
  searching.** The panel is labelled only after the stage digest of section 6 is printed
  to stdout; enforced by a code-structural lock flag (gate G5).
- n=4 exhaustive (36,720 states) is used only to validate the referee used for panel
  labelling, after the stage digest.

## 5. Search (frozen budget lattice and machinery)

The QG-15b language L1 and search machinery are reused **verbatim in form**:
- Literal: `[feature op threshold]`, op in {==, <=, >=}, closed under negation.
- Threshold grid: the values attained by that feature on the training domain (complete
  over integer thresholds on train).
- Member: disjunction of at most D conjunctions of at most K literals; constants
  included.
- Complete depth-first branch-and-bound over the cell-collapsed table with the frozen
  reductions R1 (constants), R2 (duplicate literal truth-vectors), R3 (duplicate
  conjunction truth-vectors), R4 (empty conjunctions), R5 (non-negative potential),
  R6 (relevant-restriction dedupe); all reduction counts recorded.
- **Frozen lattice: K in {1, 2}, D in {1, 2, 3, 4, 5, 6}.** K = 3 is excluded by
  runtime arithmetic before the freeze: V2 has roughly three times V1's literal pool,
  so the K=3 conjunction enumeration is ~10^8 raw triples and cannot fit the 25-minute
  cap. Disclosed as a cap in section 8, exactly as QG-15b disclosed its K=4 exclusion.
- **Node budget: 3,000,000 DFS expansions per lattice cell.** A cell that exhausts its
  budget is recorded `truncated: true` and its `minerr` is an upper bound only;
  minimality claims resting on it are flagged `minimality_compromised_by_truncation`.
- Search is over the training domain only.

The **primary result of this lane does not depend on the search**: the mixed-cell count
and `E_floor(V2)` are properties of the cell table alone, hence budget- and
grid-independent. The lattice search supplies the predicate and its budget when the
floor permits it.

## 6. Stage digest and held-out discipline

After the training cell table, `E_floor(V2)`, the surviving-collision census and the
full min-error surface are computed, and **before** any n=4 referee call or any panel
labelling, the analyzer prints

```
ORIONQG_QG15C_STAGE_DIGEST=<sha256 of the canonical JSON of the pre-heldout stage object>
```

and only then sets the held-out lock flag. Gate G5 asserts the flag was unset at the
moment of stamping.

Held-out tests, both frozen here, both applied **untouched** (no re-fitting, no
threshold adjustment) and reported honestly — a held-out failure is first-class:

- **H1 — cell-lookup rule.** Predict donor-exact on a held-out state iff its V2 vector
  equals the V2 vector of some training cell whose training members are *all*
  donor-exact. A V2 vector unseen in training predicts negative and is additionally
  counted and reported as `unseen_cells`. This is the natural test of a
  *feature-determining* vocabulary and is defined whether or not the floor is zero.
- **H2 — the lattice predicate.** The witness at the headline achieving cell (zero-error
  headline cell if zero is achieved; otherwise the floor-attaining headline cell;
  otherwise the best cell on the lattice), serialized and re-evaluated verbatim.

## 7. Terminals (frozen)

Decided on the **training** domain only:

- `QG15C_FEATURE_DETERMINATION_RESTORED` — `E_floor(V2) == 0` and `mixed_cells(V2) == 0`
  on the 1146-instance training domain (V2 determines the donor-exact label as a
  function). The minimal exact predicate and its budget are reported when the frozen
  lattice attains zero; if the lattice does not attain zero within its budget that is
  disclosed as `LATTICE_DID_NOT_ATTAIN_ZERO` and does not change the terminal. The
  held-out result is reported separately and honestly, and never changes the terminal.
- `QG15C_FLOOR_PERSISTS__COLLISIONS_CHARACTERIZED` — `E_floor(V2) > 0`. The surviving
  mixed cells are serialized with a minimal distinguishing pair each, characterized
  (section 7.1), and the impossibility-theorem obligation of section 7.2 is stated. No
  impossibility claim is made.
- `QG15C_CANNOT_CHECK` — any gate fails, any receipt binding fails, or the runtime cap
  is breached.

### 7.1 Frozen characterization battery for surviving collisions

For each surviving mixed cell: n; pos/neg counts; the V2 vector; the canonically-first
donor-exact member and the canonically-first trade member, with Pauli strings, ordered
donor step-cost profiles, gap `C_D - C_opt` of the trade member. Aggregated:
whether all surviving collisions sit at a single n; whether all trade members in a cell
share one gap; whether the two members of the minimal pair are related by a **qubit
permutation** (all n! permutations tested) — a permutation-related collision would show
that *no permutation-invariant* vocabulary can separate; whether they share the same
tensor-factor size profile; whether they share the same Pauli weight enumerator; and
whether they share the same negative-sign census.

### 7.2 The impossibility-theorem obligation (stated, not claimed)

Two failed vocabularies are evidence, not proof. A genuine impossibility theorem for
this family would have to fix a precise feature class F — e.g. "all functions of the
state computable from the r-local marginals of the stabilizer group", or "all
permutation-invariant functions of the signed Pauli weight enumerator", or "all
functions of the frozen donor's gate word up to reordering" — and prove: for every
f in F there exist two n-qubit stabilizer states S+, S- with f(S+) = f(S-),
`C_opt(S+) = C_D(S+)` and `C_opt(S-) < C_D(S-)`. QG-15c can supply the witnesses; it
cannot quantify over F. Nothing below the level of that quantification is an
impossibility result, and this lane will not assert one.

## 8. Caps, gates and outputs (frozen)

Caps disclosed:
- runtime cap < 25 minutes per analyzer run;
- lattice frozen at K <= 2, D <= 6 (K = 3 excluded by pre-freeze runtime arithmetic);
- node budget 3,000,000 DFS expansions per lattice cell;
- mixed cells serialized verbatim capped at 20 per vocabulary (counts always exact);
- held-out panel is the single seeded 120-state n=4 panel; no other n=4 sampling;
- generic verifier scope: full independent rebuild of the referee, donor, schedule
  trace and all 33 V2 features on n <= 3, the V1 and V2 cell tables and floors, every
  serialized witness re-evaluation, a complete brute-force minimum-error check on the
  sub-lattice {(K,D)} = {(1,1), (1,2), (1,3), (2,1)} with an independent enumerator and
  no R5/R6 reductions, and the independent regeneration and labelling of the n=4 panel.

Gates (all must pass; any failure forces `QG15C_CANNOT_CHECK`):
- **G1 receipt binding** — QG-15 donor censuses (5/6, 28/60, 189/1080) and the QG-15
  P0/P1/P2/selected confusion matrices on n=1, n=2, n=3 and the n=4 panel reproduced
  exactly; QG-15b V1 cell table reproduced exactly: 243 cells, 12 mixed cells (records
  verbatim-equal as a set to the stored `mixed_cells_verbatim_capped`), E_floor = 43,
  1146 rows.
- **G2 donor validity** — for every instance, the donor prep circuit applied to
  |0..0> reproduces the state, and `LB <= C_opt <= C_D`.
- **G3 schedule-trace consistency** — `sum_q c_q == C_D` and the summed per-step event
  counts equal the aggregate `nCZ, nY, nSignX, nSignZ, nCN` of the committed donor, for
  every instance in every domain.
- **G4 referee-free features** — the referee entry points are stubbed to raise for the
  whole feature-computation phase; the stub is never triggered.
- **G5 held-out discipline** — the stage digest is printed before the lock flag is set;
  no n=4 referee call, no panel labelling, and no held-out evaluation occurs before it.
- **G6 search completeness accounting** — per (K, D): pool size, DFS node count,
  truncation flag, and all R1-R6 reduction counts recorded.
- **G7 surface monotonicity** — for untruncated cells, `minerr` is non-increasing in K
  and in D.
- **G8 floor consistency and witness re-evaluation** — every recorded `minerr` is
  >= `E_floor(V2)`, and every serialized witness re-evaluated from its description
  reproduces its recorded `minerr` exactly.
- **G9 determinism** — no wall-clock value enters any digest; double run byte-identical
  results file and stdout.
- **G10 no new subject data, no network** — the protected stretched-N2 subject is never
  read; no network access; no chemistry sources read.

Outputs:
- `research/extensions/orion-qg/qg15c_vocabulary.py` — analyzer.
- `research/extensions/orion-qg/QG15C_VOCABULARY_RESULTS.json` — results.
- stdout: exactly two deterministic token lines,
  `ORIONQG_QG15C_STAGE_DIGEST=<sha256>` then
  `ORIONQG_QG15C_VOCABULARY=<canonical receipt JSON>`; stderr carries stage runtimes
  (the only non-deterministic output).
- `development/orion-qg-regime-geometry/qg15c_generic_verify.py` — independent
  pure-primitive verifier printing exactly one line
  `ORIONQG_QG15C_GENERIC_VERIFY={"decision":"ACCEPT"|"REJECT",...}`.

Authority string:
`ORION_QG15C_FEATURE_VOCABULARY_<TERMINAL>__STABPREP_DONOR_EXACT_BOUNDARY_VOCABULARY_DETERMINATION_ON_VERIFIED_DOMAINS__NOT_R6`.

## 9. Claim boundary

All measurements are over the frozen finite domains and the frozen vocabularies only:
StabPrep exhaustive n <= 3 (1146 instances) with one seeded 120-state n=4 panel. The
mixed-cell count and floor are properties of the frozen vocabulary V2 on that domain;
nothing here is a theorem for all n, for other vocabularies, or for other families.
Ground-truth machinery is the committed QG-15 machinery, imported unmodified, and earns
no new credit. NOT_R6. No new subject data; the protected stretched-N2 subject is
untouched.
