# Paper C / C3 — arbitrary-order interaction data and exact value

Date: 2026-08-24  
Base: `cfce47d8c4edb9c3df83efd35c699cb9a25a8a07`  
Status: **POST-EXPLORATORY CONSTRUCTION; FROZEN BEFORE FORMAL ANALYZER AND DUAL-HARNESS RUN**  
Primary owner: `PAPER_C`  
Parent results: C1 all-`m>=5` decision theorem and C2 pair-information value/optimizer separation.  
Authority ceiling: exact frozen structural `SELECT+PREP+WIDTH` grammar only.

## Atomic question

Can the C2 pair-information counterexample be strengthened so that, for every term count `m>=5`, even the complete labeled common-factor tensor through order `m-2` fails to determine the exact improvement value?

## Outcome-independent disclosure

An exploratory threshold search found that adding sufficiently many common all-term columns makes the one-block compiler optimal in both members of a parity-trade pair. The conservative column count below was chosen after that exploration to permit a short symbolic dominance proof. No claim of a minimal padding count is made. The construction and all acceptance gates below are frozen before the formal analyzer, independent verifier, and native campaign are run.

## Frozen construction

Fix integers `m>=5` and `L>=1`. Let `q=m-1`, with terms consisting of an anchor `a` and variables `v_1,...,v_q`. Put

- `b=ceil(log2(m))=(m-1).bit_length()`;
- `d(m)` equal to the balanced PREP depth recurrence used by the frozen grammar;
- `H=m-1+d(m)+b`, the non-SELECT cost of the one-block compiler;
- `N=2^(m-2)L`, the number of parity-trade columns in either instance;
- `K=N*m*(b+1)+H+1` common all-term columns.

Every trade column contains the anchor. In instance `A`, use `L` copies of every support `{a} union S` whose variable subset `S` has the same parity as `q`; in instance `B`, use the opposite parity class. Thus the all-variable support occurs `L` times in `A` and zero times in `B`. Add the same `K` all-term columns to both instances. Every column is nonempty and carries only `X` or `I`.

## Frozen theorem target

For every `m>=5` and `L>=1`:

1. `A` and `B` have the same ordered term weights, term count, and qubit count;
2. for every labeled nonempty term subset `T` with `|T|<=m-2`, the exact common-factor count `f_A(T)=f_B(T)`;
3. both instances are strictly improved over unary and have the unique one-block optimum;
4. their exact improvements satisfy

   `Delta(A)-Delta(B)=[m(b+1)-1]L`;

5. therefore all labeled interaction data through order `m-2` is insufficient to determine exact value, with ambiguity linear and unbounded in `L` for every fixed `m>=5`.

The theorem does not say that a particular compressed representation is necessary, that physical resource costs differ by this amount, or that parity trades are new.

## Human-readable proof obligations

### Low-order equality

For any fixed set of `t<q` variables, exactly `2^(q-t-1)` subsets in either parity class contain it. A labeled subset `T` of at most `m-2=q-1` terms fixes at most `q-1` variables, whether or not it contains the anchor. Hence

`f_A(T)=f_B(T)=K+L*2^(q-t-1)`.

Singletons give identical ordered term weights. Both variants contain `N+K` columns.

### Unique one-block optimum

Consider any partition with `k>=2` blocks. Each common all-term column costs `2k` in that partition and `1` in the one-block compiler, producing a penalty of at least `3K`.

Across all `N` trade columns, the one-block SELECT contribution is nonnegative and at most `N*m*(b+1)`, while the competing contribution is nonnegative. The competing structural overhead is nonnegative, whereas the one-block overhead is `H`. Therefore

`C(partition)-C(one block) >= 3K-N*m*(b+1)-H > 0`.

The one-block compiler is unique. The all-singleton partition equals the unary compiler, so the improvement is strict.

### Exact value gap

The ordered weights are equal. The full common factor differs by exactly `L`. In the one-block formula, the coefficient of the full common factor is `1-m(b+1)`. Hence `A` costs `[m(b+1)-1]L` less than `B`, and their improvements differ by the same positive amount.

## Required machine corroboration

The source analyzer and an independently written generic verifier must:

1. construct the two Pauli families without loading a frozen answer table;
2. compare every labeled factor count through order `m-2`;
3. enumerate every set partition and optimize exactly for `m=5,6,7,8,9` at `L=1`;
4. bind the symbolic dominance margin and exact gap for multiple larger `m,L` values;
5. bind the C1 and C2 parent receipts;
6. disagree or reject if any exact row, digest, scope flag, or parent binding fails.

## Donor subtraction and authority boundary

Parity trades, orthogonal-array style marginal equality, and the generic fact that low-order marginals need not determine higher-order structure are donor mathematics. The residual claim is the exact compiler realization, one-block dominance argument, and exact value-gap formula in this frozen grammar.

No novelty authority is granted by the harness. No physical T-count, runtime, qubit advantage, cross-objective transfer, cross-grammar transfer, minimal-padding result, or multiplicative approximation lower bound is claimed. CI is skipped by request and is not evidence.

