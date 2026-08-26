# OAuth Token-Splice R9 Replay Protocol

## Frozen files

- `OAUTH_POLICY_SOURCE_REGISTRY_R9.json`
- `OAUTH_TOKEN_SPLICE_CORPUS_R9.json`
- `verify_oauth_token_splicing_r9.py`
- `OAUTH_TOKEN_SPLICE_R9_RESULTS.json`

## Command

```bash
python papers/five-paper-top-tier-r8/D/verify_oauth_token_splicing_r9.py
```

The command uses the standard library only and must reproduce the registered result byte-for-byte.

## Required controls

1. Fourteen corpus cases are evaluated.
2. Typed Horn closure agrees with an independent direct Boolean evaluator on every case.
3. Clean bearer and clean DPoP controls authorize.
4. Same-token fragmented validation authorizes when both records carry an identical coordinate.
5. A read-only token is denied.
6. Every registered cross-token or cross-request splice is denied by the typed evaluator.
7. The typed evaluator has zero false positives and zero false negatives against the frozen fixture.
8. The untyped coordinate-erasure baseline produces the registered nine false positives.

Any mismatch is a nonzero terminal. The verifier may not rewrite the source registry or expected decisions.

## Structurally independent replay

The independent lane must not reuse the Horn worklist, rule constants, or case-construction functions. It should parse the corpus JSON, build an explicit relational or Datalog representation, and derive decisions from the source registry. A useful alternative is Soufflé/Datalog, OPA/Rego, Cedar, or a small SAT encoding.

## Authority ceiling

A local PASS establishes deterministic agreement on the frozen RFC-grounded fixture. It does not establish independent domain validity, deployed vulnerability prevalence, or journal authority.
