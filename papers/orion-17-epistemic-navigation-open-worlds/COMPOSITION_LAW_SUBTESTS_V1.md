# The composition calculus's two open sub-tests, performed

**Status:** `BOTH_SUBTESTS_PERFORMED__PARENTAGE_MADE_PRECISE__NO_NEW_TERRITORY`
**Date:** 2026-09-02
**Scientific authority delta:** `NONE`. This document performs the two tests
`COMPOSITION_LAW_PARENT_FINDING_V1.md` left open. Tests can only sharpen or narrow.

The parent finding identified interface/contract theories as the true parent of the
composition calculus (not MDP homomorphism) and left exactly two things unestablished:

> 1. That the A/G identification is exact. … Confirming it requires mapping `Demands`,
>    `Discharged` and `Fresh` onto a specific A/G formulation from the meta-theory and
>    checking the correspondence in both directions.
> 2. That no interface theory already has the exact V4.1. … a survey of the
>    meta-theory's frameworks against them has not been run.

Both are performed below, against primary sources verified in session (publisher and
author-hosted copies only; every definitional quote was read in the fetched text, none
recalled). One attribution correction surfaced and is recorded in §4.

## Test 1 — the A/G mapping, both directions

**Formulation used:** Benveniste, Caillaud, Nickovic, Passerone, Raclet, Rumpler,
Sangiovanni-Vincentelli, Damm, Henzinger & Larsen, *Contracts for System Design*,
FnT EDA 12(2–3):124–400 (2018), DOI 10.1561/1000000053 — verified from the
author-hosted PDF. Its primitives: a contract `C = (A,G)`; implementation
`A × M ⊆ G` (saturated: `M ⊆ G ∪ ¬A`); refinement `C2 ⪯ C1 iff A2 ⊇ A1 ∧ G2 ⊆ G1`;
parallel composition `C1 ⊗ C2` with `G = G1 ∩ G2` and
`A = (A1 ∩ A2) ∪ ¬(G1 ∩ G2)` (Def 5.4(3), eq 5.7), where the `∪ ¬(G1∩G2)` term is
the mutual-discharge weakening; compatibility = the composed assumption differs from
false. Crucially, `×` is required associative and commutative (Table 4.1) — the
meta-theory has **no sequential composition operator**. The sequential discharge shape
appears exactly once, as a *derived proof obligation* (Ch. 11, Autosar chain, eq 11.4:
`Atop ∩ GBL ⊆ L1A,TL` — upstream guarantee contained in downstream assumption).

**Direction 1 — ORION-17 → meta-theory.** The mapping:

| ORION-17 | meta-theory reading |
|---|---|
| `Demands(Tgt t, o)` | the assumption side: what the composite's target contract demands of its consumer/environment |
| `Demands(Src t, o)` | assumption already carried by the source context |
| `Discharged(t, o)` | guarantee-discharges-assumption — the directional reading of the `∪ ¬(G1∩G2)` mutual-discharge term, i.e. Ch. 11's `G_upstream ⊆ A_downstream` |
| `Fresh(t, o)` | **no counterpart** |

