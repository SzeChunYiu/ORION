# Low-Order Optimality Certificates with Sharp Value-Estimation Lower Bounds

**Paper C — hardened manuscript V2**
Scientific cut: C1–C3 parents, Boolean-lattice trade theorem, and R2 minimax corollaries
Workflow cut: `academic-paper-skills@188e83e639571c435344630ae68fdc66072650d2`

## Abstract

A compact statistic can determine whether optimization is necessary while remaining provably inadequate for the value and structure of the optimum. We establish this hierarchy exactly for a Pauli partition compiler with a frozen structural `SELECT+PREP+WIDTH` objective. For every number of terms `m>=5`, the unary compiler is globally optimal if and only if two clause families hold: every pair gain is nonpositive, and every sum of two disjoint pair gains plus one is nonpositive. Thus an optimizer over all set partitions has a decision certificate whose largest clause touches four term indices. The threshold is sharp at `m=4`.

Decision sufficiency does not imply value or witness sufficiency. For every `t>=1`, two `5t`-term instances have identical ordered weights and identical complete labeled pair-gain matrices, and both strictly improve on unary, but their exact improvements are

`Delta_A=12t-2`, `Delta_B=10t-1`.

Every estimator using only that pair representation must return the same value on both instances. Consequently its worst-case real additive error is at least `(2t-1)/2`, its worst-case integer error at least `t`, and its symmetric multiplicative factor at least

`sqrt((12t-2)/(10t-1))`.

No pair-information-only estimator can guarantee a uniform factor below `sqrt(6/5)`, while one-sided certified upper or lower estimates require asymptotic factor at least `6/5`. The same fiber forces incompatible optimizer structures: every optimum in one family contains a triple block, whereas every optimum in the other uses only pairs and singletons.

We then raise the observed interaction order. For every `m>=5` and `L>=1`, two instances agree on every labeled common-factor count through order `m-2` yet have exact improvements separated by `[m(ceil(log2 m)+1)-1]L`. Boolean-lattice Möbius inversion proves that any nonzero integer trade preserving all proper labeled marginals is an integer multiple of the parity trade, touches every one of the `2^(m-1)` cells, and has at least `2^(m-2)` columns on each signed side. Primary Markov-basis and hierarchical-model literature owns the generic fiber and move mathematics. The residual contribution is the compiler-specific conjunction of exact constant-order decision, unbounded and multiplicative value impossibility, optimizer separation, and a sharp high-order witness.

## 1. Introduction

Global combinatorial optimization often supports several downstream questions:

- Is a baseline already optimal?
- How much improvement is available?
- What structure must an optimizer contain?
- Can a feature representation approximate the optimum uniformly?

A representation may be complete for one query and incomplete for another. This paper provides an exact, scalable example rather than an empirical feature-ablation result.

The compiler partitions `m` Pauli terms into arbitrary blocks, optionally extracts common Pauli factors, and pays a structural cost. Although the candidate space contains every set partition, unary optimality is decided by inequalities involving at most four indices. That theorem makes pair information look unexpectedly powerful. The remaining results identify its precise limits.

### 1.1 Contributions

1. **All-`m` decision theorem:** four-index clauses decide unary optimality for every `m>=5`.
2. **Sharp term-count boundary:** a four-term exact counterexample.
3. **Pair-information value/witness separation:** identical complete pair data, unbounded additive gap, and forced triple-versus-pair optimizer structure.
4. **Exact estimation lower bounds:** additive minimax radius, integer radius, symmetric multiplicative factor, and one-sided factor.
5. **Arbitrary-order separation:** all labeled interactions through order `m-2` remain insufficient for exact value.
6. **Primitive witness theorem:** proper-marginal-preserving trades are exactly parity multiples, making exponential difference support unavoidable.

## 2. Frozen compiler

An instance is an ordered tuple of nonidentity Pauli strings `p_1,...,p_m`. Let `w_i` be term weight, `W=sum_i w_i`, and `f(S)` the number of columns on which every term in nonempty block `S` has the same nonidentity Pauli.

The compiler chooses a set partition `Pi` and factor/ancilla options. Under the frozen equal-weight structural objective, factoring and shared width dominate their alternatives. For `|Pi|>=2`, the reduced cost is

`C(Pi)=2m+|Pi|-3 + sum_S d(|S|) + max_S b(|S|)`

`       + sum_S [2f(S)+(b(|S|)+2)(w(S)-|S|f(S))]`,

where `b(s)=ceil(log2 s)`, `b(1)=0`, and

`d(1)=0`,

`d(s)=d(ceil(s/2))+d(floor(s/2))+s-2`.

