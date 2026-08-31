# ORION20.TEMPLATE_KERNEL_QUOTIENT.v1

## Object

For a Boolean binary primitive `p : {0,1}^2 -> {0,1}`, define the frozen three-pair template

`T_p(x,y,z) = p(x,y) XOR p(x,z) XOR p(y,z)`.

There are 16 binary Boolean functions. We encode each by its four-bit truth table in input order `(0,0),(0,1),(1,0),(1,1)`.

The failed promotion experiment observed that both code 8 (AND) and code 14 (OR) map to `majority3`. The result below identifies the exact reason.

## Theorem 1 — exact kernel

Viewed as a linear map over `F_2`, `T : F_2^4 -> F_2^8` has

`ker(T) = {0, x XOR y}`.

In the repository's code convention these are truth-table codes `{0, 6}`.

### Proof

Linearity follows because `T` is an XOR of three evaluations of `p`. The zero primitive is in the kernel. For `q(x,y)=x XOR y`,

`q(x,y) XOR q(x,z) XOR q(y,z)`

`= (x XOR y) XOR (x XOR z) XOR (y XOR z) = 0`.

So `{0,q}` is contained in the kernel. Direct evaluation of the 16 functions shows the image has eight elements. Rank-nullity over `F_2` therefore gives kernel dimension one, hence the kernel is exactly the span of `q`. The independent checker exhaustively verifies the finite rank statement rather than taking it as an assumption. QED.

## Corollary 1.1 — exact observational quotient

For every primitive `p`,

`T_p = T_{p XOR (x XOR y)}`.

Moreover these are the only collisions. Thus the 16 primitives form exactly eight observational equivalence classes:

- `{0,6}`
- `{1,7}`
- `{2,4}`
- `{3,5}`
- `{8,14}`
- `{9,15}`
- `{10,12}`
- `{11,13}`.

Every fibre has size two.

## Corollary 1.2 — AND versus OR is structural

AND has code 8 and OR has code 14, and `8 XOR 14 = 6`, the parity kernel element. Therefore their equality under the template is forced by the quotient:

`T_AND = T_OR = majority3`.

The observed duplicate is not a sampling accident and cannot be removed by a larger census over the same primitive vocabulary and the same template.

## Theorem 2 — unique primitive identification is impossible under the frozen observable

Let a selector or certificate depend only on `T_p`. On any candidate vocabulary containing both members of a nontrivial quotient fibre, no such selector can identify which member generated the observable.

### Proof

The two primitives emit identical `T_p`. Any function of that observable returns the same output for both. QED.

In particular, no structural-indispensability claim can distinguish AND from OR under this frozen observation interface. An external complexity ordering may prefer one representative, but that preference is supplied by the ordering, not by the template.

## Design consequence

A successor asking for a **unique structural primitive** must change the scientific question or add an observation that is not invariant under parity translation. Merely enlarging the sample, formula size, or repeated evaluation of the same template cannot identify within a quotient fibre.

A legitimate new observable `S_p` must pass a pre-outcome separation control such as `S_AND != S_OR`; otherwise the same impossibility remains.

## Relation to the adverse promotion result

The frozen ORION-20 promotion terminated `T3_PROMOTION_FAILS__NO_UNIQUE_MINIMUM`: admissible primitives were `[8,14]`, the minimal bases were `{8}` and `{14}`, and the indispensable set was empty. This theorem strengthens the interpretation without changing that terminal: the failure arises from the exact one-dimensional kernel of the frozen template.

## Claim boundary

Earned deductive claim:

> The frozen pairwise-XOR template identifies binary primitives only modulo addition of parity `x XOR y`; its eight fibres are exactly two-element cosets, and majority3 has preimage `{AND, OR}`. Unique primitive identification is therefore impossible from this template alone.

Not earned:

- a new successful primitive basis;
- a broader practical compiler advantage;
- a novelty claim over Boolean clone theory;
- authority to reopen the spent promotion identity.

`scientific_authority_delta: NONE`