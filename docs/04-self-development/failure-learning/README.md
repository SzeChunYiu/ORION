# Failure learning

Failures are first-class ORION knowledge.

A failed task is not merely a log line. It produces an immutable episode containing root/atomic run identity, parent-run identity, evaluation epoch, split, problem/variation signature, mechanic identity, pre-state, exact receipt/action/handoff/metric data, observations, outcome, failure/residual signature, content-bound evidence, provenance, post-state, cost and latency. Runtime trace events carry `MechanicReceipt` objects, so atomic SEARCH/ABSORB/DIAGNOSE/etc. outcomes enter the same experience store as the root solve. Operator/provider exceptions fail closed into receipts instead of escaping without experience; an external process kill or failed persistence device remains a separate durability problem.

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

Repeated failure is evidence of recurrence, not proof of cause. Multiple atomic observations from one root run are not independent recurrence. Candidate construction, registration, receipt minting and assessment all recheck distinct root-run identities and the exact variation manifest; `FailurePatternCandidate` cannot self-assert promoted authority. A same-context pattern remains `CANDIDATE`. A guard becomes `VERIFIED_LOCAL` only after a distinct replay run matches a supporting task/problem/variation and records an actually invoked host-installed action `guard:<pattern_id>`. Fresh run, task, split, evaluation and variation identities plus a protected verification receipt can strengthen that local result, but V0 does not promote any pattern to `CONDITIONALLY_REUSABLE`: unequal in-process lineage hashes establish label inequality, not independent custody. The receipt is Ed25519-verified against a host-pinned public-key trust store and binds the exact candidate hash and complete support/replay/transfer episode contents. An externally rooted separation attestor is required before conditional reuse can be enabled. An unrelated successful episode, caller-supplied independence label, forged receipt, same-ID evidence substitution or unprotected assessment call cannot promote the guard. A failed fresh transfer contradicts or narrows the lesson instead of being averaged away.

Negative episodes are immutable. Promotion creates a new lesson/pattern version; it never rewrites the episodes that motivated it.

Episode event identity is distinct from task/result identity. Repeating the same task, state and variation creates a new immutable episode rather than colliding with the earlier observation; the stable task and variation signatures remain available for structural comparison.

The general assessment path has no trust-store parameter and cannot promote beyond `VERIFIED_LOCAL`. Only a host-owned `ProtectedPatternReuseAssessor`, constructed outside candidate/solver control, can resolve a receipt against pinned Ed25519 public keys. Signing keys never enter assessment. Deployment key custody, rotation, protected-assessor isolation, exact build-artifact hashing, external evaluator operation, crash-consistent persistence and live hostile trials remain open before governed self-promotion.

## Why this matters for Self-ORION

When ORION develops ORION, development failures enter the same experience substrate as target-problem failures. Future mechanic cells can retrieve structurally related failures before choosing a method. This is the operational meaning of: ORION may fail once, but a diagnosed failure should become searchable protection against recurrence.
