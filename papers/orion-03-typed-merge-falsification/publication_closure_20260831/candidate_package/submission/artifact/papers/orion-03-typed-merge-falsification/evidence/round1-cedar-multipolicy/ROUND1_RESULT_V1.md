# ORION-03 Round 1 — Cedar multi-policy result

Exact ORION base: `27ea5e1b04dbed853b7ddba60c8bf736ef087bf5`  
Protocol freeze: `e393958512d9f726f0f39fe02ae22520db647d08`  
Corrected pre-execution runner: `097210a821b4d4f7c76f296d66c2614b8a0dc93f`
Round disposition: **NULL / adverse for the proposed real-domain residual**

## Terminal

```text
D_R11_POLICY_REQUIRES_RICHER_SEMANTICS
```

## Source identity

The selected source is confirmed as the public official
`cedar-policy/cedar-integration-tests` repository at the GitHub-verified commit
`75989795c75d861270ce6cac38ef9d9e5b220a0c`, tree
`3aed7b26a11a3b85bd29a4b2156437be74c33333`. It is Apache-2.0 with Cedar
Contributor NOTICE. All selected bytes are unmodified and content-bound.

The complete handwritten `tests/multi` family was used: five fixtures, five
multi-policy files, every referenced schema/entity object and all 15 requests.
The native engine is Cedar 4.1.0 at the source repository's pinned submodule
commit `bcb8bd93a292b59ae8f1dcf53b9b4176a2d3405d`.

## Exact result

| Gate | Result |
|---|---:|
| native Cedar fixtures | `5/5 PASS` |
| native requests | `15/15 PASS` |
| official allows / denies | `9 / 6` |
| native decision, reason, error and validation agreement | `15/15` |
| flat/native decision agreement | `15/15` by origin-erased response projection |
| typed/native decision agreement | `15/15` |
| nonempty native reason sets retained by typed projection | `13/13` |
| multi-reason sets retained | `2/2` |
| default denies not promoted to policy origins | `2/2` |
| official upstream evidence-authority/licence/retraction fields | `0` |
| independent Rust hostile/safe controls | `8/8 PASS` |
| independent Lean theorems | `4/4 PASS` |

The native engine reproduces every official multi-policy outcome and preserves
policy-level reason IDs. Typed retention does not change an official decision.
More importantly, the corpus has no independently adjudicated upstream evidence
origin, source licence or retraction field. The injected splicing and
retraction controls correctly separate flat and typed construction, but those
labels were added by ORION and cannot authorize a real-domain positive result.

This is why the result is not
`D_R11_REAL_AUTHORITY_PROMOTION_ERROR_PREVENTED`. It is also narrower than
claiming that native Cedar subsumes every possible upstream provenance layer:
the corpus does not represent that layer and therefore cannot adjudicate it.

## Controls and adverse custody

The Rust controls passed for foreign-origin splicing, retraction erasure,
unsupported cycles, a stronger target made from two partial sources,
alternative complete origins, explicit bridge licences, complete single
origins and multiple complete origins. These are mechanism controls only.

The existing real source-bound control remains exactly:

```text
AGENTGATEWAY_RULESETS_ORIGIN_WITNESS_SAFE
```

It is not relabeled as a vulnerability or whole-gateway certification.

The first Rust execution failed before the first fixture was parsed because the
pinned upstream path override accepts an exact file rather than a directory.
That zero-request pre-execution failure is preserved in
`PREEXECUTION_FAILURE_V1.json`; the corrected runner binds every referenced
policy, schema and entity path explicitly without changing the protocol.

## Round accounting and next gate

This is ORION-03 breakthrough Round `1/3`; two scientifically distinct rounds
remain. Round 2 must switch to a different permission-bearing corpus in which
provenance or retraction is native and independently adjudicated before outcome
access. A Cedar mutation, threshold change or retuning does not count as a new
round.

The bounded first-mixing theorem and both safe Agentgateway controls remain
preserved. This result grants no real operational error-prevention,
deployed-vulnerability, whole-system-security, external-independence, novelty,
journal, top-tier, specialist, production-safety or submission authority.
