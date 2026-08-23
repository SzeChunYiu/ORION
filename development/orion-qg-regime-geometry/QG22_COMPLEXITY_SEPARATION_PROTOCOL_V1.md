# QG-22 — the complexity separation: is regime membership cheap while exact optimization is hard?

Date: 2026-08-22
Lane: ORION-QG / regime geometry, wave 3
Branch: `claude/orion-harness-verification-b17qdj`
Base revision: `4fb20e30`
Status: **FROZEN BEFORE ANY OUTCOME-DETERMINING RUN.**

Authority ceiling: **NOT_R6**. `novelty_authority: false`, `donor_novelty_credit: false`,
`physical_quantum_advantage_claim: false`. No chemistry data is read. The protected
stretched-N₂ discriminator
`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt`
is never read. No network. Every committed analyzer this lane imports is imported
**unmodified**; no repository file outside the five listed in §12 is created or changed,
and no existing repository file is modified.

Runtime cap: **< 25 minutes per run** (wall clock, single process). Every domain in
§5–§8 is sized against that cap and every cap is disclosed in §9. No silent truncation:
every declared domain is executed in full and its size recorded verbatim in the RESULTS
file; every domain that is *not* attempted is named in §9 with the reason.

---

## 0. Why this lane exists

The programme has, for TARE under the frozen unit-cost objective O0:

* an exact decidable regime predicate (R6Q `P1`, prospectively confirmed in QG-3);
* an all-n closed form `C_DP == min(C_D+, f_B', f_B'')` (QG-7e, theorem terminal);
* a certified-search corollary `O(n^d A^d)` with `d = 2` (QG-6);
* a DP-free polynomial exact cost oracle on its stated domain (QG-5b).

It has never stated the **complexity-theoretic** content of that bundle: how hard is it to
*decide regime membership*, versus to *compute the optimum*, versus to *decide whether a
given compilation is optimal*? Donor D3 in `QG_EXTERNAL_DONOR_REGISTER_V1.md`
(Touati et al. 2006, undecidability of optimal phase ordering) is the backdrop that makes
decidable optimality characterizations inside a restricted family interesting at all.

## 1. Donor boundary (zero novelty credit)

The following are **donor mathematics** and receive **zero** novelty credit in this lane:

* the complexity classes and their vocabulary (P, NP, NP-hardness, #P, EXPTIME,
  parameterized complexity, FPT, XP, W-hierarchy);
* asymptotic notation and the least-squares fitting of measured runtimes;
* dynamic programming, min-plus (tropical) semiring composition, subset/don't-care
  ζ-transforms, Bellman–Ford / Dijkstra shortest paths;
* Touati et al. 2006 (D3) and every other register entry D1–D5.

The only thing this lane can contribute is the **compiler-specific separation statement**
(or its refutation) for the frozen families of this programme. Nothing here is a result
about compilation in general.

## 2. Frozen objects

**Family (TARE / R6M).** Instance
`I = (t_A0, t_A1, t_B0, t_B1, t_C0, t_C1)`, six nonzero n-qubit Pauli targets, each given
as a symplectic bit-pair `(x, z) ∈ [0,2^n)²`. Frozen block matching `((0,1),(2,3),(4,5))`.
Input size `|I| = 12n` bits. Grammar constants: `K = 3` blocks, `L = 2K+1 = 7` local
letters per qubit (six frame letters + one Tag letter), local alphabet `A = 4` (`I,X,Y,Z`),
`D = 9` syndrome parity bits (the R6M acceptance predicate), `C_ext = 32` external
configuration choices (`perm_B, perm_C ∈ {0,1}` × `centrals ∈ {0,1}³`).

**Objective.** The frozen unit-cost support objective O0 of R6M/R6S (identical to the one
frozen in QG-18 §1). The alternative objective **O1** is QG-2's frozen T-count-weighted
objective `(t_nc, t_c, t_tag, t_r, ρ) = (7, 1, 4, 3, 0)`.

**Algorithms, all imported unmodified.**

