# CRITICAL CORRECTION — C15^3 is OPEN; C45 downstream chain is conditional

Parent programme: #896 / #899. This correction supersedes the erroneous donor-closure disposition of #900 and any downstream X1-C finding that used `D(C_15^3)=43` as an earned donor theorem.

## Error found by hostile audit

An earlier ORION-RG donor map incorrectly treated the theorem

`D(Z_3 ⊕ Z_3 ⊕ Z_(3d)) = 1+d*`

as if it implied the homocyclic value

`D(C_15^3)=43`.

That inference is false. In particular,

`C_15^3 = C_15 ⊕ C_15 ⊕ C_15`

is **not** isomorphic to

`C_3 ⊕ C_3 ⊕ C_45`.

Their orders already differ:

- `|C_15^3| = 15^3 = 3375`;
- `|C_3 ⊕ C_3 ⊕ C_45| = 3*3*45 = 405`.

Therefore the Bhowmik--Schlage-Puchta / Sheikh `Z_3⊕Z_3⊕Z_(3d)` theorem does not determine `D(C_15^3)`.

## Current 2026 donor state

The current Optimization Constants entry for `D(C_n^3)` explicitly records:

- the pointwise conjecture `D(C_n^3)=3(n-1)+1` for all n;
- **prime powers** as an unconditional exact family, because `C_n^3` is then a p-group;
- the general pointwise determination of `D(C_n^3)` as open;
- Grinsztajn's 2026 bound `D(C_n^3)<=4n-P(n)-2` as the current uniform upper-bound improvement.

No exact `D(C_15^3)` theorem was found in the renewed hostile search.

Thus the scientifically correct status is

`D(C_15^3) OPEN`,

with standard lower bound

`D(C_15^3) >= 3(15-1)+1 = 43`.

## Stronger exact inductive upper bound for n=15

The earlier one-block arithmetic remains valid, but it is now an **open-problem attack**, not a known-answer calibration.

Project

`C_15^3 -> C_3^3`

with kernel `C_5^3`.

Donor p-group theorem gives

`D(C_5^3)=13`.

Freeze--Schmid / Bhowmik--Schlage-Puchta give for k>=3

`D_k(C_3^3)=3k+6`.

The subgroup/quotient inductive inequality therefore yields

`D(C_15^3) <= D_13(C_3^3)=3*13+6=45`.

Hence the true live interval is

`43 <= D(C_15^3) <= 45`.

This is substantially sharper than the general Grinsztajn 2026 bound, which gives `D(C_15^3)<=53`.

## Live one-block deficit restored

At the conjectured contradiction threshold 43:

- `D_12(C_3^3)=42`;
- `D_13(C_3^3)=45`;
- every projected 43-term sequence has at least 12 disjoint quotient zero-sum blocks;
- ordinary induction needs 13 C5^3 block sums to invoke `D(C_5^3)=13`.

Thus C15 is exactly **one effective quotient block short**.

Unlike the downstream C45 version, the kernel is the p-group `C_5^3`, so the fresh Geroldinger--Yang sharp p-group `nu_5` theorem is directly available. This makes C15 a cleaner and more credible breakthrough target than C45.

## Effect on existing ORION-RG artifacts

### Reopened / restored

Issue #900 must be reopened. Its one-block-deficit mathematical setup is relevant, but its previous `donor-owned C15` disposition is invalid.

### Downstream C45 findings become conditional

Issue #901 and the following committed files used `D(C_15^3)=43` as an earned premise. They are **not deleted**; they remain historical/conditional derivations that may reactivate only if C15 is independently proved:

- `X1C_GREEDY_TRIPLE_DEFICIT_CASCADE_2026-08-22.md` insofar as it invokes `d(C15^3)=42`;
- `X1C_MAXIMAL_KERNEL_COMPLETION_2026-08-22.md`;
- `X1C_PRIMARY_PROJECTION_PACKING_CONSTRAINTS_2026-08-22.md`;
- `X1C_REVERSE_D7_ROUTE_REFUTED_2026-08-22.md` (its local D7 lower bound remains mathematically valid, but its role in C45 is downstream);
- `X1C_FORCED_KERNEL_FULL_ORDER_39_OF_42_2026-08-22.md`;
- `X1C_ORDER5_DEFECT_UNIQUE_C3_ORBIT_2026-08-22.md`;
- `X1C_NESTED_PRIMARY_EXTREMALITY_2026-08-22.md`;
- `X1C_DONOR_RANK2_KERNEL_BOUNDARY_2026-08-22.md` as methodological context;
- all other C45 artifacts that assume maximal length 42 in C15^3.

These files must not be cited as earned C45 evidence until a C15 theorem establishes the missing premise.

### Erroneous provenance sentence withdrawn

`X1C_DONOR_PROVENANCE_REPAIR_Z3Z3Z3D_2026-08-22.md` contains an erroneous sentence asserting a homocyclic C15 specialization. That sentence is explicitly withdrawn by this correction. The thesis/proof-quality provenance note about the `Z_3⊕Z_3⊕Z_(3d)` theorem remains valid for that donor theorem itself.

## New priority order

1. **C15 theorem-or-obstruction first:** prove `D(C_15^3)=43`, find a counterexample, or identify the missing structural invariant.
2. If C15 is proved, reactivate C45 using the conditional downstream reductions.
3. Lift any successful C15/C45 lemma toward the full `3^a5^b` family.

## Authority boundary

This correction intentionally removes previously assumed authority. It is not a negative result about the rank-3 conjecture. It strengthens the programme by restoring the first genuinely open homocyclic two-prime target.