V4.3's `Total(t) ↔ ∀o. Demands(Tgt t, o) → Demands(Src t, o) ∨ Discharged(t,o) ∨
Fresh(t,o)` reads, in meta-theory terms, as "every demanded assumption is met by the
context, discharged by a guarantee, or newly issued" — the intent of `A = weakest{A |
A∧G₂⇒A₁ ∧ A∧G₁⇒A₂}` (primer eq 2.4), directionalized. The exact compositability
condition V4.3 derives (second leg's source demands contained in first leg's target
demands) **is the shape of eq 11.4's derived containment**. Confirmed.

**Direction 2 — meta-theory → ORION-17.** The correspondence fails to transport in two
named places: (i) the meta-theory's composition operator is commutative and mutual —
there is no `⊗`-level directional operator for V4.3's sequential containment to be a
special case of; the sequential shape exists only one level down, inside refinement
checking. (ii) `Fresh` has no counterpart: meta-theory guarantees are behavioral
propositions and composition only intersects/weakens them, whereas ORION-17
obligations are records with identity and composition can create new ones.

**Verdict: the identification is now `PROVED` *as a specialization*, not an identity.**
V4.3 is not a rederivation of the meta-theory's composition law; it is the meta-theory's
*derived proof-obligation pattern* (guarantee-discharges-assumption containment),
promoted from a verification side-condition to the operator's defining condition and
made directional. The parent finding's `PLAUSIBLE` closes as `PROVED with the two
non-transporting places stated`. What ORION-17 may claim is exactly the promotion and
the direction — never the A/G pattern itself.

## Test 2 — does any interface theory already have the exact V4.1?

V4.1: `Carries(Comp(t,u)) ↔ Carries(t) ∧ Carries(u) ∧ Match(Tgt t, Src u)` —
sequential (t-then-u), iff-gated partial operator, asymmetric test of first leg's
output contract against second leg's input contract, `Match = equality ∨ Bridge` with
`Bridge` assumed of no properties. Survey results:

| framework | sequential? | iff-gated partiality? | bridge-style non-identity matching? | verdict |
|---|---|---|---|---|
| A/G contract meta-theory (Benveniste et al. 2018) | no — ⊗ commutative, mutual | symmetric only ("M1 × M2 defined iff composable", Table 4.1) | no | **no** |
| Interface Automata (de Alfaro & Henzinger 2001) | no — parallel | optimistic, fixpoint pruning | no — shared actions only | **no** |
| **Relational interfaces** (Tripakis, Lickly, Henzinger & Lee, TOPLAS 33(4) 2011, DOI 10.1145/1985342.1985345) | **yes** — serial composition with `Φ := (f₁ ∧ ρθ) → in(f₂)`: "no matter which outputs I₁ chooses… all such outputs are legal inputs for I₂" | **deliberately no** — "we do not impose an a-priori compatibility condition"; compatibility = well-formability of the composite (Def 10) | no — connection is identity `y = x` only | **partial — nearest parent** |
| Tagged Signal Model (Lee & Sangiovanni-Vincentelli, IEEE TCAD 17(12) 1998, DOI 10.1109/43.736561) | — | no — total, denotational intersection | no | **no** |
| I/O automata (Lynch & Tuttle 1989); Moore/bidirectional interfaces (Chakrabarti et al. CAV 2002) | no — symmetric output-disjointness / mutual predicate satisfaction | — | no | **no** |

**Verdict: no verified source combines sequential + iff-gated + bridged matching.**
V4.1 decomposes into: the **directional core** from relational interfaces' serial
`Φ`-term (the nearest parent — the same asymmetric output-vs-input containment as
`Match(Tgt t, Src u)`), the **iff-shaped partiality** from the compositability
tradition (meta-theory Table 4.1, IA compatibility — precisely the tradition
relational interfaces rejected), and the **Bridge disjunct**, which has no counterpart
in any verified source: connections in every theory checked are variable-identity or
shared-action, never a registered relation between distinct contract identities.

The parent finding's table said V4.1 is a `SPECIALIZATION` of compatibility-gated
composition. With the survey run, the specialization decomposes into two donor
mechanisms plus one unclaimed disjunct. ORION-17 may own the **Bridge disjunct over
obligation-contract identity** and the obligation typing; it may not present the
compatibility-gated shape, nor the directional discharge test, as new.

## What this does to the resized claim

The parent finding's resized claim — "a decidable, registry-based compatibility test
for sequential composition of obligation-carrying transformations, proved sound against
a demand-containment semantics, with its incompleteness characterised rather than
hidden" — survives unchanged and gains precise parentage:

1. its semantic core is eq 11.4's derived-containment pattern, directionalized (Test 1);
2. its operator shape is relational interfaces' serial term fused with the
   compositability partiality those same authors explicitly rejected (Test 2) — a
   combination the literature has not made, for a contract domain (obligation records)
   the literature does not have;
3. the Bridge disjunct and `Fresh` are the two elements with no counterpart anywhere
   checked, and are therefore the only parts a novelty claim can rest on — along with
   the proved sound/incomplete gap of the registry surrogate, which remains the
   calculus's honest core.

This remains a bounded, interface-theory-tradition contribution. Nothing here promotes
it to a new composition law.

## Attribution correction

An intermediate attribution — "a theory of relational interfaces, ACM TECS 2017, Zhao,
Zhu, Sanán" — was `NOT_FOUND`/refuted in every search; the journal version of the
relational-interfaces theory is the **TOPLAS 2011** article by Tripakis, Lickly,
Henzinger & Lee (conference version: "On Relational Interfaces", EMSOFT'09,
DOI 10.1145/1629335.1629346). Recorded so the chain never cites the phantom.

## Boundary and honesty

The survey covered the A/G meta-theory, interface automata, relational interfaces, the
tagged signal model, I/O automata, and Moore/bidirectional interfaces — the families
the parent finding named, plus the meta-theory's own frameworks. Scope limits: the
Interface Automata 2001 PDF is Type-3-font-encoded and could not be text-extracted
directly; its composition definition was verified via the 2018 monograph's restatement
(Def 8.5, whose illegal-state test (8.23) quantifies over both orders — symmetric),
and this is marked as such. Lynch–Tuttle and Chakrabarti et al. were verified via the
monograph's and Tripakis et al.'s restatements, not the originals. The no-source-combines
claim is scoped to the sources above; a framework outside these families combining the
three features would amend this document, not the claim's defense.
