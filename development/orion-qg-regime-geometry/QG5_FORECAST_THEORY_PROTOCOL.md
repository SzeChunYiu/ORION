# QG-5 — Certified static resource forecaster: frozen protocol V1

Date: 2026-08-21. Programme: ORION-QG (charter:
`development/orion-qg-regime-geometry/PROGRAMME_CHARTER_V1.md`, issue #740).
Parent evidence: ORION-Q MAX R6L/R6M/R6N/R6O/R6P/R6Q/R6R/R6S receipts, all
committed and replay-verified on branch `claude/orion-harness-verification-b17qdj`.

STATUS: FROZEN BEFORE ANY QG-5 OUTCOME. No forecast error, no timing number,
and no library-candidate admission result had been computed under this
protocol when this file was written. No gate below may be weakened after any
outcome is seen.

Authority ceiling: NOT_R6. No novelty credit, no donor credit, no scientific
authority. The library forecast table produced under this protocol grants NO
verification authority whatsoever: every row not backed by a committed DP
receipt is an unverified forecast and must be labeled as such.

## 1. Object under test — the certified static forecaster

Family: the frozen R6L/R6M three-block TARE-M2 shared-one-bit-Tag grammar
with the donor-owned all-three Restore common-factor rule under the frozen
raw support-count objective (multipliers 4 non-central / 2 central), exactly
as committed in `max_r6m_exact_three_tare2_shared_factor_dp.py`. All
machinery is imported UNMODIFIED from the committed modules
(`max_r6m_*`, `max_r6o_*`, `max_r6q_*`, `max_r6f_*`, `max_r6r_*`,
`max_r6_p10_*`); this lane adds no new grammar and changes no frozen table.

Input: the six frozen target Paulis of one instance — three ordered blocks of
target pairs `t = ((A0,A1),(B0,B1),(C0,C1))` on n qubits — plus, when the
instance comes from a real Hamiltonian batch, the six coefficients (used ONLY
for the Lambda report field `lambda_r6m`; coefficients never enter the
structural cost, per the frozen R6M grammar).

Output (NO dynamic-programming call of any kind):

- `C_R6L(t)` — exact minimum of the frozen weight-one shared-Tag donor
  family (`r6m.donor_r6l_matching`, complete frozen enumeration, R6L
  protocol + Erratum 1).
- `C_Dplus(t)` — exact minimum of the frozen D+ anchor-splitting family
  (`r6o.dplus_pairs`, complete frozen enumeration).
- `f_B(t)` — exact minimum of the frozen Tag-borrow family B(t)
  (`r6q.borrow_family_min`, frozen restricted enlargement; +INF sentinel
  when the family is empty).
- predicted exact optimal cost `F(t) := min(C_R6L, C_Dplus, f_B)`.
- certified regime (frozen R6R rule): `donor_exact` if `F == C_R6L`, else
  `split` if `F == C_Dplus`, else `borrow`.
- certificate: the closed-form witness family attaining the minimum plus the
  two-trade profitability/non-profitability checks
  `Gsplit := C_R6L - C_Dplus` (split profitable iff > 0) and
  `borrow_profitable := f_B < min(C_R6L, C_Dplus)`; the R6Q predicate
  `P1(t) := [C_Dplus == C_R6L] AND [f_B >= C_R6L]` must coincide with the
  regime `donor_exact` (hard assertion, identical to R6R stage 1).

Hard structural assertion on every evaluated instance: `C_Dplus <= C_R6L`
(family containment); on every instance where a DP truth value is available:
`C_DP <= C_Dplus <= C_R6L` and `C_DP <= f_B` (borrow soundness).

## 2. Certificate components and their proof status (frozen claim boundary)

The certificate distinguishes three statuses honestly. The receipt must carry
this table verbatim; no component may be promoted after the run.

1. UPPER BOUND — PROVEN (constructive). Each of C_R6L, C_Dplus, f_B is the
   exact minimum of a complete enumeration of an explicitly constructible
   sub-family of the frozen grammar, so `C_DP <= F(t)` always. Backing:
   MAX_R6L (+ Erratum 1) and MAX_R6M receipts (R6L family + witness checks),
   MAX_R6O receipt (D+ family + independent witness re-verification),
   MAX_R6Q protocol (borrow family definition; `C_DP <= f_B` machine-asserted
   on every DP-compared instance ever recorded, and re-asserted here).
2. SUPPORT-2 SUFFICIENCY — PROVEN, ALL n (machine-checked theorem). The
   MAX_R6S all-n composition theorem (`C_DP == C_Dxx` for every qubit count,
   every target six-tuple, every matching: frames of global support >= 3
   never pay; Lemma B pigeonhole + Lemma E 18,432-case exhaustive check +
   exchange induction) makes the DP optimum unconditionally attained inside
   support-<=2 frames. Consequence for the certificate: any gap between F(t)
   and C_DP can only be realized by support-<=2 frames outside the three
   enumerated families. Backing: MAX_R6S_ALL_N_COMPOSITION receipt
   (authority ...SUPPORT3_NEVER_PAYS__DXX_EQUALS_DP_ALL_N__NOT_R6).
3. EXACTNESS (the two-trade completeness identity
   `C_DP == min(C_R6L, C_Dplus, f_B)`) — MACHINE-EVIDENCED ONLY, on the
   verified domains: the MAX_R6Q receipt (9,261-instance exhaustive
   structured n=2 slice; two 240-instance seeded panels at n=2..3; 30
   receipted chemistry matchings — identity_two_trade held on all 9,771
   rows) and the MAX_R6R receipt (15 further matchings of a fresh subject,
   predicted before computation, all confirmed). The identity for all n and
   all targets is CONJECTURE. The forecaster's exactness claim inherits
   exactly this status and no more.
4. REGIME CERTIFICATE — the R6Q predicate P1 and the regime label are exact
   on all verified domains (MAX_R6Q outcome EXACT_PREDICATE_FOUND, zero
   confusion errors everywhere; prospectively confirmed by MAX_R6R). Same
   evidenced-not-proven boundary as component 3.

Consequently: wherever the completeness identity holds, the forecast error is
exactly zero. A single reproducible nonzero forecast error on a DP-compared
instance REFUTES the identity on a new instance and is a first-class
discovery, to be reported verbatim, never suppressed.

## 3. Benchmark protocol (all frozen before outcome)

### (a) Correctness — forecast vs committed unrestricted DP

- Domain A — exhaustive structured n=2 slice: the 9,261 instances generated
  exactly as the frozen R6Q training panel (21 unordered weight-one target
  pairs over qubits {0,1}, cubed; identical iteration order; identical
  `r6m._local_table.cache_clear()` every 256 instances). DP truth:
  `r6o.dp_cost_n2_reader` (the committed unrestricted DP reader, bound in
  the R6O receipt). Additional binding gate: recomputed rows must bind to
  the committed R6O receipt via the frozen `r6q.bind_training_to_receipt`.
- Domain B — fresh seeded panel: seed 20260826, generator copied
  digit-for-digit from the frozen `r6q.random_panel` (120 instances at n=2
  and 120 at n=3; 240 >= 200). DP truth: `r6o.dp_cost_frozen_configs`
  (unrestricted frozen-config DP), `r6m._local_table.cache_clear()` before
  each instance exactly as in the frozen generator.
- Domain C — every real library batch already receipted: H4 and
  equilibrium-N2 (frozen `p10.base.SUBJECTS` configs; blob-verified
  `r6f._frozen_batch` load; DP truth taken from the committed
  MAX_R6M receipt `C_R6M` per matching, with `C_R6L_same_matching`, the R6O
  receipt `C_Dplus`, and `frozen_source_indices` all hard-bound — the heavy
  subject DP is NEVER re-run) and Benzene 6Elec_6Orbs DUCC2 (the R6R fresh
  subject; DP truth and stage-1 fields hard-bound to the committed MAX_R6R
  receipt). The protected stretched-N2 subject is NEVER read, listed, or
  fetched; the frozen R6R exclusion list (which excludes the entire N2
  molecule from enumeration) is reused verbatim, making it unreachable.

Correctness gate: forecast error `F(t) - C_DP` must be exactly zero on every
DP-compared instance. Any nonzero error is reported verbatim (instance,
components, DP value) and flips the outcome to the refutation branch below.

### (b) Cost — wall-time of forecast vs DP per instance

- `time.perf_counter` around the forecast computation (C_R6L + C_Dplus +
  f_B) and around the DP call, per instance.
- Domain A timing discipline: warm shared caches exactly as the committed
  R6Q loop (cache clear every 256 instances) — reported as warm-cache
  medians.
- Domain B timing discipline: cold per instance — `r6m._local_table` cleared
  before the DP call and the forecast caches (`r6o._block_cache`,
  `r6q._borrow_block_cache`) cleared before the forecast, per instance.
- Report per domain: median forecast seconds, median DP seconds, and the
  speedup distribution (per-instance DP/forecast ratio: min, p10, median,
  p90, max). Chemistry subjects get forecast-only timing (no DP re-run), and
  are excluded from speedup statistics.
- Determinism convention (R6P): ALL timing fields live exclusively under a
  top-level `timing` key of the RESULTS file and on stderr; the canonical
  stdout receipt line contains NO timing field. Double runs must produce
  byte-identical canonical lines.

### (c) Library forecast table — predictions only

- Enumeration: the frozen R6R machinery reused verbatim —
  `r6r.pinned_tree_listing()` at pinned commit
  be306f5830549304176365750d712093950bbdde of
  npbauman/DUCC-Hamiltonian-Library (git tree listing: paths + blob SHA1s
  only), `r6r.eligible_candidates` (same exclusion list, same active-space
  rule, same n_qubits-then-path order), `r6r.try_admit` (same R6B six-term
  batch admission, blob-verified fetch).
- FROZEN CAP: exactly the first 4 eligible candidates in frozen order are
  attempted (admission may fail; failures are recorded with reasons and kept
  in the table as NOT_ADMITTED rows). This cap is a runtime budget choice
  frozen now, before any admission result is known.
- For every admitted candidate and every one of its 15 matchings: the full
  forecast (components, predicted C_DP, regime, P1, Lambda). Certificate
  status per subject:
  - `DP_RECEIPT_COMMITTED__FORECAST_BOUND` where a committed DP receipt
    exists for that exact blob and batch (H4, eq-N2 via MAX_R6M; Benzene
    6E6O DUCC2 via MAX_R6R) and the zero-error binding passed;
  - `UNVERIFIED_FORECAST__NO_DP_RECEIPT` otherwise. These rows are
    predictions ONLY; they verify nothing and grant no authority.
- The table also records the full frozen eligible-candidate list (path,
  blob, n_qubits) so the enumeration itself is auditable.

## 4. Receipts and determinism

- Single canonical stdout line:
  `ORIONQ_QG5_CERTIFIED_FORECAST=<canonical sorted JSON>` (sorted keys,
  compact separators, no NaN; NO timing fields).
- Pretty RESULTS file:
  `research/extensions/orion-qg/QG5_CERTIFIED_FORECAST_RESULTS.json` =
  canonical payload + the `timing` section (including runtime_seconds).
- stderr: runtime and timing summary lines only.
- Double-run requirement: two full runs must emit byte-identical canonical
  lines.
- Runtime budget: each full run under 25 minutes on the session interpreter.
- All external fetches blob-pinned: every Hamiltonian file read is verified
  against its git blob SHA1 before use (`r6f._frozen_batch` /
  `r6r.try_admit` machinery); the tree listing is taken at the pinned
  commit only.

## 5. Frozen outcome space and authority strings (both contain NOT_R6)

- `FORECASTER_CERTIFIED_ON_VERIFIED_DOMAINS` — every DP-compared instance
  has forecast error exactly zero AND every receipt binding passed.
  Authority: `QG5_CERTIFIED_STATIC_FORECASTER__ZERO_ERROR_ON_ALL_DP_COMPARED_INSTANCES__LIBRARY_TABLE_IS_FORECAST_ONLY__NOT_R6`.
- `COMPLETENESS_IDENTITY_REFUTED_ON_NEW_INSTANCE` — at least one nonzero
  forecast error on a DP-compared instance; all such instances reported
  verbatim. This is a discovery about the identity's boundary, not a lane
  failure. Authority:
  `QG5_FORECAST_IDENTITY_REFUTED__BOUNDARY_INSTANCES_REPORTED_VERBATIM__NOT_R6`.
- Hard assertion failures (receipt-binding mismatch, sandwich violation,
  borrow-soundness violation, blob mismatch, authority-ceiling violation)
  abort the run with no receipt; they are implementation-integrity failures,
  not scientific outcomes.

## 6. Honesty constraints

- The two PROVEN certificate components stay PROVEN, the EVIDENCED component
  stays EVIDENCED, and the all-n identity stays CONJECTURE in every emitted
  artifact; the receipt carries the statuses verbatim.
- `heavy_subject_dp_rerun = false`; `reserved_stretched_n2_accessed = false`;
  `donor_novelty_credit = false`; `novelty_credit = false`;
  `r6_authority = false`; the authority string contains NOT_R6 (hard
  assertion before emission).
- No existing repository file is modified; this lane only adds this
  protocol, `research/extensions/orion-qg/qg5_certified_forecast.py`, and
  the RESULTS JSON from the real run.
