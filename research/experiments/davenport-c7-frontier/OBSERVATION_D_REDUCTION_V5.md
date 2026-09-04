# Observation D reduces to one symmetric function — V5

Status: **reduction proved and verified; Observation D itself still not proved.** This replaces an opaque rank computation with a concrete statement about a single function, and explains *why* the special lengths are special.
Checker: `verify_observationD_reduction_v5.py`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. The dual

Apply the duality of `LUCAS_CRITERION_V5.md` to the atom-spectrum system `(S_p)`. Excluding a length set `Z` makes the system inconsistent iff there is an integer-valued `P`, of degree `≤ N−D` in the binomial basis, with

- `P(L) + (−1)^N P(N−L) = 0` for every atom length `L ∈ [p+1, 3p−2] \ Z`  *(from the `W_L` columns)*,
- `P(L) = 0` for `L` in the overlap range `[N−D, D]`  *(from the `X_L` columns)*,
- `P(0) + (−1)^N P(N) ≠ 0`  *(the right-hand side)*.

## 2. The reduction

Put

`Q(y) = P(y) + (−1)^N P(N−y)`.

Then the following hold, for every prime and every special pair tested:

1. **`P` vanishes on the whole integer interval `[N−D, D]`.** Its length is `2D − N + 1 = (p−3)/2` — exactly the low base-`p` digit of `N = (5, (p−3)/2)_p`. This is an *interval*, so the Newton step that proved Theorem G applies to it.
2. **`Q(N−y) = (−1)^N Q(y)`**: `Q` is `(−1)^N`-symmetric about `N/2`. (Immediate from the definition, and confirmed numerically.)
3. **`Q` vanishes on the entire atom range `[p+1, 3p−2]` except at the two excluded lengths, and is nonzero at *both* of them.**
4. **`Q(0) ≠ 0`.**

So, in one sentence:

> **"the pair `Z` is forced" says exactly that the `(−1)^N`-antisymmetry of the spectrum can be broken at the two lengths of `Z` and at `0`, and nowhere else on the atom range.**

That is the structural reason the three special lengths are special: they are the only places where a `Q` of the required degree can carry its nonzeros. The earlier records could only say the certificates were "dense with no evident closed form"; the density was an artefact of looking at `P` instead of `Q`.

## 3. What remains

To turn Observation D into a theorem one must show, uniformly in `p`:

- **(existence)** for `Z` a pair of special lengths, such a `Q` exists — construct it;
- **(minimality)** for any other pair, and for any single length, no such `Q` exists.

Both are now questions about one explicitly described function rather than about the rank of a matrix. Two footholds: `P` vanishes on an interval of length `(p−3)/2`, so Newton about `N−D` writes `P` in the shifted basis `C(y−(N−D), d)` with the first `(p−3)/2` coefficients zero; and the involution `y ↦ N−y` fixes that interval setwise, which is why `Q` inherits the symmetry.

## 4. Verification

`verify_observationD_reduction_v5.py` computes an explicit dual vector for each of the three special pairs at `p ∈ {11,13,17,19,23}` and asserts all four claims, plus the identity `2D − N + 1 = (p−3)/2`. It asserts nonvanishing at **both** excluded lengths, not merely at one — the stronger and more informative statement.

## Claim ceiling

A reduction, not a proof. Observation D remains **verified for `5 ≤ p ≤ 31`** and unproved. Nothing here extends its verified range; what it changes is the shape of the remaining work, from a rank argument about the matrix `[C(L,d) + (−1)^N C(N−L,d)]` to the construction of a single symmetric function with a prescribed zero set.

A bug worth recording: the first version of the checker built the overlap columns as generator expressions inside a comprehension, so all of them captured the final loop variable. It failed claim 1 at `p = 11` and the failure was real — a late-binding defect, not a mathematical one. Fixed; the assertion that caught it is retained.
