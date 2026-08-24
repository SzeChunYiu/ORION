# Paper C / C1 — all-`m` partition-compiler decision certificate

Date: 2026-08-24  
Base: `3616f0f1a69b571fcbf85fa3093aa050765c7fc9`  
Status: **FROZEN BEFORE IMPLEMENTATION AND DUAL-HARNESS OUTCOME**  
Primary scientific owner: `PAPER_C`  
Authority ceiling: exact mathematics for the frozen structural compiler grammar; no novelty, physical-resource, or cross-grammar authority.

## Atomic question

For the natural `m`-term extension of the frozen SixLCU partition compiler, can equality between the full partition optimum and the unary incumbent be decided exactly by inequalities involving at most four term indices, even though the optimizer ranges over every set partition?

The test is deliberately stronger than another six-term enumeration. It must either establish an all-`m` theorem with a human-readable proof or preserve the first exact counterexample.

## Frozen compiler grammar

An admitted instance is an ordered tuple of nonidentity Pauli strings

`p_1,...,p_m in {I,X,Y,Z}^n \ {I^n}`,

with term weights `w_i`, total weight `W=sum_i w_i`, and common-factor weight `f(S)` for each nonempty block `S`: the number of qubit columns on which every term in `S` has the same nonidentity Pauli.

The compiler may choose any set partition `Pi` of `{1,...,m}`, independently enable or disable common-factor extraction on every block, and choose shared or dedicated index ancillas. Costs use the frozen equal-weight structural objective

`SELECT + PREP + WIDTH`.

This is a combinatorial node/support cost. It is **not** a physical T count, circuit depth, runtime, qubit count, fault-tolerant overhead, or hardware advantage.

For a block of size `s`, define

- `b(s)=ceil(log2 s)`, with `b(1)=0`;
- `d(1)=0` and `d(s)=d(ceil(s/2))+d(floor(s/2))+s-2`, the frozen balanced-tree depth sum.

For a partition with `k>=2`, factor extraction and shared ancillas weakly dominate their alternatives. The resulting exact cost is

`C(Pi)=2m+k-3 + sum_S d(|S|) + max_S b(|S|)`

`       + sum_S [2 f(S) + (b(|S|)+2)(w(S)-|S| f(S))]`.

The unary incumbent is

`C_U=2W+3m-3`.

For the single-block partition, the same frozen grammar has flag zero and must be treated separately rather than silently applying the `k>=2` formula.

## Frozen certificate

For each pair `ij`, let

`g_ij = 4 f({i,j}) - (w_i+w_j)`.

Define `P4(m)` by exactly two clause families:

1. `g_ij <= 0` for every pair;
2. `g_ij + g_kl + 1 <= 0` for every two disjoint pairs `{i,j}` and `{k,l}`.

The interaction arity is two and the maximum clause support is four term indices. Generic facts about matching inequalities, graph packings, and decision-versus-optimization complexity are donor mathematics, not ORION novelty.

## Frozen target theorem

For every `m>=5`, every admitted `n`, and every admitted Pauli tuple in the frozen grammar,

`min_Pi C(Pi) = C_U  iff  P4(m)`.

The equivalence is about equality with the unary incumbent. It does not say the full optimizer witness can be reconstructed from the certificate, nor that the certificate determines the exact improvement value.

## Human-readable proof obligations

### 1. Dominance reduction

For every block, enabling factor extraction changes SELECT by a nonpositive amount because the extracted common factor is charged fewer times. Shared width is at most dedicated width. Therefore the full grammar optimum equals the factored/shared optimum used below. The verifier must derive this inequality from the frozen cost formula.

### 2. Exact gain decomposition for `k>=2`

For a block of size `s`, define

`T_s(S)=[s(b(s)+2)-2]f(S)-b(s)w(S)`.

Then

`C_U-C(Pi)=sum_S T_|S|(S)+c(Pi)`,

where

`c(Pi)=sum_S (|S|-1-d(|S|))-max_S b(|S|)`.

The balanced recurrence gives

- `|S|-1-d(|S|)=1` for sizes 2, 3, and 4;
- `=0` for size 5;
- `<=0` for every size at least 5.

The last statement follows directly for size 5 and, for `s>=6`, from `d(s)=d(ceil(s/2))+d(floor(s/2))+s-2` and the fact that at least one child has size at least 3 and hence positive depth sum.

### 3. Large-block bound from pair clauses

For any block `S` of size `s>=3`, use a perfect matching when `s` is even and an `s`-cycle when `s` is odd. Summing pair nonpositivity counts each term once (matching) or twice (cycle), while every selected pair has common-factor weight at least `f(S)`. In both cases,

`w(S) >= 2s f(S)`.

Consequently

`T_s(S) <= [s(2-b(s))-2] f(S)`.

If `f(S)>=1`, this is at most `-2`; if `f(S)=0`, nonidentity terms give `T_s(S)=-b(s)w(S)<=-b(s)s<=-6`. Hence every block of size at least three contributes at most `-2`.

### 4. Arbitrarily many pair blocks collapse to four-index clauses

