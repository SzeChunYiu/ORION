# ORION Negative-to-Working-Method Recovery Programme V1

Status: `R0_ATLAS_CONSTRUCTION_ACTIVE`
Parent coordinator: #964
Base: `611b885c1e84719ea3e4791d4fb2d7b1b65219f0`

## Research objective

Historical negative results are not publication debris. They are causal evidence about where a research process failed.

The programme asks:

> Can ORION learn from cutoff-correct historical failures to diagnose the responsible scientific layer and select materially better successor research moves, then transfer that recovery behavior to a new negative whose repair is not known at freeze time?

The target is research competence, not a paper.

## Governing rule

```text
NEGATIVE
 -> preserve exact result
 -> reconstruct cutoff-valid evidence
 -> dual-harness responsibility diagnosis
 -> freeze successor
 -> execute
 -> preserve new evidence
 -> recurse
 -> WORKING METHOD / REGIME POSITIVE / LOWER BOUND / SATURATION
```

A later successful repair may be used only by the evaluator. It is never visible to the recovery system during a historical blind replay.

## Episode object

`NegativeRecoveryEpisode.v1` binds:

- episode id/version;
- scientific owner/domain;
- cutoff identity;
- exact failed target/protocol;
- raw negative evidence references;
- attempted mechanism;
- candidate responsibility classes that were expressible at cutoff;
- known donor/search state at cutoff where reconstructible;
- representation/method-language/resource state;
- evaluator-only later trajectory;
- evidence-admissibility state.

Admissibility is one of:

- `ADMISSIBLE_CONTENT_BOUND` — immutable artifacts/commit/receipts are sufficient for blind replay;
- `ADMISSIBLE_BOUNDED_WITH_EXTERNAL_POINTERS` — source is stable but some evidence is issue/PR bound rather than merged-tree bound;
- `RECONSTRUCTION_REQUIRED` — scientifically interesting but cannot yet be used as scored gold;
- `REJECTED_LEAKY_OR_UNBOUND`.

## R0 — atlas construction

Build a deliberately mixed atlas containing:

1. **recoverable failures** where a later materially different successor worked;
2. **regime-boundary failures** where the old negative becomes the boundary of a positive method;
3. **donor collapses** where the correct action is to absorb prior art rather than invent;
4. **exact/lower-bound stops** where more neural/search complexity is scientifically unjustified;
5. **evidence-admissibility failures** where the first task is reconstructing the experiment, not solving it.

The model must not be able to win by learning `NEGATIVE -> INVENT`.

## R1 — blind historical recovery

At each episode cutoff, both lanes receive only cutoff-valid evidence.

### Lane A — generic ORION research harness

Outputs:
- responsibility distribution / surviving hypotheses;
- cheapest discriminating next observation;
- proposed successor mechanism class;
- expected observations under alternatives;
- whether representation/method-language escalation is licensed.

### Lane B — native owner harness

Uses the strongest exact/domain-native state available at the historical cutoff and independently outputs the same comparison coordinates.

### Frozen scoring coordinates

- responsible-layer match;
- functional successor-family match;
- discriminator validity;
- false broad-escalation rate;
- unnecessary invention rate;
- lower-bound/donor-sufficient recognition;
- evidence citations limited to cutoff-valid sources;
- recovery cost.

Functional equivalence is accepted; exact historical wording is not required.

## R2 — recovery policy

Only after R1 is leakage-safe, learn/derive a policy over failure structure.

Candidate state:

```text
FailureState = (
  failed_contract,
  counterexamples,
  information_ceiling,
  resource_profile,
  representation,
  method_language,
  failure_scope,
  donor_pressure,
  unresolved_discriminators
)
```

Candidate transition:

```text
RecoveryDelta in {
  ACQUIRE_DISCRIMINATING_EVIDENCE,
  CHANGE_ACCESS_GEOMETRY,
  CHANGE_STATE_REPRESENTATION,
  INCREASE_MODEL_CAPACITY,
  ALLOCATE_MORE_TEST_TIME_COMPUTE,
  REOPEN_SCOPED_FAILURE,
  ADOPT_DONOR_MECHANIC,
  CHANGE_RESOURCE_REGIME,
  REPAIR_EVALUATOR_OR_CUSTODY,
  EXPAND_METHOD_LANGUAGE,
  PROVE_LOWER_BOUND,
  UNRESOLVED
}
```

The exact downstream mechanic/verifier gets first right of refusal. The learned system proposes the research transition; it does not self-authorize correctness or novelty.

## R3 — prospective unknown-negative recovery

The decisive experiment uses a newly frozen failure for which no successful repair is known.

1. freeze evidence and budgets;
2. execute both diagnoses independently;
3. seal next discriminator/successor;
4. run the successor;
5. retain failure if negative;
6. recurse using only newly earned evidence;
7. stop only at working method, regime-limited positive, rigorous lower bound, donor/successor saturation, or concrete external blocker;
8. independently replay the terminal.

## Success terminals

Primary:

`ORION_NEGATIVE_TO_WORKING_METHOD_RECOVERY_SUPPORTED`

Requires historical blind recovery across materially different responsibility classes plus at least one prospective unknown-negative recovery that reaches a verified working method or bounded positive.

Higher-order:

`ORION_BOUNDED_METHOD_LANGUAGE_EXPANSION_FROM_FAILURE_SUPPORTED`

Requires correct rejection of lower-level repairs, independently certified bounded inadequacy of the incumbent method language, a generated method/representation edit, held-out reach expansion, and false-invention controls.

## Necessary negative control

At least one protected episode must have the correct terminal `LOWER_BOUND_CLOSED` or `DONOR_COMPLETE` and the recovery system must **not** continue inventing. A system that always proposes a more complex successor fails the research objective.

## Publication boundary

No manuscript optimization is part of V1. Publication work reopens only after the research terminal is earned or the strongest honest bounded terminal is stable.