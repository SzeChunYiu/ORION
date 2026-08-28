# ORION-02 — theory core freeze V1

**Document ID:** `ORION02.THEORY_CORE_FREEZE.V1`
**Date:** 2026-08-28
**Status:** `RECORD_ONLY__NO_SCIENTIFIC_AUTHORITY`
**scientific_authority_delta:** `NONE`
**Protocol freeze:** `false` · **Manuscript authority:** `NONE` · **Submission authority:** `false`

This document records which results form the paper's correct core, with exact
scope, assumptions and exclusions. It promotes nothing. It does not soften any
preserved adverse or `CANNOT_CHECK` finding. Where the manuscript uses an
assumption without declaring it, this freeze records the gap rather than
repairing it; repair belongs to the authors, and the analysis is in
`INDEPENDENT_PROOF_REVIEW_V1.md`.

---

## 0. The categorical split this freeze enforces

Two different objects live in `papers/orion-02-fiberguard-finite-fibre/`, and
they must never share a status table:

| Object | What it is | Epistemic class |
|---|---|---|
| **Theory core** (Part A) | Pure combinatorics on one frozen Pauli-partition compiler | Proven theorems, all-`m` / all-`t` / all-`q` |
| **FiberGuard empirical programme** (Part C, `extensions/`, `rounds/`) | Attempts to build a usable certificate on PMLB / ASlib / CSP-MZN | Adverse; terminal `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID` |

The manuscript itself already keeps these apart: a raw grep of
`MANUSCRIPT_V2.md` for `fiberguard|pmlb|aslib` returns **0 matches**. That
separation is a property worth preserving and is recorded here as verified.

**This freeze must not be read as "the theory is fine, only the empirics
failed."** The empirical programme is a preserved adverse record with its own
standing (Part C), and the theory core carries undeclared assumptions
(Part B.3).

---

## Part A — the paper's correct core

Source of statements: `papers/orion-02-fiberguard-finite-fibre/MANUSCRIPT_V2.md`.
Source of status: `CLAIM_LEDGER.md`, `CLAIM_LEDGER_R2.md`.

### A.1 Global scope conditions (bind every result in Part A)

Every theorem below holds **only** under all of:

1. **Frozen compiler grammar.** Instance = ordered tuple of nonidentity Pauli
   strings `p_1,...,p_m`; compiler chooses a set partition `Pi` with
   factor/ancilla options (`MANUSCRIPT_V2.md:46`).
2. **Frozen structural objective** `SELECT+PREP+WIDTH`, with the cost formula
   at `MANUSCRIPT_V2.md:50-60`:
   `C(Pi)=2m+|Pi|-3 + sum_S d(|S|) + max_S b(|S|) + sum_S [2f(S)+(b(|S|)+2)(w(S)-|S|f(S))]`,
   `b(s)=ceil(log2 s)`, `b(1)=0`, `d(1)=0`, `d(s)=d(ceil(s/2))+d(floor(s/2))+s-2`;
   unary incumbent `C_U=2W+3m-3`.
3. **Costs are structural, not physical.** Explicitly not T counts, circuit
   depth, runtime, qubits, or fault-tolerant overhead (`MANUSCRIPT_V2.md:64`).
4. **Not a computational-hardness statement.** These are information /
   representation lower bounds (`CLAIM_LEDGER_R2.md` C2-C12, status
   `FORBIDDEN`).

### A.2 Frozen core results

