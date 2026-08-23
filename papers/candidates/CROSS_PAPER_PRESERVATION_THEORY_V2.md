# P6–P8 cross-paper preservation theory V2 — the determination dichotomy

**Date:** 2026-08-23
**Base:** `CROSS_PAPER_PRESERVATION_THEORY_V1.md` (2026-08-17), `DONOR_PROJECTION_SEPARATION_THEOREM_V1.md` (2026-08-18)
**Support:** `check_preservation_dichotomy_v2.py`, 7 of 7 laws discharged by exhaustive enumeration
**Weighting:** one law (§4) carries the contribution; six are internal-consistency checks — see §3.1
**Publication terminal:** `SYNTHESIS_WITH_MECHANIZED_SUPPORT` — up from V1's `SYNTHESIS_ONLY`
**Novelty terminal:** `PARTIALLY_RESOLVED` — see §6; still not `RESOLVED`

## 1. What changed, and why it matters

V1 wrote down a five-level preservation ladder and a transport rule, then filed itself as
`SYNTHESIS_ONLY` with novelty `CANNOT_CHECK`. It was never mechanized. Meanwhile P6, P7 and P8
each proved *the same five laws* over a different subject matter, with three independently written
finite enumerations that share no code:

| Law | P6 (certificate lifting) | P7 (navigation closure) | P8 (authority discharge) |
|---|---|---|---|
| donor engulfment | V4.1 | V3.1 | V3.1 |
| separation | V4.2 | V3.2 | V3.2 |
| non-laundering | V4.3 | V3.3 | V3.7 |
| selective revalidation | V4.4 | V3.4 | V3.4 (coercion) |
| negative equivalence | V4.5 | V3.6 | V3.10 |

Three instances of one structure is a theory, stated three times. V2 states it once, over a general
model, and discharges it by enumeration.

## 2. The general model

A **standing problem** is a coordinate vocabulary and the subset a contract makes load-bearing.
A **system** is the subset of coordinates it retains. A **donor** is what it observes plus the
native question it actually answers — which it is not free to redefine into whatever the target
contract needs. That last distinction carries the whole result in §4.

Standing is granted exactly when every required coordinate is preserved. A system sees only its
projection, so it sees a whole fibre of states at once; the canonical rule returns the standing
value when the fibre forces one and `CANNOT_CHECK` when it does not. Every sound rule is
dominated by that one, so an impossibility proved against it holds against all rules.

## 3. The determination theorem

> A system decides standing correctly **iff** its retained coordinates separate every
> standing-distinct pair of states — equivalently, iff it retains every required coordinate.

Necessity is the donor-projection argument of `DONOR_PROJECTION_SEPARATION_THEOREM_V1` Theorem 1:
equal projections force equal outputs, so a projection that identifies two states of different
standing is wrong on one of them. Sufficiency is the quotient construction: on a separating
projection the standing value is constant on each fibre.

Checked over all 1,024 (required, retained) pairs of the five-level ladder, 32 states each:
decidable ≡ separating ≡ required ⊆ retained, with no exception.

**The mathematics here is elementary — factorization through a quotient.**

### 3.1 What §3.2 and §3.3 do and do not establish — read this before quoting them

An earlier draft of this document claimed that the irredundancy and selective-revalidation checks
below make the five-coordinate claim *refutable*. **That was wrong and is withdrawn.** Both are
consequences of the model's own definition of standing (`AND` over the required coordinates), so
neither can ever come out any other way, for any vocabulary:

- §3.2 asks whether dropping a required coordinate loses decidability. By the determination theorem
  it must, for every coordinate of every vocabulary. The planted inert coordinate is outside the
  required set, so retaining the rest keeps `required ⊆ retained` and it must come back redundant.
  The check is law 3.3 restated, not evidence about L0–L4.
- §3.3's counts are subset combinatorics of a conjunction: 31 = 2⁵ − 1 and
  211 = Σₖ C(5,k)(2ᵏ − 1). They would be those numbers for any five coordinates whatsoever.

