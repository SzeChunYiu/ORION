# P2 Zenodo transport V1 binding failure and V2 discriminator

## Retained V1 terminal

`P2_ZENODO_ACTIVE_ACQUISITION_TRANSPORT_CANNOT_CHECK_BINDING`

V1 is preserved byte-for-byte as `RESULT_V1_RETAINED.json` with SHA-256
`775f3a105487cbce22839a90ae7441f8bb0b154ee0bc9b02ed0c53159f06b23b`.
The exact source body and excluded first-row hash passed, but the frozen
eligibility assumptions did not:

- all 25,539 post-incident rows had five tab-separated fields;
- 25,537 used the canonical class literals `include` or `exclude`;
- one row used `excludes` and one had an empty class;
- three canonical `exclude` rows collided with an earlier canonical row under
  the frozen class-free record identity.

Therefore the V1 model arms were not executed.  This is a source-schema failure,
not an adverse model result, and it cannot be relabelled as support.

## New V2 research identity

V2 is a post-schema-repair public-label development successor.  Before any
model outcome was computed, it froze three population-binding changes and no
V1-to-V2 learner-code change. This is not a claim of an unchanged complete
controller between the SYNERGY and Zenodo source families:

1. retain only exact `include` and `exclude` class literals;
2. within a class-free record-identity collision, retain the earliest raw line;
3. require the now-observed structural census exactly: 25,540 total raw lines,
   one incident-excluded first line, two noncanonical-class exclusions, three
   duplicate-identity exclusions, and 25,534 eligible unique records.

These repairs are responsive to V1 and make V2 nonconfirmatory. V2 still asks
the useful discriminator that V1 could not: does a newly fitted active model
using the previously fixed estimator family, hyperparameters and batch-size
rule exceed the registered within-pool baselines after source-specific
representation, identity adaptation and public-label seed selection on this
one physiotherapy screening pool?
