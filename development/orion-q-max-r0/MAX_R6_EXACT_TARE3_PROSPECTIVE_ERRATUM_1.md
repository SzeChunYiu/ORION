# MAX-R6 exact TARE-3 prospective erratum 1

Date: 2026-08-20
Applies before any protected stretched-N2 coefficient outcome.
Authority: pre-outcome execution/integrity clarification only; no R6 or novelty authority.

## E1 — source identity must be observed, not echoed

The prospective gate `source_blob_matches_frozen` must compare the frozen stretched-N2 git-blob identity against an identity recomputed from the source content actually fetched after the pre-access gate opens. A receipt field copied from the configured subject dictionary is not evidence of source identity.

The first fresh-source fetch remains forbidden until every previously frozen pre-access gate passes. Once release is permitted, the fetched source is independently git-blob-hashed and the observed identity is serialized in the receipt. Any mismatch is a negative/integrity failure.

## E2 — matched resources must be derived from witnesses and the selected coefficients

The matched-resource gate may not pass by inserting constants into a candidate-only record and checking those same constants.

For every one of the four prospectively selected triples, the primary receipt must instead:

1. reconstruct the original three target Pauli strings from each of the three serialized representations: exact-joint candidate, `B_CANONICAL_STRONG`, and `B_FRAME_ONLY_STRONG`;
2. require all three reconstructed target triples to equal the source-selected target triple in the same original order;
3. serialize the actual coefficient vector taken from those frozen source term indices and recompute `Lambda_TARE3 = sqrt(3) * ||alpha||_2` from that vector;
4. derive block cardinality from each representation's serialized `R` family;
5. derive the Uanti Pauli-exponential count as `2m-1` from that serialized cardinality, not from a hardcoded gate value;
6. derive control-register width from the serialized control labels and require the three distinct labels to fit exactly the frozen two-bit TARE-3 label space;
7. require the candidate and both comparators to agree exactly on block cardinality, Uanti rotation count, and control-register width, and to share the same source coefficient vector / recomputed TARE normalization.

The prospective support conjunction must include these derived matched-resource checks. A missing witness field, target mismatch, source-coefficient mismatch, or resource-coordinate mismatch is a negative/integrity failure.

## E3 — replay must bind this erratum

The independent replay and the execution workflow must bind this erratum's git-blob identity before protected access. The replay must independently reconstruct the same three target triples and confirm the primary's matched-resource/source-identity predicates; it must not grant R6 from the primary's booleans alone.

No scientific objective coefficient, comparator, selected subject, top-four rule, donor subtraction, novelty rule, evidence budget, or protected-source rule is weakened or changed. The original prospective protocol and exact-DP Errata 1--3 remain controlling.