# Constitutional revival doctrine V1 — checked protocol

**Protocol id:** `ORION.research-revival.constitutional-doctrine.v1`  
**Status:** `IN_FORCE`  
**Machine check:** `CONSTITUTIONAL_DOCTRINE_V1.json` via `tracker.py`  
**Authority:** process constraint only. Passing the check does not make any child result positive.

This is the executable form of the #284 doctrine. Child lanes must treat it as a gate, not as prose to paraphrase after the fact.

## Checked rules

1. **Never tune an outcome positive.** Frozen margins, baselines, exclusions, gold, evaluators and V1 results stay frozen after outcome access. A later success requires a new immutable protocol.
2. **One-stage attribution.** Localize to the earliest causal stage that a discriminator can separate. Do not repair a later stage while an upstream failure remains total.
3. **Freeze the discriminator before repair.** Competing causes stay live until the discriminator is written. The programme tracker rejects `PROTOCOL_FROZEN` from any state before `DISCRIMINATOR_FROZEN`.
4. **New immutable protocol.** V1 remains history. Repair lives in V2/V3 with bindings frozen before final outcomes.
5. **Preserve negative history.** Null, harmful and `CANNOT_CHECK` runs remain addressable. They are not relabelled PASS.

## Forbidden revival levers

- post-outcome margin relaxation
- weakening a winning baseline
- changing exclusions after seeing results
- converting `CANNOT_CHECK` into zero or PASS
- deleting null/harmful runs
- rewriting V1 in place
- treating sample expansion as a mechanism repair for an upstream near-total failure
- calling implementation novelty scientific novelty

## Allowed revival levers

- new immutable protocol after diagnosis
- fresh holdout after the mechanism is frozen
- stronger baseline as secondary pressure
- shrinking a claim to the tested scope
- terminating as REFUTED

Green tests, a merged PR, or a polished manuscript are not scientific terminals.
