# X1-C finding — dual primary projection trade for C_45^3

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #901

## Finding

The live C45 target has two materially different primary-projection proof routes. They should be treated as competing research fibres rather than forcing the smallest raw block deficit.

---

## Route P3 — project to C_3^3

Exact sequence:

`0 -> C_15^3 -> C_45^3 -> C_3^3 -> 0`.

This extension is not split (already in one coordinate, `C_45` is not isomorphic to `C_3 direct_sum C_15`, because the latter has exponent 15).

Donor arithmetic:
- `D(C_15^3)=43`;
- `D_k(C_3^3)=3k+6` for `k>=3`;
- target length 133 gives 42 quotient blocks (`D_42=132`) but not generically 43 (`D_43=135`).

Thus P3 has an **exact one-block deficit**, but the 42 lifted block sums live in the mixed-primary rank-three kernel `C_15^3`, where the sharp `nu_p=d-1` p-group theorem does not apply automatically.

---

## Route P5 — project to C_5^3

By CRT,

`C_45^3 isomorphic_to C_5^3 direct_sum C_9^3`.

This projection is split, with kernel `K=C_9^3`.

### Donor-derived C_5^3 multi-wise bound

Published short-zero-sum inputs used in the current Grinsztajn proof include:
- every 33-term sequence over `C_5^3` contains 3 disjoint nonempty zero-sum subsequences (`D_3(C_5^3)<=33`);
- every 33-term sequence over `C_5^3` contains a nonempty zero-sum subsequence of length at most 5 (`eta(C_5^3)<=33`).

Inductively, if `D_j(C_5^3)<=33+5(j-3)`, a sequence of length

`33+5((j+1)-3) = (33+5(j-3))+5`

contains a short zero sum of length at most 5; deleting it leaves at least `D_j` terms and therefore `j` further disjoint zero sums. Hence for every `k>=3`,

`D_k(C_5^3) <= 33 + 5(k-3) = 5k+18`.

In particular,

`D_23(C_5^3) <= 133`.

Therefore every hypothetical zero-sum-free sequence of the C45 contradiction length 133 admits at least **23 disjoint quotient zero-sum blocks** under the split C5 projection.

### Kernel geometry

For `K=C_9^3`, the p-group formula gives

`d(K)=3(9-1)=24`, `D(K)=25`.

Thus 23 block sums are two short of the ordinary Davenport block count, but they are exactly at length `d(K)-1`.

Geroldinger--Yang, *On a classical zero-sum invariant* (arXiv:2608.19090, Theorem 3.5), prove for every finite abelian p-group

`nu(K)=nu_p(K)=d(K)-1`.

Hence

`nu_3(C_9^3)=23`.

Consequently, if the 23 lifted block sums form a zero-sum-free sequence `T` in `C_9^3`, all nonzero kernel elements not representable as a subsequence sum of `T` are contained in one affine coset of an index-3 subgroup.

---

## Research consequence

The two routes trade raw deficit against structural control:

| route | quotient | kernel | split? | guaranteed blocks | ordinary blocks needed | deficit | missing-sum geometry |
|---|---|---|---|---:|---:|---:|---|
| P3 | `C_3^3` | `C_15^3` | no | 42 | 43 | 1 | mixed-rank-3, unresolved |
| P5 | `C_5^3` | `C_9^3` | yes | 23 | 25 | 2 | sharp p-group `nu_3=23` available |

Therefore the next proof search should not automatically privilege P3. P5 may be easier despite being two blocks short because its extension semantics are split and its near-maximal kernel subsequence-sum geometry is already theorem-controlled.

## Candidate P5 deficit-repair shape

If legal quotient-block exchanges can produce one or two new kernel correction values outside the exceptional affine coset(s) supplied by the p-group `nu_3` theorem, the missing two ordinary blocks may be repairable without solving any new mixed-kernel `nu_p` problem.

This is only a research hypothesis. A precise exchange theorem must be frozen before protected computation.

## Claim boundary

The CRT decomposition, short-zero-sum extraction, p-group Davenport constants, and Geroldinger--Yang `nu_p` theorem are donor mathematics. This note records a new programme-level route comparison, not a mathematical novelty claim.
