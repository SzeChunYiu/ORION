# Where the composition calculus actually sits — parent finding V1

**Status:** `NEAREST_PARENT_REIDENTIFIED__CLAIM_RESIZED__NO_AUTHORITY_DELTA`
**Date:** 2026-09-02
**Scientific authority delta:** `NONE`. This document re-positions a claim and
narrows it. It proves nothing new and promotes nothing.

`DONOR_MATRIX_V1.md` flagged planning abstraction / MDP homomorphism as a threat
to the surviving residue and left the test unperformed. Performing it moves the
threat: **Ravindran–Barto is the wrong parent, and a closer one exists.**

## What the calculus states

From `manuscript/sections/02-composition-calculus.tex`:

- `Carries(t) ↔ Native(t) ∧ ∀c. Holds(t, c)` — the closure lift.
- `Match(a, b) := a = b ∨ Bridge(a, b)` — the intermediate-contract test.
- **V4.1** `Carries(Comp(t,u)) ↔ Carries(t) ∧ Carries(u) ∧ Match(Tgt t, Src u)`.
- **V4.2** `Ident(a)` is a two-sided unit and the two bracketings of a
  three-transformation chain are observationally equal, with `Bridge` assumed
  neither reflexive, symmetric, nor transitive.
- **V4.3** the rule is **sound but incomplete**: `Match` on intermediate
  contracts suffices for obligation-totality but is not necessary; the exact
  condition is containment of the second leg's source demands in the first
  leg's target demands.

## Why MDP homomorphism is not the parent

Homomorphism composition is closure of a class under composition, and it
composes on **strict object matching** — `cod(h₁) = dom(h₂)`. It provides no
compatibility relation, so V4.1's `Bridge` disjunct has no homomorphic
counterpart, and V4.1's side condition cannot be a corollary of homomorphism
composition. The threat recorded in `DONOR_MATRIX_V1.md` is **weaker than
stated there**, and that entry should be read as superseded by this document.

## The actual parent: interface and contract theories

`Src`/`Tgt` interface contracts, a compatibility relation gating composition,
composition-under-compatibility, refinement, and associativity are the primitive
apparatus of interface theories and of the contract meta-theory:

- de Alfaro & Henzinger, *Interface Automata*, ESEC/FSE (2001);
  de Alfaro & Henzinger, *Interface-Based Design*, NATO Science Series 195 (2005);
- Benveniste, Caillaud, Nickovic, Passerone, Raclet, Reinkemeier,
  Sangiovanni-Vincentelli, Damm, Henzinger & Larsen, *Contracts for System
  Design*, Foundations and Trends in Electronic Design Automation, Now
  Publishers (2018), ISBN 978-1-68083-402-4.

The meta-theory's stated purpose is to give a generic contract notion and relate
existing interface theories to it, with parallel composition, conjunction,
quotient, refinement, and **compatibility/consistency conditions** instantiated
per framework. That is the shape of the calculus.

## What this does to each theorem

| theorem | disposition | reason |
|---|---|---|
| V4.1 | `SPECIALIZATION` of compatibility-gated composition | "composite is well-formed iff both legs are and their interfaces are compatible" is the standard shape. |
| V4.2 | `DONOR`, and **currently overstated** | see below. |
| V4.3 | the honest core, and it points at the same parent | see below. |

**V4.2 is shallower than its framing suggests.** Both bracketings of
`Comp(Comp(t,u),v)` and `Comp(t,Comp(u,v))` reduce to the same obligation set
— `Match(Tgt t, Src u)` and `Match(Tgt u, Src v)` — given only the projection
laws `Tgt(Comp(t,u)) = Tgt u` and `Src(Comp(u,v)) = Src u`. No property of
`Bridge` is needed because none is used: associativity follows from the
projections, not from the relation. The unit law likewise uses only the equality
disjunct of `Match`. Presenting "no reflexivity, no symmetry, no transitivity"
as a strength therefore claims difficulty the proof does not face, and the
manuscript should not lean on it.

**V4.3 is the result worth keeping, and it identifies its own parent.** The
exact condition it derives — containment of the second leg's source demands in
the first leg's target demands — is the assume/guarantee composability
condition: the first component's guarantee must discharge the second's
assumption. The paper has independently rederived the A/G condition and then
shown that its own registry-based `Match` is a strictly coarser, sound
approximation of it.

## The resized claim

The defensible contribution is **not** a new composition law. It is:

> a decidable, registry-based compatibility test for sequential composition of
> obligation-carrying transformations, proved sound against a demand-containment
> semantics, with its incompleteness characterised rather than hidden.

That is smaller than "new composition calculus" and larger than nothing: a
checkable surrogate for a semantic condition, with a proved gap, is a normal and
publishable contribution in the interface-theory tradition. It also explains why
the calculus refuses composites that are in fact obligation-total — a behaviour
the manuscript already reports as a real gap in its own rule.

## Two things this does not establish

1. **That the A/G identification is exact.** It rests on reading V4.3's
   `Demands` containment as an assume/guarantee condition. Confirming it
   requires mapping `Demands`, `Discharged` and `Fresh` onto a specific A/G
   formulation from the meta-theory and checking the correspondence in both
   directions. Until that is done the identification is `PLAUSIBLE`, not
   `PROVED`, and this document does not claim otherwise.
2. **That no interface theory already has the exact V4.1.** Interface automata
   compose *optimistically* — two components may compose even where each alone
   has unsatisfiable assumptions — whereas V4.1's left-to-right direction is
   conjunctive, and contract composition is usually commutative with a symmetric
   compatibility whereas `Match` is sequential and not assumed symmetric. Those
   are real differences, but a survey of the meta-theory's frameworks against
   them has not been run.

Both are concrete, in-house, and decidable without external data. They are the
next tests, and they are the ones that would settle the residue.
