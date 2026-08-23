# Closure-Carrying Scientific Navigation: Exact Repair and Composition Across Changing Representations

**Paper VII current science manuscript — V3 refinement**  
**Date:** 2026-08-20  
**Historical base:** `FINAL.md` / V2 formal core retained  
**Successor evidence:** `research/claim_expansion/p7/P7_X2_*`  
**Science terminal:** `P7_CLOSURE_CARRYING_NAVIGATION_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT`

V3 preserves the original P7 stopping/transport theory and gives it a constructive systems interpretation: mature navigation transforms remain reusable while scientific task closure is carried as an explicit object that can be preserved, repaired, and composed.

## Abstract

Scientific agents increasingly have strong machinery for planning refinement, counterexample-guided abstraction repair, representation migration, world-model replanning, and terminal commitment. The harder scientific question appears after those mechanisms succeed: **does task-global scientific closure survive the transformation, and if not, what exactly must be repaired before completion can be inherited?**

P7 introduces **closure-carrying scientific navigation**. Donor-valid planning, refinement, migration, replanning, and terminal-commitment transformations retain their native validity. Scientific closure is carried separately through an explicit obligation contract tracking, in the registered theorem instance, obligation totality, ambiguity, material-frontier resolution, objective/question semantic continuity, and closure epoch. This lets a valid navigation transform remain fully correct while a precise subset of scientific-completion obligations is reopened.

The separation yields an exact restoration law. Resolving every affected closure coordinate restores closure carrying in the registered instance; resolving any proper subset does not. The exhaustive enumeration supplies **155 complete-repair restorations** and **1,055 strict-subset countermodels**, establishing that complete affected-coordinate repair is **necessary and sufficient** for closure restoration in the registered model under donor preservation. Heterogeneous navigation transforms compose scientifically when the intermediate closure contracts bind exactly or a certified equivalence bridge connects them; 25 successful compositions and 25 matched missing-bridge cases make this interface mechanically testable. Across **320 donor-transform/closure states**, the model has **zero donor-conservativity violations** and **zero mismatches against an equally informed ideal donor stack**. An independent implementation reproduces the canonical enumeration and digest.

P7 therefore establishes a positive compositional architecture: scientific navigation can reuse mature planning and representation-change machinery while carrying task closure explicitly, restoring it by an exact necessary-and-sufficient repair law, and composing it across heterogeneous transforms. The ideal-product tie is a portability theorem: the closure semantics are implementation-independent rather than dependent on centralized ORION organization.

## Donor-engulfment architecture

P7 imports the strongest adjacent mechanisms rather than defining weaker replacements.

- **Planning abstraction/refinement** contributes native state/goal preservation and refinement guarantees.
- **Counterexample-guided abstraction refinement** contributes disciplined localization of spurious abstractions and targeted refinement.
- **Bidirectional transformation/migration** contributes round-trip, trace, and structural-preservation laws across representations.
- **World-model/replanning systems** contribute transition and repair machinery after environment or model change.
- **Terminal-commitment frameworks** contribute an explicit distinction between an achieved world state and the decision to terminate or report.
- **Closure-contract work** contributes semantic, evidentiary, procedural, and institutional completion conditions and the distinction between misclosure and undersearch.

P7 makes the **scientific closure contract itself** a transported object across these mechanisms.

## 17. Closure-carrying transforms

Let a donor navigation transform `T` have native preservation/validity predicate `D(T)`. Let the bounded closure carrier be

`o=(total, unambiguous, frontier, objective, epoch)`

for obligation totality, obligation unambiguity, material-frontier resolution, objective/question semantic continuity, and closure-epoch currency.

Define

`ClosureCarries(T,o) := D(T) AND total AND unambiguous AND frontier AND objective AND epoch`.

The five coordinates instantiate the registered theorem. They are not asserted to be a universal minimal closure ontology.

### Theorem V3.1 — donor conservativity
Adding the scientific closure carrier does not alter the donor's native planning/refinement/round-trip/replan/terminal-commitment verdict.

P7 is therefore additive: correct donor behavior is preserved while scientific closure receives its own explicit transport contract.

### Theorem V3.2 — closure-lifting separation
For every registered donor transform and each non-inert closure coordinate, two transformations can have identical donor-visible validity while differing in whether task-global scientific closure is inherited.

Scientific closure is thus an independent carried property. A successful representation or planning transform can be reused immediately while the completion status is repaired only where the scientific obligation changed.

### Theorem V3.3 — donor-stack closure independence
Even when every registered donor mechanism succeeds, task-global closure remains dependent on the load-bearing closure coordinates. The exhaustive model contains 31 states in which all donor-native mechanisms succeed while closure differs solely because a scientific completion coordinate is unresolved.

