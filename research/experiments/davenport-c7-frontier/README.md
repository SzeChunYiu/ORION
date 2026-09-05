# Davenport `C_7^3` frontier packet — index

Working packet for the generalized (multiwise) Davenport constant `D_k(C_p^r)`. Everything here
is additive: ~250 records, 68 checkers, one CI workflow
(`.github/workflows/claude-davenport-c7-v2-checks.yml`, which runs on this branch and now covers
the results below).

Throughout `p` is an odd prime, `D = D(C_p^r) = r(p−1)+1` (Olson), and `z(S)` is the packing
number — the largest number of pairwise disjoint nonempty zero-sum subsequences. `D_k(G)` is the
least `ℓ` such that every sequence of length `ℓ` has `z ≥ k`.

**Olson's `D(C_p^r) = r(p−1)+1` is the only external input anywhere in the chain.**

## Results, and where each one lives

| result | status | record | checker |
|---|---|---|---|
| `D_2(C_p^3) = (9p−5)/2`, every prime `p ≥ 5` | proved | `D2_UNIFORM_SELFCONTAINED_THEOREM_V3.md` | `verify_atom_spectrum_v3.py` |
| Hypothesis `(Z)` — the last donor dependency | proved | `HYPOTHESIS_Z_PROVED_V3.md` | `verify_hypothesis_Z_v3.py` |
| **`D_3(C_7^3) = 36`** | proved | `D3_C7_CONDITIONAL_CLOSURE_V3.md` | `verify_D3_C7_end_to_end_v3.py` |
| **`D_4(C_5^3) = 30`** (Theorem T), closing `D_k(C_5^3) = 5k+10` | proved | `D4_C5_DECIDED_V6.md` | `verify_D4_C5_end_to_end_v6.py` |
| Theorem G — Lucas digit criterion for inconsistency | proved | `LUCAS_CRITERION_V5.md` | `verify_lucas_criterion_v5.py` |
| Short-atom law, closed form in `(p,m)` | verified `5 ≤ p ≤ 23` | `SHORT_ATOM_LAW_UNIFORM_V5.md` | `verify_short_atom_law_v5.py` |
| Theorem I (third-difference law) | proved | `SUPP_Q_PROVED_V5.md` | `verify_supp_Q_proof_v5.py` |
| Theorem J (explicit dual) | proved | `OBSERVATION_D_EXISTENCE_PROVED_V5.md` | `verify_existence_proved_v5.py` |
| Three special lengths | verified `5 ≤ p ≤ 31` | `GENERAL_SPECTRUM_SPECIAL_LENGTHS_V4.md` | `verify_general_spectrum_v4.py` |
| Prop 4.3′ short-atom bound | proved | `SHORT_ATOM_BOUND_UNIFORM_V4.md` | `verify_short_atom_bound_v4.py` |
| Two-sided `D_2(C_p^r)` framework, all ranks | per-`(p,r)` | `D2_ALL_RANKS_V3.md` *(superseded in part)* | `tools/d2_rank_bounds_v3.py` |
| **Witness-coordinate criterion** — Theorems W, W_t, X, X′, Cor. 1–5 | proved | `WITNESS_CRITERION_V6.md` | `verify_witness_criterion_v6.py` |

## The current frontier: `WITNESS_CRITERION_V6.md`

Start here. For the algebraic families used for `D_k` lower bounds,
`S = ∏ᵢ eᵢ^{p−1} · ∏_A v_A^{m_A}`, a block is indexed by the multiplicity vector `b` of the
`v`-part alone — the `e`-part is forced — and two blocks are disjoint iff their `e`-parts add
**with no carry**. That equivalence (Theorem W, and W_t for every `k`):

- contains the previous intersecting-family condition as the case `b = e_A, b′ = e_B`;
- improves five lower bounds: `D_2(C_3^5) ≥ 17`, `D_2(C_3^6) ≥ 20`, `D_2(C_5^4) ≥ 26`,
  `D_2(C_7^4) ≥ 37`, `D_2(C_5^5) ≥ 31`, each propagating to all `k` via `M*_k = M*_2 + (k−2)p`;
- reproduces **all ten** exact `D_k(C_p^r)` values the packet owns, across `k = 2, 3, 4`, with
  nothing fitted — including the two hardest, `D_3(C_7^3) = 36` and `D_4(C_5^3) = 30`.

## Recorded negatives (read before re-attempting)

| negative | record |
|---|---|
| Extremal families have no uniform shape; two candidate shapes fail | `WITNESS_CRITERION_V6.md` §8 |
| Intersecting + zero-sum-free are strictly weaker than the criterion | `WITNESS_CRITERION_V6.md` §7c |
| Flat-triple enumeration infeasible from short atoms | `FLAT_TRIPLE_INFEASIBILITY_MEASURED_V6.md` |
| The `p=5` bridge does not generalise to `p ≥ 11` | `D3_BRIDGE_NEGATIVE_V6.md` |
| `D_2(C_5^4)` out of reach of post-hoc deduplication | `D2_RANK4_SCALE_MEASURED_V6.md` |
| Minimality attempt | `MINIMALITY_ATTEMPT_V5.md` |

## Open

1. A closed form for `M*(r,p)`. The `M*(r,3) = r+1` reading is **refuted**: it holds for `r ≤ 6`
   but `M*(7,3) = 7`, not 8, so `D_2(C_3^r) = 3r+2` fails on the construction side at `r = 7`
   (`D_2(C_3^7) ≥ 22`). `M*(4,p) = ⌊9p/5⌋` for `p = 3,5,7` still stands as an observation.
   §7c shows the elementary route cannot reach a closed form.
2. A uniform-in-`(p,r)` proof of the rank-`r` upper bound — still per-`(p,r)` certificates.
3. `D_3(C_p^3)` for `p ≥ 11`, blocked on flat-triple elimination.
4. Whether `D_2(C_3^5) = 17` exactly (an exhaustive sweep is the deciding computation).

## Claim ceiling

Machine-assisted throughout; every computational step has a checker, and the checkers are run in
CI. **Nothing here has been read by a mathematician, and novelty is `CANNOT_CHECK` from this
host** — whether these results are already known has not been verified against the literature.
Both remain necessary before any submission.