| Ledger ID | Statement (as frozen) | Scope / assumptions | Status |
|---|---|---|---|
| **C-C1 / C2-C1** | For every `m>=5`, `min_Pi C(Pi)=C_U` iff `P4(m)`: (i) `g_ij<=0` for every pair, (ii) `g_ij+g_kl+1<=0` for every two disjoint pairs, where `g_ij=4f({i,j})-(w_i+w_j)`. Largest clause touches four term indices. | A.1; **plus two assumptions the manuscript does not declare — see B.3(a) integrality and B.3(b) dominance** | PROVEN-ALL-M *conditional on B.3* |
| **C-C2 / C2-C2** | Threshold sharp at `m=4`: registered instance `XXII, XYII, XZII, XIXX` satisfies both clause families yet `C_U=27 > 23` one-block cost. | A.1; single registered instance; **plus the missing single-block cost convention — see B.3(f)** | `C_U=27` **PROVEN-EXACT** (independently reproduced from `w=(2,2,2,3)`, `W=9`); the one-block cost `23` is **CANNOT_CHECK** — not derivable from anything stated in the manuscript (`INDEPENDENT_PROOF_REVIEW_V1.md` §2.3) |
| **C-C3 / C2-C3** | For every `t>=1` there exist `5t`-term instances `A_t,B_t` with identical ordered weights and identical complete labeled pair-gain matrices, both strictly beating unary, with `Delta_A=12t-2`, `Delta_B=10t-1`; value gap `2t-1` is unbounded. | A.1; **plus the cross-gadget separability lemma the manuscript does not state — see B.3(c)** | PROVEN-ALL-T *conditional on B.3(c)* |
| **C-C4 / C2-C7** | Complete pair information does not determine whether an optimal triple block exists: every optimum in `A_t` contains a distinguished triple block; every optimum in `B_t` is forced to pairs and singletons only. | A.1; same fibre as C-C3 | PROVEN-ALL-T *conditional on B.3(c)* |
| **C-C5 / C2-C8** | For every `m>=5, L>=1`, two instances agree on all labeled common-factor counts through order `m-2` yet differ in exact improvement by `[m(ceil(log2 m)+1)-1]L`. | A.1; **plus the padding-uniqueness assumption — see B.3(d)**; argument depends on C-C6 (forward reference, B.3(e)) | PROVEN-ALL-M,L *conditional on B.3* |
| **C-C6 / C2-C9** | (Theorem 4, proper-marginal kernel) If all proper upper marginals `M(T)=sum_{S superset T} delta(S)` vanish, then `delta(S)=(-1)^(q-|S|)c` with `c=delta([q])`. | Boolean upper-marginal representation; integer-valued `delta` | PROVEN-ALL-Q — **proof independently checked and found complete** (`INDEPENDENT_PROOF_REVIEW_V1.md` §2.6) |
| **C-C7** | Such a trade touches all `2^q` cells with signed mass `2^(q-1)|c|` per side; the primitive parity trade is sharp. | C-C6 + parity count | PROVEN-EXACT |

### A.3 Minimax corollaries (Theorem 2 family) — scope is narrower than the abstract states

| Ledger ID | Statement | Binding restriction |
|---|---|---|
| C2-C4 | Real pair-only minimax additive radius `(2t-1)/2`; integer radius `t`. | **Deterministic** estimators only (`MANUSCRIPT_V2.md:104`), input exactly = term count + ordered weights + complete labeled pair-gain matrix |
| C2-C5 | Symmetric factor `>= sqrt((12t-2)/(10t-1))`; no uniform factor strictly below `sqrt(6/5)`. | Same; positive values, stated symmetric convention. The ratio **increases toward** `sqrt(6/5)` and never attains it — "no uniform factor strictly below" is the correct form; "at least `sqrt(6/5)` for each `t`" would be false |
| C2-C6 | One-sided upper/lower factor tends to at least `6/5`. | Same; stated one-sided convention; **asymptotic** |

**Recorded defect:** the deterministic restriction is stated at
`MANUSCRIPT_V2.md:104` and conceded in Limitation 4 (`:196`), but is **absent**
from the abstract (`:15`, `:19`) and from the §5 conclusion (`:132`). This is
carried as `LA-01/02/03` in `LANGUAGE_AUDIT_V1.md` and corrected there.

---

## Part B — exclusions and undeclared assumptions

