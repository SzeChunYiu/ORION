# P10 OCME formal non-vacuity result receipt V1

**Run:** GitHub Actions `32645458392`  
**Artifact:** `p10-ocme-formal-v1`, artifact ID `9494736360`  
**Artifact ZIP SHA-256:** `4c597346f4e2044b3a8a67e4c07db526e8e5b5449394d00529cd2dd65737feeb`  
**Replay:** `P10_OCME_FORMAL_V1_BYTE_REPLAY_GREEN`  
**Terminal:** `P10_OCME_FORMAL_NONVACUITY_V1_GREEN`

## Exact content binding

- protocol SHA-256: `8473bd78c083886460221edd6d9526176df1e5f198de7a7eb41c8087343a6b8c`
- frozen cases SHA-256: `d7bcaa6e414847d5aa6aab9aec859f6cdd0106be7baeeb779a10809bf25d154c`
- canonical receipt SHA-256: `4921bffec06687581dbd035668245e3794d1dcb9c731b25cc9e64add688a7896`

## Results

### Boolean affine setting

The old closure contains exactly all `32` affine Boolean functions over four inputs. The frozen pairwise conjunction targets are outside that closure. The registered `AND2` primitive is itself outside the old closure and exactly verifies the originating conjunction plus three held-out variable-pair conjunctions.

Frozen XOR/projection/constant controls were all classified `KNOWN_COMPOSITION`; false expansion count was `0`.

### Integer affine setting

On the frozen verifier domain `{-3,-2,-1,0,1,2,3}`, every shifted-square target had nonzero constant second finite difference `2`, and the exact affine candidate fixed by the first two points failed another point. The registered `SQUARE` primitive is outside the affine closure and, composed with old affine pre-maps, exactly verifies the originating square plus three held-out shifted squares.

Frozen affine controls `2*x+3` and `-x+1` were correctly classified `KNOWN_COMPOSITION`; false expansion count was `0`.

## Aggregate

- exact obstruction-certificate families: `2`;
- independently checked outside-closure edit types: `2`;
- frozen held-out transfer targets solved by the same edit families: `6`;
- false expansions on known-method controls: `0`.

## Scientific disposition

P10 now has an executable **formal OCME non-vacuity** object rather than only a prospective manuscript definition. This does **not** establish autonomous method invention: the candidate edits were frozen explicitly before execution and were not discovered by ORION.

The broad P10 top-tier gate remains open for generated/non-hand-coded edits, strong native verifier-backed solving, donor-complete search/repair/synthesis/evolutionary comparators at matched resources, a second independent implementation and immediate submission-day literature saturation.
