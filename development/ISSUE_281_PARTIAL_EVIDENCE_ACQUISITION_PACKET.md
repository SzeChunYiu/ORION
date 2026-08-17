# Issue #281 partial-evidence acquisition packet — 2026-08-17

Task: GitHub issue #281. Impact: HIGH (new prospective protocol over frozen P4 V2).  
This packet does **not** authorize coding that edits `P4.protected-authority.v2` or relabels H3.

## Atomic development questions

1. Do frozen P4 V2 artifacts independently re-derive H1 PASS, H2 PASS, and H3 NOT_SUPPORTED (`0/360` vs `180/360`, `60/60`, `30/30`) without relabeling H3?
2. Can a new protocol `P4.partial-evidence-acquisition.v2` freeze case families, gold, action registry, cost envelope and margins while `outcome_accessed=false`?
3. Can #140's planner be used as substrate so that only custody-admissible actions that discharge a real defeater are selected, while planner output remains `authority_terminal=NONE`?
4. Can authority be re-evaluated only from new evidence under the existing hard-gate lattice, stopping in AUTHORIZE / BLOCK / CANNOT_CHECK?
5. Do hostile controls hold: unprotected action cannot discharge a protected defeater; planner output does not authorize; no valid action => CANNOT_CHECK; candidate cannot modify the action registry?
6. If the protected host/evaluator is unavailable, is the campaign terminal `CANNOT_CHECK` without touching frozen P4 V2 readiness?

## Bounded saturation assessment

Knowledge boundary: frozen P4 V2 readiness/bindings/metrics, #140 defeater planner, P4 threat model, and the 2026-08-17 function-only literature seed. Search-universe boundary: repository implementation plus the disposition matrix in `research/p4-partial-evidence-acquisition-v2/LITERATURE_SATURATION_V2.md`. Formulation boundary: no edit to `P4.protected-authority.v2`; no conversion of the H3 null into a win.

Two consecutive literature rounds added no mechanism-changing defeater, custody, cost, or authority rule. The implementation hypothesis is bounded closed for scaffolding plus hostile tests. Fresh protected-split execution remains `CANNOT_CHECK` until an independent host exists.

## Saturation-basis challenge

Saturation could be false if retrieve-or-verify already selected the same next check without custody, if a cheap unprotected action were treated as discharging a protected defeater, if planner GATHER_EVIDENCE were copied into AUTHORIZE, or if missing protected actions were scored as BLOCK/AUTHORIZE instead of CANNOT_CHECK.

Potentially missing parent domains: value-of-information decision theory under adversarial evaluators, confidential-benchmark action registries, and assurance-case evidence collection.

Prior-miss hypotheses: P4 V2 H3 looked like an abstention failure rather than an easy-saturation ceiling; #140 proved planner/authority separation locally but did not freeze a partial-evidence benchmark.

## Reopen triggers

- any frozen P4 V2 artifact hash changes, or H3 is relabeled;
- planner output can construct AUTHORIZE;
- an unprotected/self-authored action discharges a protected defeater;
- the candidate can mutate the action registry digest;
- a campaign result is written while `outcome_accessed` is still false and no protected host exists.

## Frozen implementation hypothesis

Additive files only. Independently re-derive H1/H2/H3 into a hashed receipt. Freeze `P4.partial-evidence-acquisition.v2` before outcomes. Wrap #140 planning with a custody-filtered action registry and re-evaluate authority from new evidence via production hard gates. Land hostile tests. Record campaign `CANNOT_CHECK` when no protected host/evaluator is available. Do not execute or archive a secret-seeded experiment in this change.
