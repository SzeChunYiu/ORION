# Mathematical Extensions R6 — Dominance Antichains and Typed Intervention Queries

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, and `MATHEMATICAL_EXTENSIONS_R5.md`

Status: rigorous typed-semantics addendum with exhaustive finite fixtures. The generic support-hypergraph and hitting-set machinery remains prior art; the new statements exploit the license dominance preorder and therefore depend on the typed cap-preserving semantics.

## 1. Argument and boundary

R5 proved that a syntactic dominance relation

`lambda preceq mu`

forces the derived authority set of `lambda` to be contained in that of `mu` under every common direct-refutation set. This addendum turns that inclusion into an exact query compiler.

For a conjunction asking whether a claim carries *all* licenses in a set, only dominance-minimal licenses matter. For a disjunction asking whether it carries *any* listed license, only dominance-maximal licenses matter. The same antichains determine two different intervention problems: destroying an all-query requires breaking one retained coordinate, whereas destroying an any-query requires breaking every retained coordinate simultaneously.

The result is specific to typed authority projections. It does not reclaim novelty for minimal supports, hypergraph blockers, or generic deletion hardness.

## 2. Dominance quotient

For each license `lambda`, let `C_lambda(R)` be the set of claims carrying `lambda` after direct refutation set `R`. R5 defines

`lambda preceq mu`

when the seed projection and retained-rule projection of `lambda` are contained in those of `mu`. Theorem D8 gives

`C_lambda(R) subseteq C_mu(R)`

for every `R`.

Licenses with identical seed-and-rule signatures are equivalent and should first be quotient-compressed as in R5 Corollary D7. The relation `preceq` then becomes a partial order on the quotient classes.

For a finite license set `L`, write

- `Min(L)` for its dominance-minimal classes; and
- `Max(L)` for its dominance-maximal classes.

## 3. Exact antichain compilation

For a claim `q`, define

`ALL_L(q,R)` iff `q in C_lambda(R)` for every `lambda in L`,

and

`ANY_L(q,R)` iff `q in C_lambda(R)` for at least one `lambda in L`.

**Theorem D10 (dominance-antichain query compression).**

For every claim `q` and refutation set `R`,

`ALL_L(q,R) = ALL_Min(L)(q,R)`

and

`ANY_L(q,R) = ANY_Max(L)(q,R)`.

**Proof.** If `lambda preceq mu`, then membership in `C_lambda(R)` implies membership in `C_mu(R)`. Therefore, in a conjunction containing both coordinates, the `mu` test is redundant; repeatedly deleting nonminimal coordinates leaves `Min(L)` without changing the truth value.

For a disjunction, `C_lambda(R) subseteq C_mu(R)` means the `lambda` alternative adds no accepting claim beyond the `mu` alternative. Repeatedly deleting nonmaximal coordinates leaves `Max(L)`. ∎

The theorem is exact for every direct-refutation set. It is not a heuristic based on observed closure frequencies.

## 4. Typed intervention laws

Fix a target `q`, an admissible intervention universe `E`, and nonnegative intervention costs. For each license `lambda`, let

`P_lambda(q)`

be the family of inclusion-minimal admissible support sets whose survival derives `q` in the `lambda` projection. A refutation set destroys `lambda` authority exactly when it hits every member of `P_lambda(q)`.

Let `tau(F)` denote the minimum cost of a hitting set for a family `F`, with infinity if no admissible hitting set exists.

**Theorem D11 (all-query and any-query interventions).**

After dominance-antichain compression:

1. the minimum cost to make `ALL_L(q,R)` false is

   `min_{lambda in Min(L)} tau(P_lambda(q))`;

2. the minimum cost to make `ANY_L(q,R)` false is

   `tau(union_{lambda in Max(L)} P_lambda(q))`.

**Proof.** The all-query fails as soon as one retained coordinate fails. The cheapest intervention therefore chooses the least-cost coordinate blocker.

The any-query fails only when every retained coordinate fails. A refutation set must consequently hit every minimal support of every retained coordinate, which is precisely a hitting set for the union of their support families. ∎

The formulas remain valid with weighted interventions. They expose a qualitative difference that an untyped reachability query cannot express: disjunctive authority survival is a joint multi-coordinate blocker, while conjunctive authority failure is a cheapest-coordinate blocker.

