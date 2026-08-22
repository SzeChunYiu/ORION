# QG-20 SixLCU P0 objective-scope census — protocol V1

**Frozen after Q3-R2 instruments and before QG20 execution.**  
Scientific parent: QG12 all-instance P0 theorem under the equal-weight `SELECT+PREP+WIDTH` objective.  
Authority target: complete finite-domain reweighted result only; no all-n weighted theorem unless separately proved.

## Frozen objective

`O20 = 2*SELECT + PREP + WIDTH`.

The admitted family is unchanged: the same 203 set partitions, factor choices, and shared/dedicated index encoding. Positive WIDTH weight preserves shared-width dominance; factorization changes SELECT only and remains non-increasing relative to the unfactored member for a fixed partition.

The unary incumbent remains cheaper than the binary incumbent for every admitted nonzero instance:

- `C_U = 4W + 15`;
- `C_B = 8W + 14`;
- `W >= 1`, hence `C_U < C_B`.

## Frozen domain

- complete ordered `n=1` SixLCU domain: `3^6 = 729` instances;
- complete reorder-quotiented `n=2` multiset domain: `C(20,6) = 38,760` instances.

Total: 39,489 instances.

## Frozen test

For every instance:

1. compute the original QG12 predicate `P0` unchanged;
2. compute exact O20 family optimum over all 203 partitions with factorization enabled and shared width;
3. compute the O20 unary incumbent;
4. label `incumbent_exact_O20 := (C_F_O20 == C_U_O20)`;
5. compare `P0` with `incumbent_exact_O20`.

## Outcome space

- `P0_REWEIGHTED_BOUNDARY_REFUTED`: at least one mismatch;
- `P0_ZERO_MISMATCH_ON_COMPLETE_N1_N2`: no mismatch on the complete frozen domain;
- `REFEREE_OR_EXECUTION_INVALID`.

Zero mismatch is exhaustive for the frozen n=1/n=2 domain but is not an all-n theorem.

## Required receipt

- objective weights;
- n1/n2 counts;
- mismatch counts by direction (`P0 true / label false`, `P0 false / label true`);
- first 50 mismatches serialized with costs/features;
- deterministic enumeration digest;
- direct-member cross-check on a deterministic sample using `member_components` rather than the fast aggregate formula;
- no-Q3-import gate.

## Replay

Run the analyzer twice from the same commit. Canonical result JSON excluding runtime must be byte-identical.