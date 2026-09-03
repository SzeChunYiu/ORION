# Exhaustive determination of `D_k(C_3^3)`, `D_2(C_5^3)` and the extremal inverse structure — V2

Status: **exact finite results, machine-produced, symmetry-reduced, replayable** (`run_exhaustive_analogs_v2.sh`; enumerator `tools/enum_packing_v2.c`, canonical forms `tools/canon_gl3.py`). Priority: the values `D_k(C_3^3) = 3k+5` (k = 2,3,4) and `D_2(C_5^3) = 20` are **donor-owned or donor-derived** (Delorme–Ordaz–Quiroz 2001 / Freeze–Schmid 2010 for `C_3^3`; `D2_PRIME_POWER_COROLLARY_V1.md` for `C_5^3`); the orbit classifications and the multiplicity observations are, as far as this host could check, **not in the retained literature routes** — priority CANNOT_CHECK. The `p = 7` and the `D_3(C_5^3)` frames below are marked with their execution status; nothing marked PENDING/PARTIAL is claimed.
Branch: `claude/orion-research-frontier-3ck9yt`.

## 1. Method

For a target `D_k(C_p^3) ≤ L` the reduction lemmas (`OBSTRUCTION_REDUCTION_LEMMAS_V2.md`, §3–4) show that a counterexample `S` (length `L`, `pk(S) ≤ k−1`) satisfies: multiplicities `≤ p−1`, no zero-sum subsequence of length `≤ s := L − D_{k−1}(C_p^3)`, spanning support, and `|S ∩ H| ≤ D_k(C_p^2) − 1 = (k+1)p − 2` for every plane `H`. The enumerator performs a depth-first search over multiplicity vectors in a fixed point order with

- incremental bitsets `Σ_j` of all sums of size-`j` sub-multisets (`j ≤ s`), rejecting any extension that creates a zero-sum of length `≤ s`;
- an availability bound (`Σ_v c_v ≥ L − |partial|`, where `c_v` is the number of further copies of `v` that can still be added without a short zero-sum);
- the `GL(3,p)` symmetry-breaking rule *`e_1, e_2, e_3 ∈ supp`, `m(e_1) = max mult`, `m(e_2) = max mult off ⟨e_1⟩`, `m(e_3) = max mult off ⟨e_1,e_2⟩`* (valid because the support spans);
- at each leaf, the exact packing number by recursion over minimal zero-sum sub-multisets (blocks in non-decreasing size, smallest block `≤ |S|/t`).

`found = 0` in a frame proves the upper bound; the leaves of the witness frame (length `D_k − 1`) are reduced to `GL(3,p)`-orbits by `tools/canon_gl3.py` (lexicographically least image over all ordered independent triples of support points mapped to the standard basis).

Each frame line below reports the enumerator's own counters (`nodes`, `leaves` = sequences surviving the short-zero-sum frame, `found` = leaves with `pk ≤ k−1`).

## 2. `C_3^3`: `D_2 = 11`, `D_3 = 14`, `D_4 = 17` (all reproduced)

| frame | parameters (p L cap s kmax) | nodes | leaves | found | conclusion |
|---|---|---|---|---|---|
| D2 witnesses | 3 10 2 3 1 | 8 005 | 1 526 | 529 → **43 orbits** | `D_2 ≥ 11` |
| D2 bound | 3 11 2 4 1 | 255 | 0 | 0 | `D_2 ≤ 11` |
| D3 witnesses | 3 13 2 2 2 | 800 233 | 233 728 | 7 317 → **161 orbits** | `D_3 ≥ 14` |
| D3 bound | 3 14 2 3 2 | 7 953 | 476 | 0 | `D_3 ≤ 14` |
| D4 witnesses | 3 16 2 2 3 | 4 300 388 | 1 123 072 | 8 921 → **69 orbits** | `D_4 ≥ 17` |
| D4 bound | 3 17 2 3 3 | 1 780 | 0 | 0 | `D_4 ≤ 17` |

Orbit statistics (support size, multiplicity profile): D2-extremal: supports 5 (1 orbit, profile `2^5`), 6 (20), 7 (22); D3-extremal: supports 7 (22), 8 (109), 9 (30); D4-extremal: supports 8 (1, profile `2^8`), 9 (44), 10 (24). **Every extremal sequence has an element of multiplicity `p − 1 = 2`.** The `D_4` bound frame has no leaves at all: every sequence of length 17 with multiplicities `≤ 2` has a zero-sum of length `≤ 3`, i.e. this frame re-derives `η(C_3^3) = 17`.

## 3. `C_5^3`: `D_2 = 20` (exhaustively re-proved), inverse structure

