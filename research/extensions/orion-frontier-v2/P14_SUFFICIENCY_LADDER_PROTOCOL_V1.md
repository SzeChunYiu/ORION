# P14 Sufficiency Ladder — Protocol V1

Status: PROSPECTIVE / FROZEN BEFORE P14 OUTCOMES
Frozen: 2026-08-20

## Programme question

When a representation is declared "sufficient," sufficient for **what**? P14 turns that ambiguity into an escalation benchmark.

The same latent world is evaluated at four increasingly demanding rungs:

1. `PREDICT` — predict the next observation/label.
2. `DECIDE` — choose an action maximizing task value.
3. `INTERVENE` — answer counterfactual/interventional queries about alternative actions.
4. `VERIFY_REPAIR` — retain enough state to explain/repair a failed action under an external verifier.

A representation may be certified at one rung and fail at the next. That failure is the object of study, not an implementation bug to be hidden.

## Core metric: sufficiency debt

For representation R certified at rung L, define descriptive sufficiency debt at higher rung H as the protected performance gap between R and the best representation independently certified for H under matched downstream model/search cost.

No single scalar is assumed to summarize all tasks. Report a matrix of rung-to-rung transfer.

## Controlled construction

Build latent states with nested independent coordinates so that each rung has a prospectively known minimal statistic:
- predictive coordinate p;
- decision coordinate a not needed for passive prediction;
- intervention coordinate c needed only to distinguish action-conditioned futures;
- verifier coordinate v needed only to identify/repair invalid transitions.

The generator must mechanically verify the intended conditional-independence/sufficiency relations before model fitting.

Primary hostile controls:
- label shuffle;
- leaked higher-rung coordinate into lower-rung state;
- nuisance coordinate with matched marginal frequency;
- state renaming/permutation;
- counterfactual consistency checks.

## Real-system mappings

### P9
Prediction/decision-like rungs map to relation classification and exact composition/inquiry tasks. A P9-specific rung is allowed only when the mapping is content-bound and not invented after outcomes.

### P10 / Lean
- `PREDICT`: next coarse tactic family;
- `DECIDE`: choose among candidate tactics under a verifier-call cap;
- `INTERVENE`: predict outcome of alternative tactic applications from the same native proof state;
- `VERIFY_REPAIR`: use typed verifier feedback to repair a rejected proof attempt.

Native-state execution is a prerequisite for P10 promotion.

### Agentic coding
- `PREDICT`: next tool/result class;
- `DECIDE`: choose next tool/action;
- `INTERVENE`: estimate consequences of alternate edits/commands;
- `VERIFY_REPAIR`: retain exact evidence needed to repair a failing test/build.

Any public benchmark used here must preserve source/evidence identities and avoid training contamination where measurable.

## Positive terminal

A strong cross-domain terminal `SUFFICIENCY_LADDER_EMPIRICALLY_SEPARATED` requires:
1. at least two prospectively certified lower-rung representations that materially fail a higher rung;
2. higher-rung representations recover that performance under matched or lower downstream compute;
3. at least one real-system domain reproduces a lower-to-higher-rung separation with paired uncertainty excluding zero;
4. all leakage and counterfactual consistency controls pass.

A controlled-only result receives `CONTROLLED_SUFFICIENCY_LADDER_ONLY`.

## Claim boundary

Prior causal/RL theory already establishes that predictive sufficiency need not imply control or counterfactual sufficiency. P14 does not claim that logical distinction as new. The intended contribution is an auditable multi-rung benchmark showing **where state compression fails as agent responsibility escalates**, and connecting that debt to representation/compute allocation.
