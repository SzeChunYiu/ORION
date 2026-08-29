# ORION02.SELECTIVE_FIBRE_RISK.v1 — theory and design rationale

**Candidate ID:** `ORION02.SELECTIVE_FIBRE_RISK.v1`
**Date:** 2026-08-28
**Status:** `PREREGISTRATION_ONLY__NOT_EXECUTED__NO_SCIENTIFIC_AUTHORITY`
**scientific_authority_delta:** `NONE`
**Protocol freeze:** `false` (freeze is claimed only when PROTOCOL.json is committed and hash-registered before any outcome access)
**Compute performed:** **none.** No data fetched, no PMLB/ASlib download, no run.

Upstream: issue #1608 (ORION-02 section) and
`refs/rev/pr1615:papers/publication_closure/wave2/WAVE2_SUCCESSOR_THEORY_CANDIDATES_2026-08-28.md`
Priority 2 (`ORION02.FIBRE_AMBIGUITY_RISK.v1`, `HYPOTHESIS_ONLY__NO_SCIENTIFIC_AUTHORITY`).

---

## 1. What failed, mechanically

Two independent structural defects made the R24 certificate unable to meet its
registered `0.10` strict-violation cap. Both are properties of the committed
construction, not tuning accidents.

### 1.1 The tau ceiling (range mismatch)

Every pool branch in `fiberguard_pmlb_arm_conditional_r24.py` admits a member
only under `excess <= tau + TOL` (lines `115`, `132`, `198`), with `TAU = 0.02`
inherited from R23 and `TOL = 1e-9`. The certified bound is the pool maximum, so

> `bound <= tau + TOL` **identically, by construction.**

Verified exhaustively over the committed result: 1,760 bound-valued cells,
1,633 non-null, **0** exceeding `tau`, maximum `0.019561442517`
(see `THEORY_CORE_FREEZE_V1.md` §C.3 for the census).

The bound therefore ranges over `[0, tau]` while the realised excess ranges over
`[0, 0.077969870875]` (`primary.max_excess`). Since `certified_fraction = 1.0`,

> `violations_strict >= violations_tau = 11/44 = 0.25 > 0.10`.

**Scope limit, binding.** The *form* of this floor is invariant — pool size,
radius and metric cannot lower it. The *value* `11/44` is **not** invariant: those
levers change which classifier is committed, which changes realised excess. This
design must not be justified by, and must not assert, an unconditional
impossibility "for any pool size, radius or metric".

### 1.2 The exchangeability floor (order-statistic mismatch)

Independently, issue #1608 records that a raw maximum over `K` exchangeable
calibration losses has exceedance probability about `1/3` at `K = 2`. Precisely,
for exchangeable continuous losses,

> `P(L_new > max(L_1,...,L_K)) = 1/(K+1)`.

`POOL_K = 2` gives `1/3 = 0.333... > 0.10`. Reaching `alpha = 0.10` by a maximum
alone requires `K >= 1/alpha - 1 = 9`.

These two mechanisms are complementary: §1.1 caps the bound's *range*, §1.2 caps
the *confidence* a two-element maximum can carry. Either alone defeats the cap.

**Note on `k`.** `POOL_K = 2` is a module-level global for every arm. The `k` in
`LEARNED_KNN_k` is the acquisition regressor's neighbour count and never enters
bound construction. No claim in this design depends on `k` being the pool size.

---

## 2. Why the raw selected maximum must be replaced

The R24 risk functional is the maximum excess over an admitted pool. It is
simultaneously (a) capped by the admission gate that defines the pool, and
(b) a `1/(K+1)`-confidence statistic at `K = 2`. It cannot be repaired by
choosing a better pool: the defect is in the functional.

**The replacement is a finite-sample calibrated selective risk.**

### 2.1 Construction

Let `s(x) in {select, abstain}` be the selection rule and `L(x)` the realised
excess loss. Define selective risk

> `R_sel = E[ L(X) | s(X) = select ]`,

and the certified radius `r_hat` as an order statistic of the loss on the
**calibration-selected** rows — never on a tau-admitted pool, and never on TEST:

