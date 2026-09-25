# A linear prime threshold for multiplicative half-interval stability

Status: **proved elementary harmonic strengthening**. A single geometric-series coefficient replaces the previous quadratic prime threshold by a linear one. The two-hole case has a sharper exact endpoint proved by signed products and four interval counts.

Let `p=2H+1>=7` be prime, `I={1,...,H}`, and

\[
d(\gamma)=|I\setminus\gamma I|,
\qquad\gamma\in\mathbb F_p^*.
\]

## 1. A nonidentity multiplier moves more than p/10 points

**Theorem.** If `gamma!=1`, then

\[
\boxed{d(\gamma)>p/10.}
\tag{1}
\]

In particular `d(gamma)<=b` and `p>=10b` force `gamma=1`.

For proof, put `alpha=pi/(2p)`, `zeta=exp(2 pi i/p)`, and

\[
F(t)=\sum_{j=1}^{H}\zeta^{tj}.
\]

For a signed centered nonzero integer representative `t`, the geometric-series identity gives

\[
|F(t)|=
\begin{cases}
\dfrac1{2\sin(|t|\alpha)},&t\text{ odd},\\[4pt]
\dfrac1{2\cos(|t|\alpha)},&t\text{ even}.
\end{cases}
\tag{2}
\]

Indeed, its usual magnitude is `|sin(pi Ht/p)/sin(pi t/p)|`; substitute `Ht/p=t/2-t/(2p)` and use the double-angle identity.

If `gamma` is neither `1` nor `-1`, its centered magnitude is at least two. The odd alternatives in (2) are bounded by `1/(2 sin(3 alpha))`. The even alternatives are below `1/sqrt(2)` because `H alpha<pi/4`; and `1/sqrt(2)<1/(2 sin(3 alpha))` because `3 alpha<=3 pi/14<pi/4`. Hence

\[
2d(\gamma)=|I\mathbin\triangle\gamma I|
\ge|F(1)-F(\gamma)|
\ge\frac1{2\sin\alpha}-\frac1{2\sin3\alpha}.
\tag{3}
\]

The first inequality follows by cancelling common set entries; every uncancelled complex summand has magnitude one.

Write `v=sin alpha`. Since `alpha<=pi/14<1/4`, one has `0<v<1/4`. The last difference in (3) equals

\[
\frac{1-2v^2}{v(3-4v^2)}.
\]

The function `(1-2x)/(3-4x)` is strictly decreasing on `[0,1/16]`, so this is greater than `7/(22v)`, and then greater than `7/(22 alpha)`. Using the elementary bound `pi<22/7`,

\[
\frac7{22\alpha}=\frac{7p}{11\pi}
>\frac{49p}{242}>\frac p5.
\]

Thus `2d>p/5`, proving (1). Finally `gamma=-1` has `d=H>p/10` directly. No estimate on an unknown character sum or outside harmonic-analysis theorem is used.

## 2. Exact two-hole rigidity from p = 17 onward

**Corollary.** If `p>=17` and `d(gamma)<=2`, then `gamma=1`.

The quadratic theorem already bounds the signed centered representatives `a,b` of `gamma,gamma^{-1}` by five. If `gamma!=1`, it is also not `-1`, since `d(-1)=H>2`. Therefore `ab!=1` as ordinary integers, whereas `ab==1 (mod p)` and `|ab|<=25`.

For `p>=17`, this forces `ab=1+p` or `ab=1-p`; larger multiples of `p` exceed the product bound. A positive product in `[18,25]` of two integers with magnitudes at most five can only be `20` or `25`. The latter would give the composite `p=24`, so the positive case forces `p=19` and `|a|,|b|` equal to `4,5` in either order. A negative product with magnitude in `[16,25]` can only have magnitude `16,20,25`; primality of `p=1+|ab|` leaves only `p=17,|a|=|b|=4`.

The resulting interval counts are explicit:

- For `p=17`, multiplication by `4` sends exactly the indices `1,2,5,6` of `I={1,...,8}` back into `I`. Both multipliers `4,-4` therefore have distance four.
- For `p=19`, multiplication by `4` sends exactly `1,2,5,6,7` of `I={1,...,9}` back into `I`; multiplication by `5` sends exactly `1,4,5,8,9` back into `I`. The positive multipliers have distance four, and their negatives distance five.

None has distance at most two. These are the only products allowed by the prior structural bound, proving the corollary. This finite arithmetic endpoint is not a search over hypothetical companion vectors.

## 3. Immediate donor consequences

In either bounded-hole donor theorem, the intersection of the two coordinate half-intervals has size at most `b`. As explained in `MULTIPLICATIVE_HALF_INTERVAL_STABILITY_V1.md`, that is exactly `d(-B/A)`. Therefore their opposite-coordinate conclusion now holds under the weaker sufficient condition

\[
\boxed{p\ge10b,}
\]

and on the first unsaturated face `b=2` it holds for every `p>=17`.

The original core hypotheses remain in force: `b<=H-1` for the fully saturated basis donor and `b<=H-2` for the donor missing one `g`. The linear threshold implies these bounds for `b>=1,p>=7`; they are not discarded when applying the centered restrictions below that threshold.

The rank-two top-overlap elimination therefore extends to every smaller new multiplicity `r` with `p>=10r`, and to `r=2` at all permitted primes `p>=17`. The analogous rank-three top band extends to `p>=10b`.

This theorem supplies sufficient and exact two-hole thresholds; it does not assert that `p/10` is the optimal general constant. The argument was checked locally for both parity cases of the geometric series, the excluded signs, the strict trigonometric estimates, and the exhaustive signed-product endpoint.
