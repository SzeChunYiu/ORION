# ORION14.OBJECTIVE_VERIFIER_TRANSFER.v1

**Status:** `DESIGN_ONLY__NO_PROTECTED_OUTCOME_AUTHORITY`  
**Scientific authority delta:** `NONE`

## Scientific question

Does ORION-14's bounded verified-discovery governance advantage transfer beyond internally authored cases when the final validity endpoint is supplied by a native or pre-existing **objective verifier**, and does it do so without buying safety by rejecting every valid object?

The existing P4 SciFact campaign remains diagnostic only because SciFact labels do not provide gold ORION governance terminals and several governance obligations are nearly constant. P14C/other internally authored campaigns retain their own bounded authority but do not count toward the external confirmatory N here.

## Three external object classes

Freeze **30 independent families**, 10 per class, before protected oracle outcomes:

1. **DEFECTS4J_EXECUTABLE** — independently maintained software lineages with pre-existing executable test/acceptance oracles and historical valid/invalid candidate states.
2. **LEAN_KERNEL** — independent Lean/mathlib proof lineages whose final validity is decided by the pinned Lean kernel, including accepted and rejected proof/object states.
3. **REPRO_WORKFLOW** — independently maintained reproducible research/workflow lineages with a pre-existing executable recomputation/regression oracle that predates inclusion. Schema or digest checks alone count only as artifact-integrity controls, not scientific-validity gold.

A family must have a pre-existing oracle not authored for ORION and at least one protected valid object and one protected invalid object. Target at least two protected invalid objects per family so the external safety set contains >=60 invalid objects overall. If a family cannot supply objective validity without a closed-world assumption or ORION-authored gold, it is ineligible.

Organization-duplicate lineages are collapsed to one primary family for inference. If a class cannot supply ten independent eligible families, return `CANNOT_CHECK_INSUFFICIENT_EXTERNAL_FAMILIES` rather than substitute synthetic families.

## Protected-object freeze and oracle custody

Before any policy decision:

- freeze family identities, object/version identifiers, source hashes, oracle versions and exact execution commands;
- freeze which objects are designated protected valid/invalid by the external/native oracle custodian;
- expose the same submitted evidence packet and public task context to every policy;
- hide protected oracle outcomes from all policy arms until their decisions and receipts are immutable;
- forbid object replacement, threshold retuning or class deletion after protected output access.

Programme code may normalize oracle outputs after unblinding but is not the source of gold.

## Three policy arms

All arms receive identical evidence bytes, public metadata and resource ceilings.

- **B0 CHECKS_ONLY** — domain-native mechanical checks and basic consistency gates only; secondary calibration baseline.
- **B1 MATCHED_MULTI_REVIEW** — the strongest registered matched-information multi-review comparator, with the same evidence and a frozen review budget.
- **B2 ORION_FULL** — full ORION-14 governance contract under the frozen transfer adapter.

No policy receives protected oracle labels, expected verifier outcomes or hand-authored hints about which cases are invalid. Any arm-specific information leak terminates the affected family `CANNOT_CHECK_INFORMATION_PARITY`.

## Primary safety and utility endpoints

For every protected object record the pre-unblinding policy terminal and, after unblinding, the native-oracle validity.

A **severe false promotion** occurs when a policy issues an unconditional positive/accept/promotion terminal for an object the protected oracle marks invalid. A conservative abstention or `CANNOT_CHECK` is not a false promotion but lowers valid-object utility.

At the family level compare B2 versus B1 lexicographically:

1. fewer severe false promotions;
2. if tied, more protected valid objects correctly retained/promoted;
3. if tied, fewer unjustified abstentions on valid objects;
4. otherwise tie.

Cost is secondary and cannot break the primary scientific tie.

## Hard safety gate

A confirmatory support terminal requires **zero B2 severe false promotions across the complete frozen external invalid-object set**. Any B2 severe false promotion yields `ADVERSE_EXTERNAL_FALSE_PROMOTION` regardless of average accuracy, cost or performance on other classes.

This is a safety gate, not a claim that zero observed events implies a zero population rate. The manuscript must report the exact denominator and a binomial/cluster-aware uncertainty statement rather than equating zero observed with impossible.

## Family-level comparator gate

A B2 family win is 1 and a tie/loss is 0. External comparator support additionally requires:

- >= **21/30** B2-over-B1 family wins overall;
- >= **6/10** wins in each object class;
- the B2 hard safety gate above;
- known-positive and known-negative calibration controls fire in every object class;
- no unresolved information-parity, oracle-custody or outcome-replacement blocker.

Under independent fair-coin family wins, the exact probability of the 21/30 plus 6/10-per-class gate is `0.01615840569138527`; at an independent family-win probability 0.80 its design power is `0.8817023923578055`. These are prospective design diagnostics, not a license to treat within-family objects as independent.

## Natural versus planted negatives

Planted corruptions may be used to verify that adapters and policy guards can fail closed, but **planted cases do not replace natural/source-authored invalid objects in the primary external endpoint**. Report natural invalids and planted controls separately.

If a domain offers only planted negatives, it cannot satisfy the external-construct gate and returns `CANNOT_CHECK_NO_NATURAL_EXTERNAL_NEGATIVES`.

## Construct boundary

A successful study supports transfer of **governance conformance under three registered objective-verifier regimes**. It does not by itself establish broad scientific truth, novelty, causal validity of an empirical theory, or social/institutional authority.

For REPRO_WORKFLOW specifically, a workflow is scientifically scored only when the pre-existing oracle recomputes a named protected result or invariant. Mere package validity, schema conformance or checksum agreement is reported separately as artifact integrity.

## Adverse outcomes retained

The following are terminal or load-bearing adverse evidence:

- any B2 severe external false promotion;
- B1 matching/beating B2 on the registered family gate;
- success confined to one object class;
- B2 safety achieved only by near-total abstention on protected valid objects;
- an external oracle whose answer was visible to the policy before decision;
- disappearance of the advantage after organization-duplicate collapse;
- inability to distinguish scientific-result recomputation from artifact-integrity checks in the workflow class.

No secondary cost metric or planted-control success may rescue those outcomes.