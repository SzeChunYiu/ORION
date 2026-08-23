# ORION-RG X1-K — D4(C5^3) linear-regime gate and p=5 inductive lift

Issue: #981. Parent: #899. Coordinates: #896, #912, #915, #916, #980.

## Authority

`mathematical_proposal: true`

`mathematical_result_credit: false`

`proof_authority: false` except for already committed/donor inputs explicitly cited below.

`novelty_claim: false`

The explicit 29-term lower witness in K1 is **provisional until independent repository replay**. Candidate p=5 global bounds are algebraic consequences to be audited, not publication claims.

## K0 — frozen donor/ORION inputs

Use only:

- ORION exact `D_2(C_5^3)=20`;
- ORION exact `D_3(C_5^3)=25`;
- donor `D(C_5^3)=13` and `eta(C_5^3)=s_{<=5}=33`;
- ORION exact short-zero-sum thresholds `s_{<=6}=24`, `s_{<=8}=18`;
- Freeze--Schmid Prop. 3.1(3):
  `D_{k+1}(G) <= max{D_k(G)+l, s_{<=l}(G)-1}`;
- Freeze--Schmid/Grinsztajn specialized inductive inequality:
  `D(C_{pm}^3) <= D_{D(C_m^3)}(C_p^3)`;
- Grinsztajn 2026 incumbent bound `D(C_n^3) <= 4n-P(n)-2` only as a donor benchmark.

No exact `D_4(C_5^3)` donor was found in the 2026-08-23 hostile search. `NOT_FOUND` is not proof of novelty.

## K1 — lower-bound witness packet

Candidate sequence of length 29:

`W_29 = e1^4 e2^4 e3^14 a^2 b^2 c^3`,

where

- `a=(1,1,0)`;
- `b=(1,0,1)`;
- `c=(0,1,1)`;
- all coordinates are in `F_5^3`.

It extends the established 24-term `D_3` lower witness only by increasing `e3` multiplicity from 9 to 14.

Frozen replay rows:

| row | multiplicities `(e1,e2,e3,a,b,c)` | expected max disjoint zero-sums |
|---|---|---:|
| established D3 control | `(4,4,9,2,2,3)` | 2 |
| proposed D4 lower witness | `(4,4,14,2,2,3)` | 3 |
| anti-always-negative neighbour | `(4,4,15,2,2,3)` | 4 |

The verifier must enumerate **all** nonzero count vectors within the multiplicity box whose weighted coordinate sum is zero mod 5, then solve the exact componentwise packing number. A second traversal must independently confirm the packing number from forward reachable aggregate-use layers.

If the middle row replays at 3, it proves `D_4(C_5^3)>=30`.

## K2 — immediate upper bound

Freeze--Schmid with `k=3`, `l=5` gives

`D_4 <= max(D_3+5, s_{<=5}-1) = max(30,32)=32`.

Thus after K1 replay:

`30 <= D_4(C_5^3) <= 32`.

No wider search is authorized before using the structural reduction below.

## K3 — length-30 obstruction compression theorem

Assume `|M|=30` and `M` has no four pairwise-disjoint nonempty zero-sums.

### Step 1 — global minimum zero-sum length

If `A|M` is a zero-sum with `|A|<=5`, then `|M A^{-1}|>=25=D_3`; the complement contains three disjoint zero-sums, giving four with A. Contradiction.

Therefore every zero-sum of M has length at least 6.

### Step 2 — first exact six-atom

`s_{<=6}=24 <=30`, so M contains a zero-sum of length at most 6. By Step 1 its length is exactly 6. Call it `A_6`.

### Step 3 — second exact six-atom

The complement `M A_6^{-1}` has length 24, no three disjoint zero-sums, and inherits minimum zero-sum length at least 6. Since `s_{<=6}=24`, it contains another exact 6-term zero-sum `B_6`.

### Step 4 — 18-term hard core

`R=M(A_6B_6)^{-1}` has length 18 and no two disjoint zero-sums. Rank <=2 is donor-closed: rank two has `D_2(C_5^2)=14`, so length 18 already forces two disjoint zero-sums. Hence R has rank 3.

### Step 5 — third bounded atom and ZSF tail

`s_{<=8}=18`, while the global minimum zero-sum length is at least 6. Therefore R contains a zero-sum `C_t` with `t in {6,7,8}`.

Let `Z=R C_t^{-1}`. If Z contained a nonempty zero-sum, then `A_6`, `B_6`, `C_t`, and that zero-sum would be four disjoint zero-sums. Hence Z is zero-sum-free.

### Frozen compressed form