### B.1 Open, explicitly not claimed
- **C-C8 / C2-C10** — minimality of C3's common padding. `OPEN`. Only the
  *difference trade* is proved minimal (`MANUSCRIPT_V2.md:112`).
- **C-C9** — that the separation is multiplicative or transfers to all
  objectives/grammars. `OPEN / not claimed`.
- Cross-objective and cross-grammar transfer (`MANUSCRIPT_V2.md:199`).

### B.2 Donor-owned — outside the residual contribution
- **C-C10 / C2-C11** — Markov bases, marginal fibres, Möbius inversion, generic
  lower-order insufficiency. `DONOR-OWNED`.
- Additional donor credit **owed but not currently given**: Rota (Möbius
  inversion on a finite poset) for Theorem 4, and the Le Cam / Tsybakov
  two-point minimax lineage for Theorem 2. See
  `INDEPENDENT_PROOF_REVIEW_V1.md` §3.2.
- **C2-C12** — `FORBIDDEN`: this is not a computational hardness theorem.

### B.3 Assumptions used but not declared in the manuscript

These are load-bearing. Each is recorded, not repaired.

- **(a) Integrality of weights.** Theorem 1's proof sketch uses "integrality
  prevents two disjoint pair blocks from simultaneously attaining zero gain"
  (`MANUSCRIPT_V2.md:80`), and the `+1` in clause (ii) is an
  integrality-derived strengthening of `g_ij+g_kl<0`. §2 introduces `w_i` as
  "term weight" with no integrality declaration (`:46`).
- **(b) Dominance of factoring / shared width.** "Under the frozen equal-weight
  structural objective, factoring and shared width dominate their alternatives"
  (`:46`) is asserted without proof or lemma reference, and the reduction to
  four-index clauses depends on it. If assumed rather than proved, **Theorem 1
  is conditional**.
- **(c) Cross-gadget blocks.** §4 builds `t` **disjoint** five-term gadgets
  (`:88`) but the optimizer ranges over all set partitions of all `5t` terms,
  including blocks spanning gadgets. The cost function is **not additively
  separable** across gadgets: `max_S b(|S|)` in A.1(2) is a single global term
  over all blocks. "Exact decomposition gives `Delta_A(t)=12t-2`" (`:90-94`)
  therefore needs a lemma that cross-gadget blocks never help. **This is the
  most consequential undeclared step; Theorem 2's entire premise rests on it.**
- **(d) Padding uniqueness.** §6 adds "identical all-term padding that makes the
  single block uniquely optimal" (`:142`). Uniqueness is asserted, not proved,
  and is distinct from the minimality that C-C8 openly leaves open. If
  uniqueness fails, the `Delta` computation in C-C5 breaks.
- **(e) Forward reference.** §6's premise (agreement through order `m-2`) is
  justified by §7's kernel theorem, presented after it.
- **(f) The single-block cost convention is never stated.** The §2 cost formula
  is explicitly introduced "For `|Pi|>=2`" (`MANUSCRIPT_V2.md:48`), and `:62`
  says "The single-block flag convention is treated separately" — but that
  convention appears nowhere in the manuscript. It is **load-bearing for three
  separate results**: C-C2's one-block cost `23`; Theorem 1's proof step "the
  exceptional one-block formula is bounded separately" (`:80`); and §6's
  reliance on a single block being optimal. Applying the `|Pi|>=2` formula to
  the single block anyway yields `32`, not `23` — which is not evidence of an
  error, but evidence that the missing convention is doing real work
  (`INDEPENDENT_PROOF_REVIEW_V1.md` §2.3).
- **(g) "Equal-weight" is ambiguous and conflicts with the rest of the paper.**
  §2 (`:46`) says "frozen **equal-weight** structural objective", yet §5 (`:104`)
  feeds the estimator "**ordered weights**", and the registered `m=4` instance has
  unequal weights `(2,2,2,3)`. Either the phrase means equal weighting of the
  `SELECT`/`PREP`/`WIDTH` components rather than equal term weights, or it is
  wrong. The two readings give different theorems
  (`INDEPENDENT_PROOF_REVIEW_V1.md` §2.2c).

