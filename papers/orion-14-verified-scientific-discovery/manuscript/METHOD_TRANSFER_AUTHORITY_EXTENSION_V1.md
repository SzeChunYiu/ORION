# P4 additive manuscript bridge — authority for transferred and machine-generated methods

**Status:** additive extension for #410/#412. The citation-saturated peer-review-ready P4 manuscript/PDF and protected V2 campaign remain immutable historical publication authority. This text is the canonical successor-manuscript bridge; it does not rewrite the existing P4 headline result.

## Authority for transferred and machine-generated methods

A method proposal can be structurally plausible, empirically useful, and even mathematically valid in one setting without earning every scientific claim that researchers may wish to attach to it. P4 therefore extends its non-escalating authority rule from claim/evidence verification to a method-specific coordinate product.

`MethodTransferReceipt.v1` binds the exact target, donor lineage and content digests, the structural signature used to motivate transfer, retained/dropped/modified assumptions, target adaptation steps, predicted effects, reconstruction obligation, visible and protected outcomes, evaluator identity/custody state, novelty-search state and reopen-relevant evidence. Donor IDs and digests remain paired during canonicalization; provenance cannot be reconstructed by independently sorting two lists.

The receipt itself grants no authority. P4 derives independent coordinates:

- **VALIDITY** — does protected evidence support the claimed transformation/result?
- **APPLICABILITY** — are the method's load-bearing assumptions satisfied on this target?
- **TRANSFER** — does donor-to-target adaptation preserve source lineage, assumptions and reconstruction obligations?
- **NOVELTY** — does the bounded prior-art state support the claimed novelty scope?
- **UTILITY** — does the method survive protected evaluation for the declared outcome?
- **ADOPTION** — may Self-ORION incorporate it? P4 never grants this coordinate; it remains P5/host-governance owned.

The coordinates are intentionally non-substitutable. High model confidence or structural similarity cannot grant validity. A useful known donor can be VALID, APPLICABLE, TRANSFER-supported and useful while NOVELTY is blocked by prior art. A mathematically valid method can still fail transfer because its donor assumption was erased. Novelty does not imply correctness, and validity does not imply novelty.

### Worked cases

**Useful known donor.** A transferred method preserves its assumptions, reconstruction and protected result, but the current novelty search identifies prior art. P4 permits the bounded validity/transfer/utility claim while blocking novelty. The prior-art finding does not erase the useful scientific result.

**Structurally similar but assumption-invalid transfer.** A proposed adaptation drops a finite-state assumption required by the donor. Even if visible examples pass, APPLICABILITY and TRANSFER are blocked. The method may later be repaired under a new receipt; the current receipt cannot be averaged into a positive terminal.

**Machine-generated candidate.** A generator proposes an apparently new method and succeeds on visible cases. Without protected evaluator evidence and a current novelty search, VALIDITY/UTILITY/NOVELTY remain `CANNOT_CHECK`. If the generator accessed evaluator feedback, protected validity and utility are blocked rather than rewarded.

## Protected MethodAuthorityBench

The additive extension freezes `method_authority_extension/METHOD_AUTHORITY_BENCH_V1.json`, a closed ten-case synthetic authority world containing valid transfer, assumption deletion, invalid reconstruction, known prior art, known composition mislabeled as a new primitive, genuine closed-world synthetic novelty, visible-success/protected-failure, unavailable novelty authority, evaluator leakage and clean fully supported cases.

The coordinate-product policy is compared with three deliberately diagnostic policies: visible-success promotion, provenance-only promotion, and all-deny refusal. The frozen summary records zero false promotions with full clean promotion coverage for the P4 coordinate product. Visible-success and provenance-only policies promote all seven negative/blocked cases; all-deny avoids false promotion but rejects every clean case. This is a closed-world anti-laundering discriminator, not external evidence that P4 can determine real-world method novelty or scientific importance.

## Nonclaims and ownership

This extension does not claim that P9 learns useful structures or that P10 invents good methods. P2/P7 may discover candidate routes; P3/P6 own structural mapping/equivalence; P8 owns the broader typed cross-capability authority calculus; external novelty review remains required for real novelty claims; P5/host governance owns adoption. The existing protected V2 P4 paper remains exactly as published in its current peer-review-ready package.
