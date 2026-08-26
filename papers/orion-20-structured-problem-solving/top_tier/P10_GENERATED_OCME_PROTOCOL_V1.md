# ORION-20 generated OCME protocol V1

**Programme:** #977  
**Purpose:** test the still-open requirement that at least one outside-closure edit be *generated/selected by a preregistered method search* rather than hand-declared from the gold obstruction solution.

## Authority boundary

This is a new protected study. It does not reinterpret the earlier `P10_OCME_FORMAL_NONVACUITY_V1_GREEN` result. The earlier AND2/SQUARE edits remain hand-declared formal non-vacuity witnesses.

The protocol, candidate grammars, originating tasks, held-out tasks and known-method controls are frozen before the generator/checker implementation or outcome is committed.

A positive result may establish **generated finite OCME under the two registered exact closure models**. It may not establish unrestricted autonomous mathematical invention, Lean-native superiority, or superiority to arbitrary external synthesis/evolution systems.

## Shared rules

For each setting:

1. Freeze an old language/closure `Cl(B)` and an exact verifier.
2. Freeze an *originating* obstruction task and disjoint held-out tasks.
3. Freeze a candidate primitive grammar independently of the protected outcome.
4. Generator sees the old closure, originating task and candidate grammar only. It must not inspect held-out target tables while selecting a primitive.
5. Generator selects the lowest-complexity primitive that enables an exact originating solution under the registered composition template.
6. A separate verifier checks that the selected primitive is outside `Cl(B)`, validates the originating solution and only then opens/evaluates held-out transfer.
7. Exhaustive search/synthesis over the old language is the donor-complete finite baseline: if the exact target is in the old closure, OCME is invalid; if not, no amount of old-language enumeration/evolution may be called method expansion.
8. Known-method controls must remain classified `KNOWN_COMPOSITION` with zero false expansions.

## Setting A — Boolean affine -> generated nonlinear binary primitive

### Old language

Four Boolean inputs. `Cl(B)` is the complete affine family over GF(2): constants, projections, negation-as-XOR-with-1 and arbitrary XOR composition. Exact closure size is 32 functions.

### Fresh obstruction family

The originating target is three-input majority on one registered variable triple. Held-out targets are the same semantic responsibility on the other three variable triples. Majority is nonlinear over GF(2), so old-language exhaustive closure must fail exactly.

### Candidate primitive grammar

Enumerate **all 16 binary Boolean truth tables** in canonical code order. No primitive name such as AND/OR is supplied to the generator. For each candidate primitive `g`, the registered composition template is

`g(a,b) XOR g(a,c) XOR g(b,c)`.

Selection complexity is prospectively fixed as:

1. exact originating solve required;
2. primitive must be outside affine closure;
3. minimize Hamming weight of the four-bit truth table;
4. tie-break by integer truth-table code.

The generator is not allowed to inspect held-out triples during selection.

### Donor-first failure criterion

The exact affine closure is enumerated independently. Failure of every affine truth table on the originating majority target is an exact obstruction certificate; stochastic/search/evolution variants restricted to the same closure are therefore semantically unable to solve it.

## Setting B — integer affine -> generated unary primitive

### Old language

Integer input evaluated exactly on the frozen verifier domain `{-4,-3,-2,-1,0,1,2,3,4}`. `Cl(B)` is the family `a*x+b` over rational coefficients.

### Fresh obstruction family

The originating target is a cubic-plus-affine function. Held-out targets change only the affine correction while preserving the same latent nonlinear mechanic. Exact affine closure must fail on every cubic target.

### Candidate primitive grammar

The generator receives anonymous candidate unary tables produced prospectively by the registered catalog:

- square;
- cube;
- absolute value;
- sign;
- fourth power.

Selection is by exact originating fit under the wrapper `primitive(x) + a*x + b`, with rational `a,b` solved by the registered exact fitter. The generator sees anonymous candidate IDs and originating values only; semantic names are revealed only in the post-selection receipt.

Selection complexity is prospectively fixed as:

1. exact originating solve required;
2. primitive must be outside affine closure;
3. minimize catalog complexity rank `[ABS, SIGN, SQUARE, CUBE, FOURTH_POWER]` only after exactness/outside-closure checks;
4. deterministic candidate-ID tie-break.

Held-out targets are not available to primitive selection.

### Donor-first failure criterion

An independent exact affine-membership checker must reject the originating and held-out cubic targets. Thus exhaustive search, synthesis or evolutionary recombination restricted to the old affine language cannot solve them regardless of search budget.

## Protected endpoints

- exact old-closure obstruction on the originating task;
- generated primitive identity and whether it was selected without held-out access;
- outside-closure verification;
- originating exact solve;
- number of held-out tasks solved after opening held-out targets;
- false expansion count on known-method controls;
- number of candidate primitives evaluated;
- whether old-language exhaustive search/synthesis/evolution is formally closed;
- deterministic replay;
- second implementation agreement on closure membership and selected primitive semantics.

## Positive gate

`P10_GENERATED_OCME_V1_SUPPORTED` requires:

- both originating tasks outside their frozen old closures;
- the generator selects at least one outside-closure primitive without held-out target access;
- selected primitive closes its originating obstruction exactly;
- selected primitive transfers to every held-out task in that setting under old-language wrappers/composition;
- zero false expansions on frozen known-method controls;
- exact proof that old-language exhaustive search/synthesis/evolution cannot reach the promoted targets;
- deterministic replay;
- a structurally independent verifier agrees on closure membership, primitive selection result and transfer count.

If a generated primitive solves the origin but does not transfer, retain the result as `GENERATED_EDIT_NO_TRANSFER`. If no primitive survives, retain `GENERATED_OCME_NOT_SUPPORTED`; do not expand the grammar after outcome inspection.
