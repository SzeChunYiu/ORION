# Q1-XOVER crossover/resource evaluation protocol (V1)

Date frozen: 2026-08-27
Paper lane: ORION-05 (`papers/orion-05-tare-expressivity/`), plan §3 gate
`Q1-XOVER` of `papers/PAPER_PORTFOLIO_REFACTOR_PLAN_V1.md`.
Status: FROZEN BEFORE ANY Q1-XOVER RUN.
Authority ceiling: exact crossover/resource accounting over the frozen R6 stack.
No new theorem authority, no novelty credit, no new subject data beyond the one
fresh public subject admitted by the frozen R6R selection rule below.

## Scientific question

ORION-05 §1 states the representation-count corollary
`(3n + 9*C(n,2))^6 = O(n^12)` for the support-two active core `D++` against the
unrestricted family `(4^n - 1)^6`, with an explicit disclaimer that no DP
acceleration is claimed. The paper currently has no exact crossover table. Q1-XOVER
quantifies, with exact numbers per resource regime:

> **Where does the support-two active core beat the strongest available baseline,
> and where does it lose?**

Three resource axes are swept: instance size `n`, instance structure, and compute
budget (wall-clock / memory feasibility). "Strongest available baseline" is defined
per regime, honestly:

- exact-quality regime: the unrestricted production DP referee `r6m.exact_r6m_matching`
  (`C_DP`). The active core can at best TIE quality here; its wins are family size,
  witness support, and any wall-clock regime where the direct `D++` search completes
  faster. It LOSES wall-clock wherever the DP's O(n) sweep beats the O(n^12)-family
  direct search.
- practical-family regime: the support-one enlarged donor family `r6o.dplus_pairs`
  (`C_Dplus`), the previously registered cheapest exact-over-family optimizer. The
  active core wins exactly on the critical set `{C_Dplus > C_DP}` (quality gap closed
  at the price of higher search cost).
- donor-referee cross-check: `r6m.donor_r6l_matching` (`C_R6L`) for the sandwich
  `C_DP <= C_Dxx <= C_Dplus` and `C_DP <= C_R6L`.

## Frozen arms (registered modules, imported UNMODIFIED)

| Arm | Call | Family size (six-frame tuples) |
|-----|------|-------------------------------|
| A_DPLUS | `max_r6o_enlarged_tag_donor_closure.dplus_pairs` | `(3n)^6` |
| A_DXX | `max_r6p_weight2_frame_donor_closure.dxx_search(max_weight=2)` | `(3n+9*C(n,2))^6` |
| A_DP | `max_r6m_exact_three_tare2_shared_factor_dp.exact_r6m_matching` | `(4^n-1)^6` |
| C_R6L | `max_r6m_exact_three_tare2_shared_factor_dp.donor_r6l_matching` | (cross-check) |

## Frozen resource regimes

### R1. Size x structure panel sweep (synthetic instances)

Seed: `20260827` (frozen; distinct from R6P's `20260821` so the random panels are
fresh draws, cross-checkable against the registered R6P counts).

Structure generators (all deterministic given seed; instances are six targets
grouped into ordered pairs `((t0,t1),(t2,t3),(t4,t5))`, nonzero Paulis as `(x,z)`
bitmask pairs via `p10.codes`):

1. `uniform` — each target sampled uniformly from the `4^n - 1` nonzero Paulis
   (same law as the registered R6P random panel, fresh seed).
2. `commuting_symmetric` — `z = A*x` over F_2 with `A = D + P + P^T`, `D` a random
   diagonal, `P` a random partial permutation matrix with `n//2` ones; `x` a random
   nonzero bitmask. Symmetry of `A` makes all six targets pairwise commuting
   (chemistry-like syndrome), the regime where ORION-05 §6 observes all-equal costs.
3. `lowweight` — uniform over the wt<=2 Pauli set via rejection sampling from
   `uniform` (the active core's exact native family; probes whether `D++` saturates
   its family at low weight and where uniform/lowweight critical counts diverge).

Panel sizes (frozen; shrink with n because per-instance cost grows):

| n | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| instances/family | 24 | 32 | 32 | 24 | 12 | 4 |

Notes: at n=1 `lowweight` equals `uniform` in distribution (all nonzero Paulis have
wt<=1); both cells are still run as independent draws and the overlap is recorded.
Direct A_DXX is attempted on every panel cell with n<=6 (see budget).

