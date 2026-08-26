# Epistemic Navigation in Open Worlds — V4

**Paper VII current science manuscript overlay**
**Date:** 2026-08-22
**Historical base:** `FINAL.md` / V2 formal core / `FINAL_V3.md` retained
**Formal artifacts:** `formal/mechanized/P7_COMPOSITION_CALCULUS_MECHANIZED_2026-08-21.json`,
`formal/mechanized/P7_DONOR_STACK_AS_TRANSFORMATION_FAMILY_2026-08-22.json`
**Science terminal:** `P7_CLOSURE_CARRYING_NAVIGATION_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT`

V3 presented a closure-carrying navigation semantics whose support was an
exhaustive enumeration over a bounded donor stack. V4 changes what the paper
claims about that support, in both directions. The composition laws are now
discharged by a solver over uninterpreted sorts, so they hold for chains of any
length over any number of donor families, closure coordinates and obligation
contracts; and the two composition counts V3 reported as findings are shown here
to carry far less than their size suggests, so what they establish is stated
precisely rather than left to the number.

## Replacement abstract for V4

Scientific navigation already has strong donor mechanisms: sound planning
abstraction and refinement, counterexample-guided refinement, bidirectional
transformation and migration, world-model replanning, and terminal-commitment
frameworks. P7 treats these as reusable navigation transforms and asks how
task-global scientific closure survives them. The answer is a closure-carrying
navigation semantics in which a donor-valid transformation carries closure only
through an explicit obligation witness, and in which heterogeneous transforms
compose only when the intermediate obligation contract is exactly bound or
explicitly bridged.

That composition law is now a **theorem rather than an enumeration**. Over
uninterpreted sorts of transformations, contracts, closure coordinates and
obligations, with the donor-native validity predicate left uninterpreted,
identity is a unit, composition is associative, and a composite carries closure
if and only if both legs carry it and the intermediate contract matches. The
side conditions are named rather than assumed away: the unit law needs the
contract test to be reflexive, the equational forms of the laws need
extensionality, and obligation-totality composition needs containment of
demanded obligations rather than a registered bridge. One consequence is
negative and is kept: P7's composition rule is provably **incomplete against its
own obligation semantics**, refusing composites whose contracts demand exactly
the same obligations when no bridge is registered. It is sound and fail-closed,
not exact.

The bounded model is then recovered as an instance rather than repeated as
separate support. The five donor families are interpreted as a **transformation
family**: each is a transformation with its own source and target obligation
contracts, and the intermediate-contract test becomes a function of the two
transformations and of the registered bridge relation rather than a value
supplied by the caller. Under three frame conditions, twelve further theorems
are discharged at arbitrary width, and P7's published 25 composition successes
and 25 bridge-mismatch countermodels are recomputed by running the committed
implementation with the hand-off computed rather than typed.

What that recovery exposes is reported in full below, because it is a limit on
the paper's own evidence and not on the theorems.

## 18. The composition calculus (replaces the informal V3.5)

