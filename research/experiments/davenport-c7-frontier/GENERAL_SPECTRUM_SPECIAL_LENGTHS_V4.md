# The atom spectrum of a `D_3(C_p^3)` obstruction: three special lengths, uniformly in `p` — V4

Status: **verified for every prime `5 ≤ p ≤ 31`** (a finite computation per prime, not yet a uniform proof). The `p = 7` instance is part of the already-proved `D_3(C_7^3) = 36` chain.
Checker: `verify_general_spectrum_v4.py`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. The uniform setting

Everything in the `p = 7` programme has a `p`-uniform shape. For a prime `p ≥ 5` put

| | | at `p = 7` |
|---|---|---|
| `N = (11p−3)/2` | length of the zero-sum object attached to an obstruction | 37 |
| `D = 3p−2` | Olson | 19 |
| `D_2 = (9p−5)/2` | proved uniformly in this packet | 29 |
| `amin = p+1` | no zero-sum of length `≤ p` (Lemma 2.2, and its proof is uniform: `\|T U^{−1}\| ≥ N − p = D_2 + 1`) | 8 |

Atom lengths lie in `[amin, D]`. Zero-sum sub-multisets of the obstruction are exactly `∅`, the whole thing, the atoms, and the complements of atoms; a multiset that is **both** an atom and the complement of an atom has length in `[N−D, D]`. Writing `W_L` for the weighted atom count at length `L` and `X_L` for the weighted count of the double-counted ones, the counting identity gives for every `0 ≤ d ≤ N−D`

> **(S)**  `C(0,d) + (−1)^N C(N,d) + Σ_L (−1)^L W_L [C(L,d) + (−1)^N C(N−L,d)] − Σ_{L ∈ [N−D,D]} (−1)^L X_L C(L,d) ≡ 0 (mod p)`.

Note `N` changes parity with `p` (`N = 37` is odd, `N = 26` and `N = 70` are even), which is why the `(−1)^N` must be carried rather than specialised.

## 2. The special lengths

> **Definition.** `L ∈ [amin, D]` is **special** when `p | L` or `p | (N−L)`.

There are exactly three, for every prime `p ≥ 5`:

| special `L` | in base `p` | complement `N−L` | in base `p` |
|---|---|---|---|
| `3(p−1)/2` | `(1, (p−3)/2)` | `4p` | `(4,0)` |
| `2p` | `(2, 0)` | `(7p−3)/2` | `(3, (p−3)/2)` |
| `(5p−3)/2` | `(2, (p−3)/2)` | `3p` | `(3,0)` |

At `p = 7` these are `9, 14, 16`; at `p = 11`, `15, 22, 26`; at `p = 13`, `18, 26, 31`.

Since `N = (5, (p−3)/2)_p`, a length is special exactly when its base-`p` low digit is `0` or `(p−3)/2` — i.e. when Lucas makes either its own column or its complement's column vanish off `d ≡ 0 (mod p)`. This is the same mechanism that made `14 = (2,0)_7` the pivot of `HYPOTHESIS_Z_PROVED_V3.md`, now identified as a general phenomenon rather than a `p = 7` accident.

## 3. The result

> **Theorem (verified for every prime `5 ≤ p ≤ 31`).** In the system `(S)`:
> 1. the unrestricted system is consistent;
> 2. forbidding **any two** of the three special lengths makes it **inconsistent**;
> 3. for `11 ≤ p ≤ 19` those three pairs are the **only** minimal inconsistent length sets of size `≤ 2` — in particular no single length is forced.
>
> Consequently **every obstruction has atoms of at least two of the three special lengths `3(p−1)/2`, `2p`, `(5p−3)/2`.**

Part 2 was checked for `p ∈ {5,7,11,13,17,19,23,29,31}`, part 3 exhaustively for `p ∈ {5,7,11,13,17,19}`.

The two smallest primes are **richer**, not weaker: at `p = 5` and at `p = 7` there are 18 minimal forced pairs, the three special ones among them. At `p = 7` the extra ones include `{13,14}` — the pair that `ATOM_SPECTRUM_CONGRUENCE_V3.md` uses and on which the second corridor and hence the `D_3(C_7^3) = 36` proof rest. So the uniform statement is a floor that the small primes exceed, and the `p = 7` proof is not weakened by it.

## 4. Validation

`verify_general_spectrum_v4.py`:

1. re-derives the system from scratch and checks it **agrees with the recorded `p = 7` verifier** (`verify_atom_spectrum_v3.py`, the one behind the published `D_3(C_7^3)` chain) on **all 298 length subsets of size `≤ 3`** — zero disagreements. This is the load-bearing control: the general system is a faithful generalisation, not a new and differently-behaved object;
2. checks the three special lengths match the closed form for every prime tested;
3. checks consistency of the unrestricted system for every prime (non-vacuity);
4. checks each special pair is forced, **both** with `X_L` free and with the valid relation `X_L = X_{N−L}` imposed (complementation preserves the weight), so the conclusion does not depend on that modelling choice;
5. searches all pairs exhaustively for `p ≤ 19` to establish minimality.

## 5. What this is and is not

It **is** a uniform structural constraint on `D_3(C_p^3)` obstructions, replacing a `p = 7`-specific "atom of length 13 or 14" with a statement that has the same shape at every prime and a reason (Lucas at low digit `0` or `(p−3)/2`).

It is **not** yet a proof. The obstacle is recorded honestly: greedy minimisation of the degree set shows the contradiction uses essentially every degree in `[p+2, (5p+1)/2]` — there is no small subsystem and no short hand-chain of the kind that closed `|C| = 28` in `SHORT_ATOM_BOUND_UNIFORM_V4.md`. The dual certificates are dense with no evident closed form, although their right-hand sides sit in the constant ratio `4 : 2 : 3` (mod `p`) across the three pairs for every prime tested — a hint that a generating-function identity is behind it. A uniform proof therefore needs a rank argument for the matrix `[C(L,d) + (−1)^N C(N−L,d)]` over the degree window, not a clever choice of a few `d`.

It also does **not** by itself decide `D_3(C_p^3)` for any `p > 7`: the forced lengths constrain the spectrum, but the corridors still have to be closed, and for `p ≥ 11` the first corridor has 9 or more triples (against 4 at `p = 7`) with no support classification available. The distance to `D_3(C_p^3) = (11p−5)/2` in general is honestly large; this narrows the target rather than hitting it.

## Claim ceiling

Verified range `5 ≤ p ≤ 31`, parts 1–2; `5 ≤ p ≤ 19` for the minimality part 3. No claim is made for `p > 31`, and no claim that the pattern continues — only that it holds where checked and that the mechanism (Lucas on the low base-`p` digit) is prime-independent.
