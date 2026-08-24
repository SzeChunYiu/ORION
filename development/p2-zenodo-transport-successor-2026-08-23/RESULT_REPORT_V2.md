# P2 Zenodo 10423427 transport V2 result

## Frozen terminal

`P2_ZENODO_ACTIVE_ACQUISITION_TRANSPORT_V2_SUPPORTED_ON_ONE_PUBLIC_PHYSIOTHERAPY_POOL`

All five declared V2 gates passed in the producing lane on the frozen
post-schema-repair population of 25,534
unique canonical records: 2,259 `include` and 23,275 `exclude`.  The exact
53,881,052-byte CC BY 4.0 source body, MD5, excluded incident-row hash, raw-line
census, two noncanonical-class exclusions, and three duplicate-identity
exclusions all matched the V2 freeze.

## Estimator-family reuse with source-specific re-instantiation

At 10% screened, `ACTIVE_LOGREG` recall was **0.703409**. The better-performing
of the two registered within-pool baselines was `STATIC_SEED_CENTROID` at
**0.335989**; the paired one-pool
difference was **+0.367419**.  The 20-permutation random mean was **0.102789**.

| Arm | Recall @ 5% | Recall @ 10% | Recall @ 20% | Fraction screened for 95% recall | WSS@95 |
|---|---:|---:|---:|---:|---:|
| ACTIVE_LOGREG | 0.406375 | 0.703409 | 0.945994 | 0.205256 | 0.744744 |
| STATIC_SEED_CENTROID | 0.177512 | 0.335989 | 0.560425 | 0.676941 | 0.273059 |
| RANDOM, 20-seed mean | 0.051439 | 0.102789 | 0.201239 | 0.950305 | -0.000305 |

Thus a newly fitted active SGD model using the previously fixed estimator
family, hyperparameters and batch-size rule produced a large conditional
contrast on this pool after the representation and identity adapter were
re-instantiated for its title--abstract--MeSH records. All arms used a
label-informed warm start selected by scanning the complete public labels for
one known inclusion and one known exclusion, so this does not measure
cold-start screening. From the unrounded receipt values, the observed estimand
is the within-pool difference
$\Delta_{10}(P,z)=0.7034085878707392-0.33598937583001326
=0.367419212040726$, conditional on this repaired pool and disclosed seed
rule. It is not a population-average transport effect.

## Identity and claim boundary

V1 remains the retained terminal
`P2_ZENODO_ACTIVE_ACQUISITION_TRANSPORT_CANNOT_CHECK_BINDING`; it was not
rewritten or counted as a model failure.  V2 was opened only after diagnosing
V1's two noncanonical class literals and three identity collisions.  Therefore
V2 is post-schema-repair public-label development, not outcome-blind
confirmation.

This one-pool result does **not** establish multi-world replication,
source-disjoint inferential generality, protected labels, independent custody,
ORION-specific superiority, open-world route invention, or task closure.  No
cross-world p-value is admissible.  The next publication-grade discriminator is
an externally frozen multi-review family from a source disjoint from both
SYNERGY and Zenodo 10423427, with a stronger modern screening comparator and
custodied labels.

## Machine-readable evidence

- `RESULT_V1_RETAINED.json` SHA-256:
  `775f3a105487cbce22839a90ae7441f8bb0b154ee0bc9b02ed0c53159f06b23b`
- `PROTOCOL_FREEZE_V2.json` SHA-256:
  `b564c9546def95db55ca0c2733d32198112241669e5c0917d48bb878ede27efb`
- `IMPLEMENTATION_FREEZE_V2.json` SHA-256:
  `174a475fd820505fd5bc2a6d8cc946b612294901bfceb6c121a23b9a7ef55b6c`
- `RESULT_V2.json` SHA-256:
  `60c050a0bb1580c279d80ac365a80c9122de25fa0c796190ab897f2ed8119b3b`

The producing lane reports that a second execution produced a byte-identical
result with the same SHA-256. No separate replay receipt is archived. This is
not independent verification or scientific replication.
