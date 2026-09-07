# Combined completion map — all three lanes merged — V6

Status: **synthesis record.** Merges `shadow/davenport-c7-frontier-20260903` and `shadow/c7-davenport-frontier-20260903-sol` into this lane, derives a new corridor from two of this lane's proved theorems, and states precisely what is still required to complete `D_3(C_p^3)` for `p ≥ 11`.
Checker: `verify_special_corridor_v6.py`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. What is proved, across all lanes

**This lane, all primes `p ≥ 5`:** `D_2(C_p^3) = (9p−5)/2`; the digit criterion for pointed infeasibility (Theorem G) and the closed-form short-atom law it yields; `supp Q ⊆ S` (Theorem I); the forcing theorem — every obstruction carries atoms of at least two of `a = 3(p−1)/2`, `b = 2p`, `c = (5p−3)/2` (Theorem J); Lemmas H and K.

**This lane, `p = 7`:** `D_3(C_7^3) = 36`, with Olson the only external input; both corridors halved (4 triples, 3 profiles).

**This lane, `p = 5`:** a five-profile four-atom corridor for the length-31 obstruction that decides `D_4(C_5^3)`.

**Lane A (`shadow/davenport-…`):** the support-four maximal-atom classification; the prime-uniform maximal-atom corridor `C_j(p) = (p+j, p+(p+1)/2−j, 3p−2)`; complete support-7 closure at `p = 7`; the `(8,10,19)` and `(9,9,19)` support-six faces; and a run of equality-face eliminations (`a=1` shared multiplicity `c = 1,2,3`, `a=2` heavy) driving toward *support-four maximal atom ⟹ maximal pair support ≥ 7*.

**Lane B (`shadow/c7-…-sol`):** the `B7` one-split and two-to-three neighbourhood closures, and the `C7^3` frontier witness verifiers.

## 2. New: the special-length corridor

Two proved results of this lane combine into a corridor neither lane had.

> **Corollary L.** Let `A` be an atom of an obstruction whose length `L` is special. Then `C = T A^{−1}` has length `N − L > D`, so by the short-atom law it contains an atom `E` with `|E| ≤ w(p, N−L)`; and `F = C E^{−1}` must be an atom, since otherwise `A, E` and two blocks of `F` are four disjoint blocks. So `T` has a three-atom factorization through **every** special length it carries — and by Theorem J it carries **at least two of the three**.

| `p` | triples through `a` / `b` / `c` | total | of which contain a maximal atom |
|---|---|---|---|
| 7 | 2 / 3 / 3 | 8 | **1** / 0 / 0 |
| 11 | 4 / 5 / 5 | 14 | **1** / 0 / 0 |
| 13 | 5 / 6 / 6 | 17 | **1** / 0 / 0 |
| 19 | 8 / 9 / 9 | 26 | **1** / 0 / 0 |
| 31 | 14 / 15 / 15 | 44 | **1** / 0 / 0 |

At `p = 7` the `a`-row is exactly `{(9,9,19), (9,10,18)}` — the two non-`(8,10,19)` members of the tightened first corridor, so the new corridor is consistent with the settled case.

## 3. The gap this exposes

**Exactly one triple of the whole special-length corridor contains a maximal atom, at every prime tested — and none of the `b`- or `c`-row triples do.**

Lane A's programme, including its prime-uniform target *support-four maximal atom ⟹ pair support ≥ 7*, applies **only to triples containing a maximal atom**. So:

- completing lane A's target closes at most **one** triple per prime of this corridor;
- an obstruction carrying `b` and `c` but not `a` exhibits two rows in which **no** triple has a maximal atom, and is therefore invisible to that machinery entirely.

This is the structural reason `p = 7` closed and `p ≥ 11` has not. At `p = 7` the extra forced pair `{13,14}` (from the richer small-prime spectrum) plus the halved corridors reduced the problem to eight spectra that complement systems could finish. For `p ≥ 11` the spectrum gives only Theorem J's floor, and two of its three rows lie outside every existing elimination method.

## 4. What completion actually requires

For `D_3(C_p^3) = (11p−5)/2` at a given `p ≥ 11`:

1. **An elimination method for flat triples** — those with no maximal atom. This is the binding constraint. Lane A's next target (the uniform multiplier-existence lemma) does not supply it, because the maximal-atom normal form is where its support-four classification lives.
2. Completion of lane A's support-seven target, which then closes the single maximal-atom triple per row.
3. A `p ≥ 11` analogue of the `p = 7` complement-system elimination, which needs the richer forced-pair structure that Theorem J does not give beyond the floor.

Items not on the critical path: sharpness of Theorem J (verified `p ≤ 19`, nothing depends on it); `D_4(C_5^3)`, which is a separate question that §6.5's corridor plus the existing pseudo-Boolean encoding could decide.

**Honest assessment.** Merging the lanes does not close `p = 11`, and no combination of the currently proved results does. The distance is one missing method — elimination for atom triples with no maximal part — and this record's contribution is to have identified it precisely rather than leaving "close the corridors" as an undifferentiated goal.

## Claim ceiling

Corollary L is proved for all primes, given Theorem J and the short-atom law. The table is computed for the listed primes. No `D_3` closure is claimed for any `p > 7`; §3 and §4 are an analysis of what remains, not a result.
