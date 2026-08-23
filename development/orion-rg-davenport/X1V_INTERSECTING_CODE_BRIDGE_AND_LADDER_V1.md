# ORION-RG X1-V — the intersecting-code bridge: conjecture falsified, `D_2(C_2^9) = 16`, `D_2(C_2^10) = 17`, and the ladder to `r = 15`

## The bridge (published — prior-art hit #14)

The parity-check dictionary: a length-`n` sequence `W` over `C_2^r` of rank `r` corresponds
to the kernel code `C = ker H ⊆ F_2^n` (`H` = the matrix with columns `W`), `dim C = k =
n − r`, and

- zero-sum subsets of `W` ⟷ nonzero codewords of `C` (support = the subset);
- min zero-sum length = minimum distance `d(C)`;
- **no two disjoint zero-sums ⟷ `C` is an *intersecting* code** (no two nonzero codewords
  with disjoint supports; for binary codes, equivalently a *minimal* code);
- Lemma A in code language: intersecting `[n,k]` ⇒ `d ≥ k` (a codeword of weight
  `≤ k−1` leaves `≥ r+1` columns, which are dependent — Davenport).
- the padding lemma ⟷ prepending a degenerate coordinate.

Hence

> **`D_2(C_2^r) = 1 + r + K(r)`, `K(r) = max{k : ρ(k) ≤ r}`, `ρ(k) = i(k,2) − k`,**

where `i(k,2)` is the minimum length of a binary intersecting code of dimension `k`.

This reduction was derived independently here and **is published**: Borello–Schmid–Scotti,
*The geometry of intersecting codes and applications to additive combinatorics and
factorization theory* (arXiv:2406.04034, JCTA 2025 — Schmid is the Freeze–Schmid author)
state the Davenport connection as their Theorem 5.12, citing earlier links (their [48],
[42]) for the `j = 2` prime-field case; the `1.26r ≤ D_2 ≤ 1.40r` band recorded in X1-L is
exactly the intersecting-code rate band. **Hit #14 of this programme** (the reduction; the
verbatim Thm 5.12 statement sits in a part of the paper not yet retrieved — flagged below).

### Two communities computed the same numbers

Their Table 2: `i(k,2) = 3, 6, 9, 13, 15, 20, 24, 26` for `k = 2..9`. Concordance with this
programme's exhaustive searches, computed with no knowledge of each other:

| quantity | zero-sum side (ours, exhaustive) | code side (published) |
|---|---|---|
| `ρ(4) = 5` | first `k=4` witnesses at `r = 5` (X1-K/T) | `i(4,2) = 9` (minimal-codes table, Sloane era) |
| `ρ(5) = 8` | `r=7` empty, `r=8` nonempty (X1-U) | `i(5,2) = 13`; and `d_max(12,5) = 4` is Fontaine–Peterson **1959** |
| `ρ(6) = 9` | no `k=6` at `r=8` (X1-U, via FS 7.8) | `i(6,2) = 15`; independently `d_max(14,6) = 5` proven (Grassl) |

Our `r=5` and `r=8` extremal witnesses *are* the parity-check views of the extremal
minimal codes of dimensions 4 and 5. The `D_2(C_2^7) = 12` upper bound is equivalent to a
**66-year-old theorem** (no `[12,5,5]` code, Fontaine–Peterson 1959) — our exhaustive
search reproduced it independently, which now serves as validation of the search rather
than as the result's foundation.

## The conjecture is FALSIFIED — exactly as registered

X1-U registered: `D_2(C_2^r) = r + 3 + ⌊(r+1)/3⌋`, predicting `D_2(C_2^9) = 15`, with the
`r=9` hunt as the test. The literature killed it faster than the search: `i(6,2) = 15`
means a dimension-6 intersecting code of redundancy 9 exists — the (reported unique)
extremal length-15 minimal code, the even-weight subcode of the 2-error-correcting BCH
code. Constructed and verified here from scratch (`x1v_bch_witness_certificate.py`):