The unary incumbent costs

`C_U=2W+3m-3`.

The single-block flag convention is treated separately. These costs are structural, not physical T counts, circuit depth, runtime, qubits, or fault-tolerant overhead.

## 3. Four-index decision certificate

For each pair define

`g_ij=4f({i,j})-(w_i+w_j)`.

Let `ORION-14(m)` require:

1. `g_ij<=0` for every pair;
2. `g_ij+g_kl+1<=0` for every two disjoint pairs.

**Theorem 1.** For every `m>=5`, `min_Pi C(Pi)=C_U` if and only if `ORION-14(m)` holds.

The proof derives the exact partition gain. Matching or cycle sums of pair inequalities control every block of size at least three; integrality prevents two disjoint pair blocks from simultaneously attaining zero gain; the exceptional one-block formula is bounded separately; and every failed clause supplies its own witness partition.

The registered four-term instance

`XXII, XYII, XZII, XIXX`

satisfies all two clause families but has `C_U=27` and one-block cost `23`. Hence `m>=5` is sharp.

## 4. Complete pair information: one fiber, two optima

For each `t>=1`, construct `t` disjoint five-term gadgets. The two families `A_t,B_t` have the same ordered term weights and every labeled pair common-factor count, hence the same pair-gain matrix. Both violate `ORION-14` and strictly beat unary.

Exact decomposition gives

`Delta_A(t)=12t-2`,

`Delta_B(t)=10t-1`.

The value gap is `2t-1`.

Every optimum in `A_t` contains one distinguished triple block and one pair per gadget. Every optimum in `B_t` can be chosen—and is forced globally—to use pairs and singletons only. Thus pair information does not determine whether an optimal triple exists.

## 5. Minimax consequences of indistinguishability

Let `Phi` be any deterministic real-valued estimator whose input is exactly the term count, ordered weights, and complete labeled pair-gain matrix. Since `A_t` and `B_t` have identical inputs, `Phi` returns one number `y_t` for both.

**Theorem 2 (additive minimax radius).** For every `t>=1`,

`max(|y_t-Delta_A|,|y_t-Delta_B|) >= (2t-1)/2`.

Equality is attained at the midpoint. If `Phi` must output an integer, the minimum worst-case error is exactly `t`.

**Proof.** Two real points at distance `2t-1` cannot both lie within radius smaller than half their distance from one common estimate. The integer radius is the ceiling of that half-distance. ∎

This is an exact information lower bound: no training procedure, model class, or computational budget can evade it while using only the stated representation.

### 5.1 Symmetric multiplicative approximation

Assume improvements are positive and a factor `rho>=1` means

`Delta/rho <= y <= rho Delta`.

**Theorem 3.** A common estimate valid for both fiber members requires

`rho >= sqrt(Delta_A/Delta_B)`

`    = sqrt((12t-2)/(10t-1))`.

The geometric mean `sqrt(Delta_A Delta_B)` attains equality. The factor increases with `t` and tends to

`sqrt(6/5) approximately 1.095445`.

Therefore no pair-information-only estimator has a uniform symmetric approximation factor strictly below `sqrt(6/5)` over the family.

### 5.2 One-sided certificates

A common upper estimate must be at least `Delta_A` but, to be an `alpha`-approximation for `B_t`, at most `alpha Delta_B`. Hence

`alpha >= Delta_A/Delta_B`.

The same ratio lower-bounds a common certified lower estimate. It tends to `6/5`. These are representation lower bounds, not hardness assumptions.

## 6. All proper interactions still miss exact value

Fix `m>=5`, let `q=m-1`, and distinguish one anchor from `q` variable terms. Use every anchor-plus-variable support of one parity class versus the opposite parity class, with multiplicity `L`, then add identical all-term padding that makes the single block uniquely optimal.

The two instances agree on ordered weights and every labeled common-factor count for subsets of size at most `m-2`, yet

`Delta(A)-Delta(B)=[m(ceil(log2 m)+1)-1]L`.

For fixed `m`, the value ambiguity is unbounded in `L`.

## 7. The parity trade is the unique invisible direction

Represent a trade column by a subset of `[q]`. Let `delta:2^[q]->Z` be the signed multiplicity difference and

`M(T)=sum_{S superset T} delta(S)`

its upper marginal. Equality of all proper labeled marginals means `M(T)=0` for every proper `T`.

**Theorem 4 (proper-marginal kernel).** If all proper upper marginals vanish, then

`delta(S)=(-1)^(q-|S|)c`,

where `c=delta([q])`.

