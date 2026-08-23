# P10 Cross-Revision Target Freeze V1

Status: **FROZEN BEFORE SOURCE NATIVE-STATE OUTCOME**

Frozen: 2026-08-20

The source native-state workflow was still queued when this target was selected. No B4 source-revision outcome, feature coefficient, cross-revision coverage, or target-revision performance had been observed.

## Source revision

- Mathlib: `e72c1e277f31441626621f7d0c7207862fc25569`
- source commit time: 2026-08-18 08:09:40 UTC
- Lean toolchain: `leanprover/lean4:v4.34.0-rc1`

## Prospectively frozen target revision

Target is the Mathlib protected `master` head observed on 2026-08-20 before source native outcomes:

- Mathlib: `d77ef0741c6da1ff12df68fb4145ea0ae0850c54`
- commit time: 2026-08-20 02:52:35 UTC
- commit message begins `feat: fun x ↦ x⁺ is monotone on commuting elements of a C⋆-algebra`
- Lean toolchain at target: `leanprover/lean4:v4.34.0-rc1`

The identical Lean toolchain is useful: the primary cross-revision perturbation is Mathlib ecosystem/source revision rather than an intentional compiler-version change.

## Population rule

Use exactly the 457 **source-manifest paths** as the prospective target file list. A target path that no longer exists is ineligible and counted against path coverage. For every existing path, derive the target revision's own corrected V2.1 coarse trajectories and native pre-tactic states using the same extractor semantics. Do not require source and target proofs to have identical action counts or labels.

The prospectively matched target population is all target-revision transitions found in those surviving frozen paths. Eligibility coverage is native-state receipt coverage divided by that target transition population. The >=80% cross-revision coverage gate remains unchanged.

## No-refit rule

B1 and B4 are fitted/selected only on source-revision training data under the source native-state protocol. Target data may not alter:

- B1 counts or smoothing;
- B4 coefficients or C selection;
- feature encoding or category set;
- target quality/thresholds;
- exclusions beyond the predeclared path/receipt rules.

Target evaluation reports B1/B4 accuracy and log loss, module-block uncertainty, and absolute degradation from the corresponding source-revision held-out metrics.

## Positive terminal

Unchanged from the frozen runtime-gated contract:

1. target native-state eligibility >=80% of the prospectively matched target transition population;
2. target B4 accuracy > target B1 accuracy;
3. B4 absolute accuracy degradation from source is smaller than B1 degradation;
4. target module-block bootstrap lower 95% bound for B4-B1 >0;
5. zero target refitting;
6. all target revision/toolchain/source/receipt identities pass.

A failed source native-state primary result blocks cross-revision structural promotion even if a descriptive target run is later available.