| tag | object | implementation |
|---|---|---|
| `STRUCT` | structure-only feature vector `(s1,s2,s3,a3,a2max)` | `max_r6q_regime_predicate.simple_features` |
| `P1` | regime predicate `Gsplit == 0 ∧ f_B ≥ C_R6L` | `max_r6q_regime_predicate.predicate_p1` over `evaluate_instance` fields |
| `DPLUS` | `C_D+` | `max_r6o_enlarged_tag_donor_closure.dplus_pairs` |
| `R6L` | `C_R6L` (weight-one donor) | `max_r6m_...dp.donor_r6l_matching` |
| `FB` | `f_B` (frozen borrow family) | `max_r6q_regime_predicate.borrow_family_min` |
| `FBP` | `f_B'` (enlarged borrow family) | `qg5b_exact_forecaster.bprime_family_min` |
| `FBPP` | `f_B''` (weight-2-Tag hybrid family) | `qg7b_hybrid_family.bsecond_family_min` |
| `CF` | the QG-7e closed form `min(C_D+, f_B', f_B'')` | composition of `DPLUS`, `FBP`, `FBPP` |
| `DP` | the unrestricted syndrome DP referee `C_DP` | `max_r6p_weight2_frame_donor_closure.dp_cost_frozen_configs` |
| `NAIVE` | the naive configuration referee | `max_r6m_...dp._brute_config_n1` / `_brute_config_n2` swept over the 32 external configs |
| `FAM` | the committed support-capped family search | `max_r6p_weight2_frame_donor_closure.dxx_search` |
| `DP_O1` | the O1-parameterized DP | `qg2_objective_robustness` objective-parameterized DP path |

## 3. The frozen questions (verbatim)

> **Q1 (upper bounds, exactly stated).** For the frozen TARE grammar under the unit
> objective, state and prove the exact time complexity, as a function of n and the local
> alphabet size A, of: (a) evaluating the regime predicate; (b) computing
> `min(C_D+, f_B′, f_B″)`, i.e. the certified exact optimum via QG-7e; (c) the unrestricted
> DP referee. Give each as a proven bound with the counting argument written out, and
> machine-measure the actual scaling to confirm the exponents empirically (fit measured
> runtimes across the n you can reach; report the fit, do not assert it). The interesting
> content is the *gap* between (b) and (c).

> **Q2 (is the hardness real, or did we define it away?).** The honest threat to any
> separation claim here: `C_DP` may be computable in polynomial time *because of QG-7e
> itself* — the closed form is a polynomial-time exact algorithm, so for this family
> "exact optimization" may simply not be hard. Confront that directly. State precisely
> what remains hard, if anything: the unrestricted DP's own runtime is not a lower bound
> on the problem. Candidates worth examining: does hardness reappear under the O1
> objective, where QG-2 showed support-3 configurations pay and no closed form is known?
> Does it reappear for a family *without* a closed form (SixLCU, StabPrep)? **If the
> honest answer is "for unit-cost TARE there is no separation because we solved the
> problem," say exactly that** — it is a strong and publishable statement, and dressing it
> up would be worthless.

> **Q3 (the durable statement).** Whatever Q1/Q2 yield, formulate the general claim the
> programme can defend, with its quantifiers exact. A candidate shape: *for a compilation
> family admitting an all-n finite-support classification, exact optimization is
> polynomial-time in n while the naive referee is exponential — and the classification is
> what collapses it.* State which of its components are proven, which are evidenced on
> finite domains, and which are conjecture. Name explicitly what a family would have to
> look like for the statement to fail.

## 4. What counts as PROVEN vs MEASURED vs CONJECTURE

Every complexity statement emitted by this lane carries exactly one label.

* **PROVEN** — a counting argument written out over the *imported code's own* loop and
  array structure, giving an exact operation count `V(n)` (not an O-symbol), where the
  counted quantities are additionally **machine-instrumented in the run** and asserted
  equal to the closed-form count on a declared domain. A PROVEN label is a statement about
  **the named algorithm**, never about the problem. `Θ` may be used for an algorithm's own
  work; it may never be used for a problem.
* **MEASURED** — wall-clock timing on the frozen ladders of §5, fitted by ordinary least
  squares in the stated coordinates, reported with slope, intercept, R², RMS residual, max
  absolute residual, the exact n-domain, and the repeat count. Never extrapolated beyond
  the measured domain; any statement about larger n is labelled CONJECTURE.
* **CONJECTURE** — everything else, including every statement about families or parameter
  regimes for which this lane executed no code.

