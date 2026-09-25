# ORION-25 external native trust-domain protocol

**Identity:** `ORION25.EXTERNAL_NATIVE_TRUST_DOMAINS.v1`
**State:** `PROTOCOL_FROZEN__EXECUTION_NOT_RUN`
**Outcome access:** none under this identity

## Question

Do native trust systems preserve the synthetic ORION-25 law's core prediction—that
acceptance safety depends on independent trust-domain evidence rather than the count of
cryptographic objects—under their own real verification semantics?

This protocol does not test whether ORION invented signatures, threshold roles,
delegation or supply-chain provenance. It tests a bounded cross-system prediction.

## Immutable systems

The exact tag objects, peeled source commits and artifact digests are in
`EXTERNAL_SYSTEM_PINS.json`.

- cosign `v3.1.3`;
- python-tuf `v7.0.0`; and
- in-toto `v3.1.0`.

A minimum of two systems must complete. Failure to install or express a registered case
is `CANNOT_CHECK`, not permission to substitute a later version or easier case.

## Native case families

Each system receives a frozen fixture family wherever its native semantics make the case
well-defined:

1. valid native artifact and policy;
2. content corruption after signing/metadata creation;
3. benign re-encoding only when the native format defines semantic equivalence;
4. compromise or forgery within one trust domain;
5. threshold or multiple-domain evidence satisfying the native policy;
6. stale, expired, revoked or rollback material;
7. wrong identity, role, delegation or authority.

A case that the system cannot represent remains visibly absent from that system's
denominator and is reported `CANNOT_CHECK`. It is never silently mapped to a nearby case.

## Arms

- native verifier and native policy;
- flat single-signature acceptance;
- provenance-blind key/value merge;
- direct frozen-case oracle as a diagnostic ceiling; and
- the existing ORION-25 synthetic law as a prior prediction, not fresh evidence.

## Gold and measurements

Gold is the frozen native-policy expectation plus the native verifier's objective
exit/status output. Every fixture, policy, command, environment, stdout/stderr digest and
exit code must be retained. An independent checker replays the fixtures without importing
the fixture generator.

Primary endpoints are false promotion, false rejection and agreement with the frozen
native-policy disposition. Runtime, bytes and number of operators/custodians are secondary.

## Authority separation

Cryptographic independence, process separation, operator separation, organizational
custody and external-investigator authority are separate fields. None is inferred from
another. Same-team keys, bots, repositories or agents do not establish organizational
independence.

The strongest possible scientific terminal is unavailable until independent custody is
proven by evidence that the candidate team cannot mint or edit unilaterally.

## Stop rule

Stop after all frozen cases for at least two systems have one native execution and one
independent replay. Unavailable cases remain `CANNOT_CHECK`; no post-outcome replacement,
version update, threshold change or case remint is allowed under this identity.
