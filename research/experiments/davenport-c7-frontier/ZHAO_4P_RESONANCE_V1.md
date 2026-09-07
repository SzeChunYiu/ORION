# Zhao Lemma 4.4 has a rank-three `4p` resonance hole — V1

Status: **analytic lemma about one donor proof instrument**. It does not assert absence of short zero-sums. Novelty/priority: **CANNOT_CHECK**.

## Statement

Let `p>=5` be an odd prime and `G=C_p^3`, so `D(G)=3p-2`. Let `T` be a zero-sum sequence of length `4p`. For every pair `(k,i)` admissible in Zhao Lemma 4.4,

`ceil(3p/2) <= k <= 2p`,

`1 <= i <= 2k-(3p-2)`,

the Zhao coefficient

`a_i = C(4p-k,k-i) + (-1)^i C(4p-k+i-1,k-1)`

vanishes modulo `p`.

Therefore Zhao Lemma 4.4, by itself, cannot certify a bounded short zero-sum from a length-`4p` total-zero sequence in `C_p^3`.

## Proof

Write `k=2p-q`, where `0<=q<=(p-1)/2`. The admissible range for `i` becomes `1<=i<=p-2q+2`. Put

`A_i=C(2p+q, 2p-q-i)` and `B_i=C(2p+q+i-1, 2p-q-1)`.

Lucas' theorem shows that both terms vanish modulo `p` whenever `i<p-2q`. Thus only `i=p-2q+j`, with `j=0,1,2`, can contribute. The boundary cases `q=0,1` are included by the same Lucas carry calculation. Modulo `p`:

| `j` | `A_i` | `B_i` | parity of `i` | `A_i+(-1)^i B_i` |
|---|---:|---:|---|---:|
| 0 | `2` | `2` | odd | `0` |
| 1 | `2q` | `-2q` | even | `0` |
| 2 | `q(q-1)` | `q(q-1)` | odd | `0` |

Hence every admissible coefficient is zero modulo `p`.

## Interpretation boundary

This is a **proof-route resonance**, not yet a physical or combinatorial phase theorem. In the current `p=7` programme it explains why length 28 (`4p`) is the unique near-`D_2` complement on which the same Zhao mechanism that resolves lengths 27 and 29 goes completely silent. Any claim connecting this algebraic cancellation to the exceptional `p=3` multiwise behaviour remains open.