**Forbidden without a reduction.** No statement of the form "problem X is NP-hard /
#P-hard / not in P / requires exponential time" may appear anywhere in the RESULTS file or
in the report. The RESULTS file carries `complexity_class_claim: "none"` and
`reduction_supplied: false`, and gate G6 machine-checks that no hardness verb occurs
outside an explicitly negative context. "The DP is exponential" is a statement about our
algorithm and is never written as a statement about the problem.

## 5. Q1 — frozen measurement ladders

One frozen instance per n, drawn by the frozen generator of §6 with seed `20260822`.
Timing is `time.perf_counter`, minimum over the declared repeat count (minimum, not mean:
it is the least noise-contaminated estimator of the deterministic work).

| object | n-ladder | repeats |
|---|---|---|
| `STRUCT` | 1,2,3,4,6,8,12,16,24,32,48,56 | 5 |
| `DP` | 1,2,3,4,6,8,12,16,24,32,48 | 3 for n ≤ 8, else 1 |
| `R6L` | 1,2,3,4,6,8,12,16,24,32 | 3 for n ≤ 8, else 1 |
| `DPLUS` | 1,2,3,4,6,8,12,16,24 | 3 for n ≤ 8, else 1 |
| `FBP` (`f_B'`) | 2,3,4,5,6,7,8 | 3 for n ≤ 6, else 1 |
| `FBPP` (`f_B''`) | 3,4,5,6 | 3 for n ≤ 4, else 1 |
| `FAM` (`dxx_search`, `max_weight=1`) | 1,2,3,4,5 | 1 |
| `NAIVE` | 1,2 | 1 |

Fits: polynomial objects are fitted as `log10 t` vs `log10 n` (slope = exponent);
exponential objects as `log10 t` vs `n` (slope = per-qubit factor, base `10^slope`).
Because every object carries a large additive constant (module/table warm-up), each
polynomial object **also** reports a tail fit restricted to the largest four ladder points,
and both fits are reported. The reported exponent is the tail fit; the full-domain fit is
reported beside it and never suppressed.

## 6. Frozen instance generator

`numpy.random.default_rng(seed)`, seed `20260822`; for each of the six targets, draw
`x, z` uniformly from `[0, 2^n)` and reject `(0,0)`. This is the generator shape already
frozen in `max_r6p_weight2_frame_donor_closure.domain_random_panel`. Instances are drawn
in ascending ladder order from a single stream, so the ladder is reproducible byte-for-byte.

## 7. Q1 — the counting arguments to be verified

Each `V(n)` below is asserted in the run against instrumented counters taken from the
imported code itself (`lru_cache.cache_info()`, array `.shape`, block-option row counts).
A mismatch fails gate G3.

1. `STRUCT`: `V = n` local-letter comparisons, constant work per qubit. Bound `Θ(n)`.
2. `R6L`: `V = 24n` representations per block; `V_triples = Σ_{common keys} |g_A||g_B||g_C|`;
   each triple costs `Θ(n)` word-ops. Bound `O(n²)` word-ops.
3. `DPLUS`: per label orientation, per block `m = 12n` choices; the F3 accumulation touches
   `2 · m³ · (1 + 2n)` array cells. Bound `Θ(A^? )`-free, exactly `Θ(n⁴)` cells,
   `Θ(n³)` words of memory.
4. `FB`/`FBP`: `O(n)` tag qubits × 3 tag letters × per-block row counts `O(n)` ⇒
   `O(n³)` cells × `O(n)` F3 passes ⇒ `O(n⁵)` cells.
5. `FBPP`: `O(n²)` tag qubit pairs × 9 letter pairs × per-block row counts `O(n)` ⇒
   `O(n³)` cells × `O(n)` F3 passes ⇒ `O(n⁶)` cells.
6. `CF = min(DPLUS, FBP, FBPP)`: dominated by `FBPP`, `O(n⁶)`.
7. `DP`: `C_ext = 32` external configurations × n qubits × `2^D × 2^D = 2^18` min-plus
   transition cells, plus at most `min(4·8·n, A^{2K} · 2^K)` distinct local tables each
   built from `A^{2K+1} = 4^7` options. Bound `Θ(C_ext · 2^{2D} · n + n · A^{2K+1})`,
   i.e. **`Θ(n)`** for the frozen grammar.
