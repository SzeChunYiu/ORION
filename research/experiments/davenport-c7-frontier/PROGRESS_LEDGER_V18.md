# Davenport prime-uniform generalization checkpoint — V18

Status: live theorem-generalization checkpoint. No novelty/priority authority. This file supplements the older C7-focused `PROGRESS_LEDGER_V1.md` and records the prime-uniform advances made after its V17 state.

## 1. Candidate theorem and maximal corridors

For prime `p>=5`, put

`M_p=(5p-5)/2`.

The target remains

`D_k(C_p^3)=kp+M_p=((2k+5)p-5)/2`, `k>=2`.

At the critical three-factor completion length

`N_3(p)=(11p-3)/2`,

a factorization containing a maximal atom of length `3p-2` has a prime-uniform corridor

`C_j(p)=(p+j, p+(p+1)/2-j, 3p-2)`,

`1<=j<=floor((p+1)/4)`.

Let `U` be the maximal atom and let `V` be the longer nonmaximal companion, of length

`m=p+b`, `b=(p+1)/2-j`.

Hereditary first-failure rigidity gives

- `z(UV)=2`;
- `UV` is zero-sum-free through length `m-1`;
- every rank-two subgroup `K` satisfies the pair-plane cap

`|(UV)_K|<=4p-3-(m-1)`.

## 2. All-corridor support-six theorem

`MAXIMAL_PAIR_SUPPORT6_ALL_CORRIDORS_V1.md` proves for every prime `p>=5` and every maximal corridor

`boxed{|supp(UV)|>=6.}`

The old `j<=2` support-complement argument is generalized by allowing scalar residues `1,2,3` of the complement relation. A hypothetical five-support pair always yields a nonempty zero-sum subsequence of length `<p`.

The same file freezes the first exact method ceiling: scalar multiples of the complement relation alone cannot eliminate support six. A genuine rank-three/projective input is required next.

## 3. Exact support-six normal form when the maximal atom has support four

A support-four maximal atom has the prime-uniform canonical form

`U=e1^(p-1)e2^(p-1)e3^a g4^(p-a)`,

`g4=e3-a^{-1}(e1+e2)`,

`1<=a<=(p-1)/2`.

Assume `|supp(UV)|=6`. Then `SUPPORT4_MAXIMAL_PAIR_SUPPORT6_NORMAL_FORM_V1.md` proves:

- `V` cannot use the two saturated actual values `e1,e2`;
- exactly two actual support values of `V` lie outside `supp(U)`;
- `V` has support 3 or 4;
- support 3 forces rank at most two;
- if `V` is rank two, the amount of U-mass in its plane is at most

`p+2j-3`.

For the first corridor `j=1`, equality has exactly two branches:

1. a support-three rank-two companion whose plane meets `supp(U)` in exactly one unsaturated point;
2. a support-four rank-three companion sharing both unsaturated points.

## 4. Exact representation-depth formulation

Define

`rho_U(x)=min{|T|: T|U, sigma(T)=x}`.

For every nonempty proper `W|V`, pair short-freeness is equivalent to the graded inequality

`boxed{|W|+rho_U(-sigma(W))>=m.}`

Equivalently, after complementing in `V`,

`rho_U(sigma(W))>=|W|`.

For the canonical support-four maximal atom, writing `u=a^{-1} mod p`, one has the exact one-parameter formula

`rho_U(x1,x2,x3)=min_t([x1+ut]_p+[x2+ut]_p+[x3-t]_p+t)`,

where `0<=t<=p-a` and `[x3-t]_p<=a`.

A fresh C++ depth-oracle implementation that does not materialize U-subset tables independently reproduces the old C7 first-stage counts

`538,24,0`

and gives the p=5 base counts

`169,30`.

## 5. Antipodal depth and simultaneous quotient atoms

Put

`delta_U(x)=rho_U(x)+rho_U(-x)`.

`SUPPORT4_ANTIPODAL_DEPTH_AND_QUOTIENT_ATOMS_V1.md` proves

`delta_U(x)>=p`

for every nonzero `x`, and classifies equality exactly.

The two saturated projective lines `<e1>` and `<e2>` lie entirely in the equality shell `delta=p`. But every proper companion subsum has

`delta_U(sigma(W))>=m>p`.

Consequently:

- no proper V-subsum lies on either saturated line;
- no term of V lies on either saturated projective direction;
- the projections of V modulo `<e1>` and modulo `<e2>` are both atoms of unchanged length `m` in `C_p^2`.

For the type `a=1`, the third saturated direction `<g4>` gives a third quotient atom.

## 6. Modular-inverse support selector

The exact singleton depths of the two unsaturated actual values are

