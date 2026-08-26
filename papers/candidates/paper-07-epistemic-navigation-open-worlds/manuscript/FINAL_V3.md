# Epistemic Navigation in Open Worlds — V3 science update

**Paper VII current science manuscript overlay**  
**Date:** 2026-08-19  
**Historical base:** `FINAL.md` / V2 formal core retained  
**Successor evidence:** `research/claim_expansion/p7/P7_X2_*`  
**Science terminal:** `P7_CLOSURE_CARRYING_NAVIGATION_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT`

V3 preserves the original ORION-17 stopping/transport theory and widens its interpretation constructively by absorbing mature planning, refinement, representation-migration and completion mechanisms into a closure-carrying navigation architecture.

## Replacement abstract for V3

Scientific navigation already has strong donor mechanisms. Planning theory supplies sound abstraction/refinement; counterexample-guided refinement reopens spurious abstractions; bidirectional transformations and migration systems preserve representation structure through round-trip/trace relations; world-model systems replan after state change; and recent completion work separates achieved world state from an agent's terminal commitment. ORION-17 treats these as reusable navigation transforms rather than as competing novelty claims.

The remaining scientific problem is how task-global closure survives such transforms. ORION-17 introduces a bounded **closure-carrying navigation semantics**: a donor-valid transformation carries scientific task closure only through an explicit obligation witness. In the registered theorem instance the carrier tracks obligation totality, ambiguity, material frontier resolution, objective/question semantic continuity, and closure epoch. A valid planning refinement, representation round trip, replan or terminal commitment can therefore remain valid in its native theory while failing to inherit scientific task closure. Conversely, a transport failure need not discard the donor transform: the failed closure coordinates become a targeted refinement/reopen problem, extending counterexample-guided refinement from state abstraction to closure obligations. Closure-carrying transforms compose across heterogeneous mechanisms only when the intermediate obligation contract is exactly bound or explicitly bridged.

An exhaustive finite model evaluates 320 donor-transform/closure states with zero donor-conservativity and zero ideal-product mismatches. It contains 25 minimal one-coordinate closure separations, 31 donor-product nonclosure countermodels, 155 exact closure-refinement successes, 1,055 failures of proper-subset refinement, 25 heterogeneous transform-pair composition successes and 25 bridge-mismatch composition countermodels. An independent implementation reproduces the canonical enumeration. The result is a bounded compositional scientific-closure architecture over absorbed navigation mechanisms, not generic planning, stopping, representation change or deployed-agent superiority.

## Donor-engulfment interpretation

V3 explicitly imports rather than subtracts the strongest adjacent mechanisms.

- **Planning abstraction/refinement** contributes native state/goal preservation and refinement guarantees.
- **Counterexample-guided abstraction refinement** contributes a disciplined way to turn a spurious abstraction into the next refinement target.
- **Bidirectional transformation/migration** contributes round-trip, trace and structural-preservation laws across representations.
- **World-model/replanning systems** contribute transition and repair machinery after environment/model change.
- **Terminal-commitment frameworks** contribute an independent representation of world completion versus an agent's decision to terminate/report.
- **Closure-contract work** contributes explicit semantic/evidentiary/procedural/institutional completion conditions and the distinction between misclosure and undersearch.

ORION-17's contribution is to make the scientific closure contract itself a transported object across these mechanisms.

## 17. Closure-carrying transforms

Let a donor navigation transform `T` have a native preservation/validity predicate `D(T)`. Let the bounded closure carrier be

`o=(total, unambiguous, frontier, objective, epoch)`

for obligation totality, obligation unambiguity, resolution of material frontiers, objective/question semantic continuity, and closure-epoch currency.

Define

`ClosureCarries(T,o) := D(T) AND total AND unambiguous AND frontier AND objective AND epoch`.

These coordinates instantiate the theorem; they are not asserted to be a universal minimal closure ontology.

### Theorem V3.1 — donor conservativity
Adding the scientific closure carrier does not alter the donor's native planning/refinement/round-trip/replan/terminal-commitment verdict.