### R2. Family-size exact table

Exact integer counts `4^n - 1`, `3n + 9*C(n,2)`, `3n` raised to the 6th power for
n = 1..20, plus the per-block ordered anticommuting wt<=2 pair count independently
recounted by this runner and asserted equal to
`max_r6s_all_n_composition.PAIR_COUNTS_SUPPORT2[n]` for n in {1,2,3,4}
(registered: 6, 120, 666, 1968). Integer crossover identification: identity
`active_core_family == unrestricted_family` for n<=2, strict `<` for n>=3.

### R3. Chemistry scale-out (registered public subjects)

Subjects from `max_r5h_mixed_cardinality_development.SUBJECTS`: H4 (n=8) and N2
(n=12), pinned DUCC library commit `be306f58...`, fetched via the registered
`r6f._frozen_batch` + blob verify. All `r6m.perfect_matchings(six)` evaluated per
arm. Direct A_DXX is NOT attempted: a-priori memory infeasibility (below).

### R4. Fresh-subject prospective lane (R6R machinery reused)

Selection reuses `max_r6r_prospective_fresh_subject` imported UNMODIFIED:
`pinned_tree_listing`, `eligible_candidates` (order: n_qubits asc, path asc,
CANDIDATE_CAP=6), `try_admit`. Frozen admission rule for THIS run: molecule-level
exclusion `{H2, H2O, H4, LiH, N2}` (the R6R set; N2 molecule excluded entirely),
BLOB-level exclusion of the four previously read subject blobs (the three R6R
`COMMITTED_SUBJECT_BLOBS` plus the benzene DUCC2 blob `5c02c72b...` read by R6R
itself). Next eligible unread candidate under that rule (deterministic): a
benzene/cc-pVDZ DUCC3 n=12 Hamiltonian. Staging: `r6r.stage1_predict` (donor-exact
prediction, digest printed BEFORE the referee) then `r6r.stage2_referee`
(unrestricted DP). Resource annotation layer added by this runner only: timing and
arm-level family accounting around the registered calls.

## Compute-budget rules (frozen, with justification)

- **Direct A_DXX per-instance budget: 600 s wall-clock**, enforced by forked child
  process with timeout; a timed-out cell records `dxx_status = TIMEOUT` and the
  timing receipt carries it as machine-dependent feasibility-boundary data.
  Justification: the `dxx_search` zeta transform allocates `M = 4^(2n)` int64
  arrays per level; measured registered runtimes grow ~an order of magnitude per n
  (R6P: full 313-instance n<=3 sweep in 440 s total), so 600 s bounds each n<=6
  cell while keeping the worst-case job under the sbatch walltime.
- **A-priori direct-D++ infeasibility rule: direct A_DXX attempted iff n <= 6.**
  Memory arithmetic: `M = 4^(2n)` int64 = `8 * 4^(2n)` bytes; n=7 -> 2.15 GiB per
  array plus the zeta working set (multiplicative constant >= 3 observed) exceeds
  a 16 GiB node allocation; n=8 -> 34.4 GiB; n=12 -> 2.25e14 bytes. This rule is a
  declared feasibility boundary, NOT a claim that the active core "loses" at n>=7:
  the theorem guarantees a support-two optimum exists; only the *direct brute-force
  over the family* is infeasible. The paper-facing statement separates "optimum
  containment" (all n) from "direct family search feasibility" (n<=6 on 16 GiB).
- **Node budget: 16 GiB, 240 min walltime** (sbatch `-t 240`, `--mem=16G`), covering
  the worst case of 12 n=6 direct-A_DXX cells at the 600 s cap plus the n=5 band.
- **Determinism discipline**: all costs, witnesses, counts and cell structures are
  deterministic given the seed; every wall-clock number, timeout status, hostname,
  python/numpy version lives ONLY in `Q1_XOVER_TIMING_V1.json` (machine-dependent
  receipt). `Q1_XOVER_RESULTS_V1.json` is deterministic modulo the documented
  `machine_dependent_keys` (timeout cells mark `C_Dxx = null`). Determinism is
  checked by a double-run of the full n<=3 panel core in the same job, byte-compare
  after stripping `machine_dependent_keys`.

