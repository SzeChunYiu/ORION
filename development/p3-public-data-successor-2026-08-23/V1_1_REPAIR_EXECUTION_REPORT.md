# P3 public-data successor V1.1 repair execution

**Date:** 2026-08-23  
**Identity:** `P3.PUBLIC.TRANSPORT.CRAFT_SCIREX_OAEI.V1.1`  
**Authority:** adapter repair and input-only execution; no scientific outcome

## Preserved adverse identity

The original audit terminal remains immutable:

`ADVERSARIAL_AUDIT_FAIL__OAEI_INPUT_INDEX_REPLAY_ONLY__NO_END_TO_END_PUBLIC_RESULT`

V1.1 is a new pre-outcome repair iteration. It does not retroactively turn V1
into a pass, and it has not accessed public reference content or produced a P3
candidate result.

## Repairs implemented

1. **Four-terminal loss:** `GLUE`, `OBSTRUCTION`, `PLURAL`, and `UNRESOLVED`
   now have explicit action-by-state costs. `PLURAL` is no longer the default
   obstruction branch. The robust floor optimizes over all four actions.
2. **Leakage:** outcome-bearing keys are rejected recursively and inventory,
   case, prediction and rights records use closed contracts.
3. **Prediction integrity:** scoring requires sealed cases; validates relation
   and digest; rejects duplicate or incomplete `(system_id, case_id)` coverage;
   and refuses prediction-supplied source, panel or cluster identities.
4. **Gold authority:** public gold must match the sealed case's source, panel,
   cluster and input digest and must contain a nonempty identified set.
5. **Opportunity gates:** every coordinate named by a sealed case must be
   present on every evaluator row, have a decided status and have a nonzero
   source-level total. Zero, absent or `CANNOT_CHECK` stops scoring.
6. **Rights:** CRAFT and SciREX bodies require a human-owned rights-decision
   record. Legacy Boolean flags no longer authorize acquisition. SciREX without
   a checksum is labelled size-checked, not verified.
7. **No pooling:** score output is donor-specific and the cross-source terminal
   is always `NO_POOLED_PASS`.
8. **Executable source-to-case path:** the OAEI builder reads only `onto.rdf`,
   verifies the provider archive MD5, hashes every input member and constructs
   an exhaustive type-compatible candidate universe.

## Direct evidence

The direct non-pytest harness passed 10/10 checks:

- valid sealing and valid four-terminal scoring;
- recursive case leakage rejection;
- closed inventory leakage rejection;
- zero coordinate-opportunity rejection;
- duplicate prediction rejection;
- invalid relation rejection;
- input-digest mismatch rejection;
- prediction cluster injection rejection; and
- a `CANNOT_CHECK` human-rights decision blocking CRAFT body acquisition.

Semantic assertions passed: exact `PLURAL` has zero loss; obstruction on a
plural truth is a positive-cost plurality collapse; coordinate PASS is emitted;
no pooled PASS is emitted; and an unresolved rights decision causes no body
acquisition.

## Input-only OAEI execution

Using the already provider-MD5-verified OAEI archive:

- source ontology: test 101, 105 parsed input entities;
- target ontologies: 20;
- exhaustive type-compatible cases: 68,043;
- independent clusters: 1;
- case-file SHA-256:
  `4e7037f6f707dd1c3af9cfe9b4c274a640f79c748bc50354403c1f0aa3763eb4`;
- `refalign.rdf` members read: 0;
- eight retained input-only cases produced 32 comparator mechanics rows.

The full 77,816,448-byte case file was removed because it is deterministically
reproducible and inappropriate as a large repository artifact. Its receipt and
hash are retained.

## Remaining scientific blockers

- no P3 epistemic-envelope candidate;
- no strongest source-native external comparator;
- no public-gold join or empirical output;
- OAEI remains one seed family and supports no population interval;
- CRAFT and SciREX human rights decisions remain absent;
- no natural temporal-context donor;
- no fresh protected gold, independent adjudication or external custody; and
- no execution of the frozen 768-cluster programme.

**Current terminal:**
`V1_1_MECHANICS_REPAIRED__OAEI_INPUT_CASE_PATH_EXECUTED__EMPIRICAL_AND_COMPARATIVE_TERMINALS_CANNOT_CHECK`