### Theorem V3.2 — closure-lifting separation
For every registered donor transform and each non-inert closure coordinate, two transformations can have identical donor-visible validity while differing in whether task-global scientific closure is inherited.

Thus successful refinement, evidence/state transport or terminal commitment is not weakened; it is recognized as a lower-level property that may or may not carry the full scientific closure contract.

### Theorem V3.3 — donor-product nonclosure
Even a product in which all registered donor mechanisms succeed does not infer task-global scientific closure when a load-bearing closure coordinate is unresolved. More successful navigation machinery is not a substitute for an absent closure obligation.

### Theorem V3.4 — closure refinement
If a donor-valid transform fails scientific closure transport because a nonempty set `S` of closure coordinates is unresolved or wrong, resolving all members of `S` restores closure carrying under the registered contract; resolving a proper subset does not.

This is the constructive improvement over the donors: a closure failure becomes a targeted refinement/reopen operation, analogous to CEGAR but acting on the scientific completion contract rather than throwing away a valid underlying transform.

### Theorem V3.5 — compositional closure transport
Two closure-carrying transforms compose only when the target obligation contract produced by the first is exactly the source obligation contract consumed by the second, or when a registered bridge proves them equivalent. Donor-visible composability alone does not establish closure composability.

### Theorem V3.6 — ideal-product equivalence
An information-equivalent donor stack carrying the same closure coordinates, bridge rules and composition predicate ties ORION-17 extensionally. ORION-17 therefore claims a reusable closure-carrying interface, not inherent centralization or expressive superiority.

## Exhaustive bounded support

Registered donor transforms: planning refinement, CEGAR refinement, bidirectional migration, world-model replan, terminal commitment.

Exact enumeration:
- states: **320**;
- donor-conservativity violations: **0**;
- minimal one-coordinate closure separations: **25**;
- donor-product nonclosure countermodels: **31**;
- exact full closure-refinement successes: **155**;
- proper-subset closure-refinement failures: **1,055**;
- heterogeneous composition successes under exact bridge: **25**;
- bridge-mismatch composition countermodels: **25**;
- ideal-product mismatches: **0**;
- canonical rows SHA-256: `25f40385714adb15bca298a8cfd2b7fe2b28c96bfe462f6b60583be8f735b95f`.

A second checker independently reproduces these counts and the canonical digest.

## Wider ORION-17 claim

> Scientific navigation can reuse mature planning/refinement, counterexample-guided reopening, representation-migration, replanning and terminal-commitment machinery while carrying task-global closure as an explicit obligation object; closure-transport defects can be selectively refined, and heterogeneous navigation transforms compose scientifically only when their intermediate closure contracts are correctly bridged.

This is intentionally broader and more constructive than the earlier slogan that evidence transport is weaker than closure transport.

## Limits

The registered closure coordinates are a bounded formal instance, not claimed universally minimal. Missing a closure witness does not itself prove ambiguity; `CANNOT_CHECK/REOPEN` is the fail-closed outcome unless incompatible completions are established. The theorem does not establish deployed-agent superiority, universal open-world completeness, or inherent expressive benefit over an equally typed donor product.

## Replacement conclusion for V3

ORION-17's strongest interpretation is not that existing navigation systems fail. Their strongest mechanisms become the substrate. Sound planning refinement tells us when a coarse plan maps safely to a concrete one; CEGAR tells us how to refine spurious abstractions; bidirectional transformations tell us how representations can round-trip; replanning handles changed worlds; terminal-commitment systems keep achieved state separate from the decision to stop. ORION-17 adds the missing scientific carrier that makes these mechanisms composable at the level of task closure.

The result is a navigation architecture in which closure is not recomputed from scratch after every representation change and is not silently inherited from ordinary preservation either. It is transported explicitly, selectively refined when broken, and composed through typed intermediate contracts. An equally informed donor product ties, so the contribution is the closure-carrying abstraction and its bridge/refinement laws rather than centralized implementation.

**Current science terminal:** `P7_CLOSURE_CARRYING_NAVIGATION_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT`.