## Frozen predictions (staged, theorem-backed only; digest before referee)

Stage-0 predictions committed (SHA-256 of the prediction block printed to stdout
and embedded in the receipt BEFORE any A_DP call on each lane):

- P1 (Theorem 1, all-size): for every executed direct A_DXX cell, `C_Dxx == C_DP`.
- P2 (sandwich, registered): everywhere `C_DP <= C_Dxx <= C_Dplus` and
  `C_DP <= C_R6L`.
- P3 (family-size identity): `active_core_family(n) == unrestricted_family(n)` iff
  n<=2; strict `<` for n>=3 up to 20.
- P4 (witness support): total six-frame support of every verified A_DXX witness
  `<= 12`; A_DP witness support recorded (unbounded a priori).
- P5 (R6Q two-trade identity, fresh subject): predicted
  `C_DP == min(C_R6L, C_Dplus, f_B)` on all 15 matchings, with the R6Q regime
  label matching the observed argmin structure.
- P6 (a-priori feasibility rule): direct A_DXX attempted iff n<=6; chemistry cells
  record `dxx_status = A_PRIORI_INFEASIBLE_N_GT_6`.

## Honest outcome space

- `CROSSOVER_EVALUATION_CONFIRMED` — P1..P6 hold, all integrity gates pass, every
  cell executed or explicitly bounded.
- `PREDICTION_REFUTED` — any P fails; the refuting rows are reported verbatim
  (this is a valid discovery, e.g. a `C_Dxx != C_DP` cell would reopen the
  exchange argument; a `C_Dplus < C_DP` cell would indicate a registered-code
  defect).
- `RUN_INCOMPLETE` — infrastructure/budget failure after one revival attempt;
  partial cells reported with explicit coverage accounting.

## Integrity gates

1. Content hashes (SHA-256) of the protocol document, the runner, and every
   local `sys.modules` entry under `research/extensions/orion-q/` embedded in the
   receipt; import of registered modules must not modify them (checked by git
   status at commit time).
2. `r6p.EXPECTED_PAIR_COUNTS` runtime extension: the committed guard dict covers
   only n in {1,2,3}. This runner recounts the ordered anticommuting wt<=2 pair
   count independently for n in {4,5,6}, asserts the n=4 recount equals
   `r6s.PAIR_COUNTS_SUPPORT2[4] = 1968`, then sets the recounted values into
   `r6p.EXPECTED_PAIR_COUNTS` (in-memory amendment, committed file untouched,
   recorded in the receipt under `guard_extensions`). Without it the guard raises
   KeyError at n>=4 — evidence the committed direct search never ran at n>=4.
3. Every stored A_DXX witness re-verified by `r6p.verify_dxx_witness`; every A_DP
   result carries the referee's internal checks (it raises on failure).
4. `r6m._local_table.cache_clear()` and `r6o._block_cache.clear()` between
   instances (registered hygiene).
5. Receipt mode `x` for all output files (job fails if outputs pre-exist).
6. No network to crypto/exchange platforms (binding LUNARC rule; the only network
   is the pinned DUCC library GitHub fetch used by the registered subject loader).

## Runtime and outputs

Runner: `research/extensions/orion-q/q1_crossover_evaluation.py`
(env-configurable: `Q1XOVER_SEED`, `Q1XOVER_DXX_BUDGET_S`, `Q1XOVER_SMOKE`;
CLI `--smoke` runs a 4-instance n<=2 sanity core with no network).

Outputs (written by the LUNARC job, mode `x`):
- `research/extensions/orion-q/Q1_XOVER_RESULTS_V1.json` — deterministic receipt.
- `research/extensions/orion-q/Q1_XOVER_TIMING_V1.json` — machine-dependent
  receipt (timings, timeouts, host, versions).
- `research/extensions/orion-q/Q1_XOVER_RESULTS_V1.md` — authored after the run
  from the receipts; carries the crossover statement ORION-05 will cite.

## Claim boundary

This gate produces an exact crossover/resource table for the frozen grammar. It
does NOT claim a new theorem, does not certify the DP accelerated, does not claim
the active core is "faster in general" (the table itself will show where it is
slower), and does not modify any registered module. Chemistry and fresh-subject
results corroborate; they do not extend ORION-05's claim boundary.
