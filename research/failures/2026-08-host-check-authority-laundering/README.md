# Host-check authority laundering

## Observed

At exact `main` commit `3fdff9e252ee0869b52f0e8f04b55897b38757be`,
`work/main_gate_attack.py` supplied:

- a digest-valid weather file unrelated to the mathematical claim;
- the answer `P equals NP because the weather is rainy`;
- an answer-specific equality predicate and its own positive fixture;
- caller-selected producer/verifier lane labels; and
- caller-declared `frozen_at_round=0`.

The host battery rejected empty, junk and envelope checks, but this
answer-specific predicate rejected those generic negatives and was admitted:

```text
authority VERIFIED
check_outcome PASSED
applied ('attacker-answer',)
provisional []
math ('P equals NP because the weather is rainy',)
```

The unchanged attack was re-run after concurrent PRs #27 and #28 at
`5894ac7814d194b3c60d9655af87ef2d9828d56c` and produced the same output.

The first reproduction command used an interpreter without the repository on
`sys.path` and returned `ModuleNotFoundError`. That was an instrument failure,
not evidence about ORION. Re-running the unchanged attack with
`PYTHONPATH=src` produced the system failure above.

## Failure

The battery establishes that a predicate is not mere non-emptiness. It does
not establish that the predicate is an authorized evaluator for this mechanic,
claim type, evidence set, policy epoch or pre-state. The candidate path still
supplies the executable predicate, fixture, lane label and chronology claim.
A digest authenticates weather-file content; it does not make that content
relevant evidence for a P-versus-NP claim.

## Failure class

`CHECK_AUTHORITY_LAUNDERING` + `EVIDENCE_RELEVANCE_NOT_ESTABLISHED` +
`CALLER_DECLARATION_AS_INDEPENDENCE`.

## Correct response

- The host owns the evaluator registry, policy, trust roots, evidence index,
  chronology and signing identity.
- Evaluation is selected by mechanic, dimension, claim schema, evidence role,
  policy/evaluator epoch and pre-state; candidates cannot submit raw
  predicates as authority.
- Execution provenance and assurance are different receipts.
- Promotion requires an assurance receipt bound to the exact subject,
  pre-state, evidence content, evaluator artifact and policy epoch.
- Missing a registered evaluator or relevance check returns `CANNOT_CHECK`.

## General lesson candidate

Rejecting a fixed set of generic negatives proves only local discrimination.
It does not prove semantic validity, relevance, authorization or independence.
A check becomes authoritative through a protected, scope-bound evaluator path,
not because its author can construct examples it classifies correctly.

## Residuals and reopen coordinates

- hostile tests for unrelated-but-authentic evidence and answer-specific checks;
- protection against caller-declared lane and chronology;
- evaluator registry rotation/revocation and stale receipts;
- explicit `CANNOT_CHECK` when no suitable protected evaluator exists.