8. `NAIVE`: the configuration space is
   `|Cfg(n)| = C_ext · Σ_{S ≠ 0} Σ_{(l0,l1) ∈ {(0,1),(1,0)}} |Pairs(S,l0,l1)|³`
   where `Pairs(S,l0,l1) = {(R0,R1) : symp(R0,R1)=1, symp(S,R0)=l0, symp(S,R1)=l1}`.
   Bound `Θ(A^{(2K+1)n}) = Θ(4^{7n})`. Exact counts are enumerated for n ≤ 3 and checked
   against the closed form; the referee is *executed* only for n ∈ {1,2}.
9. `FAM` (`dxx_search`): pattern space `M = A^{2n}`, ζ-transform `2n` passes over `M`,
   Tag sweep over `A^n − 1` Tags ⇒ `O(n · A^{3n})` cells. Exponential in n.

## 8. Q2 and Q3 — the frozen confrontation

**Q2-A (does the closed form supply the tractability?).** Compare the measured exponent of
`CF` with that of `DP` on the ladders of §5. If `DP` is asymptotically *cheaper* than `CF`,
then the closed form is not the source of tractability and the QG-7e theorem cannot be
credited with a complexity collapse. Outcome recorded either way.

**Q2-B (does hardness reappear under O1?).** Run the QG-2 objective-parameterized DP under
O1 on the `DP` ladder (n ≤ 16, repeats 1) and fit it. O1 has no closed form. If the O1 DP
scales like the O0 DP, "no closed form" does not imply "no polynomial exact algorithm" and
the O1 escape hatch is closed. Outcome recorded either way.

**Q2-C (verification).** The decision problem "is this given compilation optimal?" is
solved by evaluating its cost (`Θ(n)` by the frozen objective) and comparing against the
optimum. Its complexity is therefore that of the optimum. Recorded, with the objective
evaluator's own count instrumented.

**Q2-D (located candidate: a family without a finite conserved syndrome).** For StabPrep
(QG-15) the exact referee is a shortest path over the complete n-qubit stabilizer-state
graph, `|S_n| = 2^n ∏_{k=1}^n (2^k + 1) = 2^{Θ(n²)}`. The closed form is computed for
n ≤ 12 and checked against QG-15's committed domain counts for n ∈ {1,2,3} and its
`n4_expected`. QG-15's own predicate terminal (`NO_CLEAN_PREDICATE`) and cost terminal
(`COST_FORECAST_REFUTED`) are re-bound from its receipt. This locates a **candidate**; it
is not a hardness result and is labelled CONJECTURE.

**Q2-E (located candidate: the grammar parameters).** The DP's proven bound is
`Θ(C_ext(K) · 2^{2D(K)} · n + n · A^{2K+1})` with `C_ext(K) = 2^{K-1} · 2^K` for the
external choices of a K-block grammar and matching count `(2K−1)!!` when the pairing is not
given. Both grow super-polynomially in K while every factor is polynomial (linear) in n.
`(2K−1)!!` is computed exactly; `D(K)` is **CONJECTURE** — this lane runs no K ≠ 3 grammar.

**Q3.** The durable statement is assembled from the Q1/Q2 outcomes with each component
labelled PROVEN / MEASURED / CONJECTURE and an explicit failure clause naming what a family
must look like for the statement to fail.

## 9. Caps disclosed

* Runtime cap < 25 min per run; the lane budgets ≈ 8 min of measurement.
* The instrumented exact cell counts of §7 are computed on `n ∈ {1,…,10}`. They are
  exact integers, not timings, so the exponent read off them is a property of the
  code, not of the machine; it is still reported as a fit with residuals, and at these
  n the finite-size constants (`4 + 24(n−1)` rows, `8 + 48(n−2)` rows) make the fitted
  exponent approach the proven exponent **from above**. That is disclosed, not hidden.
* `NAIVE` executed only for n ∈ {1,2}. n = 3 is **not attempted**: `|Cfg(3)|` exceeds
  10¹² configuration triples and the committed brute enumerators are defined for n ∈ {1,2}
  only. Recorded as `not_attempted` with the exact count.
* `FAM` executed at `max_weight = 1` for n ≤ 5 (memory: `A^{2n}` int64 arrays) and at
  `max_weight = 2` only for n ∈ {1,2,3}, which is the guard range of
  `EXPECTED_PAIR_COUNTS` in the committed module. Larger n **not attempted**.
