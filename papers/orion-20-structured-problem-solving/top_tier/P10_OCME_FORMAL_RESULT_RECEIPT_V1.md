# ORION-20 OCME formal non-vacuity result receipt V1

**Primary run:** GitHub Actions `32645458392`  
**Two-checker run:** GitHub Actions `32653800366`  
**Latest artifact:** `p10-ocme-formal-v1`, artifact ID `9496899438`  
**Latest artifact ZIP SHA-256:** `8721d02a02b78c6b6f3ee7281f60f106070a462e0c84de821be34ab2dedd91fd`  
**Primary replay:** `P10_OCME_FORMAL_V1_BYTE_REPLAY_GREEN`  
**Independent replay:** `P10_OCME_FORMAL_INDEPENDENT_V1_BYTE_REPLAY_GREEN`  
**Cross-implementation agreement:** `P10_OCME_FORMAL_TWO_IMPLEMENTATIONS_AGREE`  
**Scientific terminal:** `P10_OCME_FORMAL_NONVACUITY_V1_GREEN`  
**Independent verification terminal:** `P10_OCME_FORMAL_SECOND_INDEPENDENT_CHECKER_GREEN`

## Exact content binding

- protocol SHA-256: `8473bd78c083886460221edd6d9526176df1e5f198de7a7eb41c8087343a6b8c`
- frozen cases SHA-256: `d7bcaa6e414847d5aa6aab9aec859f6cdd0106be7baeeb779a10809bf25d154c`
- original canonical primary receipt SHA-256: `4921bffec06687581dbd035668245e3794d1dcb9c731b25cc9e64add688a7896`
- original artifact ZIP SHA-256: `4c597346f4e2044b3a8a67e4c07db526e8e5b5449394d00529cd2dd65737feeb`
- latest two-checker artifact ZIP SHA-256: `8721d02a02b78c6b6f3ee7281f60f106070a462e0c84de821be34ab2dedd91fd`

The second verifier does not import or execute `check_ocme_formal_nonvacuity_v1.py`. It rederives the Boolean and integer closure-membership decisions using different mathematics and implementation structure.

## Results

### Boolean affine setting

The primary checker enumerates exactly all `32` affine Boolean functions over four inputs. Frozen pairwise conjunction targets are outside that closure. The registered `AND2` primitive is itself outside the old closure and exactly verifies the originating conjunction plus three held-out variable-pair conjunctions.

The second checker does **not** enumerate affine truth tables. It computes each frozen Boolean target's GF(2) algebraic normal form and recognizes the affine closure as degree `<= 1`. Every conjunction obstruction has degree `2`; XOR/projection/constant controls have degree `<= 1`; `AND2` is independently certified outside the affine closure.

Frozen XOR/projection/constant controls are `KNOWN_COMPOSITION` in both implementations; false expansion count is `0`.

### Integer affine setting

The primary checker uses an affine candidate from the first two points and nonzero second finite differences to reject shifted-square targets on `{-3,-2,-1,0,1,2,3}`. The registered `SQUARE` primitive, composed with old affine pre-maps, exactly verifies the originating square plus three held-out shifted squares.

The second checker does **not** fit from the first two points or use second differences. It requires exact collinearity of every three-point subset for affine membership. Each shifted square has a non-collinear triple; both frozen affine controls satisfy all-triples collinearity; `SQUARE` is independently certified outside the affine closure.

Frozen affine controls `2*x+3` and `-x+1` are `KNOWN_COMPOSITION` in both implementations; false expansion count is `0`.

## Aggregate

Both implementations agree exactly on:

- exact obstruction-certificate families: `2`;
- outside-closure edit types: `2`;
- frozen held-out transfer targets solved by the same edit families: `6`;
- false expansions on known-method controls: `0`;
- every frozen obstruction identity and every known-method-control identity.

## Scientific disposition

ORION-20 now has an executable **formal OCME non-vacuity object with independent two-implementation verification**. This does **not** establish autonomous method invention: the candidate edits were frozen explicitly before execution and were not discovered by ORION. Nor does it establish donor-complete native theorem-proving superiority.

The broad ORION-20 top-tier gate remains open for generated/non-hand-coded edits, strong native verifier-backed solving, donor-complete search/repair/synthesis/evolutionary comparators at matched resources, qualifying broader verifier-backed settings and immediate submission-day literature saturation.
