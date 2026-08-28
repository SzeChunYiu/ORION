# A2 — Exhaustive-search dominance

`scientific_authority_delta = NONE` · detail file for
[`../THEOREM_PROOF_AUDIT_V1.md`](../THEOREM_PROOF_AUDIT_V1.md)

This object received the deepest scrutiny, because dominance over
exhaustive search is a strong claim. **The phrase denotes two different
propositions in the corpus, pointing in opposite directions.** Neither is
the claim a reader is most likely to infer. Disambiguating them in the
manuscript is mandatory.

---

## Reading 1 — `ORION-20-T2` as written: exhaustive search is the *upper bound*

> "no selector exceeds complete affordable exhaustive verification on solve
> rate" — `TOP_TIER_DYNAMIC_EPISTEMIC_MANUSCRIPT_V1.md:20`

Here exhaustive verification **dominates every selector**, not the reverse.
Any selector's output lies in the menu, so its solved set is a subset of
the exhaustively-verified solved set. Near-trivially true — *provided*:

1. the menu is finite and fully enumerable **within the budget**;
2. the verifier is decisive: no false negatives, no stochastic acceptance;
3. "solve" means "some menu element verifies".

**No proof of this statement exists in the repository.** It has no
counterpart in `PAPER_THEOREM_PACKAGES_V1.md` or
`PAPER_THEOREM_PROOFS_V1.md`.

### G-14 (major) — quantifier order unstated; "complete affordable" undefined

`∃ budget ∀ task (exhaustive is affordable)` is a strong uniform
hypothesis. `∀ task ∃ budget` is nearly vacuous. The theorem's entire
content sits in which one is meant, and neither is stated. "Complete
affordable" carries that whole load and is never defined.

Condition 2 is also a genuine hypothesis rather than boilerplate: if the
verifier admits false negatives, a selector **can** exceed exhaustive
verification by proposing a semantically equivalent but differently
presented candidate that the verifier happens to accept. Verifier
decisiveness must be stated.

### Useful consequence, currently unstated

`ORION-20-T2` is self-limiting **in the paper's favour**: it entails that
ORION's contribution cannot be search efficiency inside a fixed menu, only
menu expansion. That is an argumentative asset and should be said out loud.
It also constrains H2, which must be read as a *cost* claim (verifier
calls, search depth, branching, time-to-first-correct at matched verified
quality — as `sections/11-primary-hypotheses.tex` in fact words it) and
never as a solve-rate claim.

---

## Reading 2 — the receipts' "exhaustive closure GREEN": exhaustive search is the *dominated* party

> "arbitrary search/synthesis/evolution restricted to that old language is
> semantically unable to reach the majority target; this is not a
> finite-search timeout argument" —
> `P10_GENERATED_OCME_RESULT_RECEIPT_V1.md:32`

This is the closure tautology of [A1](AUDIT_A1_FINITE_CLOSURE_V1.md): a
procedure whose output range is `Cl(B)` cannot emit an element outside
`Cl(B)`. True, and correctly qualified *within that sentence*.

### G-15 (major) — the comparison is not information-matched

What is quantified over is a class of searches **definitionally denied the
very grammar the ORION generator was handed**.

| | candidate grammar | composition template | budget | outcome |
|---|---|---|---|---|
| "donor" baseline | old closure only | — | unbounded | cannot reach target, by definition |
| ORION generator | 16 truth tables (A) / 5 unary candidates (B) | supplied | 16 / 5 evaluations | reaches target |

A **fair** exhaustive baseline with the same information and the same
budget is: hand a plain enumerator the same candidate grammar and the same
template, and let it enumerate. That baseline succeeds immediately — and in
fact the ORION "generator" *is* that enumerator: `select_bool` iterates the
16 truth-table codes and `select_int` iterates the 5 catalogue rows.

Under matched information there is no dominance in either direction. There
is a **definitional partition** between a grammar that contains a fitting
primitive and one that does not.

### Recommended wording

The defensible claim is:

> once a target is certified outside a registered closure, no procedure
> whose output range is that closure can reach it, at any budget.

That is a statement about closure — not about search quality, and not a
comparison against any deployed system. Any sentence in which
"donor-complete", "AlphaEvolve", "synthesis" or "evolutionary" appears near
"dominance" **without the range restriction in the same sentence** is a
defect.
