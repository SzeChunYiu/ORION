# ORION-QG QG-37 — one-corruption-resilient indexed probe identification

Date: 2026-08-22
Issue: SzeChunYiu/ORION#937
Parent programme: #740
Earned observation parents: QG-32 #911, QG-32c #928, QG-34 #924.
Pending optional comparison parent: QG-35 #932.

## Status

**PROSPECTIVE ROBUST-OBSERVATION FRONTIER. FROZEN BEFORE ANY ROBUST CARDINALITY, DISTANCE, DECODER, OR OVERHEAD OUTCOME.**

QG-32/QG-34 assume exact indexed probe responses. QG-37 asks for authority that survives one adversarially corrupted selected-probe response after the exact joint bulk+spectrum summary class is already known.

This is an evidence-reliability problem for ORION-Q research control. It is not a hardware noise model, quantum error-correction threshold, or physical measurement claim.

## 1. Exact robustness semantics

For a selected set of **distinct physical indexed probes** `P`, define the response word of orbit `o`

`W_P(o) = (K[o,p])_{p in P}`.

For a known initial joint summary class `S`, unique recovery after at most one arbitrary coordinate corruption is possible iff

`d_H(W_P(a), W_P(b)) >= 3`

for every distinct `a,b in S`.

Equivalently, every orbit pair must be distinguished by at least three selected probes.

Define:

`R1(S) = min |P| : every pair in S is distinguished by >=3 distinct probes`.

`R1_* = max_S R1(S)` over the canonical 92 QG-32 joint classes.

Singleton classes have `R1(S)=0`.

A separate universal quantity may be computed:

`R1_universal = min |P|` for one fixed P that satisfies the same distance>=3 condition simultaneously inside every one of the 92 classes.

Keep class-conditioned and universal quantities separate.

## 2. Non-negotiable physical-probe multiplicity rule

Ordinary noiseless test-cover deduplication is **not sound** here if it replaces an identical coverage class by a single representative.

Two or three distinct physical probe coordinates can induce identical pair-incidence patterns and can still be jointly necessary to accumulate Hamming distance three.

Therefore:
- physical probe identity is preserved in the exact optimization;
- an implementation may group identical pair-incidence masks only if it preserves multiplicity;
- for demand three, any identical coverage class may be safely capped at `min(original_multiplicity, 3)` representatives, because a fourth identical probe cannot reduce any pair's residual demand below zero after three copies have already been selected;
- a mandatory ablation must compare robust feasibility with naive multiplicity-one collapse and report whether that ordinary QG-35-style reduction changes any class result. The ablation is diagnostic only and cannot redefine the robust target.

Coverage dominance elimination is forbidden in V1 unless a proof explicitly preserves distinct-probe multiplicity under all selected-set contexts. Default: **no dominance elimination** in the robust exact solver.

## 3. Frozen universe

Reconstruct from the earned QG-32 generic primitives only:
- 715 orbit representatives;
- 384 physical indexed probe coordinates;
- exact integer response matrix `K[o,p]`;
- 92 canonical joint bulk+spectrum classes;
- class-size histogram `{1:7,2:22,3:6,4:6,6:25,8:2,12:14,24:8,48:2}`.

No QG-35 result is needed for the primary robust minima.

## 4. Production exact optimization

For each non-singleton class S, build one binary variable `x_p in {0,1}` for each of the 384 distinct physical probes and one constraint per orbit pair:

`sum_{p: K[a,p] != K[b,p]} x_p >= 3`.

Primary production solver: exact binary MILP with objective `min sum_p x_p`, zero MIP gap, deterministic coefficient/order construction, and a declared per-class solver time cap.

A class earns an exact minimum only when the solver returns proven optimality. If a class has an incumbent but no optimality proof, that class is `UPPER_ONLY` and QG-37 cannot claim exact `R1_*`.

For every exact class record:
- optimum cardinality;
- selected physical probe indices;
- solver status/message;
- exact objective and bound agreement;
- physical-probe multiplicity / grouped-coverage diagnostics.

Universal robust optimization may run only after all class-conditioned problems finish. It uses the union of all within-class pair constraints and the same 384 binary physical-probe variables. If it does not prove optimality under its declared cap, report only a certified upper bound.

## 5. Independent generic exact verification

Generic ORION must independently reconstruct the QG-32 response matrix from phase-free F2^2/F3 primitives and must not import production QG-37 results as semantics.