**Proof.** Möbius inversion on the Boolean lattice writes `delta(S)` as the alternating sum of upper marginals over supersets of `S`. Only the top marginal survives. ∎

If `c!=0`, every Boolean cell is used; exactly half are positive and half negative. For a primitive integer trade, each signed side has mass at least `2^(q-1)=2^(m-2)`. The registered `L=1` parity trade attains this bound. This proves minimality of the **difference trade**, not of the common padding.

## 8. Primary-source donor subtraction

Diaconis and Sturmfels established Markov bases as algebraic moves connecting fibers with fixed sufficient statistics. Dobra identified primitive moves for decomposable graphical models. Hosten and Sullivant proved finiteness/stabilization phenomena for hierarchical-model Markov bases through Graver complexity. Binary graph-model work studies degree and width of Markov moves.

Those sources own the generic language of fibers, marginal-preserving moves, toric ideals, Graver/Markov complexity, and the possibility that higher-order moves survive fixed lower marginals. Boolean-lattice Möbius inversion is also classical.

The residual Paper-C result is not “lower marginals can miss higher interactions.” It is the exact joint theorem for one compiler:

- a global set-partition decision has a four-index certificate for all `m>=5`;
- the same complete pair representation has an exact unbounded/minimax value gap and optimizer-structure ambiguity;
- even order `m-2` information fails;
- the compiler witness is the primitive kernel direction.

No inspected primary source supplies that decision/value/witness hierarchy or its compiler cost formulas. This is an author-side overlap conclusion, not external priority certification.

## 9. Reproducibility

C1–C3 are separately bound to source, generic, and native exact records. The R2 verifier checks all additive and multiplicative formulas through large `t`, validates the optimal midpoint and geometric mean, and rechecks the Boolean-lattice kernel in dimensions through eight. All-size authority comes from the proofs.

A submission archive should include the exact four-term witness, one gadget pair, generated product instances, the parity construction, and source data for every main figure.

## 10. Limitations

1. The objective is the frozen structural compiler grammar.
2. The decision theorem does not reconstruct an optimizer.
3. Minimax bounds apply to estimators restricted to the exact stated pair representation.
4. Randomized estimators are not separately analyzed; under worst-case expected loss, the same two-point argument can be added with an explicit loss convention.
5. The high-order construction uses conservative common padding; its minimality is open.
6. Generic fiber/Markov/Möbius mathematics is donor-owned.
7. Cross-objective and cross-grammar transfer remain open.

## 11. Discussion and conclusion

Information sufficiency is query-dependent. Pair data completely decides one global question—whether unary is optimal—yet cannot approximate the amount of improvement beyond fixed factors and cannot determine optimizer block structure. Observing all but the top interaction order still fails to determine exact value, and the invisible parity direction is provably dense.

The result matters for static compiler prediction and for learned surrogates of combinatorial optimization. A zero-error decision classifier does not imply a useful value regressor; a sufficient statistic for one query need not be sufficient for another. Here those distinctions are exact, scalable, and independent of computational assumptions.

## Selected references

- P. Diaconis and B. Sturmfels, *Algebraic Algorithms for Sampling from Conditional Distributions*, Ann. Statist. 26, 363–397 (1998), DOI `10.1214/aos/1030563990`.
- A. Dobra, *Markov Bases for Decomposable Graphical Models*, Bernoulli 9, 1093–1108 (2003), DOI `10.3150/bj/1072215202`.
- S. Hosten and S. Sullivant, *A Finiteness Theorem for Markov Bases of Hierarchical Models*, J. Combin. Theory A 114, 311–321 (2007), DOI `10.1016/j.jcta.2006.06.001`.
- M. Develin and S. Sullivant, *Markov Bases of Binary Graph Models*, Ann. Comb. 7, 441–466 (2003), arXiv:math/0308280.
- D. Král', S. Norine and O. Pangrác, *Markov Bases of Binary Graph Models of K4-Minor Free Graphs*, J. Combin. Theory A 117, 759–765 (2010), DOI `10.1016/j.jcta.2009.07.007`.

## Publication decision record

**Primary posture:** top specialist combinatorics/optimization or `Quantum`, selected according to whether the editor sees the compiler hierarchy or the marginal-kernel theorem as central.
**R2 status:** `TOP_TIER_THEORY_CANDIDATE__AUTHOR_SIDE_PRIMARY_SOURCE_BLOCKER_SUBSTANTIALLY_CLOSED`.
**Residual risk:** external experts may identify a closer hierarchical-model theorem or judge the frozen compiler grammar too narrow.
**External-only gates:** independent proof audit, exact target resolution, figure/source-data package, reference verification, archive and final PDF review.
