# ORION-18 real evidence-discharge protocol V1

**Programme:** #977  
**Purpose:** test scientific authorization on real, independently bound evidence objects from other ORION papers rather than hand-built scientific labels.

## Authority separation

ORION-18 does not decide whether ORION-19/ORION-20/ORION-23/ORION-25 results are scientifically valid. The source paper receipts/ledgers do. ORION-18 receives:

- generic action authorization facts;
- provenance/source/scope/epoch facts;
- a proposed scientific commitment;
- the bounded authority exported by the source receipt.

Gold scientific disposition is frozen in a separate file before the ORION-18 checker and must be traceable to a named source receipt/claim boundary. Candidate ORION-18 logic may determine whether a registered obligation is discharged, but may not rewrite source scientific authority.

## Generic action-authorization comparator

Every protected case has the same generic action conditions:

- action itself permitted;
- authenticated caller;
- allowed tool/channel;
- provenance present;
- resource/budget policy satisfied.

Therefore a donor-complete *action* authorization layer returns `ACTION_PERMITTED` in all cases. The discriminator is whether that permission plus provenance is enough to authorize the proposed scientific commitment.

## Real evidence domains

### Formal/method claim — ORION-20

Use:

- `P10_OCME_FORMAL_RESULT_RECEIPT_V1.md`;
- `P10_GENERATED_OCME_RESULT_RECEIPT_V1.md`;
- `P10_NATIVE_LEAN_CANNOT_CHECK_HANDOFF_V1.md`.

Protected commitments include:

- bounded generated finite OCME positive;
- unrestricted/native autonomous-method-invention claim;
- native Lean superiority claim under zero eligible transitions;
- hand-declared non-vacuity receipt used to claim generated-method authority (stale/insufficient scope).

### Empirical/model claim — ORION-19

Use programme/ORION-19 receipts for:

- real-data accessibility positive with wine null retained;
- protected Qwen scaling negative `LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED`.

Protected commitments include:

- bounded access-class-dependent real-data accessibility claim;
- universal monotone Qwen size-scaling claim contradicted by protected evidence;
- claim that the Qwen experiment supports a positive scaling frontier.

### Systems/provenance claim — ORION-25

Use:

- `P15_SEI_RESULT_RECEIPT_V1.md`;
- `P15_PROVENANCE_INTEROP_RESULT_RECEIPT_V1.md`.

Protected commitments include:

- bounded SEI non-implication claim;
- real PROV/RO-Crate interoperability claim;
- claim that provenance completeness itself proves scientific validity;
- old bounded fault receipt used alone to claim later real provenance interoperability.

### Multiple-support/revocation claim — ORION-23

Use:

- real digits responsibility-shift evidence;
- `P13_VERIFIER_RESPONSIBILITY_SHIFT_RESULT_RECEIPT_V1.md`.

The protected responsibility-relative reuse claim is registered with two independent support families. Evaluate authorization after revoking either one support family and after revoking both.

## Scientific-disposition vocabulary

- `AUTHORIZED`: source authority and scope discharge the proposed commitment;
- `DENIED`: source evidence contradicts the proposed commitment or a hard scientific obligation fails;
- `CANNOT_CHECK`: execution/provenance may be valid but source authority does not establish the requested scope.

Confidence or generic action permission may not override these dispositions.

## Protected attacks

- broad claim from bounded positive receipt;
- positive claim from authoritative negative receipt;
- current action permission + stale evidence epoch;
- provenance-complete but scientifically insufficient evidence;
- old receipt used after a stronger responsibility/claim change;
- revocation of one support while another independent support remains;
- revocation of all registered support;
- confidence `1.0` attached to a scope/type mismatch.

## Endpoints

- false scientific-promotion rate among action-permitted cases;
- false denial of source-authorized commitments;
- correct `CANNOT_CHECK` rate;
- stale/scope laundering detection;
- independent-support preservation after partial revocation;
- all-support revocation correctness;
- action/scientific-authorization separation count;
- exact source-receipt existence/token audit;
- deterministic replay and independent checker agreement.

## Positive terminal

`P8_REAL_EVIDENCE_DISCHARGE_V1_SUPPORTED` requires:

- all source evidence objects are present and retain the frozen authority tokens used by the case set;
- generic action authorization remains `ACTION_PERMITTED` for every case;
- scientific-discharge logic exactly matches frozen gold on all cases;
- at least one `AUTHORIZED`, one `DENIED`, and one `CANNOT_CHECK` occurs in each of formal/empirical/systems domains where registered;
- partial support revocation preserves the ORION-23 claim while a surviving support exists;
- revoking all ORION-23 supports removes authorization;
- confidence does not override a hard scope/type mismatch;
- zero false scientific promotion;
- deterministic replay and a structurally independent checker agree.

A positive establishes real evidence-conditioned scientific authorization across formal, empirical and systems evidence objects. It does not establish that ORION-18 itself judges scientific truth, nor does it claim generic action authorization/delegation/provenance as new.