### B.4 Publication-posture tension (recorded, not resolved)
`MANUSCRIPT_V2.md:220` carries
`R2 status: TOP_TIER_THEORY_CANDIDATE__AUTHOR_SIDE_PRIMARY_SOURCE_BLOCKER_SUBSTANTIALLY_CLOSED`
directly above an **External-only gates** list (`:222`) that still includes
*independent proof audit*. A status token reading `SUBSTANTIALLY_CLOSED` above
an open proof-audit gate is a tension for the orchestrator to adjudicate.

---

## Part C — the tau-ceiling: verified structural property of a committed pipeline

**Epistemic class: NOT a theorem of the paper.** This is a verified property of
the R24 executor implementation on the PMLB corpus. It is recorded here because
it explains the R24 terminal, and it is kept in its own section so it can never
be mistaken for Part A.

### C.1 Custody
All numbers below are from branch `codex/revive-orion02-r24-20260828`
(fetched as `refs/rev/pr1598`), path
`papers/orion-02-fiberguard-finite-fibre/rounds/r24-arm-conditional-fibres-revival/`.

Independent-verify custody confirmed by this freeze:
`failed-executions/3550275/run_a.result.json` and `run_b.result.json` are
**byte-identical** — both resolve to git blob `1fe5f16cb22ebf8611e29de3b48a48b6ce496b16`.
`run_a.terminal.txt` and `run_b.terminal.txt` are likewise byte-identical
(blob `d6f889792ba84f20f5547d5eef9f2b2d415f3f7a`), both reading
`C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID`. `STAGE.txt` = `INDEPENDENT_VERIFY_A`,
`WRAPPER_EXIT_CODE.txt` = `1`.

### C.2 Committed constants
- `TAU = 0.02` — `rounds/r23-density-backoff-revival/fiberguard_pmlb_proposal_ordering_r23.py:51`,
  imported at `rounds/r24-.../fiberguard_pmlb_arm_conditional_r24.py:59` as `TAU = r23.TAU`.
- `TOL = 1e-9` — `fiberguard_pmlb_arm_conditional_r24.py:21`.
- `POOL_K = 2` — `fiberguard_pmlb_arm_conditional_r24.py:24`, and `pool_k: 2`,
  `tau: 0.02` in the `r24_mechanism` block of `run_a.result.json`.

### C.3 The mechanism (invariant part)

Every pool-construction branch admits a member only under the predicate
`excess <= tau + TOL`:
- `arm_conditional_boundary_pool` — `fiberguard_pmlb_arm_conditional_r24.py:115`
- `lexical_good_boundary_pool` — `:132`
- exact-cell preservation branch — `:198`

Because the certified bound is `bound = max(excess over pool)` and every pool
member satisfies the same gate, **`bound <= tau + TOL` identically, by
construction**. `POOL_K`, the Hamming radius rule and the distance/tie-break
metric are all irrelevant to this conclusion: they change *which* members enter
the pool, never the admission predicate that caps them.

**Independent verification performed by this freeze.** Exhaustive census of
every bound-valued cell in `run_a.result.json` (recursive walk over
`arm_bounds`, `bound`, `best_bound` under `coverage_records` and `folds`):

| Quantity | Value |
|---|---|
| bound-valued cells enumerated | 1,760 |
| non-null bounds | 1,633 |
| non-null bounds exceeding `tau = 0.02` | **0** |
| maximum bound observed | `0.019561442517` (`R24_ARM_CONDITIONAL_BOUNDARY_FIBRES` / `breast_cancer` / `logreg`) |

The bound's range is `[0, tau]` **by construction**, while the target excess
ranges over `[0, max_excess]` with `max_excess = 0.077969870875`
(`primary.max_excess`). This is a structural range mismatch, not a tuning
failure.

