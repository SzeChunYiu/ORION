# R1 Blind Historical Recovery Protocol V1

Status: `FROZEN_BEFORE_R1_RECOVERY_OUTCOMES`
Parent: #964
Atlas: `NEGATIVE_RECOVERY_ATLAS_V1.json`

## Purpose

Historical negative-to-positive trajectories are useful only if the recovery system cannot see the later repair.

Because ORION's current repository and issue history already contain many later outcomes, **current-repo access is forbidden during scored historical recovery**.

## Three-custody split

### 1. Evaluator custody

The evaluator may read:
- the full atlas;
- later commits/issues/PRs;
- hidden successor identities;
- final historical disposition;
- independent verification artifacts.

These fields are never copied into the candidate workspace.

### 2. Cutoff builder custody

A host process reconstructs one `RecoveryCaseBundle.v1` from evidence that existed no later than the episode cutoff.

Required bundle fields:

```text
case_id
cutoff_identity
failed_contract
negative_evidence
attempted_method
available_state_representation
available_method_language
resource_budget
cutoff_valid_donors
candidate_responsibility_hypotheses
allowed_capabilities
forbidden_capabilities
bundle_digest
```

The builder must produce an audit ledger showing the provenance/date/commit of every included item.

### 3. Candidate custody

Lane A and Lane B receive only the sealed bundle plus the capabilities explicitly listed in it.

They must not receive:
- current ORION repository checkout;
- current issue/PR comments;
- post-cutoff commits;
- evaluator atlas fields;
- later terminology uniquely naming the successful repair;
- current web/GitHub search that can surface post-cutoff ORION material.

For R1 V1, external web is **off** by default. If a case requires literature access, the host supplies a frozen cutoff-valid source index and records its digest.

## Candidate outputs

Both lanes seal, independently:

```text
RecoveryProposal.v1 = {
  responsibility_state,
  defeated_hypotheses,
  unresolved_hypotheses,
  next_discriminator,
  expected_observations,
  successor_mechanism_class,
  escalation_level,
  predicted_failure_boundary,
  evidence_refs,
  cost
}
```

No candidate output can authorize scientific validity or novelty.

## Evaluation

Only after both proposals are sealed does evaluator custody open the later trajectory.

Scoring is functional:

- Did the proposal identify the correct responsible layer or an independently valid alternative?
- Would the proposed discriminator separate the live competing causes?
- Is the proposed successor materially capable of escaping the failed class?
- Did the lane avoid an unnecessary broader revision?
- Did it correctly stop on lower-bound/donor-complete controls?
- Did it cite only cutoff-valid evidence?

Exact historical method identity is not required.

### Alternative-better-than-history rule

If a candidate proposes a different successor than history, the evaluator must not mark it wrong solely for mismatch. If the alternative was derivable from cutoff-valid information, is prospectively frozen, and later verifies a stronger result under matched scope/resources, it is a **research improvement over the historical path**.

## Leakage sentinels

Before scoring, plant/verify:

- later-successor name absent from bundle;
- later terminal strings absent;
- later commit/PR/issue ids absent unless they already existed at cutoff for another reason;
- post-cutoff terminology absence scan;
- candidate filesystem has no full atlas file;
- network/GitHub access blocked for V1;
- model prompt/context contains no evaluator-only fields;
- if model pretraining could plausibly contain the historical outcome, use opaque/reminted case vocabulary and score mechanism recovery rather than names.

Any sentinel failure yields `R1_LEAKAGE_INVALIDATED`, not a recovery score.

## Split doctrine

The initial atlas is calibration only.

Before any learned recovery-policy claim:
- freeze train/development historical episodes;
- freeze held-out historical episodes from different owners/failure classes;
- keep at least one prospective future negative completely outside the historical corpus;
- ensure one lower-bound/donor-sufficient control is held out.

## R1 terminal

`R1_HISTORICAL_BLIND_RECOVERY_VALIDATED`

requires:
- sealed cutoff bundles;
- both lanes executable on the same candidate-visible evidence;
- zero leakage sentinel failures;
- successful functional recovery on heterogeneous held-out historical cases;
- nontrivial lower-bound/donor-sufficient recognition;
- independent scorer/replay.

R1 success is prerequisite evidence for R2 learning and R3 prospective unknown-negative recovery. It is not the final research goal.