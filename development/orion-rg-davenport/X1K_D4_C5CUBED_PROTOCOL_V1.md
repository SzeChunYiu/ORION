# ORION-RG X1-K — D4(C5^3) linear-regime gate and p=5 inductive lift

Issue: #981. Parent: #899. Coordinates: #896, #912, #915, #916, #980.

## Authority

`mathematical_proposal: true`

`mathematical_result_credit: false`

`proof_authority: false` except for already committed/donor inputs explicitly cited below.

`novelty_claim: false`

**Standing correction.** The lower bound `D_4(C_5^3)>=30` is donor-owned: Freeze--Schmid Theorem 4.1 gives, for odd prime p in the relevant specialization,

`D_k(C_p^3) >= p k + 5(p-1)/2`.

At `p=5,k=4` this is 30. The explicit 29-term witness below is therefore an independent reconstruction/control, not a new lower-bound theorem. Candidate p=5 upper/global bounds remain algebraic consequences to be audited before any novelty framing.

## K0 — frozen donor/ORION inputs

Use only:

- ORION exact `D_2(C_5^3)=20`;
- ORION exact `D_3(C_5^3)=25`;
- donor `D(C_5^3)=13` and `eta(C_5^3)=s_{<=5}=33`;
- donor Freeze--Schmid lower bound, giving `D_4(C_5^3)>=30`;
- ORION exact short-zero-sum thresholds `s_{<=6}=24`, `s_{<=8}=18`;
- Freeze--Schmid Prop. 3.1(3):
  `D_{k+1}(G) <= max{D_k(G)+l, s_{<=l}(G)-1}`;
- Freeze--Schmid/Grinsztajn specialized inductive inequality:
  `D(C_{pm}^3) <= D_{D(C_m^3)}(C_p^3)`;
- Grinsztajn 2026 incumbent bound `D(C_n^3) <= 4n-P(n)-2` only as a donor benchmark.

No exact published `D_4(C_5^3)` value was surfaced in the 2026-08-23 hostile search. `NOT_FOUND` is not proof of novelty.

## K1 — explicit donor-lower-bound reconstruction packet

Replay the length-29 sequence

`W_29 = e1^4 e2^4 e3^14 a^2 b^2 c^3`,

where `a=(1,1,0)`, `b=(1,0,1)`, `c=(0,1,1)` in `F_5^3`.

It extends the established 24-term D3 lower witness only by increasing `e3` multiplicity from 9 to 14.

Frozen rows:

| row | multiplicities `(e1,e2,e3,a,b,c)` | expected max disjoint zero-sums |
|---|---|---:|
| established D3 control | `(4,4,9,2,2,3)` | 2 |
| explicit length-29 reconstruction | `(4,4,14,2,2,3)` | 3 |
| anti-always-negative neighbour | `(4,4,15,2,2,3)` | 4 |

The verifier enumerates every nonzero count vector in the multiplicity box whose weighted sum is zero mod 5, computes the exact componentwise packing number recursively, and independently recomputes it through forward aggregate-use layers.

A successful middle-row replay reconstructs the donor lower bound on an explicit witness and validates the new instrument. It carries **no novelty credit**.

## K2 — exact current interval

Freeze--Schmid Prop. 3.1(3), with `k=3`, `l=5`, gives

`D_4 <= max(D_3+5, s_{<=5}-1) = max(30,32)=32`.

Together with the donor lower bound:

`30 <= D_4(C_5^3) <= 32`.

The open mathematical question is therefore exact `30/31/32`, not the lower endpoint.

## K3 — length-30 obstruction compression theorem

Assume `|M|=30` and M has no four pairwise-disjoint nonempty zero-sums.

### Step 1 — minimum zero-sum length is at least six

If `A|M` is a zero-sum with `|A|<=5`, then the complement has at least 25 elements. ORION's exact `D_3=25` gives three disjoint zero-sums there, contradicting the no-four assumption. Thus every zero-sum of M has length at least 6.

### Step 2 — first exact six-atom

`s_{<=6}=24`, so M contains a zero-sum of length at most 6. By Step 1 it has length exactly 6. Call it `A_6`.

### Step 3 — second exact six-atom

`M A_6^{-1}` has length 24, no three disjoint zero-sums, and still no zero-sum shorter than 6. Again `s_{<=6}=24`, so it contains an exact six-term zero-sum `B_6`.

### Step 4 — rank-three 18-term hard core

`R=M(A_6B_6)^{-1}` has length 18 and no two disjoint zero-sums. Rank at most two is donor-closed because `D_2(C_5^2)=14`; hence R has rank 3.

### Step 5 — bounded third atom and ZSF tail

`s_{<=8}=18`, while every zero-sum in R has length at least 6. Hence R contains a zero-sum `C_t` with `t in {6,7,8}`.

Set `Z=R C_t^{-1}`. If Z contained a nonempty zero-sum, then `A_6,B_6,C_t` plus that zero-sum would be four disjoint zero-sums. Therefore Z is zero-sum-free.

### Frozen compressed form

Every length-30 obstruction must admit

