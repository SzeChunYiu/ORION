# Mathematical Extensions R6 — An Exact Subset-Sum Automaton for Restricted Alphabets

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, and `MATHEMATICAL_EXTENSIONS_R5.md`

Status: rigorous theorem addendum. It supplies an exact finite engine for the alphabet-restricted invariant used by the paper. It does not by itself prove that a production compiler realizes the paper's deletion semantics.

## 1. Contribution

R5 gave closed formulas for independent cyclic-axis alphabets and quotient–kernel bounds for general alphabets. The remaining abstract task was exact computation when neither formula is sharp. This addendum closes that task with a finite acyclic automaton whose longest path is exactly the restricted zero-sum-free budget.

The construction is intentionally certificate-oriented: a longest path supplies an extremal word, while a terminal state supplies a checkable proof that no alphabet letter can extend that word without creating a zero sum.

## 2. Reachable-sum states

Let `H` be a finite abelian group and let `A subseteq H` be a finite alphabet. For a word `W` over `A`, define

`R(W)={sigma(U): U is a nonempty subsequence of W}`.

Thus `W` is zero-sum-free exactly when `0 notin R(W)`. For `a in A`, define the transition

`T_a(R)=R union {a} union (R+a)`.

If `R=R(W)`, then `T_a(R)=R(Wa)`: every nonempty subsequence of `Wa` either omits the new letter, consists only of the new letter, or contains it together with a nonempty subsequence of `W`.

A transition is *valid* when `0 notin T_a(R)`.

## 3. Strict growth

**Theorem A12 (strict-growth lemma).** Every valid transition strictly enlarges its state:

`T_a(R) != R`.

**Proof.** Suppose instead that `T_a(R)=R`. Then `a in R` and `R+a subseteq R`. Translation is injective, so the finite sets `R+a` and `R` have the same cardinality; hence `R+a=R`. Starting from `a in R` and repeatedly translating by `a` shows that

`2a,3a,...,ord(a)a=0`

all belong to `R`. This contradicts validity, because a reachable zero sum would already be present. ∎

**Corollary A13.** The directed graph of valid reachable-sum states is acyclic. Every path has length at most `|H|-1`, because valid states are subsets of `H\{0}` and each transition adds at least one new sum.

The bound is a coarse finiteness certificate, not a claim that the state graph is small in every instance.

## 4. Exact longest-path characterization

Let the initial state be the empty set. Retain only states reachable by valid transitions labeled by letters of `A`.

**Theorem A14 (exact automaton formula).**

`zsf(H;A)=maximum length of a directed path from the empty state.`

**Proof.** Reading the labels of a valid path produces a word whose state never contains zero, so the word is zero-sum-free. Conversely, every prefix of a zero-sum-free word induces a valid transition and therefore traces a path from the empty state. The two constructions preserve word length. ∎

Because the graph is a finite DAG, memoized dynamic programming computes the exact value and an extremal word. No multiplicity ceiling, guessed normal form, or integer-program relaxation is needed.

## 5. Terminal certificates

**Corollary A15 (finite terminality certificate).** Let `W` be a word attaining a longest path and let `R=R(W)`. Then for every `a in A`,

`0 in R union {a} union (R+a)`.

The pair consisting of `W` and the finite table of its reachable sums is therefore a complete certificate for the exact alphabet budget: the path proves the lower bound and the absence of a valid outgoing transition proves local maximality; the DAG dynamic program proves that no other branch is longer.

For independently structured alphabets, R5's closed formula remains preferable. The automaton is the exact fallback for irregular realized alphabets and for hostile replay of proposed formulas.

## 6. Compiler interpretation

Assume a compiler grammar has already established the V3 persistent-deletion hypotheses and associates every active coordinate with a letter of `A`. Then the exact automaton value is a sound terminal support ceiling for that named proof language. The terminal word is also the correct object to attempt to realize in production when testing whether the abstract certificate complexity is exact.

The theorem does not establish that a production state realizes every automaton word, that all production moves are represented by zero-sum deletion, or that the resulting support is intrinsic.

## 7. Verification

`papers/verify_five_math_extensions_r6.py` implements the reachable-sum DAG and a separate bounded-multiplicity brute-force engine. They agree on:

1. the standard basis of `C_2^3`, giving value three;
2. the alphabet `{(1,0),(0,1),(1,1)}` in `C_2 direct_sum C_4`, giving value four; and
3. the same three-letter alphabet in `C_3^2`, again giving value four.

Every accepted transition is checked to increase the reachable-sum state strictly, and each returned witness ends at a state with no valid outgoing transition.

## 8. Prior-art and novelty calibration

Finite-state subset-sum dynamic programming and longest paths in acyclic state graphs are standard algorithmic ideas. No generic novelty is claimed for representing subsequence sums by a state set. The paper-specific contribution is the exact certificate interface for the declared alphabet-restricted normal-form invariant: it connects a finite extremal word, an independently replayable terminality object, and the compiler realization gate already isolated in R4–R5.

## 9. Atomic status

- Reachable-sum transition identity: `VERIFIED`.
- Strict state growth: `VERIFIED` symbolically.
- Acyclicity and finite termination: `VERIFIED`.
- Longest-path equality with `zsf(H;A)`: `VERIFIED`.
- Three finite cross-check fixtures: `PASS` under two exact engines.
- Transfer to any named production compiler: `CONDITIONAL` on the persistent-deletion and realization hypotheses.
- Intrinsic production support or physical-resource improvement: `NOT_INFERRED`.

## 10. Remaining scientific frontier

The abstract algebraic layer is now closed by formulas, quotient bounds, and an exact fallback engine. The next non-duplicative advance is production realization: select a compiler alphabet, bind its complete edit grammar, realize an automaton-extremal terminal word, and test every stronger production move against it. Further generic finite-group refinements would not replace that semantic experiment.
