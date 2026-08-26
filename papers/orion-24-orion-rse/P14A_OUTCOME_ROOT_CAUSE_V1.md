# P14A Outcome Disposition and Root-Cause Audit V1

**Terminal:** `P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET`  
**Result SHA-256:** `3ac625b799eeb00acee68deecb45ab9ae771b977dbf6303a0795cb80057a28fe`

The protected result is retained as a negative. No P14A threshold, seed, arm, family or outcome is edited.

## What passed

`ORION_RSE_FULL` produced:
- false scientific promotion rate: `0.000000`;
- useful-discovery recall: `1.000000`;
- full disposition accuracy: `1.000000`;
- negative-history/reopen accuracy: `1.000000`;
- matched seven-check decision budget.

Every registered component ablation was worse on at least one scientific decision.

## What failed

The strongest non-ORION baseline was `MULTI_REVIEW`:
- false promotion rate: `0.018375`;
- disposition accuracy: `0.981625`;
- useful-discovery recall: `1.000000`;
- history/reopen accuracy: `0.5050505`.

Therefore two preregistered aggregate gates failed:
- strongest baseline false promotion `>=0.05`;
- ORION-RSE accuracy gain `>=0.08`.

## Root cause

After evidence-integrity, protocol-freeze, identifiability, donor and interaction filters, the only remaining distinction between `MULTI_REVIEW` and `ORION_RSE_FULL` is live negative/subsumed history with no material new evidence. The independent Bernoulli mixture made that *effective protected discriminator* only `0.018375` of all cases. Consequently the maximum possible aggregate accuracy gap against this strongest baseline in the realized benchmark was also `0.018375`.

The failure is therefore a **benchmark-discriminator prevalence problem**: an aggregate random mixture can give an important scientific failure mode too little protected weight to evaluate a paper-level superiority threshold. It is not evidence that the full contract and `MULTI_REVIEW` made the same decisions; their history/reopen accuracy was `1.0` versus `0.5050505`.

## Independent successor rule

P14B will not change P14A's failed thresholds. It asks a more direct question with a new protocol identity: does each governance component discriminate correctly when protected evaluation is stratified by scientific disposition rather than left to incidental mixture prevalence?

The successor must:
- use a fresh seed;
- balance protected strata prospectively;
- preserve matched information and decision budget;
- include both `RETAIN_NEGATIVE` and legitimate material reopening;
- retain all P14A results verbatim.
