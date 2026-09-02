# FINDINGS — profile-Kmin asymptotics V1 (asymptotics-kmin-v1)

**Terminal: `KMIN_ASYM_DETERMINED`** (exit 0, single certified pass). P1
validation gate: **44/44 exact matches** vs the frozen float harness
(m = 5..48, integer equality of `Kmin`), first pass. The parent closure note's
open asymptotic reading — "Kmin grows like c(m)·N with the certified constant
now computable exactly for any m" — is superseded by an exact law for
`c(m) = γ*(m)` through m = 140, two dyadic bands beyond what the parent could
reach (float precision dies ~m = 51, enumeration ~m = 66).

## The law (exact, certified table m = 49..140 + validated 5..48)

```
Kmin(m, 1) = 2^(m-2) · γ*(m),   γ*(m) = 2^(b(m)-4) · (1 + ε(m))
b(m) = ceil(lg m),   ε ∈ [0.0250, 0.2251] for 49 ≤ m ≤ 140
```

- **P2 (discriminating, PASS):** γ*(129) = **16.4006** — the
  exponential-in-`b` law predicts 16; the linear alternative `4·b − 20`
  predicts 12 and is **refuted** (it agrees with `2^(b-4)` only at b = 6, 7,
  by coincidence). Band-start ε is the smallest in the table (0.0250 at
  m = 129, 0.0574 at m = 65): the law is tightest exactly at the band edge.
- **L1 (band jump, PASS):** γ*(129)/γ*(128) = 16.4006/9.2143 = **1.781** —
  `γ*` jumps by ≈ 2 at every `m = 2^B + 1` (B = 6: 4.53 → seen at m = 33;
  B = 7: 4.64 → 8.46; B = 8: 9.21 → 16.40).
- **L2 (band interior, PASS):** γ*(m)/2^(b(m)-4) ∈ (1, 1.35] for all
  m ∈ [65, 140] (observed max 1.2251 at m = 80 — top of the ((32, 32), a) anchor
  ramp — min 1.0250 at band start m = 129).
- **L4 (ε envelope, PASS):** ε(m) ∈ [0, 0.25] for all m ∈ [49, 140]
  (observed [0.0250 at m = 129, 0.2251 at m = 80]).

## Falsified registered prediction (reported, not buried)

**L3 anchor clause — FALSIFIED.** The registered claim "argmax anchor size
≤ 2^(b-3)" fails on two stretches: m = 86..96 (anchor rides 22 → 32) and
m = 121..128 (anchor 25 → 32), all in band b = 7. The **max-block clause
holds everywhere** in [65, 140]: every argmax profile's largest block is
exactly `2^(b(m)-2)` (32 in band 7; 64 in band 8); fillers and anchor sit at
or below `2^(b(m)-3)`, plus at most one just-below-`2^(b(m)-2)` rider block
(25..31 in band 7; 49..60 in band 8). Refined law:
**anchor ∈ [2^(b-3)/2, 2^(b-2)]** — the anchor grows to the full max block
size as m approaches the band top, harvesting the extra gap (this is the
mechanism behind ε reaching its in-band maximum at the top of each anchor ramp
(0.2251 at m = 80; band tops m = 64/128 sit at 0.161/0.153), and the reason the winner at
band tops is "all max-blocks, anchor = last block").

## Exact within-band ramp arithmetic (verified to 6 decimals)

The table's γ* is piecewise linear in m within a band, with slopes exactly
`[(B+1)/2 − (b(rider block)+2)/2] / (2k−1)`:
- m = 129..140 (`((64, j), 16)`, k = 3): slope = (4.5 − 4)/5 = **+0.1** ✓
  (16.400574 → 17.500574 in steps of exactly 0.100000).
- m = 121..128 (`((32, 32, 32), a)`, k = 4): slope = (4 − 3.5)/7 =
  **+1/14 ≈ 0.0714** ✓.
- Band starts drop back to 2^(B−4)(1+ε_min) by switching to a bigger block
  family (16 → 32 at m = 65; 32 → 64 at m = 129).

## Two-sided pinch (proof status)

- *Construction (proved, explicit):* the uniform family j = b(m) − 3 plus
  bounded anchor/filler correction gives γ* ≥ 2^(B−4) − O(B). The exact table
  shows the construction is realizable within ε ≤ 0.2251 through m = 140.
- *Upper bound (all profiles; sketch + numerics):* `b(s) + 2 ≥ lg s + 1` and
  Jensen on convex `s·lg s` give Σ sᵢ(b(sᵢ)+2) ≥ S(lg(S/k) + 1) for any k
  variable blocks covering S; combined with the divisor 2k−1 this caps γ by
  max_j (B−j−1)·2^(j−2) + O(B) = 2^(B−4) + O(B). The exact DP table
  certifies the O(B) term stays ≤ 0.2251·2^(B−4) for m ≤ 140. A fully formal
  write-up of the O(B) constants remains open (registered here as such).

## Method (why exact, why fast)

All C2–C10 cost quantities are dyadic rationals with denominator dividing
2^(m−2) (L = 1) → pure integer arithmetic. The competitor search becomes a
DP over (covered size, #variable blocks, running max-b) — O(m³) bigint ops
per m, seconds at m = 140 where the parent's enumeration is infeasible
(m = 66 exceeded 10 min). Decomposition: designated anchor block + multiset
of variable blocks (permutation-symmetry lemma of the parent), boundary
`(1, q)` family handled explicitly.

## Reading for the paper's claim

The certified minimality constant is not an opaque `c(m)·N`: it is
`2^(m + b(m) − 6)·(1 + ε(m))` — exponential in m with a **factor-2 ladder at
every m = 2^B + 1**, tightest at band starts (ε → 0.025) and loosest at the top of the
first in-band anchor ramp (ε → 0.225). Open beyond scope: L > 1 (Kmin(m,L) = L·Kmin(m,1) + O(m)
up to floor effects), m > 140, formal O(B) constants, and the exact
within-band piecewise-linear ε profile (empirically fully explained by the
anchor-ramp arithmetic above).
