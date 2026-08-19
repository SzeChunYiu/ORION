# P7-X2 donor engulfment and improvement map V1

Date: 2026-08-19
Parent: #534

## Doctrine
P7 absorbs the strongest preservation/completion mechanisms from adjacent fields before asking for novelty. A donor's unique strength becomes part of ORION's navigation substrate; the scientific question is what additional structure is needed to make that donor preserve scientific closure rather than only its native property.

## Donor 1 — sound planning abstraction/refinement
**Unique part absorbed:** abstraction/refinement theorems that preserve established conditions/goals or guarantee that an abstract strategy has an appropriate concrete refinement under stated assumptions.

**P7 improvement:** add a closure-obligation transport witness beside the donor's state/goal preservation witness. A plan may refine correctly while scientific closure changes because target evidence, source coverage, measurement obligations or decision conditions changed.

## Donor 2 — CEGAR / counterexample-guided refinement
**Unique part absorbed:** when an abstract plan/counterexample is spurious in the concrete system, refine the abstraction and re-check instead of trusting the coarse representation.

**P7 improvement:** treat a failed closure-transport witness as a refinement counterexample. The system refines the representation/route/obligation map until closure obligations are completely transported or returns `CANNOT_CHECK/REOPEN` if a decisive discriminator is unavailable.

## Donor 3 — bidirectional transformation / round-trip migration
**Unique part absorbed:** forward/backward transformation with round-trip/consistency laws, trace correspondences and structural preservation across representations/schema versions.

**P7 improvement:** add scientific-closure round-trip obligations. A round-trip-correct representation transform can still create/drop scientific obligations or change what is needed to justify task completion. P7 therefore keeps ordinary round-trip laws and layers an obligation-transport witness on top.

## Donor 4 — VIGIL-style terminal commitment
**Unique part absorbed:** independently score world/task-state completion and the agent's terminal commitment/report instead of collapsing them into one success signal.

**P7 improvement:** terminal commitment becomes one donor-local closure coordinate rather than the global scientific terminal. A report can be correctly grounded in an achieved state while scientific task closure remains open because evidentiary/source/representation obligations are unresolved.

## Donor 5 — Science-of-Intent closure gaps / contract tuples
**Unique part absorbed:** explicit semantic, evidentiary, procedural and institutional closure contracts; distinction between misclosure and undersearch; closure interventions as a separate control problem from more search.

**P7 improvement:** make closure contracts *transportable objects* across navigation/representation changes. P7 asks what happens when a route, abstraction, model, representation or objective transformation changes the contract itself, and supplies composition/reopen semantics for that transition.

## Absorbed product
The strongest P7 donor product therefore includes:

`planning preservation/refinement + counterexample-guided reopen + round-trip representation traces + explicit task/world completion + terminal commitment + explicit closure contracts`.

P7-X2 grants all of these. The only additional object is a scientific closure carrier that records which obligations must survive/transform for the new state to inherit task closure.

## Improvement properties
1. **closure-carrying transform** — donor transform plus exact obligation-transport witness;
2. **closure refinement** — failed/ambiguous obligation transport becomes a CEGAR-style refinement target, not forced completion;
3. **closure round trip** — representation round-trip success is supplemented by obligation round-trip/target-new-obligation accounting;
4. **terminal hierarchy** — world completion and terminal commitment are retained, but task-global scientific closure is a stronger state;
5. **compositional transport** — closure-carrying transforms compose only when the intermediate obligation contract is exactly bound;
6. **ideal-product equivalence** — a donor product with identical closure obligations and transport rules ties exactly.

## Candidate wider claim
> P7 provides closure-carrying navigation semantics: strong planning/refinement, CEGAR, round-trip representation and terminal-commitment mechanisms are reused as donor transforms, while scientific task closure is transported only by explicit obligation witnesses; transport failures become targeted refinement/reopen operations and correctly transported closures compose across heterogeneous navigation changes.

This is a wider constructive architecture claim, not the narrower statement that evidence preservation is different from closure.
