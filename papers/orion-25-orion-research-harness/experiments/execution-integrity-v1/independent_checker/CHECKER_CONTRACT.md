# Independent checker contract — execution-integrity V1

**Status:** `CONTRACT_ONLY_NO_IMPLEMENTATION_NO_RESULT`
**scientific_authority_delta:** `NONE`

This directory contains a contract. It contains **no checker implementation and no
checker output**. No green exists and none may be inferred. An implementation
written later must satisfy every clause below before any `RESULT.json` in this
programme is admissible.

## C1. Independence

The checker must not import, subclass, or copy logic from the composer or from
`run_attestation_composition_v2.py`. It re-derives every endpoint from emitted
artifacts alone. Sharing a helper module with the runner voids the independence
terminal.

## C2. Constants from manifest, never from prose

GENESIS preimage and key-seed prefix are read from
`../SOURCE_MANIFEST.json.cryptographic_constants_of_record`. The checker must fail
closed if that block is absent. Rationale: `../VERIFICATION_NOTES.md` V2 records a
live prose/code divergence in the parent study; a checker that reads prose inherits it.

## C3. Endpoints recomputed, not read

False promotion, false rejection and every overhead measure are recomputed from raw
per-case records. The checker must not accept a summary field emitted by the runner.
Denominators are taken from `../SOURCE_MANIFEST.json.bound_numbers_reused_as_denominators`
(11 valid-workload, 5 gold-AUTHORIZED_SCIENCE, 22 total) so results stay comparable
to the bound study.

## C4. Distinct exit codes

The checker uses the map in `../EXPECTED_TERMINALS.json.exit_code_map`. In
particular `CANNOT_CHECK_HOST_UNAVAILABLE` (3) and
`CANNOT_CHECK_INDEPENDENCE_UNAUDITABLE` (4) are distinct from both pass (0) and
fail (1). Collapsing a CANNOT_CHECK into either is a contract violation.

## C5. No-alarm case asserted

The checker must be validated against a known-clean corpus and assert that it raises
**nothing**, in addition to being validated against known-adverse corpora. A checker
demonstrated only on positives is not accepted: a false positive on first real use
is more costly than a miss, because it gets the checker switched off.

## C6. Trust-domain claims audited, not accepted

For each arm the checker verifies that a domain's private key bytes were generated
on that domain's host and never transmitted, from the emitted evidence. A domain
whose independence cannot be established is counted as **not separated** and yields
exit code 4. It is never resolved toward "independent".

## C7. Adverse findings preserved verbatim

Any `UNDETECTED_FAIL_OPEN`, unfavourable terminal, or CANNOT_CHECK is written
verbatim into the output and appended to
`../../P15_FAILURE_LEDGER_V1.md`. No adverse result may be summarized into a
"missing row", downgraded, or dropped.

## C8. Promotion is impossible

Reaching any terminal in this programme leaves
`../../P15_ACTIVE_CLAIM_AUTHORITY_V3.json` at `promotion_allowed=false`. The checker
emits no promotion and asserts none.
