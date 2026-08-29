# ORION-25 external acquisition disposition v1

**Terminal: `CANNOT_CHECK__NOT_OBTAINABLE_BY_PUBLIC_DATA_ACQUISITION`.**

## Finding

ORION-25 is not blocked on missing public data, so no amount of fetching could
have unblocked it. I am reporting this as `CANNOT_CHECK` rather than partially
filling the directory with data that would look like progress and is not.

`P15A_ACQUISITION_PREFLIGHT_V1.json` records terminal
`P15A_ACQUISITION_BLOCKED_NO_SCIENTIFIC_RESULT`, `execution_authorized: false`,
**0 of 7 required artifacts present**, and
`trusted_protected_input_verifier_configured: false`.

Taking the seven required artifacts one at a time, none is a public dataset:

| artifact | fetchable? | why not |
|---|---|---|
| `programme_paper_issue.json` | no | programme-internal design document; must be authored |
| `donor_matrix.json` | no | programme-internal design document |
| `estimand_and_comparator.json` | no | a protocol decision, not data |
| `protected_fault_injection_corpus.jsonl` | no | protected corpus; the trusted protected-input verifier is not configured, and a public substitute would not be the protected corpus |
| `common_receipt_schema_and_resource_envelope.json` | no | programme-internal schema |
| `independent_evaluator_custody_attestation.json` | **no — structurally** | requires an independent external evaluator to attest custody separation |
| `frozen_terminal_register.json` | no | a freeze artifact, written before outcomes |

The binding one is the evaluator custody attestation. It is a human/institutional
dependency of the same class as ORION-18's institution-disjoint expert authority:
it cannot be manufactured by this or any agent, and substituting a same-team
attestation would be faking closure.

## What I did not do

- Did not fetch a public substitute for the protected corpus. A substitute would
  silently weaken the claim while appearing to satisfy the preflight.
- Did not create a competing protocol. The disposition matrix directs that
  ORION-25's external-trust-domain protocol be rebased/revalidated if chosen, not
  duplicated.
- Did not weaken, reinterpret, or close the existing
  `P15A_ACQUISITION_BLOCKED_NO_SCIENTIFIC_RESULT` terminal. This record agrees with
  it and states why acquisition cannot lift it.