`M = A_6 * B_6 * C_t * Z`, `t in {6,7,8}`,

with:

- `A_6,B_6,C_t` zero-sums;
- `|Z|=18-t in {12,11,10}` and Z zero-sum-free;
- global minimum zero-sum length at least 6;
- `C_t*Z` a rank-three 18-term sequence with no two disjoint zero-sums.

This is the primary new structural target. It does not by itself determine D4.

## K4 — frozen upper-bound grammar

Do not launch an arbitrary length-30 multiset search first.

### Route A — core first

Enumerate/canonicalize only rank-three length-18 no-two-disjoint cores using the validated R2 machinery. For each core, enumerate `C_t*Z` decompositions with `t in {6,7,8}` and Z zero-sum-free, then test exact six-atom extensions `B_6` and `A_6` while preserving global min-ZS >=6 and no-four packing.

### Route B — tail first

Use existing maximal/near-maximal ZSF machinery to classify tails Z of length 12/11/10, then solve the bounded extension problem

`Z -> C_t -> B_6 -> A_6`.

### Route C — symbolic incompatibility

Seek an all-instance lemma showing that no allowed Z tail can coexist with three disjoint atoms under the global min-ZS>=6 condition. Route C outranks a larger finite atlas if a clean invariant emerges.

## K5 — obstruction-to-invariant rule

If a length-30 obstruction survives, do not jump immediately to length 31. Serialize the canonical core, t, Z orbit/signature, atom/subset-sum signature, exact reason every fourth zero-sum fails, and the smallest coordinate whose removal merges the obstruction with a closed case. That state becomes the successor theorem target under #980.

## K6 — local multiwise symbolic lift from exact D3

K2 and Prop. 3.1(3) imply

`D_k(C_5^3) <= 5k+12` for every `k>=4`.

Base: `D_4<=32=5*4+12`.

Induction:

`D_{k+1}<=max(D_k+5,32)<=5(k+1)+12`.

This is a derived bound. A dedicated prior-art search on the exact statement is required before novelty framing.

## K7 — p=5 global induction consequence

For `m>=2`, the standard lower bound gives `D(C_m^3)>=4`, so the classical inductive inequality and K6 give

`D(C_{5m}^3) <= 5D(C_m^3)+12`.

For prime-power q:

`D(C_q^3)=3q-2`, hence

`D(C_{5q}^3) <= 15q+2 = D*(C_{5q}^3)+4`.

If `n=5m` and the largest primary component `Q=P(n)` is inherited from m, applying Grinsztajn's incumbent bound to m yields

`D(C_n^3) <= 4n-5Q+2`,

an algebraic improvement of `4Q-4` over `4n-Q-2` on the declared subfamily.

These are candidate derived theorems pending full hypothesis/prior-art audit, not ORION novelty claims.

## K8 — leverage if exact D4=30

If the upper programme proves `D_4=30`, Prop. 3.1(3) gives

`D_k(C_5^3)<=5k+10` for every `k>=4`.

Indeed `D_5<=max(35,32)=35`, and ordinary +5 induction continues.

Consequently

`D(C_{5m}^3)<=5D(C_m^3)+10`,

and for prime-power q,

`D(C_{5q}^3)<=15q=D*+2`.

This is why exact D4 is a coefficient gate rather than an endpoint.

## K9 — relation to C45

For q=9:

- K7 gives generic `D(C_45^3)<=137`;
- exact D4=30 would give `<=135`;
- #912 remains the direct affine-missing-sum route needed to bridge to conjectural exact 133.

Target synthesis:

`p=5 multiwise compression -> small global deficit`

plus

`affine missing-sum / exchange geometry -> repair final deficit`.

Neither layer may claim the other.

## Reopen triggers

- the explicit witness fails replay, indicating an implementation/construction error (the donor lower theorem remains independent);
- exact D4 donor is found;
- any K3 threshold/rank-two input is wrong;
- the inductive inequality has an unmet K7 hypothesis;
- the P(n) inheritance condition is insufficient;
- a length-30 obstruction violates K3;
- a stronger donor p=5 local estimate absorbs K6/K7.

## Strong terminals

- `X1K_D4_C5CUBED_EXACT_30_PROVED`;
- `X1K_D4_C5CUBED_EXACT_31_OR_32_PROVED`;
- `X1K_LENGTH30_COMPRESSION_THEOREM_VALIDATED`;
- `X1K_LINEAR_REGIME_OBSTRUCTION_FOUND`;
- `X1K_P5_MULTIWISE_SHARPENING_DONOR_OWNED`;
- `X1K_P5_GLOBAL_BOUND_SURVIVES_PRIOR_ART_AUDIT`;
- `X1K_CANNOT_CHECK_RESOURCE_BOUND`;
- `X1K_CANNOT_CHECK`.

## Claim boundary

The lower bound 30 is donor mathematics. The explicit witness is a reconstruction/control. Finite search cannot promote itself to an all-k/global theorem. Exact D4 is valuable, but the high-impact target is the reusable local-to-global mechanism or the obstruction explaining why the predicted linear regime fails.