# Type-two rank-three one-light-share layer: complete elimination

Status: **proved for every prime p>=7, with a separately tasked internal proof audit of the new certificate**. This closes the whole overlap layer `c=1`, including its first unsaturated row. It does not close all exceptional type-two companions or the full first corridor.

Let `p=2H+1>=7`, `m=3H+1`, and

`U=e1^(p-1)e2^(p-1)g^(p-2)s^2`, `2s=e1+e2+2g`.

Suppose a zero-sum rank-three support-four companion shares exactly one copy of the light value:

`V=s g x^r y^t`, `r+t=m-2`, `r<=t`.

Assume toward contradiction that `UV` has no nonempty zero-sum shorter than `m`. The shared heavy count is exactly one because `U` already supplies `g^(p-2)`. The proved shared-donor interior reduction in `A2_RANK3_SHARED_DONOR_BOUNDARY_REDUCTION_V1.md` gives

`r=H-k`, `t=p-2+k`, `k in {0,1}`.

The row `k=1`, with `r=H-1,t=p-1`, is already eliminated for every prime by `A2_RANK3_ONE_SHARE_SATURATED_ELIMINATION_V1.md`.

For the remaining row `k=0`, the relation is

`s+g+Hx+(p-2)y=0`.

Multiply by three and use

`3H=p+(H-1)`, `3(p-2)=2p+(p-6)`.

The actual occurrence sequence

\[
Z=s^3g^3x^{H-1}y^{p-6}.
\]

is therefore zero-sum. Its capacities are checked as ordinary integers:

- `UV` contains exactly three copies of `s`, so `s^3` fits.
- `UV` contains `p-1` copies of `g`, so `g^3` fits.
- `1<=H-1<=H`, so the new `x` count fits.
- `1<=p-6<=p-2` for every `p>=7`, so the new `y` count fits.

Its length is

\[
|Z|=3+3+H-1+p-6=p+H-1=m-1,
\]

contradicting short-freeness. This also covers `p=7`, where the `y` count is one. The new certificate itself uses no rank hypothesis or inverse theorem beyond the displayed relation and capacities.

Together the two boundary rows and the prior interior elimination prove complete emptiness of `c=1` for exceptional rank-three type two.

The new row is not derived by applying a saturated-value theorem to `p-2` copies. It uses an independent occurrence-level relation. Fixed-ref search at `c66be6545384ee79b5bade07844b51c1e3df8f68` found no earlier statement or certificate for this unsaturated row; this is a repository novelty check, not a literature priority assertion. A separate proof-audit researcher and the coordinating researcher checked the residue identities, positivity, exact shared capacities, and strict length.