```
g(x) = (x+1)(x^4+x+1)(x^4+x^3+x^2+x+1)          [15,6,6], 64 codewords
weight enumerator 1 + 30x^6 + 15x^8 + 18x^10     (matches Cohen–Lempel)
INTERSECTING: True  (all 1953 nonzero pairs share support)
witness = parity-check columns, 15 distinct nonzero vectors spanning F_2^9:
  {1,2,4,8,16,32,64,115,128,230,256,313,421,460,491}
#ZS = 63 = 2^6−1   min-ZS = 6   two_disjoint = False
```

> **`D_2(C_2^9) = 16`** — lower by this certificate, upper by FS Thm 7.8 (`< 16.5`).

The formula `r + 3 + ⌊(r+1)/3⌋` gives 15 ≠ 16: **falsified at its first test**, before the
search ran. The rate-`1/4` reading dies with it; the true growth is governed by `ρ(k)`,
which is irregular (`1, 3, 5, 8, 9, 13, 16, 17` for `k = 2..9`) — no floor formula.

### A classification for free (sourcing caveat)

A degenerate length-15 witness over `C_2^9` would restrict to a length-14 witness over
`C_2^8`, contradicting `D_2(C_2^8) = 14`. So **every** length-15 extremal witness of
`C_2^9` is nondegenerate, i.e. comes from a dimension-6 intersecting `[15,6]` code — and
the extremal minimal code of dimension 6 is reported **unique** (via the minimal-codes
literature; sourced from a survey of arXiv:2312.00885, *not yet read directly* — flagged).
Modulo that citation, the `C_2^9` extremal witnesses form essentially a single
`GL(9,2)`-orbit.

## The ladder (`x1v_ladder_from_code_tables.py`)

`D_2(C_2^r) = 1 + r + K(r)` reproduces **all eight** known/certified values `r = 2..9`
with no mismatch, and extends:

| `r` | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|---|---|---|
| `D_2(C_2^r)` | **17** | 18 | 19 | 21 | 22 | 23 | (25) | (27) | (28) |

Provenance, per rung — these are **not** all equal in standing:

- **`r = 10` → 17, UNCONDITIONAL on refereed sources:** lower = padding of the certified
  `r=9` witness; upper: `k = 7` would need a `[17,7]` intersecting code, hence
  `d ≥ 7` — and `d_max(17,7) = 6` is *proven* (Grassl tables, one-step Griesmer);
  `k ≥ 8` is excluded by the Griesmer bound outright (`ρ(8) ≥ 11 > 10`).
- **`r = 11..15`:** rest on Borello–Schmid–Scotti Table 2 rows `i(7,2) = 20` and
  `i(8,2) = 24`. The retrieved text presents these as exact values, but the surrounding
  wording (proven-exact vs best-known) **could not yet be retrieved** — until it is, these
  five values are *conditional on BSS Table 2 exactness*.
- **`r = 16..18`:** additionally conditional on the unknown `i(10,2)` (Griesmer floor 26).

Every rung satisfies the independent FS Thm 7.8 cap, usually strictly.

## Corrections and standing

- X1-U's conjecture: **falsified**, banner added there. Registered-prediction → falsified
  is this programme's intended failure mode; the conjecture cost one search launch.
- The `r = 7, 8` values keep their direct certificates and now also rest on refereed code
  tables; the `r = 9, 10` values are new here, with the `r = 9` certificate constructed
  from the literature's own extremal object.
- **Gate-pending, before any external claim:** (1) BSS §5–6 full text — the verbatim
  Thm 5.12, the exactness wording of Table 2, and whether they (or their refs [48], [42])
  already *tabulated* `D_2(C_2^r)` values; (2) Cohen–Lempel 1985 / the divisible-minimal-
  codes paper read directly for the `m(6,2)` uniqueness; (3) the standing MathSciNet gap.
  The assembled values may prove to be new-to-print or already assembled by someone —
  either outcome is recorded when known.

## What this changes strategically

The `D_2(C_2^r)` lane and the minimal/intersecting-codes lane are **the same lane** in two
languages. Nothing in the zero-sum lane should be attacked by raw search again before
translating it through the dictionary and checking the code tables first — the shortest
path runs through the bridge in both directions (their exact `i(k,2)` values gave our new
`D_2` rungs; our exhaustive small-`r` enumerations — 3,480 / 138,880 / 3.39B witness
classifications — translate into classifications of short intersecting codes that their
geometric methods do not enumerate).
