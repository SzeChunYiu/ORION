# X1-B k=4 — global bilinear discriminator, linear-stage result

Parent: #900.
Prospective protocol freeze: `d962a865fb6e371b3e58e9044da71027b1954bc1`.
Verifier: `research/domains/orion-rg/x1b_k4_global_bilinear_linear_stage.py`.

## Status

**PROSPECTIVE POSITIVE PARTIAL RESULT.**

The global common-bilinear-form condition eliminates four of the six surviving quotient obstruction orbits **before** the rank<=3 condition is imposed.

This result is committed before minimum-rank analysis of the final two affine-consistent orbits.

## Exact affine systems

For each quotient orbit, a symmetric `13x13` matrix B over `F_5` has 91 upper-triangular variables. Every disjoint quotient-zero-sum pair `(Z,W)` contributes

`sum_{j in Z,k in W} B[j,k] = 1`.

Primitive replay gives:

| canonical code | zero-sum masks | disjoint-pair edges | equation rank | affine status | affine dimension |
|---|---:|---:|---:|---|---:|
| `942777` | 305 | 860 | 77 | CONSISTENT | 14 |
| `1470123` | 293 | 800 | 76 | CONSISTENT | 15 |
| `130007745` | 309 | 577 | 78 | **INCONSISTENT** | — |
| `130165209` | 306 | 625 | 78 | **INCONSISTENT** | — |
| `942621` | 299 | 830 | 77 | **INCONSISTENT** | — |
| `938409` | 311 | 890 | 78 | **INCONSISTENT** | — |

Summary digest of these six rows:

`9e08a876608595fba2c8999a8150f4dffddbae1c3bbcc26ebd34e42621f29f36`.

## Mathematical consequence

The four inconsistent orbits cannot admit **any** symmetric bilinear position matrix satisfying the necessary extension equations. In particular they cannot admit a rank<=3 matrix coming from residual kernel vectors in `C_5^3`.

Therefore these four quotient residuals are rigorously eliminated from any hypothetical C15 counterexample, conditional only on the already committed global two-extension theorem.

No catalecticant or detailed maximal-kernel classification is needed for these four eliminations.

## Live residual frontier

Only two of the original six k=4 quotient obstructions remain:

### R1 — `942777`

- affine dimension: 14;
- exact remaining question: does the affine space contain a symmetric matrix of rank <=3?

### R2 — `1470123`

- affine dimension: 15;
- exact remaining question: does the affine space contain a symmetric matrix of rank <=3?

The frozen protocol's full affine enumeration cap is `5^10`, so neither space may be exhaustively enumerated by its complete parameter cube. The next step must use exact minimum-rank algebra / branch-and-bound / finite-field polynomial solving, preserving `CANNOT_CHECK_RESOURCE_BOUND` if not closed.

## Scientific significance

The sequence of refutations now isolates why the global invariant matters:

- single deletion hyperplane: insufficient (six obstructions survive);
- two exact cofactors for one packing: insufficient (constructive standard-kernel realization);
- **one common bilinear extension form across every residual packing: eliminates 4/6 immediately**.

Thus the first genuinely load-bearing cross-packing state is the fixed-ten-block bilinear form, not the individual deletion hyperplanes.

## Authority boundary

This is a partial k=4 closure only. The two affine-consistent orbits remain unresolved until the rank<=3 condition is decided exactly. The result does not yet close k=4, prove `D(C_15^3)=43`, or grant novelty authority.