`rho_U(-e3)=3p-3-2u`,

`rho_U(-g4)=p+2u-3`.

Thus reuse of `e3` requires

`u <= (3p+2j-5)/4`,

while reuse of `g4` requires

`u >= (p+5-2j)/4`.

Outside the middle inverse interval, an exact support-six pair is automatically forced into the support-three rank-two branch.

For `p=7,j=1`, the three support-four types split exactly as

- `a=1`: light only;
- `a=2`: middle, either side allowed;
- `a=3`: heavy only.

## 7. Exact multi-copy overlap criterion

Let `h=ceil(b/2)`. If V reuses `c` copies of the light value `e3`, then exact graded depth gives

`[u k]_p<=p-h` for every `k in [a,a+c]`.

If V reuses `c` copies of the heavy value `g4`, then

`[u k]_p<=p-h` for every `k in [a-c,a]`.

So the maximum reusable overlap is the forward/backward distance from `a` to the first top-block residue under multiplication by `u`.

For `p=7,j=1`, the exact maxima `(c_light,c_heavy)` are

- `a=1`: `(4,0)`;
- `a=2`: `(2,1)`;
- `a=3`: `(0,2)`.

The checker now uses complete oracle comparison only on a bounded prime set and cheap broad algebraic regression through p=401; the accidentally over-expensive first draft was corrected before being used as evidence.

## 8. Exact first-corridor support-six face sweep

`FIRST_CORRIDOR_SUPPORT6_FACE_SWEEP_V1.md` and its C++ verifier enumerate only the two equality branches from Section 3, using the exact depth oracle.

Frozen result:

- `p=5`: type `a=2` has 4 ordered support-three equality-face survivors; this is a genuine mutation/control boundary;
- for every support-four type at

`p in {7,11,13,17,19,23,29}`,

both the support-three and support-four equality branches have zero survivors.

Therefore the next theorem target is now sharply registered:

> **Target, not proved:** for every prime `p>=7`, in the first maximal corridor, a pair containing a support-four maximal atom has support at least seven.

No value for p>=31 is inferred from the finite sweep.

## 9. Current analytic bottleneck

The first-corridor support-three branch is a three-coefficient rank-two residue problem.

Write `p=2h+1`, `m=(3p-1)/2=3h+1`. If the companion multiplicities are `(c,r,t)` and the pair contributes at least

`d=(p+1)/2=h+1`

additional copies of the shared maximal-atom value, the empirical arithmetic statement is:

> extending the first multiplicity from `c` to `c+d` always exposes a nontrivial scalar relation of total length at most `m-1`, provided `c<=h-1`.

This has been checked as a discovery lemma on all primes through 97 but is **not yet proved** and is not committed as theorem authority.

A useful reduction of the hard case is obtained by writing

`alpha=p-r`, `beta=p-t`,

so

`alpha+beta=h+1+c`.

If `alpha,beta<=h`, scalar `q=2` already gives the required short relation.

If, say, `alpha>h`, write

`c=h-k`, `beta=r-k`.

Then the extended coefficient box becomes

`(p-k, r, p-r+k)`.

Simple inclusion-exclusion guarantees a nontrivial scalar relation fitting this box; the remaining proof gap is to force at least one such fitting scalar onto the short residue-sum level rather than the long level.

This is the current smallest atomic logic gap.

## 10. Literature gate

A fresh search found strong rank-two inverse theorems for maximal/extremal zero-sum regimes and for k-th Davenport inverse problems, but no theorem surfaced that directly classifies these intermediate-length three-support atoms at `(3p-1)/2`.

Accordingly, the half-extension lemma remains an active ORION proof target rather than being imported as donor structure.

## 11. Next discriminators

1. Prove the half-extension residue lemma above; this should eliminate the heavy-share support-three equality branch uniformly.
2. Derive the light-share analogue using the exact multi-copy modular interval and the one-point plane normal form.
3. Attack the middle-inverse support-four rank-three equality branch through simultaneous quotient atomicity and low-cardinality depth shells.
4. Once the first-corridor support-seven theorem is analytic, transplant the same depth machinery to later maximal corridors.
5. Keep the p=5 equality survivor as a mandatory mutation control for any claimed all-prime proof.
6. Continue the independent p=7 Type-A / higher-overshoot lanes only after the prime-uniform theorem machinery is preserved.

## Claim ceiling

- `D_3(C_7^3)` is not claimed solved here.
- The all-prime formula is not claimed proved or novel.
- The support-seven statement is a theorem target, with exact finite evidence only on the listed primes.
- Donor rank-two/projective results receive zero ORION novelty credit.
- Failed, resource-bounded, and small-prime counter-boundaries remain explicit rather than being smoothed over.
