# ORION-Q N2-F3 — Partial-evidence route selection with typed QUERY / CANNOT_COMPARE (frozen protocol)

Date frozen: 2026-08-21 (before any outcome artifact exists)
Parent programme: #633; lane issue: #675 (successor family 3); immutable prior negative: #671
Branch: `claude/orion-harness-verification-b17qdj`
Status: **PROTOCOL FREEZE BEFORE OUTCOMES.** The runner `research/extensions/orion-q/nlanes/n2_f3_partial_evidence.py` implements exactly this document; gates below are prespecified and will be reported honestly whatever they yield.

## Registered design being executed (from #675, authoritative text)

> **Partial evidence:** intervals/unknown constants; decisions include `QUERY`, `CANNOT_COMPARE`, Pareto set.

Successor families 1–2 of #675 (multi-route regimes, vector resources) are treated as absorbed in spirit by the MAX lane (`MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json`, `MAX_R5_N2_JOINT_INTERNAL_CONFIRMATION_RESULTS.json` — the "N2" there is the nitrogen molecule, unrelated to this lane) and are not re-executed here. This protocol executes family 3 only.

## Exact-synthetic world (frozen)

Two QSVT-descended routes per instance, with vector resources (queries q, ancillas a, classical preprocessing p):

- Route `S` (standard block-QSVT proxy): `q_S = c_std * L * lam * d`, `a_S = floor(log2(L)) + 2`, `p_S = L`.
- Route `R` (randomized proxy): `q_R = c_rnd * (lam*d)^2`, `a_R = 1`, `p_R = 0`.

Component transform for comparison: `f_c = log10(1 + resource_c)` per component (frozen; keeps decades comparable).

Admissible downstream-context weight polytope `W`: `w = (w_q, w_a, w_p)`, `w >= 0`, `sum w = 1`, `w_q >= 0.5`. Vertices: `(1,0,0)`, `(0.5,0.5,0)`, `(0.5,0,0.5)`. The true per-instance weight `w*` is drawn uniformly from `W` and revealed only at scoring.

`SEED = 20260821`. All draws from `numpy.random.default_rng(SEED + fixed offsets)`; no wall-clock, no environment input.

### Worlds

- `W_PRIMARY` (400 instances): `L in {4,8,16,32,64,128}` uniform choice; `lam = 10**U(-0.3, 0.9)`; `d in {4,8,16,32,64,128}` uniform choice; true constants `c_std, c_rnd ~ U(0.5, 2.0)`. Evidence: mechanism sees only intervals containing the truth. Interval width ratio `rho = 1.05` (tight) or `rho = 2.5` (wide), each with probability 0.5; `lo = c_true * rho**(-u)`, `hi = lo * rho`, `u ~ U(0,1)`.
- `W_ADV_DECIDABLE` (hostile, 100 instances; refusing to compare is wrong here): `L = 2`, `d = 256`, `lam ~ U(2,3)`, wide intervals (`rho = 2.5`). By construction route `S` certainly dominates over all of `W` and all interval realizations. Any abstention or query here is a mechanism failure.

### Actions and scoring (frozen)

- Point decision `X`: loss = regret `w*·f(X) - min_Y w*·f(Y)` at true constants.
- Set answer `{S,R}` (`CANNOT_COMPARE` / Pareto set): loss = mean member regret (expected regret of a uniform pick).
- `QUERY`: pays `query_price = 0.02` loss units, then receives exact constants and re-decides.
- Oracle arm loss is 0 by definition (knows `c` and `w*`).

## Candidate ORION mechanism (typed partial evidence; frozen decision procedure)

1. **Certain dominance over `W`:** `DECIDE X` iff for every vertex `w` of `W`: `w·f_X(worst-case constants for X) - w·f_Y(best-case constants for Y) <= 0`.
2. Else **pivotality test** at evidence corners: realization `A = (c_std_lo, c_rnd_hi)`, `B = (c_std_hi, c_rnd_lo)`. Pivotal iff `S` dominates over `W` at `A` or `R` dominates over `W` at `B`.
3. Pivotal: emit `QUERY` (pay price), receive exact constants, re-run vertex dominance with point constants; dominance -> `DECIDE`, else -> `CANNOT_COMPARE` with Pareto set `{S,R}`.
4. Not pivotal: `CANNOT_COMPARE` with Pareto set `{S,R}`, no query (constants cannot settle it; only `w*` could).

## Strongest non-ORION baselines (first right of refusal)

- `B1_scalarized_midpoint`: constants = interval midpoints, `w` = centroid of `W` = `(2/3, 1/6, 1/6)`, always answers argmin.
- `B2_minimax_always_answer`: picks route minimizing `max` over `W` vertices and constant intervals of scalar cost (upper-bound minimizer), always answers.
- `B3_always_query_scalarize`: always pays `query_price`, gets exact constants, answers with centroid `w`. (Strongest constant-evidence baseline.)
- `LAZY_ABSTAINER` (anti-mechanism control, not a baseline for the residual gate): always outputs `CANNOT_COMPARE`.
- `ORACLE`: true constants and true `w*`; loss 0; upper bound.

## Prespecified gates

| Gate | Statement | Threshold |
|---|---|---|
| F3-G1 | Determinism: full pipeline computed twice in-process yields byte-identical canonical JSON | exact equality |
| F3-G2 | Hostile decidable world: ORION query rate = 0, abstention rate = 0, mean loss | `<= 1e-12` |
| F3-G3 | Lazy abstainer punished on `W_ADV_DECIDABLE`: `lazy_mean_loss >= orion_mean_loss + 0.05` | margin 0.05 |
| F3-G4 | Oracle bound: no arm mean loss `< oracle - 1e-12` on any world | 1e-12 |
| F3-G5 | Residual: ORION mean total loss on `W_PRIMARY` `<= 0.99 *` min over B1–B3 | 1% relative margin |

Terminal vocabulary: `N2_F3_PARTIAL_EVIDENCE_RESIDUAL_SUPPORTED__EXACT_SYNTHETIC_ONLY`; `N2_F3_PARTIAL_EVIDENCE_NO_RESIDUAL__EXACT_SYNTHETIC_ONLY` (honest negative, valid); `N2_F3_HOSTILE_CONTROL_FAILED__MECHANISM_NOT_PROMOTED` (any of G1–G4 fails).

## Determinism and receipt rules

Stdlib + numpy only; single fixed seed; sorted-key canonical JSON receipt on one stdout line `ORIONQ_N2_F3_PARTIAL_EVIDENCE=<canonical sorted json>`; pretty results written to `research/extensions/orion-q/nlanes/N2_F3_PARTIAL_EVIDENCE_RESULTS.json`; process exits 0 regardless of gate outcomes.

## Claim boundary

Exact-synthetic scope only. The route cost formulas are the stripped proxies of #671/#675, not compiled resource estimates; no claim about real QSVT implementations, hardware, or novelty of interval/Pareto decision theory (donor-owned). A positive residual here says only: within this frozen world, the typed partial-evidence policy beats the frozen always-answer baselines. A negative says only that it does not; neither is a `LOWER_BOUND` claim.
