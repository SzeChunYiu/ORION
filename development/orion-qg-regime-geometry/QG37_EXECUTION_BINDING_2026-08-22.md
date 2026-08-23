# QG-37 robust execution binding

Date: 2026-08-22
Issue: SzeChunYiu/ORION#937
Execution branch: `research/qg37-robust-execution-20260822`

This execution is stacked on the earned QG-38 lineage so that QG-35/QG-36/QG-38 evidence is available, but it does **not** modify the QG-37 scientific protocol that was frozen before robust outcomes.

Frozen protocol source:
- branch: `codex/orion-qg-qg37-one-corruption-robust-20260822`
- path: `development/orion-qg-regime-geometry/QG37_ONE_CORRUPTION_ROBUST_PROTOCOL_V1.md`
- Git blob SHA: `c99f6ee73ab8e44e588a14ad0ab79b3fe426311c`

The frozen target remains: for each of the 92 joint bulk+spectrum classes, find the minimum set of distinct physical indexed probes whose class code has pairwise Hamming distance at least three, hence uniquely corrects at most one adversarially corrupted selected-probe response. Preserve physical-probe multiplicity. Do not reinterpret the result as a hardware-noise, stochastic-error, fault-tolerance-threshold, full finite-n optimum, generic coding novelty, or physical-advantage claim.

## Successor proof certificate used in this execution

QG-35 is now earned on the stacked lineage. Let `D_t(S)` be the minimum number of selected physical probes giving pairwise Hamming distance at least `t` within known summary class `S`. QG-35 supplies `D_1(S)=F(S)`.

A general puncturing lemma is used only as an additional independently checkable lower-bound certificate:

> If a probe code has minimum distance at least `t+1`, deleting any one selected coordinate leaves minimum distance at least `t`. Therefore `D_{t+1}(S) >= D_t(S)+1` whenever the class is non-singleton.

In particular, one-corruption robustness satisfies `D_3(S) >= F(S)+2`. A distance-three witness of exactly `F(S)+2` is therefore exact without relying on an optimizer lower bound. Classes where the witness requires more than this puncturing floor remain exceptional and require an additional exact infeasibility certificate.

This lemma is donor mathematics, not novelty authority. Its purpose is to make the compiler-specific robustness result less solver-dependent and to localize the genuinely nontrivial redundancy geometry.