Let `Trans`, `Contract`, `Coord` and `Obl` be sorts, `Native : Trans -> Bool` the
donor's own preservation/refinement/round-trip verdict, `Holds : Trans x Coord ->
Bool` the per-coordinate closure status, `Src`, `Tgt : Trans -> Contract` the
obligation contracts a transformation consumes and emits, and `Bridge : Contract
x Contract -> Bool` the registered bridge relation.

**The closure lift.** `Carries(t) <-> Native(t) AND forall c. Holds(t, c)`. This
is V3's `ClosureCarries(T, o)` with the five-tuple replaced by a quantifier, so
nothing below depends on there being five coordinates.

**The intermediate-contract test.** `Match(a, b) := a = b OR Bridge(a, b)`,
verbatim from V3.5's "exactly the same contract, or a registered bridge".

**Coordinate transport (the one substantive axiom).** A composite holds a closure
coordinate exactly when both legs hold it, and the distinguished coordinate
`obligations_total` additionally requires `Match(Tgt t, Src u)`.

### Theorem V4.1 — intermediate-contract composition
`Carries(Comp(t,u)) <-> Carries(t) AND Carries(u) AND Match(Tgt t, Src u)`, for
every pair of transformations. This is V3.5, and it is *derived* from coordinate
transport rather than assumed; a calculus that took it as an axiom would be
assuming its own conclusion.

### Theorem V4.2 — unit and associativity
`Ident(a)` carries closure, is a two-sided unit, and the two bracketings of a
three-transformation chain are observationally equal — with nothing assumed of
the bridge relation: no reflexivity, no symmetry, no transitivity. Under
extensionality both laws hold as equations. The unit law needs the *test* to be
reflexive, which it is because `Match` has an equality disjunct; with the raw
registered relation in its place there is a countermodel.

### Theorem V4.3 — the rule is sound and incomplete
Under an obligation semantics defined without reference to any composition rule,
`Total(t) <-> forall o. Demands(Tgt t, o) -> Demands(Src t, o) OR Discharged(t,o)
OR Fresh(t,o)`, matching intermediate contracts **suffice** for totality to
compose but are **not necessary**. The exact condition is weaker: containment of
the second leg's source demands in the first leg's target demands. P7's rule
therefore refuses composites that are in fact obligation-total. This is a real
gap in the paper's own rule and is reported as one.

## 19. The donor stack as a transformation family

V3's composition support is a `5 x 5` loop over donor families in which, in the
committed checker, neither donor appears on the right-hand side of anything and
both legs are the same loop-invariant expression. Instrumented, that loop
evaluates `compose` at **2 of its 8 possible argument triples**. Under the
interpretation each family becomes a transformation with its own hand-off
contracts, and the third argument is computed from the pair rather than typed.

Three frame conditions are stated as axioms rather than folded into an encoding:

1. **Hand-offs are never contract identities** — no family's target contract is
   any family's source contract, its own included.
2. **Distinct families have distinct endpoints.**
3. **The stack is inhabited.**

### Theorem V4.4 — the composition rows, generalised
A bridged hand-off between two carrying donors composes; an unbridged one
refuses; a donor composed with itself still needs a bridge registered from its
own target contract back to its own source contract; and a chain of three donors
carries exactly when all three legs carry and both interior hand-offs are
bridged. For a stack of any size.

### Theorem V4.5 — the rows the enumeration does not contain
If either leg fails to carry, the composite does not carry, whatever the other
leg is and whatever the registry says. These are the six argument triples the
published loop never evaluates.

### Theorem V4.6 — the donor axis indexes something
Distinct ordered donor pairs present distinct hand-offs, and two pairs whose
hand-offs the registry decides differently have composites that carry
differently. On an inhabited carrying stack, both the successes and the refusals
have witnesses rather than holding vacuously.

Two conditions that looked like frame conditions — that no identity is a donor,
and that a composite's hand-off is separated too — were written as axioms first,
reported inert, and are now discharged as theorems from the remaining three.
Their inertness is re-measured rather than remembered: both are added back to the
axiom set on every run and the theorems that becomes newly provable are reported,
and the answer has to stay none.

## 20. What the published composition counts do and do not carry

This section exists because the numbers in V3's support table are larger than
the facts behind them, and the difference is measurable.

**25 bridge-mismatch countermodels is exactly one frame condition.** Once the
hand-off is computed rather than typed, a refused composite is one whose
hand-off does not match, so 25 refusals under an empty registry *is* the
statement that no family's target contract is any family's source contract. Read
as a check on the interpretation this is good news: the condition is P7's own
assertion and not a modelling convenience. Read as a count it is one fact.
Assignments that violate it return 0, 20 and 21 instead of 25.

**25 composition successes discriminates nothing about the interpretation.**
Every contract assignment tried — including ones that collapse the whole stack to
a single contract pair — returns 25 under a registry that bridges every hand-off,
because a full registry satisfies the match test whatever the contracts are.

**The counts cannot see the second frame condition at all.** Reading every family
as consuming one shared input contract and emitting one shared output contract
reproduces both published numbers exactly, and so does reading them as emitting
one shared output contract. Those are the readings in which the `5 x 5` loop
visits **1** and **5** distinct hand-offs rather than 25 — precisely the
multiplier the interpretation is supposed to remove — and the published pair is
blind to both. What separates them is Theorem V4.6 and the directly measured
hand-off count, not the counts. A registry that bridged some hand-offs and not
others would have separated them empirically; P7 shipped no such registry.

**The published counts still reach two argument triples, and this is now a fact
about the registries.** Reproducing 25 successes requires every hand-off bridged
and reproducing 25 countermodels requires none bridged, both over an all-carrying
stack. The 25 rows are 25 distinct hand-offs rather than 25 copies of one
argument; they remain 25 agreeing verdicts. The other six triples are exercised
separately, over 204,800 evaluations of the committed functions against the
proved rule. Both verdicts occur, but the corpus is heavily skewed — only 25 of
those rows compose successfully, one per ordered donor pair, because a leg
carries at exactly one of the 64 (native verdict, closure vector) rows it is
given — and the per-triple counts are published beside the total rather than
summarised. That enumeration is not part
of P7's published result and does not become part of it by being run.

## Exhaustive bounded support (unchanged, re-read)

The enumeration of V3 is unchanged on disk and its digest is unchanged:

- states: **320**; donor-conservativity violations: **0**; ideal-product
  mismatches: **0**;
- minimal one-coordinate closure separations: **25**;
- donor-product nonclosure countermodels: **31**;
- exact full closure-refinement successes: **155**;
- proper-subset closure-refinement failures: **1,055**;
- heterogeneous composition successes under exact bridge: **25**;
- bridge-mismatch composition countermodels: **25**;
- canonical rows SHA-256:
  `25f40385714adb15bca298a8cfd2b7fe2b28c96bfe462f6b60583be8f735b95f`.

What V4 changes is the reading. The 155 and 1,055 are a five-way donor
multiplication of 31 and 211: the donor loop enters neither the closure vector
nor the repair set. Neither does anything else under it — 320 states is the
64-point (native verdict, closure vector) space enumerated once per family, the
25 minimal separations are 5 counted five times, and the 25 successes and 25
bridge countermodels are one of each counted once per ordered donor pair. Only
the 31 nonclosure countermodels are 31 distinct facts. The `donor_axis` block of
`research/claim_expansion/p7/P7_X2_CLOSURE_CARRYING_RESULT_V1.json` carries the
same table, computed by running the checker at one donor and at five. The
composition pair is discussed in §20. The counts remain
correct and remain reproducible; they are support for a bounded instance, and
the general claims are now carried by §§18–19 instead.

## Non-synthetic evidence in three change classes

The support enumerated above is bounded and synthetic. Three executed studies
carry the same separation into real data, one per change class, each frozen
before execution and reproduced by a second implementation sharing no facts or
gold code with the first.

**Representation change.** The public RO-Crate `1.2 -> 1.3` transition, where
four Bioschemas workflow terms changed canonical URI bindings while ordinary
value-level JSON usage can appear unchanged. Across 14 frozen cases,
witness-aware transport is exact (**1.0**) with **0** false closures, **0**
unnecessary reopens and **4** correct `CANNOT_CHECK`. Value-only reaches
**0.428571** with **8** false closures; always-reopen **0.285714** with **6**
unnecessary reopens.

**Responsibility/ontology change.** The 178-example UCI Wine data, where the
coarse responsibility `class0_vs_other` makes the reverse coarse-to-fine map
non-injective because coarse `0` merges fine classes `1` and `2`. Across 712
protected transport rows, witness-aware transport is **1.0** with **238**
correct `CANNOT_CHECK`; value-only reaches **0.665730**, converting those same
238 into false closures; always-reopen reaches **0.0** with **474** unnecessary
reopens. The **119** ambiguous coarse-0 examples are where locally well-formed
representation changes require different dispositions depending on retained
support history.

**Objective/obligation change.** The 569-example Wisconsin Diagnostic Breast
Cancer data under a frozen `StratifiedKFold(n_splits=5, shuffle=True,
random_state=20261217)` split, with the obligation moving from aggregate
accuracy to malignant recall. The two obligations come apart in both directions:
fold 0 satisfies the old (`0.965 >= 0.95`) and fails the new (`0.907 < 0.95`),
while fold 1 fails the old (`0.947 < 0.95`) and satisfies the new
(`0.953 >= 0.95`). All five accuracy-only cells are `CANNOT_CHECK`, because
malignant recall is not inferable from aggregate accuracy; value-only produces
**5** false closures and always-reopen **4** unnecessary reopens.

Witness-aware transport is **1.0** in all three classes and both degenerate
policies separate in every one: value preservation alone closes transitions it
has not earned, and always reopening pays for transitions already witnessed.

**What this does not establish.** Three executed change classes, not a universal
claim. It does not establish scientific-regime transport across arbitrary
world-model, objective or research-agent changes, and the agreement is between
two implementations inside the same workflow, not an external adjudication. The
breast-cancer study is a transport experiment over a frozen split: no clinical
use is claimed and no classifier or medical decision rule is offered.


## Wider P7 claim (V4 wording)

> Scientific navigation can reuse mature planning/refinement,
> counterexample-guided reopening, representation-migration, replanning and
> terminal-commitment machinery while carrying task-global closure as an explicit
> obligation object; closure-transport defects can be selectively refined; and
> heterogeneous navigation transforms compose scientifically only when their
> intermediate closure contracts are correctly bridged — which holds for chains
> of any length over donor stacks of any size, and is sound but not complete
> against P7's own obligation semantics.

## Limits

The registered closure coordinates remain a bounded formal instance and are not
claimed universally minimal. The composition rule is fail-closed and provably
incomplete: it refuses composites that are obligation-total but unbridged. No
naturalistic multi-stage pipeline corpus exists, so nothing here is an empirical
or deployed-agent claim, and the false-closure/recomputation trade-off is not
measured. No formal or empirical reproduction outside the producing lane has been
arranged: the calculus, the interpretation and the tests were written in the same
lane, and independent reproduction remains open. P7's other formal core — the
64-state support-transport theorem — is a different model and is untouched here.

**Current science terminal:**
`P7_CLOSURE_CARRYING_NAVIGATION_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT`.

## 19. The exact containment rule (2026-08-24)

Section 18's rule asks whether the intermediate contract is *identical or
registered-bridged*, and that section keeps the finding that the rule is sound
but incomplete against the obligation semantics: it refuses composites whose
contracts demand exactly the same obligations when no bridge has been
registered. This section replaces the rule; the incompleteness finding about
the old rule stands, append-only, as the reason the replacement exists.

The replacement is the condition Section 18's own characterization named:

    Contains(a, b)  :=  forall o. Demands(b, o) -> Demands(a, o)

read as "the emitted contract demands every obligation the consumed contract
demands". Coordinate transport becomes: a composite holds a closure coordinate
exactly when both legs hold it, and the distinguished `obligations_total`
coordinate additionally requires `Contains(Tgt t, Src u)`. Nothing else in the
calculus changes, and nothing is typed by a caller or waiting on a registrar:
the hand-off is a function of the two contracts' obligation content.

Twelve discharges under contract `P7.CONTAIN.EXACT_BRIDGE_RULE.V1`
(`src/orion/study/p7/exact_containment.py`, receipt
`formal/mechanized/P7_EXACT_CONTAINMENT_MECHANIZED_2026-08-24.json`, bound by
`formal/check_exact_containment_binding_v1.py`):

- **Soundness.** Under the obligation semantics alone — which mentions no
  composition rule — two total legs with a containing hand-off compose to a
  total composite.
- **The condition is not droppable.** A model with two total legs, a
  non-containing hand-off and a non-total composite exists, so the condition is
  load-bearing.
- **Completeness, stated precisely.** The old rule implies containment (nothing
  previously licensed is lost), and a closed-world witness exhibits a composite
  the old rule refuses — distinct, unbridged, obligation-equivalent contracts —
  that the replacement licenses. Together with soundness this is the sense in
  which the replacement is exact: the weakest condition of this form that keeps
  totality composing.
- **Unit and associativity survive.** Containment is reflexive and transitive;
  the unit laws hold observationally and, under extensionality, as equations;
  associativity holds both ways. No bridge relation appears anywhere in the new
  calculus.

What this does not change: the composition calculus of Section 18 and its
receipt remain bound and un-retracted; the replacement is a second calculus
whose transport clause differs in one place. The data-heavy sub-box — at least
two non-retrieval domains with at least fifty transitions per domain — remains
open: no such corpus exists in the repository, and none is simulated.
