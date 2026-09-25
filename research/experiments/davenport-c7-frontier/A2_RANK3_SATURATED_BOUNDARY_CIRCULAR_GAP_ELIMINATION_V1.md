# Type-two saturated new-value boundary: a circular-gap mixed elimination — V1

Status: **proved prime-uniform mixed-subsequence elimination, internally cross-checked**. The constant-donor inverse normal form converts every sufficiently overlapping row with a saturated new multiplicity into a one-dimensional circular-gap problem. A parity-adaptive selector reaches the square-root-of-`p` overlap scale. One close pair gives an actual mixed zero-sum substantially below the forbidden length.

This removes a full variable-overlap band. It does not close smaller-overlap rows outside the displayed inequality, unsaturated new multiplicities, or the generalized Davenport formula.

## 1. Exact setup and theorem

Let `p=2H+1>=7` be prime, `u=H+1=2^(-1)` in `F_p`, `m=p+H`, and `s=(u,u,1)` in the basis `(e1,e2,g)`. Set

`U=e1^(p-1)e2^(p-1)g^(p-2)s^2`.

Consider a hypothetical zero-sum companion

`V=s^c g x^r y^(p-1)`,

where

`1<=c<=H-1`, `r=H-c>0`.

The values `x,y` are the displayed new values and all occurrences belong to the sequences shown. Define

`E=2 floor(c/2)`.

> **Theorem.** If
>
> `p<(c+1)^2`,                                      (1)
>
> then `UV` contains a nonempty zero-sum of length below `m`.

The conclusion is based on an explicit occurrence formula and an elementary circular-gap argument, not a search through the new values or primes.

## 2. The exact inverse theorem supplies the plane family

Suppose toward contradiction that `UV` is short-free. The shared donor is

`B_(c+2)=e1^(p-1)e2^(p-1)g^(p-1)s^(c+2)`.

Here `3<=c+2<=H+1`. The exact theorem in `A2_CONSTANT_DONOR_INVERSE_CLASSIFICATION_V1.md` therefore restricts `y` to

`y=(A,-A,1)`, `A!=0`,                                (2)

or to its exceptional family with `c=1` or `(p,c)=(11,2)`.

Neither exception is compatible with (1). When `c=1`, its right-hand side is `4`, below every allowed prime. At `(p,c)=(11,2)`, its right-hand side is `9`, again below `p`. Thus (2) holds throughout the theorem's stated range.

The companion relation gives

`r x=y-c s-g`.                                       (3)

This is an identity for the sum of all `r` actual `x` occurrences; it does not assert that those occurrences may be divided as a sequence by a field scalar.

## 3. A general mixed occurrence certificate

Let integers `n,j` obey

`0<=n<=c`, `1<=j<=n+1`,

and suppose the two forced least residues satisfy

`[nu-jA]_p+[nu+jA]_p=n`.                              (4)

Then the following is an actual zero-sum subsequence of `UV`:

`x^r y^(j-1) s^(c-n) g^(1+n-j)`

`             e1^[nu-jA]_p e2^[nu+jA]_p`.             (5)

Indeed, by (3), the new-value sum is `j y-c s-g`. After adjoining the displayed `s,g` counts, it becomes

`j y-n s+(n-j)g`,

whose coordinates are `(jA-nu,-jA-nu,0)`. The two saturated counts cancel them.

Every count is available:

- all `r` copies of `x` are used;
- `0<=j-1<=n<=c<=H-1<p-1` copies of `y` are used;
- `0<=c-n<=c<c+2` copies of `s` are used;
- `0<=1+n-j<=n<=c<p-1` copies of `g` are used;
- (4) makes both saturated counts nonnegative and at most `n<=c<p-1`.

The sequence is nonempty because `r>0`. Its length is exactly

`r+(j-1)+(c-n)+(1+n-j)+n=H+n<=H+c<m`.                (6)

Thus it remains to obtain (4) for one permitted pair `n,j`.

## 4. The fixed-even circular-gap selector

This section preserves the initial fixed-even route, which proves the narrower sufficient condition `p<2(floor(c/2)+1)^2=(E+2)^2/2`. The next section proves the stronger bound (1).

Use `n=E`, which is even and at most `c`. Under the present inequality, `c>=2`, so `E>=2`. Consider the `E+2` distinct residues

`0,A,2A,...,(E+1)A`

on the cyclic group `F_p`, represented on the integer circle of circumference `p`. They are distinct since `A!=0` and `E+1<=c+1<=H<p`.

Their `E+2` positive circular gaps sum to `p`. Hence some gap is at most

`floor(p/(E+2))`.

The difference of its two endpoints is a signed multiple `jA` for an integer `1<=j<=E+1`. The centered magnitude of that multiple is therefore at most the gap, and the present inequality gives

