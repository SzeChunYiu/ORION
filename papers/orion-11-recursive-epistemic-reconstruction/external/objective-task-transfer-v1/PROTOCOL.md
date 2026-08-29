# ORION11.OBJECTIVE_TASK_TRANSFER.v1

**Status:** `DESIGN_ONLY__NO_PROTECTED_OUTCOME_AUTHORITY`  
**Scientific authority delta:** `NONE`

## Scientific question

Does the bounded ORION-11 claim that a targeted epistemic-state mutation is mechanically necessary for reliable recovery survive on independently sourced real task families with external objective verifiers, or is the current effect a property of the synthetic world generator and its state representation?

This is a new transfer identity. The historical 2,880-record campaign remains instrument validation only, and the faithful-comparator negative history is retained. No historical record can count toward the confirmatory N below.

## Three domain strata

Freeze **30 independent task families**, 10 per stratum, before protected outcomes:

1. **Defects4J / executable bug-repair lineages.** A family is one independently maintained Java project with a historical change whose validity can be scored by a frozen external test oracle.
2. **Lean/mathlib / proof-maintenance lineages.** A family is one source module or project lineage with a historical dependency change and a theorem/proof obligation scored by the Lean kernel under a pinned toolchain.
3. **Reproducible workflow lineages.** A family is one independently maintained public workflow/data-analysis project with a historical dependency/schema/input change and a pre-existing executable regression/reproduction oracle. The oracle must predate ORION inclusion and must not be authored for this study.

If a stratum cannot yield ten eligible independent families without reusing organizations or constructing a new ORION-authored gold oracle, terminate that stratum `CANNOT_CHECK_INSUFFICIENT_INDEPENDENT_FAMILIES` rather than substitute synthetic cases.

## Task construction

For each family select one or more real historical state transitions **without inspecting arm outcomes**. A transition must expose:

- a pre-change task/evidence state;
- a real exogenous change `delta`;
- an externally checkable post-change target;
- a declared dependency/impact relation available to all arms;
- at least one invariant that must remain preserved.

Candidate transitions are frozen before any arm is executed. No transition may be replaced after protected output is observed.

## Four matched arms

All arms receive the same task bytes, change bytes, dependency information, verifier interface **description** (not its protected answer), and wall-clock/resource ceiling.

- **A0 STALE_STATE:** retain the pre-change epistemic state; no targeted update. Negative mechanism control.
- **A1 MATCHED_RANDOM_MUTATION:** mutate the same number/type of state elements as A2, sampled from a frozen outcome-blind rule that ignores dependency impact. Controls for generic perturbation and mutation budget.
- **A2 TARGETED_MUTATION:** apply the ORION-11 dependency-impact-bound mutation under the frozen bounded semantics.
- **A3 GLOBAL_RESET:** rebuild/reconstruct the complete admissible state from post-change inputs. Strong correctness comparator; its extra realized resource cost is measured, not hidden.

No arm may receive information unavailable to another arm except that A3 is allowed to spend work reconstructing information from the common inputs. If A2 consumes privileged gold dependency labels unavailable in the real task interface, the family is `CANNOT_CHECK_INFORMATION_PARITY`.

## Primary endpoints

The family is the inference unit. Within-family transitions are descriptive support, not independent replicates.

For each family record:

1. **objective recovery correctness** under the external verifier;
2. **protected-invariant violation rate**;
3. **false recovery / unsafe acceptance**;
4. **realized work** under a frozen cost vector (CPU/wall/tool calls/bytes as applicable);
5. **mutation footprint**.

Define the pre-outcome family comparison `A2 > A1` lexicographically:

1. fewer unsafe acceptances;
2. if tied, more objectively correct recoveries;
3. if tied, fewer protected-invariant violations;
4. otherwise tie. Cost does **not** break the primary scientific tie.

Define A2 versus A3 separately: A2 must be correctness-noninferior at the family level while using strictly less median realized work. The noninferiority margin and work metric must be frozen per domain before protected execution.

## Portfolio gate

For the A2-versus-A1 mechanism test, a family win is 1 and tie/loss is 0. Promotion support requires all of:

- at least **21/30** family wins overall;
- at least **6/10** wins in each of the three domain strata;
- no post-outcome family deletion;
- all known-negative controls fire;
- A2 versus A3 satisfies the separately frozen correctness-noninferiority + work-reduction gate in every domain;
- no unresolved information-parity or verifier-custody blocker.

Under independent fair-coin family wins, the exact probability of `>=21/30` and `>=6/10` in each stratum is **0.01615840569138527**. At a true independent family-win probability 0.80, the gate power is **0.8817023923578056**. These operating characteristics are design diagnostics, not assumptions that real families are independent; dependence is handled by keeping the family, not the transition, as the primary unit and by reporting domain-stratified uncertainty.

## Mechanism interpretation

A favourable A2-versus-A1 result supports **targeting by the declared impact relation**, not “mutation in general.” A favourable A2-versus-A3 result supports an efficiency claim conditional on matched correctness. Neither result establishes that ORION's internal dependency map is causally complete in arbitrary open-ended science.

The following outcomes are explicitly adverse:

- A1 matches or beats A2 on the registered gate;
- A3 is materially more correct than A2;
- A2 succeeds only in one domain;
- a family-level advantage disappears when organization duplicates are collapsed;
- real dependency information required by A2 is unavailable without gold leakage.

## External-authority boundary

The task oracles must be native and pre-existing (tests, kernel, or independently maintained regression/reproduction checks). Same-programme scoring code may aggregate them but does not become the gold source. External peer review and novelty remain separate publication gates.
