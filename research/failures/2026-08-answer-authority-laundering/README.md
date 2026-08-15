# Answer authority laundering and incomplete supersession audit

## Observed

At `8813566940e56e8329a08908db2481e246f001f1`, the ordinary suite passed
(`134 passed`), but hostile answer-loop review found that a non-empty waiver
reason could close any mechanic dimension without evidence or protected
authority. One evidence-free waiver per open question changed the observed
program from 1,298 open questions and zero ready mechanics to zero open
questions and 59 ready mechanics with no audit residual.

A second hostile construction combined a valid base-to-tip supersession chain
with a disconnected two-node cycle. The reducer selected the apparent tip,
ignored the disconnected cycle and applied the answer.

Content answers also treated any non-empty `evidence_refs` string as evidence;
the referenced content was neither resolved nor content-bound.

## Failure

The answer reducer conflated three different claims:

1. an LLM or lane proposed text for a dimension;
2. evidence for that proposal was resolvable and immutable;
3. the proposal was authorized to remove provisional status.

The waiver path skipped even the weak presence-only evidence check. The audit
then licensed question-count reduction because it counted applied records
without checking their authority class. Supersession validation counted tips
but did not prove that every record belonged to one acyclic linear chain.

## Failure class

`DECLARATION_AS_AUTHORITY` + `EVIDENCE_IDENTITY_NOT_BOUND` +
`INCOMPLETE_GRAPH_VALIDATION`.

This is false structural closure, not merely malformed input. It can make an
unready mechanics program appear complete and thereby authorize downstream
work that has not demonstrated its prerequisites.

## Correct response

- V0 rejects every answer-loop waiver with `UNAUTHORIZED_WAIVER`; no protected
  waiver attestor exists yet.
- Every content answer binds each evidence reference to the canonical
  `EvidenceRecord` fingerprint and applies only when the host-owned evidence
  index resolves the exact record.
- Applied-answer reports retain the exact `(answer, reference, digest)` binding.
- Supersession validation requires one root, one tip, no branching, no cycle,
  globally unique record IDs and coverage of every record in the group.
- The audit independently rejects waiver-driven closure.

## General lesson candidate

Question-count reduction is workload accounting, not readiness evidence.
Closure is valid only when the exact live answer has resolved content-bound
support and an authority path appropriate to the transition. A graph validator
must prove the property over all nodes; finding one plausible terminal node is
not enough.

## Residuals and reopen coordinates

- A future waiver path requires a protected, subject-bound signed receipt over
  the answer record, mechanic, dimension, scope and evaluator/governance epoch.
- The evidence index must ultimately resolve pinned Git commit plus blob
  identity rather than trusting a path label.
- The step-verification lifecycle must prevent structurally answered cells from
  authorizing execution until scoped conformance is demonstrated.
- Reopen if an answer evidence record changes content, source URI, provenance
  certificates, or supersession lineage.
