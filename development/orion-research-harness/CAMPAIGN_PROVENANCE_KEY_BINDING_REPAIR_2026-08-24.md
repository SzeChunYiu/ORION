# Campaign provenance-key binding repair

Date: 2026-08-24  
Base: `3616f0f1a69b571fcbf85fa3093aa050765c7fc9`  
Status: frozen before implementation  
Authority: harness execution semantics only; no scientific, novelty, publication, or merge authority.

## Observed failure

The native Paper C / C1 campaign issued a Python request through the current campaign runner. The runner bound the request to its issuing cycle with six provenance fields:

`campaign_id`, `phase_id`, `selected_id`, `selected_kind`, `campaign_state_digest`, and `campaign_decision_digest`.

The local executor accepted only the first four as reserved provenance and rejected the latter two:

`ValueError: PYTHON payload has unsupported key(s) ['campaign_decision_digest', 'campaign_state_digest']`

The scientific analyzer and independent generic verifier had completed, but native admission did not run. This is `CANNOT_CHECK` engineering state, not adverse scientific evidence.

## Atomic development question

Can the executor and campaign runner be rebound to one exact provenance vocabulary without weakening fail-closed rejection of genuinely unknown payload keys?

## Recovered mechanics and negative history

- Every request digest covers the complete payload.
- Capability-specific keys that an executor silently ignores are forbidden because they can make a receipt attest to semantics that never ran.
- Campaign provenance is deliberately not interpreted by the process executor; it binds request identity to campaign identity and controller state.
- The campaign runner currently injects all six fields unconditionally.
- Removing the two digests would weaken replay identity. Globally allowing arbitrary extra keys would reopen the silent-ignore failure.

## Saturation and formulation challenge

The bounded search universe is the exact set difference between keys injected by `campaign_runner.run_campaign_cycle` and `_RESERVED_PROVENANCE_KEYS` in `local_tools`. Inspection found exactly two missing fields. The formulation is challenged by both directions:

1. an injected provenance key rejected by the executor blocks every local campaign;
2. a non-provenance unknown key accepted by the executor launders unexecuted semantics.

The repair must satisfy both simultaneously.

## Frozen implementation hypothesis

Add `campaign_state_digest` and `campaign_decision_digest` to the reserved provenance set and no other vocabulary. Add tests that:

1. execute a Python request containing all six provenance keys successfully;
2. continue to reject an adjacent invented provenance-like key;
3. exercise a minimal two-phase native campaign end to end through `run_campaign(..., auto_service_local=True)`;
4. verify the terminal state is saved and loadable;
5. preserve the existing unsupported capability-key rejection tests.

## Reopen triggers

Reopen if the runner injects any field not accepted by the executor, the executor accepts any unregistered non-provenance field, the campaign cannot reach its terminal state, or a single request is executed more than once.

## Positive terminal

`CAMPAIGN_STATE_AND_DECISION_PROVENANCE_KEYS_BOUND__NATIVE_LOCAL_CAMPAIGN_RESTORED`

## Honest alternatives

- `CAMPAIGN_PROVENANCE_VOCABULARY_STILL_DIVERGENT`
- `UNKNOWN_PAYLOAD_KEY_FAIL_CLOSED_REGRESSION`
- `NATIVE_LOCAL_CAMPAIGN_STILL_CANNOT_CHECK`

## Authority boundary

A passing result repairs native local campaign execution and receipt identity only. It says nothing about the truth, novelty, or publication readiness of any scientific claim admitted by a campaign.
