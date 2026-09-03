# A4 intervention-menu design — DRAFT V1 (NOT FROZEN)

> **DRAFT — NOT A FROZEN PROTOCOL.** Nothing here is preregistered; no
> threshold, menu item, or partition use is binding until a successor
> `A4_INTERVENTION_PREREG_V1.json` is committed with all DRAFT-DECISION rows
> resolved and every value frozen BEFORE any primary/replication-partition
> agent run. Freezing is deliberately deferred to an attended session:
> freezes are one-shot, and three base-context facts below must be pinned
> from gym code first.

**Substrate:** SciAgentGym at `e9dbbea43` (PREFLIGHT_V2 + scoring/partition
freeze in this directory). **Unit:** base task; variants inherit partitions.
**Denominator rule (frozen upstream by #49 A4):** only tasks that FAIL
`strict_success` (deterministic scorer) under the frozen BASE condition enter
the diagnosis denominator.

## Base condition (to freeze)

Gym as shipped per task: registered `usage_tool_protocol` tools, `--test-type
refine`, `--text-only`, study model lane, 1 run/cell, rounds cap = the gym's
default max-rounds constant (**DRAFT-DECISION-1: pin the exact constant and
its code location from `gym/` before freezing**).

## Intervention menu (one coordinate per intervention; drafts)

| coordinate | operationalization (draft) | invariant held |
|---|---|---|
| `INFORMATION` | expose ONE benchmark-provided item absent from the base context (**DRAFT-DECISION-2: inventory exactly what the base prompt includes — if `metadata.domain_knowledge` is already served in base, the information item must instead be a withheld `local_db` row/tool doc; pin from `gym/core` prompt-assembly code**) | model, representation, rounds cap fixed |
| `ACCESSIBILITY` | semantic-preserving access-path change: registered tool renamed to its documented alias + DB table flattened to CSV with identical bytes of content (**DRAFT-DECISION-3: pick ONE mechanism and freeze its exact transform script**) | information bytes, model, rounds fixed |
| `COMPUTATION` | rounds cap x2 (registered budget increase, nothing else) | information, representation fixed |
| `RECONSTRUCTION` | one registered replan: context cleared, task re-served fresh with the same remaining budget | information, representation, total rounds fixed |

## Arms (draft, per the #49 A4 gate text)

Candidate diagnosis policy (reads pre-outcome failure evidence from the base
trace only — no gold, no intervention outcomes) vs fixed policies:
`ALWAYS_INFORMATION`, `ALWAYS_ACCESSIBILITY`, `COMPUTE_FIRST`,
`CHEAPEST_FIRST`, plus the hindsight oracle for regret analysis only (never a
comparator). Strongest fixed policy selected on the development partition
before primary outcomes.

## Frozen gate (already fixed by #49/#2057 — restated, not draftable)

Candidate final-success gain >=5pp over the strongest fixed policy with
paired 95% bootstrap lower bound >0; mean charged regret <=0.5x strongest
fixed; false-compute escalation below COMPUTE_FIRST; positive direction in
>=3/4 domains; source-disjoint replication same direction; any leakage
violation -> `LEAKAGE_INVALID`. Failure publishes the boundary/null; no
post-hoc cause-class redefinition.

## Freezing checklist (the attended session's to-do)

1. Resolve DRAFT-DECISION-1..3 by reading the pinned gym code (rounds
   constant, base prompt inventory, one accessibility transform).
2. Instantiate the candidate diagnosis policy's readable surface (base-trace
   features only) and freeze its functional form + any thresholds fit on the
   development partition alone.
3. Commit `A4_INTERVENTION_PREREG_V1.json` with all values, dev-partition
   calibration receipts, and every execution flag false — then, and only
   then, primary runs.
