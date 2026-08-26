# Mechanism verdicts — ADOPT / ADAPT / COMPOSE / DEFER / REJECT

Closes the per-mechanism disposition required by issue #99 Step 1. Each row is a
mechanism carried by a parent in the family index of
[`../NEAREST_WORK_AUDIT_2026-08.md`](../NEAREST_WORK_AUDIT_2026-08.md), with what
Paper II does with it and why. Runnability verdicts come from
[`../../protocol/EXTERNAL_ACCESS_AUDIT_V1.json`](../../protocol/EXTERNAL_ACCESS_AUDIT_V1.json);
this file never asserts access facts of its own.

Verdict meanings, fixed here so the labels cannot drift:

- **ADOPT** — used unchanged, including as an evaluation obligation on us.
- **ADAPT** — the mechanism is kept but its contract is changed, and the change
  is the thing under test.
- **COMPOSE** — the mechanism enters only as a component of the residual fibre;
  it is not claimed as a contribution on its own.
- **DEFER** — recognised, out of scope for this paper, with the condition that
  would bring it back in.
- **REJECT** — deliberately not used, with the reason.

## Discovery and retrieval substrate

| mechanism | parent | verdict | disposition |
|---|---|---|---|
| Split of discovery into specific-target (Deep) and open-set (Wide) tasks | AutoResearchBench | **ADOPT** | Task-family split adopted verbatim as the external evaluation shape; ORION does not redefine the task. Official execution is `CANNOT_CHECK` (unpublished paper-search backend), which changes what we can *run*, not what we adopt. |
| Strong lexical retrieval as the reference point, not a straw man | SAGE | **ADOPT** | Becomes a promotion gate: a same-call BM25/keyword baseline runs inside every comparison, and ORION may not be promoted over an untested lexical alternative. This is an obligation on us, so it survives SAGE being unrunnable as a benchmark. |
| SAGE as an executable retrieval benchmark | SAGE | **REJECT** | Struck, not deferred: the 200k-paper corpus is published nowhere, no official evaluator exists, the open-ended weights are never stated, and the gold is public plaintext that a live provider can return verbatim. Nothing here is fixable by waiting. |
| Discovery → selection → organization staging | ResearchArena | **ADAPT** | The staging is kept as far as screening; organization is out of scope because Paper II measures discovery, not synthesis. The stage boundary is retained so a retrieval win cannot be claimed from a screening result. |
| One-pass scientific RAG over a fixed index | OpenScholar | **COMPOSE** | Enters as a required baseline (one-pass RAG), not as a contribution. Its ceiling is exactly what a route-governance claim has to beat. |
| Resource selection and result merging across heterogeneous backends | federated search | **COMPOSE** | Supplies the multi-backend substrate that makes route identity meaningful. Merging is done over content digests rather than result lists, which is a strictness change, not a novelty claim. |
| Query diversification to cover distinct intents | diversification literature | **ADAPT** | Reused as query-derivation identity: diversification usually optimises a result set, here it is evidence about whether two routes are independent capture occasions. |

## Screening, stopping and completeness

| mechanism | parent | verdict | disposition |
|---|---|---|---|
| Retrieval recall and eligibility/screening recall as separate stages | MetaSyn | **ADOPT** | Adopted as a measurement requirement: a retrieval ceiling never stands in for inclusion recall, and the two are reported separately. Judged report metrics need an LLM key, so the *external* MetaSyn run stays `CANNOT_CHECK`; the stage separation is enforced in our own metrics regardless. |
| End-to-end protocol-driven SLR automation | AgentSLR | **REJECT** *(as novelty)* / **COMPOSE** *(as baseline)* | Explicitly not claimed: automating the SLR pipeline is an active, occupied field. It enters only as the strongest protocol-driven baseline where runnable. Its code carries no licence, so a frozen redistributable snapshot is not possible. |
| "Already reviewed" state in technology-assisted review | CAL / TAR | **ADAPT** | Kept, but conditioned: read state is keyed on (work, content digest, extraction schema, frame) rather than a seen/unseen bit, so a changed question reopens a source without pretending it is newly discovered. The adaptation is the thing under test in H4. |
| Statistical stopping against a recall target | SR stopping literature | **ADAPT** | Kept as the shape of a stopping guarantee, but split in two: a route may stop while the task stays open. The parent's binding constraint — a work-reduction number means nothing without a retained-recall guarantee — is adopted unchanged. |
| Capture–recapture estimation of what remains unfound | CMR literature | **ADAPT** | Kept as a diagnostic and inverted in authority: the estimator may refuse, is undefined at zero overlap, reports its most conservative admissible value, and can never certify closure. Adaptive routes are not treated as independent capture occasions. |
| Value-of-patch calculus for when to leave or revisit | information foraging | **COMPOSE** | Enters as the rationale for route switching and legitimate re-reads. No foraging model is fitted; the mechanism informs the control policy, it is not itself evaluated. |
| Expert-versus-AI reference overlap as an evaluation object | physics/astro/cosmology study | **DEFER** | Expert review cases are optional in the protocol and are not in the frozen campaign: they need domain experts we do not have. Returns if expert adjudication becomes available. The study's finding — that expert search is not yet reproduced — is kept as a limitation, not converted into a target. |

## What the verdicts leave as the tested object

Every mechanism above is either adopted as an obligation, composed as a
component, or rejected with a reason. None is claimed as novel. What remains is
the composition — earned route independence, question-conditioned read memory,
typed route-versus-task stopping, fail-closed coverage — evaluated under a
complete denominator against strong simple baselines. That composition is the
only thing Paper II asks the reader to accept as new, and it is stated as a
question under test rather than an expected result.
