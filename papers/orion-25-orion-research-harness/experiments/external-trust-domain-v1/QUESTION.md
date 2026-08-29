# ORION-25 external trust-domain successor

## Scientific question

Across two structurally different production verification stacks, does requiring
independently custodied approvals prevent false promotion after compromise of one
trust domain without causing false rejection of registered benign input
re-encodings, and where do the systems fail under multi-domain compromise,
stale/replay, revocation, and process-liveness faults?

## Systems

1. A dual-identity Sigstore/cosign policy using native cosign bundle
   verification.
2. A threshold TUF repository combined with an in-toto layout, using native
   python-tuf and in-toto verification paths.

## Prospective boundary

This commit freezes software, corpus, attack families, baselines, metrics,
terminals, and the external-custody acquisition contract. It contains no
outcomes. Execution is blocked until exact public keys, OIDC identities,
repositories, workflow references, role assignments, and custodian evidence are
committed in a separate identity-binding addendum. Merely naming two domains or
generating all keys under one operator is inadmissible.
