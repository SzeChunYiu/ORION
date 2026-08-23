# X1-B k=4 / 13-point residual — first frozen-protocol result

Parent: #900.
Protocol freeze: `c7bb81ae64a39cd70f77242d667c2e6b2337dc7a`.
Verifier: `research/domains/orion-rg/x1b_k4_13pt_anchored_scalar.py` committed at `8514cee383576005b8d2cfe9dccb9841b07b2af9`.

## Status

**NEGATIVE RESULT FOR THE ONE-FUNCTIONAL ANCHOR STRATEGY.**

This finding was obtained only after the exact finite test was frozen. It is committed before any downstream reframe. Harness/independent replay is still required before promotion beyond a first exact computation receipt.

## Exact census

The full-multiplicity / full-`GL(3,3)` enumeration gives:

- raw 13-position multiplicity vectors passing the no-short-zero-sum generator: `170352`;
- canonical `GL(3,3)` orbits at that gate: `22`;
- admitted residual orbits with packing number exactly 2: `15`;
- support-size histogram among admitted residuals: support 7 -> `12`, support 8 -> `3`;
- admitted canonical-code digest: `e8af9c90a8a0b3c2ded358c26a5bb23f21793e5b122fd876ca4e41297694c527`.

Closing-anchor counts across the 15 admitted orbits are:

- `0` closing anchors: `6` orbits;
- `4` closing anchors: `3` orbits;
- `8` closing anchors: `2` orbits;
- `14` closing anchors: `1` orbit;
- `16` closing anchors: `1` orbit;
- `20` closing anchors: `2` orbits.

Therefore the frozen target

> every admitted 13-position residual has a closing anchor

is **false**.

## Six exact obstruction orbits

Below each support entry is `element : multiplicity` in `F_3^3`. Every listed orbit:

- has no nonempty zero-sum of size <=3;
- has packing number exactly 2;
- has no pair-compatible anchor whose complement common-RHS system is inconsistent over `F_5`.

### O1 — canonical code 942777

- `(1,1,2):1`
- `(1,2,1):2`
- `(1,2,2):2`
- `(2,0,1):2`
- `(2,0,2):2`
- `(2,2,0):2`
- `(2,2,2):2`

Primitive zero-sum masks: `305`. Pair-compatible anchors: `225`.

### O2 — canonical code 1470123

- `(1,1,2):1`
- `(1,2,1):2`
- `(1,2,2):2`
- `(2,0,0):2`
- `(2,0,1):2`
- `(2,2,0):2`
- `(2,2,2):2`

Primitive zero-sum masks: `293`. Pair-compatible anchors: `201`.

### O3 — canonical code 130007745

- `(1,1,1):1`
- `(1,1,2):1`
- `(1,2,1):1`
- `(1,2,2):2`
- `(2,0,1):2`
- `(2,0,2):2`
- `(2,1,0):2`
- `(2,2,0):2`

Primitive zero-sum masks: `309`. Pair-compatible anchors: `203`.

### O4 — canonical code 130165209

- `(1,1,1):1`
- `(1,1,2):1`
- `(1,2,1):2`
- `(1,2,2):2`
- `(2,0,1):2`
- `(2,0,2):2`
- `(2,1,0):1`
- `(2,2,0):2`

Primitive zero-sum masks: `306`. Pair-compatible anchors: `188`.

### O5 — canonical code 942621

- `(0,2,2):1`
- `(1,1,2):2`
- `(1,2,0):2`
- `(1,2,2):2`
- `(2,0,0):2`
- `(2,1,2):2`
- `(2,2,0):2`

Primitive zero-sum masks: `299`. Pair-compatible anchors: `213`.

### O6 — canonical code 938409

- `(0,2,2):2`
- `(1,1,2):2`
- `(1,2,1):2`
- `(1,2,2):2`
- `(2,0,0):1`
- `(2,0,1):2`
- `(2,1,0):2`

Primitive zero-sum masks: `311`. Pair-compatible anchors: `237`.

## Scientific consequence

The k=4 residual cannot be closed by selecting one residual block `Z`, fixing the other eleven blocks, and using only the single Geroldinger--Yang affine-hyperplane functional supplied by local scalarization.

The six obstruction orbits prove that a **strictly richer state is required**. Candidate successor states include, in increasing strength:

1. simultaneous compatibility of the two residual blocks' local functionals;
2. compatibility across multiple 12-block packings / exchange graph cycles;
3. direct vector-valued missing-sum geometry in `C_5^3` beyond one affine hyperplane;
4. a quotient-side theorem forcing one of the six orbits to be unrealizable as an actual lift from a zero-sum-free C15 sequence.

No widening is selected in this packet; that is a successor decision after donor subtraction.

## Authority boundary

This result refutes only the frozen one-functional anchor strategy. It is not a C15 counterexample and does not weaken the conjectured `D(C_15^3)=43`. The six quotient obstructions may themselves be lift-infeasible once multiple local scalarizations are coupled.