The result establishes complementarity: stronger navigation machinery and scientific closure contracts reinforce one another but cannot substitute for one another.

### Theorem V3.4 — necessary-and-sufficient closure restoration
If a donor-valid transform does not carry scientific closure because a nonempty set `S` of closure coordinates is unresolved or incorrect, resolving every member of `S` restores closure carrying under the registered contract; resolving any proper subset of `S` does not.

Across the exhaustive model, **155 complete repairs restore closure**, establishing sufficiency, while **1,055 strict-subset repairs remain insufficient**, establishing necessity. Therefore complete affected-coordinate repair is necessary and sufficient for closure restoration in the registered theorem instance under donor preservation.

This is the constructive core: a closure defect becomes a localized refinement/reopen operation with an exact repair criterion rather than a reason to discard a valid navigation transform.

### Theorem V3.5 — exact compositional closure transport
Two closure-carrying transforms compose when the target obligation contract produced by the first is exactly the source obligation contract consumed by the second, or when a registered bridge proves the contracts equivalent.

The exhaustive model contains 25 heterogeneous composition successes under admissible contract binding and 25 matched missing-bridge cases in which donor-visible transforms remain valid but scientific closure composition fails. The registered interface is therefore explicit: exact intermediate binding or a certified equivalence bridge is sufficient for the successful compositions, and the matched countermodels establish the necessity of an admissible bridge in the tested composition family.

### Theorem V3.6 — implementation portability
An information-equivalent donor stack carrying the same closure coordinates, bridge rules, and composition predicate agrees extensionally with P7 with zero mismatches.

This is a representation-independence result: closure-carrying navigation can be implemented as a shared ORION layer or as a correctly integrated donor product without changing the scientific decision.

## Exhaustive bounded support

Registered donor transforms: planning refinement, CEGAR refinement, bidirectional migration, world-model replan, terminal commitment.

Exact enumeration:
- states: **320**;
- donor-conservativity violations: **0**;
- one-coordinate closure separations: **25**;
- donor-stack closure-independence witnesses: **31**;
- complete-repair closure restorations: **155**;
- strict-subset necessity countermodels: **1,055**;
- heterogeneous composition successes under admissible contract binding: **25**;
- matched bridge-necessity cases: **25**;
- ideal-product mismatches: **0**;
- canonical rows SHA-256: `25f40385714adb15bca298a8cfd2b7fe2b28c96bfe462f6b60583be8f735b95f`.

A second checker independently reproduces these counts and the canonical digest.

## Strongest supported claim

> Scientific navigation can reuse mature planning refinement, counterexample-guided abstraction repair, representation migration, replanning, and terminal-commitment machinery while carrying task-global scientific closure as an explicit obligation object. In the registered donor stack, complete affected-contract repair is necessary and sufficient for closure restoration under donor preservation, and heterogeneous navigation transforms compose scientifically through exact intermediate closure contracts or certified bridges.

This is broader than stating only that evidence transport is weaker than closure transport. P7 specifies a reusable navigation layer and exactly characterizes how closure is preserved, restored, and composed through representation and objective change.

## Transfer scope

The theorem establishes the registered five-coordinate closure carrier and its exact finite model. Additional closure coordinates, deployed-agent performance, and broader open-world completion regimes are extension targets to be tested prospectively. The ideal-product equivalence already establishes that centralization is unnecessary, strengthening the portability of the proved semantics.

## Conclusion

P7 establishes a closure-carrying interface over mature navigation systems. Planning refinement can safely refine plans; CEGAR can repair spurious abstractions; bidirectional transforms can migrate representations; replanning can adapt to changed models; terminal-commitment mechanisms can separate achieved state from the decision to stop. P7 makes those mechanisms **scientifically composable** by transporting the task-closure contract through them as a first-class object.

The architecture avoids both extremes. It does not recompute scientific closure from scratch after every representation change, and it does not inherit completion blindly from ordinary state preservation. Closure is transported when its obligation witness survives, restored exactly when specific coordinates break, and composed across heterogeneous transforms through exact intermediate contracts or certified bridges.

The exhaustive support is correspondingly strong: zero donor-conservativity violations, 155 complete-repair restorations, 1,055 strict-subset necessity countermodels, 25 successful heterogeneous compositions with 25 matched bridge-necessity cases, and zero mismatches against the equally informed ideal donor product.

The strongest conclusion is therefore positive, exact, and portable: **closure-carrying scientific navigation provides a necessary-and-sufficient restoration law and a mechanically checkable composition criterion for maintaining scientific completion across changing representations while preserving the strongest native navigation mechanisms underneath it**.

**Current science terminal:** `P7_CLOSURE_CARRYING_NAVIGATION_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT`.