For every class for which production claims exact optimum `k`:
1. independently verify the serialized k-probe witness has minimum pairwise Hamming distance >=3;
2. independently prove infeasibility of cardinality `<=k-1` using a distinct exact bounded-search formulation over residual pair demands, preserving physical-probe multiplicity;
3. the bounded search must not use the production MILP basis, branch tree, LP relaxation, solver incumbent, or solver lower bound.

Frozen generic bounded-search semantics:
- state contains residual demands in `{0,1,2,3}` for every pair, available distinct probe identities (or an exactly equivalent multiplicity-preserving grouped state), and slots remaining;
- choose a pair with positive residual demand and the smallest number of currently available distinguishing probes as the branch constraint;
- use only sound lower bounds, including maximum total marginal residual-demand reduction and per-pair candidate-count feasibility;
- include/exclude branching or exhaustive required-subset branching is allowed, but no order-sensitive pruning may remove a lower-index companion merely because a higher-index probe was selected first;
- memoization must include every state component that affects future availability.

If the independent lower-bound proof does not finish under its cap, the class cannot be promoted to exact robust minimum even if production MILP is optimal.

## 6. Distance and decoder certificate

For each positive class result, recompute the full selected response codebook and serialize:
- minimum pairwise Hamming distance;
- count of pairs at that minimum;
- first canonical minimum-distance pair;
- complete histogram of pairwise selected-word distances.

For every exact class with `R1(S)>0`, verify radius-1 unique decoding directly:
- enumerate each clean codeword;
- enumerate every selected coordinate and every response symbol appearing in that coordinate within the class, plus one deterministic foreign-symbol control;
- mutate at most one coordinate;
- require that no corrupted word lies within Hamming radius 1 of two distinct clean codewords.

The Hamming-distance>=3 theorem is the proof principle; the explicit decoder enumeration is an implementation binder.

## 7. Robustness overhead — gated on QG-35

Primary QG-37 does not require QG-35.

Only after an immutable exact QG-35 receipt exists may a separate composition compute

`R1(S)-F(S)`

and related maxima/histograms. QG-37 production itself must keep `NOISELESS_OVERHEAD_AUTHORITY=false` unless that parent is bound under a separately frozen composition rule.

Do not infer physical error cost from this difference.

## 8. Native ORION-Q authority

May authorize only:
- exact class-conditioned one-corruption structural-probe identity robustness on classes independently closed by production+generic;
- exact robust worst case only if all 92 classes are exact;
- exact universal robust fixed code only if separately solved and independently verified;
- explicit radius-1 decoder/distance certificates.

ORION-Q control consequence:
- a noiseless distinguishing receipt is insufficient identity authority when one selected probe answer may be corrupted;
- require a radius-1 robust code/decoder or escalate to richer state/referee.

Mandatory false:
- hardware measurement noise model;
- stochastic physical error rate;
- quantum fault-tolerance threshold;
- noiseless QG-35 comparison/overhead unless separately composed;
- full finite-n optimum probes;
- generic coding/separating-system novelty;
- physical quantum advantage.

## 9. Harness

Require before any promotion:
- production exact/upper-only result file;
- generic independent per-class verification;
- native ORION-Q authority gate;
- deterministic byte-identical production replay;
- self-consistent tamper: remove one selected redundancy probe or lower a serialized minimum distance, recompute result digest, and require generic rejection;
- multiplicity-one-collapse diagnostic serialized but never used as authority;
- hard false stronger fields.

## 10. Honest terminals

Whole-lane terminals:
- `QG37_EXACT_ONE_CORRUPTION_CLASS_CONDITIONED_PROBE_CODE_MACHINE_CHECKED`
- `QG37_ROBUST_CLASS_CONDITIONED_UPPER_BOUND_ONLY`
- `QG37_ROBUST_CODE_INFEASIBLE_IN_FROZEN_PROBE_LIBRARY`
- `QG37_CANNOT_CHECK`

Universal subresult authority is independent and must be explicitly `EXACT`, `UPPER_ONLY`, or `CANNOT_CHECK`.

## Donor subtraction

Minimum test cover, set multicover, Hamming-distance error correction, separating systems, active diagnosis, liar games and noisy group testing are donor ideas. Candidate value is only the exact compiler-specific QG-32 response-code geometry and its scoped ORION-Q evidence-reliability consequence.