Every length-30 obstruction must admit

`M = A_6 * B_6 * C_t * Z`, `t in {6,7,8}`,

with:

- `A_6,B_6,C_t` zero-sums;
- `|Z|=18-t in {12,11,10}` and Z zero-sum-free;
- global minimum zero-sum length >=6;
- `C_t*Z` a rank-3 18-term sequence with no two disjoint zero-sums.

This is a symbolic structural reduction. It does not by itself prove `D_4=30`.

## K4 — frozen upper-bound search grammar

### Route A — core-first

Enumerate/canonicalize only rank-3 length-18 no-two-disjoint cores using the already validated R2 state machinery. For each core:

1. identify all `C_t * Z` decompositions, `t in {6,7,8}`, with Z zero-sum-free;
2. attach exact six-atoms `B_6`, then `A_6`;
3. reject as soon as global minimum zero-sum <6 or four disjoint zero-sums appear;
4. preserve the first surviving obstruction exactly.

### Route B — tail-first

Use existing maximal/near-maximal ZSF `C_5^3` census machinery to classify possible Z tails of length 12/11/10, then solve the bounded extension problem `Z -> C_t -> B_6 -> A_6`.

### Route C — symbolic incompatibility

Search for an all-instance lemma proving that no zero-sum-free tail of the allowed size can coexist with the three disjoint atoms under the global min-ZS>=6 condition.

Route C has priority over a full extension atlas if a clean invariant emerges.

## K5 — obstruction-to-invariant rule

If a length-30 obstruction survives, do not jump immediately to length 31. Serialize:

- canonical core;
- `t`;
- Z tail orbit/signature;
- atom-intersection/subset-sum signature;
- exact reason all candidate fourth zero-sums fail;
- smallest coordinate whose removal makes the obstruction indistinguishable from a closed case.

That state becomes the next theorem candidate under #980.

## K6 — local multiwise symbolic lift already available from D3

From K2 and Prop. 3.1(3):

`D_k(C_5^3) <= 5k+12` for all `k>=4`.

Proof skeleton:

- base k=4: `D_4<=32=5*4+12`;
- if `D_k<=5k+12`, then
  `D_{k+1}<=max(D_k+5,32)<=max(5(k+1)+12,32)=5(k+1)+12`.

This statement must receive a primary-source prior-art audit before novelty framing.

## K7 — p=5 global induction consequence

For `m>=2`, the standard lower bound gives `D(C_m^3)>=4`, so K6 applies at `k=D(C_m^3)`:

`D(C_{5m}^3) <= D_{D(C_m^3)}(C_5^3) <= 5D(C_m^3)+12`.

For prime-power `q`:

`D(C_q^3)=3q-2`, hence

`D(C_{5q}^3) <= 15q+2 = D*(C_{5q}^3)+4`.

If `n=5m` and the largest primary component `Q=P(n)` is inherited from m, Grinsztajn on m gives

`D(C_n^3) <= 5(4m-Q-2)+12 = 4n-5Q+2`.

Compared with `4n-Q-2`, the improvement is `4Q-4` on this declared subfamily.

These are **derived bounds pending donor/novelty audit**, not ORION credit claims.

## K8 — leverage if D4=30

If K4 proves `D_4=30`, Prop. 3.1(3) gives for all `k>=4`

`D_k(C_5^3)<=5k+10`,

because the base is 30 and the threshold term 32 is dominated from k=4 onward by the next step.

Then

`D(C_{5m}^3)<=5D(C_m^3)+10`.

For prime-power q:

`D(C_{5q}^3)<=15q=D*+2`.

This is why exact D4 is a structural coefficient gate rather than an endpoint.

## K9 — relation to C45

For q=9:

- K7 yields generic `D(C_45^3)<=137`;
- D4=30 would yield `<=135`;
- #912 remains the direct affine-missing-sum route needed to bridge to the conjectural exact 133.

The intended synthesis is:

`p=5 multiwise compression -> small global deficit`

plus

`affine missing-sum / exchange geometry -> repair final deficit`.

Neither layer may claim the other.

## Reopen triggers

- lower witness fails independent replay;
- exact D4 donor is found;
- any step in K3 uses an incorrect threshold/rank-two constant;
- the standard inductive inequality has an unmet hypothesis in K7;
- the claimed `P(n)` inheritance condition is insufficient;
- a length-30 obstruction violates the frozen compressed form;
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

Finite search cannot promote itself to an all-k/global theorem. Exact D4 is valuable but the high-impact target is the reusable local-to-global mechanism or the obstruction that explains why the predicted linear regime fails.