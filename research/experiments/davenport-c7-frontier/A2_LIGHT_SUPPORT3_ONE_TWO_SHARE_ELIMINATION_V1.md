# First-corridor `a=2` light-share multiplicities one and two are impossible — V1

Status: **proved prime-uniform branch elimination**. For every prime `p>=7`, an exact-support-six first-corridor support-three companion of the support-four maximal-atom type `a=2` cannot reuse the light value `e3` only once or twice. The one-share statement in fact holds already for `p>=5`. The lower endpoint is sharp: at `p=5`, the two-share face has four ordered exact-depth survivors.

No generalized Davenport value or novelty/priority claim is made here.

## 1. Setup

Let

`p=2h+1`, `m=(3p-1)/2=3h+1`,

and consider the support-four maximal atom

`U=e1^(p-1)e2^(p-1)s^2 g^(p-2)`,

where

`s=e3`, `g=s-2^(-1)(e1+e2)`.

Assume the first-corridor maximal pair `UV` attains total support six and lies in the support-three rank-two branch sharing only the light value `s`. Then

`V=s^c x^r y^t`

for two genuinely new values `x,y`, with

`c+r+t=m`.

After interchanging `x,y`, assume

`r<=t<=p-1`.

The companion is an atom, so its coefficient relation is

`c s+r x+t y=0`,

and the pair `UV` is `(m-1)`-short-zero-free.

## 2. A light-direction lifting identity

Because `2*2^(-1)=1` in `F_p`,

`boxed{2s=2g+e1+e2.}`

Thus two additional formal copies of `s` can be realized inside `U` using four terms. The pair also contains `c+2` actual copies of `s`, namely `c` from `V` and two from `U`.

For a scalar multiple `n` of the companion relation, put

`D=[nc]_p`, `A=[nr]_p`, `B=[nt]_p`.

Whenever `A<=r` and `B<=t`, the `x,y` terms are available in `V`. The `D s` part may be realized by actual `s` terms and, when needed, copies of the displayed two-for-four identity. Every relation below uses only one of the following certified costs:

| shared multiplicity | required `D` | certified term cost for `D s` |
|---:|---:|---:|
| `c=1` | `2` | `2` actual `s` terms |
| `c=1` | `3` | `3` actual `s` terms |
| `c=2` | `3` | `3` actual `s` terms |
| `c=2` | `4` | `4` actual `s` terms |
| `c=2` | `5` | `3` actual `s` terms plus `2g+e1+e2=2s`, total cost `7` |

If the resulting total cost is at most `m-1`, it is a forbidden nonempty zero-sum subsequence of `UV`.

## 3. Eliminate one shared copy

Assume

`V=s x^r y^t`.

Then

`r+t=m-1=3h`.

Since `t<=p-1=2h`, write

`r=h+d`, `t=2h-d`,

where

`0<=d<=floor(h/2)`.

### Interior `d>=1`

Double the atom relation. Its least residues are

`2s+(2d-1)x+(p-2d-2)y=0`.

All coefficients fit the pair. The length is

`2+(2d-1)+(p-2d-2)=p-1<m`.

This contradicts pair short-freeness.

### Boundary `d=0`

Now `(r,t)=(h,p-1)`. Triple the atom relation:

`3s+(h-1)x+(p-3)y=0`.

The pair contains exactly three actual `s` terms. The length is

`3+(h-1)+(p-3)=p+h-1=m-1`.

This is again forbidden.

Therefore:

> **One-share theorem.** For every odd prime `p>=5`, the `a=2` light-share support-three equality branch cannot have `v_s(V)=1`.

## 4. Eliminate two shared copies

Assume

`V=s^2 x^r y^t`.

Then

`r+t=m-2=3h-1`.

Since `t<=2h`, write

`r=h-1+d`, `t=2h-d`,

with

`0<=d<=floor((h+1)/2)`.

### Interior `d>=2`

Double the relation. The residue relation is

`4s+(2d-3)x+(p-2d-2)y=0`.

The pair contains four actual `s` terms, and the total length is

`4+(2d-3)+(p-2d-2)=p-1<m`.

So every interior row is impossible.

