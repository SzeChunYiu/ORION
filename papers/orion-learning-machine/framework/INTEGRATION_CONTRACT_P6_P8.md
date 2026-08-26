# Prospective P6/P7/P8 integration contract

**Status:** research adapter contract; no edits to the P6–P8 lane.

P9/P10 deliberately avoid re-owning mechanics, navigation or authority.

## P6 dependency

P9 currently uses `MechanicSpec` and `EmpiricalMechanicContract` as local placeholders. When P6 stabilizes, the adapter should map each absorbed mechanic into the P6 mechanic/effect contract while preserving:

- read/write/effect identity;
- hard residual obligations;
- dependency effects/reopening requirements;
- provenance;
- donor-protected traits;
- execution/failure terminals.

If two local donor records cannot conservatively embed into one P6 contract, they remain distinct mechanics; generalization must not erase the discriminator.

## P7 dependency

The P9 planner currently treats state transition models as fixed caller-provided functions. P7 should own any operation that changes the problem/world topology or representation chart. A P9 plan may request a reframe mechanic, but P7 determines what state/route identities survive or reopen after that transformation.

## P8 dependency

`LearningMachine.execute_plan` requires an external `authorizer(state, mechanic) -> Verdict`. P8 should implement the eventual authority derivation. P9 competence, frequency, success history, macro support or predicted benefit are never sufficient authority tokens.

## P4/P10 verification dependency

P10's `bind_verifier_receipt` checks identity binding only. P4/P8 decide whether the verifier identity, custody, chronology and evidence are admissible for scientific promotion.
