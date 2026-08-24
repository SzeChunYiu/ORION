# Paper A / A1 — explicit multi-Tag TARE constraint-rank theorem

Date: 2026-08-24

Base: `346cbf8bffbbaef200b86a9f9921393cce916716`

Status: **FROZEN BEFORE FORMAL A1 ANALYZER AND DUAL-HARNESS RUN**

Primary owner: `PAPER_A`

Authority ceiling: explicitly defined structural MultiTag-TARE-M2 grammar only.

## Scientific gap

The archive contains a general conditional constraint-rank lemma and the sharp frozen one-Tag R6M theorem. It does not instantiate the lemma in a broader TARE grammar. A generalization requires an explicit multi-Tag grammar and a proof that its coupled objective is deletion-dominated; merely adding more abstract syndrome bits is insufficient.

## MultiTag-TARE-M2 grammar

Fix any integer `s>=0`. An instance retains the three ordered two-term TARE blocks, frame pairs `(R_j0,R_j1)`, target assignments, central branches, and three-way Restore strings of R6M. It has `s` shared Tag Paulis `S_1,...,S_s`. For each Tag, prescribed branch labels are common across the three blocks and opposite between the two branches. Thus every frame Pauli has one partner-anticommutation constraint and `s` shared-Tag symplectic constraints.

The structural objective is

1. frame support with branch multipliers `m_jk>=mu`;
2. `t_tag,l * w(S_l)` for arbitrary nonnegative Tag weights;
3. `t_R` times the same three-way local Restore function `F_3` as R6M, with `t_R>=0`.

Tags are held fixed during the exchange. The theorem region is

`mu >= 2*t_R`.

Frozen R6M is `s=1`, `mu=2`, `t_R=1`, and Tag weight 2.

## Constraint-rank theorem target

For a frame Pauli `R` with partner `R'`, assign every active coordinate

`v_q=(<R_q,R'_q>,<S_1q,R_q>,...,<S_sq,R_q>) in F_2^(s+1)`.

Let `d_R` be the rank of the realized signature multiset. Its total has first component one, so it is nonzero. If `w(R)>d_R`, linear dependence yields a nonempty proper zero-signature subset. Zeroing `R` on that subset preserves partner anticommutation and every Tag label.

Changing one Restore letter at a coordinate can increase `F_3` by at most two. The frame refund is at least `mu`; therefore the exchange is non-increasing whenever `mu>=2*t_R`. Iteration gives

`w(R)<=d_R<=s+1`

for every frame Pauli in an optimum. Hence every admitted instance and every `n` has an optimum with all frame supports at most their realized constraint ranks, and in particular at most `s+1`.

The Tag cost is unchanged by the exchange, so arbitrary nonnegative Tag weights do not affect the theorem region.

## Local Restore obligation

For local Pauli letters `a,b,c`,

`F_3=1` if `a=b=c!=I`, and otherwise equals the number of nonidentity letters.

Exhaust all three changed positions and all `4^4` old/new letter combinations. The maximum increase from changing one letter must be exactly two. The source and independent implementations must derive all 768 rows and the same histogram.

## Multi-Tag signature obligation

For `s=0,...,8`, independently realize every one of the `2^(s+1)` signature vectors using local `X/I/Z` letters and recompute its symplectic bits. This demonstrates that the rank parameter is not an artifact of dependent raw checks. It is not a lower bound on the global intrinsic support number for `s>1`.

## R6M sharp corollary

Bind the protected all-`n` R6M support-two upper theorem and the exact support-two necessity witness. The `s=1` specialization therefore remains the sharp statement `kappa_R6M=2`.

No sharpness claim is authorized for `s=0` or `s>=2`.

## Required lanes

Source and independent verifier must:

1. derive the 768-row Restore table and exact maximum increase two;
2. derive all multi-Tag signature realizations for `s=0,...,8`;
3. verify the linear-dependence descent for standard-basis and exhaustive small-dimensional words;
4. verify the weighted boundary `mu>=2*t_R` symbolically and on exact rational examples;
5. bind the R6M upper and lower parent receipts;
6. reject on any disagreement or authority broadening.

## Donor subtraction and authority boundary

Linear dependence, zero-sum deletion, Pauli symplectic algebra, TARE itself, and generic shared-syndrome sparsification are donor material. The residual result is the explicit MultiTag-TARE-M2 grammar, its all-`n` deletion-dominance proof, its realized-rank normal form, and the sharp R6M specialization.

No claim is made that `s+1` is necessary for general `s`, that every possible multi-Tag TARE grammar has this objective, that a point outside `mu>=2*t_R` needs higher support, or that structural savings map to physical T-count/runtime/qubits. No novelty or venue authority is granted by the harness. CI is skipped and is not evidence.
