# Closure-Carrying Scientific Navigation Across Changing Representations

**Paper VII current science manuscript — V3 refinement**  
**Date:** 2026-08-20  
**Historical base:** `FINAL.md` / V2 formal core retained  
**Successor evidence:** `research/claim_expansion/p7/P7_X2_*`  
**Science terminal:** `P7_CLOSURE_CARRYING_NAVIGATION_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT`

V3 preserves the original P7 stopping/transport theory and strengthens its interpretation constructively by absorbing mature planning, refinement, representation-migration, replanning, and completion mechanisms into a closure-carrying navigation architecture.

## Abstract

Scientific navigation already has powerful mechanisms for planning refinement, counterexample-guided abstraction repair, representation migration, world-model replanning, and terminal commitment. The unresolved systems problem is not how to replace these mechanisms, but how to preserve **task-global scientific closure** when they transform the state, representation, or objective on which completion was originally certified. P7 introduces a bounded closure-carrying navigation semantics in which a donor-valid transformation carries scientific task closure only through an explicit obligation witness. In the registered theorem instance the carrier tracks obligation totality, ambiguity, material-frontier resolution, objective/question semantic continuity, and closure epoch. A valid planning refinement, representation round trip, replan, or terminal commitment can therefore remain fully correct in its native theory while requiring targeted repair of one or more closure coordinates before scientific completion can be inherited.

The theory turns that separation into a constructive navigation rule. Exact repair of every affected closure coordinate restores closure carrying in the registered instance, while every tested proper-subset repair leaves at least one load-bearing obligation unresolved. Heterogeneous navigation transforms compose scientifically when their intermediate closure contracts match exactly or are connected by a registered equivalence bridge. An exhaustive finite model evaluates 320 donor-transform/closure states with **zero donor-conservativity violations and zero ideal-product mismatches**. It contains 25 one-coordinate closure separations, 31 all-donors-succeed states that isolate missing closure authority, 155 exact closure-refinement restorations, 1,055 proper-subset necessity witnesses, 25 heterogeneous composition successes under exact bridges, and 25 bridge-necessity witnesses. An independent implementation reproduces the canonical enumeration and digest.

The result is a positive compositional architecture: mature navigation mechanisms remain reusable donor transforms, while task-global closure becomes an explicit object that can be transported, selectively repaired, and composed across representation changes. An information-equivalent donor stack implementing the same closure fields and bridge rules ties P7 exactly, establishing that the abstraction is portable rather than dependent on centralized ORION expressivity.

## Donor-engulfment interpretation

V3 explicitly imports rather than subtracts the strongest adjacent mechanisms.

- **Planning abstraction/refinement** contributes native state/goal preservation and refinement guarantees.
- **Counterexample-guided abstraction refinement** contributes a disciplined way to turn a spurious abstraction into the next refinement target.
- **Bidirectional transformation/migration** contributes round-trip, trace and structural-preservation laws across representations.
- **World-model/replanning systems** contribute transition and repair machinery after environment/model change.
- **Terminal-commitment frameworks** contribute an independent representation of world completion versus an agent's decision to terminate/report.
- **Closure-contract work** contributes explicit semantic/evidentiary/procedural/institutional completion conditions and the distinction between misclosure and undersearch.

P7's contribution is to make the scientific closure contract itself a transported object across these mechanisms.

## 17. Closure-carrying transforms

Let a donor navigation transform `T` have a native preservation/validity predicate `D(T)`. Let the bounded closure carrier be

`o=(total, unambiguous, frontier, objective, epoch)`

for obligation totality, obligation unambiguity, resolution of material frontiers, objective/question semantic continuity, and closure-epoch currency.

Define

`ClosureCarries(T,o) := D(T) AND total AND unambiguous AND frontier AND objective AND epoch`.

These coordinates instantiate the theorem; they are not asserted to be a universal minimal closure ontology.

### Theorem V3.1 — donor conservativity
Adding the scientific closure carrier does not alter the donor's native planning/refinement/round-trip/replan/terminal-commitment verdict.

This theorem is the compatibility foundation: P7 strengthens the scientific contract without weakening or redefining correct donor behavior.

### Theorem V3.2 — closure-lifting separation
For every registered donor transform and each non-inert closure coordinate, two transformations can have identical donor-visible validity while differing in whether task-global scientific closure is inherited.

The theorem identifies scientific closure as an independent carried property. Successful refinement, evidence/state transport, or terminal commitment remains valid in its native theory; P7 determines whether that success also transports the full completion contract.

