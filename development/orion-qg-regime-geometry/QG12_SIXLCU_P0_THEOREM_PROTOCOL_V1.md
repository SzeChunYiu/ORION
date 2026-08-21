# ORION-QG QG-12 — SixLCU all-instance P0 boundary theorem protocol V1

Date: 2026-08-21
Parent: #740
Issue: #765
Base: `318d1cbbec451170448bb8e126c7ab50801930ce`
Status: **FROZEN BEFORE QG-12 MACHINE OUTCOME**.
Authority: theorem research only; no novelty/paper/merge/physical-advantage authority.

## Scientific question

QG-4 found `EXACT_PREDICATE_FOUND_P0` on exhaustive n=2 + held-outs even though Stage 3 found `NO_STRICT_SUBEXTENSION_CLOSES`. QG-12 asks whether P0 is not merely an empirical classifier but an **all-instance theorem** for the frozen six-term SixLCU family.

Target label:

`incumbent_exact := [C_F == C_U]`

(the binary incumbent is always worse under the frozen objective).

P0:

1. every pair gain `g2(i,j) <= 0`;
2. every two-disjoint-pair aggregate `g2(a)+g2(b)+1 <= 0`;
3. every perfect three-pair aggregate `g2(a)+g2(b)+g2(c)+2 <= 0`.

## Exact production gain decomposition

For any partition with k>=2, factoring enabled and shared ancilla (QG-4 proved these choices dominate), each block g of size m contributes

`T_m(g) = A_m * wF(g) - b_m * sw(g)`

with

- m=1: `b=0, A=0`;
- m=2: `b=1, A=4`;
- m=3: `b=2, A=10`;
- m=4: `b=2, A=14`;
- m=5: `b=3, A=23`.

The partition gain over unary is

`G(partition) = sum_g T_|g|(g) + c_shape`,

where the production PREP+WIDTH formula gives the 11 integer-partition shapes:

```text
1+1+1+1+1+1: c=0
2+1+1+1+1:   c=0
2+2+1+1:     c=+1
2+2+2:       c=+2
3+1+1+1:     c=-1
3+2+1:       c=0
3+3:         c=0
4+1+1:       c=-1
4+2:         c=0
5+1:         c=-3
6:            special single-block formula g6=23*wF-2*W+1
```

The analyzer must derive, not hard-code, `A_m,b_m,c_shape` from the frozen production `partition_static/member_components` formula and compare against this registered table.

## P0 -> every partition nonprofitable

Frozen proof obligations:

### B2 — pair block
`T_2(i,j) = g2(i,j) <= 0` by P0.

### B3 — triple block
For a triple g, sum its three pair inequalities:

`sum_pairs g2 = 4*sum_pairs sh - 2*sw <= 0`.

Every common-factor column of g is shared by all three pairs, so `sum_pairs sh >= 3*wF`. Hence

`sw >= 2*sum sh >= 6*wF`

and

`T_3 = 10*wF - 2*sw <= -2*wF <= 0`.

### B4 — quad block
Take any perfect matching of the four terms. Pair nonpositivity gives

`sw >= 4*(sh_1+sh_2) >= 8*wF`.

Therefore

`T_4 = 14*wF - 2*sw <= -2*wF <= 0`.

### B5 — quint block
Take a 5-cycle through the five terms. Summing the five pair inequalities counts every term weight twice:

`4*sum_cycle sh - 2*sw <= 0`.

Every common-factor column belongs to all five cycle pairs, so

`sw >= 2*sum sh >= 10*wF`,

hence

`T_5 = 23*wF - 3*sw <= -7*wF <= 0`.

### B6 — single block of six
Take any perfect matching of three pairs. P0's three-pair clause gives

`sum_matching g2 + 2 <= 0`, i.e.

`W >= 4*sum_matching sh + 2 >= 12*wF + 2`.

Thus

`g6 = 23*wF - 2*W + 1 <= -wF - 3 < 0`.

## Shape closure

Using B2-B5:
- shapes with no positive c are immediately nonpositive;
- `2+2+1+1`: gain is exactly two disjoint pair gains +1, P0 clause 2;
- `2+2+2`: gain is exactly three matching pair gains +2, P0 clause 3;
- negative constants only strengthen closure.

Therefore **P0 implies `C_F=C_U` for every admitted instance and every n**.

## Converse

If any P0 clause fails, its corresponding partition is an explicit strict witness:
- pair clause -> shape `2+1+1+1+1`;
- two-pair clause -> shape `2+2+1+1`;
- three-pair clause -> shape `2+2+2`.

Therefore `not P0 -> C_F<C_U`.

Combined theorem:

`C_F == C_U  iff  P0`.

## Production/machine binding

The checker must:
1. import the frozen QG-4 production module read-only;
2. verify 203 partitions and exact `partition_static` constants;
3. group all partitions by the 11 integer shapes and show their symbolic coefficients depend only on shape/block masks as registered;
4. derive the block coefficients from production `flag/bbits/PREP/WIDTH`, not literal registered constants;
5. mechanically verify every proof inequality as coefficient algebra plus the relations `sh(pair)>=wF(block)`;
6. bind QG-4 receipt authority, P0 selected definition, zero errors, and Stage-3 `NO_STRICT_SUBEXTENSION_CLOSES`;
7. independently test theorem equivalence on the complete n=1 and n=2 QG-4 domains without using the QG-4 stored labels as inputs;
8. serialize any mismatch as a theorem refutation.

## Certificate-arity claim boundary

If theorem passes, QG-12 may claim:
- SixLCU incumbent exactness has an all-instance boundary certificate generated entirely from pair gains plus disjoint-packing bonuses;
- global optimizer witness complexity remains high (`NO_STRICT_SUBEXTENSION_CLOSES` on verified domains), so recognition complexity and optimization-family complexity are separated.

It may NOT yet claim a universal `a_cert=2` across compiler families. Interaction arity (pair-derived gains) and support arity (up to six terms across a perfect matching) remain distinct.

## Independent generic verifier

Must reconstruct the shape constants and block upper bounds from the production formulas independently, then blind-check complete n1/n2 instances. It must not trust the analyzer terminal.

## Native ORION-Q controller

May accept `ALL_INSTANCE_P0_THEOREM`, reject, or CANNOT_CHECK. It keeps SixLCU theorem scope separate from any TARE/other-family transfer.

## Positive terminal

`QG12_SIXLCU_P0_ALL_INSTANCE_THEOREM_MACHINE_CHECKED`

## Honest alternatives

- `QG12_P0_GLOBAL_COUNTEREXAMPLE_FOUND`
- `QG12_PRODUCTION_GAIN_DECOMPOSITION_REFUTED`
- `QG12_NATIVE_GENERIC_DISAGREEMENT`
- `QG12_CANNOT_CHECK`

## Novelty boundary

Helly/Carathéodory/forbidden-substructure/CSP/local-certificate mathematics and quantum LCU compilation are prior art. Candidate contribution is only this compiler-specific exact separation between global optimization family complexity and pair-derived regime-boundary certificate structure. External novelty review remains required.
