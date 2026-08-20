# ORION-RSE host-verification exception V1

**Date:** 2026-08-20  
**Scope:** integration custody only; no scientific claim widening.

## Why this exception exists

The frozen closure packet preferred exact-head GitHub Actions execution. At final closure time, repository Actions were unavailable independently of this branch:

- RSE formal workflow run `32353860983` remained `queued` with its only `verify` job queued;
- the already-merged `main` CI run `32346610492` also remained `queued`;
- multiple unrelated paper/main workflows were likewise queued.

Therefore queued Actions are neither PASS nor FAIL and cannot be used as scientific evidence.

## Equivalent formal verification performed

A second verifier was written that imports **no ORION research module** and reconstructs RSE.T1–T5 directly from their finite mathematical contracts:

`independent_formal_verifier.py`

The exact committed verifier source was independently executed after confirming its Git blob identity:

- verifier source commit: `d71d53af4a9830d2df520797708377f543dee4fe`;
- Git blob SHA-1: `d8fdd7d5d2eeb26580ca343b10c17bcdc6bd5f74`;
- source SHA-256: `2422cd61289a4c5829dc6221bfbbdbb198de61572e57630eaaf1fe79b4db11e6`;
- canonical result SHA-256: `724e91995c3fbfca9ff04974188fcd9c19a1536284c0a82eb477cab9433d1ad7`;
- terminal: `RSE_INDEPENDENT_FORMAL_RECONSTRUCTION_PASS`;
- checks: RSE.T1–RSE.T5 all `true`.

Receipt: `INDEPENDENT_FORMAL_VERIFICATION_V1.json`.

This independently verifies the **formal/mechanic statements**, which is the scientific closure requested by the wave. It does not claim that GitHub Actions executed the research implementation.

## Static integration audit

The branch diff against base `6460410595a14cf9894c9acd450ab2b649a3b858` is additive except the bounded `papers/README.md` synchronization paragraph. It does not modify:

- an existing numerical result artifact;
- an existing claim ledger;
- a protected evaluator or authority implementation;
- runtime `src/orion/` code;
- an existing paper manuscript result section.

Paper-local additions are boundary/handoff files only. Therefore no numerical result or existing publication claim is silently rewritten by this integration.

## Closure authority under the outage

The current research wave may close at its **scientific terminals** because:

1. donor saturation reached its registered fixed point;
2. every derived finite formal/mechanic statement has an explicit disposition;
3. RSE.T1–T5 were independently reconstructed and all passed;
4. the strongest registered state-schema candidate is subtractively closed by the generic justification donor;
5. framework-level constructs that are not theorems are explicitly labelled definitions/design rules;
6. papers P1–P10 are synchronized without widening current claims.

GitHub-hosted implementation CI is recorded separately as:

`CANNOT_CHECK_INFRASTRUCTURE_UNAVAILABLE`.

That status is **not** converted to PASS.

## Automatic reopen rule

If a later GitHub Actions execution of the exact merged RSE sources produces a failing RSE formal-verification job or contradicts the independent receipt, reopen #625/#628/#629 as appropriate and treat this integration exception as superseded by the observed failure.

## Scientific terminals preserved

- #627 — `INTERACTION_ONLY_RESIDUAL_FROZEN`;
- #628 — `DONOR_COMPOSITION_SUFFICIENT`;
- #629 — `FULL_HISTORY_OR_DONOR_STATE_SUFFICIENT`;
- #625 — `DONOR_COMPOSITION_SUFFICIENT`.

No terminal asserts ORION-specific recursive-evolution superiority.
