# ORION-RG X1-W — classifying the `C_2^8` extremal witnesses: a fully registered prediction

## The last unclaimed piece of this lane

BSS (Remark 5.15) print the values; Kurz (arXiv:2312.00885, read directly) classifies the
extremal *codes*: `m(5,2) = 13` is attained by **exactly two non-equivalent codes**, with
weight enumerators (verbatim) `1 + 8x⁵ + 8x⁶ + 4x⁷ + 7x⁸ + 4x⁹` (`|Aut| = 8`) and
`1 + 6x⁵ + 12x⁶ + 4x⁷ + 3x⁸ + 6x⁹` (`|Aut| = 48`); and the minimal `[15,6]` code is
confirmed **unique** (settling the sourcing debt flagged in X1-V).

Nobody has connected this to the *witness census*: every length-13 extremal `D_2` witness
over `C_2^8` is nondegenerate (a degenerate one would restrict to a length-12 witness over
`C_2^7`, contradicting `D_2(C_2^7) = 12`), hence is the parity-check view of one of Kurz's
two codes. Since a `GL`-stabiliser of a witness is exactly the permutation automorphism
group of its code, the census must satisfy `g_i = b_i · 8! / |Aut_i|` (`b_i` = number of
independent 8-subsets of the witness).

## Registered prediction — filed while the enumeration is still running

The fingerprint enumeration over all 3,971,520 basis-containing witnesses must return:

1. **Exactly 2 classes** (fingerprint = zero-sum size profile = kernel weight enumerator).
2. Class B: profile `{5:6, 6:12, 7:4, 8:3, 9:6}`, count **584,640** — computed in advance
   as `b_B · 8!/48 = 696 · 840` from a reconstruction of Kurz's second code (obtained by
   his own recipe: coordinate omission from the unique `[15,6]` code; 15 of 210 omission
   pairs produce it; weight enumerator matches verbatim; witness property verified).
3. Class A: profile `{5:8, 6:8, 7:4, 8:7, 9:4}`, count **3,386,880** (= total − 584,640),
   which forces `b_A = 672` via `b_A · 8!/8 = g_A` — checkable post-hoc on the returned
   representative.

Any deviation falsifies either the stabiliser↔automorphism identification, Kurz's
two-code classification, or our census — and will be reported as such.

## Instrument validation (already done, before the run)

The fingerprint pass reproduced ground truth on both available test beds:
- `r = 6, k = 4`: exactly **4 classes** — equal to the 4 known orbits (X1-T), so the
  invariant is complete there; total 14,685 ✓; class representatives match the X1-T orbit
  representatives.
- `r = 7, k = 4`: 13 classes, one of which has count exactly **21,840** — the min-ZS-5
  stratum of X1-U, recovered to the witness.

A failed transcription of Kurz's generator matrices from the PDF (pdftotext mangles the
side-by-side matrix block) produced wrong codes and wrong predictions (`644/651`, total
mismatch); those numbers were **discarded before registration** and the reconstruction was
redone from the verified BCH code instead. Recorded because "predicted from a corrupted
source" is exactly the failure this programme's registration discipline exists to catch.

## CONFIRMED — to the digit

The enumeration returned (`r8fp.log`, 52,768,800 leaves):

```
fingerprint classes (kernel weight-enum): 2
  class 0 count 3386880 rep 15 51 85 169 205
  class 1 count  584640 rep 15 51 85 169 206
```

Every registered number hit exactly. Post-hoc checks on the returned representatives:
class 0's zero-sum profile is `{5:8, 6:8, 7:4, 8:7, 9:4}` — Kurz code 1's weight
enumerator verbatim — with `b = 672` (exactly the value the prediction forced) and
`672·8!/8 = 3,386,880`; class 1's profile matches Kurz code 2 with `b = 696` and
`696·8!/48 = 584,640`.

> **Theorem (computational).** The extremal `D_2` witnesses of `C_2^8` (length 13) form
> exactly **two** `GL(8,2)`-orbits, in bijection with the two non-equivalent extremal
> minimal `[13,5]` codes of Kurz/Sloane, with stabilisers of orders 8 and 48 (equal to the
> codes' automorphism groups) and orbit sizes `|GL(8,2)|/8` and `|GL(8,2)|/48`.

The complete orbit table of this lane now reads:

| `r` | 2 | 3 | 4 | 5 | 6 | 8 | 9 |
|---|---|---|---|---|---|---|---|
| `GL`-orbits of extremal witnesses | 2 | 1 | 3 | 1 | 4 | **2** | 1 (mod uniqueness, Kurz) |

(`r = 7` has ≥ 13 fingerprint classes and is left open; `r = 9` follows from the
`[15,6]` uniqueness plus the nondegeneracy argument of X1-V.)

## Lane status

This is the closing atom of the RG lane. Per the standing venue calibration, everything
surviving here (criterion framework, classification layer, this census) assembles into a
specialist paper at best. The programme's top-tier ambition moves to the queued lanes.