| frame | parameters | nodes | leaves | found | conclusion |
|---|---|---|---|---|---|
| D2 witnesses | 5 19 4 6 1 --planecap 14 | 98 499 683 | 48 396 | 7 847 → **1 405 orbits** | `D_2 ≥ 20` |
| D2 bound | 5 20 4 7 1 --planecap 14 | 33 148 115 | 0 | 0 | `D_2 ≤ 20` |

So `D_2(C_5^3) = 20` holds by exhaustive enumeration, independently of both the donor route (Freeze–Schmid + Zhao) and the spectrum route (`SPECTRUM_CONGRUENCE_THEOREM_V2.md`). The 1 405 orbits of `D_2`-extremal sequences have supports of size 5 (2 orbits, profile `4^4·3`), 6 (136), 7 (582), 8 (543), 9 (133) and 10 (9); **every one of them has an element of multiplicity `p − 1 = 4`**.

Contrast (same enumerator, `--zsfree` mode): the 181 979 symmetry-reduced zero-sum-free sequences of length 12 over `C_5^3`, completed by `−σ` to minimal zero-sum sequences of the maximal length `D(C_5^3) = 13`, have maximal multiplicity 4 in 136 949 cases, 3 in 44 277 cases and 2 in 753 cases. So *maximal atoms* of `C_5^3` need not contain an element of multiplicity `p − 1`, while all *`D_2`-extremal* sequences do (for `p = 3, 5`). This separates the two inverse problems and is the empirical basis of Conjecture 5.1 below.

## 4. `C_5^3`: `D_3 = 25` (exhaustive)

| frame | parameters | nodes | leaves | found | conclusion |
|---|---|---|---|---|---|
| D3 bound | 5 25 4 5 2 --planecap 18 | 848 752 855 | 7 716 438 | **0** | `D_3 ≤ 25` |
| D3 witnesses | 5 24 4 4 2 --planecap 18 | RUNNING (classification of extremal sequences) | | | `D_3 ≥ 25` is already witnessed by `S_3(5)` |

**Theorem 4.1.** `D_3(C_5^3) = 25 = (11·5 − 5)/2`.

*Proof.* Lower bound: `S_3(5) = e_1^4 e_2^4 e_3^4 e_12^4 e_13^3 e_23^2 e_123^3` has length 24 and packing number 2 (`CUBE_FAMILY_LOWER_BOUNDS_V2.md`, Theorem 2, and `verify_cube_family_v2.py`). Upper bound: by `OBSTRUCTION_REDUCTION_LEMMAS_V2.md` §4 a sequence of length 25 with packing number `≤ 2` would have all multiplicities `≤ 4` (a fifth copy `v^5` plus `D_2(C_5^3) = 20` on the remaining 20 elements gives three blocks), no zero-sum subsequence of length `≤ 5` (else `T = S·(−σ(S))` has four blocks by `D_2 + 1 = 21`), spanning support (`D_3(C_5^2) = 19 ≤ 25`), and at most `D_3(C_5^2) − 1 = 18` elements in every plane; the symmetry-breaking rule of §1 loses no `GL(3,5)`-orbit of such sequences. The frame enumerates every multiplicity vector meeting these conditions — 7 716 438 leaves — and finds none with packing number `≤ 2`. ∎

The run took about 35 minutes on one core (`enum_packing_v2`, `-O2`). A second run with the non-basis points visited in reverse order (`--reverse`) is the independence check recorded in the JSON (leaf and found counts must agree; node counts differ). This is the first `p ≥ 5` instance of the pattern `D_3(C_p^3) = (11p−5)/2` whose `p = 7` case is the frozen question.

## 5. `C_7^3`: inverse problem for `D_2` (length 28, `pk = 1`) — partial classes

Frame: `7 28 6 9 1 --planecap 20`, split by the maximal multiplicity `m(e_1)`:

| class | status |
|---|---|
| `m(e_1) = 6` | RUNNING; `> 12 000` raw witnesses already, first 2 000 reduce to 1 047 orbits with supports 5–10 (e.g. support 5, profile `6^4·4`: 3 orbits) |
| `m(e_1) = 5` | RUNNING; no witness yet |
| `m(e_1) ≤ 4` | NOT STARTED |

**Conjecture 5.1 (empirical).** For every odd prime `p`, every sequence of length `(9p−7)/2` over `C_p^3` with zero-sum packing number 1 contains an element of multiplicity `p − 1`. (True for `p = 3, 5` by §2–3; the `p = 7` classes `m(e_1) ≤ 5` are open.) A proof would reduce the `u = 8` case of `OBSTRUCTION_REDUCTION_LEMMAS_V2.md` Lemma 2.4 to sequences containing `v^6`.

## Claim ceiling

The tables are exact for the frames listed as complete. The pending and partial frames are execution status, not results. No statement about `D_3(C_7^3)` follows from this record.
