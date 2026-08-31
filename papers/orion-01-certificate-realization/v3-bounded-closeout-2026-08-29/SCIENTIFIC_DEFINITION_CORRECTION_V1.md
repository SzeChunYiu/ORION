# ORION-01B R6I support-statistic correction V1

**Date:** 2026-08-31  
**Correction class:** genuine scientific-definition defect; same evidence, narrower and coherent statement  
**New experiment:** none

## Superseded wording

An intermediate V3 draft described the R6I support statistic as the maximum weight of the four independent frames while also assigning rank-only budget five to the registered block-deletion word.

Those are different objects. The maximum individual-frame weight cannot be used as the exact length of that word.

## Evidence that resolves the definition

The registered R6I transition simultaneously replaces both independent generators of one block by the identity at one coordinate. Therefore one word position is one block column in

\[
\operatorname{supp}(R_{j0})\cup\operatorname{supp}(R_{j1}),
\]

not one support position of a selected independent generator.

The source-bound evidence is preserved at:

- `development/orion-qg-regime-geometry/QG6_SYNDROME_DIMENSION_COMPRESSION_PROTOCOL_V1.md`, which defines the simultaneous two-generator block deletion and its five-dimensional change space;
- `research/extensions/orion-qg/qg6_syndrome_rank.py`, whose frozen rewrite is `ZERO_BOTH_INDEPENDENT_GENERATORS_OF_ONE_BLOCK`;
- `development/orion-qg-regime-geometry/QG1_RANK2_SUPPORT5_PROTOCOL_V1.md`, which defines the active set as the union support of the two independent generators and proves the separately required semantics and objective descent; and
- `development/orion-qg-regime-geometry/QG9_V6_SUPPORT1_NORMALIZATION_PROTOCOL_V1.md` and its protected receipt, which localize both independent generators of each block to one anticommuting core under the frozen unit objective.

## Corrected common statistic

For a compiler state \(x\), the current manuscript uses

\[
\sigma_I(x)
=
\max_{j\in\{A,B\}}
\left|
\operatorname{supp}(R_{j0})\cup\operatorname{supp}(R_{j1})
\right|.
\]

The rank-only word length is exactly this joint active-column count. The rank-five bases therefore establish an exact budget of five in the declared rank-only state language. The whole-system one-core normalization gives \(\sigma_I=1\), and \(\sigma_I=0\) is infeasible because an anticommuting frame pair cannot be identically supported on no column.

The direct-product statistic is the sum of these per-component joint-column values. The direct-enumeration corollary likewise enumerates candidate block columns.

## Authority boundary

This correction does not create a maximum-individual-frame lower bound, a lower bound for richer proof systems, a production-registry completeness result, an algorithm-independent complexity lower bound, or a hardware advantage. It preserves the five-to-one comparison only for the exact rank-only calculus, frozen objective, canonical-label R6I subfamily, and joint active-column statistic.

All original adverse/null/indeterminate production-transfer records remain unchanged, including `FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED`, `AB_PR1469_PRODUCTION_TRANSFER_NOT_ESTABLISHED`, and `CANNOT_CHECK_MOVE_COMPLETENESS`.