**Provenance note on the figure "704".** The brief cites 704 rows. That figure
does not appear in `FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_RESULT.md` (grep count
0) and is not reproducible as an exact row count from `run_a.result.json`; it is
consistent with `2 policies x 8 folds x 44 datasets = 704`, but the committed
`folds` object holds 9 fold keys (`0`-`8`) per policy, giving 792 under that
slicing. This freeze therefore relies on the exhaustive 1,633-cell census above,
which is a **superset** check and leaves the mechanism conclusion unaffected.
The number 704 is not repeated as verified.

### C.4 The floor, and exactly how far it reaches

From `primary` in `run_a.result.json`:
`certified_n = 44`, `certified_fraction = 1.0`, `violations_strict = 20`,
`violations_tau = 11`, `mean_bound = 0.01001183906`,
`mean_excess = 0.016287757328`, `p95_excess = 0.061509651522`.

Since `bound <= tau` identically, any certified row whose realised excess
exceeds `tau` is a strict violation. Hence

> `violations_strict >= #{certified rows with excess > tau} = violations_tau = 11/44 = 0.25`

Because `certified_fraction = 1.0`, the certified set is the whole set, so
"certified rows with excess > `tau`" is simply "rows with excess > `tau`" — no
selection-conditioning subtlety arises, and the step is unconditional **for this
run**. The registered strict-violation cap was `0.10`, so that gate was
**structurally unreachable** for this committed-classifier assignment.

### C.5 Scope limit — binding

- **Invariant:** the *form* of the floor. `bound <= tau + TOL` holds for every
  pool the R24 construction can produce; pool size, radius and metric cannot
  lower it.
- **NOT invariant:** the *value* `11/44`. It is a function of the realised
  excess vector under the committed classifier assignment. Changing pool size,
  radius or metric changes which classifier is committed, which changes realised
  excess, which changes the count.
- **This does NOT license** an unconditional impossibility claim "for any pool
  size, radius or metric". Any such wording is out of scope and must not be
  written.

---

## Part D — preserved adverse findings (undiluted)

1. Terminal: `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID`. Paper freeze withheld.
2. Coverage rose `32/44 = 0.727272727273` (R23) to `44/44 = 1.0`, meeting the
   registered `0.95` gate — **and validity still failed**: `20/44 = 0.454545454545`
   held-out strict violations against a registered `0.10` cap.
3. **The matched no-geometry LEXICAL control also covered `44/44`, with FEWER
   violations (14 vs 20).** Geometry supplied no value over lexical.
4. R24 vs R23 parent: mean paired excess difference `-0.008448463125`, but the
   20,000-bootstrap 95% interval `[-0.018359034781, 0.000107770719]`
   **crosses zero**.
5. Against the matched lexical control: mean difference `+0.000323174048`,
   interval `[0.0, 0.000969522145]` — geometry does not supply value on the
   frozen corpus.
6. Attempt accounting: counted adverse attempt 2 of 100; 98 remain.

Source for 1-6: `refs/rev/pr1598:papers/orion-02-fiberguard-finite-fibre/rounds/r24-arm-conditional-fibres-revival/FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_RESULT.md`,
corroborated for 2 by `primary` in `run_a.result.json`.

---

## Part E — what this freeze does NOT do

- Does not promote any claim. `scientific_authority_delta: NONE`.
- Does not repair B.3(a)-(e); it records them.
- Does not treat `ORION02.FIBRE_AMBIGUITY_RISK.v1` or the `D(z)/2` diameter
  bound as established. That candidate is `HYPOTHESIS_ONLY__NO_SCIENTIFIC_AUTHORITY`
  per `refs/rev/pr1615:papers/publication_closure/wave2/WAVE2_SUCCESSOR_THEORY_CANDIDATES_2026-08-28.md`.
- Does not license any successor experiment. The design in
  `experiments/selective-fibre-risk-v1/` is preregistration only, unexecuted.
