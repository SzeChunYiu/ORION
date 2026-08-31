# ORION-04 one-shot authorization: audit result

Closes the `immediate_safe_actions` item *"audit the one-shot authorization schema for
machine-verifiable presence and scope"* from `TOP_TIER_ATOMIC_GAP_LEDGER_V2`.

This matters more than a normal audit because ORION-04's own `collision_rule` reads: *do
not spend the one-shot or fork a competing encoding until the authority record machinery
is machine-verifiable.* The audit gates a resource that can be spent exactly once.

**Result: `AUDIT_PASS`.** The schema is machine-verifiable and the replay lists agree.
Nothing here authorizes anything.

## What the gate already enforces

`submission_gate.py` (561 lines) implements the verification. All eight required guards
are present, tracked by the gate's own refusal messages rather than a restatement:

| guard | refusal |
|---|---|
| exact field set | `authorization fields are not exact` |
| consumed-key refusal | `authorization reuses a consumed or terminal key` |
| schema pin | `authorization schema mismatch` |
| one-shot status | `authorization status is not a one-shot execution request` |
| subject binding | `authorization subject mismatch` |
| key derivation | `authorization nonduplication key derivation mismatch` |
| malformed key | `authorization nonduplication key is malformed` |
| scope pin | `authorization declared scopes or denominators mismatch` |

It also pins `attempt_limit` to the integer `1` by type as well as value, and binds
`paper_id`, `subject_commit` and `successor_commit`.

## The gap this audit closes

Two independent replay lists existed and **nothing compared them**:

- `CONSUMED_KEYS` in `submission_gate.py` — what the gate refuses
- `forbidden_keys` in `AWAITING_NEW_ONE_SHOT_AUTHORIZATION.json` — what the record tells
  an operator is already spent

They agree today: **3 keys each, zero divergence in either direction**. But nothing kept
them in step. Divergence is a one-way error on a one-shot resource — a key the record
calls spent could still pass the gate, or the record could understate what has been
consumed. This audit makes that invariant checkable.

## Record state, confirmed consistent

| field | value |
|---|---|
| `terminal` | `AWAITING_NEW_ONE_SHOT_AUTHORIZATION` |
| `live_authorization_file_present` | `false` |
| `execution_performed` | `false` |
| `d4_rounds_consumed` | `0` |

No live authorization, nothing executed, no round consumed. The record and the gate tell
the same story.

## Also observed, and not fixed here

`tests/test_batch_and_authority.py` contains 15 tests covering manifests, parsers,
receipts, certificates, SLURM envelopes and dispatch — and **none exercises
`validate_authorization`**, despite the file's name. The verification logic is the least
tested part of the packet that guards its scarcest resource. That is a test-coverage gap
rather than a defect in the gate, and it is recorded rather than silently repaired,
because adding tests to a frozen evidence packet is a separate decision.

## Audit validation

Exercised in both directions, including the no-alarm control:

| case | want | got |
|---|---|---|
| unperturbed | `0` PASS | **0** |
| record drops one `forbidden_key` | `1` FAIL | **1** |
| gate loses its consumed-key guard | `1` FAIL | **1** |
| restored | `0` PASS | **0** |

Tree left clean afterwards. `grants_authority: NONE` — this audits verifiability, not the
D4 claim.
