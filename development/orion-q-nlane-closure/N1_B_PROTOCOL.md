# ORION-Q N1-B frozen protocol — hierarchical grammar under matched bounded search (FIRST EXECUTION)

Date frozen: 2026-08-21
Lane: ORION-Q N1 (issue #674), family N1-B
Registered design source: issue #674 body ("N1-B — hierarchical grammar under matched bounded
search") and the recursion instruction in issue comment 5355080062. **N1-B was never executed
before**; unlike N1-A/C/D there is no prior recorded outcome. This run is the first execution and
whatever the frozen gates yield is the result.
Status of this document: protocol frozen BEFORE the result-bearing run of
`research/extensions/orion-q/nlanes/n1b_failure_conditioned_grammar_growth.py`.

## Disclosure of world-construction piloting

The world below is fully deterministic (no RNG). World-validity properties (origin tasks solvable,
protected tasks outside the primitive budget, quotient identity) were necessarily observed while
constructing it. Because outcome visibility during construction cannot be excluded for a
deterministic world, this study carries **diagnostic authority only** — it is not a protected
confirmatory experiment. The arms, parent variants, budget, splits, and gates below were fixed
before the receipt-bearing script was written and are not altered afterwards.

## Frozen synthetic world

- Carrier: the symmetric group `S_12` (permutations of 12 points, exact composition; a bounded
  exact stand-in for a discrete gate world). Program = word over the current library; semantics =
  composition (apply rightmost symbol first is NOT used; word `s1..sm` evaluates as
  `s1 ∘ s2 ∘ ... ∘ sm` built left-to-right with `state' = state ∘ s`).
- Primitive library `L0 = {a, b, c}` with fixed generators:
  `a = (i -> i+1 mod 12)`, `b = swap(0,1)`, `c = (2 5)(6 7)`.
- Hidden gadget: `g* = eval("abac")` (primitive geodesic exactly 4, asserted).
- Search procedure for every arm: budgeted breadth-first search from the identity with visited-state
  deduplication; **node budget = 400,000 child expansions per library configuration**. BFS from the
  identity is target-independent, so one budgeted BFS per library serves all tasks of that arm at
  matched budget (a per-task search could only cost more).
- Task splits (all targets are exact group elements; asserted pairwise-distinct across splits):
  - ORIGIN (12 tasks, solvable at primitive level): `t = w1 ∘ g* ∘ w2` for the fixed spec list
    `[(a,b),(b,c),(c,a),(aa,b),(ab,c),(ba,a),(bc,b),(ca,c),(cb,a),(a,bb),(b,aa),(c,ab)]`.
  - DEV / obstruction split (9 tasks): `t_{k,d} = g*^k ∘ d` for `k in {4,5,6}`, `d in {a,b,c}`.
  - HELD-OUT protected family (12 tasks): `t_{k,d} = g*^k ∘ d` for `k in {5,6}`,
    `d in {aa,ab,ac,ba,bc,ca}`. Origin solutions/tasks never appear in held-out
    (registered control: origin tasks removed before transfer; d-sets are disjoint by construction).

  AMENDMENT (2026-08-21, pre-outcome): the originally frozen held-out decoration set
  `{aa,ab,ac,ba,bb,bc,ca,cb,cc}` failed the protocol's own distinctness assertion at first
  execution — `b` and `c` have disjoint supports, so `cb ≡ bc` and `cc ≡ bb ≡ identity` in `S_12`.
  The run aborted on the validity assertion before any outcome was computed. The aliased
  decorations `{bb,cb,cc}` are removed; held-out is therefore 12 tasks. No gate, arm, budget, or
  terminal rule is altered; the amendment is also recorded in the receipt.

## Arms (all receive `L0`, the exact verifier, and the same 400,000-expansion budget per library)

1. **PRIMITIVE_ENUMERATION:** budgeted BFS over `L0` only. Expected to solve ORIGIN and fail the
   protected family (world-validity property, gated below).
2. **LIBRARY_LEARNING_PARENT (strongest parent, first right of refusal; three frozen variants, the
   parent's score is the MAX over variants):** each variant receives the *solved ORIGIN traces*
   (shortest words found by the primitive BFS) — its full registered entitlement — mines macros,
   and re-searches the held-out family with `L0 + mined macros`:
   - `P1_DL_ITERATIVE`: three rounds; each round mines all contiguous n-grams (n in 2..4) over the
     current corpus alphabet (macros included), promotes the gram maximizing description-length gain
     `(len-1)*count - len` if positive, rewrites the corpus; final library = `L0` + all promoted
     macros (canonical DreamCoder/Stitch-style compression).
   - `P2_TOP_4GRAM`: promotes the single most frequent 4-gram (a length-prior variant).
   - `P3_TOP_DL_SINGLE`: promotes the single gram (n in 2..4) with maximal one-shot DL gain.
3. **ORION_FAILURE_CONDITIONED_GROWTH (candidate mechanism; receives NO solved traces):** runs the
   primitive BFS, obtains certified `BUDGET_EXHAUSTED` failures on the DEV split; for every
   decoration `d` and consecutive `k` where **both** instances failed, computes the inter-instance
   quotient `q = t_{k+1,d} ∘ t_{k,d}^{-1}`; requires all computed quotients to be identical
   (certified recurring obstruction pattern — the registered failure-conditioned trigger); realizes
   a primitive word for `q` from the already-paid primitive BFS table; promotes it as one macro;
   re-searches held-out with `L0 + {q}` under the same budget.
4. **RANDOM_MACRO control (hostile):** `L0` + the fixed arbitrary length-4 macro `eval("cbba")`;
   shows that reach is not produced by merely enlarging the branching alphabet.

Budget accounting is reported per arm (primitive BFS + macro search; mining/quotient arithmetic
counted and reported).

## Prespecified gates

- `G1_WORLD_VALID`: primitive enumeration solves 12/12 ORIGIN and 0/18 held-out.
- `G2_RANDOM_MACRO_FAILS`: random-macro control solves 0/18 held-out.
- `G3_QUOTIENT_CERTIFIED`: >= 2 usable failed dev pairs, all quotients identical.
- `G4_NOT_TRACE_COMPRESSION_EQUIVALENT`: whether the promoted ORION macro element equals any macro
  element promoted by `P1_DL_ITERATIVE` (registered "not an equivalent compression of already
  solved programs" check; reported either way).
- `G5_REACH`: held-out solve counts for ORION and for each parent variant; parent score =
  max over variants.

## Terminal rule (frozen)

- If G1 or G2 fails: `N1B_WORLD_INVALID` (no outcome claim).
- If parent_max >= ORION reach: `N1B_LIBRARY_LEARNING_SUFFICIENT` (parent-sufficient negative;
  any per-variant nuance recorded but grants no residual claim).
- If ORION reach > parent_max and G3 passes: `N1B_FAILURE_CONDITIONED_LANGUAGE_GROWTH_VALUE`
  (bounded; exact-synthetic only; no novelty authority — inter-instance quotienting is adjacent to
  known abduction/CEGIS-style reasoning and this terminal explicitly does not claim otherwise).
- If both fail on held-out: `N1B_NO_REACH` (negative retained).

## Determinism

No RNG anywhere. All generators, specs, splits, and budgets are fixed constants above. Receipt line:
`ORIONQ_N1B_GRAMMAR_GROWTH=<canonical sorted json>`; pretty receipt written to
`research/extensions/orion-q/nlanes/N1_B_GRAMMAR_GROWTH_RESULTS.json`.

## Claim boundary

Exact-synthetic group-word scope only. DreamCoder/Stitch/library learning, gadget learning, and
recursive synthesis remain acknowledged parents; no novelty or real-quantum authority is granted by
any terminal of this study.