## 5. Query compiler

**Corollary D12 (static typed-query compiler).**

A frozen policy graph can preprocess a license query as follows:

1. quotient identical license signatures;
2. compute the dominance poset;
3. replace an `ALL` query by its minimal antichain;
4. replace an `ANY` query by its maximal antichain; and
5. route intervention analysis to the corresponding formula in Theorem D11.

The compilation is independent of the direct-refutation set. The fixed-point evaluator then runs only the retained coordinates.

The antichain can be much smaller than the policy vocabulary when licenses form chains or broad permission tiers. No asymptotic compression factor is claimed without a distribution on policy signatures.

## 6. Exhaustive fixture

The R6 verifier constructs two coordinates.

- `strict` has seed `a` and rules `a->b`, `b->c`.
- `broad` contains every strict seed and rule, plus seed `d` and rule `d->c`.

Thus

`strict preceq broad`.

The verifier enumerates all sixteen direct-refutation subsets of `{a,b,c,d}` and checks:

`C_strict(R) subseteq C_broad(R)`

for every `R`. It also confirms, for every claim and every refutation set, that

- `ALL_{strict,broad}` equals `strict`; and
- `ANY_{strict,broad}` equals `broad`.

When direct refutation of the target `c` is excluded and interventions may hit `{a,b,d}`:

- strict authority can be destroyed with one refutation;
- broad authority requires two;
- the all-query requires one; and
- the any-query requires two.

The fixture is exhaustively enumerated rather than inferred from one selected intervention.

## 7. Policy interpretation

A typical order is

`PROSPECTIVE preceq POST_OUTCOME`

only when every prospective seed and cap is also admitted by the post-outcome coordinate. Under that declared order:

- asking whether a result carries both permissions reduces to the prospective coordinate; and
- asking whether it carries either permission reduces to the post-outcome coordinate.

The order must be encoded and audited. It is not an inherent moral or legal ordering of evidence types.

For incomparable licenses, such as a jurisdictional permission and an independently verified theorem license, both remain in the relevant antichain. The query compiler never invents an ordering that the policy projections do not prove.

## 8. Prior-art and reference correction

The July 2026 paper by Ratan Bahadur Thapa and Steffen Staab, *Causality and Minimal Supports in Recursive Datalog* (arXiv:2607.16443; submitted 17 July 2026), studies inclusion-minimal supports, support hypergraphs, responsibility, deletion robustness, reachability paths, minimum cuts, and an NP-hardness calibration. Those generic components remain donor-overlapping context rather than residual novelty.

The defensible contribution here is the typed policy layer:

- cap-preserving coordinate projections;
- exact nonpromotion;
- direct-refutation retraction;
- static license noninterference and dominance; and
- dominance-antichain compilation of typed authority and intervention queries.

## 9. Academic positioning

The manuscript should lead with an operational error made by untyped reachability: a conclusion remains derivable after a prospective source is refuted, but the repaired path is only post-outcome and must not inherit prospective authority. The formalism then explains why this error cannot occur under typed caps.

The generic hypergraph complexity story should be compressed into related work and supporting propositions. The main theorem chain should be

`typed fixed point -> projection theorem -> noninterference -> dominance -> antichain query compiler -> application record`.

## 10. Atomic status

- Dominance quotient: retained and `VERIFIED` from R5.
- ALL/ANY antichain compression: `VERIFIED`.
- Typed intervention laws: `VERIFIED`.
- Static query compiler: `VERIFIED`.
- Exhaustive Horn fixture: `FINITE_EXACT`.
- Generic support-hypergraph, blocker, and deletion-hardness novelty: `WITHDRAWN`.
- Independently sourced real policy record: `MISSING_EXTERNAL_ARTIFACT`.

## 11. Remaining scientific frontier

Paper D’s formal core is now coherent and sharply separated from prior art. The remaining publication gate is an independently sourced application record with a real authority distinction—prospective versus post-outcome evidence, data-use permissions, or jurisdictional authorization. The record should demonstrate an operationally wrong untyped answer and the correct typed answer. Without that evidence, the paper remains a rigorous formal-methods contribution with limited systems validation.
