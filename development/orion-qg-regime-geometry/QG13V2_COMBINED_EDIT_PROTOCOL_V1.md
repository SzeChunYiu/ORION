# QG-13 V2 — combined-deletion theorem mining for R6I support-five tightness

Issue: SzeChunYiu/ORION#777
Frozen base: `3202e52371d018b5f6547ed44490f089400d8485`
Branch: `shadow/orion-qg-qg13-v2-r6i-combined-edits`
Status: FROZEN BEFORE REPOSITORY/HARNESS OUTCOME.

## Question

Can a prospectively frozen two-column edit grammar close the gap between the machine-checked R6I support<=5 theorem and a stronger support<=4 normal form?

This packet does not import QG-1 or QG-13 V1 answers during synthesis.

## Edit grammar E2

For two distinct local columns in one R6I block, each column receives one of:

- A: zero generator R0; recompute dependent R2=R0*R1.
- B: zero generator R1; recompute dependent R2.
- AB: zero both independent generators; R2 becomes identity.
- KEEP.

A candidate combined move must use two non-KEEP actions, delete at least two generator letters total, preserve the inferred five-coordinate block syndrome under XOR, leave Tag/targets/permutation/central choices unchanged, and keep the global block anticommutation condition.

No Tag repair and no new coordinate is allowed in V2.

## Complete local resource domain

The analyzer sweeps every `(r0,r1,s0,s1,p0,p1,p2,central) in {I,X,Y,Z}^7 x {0,1,2}` for every applicable A/B/AB action. The exact local R6I cost is

`sum_k m_k wt(R_k) + sum_k wt(P_k R_k)`

with one central multiplier 2 and the other multipliers 4; the global -10 constant is unchanged and omitted. Tag cost is unchanged.

For every `(action, inferred_syndrome_change)` the analyzer records the exact minimum/maximum cost delta and a maximizing witness. For a two-column syndrome-cancelling action pair, the exact worst possible delta is the sum of the two single-column maxima because R6I has no cross-column Restore factor.

The miner may use only action pairs whose worst possible combined delta <=0. Positive-cost syndrome-cancelling pairs remain explicit boundary counterexamples and are not silently accepted.

## Frozen global obstruction census

The V2 structural census uses exactly five columns, the minimal size relevant to QG-9 support-five tightness.

A local structural type is the quotient of `(r0,r1,s0,s1)` retaining: five-bit block syndrome contribution; support activity of R0/R1; coincidence flag `r0=r1!=I`; QG-1-style N0/N1 F2^3 classes and C F2^2 class; and applicable E2 actions with their inferred syndrome changes.

All realizable local tuples are quotiented by that exact record. Then enumerate all multisets of five structural types in canonical combination-with-replacement order.

Keep a pattern iff:
1. its total five-bit syndrome is an accepting R6I block syndrome: anticommutation parity 1; both Tag labels nonzero/distinct;
2. it is irreducible under the already-certified QG-1 SOLO/PAIR conditions: no nonempty zero-sum subset in N0, N1, or C;
3. at least one independent generator has support exactly five.

A pattern is E2-covered iff two distinct columns admit a globally safe syndrome-cancelling E2 action pair that strictly lowers `(max_generator_support,total_generator_support)` lexicographically.

## Honest outcomes

- `QG13V2_SUPPORT4_CANDIDATE`: every frozen support-five irreducible pattern is E2-covered. This is only a theorem candidate; all-n theorem authority remains false.
- `QG13V2_MINIMAL_COMBINED_EDIT_OBSTRUCTION`: serialize the first canonical support-five irreducible pattern not covered by any globally safe E2 move.
- `QG13V2_RESOURCE_COUNTEREXAMPLE`: no globally safe E2 pair exists at all.
- `QG13V2_SEMANTIC_QUOTIENT_INCOMPLETE`: production transition binding fails.
- `QG13V2_CANNOT_CHECK`.

Finite obstruction coverage can never by itself authorize the all-n support<=4 theorem. Any candidate must open a new theorem packet under QG-9.

## Anti-leakage

- No QG-1/QG-13 V1 result file is read by analyzer or generic verifier.
- No chemistry or protected subject source.
- No network access.
- No post-outcome grammar widening.
- Parent comparisons, if later performed, occur only after the candidate or obstruction packet is digest-sealed.

## Authority

`new_theorem_authority=false`
`novelty_authority=false`
`physical_quantum_advantage_claim=false`