Within one partition, pair blocks are mutually disjoint. All `g_ij` are integers. Clause 1 makes them nonpositive, and clause 2 prevents two disjoint pair gains from both being zero. Thus among any `r>=2` pair blocks, at most one gain is zero and the other `r-1` gains are at most `-1`:

`sum pair-block gains <= -(r-1)`.

This exactly pays the `r-1` positive shape constant of an all-pair partition. If a size-three-or-larger block is present, `max b>=2`; its `-2` block bound pays the remaining possible shape constants. The analyzer and independent verifier must record the explicit case algebra, not merely assert that all shapes were searched.

### 5. Single-block partition

For the one-block compiler, with `b=b(m)`, `F=f({1,...,m})`, and `d=d(m)`,

`C_U-C_single=(1-b)W+[m(b+1)-1]F+2m-2-d-b`.

Pair nonpositivity, summed over a perfect matching or odd cycle, gives `W>=2mF`.

- If `F=0`, `W>=m` and the displayed gain is strictly negative for `m>=5`.
- If `F>=1`, substitution gives a coefficient bounded by `m(3-b)-1`; direct recurrence values close `5<=m<=8` (`b=3`, `d=2m-6`), `d>=m-1` closes `9<=m<=16` (`b=4`), and `b>=5` closes `m>=17`.

Thus the exceptional single-block formula is nonprofitable for every `m>=5`.

### 6. Converse

Failure of clause 1 is witnessed by the partition containing that pair and all remaining singletons. Failure of clause 2 is witnessed by the partition containing those two pair blocks and all remaining singletons. Their gains are exactly `g_ij` and `g_ij+g_kl+1`, respectively.

## Frozen sharpness falsifier at `m=4`

The threshold `m>=5` must not be weakened. At `m=4`, `n=4`, take the four strings (qubit order shown left to right)

`XXII, XYII, XZII, XIXX`.

Their weights are `(2,2,2,3)`, total weight is 9, and every pair has exactly one common nonidentity column. Pair gains are `(0,0,-1,0,-1,-1)` in lexicographic pair order. Every one-pair and two-disjoint-pair clause holds, but

`C_U=27` and `C_single=23`.

This is a registered support-four counterexample to transfer below five terms. It is part of the positive theorem package and must never be relabelled as noise.

## Independent machine corroboration

The production analyzer and generic verifier must use independent implementations. Required checks are:

1. derive the cost/gain coefficients from the grammar;
2. check the symbolic integer inequalities above;
3. reproduce the exact `m=4` falsifier;
4. exhaust the complete reorder-quotiented `n=1,2` domains for `m=5`;
5. exhaust complete `n=1` for `m=6` and bind the existing complete `m=6,n=2` QG-12 parent without using its labels as a proof premise;
6. reject on any mismatch between `P4(m)` and exact partition optimization;
7. run the analyzer/generic route and a separate native campaign route in isolated harness workspaces;
8. call the local executor exactly once per request.

Enumeration is corroboration only. The all-`m` authority comes from the written proof and exact formula binding.

## Frozen terminals

Positive:

`PAPER_C_C1_ALL_M_GE_5_FOUR_INDEX_DECISION_THEOREM_MACHINE_CORROBORATED__M4_SHARP_COUNTEREXAMPLE`

Honest alternatives:

- `PAPER_C_C1_ALL_M_THEOREM_REFUTED`
- `PAPER_C_C1_M4_SHARPNESS_WITNESS_REFUTED`
- `PAPER_C_C1_PRODUCTION_GENERIC_DISAGREEMENT`
- `PAPER_C_C1_NATIVE_GENERIC_DISAGREEMENT`
- `PAPER_C_C1_PARENT_BINDING_FAILED`
- `PAPER_C_C1_CANNOT_CHECK`

## Saturation assessment and reopen triggers

Knowledge saturation is not claimed. The theorem uses standard matching/cycle arguments and requires a fresh primary-source review in LCU compilation, partition optimization, sparse certificates, and local-to-global optimality before any novelty statement.

The frozen search universe is saturated only for the exact grammar and the exact two-clause language above: arbitrary set partitions are handled symbolically, the exceptional one-block formula is separate, complete low-`n` regressions are registered, and the first excluded term count has an exact falsifier.

Reopen immediately if:

- any alternative factor/ancilla option beats the dominance reduction;
- a legal size or depth-sum convention differs from the frozen recurrence;
- production and independent formulas disagree;
- any `m>=5` counterexample is found;
- the paper seeks a physical cost interpretation or another LCU grammar;
- literature subsumes the compiler-specific theorem.

## Implementation hypothesis

The smallest justified implementation is additive: one generalized evaluator/proof ledger, one independent generic verifier, one native campaign manifest, focused tests, and one isolated dual-harness driver. Existing SixLCU code and receipts remain read-only scientific parents.

## Authority boundary

If every gate passes, Paper C may claim an exact all-`m>=5` four-index decision theorem and a sharp `m=4` counterexample for this frozen structural partition compiler. It may not claim generic decision/optimization separation as new, exact value sufficiency, optimizer reconstruction, physical quantum advantage, cross-objective robustness, novelty, or venue readiness.
