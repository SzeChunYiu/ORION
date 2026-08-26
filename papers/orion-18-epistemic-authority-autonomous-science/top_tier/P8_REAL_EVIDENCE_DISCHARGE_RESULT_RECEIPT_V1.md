# ORION-18 real evidence scientific-discharge result receipt V1

**Run:** GitHub Actions `32659749882` (pull_request, head `2b336d07273d11a99148cceaffa7d1a6d69e650f`, started 2026-08-23T18:58:38Z, conclusion `success`)  
**Artifact:** `p8-real-evidence-discharge-v1`, artifact ID `9498475873`  
**Artifact ZIP SHA-256:** `80bf1eadb9930fbe289415f974f4a1227a4b06425088237227fb3ea1efa60d5a`  
**Primary terminal:** `P8_REAL_EVIDENCE_DISCHARGE_V1_SUPPORTED`  
**Independent terminal:** `P8_REAL_EVIDENCE_DISCHARGE_SECOND_INDEPENDENT_CHECKER_GREEN`  
**Agreement:** primary and second independent checker agree on all `20` gold dispositions (`independent_gold_complete: true`; workflow step `Verify candidate against independent authority` = `success`)

## Exact binding

- protocol SHA-256: `57b9a13904326485bdb6803b535d5799dea4255b75b939fc894544624156c47f`
- frozen cases SHA-256: `128009d7d2e7cce17f59d8bafde9d574dae4fec886ff2074d91f00fd55157d63`
- frozen gold SHA-256: `6186a483d26de39e6c5c2e5039ba70a3b4de0c9a3957405d3faabf4b3ba2a9c0`
- primary receipt SHA-256: `b92d1e5b5d2f113272c80d5f31d50eef3246e5390210a465a3a0d3b84ade10cb`
- independent receipt SHA-256: `ebf72c13afe8f35ada9d27c2aa5ac85d7065cad5cbfde9a6b21dc329c111f167`
- deterministic primary replay: GREEN (workflow step `Verify deterministic replay` = `success`)
- independent implementation agreement: GREEN

The frozen trio above hashes identically at branch head `ecdf7798f8284abb075d207fce4cd2b830a1cd6d`, so this binding remains valid for the current tree.

## Result — real evidence scientific discharge

Across the `20` frozen real-domain cases (`5` per domain: empirical, formal, multiple_support, systems):

| domain | n | accuracy | false promotion |
|---|---|---|---|
| empirical | 5 | 1.0 | 0 |
| formal | 5 | 1.0 | 0 |
| multiple_support | 5 | 1.0 | 0 |
| systems | 5 | 1.0 | 0 |

- `action_scientific_separation_count`: `12` cases where action authorization and scientific-support discharge are explicitly separated;
- independent checker confirms `all_support_revocation_blocks: true` — revoking every support source blocks the dependent action authorization;
- independent checker confirms `partial_revocation_preserves_support: true` — revoking a strict subset of support sources preserves the support carried by the retained sources;
- independent checker confirms `generic_action_authorization_all_permitted: true` on the permitted set;
- independent checker domain counts: empirical `5`, formal `5`, multiple_support `5`, systems `5`; `source_token_audit: GREEN`.

## Scientific disposition

ORION-18 now has a machine-checked, replay-stable, independently corroborated discharge result on frozen real-domain cases: support revocation semantics (full-block, partial-preserve) and action/scientific separation behave exactly as the epistemic-authority calculus specifies, with zero false promotions in all four domains.

This result does **not** establish autonomous scientific authority in the wild, does not constitute external adjudication of ORION-18's calculus, and does not by itself move ORION-18 to `TOP_TIER_SUBMISSION_READY`. External evaluation and manuscript-level claim scoping remain open per the promotion programme (#977).
