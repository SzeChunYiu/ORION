# P4.partial-evidence-acquisition.v2 literature saturation

**Date:** 2026-08-17  
**Protocol:** `P4.partial-evidence-acquisition.v2`  
**Does not mutate:** `P4.protected-authority.v2` / `ORION-P4 = PEER_REVIEW_READY`

Stop rule: two consecutive primary-source rounds add no mechanism-changing item to defeater representation, action selection, custody requirement, acquisition cost model, or the non-escalating authority boundary.

Disposition vocabulary: `ADOPT` / `ADAPT` / `COMPOSE` / `DEFER` / `REJECT`.

## Round 1 — P4 nearest work re-read (already absorbed by frozen V2)

| Work | Function | Disposition | Follow-up consequence |
|---|---|---|---|
| FIRE, arXiv:2411.00784 | iterative retrieve-or-verify | `ADOPT` | Matched baseline family. Confidence-triggered search is not an authority grant. |
| ProvenanceGuard, arXiv:2606.18037 | source-aware verification | `ADOPT` | Matched source-aware baseline. Does not select protected next checks. |
| ProvenAI, arXiv:2606.26449 | citation fidelity vs influence | `COMPOSE` | Behavioral-influence defeater already in the P4 lattice; not standalone novelty. |
| AttributionBench, ACL 2024 | multi-source attribution | `ADOPT` | Attribution remains distinct from authority. |
| CLAIM-BENCH, arXiv:2506.08235 | scientific claim-evidence | `ADOPT` | Scientific-evidence baseline; no protected evaluator. |
| RewardHackingAgents, arXiv:2603.11337 | evaluator/holdout tamper | `ADAPT` | Hostile control: candidate cannot modify evaluator/action registry. |
| Search-Time Contamination, arXiv:2606.05241 | search leakage | `ADAPT` | Acquisition actions remain contamination-gated. |
| AgentAbstain, arXiv:2607.10059 | should-act vs should-abstain | `ADAPT` | Positions H3 null as easy-abstention saturation, not generic refusal novelty. |
| SciIntegrity-Bench, arXiv:2605.10246 | honest inability | `ADAPT` | CANNOT_CHECK is the correct terminal when no admissible action exists. |
| DeepSciVerify, arXiv:2605.27710 | evidence escalation | `COMPOSE` | Escalation without protected custody cannot discharge protected defeaters. |

## Round 2 — function-only neighbors for acquisition/planning

| Work | Function | Disposition | Follow-up consequence |
|---|---|---|---|
| HARIS, ACL 2026 long 119 | search-informed reasoning / reasoning-guided search | `DEFER` | Action selection over queries, not protected custody or authority terminals. Baseline pressure only. |
| MERMAID, arXiv:2601.22361 | memory-enhanced retrieve-and-verify | `DEFER` | Persistent evidence memory; no protected evaluator or non-escalating lattice. |
| #140 defeater planner (in-tree) | expected unresolved-risk reduction / cost | `ADAPT` | Substrate only. Planner receipt `authority_terminal` remains `NONE`. |
| Value-of-information / active hypothesis testing | expected risk reduction per cost | `COMPOSE` | Scoring already in the #140 helper; not a new authority rule. |
| Defeasible reasoning / defeaters | unresolved blocker representation | `COMPOSE` | Already the case schema. |
| Selective prediction / abstention | when to stop | `DEFER` | H3 already null under easy abstention; this study tests *next protected check*, not better refusal. |
| Assurance cases / secure evaluation / protected evaluator | custody of evaluator and gold | `ADAPT` | Required host/evaluator; unavailable host => campaign `CANNOT_CHECK`. |
| Cost-sensitive verification | action costs and budgets | `COMPOSE` | Frozen cost envelope and matched budgets. |

Round 2 added **no** change to: defeater schema, admissible-action custody filter, cost envelope, or AUTHORIZE/BLOCK/CANNOT_CHECK lattice. A third round is not required under the stop rule.

## Mechanism-changing residuals (explicitly not claimed as novelty yet)

Protected custody + non-escalating authority semantics can change *which* actions are admissible relative to FIRE-like retrieve-or-verify. That is a prospective discriminator, not an outcome. If a simpler matched baseline later equals the planner under the frozen safety ceiling, novelty is not promoted.

## Reopen triggers

- a system implements protected-custody action selection that itself grants scientific authority;
- a retrieve-or-verify method dominates the frozen action registry without custody;
- protected-host assumptions in the P4 V2 threat model are invalidated.
