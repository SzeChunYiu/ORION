# P3 V14 provider-native public-reference identity audit

**Terminal:** `P3_V14_PROVIDER_NATIVE_REFERENCE_IDENTITY_CANNOT_CHECK__FROZEN_PAIR_IS_SYNTHETIC_AND_MATCHES_NO_OAEI_BIOML_CASE__NO_PUBLIC_GOLD_ADMITTED__NO_METRICS_OR_COMPARATOR_COMPUTED`

## Result

The V12/V13 pair is not provider-native OAEI or Bio-ML data. It is a frozen local synthetic pair with ontology IRIs `urn:orion:p3:v6:bertmap-smoke:source` and `urn:orion:p3:v6:bertmap-smoke:target` and SHA-256 digests `c347f32626f6c5b3b782b2f6344bca5ac2282a701161d11f1e02a7422fef4d9e` and `16bd34ec22c3d130b94257404fd60a112a3383d16255a67472e0c5e1518c5521`. Its construction receipt explicitly says it contains no truth, gold, or reference.

The admitted OAEI 2004 provider packet is Zenodo record 15827226, DOI `10.5281/zenodo.15827226`, archive `oacontest17.zip`, provider checksum `md5:31676c68912a22622f6ca6d031519df9`, under `CC-BY-4.0` with attribution, DOI citation, and adaptation-notice conditions. The audit checked 21 ontology-member hashes, 19 reference-member hashes, and 21 input inventory units. None matches either frozen ontology hash, and none of the provider receipts contains either frozen ontology IRI. The registry contains no exact Bio-ML version/rights/ontology-hash/reference-hash identity packet.

Therefore V14 admitted no public gold or reference file and did not invent an identity-by-equal-label alignment. Precision, recall, and F1 are `CANNOT_CHECK`; a same-universe frozen comparator is also `CANNOT_CHECK`. The pre-existing OAEI public data remains development evidence, not protected confirmation.

## Preservation

The V13 decoded mapping remains unchanged: 16 rows, SHA-256 `c67ee88d541013f41984b239f9cdeaebdcd81573f2080d8af24c7688207dd0f3`. Raw V12 was recorded unchanged by V13. V14 performed no training, matcher execution, Java execution, downloads, retry, tuning, scientific scoring, or comparator run.

## Efficient successor

Do not spend more compute on this synthetic pair for truth/performance metrics. The shortest valid next gate is a provider-native identity packet binding exact version, rights, both ontology hashes, reference hash, and comparator universe before one prospective matcher run.