### Theorem V3.3 — donor-stack closure independence
Even when every registered donor mechanism succeeds, task-global scientific closure still depends on each load-bearing closure coordinate. The exhaustive model contains 31 such separating states. This establishes that stronger navigation machinery and scientific closure are complementary rather than substitutable layers.

### Theorem V3.4 — exact closure refinement
If a donor-valid transform does not carry scientific closure because a nonempty set `S` of closure coordinates is unresolved or incorrect, resolving every member of `S` restores closure carrying under the registered contract. Across the exhaustive model this produces 155 exact restorations. Every one of the 1,055 tested proper-subset repairs leaves a required coordinate unresolved, certifying the necessity of complete targeted repair for those theorem instances.

This is the constructive step: a closure defect becomes a localized refinement/reopen operation, analogous to CEGAR but acting on the scientific completion contract rather than discarding a valid underlying transform.

### Theorem V3.5 — compositional closure transport
Two closure-carrying transforms compose when the target obligation contract produced by the first is exactly the source obligation contract consumed by the second, or when a registered bridge proves them equivalent. The exhaustive model contains 25 heterogeneous composition successes under exact bridges and 25 matched bridge-necessity witnesses, making the interface requirement directly checkable.

### Theorem V3.6 — ideal-product equivalence and portability
An information-equivalent donor stack carrying the same closure coordinates, bridge rules, and composition predicate ties P7 extensionally with zero mismatches. This is a portability theorem: the closure-carrying semantics can be implemented as a shared calculus or as a correctly integrated donor product without changing behavior.

## Exhaustive bounded support

Registered donor transforms: planning refinement, CEGAR refinement, bidirectional migration, world-model replan, terminal commitment.

Exact enumeration:
- states: **320**;
- donor-conservativity violations: **0**;
- one-coordinate closure separations: **25**;
- donor-stack closure-independence witnesses: **31**;
- exact full closure-refinement restorations: **155**;
- proper-subset refinement necessity witnesses: **1,055**;
- heterogeneous composition successes under exact bridge: **25**;
- bridge-necessity witnesses: **25**;
- ideal-product mismatches: **0**;
- canonical rows SHA-256: `25f40385714adb15bca298a8cfd2b7fe2b28c96bfe462f6b60583be8f735b95f`.

A second checker independently reproduces these counts and the canonical digest.

## Strongest supported claim

> Scientific navigation can reuse mature planning/refinement, counterexample-guided reopening, representation-migration, replanning, and terminal-commitment machinery while carrying task-global closure as an explicit obligation object. In the registered donor stack, closure defects are exactly refinable, and heterogeneous navigation transforms compose scientifically through typed intermediate closure contracts or certified bridges.

This claim is broader and more constructive than the earlier formulation that evidence transport is weaker than closure transport. It identifies a reusable navigation layer and proves how closure is preserved, repaired, and composed.

## Scope of the theorem

The five registered closure coordinates form a bounded formal instance rather than a universal minimal ontology. A missing closure witness by itself does not prove extension ambiguity; unresolved cases remain `CANNOT_CHECK/REOPEN` unless incompatible completions are established. Deployed-agent performance and universal open-world completeness are empirical extension questions. The ideal-product equivalence theorem already establishes that centralization is unnecessary: any implementation carrying the same closure semantics is expected to reproduce the same decisions.

## Conclusion

P7's strongest interpretation is constructive. Sound planning refinement tells us when a coarse plan maps safely to a concrete one; CEGAR tells us how to repair spurious abstractions; bidirectional transformations tell us how representations can round-trip; replanning handles changed worlds; and terminal-commitment systems keep achieved state separate from the decision to stop. P7 makes these mechanisms scientifically composable by carrying the task-closure contract through them as a first-class object.

The resulting architecture neither recomputes closure from scratch after every representation change nor inherits completion silently from ordinary preservation. Closure is transported when its obligation witness survives, selectively refined when specific coordinates break, and composed across heterogeneous transforms through exact intermediate contracts or certified equivalence bridges. The exhaustive model provides zero donor-conservativity violations, 155 exact refinement restorations, 25 successful heterogeneous compositions, and zero mismatches against the information-equivalent ideal donor product.

The strongest supported conclusion is therefore positive: **closure-carrying scientific navigation is a reusable interface over mature navigation mechanisms, with exact repair and composition laws for scientific completion across changing representations**. The ideal-product tie strengthens this interpretation by showing that the semantics are architecture-independent rather than ORION-specific.

**Current science terminal:** `P7_CLOSURE_CARRYING_NAVIGATION_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT`.
