# Maximal atoms over `C_5^3` are enumerable — the sweep is a few minutes, not a research project — V6

Status: **feasibility established with measurements.** Two of the five `D_4(C_5^3)` profiles become decidable by a computation that is cheap once the atoms are reduced up to `GL(3,5)`. Not run to completion here.
Tools: `tools/enumerate_maximal_atoms_c5_v6.c`, `tools/sweep_maximal_atoms_c5_v6.c`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. The enabling fact

A maximal atom over `C_5^3` has length `13 = D(C_5^3)`, so it is an **extremal zero-sum-free sequence of length 12** plus its completing element `−σ`. Zero-sum-freeness prunes far harder than the 5-short-freeness used elsewhere in this packet: carry `Σ` = the set of *all* subsums as one 125-bit mask, and adding `v` is legal exactly when `−v ∉ Σ`.

> **Measured.** With the first independent triple normalised to `e_1,e_2,e_3`, the enumeration produces **6,315,607** `(prefix, completion)` pairs in **72 seconds**, which is **998,182 distinct maximal atoms** — each atom arises once per element whose removal leaves a zero-sum-free sequence, about 6.33 times. The earlier version of this record misreported the pair count as the atom count.

That is the fact that changes the picture: `FLAT_TRIPLE_INFEASIBILITY_MEASURED_V6.md` §4 listed "work from the longest part" as untried because classifying long atoms looked like the hard half. For `p = 5` it is not hard at all.

## 2. Cost of the sweep

| quantity | measured |
|---|---|
| `(prefix, completion)` pairs (NOT the atom count — see correction) | 6,315,607 |
| distinct maximal atoms | 998,182 |
| enumeration time | 72 s |
| full extension search to length 31, per atom | **65 ms** |
| raw sweep, no deduplication | **114 hours** |
| zero-sum length-31 completions found in a 2,000-atom sample | **0** |

114 hours is too long here, but the raw count is the wrong denominator. The normalisation fixes an *ordered* independent triple, and an atom of length 13 contains at most `13·12·11 = 1716` of them, so each `GL(3,5)`-orbit is generated at most 1716 times:

`orbits ≥ 998,182 / 1716 ≈ 582` — a weak bound; the measured count is 3,325.

At 65 ms per representative the sweep is **about four minutes** (measured: 199 s). The sweep is a deduplication problem, not a compute problem.

## 3. What the sweep would decide

By Theorem M the support-four branch is already closed. A completed sweep over all maximal-atom orbits would decide, outright:

- **`(6,6,6,13)`** — carries a maximal atom by construction;
- **`(7,7,7,10)`** — carries one by Theorem O.

That is two of the five profiles of `D4_C5_FOUR_ATOM_CORRIDOR_V4.md`, including the flat one. The three profiles containing a 6 would remain, and `D_4(C_5^3)` would remain open — but the fraction of the problem reachable by a short computation is much larger than this packet previously believed.

## 4. Evidence, stated as evidence

In 2,000 sampled maximal atoms — 200 million extension nodes — **no** zero-sum 5-short-free length-31 completion was found. That is consistent with `D_4(C_5^3) = 30` and with Theorem M, and it is **not** a proof: the sample is 0.03% of the atoms and was not chosen uniformly (it is the DFS prefix order). It is recorded as a directional signal only.

## 5. The next step, precisely

1. Dedupe the 6,315,607 atoms to `GL(3,5)`-orbit representatives (expected `≈ 3,700`). The obvious route is a canonical form: for each atom, the lexicographic minimum over its `≤ 1716` normalisations.
2. Run the extension search on the representatives (`≈ 4` minutes at the measured rate).
3. If no orbit admits a zero-sum length-31 completion, the `(6,6,6,13)` and `(7,7,7,10)` profiles are both eliminated.

Step 1 is the only real work, and it is bounded and standard.

## Claim ceiling

Every number here is a measurement on this host, not a theorem. The orbit estimate `≈ 3,680` is a lower bound from the `1716` divisor and could be larger if many atoms have few independent triples in general position; the sweep time scales linearly with whatever the true orbit count is. Nothing here decides `D_4(C_5^3)`, and the 2,000-atom sample proves nothing.
