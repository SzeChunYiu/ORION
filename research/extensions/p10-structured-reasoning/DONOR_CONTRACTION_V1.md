# P10 donor contraction V1 — before A0 execution

P10's initial `LLM + structured workspace` framing is too broad. Primary-source pressure already assigns the following mechanisms to donors.

| Donor | Mechanism P10 must inherit/credit | Claim struck from P10 | A0 consequence |
|---|---|---|---|
| SymPlanner, arXiv:2505.01479 | policy LM proposes; symbolic state executes/verifies; iterative correction and candidate comparison | `language model + symbolic world improves planning` | exact symbolic feasibility is a first-right-of-refusal control |
| TAPE, OpenReview 2026 | multiple plans -> graph -> external solver; constrained execution and replanning | `plan graph + solver + replan` | graph/search feasibility cannot be ORION novelty |
| Grounded Continuation, arXiv:2605.14175 | explicit claim/evidence dependency graph; retraction/support via symbolic graph walk | `explicit evidence graph prevents stale-premise reasoning` | support/retraction gets its own donor control |
| EoG / Think Locally, Explain Globally, arXiv:2601.17915 | LLM local evidence labeling separated from deterministic traversal/state/belief propagation; ITBench RCA | `separate LLM semantics from graph controller` | fixed-proposal controller study must beat a donor-composed graph control |
| Wu et al., NeurIPS 2024 graph planning | graph learning can improve language-agent planning | `graph structure helps LLM planning` | graph-only is baseline, never novelty |
| GTA / GT Bench, ICLR 2026 submission | representation choice materially affects LLM graph reasoning | `better structural serialization helps graph reasoning` | same-information serialization is mandatory |
| SCOPE, arXiv:2606.22488 | symbolic world can be incomplete and revised from execution feedback | `evolving symbolic world for open-ended planning` | representation repair/revision is donor pressure, not headline novelty |

## Surviving experimental question

The residual is **not** another structured memory or symbolic executor. A0 asks whether, with candidate proposals held identical, there is incremental value in identifying *which epistemic responsibility is active*:

`ACT locally / ACQUIRE EVIDENCE / LOCAL REPAIR / REFRAME REPRESENTATION / remain UNRESOLVED`.

This is deliberately a controller study. It cannot establish an LLM advantage because no LLM is required in A0.

## Promotion discipline

If a donor-composed support + feasibility + history controller matches the ORION responsibility controller, P10's broad structured-control claim is closed as prior-work-sufficient. Live LLM generation must **not** be introduced merely to make the residual reappear.

If A0 leaves a reproducible residual, A1 may freeze a language proposal generator separately and ask whether better/poorer proposal generation changes the already-fixed controller result. That sequencing separates proposal intelligence from control structure.

## Current nonclaims

P10 does not own:

- symbolic planning;
- graph planning;
- evidence dependency/retraction;
- structured memory;
- constrained execution;
- replanning;
- symbolic-world revision;
- LLM/tool decomposition;
- generic abstention or verification.

A P10 paper exists only if a bounded residual survives these donors and translates into verified task value.
