# Nearest-work saturation — P1 causal responsibility (#278)

**Session:** `cursor/issue-278` on current `main`  
**Constraint:** no arXiv API this session. Primary-source re-read is from the
frozen P1 nearest-work matrix and issue #278's named seeds. CAR is not in that
matrix.

## Search rounds

### Round 1 — named seeds + frozen P1 matrix

Function-only terms: agent failure localization, counterfactual trace
attribution, active diagnosis, value of information, fault isolation,
adaptive testing, causal debugging, change-impact authorization, epistemic
action policy, diagnostic experimental design.

Sources consulted (local, already retrieved for P1 V1 / #137):

- Who&When / Who&When Pro (arXiv:2505.00212 / 2607.09996)
- REFLECT (arXiv:2606.09071)
- AREX, Iris, EviGraph, ARTS, MAST, AgenTracer, TRAIL, AgentErrorBench,
  ErrorProbe, AgentRx, span-level/DRIFT
- #137 substrate: `P1.responsibility-diagnosability.v2` (diagnosability +
  scoped licensing; a probe *can* become decisive evidence)

CAR (arXiv:2606.08275) was named in #278 and is **absent** from
`NEAREST_WORK_MATRIX_V2`. Primary PDF was not fetched (no arXiv API).
Disposition uses the issue's stated mechanism (controlled replay attribution)
and is marked `CANNOT_CHECK` for primary-source confirmation.

### Round 2 — parent-discipline vocabulary

Same axes, different words: change-impact analysis, VoI experimental design,
fault isolation in diagnosis, adaptive testing, epistemic-action policies.
No additional local document changed one of: responsibility representation;
discriminator/probe selection; intervention update; authority/licensing
semantics; dependency-scoped reopening. Stop rule met for *this session's
local corpus*. A later arXiv/PDF pass is a reopen trigger, not a silent close.

## Dispositions

| mechanism | disposition | residual vs #278 |
|---|---|---|
| Who&When Pro | COMPOSE | agent/step label; no typed authority over W/M |
| REFLECT | ADAPT | intervention-supported attribution for silent failures; no permission layer |
| CAR (replay) | ADAPT | controlled replay as discriminator; primary PDF `CANNOT_CHECK` this session |
| AREX | COMPOSE | V1 baseline; recursive audit is not a license |
| Iris | COMPOSE | information-state revision; descriptive, not an authority gate |
| EviGraph | COMPOSE | P1.D3 already struck; dependency reopen is published |
| ARTS | COMPOSE | implementation-fault vs bad-hypothesis split; still a label |
| MAST / TRAIL / AgenTracer / cluster | COMPOSE | taxonomies and replay; descriptive labels |
| #137 diagnosability + licensing | ADOPT (substrate) | keep; residual is intervention-backed authority + UNRESOLVED as a class + H-R discriminators + cause-confusable holdout |
| one-shot LLM classifier | REJECT as sufficient | V1 live arm: WRONG_RESPONSIBILITY 16 cases / 80 trials |

## Residual after saturation

No local neighbour couples **intervention-supported causal class** to an
**explicit epistemic-action permission** that fails closed on `UNRESOLVED`.
That composition remains the candidate residual. It is not yet a paper-level
claim: the prospective protocol is frozen with `outcome_accessed: false`.

## Stop / reopen

Stop for protocol freeze. Reopen if a primary-source read of CAR or a new
2026 paper shows the same composition, or if V1 reproduction hashes move.