Of the seven laws the checker discharges, **six are internal-consistency checks on the model** —
worth having, since a core that failed one would be broken, but carrying no information about
whether these are the right coordinates. **One law has content: §4.** The claim that L0–L4 are the
right coordinate system for scientific standing is, as of this document, **unvalidated**. What would
validate it is §8 step 1, and only that.

### 3.2 Dropping a required coordinate loses decidability

Each of `L0_identity`, `L1_support`, `L2_semantic`, `L3_obligation`, `L4_authority` is load-bearing
in the sense above, and a planted inert sixth coordinate is correctly found redundant — so the
engine can return both answers rather than only ever "load-bearing". This is *irredundancy in the
registered model*, not universal minimality: P6.V4.4, P7.V3.4 and P8's ledger each forbid the
universal claim, and this does not make it.

### 3.3 Repairing part of what broke restores nothing

Over every affected set and every repair of it: 31 total revalidations restore standing, and all
211 proper-subset repairs are denied. P6.V4.4 and P7.V3.4, generalized — and see §3.1 on what these
counts are and are not.

## 4. The result that changes the programme's position

P6, P7 and P8 each proved a **negative equivalence theorem**: an ideal donor product carrying
identical typed fields ties the centralized system extensionally, so centralization buys no
expressivity. Three reviewers read those as weaknesses.

They are not weaknesses. They are the **sufficiency half of a dichotomy whose necessity half is a
positive superiority result**, and the discriminating variable is the donor *interface*:

> **Coordinate-exposing donors tie. Verdict-exposing donors do not.**
>
> - If donors expose their coordinates, a product over them decides exactly what a centralized
>   system retaining the same coordinates decides. Over all 1,024 (required, observed) pairs:
>   **0 mismatches.** This recovers P6.V4.5, P7.V3.6 and P8.V3.10 as one statement.
> - If donors expose only their own native verdicts, the tie fails. Enumerating every two-donor
>   stack over the required coordinates and **every join function over their verdicts**: of the 196
>   stacks in which both donors answer something (non-constant), **96 admit no sound, decisive join
>   at all** — while every one of them observes every required coordinate, and the ideal
>   coordinate-exposing stack over the same coordinates still decides.

The named witness is interpretable: donor A answers *"is any evidence still applicable?"* (`L2 ∨ L3`),
donor B answers *"is it semantically applicable?"* (`L2`). Between them they look at both required
coordinates. Neither their verdicts nor any function of them recovers whether the obligation is
discharged, because `L2` alone already forces A's answer.

**What this licenses, exactly.** The negative equivalence theorems are true *and* interface-relative.
Centralization is not inherently more expressive; carrying the coordinates is. Whether a deployed
donor stack exposes coordinates or verdicts is an empirical question about interfaces, and this
result does not answer it — it says which question decides the matter.

**What it does not license.** No claim that real donor stacks are verdict-exposing. No claim about
deployed-agent performance. The enumeration is a finite existence-and-prevalence result over the
registered model.

## 5. The no-alarm case

Cases 1–4 of V1 §10 are separations. Case 5 is the productive one: when every required coordinate
holds and is retained, transport must **succeed**. All 243 fully-satisfied contracts grant, with 0
spurious abstentions. A transport rule that refuses everything passes the four separations
perfectly and is worthless, so this is asserted rather than assumed.

## 6. Novelty — moved, not resolved

V1 §11 said outright: if a mature formalism already represents all the levels and the transport
rule without loss, adopt it rather than claim a new calculus. One facet of V1 §9's nine-formalism
list has now been searched, and it surfaced a strong parent that V1 did not list:

**McCann, *Effect-Transparent Governance for AI Workflow Architectures* (arXiv:2605.01030, May 2026)** —
machine-checked in Rocq, 454 theorems, 0 admitted lemmas. It proves semantic transparency of
governance on permitted executions, expressive minimality of five primitive capabilities, a
structural decidability boundary, and a strict subsumption asymmetry of structural over content
governance.

