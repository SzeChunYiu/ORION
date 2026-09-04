# Fan critical short-free family and explicit four-pack — V1

Status: **donor construction + new-to-this-packet algebraic unpacking/certificate**. No priority claim.

This note records a prime-uniform phenomenon at the exact critical length for the conjectural lower-bound value of `D_3(C_p^3)`.

Let `p>=5` be an odd prime and let

\[
G=C_p^3=\langle e_1\rangle\oplus\langle e_2\rangle\oplus\langle e_3\rangle.
\]

Write

- `a=e1`, `b=e2`, `c=e3`,
- `d=e1+e2`, `e=e1+e3`, `f=e2+e3`,
- `g=e1+e2+e3`.

Let

\[
S_p=(abcdefg)^{p-1}.
\]

This is the rank-three sequence `S_3` used by Fan--Gao--Wang--Zhong--Zhuang, *On Short Zero-Sum Subsequences of Zero-Sum Sequences*, Electron. J. Combin. 19(3) (2012), P31. Their Lemma 3.2 proves that `S_p` is `p`-short-free, and their Lemma 3.5 / Proposition 3.1 constructs many zero-sum short-free divisors of it.

The total sum is

\[
\sigma(S_p)=-4g=(p-4)g.
\]

The critical length one above the Freeze--Schmid `k=3` lower bound is

\[
N_p:=\frac{11p-3}{2}.
\]

## Case `p == 3 (mod 4)`

Put

\[
t=\frac{p-7}{4}.
\]

Define the divisor `B_p|S_p` by multiplicities

\[
(a,b,c,d,e,f,g):
\quad
(p-2-t,\ p-2-t,\ p-2-t,\ p-1,\ p-1,\ p-1,\ 4+t).
\]

Equivalently this is the Fan Step-3 construction obtained from `S_p` by deleting

\[
g^{p-5-t}(abc)^t abc.
\]

The deleted sequence has sum `(p-4)g`, so `B_p` is zero-sum. Its length is

\[
|B_p|=N_p.
\]

Since `B_p|S_p`, it remains `p`-short-free.

Nevertheless it has the following explicit partition into four nonempty zero-sum blocks:

\[
Z_{12}=ab\,d^{p-1},\qquad
Z_{13}=ac\,e^{p-1},\qquad
Z_{23}=bc\,f^{p-1},
\]

and

\[
Z_0=a^{p-4-t}b^{p-4-t}c^{p-4-t}g^{4+t}.
\]

Indeed each `Z_ij` has coordinate sum `p(e_i+e_j)=0`, while each coordinate of `Z_0` has coefficient

\[
(p-4-t)+(4+t)=p.
\]

The four blocks are disjoint and their product is exactly `B_p`.

For `p=7`, this specializes to

\[
(a,b,c,d,e,f,g)=(5,5,5,6,6,6,4)
\]

with block lengths `(8,8,8,13)`. This is an explicit donor-controlled member of the support-7 universe eliminated computationally by the C7 packet.

## Case `p == 1 (mod 4)`

Put

\[
t=\frac{p-5}{4}.
\]

Define `B_p|S_p` by multiplicities

\[
(a,b,c,d,e,f,g):
\quad
(p-1-t,\ p-1-t,\ p-2-t,\ p-2,\ p-1,\ p-1,\ 4+t).
\]

Equivalently delete

\[
g^{p-5-t}(abc)^t dc.
\]

Again the deleted sequence has sum `(p-4)g`, so `B_p` is zero-sum, has length `N_p`, and is `p`-short-free as a divisor of `S_p`.

A four-pack is

\[
Z_{12}=a^2b^2d^{p-2},\qquad
Z_{13}=ac\,e^{p-1},\qquad
Z_{23}=bc\,f^{p-1},
\]

and the same

\[
Z_0=a^{p-4-t}b^{p-4-t}c^{p-4-t}g^{4+t}.
\]

The first block sums to `p(e1+e2)`, the next two to `p(e1+e3)` and `p(e2+e3)`, and `Z_0` is zero-sum coordinatewise. They again cover `B_p` exactly.

For `p=5` the block lengths are `(7,6,6,7)`.

## Consequence: the short-zero route is uniformly impossible

For rank three, Fan et al. define `alpha_3 == -4 (mod p)`, so for every prime `p>=5`, `alpha_3=p-4`. Their Proposition 3.1 places `C_0(C_p^3)` above the entire interval containing `N_p`; equivalently, zero-sum `p`-short-free sequences exist at the critical length `N_p`.

Thus a proof of

\[
D_3(C_p^3)=\frac{11p-5}{2}
\]

cannot proceed by proving that every critical zero-sum sequence has a short zero-sum. The model family above is a counterexample to that stronger assertion for every `p>=5`.

What the family demonstrates instead is the structurally correct target:

> critical zero-sum short-free sequences may exist, but they must still admit four disjoint nonempty zero-sum factors if the lower-bound formula for `D_3` is true.

This is exactly the phenomenon verified exhaustively for every support-7 critical sequence at `p=7`.

## Boundary

- Fan et al. own the short-free construction mechanism; this packet only specializes it to the critical multiwise length and writes down the four-factor certificates explicitly.
- The displayed family is **not** a counterexample to the desired `D_3` formula; it has a four-pack by construction.
- No statement is made here that every critical short-free sequence for general `p` has a four-pack.
