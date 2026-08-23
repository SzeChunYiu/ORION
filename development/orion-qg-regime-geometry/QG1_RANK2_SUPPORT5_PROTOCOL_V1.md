# QG-1 rank-2 all-n support-five theorem protocol V1

Date: 2026-08-21
Parent: ORION #740
Child: ORION #747
Base revision: `e6011bbeae68d91b5cce45ffa34e67306905844d`
Status: **FROZEN BEFORE OFFICIAL MACHINE-CHECK OUTCOME**.

Exploratory scratch work suggested the theorem below. This packet freezes the exact statement, complete finite validation domains, falsifiers and claim boundary before the repository checker is executed under either harness.

## Theorem candidate

In the frozen R6I two-block rank-2 dependent TARE-3 shared-Tag grammar under the raw structural support-count objective, every feasible global configuration can be transformed without increasing system size or changing target data so that each block's generator-union support is at most five; if a block has union support >=6 the transformation is strictly cost-decreasing. Therefore every global optimum has a representative with per-block generator-union support <=5, for every qubit count n.

For one block write independent generators `R0,R1`, dependent third `R2=R0 R1`, shared Tag pair `S0,S1`, and active support `A={q:(R0q,R1q)!=(I,I)}`.

For each q in A define

`v(q)=(<R0q,R1q>,<S0q,R0q>,<S1q,R0q>,<S0q,R1q>,<S1q,R1q>) in F_2^5`.

If `|A|>=6`, linear dependence gives nonempty `Q subset A` with XOR of v(q) equal zero. Set both generator letters to identity on Q; then the dependent third is identity there too. The five zero parities preserve global anticommutation and all four independent Tag-syndrome coordinates. The unchanged other block therefore retains the shared labels. Since global `<R0,R1>=1`, Q cannot equal A, and preserved anticommutation guarantees the edited generators remain nonzero and rank 2.

## Frozen local cost lemma

Local Pauli codes are `0=I,1=X,2=Y,3=Z`, multiplication modulo phase is production R6I `local_mul`, symplectic product is production `local_symp`, and local support is production `local_wt`.

Complete local domain:

- all `a,b in {0,1,2,3}` except `(0,0)`;
- all three target letters `p0,p1,p2`;
- all Tag letters `s0,s1`;
- all central choices `c in {0,1,2}` with branch multipliers `(4,4,4)` except multiplier 2 on c.

Old dependent letter is `r2=a*b`. Old local cost is

`m0*w(a)+m1*w(b)+m2*w(r2)+w(p0*a)+w(p1*b)+w(p2*r2)`.

After deleting both generators locally, frame letters are all I and new local cost is

`w(p0)+w(p1)+w(p2)`.

The checker must enumerate all `3*15*4^5 = 46,080` cases, serialize every case with delta > -4 verbatim, and report the exact maximum delta. Required theorem gate: zero violations and `max_delta <= -4`.

Tag cost is unchanged by the exchange and therefore absent from the local delta.

## Frozen constraint truth table

For every active `(a,b,s0,s1)` combination (15*16=240), independently verify:

- first class bit equals the change in the block anticommutation parity after local deletion;
- the remaining four bits equal the changes in the four Tag syndrome coordinates;
- `symp(s,a*b) == symp(s,a) XOR symp(s,b)` for both Tag letters, so preserving the four generator syndromes also preserves the dependent-third label;
- the production local multiplication/symplectic/weight tables equal the independently specified Pauli truth tables.

## F_2^5 lemma and bound sharpness for this exchange

The checker must enumerate all realizable five-bit classes and their rank.

Abstract zero-sum verification:

- zero vector gives a one-element zero-sum subset;
- any repeated nonzero vector gives a two-element zero-sum subset;
- enumerate every six-element subset of the 31 nonzero vectors in F_2^5 and verify GF(2) rank < 6.

This covers every six-vector multiset.

Boundary witness: the checker must find an explicit set of five **realizable** local classes that has rank 5 and whose XOR is a valid accepting global class (first bit 1; the two Tag labels are distinct nonzero). This proves the dimension/zero-sum argument itself cannot lower the universal bound below five.

## Global proof audit

The independent verifier must reconstruct these implications without trusting a theorem PASS flag:

1. zero class XOR preserves `<R0,R1>` and all four Tag syndrome bits;
2. unchanged Tag pair + unchanged syndromes preserves shared Tag labels against the untouched other block;
3. preserved `<R0,R1>=1` implies both generators remain nonzero, independent and rank 2;
4. `R2'=R0'R1'` preserves the dependent-triple grammar;
5. each deleted active qubit lowers cost by at least four, so every nonempty Q is a strict descent;
6. the full active support cannot be Q because its first-coordinate XOR is one;
7. repeated descent terminates with support <=5;
8. apply independently to both blocks.

## No-subject rule

The proof and both harness validations may read **no chemistry source and no R6I subject coefficients**. They may import production local algebra/code identities only. Existing chemistry receipts are post-theorem corroboration and play no role in proof authority.

## Dual harness

Lane A, generic ORION research harness:
- run the theorem checker as a local PYTHON capability;
- run a separately implemented reconstruction over the serialized theorem artifact;
- both outputs must be digest-bound and agree.

Lane B, native ORION-Q campaign:
- consume only the theorem artifact + generic reconstruction artifact;
- independently re-hash the freeze and theorem artifacts;
- select `ACCEPT_THEOREM / REJECT / CANNOT_CHECK` with no scientific/novelty authority.

## Positive terminal

`QG1_RANK2_ALL_N_SUPPORT5_SUFFICIENCY_MACHINE_VERIFIED`

Requires all frozen local/constraint/F2^5/global proof gates plus both harnesses agreeing on ACCEPT, no chemistry access, and novelty authority false.

## Claim boundary

The theorem covers only the frozen R6I structural grammar/objective. It does not prove weight-one all-n sufficiency, coefficient-weighted optimality, a physical quantum advantage, or novelty over external literature.
