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

Repeated failure is evidence of recurrence, not proof of cause. A same-context pattern remains `CANDIDATE`. A guard becomes `VERIFIED_LOCAL` only after replay. Conditional reuse additionally requires successful fresh transfer plus independent/protected verification. A failed fresh transfer contradicts or narrows the lesson instead of being averaged away.

Negative episodes are immutable. Promotion creates a new lesson/pattern version; it never rewrites the episodes that motivated it.

## Why this matters for Self-ORION

When ORION develops ORION, development failures enter the same experience substrate as target-problem failures. Future mechanic cells can retrieve structurally related failures before choosing a method. This is the operational meaning of: ORION may fail once, but a diagnosed failure should become searchable protection against recurrence.