> Let `n` = number of CALIBRATION rows with `s = select`, losses `L_(1) <= ... <= L_(n)`.
> Set `r_hat = L_(ceil((n+1)(1-alpha)))`, requiring `n >= ceil(1/alpha) - 1`.

For `alpha = 0.10` this requires `n >= 9`; the protocol registers a far larger
floor for stability (`PROTOCOL.json`, `calibration.min_selected_per_domain`).

Violation rate on TEST is reported with a **one-sided Clopper-Pearson 95% upper
bound**, per issue #1608's gate.

### 2.2 Why this escapes the tau ceiling

`r_hat` is estimated **from the realised loss distribution on a held-out
calibration split**, not read off an admission-gated pool. No branch predicate
caps it. Its range is the range of observed losses, `[0, max L]`, matching the
target's range instead of contradicting it. This removes §1.1.

Using the `ceil((n+1)(1-alpha))`-th order statistic rather than the maximum, with
a registered minimum `n`, gives finite-sample validity at the declared `alpha`
under exchangeability. This removes §1.2.

**Both removals are structural, not empirical. Neither is a claim that the
experiment will succeed.** The design is built so that it can fail — see
`EXPECTED_TERMINALS.json`.

### 2.3 What is deliberately NOT claimed

- No conditional (fibre-wise) validity is claimed by the marginal construction
  above. Fibre-conditional validity is a **separate, harder** target and is
  addressed only by the Mondrian / group-conditional variant registered as a
  secondary arm.
- Exchangeability between CALIBRATION and TEST is an **assumption**, not a
  result. Cross-domain transfer breaks it; that is why validity is assessed
  **within** each domain and never pooled across domains.

---

## 3. Theory obligations (issue #1608) — stated, unproved

Both are recorded as obligations. **Neither is proved here.** Nothing in this
document may be cited as proof.

- **T1 — finite-fibre non-transfer theorem.** Closed-world fibre maxima do not
  imply held-out risk control without explicit additional assumptions. Target:
  identify the minimal assumption set under which transfer holds, and exhibit a
  witness where it fails.
- **T2 — calibrated selective-risk theorem.** Geometry / arm selection separates
  from final risk calibration: selection may be arbitrary (even adversarial)
  provided calibration is performed on a split disjoint from selection, with
  validity depending on selection only through `n`.

### 3.1 The `D(z)/2` diameter floor — HYPOTHESIS_ONLY

From #1615 Priority 2. For a representation fibre `F_z = {x : phi(x) = z}` and
target `V`, with `D(z) = sup_{x,x' in F_z} |V(x) - V(x')|`, any deterministic
point certificate accepted on the whole fibre incurs worst-case absolute error
at least `D(z)/2`; an accepted interval of radius `< D(z)/2` must miss at least
one member; on a balanced two-point distribution on a diameter-attaining pair,
conditional miscoverage is at least `1/2`. On the frozen `A_t / B_t` pair,
`D(z) >= 2t-1`.

This is carried as a **negative control**, not as an assumption of the design.
Observing achievable risk **below** the floor would indicate the theorem is
wrong or the fibre is mis-identified — a registered falsifying outcome.

---

## 4. Donor credit — owed, and stated plainly

The risk functional in §2 is **not new**. It is standard split-conformal /
selective-risk machinery. Explicit credit:

- V. Vovk, A. Gammerman, G. Shafer — *Algorithmic Learning in a Random World*
  (conformal prediction; the `ceil((n+1)(1-alpha))` order statistic).
- J. Lei, L. Wasserman; J. Lei, M. G'Sell, A. Rinaldo, R. Tibshirani,
  L. Wasserman — distribution-free predictive inference / split conformal.
- C. K. Chow (1970) — optimum error-reject tradeoff.
- R. El-Yaniv, Y. Wiener (2010) — selective classification, risk-coverage.
- S. Bates, A. Angelopoulos, L. Lei, J. Malik, M. I. Jordan — risk-controlling
  prediction sets.
