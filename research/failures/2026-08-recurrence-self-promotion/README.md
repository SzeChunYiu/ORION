# Recurrence self-promotes a failure guard

## Observed

At exact `main` commit `3fdff9e252ee0869b52f0e8f04b55897b38757be`,
the existing regression test
`test_repeated_unresolvable_evidence_produces_an_executable_guard` passes. It
constructs two caller-generated rounds/splits with recurring missing-artifact
failures and asserts that `learn_guards` returns an active guard. The targeted
test result was:

```text
Pytest: 1 passed
```

Source inspection shows that `learn_guards` assigns `VERIFIED_LOCAL` when a
core signature appears under at least two `split_id` values. No protected
held-out replay, fresh transfer or protected evaluator is required before the
guard changes later selection/gating behavior.

The targeted test was re-run after concurrent PRs #27 and #28 at
`5894ac7814d194b3c60d9655af87ef2d9828d56c` and still passed, confirming that
the behavior remains current.

## Failure

Recurrence supports abstraction of a candidate failure pattern; it does not
validate the proposed repair or guard. Caller-generated split labels are not
protected independence. Activating the guard also creates selective pressure:
the system can hide future counterevidence by filtering the very cases needed
to falsify the lesson.

## Failure class

`RECURRENCE_AS_PROMOTION_AUTHORITY` + `CALLER_LABEL_AS_INDEPENDENCE` +
`SELF_CONFIRMING_GUARD`.

## Correct response

- Repeated failures create only `CANDIDATE` patterns.
- Promotion requires support-case replay with the guard actually executed,
  disjoint fresh transfer, exact content/episode bindings and a protected
  evaluator outside candidate control.
- Keep counterfactual/holdout traffic so active guards remain falsifiable.
- Append revisions and revocations; never erase the original failure or failed
  lesson generation.

## General lesson candidate

Learning from failure has two different transitions: detect a recurring shape,
then validate a behavior-changing response. Collapsing them makes repetition a
write credential and turns memory into an authority-escalation channel.

## Residuals and reopen coordinates

- protected replay/transfer manifests and evaluator trust roots;
- guard shadow mode, counterfactual logging and rollback;
- stale or revoked lesson dependencies;
- alternative diagnoses and discriminating tests before causal repair.
