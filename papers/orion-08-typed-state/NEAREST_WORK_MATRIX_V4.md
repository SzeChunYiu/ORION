# ORION-08 nearest-work matrix — V4

**Literature cut:** 2026-08-29.  
**Scope:** nearest work for the bounded exact-synthetic typed/scoped-state composition claim.  
**Authority:** positioning only; no result or terminal is upgraded by this matrix.

V4 supersedes V3 for current positioning. V3 remains provenance. The important
change is that recent 2026 agent-memory and provenance work now occupies parts of
the design space that V3 described too broadly.

| Neighboring area | Current nearest work | What ORION-08 does **not** claim | Residual ORION-08 delta after V4 |
|---|---|---|---|
| typed / provenance-aware agent memory | MAP-Graph (arXiv:2608.10509) represents provenance in a typed execution graph with ancestry, permission filtering, path trust, and action gating; provenance-sensitivity auditing (arXiv:2607.20827) changes source authority while holding other task factors fixed | invention of typed memory, provenance-aware memory, or provenance-sensitive action | an **exact matched-information mechanism suite** in which the binding relation is manipulated while the factual world is held fixed, plus an exact fibre criterion for when any binding can support a zero-regret action |
| stale-memory / state revision | STALE (arXiv:2605.06527) directly benchmarks whether agents detect and act on invalidated memory; Nakayashiki (arXiv:2608.25553) studies inherited stale constraints under a fixed verification budget | first stale-state benchmark or first study of superseded memory | an exact decision-sufficiency formulation: worlds merged by one readable binding require a common optimal action; refinement helps exactly when it separates an action-impure fibre |
| value of information / information acquisition | classical VoI and active-learning parents remain; recent agent work makes budgeted information selection operational | invention of VoI, active acquisition, or budget matching | type/scoping enters as the **state variable that determines decision sufficiency**, with exact action-regret consequences and prespecified no-value regimes rather than a general acquisition heuristic |
| provenance / lineage transport | MAP-Graph and provenance-sensitivity auditing establish provenance as an operational action signal, not only audit metadata | invention of provenance, lineage, or permission filtering | exact constructed tests separating full-path transport validity from weaker last-hop readings, with the claim restricted to the frozen synthetic mechanism |
| uncertainty / Pareto verification | Nakayashiki (arXiv:2608.25553) uses the same verification budget in every arm and explicitly includes a random-record control | priority on matched-budget verification, random verification controls, or uncertainty-aware planning | **not matched budget itself**. The residual is the exact common-optimal-action/fibre criterion and its mechanism-isolation use: the paper asks when the readable binding is sufficient and when a refinement can change the optimum |
| governed / versioned long-context state | Governance Decay (arXiv:2606.22528) shows safety constraints can disappear under compaction; Gamage (arXiv:2604.20911) shows asymmetric persistence of omission vs commission constraints | first observation that long-context governance/state can decay | explicit scope/version/remint constructions with a prespecified **no-value regime** where the typed mechanism must tie re-derivation; this is a bounded synthetic mechanism claim, not deployment prevalence |
| cross-family composition | the nearest 2026 parents above are each organized around one principal mechanism family | priority on any component primitive | six separately frozen studies share one post-study contract: same factual world → vary epistemic binding → matched comparator → hostile/no-value control → exact bounded terminal |

## Nearest new parent: budgeted verification of inherited stale constraints

Nakayashiki, arXiv:2608.25553, is the closest new parent because it overlaps
four design commitments that can no longer be described as ORION-specific:
fixed factual payload across policy comparisons, equal verification budget,
a random/no-value control structure, and deterministic outcome scoring.

The remaining distinction is therefore **not** “matched-budget verification
against random verification.” It is the object being identified:

- Nakayashiki measures how a fixed two-record allocation changes behavior in a
  sampled 5,400-episode agent study.
- ORION-08's binding-sufficiency lattice is an exact finite object and states a
  biconditional: a binding supports deterministic zero regret iff each positive
  fibre has a common optimal action; a refinement is useful only when it splits
  an action-impure fibre.
- The existing transfer note maps the new parent's reported effect/null pattern
  onto that criterion, but it is explicitly a prediction check, **not** an
  episode-level re-analysis. Its stated fibre-level falsifier remains open.

This absorbs the parent rather than fencing it off.

## Boundary after V4

The bounded contribution is now stated as:

> Across six separately frozen exact-synthetic studies, ORION-08 isolates when
> an explicit epistemic binding is decision-sufficient under matched
> information. Its exact fibre criterion separates cases where refinement can
> change the optimal action from cases where it cannot. Recent empirical
> stale-memory, provenance, and budgeted-verification studies establish nearby
> phenomena; ORION-08 does not claim priority on those primitives or controls.

That statement is deliberately narrower than V3 and is the wording the
manuscript should support.
