# CLAIM_DISPOSITION — execution integrity V1

**Successor ID:** `ORION25.TRUST_DOMAIN_FRONTIER.v1`
**scientific_authority_delta:** `NONE` · **promotion_allowed:** `false`
**State:** `PREREGISTERED_NOT_EXECUTED`

## Disposition of every claim touched by this programme

| Claim | Disposition now | What would change it |
|---|---|---|
| Chained attestation V2 is bound to ORION-25 | **UNCHANGED / BOUND** — `P15_ATTESTATION_COMPOSITION_V2_SUPPORTED`, independent terminal green, RUN2 deterministic replay | nothing here |
| False rejection `0/11` chain-layer, `0/5` disposition-level | **UNCHANGED / BOUND at internal-panel scope** | a production-like campaign could move these; none has run |
| Full key compromise detected `0/6`, false-promotes `6/6` | **UNCHANGED / PRESERVED ADVERSE** | nothing here; this is a frozen honest negative and is not softened |
| Trust-domain threshold law | **HYPOTHESIS_ONLY** — no evidence, no authority | executing this protocol |
| ORION-25 has `d = 1` custody-separated domains at `k = 3` | **READING OF COMMITTED SOURCE**, not a measurement | nothing; it is a source reading, stated as such |
| Production-like host/process fault behaviour | **NOT MEASURED** | executing the fault matrix |
| Overhead of attestation | **NOT MEASURED** | executing the overhead arms |
| Cross-site replay | **NOT PERFORMED**; sites verified reachable | executing the three-site protocol |

## What this programme does not do

It does not promote ORION-25. It does not modify a frozen paper byte. It does not
relabel the preserved adverse key-compromise boundary. It produces no `RESULT.json`,
and the absence of that file is deliberate — a result file here without a
corresponding independent checker run is invalid by construction.

## Standing constraints carried forward

- `P15_INTERNAL_PANEL_EVIDENCE_BINDING_V1.json` caps the evidence class at
  `INTERNAL_UNIT_TEST_EVIDENCE` with `population_inference: false`. Executing this
  protocol would raise scope but not remove the cap on its own.
- Forbidden states from `P15_ACTIVE_CLAIM_AUTHORITY_V3.json` remain forbidden at
  every outcome: `SIGNATURE_PROVES_SCIENTIFIC_TRUTH`, `KEY_CUSTODY_VERIFIED`,
  `UNIVERSAL_EXECUTION_CORRECTNESS`, `PRODUCTION_SCALE_VALIDATED`,
  `SUPERIORITY_SUPPORTED`, `EXTERNAL_VALIDATION_COMPLETE`,
  `TOP_TIER_SUBMISSION_READY`.
- Key custody remains an unregistered premise of the scientific-admission layer at
  every `d`. Raising `d` changes the compromise threshold, not the epistemics of
  admission.

## Open defects queued, not dropped

1. `P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2.md` declares a protocol digest
   that does not verify at the artifact's current path (`VERIFICATION_NOTES.md` V1).
   Correct locator pinned in `SOURCE_MANIFEST.json`; the receipt itself is frozen and
   was not edited.
2. Protocol prose and implementation disagree on the cryptographic
   domain-separation constants after the namespace pass
   (`VERIFICATION_NOTES.md` V2). Bound result unaffected; reproduction from prose
   would fail. Owner action required in the frozen-artifact lane.