- Mondrian / group-conditional conformal — the fibre-conditional variant.
- C. J. Clopper, E. S. Pearson (1934) — exact binomial one-sided interval.

**The only place a residual delta can live** is (i) conditioning validity on a
*representation fibre* — an equivalence class of `phi` rather than a
label/covariate group — and (ii) the `D(z)/2` diameter floor tying representation
ambiguity to achievable risk. Everything else is donor-owned. This design does
not imply the functional is novel.

Consistent with `CLAIM_LEDGER.md` C-C10 / `CLAIM_LEDGER_R2.md` C2-C11
(`DONOR-OWNED`).

---

## 5. Design holes closed explicitly

### 5.1 The 60-selected requirement interacts with abstention

Abstention shrinks the selected count, so "at least 60 selected final-test
decisions per domain" is unsatisfiable if left unqualified. **Resolution:** 60 is
a **post-selection, post-abstention** floor on TEST. The protocol therefore
registers a **pre-selection TEST pool floor** derived from the anticipated
abstention rate:

> `test_pool_min = ceil(60 / (1 - a_max))`, with registered `a_max = 0.40`,
> giving `test_pool_min = 100` per domain.

If a domain cannot supply 100 pre-selection TEST decisions, that domain is
**dropped before outcome access** and recorded as a prerequisite failure — never
back-filled after seeing results.

### 5.2 Four disjoint domains — a prerequisite, not an assumption

The R24 corpus is 44 PMLB datasets and **cannot by itself supply four disjoint
domains**. Named candidates, all already present in the frozen tree:

| Domain | Source in tree | Availability |
|---|---|---|
| PMLB tabular (44 datasets) | `rounds/r22-.../FIBERGUARD_PMLB_R22_DATASET_FREEZE.json` | present |
| ASlib SAT12-ALL | `extensions/r11`, `extensions/r14` | present |
| ASP-POTASSCO | `extensions/r15/FIBERGUARD_MULTIDOMAIN_R15_PROTOCOL.md:23` | present |
| CSP-Minizinc-Time-2016 | `extensions/r15/...:36`; `rounds/r21-direct-relative` | present |
| GRAPHS-2015 | `extensions/r15/FIBERGUARD_MULTIDOMAIN_R15_PROTOCOL.md:49` | present |
| BNSL | `extensions/r20` | present |

Availability must be **verified before freeze** and recorded as a prerequisite.
`FIBERGUARD_TSP_DIRECT_RELATIVE_R21_PREREQUISITE_FAILURE.md` is the precedent for
how a missing domain is recorded rather than substituted. TSP is **excluded** on
that precedent.

Domain-level disjointness replaces R24's fold-role reuse: in R24 the same 44
datasets rotated through proposer-train / shield / test roles across folds
(`folds[*].roles` in `run_a.result.json`). Here, domains are disjoint corpora.

### 5.3 Custody invariant, with a verifiable check

> **INVARIANT.** `r_hat` is derived from CALIBRATION only. TEST never touches
> metric learning, arm selection, or threshold choice.

**Verifiable check (registered, must be implemented as an executable assertion):**
each split emits a sorted SHA-256 manifest of its instance identifiers; the
executor asserts pairwise-empty intersection of TRAIN / CALIBRATION / TEST
manifests, and asserts that the recorded `r_hat` value is bit-identical to the
value recomputable from the CALIBRATION manifest alone. Any TEST identifier
appearing in a fitting or thresholding trace is a hard executor failure, not a
warning.

---

## 6. Standing-doctrine note

`PROMOTE_CONDITIONALLY` is an **intermediate** terminal, not a stopping point. A
regime-conditional positive obligates a further iteration that either extends the
working regime or diagnoses the failing one. A conditional positive here must
name the failing domain and register the next lever before any promotion is
considered.

Issue #1608's stop rule is registered and binding: **if the lexical or learned
control matches geometry after valid calibration, stop rehabilitating geometric
transfer and publish the boundary result.** That is a legitimate, publishable
terminal, not a failure to be revived.
