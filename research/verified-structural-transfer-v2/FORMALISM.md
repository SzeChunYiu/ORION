# Verified Structural Transfer V2 formalism

## Content identity

For a canonical JSON normalization `J(x)`, every signature, algorithm cell, evidence envelope and decision receives

\[
D(x)=\mathrm{SHA256}(J(x)).
\]

Mappings are key-sorted; sets are content-sorted; non-finite floats are rejected. A duplicate logical identifier with a different digest is an identity collision and is rejected.

## Transfer receipt

For target problem `P`, candidate algorithm cell `C`, declared assumption evidence `A`, declared falsifier results `F`, and provenance `R`, V2 emits

\[
\rho = (D(P), D(C), D(A,F,R), s, q, m, \Gamma)
\]

where `s` is the V1 fail-closed transfer status, `q` is the structural retrieval score, `m` is the mechanism label and `Γ` is an explicit reason-code vector. The receipt itself is content-addressed. Structural similarity is never an authority field.

Unknown declared evidence is serialized as `null` and yields `CANNOT_CHECK`; false assumptions yield `BLOCKED_ASSUMPTION`; failed falsifiers yield `OBSTRUCTED`.

## Portfolio receipt

A portfolio evaluates **every registered cell**, including those with no evidence. Missing evidence therefore produces an explicit `CANNOT_CHECK` decision rather than silent omission. Candidate order is deterministic by decreasing structural score then cell ID.

Optional cross-confirmation requires at least `k` distinct source domains for the same mechanism. Multiple cells from one source domain cannot satisfy the domain count.

## P1 — diagnosability and scoped licensing

Responsibility probes retain the V1 information-gain mechanic. V2 adds a receipt and an explicit licensing matrix. A requested epistemic action is licensed only if the problem is diagnosable, observed evidence yields posterior mass at or above the frozen threshold, and the best responsibility class explicitly licenses that action. Non-diagnosable or low-confidence states are `CANNOT_CHECK`; a confident but wrong-scope class is `BLOCKED`.

## P2 — replayable conservative allocation

Every route update binds the before/after allocator state digest. A safety-floor rejection must leave the exact before state intact. Censored observations carry no reward and therefore cannot become zero-reward evidence. Receipts declare `ROUTE_ALLOCATION_ONLY` and `can_close_task=false`.

## P3 — typed scientific consistency

Each lens edge is typed as REFERENT, CONSTRUCT, MEASUREMENT, CONTEXT, MODALITY or ATTRIBUTION and binds protected provenance. A cycle may `GLUE` only if all edges have the requested scientific coordinate type, bidirectionality has been validated, provenance anchors exist, validation anchors exist, and cycle error is within tolerance. Otherwise the result is `OBSTRUCTION` or `CANNOT_CHECK`.

## P4 — protected evidence planning

Only evidence actions held by a protected evaluator or independent host and carrying a content digest can enter planning. If a critical defeater exists, selection is restricted to actions that address the critical set; cheap noncritical actions cannot pre-empt it. The receipt vocabulary has no authority terminal: `authority_terminal` is structurally fixed to `NONE`.

## P5 — non-compensatory staged gate

V2 preserves `STATIC -> REPLAY -> FRESH -> PROTECTED` and adds append-only revision history. Any known fail or harm dominates missing earlier stages. `CANNOT_CHECK` blocks. The strongest terminal remains `RECOMMEND_HOST_PROMOTION`; receipts bind `HOST_ONLY_RECOMMENDATION`, never self-promotion.
