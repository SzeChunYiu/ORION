# The fibre-diameter floor — ORION02.FIBRE_DIAMETER_FLOOR.v1

Frozen before outcome access. Authority: proof and measurement only,
`scientific_authority_delta: NONE`.

## The setting

Let `phi` be a representation map and `F_z = {x : phi(x) = z}` the fibre over `z`.
Let `V` be the target and

    D(z) = sup_{x, x' in F_z} |V(x) - V(x')|

the target diameter of the fibre.

A certificate is **accepted on the fibre** when it is issued for every member of
`F_z`. The load-bearing observation is what that means: since `phi(x) = phi(x') = z`
for all `x, x' in F_z`, a certificate accepted on the fibre and computed from the
representation is **a function of `z` alone**. It cannot separate two members. Every
statement below is a consequence of that one fact.

## Theorem 1 (point-certificate floor)

Let `c(z)` be a deterministic point certificate accepted on `F_z`. Then

    sup_{x in F_z} |c(z) - V(x)| >= D(z)/2.

*Proof.* Take `x, x'` in `F_z` with `|V(x) - V(x')| >= D(z) - eps` for arbitrary
`eps > 0`. By the triangle inequality,

    |V(x) - V(x')| <= |c(z) - V(x)| + |c(z) - V(x')| <= 2 sup_{y in F_z} |c(z) - V(y)|,

so the supremum is at least `(D(z) - eps)/2`. Let `eps -> 0`. ∎

The bound is **tight**: on a two-point fibre `c(z) = (V(x) + V(x'))/2` attains
exactly `D(z)/2`. So `D(z)/2` is the exact minimax radius, not merely a lower bound.

## Theorem 2 (interval-certificate floor)

Let `I(z)` be an interval of radius `r` accepted on `F_z`. If `r < D(z)/2` then
`I(z)` fails to contain `V(x)` for at least one `x in F_z`.

*Proof.* Suppose `I(z)` contained `V(x)` for every `x in F_z`. Then `I(z)` contains
the closure of `{V(x)}`, whose diameter is `D(z)`, so `2r >= D(z)`, contradicting
`r < D(z)/2`. ∎

## Theorem 3 (conditional miscoverage floor)

Let `x, x'` attain the diameter and let the conditional law on `F_z` be the balanced
two-point distribution `1/2` on each. For any accepted interval of radius
`r < D(z)/2`,

    P(V not in I(z) | phi = z) >= 1/2.

*Proof.* By Theorem 2 the interval misses at least one of the two atoms, each of
which carries mass `1/2`. ∎

## Why this is the mechanism behind the ORION-02 negative

`C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID` recorded that arm-conditional
certificates failed conditional validity while raw coverage looked acceptable.
Theorem 3 says that is not a tuning failure and cannot be repaired by recalibration,
better geometry, or a stronger selector: on any fibre with `D(z) > 0`, conditional
miscoverage is bounded below by a quantity no accepted certificate can reduce,
because the certificate cannot see which member it is being asked about.

Raw marginal coverage escapes this only by averaging over fibres — which is exactly
why it "cannot substitute for conditional risk control". The two quantities are
separated by the fibre diameter.

## Relation to the frozen ORION-02 results

`C-C3` supplies, for every `t >= 1`, instances `A_t, B_t` with identical ordered
weights and identical complete labeled pair-gain matrices — hence in one fibre of the
representation `phi = (term count, ordered weights, pair-gain matrix)` — with value
gap `2t - 1`. So `D(z) >= 2t - 1` on that fibre and, by Theorem 1, the floor is
`(2t - 1)/2`, unbounded in `t`.

That recovers the frozen `C2-C4` minimax radius `(2t-1)/2` as the instance of
Theorem 1 at this fibre. The direction of the contribution matters: **Theorem 1 is
not evidence for C2-C4, and this packet does not re-prove it.** No executable `A_t/B_t`
constructor exists here and the family rests on `B.3(c)`, a cross-gadget separability
lemma the manuscript does not state. `C-C3` and `C2-C4` are cited exactly as frozen,
including that conditionality.

What is new is only the generality: the floor is a property of accepted fibre
certificates as such, with `A_t/B_t` demonstrating that `D(z)` — and therefore the
floor — can be made arbitrarily large.

## What would refute this

An accepted certificate achieving worst-case error strictly below `D(z)/2` on some
fibre, or conditional miscoverage below `1/2` on a balanced diameter-attaining pair.
`PROTOCOL.json` searches exhaustively for exactly that over a finite family and
registers the outcome as `T2` or `T3`.

The search must also demonstrate it *can* find violations: a certificate permitted to
see the member index, rather than `z` alone, must beat the floor whenever `D(z) > 0`.
That is control `C1`, and it is the difference between "no counterexample exists" and
"the search cannot see counterexamples".