* `FBPP` ladder stops at n = 6 (single call ≈ 40–90 s at n = 6; n = 7 exceeds the budget).
* `DPLUS` ladder stops at n = 24 (single call ≈ 21 s; n = 32 ≈ 70 s).
* `FBP` ladder stops at n = 8.
* Agreement panel: 20 instances at n = 2, 20 at n = 3, 6 at n = 4 (bounded by `FBPP`).
* Verbatim serialization caps: at most 20 rows per panel; every cap and every count is
  written to the RESULTS file.
* Ladders stop at n = 56: the frozen generator of §6 is the committed panel shape
  `rng.integers(0, 2^n)`, which is bounded by the int64 range. Disclosed, not
  worked around — no ladder point beyond n = 56 is attempted.
* StabPrep is treated **analytically only** — no StabPrep referee is executed in this lane.

## 10. Gates (all must pass; any failure ⇒ `QG22_CANNOT_CHECK`)

* **G1 receipt bindings exact** — sha256 of `QG7E_TWELVE_STATES_RESULTS.json`,
  `QG6_SYNDROME_DIMENSION_RESULTS.json`, `QG5B_EXACT_FORECASTER_RESULTS.json`,
  `QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json`, `QG18_TARE_KAPPA_RESULTS.json`,
  `QG15_THIRD_FAMILY_RESULTS.json`, `QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json` recorded, and
  the semantic fields this lane relies on (QG-7e `proof_audit.statement` and
  `terminal`; QG-6 `search_complexity_corollary`; QG-5b `q1.outcome`/`q2.outcome`;
  QG-18 `intrinsic_support_number`; QG-9 V6 `support_bound`; QG-15 `component_outcomes`)
  re-read and asserted verbatim.
* **G2 label discipline** — every emitted complexity statement carries exactly one of
  PROVEN / MEASURED / CONJECTURE.
* **G3 counting instrumented** — every PROVEN `V(n)` of §7 equals the instrumented count
  from the imported code on its declared domain.
* **G4 agreement** — on the agreement panel, `C_DP == min(C_D+, f_B', f_B'')` (QG-7e), and
  on n ∈ {1,2} additionally `C_DP == NAIVE` and the sandwich `C_DP ≤ C_Dxx ≤ C_D+ ≤ C_R6L`.
* **G5 fits reported with residuals and domain** — slope, intercept, R², RMS and max
  residual, n-domain and repeats present for every MEASURED statement; no extrapolation.
* **G6 no complexity-class claim without a reduction** — `complexity_class_claim: "none"`,
  `reduction_supplied: false`, and a machine scan of the serialized RESULTS text finds no
  hardness verb outside an explicitly negative context.
* **G7 authority** — `r6_authority: false`, `novelty_credit: false`,
  `donor_novelty_credit: false`, `novelty_authority: false`,
  `physical_quantum_advantage_claim: false`.
* **G8 isolation** — no chemistry source read, no network, protected subject not read.
* **G9 determinism** — two runs produce byte-identical RESULTS (timing section excluded
  from the digest per the R6P convention) and an identical canonical stdout token.
* **G10 no silent truncation** — every declared domain size recorded; every not-attempted
  domain named with its reason and its exact count.

## 11. Terminals (frozen, all valid)

* `QG22_SEPARATION_ESTABLISHED` — a proven complexity gap with exact quantifiers.
* `QG22_NO_SEPARATION__CLASSIFICATION_COLLAPSES_THE_PROBLEM` — the closed form makes exact
  optimization tractable, so there is nothing to separate for this family.
* `QG22_PARTIAL__HARDNESS_LOCATED_ELSEWHERE` — no separation for unit-cost TARE, but a
  located candidate under another objective or family, with the evidence for it.
* `QG22_CANNOT_CHECK`.

## 12. Files this lane may create (and no others)

1. `development/orion-qg-regime-geometry/QG22_COMPLEXITY_SEPARATION_PROTOCOL_V1.md` (this file)
2. `research/extensions/orion-qg/qg22_complexity_separation.py`
3. `research/extensions/orion-qg/QG22_COMPLEXITY_SEPARATION_RESULTS.json`
4. `development/orion-qg-regime-geometry/qg22_generic_verify.py`
5. `development/orion-qg-regime-geometry/QG22_GENERIC_VERIFICATION.json`
   (the independent verifier's own output)

Canonical stdout token prefix: `ORIONQG_QG22_COMPLEXITY_SEPARATION=`.