`min([jA]_p,[-jA]_p)<=floor(p/(E+2))<=E/2`.           (7)

The final inequality follows because `p/(E+2)<(E+2)/2=E/2+1`, and `E/2` is an integer.

As `E` is even, `Eu=E/2` in `F_p`. Condition (7) means that the two residues in (4) are the two nonnegative integers `E/2-d,E/2+d` for some `0<=d<=E/2`, in either order. Their sum is exactly `E`, with no modular carry. Hence (4) holds with `n=E` and the selected `j`.

Applying (5)--(6) proves this narrower sufficient range. The constructed short length is `H+E`, at most `H+c<=p-2`.

## 5. The adaptive-parity circular-gap selector

Now suppose the theorem's full inequality (1) holds:

`p<(c+1)^2`.

Consider instead the `c+1` distinct circle points

`0,2A,4A,...,2cA`.

They are distinct because `2A!=0` and `c<p`. Their gaps sum to `p`, so some signed endpoint-index difference gives an integer `1<=j<=c` and a centered representative `v` with

`v==2jA (mod p)`, `|v|<=floor(p/(c+1))<=c`.         (8)

The sign of the gap only determines whether the representative is positive or negative; it does not change the positive occurrence parameter `j`, which is the absolute difference of the two indices.

Let `n` be the smallest integer at least `max(j-1,|v|)` with

`n==v (mod 2)`.

If `|v|<=c-1`, both entries in the maximum are at most `c-1`, so the parity adjustment increases their maximum by at most one. If `|v|=c`, the maximum is exactly `c` and already has the parity of `v`, whether `v=c` or `v=-c`; in that case `n=c`. Thus in every case

`0<=n<=c`, `1<=j<=n+1`.

Moreover, the two integers

`(n-v)/2`, `(n+v)/2`

are nonnegative and at most `n<=c<p`. Since `2jA=v` in `F_p`, they are precisely the least residues `[nu-jA]_p` and `[nu+jA]_p`. Their sum is `n`, with no carry. Thus the mixed certificate (5) is available and has length `H+n<=H+c<=p-2<m`.

This proves the theorem. The final threshold includes the whole fixed-even range and the endpoint `(p,c)=(7,2)`. Since the prime `p` is not a square, the condition is equivalently `c>=floor(sqrt(p))`; the integer inequality (1), including its strict endpoint, remains the authoritative statement.

## 6. Scope, authority, and next interface

The complete range is exactly (1) with `1<=c<=H-1` and `r=H-c`; no asymptotic replacement of its floor or strict inequality is used. The square-root scale describes its size but is not the theorem's hypothesis.

The argument uses the complete new-value part `x^r` together with a selected number of `y` occurrences. It therefore passes the pure-power obstruction identified by the inverse theorem. It does not rely on dividing an occurrence count by `r`, and it does not require the new-value subsequence to lie in the original overlap plane.

A discarded partial-`x` route incorrectly treated the third coordinate of `x` as zero. The actual relation (3) gives `r x_C=-c` and `x_1+x_2=x_C=-c/r`; omitting the contribution of `c s` invalidates that projection and any partial-occurrence length estimate derived from it. The proof above retains the full relation throughout.

There is also an infinite obstruction to extending the specific mixed formula (5) to all smaller overlaps. Suppose `p>=(c+1)(c+2)` and choose `A=(c+1)/2` in `F_p`. For every `1<=j<=c+1`, the integer `j(c+1)` and its complement `p-j(c+1)` are both at least `c+1`. Hence the centered magnitude of `2jA` is at least `c+1`. But (4) for any `n<=c` would force `2jA` to have a centered representative of magnitude at most `n`. Thus no choice within formula (5) works for these values. This is a proved limitation of that occurrence family; it does not assert that the full companion survives other mixed subsequences.

The coordinating researcher supplied the mixed formula and the fixed-even circular-gap reduction. The independently tasked proof auditor supplied the adaptive-parity selector, and the inverse specialist supplied its `|v|=c` endpoint sharpening to (1). These steps were independently checked across the team, including the signed residue, parity choice, capacities, strict threshold, original formula, circle argument, and both exact inverse-theorem exceptions. This is internal mathematical review, not external referee or novelty approval.

Independent internal audit: GREEN for the fixed-even proof by the separate proof auditor, for the adaptive-parity extension by the inverse specialist and coordinator, and for the final endpoint sharpening by the proof auditor. These checks cover the exact group identity, all six occurrence capacities, both inverse exceptions, the number and distinctness of circle points, the signed endpoint-index difference, and the strict floor and parity conversions to a residue pair with no carry. No full first-corridor or generalized Davenport value is asserted.