**Absorbed as donor-owned:**

- *Expressive minimality methodology.* Their minimality proof and our §3.1 irredundancy check have
  the same shape: class disjointness plus each primitive emitting what no combination of the others
  can. Ours is the finite-enumeration analogue and is not independent of it.
- *Governance/expressivity orthogonality.* Their transparency theorem is the stronger and
  better-mechanized statement that governance does not change what permitted programs compute.

**Residual delta, after subtraction:**

- Their governance is a **static per-directive check**; the ladder is about **what survives a
  transformation**. Preservation across change is absent from their model.
- No determination theorem — decidable iff the retained coordinates separate — appears there.
- Their subsumption asymmetry is *structural vs. content*. The §4 dichotomy is *coordinate-exposing
  vs. verdict-exposing*. This is the objection a reviewer will press hardest — same theorem shape,
  five primitives, minimality, machine-checked — so it is worth arguing rather than asserting.
  Their asymmetry is about **what the wrapper mediates**: a structural wrapper interposes on every
  effect, a content filter only rewrites returned values, so the filter cannot prevent an
  unauthorized effect from occurring at all. Both sides of their comparison are *mediators*, and the
  question is where the mediator sits. The §4 dichotomy is about **what an interface reveals to a
  composer**: both donor stacks observe exactly the same coordinates and are equally trustworthy
  locally, and the only difference is whether a downstream composer receives the coordinates or a
  verdict computed from them. Nothing is mediated, blocked or filtered in either regime; what
  differs is what survives the hop. The two results are compatible and neither implies the other —
  a structurally governed system whose donors expose only verdicts still loses §4's information.
- `L3_obligation` and `L4_authority` — discharge of a target obligation, and commit-time authority —
  have no counterpart in their capability taxonomy.

**Terminal: `PARTIALLY_RESOLVED`.** One facet of nine was searched. Lens/bidirectional-transformation
laws, truth maintenance, information-flow non-interference, self-adjusting computation and
proof-carrying stateful authorization remain unsearched, and the determination theorem in particular
is close enough to observational determinism that the non-interference literature must be read
before any novelty claim is made for it. **A green enumeration is formal support; it is not novelty
resolution, and the two must not be reported as one thing.**

## 7. What this does and does not do for publication

It moves `SYNTHESIS_ONLY` to `SYNTHESIS_WITH_MECHANIZED_SUPPORT`. It does not by itself create a
publication identity, and it closes none of the programme's external-custody blockers, because it
is not that kind of result. What it does is take the three papers' most-criticized outputs and show
they are one theorem with a positive half.

## 8. Next, in order

1. **Re-derive the three registered instances through the general core — this now carries all the
   empirical weight.** Since §3.1 establishes that six of the seven laws are vacuous, instance
   reproduction is the *only* thing that can validate the coordinate claim. Targets: P6's
   320 / 25 / 31 / 155 / 1,055; P7's plus 25 compositions and 25 bridge countermodels; P8's
   39,936 / 65 / 65+65 / 26 / 13 / 169 / 169. If the general engine reproduces those counts exactly,
   the unification is load-bearing rather than decorative. If any count differs, that is the finding —
   investigate before adjusting.

   **Known structural blocker.** The core enumerates `2ⁿ` bit-vectors over coordinates. But
   320 = 2⁶ × 5 and 39,936 = 2¹⁰ × 39 are not powers of two — P8's 13 donor families are visible in
   its count — so the registered models are not bit-vectors and **the core as written cannot
   enumerate those state spaces at all**. Step 1 is a core-generalization task (coordinates with
   arbitrary finite domains, plus a donor-family index), not a parameterization task. Start there.
2. **Finish the novelty search** across the remaining eight formalisms of V1 §9, non-interference
   first.
3. **Decide the publication identity** only after 1 and 2. Both of V1 §11's terminals must move.
