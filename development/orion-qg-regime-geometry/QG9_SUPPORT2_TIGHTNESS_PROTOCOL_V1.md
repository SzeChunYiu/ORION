# QG-9 V5 — support-2 tightness exact-referee protocol

Date frozen: 2026-08-21. Issue: #795. Parent: #762.
Frozen parent commit: `a80dbd57d9124f058de7465a13de8c69416c368b`, carrying the protected all-n R6I support<=2 theorem receipt.
Authority ceiling: tightness of this frozen R6I support bound only; no novelty, R6, physical-advantage, or support<=1 authority.

## Question

Does any actual `n=2` target instance satisfy

`C_cap2 = C_unrestricted < C_cap1`?

At n=2, cap 2 is the unrestricted frame-pair space. A strict gap proves support 2 is necessary for that instance; combined with the parent support<=2 theorem, the all-n bound is tight.

## Candidate source — frozen before cap outcomes

Reconstruct the V4 full-acceptance support-2 boundary. Use only action-profile cases that are:
- fully accepted R6I single-block states;
- unsafe under the V3 support-nonincreasing relabel+delete grammar.

For each such type case enumerate all concrete two-qubit local-state realizations. Build exact block objects `(R0,R1,S0,S1)` and deduplicate. Every block must satisfy `<R0,R1>=1` and ordered labels `(c0,c1)` both nonzero/distinct.

Group blocks by exact shared Tag pair `(S0,S1)` and ordered labels `(c0,c1)`. Candidate block pairs are frozen in this order:
1. all self-pairs, block lexicographic;
2. all unordered distinct block pairs within a common Tag/label group, group then block lexicographic.

## Frozen target-template ladder

For each block pair define its frame triples `(R0,R1,R0R1)`.

Search template families in this order; a family is exhausted before the next opens:

1. `IDENTITY_RESTORE`: A/B target triples equal their generating frame triples.
2. `ONE_DEFECT_A`: multiply one A target branch by one single-qubit nonidentity Pauli, ordered branch 0..2, qubit 0..1, letter X,Y,Z.
3. `ONE_DEFECT_B`: same on B.
4. `MATCHED_DEFECT`: apply the same branch/qubit/letter defect to both blocks.

Skip templates creating an identity target branch. Selection is the first strict cap gap in the frozen order. No target-template widening after outcome.

## Exact capped referee

Primary search referee: canonical QG-1 `PairTables(2).capped_costs(targets_a, targets_b, caps=(1,2))`.

It globally enumerates anticommuting rank-2 frame pairs and exact minimum two-Pauli shared-Tag cost. Cap 1 filters both independent generators in each block to support <=1; cap 2 is the full n=2 pair space.

On the selected strict candidate only:
- run production R6I `shared_tag_exact`;
- require production `C_shared == C_cap2`;
- require all production witness checks true;
- record the support of all four independent production-witness generators.

## Independent verification

Generic ORION verifier reimplements the n=2 Pauli algebra and exact global pair/tag brute independently of QG-1/R6I for the selected witness, and must reproduce `C_cap1`, `C_cap2`, and the strict gap.

Native ORION-Q verifier binds:
- protected parent support<=2 receipt;
- production R6I exact witness;
- cap-2 equals unrestricted;
- strict cap-1 separation.

## Honest terminals

- `QG9_SUPPORT2_TIGHT_WITNESS_MACHINE_VERIFIED`
- `QG9_NO_SUPPORT2_TIGHT_WITNESS_IN_FROZEN_INVERSE_PANEL`
- `QG9_CAP_REFEREE_DISAGREEMENT`
- `QG9_CANDIDATE_GENERATOR_BINDING_GAP`
- `QG9_GENERIC_NATIVE_DISAGREEMENT`
- `QG9_CANNOT_CHECK`

A negative panel result is not a support<=1 theorem.
