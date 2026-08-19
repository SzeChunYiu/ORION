# P9 A2/A4 — explicit inference first-right-of-refusal for D0 mechanic atoms

## Development question

Do the D0 relation-semantics and failure-history mechanic-selection atoms require learned neural mechanics/memory, or are they exhausted by small explicit operations over the already visible typed state?

This tranche is intentionally bounded to the generated D0 families from #473/#481. A positive result closes only those atoms; it does not establish that general scientific mechanic selection is rule-based.

## Atomic questions

1. Can relation worlds be solved from typed relation semantics + candidate declared effects without learned parameters?
2. Can history worlds be solved by excluding a candidate explicitly named in admitted negative history and choosing the remaining admissible candidate?
3. Do weaker views remain non-identifying when the decisive coordinate is absent?
4. Does candidate order affect the explicit selector?
5. Does changing evaluator gold affect the explicit selector?
6. Does reminting all identities/surfaces preserve predictions?
7. Does malformed/ambiguous visible state fail closed rather than guess?

## Frozen payload-only algorithms

### Relation selector

At TYPED/CURRENT/SEMANTIC:
- inspect visible relation types;
- if exactly one of `SUPPORTS` or `DEFEATS` is present as the decisive evidence relation, map it to a required declared candidate effect (`ASSIMILATE_EVIDENCE` or `REOPEN_CLAIM`);
- choose only if exactly one current candidate declares that effect;
- otherwise return `AMBIGUOUS` in the diagnostic API.

At SURFACE/TOPOLOGY, typed relation/effect semantics are absent -> `AMBIGUOUS`.

### Failure-history selector

At SEMANTIC:
- read visible history records;
- collect current candidate ids appearing as failed mechanics;
- if exactly one candidate remains unfailed, choose it;
- if no failure record is present, choose the unique minimum-cost candidate only when cost is visible and uniquely minimal;
- ambiguous/malformed cases -> `AMBIGUOUS`.

At CURRENT or weaker, negative history is absent. On the hostile pair the selector must not pretend to distinguish the negative world from the clean world.

## Pre-outcome expectations

- relation selector should be perfect on TYPED+ and ambiguous on weaker views;
- failure selector should be perfect on SEMANTIC and cannot exceed the exact CURRENT pair ceiling when history is hidden;
- candidate order/gold/surface reminting must not matter.

## Stop rule

If the explicit selectors exhaust the D0 relation/history atoms, A2/A4 do not justify neural mechanics, modular memory, recurrent latent state or sophisticated training **for the final D0 claim**. Richer A2/A4 research remains a successor/P10 question only if the final P9 paper needs it.

## Nonclaims

No universal rule-based scientific reasoning, no authority, no learned mechanism discovery, no claim that negative history is always sufficient, and no claim about natural-science tasks.