### First boundary `d=0`

Here

`(r,t)=(h-1,p-1)`.

#### `p=4k+3`

Take `n=h+1`. The multiplied coefficient vector is

`(1,k,h)`.

It lies componentwise below `(2,h-1,p-1)`, with first coordinate strictly smaller. Hence it is a nonempty proper zero-sum subsequence of `V`, contradicting that `V` is an atom.

#### `p=4k+1`

In the range `p>=7`, this forces `p>=13`. Take `n=h+2`. The residue relation is

`3s+(k-2)x+(h-1)y=0`.

All coefficients fit and the length is

`3+(k-2)+(h-1)=3k<m`.

Thus the first boundary is empty.

### Second boundary `d=1`

Here

`(r,t)=(h,p-2)`.

#### `p=4k+3`

Take `n=h+2`. The residue relation is

`3s+kx+(p-3)y=0`.

Its length is

`3+k+(p-3)=p+k<m`.

#### `p=4k+1`

Again `p>=13`. Take `n=h+3`. The residue relation is

`5s+(k-1)x+(p-5)y=0`.

Realize `5s` using three actual `s` terms and the four-term identity `2g+e1+e2=2s`. The resulting zero-sum has term length

`7+(k-1)+(p-5)=5k+2`.

Since `m=6k+1`, this is less than `m`.

Thus the second boundary is empty as well.

Combining the three multiplicity regions:

> **Two-share theorem.** For every prime `p>=7`, the `a=2` light-share support-three equality branch cannot have `v_s(V)=2`.

## 5. Combined consequence

The heavy-share support-three branch is already eliminated in `A2_HEAVY_SUPPORT3_DOUBLE_TRIPLE_V1.md`. The present theorem gives the following new reduction on the only remaining support-three side:

> For every prime `p>=7`, every hypothetical exact-support-six `a=2` support-three companion sharing the light value must satisfy
>
> `boxed{v_e3(V)>=3.}`

This is a local first-corridor theorem. It does not eliminate shared multiplicity three or greater, and it does not treat the support-four rank-three equality branch.

## 6. Sharp `p=5` mutation boundary

The restriction `p>=7` in the two-share theorem is necessary. At `p=5`, `a=2`, `c=2`, the exact equality-face referee has four ordered survivors:

- `(r,t,x,y)=(2,3,(1,3,0),(1,3,1))`;
- `(2,3,(3,1,0),(3,1,1))`;
- and the two ordered reversals with `(r,t)=(3,2)`.

These are precisely the small-prime control behind the previously recorded `p=5` support-six exception. They prevent a checker that accidentally rejects every two-share face from passing.

## 7. ORION verification architecture

`check_a2_light_support3_one_two_share_elimination_v1.py` verifies every symbolic residue and length identity for all primes through `1009`. It independently runs the exact support-six depth predicate at `p=5` and freezes the four ordered mutation survivors.

`verify_a2_light_support3_one_two_share_independent_v1.cpp` changes the load-bearing mechanisms:

- it computes the shortest cost of every radial target `D s` by bounded enumeration of the actual resources `s^(c+2) g^(p-2) e1^(p-1) e2^(p-1)`, rather than using the displayed case costs;
- it scans every scalar multiplier for every atom-compatible multiplicity row through prime `1009`, rather than following the symbolic congruence split;
- at `p=5`, it builds the maximal-atom depth table by occurrence-level dynamic programming and tests all companion subsequence cardinalities by a separate length-bitset dynamic program.

The independent scan returns zero scalar residuals for every prime `p>=7`, while the `p=5`, `c=2` mutation retains two residual multiplicity rows and exactly four full equality-face survivors.

A branch-scoped workflow runs the primary replay, the independent optimized replay, and the independent replay under AddressSanitizer and UndefinedBehaviorSanitizer.

## Boundary

- The `a=2` light-share family with shared multiplicity `c>=3` remains open.
- The `a=2` support-four rank-three equality branch remains open.
- The theorem assumes the first maximal corridor and a support-four maximal atom.
- The finite `p=5` row is a declared mutation/control, not evidence against the `p>=7` theorem.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
