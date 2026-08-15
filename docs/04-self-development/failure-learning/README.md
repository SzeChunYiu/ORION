# Failure learning

Failures are first-class ORION knowledge.

A failed task is not merely a log line. It produces an immutable episode containing the problem/variation signature, mechanic identity, pre-state, action trace, observations, outcome, failure/residual signature, evidence, post-state and cost.

A provisional episode is

\[
e_t=(p_t,v_t,m_t,x^-_t,a_t,y_t,o_t,\phi_t,r_t,e_t,x^+_t,c_t).
\]

## Cross-variation recurrence

If distinct task variations fail under the same mechanic with a shared structural failure signature, ORION may propose a candidate pattern:

```text
episodes
-> structural matching
-> shared failure coordinates
-> variation boundary
-> candidate causal/diagnostic pattern
-> candidate guard or routing rule
-> falsifier
```

V0 uses deterministic signature matching. A learned model may later replace ranking only after frozen evidence shows benefit.

Repeated failure is evidence of recurrence, not proof of cause. A same-context pattern remains `CANDIDATE`. A guard becomes `VERIFIED_LOCAL` only after a replay episode from the same mechanic records the explicit action `guard:<pattern_id>`. Conditional reuse additionally requires a distinct fresh variation and an independent/protected verification receipt bound to the exact candidate-content hash and exact replay/transfer episode identities. An unrelated successful episode, a caller-supplied boolean, or a certificate bound only to a reused name cannot promote the guard. A failed fresh transfer contradicts or narrows the lesson instead of being averaged away.

Negative episodes are immutable. Promotion creates a new lesson/pattern version; it never rewrites the episodes that motivated it.

Episode event identity is distinct from task/result identity. Repeating the same task, state and variation creates a new immutable episode rather than colliding with the earlier observation; the stable task and variation signatures remain available for structural comparison.

The current receipt is a provider-bound V0 contract, not yet a cryptographic trust root. Live Shadow trials must obtain it outside the candidate/solver path. Protected attestation, evaluator identity and evidence-lineage validation remain open before governed self-promotion.

## Why this matters for Self-ORION

When ORION develops ORION, development failures enter the same experience substrate as target-problem failures. Future mechanic cells can retrieve structurally related failures before choosing a method. This is the operational meaning of: ORION may fail once, but a diagnosed failure should become searchable protection against recurrence.
