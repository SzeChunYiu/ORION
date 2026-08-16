# Candidate answer — ABSORB.EVIDENCE_BIND.v0

**Target dimensions:** MATHEMATICS, VERIFICATION, FAILURE.
**Incumbent evidence:** RAKL `publication/papers/paper-05-verified-discovery-in-mathematics/ASSURANCE_V3_BINDING_ADDENDUM_20260815.md`, `ASSURANCE_V4_CONTENT_IDENTITY_ADDENDUM_20260815.md`, `STRICT_PROMOTION_PATH_ADDENDUM_20260815.md` @ `bd4ce50f`.

## Proposed step-specific contract

**Mathematics — identity is content, and the trust root is explicit.** Every load-bearing actor/procedure/artifact identity on an authority path is a lowercase SHA-256 content digest; human display labels are inadmissible *even when placed in fields named `*_hash`* (the local naming attack). Binding is transitive over the receipt chain: a receipt binds the digests of everything it judged, so changing any judged element invalidates the receipt rather than silently surviving. The digest↔external-world mapping (that a key, person, corpus or file truly corresponds to the bytes) is the **declared trust root**, established by the external acquisition/review process — recursing past it would self-certify exactly what the design refuses to self-certify.

**Verification — the four bindings every evidence-bearing receipt needs.**

1. *Current-proposer binding*: a receipt records the proposer it was issued against; cross-proposer reuse fails closed.
2. *Subject-pair binding*: review binds the digest of the (informal claim, formal statement) pair; changing intent while keeping the formal object requires a new review.
3. *Complete-dossier binding*: a novelty/coverage review binds cutoff, corpus and search routes, fingerprint, manifest and candidate matches; any post-review flip invalidates the receipt.
4. *Independent attestation*: verifier trust binds current proposer, exact source, checker identity/manifest and a separate attestor; self-attestation fails closed.

Refinement is conservative and non-sovereign: a stricter binding layer may narrow what an earlier layer admitted, never promote what it rejected, and even a fully bound record grants no scientific authority by itself — concrete claims still require the external trust roots the digests represent.

**Failure.** Signatures: *naming attack* (label in a hash field reaches the authority path), *receipt reuse* (cross-proposer or post-supersession), *dossier flip* (judged element changed after review while the receipt survives). Falsifier for the binding layer: construct a receipt chain where one judged element's bytes change and the chain still validates — a single such case refutes the binding.

## Known-answer / hostile test candidates

1. Replace an actor digest with `reviewer-B` in a `*_hash` field → rejected on the authority path.
2. Reuse a valid receipt under a different proposer → fails closed.
3. Flip one dossier element post-review → receipt invalid, earlier state addressable.

## Not licensed

Nothing here establishes that any external identity mapping is correct — that remains the explicit trust root — nor that bound records carry novelty/value authority.
