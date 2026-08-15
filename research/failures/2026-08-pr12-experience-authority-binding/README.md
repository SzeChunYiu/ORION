# PR 12 experience-authority binding failure

**Status:** preserved negative engineering history; regression guards added.

## Observed failure

Review of the first mechanics/failure-learning substrate found three ways that the implementation was weaker than its stated authority boundary:

1. any successful episode IDs could be supplied as replay/fresh-transfer evidence, even when they came from another mechanic and never executed the candidate guard;
2. a bare `independent_verification=True` flag could conditionally promote a pattern without binding verification to the exact candidate content or exact episodes;
3. repeated identical runtime attempts generated the same deterministic episode ID and collided in the immutable store, so recurrence could be lost instead of learned.

Duplicate episode identities could also masquerade as distinct cross-variation support when constructing a candidate.

## Diagnosis

The initial ORION port preserved the high-level RAKL rule (replay plus fresh transfer) but omitted some of RAKL's content/lineage binding mechanics. The failure class is therefore `AUTHORITY_BINDING_LOST_DURING_MINIMAL_PORT`, with an independent event-identity defect in runtime recording.

## Repair

- candidate patterns require distinct support episode identities;
- assessment requires the exact candidate to be registered in the immutable ledger;
- validation episodes must use the same mechanic and record `guard:<pattern_id>` in their action trace;
- fresh-transfer variations must be outside the candidate's support variations;
- conditional reuse requires a protected receipt bound to the SHA-256 fingerprint of the exact candidate and the exact validation episode set;
- every runtime attempt receives a unique run identity before the episode content hash is formed;
- `CANNOT_CHECK` receipts/episodes must retain a failure signature or residual.

## Remaining boundary

The V0 receipt is a typed external-verifier boundary, not yet a cryptographic attestation system. Live Shadow Self-ORION must keep the verifier outside the candidate/solver path, and governed promotion remains blocked until evaluator identity and evidence-lineage independence are protected mechanically.
